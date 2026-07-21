"""
Generator script untuk spatial_clustering_pipeline.ipynb
Jalankan: python build_notebook.py
"""
import json, os, re

def read_src(path):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    # Hapus docstring modul di awal
    src = re.sub(r'^""".*?"""\s*', '', src, flags=re.DOTALL)
    # Ganti guard if __name__ == "__main__": main() dengan main()
    src = re.sub(r'\nif __name__\s*==\s*["\']__main__["\']\s*:\s*\n\s*main\(\)\s*$', '\nmain()', src.rstrip())
    return src.strip()

def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source}

def code(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source}

# ── baca source scripts ──────────────────────────────────────────────────────
bps_code    = read_src('src/2_bps_consolidation.py')
geocode_raw = read_src('src/3_geocoding_regencies.py')
fusion_code = read_src('src/4_data_integration.py')
oppidx_code = read_src('src/5_opportunity_index.py')
dbscan_code = read_src('src/6_spatial_clustering_dbscan.py')

# Geocoding: bungkus dengan skip-if-exists
geocode_code = '''import pandas as pd
import os
import time

COORD_PATH = 'data/java_regency_coordinates.csv'

if os.path.exists(COORD_PATH):
    print(f"[SKIP] File koordinat sudah ada: {COORD_PATH}")
    df_coords_preview = pd.read_csv(COORD_PATH)
    print(f"Total wilayah: {len(df_coords_preview)}")
    display(df_coords_preview.head(3))
else:
    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter

''' + '\n'.join('    ' + line for line in geocode_raw.splitlines()) + '''

    main()
'''

# ── visualisasi ──────────────────────────────────────────────────────────────
viz1 = '''import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('data/java_job_market_hubs_final.csv')
df_plot = df[(df['Latitude'] != 0.0) & (df['Longitude'] != 0.0)].copy()

cluster_colors = {-1: '#888888', 0: '#2196F3', 1: '#FF5722'}
cluster_labels = {
    -1: 'Isolated Zone (Noise)',
    0:  'Cluster 0 — Mainland Java',
    1:  'Cluster 1 — Jabodetabek & Koridor Barat'
}

fig, ax = plt.subplots(figsize=(16, 8))
ax.set_facecolor('#f5f5f5')
fig.patch.set_facecolor('#ffffff')

for cid, group in df_plot.groupby('cluster_id'):
    color = cluster_colors.get(cid, '#cccccc')
    sizes = group['job_volume'] * 0.15 + 15
    ax.scatter(
        group['Longitude'], group['Latitude'],
        s=sizes, c=color, alpha=0.75,
        edgecolors='white', linewidth=0.5,
        label=cluster_labels.get(cid, f'Cluster {cid}')
    )

# Label 10 kota terbesar
top_cities = df_plot.nlargest(10, 'job_volume')
for _, row in top_cities.iterrows():
    ax.annotate(
        row['matched_regency'],
        xy=(row['Longitude'], row['Latitude']),
        xytext=(5, 5), textcoords='offset points',
        fontsize=7.5, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='gray')
    )

# Label centroid per klaster
for cid, group in df_plot[df_plot['cluster_id'] != -1].groupby('cluster_id'):
    cx, cy = group['Longitude'].mean(), group['Latitude'].mean()
    ax.text(cx, cy, f'Hub {cid}', fontsize=13, fontweight='bold', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=cluster_colors.get(cid, 'white'),
                      alpha=0.25, edgecolor='black', linewidth=1.5))

ax.set_title(
    'Aglomerasi Geospasial Hub Ekonomi Pulau Jawa (DBSCAN)\\n'
    'eps=0.40 | min_samples=3 | Fitur: Latitude & Longitude',
    fontsize=14, fontweight='bold', pad=15
)
ax.set_xlabel('Longitude', fontsize=11)
ax.set_ylabel('Latitude', fontsize=11)

handles, labels_leg = ax.get_legend_handles_labels()
ax.legend(handles, labels_leg, loc='upper left', fontsize=9, framealpha=0.9,
          title='Tipe Klaster', title_fontsize=9)

# Bubble size legend
for sz, lbl in [(15, '1 lowongan'), (60, '300 lowongan'), (165, '1.000 lowongan')]:
    ax.scatter([], [], s=sz, c='gray', alpha=0.5, label=lbl)
ax.legend(loc='lower right', fontsize=8, title='Ukuran ∝ Volume Lowongan',
          title_fontsize=8, framealpha=0.9)

plt.tight_layout()
plt.savefig('viz_cluster_map.png', dpi=150, bbox_inches='tight')
plt.show()
print("Disimpan: viz_cluster_map.png")
'''

