import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from io import StringIO

# Times-like font
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']

# Full original CSV (we only need scenario, tps_target, throughput)
data = """scenario,tps_target,report,round,avg,p95,p99,throughput,succ,fail
W1,5,src/reports/W1/report_5TPS_20260115_054313.html,W1_RegisterAsset,2.53,,,3.9,50.0,0.0
W1,5,src/reports/W1/report_5TPS_20260131_183632.html,W1_RegisterAsset,2.39,,,3.9,50.0,0.0
W1,10,src/reports/W1/report_10TPS_20260115_054341.html,W1_RegisterAsset,3.96,,,4.5,50.0,0.0
W1,10,src/reports/W1/report_10TPS_20260131_183700.html,W1_RegisterAsset,3.85,,,4.5,50.0,0.0
W1,15,src/reports/W1/report_15TPS_20260115_054409.html,W1_RegisterAsset,4.92,,,4.4,50.0,0.0
W1,15,src/reports/W1/report_15TPS_20260131_183728.html,W1_RegisterAsset,4.86,,,4.5,50.0,0.0
W1,20,src/reports/W1/report_20TPS_20260115_054437.html,W1_RegisterAsset,5.37,,,4.4,50.0,0.0
W1,25,src/reports/W1/report_25TPS_20260115_054505.html,W1_RegisterAsset,5.61,,,4.4,50.0,0.0
W1,30,src/reports/W1/report_30TPS_20260115_054533.html,W1_RegisterAsset,5.96,,,4.3,50.0,0.0
W1,35,src/reports/W1/report_35TPS_20260115_054601.html,W1_RegisterAsset,6.02,,,4.4,50.0,0.0
W1,40,src/reports/W1/report_40TPS_20260115_054629.html,W1_RegisterAsset,6.06,,,4.4,50.0,0.0
W2,5,src/reports/W2/report_5TPS_20260131_184012.html,W2_HireAsset,2.26,,,4.6,50.0,0.0
W2,10,src/reports/W2/report_10TPS_20260131_184040.html,W2_HireAsset,2.29,,,7.6,50.0,0.0
W2,15,src/reports/W2/report_15TPS_20260131_184104.html,W2_HireAsset,,,,7.2,0.0,50.0
W2,20,src/reports/W2/report_20TPS_20260131_184316.html,W2_HireAsset,,,,10.3,0.0,50.0
W2,25,src/reports/W2/report_25TPS_20260131_184336.html,W2_HireAsset,,,,15.9,0.0,50.0
W2,30,src/reports/W2/report_30TPS_20260131_184356.html,W2_HireAsset,,,,14.7,0.0,50.0
W2,35,src/reports/W2/report_35TPS_20260131_185432.html,W2_HireAsset,,,,15.1,0.0,50.0
W2,40,src/reports/W2/report_40TPS_20260131_185452.html,W2_HireAsset,,,,16.5,0.0,50.0
W3,5,src/reports/W3/report_5TPS_20260115_075629.html,W3_PayAsset,1.91,,,3.7,50.0,0.0
W3,5,src/reports/W3/report_5TPS_20260131_184900.html,W3_PayAsset,,,,4.7,0.0,50.0
W3,10,src/reports/W3/report_10TPS_20260115_075653.html,W3_PayAsset,,,,7.1,0.0,50.0
W3,10,src/reports/W3/report_10TPS_20260131_195749.html,W3_PayAsset,3.64,,,5.9,20.0,30.0
W3,15,src/reports/W3/report_15TPS_20260115_075717.html,W3_PayAsset,,,,6.9,0.0,50.0
W3,15,src/reports/W3/report_15TPS_20260131_184948.html,W3_PayAsset,,,,6.9,0.0,50.0
W3,15,src/reports/W3/report_15TPS_20260131_195813.html,W3_PayAsset,,,,7.1,0.0,50.0
W3,20,src/reports/W3/report_20TPS_20260115_075737.html,W3_PayAsset,,,,14.9,0.0,50.0
W3,20,src/reports/W3/report_20TPS_20260131_185008.html,W3_PayAsset,,,,15.9,0.0,50.0
W3,25,src/reports/W3/report_25TPS_20260115_075757.html,W3_PayAsset,,,,15.4,0.0,50.0
W3,25,src/reports/W3/report_25TPS_20260131_185028.html,W3_PayAsset,,,,17.8,0.0,50.0
W3,30,src/reports/W3/report_30TPS_20260115_075817.html,W3_PayAsset,,,,19.1,0.0,50.0
W3,30,src/reports/W3/report_30TPS_20260131_185048.html,W3_PayAsset,,,,16.6,0.0,50.0
W3,35,src/reports/W3/report_35TPS_20260115_075837.html,W3_PayAsset,,,,14.9,0.0,50.0
W3,35,src/reports/W3/report_35TPS_20260131_185108.html,W3_PayAsset,,,,15.1,0.0,50.0
W3,40,src/reports/W3/report_40TPS_20260115_075857.html,W3_PayAsset,,,,15.6,0.0,50.0
W3,40,src/reports/W3/report_40TPS_20260131_185128.html,W3_PayAsset,,,,16.6,0.0,50.0
W4,5,src/reports/W4/report_5TPS_20260115_072641.html,W4_CreateServiceRecord,2.25,,,2.9,15.0,0.0
W4,5,src/reports/W4/report_5TPS_20260115_073137.html,W4_CreateServiceRecord,2.08,,,3.9,50.0,0.0
W4,5,src/reports/W4/report_5TPS_20260131_194028.html,W4_CreateServiceRecord,2.01,,,3.6,50.0,0.0
W4,10,src/reports/W4/report_10TPS_20260115_072701.html,W4_CreateServiceRecord,2.5,,,4.7,15.0,0.0
W4,10,src/reports/W4/report_10TPS_20260115_073201.html,W4_CreateServiceRecord,2.63,,,6.8,50.0,0.0
W4,10,src/reports/W4/report_10TPS_20260131_194108.html,W4_CreateServiceRecord,3.38,,,6.0,50.0,0.0
W4,15,src/reports/W4/report_15TPS_20260115_072721.html,W4_CreateServiceRecord,2.81,,,4.6,15.0,0.0
W4,15,src/reports/W4/report_15TPS_20260115_073225.html,W4_CreateServiceRecord,3.36,,,6.9,50.0,0.0
W4,15,src/reports/W4/report_15TPS_20260131_194132.html,W4_CreateServiceRecord,3.0,,,7.2,50.0,0.0
W4,20,src/reports/W4/report_20TPS_20260115_072757.html,W4_CreateServiceRecord,2.46,,,5.3,15.0,0.0
W4,20,src/reports/W4/report_20TPS_20260115_073305.html,W4_CreateServiceRecord,3.6,,,7.0,50.0,0.0
W4,25,src/reports/W4/report_25TPS_20260115_072817.html,W4_CreateServiceRecord,2.72,,,5.0,15.0,0.0
W4,25,src/reports/W4/report_25TPS_20260115_073329.html,W4_CreateServiceRecord,4.01,,,6.8,50.0,0.0
W4,30,src/reports/W4/report_30TPS_20260115_072837.html,W4_CreateServiceRecord,2.82,,,4.9,15.0,0.0
W4,30,src/reports/W4/report_30TPS_20260115_073353.html,W4_CreateServiceRecord,4.18,,,6.9,50.0,0.0
W4,35,src/reports/W4/report_35TPS_20260115_072857.html,W4_CreateServiceRecord,3.29,,,4.3,15.0,0.0
W4,35,src/reports/W4/report_35TPS_20260115_073417.html,W4_CreateServiceRecord,4.43,,,6.7,50.0,0.0
W4,40,src/reports/W4/report_40TPS_20260115_072917.html,W4_CreateServiceRecord,3.06,,,4.6,15.0,0.0
W4,40,src/reports/W4/report_40TPS_20260115_073441.html,W4_CreateServiceRecord,4.43,,,6.8,50.0,0.0
W5,5,src/reports/W5/report_5TPS_20260115_073917.html,W5_CreateServiceRecordWithAssets,4.51,,,3.0,50.0,0.0
W5,10,src/reports/W5/report_10TPS_20260131_185824.html,W5_CreateServiceRecordWithAssets,,,,8.8,0.0,50.0
W5,15,src/reports/W5/report_15TPS_20260131_190052.html,W5_CreateServiceRecordWithAssets,1.95,,,8.4,10.0,40.0
W5,20,src/reports/W5/report_20TPS_20260131_190112.html,W5_CreateServiceRecordWithAssets,,,,8.6,0.0,50.0
W5,25,src/reports/W5/report_25TPS_20260131_190144.html,W5_CreateServiceRecordWithAssets,,,,9.1,0.0,50.0
W5,30,src/reports/W5/report_30TPS_20260131_190204.html,W5_CreateServiceRecordWithAssets,,,,8.7,0.0,50.0
W5,35,src/reports/W5/report_35TPS_20260131_190224.html,W5_CreateServiceRecordWithAssets,,,,8.2,0.0,50.0
W5,40,src/reports/W5/report_40TPS_20260131_190244.html,W5_CreateServiceRecordWithAssets,,,,8.7,0.0,50.0
W6,5,src/reports/W6/report_5TPS_20260115_074109.html,W6_HireService,2.22,,,4.9,50.0,0.0
W6,5,src/reports/W6/report_5TPS_20260131_193716.html,W6_HireService,2.39,,,4.4,50.0,0.0
W6,10,src/reports/W6/report_10TPS_20260115_074133.html,W6_HireService,2.37,,,7.0,50.0,0.0
W6,10,src/reports/W6/report_10TPS_20260131_193740.html,W6_HireService,2.44,,,6.9,50.0,0.0
W6,15,src/reports/W6/report_15TPS_20260115_074157.html,W6_HireService,2.25,,,6.6,50.0,0.0
W6,15,src/reports/W6/report_15TPS_20260131_193804.html,W6_HireService,2.24,,,7.1,50.0,0.0
W6,20,src/reports/W6/report_20TPS_20260115_074217.html,W6_HireService,2.27,,,14.3,50.0,0.0
W6,25,src/reports/W6/report_25TPS_20260115_074237.html,W6_HireService,2.67,,,13.7,50.0,0.0
W6,30,src/reports/W6/report_30TPS_20260115_074257.html,W6_HireService,2.58,,,14.7,50.0,0.0
W6,35,src/reports/W6/report_35TPS_20260115_074317.html,W6_HireService,2.45,,,15.8,50.0,0.0
W6,40,src/reports/W6/report_40TPS_20260115_074337.html,W6_HireService,2.39,,,16.6,50.0,0.0
W7,5,src/reports/W7/report_5TPS_20260115_074717.html,W7_PayService,2.24,,,4.1,50.0,0.0
W7,5,src/reports/W7/report_5TPS_20260131_193548.html,W7_PayService,,,,4.2,0.0,50.0
W7,10,src/reports/W7/report_10TPS_20260115_074741.html,W7_PayService,,,,6.7,0.0,50.0
W7,10,src/reports/W7/report_10TPS_20260131_193612.html,W7_PayService,,,,7.4,0.0,50.0
W7,15,src/reports/W7/report_15TPS_20260115_074801.html,W7_PayService,,,,14.2,0.0,50.0
W7,15,src/reports/W7/report_15TPS_20260131_193636.html,W7_PayService,,,,7.0,0.0,50.0
W7,20,src/reports/W7/report_20TPS_20260115_074821.html,W7_PayService,,,,15.3,0.0,50.0
W7,25,src/reports/W7/report_25TPS_20260115_074841.html,W7_PayService,,,,15.1,0.0,50.0
W7,30,src/reports/W7/report_30TPS_20260115_074901.html,W7_PayService,,,,15.9,0.0,50.0
W7,35,src/reports/W7/report_35TPS_20260115_074921.html,W7_PayService,,,,14.9,0.0,50.0
W7,40,src/reports/W7/report_40TPS_20260131_190332.html,W7_PayService,,,,9.6,0.0,50.0
W7,40,src/reports/W7/report_40TPS_20260131_190440.html,W7_PayService,2.76,,,16.6,20.0,30.0
"""

