# This is just a way to add methods to chess.Board without modifying the python-chess code itself.
# I could also just write functions that accept a chess.Board as an argument. That approach actually 
# seems more straightforward to me, but I see one problem with it: someone reading the module might
# not know what these "board" things are and where their methods are defined. If we do it this way,
# it's immediately clear that in order for the code to work you need to have a module named chess.py
# in your Python path, and that module must have a class named Board.
#
# The other way to do it would be to add the methods directly to the Board class, but I'd rather keep
# my code separate from library code, even though I'm clearly leveraging a library here.

from chess import Board, BB_FILES, PAWN, WHITE, BLACK

class BoardWrapper(Board):
  def get_num_pieces(self):
    return len(self.piece_map().keys())

  def num_legal_moves(self):
    return self.legal_moves.count()

  def get_captures(self):
    return [move for move in self.legal_moves if self.is_capture(move)]

  def get_num_captures(self):
    return len(self.get_captures())

  def _pawns_mask(self):
    return self.pieces_mask(PAWN, WHITE) | self.pieces_mask(PAWN, BLACK) 

  def num_open_files(self):
    count = 0
    pawns_mask = self._pawns_mask()
    for file in BB_FILES:
      if pawns_mask & file == 0:
        count +=1
    return count 
