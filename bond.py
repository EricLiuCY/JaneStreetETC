# Decision for the market


def bond_pricing(buy_prices, sell_prices, min_profit):
    print("Decision got buy at " + str(buy_prices) + " and sell at " + str(sell_prices))
    fair_price = 1000

    buy_profit = 0
    short_profit = 0

    for buy_price in buy_prices:
        if buy_price < fair_price - min_profit:
            buy_profit = fair_price - buy_price

    for sell_price in sell_prices:
        if sell_price > fair_price + min_profit:
            short_profit = sell_price - fair_price

    if buy_profit > short_profit & buy_profit > 0:
        return "BUY", buy_profit
    elif short_profit > 0:
        return "SELL", short_profit
    else:
        return "NOTHING", 0


