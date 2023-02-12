# -*- coding: utf-8 -*-
import os
import random

from PIL import Image

from chess_ng.board import Board
from chess_ng.consts import BLACK, WHITE
from chess_ng.piece import PIECES
from chess_ng.renderer import ImageRenderer

FILENAME = "board.png"

# pylint: disable=missing-function-docstring
def setup():
    if os.path.isfile(FILENAME):
        os.unlink(FILENAME)


def teardown():
    if os.path.isfile(FILENAME):
        os.unlink(FILENAME)


class DummyReader:
    def read_pieces(self):
        im = Image.new("RGBA", (60, 60), color=(255, 0, 0, 255))
        piece_dict = {
            x: im for x in ["queen", "king", "rook", "knight", "bishop", "pawn"]
        }
        return {WHITE: piece_dict, BLACK: piece_dict}


def test_render():
    pieces = [
        PIECES[name](
            direction=1,
            position=(random.randint(0, 8), random.randint(0, 8)),
            representation=name[0] + WHITE,
        )
        for name in random.choices(list(PIECES.keys()), k=32)
    ]
    board = Board(pieces)
    ImageRenderer(piece_reader=DummyReader()).render(board).save(FILENAME)
    assert os.path.isfile(FILENAME)