# Robust CSV read: handle occasional malformed line by selecting needed columns after parse
df = pd.read_csv(StringIO(data))
df = df[['scenario', 'tps_target', 'throughput']].copy()
df['tps_target'] = df['tps_target'].astype(int)

# Aggregate duplicates (W4 duplicated TPS): mean throughput per scenario & TPS
df_agg = df.groupby(['scenario', 'tps_target'], as_index=False)['throughput'].mean()

scenarios = [f'W{i}' for i in range(1, 8)]
tps_levels = [5, 10, 15, 20, 25, 30, 35, 40]

# Build matrix for plotting
mat = pd.DataFrame(index=tps_levels, columns=scenarios, dtype=float)
for _, r in df_agg.iterrows():
    mat.loc[int(r['tps_target']), r['scenario']] = float(r['throughput'])

# Soft, harmonious palette (blue → gray → red → brown), paper-friendly
colors = {
    'W1': '#b3cde3',  # pastel blue
    'W2': '#ccebc5',  # soft teal/green
    'W3': '#dddddd',  # light gray
    'W4': '#fbb4ae',  # pastel red
    'W5': '#fee8c8',  # light peach
    'W6': "#f8d99a",  # light tan
    'W7': '#decbe4',  # light mauve
}

# IMPORTANT FIX:
# Place labels "in front of the camera" by projecting 3D points to 2D and drawing with fig.text.
# This guarantees no label can be hidden by bars.
from mpl_toolkits.mplot3d.proj3d import proj_transform

