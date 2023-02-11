# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 14:33:33 2022

@author: richa
"""
import math
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Protocol, Tuple, Union

import numpy as np

from chess_ng.board import BitBoard, Board
from chess_ng.hashing import compute_hash
from chess_ng.interfaces import Piece
from chess_ng.move import Move
from chess_ng.piece import King

Number = Union[int, float]


class _TeamInterface(Protocol):

    king: King
    pieces: List[Piece]

    def compute_all_moves(  # pylint: disable=missing-function-docstring
        self, board: Board
    ) -> List[Tuple[Piece, Move]]:
        ...

    def compute_valid_moves(  # pylint: disable=missing-function-docstring
        self, board: Board, enemy_pieces: List[Piece]
    ) -> List[Tuple[Piece, Move]]:
        ...


@dataclass
class ReversibleMove:
    """Context manager move that reverses board state to initial state on exit"""

    board: Board
    piece: Piece
    position: Tuple[int, int]
    enemy_pieces: List[Piece]

    def __post_init__(self):
        self.original_position: Tuple[int, int] = None  # type: ignore
        self.captured_piece: Optional[Piece] = None
        self._original_bit_representation: int = 0

    def __enter__(self):
        self.original_position = self.piece.position

        if isinstance(self.board, BitBoard):
            self._original_bit_representation = self.board.bit_representation
            if not self.board.is_empty_at(self.position) and self.board.is_enemy(
                self.position, self.piece.team
            ):
                index, self.captured_piece = [
                    (i, x)
                    for i, x in enumerate(self.enemy_pieces)
                    if x.position == self.position
                ][0]
                self.enemy_pieces.pop(index)
            self.board[self.position] = self.piece
            self.piece.position = self.position
            self.board[self.original_position] = None
            return self

        self.captured_piece = self.board.move_piece_and_capture(
            self.position, self.piece, self.enemy_pieces, log=False
        )
        return self

    def __exit__(self, *_):
        if isinstance(self.board, BitBoard):
            self.piece.position = self.original_position
            self.piece.update(self.board)
            self.board.bit_representation = self._original_bit_representation
            if self.captured_piece is not None:
                self.captured_piece.captured = False
                self.enemy_pieces.append(self.captured_piece)
            return

        # undo move
        self.board.move_piece_and_capture(
            self.original_position, self.piece, self.enemy_pieces, log=False
        )
        self.piece.position_history.pop()
        self.piece.position_history.pop()
        self.piece.update(self.board)
        self.board[self.position] = self.captured_piece
        self.board.move_history.pop()
        self.board.move_history.pop()
        if self.captured_piece is not None:
            self.captured_piece.captured = False
            self.enemy_pieces.append(self.captured_piece)


def evaluate_length(board: Board, team: _TeamInterface, enemy: _TeamInterface):
    """Evaluates the board state based on the amount of moves allied pieces
    and enemy pieces can make.
    """
    # HACK: using compute_all_moves instead of compute_valid_moves to save computation time
    return len(team.compute_all_moves(board)) - len(enemy.compute_all_moves(board))


def evaluate_length_with_captures(
    board: Board, team: _TeamInterface, enemy: _TeamInterface
):
    """Evaluates the board state based on the amount of moves allied pieces
    and enemy pieces can make.
    """
    # HACK: using compute_all_moves instead of compute_valid_moves to save computation time
    ally_moves = sum(
        2 if move.can_capture else 1 for _, move in team.compute_all_moves(board)
    )
    enemy_moves = sum(
        3 if move.can_capture else 1 for _, move in enemy.compute_all_moves(board)
    )
    return (ally_moves - 1) / enemy_moves if enemy_moves else math.inf


def mating_strategy(board: Board, team: _TeamInterface, enemy: _TeamInterface):
    """Incentivizes disabling the enemy kings movements while keeping own movement high"""
    return len(team.compute_valid_moves(board, enemy.pieces)) - len(
        enemy.king.compute_valid_moves(board)
    )


def evaluate_distance(board: Board, team: _TeamInterface, enemy: _TeamInterface):
    """Evaluates board state based on the closeness to the enemy king"""
    # HACK: using compute_all_moves instead of compute_valid_moves to save computation time
    # pylint: disable=invalid-name
    def inverse_distance(point1: Tuple[int, int], point2: Tuple[int, int]):
        x1, y1 = point1
        x2, y2 = point2
        value = math.sqrt((x1 - x2) ** 2 + abs(y1 - y2) ** 2)
        if value == 0:
            return 1
        return 1 / value

    sum_ally = sum(
        inverse_distance(enemy.king.position, move.position)
        for _, move in team.compute_all_moves(board)
    )
    sum_enemy = sum(
        inverse_distance(team.king.position, move.position)
        for _, move in enemy.compute_all_moves(board)
    )
    return sum_ally - sum_enemy


def evaluate_distance_np(
    board: Board, team: _TeamInterface, enemy: _TeamInterface
) -> float:
    """Evaluates board state based on the closeness to the enemy king"""
    # seems to lead to very wonky games...
    ally_moves = np.array([move.position for _, move in team.compute_all_moves(board)])  # type: ignore #pylint: disable=line-too-long
    enemy_moves = np.array(  # type: ignore
        [move.position for _, move in enemy.compute_all_moves(board)]
    )
    king_position = np.array([team.king.position])  # type: ignore
    enemy_king_position = np.array([enemy.king.position])  # type: ignore
    ally_distances: float = np.linalg.norm(enemy_king_position - ally_moves)  # type: ignore
    enemy_distances: float = np.linalg.norm(king_position - enemy_moves)  # type: ignore
    return enemy_distances - ally_distances


@dataclass
class Minimax:
    """Minimax algorithm class with alpha-beta pruning and customizable evaluation"""

    evaluation_function: Callable[[Board, _TeamInterface, _TeamInterface], float]
    hash_values: Dict[str, int]

    def __post_init__(self):
        self.board_hashes: Dict[int, Number] = {}

    # pylint: disable=too-many-arguments,too-many-locals,too-many-branches #for now...
    def run(
        self,
        board: Board,
        team: _TeamInterface,
        enemy: _TeamInterface,
        depth: int,
        maximizing_player: bool,
        alpha: Number = -math.inf,
        beta: Number = math.inf,
    ) -> Tuple[Number, Optional[Tuple[Piece, Move]]]:
        """Minimax algorithm with alpha-beta pruning.
        At depth=3, computation speed is still relatively fast.
        At depth=4, it slows down considerably, but does make much better moves.
        """

        if board.is_draw_by_repetition():
            return 0, None

        if depth == 0:  # or game over
            evaluation = self.evaluation_function(board, team, enemy)
            hash_ = compute_hash(board, self.hash_values)
            self.board_hashes[hash_] = evaluation
            return evaluation, None

        if maximizing_player:
            best_move = None
            for piece, move in team.compute_valid_moves(board, enemy.pieces):
                with ReversibleMove(board, piece, move.position, enemy.pieces):
                    hash_ = compute_hash(board, self.hash_values)
                    eval_position = self.board_hashes.get(
                        hash_,
                        self.run(board, team, enemy, depth - 1, False, alpha, beta)[0],
                    )

                if eval_position > alpha:
                    best_move = (piece, move)
                alpha = max(alpha, eval_position)
                if eval_position >= beta or beta <= alpha:
                    break
            return alpha, best_move

        min_move = None
        for piece, move in enemy.compute_valid_moves(board, team.pieces):
            with ReversibleMove(board, piece, move.position, team.pieces):
                hash_ = compute_hash(board, self.hash_values)
                eval_position = self.board_hashes.get(
                    hash_,
                    self.run(board, team, enemy, depth - 1, True, alpha, beta)[0],
                )

            if eval_position < beta:
                min_move = (piece, move)
            beta = min(beta, eval_position)
            if eval_position <= alpha or beta <= alpha:
                break

        return beta, min_move
