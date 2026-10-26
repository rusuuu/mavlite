"""
Grafice pentru contributia 1: costul codarii.
  1. octeti vs. eroare, pentru cele trei metode
  2. limita de raza a delta-encoding
  3. costul keyframe-urilor periodice
"""
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import lpp

RADACINA = os.path.dirname(os.path.abspath(__file__))
DATE = os.path.join(RADACINA, 'date')
REZULTATE = os.path.join(RADACINA, 'rezultate')
os.makedirs(REZULTATE, exist_ok=True)

SCENARII = ['linie', 'patrat', 'zigzag', 'hover']
METODE = ['standard', 'custom', 'delta']
CULORI = {'standard': '#d62728', 'custom': '#1f77b4', 'delta': '#2ca02c'}


def incarca(scenariu):
    cale = os.path.join(DATE, f'{scenariu}.csv')
    if not os.path.exists(cale):
        cale = os.path.join(RADACINA, f'{scenariu}.csv')   # fallback
    d = pd.read_csv(cale)
    return d[d['lat'].abs() > 0.001].reset_index(drop=True)


def codeaza(metoda, r, lat_ref, lon_ref):
    if metoda == 'standard':
        p = lpp.encode_lpp_standard(r['lat'], r['lon'], r['alt'])
        lat2, lon2, _ = lpp.decode_lpp_standard(p)
    elif metoda == 'custom':
        p = lpp.encode_lpp_custom(r['lat'], r['lon'], r['alt'])
        lat2, lon2, _ = lpp.decode_lpp_custom(p)
    else:
        p = lpp.encode_delta(r['lat'], r['lon'], r['alt'], lat_ref, lon_ref)
        lat2, lon2, _ = lpp.decode_delta(p, lat_ref, lon_ref)
    return len(p), lpp.distanta(r['lat'], r['lon'], lat2, lon2)

# ---- 1. octeti vs. eroare ------------------------------------------------

rezultate = {m: {'octeti': [], 'erori': []} for m in METODE}

for s in SCENARII:
    d = incarca(s)
    lat_ref, lon_ref = d['lat'].iloc[0], d['lon'].iloc[0]
    for m in METODE:
        for _, r in d.iterrows():
            n, err = codeaza(m, r, lat_ref, lon_ref)
            rezultate[m]['octeti'].append(n)
            rezultate[m]['erori'].append(err)

fig, ax = plt.subplots(figsize=(7, 5))

for m in METODE:
    e = pd.Series(rezultate[m]['erori'])
    o = pd.Series(rezultate[m]['octeti'])
    x = o.mean()

    eticheta = f'LPP {m}' if m != 'delta' else 'delta'
    if o.nunique() > 1:
        eticheta += f' ({o.min()}–{o.max()} B)'

    ax.scatter(x, e.mean(), s=140, color=CULORI[m], zorder=3)

    # bara verticala: eroarea intre percentilele 5 si 95
    # bara orizontala: dimensiunea intre percentilele 5 si 95 (daca variaza)
    ax.errorbar(x, e.mean(),
                yerr=[[e.mean() - e.quantile(0.05)],
                      [e.quantile(0.95) - e.mean()]],
                xerr=[[x - o.quantile(0.05)],
                      [o.quantile(0.95) - x]] if o.nunique() > 1 else None,
                color=CULORI[m], capsize=5, zorder=2)

    text_octeti = f'{x:.0f} B' if o.nunique() == 1 else f'{x:.1f} B med.'
    offset = (12, -28) if m == 'delta' else (12, 0)
    ax.annotate(f'{eticheta}\n{e.mean():.2f} m\n{text_octeti}',
                (x, e.mean()), textcoords='offset points',
                xytext=(12, 0), fontsize=9, va='center')

# referinta MAVLink
ax.axvline(40, color='gray', linestyle='--', alpha=0.6)
ax.text(40, ax.get_ylim()[1] * 0.5, ' MAVLink\n (40 B)',
        color='gray', fontsize=9, va='center')

ax.set_yscale('log')
ax.set_xlabel('octeți per pachet')
ax.set_ylabel('eroare de poziție (m, scară log)')
ax.set_title('Costul codării: dimensiune vs. precizie')
ax.set_xlim(0, 46)
ax.grid(alpha=0.3, which='both')
plt.tight_layout()
plt.savefig(os.path.join(REZULTATE, 'encodere_octeti_vs_eroare.png'), dpi=140)
print('salvat: encodere_octeti_vs_eroare.png')


# ---- 2. limita de raza a delta-encoding ----------------------------------

lat_ref, lon_ref = -35.363262, 149.165237
distante = list(range(100, 5100, 100))
erori_raza = []

for dm in distante:
    lat, lon = lpp.ne_to_latlon(dm, 0, lat_ref, lon_ref)
    p = lpp.encode_delta(lat, lon, 20.0, lat_ref, lon_ref)
    lat2, lon2, _ = lpp.decode_delta(p, lat_ref, lon_ref)
    erori_raza.append(lpp.distanta(lat, lon, lat2, lon2))

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(distante, erori_raza, color='#2ca02c', linewidth=2)
ax.axvline(3276.7, color='red', linestyle='--', alpha=0.7)
ax.text(3276.7, max(erori_raza) * 0.6, ' limita teoretică\n 3276,7 m',
        color='red', fontsize=9)
ax.set_xlabel('distanța față de punctul de referință (m)')
ax.set_ylabel('eroare de reconstrucție (m)')
ax.set_title('Limita de rază a delta-encoding (2 octeți, unitate 0,1 m)')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(REZULTATE, 'delta_limita_raza.png'), dpi=140)
print('salvat: delta_limita_raza.png')


# ---- 3. costul keyframe-urilor -------------------------------------------

n_values = list(range(1, 101))
cost = [(11 + (n - 1) * 8) / n for n in n_values]

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(n_values, cost, color='#2ca02c', linewidth=2)
ax.axhline(8, color='gray', linestyle='--', alpha=0.7)
ax.text(60, 8.08, 'delta pur (8 B)', color='gray', fontsize=9)
ax.axhline(11, color='#d62728', linestyle='--', alpha=0.7)
ax.text(60, 11.1, 'LPP standard (11 B)', color='#d62728', fontsize=9)
for n in (10, 20, 50):
    ax.plot(n, (11 + (n - 1) * 8) / n, 'o', color='black', ms=5)
    ax.annotate(f'{(11 + (n-1)*8)/n:.2f} B',
                (n, (11 + (n - 1) * 8) / n), textcoords='offset points',
                xytext=(6, 8), fontsize=8)
ax.set_xlabel('keyframe la fiecare N pachete')
ax.set_ylabel('cost mediu (octeți / pachet)')
ax.set_title('Costul keyframe-urilor periodice')
ax.set_ylim(7.5, 11.5)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(REZULTATE, 'keyframe_cost.png'), dpi=140)
print('salvat: keyframe_cost.png')
