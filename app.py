import time

import requests
import schedule
from prometheus_client import Gauge, start_http_server

player_count = Gauge('player_count', '', ['server'])
lobby_count = Gauge('lobby_count', '')

def update_stats():
  response = requests.get('http://ta.kfk4ever.com:9080/detailed_status').json()

  in_server = set()
  for server in response['online_servers_list']:
    if server['name'] is not None:
      for player in server['players']:
        in_server.add(player)
      player_count.labels(server['name']).set(len(server['players']))

  online_players = set(response['online_players_list'])
  online_players.remove('taserverbot')
  lobby_count.set(len(online_players - in_server))


def main():
  schedule.every(1).minutes.do(update_stats)
  update_stats()
  start_http_server(8080)

  while True:
    schedule.run_pending()
    time.sleep(1)

if __name__ == '__main__':
  main()
