# Chess Engine

This is a small chess engine written in Python. It is currently still a work in progress.

## Current features

The engine currently supports basic moves for all chess pieces, as well as capturing, both for pawns and major pieces (King, Queen, rook and bishop).

## Missing features

- The knight currently can neither move nor capture
- Captures are bugged
- En passant captures
- Castling

## Features planned down the line

### Improved AI

Currently, the AI just picks a random move each turn. This should be improved using a [minimax](https://en.wikipedia.org/wiki/Minimax) algorithm and weighted squares with a priority on the centre of the chess board.

### Machine learning

With weighted square parameters being given to improve the positional play of the AI, it seems to be a logical next step to improve the AI using machine learning by combining random parameter adjustments with a genetic algorithm.

## Getting started

To get a copy of this repository, simply open up git bash in an empty folder and use the command:

    $ git clone https://github.com/rbaltrusch/chess_engine

To install all python dependencies, run the following in your command line:

    python -m pip install -r requirements.txt

## Python

Written in Python 3.8.3.

## License

This repository is open-source software available under the [MIT license](https://github.com/rbaltrusch/chess_engine/blob/master/LICENSE).

## Contact

Please raise an issue for code changes. To reach out, please send an email to richard@baltrusch.net.
