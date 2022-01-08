# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 14:54:55 2022

@author: richa
"""
import random
from dataclasses import dataclass
from typing import List

from .algorithm import ReversibleMove
from .piece import King
from .piece import Piece

@dataclass
class Team:
    """Contains all the pieces for a side"""

    pieces: List[Piece]

    def __post_init__(self):
        self.king = [x for x in self.pieces if isinstance(x, King)][0]

    def __iter__(self):
        for piece in self.pieces:
            yield piece

    def compute_all_moves(self, board):
        """Returns all valid moves for all pieces passed in"""
        return [(piece, pos) for piece in self for pos in piece.compute_valid_moves(board)]

    def compute_valid_moves(self, board, enemy_pieces):
        """Returns moves not resulting in a check of the allied king"""
        valid_moves = []
        for piece, position in self.compute_all_moves(board):
            with ReversibleMove(board, piece, position, enemy_pieces):
                if not self.in_check(board, enemy_pieces):
                    valid_moves.append((piece, position))
        random.shuffle(valid_moves) #HACK to avoid the same game consistently
        return valid_moves

    def in_check(self, board, enemy_pieces) -> bool:
        """Returns True if any enemy pieces can capture at the specified position"""
        return any(x.can_capture_at(board, self.king.position) for x in enemy_pieces)
