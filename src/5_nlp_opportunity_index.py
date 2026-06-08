import pandas as pd
import numpy as np
import os
import json

"""
TAHAP 4: PERHITUNGAN OPPORTUNITY INDEX & INTEGRASI DATA SPASIAL
Penulis: Antigravity AI
Deskripsi: Script ini menggabungkan batas administratif GeoJSON, data sosio-ekonomi BPS, 
           koordinat wilayah, dan volume pekerjaan dari Jobstreet secara utuh.
           TF-IDF dan pemrosesan teks NLP telah dihapus untuk berfokus pada Data Science Spasial.
"""

def get_qualification_score(title):
    title = str(title).lower()
    if any(k in title for k in ['manager', 'kepala', 'director', 'lead', 'senior', 'head', 'vp', 'chief']):
        return 3
    if any(k in title for k in ['specialist', 'supervisor', 'coordinator', 'analyst', 'spv', 'expert']):
        return 2
    return 1

def main():
    print("=== TAHAP 4: INTEGRASI DATA & OPPORTUNITY INDEX ===")
    
    data_dir = 'data'
    input_file = os.path.join(data_dir, 'integrated_job_market_java_v2.csv')
    geojson_file = os.path.join(data_dir, 'java_regencies.geojson')
    coord_file = os.path.join(data_dir, 'java_regency_coordinates.csv')
    bps_file = os.path.join(data_dir, 'master_bps_socioeconomic.csv')
    
    # Validasi file input
    for f_path in [input_file, geojson_file, coord_file, bps_file]:
        if not os.path.exists(f_path):
            print(f"Error: File '{f_path}' tidak ditemukan.")
            return
            
    df_jobs = pd.read_csv(input_file)
    
    # 1. LOAD MASTER LIST DARI GEOJSON (119 Wilayah)
    print("Memuat Master Wilayah dari GeoJSON...")
    with open(geojson_file, 'r') as f:
        g_data = json.load(f)
    master_names = sorted(list(set([f['properties']['clean_name'] for f in g_data['features']])))
    master_df = pd.DataFrame(master_names, columns=['matched_regency'])
    
    # Standardisasi nama untuk menyelaraskan GeoJSON dengan BPS & Koordinat
    # GeoJSON menggunakan: "Administrasi Kepulauan Seribu" dan "Gunungkidul"
    # BPS & Koordinat menggunakan: "Kepulauan Seribu" dan "Gunung Kidul"
    def std_name(name):
        if not isinstance(name, str): return ""
        name = name.strip()
        if name == 'Administrasi Kepulauan Seribu':
            return 'Kepulauan Seribu'
        if name == 'Gunungkidul':
            return 'Gunung Kidul'
        return name
        
    master_df['join_key'] = master_df['matched_regency'].apply(std_name)
    
    # 2. LOAD & INTEGRASIKAN DATA SOSIO-EKONOMI BPS
    print("Mengintegrasikan data sosio-ekonomi BPS...")
    df_bps = pd.read_csv(bps_file)
    df_bps['join_key'] = df_bps['Kabupaten/Kota'].apply(std_name)
    df_bps_unique = df_bps.drop_duplicates(subset=['join_key'])
    
    # Gabungkan data Angkatan Kerja (Labor Force)
    hub_stats = pd.merge(master_df, df_bps_unique[['join_key', 'Provinsi', 'Angkatan Kerja - Jumlah Angkatan Kerja']], on='join_key', how='left')
    hub_stats.rename(columns={'Angkatan Kerja - Jumlah Angkatan Kerja': 'labor_force_num'}, inplace=True)
    
    # 3. LOAD & INTEGRASIKAN KOORDINAT WILAYAH
    print("Mengintegrasikan koordinat geospasial...")
    df_coords = pd.read_csv(coord_file)
    df_coords['join_key'] = df_coords['City_Name'].apply(std_name)
    df_coords_unique = df_coords.drop_duplicates(subset=['join_key'])
    
    hub_stats = pd.merge(hub_stats, df_coords_unique[['join_key', 'Latitude', 'Longitude']], on='join_key', how='left')
    
    # Hapus join_key sementara
    hub_stats.drop(columns=['join_key'], inplace=True)
    
    # 4. PROSES & AGREGASI DATA VOLUME LOWONGAN
    print("Memproses volume pekerjaan & indeks kualifikasi...")
    df_jobs['qual_score'] = df_jobs['title'].apply(get_qualification_score)
    
    job_stats = df_jobs.groupby('matched_regency').agg({
        'id': 'count',
        'qual_score': 'mean'
    }).rename(columns={'id': 'job_volume', 'qual_score': 'competitive_index'})
    
    # Konversi indeks job_stats (dari nama koordinat/BPS) ke nama GeoJSON
    def rev_std_name(name):
        if name == 'Kepulauan Seribu':
            return 'Administrasi Kepulauan Seribu'
        if name == 'Gunung Kidul':
            return 'Gunungkidul'
        return name
        
    job_stats.index = job_stats.index.map(rev_std_name)
    job_stats.index.name = 'matched_regency'
    
    # 5. GABUNGKAN LOWONGAN KE DATAFRAME UTAMA
    print("Menggabungkan statistik lowongan ke master wilayah...")
    hub_stats = pd.merge(hub_stats, job_stats, on='matched_regency', how='left')
    
    # Mengisi default jika wilayah tidak memiliki lowongan kerja
    hub_stats['job_volume'] = hub_stats['job_volume'].fillna(0).astype(int)
    hub_stats['competitive_index'] = hub_stats['competitive_index'].fillna(1.0)
    
    # 6. HITUNG INDEKS PELUANG (OPPORTUNITY INDEX)
    print("Menghitung Opportunity Index...")
    # Gunakan .replace(0, np.nan) untuk menghindari pembagian dengan nol
    hub_stats['opportunity_index'] = hub_stats['job_volume'] / hub_stats['labor_force_num'].replace(0, np.nan)
    hub_stats['opportunity_index'] = hub_stats['opportunity_index'].fillna(0.0)
    
    # 7. KLASIFIKASI KESEJAHTERAAN & MEMBERSIHKAN NAN
    # Gunakan median dari wilayah yang memiliki lowongan kerja untuk pengelompokan
    mask_has_jobs = hub_stats['job_volume'] > 0
    med_opp = hub_stats[mask_has_jobs]['opportunity_index'].median() if any(mask_has_jobs) else 0.0
    hub_stats['prosperity_status'] = np.where(hub_stats['opportunity_index'] >= med_opp, "Lautan Peluang", "Zona Merah")
    
    # Pengisian data koordinat/provinsi sisa (jika ada yang terlewat)
    hub_stats['Latitude'] = hub_stats['Latitude'].fillna(0.0)
    hub_stats['Longitude'] = hub_stats['Longitude'].fillna(0.0)
    hub_stats['Provinsi'] = hub_stats['Provinsi'].fillna("Jawa")
    
    # EXPORT KE CSV
    output_path = os.path.join(data_dir, 'java_job_market_final_analysis.csv')
    hub_stats.to_csv(output_path, index=False)
    
    print(f"Sukses! Data final terintegrasi disimpan: {output_path} (Total Wilayah: {len(hub_stats)})")

if __name__ == "__main__":
    main()
