import pandas as pd
from rapidfuzz import process, utils
import numpy as np
import os

"""
TAHAP 3 (v2 - OPSI C): INTEGRASI DATA MULTI-PLATFORM
Penulis: Antigravity AI (Falah's Thesis Assistant)

Perubahan dari v1:
1. Input lowongan diperluas: Jobstreet (nasional) + Glints (Jawa, onsite).
2. Jobstreet  -> fuzzy match string `location` ke 119 kab/kota Jawa.
   Glints      -> nearest-centroid dari lat/lon (Glints tak selalu beri nama kota).
3. Tambah kolom `source` (jobstreet/glints) + dedup lintas platform
   pada (company, title, matched_regency) untuk menghindari double-count.
4. Remote/hybrid TIDAK dimasukkan (Glints sudah di-exclude di cleaning;
   Jobstreet nasional difilter lewat match ke kab/kota Jawa + threshold).
"""

# ---------------------------------------------------------------------------
# Rescue cache: nama kecamatan/kawasan -> kab/kota induk (dipertahankan dari v1)
# ---------------------------------------------------------------------------
CACHE = {
    "Bandung, Jawa Barat": ("Kota Bandung", 100), "Bandung": ("Kota Bandung", 100),
    "Kabupaten Bandung, Jawa Barat": ("Bandung", 100),
    "Bogor, Jawa Barat": ("Kota Bogor", 100), "Bogor": ("Kota Bogor", 100),
    "Kabupaten Bogor, Jawa Barat": ("Bogor", 100),
    "Bekasi, Jawa Barat": ("Kota Bekasi", 100), "Bekasi": ("Kota Bekasi", 100),
    "Kabupaten Bekasi, Jawa Barat": ("Bekasi", 100),
    "Tangerang, Banten": ("Kota Tangerang", 100), "Tangerang": ("Kota Tangerang", 100),
    "Semarang, Jawa Tengah": ("Kota Semarang", 100), "Semarang": ("Kota Semarang", 100),
    "Surabaya, Jawa Timur": ("Kota Surabaya", 100), "Surabaya": ("Kota Surabaya", 100),
    "Malang, Jawa Timur": ("Kota Malang", 100), "Malang": ("Kota Malang", 100),
    "Yogyakarta, DI Yogyakarta": ("Kota Yogyakarta", 100), "Yogyakarta": ("Kota Yogyakarta", 100),
    "Cirebon, Jawa Barat": ("Kota Cirebon", 100), "Cirebon": ("Kota Cirebon", 100),
    "Sukabumi, Jawa Barat": ("Kota Sukabumi", 100), "Sukabumi": ("Kota Sukabumi", 100),
    "Tegal, Jawa Tengah": ("Kota Tegal", 100), "Tegal": ("Kota Tegal", 100),
    "Magelang, Jawa Tengah": ("Kota Magelang", 100), "Magelang": ("Kota Magelang", 100),
    "Tasikmalaya, Jawa Barat": ("Kota Tasikmalaya", 100), "Tasikmalaya": ("Kota Tasikmalaya", 100),
    "Madiun, Jawa Timur": ("Kota Madiun", 100), "Madiun": ("Kota Madiun", 100),
    "Pasuruan, Jawa Timur": ("Kota Pasuruan", 100), "Pasuruan": ("Kota Pasuruan", 100),
    "Mojokerto, Jawa Timur": ("Kota Mojokerto", 100), "Mojokerto": ("Kota Mojokerto", 100),
    "Kediri, Jawa Timur": ("Kota Kediri", 100), "Kediri": ("Kota Kediri", 100),
    "Cikarang Pusat, Jawa Barat": ("Kota Bekasi", 100), "Cikarang, Jawa Barat": ("Kota Bekasi", 100),
    "Cikarang": ("Kota Bekasi", 100),
    "Kebayoran Lama, Jakarta Raya": ("Kota Jakarta Selatan", 100),
    "Kebayoran Baru, Jakarta Raya": ("Kota Jakarta Selatan", 100),
    "Kemayoran, Jakarta Raya": ("Kota Jakarta Pusat", 100),
    "Cikupa, Banten": ("Kota Tangerang", 100), "Ciawi, Jawa Barat": ("Kota Bogor", 100),
    "Serpong, Banten": ("Kota Tangerang Selatan", 100), "Bsd City, Banten": ("Kota Tangerang Selatan", 100),
    "Cileungsi, Jawa Barat": ("Kota Bogor", 100), "Kalideres, Jakarta Raya": ("Kota Jakarta Barat", 100),
    "Kelapa Gading, Jakarta Raya": ("Kota Jakarta Utara", 100),
    "Gunung Putri, Jawa Barat": ("Kota Bogor", 100), "Purwokerto": ("Banyumas", 100),
    "Padalarang, Jawa Barat": ("Bandung Barat", 100), "Pulo Gadung, Jakarta Raya": ("Kota Jakarta Timur", 100),
    "Waru, Jawa Timur": ("Sidoarjo", 100), "Cengkareng, Jakarta Raya": ("Kota Jakarta Barat", 100),
    "Balaraja, Banten": ("Tangerang", 100), "Penjaringan, Jakarta Raya": ("Kota Jakarta Utara", 100),
    "Tambun, Jawa Barat": ("Bekasi", 100), "Matraman, Jakarta Raya": ("Kota Jakarta Timur", 100),
    "Sunter, Jakarta Raya": ("Kota Jakarta Utara", 100), "Cikande, Banten": ("Serang", 100),
    "Pesanggrahan, Jakarta Raya": ("Kota Jakarta Selatan", 100),
    "Gunung Sindur, Jawa Barat": ("Bogor", 100), "Driyorejo, Jawa Timur": ("Gresik", 100),
    "Jetis, DI Yogyakarta": ("Kota Yogyakarta", 100), "Batujajar, Jawa Barat": ("Bandung Barat", 100),
    "Gedangan, Jawa Timur": ("Sidoarjo", 100), "Kebon Jeruk, Jakarta Raya": ("Kota Jakarta Barat", 100),
    "Setiabudi, Jakarta Raya": ("Kota Jakarta Selatan", 100),
    # Normalisasi nama kota berbahasa Inggris (Kalibrr) -> nama BPS
    "Central Jakarta": ("Kota Jakarta Pusat", 100),
    "South Jakarta": ("Kota Jakarta Selatan", 100),
    "West Jakarta": ("Kota Jakarta Barat", 100),
    "East Jakarta": ("Kota Jakarta Timur", 100),
    "North Jakarta": ("Kota Jakarta Utara", 100),
    "South Tangerang": ("Kota Tangerang Selatan", 100),
    "Depok": ("Kota Depok", 100),
}


