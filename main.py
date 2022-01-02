# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:36:04 2021

@author: Korean_Crimson
"""
import random
from typing import Dict
from typing import List

from chess_engine.board import Board
from chess_engine.consts import BLACK
from chess_engine.consts import BOARD
from chess_engine.consts import DIRECTIONS
from chess_engine.consts import WHITE
from chess_engine.piece import Piece
from chess_engine.piece import PIECES

def init_pieces() -> Dict[int, List[Piece]]:
    """Initialises white and black pieces and returns them in a dict"""
    #pylint: disable=invalid-name
    pieces = {WHITE: [], BLACK: []}
    for y, row in enumerate(BOARD):
        for x, square in enumerate(row):
            if square is not None:
                piece_type, team = square
                piece_class = PIECES[piece_type]
                direction = DIRECTIONS[team]
                new_piece = piece_class(direction, position=(x, y), representation=square)
                pieces[team].append(new_piece)
    return pieces

def main():
    """Main function"""

    pieces = init_pieces()
    board = Board(pieces[WHITE] + pieces[BLACK], size=8)

    for _ in range(15):
        for team in [WHITE, BLACK]:
            squares = [(piece, s) for piece in pieces[team]
                       for s in piece.compute_valid_moves(board)]
            piece, position = random.choice(squares)

            if not board.is_empty_at(position):
                enemy = BLACK if team is WHITE else WHITE
                if board[position] in pieces[enemy]:
                    board.capture_at(position)
                    pieces[enemy] = [piece_ for piece_ in pieces[enemy] if not piece_.captured]
            board.move_piece(piece, position)
            print(board)

if __name__ == '__main__':
    main()
