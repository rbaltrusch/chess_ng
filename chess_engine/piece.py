# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:33:57 2021

@author: Korean_Crimson
"""

from chess_engine import move
from chess_engine.util import convert
from chess_engine.consts import PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING
from chess_engine.move import InitialPawnMove

class Piece:
    def __init__(self, moves, position, representation):
        self.moves = moves
        self.position = position
        self.representation = representation
        self.team = representation[-1]
        self.captured = False
        self.position_history = []

    def __repr__(self):
        return f'{self.__class__.__name__}{self.position}'

    def compute_valid_moves(self, board):
        valid_squares = []
        for move_ in self.moves:
            valid_squares_ = move_.compute_valid_moves(self.position, board, self.team)
            valid_squares.extend(valid_squares_)
        return list(set(valid_squares))

    def move_to(self, position):
        print(f'{self.representation} from {convert(self.position)} to {convert(position)}')
        self.position = position
        self.position_history.append(position)

class Pawn(Piece):
    def __init__(self, direction, position, representation):
        moves = [move.InitialPawnMove(direction), move.PawnMove(direction), move.PawnCapture(direction)]
        super().__init__(moves, position, representation)

    def move_to(self, position):
        super().move_to(position)
        if len(self.position_history) == 1:
            self.moves = [move_ for move_ in self.moves if not isinstance(move_, InitialPawnMove)]

class Knight(Piece):
    def __init__(self, direction, position, representation):
        moves = []
        super().__init__(moves, position, representation)

class Bishop(Piece):
    def __init__(self, direction, position, representation):
        moves = [move.BishopMove(8)]
        super().__init__(moves, position, representation)

class Rook(Piece):
    def __init__(self, direction, position, representation):
        moves = [move.RookMove()]
        super().__init__(moves, position, representation)

class Queen(Piece):
    def __init__(self, direction, position, representation):
        moves = [move.RookMove(), move.BishopMove(8)]
        super().__init__(moves, position, representation)

class King(Queen):
    def __init__(self, direction, position, representation):
        super().__init__(direction, position, representation)
        for move_ in self.moves:
            move_.range = 1

PIECES = {PAWN: Pawn,
          KNIGHT: Knight,
          BISHOP: Bishop,
          ROOK: Rook,
          QUEEN: Queen,
          KING: King}
