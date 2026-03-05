import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from io import StringIO

data = """scenario,tps_target,report,round,avg,p95,p99,throughput,succ,fail
W1,5,src/reports/W1/report_5TPS_20260115_054313.html,W1_RegisterAsset,2.53,,,3.9,50.0,0.0
W1,10,src/reports/W1/report_10TPS_20260115_054341.html,W1_RegisterAsset,3.96,,,4.5,50.0,0.0
W1,15,src/reports/W1/report_15TPS_20260115_054409.html,W1_RegisterAsset,4.92,,,4.4,50.0,0.0
W1,20,src/reports/W1/report_20TPS_20260115_054437.html,W1_RegisterAsset,5.37,,,4.4,50.0,0.0
W1,25,src/reports/W1/report_25TPS_20260115_054505.html,W1_RegisterAsset,5.61,,,4.4,50.0,0.0
W1,30,src/reports/W1/report_30TPS_20260115_054533.html,W1_RegisterAsset,5.96,,,4.3,50.0,0.0
W1,35,src/reports/W1/report_35TPS_20260115_054601.html,W1_RegisterAsset,6.02,,,4.4,50.0,0.0
W1,40,src/reports/W1/report_40TPS_20260115_054629.html,W1_RegisterAsset,6.06,,,4.4,50.0,0.0
W2,5,src/reports/W6/report_5TPS_20260115_074133.html,W2_HireAsset,2.57,,,3.4,50.0,0.0
W2,10,src/reports/W6/report_10TPS_20260115_074133.html,W2_HireAsset,2.57,,,7.0,50.0,0.0
W2,15,src/reports/W6/report_15TPS_20260115_074157.html,W2_HireAsset,2.25,,,6.6,50.0,0.0
W2,20,src/reports/W6/report_20TPS_20260115_074217.html,W2_HireAsset,2.77,,,14.3,50.0,0.0
W2,25,src/reports/W6/report_25TPS_20260115_074237.html,W2_HireAsset,2.17,,,13.7,50.0,0.0
W2,30,src/reports/W6/report_30TPS_20260115_074257.html,W2_HireAsset,2.28,,,14.7,50.0,0.0
W2,35,src/reports/W6/report_35TPS_20260115_074317.html,W2_HireAsset,2.15,,,15.8,50.0,0.0
W2,40,src/reports/W6/report_40TPS_20260115_074337.html,W2_HireAsset,1.99,,,16.6,50.0,0.0
W3,5,src/reports/W3/report_5TPS_20260115_075629.html,W3_PayAsset,1.91,,,3.7,50.0,0.0
W3,10,src/reports/W3/report_10TPS_20260115_075653.html,W3_PayAsset,1.81,,,7.1,0.0,50.0
W3,15,src/reports/W3/report_15TPS_20260115_075717.html,W3_PayAsset,1.79,,,6.9,0.0,50.0
W3,20,src/reports/W3/report_20TPS_20260115_075737.html,W3_PayAsset,1.51,,,14.9,0.0,50.0
W3,25,src/reports/W3/report_25TPS_20260115_075757.html,W3_PayAsset,1.31,,,15.4,0.0,50.0
W3,30,src/reports/W3/report_30TPS_20260115_075817.html,W3_PayAsset,1.41,,,19.1,0.0,50.0
W3,35,src/reports/W3/report_35TPS_20260115_075837.html,W3_PayAsset,1.31,,,14.9,0.0,50.0
W3,40,src/reports/W3/report_40TPS_20260115_075857.html,W3_PayAsset,1.1,,,15.6,0.0,50.0
W4,5,src/reports/W4/report_5TPS_20260115_072641.html,W4_CreateServiceRecord,2.25,,,2.9,15.0,0.0
W4,5,src/reports/W4/report_5TPS_20260115_073137.html,W4_CreateServiceRecord,2.08,,,3.9,50.0,0.0
W4,10,src/reports/W4/report_10TPS_20260115_072701.html,W4_CreateServiceRecord,2.5,,,4.7,15.0,0.0
W4,10,src/reports/W4/report_10TPS_20260115_073201.html,W4_CreateServiceRecord,2.63,,,6.8,50.0,0.0
W4,15,src/reports/W4/report_15TPS_20260115_072721.html,W4_CreateServiceRecord,2.81,,,4.6,15.0,0.0
W4,15,src/reports/W4/report_15TPS_20260115_073225.html,W4_CreateServiceRecord,3.36,,,6.9,50.0,0.0
W4,20,src/reports/W4/report_20TPS_20260115_072757.html,W4_CreateServiceRecord,2.46,,,5.3,15.0,0.0
W4,20,src/reports/W4/report_20TPS_20260115_073305.html,W4_CreateServiceRecord,3.6,,,7.0,50.0,0.0
W4,25,src/reports/W4/report_25TPS_20260115_072817.html,W4_CreateServiceRecord,2.72,,,5.0,15.0,0.0
W4,25,src/reports/W4/report_25TPS_20260115_073329.html,W4_CreateServiceRecord,4.01,,,6.8,50.0,0.0
W4,30,src/reports/W4/report_30TPS_20260115_072837.html,W4_CreateServiceRecord,2.82,,,4.9,15.0,0.0
W4,30,src/reports/W4/report_30TPS_20260115_073353.html,W4_CreateServiceRecord,4.18,,,6.9,50.0,0.0
W4,35,src/reports/W4/report_35TPS_20260115_072857.html,W4_CreateServiceRecord,3.29,,,4.3,15.0,0.0
W4,35,src/reports/W4/report_35TPS_20260115_073417.html,W4_CreateServiceRecord,4.43,,,6.7,50.0,0.0
W4,40,src/reports/W4/report_40TPS_20260115_072917.html,W4_CreateServiceRecord,3.06,,,4.6,15.0,0.0
W5,5,src/reports/W5/report_5TPS_20260115_073917.html,W5_CreateServiceRecordWithAssets,4.51,,,3.0,50.0,0.0
W5,10,src/reports/W5/report_10TPS_20260115_073917.html,W5_CreateServiceRecordWithAssets,4.31,,,3.0,50.0,0.0
W5,15,src/reports/W5/report_15TPS_20260115_073917.html,W5_CreateServiceRecordWithAssets,3.91,,,3.0,50.0,0.0
W5,20,src/reports/W5/report_20TPS_20260115_073917.html,W5_CreateServiceRecordWithAssets,4.61,,,3.0,50.0,0.0
W5,25,src/reports/W5/report_25TPS_20260115_073917.html,W5_CreateServiceRecordWithAssets,3.71,,,3.0,50.0,0.0
W5,30,src/reports/W5/report_30TPS_20260115_073917.html,W5_CreateServiceRecordWithAssets,4.41,,,3.0,50.0,0.0
W5,35,src/reports/W5/report_35TPS_20260115_073917.html,W5_CreateServiceRecordWithAssets,4.21,,,3.0,50.0,0.0
W5,40,src/reports/W5/report_40TPS_20260115_073917.html,W5_CreateServiceRecordWithAssets,3.85,,,3.0,50.0,0.0
W6,5,src/reports/W6/report_5TPS_20260115_074109.html,W6_HireService,2.22,,,3.9,50.0,0.0
W6,10,src/reports/W6/report_10TPS_20260115_074133.html,W6_HireService,2.37,,,7.0,50.0,0.0
W6,15,src/reports/W6/report_15TPS_20260115_074157.html,W6_HireService,2.25,,,6.6,50.0,0.0
W6,20,src/reports/W6/report_20TPS_20260115_074217.html,W6_HireService,2.27,,,14.3,50.0,0.0
W6,25,src/reports/W6/report_25TPS_20260115_074237.html,W6_HireService,2.67,,,13.7,50.0,0.0
W6,30,src/reports/W6/report_30TPS_20260115_074257.html,W6_HireService,2.58,,,14.7,50.0,0.0
W6,35,src/reports/W6/report_35TPS_20260115_074317.html,W6_HireService,2.45,,,15.8,50.0,0.0
W6,40,src/reports/W6/report_40TPS_20260115_074337.html,W6_HireService,2.39,,,16.6,50.0,0.0
W7,5,src/reports/W7/report_5TPS_20260115_074717.html,W7_PayService,2.24,,,4.1,50.0,0.0
W7,10,src/reports/W7/report_10TPS_20260115_074741.html,W7_PayService,2.04,,,6.7,0.0,50.0
W7,15,src/reports/W7/report_15TPS_20260115_074801.html,W7_PayService,1.7,,,14.2,0.0,50.0
W7,20,src/reports/W7/report_20TPS_20260115_074821.html,W7_PayService,1.8,,,15.3,0.0,50.0
W7,25,src/reports/W7/report_25TPS_20260115_074841.html,W7_PayService,1.5,,,15.1,0.0,50.0
W7,30,src/reports/W7/report_30TPS_20260115_074901.html,W7_PayService,1.2,,,15.9,0.0,50.0
W7,35,src/reports/W7/report_35TPS_20260115_074921.html,W7_PayService,0.9,,,14.9,0.0,50.0
W7,40,src/reports/W7/report_35TPS_20260115_074921.html,W7_PayService,0.8,,,14.9,0.0,50.0
"""

