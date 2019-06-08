import get_EMA as EMA


def etf_decision(etf, etf2, bond, bond2, gs, gs2, ms, ms2, wfc, wfc2, ema):

    bond_fair = EMA.get_EMA(bond, bond2, ex_EMA=ema)
    gs_fair = EMA.get_EMA(gs, gs2, ex_EMA=ema)
    ms_fair = EMA.get_EMA(ms, ms2, ex_EMA=ema)
    wfc_fair = EMA.get_EMA(wfc, wfc2, ex_EMA=ema)

    etf_fair = 3*bond_fair + 2*gs_fair + 3*ms_fair + 2*wfc_fair + 100 + 100
    etf_to_buy = etf  # TODO double check
    etf_to_sell = etf2

    if etf_to_buy > etf_fair:
        return "BUY", EMA
    elif etf_to_sell < etf_fair:
        return "SELL", EMA
    else:
        return "NOTHING", EMA