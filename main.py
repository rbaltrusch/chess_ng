# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:36:04 2021

@author: Korean_Crimson
"""

import random

from chess_engine.board import Board
from chess_engine.piece import PIECES
from chess_engine.consts import BOARD, EMPTY, DIRECTIONS, WHITE, BLACK

board = Board(BOARD)
pieces = {WHITE: [], BLACK: []}

for y, row in enumerate(board):
    for x, square in enumerate(row):
        if square != EMPTY:
            piece_type, team = square
            piece_class = PIECES[piece_type]
            direction = DIRECTIONS[team]
            new_piece = piece_class(direction, position=(x, y), representation=square)
            pieces[team].append(new_piece)

for _ in range(150):
    for team in [WHITE, BLACK]:
        all_valid_squares = []
        for piece_ in pieces[team]:
            valid_squares = piece_.compute_valid_moves(board)
            for valid_square in valid_squares:
                all_valid_squares.append((piece_, valid_square))
        
        piece_, position = random.choice(all_valid_squares)
        piece_.move_to(position)

        if not board.is_empty_at(position):
            enemy = WHITE if team is not WHITE else BLACK
            board.capture_at(pieces[enemy], position)
            pieces[enemy] = [piece_ for piece_ in pieces[enemy] if not piece_.captured]

        board.update(pieces)
        
        # print(board)
