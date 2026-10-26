import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATE = os.path.join(RADACINA, 'date')

import pandas as pd
import lpp

SCENARII = ['linie', 'patrat', 'zigzag', 'hover']

print(f"{'scenariu':10} {'metoda':14} {'octeti':>7} {'err_med':>9} {'err_p95':>9} {'err_max':>9}")
print("-" * 62)

for s in SCENARII:
    d = pd.read_csv(os.path.join(DATE, f'{s}.csv'))
    d = d[d['lat'].abs() > 0.001].reset_index(drop=True)
    lat_ref = d['lat'].iloc[0]
    lon_ref = d['lon'].iloc[0]

    for nume in ['standard', 'custom', 'delta']:
        erori = []
        n_octeti = 0
        for _, r in d.iterrows():
            if nume == 'standard':
                p = lpp.encode_lpp_standard(r['lat'], r['lon'], r['alt'])
                lat2, lon2, _ = lpp.decode_lpp_standard(p)
            elif nume == 'custom':
                p = lpp.encode_lpp_custom(r['lat'], r['lon'], r['alt'])
                lat2, lon2, _ = lpp.decode_lpp_custom(p)
            else:
                p = lpp.encode_delta(r['lat'], r['lon'], r['alt'], lat_ref, lon_ref)
                lat2, lon2, _ = lpp.decode_delta(p, lat_ref, lon_ref)
            n_octeti = len(p)
            erori.append(lpp.distanta(r['lat'], r['lon'], lat2, lon2))

        e = pd.Series(erori)
        print(f"{s:10} {nume:14} {n_octeti:>7} {e.mean():>9.2f} "
              f"{e.quantile(0.95):>9.2f} {e.max():>9.2f}")
