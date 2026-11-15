"""
Ruleaza toate combinatiile de scenariu x strategie x prag
si salveaza rezultatele in rezultate/reducere.csv
"""
import os
import pandas as pd
import reducere, receptor, evaluare

RADACINA = os.path.dirname(os.path.abspath(__file__))
DATE = os.path.join(RADACINA, 'date')
REZULTATE = os.path.join(RADACINA, 'rezultate')
os.makedirs(REZULTATE, exist_ok=True)

SCENARII = ['linie', 'patrat', 'zigzag', 'hover']

# parametrii fixati INAINTE de a vedea rezultatele
PERIOADE = [1, 2, 5, 10, 20, 30]        # secunde
PRAGURI  = [1, 2, 5, 10, 20]            # metri

# octeti per pachet, ca sa putem compara costul real
OCTETI_POZITIE = 8       # delta-encoding: n, e, alt
OCTETI_VITEZA  = 4       # vn, ve pe 2 octeti fiecare


def construieste_strategii():
    """Lista de (strategie, mod_receptor, octeti_per_pachet)."""
    lista = []
    for T in PERIOADE:
        lista.append((reducere.Periodic(T), 'hold', OCTETI_POZITIE))
        lista.append((reducere.Periodic(T), 'extrapolare',
                      OCTETI_POZITIE + OCTETI_VITEZA))
    for d in PRAGURI:
        lista.append((reducere.ErrorThinning(d), 'hold', OCTETI_POZITIE))
        lista.append((reducere.DeadReckoning(d), 'extrapolare',
                      OCTETI_POZITIE + OCTETI_VITEZA))
    return lista


randuri = []

for scenariu in SCENARII:
    d = pd.read_csv(os.path.join(DATE, f'{scenariu}.csv'))
    d = d[d['lat'].abs() > 0.001].reset_index(drop=True)
    durata = d['t'].iloc[-1] - d['t'].iloc[0]

    for strat, mod, octeti in construieste_strategii():
        pach = reducere.ruleaza(strat, d)
        rec = receptor.Receptor(pach, mod=mod)
        m = evaluare.evalueaza(d, rec)
        if m is None:
            continue

        randuri.append({
            'scenariu': scenariu,
            'strategie': type(strat).__name__,
            'parametru': getattr(strat, 'perioada', None) or strat.prag,
            'unitate': 's' if hasattr(strat, 'perioada') else 'm',
            'mod_receptor': mod,
            'pachete': m['pachete'],
            'pachete_pe_min': round(m['pachete_pe_min'], 2),
            'octeti_pe_min': round(m['pachete_pe_min'] * octeti, 1),
            'err_med': round(m['err_med'], 2),
            'err_p95': round(m['err_p95'], 2),
            'err_max': round(m['err_max'], 2),
            'aoi_med': round(m['aoi_med'], 2),
            'aoi_max': round(m['aoi_max'], 2),
            'durata_s': round(durata, 1),
        })

df = pd.DataFrame(randuri)
cale = os.path.join(REZULTATE, 'reducere.csv')
df.to_csv(cale, index=False)
print(f"Salvat {len(df)} rezultate in rezultate/reducere.csv\n")

# rezumat pe ecran: cea mai buna strategie pentru fiecare buget de octeti
for scenariu in SCENARII:
    sub = df[df['scenariu'] == scenariu].sort_values('octeti_pe_min')
    print(f"=== {scenariu} ===")
    print(f"{'strategie':20} {'param':>7} {'mod':>12} {'B/min':>8} "
          f"{'err_med':>8} {'err_p95':>8} {'aoi_med':>8}")
    for _, r in sub.iterrows():
        print(f"{r['strategie']:20} {r['parametru']:>5}{r['unitate']:<2} "
              f"{r['mod_receptor']:>12} {r['octeti_pe_min']:>8.1f} "
              f"{r['err_med']:>8.2f} {r['err_p95']:>8.2f} {r['aoi_med']:>8.2f}")
    print()
