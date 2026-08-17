import pandas as pd
import numpy as np
import os
import json

"""
TAHAP 4 (v2 - OPSI C): OPPORTUNITY INDEX (denominator = pengangguran terbuka)
Penulis: Antigravity AI

Perubahan metodologi dari v1 (Opsi C, disepakati):
- Numerator   : total lowongan terobservasi (Jobstreet + Glints, Jawa, onsite) per wilayah.
- Denominator : PENGANGGURAN TERBUKA ("Angkatan Kerja Pengangguran - Jumlah"),
                bukan total angkatan kerja. Alasan: mengukur ketersediaan peluang
                relatif terhadap orang yang BENAR-BENAR butuh kerja (unmet supply),
                bukan seluruh populasi angkatan kerja.
- TPT (Tingkat Pengangguran Terbuka) dihitung = pengangguran / angkatan kerja * 100
  sebagai metrik konteks (bukan penyebut).
"""


def get_qualification_score(title):
    title = str(title).lower()
    if any(k in title for k in ["manager", "kepala", "director", "lead", "senior", "head", "vp", "chief"]):
        return 3
    if any(k in title for k in ["specialist", "supervisor", "coordinator", "analyst", "spv", "expert"]):
        return 2
    return 1


def main():
    print("=== TAHAP 4: OPPORTUNITY INDEX (OPSI C) ===")

    data_dir = "data"
    input_file = os.path.join(data_dir, "integrated_job_market_java_v2.csv")
    geojson_file = os.path.join(data_dir, "java_regencies.geojson")
    coord_file = os.path.join(data_dir, "java_regency_coordinates.csv")
    bps_file = os.path.join(data_dir, "master_bps_socioeconomic.csv")

    for f_path in [input_file, geojson_file, coord_file, bps_file]:
        if not os.path.exists(f_path):
            print(f"Error: File '{f_path}' tidak ditemukan.")
            return

    df_jobs = pd.read_csv(input_file)

    # 1. Master wilayah dari GeoJSON (119)
    with open(geojson_file, "r") as f:
        g_data = json.load(f)
    master_names = sorted(list(set([f["properties"]["clean_name"] for f in g_data["features"]])))
    master_df = pd.DataFrame(master_names, columns=["matched_regency"])

    def std_name(name):
        if not isinstance(name, str):
            return ""
        name = name.strip()
        if name == "Administrasi Kepulauan Seribu":
            return "Kepulauan Seribu"
        if name == "Gunungkidul":
            return "Gunung Kidul"
        return name

    master_df["join_key"] = master_df["matched_regency"].apply(std_name)

    # 2. BPS: ambil pengangguran terbuka + angkatan kerja (untuk TPT)
    df_bps = pd.read_csv(bps_file)
    df_bps["join_key"] = df_bps["Kabupaten/Kota"].apply(std_name)
    df_bps_unique = df_bps.drop_duplicates(subset=["join_key"])

    hub_stats = pd.merge(
        master_df,
        df_bps_unique[["join_key", "Provinsi",
                       "Angkatan Kerja Pengangguran - Jumlah",
                       "Angkatan Kerja - Jumlah Angkatan Kerja"]],
        on="join_key", how="left",
    )
    hub_stats.rename(columns={
        "Angkatan Kerja Pengangguran - Jumlah": "unemployment_num",
        "Angkatan Kerja - Jumlah Angkatan Kerja": "labor_force_num",
    }, inplace=True)

    # 3. Koordinat
    df_coords = pd.read_csv(coord_file)
    df_coords["join_key"] = df_coords["City_Name"].apply(std_name)
    df_coords_unique = df_coords.drop_duplicates(subset=["join_key"])
    hub_stats = pd.merge(hub_stats, df_coords_unique[["join_key", "Latitude", "Longitude"]], on="join_key", how="left")
    hub_stats.drop(columns=["join_key"], inplace=True)

    # 4. Agregasi volume lowongan per wilayah
    df_jobs["qual_score"] = df_jobs["title"].apply(get_qualification_score)
    job_stats = df_jobs.groupby("matched_regency").agg(
        id=("id", "count"),
        qual_score=("qual_score", "mean"),
    ).rename(columns={"id": "job_volume", "qual_score": "competitive_index"})

    def rev_std_name(name):
        if name == "Kepulauan Seribu":
            return "Administrasi Kepulauan Seribu"
        if name == "Gunung Kidul":
            return "Gunungkidul"
        return name

    job_stats.index = job_stats.index.map(rev_std_name)
    job_stats.index.name = "matched_regency"

    hub_stats = pd.merge(hub_stats, job_stats, on="matched_regency", how="left")
    hub_stats["job_volume"] = hub_stats["job_volume"].fillna(0).astype(int)
    hub_stats["competitive_index"] = hub_stats["competitive_index"].fillna(1.0)

    # 5. OPPORTUNITY INDEX (OPSI C): lowongan / pengangguran terbuka
    hub_stats["unemployment_num"] = pd.to_numeric(hub_stats["unemployment_num"], errors="coerce")
    hub_stats["labor_force_num"] = pd.to_numeric(hub_stats["labor_force_num"], errors="coerce")
    hub_stats["opportunity_index"] = hub_stats["job_volume"] / hub_stats["unemployment_num"].replace(0, np.nan)
    hub_stats["opportunity_index"] = hub_stats["opportunity_index"].replace([np.inf, -np.inf], np.nan).fillna(0.0)

    # 6. TPT = pengangguran / angkatan kerja * 100 (metrik konteks)
    hub_stats["tpt"] = (hub_stats["unemployment_num"] / hub_stats["labor_force_num"].replace(0, np.nan)) * 100
    hub_stats["tpt"] = hub_stats["tpt"].replace([np.inf, -np.inf], np.nan).round(2)

    # 7. Klasifikasi kesejahteraan (median wilayah ber-lowongan)
    mask_has_jobs = hub_stats["job_volume"] > 0
    med_opp = hub_stats[mask_has_jobs]["opportunity_index"].median() if mask_has_jobs.any() else 0.0
    hub_stats["prosperity_status"] = np.where(
        (hub_stats["opportunity_index"] >= med_opp) & (hub_stats["job_volume"] > 5),
        "Lautan Peluang", "Zona Merah",
    )

    hub_stats["Latitude"] = hub_stats["Latitude"].fillna(0.0)
    hub_stats["Longitude"] = hub_stats["Longitude"].fillna(0.0)
    hub_stats["Provinsi"] = hub_stats["Provinsi"].fillna("Jawa")

    output_path = os.path.join(data_dir, "java_job_market_final_analysis.csv")
    hub_stats.to_csv(output_path, index=False)

    print("\n--- RINGKASAN OPPORTUNITY INDEX (OPSI C) ---")
    print(f"Total wilayah: {len(hub_stats)}")
    print(f"Wilayah ber-lowongan: {int((hub_stats['job_volume'] > 0).sum())}")
    print(f"Median opportunity_index (ber-lowongan): {med_opp:.6f}")
    print(f"Rentang TPT: {hub_stats['tpt'].min():.2f}% - {hub_stats['tpt'].max():.2f}%")
    print(f"Disimpan: {output_path}")


if __name__ == "__main__":
    main()
