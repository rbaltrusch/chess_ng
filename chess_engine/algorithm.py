# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 14:33:33 2022

@author: richa
"""
import math
from dataclasses import dataclass
from typing import Callable
from typing import List
from typing import Tuple

import numpy as np

from .board import Board
from .piece import Piece


@dataclass
class ReversibleMove:
    """Context manager move that reverses board state to initial state on exit"""

    board: Board
    piece: Piece
    position: Tuple[int, int]
    enemy_pieces: List[Piece]

    def __post_init__(self):
        self.original_position = None
        self.captured_piece = None

    def __enter__(self):
        self.original_position = self.piece.position
        self.captured_piece = self.board.move_piece_and_capture(
            self.position, self.piece, self.enemy_pieces, log=False
        )
        return self

    def __exit__(self, *_):
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


def evaluate_length(board, team, enemy):
    """Evaluates the board state based on the amount of moves allied pieces
    and enemy pieces can make.
    """
    #HACK: using compute_all_moves instead of compute_valid_moves to save computation time
    return len(team.compute_all_moves(board)) - len(enemy.compute_all_moves(board))

def evaluate_length_with_captures(board, team, enemy):
    """Evaluates the board state based on the amount of moves allied pieces
    and enemy pieces can make.
    """
    #HACK: using compute_all_moves instead of compute_valid_moves to save computation time
    ally_moves = sum([2 if move.can_capture else 1 for _, move in team.compute_all_moves(board)])
    enemy_moves = sum([3 if move.can_capture else 1 for _, move in enemy.compute_all_moves(board)])
    return (ally_moves - 1) / enemy_moves if enemy_moves else math.inf

def evaluate_distance(board, team, enemy):
    """Evaluates board state based on the closeness to the enemy king"""
    #HACK: using compute_all_moves instead of compute_valid_moves to save computation time
    #pylint: disable=invalid-name
    def inverse_distance(point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        value = math.sqrt((x1 - x2) ** 2 + abs(y1 - y2) ** 2)
        if value == 0:
            return 1
        return 1 / value
    sum_ally = sum(inverse_distance(enemy.king.position, move.position)
                   for _, move in team.compute_all_moves(board))
    sum_enemy = sum(inverse_distance(team.king.position, move.position)
                    for _, move in enemy.compute_all_moves(board))
    return sum_ally - sum_enemy

def evaluate_distance_np(board, team, enemy):
    """Evaluates board state based on the closeness to the enemy king"""
    #seems to lead to very wonky games...
    ally_moves = np.array([move.position for _, move in team.compute_all_moves(board)])
    enemy_moves = np.array([move.position for _, move in enemy.compute_all_moves(board)])
    king_position = np.array([team.king.position])
    enemy_king_position = np.array([enemy.king.position])
    ally_distances = np.linalg.norm(enemy_king_position - ally_moves)
    enemy_distances = np.linalg.norm(king_position - enemy_moves)
    return enemy_distances - ally_distances

@dataclass
class Minimax:
    """Minimax algorithm class with alpha-beta pruning and customizable evaluation"""

    evaluation_function: Callable

    #pylint: disable=too-many-arguments,too-many-locals #for now...
    def run(self, board, team, enemy, depth, alpha, beta, maximizing_player):
        """Minimax algorithm with alpha-beta pruning.
        At depth=3, computation speed is still relatively fast.
        At depth=4, it slows down considerably, but does make much better moves.
        """
        if board.is_draw_by_repetition():
            return 0, None

        if depth == 0: #or game over
            return self.evaluation_function(board, team, enemy), None

        if maximizing_player:
            best_move = None
            max_eval = -math.inf
            for piece, move in team.compute_valid_moves(board, enemy.pieces):
                search_depth = depth - 1
                search_depth = piece.increase_search_depth(search_depth)
                with ReversibleMove(board, piece, move.position, enemy.pieces):
                    eval_position = self.run(board, team, enemy,
                                             search_depth, alpha, beta, False)[0]

                if eval_position > max_eval or best_move is None:
                    best_move = (piece, move)
                max_eval = max(max_eval, eval_position)
                alpha = max(alpha, eval_position)
                if eval_position >= beta:
                    break
                if beta <= alpha:
                    break
            return max_eval, best_move

        min_evaluation = math.inf
        min_move = None
        for piece, move in enemy.compute_valid_moves(board, team.pieces):
            search_depth = depth - 1
            search_depth = piece.increase_search_depth(search_depth)
            with ReversibleMove(board, piece, move.position, team.pieces):
                eval_position = self.run(board, team, enemy, search_depth, alpha, beta, True)[0]

            if eval_position < min_evaluation or min_move is None:
                min_move = (piece, move.position)
            min_evaluation = min(min_evaluation, eval_position)
            beta = min(beta, eval_position)
            if eval_position <= alpha:
                break
            if beta <= alpha:
                break

        return min_evaluation, min_move
