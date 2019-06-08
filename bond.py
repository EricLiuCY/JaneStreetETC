# Decision for the market


def bond_pricing(buy_price, sell_price, min_profit):
    fair_price = 1000

    buy_profit = None
    short_profit = None

    if buy_price < fair_price - min_profit:
        buy_profit = fair_price - buy_price

    if sell_price > fair_price + min_profit:
        short_profit = sell_price - fair_price

    if buy_profit > short_profit:
        return "BUY", buy_profit
    else:
        return "SELL", short_profit


