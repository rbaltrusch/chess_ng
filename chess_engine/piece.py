# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:33:57 2021

@author: Korean_Crimson
"""
import logging
import math
from typing import List

from chess_engine import move
from chess_engine.consts import BISHOP
from chess_engine.consts import KING
from chess_engine.consts import KNIGHT
from chess_engine.consts import PAWN
from chess_engine.consts import QUEEN
from chess_engine.consts import ROOK
from chess_engine.util import convert
from chess_engine.util import convert_str
from chess_engine.util import is_diagonal
from chess_engine.util import is_straight

from .move import Move

TURN_COUNTER = 0.0

#pylint: disable=invalid-name
class Piece:
    """Piece class. Needs to be subclassed by the various chess pieces"""

    def __init__(self, moves, position, representation):
        self.moves = moves
        self.position = convert_str(position) if isinstance(position, str) else position
        self.representation = representation
        self.team = representation[-1]
        self.captured = False
        self.position_history = []

    def __repr__(self):
        return f'{self.__class__.__name__}({convert(self.position)})'

    def __hash__(self):
        return hash((self.position, self.representation))

    def update(self):
        pass

    def increase_search_depth(self, search_depth):
        return search_depth

    def compute_valid_moves(self, board) -> List[Move]:
        """Returns a list of squares that the piece can move to or capture at"""
        return [pos for move in self.moves for pos in move.compute_valid_moves(board, self)]

    def move_to(self, position, log=True) -> None:
        """Moves the piece to the specified position and adds it to the position history"""
        #pylint: disable=logging-fstring-interpolation
        pos_old = convert(self.position)
        self.position = position
        self.position_history.append(position)
        if log:
            global TURN_COUNTER #pylint: disable=global-statement
            TURN_COUNTER += 0.5
            logger = logging.getLogger('game.log')
            move_ = f'{self.representation} from {pos_old} to {convert(position)}'
            logger.info(f'Turn {math.ceil(TURN_COUNTER)}: Team {self.team}: {move_}')

    def can_capture_at(self, board, position) -> bool:
        """Returns true if this piece can move to the specified position.
        Note: doesnt check if piece is from opposite team.
        """
        return position in (move.position for move in self.compute_valid_moves(board))

class Pawn(Piece):
    """Pawn class. Contains all the pawn moves"""

    def __init__(self, direction, position, representation):
        self._unpromoted_moves = [move.InitialPawnMove(direction),
                 move.PawnMove(direction),
                 move.PawnCapture(direction)]
        self._promoted_moves = [move.RookMove(), move.BishopMove()]
        self.promoted = False
        self.direction = direction
        super().__init__(self._unpromoted_moves, position, representation)

    def update(self, board):
        self._update_promotion(board)

    def compute_valid_moves(self, board) -> List[Move]:
        """Returns a list of squares that the piece can move to or capture at"""
        self._update_promotion(board)
        return super().compute_valid_moves(board)

    def can_capture_at(self, board, position) -> bool:
        """Returns true if this piece can move to the specified position"""
        #optimization: return False if more than one square away
        if not self.promoted and abs(position[1] - self.position[1]) > 1:
            return False
        return super().can_capture_at(board, position)

    def _update_promotion(self, board):
        target_y = 0 if self.direction == -1 else board.size - 1
        if target_y in (y for _, y in self.position_history + [self.position]):
            self.promoted = True
            self.moves = self._promoted_moves
        else:
            self.promoted = False
            self.moves = self._unpromoted_moves

    @property
    def representation(self):
        return f'{QUEEN}{self.team}' if self.promoted else f'{PAWN}{self.team}'

    @representation.setter
    def representation(self, value):
        pass

class Knight(Piece):
    """Knight class. Contains all the knight moves"""

    def __init__(self, _, position, representation):
        moves = [move.KnightMove()]
        super().__init__(moves, position, representation)

    def can_capture_at(self, board, position) -> bool:
        """Returns true if this piece can move to the specified position"""
        x1, y1 = position
        x2, y2 = self.position
        #optimization: return False if not L-shaped 2 and 1 squares away
        if {abs(x1 - x2), abs(y1 - y2) > 1} != {1, 2}:
            return False
        return super().can_capture_at(board, position)

class Bishop(Piece):
    """Bishop class. Contains all the bishop moves"""

    def __init__(self, _, position, representation):
        moves = [move.BishopMove()]
        super().__init__(moves, position, representation)

    def can_capture_at(self, board, position) -> bool:
        """Returns true if this piece can move to the specified position"""
        #optimization: return False if not on same diagonal
        if not is_diagonal(position, self.position):
            return False
        return super().can_capture_at(board, position)

class Rook(Piece):
    """Rook class. Contains all the rook moves"""

    def __init__(self, _, position, representation):
        moves = [move.RookMove()]
        super().__init__(moves, position, representation)

    def can_capture_at(self, board, position) -> bool:
        """Returns true if this piece can move to the specified position"""
        #optimization: return False if not horizontally or vertically aligned
        if not is_straight(position, self.position):
            return False
        return super().can_capture_at(board, position)

class Queen(Piece):
    """Queen class. Contains all the queen moves"""

    def __init__(self, _, position, representation):
        moves = [move.RookMove(), move.BishopMove()]
        self.depth_counter = 3
        super().__init__(moves, position, representation)

    def increase_search_depth(self, search_depth):
        if self.depth_counter <= 0:
            return search_depth
        self.depth_counter -= 1
        return search_depth + 2

    def can_capture_at(self, board, position) -> bool:
        """Returns true if this piece can move to the specified position"""
        #optimization: return False if not horizontally or vertically aligned
        #and not same diagonal
        if (not is_straight(position, self.position)
            and not is_diagonal(position, self.position)):
            return False
        return super().can_capture_at(board, position)

class King(Piece):
    """King class. Contains all the king moves"""

    def __init__(self, _, position, representation):
        moves = [move.KingMove()]
        super().__init__(moves, position, representation)

    def can_capture_at(self, board, position) -> bool:
        """Returns true if this piece can move to the specified position"""
        x1, y1 = position
        x2, y2 = self.position
        #optimization: return False if more than one square away
        if abs(x1 - x2) > 1 or abs(y1 - y2) > 1:
            return False
        return super().can_capture_at(board, position)

PIECES = {PAWN: Pawn,
          KNIGHT: Knight,
          BISHOP: Bishop,
          ROOK: Rook,
          QUEEN: Queen,
          KING: King}
