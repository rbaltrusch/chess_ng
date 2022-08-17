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

![Chess artificial intelligence playing a game](media/chess_ai.gif?raw=true "Chess artificial intelligence playing a game")

## Getting started

To get a copy of this repository, simply open up git bash in an empty folder and use the command:

    $ git clone https://github.com/rbaltrusch/chess_ng

To install all python dependencies, run the following in your command line:

    python -m pip install -r requirements.txt

## Next up: Machine learning ?

With weighted square parameters being given to improve the positional play of the AI, it seems to be a logical next step to improve the AI using machine learning by combining random parameter adjustments with a genetic algorithm.

## Contributions

All contributions are welcome! All details can be found in the [contribution guidelines](CONTRIBUTING.md).

## Python

Written in Python 3.8.3.

## License

This repository is open-source software available under the [MIT license](https://github.com/rbaltrusch/chess_ng/blob/master/LICENSE).

## Contact

Please raise an issue for code changes. To reach out, please send an email to richard@baltrusch.net.