fig = plt.figure(figsize=(10, 8), dpi=300)
ax = fig.add_subplot(111, projection='3d')

# Draw bars scenario by scenario to ensure consistent colors
for xi, scen in enumerate(scenarios):
    xpos, ypos, zpos, dx, dy, dz = [], [], [], [], [], []
    for yi, tps in enumerate(tps_levels):
        val = mat.loc[tps, scen]
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
        color=colors[scen], alpha=0.85,
        edgecolor='k', linewidth=0.3, shade=True
    )

# Axis labels and ticks
ax.set_xlabel('Scenarios', labelpad=12)
ax.set_ylabel('Configured Load (TPS)', labelpad=12)
ax.set_zlabel('Throughput (tx/s)', labelpad=10)

ax.set_xticks(np.arange(len(scenarios)) + 0.3)
ax.set_xticklabels(scenarios)

ax.set_yticks(np.arange(len(tps_levels)) + 0.3)
ax.set_yticklabels([str(t) for t in tps_levels])

# Legenda lateral (proxy patches para garantir que apareça)
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=colors[s], edgecolor='k', label=s) for s in scenarios]
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.05, 0.9), title="Scenarios")


# Camera angle similar to reference
ax.view_init(elev=28, azim=-115)
#ax.view_init(elev=28, azim=-125)

# Expand margins to reduce clipping
fig.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)

# Draw once so projection matrix is ready
fig.canvas.draw()

# Add labels as 2D overlay (never occluded)
for xi, scen in enumerate(scenarios):
    for yi, tps in enumerate(tps_levels):
        val = mat.loc[tps, scen]
        if pd.isna(val):
            continue

        # Label position: top of the bar + a little lift
        x3, y3, z3 = xi + 0.3, yi + 0.3, float(val) + 0.5

        x2, y2, _ = proj_transform(x3, y3, z3, ax.get_proj())
        # Convert data coords to figure coords
        xdisp, ydisp = ax.transData.transform((x2, y2))
        xfig, yfig = fig.transFigure.inverted().transform((xdisp, ydisp))

        # Only draw if inside figure bounds (avoid weird outside labels)
        if 0.0 <= xfig <= 1.0 and 0.0 <= yfig <= 1.0:
            fig.text(xfig, yfig, f"{val:.1f}",
                     ha='center', va='center_baseline',
                     fontsize=9, color='black')

out_path = "./throughput_w1_w7_3d_labels_always_visible.png"
fig.savefig(out_path, bbox_inches="tight")
plt.close(fig)

out_path
