# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:33:57 2021

@author: Korean_Crimson
"""

from __future__ import annotations

import logging
import math
from typing import List, Sequence, Tuple, Union

from chess_ng import move
from chess_ng.consts import BISHOP, KING, KNIGHT, PAWN, QUEEN, ROOK
from chess_ng.interfaces import Board, MoveInterface
from chess_ng.move import Direction
from chess_ng.util import Move, convert, convert_str, is_diagonal, is_straight

Position = Union[str, Tuple[int, int]]

# pylint: disable=invalid-name
class Piece:
    """Piece class. Needs to be subclassed by the various chess pieces"""

    turn_counter: float = 0.0

    def __init__(
        self, moves: Sequence[MoveInterface], position: Position, representation: str
    ):
        self.moves = moves
        self.position: Tuple[int, int] = (  # type: ignore
            convert_str(position) if isinstance(position, str) else position
        )
        self.representation = representation
        self.team: str = representation[-1]
        self.captured: bool = False
        self.position_history: List[Tuple[int, int]] = []

    def __repr__(self):
        return f"{self.__class__.__name__}({convert(self.position)})"

    def __hash__(self):
        return hash((self.position, self.representation))

    def update(self, board: Board):  # pylint: disable=no-self-use
        """Update piece"""

    def increase_search_depth(
        self, search_depth: int
    ) -> int:  # pylint: disable=no-self-use
        """Does nothing to search depth"""
        return search_depth

    def compute_valid_moves(self, board: Board) -> List[Move]:
        """Returns a list of squares that the piece can move to or capture at"""
        return [
            tuple_
            for move in self.moves
            for tuple_ in move.compute_valid_moves(board, self)
        ]

    def move_to(self, position: Tuple[int, int], log: bool = True) -> None:
        """Moves the piece to the specified position and adds it to the position history"""
        # pylint: disable=logging-fstring-interpolation
        pos_old = convert(self.position)
        self.position = position
        self.position_history.append(position)
        if log:
            self.turn_counter += 0.5
            logger = logging.getLogger("game.log")
            move_ = f"{self.representation} from {pos_old} to {convert(position)}"
            logger.info(
                f"Turn {math.ceil(self.turn_counter)}: Team {self.team}: {move_}"
            )

    def can_capture_at(self, board: Board, position: Tuple[int, int]) -> bool:
        """Returns true if this piece can move to the specified position.
        Note: doesnt check if piece is from opposite team.
        """
        return position in (move.position for move in self.compute_valid_moves(board))


class Pawn(Piece):
    """Pawn class. Contains all the pawn moves"""

    def __init__(self, direction: Direction, position: Position, representation: str):
        self._unpromoted_moves: Sequence[MoveInterface] = [
            move.InitialPawnMove(direction),
            move.PawnMove(direction),
            move.PawnCapture(direction),
        ]
        self._promoted_moves = [move.RookMove(), move.BishopMove()]
        self.promoted = False
        self.direction = direction
        super().__init__(self._unpromoted_moves, position, representation)

    def update(self, board: Board):
        self._update_promotion(board)

    def compute_valid_moves(self, board: Board) -> List[Move]:
        """Returns a list of squares that the piece can move to or capture at"""
        self._update_promotion(board)
        return super().compute_valid_moves(board)

    def can_capture_at(self, board: Board, position: Tuple[int, int]) -> bool:
        """Returns true if this piece can move to the specified position"""
        # optimization: return False if more than one square away
        if not self.promoted and abs(position[1] - self.position[1]) > 1:
            return False
        return super().can_capture_at(board, position)

    def _update_promotion(self, board: Board):
        target_y = 0 if self.direction == -1 else board.size - 1
        if target_y in (y for _, y in self.position_history + [self.position]):
            self.promoted = True
            self.moves = self._promoted_moves
        else:
            self.promoted = False
            self.moves = self._unpromoted_moves

    @property  # type: ignore
    def representation(self) -> str:  # type: ignore
        """Representation getter, depends on the promoted state"""
        return f"{QUEEN}{self.team}" if self.promoted else f"{PAWN}{self.team}"

    @representation.setter
    def representation(self, value: str):
        pass


class Knight(Piece):
    """Knight class. Contains all the knight moves"""

    def __init__(self, _, position: Position, representation: str):
        moves = [move.KnightMove()]
        super().__init__(moves, position, representation)

    def can_capture_at(self, board: Board, position: Tuple[int, int]) -> bool:
        """Returns true if this piece can move to the specified position"""
        x1, y1 = position
        x2, y2 = self.position
        # optimization: return False if not L-shaped 2 and 1 squares away
        if {abs(x1 - x2), abs(y1 - y2)} != {1, 2}:
            return False
        return super().can_capture_at(board, position)


class Bishop(Piece):
    """Bishop class. Contains all the bishop moves"""

    def __init__(self, _, position: Position, representation: str):
        moves = [move.BishopMove()]
        super().__init__(moves, position, representation)

    def can_capture_at(self, board: Board, position: Tuple[int, int]) -> bool:
        """Returns true if this piece can move to the specified position"""
        # optimization: return False if not on same diagonal
        if not is_diagonal(position, self.position):
            return False
        return super().can_capture_at(board, position)


class Rook(Piece):
    """Rook class. Contains all the rook moves"""

    def __init__(self, _, position: Position, representation: str):
        moves = [move.RookMove()]
        super().__init__(moves, position, representation)

    def can_capture_at(self, board: Board, position: Tuple[int, int]) -> bool:
        """Returns true if this piece can move to the specified position"""
        # optimization: return False if not horizontally or vertically aligned
        if not is_straight(position, self.position):
            return False
        return super().can_capture_at(board, position)


class Queen(Piece):
    """Queen class. Contains all the queen moves"""

    def __init__(self, _, position: Position, representation: str):
        moves: Sequence[MoveInterface] = [move.RookMove(), move.BishopMove()]
        self.depth_counter = 3
        super().__init__(moves, position, representation)

    def increase_search_depth(self, search_depth: int) -> int:
        if self.depth_counter <= 0:
            return search_depth
        self.depth_counter -= 1
        return search_depth + 2

    def can_capture_at(self, board: Board, position: Tuple[int, int]) -> bool:
        """Returns true if this piece can move to the specified position"""
        # optimization: return False if not horizontally or vertically aligned
        # and not same diagonal
        if not is_straight(position, self.position) and not is_diagonal(
            position, self.position
        ):
            return False
        return super().can_capture_at(board, position)


class King(Piece):
    """King class. Contains all the king moves"""

    def __init__(self, _, position: Position, representation: str):
        moves = [move.KingMove()]
        super().__init__(moves, position, representation)

    def can_capture_at(self, board: Board, position: Tuple[int, int]) -> bool:
        """Returns true if this piece can move to the specified position"""
        x1, y1 = position
        x2, y2 = self.position
        # optimization: return False if more than one square away
        if abs(x1 - x2) > 1 or abs(y1 - y2) > 1:
            return False
        return super().can_capture_at(board, position)


PIECES = {
    PAWN: Pawn,
    KNIGHT: Knight,
    BISHOP: Bishop,
    ROOK: Rook,
    QUEEN: Queen,
    KING: King,
}
