# 📋 Detailed Project Plan: Job Market Spatial Clustering (Pulau Jawa)

## 1. Project Overview
Membangun sistem pemetaan spasial lowongan kerja di Pulau Jawa untuk mengidentifikasi konsentrasi peluang ekonomi dan tingkat kompetisi wilayah. Proyek ini menggabungkan teknik **Web Reverse Engineering**, **Spatial Data Science**, dan **Unsupervised Machine Learning**.

---

## 2. Methodology & Phases

### Phase 1: Advanced Data Acquisition [COMPLETE]
*   **Target**: Akuisisi data lowongan masif wilayah Indonesia.
*   **Technique**: Reverse engineering API pencarian Jobstreet (`JobSearchV6` endpoint) menggunakan `curl_cffi` untuk intersep data terstruktur dalam format JSON.
*   *(Catatan: Fase awal mencoba platform Glints terhalang oleh block proxy kuat dan densitas data yang rendah, lihat `GLINTS_HISTORY.md`)*.

### Phase 2: Data Preprocessing & Cleaning [COMPLETE]
*   **Normalization**: Pembersihan teks pada kolom `title` dan `skills`.
*   **Spatial Validation**: Memastikan koordinat berada di daratan Pulau Jawa.
*   **Fuzzy Name Matching**: Integrasi nama kota antar sumber menggunakan algoritma String Similarity (`rapidfuzz`).

### Phase 3: Feature Engineering & Socio-Economic Integration [COMPLETE]
*   **BPS Data Integration**: Memasukkan data Angkatan Kerja (Labor Force) dan Kepadatan Penduduk per Kabupaten/Kota di Jawa dari 6 provinsi terpisah (BPS 2025).
*   **Competition Index Modeling**:
    *   **Formula**: $Index = \frac{Total Lowongan}{Angkatan Kerja}$ (Mencerminkan rasio peluang per pencari kerja).
*   **NLP Extraction**: Menggunakan TF-IDF Vectorization untuk mengekstrak kelompok `skills` berbasis bi-gram secara kewilayahan.

### Phase 4: Spatial Clustering (Machine Learning) [COMPLETE]
*   **Algorithm**: **DBSCAN** (Density-Based Spatial Clustering of Applications with Noise).
*   **Parameters Tuning**:
    *   `eps`: 0.45 (radius logis ~50km lintas batas kota).
    *   `min_samples`: Ambang batas densitas ekonomi per cluster.
*   **Output**: Segmentasi aglomerasi ekonomi nyata.

### Phase 5: Interactive Visualization Dashboard [COMPLETE]
*   **Platform**: Streamlit (Python Web App).
*   **Fitur**:
    *   **Choropleth Maps**: Pemetaan interaktif tingkat densitas ekonomi per kabupaten menggunakan GeoJSON.
    *   **Scatter Density Plot**: Evaluasi linear korelasi pencari kerja versus lapangan yang tersedia.
    *   **Dynamic WordCloud**: Respon visual instan untuk `skills` bedasarkan sentuhan (on-click) di peta atas suatu kota wilayah Jawa.

---

## 3. Technical Stack
*   **Language**: Python 3.x
*   **Libraries**:
    *   Scraping: `curl_cffi`, `requests`, `json`
    *   Processing: `pandas`, `numpy`
    *   ML & Spatial: `scikit-learn` (DBSCAN), `scipy`
    *   Analysis: `TfidfVectorizer` (Text analysis)
*   **Data Source**: Glints API, BPS Open Data.

---

## 4. Risks & Mitigations
| Risk | Mitigation |
| :--- | :--- |
| **IP Blacklisted** | Implementasi random delay dan penggunaan `curl_cffi` fingerprinting. |
| **Coordinate Drift** | Validasi Lat/Lon menggunakan boundary box Pulau Jawa. |
| **Inconsistent City Names** | Mapping table dan Fuzzy Matching untuk join data BPS. |

---

## 5. Timeline & Final State
*   Sistem akuisisi Jobstreet terbukti mampu mengangkut 20,000+ records.
*   Akurasi penggabungan text nama wilayah via RapidFuzz menyentuh 88%.
*   DBSCAN berhasil mendeteksi "pusat gravitasi" ekonomi seperti gerbang Jabodetabek dan koridor Surabaya-Malang secara numerik geospasial murni.
*   **Final Output**: Streamlit WebApp `dashboard.py` siap mendemonstrasikan keabsahan dan visual hasil di ruang sidang skripsi.
