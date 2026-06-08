import pandas as pd
import numpy as np
import os

def run_verification():
    print("=== MEMULAI VERIFIKASI AKHIR PIPELINE ===")
    
    file_path = os.path.join('data', 'java_job_market_hubs_final.csv')
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' tidak ditemukan. Silakan jalankan seluruh pipeline terlebih dahulu.")
        return False
        
    df = pd.read_csv(file_path)
    
    # 1. Cek jumlah baris (harus 119 wilayah dari GeoJSON)
    print(f"1. Memeriksa jumlah wilayah... Total: {len(df)} (Harus 119)")
    assert len(df) == 119, f"Jumlah wilayah salah: {len(df)}"
    
    # 2. Cek apakah ada NaN pada kolom utama
    cols_to_check = ['matched_regency', 'labor_force_num', 'Latitude', 'Longitude', 'job_volume', 'opportunity_index', 'cluster_id']
    for col in cols_to_check:
        null_count = df[col].isna().sum()
        print(f"2. Memeriksa nilai Null pada kolom '{col}'... Null: {null_count}")
        assert null_count == 0, f"Ditemukan nilai Null pada kolom '{col}': {null_count}"
        
    # 3. Cek apakah ada nilai 0 pada labor_force_num
    zero_lf_count = (df['labor_force_num'] == 0).sum()
    print(f"3. Memeriksa nilai 0 pada labor_force_num... Zeroes: {zero_lf_count}")
    assert zero_lf_count == 0, f"Ditemukan nilai 0 pada labor_force_num: {zero_lf_count}"
    
    # 4. Verifikasi nilai angkatan kerja spesifik (Banyumas & Kota Tasikmalaya)
    tasik = df[df['matched_regency'] == 'Kota Tasikmalaya'].iloc[0]
    banyumas = df[df['matched_regency'] == 'Banyumas'].iloc[0]
    
    print(f"4. Verifikasi Angkatan Kerja Kota Tasikmalaya: {tasik['labor_force_num']} (Harus 385800.0)")
    assert np.isclose(tasik['labor_force_num'], 385800.0), f"Nilai Tasikmalaya salah: {tasik['labor_force_num']}"
    
    print(f"5. Verifikasi Angkatan Kerja Banyumas: {banyumas['labor_force_num']} (Harus 1024068.0)")
    assert np.isclose(banyumas['labor_force_num'], 1024068.0), f"Nilai Banyumas salah: {banyumas['labor_force_num']}"
    
    # 5. Cek perbedaan koordinat Kabupaten vs Kota Bandung
    kab_bdg = df[df['matched_regency'] == 'Bandung'].iloc[0]
    kot_bdg = df[df['matched_regency'] == 'Kota Bandung'].iloc[0]
    
    print(f"6. Memeriksa koordinat Bandung (Kabupaten vs Kota)...")
    print(f"   Kabupaten Bandung: {kab_bdg['Latitude']}, {kab_bdg['Longitude']}")
    print(f"   Kota Bandung:      {kot_bdg['Latitude']}, {kot_bdg['Longitude']}")
    
    assert (kab_bdg['Latitude'] != kot_bdg['Latitude']) or (kab_bdg['Longitude'] != kot_bdg['Longitude']), \
        "Koordinat Kabupaten Bandung dan Kota Bandung tidak boleh sama!"
    
    # 6. Cek perbedaan koordinat Kabupaten vs Kota Bogor
    kab_bgr = df[df['matched_regency'] == 'Bogor'].iloc[0]
    kot_bgr = df[df['matched_regency'] == 'Kota Bogor'].iloc[0]
    
    print(f"7. Memeriksa koordinat Bogor (Kabupaten vs Kota)...")
    print(f"   Kabupaten Bogor:   {kab_bgr['Latitude']}, {kab_bgr['Longitude']}")
    print(f"   Kota Bogor:        {kot_bgr['Latitude']}, {kot_bgr['Longitude']}")
    
    assert (kab_bgr['Latitude'] != kot_bgr['Latitude']) or (kab_bgr['Longitude'] != kot_bgr['Longitude']), \
        "Koordinat Kabupaten Bogor dan Kota Bogor tidak boleh sama!"
        
    print("\n>>> PIPELINE DATA TERVERIFIKASI 100% SUKSES DAN AKURAT! <<<")
    return True

if __name__ == "__main__":
    run_verification()
