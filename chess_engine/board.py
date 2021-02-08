# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 15:19:32 2021

@author: Korean_Crimson
"""

import re
from colorama import Fore, Back
from chess_engine.consts import WHITE, BLACK, EMPTY

class Board:
    def __init__(self, board):
        self.board = board

    def __repr__(self):
        for y, row in enumerate(self.board):
            for x, square in enumerate(row):
                if y % 2:
                    background = Back.BLACK if x % 2 else Back.WHITE
                else:
                    background = Back.WHITE if x % 2 else Back.BLACK

                if '1' in square:
                    foreground = Fore.GREEN
                elif '2' in square:
                    foreground = Fore.RED
                else:
                    foreground = Fore.LIGHTBLACK_EX

                square = re.sub('[12]', ' ', square)
                print(background + foreground + square, end='')
            print()
        return ''

    def __iter__(self):
        for row in self.board:
            yield row

    def __getitem__(self, value):
        return self.board[value]

    def update(self, pieces):
        self.board = [['  ' for _ in range(8)] for _ in range(8)]
        for piece in pieces[WHITE] + pieces[BLACK]:
            x, y = piece.position
            self.board[y][x] = piece.representation

    def is_empty_at(self, position):
        x, y = position
        return self.board[y][x] == EMPTY

    @staticmethod
    def capture_at(pieces, position):
        for piece in pieces:
            if piece.position == position:
                piece.captured = True
                print(f'Captured {piece}')
                break
