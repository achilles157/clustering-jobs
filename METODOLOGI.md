# 📖 Metodologi Penelitian: Klastering Spasial Pasar Kerja Jawa

Dokumen ini menjelaskan alur kerja data (data pipeline) untuk proyek skripsi mengenai analisis sebaran lowongan kerja dan indeks kompetisi di Pulau Jawa menggunakan data Jobstreet dan BPS.

## 🛠️ Alur Kerja (Pipeline)
Proyek ini terdiri dari 6 tahap pengolahan data dan 1 tahap visualisasi (dashboard) yang dieksekusi sebagai berikut:

### **Tahap 1: Akuisisi Data (`1_acquisition_jobstreet.py`)**
- **Tujuan**: Mengambil data lowongan kerja secara otonom dari Jobstreet ID.
- **Metode**: GraphQL Reverse Engineering (Query `JobSearchV6`).
- **Fitur Kunci**: Menggunakan `curl_cffi` untuk bypass Cloudflare WAF dan mensimulasikan sesi browser asli.
- **Output**: `jobstreet_results.csv`.

### **Tahap 2: Pengolahan Data Sekunder & Geocoding**
- **2.1 Konsolidasi BPS (`2_bps_consolidation.py`)**: Menggabungkan dataset kependudukan usia kerja dari 6 provinsi di Jawa menjadi satu file master.
- **2.2 Geocoding Wilayah (`3_geocoding_regencies.py`)**: Mengubah daftar nama Kabupaten/Kota menjadi koordinat Latitude/Longitude pusat wilayah (centroid).
- **Output**: `master_bps_socioeconomic.csv`, `java_regency_coordinates.csv`.

### **Tahap 3: Integrasi Data Spasial (`4_data_integration.py`)**
- **Tujuan**: Menyatukan data lowongan kerja dengan koordinat geospasial dan data BPS.
- **Logika**: Menggunakan **Fuzzy String Matching** (Levenshtein Distance) untuk memetakan nama lokasi di Jobstreet ke standar wilayah BPS.
- **Output**: `integrated_job_market_java_v2.csv`.

### **Tahap 4: NLP & Opportunity Indexing (`5_nlp_opportunity_index.py`)**
- **Teknik NLP**: Menggunakan TF-IDF (Term Frequency-Inverse Document Frequency) dengan rentang Bigram (1,2) untuk mengekstrak kata kunci industri dominan di tiap daerah.
- **Perhitungan Indeks**: 
  $$Opportunity Index = \frac{\text{Jumlah Lowongan}}{\text{Angkatan Kerja}}$$
- **Output**: `java_job_market_final_analysis.csv`.

### **Tahap 5: Klastering Spasial (DBSCAN) (`6_spatial_clustering_dbscan.py`)**
- **Tujuan**: Mengidentifikasi Hub Ekonomi (Economic Clusters) secara otonom.
- **Parameter**: Menggunakan **Radius 50 KM** (`eps=0.45`) untuk mengelompokkan aglomerasi kota (contoh: Jabodetabek).

### **Tahap 6: Visualisasi Interaktif (Dashboard) (`dashboard.py`)**
- **Tujuan**: Menyajikan hasil klastering, indeks kompetisi, dan analisis skill (TF-IDF) ke dalam antarmuka web interaktif untuk keperluan demonstrasi sidang skripsi.
- **Teknologi**: Streamlit, Plotly (untuk peta interaktif dan grafik), WordCloud.
- **Modul Utama**: 
  - **Peta Spasial (DBSCAN)**: Visualisasi klaster wilayah berdasarkan densitas lowongan.
  - **Opportunity Heatmap**: Peta sebaran warna (choropleth) berdasarkan Indeks Peluang.
  - **Skill Context (TF-IDF)**: Word cloud keterampilan dominan per daerah yang dipilih.

---

## 📂 Struktur Dataset
| Nama Kolom | Deskripsi | Sumber |
| :--- | :--- | :--- |
| `job_volume` | Total lowongan kerja unik yang tersedia. | Jobstreet |
| `labor_force_num` | Jumlah angkatan kerja (aktif). | BPS 2025 |
| `opportunity_index` | Rasio peluang kerja terhadap pencari kerja. | Hasil Hitung |
| `top_skills` | Kata kunci skill/industri paling dominan (Hasil TF-IDF). | NLP Pipeline |

## 🚀 Cara Menjalankan
Pastikan library yang dibutuhkan sudah terinstal:
```bash
pip install -r requirements.txt
```

Alur Eksekusi:
1. Jalankan script pengolahan data (`src/`) sesuai urutan dari nomor 1 sampai 6.
2. (Opsional) Jalankan utility `src/prepare_dashboard_data.py` jika struktur geojson memerlukan format ulang.
3. Luncurkan Dashboard:
```bash
streamlit run dashboard.py
```
