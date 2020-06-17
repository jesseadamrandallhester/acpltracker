class OpeningDatabase:
  def __init__(self, fens_file):
    with open(fens_file, 'r') as f:
      fens = f.read()
    self.THEORETICAL_FENS = set(fens.split('\n'))

  def is_book(self, fen):
    return fen in self.THEORETICAL_FENS
