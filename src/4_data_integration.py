import pandas as pd
from rapidfuzz import process, utils
import os

"""
TAHAP 3: INTEGRASI DATA (DATA FUSION)
Penulis: Antigravity AI (Falah's Thesis Assistant)
Deskripsi: Script ini menggabungkan data lowongan kerja (Jobstreet) dengan 
           koordinat wilayah dan data kependudukan (BPS) menggunakan teknik 
           Fuzzy String Matching untuk sinkronisasi nama wilayah.
"""

def main():
    print("Memulai Integrasi Data Spasial & Sosio-Ekonomi...")
    
    # 1. Memuat Dataset
    df_js = pd.read_csv('data/jobstreet_results.csv')
    df_coords = pd.read_csv('data/java_regency_coordinates.csv')
    df_bps = pd.read_csv('data/master_bps_socioeconomic.csv')

    # 2. Persiapan Daftar Wilayah (Master Regency)
    lookup_list = df_coords['City_Name'].tolist()
    
    # 3. Fungsi Pemetaan Fuzzy (Rescue Mapping)
    # Memetakan nama kecamatan/kawasan industri ke Kabupaten/Kota induknya
    cache = {
        "Cikarang Pusat, Jawa Barat": ("Bekasi", 100),
        "Cikarang, Jawa Barat": ("Bekasi", 100),
        "Cikarang": ("Bekasi", 100),
        "Kebayoran Lama, Jakarta Raya": ("Kota Jakarta Selatan", 100),
        "Kebayoran Baru, Jakarta Raya": ("Kota Jakarta Selatan", 100),
        "Kemayoran, Jakarta Raya": ("Kota Jakarta Pusat", 100),
        "Cikupa, Banten": ("Tangerang", 100),
        "Ciawi, Jawa Barat": ("Bogor", 100),
        "Serpong, Banten": ("Kota Tangerang Selatan", 100),
        "Bsd City, Banten": ("Kota Tangerang Selatan", 100),
        "Cileungsi, Jawa Barat": ("Bogor", 100),
        "Kalideres, Jakarta Raya": ("Kota Jakarta Barat", 100),
        "Kelapa Gading, Jakarta Raya": ("Kota Jakarta Utara", 100),
        "Gunung Putri, Jawa Barat": ("Bogor", 100),
        "Purwokerto": ("Banyumas", 100),
        "Padalarang, Jawa Barat": ("Bandung Barat", 100),
        "Pulo Gadung, Jakarta Raya": ("Kota Jakarta Timur", 100),
        "Waru, Jawa Timur": ("Sidoarjo", 100),
        "Cengkareng, Jakarta Raya": ("Kota Jakarta Barat", 100),
        "Balaraja, Banten": ("Tangerang", 100),
        "Penjaringan, Jakarta Raya": ("Kota Jakarta Utara", 100),
        "Tambun, Jawa Barat": ("Bekasi", 100),
        "Matraman, Jakarta Raya": ("Kota Jakarta Timur", 100),
        "Sunter, Jakarta Raya": ("Kota Jakarta Utara", 100),
        "Cikande, Banten": ("Serang", 100),
        "Pesanggrahan, Jakarta Raya": ("Kota Jakarta Selatan", 100),
        "Gunung Sindur, Jawa Barat": ("Bogor", 100),
        "Driyorejo, Jawa Timur": ("Gresik", 100),
        "Jetis, DI Yogyakarta": ("Kota Yogyakarta", 100),
        "Batujajar, Jawa Barat": ("Bandung Barat", 100),
        "Gedangan, Jawa Timur": ("Sidoarjo", 100),
        "Kebon Jeruk, Jakarta Raya": ("Kota Jakarta Barat", 100),
        "Setiabudi, Jakarta Raya": ("Kota Jakarta Selatan", 100),
    }

    def get_best_match(loc_string):
        if not isinstance(loc_string, str) or not loc_string.strip():
            return None, 0
        
        loc_string = loc_string.strip()
        if loc_string in cache:
            return cache[loc_string]
        
        # Ambil bagian utama nama lokasi (sebelum koma)
        primary = loc_string.split(',')[0].strip()
        
        # Gunakan fuzzy matching untuk mencari kecocokan terbaik
        match = process.extractOne(primary, lookup_list, processor=utils.default_process)
        if match:
            cache[loc_string] = (match[0], match[1])
            return match[0], match[1]
        return None, 0

    # 4. Menjalankan Pemetaan
    print(f"Memetakan {len(df_js)} data lowongan ke {len(lookup_list)} wilayah standar...")
    df_js[['matched_regency', 'match_score']] = df_js['location'].apply(
        lambda x: pd.Series(get_best_match(x))
    )

    # 5. Filter Data Valid (Threshold > 80)
    # Menghapus data yang tidak spesifik (misal: "Jawa Timur") atau tidak ada koordinatnya
    good_matches = df_js[df_js['match_score'] >= 80].copy()
    
    # 6. Penggabungan Koordinat
    final_df = pd.merge(
        good_matches, 
        df_coords, 
        left_on='matched_regency', 
        right_on='City_Name', 
        how='left'
    )
    
    # 7. Penggabungan Data BPS
    def bps_standardize(name):
        return name.replace('Kota ', '').replace('Kab. ', '').replace('Kabupaten ', '').strip().lower()

    df_bps['bps_match_key'] = df_bps['Kabupaten/Kota'].apply(bps_standardize)
    final_df['js_match_key'] = final_df['matched_regency'].apply(bps_standardize)

    final_df = pd.merge(
        final_df,
        df_bps,
        left_on='js_match_key',
        right_on='bps_match_key',
        how='left'
    )

    # 8. Seleksi Kolom Akhir
    cols_to_keep = [
        'id', 'title', 'company', 'location', 'matched_regency', 'match_score',
        'Latitude', 'Longitude', 'Provinsi',
        'Angkatan Kerja - Bekerja', 'Angkatan Kerja Pengangguran - Jumlah',
        'Angkatan Kerja - Jumlah Angkatan Kerja', 
        'Angkatan Kerja + Bukan Angkatan Kerja (Jumlah )'
    ]
    final_df = final_df[cols_to_keep].drop_duplicates(subset=['id'])

    # 9. Ekspor Hasil
    output_file = 'data/integrated_job_market_java_v2.csv'
    final_df.to_csv(output_file, index=False)
    
    print(f"\n--- RINGKASAN INTEGRASI ---")
    print(f"Total Lowongan Input: {len(df_js)}")
    print(f"Berhasil Dipetakan: {len(final_df)} ({len(final_df)/len(df_js)*100:.1f}%)")
    print(f"Dataset terintegrasi disimpan di: {output_file}")

if __name__ == "__main__":
    main()
