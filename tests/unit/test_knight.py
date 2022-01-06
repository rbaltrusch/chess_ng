# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 23:02:54 2022

@author: richa
"""
import pytest
from chess_engine.board import Board
from chess_engine.piece import Knight
from chess_engine.piece import Pawn
from chess_engine.util import convert
from chess_engine.util import convert_str

@pytest.mark.parametrize("position,expected", [("a1", 2),
                                               ("a2", 3),
                                               ("a3", 4),
                                               ("a6", 4),
                                               ("a7", 3),
                                               ("a8", 2),
                                               ("b8", 3),
                                               ("c8", 4),
                                               ("f8", 4),
                                               ("g8", 3),
                                               ("h8", 2),
                                               ("h7", 3),
                                               ("h6", 4),
                                               ("h3", 4),
                                               ("h2", 3),
                                               ("h1", 2),
                                               ("g1", 3),
                                               ("f1", 4),
                                               ("b2", 4),
                                               ("b3", 6),
                                               ("c3", 8),
                                               ])
def test_knight(position, expected):
    piece = Knight(None, convert_str(position), representation='N1')
    board = Board(pieces=[piece], size=8)
    moves = piece.compute_valid_moves(board)
    assert len(moves) == expected

@pytest.mark.parametrize("position,team,expected", [("d5", 1, False),
                                                    ("d5", 2, False),
                                                    ("b5", 2, False),
                                                    ("b4", 2, True),
                                                    ("c3", 2, True),
                                                    ("c3", 1, False),
                                                    ("e3", 2, True),
                                                    ("e3", 1, False),
                                                    ("e5", 2, False),
                                                    ("b3", 2, False),
                                                    ("f4", 2, True),
                                                    ("f4", 1, False),
                                                    ("f6", 2, True),
                                                    ("e7", 2, True),
                                                    ("e7", 1, False),
                                                    ("c7", 2, True),
                                                    ("b6", 1, False),
                                                    ("b6", 2, True)
                                                    ])
def test_knight_capture(position, team, expected):
    piece = Knight(None, convert_str("d5"), representation='N1')
    piece2 = Pawn(direction=1, position=convert_str(position), representation=f'o{team}')
    board = Board(pieces=[piece, piece2], size=8)
    moves = piece.compute_valid_moves(board)
    assert (convert_str(position) in moves) is expected

def test_knight_move_through_targets():
    knight = Knight(None, convert_str("b2"), representation='N1')
    positions = ["a1", "a2", "a3", "b3", "c3", "c2", "c1", "b1"]
    pawns = [Pawn(direction=1, position=convert_str(pos), representation='o2') for pos in positions]
    board = Board(pieces=[knight, *pawns], size=8)
    print(board)

    moves = knight.compute_valid_moves(board)
    assert set(map(convert, moves)) == {"a4", "c4", "d3", "d1"}
