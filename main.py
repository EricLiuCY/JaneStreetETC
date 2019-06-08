# Decision for the market
# from Connection import connect, write_to_exchange, read_from_exchange
from collections import OrderedDict
import pickle
import os
import sys
import socket
import json
from bond import bond_pricing
import random

# ~~~~~~============= Gloabl Vars & Helpers ============+~~~~~

ID_array = []
bond_buy_count = 50
bond_sell_count = 50

xlf_buy, xlf_sell, xlf_ema = None
bond_buy, bond_sell = None
gs_buy, gs_sell = None
ms_buy, ms_sell = None
wfc_buy, wfc_sell = None

def generate_ID():

    ID = random.randint(1, 1000)
    if ID not in ID_array:
        return ID
    else:
        generate_ID()


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
test_exchange_index=1
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


# ~~~~============== BONDS ================ ~~~~~~~


def bond_market_maker(exchange):

    write_to_exchange(exchange,
                      {"type": "add", "order_id": generate_ID(), "symbol": "BOND", "dir": "BUY", "price": 999, "size": 50})

    write_to_exchange(exchange,
                      {"type": "add", "order_id": generate_ID(), "symbol": "BOND", "dir": "SELL", "price": 1001, "size": 50})

    print("BOND: INITIAL MARKET MADE")

def bond_buy_25(exchange):
    write_to_exchange(exchange,
                      {"type": "add", "order_id": generate_ID(), "symbol": "BOND", "dir": "BUY", "price": 999, "size": 25})

def bond_sell_25(exchange):
    write_to_exchange(exchange,
                      {"type": "add", "order_id": generate_ID(), "symbol": "BOND", "dir": "SELL", "price": 1001, "size": 25})

# ~~~~============== Trash =============== ~~~~~~~


def buy_bond(exchange, start_position, ORDERS, prices):
    # return
    ORDERID = 23491
    SORDERID = 93495
    BUYNUM = 50
    SELLNUM = 50
    write_to_exchange(exchange,
                      {"type": "add", "order_id": ORDERID, "symbol": "BOND", "dir": "BUY", "price": 999, "size": BUYNUM})

    return_exchange = read_from_exchange(exchange)
    write_to_exchange(exchange,
                      {"type": "add", "order_id": SORDERID, "symbol": "BOND", "dir": "SELL", "price": 1001, "size": SELLNUM})
    sreturn_exchange = read_from_exchange(exchange)


def dispatcher(exchange):
    message = read_from_exchange(exchange)
    type = message['type']
    global bond_buy_count, bond_sell_count

    if type == "book":
        print("it works hahahah")

    # BOND
    elif type == "fill":
        symbol = message['symbol']
        if symbol == "BOND":
            if message['price'] == 999:
                bond_buy_count -= 1
                if bond_buy_count <= 25:
                    bond_buy_25(exchange)
                    print("BOND: BUY order placed")
            if message['price'] == 1001:
                bond_sell_count -= 1
                if bond_sell_count <= 25:
                    bond_sell_25(exchange)
                    print("BOND: SELL order placed")

    elif type == "ack":
        print("ack")
    elif type == "reject":
        print("rejected")


# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    bond_market_maker(exchange)

    while True:
        dispatcher(exchange)

if __name__ == "__main__":
    while True:
        main()