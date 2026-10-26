import sys
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

scenarii = ['linie', 'patrat', 'zigzag', 'hover']
fig, axes = plt.subplots(1, 4, figsize=(18, 4.5))

for ax, s in zip(axes, scenarii):
    d = pd.read_csv(f'{s}.csv')
    ax.plot(d['e'], d['n'], linewidth=1)
    ax.plot(d['e'].iloc[0], d['n'].iloc[0], 'go', label='start')
    ax.plot(d['e'].iloc[-1], d['n'].iloc[-1], 'ro', label='stop')
    ax.set_title(f'{s} ({len(d)} pct, {d["t"].iloc[-1]:.0f}s)')
    ax.set_xlabel('est (m)')
    ax.set_ylabel('nord (m)')
    ax.axis('equal')
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig('traiectorii.png', dpi=120)
print("Salvat in traiectorii.png")

