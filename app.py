import time

import requests
import schedule
from prometheus_client import Gauge, start_http_server

player_count = Gauge('player_count', '', ('server', 'loginserver'))
lobby_count = Gauge('lobby_count', '', ('loginserver',))

sources = [
  ('community', 'http://ta.kfk4ever.com:9080/detailed_status'),
  ('llamagrab', 'http://llamagrab.net:9080/detailed_status')
]

def update_stats(loginserver, url):
  player_count.clear()
  response = requests.get(url).json()

  not_in_lobby = set(['taserverbot'])
  for server in response['online_servers_list']:
    not_in_lobby.update(server['players'])
    if server['name'] is not None:
      player_count.labels(server=server['name'], loginserver=loginserver).set(len(server['players']))

  lobby_count.labels(loginserver=loginserver).set(len(set(response['online_players_list']) - not_in_lobby))

def main():
  for source in sources:
    schedule.every(1).minutes.do(update_stats, *source)
    update_stats(*source)
  start_http_server(8080)

  while True:
    schedule.run_pending()
    time.sleep(1)

if __name__ == '__main__':
  main()
