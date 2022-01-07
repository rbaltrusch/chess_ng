# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 15:19:32 2021

@author: Korean_Crimson
"""
import re
from typing import List
from typing import Tuple
from typing import Union

from colorama import Back
from colorama import Fore

from .consts import WHITE
from .piece import Piece

class Board:
    """Board class. Contains all the pieces on the chess board"""

    def __init__(self, pieces: List[Piece], size: int):
        self.pieces = {piece.position: piece for piece in pieces}
        self.size = size

    def __repr__(self):
        #pylint: disable=invalid-name
        for y in range(self.size):
            for x in range(self.size):
                if y % 2:
                    background = Back.BLACK if x % 2 else Back.WHITE
                else:
                    background = Back.WHITE if x % 2 else Back.BLACK

                piece = self[x, y]
                if piece is not None:
                    foreground = Fore.GREEN if WHITE in piece.representation else Fore.RED
                    representation = piece.representation
                else:
                    foreground = Fore.LIGHTBLACK_EX
                    representation = '  '

                square = re.sub('[12]', ' ', representation)
                print(background + foreground + square, end='')
            print()
        return ''

    def __hash__(self):
        return hash((frozenset(self.pieces.items()), self.size))

    def __iter__(self):
        #pylint: disable=invalid-name
        for y in range(self.size):
            yield [self[x, y] for x in range(self.size)]

    def __getitem__(self, value):
        return self.pieces.get(value)

    def __setitem__(self, key, value):
        self.pieces[key] = value

    def move_piece_and_capture(self, position, piece, enemy_pieces, log=True):
        """Moves piece to position on the board. Captures enemy if there is one"""
        captured_piece = None
        if not self.is_empty_at(position):
            if self[position] in enemy_pieces:
                captured_piece = self.capture_at(position, log=log)
                enemy_pieces.remove(captured_piece)
        self.move_piece(piece, position, log=log)
        return captured_piece

    def move_piece(self, piece: Piece, position: Tuple[int, int], log=True) -> None:
        """Moves the passed piece from the current position to the passed position"""
        self.pieces.pop(piece.position)
        piece.move_to(position, log=log)
        self.pieces[piece.position] = piece

    def capture_at(self, position: Tuple[int, int], log=True) -> Union[None, Piece]:
        """Removes the piece at the passed position and marks it as captured"""
        if not self.is_empty_at(position):
            piece = self.pieces.pop(position)
            piece.captured = True
            if log:
                print(f'Captured {piece}')
            return piece
        return None

    def is_empty_at(self, position: Tuple[int, int]) -> bool:
        """Returns True if the checked position is None (contains no piece) else False"""
        return self[position] is None

    def is_on_board(self, position: Tuple[int, int]) -> bool:
        """Returns True if the checked position is on the board"""
        #pylint: disable=invalid-name
        x, y = position
        return 0 <= x < self.size and 0 <= y < self.size

    def is_enemy(self, position: Tuple[int, int], team: int) -> bool:
        """Returns True if the checked position contains a piece with a team
        that is not the one specified.
        """
        return self[position] is not None and self[position].team != team