# Use Times-like font
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']

df = pd.read_csv(StringIO(data))
df = df[['scenario', 'tps_target', 'throughput']].copy()
df['tps_target'] = df['tps_target'].astype(int)

# Aggregate duplicates (W4 has duplicates per TPS): mean throughput per scenario & TPS
df_agg = df.groupby(['scenario', 'tps_target'], as_index=False)['throughput'].mean()

scenarios = [f'W{i}' for i in range(1, 8)]
tps_levels = [5, 10, 15, 20, 25, 30, 35, 40]

# matrix for convenience
mat = pd.DataFrame(index=tps_levels, columns=scenarios, dtype=float)
for _, r in df_agg.iterrows():
    mat.loc[int(r['tps_target']), r['scenario']] = float(r['throughput'])
mat_sorted = mat.loc[tps_levels, scenarios]

# Color palette: variations of blue, black, red, brown (7 colors total)
colors = {
    'W1': "#7D93B8",  # dark blue
    'W2': "#A4CAF0",  # blue
    'W3': "#918A8A",  # near-black
    'W4': "#5C3030",  # dark red
    'W5': "#E27F7F",  # red
    'W6': "#A38D82",  # brown
    'W7': "#C48B71",  # sienna/brown
}

fig = plt.figure(figsize=(10, 8), dpi=300)
ax = fig.add_subplot(111, projection='3d')

