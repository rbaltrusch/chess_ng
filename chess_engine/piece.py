# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:33:57 2021

@author: Korean_Crimson
"""
import logging
import math
from typing import List
from typing import Tuple

from chess_engine import move
from chess_engine.consts import BISHOP
from chess_engine.consts import KING
from chess_engine.consts import KNIGHT
from chess_engine.consts import PAWN
from chess_engine.consts import QUEEN
from chess_engine.consts import ROOK
from chess_engine.util import convert
from chess_engine.util import convert_str

TURN_COUNTER = 0.0

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

    def compute_valid_moves(self, board) -> List[Tuple[int, int]]:
        """Returns a list of squares that the piece can move to or capture at"""
        return list({pos for move in self.moves for pos in move.compute_valid_moves(board, self)})

    def move_to(self, position, log=True) -> None:
        """Moves the piece to the specified position and adds it to the position history"""
        pos_old = convert(self.position)
        self.position = position
        self.position_history.append(position)
        if log:
            global TURN_COUNTER
            TURN_COUNTER += 0.5
            logger = logging.getLogger('game.log')
            logger.info(f'Turn {math.ceil(TURN_COUNTER)}: Team {self.team}: {self.representation} from {pos_old} to {convert(position)}')

    def can_capture_at(self, board, position) -> bool:
        """Returns true if this piece can move to the specified position.
        Note: doesnt check if piece is from opposite team.
        """
        return position in self.compute_valid_moves(board)

class Pawn(Piece):
    """Pawn class. Contains all the pawn moves"""

    def __init__(self, direction, position, representation):
        moves = [move.InitialPawnMove(direction),
                 move.PawnMove(direction),
                 move.PawnCapture(direction)]
        super().__init__(moves, position, representation)

    def can_capture_at(self, board, position) -> bool:
        """Returns true if this piece can move to the specified position"""
        #optimization: return False if more than one square away
        if abs(position[1] - self.position[1]) > 1:
            return False
        return super().can_capture_at(board, position)

class Knight(Piece):
    """Knight class. Contains all the knight moves"""

    def __init__(self, _, position, representation):
        moves = [move.KnightMove()]
        super().__init__(moves, position, representation)

class Bishop(Piece):
    """Bishop class. Contains all the bishop moves"""

    def __init__(self, _, position, representation):
        moves = [move.BishopMove()]
        super().__init__(moves, position, representation)

class Rook(Piece):
    """Rook class. Contains all the rook moves"""

    def __init__(self, _, position, representation):
        moves = [move.RookMove()]
        super().__init__(moves, position, representation)

class Queen(Piece):
    """Queen class. Contains all the queen moves"""

    def __init__(self, _, position, representation):
        moves = [move.RookMove(), move.BishopMove()]
        super().__init__(moves, position, representation)

class King(Piece):
    """King class. Contains all the king moves"""

    def __init__(self, _, position, representation):
        moves = [move.KingMove()]
        super().__init__(moves, position, representation)

PIECES = {PAWN: Pawn,
          KNIGHT: Knight,
          BISHOP: Bishop,
          ROOK: Rook,
          QUEEN: Queen,
          KING: King}
