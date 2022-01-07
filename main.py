# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:36:04 2021

@author: Korean_Crimson
"""
import math
from typing import Tuple

from chess_engine.algorithm import ReversibleMove
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
        if beta <= alpha:
            break

    return min_evaluation, best_min_move


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
