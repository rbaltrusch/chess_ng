# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:36:04 2021

@author: Korean_Crimson
"""
import math
import random
import time
from typing import Tuple

from chess_engine.algorithm import evaluate_distance
from chess_engine.algorithm import minimax
from chess_engine.board import Board
from chess_engine.consts import BLACK
from chess_engine.consts import BOARD
from chess_engine.consts import DIRECTIONS
from chess_engine.consts import WHITE
from chess_engine.output import Logger
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
    return Team(pieces[WHITE], WHITE), Team(pieces[BLACK], BLACK)

#pylint: disable=too-many-arguments
def game(board, teams, logger, depth=2, moves=50, resign_threshold=-50):
    """Chess game function"""
    logger.info(f'Depth: {depth}')
    for _ in range(moves):
        for team, enemy in [teams, teams[::-1]]:
            initial_time = time.time()
            is_in_check = team.in_check(board, enemy.pieces)
            moves = team.compute_valid_moves(board, enemy.pieces)

            if not moves:
                if is_in_check:
                    logger.info(f'Checkmated team {team}. Team {enemy} wins.')
                else:
                    logger.info('Stalemate. Teams draw.')
                return

            if board.is_draw_by_repetition():
                logger.info('Draw by repetition.')
                return

            if is_in_check:
                logger.info('Moving out of check.')

            rating, (piece, move) = minimax(
                board, team, enemy, depth=depth,
                alpha=-math.inf, beta=math.inf,
                evaluation_function=evaluate_distance,
                maximizing_player=True
            )
            print(f'Rating: {rating}')
            if rating < resign_threshold:
                logger.info(f'Team {team} resigned. Team {enemy} wins.')
                return
            board.move_piece_and_capture(move.position, piece, enemy.pieces)

            if enemy.in_check(board, team.pieces):
                logger.info('Checking enemy king')

            print(f'Time taken for turn: {round(time.time() - initial_time, 1)}s')
            print(board)

    print('Finished')
    logger.info(board)

def main():
    """Main function"""
    seed = 0
    random.seed(seed)
    teams = init_pieces()
    board = Board([piece for team in teams for piece in team], size=8)
    with Logger(folder='logs', filename='game.log') as logger:
        logger.info('Seed: %s', seed)
        game(board, teams, logger, depth=4, moves=150, resign_threshold=-50)

if __name__ == '__main__':
    main()
