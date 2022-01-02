# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 23:03:05 2022

@author: richa
"""

import pytest
from chess_engine.util import convert_str
from chess_engine.board import Board
from chess_engine.piece import King
from chess_engine.piece import Pawn

@pytest.mark.parametrize("position,expected", [("a1", 3),
                                               ("a2", 5),
                                               ("b1", 5),
                                               ("b2", 8),
                                               ("a8", 3),
                                               ("a7", 5),
                                               ("b8", 5),
                                               ("h8", 3),
                                               ("h7", 5),
                                               ("h1", 3),
                                               ("h2", 5),
                                               ])
def test_king(position, expected):
    piece = King(None, convert_str(position), representation='L1')
    board = Board(pieces=[piece], size=8)

    moves = piece.compute_valid_moves(board)
    assert len(moves) == expected

@pytest.mark.parametrize("position, length, expected", [("a1", 8, True),
                                                        ("a2", 8, True),
                                                        ("a3", 8, True),
                                                        ("a4", 8, False),
                                                        ("b3", 8, True),
                                                        ("c4", 8, False),
                                                        ("c3", 8, True),
                                                        ("c2", 8, True),
                                                        ("c1", 8, True),
                                                        ("b1", 8, True),
                                                        ("b2", 8, False)])
def test_king_capture(position, length, expected):
    piece = King(None, "b2", representation='L1')
    piece2 = Pawn(direction=-1, position=position, representation='o2')
    board = Board(pieces=[piece, piece2], size=8)

    moves = piece.compute_valid_moves(board)
    assert len(moves) == length
    assert (convert_str(position) in moves) is expected
