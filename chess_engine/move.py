# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 12:56:04 2021

@author: Korean_Crimson
"""

from itertools import takewhile

class Move:
    def __init__(self, range_, direction=1, forward_only=False, horz_move=False, vert_move=False, can_capture=False):
        self.range = range_
        self.forward_only = forward_only
        self.horz_move = horz_move
        self.vert_move = vert_move
        self.direction = direction
        self.can_capture = can_capture

    def compute_valid_moves(self, position, board, team):
        x, y = position
        horz_moves = []
        vert_moves = []
        if self.vert_move:
            squares = [row[x] for row in board]
            horz_moves = list(self._compute_valid_moves(y, x, squares, team))

        if self.horz_move:
            squares = list(board)[y]
            vert_moves = [(x, y) for y, x in self._compute_valid_moves(x, y, squares, team)]
        return horz_moves + vert_moves

    def _compute_valid_moves(self, coord, other_coord, all_squares, team):
        start = coord if self.forward_only else 0
        end = start + self.range * self.direction
        if start > end:
            start, end = end, start
        if self.direction == 1:
            end += 1
        if end > len(all_squares):
            end = len(all_squares)

        squares = all_squares[start:end]
        for y, square in enumerate(squares, start):
            if y == coord:
                continue

            if square is None:
                if self._check_squares_between(squares, y, coord):
                    yield other_coord, y
                    continue
                break

            is_enemy = square.representation[-1] != team
            if self.can_capture and is_enemy and self._check_squares_between(squares, y, coord):
                yield other_coord, y

    def _check_squares_between(self, squares, y, coord):
        end = y - 1 if self.can_capture else y
        squares_between = squares[y:coord] if y <= coord else squares[coord+1:end]
        return all(square is None for square in squares_between)

class BishopMove():
    def __init__(self, range_, direction=1, forward_only=False):
        self.range = range_
        self.direction = direction
        self.forward_only = forward_only

    def compute_valid_moves(self, position, board, team):
        generators_forward = [self._compute_valid_moves(position, board, team, min_x=False, min_y=False),
                              self._compute_valid_moves(position, board, team, min_x=False, min_y=True)]
        generators_backward = [self._compute_valid_moves(position, board, team, min_x=True, min_y=False),
                               self._compute_valid_moves(position, board, team, min_x=True, min_y=True)]
        if self.forward_only:
            generators = generators_forward if self.direction == -1 else generators_backward
        else:
            generators = generators_forward + generators_backward
        squares = [square for generator in generators for square in generator]
        return squares

    def _compute_valid_moves(self, position, board, team, min_x=False, min_y=False):
        x, y = position
        end_x, x_step = (x - self.range, -1) if min_x else (x + self.range, 1)
        end_y, y_step = (y - self.range, -1) if min_y else (y + self.range, 1)
        get_indices = lambda start, stop, step: takewhile(lambda x: 0 <= x < 8, range(start, stop, step))
        indices = list(zip(get_indices(x, end_x, x_step), get_indices(y, end_y, y_step)))
        squares = [board[x, y] for x, y in indices]
        if squares:
            squares.pop(0)

        for (x_, y_), square in zip(indices, squares):
            if square == position:
                continue

            if square is None:
                yield (x_, y_)
            else:
                if square.representation[-1] != team: #is enemy
                    yield (x_, y_)
                break

class InitialPawnMove(Move):
    def __init__(self, direction):
        range_ = 2
        super().__init__(range_, direction, forward_only=True, vert_move=True, can_capture=False)

class PawnMove(Move):
    def __init__(self, direction):
        range_ = 1
        super().__init__(range_, direction, forward_only=True, vert_move=True, can_capture=False)

class PawnCapture(BishopMove):
    def __init__(self, direction):
        range_ = 1
        super().__init__(range_, direction, forward_only=True)

class EnPassantMove:
    pass

class RookMove(Move):
    def __init__(self):
        range_ = 8
        super().__init__(range_, horz_move=True, vert_move=True, can_capture=True)

class KnightMove:
    pass
