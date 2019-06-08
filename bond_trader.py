# Decision for the market
# from Connection import connect, write_to_exchange, read_from_exchange
from collections import OrderedDict
import pickle
import os
import sys
import socket
import json
from bond import bond_pricing

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="loremipsum"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = False

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

def buy_bond(exchange, start_position, ORDERS):
    MAX = 30
    return_exchange = read_from_exchange(exchange)
    if return_exchange['type'] == 'book':
        if return_exchange['symbol'] == 'BOND':
            print("GOT BOND: ")
            print("The exchange replied:", return_exchange, file=sys.stderr)
            max_bond_buy = 0
            max_bond_sell = 0
            bond_buy = -1
            bond_sell = 10000
            for i in range(len(return_exchange['buy'])):
                bond_buy = max(return_exchange['buy'][i][0], bond_buy)
                if bond_buy == return_exchange['buy'][i][0]:
                    max_bond_buy = return_exchange['buy'][i][1]
            for i in range(len(return_exchange['sell'])):
                bond_sell = min(return_exchange['sell'][i][0], bond_sell)
                if bond_sell == return_exchange['sell'][i][0]:
                    max_bond_sell = return_exchange['sell'][i][1]
            (decision, profitps) = bond_pricing(bond_sell, bond_buy, 1)
            # print(decision)
            # print(bond_buy)
            # print(bond_sell)

            if decision == "SELL":
                print("DECIDING TO SELL AT " + str(bond_buy))
                print("BOOK REPLY WAS", return_exchange, file=sys.stderr)
                write_to_exchange(exchange, {"type": "add", "order_id": ORDERS, "symbol": "BOND", "dir": "SELL", "price": bond_buy, "size": max_bond_buy})
                buy_return = read_from_exchange(exchange)
                counter = 0
                while True:
                    if counter > MAX:
                        ORDERS +=1
                        print("TIMED OUT")
                        return
                    if buy_return['type'] != 'FILL':
                        print("SELL REPLY:", buy_return, file=sys.stderr)
                        buy_return = read_from_exchange(exchange)
                    else:
                        if buy_return['order_id'] == ORDERS:
                            print("FILL SELL REPLY:", buy_return, file=sys.stderr)
                            ORDERS += 1
                            return
                        else:
                            print("OTHER FILL: ", buy_return, file=sys.stderr)
                            buy_return = read_from_exchange(exchange)
                    counter += 1
            if decision == "BUY":
                print("DECIDING TO BUY AT " + str(bond_sell))
                print("BOOK REPLY WAS", return_exchange, file=sys.stderr)
                write_to_exchange(exchange, {"type": "add", "order_id": ORDERS, "symbol": "BOND", "dir": "BUY", "price": bond_sell, "size": max_bond_sell})
                sell_return = read_from_exchange(exchange)
                counter = 0
                while True:
                    if counter > MAX:
                        ORDERS +=1
                        print("TIMED OUT")
                        return
                    if sell_return['type'] != 'FILL':
                        print("BUY REPLY:", sell_return, file=sys.stderr)
                        sell_return = read_from_exchange(exchange)
                    else:
                        if sell_return['order_id'] == ORDERS:
                            print("FILL BUY REPLY:", sell_return, file=sys.stderr)
                            ORDERS += 1
                            return
                        else:
                            print("OTHER FILL: ", sell_return, file=sys.stderr)
                            sell_return = read_from_exchange(exchange)
                    counter += 1
                # while sell_return['type'] != 'FILL' and sell_return['order_id'] != ORDERS:
                #     print("SELL REPLY:", sell_return, file=sys.stderr)
                #     sell_return = read_from_exchange(exchange)
                # print("FILL SELL REPLY: ", sell_return, file=sys.stderr)
                # ORDERS += 1

            if decision == "NOTHING":
                print("DOING NOTHING FOR REPLY: ")
                print("The exchange replied:", return_exchange, file=sys.stderr)
    # return

def main():
    ORDERS = 0
    exchange = connect()
    # if os.path.isfile('./BOND_HISTORY'):
    #     f = open('BOND_HISTORY', 'r')
    #     ORDERS = pickle.load(f)
    #     f.close()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    start_position = read_from_exchange(exchange)
    try:
        while True:
            buy_bond(exchange, start_position, ORDERS)
    except KeyboardInterrupt:
        # f = open('BOND_HISTORY', 'w')
        # pickle.dump(repr(ORDERS), f)
        # f.close()
        pass

if __name__ == "__main__":
    main()