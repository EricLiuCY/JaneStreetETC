import get_EMA as EMA


def etf_decision(etf, bond, gs, ms, wfc):

    bond_fair = EMA.get_EMA(bond[0], bond[1])
    gs_fair = EMA.get_EMA(gs[0], gs[0])
    ms_fair = EMA.get_EMA(ms[0], ms[0])
    wfc_fair = EMA.get_EMA(wfc[0], wfc[0])

    etf_fair = 3*bond_fair + 2*gs_fair + 3*ms_fair + 2*wfc_fair + 100 + 10
    etf_price = etf[0]  # TODO double check

    if etf_price < etf_fair:
        return "BUY", EMA
    elif etf_price > etf_fair:
        return "SELL", EMA
    else:
        return "NOTHING", EMA

