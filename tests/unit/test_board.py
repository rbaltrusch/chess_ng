# -*- coding: utf-8 -*-
# type: ignore
"""
Created on Sat Jan  1 13:28:41 2022

@author: richa
"""
import itertools

import pytest

from chess_ng.board import Board
from chess_ng.piece import Pawn, Piece
from chess_ng.util import convert_str


#pylint: disable=missing-function-docstring
def test_board_len():
    piece = Pawn(direction=-1, position="a2", representation="o1")
    piece2 = Pawn(direction=-1, position="b5", representation="o2")
    board = Board(pieces=[piece, piece2], size=8)
    assert len(board._pieces) == 2


def test_board_capture():
    piece = Pawn(direction=-1, position="a2", representation="o1")
    piece2 = Pawn(direction=-1, position="b3", representation="o2")
    board = Board(pieces=[piece, piece2], size=8)

    position = convert_str("b3")
    board.capture_at(position)
    assert len(board._pieces) == 1


@pytest.mark.parametrize(
    "pieces,size",
    [
        ({}, 8),
        ([Piece([], (0, 0), "o1")], 8),
        ([Piece([], pos, "o1") for pos in itertools.product(range(8), repeat=2)], 8),
        ([Piece([], pos, "o1") for pos in itertools.product(range(8), repeat=2)], 4),
    ],
)
def test_board_iter(pieces, size):
    board = Board(pieces, size)
    assert len(list(board)) == size


def test_board_getitem():
    piece = Pawn(direction=-1, position="a2", representation="o1")
    board = Board(pieces=[piece], size=8)
    pos = convert_str("a2")
    assert board[pos] is piece  # exists
    assert board[0, 0] is None  # doesnt exist, square is empty


def test_board_move_piece():
    piece = Pawn(direction=-1, position="a2", representation="o1")
    board = Board(pieces=[piece], size=8)
    assert len(board._pieces) == 1

    pos = convert_str("a3")
    board.move_piece(piece, pos)
    assert len(board._pieces) == 1
    assert board[pos] is piece


def test_board_is_empty_at():
    piece = Pawn(direction=-1, position="a2", representation="o1")
    board = Board(pieces=[piece], size=8)

    pos = convert_str("a2")
    assert not board.is_empty_at(pos)  # contains a2 pawn

    pos = convert_str("a3")
    assert board.is_empty_at(pos)  # empty


def test_board_repr():
    piece = Pawn(direction=-1, position="a2", representation="o1")
    board = Board(pieces=[piece], size=8)
    board.__repr__()
