import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import silhouette_score, davies_bouldin_score
import os

"""
TAHAP 5: KLASTERING SPASIAL & MULTIDIMENSI
Penulis     : Falah Fahrurozi (Skripsi UNINDRA)
Normalisasi : Min-Max Normalization (Latitude, Longitude, Opportunity Index)
Kalibrasi   : eps dipilih otomatis — sweep mencari 2 cluster dengan Silhouette terbaik
"""

def main():
    print("Memulai Tahap Akhir: Klastering Spasial (DBSCAN)...")

    input_file = os.path.join('data', 'java_job_market_final_analysis.csv')
    df = pd.read_csv(input_file)

    valid_coords_mask = (
        (df['Latitude']  != 0.0) &
        (df['Longitude'] != 0.0) &
        (df['job_volume'] > 0)
    )
    df_valid = df[valid_coords_mask].copy()

    if len(df_valid) >= 3:
        # Fitur: Latitude, Longitude, Opportunity Index  |  Min-Max ke [0,1]
        features = df_valid[['Latitude', 'Longitude', 'opportunity_index']].copy().values
        scaler = MinMaxScaler()
        features_scaled = scaler.fit_transform(features)

        # ── Auto-kalibrasi eps ──────────────────────────────────────────────
        best_eps = 0.40
        best_sil = -1.0
        TARGET_CLUSTERS = 2

        print("\n--- AUTO-KALIBRASI EPS (MinMax 3D: Lat, Lon, OI) ---")
        for eps_c in np.arange(0.25, 0.85, 0.05):
            eps_c = round(float(eps_c), 2)
            tmp_labels = DBSCAN(eps=eps_c, min_samples=3).fit(features_scaled).labels_
            n_c  = len(set(tmp_labels)) - (1 if -1 in tmp_labels else 0)
            mask = tmp_labels != -1
            if n_c == TARGET_CLUSTERS and mask.sum() > 1:
                sil = silhouette_score(features_scaled[mask], tmp_labels[mask])
                print(f"  eps={eps_c:.2f} -> {n_c} cluster | Silhouette={sil:.4f}  OK")
                if sil > best_sil:
                    best_sil, best_eps = sil, eps_c
            else:
                print(f"  eps={eps_c:.2f} -> {n_c} cluster  --")

        print(f"\n-> EPS terpilih: {best_eps}  (Silhouette={best_sil:.4f})")

        # ── Eksekusi DBSCAN final ───────────────────────────────────────────
        db = DBSCAN(eps=best_eps, min_samples=3).fit(features_scaled)
        df_valid['cluster_id'] = db.labels_

        try:
            mask_nn = db.labels_ != -1
            if len(set(db.labels_[mask_nn])) > 1:
                sil_f = silhouette_score(features_scaled[mask_nn], db.labels_[mask_nn])
                dbi_f = davies_bouldin_score(features_scaled[mask_nn], db.labels_[mask_nn])
                print(f"\n--- EVALUASI MODEL FINAL ---")
                print(f"Silhouette Score : {sil_f:.4f}")
                print(f"Davies-Bouldin   : {dbi_f:.4f}")
        except Exception as e:
            print(f"Gagal menghitung metrik: {e}")
    else:
        df_valid['cluster_id'] = -1

    df = pd.merge(df, df_valid[['matched_regency', 'cluster_id']], on='matched_regency', how='left')
    df['cluster_id'] = df['cluster_id'].fillna(-1).astype(int)
    df['hub_type']   = np.where(df['cluster_id'] == -1, 'Isolated zone', 'Economic Hub')

    labels     = df_valid['cluster_id'].values if 'cluster_id' in df_valid.columns else np.array([])
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    print(f"\n--- HASIL KLASTERING SPASIAL ---")
    print(f"Total Cluster Hub Ditemukan : {n_clusters}")
    print(f"Total Wilayah Outlier/Noise : {int((labels == -1).sum())}")

    clusters_summary = []
    for cid in sorted(set(df['cluster_id'])):
        if cid == -1: continue
        cd = df[df['cluster_id'] == cid]
        status = "Lautan Peluang" if cd['opportunity_index'].mean() > df['opportunity_index'].median() else "Zona Merah"
        clusters_summary.append({
            "Cluster_ID"  : cid,
            "Hub_Region"  : cd['Provinsi'].mode()[0] if not cd['Provinsi'].empty else "Jawa",
            "Total_Jobs"  : int(cd['job_volume'].sum()),
            "Avg_OI"      : round(cd['opportunity_index'].mean(), 5),
            "Status"      : status,
            "Member_Count": len(cd)
        })

    if clusters_summary:
        import pandas as _pd
        print("\nDetail Ringkasan Hub Ekonomi:")
        print(_pd.DataFrame(clusters_summary).to_string(index=False))

    output_file = os.path.join('data', 'java_job_market_hubs_final.csv')
    df.to_csv(output_file, index=False)
    print(f"\nData klaster disimpan: {output_file}")

if __name__ == "__main__":
    main()
