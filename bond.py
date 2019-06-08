# Decision for the market


def bond_pricing(buy_price, sell_price, min_profit):
    print("Decision got buy at " + str(buy_price) + " and sell at " + str(sell_price))
    fair_price = 1000

    buy_profit = 0
    short_profit = 0

    if buy_price < fair_price - min_profit:
        buy_profit = fair_price - buy_price
        if buy_profit <= min_profit:
            return "NOTHING", 0
    elif sell_price > fair_price + min_profit:
        short_profit = sell_price - fair_price
        if short_profit <= min_profit:
            return "NOTHING", 0
    else:
        return "NOTHING", 0


    if buy_profit > short_profit:
        return "BUY", buy_profit
    else:
        return "SELL", short_profit


