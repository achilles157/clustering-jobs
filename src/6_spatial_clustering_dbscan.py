import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler
import os

"""
TAHAP 5: KLASTERING SPASIAL & MULTIDIMENSI (DBSCAN + MinMax Normalization)
Penulis: Falah Fahrurozi (Skripsi UNINDRA)
Deskripsi: Script menggunakan Min-Max Normalization untuk menormalisasi tiga variabel
           (Latitude, Longitude, Opportunity Index) ke rentang [0,1], kemudian
           Density-Based Spatial Clustering (DBSCAN) untuk mengidentifikasi
           hub ekonomi berdasarkan kepadatan spasio-ekonomi.
"""

def main():
    print("Memulai Tahap Akhir: Klastering Spasial (DBSCAN)...")
    
    # 1. Memuat Data Hasil Analisis Indexing
    input_file = os.path.join('data', 'java_job_market_final_analysis.csv')
    df = pd.read_csv(input_file)
    
    # 2. Persiapan Fitur Kombinasi (Spasial + Numerik Opsional)
    # Filter wilayah dengan koordinat valid DAN memiliki minimal 1 lowongan kerja.
    # Wilayah tanpa lowongan (job_volume=0) dikecualikan dari DBSCAN agar tidak
    # membentuk klaster semu berdasarkan kedekatan geografis semata (contoh: Madura).
    valid_coords_mask = (
        (df['Latitude'] != 0.0) &
        (df['Longitude'] != 0.0) &
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
        
        # 3. Eksekusi DBSCAN
        # eps=0.40, min_samples=3 dipilih dari grid search k-distance.
        # eps=0.40 cukup ketat untuk memisahkan aglomerasi Jabodetabek (Cluster 1)
        # dari koridor mainland Jawa (Cluster 0), tanpa menarik outlier sejati masuk klaster.
        db = DBSCAN(eps=0.40, min_samples=3).fit(features_scaled)
        df_valid['cluster_id'] = db.labels_
        
        # Evaluasi Model (Silhouette & DBI - Eksklusi Noise -1)
        try:
            from sklearn.metrics import silhouette_score, davies_bouldin_score
            mask_non_noise = db.labels_ != -1
            unique_labels = set(db.labels_[mask_non_noise])
            if len(unique_labels) > 1:
                sil_score = silhouette_score(features_scaled[mask_non_noise], db.labels_[mask_non_noise])
                dbi_score = davies_bouldin_score(features_scaled[mask_non_noise], db.labels_[mask_non_noise])
                print(f"\n--- EVALUASI MODEL (Eksklusi Noise -1) ---")
                print(f"Silhouette Score (Cohesion): {sil_score:.4f} (-1 s/d 1)")
                print(f"Davies-Bouldin Index (DBI): {dbi_score:.4f} (Semakin kecil semakin baik)")
        except Exception as e:
            print(f"Gagal menghitung Silhouette/DBI: {e}")
            
        # Evaluasi Cluster menggunakan DBCV jika memungkinkan
        try:
            import hdbscan
            valid_labels = db.labels_[db.labels_ != -1]
            if len(set(valid_labels)) > 1:
                dbcv_score = hdbscan.validity.validity_index(features_scaled, db.labels_)
                print(f"DBCV Score: {dbcv_score:.4f} (-1.0 s/d 1.0)")
        except Exception as e:
            pass
    else:
        df_valid['cluster_id'] = -1

    # Gabungkan kembali dengan data original (wilayah tanpa koordinat mendapat ID -1)
    df = pd.merge(df, df_valid[['matched_regency', 'cluster_id']], on='matched_regency', how='left')
    df['cluster_id'] = df['cluster_id'].fillna(-1).astype(int)
    
    # 4. Pelabelan Klaster (Hub Status)
    df['hub_type'] = np.where(df['cluster_id'] == -1, 'Isolated zone', 'Economic Hub')
    
    # 5. Ringkasan Hasil Klastering
    labels = df_valid['cluster_id'].values if 'cluster_id' in df_valid.columns else np.array([])
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    print(f"\n--- HASIL KLASTERING SPASIAL ---")
    print(f"Total Cluster Hub Ditemukan: {n_clusters}")
    print(f"Total Wilayah Outlier (Noise): {list(labels).count(-1)}")
    
    # 6. Analisis Karakteristik Per Hub
    clusters_summary = []
    for cid in set(df['cluster_id']):
        if cid == -1: continue
        
        cluster_data = df[df['cluster_id'] == cid]
        avg_opportunity = cluster_data['opportunity_index'].mean()
        total_jobs = cluster_data['job_volume'].sum()
        top_province = cluster_data['Provinsi'].mode()[0] if not cluster_data['Provinsi'].empty else "Jawa"
        
        # Penentuan Status "Lautan Peluang" per Klaster
        status = "Lautan Peluang" if avg_opportunity > df['opportunity_index'].median() else "Zona Merah"
        
        clusters_summary.append({
            "Cluster_ID": cid,
            "Hub_Region": top_province,
            "Total_Jobs": total_jobs,
            "Avg_Opportunity": round(avg_opportunity, 5),
            "Status": status,
            "Member_Count": len(cluster_data)
        })

    if clusters_summary:
        summary_df = pd.DataFrame(clusters_summary)
        print("\nDetail Ringkasan Hub Ekonomi:")
        print(summary_df.to_string(index=False))
    
    # 7. Ekspor Hasil Akhir
    output_file = os.path.join('data', 'java_job_market_hubs_final.csv')
    df.to_csv(output_file, index=False)
    print(f"\nData klaster lengkap disimpan di: {output_file}")

if __name__ == "__main__":
    main()
