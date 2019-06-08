import get_EMA as EMA


def etf_decision(etf, bond, gs, ms, wfc):

    bond_fair = EMA.get_EMA(bond[0], bond[1], bond[2])
    gs_fair = EMA.get_EMA(gs[0], gs[1], gs[2])
    ms_fair = EMA.get_EMA(ms[0], ms[1], ms[2])
    wfc_fair = EMA.get_EMA(wfc[0], wfc[1], wfc[2])

    etf_fair = 3*bond_fair + 2*gs_fair + 3*ms_fair + 2*wfc_fair + 100 + 100
    etf_to_buy = etf[0]
    etf_to_sell = etf[1]

    if etf_to_buy > etf_fair:
        return "BUY", etf_fair, bond_fair, gs_fair, ms_fair, wfc_fair
    elif etf_to_sell < etf_fair:
        return "SELL", etf_fair, bond_fair, gs_fair, ms_fair, wfc_fair
    else:
        return "NOTHING", etf_fair, bond_fair, gs_fair, ms_fair, wfc_fair


