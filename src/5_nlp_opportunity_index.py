import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import os
import json

"""
TAHAP 4: NLP & OPPORTUNITY INDEX (REVISI FINAL)
Penulis: Antigravity AI
"""

def clean_bps_num(val):
    if pd.isna(val): return 0
    s = str(val).split('(')[0]
    s = s.replace('.', '').replace(',', '').strip()
    try: return float(s)
    except: return 0

def get_qualification_score(title):
    title = str(title).lower()
    if any(k in title for k in ['manager', 'kepala', 'director', 'lead', 'senior', 'head', 'vp', 'chief']):
        return 3
    if any(k in title for k in ['specialist', 'supervisor', 'coordinator', 'analyst', 'spv', 'expert']):
        return 2
    return 1

# Stopwords List
CUSTOM_STOP = {'pt', 'tbk', 'loker', 'dibutuhkan', 'urgent', 'hiring', 'area', 'penempatan', 'recruitment', 'staff', 'admin', 'cv', 'indo', 'indonesia', 'persero', 'daerah', 'posisi', 'dibuka', 'official'}

def main():
    print("=== TAHAP 4: NLP & INTEGRASI FINAL ===")
    
    data_dir = 'data'
    input_file = os.path.join(data_dir, 'integrated_job_market_java_v2.csv')
    geojson_file = os.path.join(data_dir, 'java_regencies.geojson')
    coord_file = os.path.join(data_dir, 'java_regency_coordinates.csv')
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} tidak ditemukan.")
        return
        
    df_jobs = pd.read_csv(input_file)
    
    # [DIHAPUS] Normalisasi nama wilayah ke format akademis (Kabupaten/Kota)
    # Langkah ini dihapus karena merusak proses left-join dengan GeoJSON asli.
    # df_jobs['matched_regency'] sudah tersinkronisasi otomatis dari `4_data_integration.py`
    
    # 1. LOAD MASTER LIST DARI GEOJSON (119 Wilayah)
    print("Memuat Master Wilayah Java...")
    with open(geojson_file, 'r') as f:
        g_data = json.load(f)
    master_names = sorted(list(set([f['properties']['clean_name'] for f in g_data['features']])))
    master_df = pd.DataFrame(master_names, columns=['matched_regency'])
    
    # 2. KONFIGURASI STOPWORDS (Hapus Noise Lokasi)
    print("Menyusun Stopwords dinamis...")
    loc_stopwords = set()
    for name in master_names:
        loc_stopwords.update(str(name).lower().split())
        loc_stopwords.add(str(name).lower())
    
    # Tambahan noise umum & administratif
    loc_stopwords.update({'jakarta', 'jawa', 'raya', 'pusat', 'selatan', 'utara', 'timur', 'barat', 'banten', 'jogja', 'yogyakarta', 'tengah'})
    loc_stopwords.update({'kabupaten', 'kota', 'provinsi', 'kecamatan', 'desa', 'kelurahan', 'wilayah'})
    ALL_STOPWORDS = loc_stopwords.union(CUSTOM_STOP)

    def clean_title(text):
        if not isinstance(text, str): return ""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        words = [w for w in text.split() if w not in ALL_STOPWORDS and len(w) > 2]
        return " ".join(words)

    # 3. PROSES DATA PEKERJAAN
    print("Memproses data pekerjaan & kualifikasi...")
    df_jobs['qual_score'] = df_jobs['title'].apply(get_qualification_score)
    df_jobs['clean_title'] = df_jobs['title'].apply(clean_title)
    df_jobs['labor_force_num'] = df_jobs['Angkatan Kerja - Jumlah Angkatan Kerja'].apply(clean_bps_num)
    
    # Agregasi data pekerjaan
    job_stats = df_jobs.groupby('matched_regency').agg({
        'id': 'count',
        'qual_score': 'mean',
        'clean_title': lambda x: " ".join(x)
    }).rename(columns={'id': 'job_volume', 'qual_score': 'competitive_index'})
    
    # Buat Referensi BPS & Provinsi (Untuk mengisi wilayah 0 lowongan)
    print("Menyusun referensi BPS & Provinsi...")
    bps_ref = df_jobs.groupby('matched_regency').agg({
        'labor_force_num': 'first',
        'Provinsi': 'first',
        'Latitude': 'first',
        'Longitude': 'first'
    })
    
    # 4. JOIN MASTER DENGAN JOBS (Left Join)
    print("Menggabungkan dengan Master Wilayah...")
    hub_stats = pd.merge(master_df, job_stats, on='matched_regency', how='left')
    
    # Isi data BPS/Geografis dari referensi (menggunakan 'left' join sederhana)
    hub_stats = pd.merge(hub_stats, bps_ref, on='matched_regency', how='left')
    
    # Fill defaults
    hub_stats['job_volume'] = hub_stats['job_volume'].fillna(0)
    hub_stats['competitive_index'] = hub_stats['competitive_index'].fillna(1.0)
    hub_stats['top_skills'] = ""
    hub_stats['opportunity_index'] = 0.0
    
    # 5. SINKRONISASI KOORDINAT (Untuk wilayah 0 lowongan)
    if os.path.exists(coord_file):
        print("Sinkronisasi Koordinat untuk wilayah kosong...")
        df_coords = pd.read_csv(coord_file)
        
        # Standardize for join (Hapus 'Kota ', 'Administrasi ', dan spasi untuk join koordinat)
        def std_j(n): return str(n).lower().replace('kota ', '').replace('jakarta ', '').replace('administrasi ', '').replace('kabupaten ', '').replace(' ', '').strip()
        
        df_coords['j_key'] = df_coords['City_Name'].apply(std_j)
        hub_stats['j_key'] = hub_stats['matched_regency'].apply(std_j)
        
        # Ambil koordinat unik pertama saja
        coord_map = df_coords.drop_duplicates(subset=['j_key'])
        
        # Map Latitude/Longitude yang masih kosong
        hub_stats = pd.merge(hub_stats, coord_map[['j_key', 'Latitude', 'Longitude']], on='j_key', how='left', suffixes=('', '_ref'))
        hub_stats['Latitude'] = hub_stats['Latitude'].fillna(hub_stats['Latitude_ref'])
        hub_stats['Longitude'] = hub_stats['Longitude'].fillna(hub_stats['Longitude_ref'])
        
        # Map Provinsi if missing
        if 'Provinsi' in df_coords.columns:
            hub_stats = pd.merge(hub_stats, coord_map[['j_key', 'Provinsi']], on='j_key', how='left', suffixes=('', '_ref'))
            hub_stats['Provinsi'] = hub_stats['Provinsi'].fillna(hub_stats['Provinsi_ref'])
            
        hub_stats.drop(columns=['j_key', 'Latitude_ref', 'Longitude_ref'], inplace=True, errors='ignore')
        if 'Provinsi_ref' in hub_stats.columns: hub_stats.drop(columns=['Provinsi_ref'], inplace=True)

    # 6. HITUNG PELUANG & TF-IDF
    mask = hub_stats['job_volume'] > 0
    hub_stats.loc[mask, 'opportunity_index'] = hub_stats.loc[mask, 'job_volume'] / hub_stats.loc[mask, 'labor_force_num'].replace(0, np.nan)
    hub_stats['opportunity_index'] = hub_stats['opportunity_index'].fillna(0)
    
    print("Ekstraksi Top Skills (TF-IDF)...")
    valid_titles = hub_stats[mask]['clean_title']
    if not valid_titles.empty:
        vec = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
        mtx = vec.fit_transform(valid_titles)
        feats = vec.get_feature_names_out()
        
        skills = []
        for i in range(len(valid_titles)):
            row = mtx.getrow(i).toarray()[0]
            top = row.argsort()[-5:][::-1]
            skills.append(", ".join([feats[idx] for idx in top if row[idx] > 0]))
        hub_stats.loc[mask, 'top_skills'] = skills

    # 7. KLASIFIKASI & CLEANUP
    med_opp = hub_stats[mask]['opportunity_index'].median() if any(mask) else 0
    hub_stats['prosperity_status'] = np.where(hub_stats['opportunity_index'] >= med_opp, "Lautan Peluang", "Zona Merah")
    
    # Fill remaining NaNs
    hub_stats['Latitude'] = hub_stats['Latitude'].fillna(0)
    hub_stats['Longitude'] = hub_stats['Longitude'].fillna(0)
    hub_stats['Provinsi'] = hub_stats['Provinsi'].fillna("Jawa")
    hub_stats.drop(columns=['clean_title'], inplace=True, errors='ignore')
    
    # EXPORT
    output_path = os.path.join(data_dir, 'java_job_market_final_analysis.csv')
    hub_stats.to_csv(output_path, index=False)
    print(f"Sukses! Data final disimpan: {output_path} (Total Wilayah: {len(hub_stats)})")

if __name__ == "__main__":
    main()
