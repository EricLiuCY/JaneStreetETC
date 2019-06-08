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


# ~~~~============== My Code ================ ~~~~~~~


def bond_market_maker(exchange):

    write_to_exchange(exchange,
                      {"type": "add", "order_id": generate_ID(), "symbol": "BOND", "dir": "BUY", "price": 999, "size": 50})

    write_to_exchange(exchange,
                      {"type": "add", "order_id": generate_ID(), "symbol": "BOND", "dir": "SELL", "price": 1001, "size": 50})

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

    def buyer(return_exchange, BUYNUM, ORDERID, SORDERID):

        if BUYNUM < 50:
            write_to_exchange(exchange,
                              {"type": "add", "order_id": ORDERID, "symbol": "BOND", "dir": "BUY", "price": 999,
                               "size": (50 - BUYNUM)})
            ORDERID += 1
            print("BUY ORDER PLACED OF SIZE: " + str(50 - BUYNUM))
            BUYNUM = 50
            return read_from_exchange(exchange), BUYNUM, ORDERID
        if return_exchange['type'] == 'ack':
            if return_exchange['order_id'] == ORDERID:
                print("BUY ORDER ACKNOWLEDGED")
                return read_from_exchange(exchange), BUYNUM, ORDERID
        if return_exchange['type'] == 'book':
            buys = return_exchange['buy']
            sells = return_exchange['sell']

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
            prices[return_exchange['symbol']] = (avg_buy, avg_sell, None)
        elif return_exchange['type'] == 'fill':
            if return_exchange['price'] == 999:
                BUYNUM -= return_exchange['size']
                print("BUY ORDER FULFILLED AT PRICE: " + str(return_exchange['price']) + " OF SIZE: " + str(
                    return_exchange['size']))
                ORDERID+=1
            elif return_exchange['order_id'] == SORDERID:
                return return_exchange, SELLNUM, ORDERID
            return read_from_exchange(exchange), BUYNUM, ORDERID
        return read_from_exchange(exchange), BUYNUM, ORDERID

    def seller(return_exchange, SELLNUM, ORDERID, SORDERID):
        if SELLNUM < 50:
            write_to_exchange(exchange,
                              {"type": "add", "order_id": ORDERID, "symbol": "BOND", "dir": "SELL", "price": 1001,
                               "size": (50 - SELLNUM)})
            ORDERID += 1
            print("SELL ORDER PLACED OF SIZE: " + str(50-SELLNUM))
            SELLNUM = 50

            return read_from_exchange(exchange), SELLNUM, ORDERID
        if return_exchange['type'] == 'book':
            buys = return_exchange['buy']
            sells = return_exchange['sell']

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
            prices[return_exchange['symbol']] = (avg_buy, avg_sell, None)
        if return_exchange['type'] == 'ack':
            if return_exchange['order_id'] == ORDERID:
                print("SELL ORDER ACKNOWLEDGED")
                return read_from_exchange(exchange), SELLNUM, ORDERID
        elif return_exchange['type'] == 'fill':
            if return_exchange['price'] == 1001:
                SELLNUM -= return_exchange['size']
                print("SELL ORDER FULFILLED AT PRICE: " + str(return_exchange['price']) + " OF SIZE: " + str(
                    return_exchange['size']))
                ORDERID+=1
            elif return_exchange['order_id'] == SORDERID:
                return return_exchange, SELLNUM, ORDERID
            return read_from_exchange(exchange), SELLNUM, ORDERID
        return read_from_exchange(exchange), SELLNUM, ORDERID

    while True:
        return_exchange, BUYNUM, ORDERID = buyer(return_exchange, BUYNUM, ORDERID, SORDERID)
        sreturn_exchange, SELLNUM, SORDERID = seller(sreturn_exchange, SELLNUM, SORDERID, ORDERID)

    # write_to_exchange(exchange,
    #                   {"type": "add", "order_id": 51245, "symbol": "BOND", "dir": "SELL", "price": 1001,
    #                    "size": 50})
    # SELLNUM = 50
    # return_exchange = read_from_exchange(exchange)
    # while True:
    #     if SELLNUM < 50:
    #         write_to_exchange(exchange,
    #                           {"type": "add", "order_id": 51245, "symbol": "BOND", "dir": "SELL", "price": 1001,
    #                            "size": (50 - SELLNUM)})
    #         return_exchange = read_from_exchange(exchange)
    #         continue
    #     if return_exchange['type'] == 'ack':
    #         if return_exchange['order_id'] == 51245:
    #             print("BUY ORDER ACKNOWLEDGED")
    #             return_exchange = read_from_exchange(exchange)
    #             continue
    #     elif return_exchange['type'] == 'fill':
    #         if return_exchange['order_id'] == 51245:
    #             SELLNUM -= return_exchange['size']
    #             print("BUY ORDER FULFILLED AT PRICE: " + str(return_exchange['price']) + " OF SIZE: " + str(
    #                 return_exchange['size']))
    #     return_exchange = read_from_exchange(exchange)

# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    prices = OrderedDict()
    ORDERS = 0
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    start_position = read_from_exchange(exchange)

    bond_market_maker(exchange)

    # try:
    #     while True:
    #         buy_bond(exchange, start_position, ORDERS, prices)
    # except KeyboardInterrupt:
    #     # f = open('BOND_HISTORY', 'w')
    #     # pickle.dump(repr(ORDERS), f)
    #     # f.close()
    #     pass

if __name__ == "__main__":
    main()