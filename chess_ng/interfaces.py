# -*- coding: utf-8 -*-
"""Module containing interfaces of shared types, for type hinting"""

from __future__ import annotations

from typing import List, Literal, Optional, Protocol, Tuple, Union

from chess_ng.util import Move

# pylint: disable=missing-class-docstring, missing-function-docstring

Direction = Union[Literal[-1], Literal[1]]


class MoveInterface(Protocol):  # pylint: disable=too-few-public-methods
    def compute_valid_moves(self, board: Board, piece: Piece) -> List[Move]:
        ...


class Board(Protocol):

    size: int
    move_history: List[Tuple[Piece, Tuple[int, int], bool]]

    def __getitem__(self, value: Tuple[int, int]) -> Optional[Piece]:
        ...

    def is_empty_at(self, position: Tuple[int, int]) -> bool:
        ...

    def is_on_board(self, position: Tuple[int, int]) -> bool:
        ...

    def is_enemy(self, position: Tuple[int, int], team: str) -> bool:
        ...


class Piece(Protocol):

    turn_counter: float = 0.0
    position: Tuple[int, int]
    representation: str
    team: str
    captured: bool
    position_history: List[Tuple[int, int]]

    def __hash__(self) -> int:
        ...

    def update(self, board: Board):
        ...

    def increase_search_depth(self, search_depth: int) -> int:
        ...

    def compute_valid_moves(self, board: Board) -> List[Move]:
        ...

    def move_to(self, position: Tuple[int, int], log: bool = True) -> None:
        ...

    def can_capture_at(self, board: Board, position: Tuple[int, int]) -> bool:
        ...


# pylint: disable=too-few-public-methods
class PieceFactory(Protocol):
    def __call__(
        self, direction: Direction, position: Tuple[int, int], representation: str
    ) -> Piece:
        ...
