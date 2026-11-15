"""
Verifica strategiile de reducere: cate pachete trimite fiecare,
pe fiecare scenariu.
"""
import pandas as pd
import os
import reducere

DATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'date')
SCENARII = ['linie', 'patrat', 'zigzag', 'hover']

print(f"{'scenariu':10} {'strategie':30} {'pachete':>8} {'pach/min':>9}")
print('-' * 60)

for s in SCENARII:
    d = pd.read_csv(os.path.join(DATE, f'{s}.csv'))
    d = d[d['lat'].abs() > 0.001].reset_index(drop=True)
    durata = d['t'].iloc[-1] - d['t'].iloc[0]
    total = len(d)

    strategii = [
        reducere.Periodic(5),
        reducere.Periodic(10),
        reducere.ErrorThinning(10),
        reducere.DeadReckoning(10),
    ]

    for strat in strategii:
        pach = reducere.ruleaza(strat, d)
        print(f"{s:10} {strat.nume():30} {len(pach):8} "
              f"{len(pach)/durata*60:9.1f}")

    print(f"{'':10} {'(ground truth)':30} {total:8} "
          f"{total/durata*60:9.1f}")
    print()
