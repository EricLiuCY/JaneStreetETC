import get_EMA as EMA


def etf_decision(etf, bond, gs, ms, wfc):

    bond_fair = EMA.get_EMA(bond[0], bond[1], bond[2])
    gs_fair = EMA.get_EMA(gs[0], gs[1], gs[2])
    ms_fair = EMA.get_EMA(ms[0], ms[1], ms[2])
    wfc_fair = EMA.get_EMA(wfc[0], wfc[1], wfc[2])

    etf_fair = 3*bond_fair + 2*gs_fair + 3*ms_fair + 2*wfc_fair + 100
    etf_buy_profit= etf_fair - etf[0]
    etf_sell_profit = etf[1] - etf_fair

    if int(etf_buy_profit) > 0 or int(etf_sell_profit) > 0:
        if etf_buy_profit > etf_sell_profit:
            return "BUY", etf_fair, bond_fair, gs_fair, ms_fair, wfc_fair
        else:
            return "SELL", etf_fair, bond_fair, gs_fair, ms_fair, wfc_fair
    else:
        return "NOTHING", etf_fair, bond_fair, gs_fair, ms_fair, wfc_fair
