This is the back-end code for acpltracker.com. The code for the web server isn't included; this is really the "back-end of the back-end", the code that generates the responses that the web server sends to the client. To see how it works, enter the following commands after cloning the repository. I've given commands for an Ubuntu/Debian system, but equivalent commands should work on other *nix.

We'll use a virtual environment, so once you're done you can delete everything and your system won't have changed.

```
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

This will create a virtual environment with its own Python interpreter and install the project's dependencies for use only in the environment. If the first command doesn't work for you, you'll need to install python3-venv, which is harmless to have installed on your system:

```
$ sudo apt update
$ sudo apt-get install python3-venv
```

Once you have your virtual environment set up and activated and have installed the project's dependencies to it, fire up the environment's Python interpreter:

```
$ python
>>> from position_annotator import PositionAnnotator
>>> annotator = PositionAnnotator("Hikaru")
>>> annotated = annotator.get()
>>> annotated[0].as_dict()
{'capture': False, 'check': False, 'eco': 'B02', 'fen': 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1', 'game_url': 'https://www.chess.com/live/game/4938737202', 'game_datetime': '2020-06-01T18:03:47', 'is_book': None, 'is_in_check': False, 'legal_moves': 20, 'move': 'Nf6', 'move_number': 1, 'open_files': 0, 'piece': 'Knight', 'time_per_player': 180, 'increment': 0, 'time_remaining': 174, 'time_spent': 6, 'possible_captures': 0}
```

The PositionAnnotator class fetches game PGNs using the chess.com public API and uses the python-chess library along with some custom code to "annotate" the position, i.e., inspect it and tag it with information specific to it such as the number of legal moves, etc. Because the front-end code for acpltracker.com actually runs each position through a chess engine and can therefore only handle about ten positions per second, the annotator is multi-threaded, with a "pre-fetch" thread:

```
>>> len(annotated)
521
>>> annotated += annotator.get()
>>> len(annotated)
1056
```

The default is for the pre-fetch thread to run until the annotator holds 500 positions in memory, and then stop until more positions are requested. (Games are fetched by month, which is why in the above example the annotator has a bit more than 500 positions after each call to its get() method.) If the annotator weren't designed this way, you'd either have to block for each batch of positions or let a single background thread run until all of a player's positions were fetched, which would overwhelm the server's memory resources.

In order to allow the user to filter out moves that are part of opening theory (e.g., 1. e4), I used a text file containing opening variations in SAN format (e.g., "1. e4 c5 2. d4 ...", "1. d4 d5 2. c4 e6 ...") to generate a rudimentary opening database (see theoretical_positions.py for the code used to build the database):

```
>>> from opening_database import OpeningDatabase
>>> odb = OpeningDatabase("theoretical_fens")
>>> annotator = PositionAnnotator("Hikaru", opening_database = odb)
>>> annotated = annotator.get()
>>> annotated[0].is_book()
True
>>>
```

The front-end code isn't included in this repository, but it's easy to see by using the developer console in Chrome or Firefox.


