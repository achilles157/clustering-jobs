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
    cols_to_check = [
        'matched_regency', 'labor_force_num', 'unemployment_num',
        'Latitude', 'Longitude', 'job_volume', 'opportunity_index', 'cluster_id'
    ]
    for col in cols_to_check:
        if col not in df.columns:
            print(f"2. FAIL — kolom '{col}' tidak ditemukan di CSV!")
            assert False, f"Kolom '{col}' hilang dari output pipeline"
        null_count = df[col].isna().sum()
        print(f"2. Memeriksa nilai Null pada kolom '{col}'... Null: {null_count}")
        assert null_count == 0, f"Ditemukan nilai Null pada kolom '{col}': {null_count}"

    # 3. Cek formula OI: denominator = unemployment_num (bukan labor_force_num)
    #    OI = job_volume / unemployment_num — verifikasi konsistensi
    df_valid = df[(df['unemployment_num'] > 0) & (df['job_volume'] > 0)].copy()
    df_valid['oi_recalc'] = df_valid['job_volume'] / df_valid['unemployment_num']
    mismatch = (abs(df_valid['opportunity_index'] - df_valid['oi_recalc']) > 0.0001).sum()
    print(f"3. Verifikasi formula OI (job_volume / unemployment_num)... Mismatch: {mismatch}")
    assert mismatch == 0, f"Formula OI tidak konsisten: {mismatch} wilayah mismatch"

    # 4. Cek zero unemployment_num hanya boleh ada di wilayah tanpa lowongan
    zero_unemp_with_jobs = ((df['unemployment_num'] == 0) & (df['job_volume'] > 0)).sum()
    print(f"4. Cek wilayah ber-lowongan tapi unemployment_num=0... Count: {zero_unemp_with_jobs}")
    assert zero_unemp_with_jobs == 0, f"Ada {zero_unemp_with_jobs} wilayah ber-lowongan tapi unemployment_num=0"

    # 5. Verifikasi nilai pengangguran terbuka — Kota Tasikmalaya & Banyumas
    tasik   = df[df['matched_regency'] == 'Kota Tasikmalaya'].iloc[0]
    banyumas = df[df['matched_regency'] == 'Banyumas'].iloc[0]
    print(f"5. Pengangguran Terbuka Kota Tasikmalaya : {tasik['unemployment_num']:.0f}")
    print(f"   Pengangguran Terbuka Banyumas          : {banyumas['unemployment_num']:.0f}")
    assert tasik['unemployment_num'] > 0,   "unemployment_num Tasikmalaya harus > 0"
    assert banyumas['unemployment_num'] > 0, "unemployment_num Banyumas harus > 0"

    # 6. Cek perbedaan koordinat Kabupaten vs Kota Bandung
    kab_bdg = df[df['matched_regency'] == 'Bandung'].iloc[0]
    kot_bdg = df[df['matched_regency'] == 'Kota Bandung'].iloc[0]
    print(f"6. Koordinat Bandung — Kab: ({kab_bdg['Latitude']:.4f}, {kab_bdg['Longitude']:.4f}) | "
          f"Kota: ({kot_bdg['Latitude']:.4f}, {kot_bdg['Longitude']:.4f})")
    assert (kab_bdg['Latitude'] != kot_bdg['Latitude']) or (kab_bdg['Longitude'] != kot_bdg['Longitude']), \
        "Koordinat Kabupaten Bandung dan Kota Bandung tidak boleh sama!"

    # 7. Cek perbedaan koordinat Kabupaten vs Kota Bogor
    kab_bgr = df[df['matched_regency'] == 'Bogor'].iloc[0]
    kot_bgr = df[df['matched_regency'] == 'Kota Bogor'].iloc[0]
    print(f"7. Koordinat Bogor — Kab: ({kab_bgr['Latitude']:.4f}, {kab_bgr['Longitude']:.4f}) | "
          f"Kota: ({kot_bgr['Latitude']:.4f}, {kot_bgr['Longitude']:.4f})")
    assert (kab_bgr['Latitude'] != kot_bgr['Latitude']) or (kab_bgr['Longitude'] != kot_bgr['Longitude']), \
        "Koordinat Kabupaten Bogor dan Kota Bogor tidak boleh sama!"

    # 8. Cek distribusi cluster (2 cluster ekonomi)
    counts = df['cluster_id'].value_counts().sort_index()
    n_clusters = len([c for c in counts.index if c != -1])
    n_noise    = counts.get(-1, 0)
    print(f"8. Distribusi cluster: {dict(counts)}")
    print(f"   Jumlah cluster ekonomi: {n_clusters} | Noise: {n_noise}")
    assert n_clusters == 2, f"Harus ada tepat 2 cluster ekonomi, ditemukan: {n_clusters}"
    assert n_noise <= 20, f"Noise terlalu banyak ({n_noise}) — cek pipeline DBSCAN"

    print("\n>>> PIPELINE DATA TERVERIFIKASI 100% SUKSES DAN AKURAT! <<<")
    return True

if __name__ == "__main__":
    run_verification()
