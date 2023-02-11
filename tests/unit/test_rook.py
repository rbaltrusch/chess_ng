# -*- coding: utf-8 -*-
# type: ignore
"""
Created on Sun Jan  2 23:12:07 2022

@author: richa
"""
import random

import pytest

from chess_ng.board import Board
from chess_ng.piece import Pawn, Rook
from chess_ng.util import convert, convert_str


#pylint: disable=missing-function-docstring
def test_rook():
    piece = Rook(None, convert_str("a1"), representation="R1")
    board = Board(pieces=[piece], size=8)
    for _ in range(20):
        moves = piece.compute_valid_moves(board)
        move = random.choice(moves)
        board.move_piece(piece, move)
        assert len(moves) == 14  # 14 in all positions


@pytest.mark.parametrize(
    "position,expected",
    [
        ("a1", False),
        ("a2", True),
        ("a3", False),
        ("b3", True),
        ("c3", False),
        ("c2", True),
        ("c1", False),
        ("b1", True),
        ("b2", False),
    ],
)
def test_rook_capture(position, expected):
    piece = Rook(None, convert_str("b2"), representation="R1")
    piece2 = Pawn(direction=1, position=convert_str(position), representation="o2")
    board = Board(pieces=[piece, piece2], size=8)
    moves = piece.compute_valid_moves(board)
    positions = (move.position for move in moves)
    assert (convert_str(position) in positions) is expected


@pytest.mark.parametrize(
    "team,expected_moves",
    [
        (2, {"d4", "d6", "c5", "e5"}),
        (1, set()),
    ],
)
def test_rook_move_not_going_through_targets(team, expected_moves):
    rook = Rook(None, convert_str("d5"), representation="R1")
    piece2 = Pawn(direction=1, position=convert_str("d6"), representation=f"o{team}")
    piece3 = Pawn(direction=1, position=convert_str("d4"), representation=f"o{team}")
    piece4 = Pawn(direction=1, position=convert_str("c5"), representation=f"o{team}")
    piece5 = Pawn(direction=1, position=convert_str("e5"), representation=f"o{team}")
    board = Board(pieces=[rook, piece2, piece3, piece4, piece5], size=8)
    print(board)

    moves = rook.compute_valid_moves(board)
    positions = (move.position for move in moves)
    assert set(map(convert, positions)) == expected_moves
