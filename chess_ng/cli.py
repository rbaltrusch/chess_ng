"""Cli module"""

import argparse

from chess_ng.consts import BLACK, STARTING_FEN, WHITE


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("chess_ng", description="A Python chess engine")
    parser.add_argument(
        "--depth", "-d", type=int, default=3, help="The minimax depth to use"
    )
    parser.add_argument(
        "--mode", "-m", choices=["cli", "auto"], default="cli", help="The player mode"
    )
    parser.add_argument(
        "--player",
        "-p",
        choices=[WHITE, BLACK],
        default=WHITE,
        help="The player colour",
    )
    parser.add_argument(
        "--fen",
        "-f",
        default=STARTING_FEN,
        help="The FEN string with which to initialise the game",
    )
    parser.add_argument(
        "--eval-algorithm",
        "-e",
        choices=["moves", "move-distance"],
        help="The evaluation algorithm to use in minimax",
    )
    parser.add_argument(
        "--resign-threshold",
        "-r",
        type=int,
        default=-50,
        help="The position rating at which to surrender",
    )
    parser.add_argument(
        "--max-moves",
        "--max",
        type=int,
        default=None,
        help="The maximum amount of moves to play",
    )
    parser.add_argument(
        "--seed", "-s", default=None, type=int, help="The random seed to be used"
    )
    parser.add_argument(
        "--log-folder", default="logs", help="The folder to which logfiles are written"
    )
    parser.add_argument(
        "--log-filename-suffix", default="game.log", help="The name suffix for logfiles"
    )
    parser.add_argument(
        "--disable-logs",
        action="store_true",
        help="Disables log files from being written",
    )
    return parser