# Build bars per scenario so each "column" (scenario) has its own color
for xi, scen in enumerate(scenarios):
    xpos, ypos, zpos, dx, dy, dz = [], [], [], [], [], []
    for yi, tps in enumerate(tps_levels):
        val = mat_sorted.loc[tps, scen]
        if pd.isna(val):
            continue
        xpos.append(xi)
        ypos.append(yi)
        zpos.append(0.0)
        dx.append(0.6)
        dy.append(0.6)
        dz.append(val)

    if len(dz) == 0:
        continue
    
    ax.bar3d(
        np.array(xpos), np.array(ypos), np.array(zpos),
        np.array(dx), np.array(dy), np.array(dz),
        shade=True, color=colors[scen], alpha=0.99, edgecolor='k', linewidth=0.4
    )

    # Add value labels for this scenario
    for x, y, h in zip(xpos, ypos, dz):
        ax.text(x + 0.3, y + 0.3, h + 0.2, f"{h:.1f}",
                ha='center', va='bottom', fontsize=8)

# Axis labels and ticks (Times)
ax.set_xlabel('Scenario (Workload)', labelpad=12)
ax.set_ylabel('Configured Load (TPS)', labelpad=12)
ax.set_zlabel('Throughput (tx/s)', labelpad=10)

ax.set_xticks(np.arange(len(scenarios)) + 0.31)
ax.set_xticklabels(scenarios)

ax.set_yticks(np.arange(len(tps_levels)) + 0.31)
ax.set_yticklabels([str(t) for t in tps_levels])

# View angle similar to reference
ax.view_init(elev=30, azim=-125)

# Improve spacing
fig.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)

out_path = "./throughput_w1_w7_3d_colored_times.png"
fig.savefig(out_path, bbox_inches="tight")
plt.close(fig)

out_path
