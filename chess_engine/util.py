# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 20:35:48 2021

@author: Korean_Crimson
"""
from typing import Tuple

X_POSITIONS = dict(zip(range(8), 'abcdefgh'))

#pylint: disable=invalid-name
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
    for k, v in X_POSITIONS.items():
        if v == string[0]:
            x = k
            break
    return (x, y)
