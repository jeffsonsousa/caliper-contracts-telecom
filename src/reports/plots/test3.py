import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from io import StringIO

# Configuração de fonte estilo Times
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']

data = """scenario,tps_target,throughput
W1,5,3.9
W1,10,4.5
W1,15,4.4
W1,20,4.4
W1,25,4.4
W1,30,4.3
W1,35,4.4
W1,40,4.4
W2,10,7.0
W2,15,6.6
W2,20,14.3
W2,25,13.7
W2,30,14.7
W2,35,15.8
W2,40,16.6
W3,5,3.7
W3,10,7.1
W3,15,6.9
W3,20,14.9
W3,25,15.4
W3,30,19.1
W3,35,14.9
W3,40,15.6
W4,5,3.4
W4,10,5.75
W4,15,5.75
W4,20,6.15
W4,25,5.9
W4,30,5.9
W4,35,5.5
W4,40,4.6
W5,5,3.0
W5,10,3.0
W5,15,3.0
W5,20,3.0
W5,25,3.0
W5,30,3.0
W5,35,3.0
W5,40,3.0
W6,5,4.9
W6,10,7.0
W6,15,6.6
W6,20,14.3
W6,25,13.7
W6,30,14.7
W6,35,15.8
W6,40,16.6
W7,5,4.1
W7,10,6.7
W7,15,14.2
W7,20,15.3
W7,25,15.1
W7,30,15.9
W7,35,14.9
W7,40,14.9
"""

df = pd.read_csv(StringIO(data))

scenarios = [f'W{i}' for i in range(1, 8)]
tps_levels = sorted(df['tps_target'].unique())

# Paleta de cores suaves
colors = {
    'W1': '#b3cde3', 'W2': '#ccebc5', 'W3': '#dddddd',
    'W4': '#fbb4ae', 'W5': '#fed9a6', 'W6': '#decbe4', 'W7': '#e5d8bd',
}

fig = plt.figure(figsize=(12, 9), dpi=180)
ax = fig.add_subplot(111, projection='3d')

# Ajuste da distância da visualização para evitar cortes nos rótulos dos eixos
ax.dist = 11 

for xi, scen in enumerate(scenarios):
    sub = df[df['scenario'] == scen]
    xpos = np.full(len(sub), xi)
    ypos = [tps_levels.index(t) for t in sub['tps_target']]
    zpos = np.zeros(len(sub))
    dx = dy = np.full(len(sub), 0.6)
    dz = sub['throughput'].values

    ax.bar3d(
        xpos, ypos, zpos, dx, dy, dz,
        color=colors[scen], alpha=0.85,
        edgecolor='k', linewidth=0.3, shade=True
    )

    # Valores sobre as barras
    for x, y, h in zip(xpos, ypos, dz):
        ax.text(
            x + 0.3, y + 0.3, h + 0.5,
            f"{h:.1f}", ha='center', va='bottom',
            fontsize=7, color='black'
        )

# Títulos dos eixos com maior pad para não encostar nos números
ax.set_xlabel('Scenario (Workload)', labelpad=15)
ax.set_ylabel('Configured Load (TPS)', labelpad=15)
ax.set_zlabel('Throughput (tx/s)', labelpad=10)

ax.set_xticks(np.arange(len(scenarios)) + 0.3)
ax.set_xticklabels(scenarios)

ax.set_yticks(np.arange(len(tps_levels)) + 0.3)
ax.set_yticklabels([str(t) for t in tps_levels])

# Legenda lateral (proxy patches para garantir que apareça)
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=colors[s], edgecolor='k', label=s) for s in scenarios]
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.05, 0.9), title="Workloads")

ax.view_init(elev=35, azim=-115)

# O tight_layout as vezes falha em 3D, entao usamos bbox_inches="tight" no savefig
out_path = "throughput_3d_corrigido.png"
fig.savefig(out_path, bbox_inches="tight", pad_inches=0.3)
plt.show()