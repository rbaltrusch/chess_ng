# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:36:04 2021

@author: Korean_Crimson
"""
import itertools
import random
import time
from typing import Any, Callable, Optional

from chess_ng import hashing, output
from chess_ng.algorithm import (
    Minimax,
    evaluate_distance,
    evaluate_length,
    mating_strategy,
)
from chess_ng.board import Board
from chess_ng.cli import create_parser
from chess_ng.consts import BLACK, LATE_VALUES, MID_VALUES, WHITE
from chess_ng.fen import load_fen_notation
from chess_ng.game import ChessPositionError, Game, GameParams


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


def init_game(args: Any) -> Game:
    """Initialises a game from CLI args"""
    evaluation = (
        evaluate_length
        if args.eval_algorithm == "moves"  # type: ignore
        else evaluate_distance
    )
    teams, _ = load_fen_notation(args.fen)  # type: ignore
    hash_values = hashing.get_hash_values(
        [x for team in teams.values() for x in team.pieces]
    )
    return Game(teams, Minimax(evaluation, hash_values), player=args.player)  # type: ignore


# pylint: disable=too-many-arguments
def run_game(
    game: Game,
    params: GameParams,
    player_move_source: Callable[[Game, GameParams], None],
    renderer: Callable[[Board], None],
    logger: output.LoggerProtocol,
    moves: Optional[int] = 50,
):
    """Chess game function"""
    logger.info(f"Depth: {params.depth}")
    iterable = range(moves) if isinstance(moves, int) else itertools.count()
    for i in iterable:
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
    parser = create_parser()
    args = parser.parse_args()
    random.seed(args.seed)
    _output_logger = (
        output.NoLogger()
        if args.disable_logs
        else output.Logger(folder=args.log_folder, filename=args.log_filename_suffix)
    )
    with _output_logger as logger:
        logger.info("Seed: %s", args.seed)
        run_game(
            init_game(args),
            GameParams(depth=args.depth, resign_threshold=args.resign_threshold),
            player_move_source=(
                move_player_by_cli if args.mode == "cli" else move_player_automatically
            ),
            renderer=print,
            logger=logger,
            moves=args.max_moves,
        )


if __name__ == "__main__":
    main()
