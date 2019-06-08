# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

import sys
import socket
import json
import random
from ETF_Arb import etf_decision

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

# ~~~~~============== Global ==============~~~~~

pos_bond = 0
pos_valbz = 0
pos_vale = 0
pos_gs = 0
pos_ms = 0
pos_wfc = 0
pos_xlf =0
ID_array = []


# xlf_buy   = None
# xlf_sell  = None
# xlf_ema   = None
#
# bond_buy  = None
# bond_sell = None
#
# valbz_buy = None
# valbz_sell = None
#
# vale_buy = None
# vale_sell = None
#
# gs_buy    = None
# gs_sell   = None
# ms_buy    = None
# ms_sell   = None
# wfc_buy   = None
# wfc_sell  = None

xlf_buy   = 0
xlf_sell  = 0
xlf_ema   = 0

bond_buy  = 0
bond_sell = 0

valbz_buy = 0
valbz_sell = 0

vale_buy = 0
vale_sell = 0

gs_buy    = 0
gs_sell   = 0
ms_buy    = 0
ms_sell   = 0
wfc_buy   = 0
wfc_sell  = 0

def generate_ID():

    ID = random.randint(1, 1000)
    if ID not in ID_array:
        return ID
    else:
        generate_ID()

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):

    data = json.loads(exchange.readline())

    if data['type'] == "fill":
        global pos_bond, pos_gs, pos_ms, pos_valbz, pos_vale, pos_wfc, pos_xlf
        symbol = data['symbol']
        dir = data['dir']
        size = data['size']

        if symbol == "BOND":
            if dir == "SELL":
                pos_bond -= size
            elif dir == "BUY":
                pos_bond += size

        # elif symbol == "VALBZ":
        #     if dir == "SELL":
        #         pos_valbz -= size
        #     elif dir == "BUY":
        #         pos_valbz += size
        #
        # elif symbol == "VALE":
        #     if dir == "SELL":
        #         pos_vale -= size
        #     elif dir == "BUY":
        #         pos_vale += size

        elif symbol == "GS":
            if dir == "SELL":
                pos_gs -= size
            elif dir == "BUY":
                pos_gs += size

        elif symbol == "MS":
            if pos_ms == "SELL":
                pos_bond -= size
            elif dir == "BUY":
                pos_ms += size

        elif symbol == "WFC":
            if dir == "SELL":
                pos_wfc -= size
            elif dir == "BUY":
                pos_wfc += size

        elif symbol == "XLF":
            if dir == "SELL":
                pos_xlf -= size
            elif dir == "BUY":
                pos_xlf += size

    return json.loads(exchange.readline())


def redo_position(exchange):
    if pos_bond > 70 | pos_gs > 80 | pos_ms > 70 | pos_wfc > 80:
        write_to_exchange(exchange,
                          {"type": "convert", "order_id": generate_ID(), "symbol": "XLF", "dir": "BUY", "size": 10})
    if pos_bond < -70 | pos_gs < -80 | pos_ms < -70 | pos_wfc < -80:
        write_to_exchange(exchange,
                          {"type": "convert", "order_id": generate_ID(), "symbol": "XLF", "dir": "SELL", "size": 10})

    if pos_xlf < 90:
        write_to_exchange(exchange,
                          {"type": "convert", "order_id": generate_ID(), "symbol": "XLF", "dir": "BUY", "size": 10})
    if pos_xlf > 90:
        write_to_exchange(exchange,
                          {"type": "convert", "order_id": generate_ID(), "symbol": "XLF", "dir": "SELL", "size": 10})


# ~~~~~============== MAIN LOOP ==============~~~~~

def sum_list(input):
    tot = 0
    for item in input:
        tot += item[0]
    return tot

def dispatcher_init(exchange):
    message = read_from_exchange(exchange)
    type = message['type']
    global bond_buy_count, bond_sell_count

    global xlf_buy, xlf_ema, xlf_sell
    global bond_buy, bond_sell
    global gs_buy, gs_sell
    global ms_buy, ms_sell
    global wfc_buy, wfc_sell

    if type == "book":
        symbol = message['symbol']
        sell = message['buy']
        buy = message['sell']

        if symbol == "BOND":
            bond_buy = sum_list(buy)
            bond_sell = sum_list(sell)

        elif symbol == "GS":
            gs_buy = sum_list(buy)
            gs_sell = sum_list(sell)

        elif symbol == "MS":
            ms_buy = sum_list(buy)
            ms_sell = sum_list(sell)

        elif symbol == "WFC":
            wfc_buy = sum_list(buy)
            wfc_sell = sum_list(sell)

        elif symbol == "XLF":
            xlf_buy = sum_list(buy)
            xlf_sell = sum_list(sell)

