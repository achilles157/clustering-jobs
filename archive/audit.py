import pandas as pd
import numpy as np

print("=== AUDIT PIPELINE DATA ===")

# 1. CEK INTEGRASI BPS & JOBS
try:
    df_integrated = pd.read_csv('data/integrated_job_market_java_v2.csv')
    print(f"\n[TAHAP 3] Data Terintegrasi: {df_integrated.shape[0]} lowongan (unik: {df_integrated['id'].nunique()})")
    null_coords = df_integrated['Latitude'].isnull().sum()
    print(f"Lowongan tanpa koordinat: {null_coords}")
except Exception as e:
    print("Error reading integrated:", e)

# 2. CEK FINAL ANALYSIS (NLP & aggregasi)
try:
    df_final = pd.read_csv('data/java_job_market_final_analysis.csv')
    print(f"\n[TAHAP 4] Agregasi NLP: {df_final.shape[0]} wilayah")
    
    # Cek duplikat regency
    dupes = df_final['matched_regency'].duplicated().sum()
    print(f"Duplikat nama wilayah: {dupes}")
    
    # Cek konsistensi perhitungan Opportunity Index = Volume / Angkatan Kerja
    df_final['cek_opp'] = (df_final['job_volume'] / df_final['labor_force_num']).replace([np.inf, -np.inf], 0).fillna(0)
    mismatch = (abs(df_final['opportunity_index'] - df_final['cek_opp']) > 0.0001).sum()
    print(f"Ketidaksesuaian hitungan Opportunity Index: {mismatch} baris")
    
    # Cek nilai NaN tersembunyi
    nans = df_final[['job_volume', 'opportunity_index', 'Latitude', 'Longitude']].isnull().sum()
    print(f"Missing values pada kolom inti:\n{nans.to_string()}")
    
    # Cek apakah ada Top Skills yang memuat kata kota/kabupaten
    noise_skills = df_final['top_skills'].str.contains('kota|kabupaten|jakarta|jawa|selatan|pusat|timur|barat|utara', case=False, na=False).sum()
    print(f"Daerah yang masih memuat noise geografis di Top Skills: {noise_skills}")
    
    # Cek kesesuaian koordinat dengan geojson
    import json
    with open('data/java_regencies.geojson') as f:
        g = json.load(f)
    g_names = {f['properties']['clean_name'] for f in g['features']}
    df_names = set(df_final['matched_regency'].unique())
    print(f"Wilayah di DF yang tidak ada di GeoJSON: {df_names - g_names}")
except Exception as e:
    print("Error reading final analysis:", e)

# 3. CEK CLUSTERING RESULT
try:
    df_hubs = pd.read_csv('data/java_job_market_hubs_final.csv')
    print(f"\n[TAHAP 5] Hasil DBSCAN: {df_hubs.shape[0]} wilayah")
    print(f"Distribusi Klaster:\n{df_hubs['cluster_id'].value_counts().to_string()}")
    
except Exception as e:
    print("Error reading hubs final:", e)

print("\n--- SELESAI ---")
