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

def buy_bond(exchange, start_position, ORDERS, prices):
    MAX = 30
    return_exchange = read_from_exchange(exchange)
    # if return_exchange['type'] == 'book':
    #     if return_exchange['symbol'] == 'BOND':
            # print("GOT BOND: ")
            # print("The exchange replied:", return_exchange, file=sys.stderr)
            # max_bond_buy = 0
            # max_bond_sell = 0
            # bond_buy = -1
            # bond_sell = 10000
            # for i in range(len(return_exchange['buy'])):
            #     bond_buy = max(return_exchange['buy'][i][0], bond_buy)
            #     if bond_buy == return_exchange['buy'][i][0]:
            #         max_bond_buy = return_exchange['buy'][i][1]
            # for i in range(len(return_exchange['sell'])):
            #     bond_sell = min(return_exchange['sell'][i][0], bond_sell)
            #     if bond_sell == return_exchange['sell'][i][0]:
            #         max_bond_sell = return_exchange['sell'][i][1]
            # (decision, profitps) = bond_pricing(bond_sell, bond_buy, 1)
            #
            # if decision == "SELL":
            #     print("DECIDING TO SELL AT " + str(bond_buy))
            #     print("BOOK REPLY WAS", return_exchange, file=sys.stderr)
            #     write_to_exchange(exchange, {"type": "add", "order_id": ORDERS, "symbol": "BOND", "dir": "SELL", "price": bond_buy, "size": max_bond_buy})
            #     buy_return = read_from_exchange(exchange)
            #     counter = 0
            #     while True:
            #         if counter > MAX:
            #             ORDERS +=1
            #             print("TIMED OUT")
            #             return
            #         if buy_return['type'] != 'FILL':
            #             print("SELL REPLY:", buy_return, file=sys.stderr)
            #             buy_return = read_from_exchange(exchange)
            #         else:
            #             if buy_return['order_id'] == ORDERS:
            #                 print("FILL SELL REPLY:", buy_return, file=sys.stderr)
            #                 ORDERS += 1
            #                 return
            #             else:
            #                 print("OTHER FILL: ", buy_return, file=sys.stderr)
            #                 buy_return = read_from_exchange(exchange)
            #         counter += 1
            # if decision == "BUY":
            #     print("DECIDING TO BUY AT " + str(bond_sell))
            #     print("BOOK REPLY WAS", return_exchange, file=sys.stderr)
            #     write_to_exchange(exchange, {"type": "add", "order_id": ORDERS, "symbol": "BOND", "dir": "BUY", "price": bond_sell, "size": max_bond_sell})
            #     sell_return = read_from_exchange(exchange)
            #     counter = 0
            #     while True:
            #         if counter > MAX:
            #             ORDERS +=1
            #             print("TIMED OUT")
            #             return
            #         if sell_return['type'] != 'FILL':
            #             print("BUY REPLY:", sell_return, file=sys.stderr)
            #             sell_return = read_from_exchange(exchange)
            #         else:
            #             if sell_return['order_id'] == ORDERS:
            #                 print("FILL BUY REPLY:", sell_return, file=sys.stderr)
            #                 ORDERS += 1
            #                 return
            #             else:
            #                 print("OTHER FILL: ", sell_return, file=sys.stderr)
            #                 sell_return = read_from_exchange(exchange)
            #         counter += 1
            #
            # if decision == "NOTHING":
            #     print("DOING NOTHING FOR REPLY: ")
            #     print("The exchange replied:", return_exchange, file=sys.stderr)
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
            if return_exchange['order_id'] == 23491:
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
            if return_exchange['order_id'] == 93495:
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

def main():
    prices = OrderedDict()
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
            buy_bond(exchange, start_position, ORDERS, prices)
    except KeyboardInterrupt:
        # f = open('BOND_HISTORY', 'w')
        # pickle.dump(repr(ORDERS), f)
        # f.close()
        pass

if __name__ == "__main__":
    main()