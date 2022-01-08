# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 14:33:33 2022

@author: richa
"""
import math
from dataclasses import dataclass
from typing import List
from typing import Tuple

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
        self.board[self.position] = self.captured_piece
        if self.captured_piece is not None:
            self.captured_piece.captured = False
            self.enemy_pieces.append(self.captured_piece)


def evaluate(board, team, enemy):
    """Evaluates the board state based on the amount of moves allied pieces
    and enemy pieces can make.
    """
    #HACK: using compute_all_moves instead of compute_valid_moves to save computation time
    return len(team.compute_all_moves(board)) - len(enemy.compute_all_moves(board))

#pylint: disable=too-many-arguments,too-many-locals #for now...
def minimax(board, team, enemy, depth, alpha, beta, maximizing_player):
    """Minimax algorithm with alpha-beta pruning.
    At depth=3, computation speed is still relatively fast.
    At depth=4, it slows down considerably, but does make much better moves.
    """
    if depth == 0: #or game over
        return evaluate(board, team, enemy), None

    if maximizing_player:
        best_move = None
        max_eval = -math.inf
        for piece, position in team.compute_valid_moves(board, enemy.pieces):
            with ReversibleMove(board, piece, position, enemy.pieces):
                eval_position = minimax(board, team, enemy, depth-1, alpha, beta, False)[0]

            if eval_position > max_eval or best_move is None:
                best_move = (piece, position)
            max_eval = max(max_eval, eval_position)
            alpha = max(alpha, eval_position)
            if eval_position >= beta:
                break
            if beta <= alpha:
                break
        return max_eval, best_move

    min_evaluation = math.inf
    min_move = math.inf
    best_min_move = None
    for piece, position in enemy.compute_valid_moves(board, team.pieces):
        with ReversibleMove(board, piece, position, team.pieces):
            eval_position = minimax(board, team, enemy, depth-1, alpha, beta, True)[0]

        min_evaluation = min(min_evaluation, eval_position)
        if min_evaluation < min_move:
            min_move = min_evaluation
            best_min_move = (piece, position)
        if best_min_move is None:
            best_min_move = (piece, position)

        beta = min(beta, eval_position)
        if eval_position <= alpha:
            break
        if beta <= alpha:
            break

    return min_evaluation, best_min_move