viz2 = '''import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

df = pd.read_csv('data/java_job_market_hubs_final.csv')
df_top = df[df['job_volume'] > 0].nlargest(20, 'opportunity_index').copy()

norm = plt.Normalize(df_top['opportunity_index'].min(), df_top['opportunity_index'].max())
colors = cm.RdYlGn(norm(df_top['opportunity_index'].values))

fig, ax = plt.subplots(figsize=(14, 7))
bars = ax.barh(range(len(df_top)), df_top['opportunity_index'],
               color=colors, edgecolor='white', linewidth=0.5)

ax.set_yticks(range(len(df_top)))
ax.set_yticklabels(df_top['matched_regency'], fontsize=9)
ax.invert_yaxis()
ax.set_xlabel('Opportunity Index (Lowongan / Angkatan Kerja)', fontsize=11)
ax.set_title(
    'Top 20 Wilayah Berdasarkan Opportunity Index\\n'
    '(Rasio Penyerapan Tenaga Kerja Formal per Kapita)',
    fontsize=13, fontweight='bold', pad=12
)

median_val = df['opportunity_index'].median()
ax.axvline(median_val, color='red', linestyle='--', linewidth=1.5,
           label=f'Median regional ({median_val:.5f})')
ax.legend(fontsize=9)

for bar, val in zip(bars, df_top['opportunity_index']):
    ax.text(val + df_top['opportunity_index'].max() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f'{val:.4f}', va='center', fontsize=8)

sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=norm)
sm.set_array([])
plt.colorbar(sm, ax=ax, label='Opportunity Index', shrink=0.8, pad=0.01)

ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('viz_opportunity_index.png', dpi=150, bbox_inches='tight')
plt.show()
print("Disimpan: viz_opportunity_index.png")
'''

