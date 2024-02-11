# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:36:04 2021

@author: Korean_Crimson
"""
import logging
import random
import time
from typing import Callable

from chess_ng.algorithm import mating_strategy
from chess_ng.board import Board
from chess_ng.consts import BLACK, LATE_VALUES, MID_VALUES, WHITE
from chess_ng.game import ChessPositionError, Game, GameParams
from chess_ng.output import Logger


def move_player_automatically(game: Game, params: GameParams) -> None:
    """Moves the player automatically using minimax"""
    game.player = BLACK if game.side_to_move == WHITE else WHITE
    game.run_team(params)
    game.player = BLACK if game.side_to_move == WHITE else WHITE


def move_player_by_cli(game: Game, _: GameParams) -> None:
    """Moves the player using input from stdin"""
    while True:
        try:
            source_square, dest_square = input(
                "Input a source square to move from "
                "and a destination square to move to (e.g. 'e2 e4'): "
            ).split()
            game.run_player(source_square, dest_square)
            return
        except ValueError:
            print("Invalid input: must contain two squares, separated by a space.")
        except ChessPositionError as exc:
            print(f"Invalid input: {exc.message}")


# pylint: disable=too-many-arguments,too-many-locals,too-many-branches
def run_game(
    game: Game,
    params: GameParams,
    player_move_source: Callable[[Game, GameParams], None],
    renderer: Callable[[Board], None],
    logger: logging.Logger,
    moves: int = 50,
):
    """Chess game function"""
    logger.info(f"Depth: {params.depth}")
    for i in range(moves):
        if i > 15:
            for team in game.teams.values():
                team.sort_pieces(MID_VALUES)
        elif i > 30:
            for team in game.teams.values():
                team.sort_pieces(LATE_VALUES)

        initial_time = time.time()
        if game.side_to_move == game.player:
            player_move_source(game, params)
        else:
            game.run_team(params)

        if game.rating > params.mating_threshold:
            game.minimax.evaluation_function = mating_strategy
        for message in game.consume_messages():
            logger.info(message)

        logger.info(f"Time taken for turn: {round(time.time() - initial_time, 1)}s")
        renderer(game.board)
        if game.is_over:
            break

    logger.info("Finished")


def main():
    """Main function"""
    seed = 0
    random.seed(seed)
    with Logger(folder="logs", filename="game.log") as logger:
        logger.info("Seed: %s", seed)
        run_game(
            Game.create_default(),
            GameParams(depth=3),
            player_move_source=move_player_by_cli,
            renderer=print,
            logger=logger,
            moves=50,
        )


if __name__ == "__main__":
    main()
