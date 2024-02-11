"""Game module"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from chess_ng import hashing
from chess_ng.algorithm import Minimax, evaluate_length
from chess_ng.board import Board
from chess_ng.consts import BLACK, STARTING_FEN, WHITE
from chess_ng.fen import load_fen_notation
from chess_ng.interfaces import Piece
from chess_ng.piece import King, Position, Rook
from chess_ng.team import Team
from chess_ng.util import convert, convert_str


class ChessPositionError(Exception):
    """Can be thrown when a specified board position is invalid."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


@dataclass
class GameParams:
    """Game parameters"""

    depth: int = 2
    resign_threshold: int = -50
    mating_threshold: int = 10


@dataclass
class Game:
    """Game class. Manages board and teams."""

    teams: Dict[str, Team]
    minimax: Minimax
    board_factory: Callable[[List[Piece]], Board] = Board
    player: str = WHITE

    def __post_init__(self):
        self.board: Board = self.board_factory(
            [piece for team in self.teams.values() for piece in team.pieces]
        )
        self.rating: float = 0
        self.winner: Optional[str] = None
        self.is_draw = False
        self.previously_moved = BLACK
        self._messages: List[str] = []

    @classmethod
    def create_default(cls) -> Game:
        """Creates a Game with a default configuration"""
        teams, _ = load_fen_notation(STARTING_FEN)
        hash_values = hashing.get_hash_values(
            [x for team in teams.values() for x in team.pieces]
        )
        return cls(
            teams=teams,
            minimax=Minimax(
                evaluation_function=evaluate_length, hash_values=hash_values
            ),
        )

    def consume_messages(self) -> Iterable[str]:
        for message in self._messages:
            yield message
        self._messages.clear()

    def run_team(
        self, params: GameParams
    ) -> Optional[Tuple[Piece, Position, Position]]:
        """Chess game function. Evaluates the board using the AI, picks
        the most optimal move and then plays it. Any messages emitted get
        appended to the messages buffer, which needs to be emptied after
        calling this function for the messages to be emitted somewhere.
        """
        enemy = self.player_team
        team = self.team

        is_in_check = team.in_check(self.board, enemy.pieces)
        moves = team.compute_valid_moves(self.board, enemy.pieces)

        if not moves:
            if is_in_check:
                self.message(f"Checkmated team {team}. Team {enemy} wins.")
                self.winner = self.player
            else:
                self.message("Draw by stalemate")
                self.is_draw = True
            return None

        if self.board.is_draw_by_repetition():
            self.message("Draw by repetition.")
            self.is_draw = True
            return None

        if self.board.is_draw_by_fifty_moves():
            self.message("Draw by 50 move rule.")
            self.is_draw = True
            return

        if is_in_check:
            self.message("Moving out of check...")

        self.rating, piece_move = self.minimax.run(
            self.board,
            team,
            enemy,
            depth=params.depth,
            alpha=-math.inf,
            beta=math.inf,
            maximizing_player=True,
        )
        if piece_move is None:
            self.message("Error: a move could not be found...")
            self.winner = self.player
            return None

        piece_, move = piece_move
        if self.rating < params.resign_threshold:
            self.message("Bot resigned the game.")
            self.winner = self.player
            return None

        source_pos = piece_.position
        self.board.move_piece_and_capture(move.position, piece_, enemy.pieces)
        self.previously_moved = team.representation

        if enemy.in_check(self.board, team.pieces):
            moves = enemy.compute_valid_moves(self.board, team.pieces)
            if not moves:
                self.message("Checkmated player.")
                self.winner = team.representation
                return None
            self.message("Checking player king.")
        return piece_, source_pos, piece_.position

    def run_player(self, source_square: str, dest_square: str) -> Piece:
        """Takes a source and destination square e.g. a2 a4 moves the piece
        that is currently on a2 to a4 if it is a valid move. Raises a ChessPositionError
        for invalid moves. Returns the piece that was moved.
        """
        source_pos = self._get_source_position(source_square)
        destination_pos = self._get_destination_position(dest_square)
        piece_ = self.get_piece(source_pos, self.player_team.pieces)

        # check valid move
        moves = piece_.compute_valid_moves(self.board)
        filtered_moves = [move for move in moves if move.position == destination_pos]
        castling_moves = self._compute_castling_moves(piece_, source_pos)
        if not filtered_moves and not castling_moves:
            raise ChessPositionError(f"{piece_} cannot move to {dest_square}!")

        # check if in check
        valid_moves = self.player_team.compute_valid_moves(self.board, self.team.pieces)
        if not castling_moves and not (piece_, filtered_moves[0]) in valid_moves:
            raise ChessPositionError(
                f"Player is in check! {piece_} cannot move to {dest_square}."
            )

        if castling_moves:
            result = self._handle_castling(piece_, source_pos, destination_pos)
            if result is not None:
                piece_, destination_pos = result
        self.board.move_piece_and_capture(destination_pos, piece_, self.team.pieces)
        self.previously_moved = self.player
        return piece_

    def _compute_castling_moves(
        self, piece_: Piece, source_pos: Tuple[int, int]
    ) -> List[Piece]:
        """Returns rooks that would be able to castle, or an empty list
        if no castling is possible due to any reason."""
        if not isinstance(piece_, King) or piece_.position_history:
            return []

        castling_moves: List[Piece] = []
        king_x, y = source_pos
        team1, team2 = self.teams.values()
        enemy_team = team1 if team1 != self.teams[piece_.team] else team2
        for x in [0, 7]:
            rook = self.board[x, y]
            if (
                not isinstance(rook, Rook)
                or rook.team != piece_.team
                or rook.position_history
            ):
                continue

            for x2 in range(*sorted([x, king_x])):
                square = (x2, y)
                blocking_piece = self.board[square]
                if (
                    blocking_piece is not None
                    and blocking_piece is not piece_
                    or any(
                        x.can_capture_at(self.board, square) for x in enemy_team.pieces
                    )  # blocking check
                ):
                    break
            else:
                castling_moves.append(rook)
        return castling_moves

    def _handle_castling(
        self, king: Piece, source_pos: Tuple[int, int], destination_pos: Tuple[int, int]
    ) -> Optional[Tuple[Piece, Tuple[int, int]]]:
        x_dist = destination_pos[0] - source_pos[0]
        if abs(x_dist) != 2:
            return

        x, y = source_pos
        offset = x_dist // 2
        middle_square_pos = (x + offset, y)
        self.board.move_piece_and_capture(middle_square_pos, king, self.team.pieces)
        if self.team.in_check(self.board, self.team.pieces):
            self.board.move_piece_and_capture(
                source_pos, king, self.team.pieces
            )  # reset
            raise ChessPositionError(f"{king} cannot move to {destination_pos}!")
        self.board.move_piece_and_capture(destination_pos, king, self.team.pieces)
        piece_ = self.board[7 if x_dist == 2 else 0, y]  # rook
        if piece_ is None:
            return

        destination_pos = middle_square_pos
        self.message(f"Castled {'kingside' if x_dist == 2 else 'queenside'}.")
        return (piece_, destination_pos)

    def list_moves(self, source_square: str) -> Tuple[Piece, List[str]]:
        """Takes a source square (e.g. a2) and lists all possible moves
        for the piece on that square.
        """
        source_pos = self._get_source_position(source_square)
        piece_ = self.board[source_pos]
        if piece_ is None:
            raise ChessPositionError("The specified square does not contain a piece!")
        return piece_, [
            convert(move.position) for move in piece_.compute_valid_moves(self.board)
        ]

    def show_piece(self, source_square: str) -> Piece:
        """Takes a square (e.g. a2) and returns the piece that is on that square, if any.
        If the square is empty, it returns None.
        """
        source_pos = self._get_source_position(source_square)
        piece_ = self.get_piece(source_pos, self.player_team.pieces)
        return piece_

    @staticmethod
    def get_piece(source_pos: Tuple[int, int], pieces: Iterable[Piece]) -> Piece:
        """Returns the piece at the specified position"""
        for piece_ in pieces:
            if piece_.position == source_pos:
                return piece_
        raise ChessPositionError(
            "The source square specified does not contain a piece!"
        )

    def _get_source_position(self, source_square: str):
        return self._get_position(
            source_square, "The specified source square is invalid!"
        )

    def _get_destination_position(self, dest_square: str):
        return self._get_position(
            dest_square, "The specified destination square is invalid!"
        )

    @staticmethod
    def _get_position(square: str, message: str) -> Tuple[int, int]:
        """Converts a square string (e.g. a2) to an int tuple (e.g. (0, 5)).
        Raises a ChessPositionError if this is not possible.
        """
        try:
            source_pos = convert_str(square.lower())
        except Exception as exc:
            raise ChessPositionError(message) from exc
        return source_pos

    def message(self, message: str):
        """Appends the messages to the message buffer"""
        self._messages.append(message)

    @property
    def side_to_move(self) -> str:
        """Getter for side_to_move. Returns self.player if player has not previously moved, else
        returns the AI team representation.
        """
        return (
            self.player
            if self.previously_moved != self.player
            else self.team.representation
        )

    @property
    def team(self) -> Team:
        """Team getter, returns the team not controlled by the player."""
        key = WHITE if self.player == BLACK else BLACK
        return self.teams[key]

    @property
    def player_team(self) -> Team:
        """player_team getter, returns the team controlled by the player."""
        return self.teams[self.player]

    @property
    def is_over(self) -> bool:
        """Returns True if there is a winner or game is a draw"""
        return bool(self.winner or self.is_draw)
