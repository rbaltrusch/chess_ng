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
from chess_engine.piece import King
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

def get_valid_squares(board, pieces):
    """Returns all valid moves for all pieces passed in"""
    return [(piece, s) for piece in pieces for s in piece.compute_valid_moves(board)]

def move_piece(board, position, piece, enemy_pieces, log=True):
    """Moves piece to position on the board. Captures enemy if there is one"""
    captured_piece = None
    if not board.is_empty_at(position):
        if board[position] in enemy_pieces:
            captured_piece = board.capture_at(position, log=log)
            enemy_pieces.remove(captured_piece)
    board.move_piece(piece, position, log=log)
    return captured_piece

def filter_king_check_moves(board, moves, king, enemy_pieces):
    """Returns moves not resulting in a check of the allied king"""
    valid_moves = []
    for piece, position in moves:
        original_position = piece.position
        captured_piece = move_piece(board, position, piece, enemy_pieces, log=False)

        if not in_check(board, king, enemy_pieces):
            valid_moves.append((piece, position))

        #undo move
        move_piece(board, original_position, piece, enemy_pieces, log=False)
        board[position] = captured_piece
        if captured_piece is not None:
            captured_piece.captured = False
            enemy_pieces.append(captured_piece)
    return valid_moves

def in_check(board, king, enemy_pieces) -> bool:
    """Returns True if any enemy pieces can capture at the specified position"""
    return any(x.can_move_to(board, king.position) for x in enemy_pieces)

def main():
    """Main function"""

    pieces = init_pieces()
    board = Board(pieces[WHITE] + pieces[BLACK], size=8)

    for _ in range(100):
        for team in [WHITE, BLACK]:
            king = [x for x in pieces[team] if isinstance(x, King)][0]
            enemy = BLACK if team is WHITE else WHITE
            enemy_pieces = pieces[enemy]
            is_in_check = in_check(board, king, enemy_pieces)

            moves = get_valid_squares(board, pieces[team])
            valid_moves = filter_king_check_moves(board, moves, king, enemy_pieces)

            if not valid_moves:
                if is_in_check:
                    print(f'Checkmated team {team}. Team {enemy} wins.')
                else:
                    print('Stalemate. Teams draw.')
                return

            if is_in_check:
                print('Moving out of check.')

            piece, position = random.choice(valid_moves)
            move_piece(board, position, piece, enemy_pieces)

            #check if checking enemy king
            enemy_king = [x for x in enemy_pieces if isinstance(x, King)][0]
            if in_check(board, enemy_king, pieces[team]):
                print('Checking enemy king')

            print(board)

if __name__ == '__main__':
    main()
