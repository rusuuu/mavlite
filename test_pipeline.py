import pandas as pd
import reducere, receptor, evaluare

d = pd.read_csv('date/zigzag.csv')
d = d[d['lat'].abs() > 0.001].reset_index(drop=True)

print(f"{'strategie':30} {'pach/min':>9} {'err_med':>9} {'err_p95':>9} {'err_max':>9} {'aoi_med':>9}")
print('-' * 80)

combinatii = [
    (reducere.Periodic(5), 'hold'),
    (reducere.Periodic(10), 'hold'),
    (reducere.ErrorThinning(10), 'hold'),
    (reducere.DeadReckoning(10), 'extrapolare'),
]

for s, mod in combinatii:
    pach = reducere.ruleaza(s, d)
    rec = receptor.Receptor(pach, mod=mod)
    m = evaluare.evalueaza(d, rec)
    print(f"{s.nume():30} {m['pachete_pe_min']:9.1f} {m['err_med']:9.2f} "
          f"{m['err_p95']:9.2f} {m['err_max']:9.2f} {m['aoi_med']:9.2f}")
