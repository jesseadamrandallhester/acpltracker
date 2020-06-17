from chess_com import make_datetime
from board import BoardWrapper
from timed_game import TimedGame, TimedGameNode, timed_game_from_pgn, get_subnodes_by_side

PIECE_NAMES = {
  "B": "Bishop",
  "K": "King",
  "N": "Knight",
  "Q": "Queen",
  "R": "Rook"
}
class AnnotatedPosition(object):
  def __init__(self, timed_game_node, opening_database = None):
    self._timed_game_node = timed_game_node
    self._opening_database = opening_database
    self._game_node = self._timed_game_node.game_node
    self._board = BoardWrapper(fen=self._game_node.board().fen())

  def _game(self):
    return self._game_node.game()

  def _before_board(self):
    before = self._game_node.parent.board()
    return BoardWrapper(fen=before.fen())

  def is_book(self):
    if self._opening_database is None:
      return None
    else:
      return self._opening_database.is_book(self._before_board().fen())

  def move(self):
    '''Returns the move played in the position as a SAN string.'''
    return self._game_node.san()

  def piece(self):
    piece_letter = self.move()[0]
    if PIECE_NAMES.__contains__(piece_letter):
      return PIECE_NAMES[piece_letter]
    else:
      return "Pawn"

  def game_datetime(self):
    game = self._game()
    date_string = game.headers.get("UTCDate")
    time_string = game.headers.get("UTCTime")
    return make_datetime(date_string, time_string)

  def eco(self):
    return self._game().headers["ECO"]

  def num_captures(self):
    '''Returns the number of captures that were possible in the position.'''
    return self._before_board().get_num_captures()

  def num_legal_moves(self):
    return self._before_board().num_legal_moves()

  def num_open_files(self):
    return self._before_board().num_open_files()

  def time_per_player(self):
    return self._timed_game_node.root.time_per_player

  def increment(self):
    return self._timed_game_node.root.increment

  def time_remaining(self):
    return self._timed_game_node.time_remaining

  def time_spent(self):
    '''Returns the amount of time (in seconds) that the player spent on their last move.'''
    return self._timed_game_node.time_spent()

  def fen(self):
    '''We want the position that the move was played in, not the position after the move.'''
    return self._game_node.parent.board().fen()

  def move_number(self):
    return self._timed_game_node.move_number

  def game_url(self):
    game = self._game()
    return game.headers.get("Link")

  def is_in_check(self):
    return self._before_board().is_check();

  def capture(self):
    move_san = self.move()
    return move_san[1] == 'x'

  def check(self):
    move_san = self.move()
    return move_san[len(move_san) - 1] == '+'

  def as_dict(self):
    return {
      "capture": self.capture(),
      "check": self.check(),
      "eco": self.eco(),
      "fen": self.fen(),
      "game_url": self.game_url(),
      "game_datetime": self.game_datetime().isoformat(), 
      "is_book": self.is_book(),
      "is_in_check": self.is_in_check(),
      "legal_moves": self.num_legal_moves(),
      "move": self.move(),
      "move_number": self.move_number(),
      "open_files": self.num_open_files(),
      "piece": self.piece(),
      "time_per_player": self.time_per_player(),
      "increment": self.increment(),
      "time_remaining": self.time_remaining(),
      "time_spent": self.time_spent(),
      "possible_captures": self.num_captures()
    }

def annotate_positions_in_pgn(pgn, player_name, opening_database = None):
  game = timed_game_from_pgn(pgn)
  positions = get_subnodes_by_side(game, player_name)
  # Throw out positions in which the player appears to have spent a negative amount of time, which
  # can occur if, e.g., their opponent added time to their clock
  positions = [pos for pos in positions if pos.time_spent() >= 0]  
  return [AnnotatedPosition(pos, opening_database = opening_database) for pos in positions]
