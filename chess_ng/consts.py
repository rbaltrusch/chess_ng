# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 12:43:27 2021

@author: Korean_Crimson
"""

PAWN = 'o'
KNIGHT = 'N'
BISHOP = 'B'
ROOK = 'R'
QUEEN = 'Q'
KING = 'K'

WHITE = '1'
BLACK = '2'

BACKROW = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK]
FRONTROW = [PAWN] * 8

BOARD = [[piece + BLACK for piece in BACKROW],
         [piece + BLACK for piece in FRONTROW],
         [None] * 8,
         [None] * 8,
         [None] * 8,
         [None] * 8,
         [piece + WHITE for piece in FRONTROW],
         [piece + WHITE for piece in BACKROW]
         ]

DIRECTIONS = {WHITE: -1, BLACK: 1}
EARLY_VALUES = {PAWN: 4, KNIGHT: 5, BISHOP: 4, ROOK: 1, QUEEN: 3, KING: 2}
MID_VALUES = {PAWN: 2, KNIGHT: 3, BISHOP: 3, ROOK: 4, QUEEN: 6, KING: 10}
LATE_VALUES = {PAWN: 1, KNIGHT: 3, BISHOP: 4, ROOK: 5, QUEEN: 9, KING: 10}
