# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 22:43:44 2022

@author: richa
"""

import pytest
from chess_engine.util import convert
from chess_engine.util import convert_str
from chess_engine.board import Board
from chess_engine.piece import Bishop
from chess_engine.piece import Pawn

@pytest.mark.parametrize("position,expected", [("a1", 7),
                                               ("b2", 7 + 2),
                                               ("b1", 6 + 1),
                                               ("c3", 7 + 4),
                                               ("c4", 6 + 5),
                                               ("d4", 7 + 6),
                                               ("c5", 7 + 4),
                                               ("c6", 7 + 4)
                                               ])
def test_bishop(position, expected):
    piece = Bishop(None, convert_str(position), representation='L1')
    board = Board(pieces=[piece], size=8)
    moves = piece.compute_valid_moves(board)
    assert len(moves) == expected

@pytest.mark.parametrize("position,length,expected", [("a1", 9, True),
                                               ("a2", 9, False),
                                               ("a3", 9, True),
                                               ("b3", 9, False),
                                               ("c3", 4, True),
                                               ("c2", 9, False),
                                               ("c1", 9, True),
                                               ("b1", 9, False),
                                               ("b2", 9, False)
                                               ])
def test_bishop_capture(position, length, expected):
    piece = Bishop(None, convert_str("b2"), representation='L1')
    piece2 = Pawn(direction=1, position=convert_str(position), representation='o2')
    board = Board(pieces=[piece, piece2], size=8)
    moves = piece.compute_valid_moves(board)
    assert len(moves) == length
    assert (convert_str(position) in moves) is expected

def test_bishop_move_not_going_through_targets():
    bishop = Bishop(None, convert_str("b2"), representation='L1')
    piece2 = Pawn(direction=1, position=convert_str("a1"), representation='o2')
    piece3 = Pawn(direction=1, position=convert_str("a3"), representation='o2')
    piece4 = Pawn(direction=1, position=convert_str("c3"), representation='o2')
    piece5 = Pawn(direction=1, position=convert_str("c1"), representation='o2')
    board = Board(pieces=[bishop, piece2, piece3, piece4, piece5], size=8)

    moves = bishop.compute_valid_moves(board)
    assert set(map(convert, moves)) == {'a1', 'a3', 'c3', 'c1'}