def dispatcher(exchange):
    message = read_from_exchange(exchange)
    type = message['type']
    global bond_buy_count, bond_sell_count

    global xlf_buy, xlf_ema, xlf_sell
    global bond_buy, bond_sell
    global gs_buy, gs_sell
    global ms_buy, ms_sell
    global wfc_buy, wfc_sell

    if type == "book":
        symbol = message['symbol']
        sell = message['buy']
        buy = message['sell']

        if symbol == "BOND":
            bond_buy = sum_list(buy)
            bond_sell = sum_list(sell)

        elif symbol == "GS":
            gs_buy = sum_list(buy)
            gs_sell = sum_list(sell)

        elif symbol == "MS":
            ms_buy = sum_list(buy)
            ms_sell = sum_list(sell)

        elif symbol == "WFC":
            wfc_buy = sum_list(buy)
            wfc_sell = sum_list(sell)

        elif symbol == "XLF":
            xlf_buy = sum_list(buy)
            xlf_sell = sum_list(sell)

    decision, ema = etf_decision(xlf_buy, xlf_sell, bond_buy, bond_sell, gs_buy, gs_sell, ms_buy, ms_sell, wfc_buy, wfc_sell)


    if decision == 'BUY':
        print("Decision to Buy")
        write_to_exchange(exchange,
                          {"type": "add", "order_id": generate_ID(), "symbol": "XLF", "dir": "BUY",
                           "price": xlf_buy + 1, "size": 10})

        write_to_exchange(exchange,
                          {"type": "convert", "order_id": generate_ID(), "symbol": "XLF", "dir": "SELL", "size": 10})

        write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "BOND", "dir": "SELL",
                                     "price": bond_sell - 1,"size": 30})

        write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "GS", "dir": "SELL",
                                     "price": gs_sell - 1, "size": 20})

        write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "MS", "dir": "SELL",
                                     "price": ms_sell - 1, "size": 30})

        write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "WFC", "dir": "SELL",
                                     "price": wfc_sell - 1,
                                     "size": 20})

    if decision == 'SELL':
        print("Decision to Sell")

        write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "BOND", "dir": "BUY",
                                     "price": bond_buy + 1,
                                     "size": 30})

        write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "GS", "dir": "BUY",
                                     "price": gs_buy + 1, "size": 20})

        write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "MS", "dir": "BUY",
                                     "price": ms_buy + 1, "size": 30})

        write_to_exchange(exchange, {"type": "add", "order_id": generate_ID(), "symbol": "WFC", "dir": "BUY",
                                     "price": gs_buy + 1, "size": 20})

        write_to_exchange(exchange,
                          {"type": "convert", "order_id": generate_ID(), "symbol": "XLF", "dir": "BUY",
                           "size": 10})

        write_to_exchange(exchange,
                          {"type": "add", "order_id": generate_ID(), "symbol": "XLF", "dir": "SELL",
                           "price": xlf_sell,
                           "size": 10})

# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})

    global xlf_buy, xlf_ema, xlf_sell
    global bond_buy, bond_sell
    global gs_buy, gs_sell
    global ms_buy, ms_sell
    global wfc_buy, wfc_sell

    # while xlf_buy is None or xlf_ema is None or bond_buy is None or bond_sell is None or gs_buy is None or gs_sell is None or ms_buy is None\
    #         or ms_sell is None or wfc_buy is None or wfc_sell is None:
    #     print("waiting to begin")
    #     dispatcher_init(exchange)

    while xlf_buy !=0 or xlf_ema !=0 or bond_buy !=0 or bond_sell !=0 or gs_buy !=0 or gs_sell !=0 or ms_buy !=0\
            or ms_sell !=0 or wfc_buy !=0 or wfc_sell !=0:
        print("waiting to begin")
        dispatcher_init(exchange)

    while True:
        print("begins")
        redo_position(exchange)
        dispatcher(exchange)


if __name__ == "__main__":
    while True:
        main()

