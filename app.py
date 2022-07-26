import time

import requests
import schedule
from prometheus_client import Gauge, start_http_server

player_count = Gauge('player_count', '', ['server'])

def update_stats():
  response = requests.get('http://ta.kfk4ever.com:9080/detailed_status').json()
  for server in response['online_servers_list']:
    if server['name'] is not None:
      player_count.labels(server['name']).set(len(server['players']))

def main():
  schedule.every(1).minutes.do(update_stats)
  update_stats()
  start_http_server(8080)

  while True:
    schedule.run_pending()
    time.sleep(1)

if __name__ == '__main__':
  main()