viz3 = '''import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

df = pd.read_csv('data/java_job_market_hubs_final.csv')

cluster_colors = ['#888888', '#2196F3', '#FF5722']
cluster_ids    = sorted(df['cluster_id'].unique())

fig = plt.figure(figsize=(16, 10))
gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

# Plot 1 — Boxplot distribusi job_volume per klaster
ax1 = fig.add_subplot(gs[0, 0])
data_box   = [df[df['cluster_id'] == cid]['job_volume'].values for cid in cluster_ids]
labels_box = ['Isolated (-1)', 'Mainland (0)', 'Jabodetabek (1)'][:len(cluster_ids)]
bp = ax1.boxplot(data_box, labels=labels_box, patch_artist=True,
                 medianprops=dict(color='red', linewidth=2))
for patch, color in zip(bp['boxes'], cluster_colors[:len(cluster_ids)]):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax1.set_title('Distribusi Volume Lowongan per Cluster', fontweight='bold')
ax1.set_ylabel('Job Volume (log scale)')
ax1.set_yscale('symlog')
ax1.grid(axis='y', alpha=0.3)

# Plot 2 — Pie jumlah wilayah per klaster
ax2 = fig.add_subplot(gs[0, 1])
counts     = df['cluster_id'].value_counts().sort_index()
pie_labels = [f'Isolated (-1)\\n{counts.get(-1,0)} wil.' if c == -1
              else f'Mainland (0)\\n{counts.get(0,0)} wil.' if c == 0
              else f'Jabodetabek (1)\\n{counts.get(1,0)} wil.'
              for c in counts.index]
ax2.pie(counts.values, labels=pie_labels,
        colors=cluster_colors[:len(counts)],
        autopct='%1.1f%%', startangle=90,
        wedgeprops=dict(edgecolor='white', linewidth=1.5))
ax2.set_title('Proporsi Wilayah per Cluster', fontweight='bold')

# Plot 3 — Total lowongan per klaster
ax3 = fig.add_subplot(gs[1, 0])
job_sum  = df.groupby('cluster_id')['job_volume'].sum()
bar_lbls = ['Isolated (-1)' if c == -1 else 'Mainland (0)' if c == 0 else 'Jabodetabek (1)'
            for c in job_sum.index]
bars3 = ax3.bar(bar_lbls, job_sum.values,
                color=cluster_colors[:len(job_sum)],
                edgecolor='white', linewidth=1)
for bar, val in zip(bars3, job_sum.values):
    ax3.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + job_sum.max() * 0.01,
             f'{val:,}', ha='center', fontsize=10, fontweight='bold')
ax3.set_title('Total Volume Lowongan per Cluster', fontweight='bold')
ax3.set_ylabel('Total Lowongan')
ax3.grid(axis='y', alpha=0.3)

# Plot 4 — Tabel metrik evaluasi
ax4 = fig.add_subplot(gs[1, 1])
ax4.axis('off')
metrics = [
    ('Silhouette Score',    '0.4722', '[-1, 1] lebih tinggi = lebih baik',  '#4CAF50'),
    ('Davies-Bouldin Index','0.5136', 'lebih rendah = lebih baik',           '#4CAF50'),
    ('Total Cluster',       '2',      'Mainland Java + Jabodetabek',         '#2196F3'),
    ('Total Wilayah',       '119',    'Kabupaten/Kota Pulau Jawa',           '#2196F3'),
    ('Noise / Isolated',    '28',     'job_volume = 0 atau outlier geografis','#888888'),
    ('eps  (DBSCAN)',        '0.40',   'scaled Euclidean distance',           '#FF9800'),
    ('min_samples',         '3',      'minimum tetangga inti',               '#FF9800'),
]
ax4.text(0.5, 1.03, 'Parameter & Evaluasi Model DBSCAN',
         ha='center', va='top', transform=ax4.transAxes,
         fontsize=11, fontweight='bold')
y = 0.90
for name, val, note, color in metrics:
    ax4.text(0.03, y,    f'{name}:', transform=ax4.transAxes,
             fontsize=9,  fontweight='bold', color='#333333')
    ax4.text(0.57, y,    val,         transform=ax4.transAxes,
             fontsize=9,  fontweight='bold', color=color)
    ax4.text(0.03, y-0.065, note,    transform=ax4.transAxes,
             fontsize=7.5, color='#666666', style='italic')
    y -= 0.135

fig.suptitle(
    'Ringkasan Hasil Klastering Spasial DBSCAN\\nPasar Kerja Formal Pulau Jawa',
    fontsize=14, fontweight='bold', y=1.01
)
plt.savefig('viz_cluster_summary.png', dpi=150, bbox_inches='tight')
plt.show()
print("Disimpan: viz_cluster_summary.png")
'''

