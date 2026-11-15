"""
Curbe de compromis: cost (octeti/min) vs. eroare de pozitie,
cate o curba per strategie, pentru fiecare scenariu.
"""
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RADACINA = os.path.dirname(os.path.abspath(__file__))
REZULTATE = os.path.join(RADACINA, 'rezultate')

df = pd.read_csv(os.path.join(REZULTATE, 'reducere.csv'))
df['eticheta'] = df['strategie'] + ' (' + df['mod_receptor'] + ')'

SCENARII = ['linie', 'patrat', 'zigzag']
CULORI = {
    'Periodic (hold)': '#d62728',
    'Periodic (extrapolare)': '#ff7f0e',
    'ErrorThinning (hold)': '#1f77b4',
    'DeadReckoning (extrapolare)': '#2ca02c',
}

for metrica, nume_fis, titlu in [
    ('err_med', 'reducere_pareto_medie.png', 'eroare medie'),
    ('err_p95', 'reducere_pareto_p95.png', 'eroare P95'),
]:
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))

    for ax, s in zip(axes, SCENARII):
        sub = df[df['scenariu'] == s]
        for eticheta, grup in sub.groupby('eticheta'):
            g = grup.sort_values('octeti_pe_min')
            ax.plot(g['octeti_pe_min'], g[metrica], 'o-',
                    color=CULORI.get(eticheta, 'gray'),
                    label=eticheta, markersize=5, linewidth=1.5)

            for _, r in g.iterrows():
                ax.annotate(f"{r['parametru']:.0f}{r['unitate']}",
                            (r['octeti_pe_min'], r[metrica]),
                            textcoords='offset points', xytext=(4, 4),
                            fontsize=6, color=CULORI.get(eticheta, 'gray'))

        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('cost (octeți / min)')
        ax.set_ylabel(f'{titlu} (m)')
        ax.set_title(s)
        ax.grid(alpha=0.3, which='both')

    axes[0].legend(fontsize=8, loc='upper right')
    plt.suptitle(f'Compromis cost–precizie: {titlu}', fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(REZULTATE, nume_fis), dpi=130)
    print(f'salvat: {nume_fis}')
