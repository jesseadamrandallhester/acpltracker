from chess_com import ChessComPubApi
from flushing_list import FlushingList
from threading import Thread

class PgnImporter(object):
  def __init__(self, player_name):
    self._player_name = player_name
    self._chess_com = ChessComPubApi()
    self._archive_urls = self._chess_com.get_archive_urls(self._player_name)
    self._pgns = FlushingList()
    self._prefetch_thread = Thread(target=self._get_pgns_in_archive)
    self._prefetch_thread.start()
    
  def _get_pgns_in_archive(self):
    if (len(self._archive_urls) > 0):
      pgns = self._chess_com.get_pgns_in_archive(self._archive_urls.pop())
      self._pgns.add(pgns)

  def next(self):
    self._prefetch_thread.join()
    self._prefetch_thread = Thread(target=self._get_pgns_in_archive)
    self._prefetch_thread.start()
    return self._pgns.flush()
     
