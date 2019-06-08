from collections import OrderedDict
import sys
import socket
import json
from ETF_Arb import etf_decision
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

prices = OrderedDict()
position = OrderedDict()
read_exchange = None

def trade_xlf(exchange):
    global read_exchange
    global position
    global prices

    read_exchange = read_from_exchange(exchange)

    if read_exchange['type'] == 'book':
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

    if len(prices) == 7:
        decision, ema = etf_decision(prices['XLF'], prices['BOND'], prices['GS'], prices['MS'], prices['WFC'])
        prices['XLF'] = (prices['XLF'][0], prices['XLF'][1], ema)

        if decision == 'NOTHING':
            print("Decision to do Nothing")
            return

        if decision == 'BUY':
            print("Decision to Buy")

            if position['XLF'] <= -50 or position['XLF'] <= 50:
                write_to_exchange(exchange,
                                  {"type": "add", "order_id": generate_ID(), "symbol": "XLF", "dir": "BUY",
                                   "price": prices['XLF'][1],
                                   "size": 10})

                position['XLF'] += 10

                while True:
                    read_exchange = read_from_exchange(exchange)

                    if read_exchange['type'] == 'reject':
                        print("Rejected, returning")
                        return
                    elif read_exchange['type'] == 'ack':
                        print("XLF BUY ACKNOWLEDGED")
                    elif read_exchange['type'] == 'fill':
                        print("XLF BUY FILLED")
                        break

                write_to_exchange(exchange, {"type": "convert", "order_id": generate_ID(), "symbol": "XLF",
                                             "dir": "SELL", "size": 10})
                position['XLF'] -= 10
                position['GS'] += 20
                position['WFC'] += 20
                position['BOND'] += 30
                position['MS'] += 30

                while True:
                    read_exchange = read_from_exchange(exchange)

                    if read_exchange['type'] == 'reject':
                        print("Rejected, returning")
                        return
                    elif read_exchange['type'] == 'ack':
                        print("XLF CONVERT ACKNOWLEDGED")
                        break
            elif position['XLF'] >= 50:
                write_to_exchange(exchange, {"type": "convert", "order_id": generate_ID(), "symbol": "XLF",
                                             "dir": "SELL", "size": 10})
                position['XLF'] -= 10
                position['GS'] += 20
                position['WFC'] += 20
                position['BOND'] += 30
                position['MS'] += 30

                while True:
                    read_exchange = read_from_exchange(exchange)

                    if read_exchange['type'] == 'reject':
                        print("Rejected, returning")
                        return
                    elif read_exchange['type'] == 'ack':
                        print("XLF CONVERT ACKNOWLEDGED")
                        break

            if position['BOND'] >= -50 and position['BOND'] <= 70:
                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "BOND", "dir": "SELL",
                                             "price": prices['BOND'][0],
                                             "size": 30})
                position['BOND'] -= 30

                while True:
                    read_exchange = read_from_exchange(exchange)

                    if read_exchange['type'] == 'reject':
                        print("Rejected, returning")
                        return
                    elif read_exchange['type'] == 'ack':
                        print("BOND SELL ACKNOWLEDGED")
                    elif read_exchange['type'] == 'fill':
                        print("BOND SELL FILLED")
                        break

            if position['GS'] >= -50 and position['GS'] <= 80:
                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "GS", "dir": "SELL",
                                             "price": prices['GS'][0],
                                             "size": 20})
                position['GS'] -= 20

                while True:
                    read_exchange = read_from_exchange(exchange)

                    if read_exchange['type'] == 'reject':
                        print("Rejected, returning")
                        return
                    elif read_exchange['type'] == 'ack':
                        print("GS SELL ACKNOWLEDGED")
                    elif read_exchange['type'] == 'fill':
                        print("GS SELL FILLED")
                        break

            if position['MS'] >= -50 and position['MS'] <= 70:
                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "MS", "dir": "SELL",
                                             "price": prices['MS'][0],
                                             "size": 30})
                position['MS'] -= 30

                while True:
                    read_exchange = read_from_exchange(exchange)

                    if read_exchange['type'] == 'reject':
                        print("Rejected, returning")
                        return
                    elif read_exchange['type'] == 'ack':
                        print("MS SELL ACKNOWLEDGED")
                    elif read_exchange['type'] == 'fill':
                        print("MS SELL FILLED")
                        break

            if position['WFC'] >= -50 and position['WFC'] <= 80:
                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "WFC", "dir": "SELL",
                                             "price": prices['WFC'][0],
                                             "size": 20})
                position['WFC'] -= 20

                while True:
                    read_exchange = read_from_exchange(exchange)

                    if read_exchange['type'] == 'reject':
                        print("Rejected, returning")
                        return
                    elif read_exchange['type'] == 'ack':
                        print("WFC SELL ACKNOWLEDGED")
                    elif read_exchange['type'] == 'fill':
                        print("WFC SELL FILLED")
                        break

            print("Buy Finished")
            return

        if decision == 'SELL':
            print("Decision to Sell")

            if position['BOND'] <= -50:
                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "BOND", "dir": "BUY",
                                             "price": prices['BOND'][0],
                                             "size": 30})
                position['BOND'] += 30

                while True:
                    read_exchange = read_from_exchange(exchange)

                    if read_exchange['type'] == 'reject':
                        print("Rejected, returning")
                        return
                    elif read_exchange['type'] == 'ack':
                        print("BOND BUY ACKNOWLEDGED")
                    elif read_exchange['type'] == 'fill':
                        print("BOND BUY FILLED")
                        break

            if position['GS'] <= -50:
                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "GS", "dir": "BUY",
                                             "price": prices['GS'][0],
                                             "size": 20})
                position['GS'] += 20

                while True:
                    read_exchange = read_from_exchange(exchange)

                    if read_exchange['type'] == 'reject':
                        print("Rejected, returning")
                        return
                    elif read_exchange['type'] == 'ack':
                        print("GS BUY ACKNOWLEDGED")
                    elif read_exchange['type'] == 'fill':
                        print("GS BUY FILLED")
                        break

            if position['MS'] <= -50:
                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "MS", "dir": "BUY",
                                             "price": prices['MS'][0],
                                             "size": 30})
                position['MS'] += 30

                while True:
                    read_exchange = read_from_exchange(exchange)

                    if read_exchange['type'] == 'reject':
                        print("Rejected, returning")
                        return
                    elif read_exchange['type'] == 'ack':
                        print("MS BUY ACKNOWLEDGED")
                    elif read_exchange['type'] == 'fill':
                        print("MS BUY FILLED")
                        break

            if position['WFC'] <= -50:
                write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "WFC", "dir": "BUY",
                                             "price": prices['WFC'][0],
                                             "size": 20})
                position['WFC'] += 20

                while True:
                    read_exchange = read_from_exchange(exchange)

                    if read_exchange['type'] == 'reject':
                        print("Rejected, returning")
                        return
                    elif read_exchange['type'] == 'ack':
                        print("WFC BUY ACKNOWLEDGED")
                    elif read_exchange['type'] == 'fill':
                        print("WFC BUY FILLED")
                        break

            if position['WFC'] >= -80 and position['MS'] >= -70 and position['GS'] >= -80 and position['BOND'] >= -70:

                write_to_exchange(exchange, {"type": "convert", "order_id": generate_ID(), "symbol": "XLF",
                                             "dir": "BUY", "size": 10})
                position['XLF'] += 10
                position['GS'] -= 20
                position['WFC'] -= 20
                position['BOND'] -= 30
                position['MS'] -= 30

                while True:
                    read_exchange = read_from_exchange(exchange)

                    if read_exchange['type'] == 'reject':
                        print("Rejected, returning")
                        return
                    elif read_exchange['type'] == 'ack':
                        print("XLF DE-CONVERT ACKNOWLEDGED")
                        break

                write_to_exchange(exchange,
                                  {"type": "add", "order_id": generate_ID(), "symbol": "XLF", "dir": "SELL",
                                   "price": prices['XLF'][1],
                                   "size": 10})

                position['XLF'] -= 10

                while True:
                    read_exchange = read_from_exchange(exchange)

                    if read_exchange['type'] == 'reject':
                        print("Rejected, returning")
                        return
                    elif read_exchange['type'] == 'ack':
                        print("XLF SELL ACKNOWLEDGED")
                    elif read_exchange['type'] == 'fill':
                        print("XLF SELL FILLED")
                        break

            print("Sell Finished")
            return

    else:
        return

def main():
    exchange = connect()
    global position
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    reader = read_from_exchange(exchange)
    print("Original position: ", reader, file=sys.stderr)

    for symbol in reader['symbols']:
        position[symbol['symbol']] = symbol['position']
    try:
        while True:
            trade_xlf(exchange)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()