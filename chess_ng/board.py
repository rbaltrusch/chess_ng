# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 15:19:32 2021

@author: Korean_Crimson
"""
import itertools
import re
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

from colorama import Back, Fore, Style  # type: ignore

from chess_ng.consts import WHITE
from chess_ng.interfaces import Piece
from chess_ng.piece import Pawn


class Board:
    """Board class. Contains all the pieces on the chess board"""

    def __init__(self, pieces: Optional[List[Piece]] = None, size: int = 8):
        self._pieces: Dict[Tuple[int, int], Piece] = (
            {piece.position: piece for piece in pieces} if pieces is not None else {}
        )

        self._squares = {
            pos: self._pieces.get(pos)  # type: ignore
            for pos in itertools.product(range(size), repeat=2)
        }
        self.size = size
        self.move_history: List[Tuple[Piece, Tuple[int, int], bool]] = []
        self._positions = set(self._squares)  # for optimization

    def __repr__(self):
        # pylint: disable=invalid-name
        repr_ = ""
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
                repr_ += background + foreground + square + Style.RESET_ALL
            repr_ += "\n"
        return repr_

    def __iter__(self):
        # pylint: disable=invalid-name
        for y in range(self.size):
            yield [self[x, y] for x in range(self.size)]

    def __getitem__(self, value: Tuple[int, int]) -> Optional[Piece]:
        return self._squares.get(value)

    def __setitem__(self, key: Tuple[int, int], value: Optional[Piece]):
        if value is not None:
            self._pieces[key] = value
        self._squares[key] = value

    def _pop(self, position: Tuple[int, int]) -> Piece:
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
        was_capture = False
        if not self.is_empty_at(position) and self[position] in enemy_pieces:
            captured_piece = self.capture_at(position, log=log)
            enemy_pieces.remove(captured_piece)  # type: ignore
            was_capture = True
        self.move_piece(piece, position, was_capture, log=log)
        return captured_piece

    def move_piece(
        self,
        piece: Piece,
        position: Tuple[int, int],
        capture: bool = False,
        log: bool = True,
    ) -> None:
        """Moves the passed piece from the current position to the passed position"""
        self._pop(piece.position)
        piece.move_to(position, log=log)
        self[piece.position] = piece
        self.move_history.append((piece, position, capture))
        piece.update(self)

    def capture_at(
        self, position: Tuple[int, int], log: bool = True
    ) -> Optional[Piece]:
        """Removes the piece at the passed position and marks it as captured"""
        if self.is_empty_at(position):
            return None
        piece = self._pop(position)
        piece.captured = True
        if log:
            print(f"Captured {piece}")
        return piece

    def is_empty_at(self, position: Tuple[int, int]) -> bool:
        """Returns True if the checked position is None (contains no piece) else False"""
        return self[position] is None

    @lru_cache
    def is_on_board(self, position: Tuple[int, int]) -> bool:
        """Returns True if the checked position is on the board"""
        return position in self._positions

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

    def is_draw_by_fifty_moves(self) -> bool:
        """Returns True if there has been 50 moves without a pawn move or capture"""
        if len(self.move_history) < 100:
            return False
        last_fifty_moves = self.move_history[-100:]
        for piece, _, was_capture in last_fifty_moves:
            if isinstance(piece, Pawn) or was_capture:
                return False
        return True

    def is_draw(self) -> bool:
        """Returns True if draw by repetition or draw by 50 moves rule"""
        return self.is_draw_by_repetition() or self.is_draw_by_fifty_moves()


class BitBoard:
    """Board implemented with bitfields"""

    _BITSIZE = 4
    _PIECE_BITMASK = 2**_BITSIZE - 1
    _TEAM_BITMASK = 2 ** (_BITSIZE - 1)
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
        self.move_history: List[Tuple[Piece, Tuple[int, int], bool]] = []
        self.size = size
        self.bit_representation: int = 0
        self._init_bit_representation(pieces)
        self._squares = set(itertools.product(range(self.size), range(self.size)))

    def __repr__(self):
        # pylint: disable=invalid-name
        reverse_dict = {v: k for k, v in self._BIT_REPRESENTATIONS.items()}
        piece_bitmask = self._TEAM_BITMASK - 1  # strips team bit from piece info
        team_bitmask = self._TEAM_BITMASK
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
                    representation = f"{piece_repr}{team_repr + 1}"
                    foreground = Fore.GREEN if WHITE in representation else Fore.RED
                else:
                    foreground = Fore.LIGHTBLACK_EX
                    representation = "  "

                square = re.sub("[12]", " ", representation)
                print(background + foreground + square, end="" + Style.RESET_ALL)
            print()
        return ""

    def __hash__(self):
        return self.bit_representation

    def __iter__(self):
        # pylint: disable=invalid-name
        for y in range(self.size):
            yield [self[x, y] for x in range(self.size)]

    def __getitem__(self, value: Tuple[int, int]) -> Optional[int]:
        representation = (
            self.bit_representation >> self._convert_index(value)
        ) & self._PIECE_BITMASK
        return None if representation == 0 else representation

    def __setitem__(self, key: Tuple[int, int], value: Optional[Piece]):
        bitshift = self._convert_index(key)
        self.bit_representation &= ~(  # clear bits at position
            self._PIECE_BITMASK << bitshift
        )
        if value is None:
            return

        team = 0 if value.representation[1] == "1" else self._TEAM_BITMASK
        self.bit_representation |= (  # set bits at position
            self._BIT_REPRESENTATIONS[value.representation[0]] + team
        ) << bitshift

    def _init_bit_representation(self, pieces: List[Piece]):
        for piece in pieces:
            self[piece.position] = piece

    @lru_cache
    def _convert_index(self, position: Tuple[int, int]) -> int:
        return (position[0] + position[1] * self.size) * self._BITSIZE

    def _pop(self, position: Tuple[int, int]) -> Optional[int]:
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
        captured_piece = None
        was_capture = False
        if not self.is_empty_at(position):
            self.capture_at(position, log=log)
            capturable = [x for x in enemy_pieces if x.position == position]
            if capturable:
                captured_piece = capturable[0]
                enemy_pieces.remove(captured_piece)
                was_capture = True
        self.move_piece(piece, position, was_capture, log=log)
        return captured_piece

    def move_piece(
        self, piece: Piece, position: Tuple[int, int], capture: bool, log: bool = True
    ) -> None:
        """Moves the passed piece from the current position to the passed position"""
        self._pop(piece.position)
        piece.move_to(position, log=log)
        self[piece.position] = piece
        self.move_history.append((piece, position, capture))
        piece.update(self)  # type: ignore

    def capture_at(self, position: Tuple[int, int], log: bool = True) -> Optional[int]:
        """Removes the piece at the passed position and marks it as captured"""
        if log:
            print(f"Captured piece at {position}")
        return self._pop(position)

    def is_empty_at(self, position: Tuple[int, int]) -> bool:
        """Returns True if the checked position is None (contains no piece) else False"""
        return self[position] is None

    @lru_cache
    def is_on_board(self, position: Tuple[int, int]) -> bool:
        """Returns True if the checked position is on the board"""
        return position in self._squares

    def is_enemy(self, position: Tuple[int, int], team: str) -> bool:
        """Returns True if the checked position contains a piece with a team
        that is not the one specified.
        """
        piece_ = self[position]
        if piece_ is None:
            return False
        team_bit = piece_ & self._TEAM_BITMASK
        if team == "2":
            return team_bit == 0
        return team_bit != 0

    def is_draw_by_repetition(
        self, repetitions: int = 3, number_of_teams: int = 2
    ) -> bool:
        """Returns True if the teams have repeated the same moves a specified amount of times"""
        return Board.is_draw_by_repetition(self, repetitions, number_of_teams)  # type: ignore

    def is_draw_by_fifty_moves(self) -> bool:
        """Returns True if there has been 50 moves without a pawn move or capture"""
        return Board.is_draw_by_fifty_moves(self)  # type: ignore

    def is_draw(self) -> bool:
        """Returns True if draw by repetition or draw by 50 moves rule"""
        return Board.is_draw(self)  # type: ignore
