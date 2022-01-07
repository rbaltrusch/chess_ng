# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:36:04 2021

@author: Korean_Crimson
"""
import math
import random
from typing import Dict
from typing import List

from chess_engine.board import Board
from chess_engine.consts import BLACK
from chess_engine.consts import BOARD
from chess_engine.consts import DIRECTIONS
from chess_engine.consts import WHITE
from chess_engine.piece import King
from chess_engine.piece import Piece
from chess_engine.piece import PIECES

def init_pieces() -> Dict[int, List[Piece]]:
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
    return pieces

def get_valid_squares(board, pieces):
    """Returns all valid moves for all pieces passed in"""
    return [(piece, s) for piece in pieces for s in piece.compute_valid_moves(board)]

def filter_king_check_moves(board, moves, king, enemy_pieces):
    """Returns moves not resulting in a check of the allied king"""
    valid_moves = []
    for piece, position in moves:
        original_position = piece.position
        captured_piece = board.move_piece_and_capture(position, piece, enemy_pieces, log=False)

        if not in_check(board, king, enemy_pieces):
            valid_moves.append((piece, position))

        #undo move
        board.move_piece_and_capture(original_position, piece, enemy_pieces, log=False)
        piece.position_history.pop()
        piece.position_history.pop()
        board[position] = captured_piece
        if captured_piece is not None:
            captured_piece.captured = False
            enemy_pieces.append(captured_piece)
    return valid_moves

def in_check(board, king, enemy_pieces) -> bool:
    """Returns True if any enemy pieces can capture at the specified position"""
    return any(x.can_move_to(board, king.position) for x in enemy_pieces)

def evaluate(board, pieces, enemy_pieces):
    """Evaluates the board state based on the amount of moves allied pieces
    and enemy pieces can make.
    """
    return len(get_valid_squares(board, pieces)) - len(get_valid_squares(board, enemy_pieces))

#pylint: disable=too-many-arguments,too-many-locals,too-many-statements #for now...
def minimax(board, pieces, team, enemy, depth, alpha, beta, maximizing_player):
    """Minimax algorithm with alpha-beta pruning.
    At depth=3, computation speed is still relatively fast.
    At depth=4, it slows down considerably, but does make much better moves.
    """
    best_move = None
    if depth == 0: #or game over
        return evaluate(board, pieces[team], pieces[enemy]), best_move

    if maximizing_player:
        max_eval = -math.inf
        king = [x for x in pieces[team] if isinstance(x, King)][0]
        unfiltered_moves = get_valid_squares(board, pieces[team])
        moves = filter_king_check_moves(board, unfiltered_moves, king, pieces[enemy])
        random.shuffle(moves) #HACK to avoid the same game consistently
        for piece, position in moves:
            original_position = piece.position
            captured_piece = board.move_piece_and_capture(position, piece, pieces[enemy], log=False)

            eval_position = minimax(board, pieces, team, enemy, depth-1, alpha, beta, False)[0]

            #undo move
            board.move_piece_and_capture(original_position, piece, pieces[enemy], log=False)
            piece.position_history.pop()
            piece.position_history.pop()
            board[position] = captured_piece
            if captured_piece is not None:
                captured_piece.captured = False
                pieces[enemy].append(captured_piece)

            if eval_position > max_eval or best_move is None:
                best_move = (piece, position)
            max_eval = max(max_eval, eval_position)
            alpha = max(alpha, eval_position)
            if beta <= alpha:
                break
        return max_eval, best_move

    min_evaluation = math.inf
    min_move = math.inf
    king = [x for x in pieces[enemy] if isinstance(x, King)][0]
    unfiltered_moves = get_valid_squares(board, pieces[enemy])
    moves = filter_king_check_moves(board, unfiltered_moves, king, pieces[team])
    random.shuffle(moves) #HACK to avoid the same game consistently
    best_min_move = None
    for piece, position in moves:
        original_position = piece.position
        captured_piece = board.move_piece_and_capture(position, piece, pieces[team], log=False)

        eval_position = minimax(board, pieces, team, enemy, depth-1, alpha, beta, True)[0]

        #undo move
        board.move_piece_and_capture(original_position, piece, pieces[team], log=False)
        piece.position_history.pop()
        piece.position_history.pop()
        board[position] = captured_piece
        if captured_piece is not None:
            captured_piece.captured = False
            pieces[team].append(captured_piece)

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

    pieces = init_pieces()
    board = Board(pieces[WHITE] + pieces[BLACK], size=8)

    for _ in range(50):
        for team in [WHITE, BLACK]:
            king = [x for x in pieces[team] if isinstance(x, King)][0]
            enemy = BLACK if team is WHITE else WHITE
            enemy_pieces = pieces[enemy]
            is_in_check = in_check(board, king, enemy_pieces)

            moves = get_valid_squares(board, pieces[team])
            valid_moves = filter_king_check_moves(board, moves, king, enemy_pieces)
            random.shuffle(valid_moves) #HACK: avoid infinite repeat

            if not valid_moves:
                if is_in_check:
                    print(f'Checkmated team {team}. Team {enemy} wins.')
                else:
                    print('Stalemate. Teams draw.')
                return

            if is_in_check:
                print('Moving out of check.')

            rating, (piece, position) = minimax(
                board, pieces, team, enemy, depth=4,
                alpha=-math.inf, beta=math.inf, maximizing_player=True
            )
            print(f'Rating: {rating}')
            board.move_piece_and_capture(position, piece, enemy_pieces)

            #check if checking enemy king
            enemy_king = [x for x in enemy_pieces if isinstance(x, King)][0]
            if in_check(board, enemy_king, pieces[team]):
                print('Checking enemy king')

            print(board)

if __name__ == '__main__':
    main()
