# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 14:33:33 2022

@author: richa
"""
from dataclasses import dataclass
from typing import List
from typing import Tuple

from .board import Board
from .piece import Piece


@dataclass
class ReversibleMove:
    """Context manager move that reverses board state to initial state on exit"""

    board: Board
    piece: Piece
    position: Tuple[int, int]
    enemy_pieces: List[Piece]

    def __post_init__(self):
        self.original_position = None
        self.captured_piece = None

    def __enter__(self):
        self.original_position = self.piece.position
        self.captured_piece = self.board.move_piece_and_capture(
            self.position, self.piece, self.enemy_pieces, log=False
        )
        return self

    def __exit__(self, *_):
        # undo move
        self.board.move_piece_and_capture(
            self.original_position, self.piece, self.enemy_pieces, log=False
        )
        self.piece.position_history.pop()
        self.piece.position_history.pop()
        self.board[self.position] = self.captured_piece
        if self.captured_piece is not None:
            self.captured_piece.captured = False
            self.enemy_pieces.append(self.captured_piece)
