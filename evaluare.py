"""
Compara traiectoria reconstruita la receptor cu ground truth-ul
si calculeaza metricile de performanta.
"""
import math
import pandas as pd


def evalueaza(date, receptor):
    """
    date: DataFrame cu ground truth (coloanele t, n, e)
    receptor: obiect Receptor, deja incarcat cu pachetele trimise

    Returneaza un dict cu metricile.
    """
    erori = []
    varste = []

    for _, r in date.iterrows():
        t, n, e = r['t'], r['n'], r['e']

        estimare = receptor.pozitie_la(t)
        if estimare is None:
            continue              # inainte de primul pachet nu masuram
        n_est, e_est = estimare
        erori.append(math.hypot(n - n_est, e - e_est))

        v = receptor.varsta_la(t)
        if v is not None:
            varste.append(v)

    if not erori:
        return None

    er = pd.Series(erori)
    va = pd.Series(varste)
    durata = date['t'].iloc[-1] - date['t'].iloc[0]

    return {
        'pachete': len(receptor.pachete),
        'pachete_pe_min': len(receptor.pachete) / durata * 60,
        'err_med': er.mean(),
        'err_p95': er.quantile(0.95),
        'err_max': er.max(),
        'aoi_med': va.mean() if len(va) else float('nan'),
        'aoi_max': va.max() if len(va) else float('nan'),
    }
