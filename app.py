import threading
import time

import requests
from prometheus_client import Gauge, start_http_server

INTERVAL_SECS = 60
player_count = Gauge('player_count', '', ['server', 'loginserver'])
lobby_count = Gauge('lobby_count', '', ['loginserver'])

sources = [
  ('community', 'http://ta.kfk4ever.com:9080/detailed_status'),
  ('llamagrab', 'http://llamagrab.net:9080/detailed_status')
]

def loop():
  while True:
    start = time.time()
    player_count.clear()
    for source in sources:
      try:
        update_stats(*source)
      except Exception as e:
        print(f"{e}")
    time.sleep(max(0, INTERVAL_SECS - (time.time() - start)))


def update_stats(loginserver, url):
  response = requests.get(url).json()
  not_in_lobby = set(['taserverbot'])
  for server in response['online_servers_list']:
    not_in_lobby.update(server['players'])
    if server['name'] is not None:
      player_count.labels(server['name'], loginserver).set(len(server['players']))

  lobby_count.labels(loginserver).set(len(set(response['online_players_list']) - not_in_lobby))

def main():
  threading.Thread(target=loop).start()
  start_http_server(8080)

  while True:
    time.sleep(3600)

if __name__ == '__main__':
  main()
