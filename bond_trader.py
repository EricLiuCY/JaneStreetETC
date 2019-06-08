# Decision for the market
# from Connection import connect, write_to_exchange, read_from_exchange
from collections import OrderedDict
import pickle
import os
import sys
import socket
import json

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="loremipsum"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=2
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname


# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())


ORDERS = OrderedDict()

def buy_bond():
    fair_price = 1000



def main():
    if os.path.isfile('./BOND_HISTORY'):
        f = open('BOND_HISTORY', 'r')
        ORDERS = pickle.load(f)
        f.close()
    try:
        while True:
            buy_bond()
    except KeyboardInterrupt:
        f = open('BOND_HISTORY', 'w')
        pickle.dump(ORDERS, f)
        f.close()










if __name__ == "__main__":
    main()