import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# geopandas untuk overlay batas wilayah dari GeoJSON
try:
    import geopandas as gpd
    HAS_GPD = True
except ImportError:
    HAS_GPD = False
    print("[INFO] geopandas tidak tersedia — plot tanpa overlay peta batas wilayah.")

df = pd.read_csv('data/java_job_market_hubs_final.csv')
df_plot = df[(df['Latitude'] != 0.0) & (df['Longitude'] != 0.0)].copy()

cluster_colors = {-1: '#888888', 0: '#2196F3', 1: '#FF5722'}
cluster_labels = {
    -1: 'Isolated Zone / Noise (4 wilayah: Kep. Seribu + vol=0)',
    0:  'Cluster 0 — Mainland Java (93 wilayah)',
    1:  'Cluster 1 — Jabodetabek & Koridor Barat (22 wilayah)'
}

fig, ax = plt.subplots(figsize=(18, 9))
fig.patch.set_facecolor('#ffffff')

# ── Layer 1: batas wilayah kabupaten/kota (GeoJSON) ─────────────────────────
if HAS_GPD:
    gdf = gpd.read_file('data/java_regencies.geojson')
    gdf.plot(
        ax=ax,
        color='#edf2f7',
        edgecolor='#b0bec5',
        linewidth=0.4,
        alpha=0.9
    )
    ax.set_facecolor('#cce5f0')
else:
    ax.set_facecolor('#dce8f0')

# ── Layer 2: scatter titik klaster ──────────────────────────────────────────
for cid in sorted(df_plot['cluster_id'].unique()):
    group = df_plot[df_plot['cluster_id'] == cid]
    color = cluster_colors.get(cid, '#cccccc')
    sizes = group['job_volume'] * 0.18 + 18
    ax.scatter(
        group['Longitude'], group['Latitude'],
        s=sizes, c=color, alpha=0.85,
        edgecolors='white', linewidth=0.6,
        zorder=3,
        label=cluster_labels.get(cid, f'Cluster {cid}')
    )

# ── Layer 3: label 12 kota volume terbesar ──────────────────────────────────
top_cities = df_plot.nlargest(12, 'job_volume')
for _, row in top_cities.iterrows():
    ax.annotate(
        row['matched_regency'],
        xy=(row['Longitude'], row['Latitude']),
        xytext=(6, 6), textcoords='offset points',
        fontsize=7.5, fontweight='bold', zorder=5,
        bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                  alpha=0.85, edgecolor='#90a4ae', linewidth=0.8)
    )

# ── Layer 4: label centroid tiap klaster ────────────────────────────────────
cluster_names = {0: 'Mainland Java', 1: 'Jabodetabek & Koridor Barat'}
for cid, group in df_plot[df_plot['cluster_id'] != -1].groupby('cluster_id'):
    cx = group['Longitude'].mean()
    cy = group['Latitude'].mean()
    ax.text(
        cx, cy + 0.3,
        f"● {cluster_names.get(cid, f'Hub {cid}')}",
        fontsize=10, fontweight='bold', ha='center', va='bottom', zorder=6,
        color='white',
        bbox=dict(boxstyle='round,pad=0.35',
                  facecolor=cluster_colors.get(cid, 'gray'),
                  alpha=0.85, edgecolor='white', linewidth=1)
    )

# ── Judul & label sumbu — DIPERBAIKI ─────────────────────────────────────────
ax.set_title(
    'Aglomerasi Geospasial Hub Ekonomi Pulau Jawa (DBSCAN)\n'
    'eps=0.10 | min_samples=3 | Fitur: Latitude, Longitude & Opportunity Index (MinMax 3D)',
    fontsize=14, fontweight='bold', pad=14
)
ax.set_xlabel('Longitude', fontsize=10)
ax.set_ylabel('Latitude', fontsize=10)

# ── Legend tipe klaster ──────────────────────────────────────────────────────
legend_patches = [
    mpatches.Patch(color=cluster_colors[cid], label=cluster_labels[cid])
    for cid in sorted(cluster_labels)
]
leg1 = ax.legend(handles=legend_patches, loc='upper left', fontsize=9,
                 framealpha=0.92, title='Tipe Klaster', title_fontsize=9,
                 edgecolor='#cccccc')
ax.add_artist(leg1)

# ── Legend ukuran gelembung ──────────────────────────────────────────────────
size_handles = [
    ax.scatter([], [], s=sz, c='#555555', alpha=0.6, label=lbl)
    for sz, lbl in [(18, '1 lowongan'), (72, '300 lowongan'), (198, '1.000+ lowongan')]
]
ax.legend(handles=size_handles, loc='lower right', fontsize=8,
          title='Ukuran \u221d Volume Lowongan', title_fontsize=8,
          framealpha=0.92, edgecolor='#cccccc')

plt.tight_layout()
plt.savefig('viz_cluster_map.png', dpi=150, bbox_inches='tight')
plt.show()
print("Disimpan: viz_cluster_map.png")
print()
print("Komposisi cluster:")
print(f"  Cluster 0 (Mainland Java)        : 93 wilayah")
print(f"  Cluster 1 (Jabodetabek & Barat)  : 22 wilayah")
print(f"  Noise (Kep.Seribu + vol=0)       :  4 wilayah")
