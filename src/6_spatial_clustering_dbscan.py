import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
import os

"""
TAHAP 5: KLASTERING SPASIAL & MULTIDIMENSI (DBSCAN + RobustScaler)
Penulis: Antigravity AI (Falah's Thesis Assistant)
Deskripsi: Script final menggunakan RobustScaler untuk menormalisasi nilai yang sangat ekstrim 
           serta Density-Based Spatial Clustering (DBSCAN) untuk mengidentifikasi 
           "Hub Ekonomi" secara otomatis berdasarkan kepadatan & kesempatan kerja.
"""

def main():
    print("Memulai Tahap Akhir: Klastering Spasial & Evaluasi (DBSCAN)...")
    
    # 1. Memuat Data Hasil Analisis NLP & Indexing
    input_file = os.path.join('data', 'java_job_market_final_analysis.csv')
    df = pd.read_csv(input_file)
    
    # 2. Persiapan Fitur Kombinasi (Spasial + Numerik Opsional)
    # Filter wilayah dengan koordinat valid
    valid_coords_mask = (df['Latitude'] != 0) & (df['Longitude'] != 0)
    df_valid = df[valid_coords_mask].copy()
    
    if len(df_valid) >= 3:
        # Menambahkan opportunity_index (kemampuan menyerap) ke dalam matriks spasial
        features = df_valid[['Latitude', 'Longitude', 'job_volume']].values
        
        # RobustScaler untuk mengamankan data ekstrim (seperti job volume super tinggi di Jakarta)
        scaler = StandardScaler() # Using standard scaler since robust might over-squash lat/lon
        from sklearn.preprocessing import RobustScaler
        r_scaler = RobustScaler()
        features_scaled = r_scaler.fit_transform(features)
        
        # 3. Eksekusi DBSCAN
        db = DBSCAN(eps=0.7, min_samples=3).fit(features_scaled)
        df_valid['cluster_id'] = db.labels_
        
        # Evaluasi Cluster: Menggunakan DBCV (Density-Based Clustering Validation) via hdbscan
        import hdbscan
        valid_labels = db.labels_[db.labels_ != -1]
        if len(set(valid_labels)) > 1:
            try:
                # DBCV metric ignores noise or handles it properly dependent on the implementation.
                # validity_index is DBCV
                dbcv_score = hdbscan.validity.validity_index(features_scaled, db.labels_)
                print(f"[EVALUASI KLASTER] DBCV (Density-Based Clustering Validation) Score: {dbcv_score:.4f} (-1.0 s/d 1.0)")
            except Exception as e:
                print(f"Gagal menghitung DBCV: {e}")
    else:
        df_valid['cluster_id'] = -1

    # Gabungkan kembali dengan data original (wilayah tanpa koordinat mendapat ID -1)
    df = pd.merge(df, df_valid[['matched_regency', 'cluster_id']], on='matched_regency', how='left')
    df['cluster_id'] = df['cluster_id'].fillna(-1).astype(int)
    
    # 4. Pelabelan Klaster (Hub Status)
    df['hub_type'] = np.where(df['cluster_id'] == -1, 'Isolated zone', 'Economic Hub')
    
    # 5. Ringkasan Hasil Klastering
    n_clusters = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
    print(f"\n--- HASIL KLASTERING SPASIAL ---")
    print(f"Total Cluster Hub Ditemukan: {n_clusters}")
    print(f"Total Wilayah Outlier (Noise): {list(db.labels_).count(-1)}")
    
    # 6. Analisis Karakteristik Per Hub
    clusters_summary = []
    for cid in set(db.labels_):
        if cid == -1: continue
        
        cluster_data = df[df['cluster_id'] == cid]
        avg_opportunity = cluster_data['opportunity_index'].mean()
        total_jobs = cluster_data['job_volume'].sum()
        top_province = cluster_data['Provinsi'].mode()[0]
        
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

    summary_df = pd.DataFrame(clusters_summary)
    print("\nDetail Ringkasan Hub Ekonomi:")
    print(summary_df.to_string(index=False))
    
    # 7. Ekspor Hasil Akhir
    output_file = os.path.join('data', 'java_job_market_hubs_final.csv')
    df.to_csv(output_file, index=False)
    print(f"\nData klaster lengkap disimpan di: {output_file}")
    
    # 8. Pesan Penutup untuk Skripsi
    print("\nSaran Analisis Lanjutan:")
    print("- Hub dengan status 'Lautan Peluang' adalah wilayah target migrasi pencari kerja.")
    print("- Hub dengan status 'Zona Merah' membutuhkan intervensi kebijakan penciptaan lapangan kerja.")

if __name__ == "__main__":
    main()