# ── susun semua sel ──────────────────────────────────────────────────────────
cells = [
    md(
        "# Analisis Spasial & Klastering Pasar Kerja Pulau Jawa\n"
        "**Proyek Skripsi — Analisis Klastering Lowongan Kerja (Jobstreet) & Sosio-Ekonomi (BPS) dengan DBSCAN**\n\n"
        "Notebook ini merangkum seluruh alur pengolahan data dari awal hingga akhir (*end-to-end*), meliputi:\n"
        "1. **Tahap 1: Data Acquisition** — Penjelasan mekanisme akuisisi lowongan kerja Jobstreet.\n"
        "2. **Tahap 2: Socio-Economic Data Cleaning** — Konsolidasi data ketenagakerjaan BPS.\n"
        "3. **Tahap 3: Geocoding** — Pencarian koordinat 119 Kabupaten/Kota di Jawa via Nominatim (OSM).\n"
        "4. **Tahap 4: Data Fusion & Fuzzy Matching** — Integrasi lowongan dengan wilayah BPS.\n"
        "5. **Tahap 5: Opportunity Index** — Penghitungan rasio penyerapan tenaga kerja per wilayah.\n"
        "6. **Tahap 6: Spatial Clustering (DBSCAN)** — Pemodelan aglomerasi hub ekonomi spasial.\n"
        "7. **Tahap 7: Visualisasi Eksploratif** — Peta spasial, heatmap indeks, dan ringkasan klaster.\n\n"
        "---"
    ),
    code(
        "# Install semua dependensi\n"
        "!pip install -q pandas numpy scikit-learn rapidfuzz geopy matplotlib seaborn "
        "openpyxl statsmodels plotly scipy curl_cffi python-dotenv"
    ),
    md(
        "## Tahap 1: Akuisisi Data Lowongan Kerja (Jobstreet API)\n"
        "Data lowongan kerja diakuisisi dari endpoint GraphQL `JobSearchV6` Jobstreet menggunakan "
        "reverse engineering dengan `curl_cffi` (Chrome impersonation untuk bypass Cloudflare WAF).\n"
        "Jika file `data/jobstreet_results.csv` sudah tersedia, sel ini cukup menampilkan preview."
    ),
    code(
        "import pandas as pd\n"
        "import os\n\n"
        "CSV_PATH = 'data/jobstreet_results.csv'\n\n"
        "if os.path.exists(CSV_PATH):\n"
        "    print(f'File data lowongan ditemukan: {CSV_PATH}')\n"
        "    df_js_preview = pd.read_csv(CSV_PATH)\n"
        "    print(f'Jumlah Lowongan Terdaftar: {len(df_js_preview)} lowongan.')\n"
        "    display(df_js_preview.head(3))\n"
        "else:\n"
        "    print(f'[PERINGATAN] File {CSV_PATH} tidak ditemukan.')\n"
        "    print('Akuisisi live membutuhkan JOBSTREET_BEARER_TOKEN & cookies aktif di .env')"
    ),
    md(
        "## Tahap 2: Konsolidasi Data Sosio-Ekonomi BPS\n"
        "Menggabungkan 6 file CSV data ketenagakerjaan provinsi (BPS 2025) dari folder `data-bps/` "
        "menjadi satu dataset master. Proses pembersihan mencakup:\n"
        "- Penghapusan notasi kode wilayah `[3171]` pada nama Kabupaten/Kota\n"
        "- Perbaikan nilai numerik yang rusak akibat format Excel (separator titik, format tanggal slash, "
        "pembulatan ribuan)"
    ),
    code(bps_code + '\n\nmain()'),
    md(
        "## Tahap 3: Geocoding Wilayah (Koordinat Centroid)\n"
        "Mengambil koordinat (Latitude & Longitude) pusat wilayah 119 Kabupaten/Kota di Pulau Jawa "
        "menggunakan OpenStreetMap Nominatim dengan rate limiter 1 detik.\n\n"
        "> **Catatan:** Jika `data/java_regency_coordinates.csv` sudah ada, tahap ini otomatis dilewati."
    ),
    code(geocode_code),
    md(
        "## Tahap 4: Integrasi Data Spasial & Sosio-Ekonomi (Data Fusion)\n"
        "Data mentah lowongan Jobstreet digabungkan dengan koordinat wilayah dan data kependudukan BPS.\n"
        "Karena penamaan kota di Jobstreet tidak standar (misal `\"Cikarang\"` → Kabupaten Bekasi, "
        "`\"Purwokerto\"` → Banyumas), digunakan **Fuzzy String Matching (RapidFuzz)** dengan tabel "
        "rescue manual dan threshold kecocokan minimum 80%."
    ),
    code(fusion_code + '\n\nmain()'),
    md(
        "## Tahap 5: Penghitungan Opportunity Index & Integrasi Spasial\n"
        "Menyatukan 119 wilayah GeoJSON dengan data BPS, koordinat, dan volume lowongan.\n\n"
        "$$Opportunity\\ Index = \\frac{Total\\ Lowongan}{Jumlah\\ Angkatan\\ Kerja\\ (BPS)}$$\n\n"
        "Klasifikasi:\n"
        "- **Lautan Peluang** — indeks ≥ median regional & volume > 5 lowongan\n"
        "- **Zona Merah** — di bawah median atau tidak memiliki cukup lowongan"
    ),
    code(oppidx_code + '\n\nmain()'),
    md(
        "## Tahap 6: Klastering Spasial Multidimensi dengan DBSCAN\n"
        "Algoritma **DBSCAN** (*Density-Based Spatial Clustering of Applications with Noise*) "
        "digunakan untuk mengelompokkan wilayah ke dalam aglomerasi hub ekonomi.\n\n"
        "**Keputusan desain:**\n"
        "- Hanya koordinat `(Latitude, Longitude)` yang digunakan sebagai fitur — *pure spatial clustering*\n"
        "- `job_volume` **tidak** diikutsertakan sebagai fitur karena mendistorsi jarak Euclidean "
        "(kota besar seperti Surabaya menjadi noise)\n"
        "- Wilayah dengan `job_volume = 0` dikecualikan sebelum DBSCAN untuk menghindari klaster semu "
        "(seperti Madura yang dense secara geografis tapi tidak punya lowongan)\n"
        "- `eps=0.40`, `min_samples=3` dipilih dari grid search k-distance plot\n\n"
        "**Hasil yang diharapkan:**\n"
        "- **Cluster 0** — Koridor mainland Jawa (Surabaya, Bandung, Semarang, GKS, dll)\n"
        "- **Cluster 1** — Aglomerasi Jabodetabek & koridor barat (Serang, Karawang, Cilegon, dll)\n"
        "- **Cluster -1** — Isolated zone (0 lowongan atau outlier geografis)"
    ),
    code(dbscan_code + '\n\nmain()'),
    md(
        "## Tahap 7: Visualisasi Hasil Eksploratif\n"
        "Tiga visualisasi berikut dapat disimpan langsung dari Colab:\n"
        "1. **Peta Klaster Spasial** — scatter plot koordinat, warna per cluster, ukuran ∝ volume lowongan\n"
        "2. **Heatmap Opportunity Index** — bar chart horizontal Top 20 wilayah\n"
        "3. **Ringkasan Klaster** — boxplot, pie chart, total lowongan, dan metrik evaluasi model"
    ),
    code(viz1),
    code(viz2),
    code(viz3),
    md(
        "---\n"
        "## Ringkasan Hasil Pipeline\n\n"
        "| Output File | Deskripsi | Baris |\n"
        "|---|---|---|\n"
        "| `data/master_bps_socioeconomic.csv` | Data BPS 6 provinsi yang sudah dibersihkan | 125 |\n"
        "| `data/java_regency_coordinates.csv` | Koordinat centroid 119 Kabupaten/Kota | 119 |\n"
        "| `data/integrated_job_market_java_v2.csv` | Lowongan terdedup + koordinat + BPS | ~18.182 |\n"
        "| `data/java_job_market_final_analysis.csv` | 119 wilayah + opportunity index | 119 |\n"
        "| `data/java_job_market_hubs_final.csv` | + cluster_id & hub_type dari DBSCAN | 119 |\n\n"
        "| Visualisasi | File |\n"
        "|---|---|\n"
        "| Peta klaster spasial | `viz_cluster_map.png` |\n"
        "| Top 20 opportunity index | `viz_opportunity_index.png` |\n"
        "| Ringkasan klaster & metrik | `viz_cluster_summary.png` |\n\n"
        "**Metrik Evaluasi DBSCAN (eps=0.40, min_samples=3):**\n"
        "- Silhouette Score: **0.4722**\n"
        "- Davies-Bouldin Index: **0.5136**"
    ),
]

# ── tulis notebook ────────────────────────────────────────────────────────────
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"}
    },
    "cells": cells
}

out = 'spatial_clustering_pipeline.ipynb'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=2)

print(f"OK: {out} ditulis ({len(cells)} cells)")
