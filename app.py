import threading
import time

import requests
from prometheus_client import Gauge, start_http_server

player_count = Gauge('player_count', '', ['server', 'loginserver'])
lobby_count = Gauge('lobby_count', '', ['loginserver'])

loginservers = {
  'community': 'http://ta.kfk4ever.com:9080/detailed_status',
  'llamagrab': 'http://llamagrab.net:9080/detailed_status'
}


def loop(interval_secs=60):
  while True:
    start = time.time()

    statuses = {}
    for loginserver, url in loginservers.items():
      try:
        statuses[loginserver] = requests.get(url).json()
      except Exception as e:
        print(f"{e}")
    
    player_count.clear()
    for loginserver, status in statuses.items():
      update_stats(loginserver, status)

    time.sleep(max(0, interval_secs - (time.time() - start)))


def update_stats(loginserver, detailed_status):
  not_in_lobby = set(['taserverbot'])
  for server in detailed_status['online_servers_list']:
    not_in_lobby.update(server['players'])
    if server['name'] is not None:
      player_count.labels(server['name'], loginserver).set(len(server['players']))
  
  lobby_count.labels(loginserver).set(len(set(detailed_status['online_players_list']) - not_in_lobby))


def main():
  start_http_server(8080)
  thread = threading.Thread(target=loop)
  thread.start()
  thread.join()

if __name__ == '__main__':
  main()
