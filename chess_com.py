import requests
import json
import re
from datetime import datetime

GAMES_LIMIT = 100

def make_datetime(chesscom_date_string, chesscom_time_string):
  '''The chess.com API currently formats dates as "YYYY.MM.DD" and times as "hh:mm:ss".'''
  datetime_string = chesscom_date_string + "-" + chesscom_time_string
  format_string = "%Y.%m.%d-%H:%M:%S"
  try:
    d = datetime.strptime(datetime_string, format_string)
  except:
    raise Exception("The chess.com API may have changed its date and/or time formats")
  return d 

class NoSuchPlayerError(Exception):
  pass
class ChessComPubApi():
  def __init__(self):
    self._base_url = "https://api.chess.com/pub"

  def get_games(self, player, limit=GAMES_LIMIT):
    '''Warning: we assume that the archive URLs are sorted in ascending chronological
    order, which they currently are (but might not always be).'''
    archive_urls = self.get_archive_urls(player)
    games = []
    while len(games) <= limit:
      result = decode_response(requests.get(archive_urls.pop()))
      archive_games = result["games"]
      games.extend(archive_games)
    return games[0:limit]

  def get_pgns_in_archive(self, archive_url):
    result = decode_response(requests.get(archive_url))
    normal_games = [game for game in result["games"] if game["rules"] == "chess"]
    normal_games = [game for game in normal_games if game.__contains__("pgn")]
    #live_games = [game for game in normal_games if game["time_class"] != "daily"]
    return [game["pgn"] for game in normal_games]

  def get_archive_urls(self, player):
    url = self._base_url + "/player/" + player + "/games/archives"
    response = requests.get(url)
    if response.status_code == 404:
      raise NoSuchPlayerError
    result = decode_response(requests.get(url))
    archive_urls = result["archives"]
    return archive_urls

def decode_response(json_response):
  return json.loads(json_response.text)

def timestamps(chess_com_pgn):
  timestamp_regex = "%clk (\d+):(\d+):(\d+)"
  timestamp_tuples = re.findall(timestamp_regex, chess_com_pgn)
  return [int(ts[0]) * 3600 + int(ts[1]) * 60 + int(ts[2]) for ts in timestamp_tuples] 

def time_control(chess_com_pgn):
  '''Returns a 2-tuple containing the number of seconds per player and the increment (or zero).'''
  time_control_regex = "TimeControl\D*(\d+)([\+\d+]*)"
  match = re.search(time_control_regex, chess_com_pgn)
  base_time = int(match.group(1))
  increment = match.group(2)
  if not increment:
    increment = 0
  else:
    increment = int(increment)
  return (base_time, increment)

def eco(chess_com_pgn):
  eco_regex = '\[ECO "([A-E]\d\d)"\]'
  match = re.search(eco_regex, chess_com_pgn)
  if match is None or match.group(1) is None:
    return "Unknown"
  else:
    return match.group(1) 
