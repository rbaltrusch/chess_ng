# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 15:19:32 2021

@author: Korean_Crimson
"""
import itertools
import re
from typing import Dict, List, Optional, Tuple

from colorama import Back, Fore, Style

from chess_ng.consts import WHITE
from chess_ng.interfaces import Piece


class Board:
    """Board class. Contains all the pieces on the chess board"""

    def __init__(self, pieces: Optional[List[Piece]] = None, size: int = 8):
        self._pieces: Dict[Tuple[int, int], Optional[Piece]] = (
            {piece.position: piece for piece in pieces} if pieces is not None else {}
        )

        self._squares = {
            pos: self._pieces.get(pos)
            for pos in itertools.product(range(size), repeat=2)
        }
        self.size = size
        self.move_history: List[Tuple[Piece, Tuple[int, int]]] = []

    def __repr__(self):
        # pylint: disable=invalid-name
        for y in range(self.size):
            for x in range(self.size):
                if y % 2:
                    background = Back.BLACK if x % 2 else Back.WHITE
                else:
                    background = Back.WHITE if x % 2 else Back.BLACK

                piece = self[x, y]
                if piece is not None:
                    foreground = (
                        Fore.GREEN if WHITE in piece.representation else Fore.RED
                    )
                    representation = piece.representation
                else:
                    foreground = Fore.LIGHTBLACK_EX
                    representation = "  "

                square = re.sub("[12]", " ", representation)
                print(background + foreground + square, end="" + Style.RESET_ALL)
            print()
        return ""

    def __iter__(self):
        # pylint: disable=invalid-name
        for y in range(self.size):
            yield [self[x, y] for x in range(self.size)]

    def __getitem__(self, value: Tuple[int, int]) -> Optional[Piece]:
        return self._squares.get(value)

    def __setitem__(self, key: Tuple[int, int], value: Optional[Piece]):
        self._pieces[key] = value
        self._squares[key] = value

    def pop(self, position: Tuple[int, int]) -> Optional[Piece]:
        """Removes the piece at the specified position and returns it"""
        self._squares[position] = None
        return self._pieces.pop(position)

    def move_piece_and_capture(
        self,
        position: Tuple[int, int],
        piece: Piece,
        enemy_pieces: List[Piece],
        log: bool = True,
    ) -> Optional[Piece]:
        """Moves piece to position on the board. Captures enemy if there is one"""
        captured_piece = None
        if not self.is_empty_at(position) and self[position] in enemy_pieces:
            captured_piece = self.capture_at(position, log=log)
            enemy_pieces.remove(captured_piece)  # type: ignore
        self.move_piece(piece, position, log=log)
        return captured_piece

    def move_piece(
        self, piece: Piece, position: Tuple[int, int], log: bool = True
    ) -> None:
        """Moves the passed piece from the current position to the passed position"""
        self.pop(piece.position)
        piece.move_to(position, log=log)
        self[piece.position] = piece
        self.move_history.append((piece, position))

    def capture_at(
        self, position: Tuple[int, int], log: bool = True
    ) -> Optional[Piece]:
        """Removes the piece at the passed position and marks it as captured"""
        if self.is_empty_at(position):
            return None
        piece: Piece = self.pop(position)  # type: ignore
        piece.captured = True
        if log:
            print(f"Captured {piece}")
        return piece

    def is_empty_at(self, position: Tuple[int, int]) -> bool:
        """Returns True if the checked position is None (contains no piece) else False"""
        return self[position] is None

    def is_on_board(self, position: Tuple[int, int]) -> bool:
        """Returns True if the checked position is on the board"""
        return position in self._squares

    def is_enemy(self, position: Tuple[int, int], team: str) -> bool:
        """Returns True if the checked position contains a piece with a team
        that is not the one specified.
        """
        return self[position] is not None and self[position].team != team  # type: ignore

    def is_draw_by_repetition(
        self, repetitions: int = 3, number_of_teams: int = 2
    ) -> bool:
        """Returns True if the teams have repeated the same moves a specified amount of times"""
        number_of_moves = repetitions * number_of_teams * 2
        if len(self.move_history) < number_of_moves:
            return False
        return len(set(self.move_history[-number_of_moves:])) == number_of_teams * 2


class BitBoard:
    """Board implemented with bitfields"""

    _BITSIZE = 4
    _BIT_REPRESENTATIONS = {
        None: 0,
        "o": 1,
        "R": 2,
        "N": 3,
        "B": 4,
        "Q": 5,
        "K": 6,
    }

    def __init__(self, pieces: List[Piece], size: int = 8):
        self.move_history: List[Tuple[Piece, Tuple[int, int]]] = []
        self.size = size
        self._bit_representation: int = 0
        self._init_bit_representation(pieces)

    def __repr__(self):
        # pylint: disable=invalid-name
        reverse_dict = {v: k for k, v in self._BIT_REPRESENTATIONS.items()}
        piece_bitmask = 2 ** (self._BITSIZE - 1) - 1
        team_bitmask = 2 ** (self._BITSIZE - 1)
        team_bitshift = self._BITSIZE - 1

        for y in range(self.size):
            for x in range(self.size):
                if y % 2:
                    background = Back.BLACK if x % 2 else Back.WHITE
                else:
                    background = Back.WHITE if x % 2 else Back.BLACK

                piece = self[x, y]
                if piece is not None:
                    piece_repr = reverse_dict[piece & piece_bitmask]
                    team_repr = (piece & team_bitmask) >> team_bitshift
                    repr_ = f"{piece_repr}{team_repr + 1}"
                    foreground = Fore.GREEN if WHITE in repr_ else Fore.RED
                    representation = repr_
                else:
                    foreground = Fore.LIGHTBLACK_EX
                    representation = "  "

                square = re.sub("[12]", " ", representation)
                print(background + foreground + square, end="" + Style.RESET_ALL)
            print()
        return ""

    def __iter__(self):
        # pylint: disable=invalid-name
        for y in range(self.size):
            yield [self[x, y] for x in range(self.size)]

    def __getitem__(self, value: Tuple[int, int]) -> Optional[int]:
        piece_bitmask = 2**self._BITSIZE - 1
        bitshift = self._convert_index(value) * self._BITSIZE
        representation = (self._bit_representation >> bitshift) & piece_bitmask
        return None if representation == 0 else representation

    def __setitem__(self, key: Tuple[int, int], value: Optional[Piece]):
        repr_ = None if value is None else value.representation[0]
        team_bitmask = 2 ** (self._BITSIZE - 1)
        bitmask = 2**self._BITSIZE - 1
        team = (
            0 if value is None else team_bitmask * (int(value.representation[-1]) - 1)
        )
        bitshift = self._convert_index(key) * self._BITSIZE
        rep = (self._BIT_REPRESENTATIONS[repr_] + team) << bitshift
        self._bit_representation &= ~(bitmask << bitshift)
        self._bit_representation |= rep

    def _init_bit_representation(self, pieces: List[Piece]):
        for piece in pieces:
            self[piece.position] = piece

    def _convert_index(self, position: Tuple[int, int]) -> int:
        x, y = position  # pylint: disable=invalid-name
        return x + y * self.size

    def pop(self, position: Tuple[int, int]) -> Optional[int]:
        """Removes the piece at the specified position and returns it"""
        val = self[position]
        self[position] = None
        return val

    def move_piece_and_capture(
        self,
        position: Tuple[int, int],
        piece: Piece,
        enemy_pieces: List[Piece],
        log: bool = True,
    ):
        """Moves piece to position on the board. Captures enemy if there is one"""
        return Board.move_piece_and_capture(self, position, piece, enemy_pieces, log)  # type: ignore

    def move_piece(
        self, piece: Piece, position: Tuple[int, int], log: bool = True
    ) -> None:
        """Moves the passed piece from the current position to the passed position"""
        return Board.move_piece(self, piece, position, log)  # type: ignore

    def capture_at(
        self, position: Tuple[int, int], log: bool = True
    ) -> Optional[Piece]:
        """Removes the piece at the passed position and marks it as captured"""
        return Board.capture_at(self, position, log)  # type: ignore

    def is_empty_at(self, position: Tuple[int, int]) -> bool:
        """Returns True if the checked position is None (contains no piece) else False"""
        return self[position] is None

    def is_on_board(self, position: Tuple[int, int]) -> bool:
        """Returns True if the checked position is on the board"""
        return all(0 <= x < self.size for x in position)

    def is_enemy(self, position: Tuple[int, int], team: str) -> bool:
        """Returns True if the checked position contains a piece with a team
        that is not the one specified.
        """
        piece_ = self[position]
        team_ = piece_ & 1 << (self._BITSIZE - 1) if piece_ is not None else 0
        return team == str(team_)

    def is_draw_by_repetition(
        self, repetitions: int = 3, number_of_teams: int = 2
    ) -> bool:
        """Returns True if the teams have repeated the same moves a specified amount of times"""
        number_of_moves = repetitions * number_of_teams * 2
        if len(self.move_history) < number_of_moves:
            return False
        return len(set(self.move_history[-number_of_moves:])) == number_of_teams * 2
