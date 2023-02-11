# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 14:53:45 2022

@author: richa
"""
import math
from typing import Dict, Iterable, List, Tuple

from chess_ng.board import BitBoard, Board
from chess_ng.interfaces import Piece


def get_hash_values(pieces: List[Piece]) -> Dict[str, int]:
    """Returns a hash value dict that looks up piece representations and returns
    a unique integer.
    """
    representations = set(piece.representation for piece in pieces)
    return {representation: i for i, representation in enumerate(representations, 1)}


def compute_hash(board: Board, hash_values: Dict[str, int]) -> int:
    """Computes a new hash from the board the specified hash_values lookup table"""
    if isinstance(board, BitBoard):
        return hash(board)

    # pylint: disable=invalid-name
    if not hash_values:
        return 0

    exponent = math.ceil(math.log(len(hash_values), 2))
    hash_ = 0
    for y in range(board.size):
        for x in range(board.size):
            counter = y * board.size + x
            piece = board[x, y]
            if piece is None:
                continue

            value = (
                piece if isinstance(piece, int) else hash_values[piece.representation]
            )
            num = value << counter * exponent
            hash_ ^= num
    return hash_


def update_hash(
    hash_: int,
    board: Board,
    hash_values: Dict[str, int],
    changed_positions: Iterable[Tuple[int, int]],
) -> int:
    """Updates the Zobrist hash by xor gating. 100 times fasteer than generating new hash"""
    # pylint: disable=invalid-name
    exponent = math.ceil(math.log(len(hash_values), 2))
    max_ = 2**exponent - 1
    for x, y in changed_positions:
        counter = y * board.size + x
        piece = board[x, y]
        value = (
            piece
            if isinstance(piece, int)
            else (hash_values[piece.representation] if piece is not None else 0)
        )
        num = value << counter * exponent
        hash_ &= ~(max_ << counter * exponent)
        hash_ ^= num
    return hash_
