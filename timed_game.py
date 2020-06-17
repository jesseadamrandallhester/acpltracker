import chess.pgn
import io
from chess_com import time_control, timestamps

class TimedGameNode(object):
  '''A wrapper for chess.GameNode that contains the amount of time in seconds spent on the move leading
  to the underlying GameNode object. Since there can be only one timed--i.e., main--line, we only store
  three pointers: to the next TimedGameNode, to the previous TimedGameNode, and to the root, i.e., a
  TimedGame object.'''
  def __init__(self, game_node, time_remaining, move_number, previous = None, next = None, root = None):
    self.game_node = game_node
    self.time_remaining = time_remaining
    self.move_number = move_number
    self.previous = previous
    self.next = next
    self.root = root

  def time_spent(self):
    if self.root is None:
      raise Exception("Cannot calculate time spent from an isolated TimedGameNode")
    increment = self.root.increment
    previous_node = self.previous
    if previous_node is None:
      previous_time = self.root.time_per_player
    else:
      previous_player_node = previous_node.previous
    if previous_player_node is None or type(previous_player_node) == TimedGame:
      previous_time = self.root.time_per_player
    else:
      previous_time = previous_player_node.time_remaining
    return previous_time - (self.time_remaining - increment)

class TimedGame(object):
  def __init__(self, game, time, timestamps, increment = 0):
    '''A wrapper for chess.Game that contains time information, i.e., the number of seconds per
    player for the game and any increment. When initializing a TimedGame object, we walk through
    the main line of the underlying chess.Game object and create a doubly linked list of 
    TimedGameNode objects, each of which has an underlying chess.GameNode object and also the
    amount of time remaining for the player who played the last move.'''
    self.game = game
    self.time_per_player = time
    self.increment = increment
    self.previous = None
    self.next = None
    current_game_node = game
    previous_timed_game_node = self
    timestamps_index = 0
    move_number = 0
    iteration = 0
    while current_game_node.variations: 
      try:
        timestamp = timestamps[timestamps_index]
      except:
        raise Exception("Too few timestamps!")
      if iteration % 2 == 0:
        move_number += 1
      current_timed_game_node = TimedGameNode(
        current_game_node.variations[0], 
        timestamps[timestamps_index],
        move_number,
        previous = previous_timed_game_node,
        root = self)
      previous_timed_game_node.next = current_timed_game_node
      current_game_node = current_game_node.variations[0]
      previous_timed_game_node = current_timed_game_node
      timestamps_index += 1
      iteration += 1

def game_from_pgn(pgn_str):
  pgn = io.StringIO(pgn_str)
  return chess.pgn.read_game(pgn)

def timed_game_from_pgn(pgn_str):
  game = game_from_pgn(pgn_str)
  tc = time_control(pgn_str)
  time_per_player = tc[0]
  increment = tc[1]
  ts = timestamps(pgn_str)
  return TimedGame(game, time_per_player, ts, increment)

def get_subnodes_by_side(timed_game, player):
  if not timed_game or not timed_game.next:
    return []
  black = timed_game.game.headers["Black"]
  white = timed_game.game.headers["White"]
  if player == white:
    current_node = timed_game.next
  elif player == black:
    if timed_game.next.next:
      current_node = timed_game.next.next
    else:
      return []
  else:
    raise Exception("Player %s is neither white nor black!" % player)
  subnodes = []
  while current_node and current_node.next:
    subnodes.append(current_node)
    if current_node.next.next:
      current_node = current_node.next.next
    else:
      current_node = None
  return subnodes
