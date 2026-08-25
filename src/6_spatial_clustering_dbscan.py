import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
import os

"""
TAHAP 5: KLASTERING SPASIAL & MULTIDIMENSI (DBSCAN + MinMax Normalization)
Penulis: Falah Fahrurozi (Skripsi UNINDRA)
Deskripsi: Script menggunakan Min-Max Normalization untuk menormalisasi tiga variabel
           (Latitude, Longitude, Opportunity Index) ke rentang [0,1], kemudian
           Density-Based Spatial Clustering (DBSCAN) untuk mengidentifikasi
           hub ekonomi berdasarkan kepadatan spasio-ekonomi.
Kalibrasi : eps dipilih otomatis via sweep 0.03-0.24 (ruang 3D MinMax sangat kompak:
           p75 jarak antar titik = 0.26, sehingga eps >= 0.25 menyatukan semua titik).
"""

def main():
    print("Memulai Tahap Akhir: Klastering Spasial (DBSCAN)...")

    # 1. Memuat Data Hasil Analisis Indexing
    input_file = os.path.join('data', 'java_job_market_final_analysis.csv')
    df = pd.read_csv(input_file)

    # 2. Persiapan Fitur - filter wilayah dengan koordinat valid dan minimal 1 lowongan
    valid_coords_mask = (
        (df['Latitude']   != 0.0) &
        (df['Longitude']  != 0.0) &
        (df['job_volume'] > 0)
    )
    df_valid = df[valid_coords_mask].copy()

    if len(df_valid) >= 3:
        # Fitur clustering: koordinat spasial (Latitude, Longitude) + Opportunity Index.
        # Ketiga variabel dinormalisasi ke [0,1] menggunakan Min-Max Normalization agar
        # skala derajat koordinat (ratusan) tidak mendominasi Opportunity Index (desimal kecil).
        # Min-Max Normalization: x_norm = (x - x_min) / (x_max - x_min)
        features = df_valid[['Latitude', 'Longitude', 'opportunity_index']].copy().values
        scaler = MinMaxScaler()
        features_scaled = scaler.fit_transform(features)

        # 3. Auto-kalibrasi eps via sweep 0.03-0.24
        # Di ruang 3D MinMax dengan 116 titik Jawa, 75% pasang titik berjarak < 0.26,
        # sehingga eps >= 0.25 sudah menyatukan semua titik menjadi 1 cluster raksasa.
        # Sweep ini mencari eps yang menghasilkan tepat 2 cluster dengan Silhouette terbaik.
        best_eps, best_sil = 0.10, -1.0
        TARGET_CLUSTERS = 2

        print("\n--- AUTO-KALIBRASI EPS (MinMax 3D, sweep 0.03-0.24) ---")
        for eps_c in np.arange(0.03, 0.25, 0.01):
            eps_c = round(float(eps_c), 2)
            tmp   = DBSCAN(eps=eps_c, min_samples=3).fit(features_scaled).labels_
            n_c   = len(set(tmp)) - (1 if -1 in tmp else 0)
            mask  = tmp != -1
            if n_c == TARGET_CLUSTERS and mask.sum() > 1:
                sil = silhouette_score(features_scaled[mask], tmp[mask])
                print(f"  eps={eps_c:.2f} -> {n_c} cluster | Sil={sil:.4f}  OK")
                if sil > best_sil:
                    best_sil, best_eps = sil, eps_c
            else:
                print(f"  eps={eps_c:.2f} -> {n_c} cluster | noise={int((tmp==-1).sum())}  --")

        print(f"\n-> EPS terpilih: {best_eps}  (Silhouette={best_sil:.4f})")

        # 4. Eksekusi DBSCAN final dengan eps terpilih
        db = DBSCAN(eps=best_eps, min_samples=3).fit(features_scaled)
        df_valid['cluster_id'] = db.labels_

        # Evaluasi Model (Silhouette & DBI - Eksklusi Noise -1)
        try:
            mask_non_noise = db.labels_ != -1
            unique_labels  = set(db.labels_[mask_non_noise])
            if len(unique_labels) > 1:
                sil_score = silhouette_score(features_scaled[mask_non_noise], db.labels_[mask_non_noise])
                dbi_score = davies_bouldin_score(features_scaled[mask_non_noise], db.labels_[mask_non_noise])
                print(f"\n--- EVALUASI MODEL (Eksklusi Noise -1) ---")
                print(f"Silhouette Score (Cohesion) : {sil_score:.4f}  (-1 s/d 1)")
                print(f"Davies-Bouldin Index (DBI)  : {dbi_score:.4f}  (Semakin kecil semakin baik)")
        except Exception as e:
            print(f"Gagal menghitung Silhouette/DBI: {e}")
    else:
        df_valid['cluster_id'] = -1

    # Gabungkan kembali dengan data original
    df = pd.merge(df, df_valid[['matched_regency', 'cluster_id']], on='matched_regency', how='left')
    df['cluster_id'] = df['cluster_id'].fillna(-1).astype(int)

    # 5. Pelabelan Klaster
    df['hub_type'] = np.where(df['cluster_id'] == -1, 'Isolated zone', 'Economic Hub')

    # 6. Ringkasan Hasil Klastering
    labels     = df_valid['cluster_id'].values if 'cluster_id' in df_valid.columns else np.array([])
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    print(f"\n--- HASIL KLASTERING SPASIAL ---")
    print(f"Total Cluster Hub Ditemukan  : {n_clusters}")
    print(f"Total Wilayah Outlier (Noise): {list(labels).count(-1)}")

    # 7. Analisis Karakteristik Per Hub
    clusters_summary = []
    for cid in set(df['cluster_id']):
        if cid == -1:
            continue
        cluster_data    = df[df['cluster_id'] == cid]
        avg_opportunity = cluster_data['opportunity_index'].mean()
        total_jobs      = cluster_data['job_volume'].sum()
        top_province    = cluster_data['Provinsi'].mode()[0] if not cluster_data['Provinsi'].empty else "Jawa"
        status          = "Lautan Peluang" if avg_opportunity > df['opportunity_index'].median() else "Zona Merah"
        clusters_summary.append({
            "Cluster_ID"     : cid,
            "Hub_Region"     : top_province,
            "Total_Jobs"     : total_jobs,
            "Avg_Opportunity": round(avg_opportunity, 5),
            "Status"         : status,
            "Member_Count"   : len(cluster_data)
        })

    if clusters_summary:
        summary_df = pd.DataFrame(clusters_summary)
        print("\nDetail Ringkasan Hub Ekonomi:")
        print(summary_df.to_string(index=False))

    # 8. Ekspor Hasil Akhir
    output_file = os.path.join('data', 'java_job_market_hubs_final.csv')
    df.to_csv(output_file, index=False)
    print(f"\nData klaster lengkap disimpan di: {output_file}")

main()
