# Decision for the market


def bond_pricing(cur_price, min_profit):
    fair_price = 1000
    min_profit = 10

    decision = None
    est_profit = None

    if cur_price < fair_price - min_profit:
        decision = "buy"
        est_profit = fair_price - cur_price

    if cur_price > fair_price + min_profit:
        decision = "sell"
        est_profit = cur_price - fair_price

    return decision, est_profit








