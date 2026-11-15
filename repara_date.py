"""
Recalculeaza coloanele n, e din lat/lon, folosind primul punct
ca referinta. Repara fisierele in care LOCAL_POSITION_NED a venit
prea rar si pozitia locala a ramas blocata.
"""
import os
import pandas as pd
import lpp

DATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'date')
SCENARII = ['linie', 'patrat', 'zigzag', 'hover']

for s in SCENARII:
    cale = os.path.join(DATE, f'{s}.csv')
    d = pd.read_csv(cale)
    d = d[d['lat'].abs() > 0.001].reset_index(drop=True)

    lat_ref, lon_ref = d['lat'].iloc[0], d['lon'].iloc[0]

    n_vechi = d['n'].copy()
    n_nou, e_nou = [], []
    for _, r in d.iterrows():
        dn, de = lpp.latlon_to_ne(r['lat'], r['lon'], lat_ref, lon_ref)
        n_nou.append(round(dn, 3))
        e_nou.append(round(de, 3))

    d['n'] = n_nou
    d['e'] = e_nou
    d.to_csv(cale, index=False)

    # cat de mult difera de ce era inainte
    dif = (n_vechi - d['n']).abs().max()
    print(f"{s:10} {len(d):5} randuri, n: {d['n'].min():7.1f} .. "
          f"{d['n'].max():7.1f} m, diferenta max fata de vechi: {dif:7.1f} m")
