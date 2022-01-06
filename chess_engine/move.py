# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 12:56:04 2021

@author: Korean_Crimson
"""
import itertools
from dataclasses import dataclass
from typing import List
from typing import Tuple

# pylint: disable=invalid-name
@dataclass
class Move:
    """Move class. Encapsulates how a piece moves. To be inherited from when implementing a move"""

    range_: int
    direction: int = 1
    forward_only: bool = False
    horz_move: bool = False
    can_capture: bool = False

    def compute_valid_moves(
        self, position: Tuple[int, int], board, team: int
    ) -> List[Tuple[int, int]]:
        """Computes all valid moves that can be made from the passed position"""
        x, y = position
        horz_moves = self._compute_horz_moves(x, y, board, team)
        vert_moves = self._compute_vert_moves(x, y, board, team)
        return horz_moves + vert_moves

    def _compute_horz_moves(self, current_x, y, board, team):
        if not self.horz_move:
            return []

        moves = []

        #forward
        for x in range(current_x + 1, board.size):
            square = board[x, y]
            if square is None or square.team != team:
                moves.append((x, y))
            if square is not None:
                break

        #backward
        for x in range(current_x - 1, -1, -1):
            square = board[x, y]
            if square is None or square.team != team:
                moves.append((x, y))
            if square is not None:
                break

        return moves

    def _compute_vert_moves(self, x, current_y, board, team):
        forward_moves = []
        for y in range(current_y - 1, current_y - 1 - self.range_, -1):
            if y < 0:
                break

            square = board[x, y]
            if square is None or (square.team != team and self.can_capture):
                forward_moves.append((x, y))
            if square is not None:
                break

        backward_moves = []
        for y in range(current_y + 1, current_y + 1 + self.range_):
            if y >= board.size:
                break

            square = board[x, y]
            if square is None or (square.team != team and self.can_capture):
                backward_moves.append((x, y))
            if square is not None:
                break

        if self.forward_only:
            return forward_moves if self.direction == -1 else backward_moves
        return forward_moves + backward_moves


@dataclass
class BishopMove:
    """Moves diagonally to either side of the board, backwards and forwards"""

    range_: int
    direction: int = 1
    forward_only: bool = False
    must_capture: bool = False

    def compute_valid_moves(
        self, position: Tuple[int, int], board, team: int
    ) -> List[Tuple[int, int]]:
        """Computes all valid moves that can be made from the passed position"""
        generators_forward = [
            self._compute_valid_moves(position, board, team, min_x=False, min_y=True),
            self._compute_valid_moves(position, board, team, min_x=True, min_y=True),
        ]
        generators_backward = [
            self._compute_valid_moves(position, board, team, min_x=True, min_y=False),
            self._compute_valid_moves(position, board, team, min_x=False, min_y=False),
        ]
        if self.forward_only:
            generators = (
                generators_forward if self.direction == -1 else generators_backward
            )
        else:
            generators = generators_forward + generators_backward
        squares = [square for generator in generators for square in generator]
        return squares

    # pylint: disable=too-many-arguments,too-many-locals
    def _compute_valid_moves(self, position, board, team, min_x=False, min_y=False):
        x, y = position
        end_x, x_step = (x - self.range_ - 1, -1) if min_x else (x + self.range_ + 1, 1)
        end_y, y_step = (y - self.range_ - 1, -1) if min_y else (y + self.range_ + 1, 1)
        get_indices = lambda start, stop, step: itertools.takewhile(
            lambda x: 0 <= x < 8, range(start, stop, step)
        )
        indices = list(
            zip(get_indices(x, end_x, x_step), get_indices(y, end_y, y_step))
        )
        squares = [board[x, y] for x, y in indices]

        for pos, square in zip(indices, squares):
            if pos == position:
                continue

            if square is None:
                if not self.must_capture:
                    yield pos
            else:
                if square.team != team:
                    yield pos
                break


# pylint: disable=too-few-public-methods
class InitialPawnMove(Move):
    """Moves 2 spaces forward"""

    def __init__(self, direction):
        range_ = 2
        super().__init__(
            range_, direction, forward_only=True, can_capture=False
        )


class KingMove:
    """Moves 1 space in any direction"""

    @staticmethod
    def compute_valid_moves(position: Tuple[int, int], board, team: int) -> List[Tuple[int, int]]:
        """Computes all valid moves that can be made from the passed position"""
        neighbours = lambda x: [y for y in (x - 1, x, x + 1) if 0 <= y < board.size]
        x, y = position
        return [pos for pos in itertools.product(neighbours(x), neighbours(y))
                if pos != position and (board[pos] is None or board[pos].team != team)]

class PawnMove(Move):
    """Moves 1 space forward"""

    def __init__(self, direction):
        range_ = 1
        super().__init__(
            range_, direction, forward_only=True, can_capture=False
        )


class PawnCapture(BishopMove):
    """Moves 1 space forward diagonally and needs to capture"""

    def __init__(self, direction):
        range_ = 1
        super().__init__(range_, direction, forward_only=True, must_capture=True)


class EnPassantMove:
    """Pawn capture but with a pawn that already passed"""


class RookMove(Move):
    """Moves horizontally or vertically for up to 8 spaces"""

    def __init__(self):
        range_ = 8
        super().__init__(range_, horz_move=True, can_capture=True)


class KnightMove:
    """Knight move"""

    @staticmethod
    def compute_valid_moves(position: Tuple[int, int], board, team: int) -> List[Tuple[int, int]]:
        """Computes all valid moves that can be made from the passed position"""
        x1, y1 = position
        indices = [(x, y) for x, y in itertools.product((1, 2, -1, -2), repeat=2)
                   if abs(x) != abs(y)]
        positions = [(x1 + x2, y1 + y2) for x2, y2 in indices]
        return [pos for pos in positions if board.is_on_board(pos)
                and (board.is_empty_at(pos) or board.is_enemy(pos, team))]
