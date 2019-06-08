def get_EMA(buy_list, sell_list, ex_EMA = None, days = 5):

    # buy_price = sum(buy_list) / len(buy_list)
    # sell_price = sum(sell_list) / len(sell_list)
    # price = (buy_price + sell_price) / 2

    price = (buy_list + sell_list) / 2

    w_mult = 2 / (days + 1)

    if ex_EMA is None:
        ex_EMA = price

    EMA = (price * w_mult) + (ex_EMA * (1 - w_mult))
    return EMA

