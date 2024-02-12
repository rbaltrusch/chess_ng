[![Unit tests](https://github.com/rbaltrusch/chess_ng/actions/workflows/pytest-unit-tests.yml/badge.svg)](https://github.com/rbaltrusch/chess_ng/actions/workflows/pytest-unit-tests.yml)
[![Pylint](https://github.com/rbaltrusch/chess_ng/actions/workflows/pylint.yml/badge.svg)](https://github.com/rbaltrusch/chess_ng/actions/workflows/pylint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)

# Chess Engine

This is a small chess engine written in Python. It currently supports basic moves and captures for all chess pieces (this does not include en-passant and castling). The supported game endings are checkmate and stalemate.

## Chess AI

The game currently uses a simple [minimax](https://en.wikipedia.org/wiki/Minimax) algorithm with alpha-beta pruning to decide on its best move. This works fairly well, and at recursion depth 4, the engine starts to make pretty sensible moves, such as getting hold of the center, developing major pieces, forking pieces, controlling open and semi-open files with rooks, controlling more space by playing pawn a4 -> a5, etc...

The AI is quite positionally minded, without any hard-coded square weights or similar methods. This is achieved by using a simple evaluation function in the minimax algorithm that rates the amount of legal moves the allied side can make, versus the moves of the enemy side:

```python
len(team.compute_all_moves(board)) - len(enemy.compute_all_moves(board))
```

This naturally encourages a lot of activity in the center and positional play, as well as rating pieces correctly depending on the game state (e.g. a blocked rook is worthless because it can make no moves, but a rook on a semi-open file controls a lot of space and is worth a lot), without the shortcomings of a hand-crafted or hard-coded approach.

### Example game

An example game of the chess AI playing against itself can be found [here](https://www.chess.com/analysis/game/pgn/4TbhVit3ki).

![Chess artificial intelligence playing a game](https://github.com/rbaltrusch/chess_ng/blob/master/media/chess_ai.gif?raw=true "Chess artificial intelligence playing a game")

## Getting started

Install the package using pip, then run it using:

    python -m pip install chess_ng
    python -m chess_ng

## Documentation

### CLI

The command line options for the `chess_ng` package are the following:

```
usage: chess_ng [-h] [--depth DEPTH] [--mode {cli,auto}] [--player {1,2}] [--fen FEN] [--eval-algorithm {moves,move-distance}]
                [--resign-threshold RESIGN_THRESHOLD] [--max-moves MAX_MOVES] [--seed SEED] [--log-folder LOG_FOLDER]
                [--log-filename-suffix LOG_FILENAME_SUFFIX] [--disable-logs]

A Python chess engine

optional arguments:
  -h, --help            show this help message and exit
  --depth DEPTH, -d DEPTH
                        The minimax depth to use
  --mode {cli,auto}, -m {cli,auto}
                        The player mode
  --player {1,2}, -p {1,2}
                        The player colour
  --fen FEN, -f FEN     The FEN string with which to initialise the game
  --eval-algorithm {moves,move-distance}, -e {moves,move-distance}
                        The evaluation algorithm to use in minimax
  --resign-threshold RESIGN_THRESHOLD, -r RESIGN_THRESHOLD
                        The position rating at which to surrender
  --max-moves MAX_MOVES, --max MAX_MOVES
                        The maximum amount of moves to play
  --seed SEED, -s SEED  The random seed to be used
  --log-folder LOG_FOLDER
                        The folder to which logfiles are written
  --log-filename-suffix LOG_FILENAME_SUFFIX
                        The name suffix for logfiles
  --disable-logs        Disables log files from being written
```

To print the help message, run `python -m chess_ng -h`.

### Graphical chess board

To render a graphical chess board using the `chess_ng.renderer.ImageRenderer`, the class expects images of size 60x60 in the following tree structure at the root of the repository:

```
\---media/images
    +---black
    |       bishop.png
    |       king.png
    |       knight.png
    |       pawn.png
    |       queen.png
    |       rook.png
    |
    \---white
            bishop.png
            king.png
            knight.png
            pawn.png
            queen.png
            rook.png
```

Images with a creative commons license can be downloaded from e.g. [here](https://commons.wikimedia.org/wiki/Category:PNG_chess_pieces/Standard_transparent).

## Contributions

All contributions are welcome! All details can be found in the [contribution guidelines](https://github.com/rbaltrusch/chess_ng/blob/master/CONTRIBUTING.md).

## Python

Written in Python 3.8.3.

## License

This repository is open-source software available under the [MIT license](https://github.com/rbaltrusch/chess_ng/blob/master/LICENSE).

## Contact

Please raise an issue for code changes. To reach out, please send an email to richard@baltrusch.net.
