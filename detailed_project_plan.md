📋 Detailed Project Plan: Job Market Spatial Clustering (Pulau Jawa)

1. Project Overview

Membangun sistem pemetaan spasial lowongan kerja di Pulau Jawa untuk mengidentifikasi konsentrasi peluang ekonomi dan tingkat kompetisi wilayah. Proyek ini menggabungkan teknik Web Reverse Engineering, Spatial Data Science, dan Unsupervised Machine Learning.

2. Methodology & Phases

Phase 1: Advanced Data Acquisition [COMPLETE]

Target: Akuisisi data lowongan masif wilayah Indonesia.

Technique: Reverse engineering API pencarian Jobstreet (JobSearchV6 endpoint) menggunakan curl_cffi untuk intersep data terstruktur dalam format JSON.

(Catatan: Fase awal mencoba platform Glints terhalang oleh block proxy kuat dan densitas data yang rendah, lihat GLINTS_HISTORY.md).

Phase 2: Data Preprocessing & Cleaning [COMPLETE]

Normalization: Pembersihan dan standardisasi teks pada atribut wilayah/kota.

Spatial Validation: Memastikan titik koordinat (Latitude/Longitude) berada secara valid di daratan Pulau Jawa.

Fuzzy Name Matching: Integrasi nama kota antar sumber data menggunakan algoritma String Similarity (rapidfuzz).

Phase 3: Feature Engineering & Socio-Economic Integration [COMPLETE]

BPS Data Integration: Memasukkan data Angkatan Kerja (Labor Force) dan Kepadatan Penduduk per Kabupaten/Kota di Jawa dari 6 provinsi terpisah (BPS 2025).

Opportunity Index Modeling:

Formula: $Index = \frac{Total Lowongan}{Angkatan Kerja}$

Tujuan: Mencerminkan rasio peluang per pencari kerja di suatu wilayah, yang nantinya akan dinormalisasi (Min-Max) sebagai bobot spasial.

Phase 4: Spatial Clustering (Machine Learning) [COMPLETE]

Algorithm: DBSCAN (Density-Based Spatial Clustering of Applications with Noise).

Parameters Tuning:

eps: 0.45 (radius logis ~50km lintas batas administratif kota/kabupaten).

min_samples: Ambang batas (threshold) densitas ekonomi per cluster.

Output: Segmentasi aglomerasi ekonomi nyata (Core, Border, Noise) yang tidak dibatasi oleh garis batas provinsi tradisional.

Phase 5: Interactive Visualization Dashboard [COMPLETE]

Platform: Streamlit (Python Web App / Web GIS).

Fitur:

Choropleth Maps: Pemetaan interaktif tingkat densitas ekonomi per kabupaten menggunakan GeoJSON Pulau Jawa.

Scatter Density Plot: Evaluasi linear korelasi pencari kerja versus lapangan yang tersedia.

Spatial Point Details: Panel informasi dinamis (pop-up) yang muncul saat peta suatu wilayah ditekan (on-click), menampilkan metrik numerik murni: Nama Kota, Total Lowongan, Angkatan Kerja BPS, dan Skor Indeks Peluang.

3. Technical Stack

Language: Python 3.x

Libraries:

Scraping: curl_cffi, requests, json

Processing & Matrix: pandas, numpy, rapidfuzz

ML & Spatial: scikit-learn (DBSCAN), scipy

Web GIS UI: streamlit, folium (atau library peta setara)

Data Source: Jobstreet API, BPS Open Data.

4. Risks & Mitigations

Risk

Mitigation

IP Blacklisted

Implementasi random delay dan penggunaan curl_cffi fingerprinting untuk bypass pengamanan API.

Coordinate Drift

Validasi dan clipping Lat/Lon secara ketat menggunakan boundary box (batas geografis) Pulau Jawa.

Inconsistent City Names

Mapping table manual dan algoritma Fuzzy Matching untuk proses join data BPS dengan akurasi tinggi.

5. Timeline & Final State

Sistem akuisisi Jobstreet terbukti mampu mengangkut 20,000+ records.

Akurasi penggabungan teks nama wilayah via RapidFuzz menyentuh 88%.

Algoritma DBSCAN berhasil mendeteksi "pusat gravitasi" ekonomi seperti gerbang Jabodetabek dan koridor Surabaya-Malang secara numerik geospasial murni, memisahkan wilayah noise (pelosok) secara organik.

Final Output: Streamlit WebApp dashboard.py siap mendemonstrasikan keabsahan rasio spasial dan visualisasi hasil klasterisasi secara interaktif di ruang sidang skripsi.