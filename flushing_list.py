import threading

class FlushingList(object):
  def __init__(self):
    self._lock = threading.Lock()
    self._l = []

  def add(self, item_or_items):
    with self._lock:
      if type(item_or_items) == list:
        self._l.extend(item_or_items)
      else:
        self._l.append(item_or_items)     

  def flush(self):
    with self._lock:
      l, self._l = self._l, []
    return l

  def length(self):
    with self._lock:
      return len(self._l)
