# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 12:56:04 2021

@author: Korean_Crimson
"""
import itertools
from dataclasses import dataclass
from typing import Generator, List

from chess_ng.interfaces import Board, Direction, Piece
from chess_ng.util import Move


# pylint: disable=invalid-name
@dataclass
class LineMove:
    """Move class. Encapsulates how a piece moves. To be inherited from when implementing a move"""

    range_: int
    direction: int = 1
    horz_move: bool = False
    can_capture: bool = False

    def compute_valid_moves(self, board: Board, piece: Piece) -> List[Move]:
        """Computes all valid moves that can be made from the passed position"""
        x, y = piece.position
        return list(
            itertools.chain(
                self._compute_horz_moves(x, y, board, piece.team),
                self._compute_vert_moves(x, y, board, piece.team),
            )
        )

    def _compute_horz_moves(
        self, current_x: int, y: int, board: Board, team: str
    ) -> Generator[Move, None, None]:
        if not self.horz_move:
            return

        # forward
        for x in range(current_x + 1, board.size):
            square = board[x, y]
            if square is None:
                yield Move((x, y))
            elif board.is_enemy((x, y), team):
                yield Move((x, y), can_capture=True)
            if square is not None:
                break

        # backward
        for x in range(current_x - 1, -1, -1):
            square = board[x, y]
            if square is None:
                yield Move((x, y))
            else:
                if board.is_enemy((x, y), team) and self.can_capture:
                    yield Move((x, y), can_capture=True)
                break

    def _compute_vert_moves(
        self, x: int, current_y: int, board: Board, team: str
    ) -> Generator[Move, None, None]:
        for y in range(current_y - 1, current_y - 1 - self.range_, -1):
            if y < 0:
                break

            square = board[x, y]
            if square is None:
                yield Move((x, y))
            else:
                if board.is_enemy((x, y), team) and self.can_capture:
                    yield Move((x, y), can_capture=True)
                break

        for y in range(current_y + 1, current_y + 1 + self.range_):
            if y >= board.size:
                break

            square = board[x, y]
            if square is None:
                yield Move((x, y))
            else:
                if board.is_enemy((x, y), team) and self.can_capture:
                    yield Move((x, y), can_capture=True)
                break


# pylint: disable=too-few-public-methods
class BishopMove:
    """Moves diagonally to either side of the board, backwards and forwards"""

    @staticmethod
    def compute_valid_moves(board: Board, piece: Piece) -> List[Move]:
        """Computes all valid moves that can be made from the passed position"""
        moves: List[Move] = []
        x_pos, y_pos = piece.position
        team = piece.team
        for x_dir, y_dir in itertools.product((1, -1), repeat=2):
            x = x_pos + x_dir
            y = y_pos + y_dir
            while board.is_on_board((x, y)):
                pos = (x, y)
                square = board[pos]
                if square is None:
                    moves.append(Move(pos))
                elif board.is_enemy(pos, team):
                    moves.append(Move(pos, can_capture=True))
                if square is not None:
                    break
                x += x_dir
                y += y_dir
        return moves


class InitialPawnMove:
    """Moves 2 spaces forward"""

    def __init__(self, direction: Direction):
        self.direction = direction

    def compute_valid_moves(self, board: Board, piece: Piece) -> List[Move]:
        """Computes all valid moves that can be made from the passed position"""
        if len(piece.position_history):
            return []
        x, y = piece.position
        dir_ = self.direction

        def empty(y_: int):
            pos = (x, y + y_ * dir_)
            return board.is_on_board(pos) and board.is_empty_at(pos)

        return [Move((x, y + 2 * dir_))] if empty(1) and empty(2) else []


class KingMove:
    """Moves 1 space in any direction"""

    @staticmethod
    def compute_valid_moves(board: Board, piece: Piece) -> List[Move]:
        """Computes all valid moves that can be made from the passed position"""

        def neighbours(x: int) -> List[int]:
            return [y for y in (x - 1, x, x + 1) if 0 <= y < board.size]

        x, y = piece.position
        moves: List[Move] = []
        for pos in itertools.product(neighbours(x), neighbours(y)):
            if pos == piece.position:
                continue
            square = board[pos]
            if square is None:
                moves.append(Move(pos))
            elif board.is_enemy(pos, piece.team):
                moves.append(Move(pos, can_capture=True))
        return moves


class PawnMove:
    """Moves 1 space forward"""

    def __init__(self, direction: Direction):
        self.direction = direction

    def compute_valid_moves(self, board: Board, piece: Piece) -> List[Move]:
        """Computes all valid moves that can be made from the passed position"""
        x, y = piece.position
        pos = (x, y + 1 * self.direction)
        if board.is_on_board(pos) and board.is_empty_at(pos):
            return [Move(pos)]
        return []


class PawnCapture:
    """Moves 1 space forward diagonally and needs to capture"""

    def __init__(self, direction: Direction):
        self.direction = direction

    def compute_valid_moves(self, board: Board, piece: Piece) -> List[Move]:
        """Computes all valid moves that can be made from the passed position"""
        x, y = piece.position
        moves = ((x + 1, y + self.direction), (x - 1, y + self.direction))
        return [
            Move(x, can_capture=True)
            for x in filter(board.is_on_board, moves)
            if not board.is_empty_at(x) and board.is_enemy(x, piece.team)
        ]


class EnPassantMove:
    """Pawn capture but with a pawn that already passed"""


class RookMove(LineMove):
    """Moves horizontally or vertically for up to 8 spaces"""

    def __init__(self):
        range_ = 8
        super().__init__(range_, horz_move=True, can_capture=True)


class KnightMove:
    """Knight move"""

    INDICES = [
        (x, y)
        for x, y in itertools.product((1, 2, -1, -2), repeat=2)
        if abs(x) != abs(y)
    ]

    @classmethod
    def compute_valid_moves(cls, board: Board, piece: Piece) -> List[Move]:
        """Computes all valid moves that can be made from the passed position"""
        x1, y1 = piece.position
        positions = ((x1 + x2, y1 + y2) for x2, y2 in cls.INDICES)
        moves: List[Move] = []
        for pos in filter(board.is_on_board, positions):
            if board.is_empty_at(pos):
                moves.append(Move(pos))
            elif board.is_enemy(pos, piece.team):
                moves.append(Move(pos, can_capture=True))
        return moves