# Kata kunci provinsi NON-Jawa untuk membuang lokasi luar Pulau Jawa
# (mencegah false-positive fuzzy, mis. 'Medan' -> 'Sumedang' karena substring).
NON_JAVA_PROVINCES = [
    "aceh", "sumatera", "sumatra", "riau", "jambi", "bengkulu", "lampung",
    "bangka", "belitung", "bali", "nusa tenggara", "kalimantan", "sulawesi",
    "gorontalo", "maluku", "papua",
]


def is_non_java(loc):
    if not isinstance(loc, str):
        return False
    s = loc.lower()
    return any(k in s for k in NON_JAVA_PROVINCES)


def build_fuzzy_mapper(lookup_list):
    """Kembalikan fungsi yang memetakan string lokasi -> (regency, score)."""
    def mapper(loc):
        if not isinstance(loc, str) or not loc.strip():
            return None, 0
        loc = loc.strip()
        if loc in CACHE:
            return CACHE[loc]
        primary = loc.split(",")[0].strip()
        if primary in CACHE:
            return CACHE[primary]
        match = process.extractOne(primary, lookup_list, processor=utils.default_process)
        if match:
            CACHE[loc] = (match[0], match[1])
            return match[0], match[1]
        return None, 0
    return mapper


def build_centroid_mapper(df_coords):
    """Kembalikan fungsi (lat, lon) -> nama kab/kota terdekat (centroid)."""
    names = df_coords["City_Name"].tolist()
    lats = df_coords["Latitude"].to_numpy(dtype=float)
    lons = df_coords["Longitude"].to_numpy(dtype=float)

    def mapper(lat, lon):
        if lat is None or lon is None or (isinstance(lat, float) and np.isnan(lat)) or (isinstance(lon, float) and np.isnan(lon)):
            return None
        d = (lats - lat) ** 2 + (lons - lon) ** 2
        return names[int(np.argmin(d))]
    return mapper


