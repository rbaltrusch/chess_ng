# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:36:04 2021

@author: Korean_Crimson
"""
import math
from typing import Tuple

from chess_engine.algorithm import minimax
from chess_engine.board import Board
from chess_engine.consts import BLACK
from chess_engine.consts import BOARD
from chess_engine.consts import DIRECTIONS
from chess_engine.consts import WHITE
from chess_engine.piece import PIECES
from chess_engine.team import Team

def init_pieces() -> Tuple[Team, Team]:
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
    return Team(pieces[WHITE]), Team(pieces[BLACK])

def main():
    """Main function"""
    teams = init_pieces()
    board = Board([piece for team in teams for piece in team], size=8)

    for _ in range(50):
        for team, enemy in [teams, teams[::-1]]:
            is_in_check = team.in_check(board, enemy.pieces)
            moves = team.compute_valid_moves(board, enemy.pieces)

            if not moves:
                if is_in_check:
                    print(f'Checkmated team {team}. Team {enemy} wins.')
                else:
                    print('Stalemate. Teams draw.')
                return

            if is_in_check:
                print('Moving out of check.')

            rating, (piece, position) = minimax(
                board, team, enemy, depth=4,
                alpha=-math.inf, beta=math.inf, maximizing_player=True
            )
            print(f'Rating: {rating}')
            board.move_piece_and_capture(position, piece, enemy.pieces)

            if enemy.in_check(board, team.pieces):
                print('Checking enemy king')

            print(board)

if __name__ == '__main__':
    main()
