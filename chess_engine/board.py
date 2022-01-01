# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 15:19:32 2021

@author: Korean_Crimson
"""

import re

from colorama import Fore, Back
from chess_engine.consts import WHITE

class Board:
    def __init__(self, pieces, size):
        self.pieces = {piece.position: piece for piece in pieces}
        self.size = size

    def __repr__(self):
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

    def __iter__(self):
        for y in range(self.size):
            yield [self[x, y] for x in range(self.size)]

    def __getitem__(self, value):
        return self.pieces.get(value)

    def move_piece(self, piece, position):
        self.pieces.pop(piece.position)
        piece.move_to(position)
        self.pieces[piece.position] = piece

    def is_empty_at(self, position):
        return self[position] is None

    def capture_at(self, position):
        if not self.is_empty_at(position):
            piece = self.pieces.pop(position)
            piece.captured = True
            print(f'Captured {piece}')
