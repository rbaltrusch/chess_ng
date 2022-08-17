# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:36:04 2021

@author: Korean_Crimson
"""
import logging
import random
import time
from typing import Dict, List, Optional, Sequence, Tuple

from chess_ng import hashing
from chess_ng.algorithm import Minimax, evaluate_length, mating_strategy
from chess_ng.board import Board
from chess_ng.consts import BLACK, BOARD, DIRECTIONS, LATE_VALUES, MID_VALUES, WHITE
from chess_ng.output import Logger
from chess_ng.piece import PIECES, Piece
from chess_ng.team import Team


def init_pieces() -> Tuple[Team, Team]:
    """Initialises white and black pieces and returns them in a dict"""
    # pylint: disable=invalid-name
    pieces: Dict[str, List[Piece]] = {WHITE: [], BLACK: []}
    for y, row in enumerate(BOARD):
        square: Optional[str]
        for x, square in enumerate(row):
            if square is not None:
                piece_type, team = square
                piece_class = PIECES[piece_type]
                direction = DIRECTIONS[team]  # type: ignore
                new_piece = piece_class(
                    direction, position=(x, y), representation=square
                )
                pieces[team].append(new_piece)
    return Team(pieces[WHITE], WHITE), Team(pieces[BLACK], BLACK)


# pylint: disable=too-many-arguments,too-many-locals,too-many-branches
def game(
    board: Board,
    teams: Sequence[Team],
    hash_values: Dict[str, int],
    logger: logging.Logger,
    depth: int = 2,
    moves: int = 50,
    resign_threshold: int = -50,
    mating_threshold: int = 10,
):
    """Chess game function"""
    logger.info(f"Depth: {depth}")
    minimax = Minimax(evaluation_function=evaluate_length, hash_values=hash_values)
    for i in range(moves):
        if i > 15:
            for team in teams:
                team.sort_pieces(MID_VALUES)
        elif i > 30:
            for team in teams:
                team.sort_pieces(LATE_VALUES)

        for team, enemy in [teams, teams[::-1]]:
            initial_time = time.time()
            is_in_check = team.in_check(board, enemy.pieces)

            if not team.compute_valid_moves(board, enemy.pieces):
                if is_in_check:
                    logger.info(f"Checkmated team {team}. Team {enemy} wins.")
                else:
                    logger.info("Stalemate. Teams draw.")
                return

            if board.is_draw_by_repetition():
                logger.info("Draw by repetition.")
                return

            if is_in_check:
                logger.info("Moving out of check.")

            team.queen.depth_counter = 0
            enemy.queen.depth_counter = 0
            rating, move_result = minimax.run(
                board,
                team,
                enemy,
                depth=depth,
                maximizing_player=True,
            )

            if move_result is None:
                logger.info("No move found")
                return
            piece, move = move_result

            print(f"Rating: {rating}")
            if rating < resign_threshold:
                logger.info(f"Team {team} resigned. Team {enemy} wins.")
                return
            board.move_piece_and_capture(move.position, piece, enemy.pieces)

            if rating > mating_threshold:
                minimax.evaluation_function = mating_strategy
                logger.info("Mating activated")

            if enemy.in_check(board, team.pieces):
                logger.info("Checking enemy king")

            print(f"Time taken for turn: {round(time.time() - initial_time, 1)}s")
            print(board)

    print("Finished")
    logger.info(board)


def main():
    """Main function"""
    seed = 0
    random.seed(seed)
    teams = init_pieces()
    pieces = [piece for team in teams for piece in team.pieces]
    board = Board(pieces, size=8)
    hash_values = hashing.get_hash_values(pieces)

    with Logger(folder="logs", filename="game.log") as logger:
        logger.info("Seed: %s", seed)
        game(
            board,
            teams,
            hash_values,
            logger,
            depth=5,
            moves=10,
            resign_threshold=-50,
            mating_threshold=20,
        )


if __name__ == "__main__":
    main()
