from pgn_importer import PgnImporter
from flushing_list import FlushingList
from threading import Thread, Event, Condition
from collections import deque
from annotated_position import annotate_positions_in_pgn

class PositionAnnotator(object):
  def __init__(self, player_name, opening_database = None, position_hold_limit = 500):
    self._player_name = player_name
    self._opening_database = opening_database
    self._position_hold_limit = position_hold_limit
    self._pgn_importer = PgnImporter(self._player_name)
    self._pgns = deque()
    self._annotated_positions = FlushingList()
    self._thread = Thread(target=self._annotate_positions)
    self._thread.start()
    self._finished_annotating = Event()

  def _annotate_positions(self):
    while self._annotated_positions.length() < self._position_hold_limit:
      if len(self._pgns) == 0:
        self._pgns.extendleft(self._pgn_importer.next())
      try:
        self._annotated_positions.add(annotate_positions_in_pgn(
          self._pgns.pop(),
          self._player_name,
          opening_database = self._opening_database))
      except:
        continue
    self._finished_annotating.set()
      
  def get(self):
    if self._annotated_positions.length() == 0:
      self._thread.join()
    positions = self._annotated_positions.flush()
    if self._finished_annotating.isSet():
      self._finished_annotating.clear()
      self._thread.join()
      self._thread = Thread(target=self._annotate_positions)
      self._thread.start()
    return positions
