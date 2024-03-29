# -*- coding: utf-8 -*-
# type: ignore
"""
Created on Sat Jan  1 12:17:30 2022

@author: richa
"""
import pytest

from chess_ng.board import Board
from chess_ng.piece import Bishop, Knight, Pawn, Queen, Rook
from chess_ng.util import convert, convert_str


#pylint: disable=missing-function-docstring
@pytest.mark.parametrize("direction,position", [(-1, "a2"), (1, "a7")])
def test_initial_pawn(direction, position):
    piece = Pawn(direction, position, representation="o1")
    board = Board(pieces=[piece], size=8)
    moves = piece.compute_valid_moves(board)
    assert len(moves) == 2  # initial move and normal move

    board.move_piece(piece, moves[1])
    moves = piece.compute_valid_moves(board)
    assert len(moves) == 1


@pytest.mark.parametrize("position", ["a5", "c5"])
def test_pawn_capture(position):
    piece = Pawn(direction=-1, position="b2", representation="o1")
    piece2 = Pawn(direction=1, position=position, representation="o2")
    board = Board(pieces=[piece, piece2], size=8)

    moves = piece.compute_valid_moves(board)
    board.move_piece(piece, moves[0])
    assert convert(piece.position) == "b4"

    moves = piece.compute_valid_moves(board)
    assert len(moves) == 2  # normal move and capture

    capture = convert_str(position)
    positions = (move.position for move in moves)
    assert capture in positions
    assert not board.is_empty_at(capture)  # should contain black pawn

    board.capture_at(capture)
    assert len(board._pieces) == 1  # black pawn captured
    assert board.is_empty_at(capture)

    board.move_piece(piece, capture)
    assert convert(piece.position) == position


@pytest.mark.parametrize(
    "class_,position", [(Knight, "a3"), (Bishop, "c3"), (Rook, "a3"), (Queen, "c3")]
)
def test_other_pawn_capture(class_, position):
    piece = Pawn(direction=-1, position="b2", representation="o1")
    direction = 1
    piece2 = class_(direction, position=position, representation="o2")
    board = Board(pieces=[piece, piece2], size=8)

    moves = piece.compute_valid_moves(board)
    assert len(moves) == 3  # initial move, normal move and capture

    capture = convert_str(position)
    positions = (move.position for move in moves)
    assert capture in positions
    assert not board.is_empty_at(capture)  # should contain black pawn

    board.capture_at(capture)
    assert len(board._pieces) == 1  # black pawn captured


@pytest.mark.parametrize("position", ["a3", "c3"])
def test_backward_pawn_capture(position):
    piece = Pawn(direction=-1, position="b2", representation="o1")
    piece2 = Pawn(direction=1, position=position, representation="o2")
    board = Board(pieces=[piece, piece2], size=8)

    board.move_piece(piece, convert_str("b4"))

    moves = piece.compute_valid_moves(board)
    assert len(moves) == 1  # normal move, backward capture should not be possible


def test_blocked_pawn():
    piece = Pawn(direction=-1, position="b2", representation="o1")
    piece2 = Pawn(direction=1, position="b5", representation="o2")
    board = Board(pieces=[piece, piece2], size=8)
    moves = piece.compute_valid_moves(board)
    assert len(moves) == 2  # initial move and normal move

    board.move_piece(piece, convert_str("b4"))
    moves = piece.compute_valid_moves(board)
    assert len(moves) == 0  # no move possible


@pytest.mark.parametrize("direction,position", [(-1, "b8"), (1, "b1")])
def test_pawn_at_end_of_board(direction, position):
    piece = Pawn(
        direction=direction, position=position, representation="o1"
    )  # white pawn
    board = Board(pieces=[piece], size=8)
    moves = piece.compute_valid_moves(board)
    assert len(moves) == 21  # promoted to queen
    assert piece.representation == "Q1"
