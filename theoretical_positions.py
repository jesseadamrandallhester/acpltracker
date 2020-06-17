import chess
import re

MOVE_REGEX = '([BKNQR][a-h1-8]?x?[a-h][1-8]\+?|[a-h]x[a-h][1-8]\+?|[a-h][1-8]\+?|O[\-O]*O\+?)'

def fens_from_variation(variation_string):
  fens = []
  sans = re.findall(MOVE_REGEX, variation_string)
  board = chess.Board()
  fens.append(board.fen())
  for san in sans:
    board.push_san(san)
    fens.append(board.fen())
  return fens

def fens_from_variations(variation_strings):
  fens = set()
  for vs in variation_strings:
    [fens.add(fen) for fen in fens_from_variation(vs)]
  return fens
