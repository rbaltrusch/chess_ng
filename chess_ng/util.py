# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 20:35:48 2021

@author: Korean_Crimson
"""
from dataclasses import dataclass
from typing import Tuple

X_POSITIONS = dict(zip(range(8), "abcdefgh"))


class InvalidPositionException(Exception):
    """Exception to be raised for invalid chess square string positions."""


@dataclass
class Move:
    """Moves class, takes a position that can be moved to and whether it is a capture or not"""

    position: Tuple[int, int]
    can_capture: bool = False

    def __hash__(self):
        return hash(self.position)

    def __iter__(self):
        # pylint: disable=invalid-name
        for x in self.position:
            yield x

    def __getitem__(self, key: int):
        return self.position[key]


# pylint: disable=invalid-name
def convert(position: Tuple[int, int]) -> str:
    """Converts an int index position on the board into a standard chess square name.
    Example: (0, 7) -> a1
    """
    x, y = position
    return X_POSITIONS[x] + str(8 - y)


def convert_str(string: str) -> Tuple[int, int]:
    """Converts a standard chess square name into an int index position on the board.
    Example: a1 -> (0, 7).
    """
    y = 8 - int(string[-1])
    for x, v in X_POSITIONS.items():
        if v == string[0]:
            return (x, y)
    raise InvalidPositionException("Invalid string chess board position specified!")


def is_diagonal(position1: Tuple[int, int], position2: Tuple[int, int]):
    """Returns True if position1 and position2 are on a diagonal line"""
    x1, y1 = position1
    x2, y2 = position2
    return abs(x1 - x2) == abs(y1 - y2)


def is_straight(position1: Tuple[int, int], position2: Tuple[int, int]):
    """Returns True if position1 and position2 are horizontally or vertically aligned"""
    x1, y1 = position1
    x2, y2 = position2
    return x1 == x2 or y1 == y2
