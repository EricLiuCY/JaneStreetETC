# Decision for the market
# from Connection import connect, write_to_exchange, read_from_exchange
from collections import OrderedDict
import pickle
import os
import sys
import socket
import json
from bond import bond_pricing
from ETF_Arb import etf_decision
# from bad_decision import bad_etf_decision as etf_decision
import random


ID_array = []


def generate_ID():

    ID = random.randint(0, 100000)
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
test_exchange_index=0
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

def trade_xlf(exchange, prices):
    read_exchange = read_from_exchange(exchange)
    # print("The exchange gave:", read_exch/ange, file=sys.stderr)
    def price_updater():
        buys = read_exchange['buy']
        sells = read_exchange['sell']
        avg_buy = -1
        avg_sell = -1
        max_buy = 0
        max_sell = 0
        for i in buys:
            max_buy = max(max_buy, i[1])
            if max_buy == i[1]:
                avg_buy = i[0]
        for i in sells:
            max_sell = max(max_sell, i[1])
            if max_sell == i[1]:
                avg_sell = i[0]
        prices[read_exchange['symbol']] = (avg_buy, avg_sell, None)
        return

    def wait_for_fill(MAX, currread):
        print("Waiting for fill")
        counter = 0
        while True:
            if counter > MAX:
                print("Fill never reached")
                print("The exchange gave:", currread, file=sys.stderr)
                return
            if currread['type'] == 'fill':
                print("Fill reached")
                return
            if currread['type'] == 'book':
                price_updater()
            counter += 1
            currread = read_from_exchange(exchange)

    while True:
        read_exchange = read_from_exchange(exchange)
        if read_exchange['type'] == 'book':
            price_updater()

        if len(prices) > 6:
            decision, ema = etf_decision(prices['XLF'], prices['BOND'], prices['GS'], prices['MS'], prices['WFC'])
            prices['XLF'] = (prices['XLF'][0], prices['XLF'][1], ema)

            if decision == 'NOTHING':
                print("DOING NOTHING")

            if decision == 'BUY':
                print("Decision to Buy")
                print("The exchange gave:", read_exchange, file=sys.stderr)
                print("Current prices: " + repr(prices))
                write_to_exchange(exchange,
                                  {"type": "add", "order_id": generate_ID(), "symbol": "XLF", "dir": "BUY", "price": prices['XLF'][1],
                                   "size": 10})
                while True:
                    read_exchange = read_from_exchange(exchange)
                    if read_exchange['type'] == 'reject':
                        print("The exchange REJECTED:", read_exchange, file=sys.stderr)
                        write_to_exchange(exchange,
                                          {"type": "add", "order_id": generate_ID(), "symbol": "XLF", "dir": "SELL",
                                           "price": prices['XLF'][0],
                                           "size": 10})
                        break
                    if read_exchange['type'] == 'ack':
                        print("Got xlf ack")
                        # wait_for_fill(30, read_exchange)
                        break
                    elif read_exchange['type'] == 'book':
                        price_updater()

                write_to_exchange(exchange, {"type": "convert", "order_id": generate_ID(), "symbol": "XLF", "dir": "SELL", "size": 10})
                while True:
                    read_exchange = read_from_exchange(exchange)
                    if read_exchange['type'] == 'ack':
                        print("Got convert ack")
                        # wait_for_fill(30, read_exchange)
                        break
                    elif read_exchange['type'] == 'book':
                        price_updater()

                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "BOND", "dir": "SELL", "price": prices['BOND'][0],
                                   "size": 30})
                while True:
                    read_exchange = read_from_exchange(exchange)
                    if read_exchange['type'] == 'ack':
                        print("Got bsell ack")
                        wait_for_fill(30, read_exchange)
                        break
                    elif read_exchange['type'] == 'book':
                        price_updater()
                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "GS", "dir": "SELL",
                                             "price": prices['GS'][0],
                                             "size": 20})
                while True:
                    read_exchange = read_from_exchange(exchange)
                    if read_exchange['type'] == 'ack':
                        print("Got gsell ack")
                        wait_for_fill(30, read_exchange)
                        break
                    elif read_exchange['type'] == 'book':
                        price_updater()
                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "MS", "dir": "SELL",
                                             "price": prices['MS'][0],
                                             "size": 30})
                while True:
                    read_exchange = read_from_exchange(exchange)
                    if read_exchange['type'] == 'ack':
                        print("Got msell ack")
                        wait_for_fill(30, read_exchange)
                        break
                    elif read_exchange['type'] == 'book':
                        price_updater()
                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "WFC", "dir": "SELL",
                                             "price": prices['WFC'][0],
                                             "size": 20})
                print("Selling WFC at " + str(prices['WFC'][0]))
                while True:
                    read_exchange = read_from_exchange(exchange)
                    if read_exchange['type'] == 'ack':
                        print("Got wsell ack")
                        wait_for_fill(30, read_exchange)
                        break
                    elif read_exchange['type'] == 'book':
                        price_updater()

            if decision == 'SELL':
                print("Decision to Sell")
                print("The exchange gave:", read_exchange, file=sys.stderr)
                print("Current prices: " + repr(prices))

                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "BOND", "dir": "BUY",
                                             "price": prices['BOND'][1],
                                             "size": 30})
                print("BOUGHT BOND")
                # counter = 0
                while True:
                    read_exchange = read_from_exchange(exchange)
                    if read_exchange['type'] == 'reject':
                        print("The exchange REJECTED:", read_exchange, file=sys.stderr)
                        write_to_exchange(exchange,
                                          {"type": "add", "order_id": generate_ID(), "symbol": "BOND", "dir": "SELL",
                                           "price": prices['BOND'][0],
                                           "size": 30})
                        break
                    if read_exchange['type'] == 'ack':
                        print("Got bbuy ack")
                        wait_for_fill(30, read_exchange)
                        break
                    elif read_exchange['type'] == 'book':
                        price_updater()
                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "GS", "dir": "BUY",
                                             "price": prices['GS'][1],
                                             "size": 20})
                while True:
                    read_exchange = read_from_exchange(exchange)
                    if read_exchange['type'] == 'reject':
                        print("The exchange REJECTED:", read_exchange, file=sys.stderr)
                        write_to_exchange(exchange,
                                          {"type": "add", "order_id": generate_ID(), "symbol": "GS", "dir": "SELL",
                                           "price": prices['GS'][0],
                                           "size": 20})
                        break
                    if read_exchange['type'] == 'ack':
                        print("Got gbuy ack")
                        wait_for_fill(30, read_exchange)
                        break
                    elif read_exchange['type'] == 'book':
                        price_updater()
                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "MS", "dir": "BUY",
                                             "price": prices['MS'][1],
                                             "size": 30})
                while True:
                    read_exchange = read_from_exchange(exchange)
                    if read_exchange['type'] == 'reject':
                        print("The exchange REJECTED:", read_exchange, file=sys.stderr)
                        write_to_exchange(exchange,
                                          {"type": "add", "order_id": generate_ID(), "symbol": "MS", "dir": "SELL",
                                           "price": prices['MS'][0],
                                           "size": 30})
                        break
                    if read_exchange['type'] == 'ack':
                        print("Got mbuy ack")
                        wait_for_fill(30, read_exchange)
                        break
                    elif read_exchange['type'] == 'book':
                        price_updater()
                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "WFC", "dir": "BUY",
                                             "price": prices['WFC'][1],
                                             "size": 20})
                while True:
                    read_exchange = read_from_exchange(exchange)
                    if read_exchange['type'] == 'reject':
                        print("The exchange REJECTED:", read_exchange, file=sys.stderr)
                        write_to_exchange(exchange,
                                          {"type": "add", "order_id": generate_ID(), "symbol": "WFC", "dir": "SELL",
                                           "price": prices['WFC'][0],
                                           "size": 20})
                        break
                    if read_exchange['type'] == 'ack':
                        print("Got wbuy ack")
                        wait_for_fill(30, read_exchange)
                        break
                    elif read_exchange['type'] == 'book':
                        price_updater()
                write_to_exchange(exchange,
                                  {"type": "convert", "order_id": generate_ID(), "symbol": "XLF", "dir": "BUY",
                                   "size": 10})
                while True:
                    read_exchange = read_from_exchange(exchange)
                    if read_exchange['type'] != 'book':
                        print("The exchange gave:", read_exchange, file=sys.stderr)
                    if read_exchange['type'] == 'ack':
                        print("Got xconvert ack")
                        # wait_for_fill(30, read_exchange)
                        break
                    elif read_exchange['type'] == 'book':
                        price_updater()
                write_to_exchange(exchange,
                                  {"type": "add", "order_id": generate_ID(), "symbol": "XLF", "dir": "SELL",
                                   "price": prices['XLF'][0],
                                   "size": 10})
                while True:
                    read_exchange = read_from_exchange(exchange)
                    if read_exchange['type'] == 'ack':
                        print("Got xsell ack")
                        # wait_for_fill(30, read_exchange)
                        break
                    elif read_exchange['type'] == 'book':
                        price_updater()

        else:
            break

def main():
    prices = OrderedDict()
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    print("Original position: ", read_from_exchange(exchange), file=sys.stderr)
    try:
        while True:
            trade_xlf(exchange, prices)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()