# -*- coding: utf-8 -*-
"""Module containing Board renderers"""

import glob
import itertools
import os
import string
from dataclasses import dataclass, field
from typing import Dict, Protocol, Tuple

from PIL import Image, ImageDraw, ImageFont

from chess_ng import consts
from chess_ng.board import Board
from chess_ng.interfaces import Piece

ImageDict = Dict[str, Dict[str, Image.Image]]


class PieceReader(
    Protocol
):  # pylint: disable=too-few-public-methods, missing-class-docstring
    def read_pieces(self) -> ImageDict:  # pylint: disable=missing-function-docstring
        ...


@dataclass
class DefaultPieceReader:
    """Reads in the piece images found in the glob paths specified"""

    white_glob: str = r"media\images\white\*.png"
    black_glob: str = r"media\images\black\*.png"

    def read_pieces(self) -> ImageDict:
        """Returns an ImageDict of white and black read-in piece images"""
        return {
            consts.WHITE: dict(self._read_images(self.white_glob)),
            consts.BLACK: dict(self._read_images(self.black_glob)),
        }

    @classmethod
    def _read_images(cls, path: str):
        for i in glob.glob(path, recursive=True):
            yield cls._name(i), Image.open(i)

    @staticmethod
    def _name(path: str) -> str:
        """# path/file.txt -> file"""
        filename, _ = os.path.splitext(os.path.basename(path))
        return filename


@dataclass
class ImageRenderer:
    """Renders the chess board as a PIL.Image.Image"""

    light: str = "#CCCCCC"
    dark: str = "#666666"
    text_colour: Tuple[int, int, int] = (255, 255, 255)
    font: ImageFont.FreeTypeFont = field(
        default_factory=lambda: ImageFont.truetype("arial.ttf", 20)
    )
    square_size: int = 60
    board_offset: int = 23
    piece_reader: PieceReader = field(default_factory=DefaultPieceReader)

    def render(self, board: Board) -> Image.Image:
        """Renders the board as an image and returns it"""
        pieces = self.piece_reader.read_pieces()
        full_size = self.square_size * board.size + self.board_offset
        new_im = Image.new("RGBA", (full_size, full_size))
        for pos in itertools.product(range(board.size), repeat=2):
            pixel_position = (
                pos[0] * self.square_size + self.board_offset,
                pos[1] * self.square_size,
            )
            new_im.paste(self._render_background(pos), pixel_position)
            piece = board[pos]
            if piece is None:
                continue
            image = self._render_piece(piece, pieces)
            new_im.paste(image, pixel_position, image)
        self._render_sides(new_im, board)
        return new_im

    def _render_background(self, position: Tuple[int, int]) -> Image.Image:
        x, y = position  # pylint: disable=invalid-name
        colour = self.light if (x + y) % 2 == 0 else self.dark
        return Image.new("RGBA", (self.square_size, self.square_size), color=colour)

    @staticmethod
    def _render_piece(piece: Piece, pieces: ImageDict):
        name = (
            "queen"
            if piece.representation.upper().startswith(consts.QUEEN)
            else piece.__class__.__name__.lower()
        )
        return pieces[piece.team][name]

    def _render_sides(self, image: Image.Image, board: Board):
        draw = ImageDraw.Draw(image)

        # pylint: disable=invalid-name
        # render row numbers next to board
        for y in range(board.size):
            draw.text(  # type: ignore
                xy=(0, y * self.square_size + self.board_offset),
                text=str(board.size - y),
                fill=self.text_colour,
                font=self.font,
            )

        # render column letters under board
        for x, letter in zip(range(board.size), string.ascii_lowercase):
            draw.text(  # type: ignore
                xy=(
                    self.board_offset + x * self.square_size,
                    image.height - self.board_offset,
                ),
                text=letter,
                fill=self.text_colour,
                font=self.font,
            )
