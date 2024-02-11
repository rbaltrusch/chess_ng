"""Module introducing FEN notation support"""

from typing import Dict, List, Literal, Tuple, Type, Union

from chess_ng import piece
from chess_ng.board import Board
from chess_ng.consts import BLACK, DIRECTIONS, PAWN, WHITE
from chess_ng.interfaces import Piece
from chess_ng.team import Team

FenPiece = Union[
    Literal["r"], Literal["n"], Literal["b"], Literal["q"], Literal["k"], Literal["p"]
]

FEN_CLASSES: Dict[FenPiece, Type[Piece]] = {
    "r": piece.Rook,
    "n": piece.Knight,
    "b": piece.Bishop,
    "q": piece.Queen,
    "k": piece.King,
    "p": piece.Pawn,
}


class FenNotationError(Exception):
    """Can be thrown when a FEN notation string is invalid."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def load_fen_notation(  # pylint: disable=dangerous-default-value
    board_state: str, classes: Dict[FenPiece, Type[Piece]] = FEN_CLASSES
) -> Tuple[Dict[str, Team], str]:  # pylint: disable=too-many-locals
    """Loads board state from FEN notation string. Returns teams dict and side to move."""
    try:
        squares, colour, *_ = board_state.split(" ")
    except ValueError as exc:
        raise FenNotationError(
            "Invalid FEN notation string. Could not unpack."
        ) from exc

    side_to_move = {"w": WHITE, "b": BLACK}.get(colour)
    if side_to_move is None:
        raise FenNotationError("Invalid colour specified, should be either w or b.")

    # pylint: disable=invalid-name
    pieces: Dict[str, List[Piece]] = {WHITE: [], BLACK: []}
    for y, line in enumerate(squares.split("/"), 0):
        x = 0
        for char in line:
            if char.isnumeric():
                x += int(char)  # empty space
                continue

            class_ = classes.get(char.lower())  # type: ignore
            if class_ is None:
                message = (
                    f"Invalid character {char}. Should be one of [r, n, b, q, k, p]"
                )
                raise FenNotationError(message)

            # new piece
            team = BLACK if char.islower() else WHITE
            direction = DIRECTIONS[team]
            symbol = char.upper() if char.lower() != "p" else "o"
            representation = f"{symbol}{team}"
            new_piece = class_(
                direction, position=(x, y), representation=representation
            )
            pieces[team].append(new_piece)
            x += 1

    return {
        WHITE: Team(pieces[WHITE], WHITE),
        BLACK: Team(pieces[BLACK], BLACK),
    }, side_to_move


def construct_fen_notation(board: Board, side_to_move: str) -> str:
    """Takes a board object and the side to move (WHITE or BLACK) and
    constructs a FEN notation string from it, which is returned.
    """
    # pylint: disable=invalid-name
    chars: List[str] = []
    for y in range(board.size):
        count = 0
        for x in range(board.size):
            square = board[x, y]
            if square is None:
                count += 1
                continue

            if count > 0:
                chars.append(str(count))
                count = 0

            symbol_ = square.representation[0].replace(PAWN, "p")
            symbol = symbol_.upper() if square.team == WHITE else symbol_.lower()
            chars.append(symbol)
        if count > 0:
            chars.append(str(count))
        chars.append("/")

    colour = {WHITE: "w", BLACK: "b"}.get(side_to_move)
    return f"{''.join(chars)} {colour} - - 1 1"