def main():
    print("Memulai Integrasi Data Spasial & Sosio-Ekonomi (multi-platform)...")

    # 1. Muat dataset
    df_js = pd.read_csv("data/jobstreet_results_v2.csv")
    df_gl = pd.read_csv("data/glints_jobs_v2.csv")
    df_coords = pd.read_csv("data/java_regency_coordinates.csv")
    df_bps = pd.read_csv("data/master_bps_socioeconomic.csv")

    lookup_list = df_coords["City_Name"].tolist()
    fuzzy = build_fuzzy_mapper(lookup_list)
    centroid = build_centroid_mapper(df_coords)

    # 2. Jobstreet: buang lokasi non-Jawa dulu (negative filter), lalu fuzzy match
    n_non_java = int(df_js["location"].map(is_non_java).sum())
    df_js = df_js[~df_js["location"].map(is_non_java)].copy()
    print(f"Jobstreet: {n_non_java} lowongan non-Jawa dibuang; memetakan {len(df_js)} (fuzzy)...")
    df_js[["matched_regency", "match_score"]] = df_js["location"].apply(
        lambda x: pd.Series(fuzzy(x))
    )
    df_js["source"] = "jobstreet"
    df_js = df_js[df_js["match_score"] >= 80].copy()

    # 3. Glints: nearest-centroid (lat/lon) ke kab/kota Jawa
    print(f"Glints: memetakan {len(df_gl)} lowongan (lat/lon -> centroid)...")
    df_gl = df_gl[(df_gl["is_in_java"] == True) & (df_gl["is_remote"] == False)].copy()
    df_gl["matched_regency"] = [centroid(a, b) for a, b in zip(df_gl["lat"], df_gl["lon"])]
    df_gl["match_score"] = 100
    df_gl["source"] = "glints"
    df_gl = df_gl[df_gl["matched_regency"].notna()].copy()

    # 3b. Kalibrr: buang remote/hybrid, negative filter non-Jawa, fuzzy match lokasi
    df_kb = pd.read_csv("data/kalibrr_jobs_v2.csv")
    df_kb = df_kb[(df_kb["is_work_from_home"] == False) & (df_kb["is_hybrid"] == False)].copy()
    n_kb_non = int(df_kb["location"].map(is_non_java).sum())
    df_kb = df_kb[~df_kb["location"].map(is_non_java)].copy()
    print(f"Kalibrr: {n_kb_non} non-Jawa dibuang; memetakan {len(df_kb)} (fuzzy)...")
    df_kb[["matched_regency", "match_score"]] = df_kb["location"].apply(
        lambda x: pd.Series(fuzzy(x))
    )
    df_kb["source"] = "kalibrr"
    df_kb = df_kb[df_kb["match_score"] >= 80].copy()

    # 4. Samakan kolom & gabung
    js_cols = ["id", "title", "company", "location", "matched_regency", "match_score", "source"]
    gl_cols = ["id", "title", "company", "city", "matched_regency", "match_score", "source"]
    kb_cols = ["id", "title", "company", "location", "matched_regency", "match_score", "source"]
    df_js = df_js[js_cols]
    df_gl = df_gl[gl_cols].rename(columns={"city": "location"})
    df_kb = df_kb[kb_cols]
    df_all = pd.concat([df_js, df_gl, df_kb], ignore_index=True)

    # 5. Dedup lintas platform: (company, title, matched_regency) dinormalisasi
    def norm(s):
        return str(s).lower().strip() if isinstance(s, str) else ""
    df_all["_key"] = df_all["company"].map(norm) + "|" + df_all["title"].map(norm) + "|" + df_all["matched_regency"].map(norm)
    before = len(df_all)
    df_all = df_all.drop_duplicates(subset=["_key"], keep="first")
    print(f"Dedup lintas platform: {before} -> {len(df_all)}")

    # 6. Gabung koordinat (dari master)
    final_df = pd.merge(df_all, df_coords, left_on="matched_regency", right_on="City_Name", how="left")

    # 7. Gabung BPS (presisi, tanpa menghapus awalan Kota/Kabupaten)
    final_df = pd.merge(final_df, df_bps, left_on="matched_regency", right_on="Kabupaten/Kota", how="left")

    # 8. Seleksi kolom akhir (pertahankan kolom pengangguran + angkatan kerja untuk Opsi C)
    cols_to_keep = [
        "id", "title", "company", "location", "matched_regency", "match_score", "source",
        "Latitude", "Longitude", "Provinsi",
        "Angkatan Kerja - Bekerja", "Angkatan Kerja Pengangguran - Jumlah",
        "Angkatan Kerja - Jumlah Angkatan Kerja",
        "Angkatan Kerja + Bukan Angkatan Kerja (Jumlah )",
    ]
    final_df = final_df[cols_to_keep].drop_duplicates(subset=["id"])

    output_file = "data/integrated_job_market_java_v2.csv"
    final_df.to_csv(output_file, index=False)

    print("\n--- RINGKASAN INTEGRASI (OPSI C) ---")
    print(f"Jobstreet input (nasional): {len(df_js)}")
    print(f"Glints input (Jawa onsite): {len(df_gl)}")
    print(f"Kalibrr input (Jawa onsite): {len(df_kb)}")
    print(f"Total terintegrasi (Jawa): {len(final_df)}")
    print(f"Per platform:\n{final_df['source'].value_counts().to_string()}")
    print(f"Dataset disimpan: {output_file}")


if __name__ == "__main__":
    main()
