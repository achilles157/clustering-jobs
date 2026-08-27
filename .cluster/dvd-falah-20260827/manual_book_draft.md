# MANUAL BOOK

## Aplikasi Dashboard Persebaran Peluang Kerja di Pulau Jawa (DBSCAN)

---

**Identitas Aplikasi**

| Item | Keterangan |
|---|---|
| Nama Aplikasi | Dashboard Persebaran Peluang Kerja di Pulau Jawa |
| Jenis Aplikasi | Dashboard interaktif berbasis web (Streamlit) |
| File Utama | `dashboard.py` |
| Penulis | Falah Fahrurozi (NPM 202243502165) |
| Program Studi | Teknik Informatika, Universitas Indraprasta PGRI |
| Versi | v2.0 — DBSCAN Pure Spatial (eps=0,08) — Opsi C (÷ Pengangguran) |

---

# Bab 1. Pendahuluan

## 1.1 Tujuan Aplikasi

Aplikasi ini dibangun sebagai luaran penelitian skripsi dengan judul **"Persebaran Peluang Karir Berdasarkan Jumlah Angkatan Kerja menggunakan Density Based Clustering (DBSCAN)"**. Dashboard ini memiliki dua tujuan utama:

1. **Mengidentifikasi hub ekonomi** — pusat-pusat aglomerasi pasar kerja yang terbentuk secara alami di Pulau Jawa berdasarkan kepadatan lowongan kerja.
2. **Memetakan peluang kerja** — memetakan sebaran peluang kerja di 119 kabupaten/kota melalui indeks peluang, sehingga pencari kerja dan pengambil kebijakan dapat membaca kondisi suatu wilayah secara cepat.

Seluruh hasil analisis dirangkum dalam satu dashboard interaktif berbasis Streamlit. Dashboard ini menampilkan peta spasial hasil klastering, peta panas peluang kerja, statistik efisiensi pasar kerja, serta laporan eksekutif otomatis per wilayah.

## 1.2 Lingkup Data

Data yang digunakan dalam aplikasi ini berasal dari dua kelompok sumber:

1. **Data lowongan kerja** — diambil dari tiga platform lowongan kerja melalui API publik:
   - Jobstreet (endpoint publik `JobSearchV6`).
   - Glints (`searchJobsV3`).
   - Kalibrr (`/kjs/job_board/search`).
   - Total 52.450 lowongan mentah berhasil dikumpulkan, terdiri atas 49.928 dari Jobstreet, 1.525 dari Glints, dan 997 dari Kalibrr.
   - Setelah proses integrasi, deduplikasi lintas platform, dan pemetaan wilayah, **36.058 lowongan terintegrasi** berhasil dipetakan ke **119 kabupaten/kota** di Pulau Jawa.

2. **Data sosial-ekonomi BPS** — enam dataset BPS 2025 (Banten, DKI Jakarta, Jawa Barat, Jawa Tengah, DIY Yogyakarta, Jawa Timur) berisi jumlah pengangguran terbuka per kabupaten/kota.

Cakupan analisis adalah Pulau Jawa secara keseluruhan (119 kabupaten/kota) dengan periode **snapshot April 2026**. Artinya, data mencerminkan kondisi pasar kerja pada satu titik waktu tertentu, bukan data waktu-nyata.

## 1.3 Parameter Model

Klastering spasial menggunakan algoritma **DBSCAN (Density-Based Spatial Clustering of Applications with Noise)** dengan konfigurasi berikut:

| Parameter | Nilai | Keterangan |
|---|---|---|
| `eps` | 0,08 | Jarak maksimum antar titik untuk dianggap bertetangga, pada koordinat terstandardisasi |
| `min_samples` | 3 | Jumlah minimum titik untuk membentuk klaster |
| Fitur | Latitude, Longitude | Koordinat centroid kabupaten/kota |
| Normalisasi | StandardScaler | Sebelum klastering |

Indeks peluang dihitung dengan formula (Opsi C):

```
Indeks Peluang = Volume Lowongan ÷ Pengangguran Terbuka
```

DBSCAN dipilih karena pola aglomerasi pasar kerja di Jawa memanjang horizontal mengikuti koridor Trans-Jawa dan tidak berbentuk bola (spherical), sehingga tidak cocok dengan asumsi K-Means. DBSCAN tidak memerlukan penetapan jumlah klaster di awal dan secara alami memisahkan wilayah-wilayah terpencil sebagai zona terisolasi.

---

# Bab 2. Kebutuhan Sistem

Sebelum instalasi, pastikan perangkat memenuhi kebutuhan berikut.

## 2.1 Kebutuhan Perangkat Keras dan Sistem Operasi

| Komponen | Kebutuhan Minimum |
|---|---|
| Sistem Operasi | Windows 10 atau Windows 11 (64-bit) |
| Prosesor | Dual-core 2,0 GHz atau lebih |
| RAM | 4 GB atau lebih |
| Penyimpanan | 1 GB ruang kosong |
| Browser | Google Chrome, Microsoft Edge, atau Mozilla Firefox terbaru |

## 2.2 Kebutuhan Perangkat Lunak

1. **Python 3.13** — aplikasi ini diuji pada Python 3.13. Pada mesin pengembang, interpreter berada di `C:\Users\Falah\AppData\Local\Programs\Python\Python313`. Disarankan menggunakan interpreter yang sama atau versi Python 3.12 ke atas.
2. **pip** — pengelola paket Python, biasanya sudah tersedia bersama instalasi Python.
3. **Paket dependensi** — seluruh paket tercantum dalam file `requirements.txt`, antara lain:
   - `streamlit` (≥ 1.46) — kerangka dashboard.
   - `plotly` (≥ 5.26) — peta dan grafik interaktif.
   - `pandas`, `numpy` — pengolahan data.
   - `scikit-learn` — klastering DBSCAN.
   - `statsmodels`, `scipy` — analisis statistik dan garis tren.
   - `rapidfuzz` — pencocokan nama lokasi (fuzzy matching).
   - `curl_cffi` — akuisisi data dari API platform lowongan.
   - `matplotlib`, `requests`, `fpdf2` — pendukung visualisasi dan pelaporan.

## 2.3 Kebutuhan Jaringan Internet

Koneksi internet **dibutuhkan saat aplikasi dimuat** karena beberapa aset dimuat dari layanan daring:

1. Logo sidebar (icons8).
2. Font Plus Jakarta Sans (Google Fonts).
3. Tile peta `carto-darkmatter` pada peta Plotly.

Jika ketiga aset tersebut tidak dapat dimuat, aplikasi tetap berjalan, tetapi tampilan visualnya mungkin tidak sempurna.

---

# Bab 3. Instalasi

Ikuti langkah-langkah berikut secara berurutan.

## 3.1 Menyalin Folder Proyek

1. Salin seluruh folder proyek (termasuk folder `data/`, `src/`, file `dashboard.py`, dan `requirements.txt`) ke komputer tujuan.
2. Pastikan struktur folder utuh. Jangan memisahkan file `dashboard.py` dari folder `data/`.
3. Contoh lokasi: `C:\Users\Falah\Documents\clustering-jobs\`.

## 3.2 Memasang Dependensi

1. Buka **Command Prompt** atau **PowerShell**.
2. Pindah ke folder proyek:
   ```
   cd C:\Users\Falah\Documents\clustering-jobs
   ```
3. Pasang seluruh dependensi:
   ```
   pip install -r requirements.txt
   ```
4. Tunggu hingga proses pemasangan selesai. Pastikan tidak ada pesan error.

## 3.3 Menjalankan Aplikasi

Jalankan perintah berikut dari folder proyek (perintah persis):

```
C:\Users\Falah\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run dashboard.py
```

Catatan penting:
- Gunakan interpreter Python 3.13 khusus tersebut karena Python default di mesin belum memiliki pustaka Plotly dan Streamlit.
- Perintah harus dijalankan dari folder proyek agar aplikasi dapat menemukan file data.
- Jika interpreter di mesin Anda berbeda, ganti bagian `C:\Users\Falah\AppData\Local\Programs\Python\Python313\python.exe` dengan path interpreter Anda.

## 3.4 Verifikasi Instalasi

1. Setelah perintah dijalankan, Streamlit akan menampilkan alamat lokal.
2. Browser akan terbuka secara otomatis, atau Anda dapat membuka manual ke alamat:
   ```
   http://localhost:8501
   ```
3. Jika halaman dashboard muncul dengan sidebar dan lima tab, instalasi berhasil.

---

# Bab 4. Cara Pakai Fitur

## 4.1 Sidebar dan Filter Wilayah

Sidebar berisi logo, judul aplikasi, dan filter wilayah.

1. Pilih **Provinsi** pada kotak pilihan (selectbox) pertama.
2. Pilih **Kabupaten/Kota** pada kotak pilihan kedua. Daftar kabupaten/kota otomatis menyesuaikan dengan provinsi yang dipilih (filter berjenjang/cascading).
3. Klik tombol **"Apply Filters"**.

Penting: perubahan seleksi **belum mengubah tampilan** sampai tombol "Apply Filters" diklik. Ini dirancang menggunakan session state agar data yang diproses stabil dan tidak berubah saat halaman di-refresh.

4. Setelah tombol diklik, blok **"Konteks Wilayah (Terpilih)"** memperbarui isinya: nama provinsi, status wilayah, dan klasifikasi DBSCAN-nya. Gunakan blok ini sebagai rujukan cepat saat berpindah kota.

## 4.2 Tab 1 — Filter & Parameter

Tab ini menampilkan ringkasan empat parameter untuk wilayah terpilih:

1. **Volume Lowongan** — jumlah posisi kerja yang tersedia.
2. **Pengangguran Terbuka** — jumlah penganggur terbuka dari data BPS.
3. **Indeks Peluang** — ditampilkan hingga 5 angka desimal.
4. **Indeks Kompetitif** — skala 0 hingga 3.

Di bawahnya terdapat **tabel data mentah lowongan** berisi judul pekerjaan, nama perusahaan, dan lokasi asli hasil pengambilan data. Tabel ini merupakan data riil dari tiga platform (Jobstreet, Glints, Kalibrr), bukan data simulasi. Jumlah baris yang tampil menunjukkan porsi lowongan wilayah tersebut dari total 36.058 lowongan terintegrasi.

## 4.3 Tab 2 — Klaster Ekonomi (Inti Aplikasi)

Tab ini menampilkan peta sebaran (scatter map) hasil klastering DBSCAN.

1. **Warna lingkaran** menunjukkan klaster.
2. **Ukuran lingkaran** menunjukkan volume lowongan.
3. **Penanda emas** menunjukkan lokasi wilayah yang sedang difilter, sehingga wilayah terpilih selalu mudah ditemukan.

Terdapat tiga warna yang perlu dipahami:

| Warna | Klaster | Komposisi |
|---|---|---|
| Biru | Cluster 0 — Java Mainland Hub | 93 wilayah, ±11.978 lowongan |
| Hijau toska | Cluster 1 — Jabodetabek & Koridor Barat | 22 wilayah, ±24.078 lowongan |
| Abu-abu | Isolated Red Zone (zona terisolasi) | 4 wilayah, ±2 lowongan |

Contoh anggota wilayah per klaster:
- **Cluster 0**: Surabaya, Bandung, Semarang, Yogyakarta, Sidoarjo, Sleman.
- **Cluster 1**: Jakarta Barat, Jakarta Selatan, Jakarta Utara, Jakarta Pusat, Tangerang, Bekasi.
- **Terisolasi**: Kepulauan Seribu, Kota Banjar, Kota Pekalongan, Sumenep.

Tiga kartu di bawah peta merangkum komposisi klaster. Catatan: terdapat kotak informasi (info-box) di dashboard yang menyebut "GKS" sebagai contoh Cluster 0. Singkatan tersebut tidak terdokumentasi; jika dimaknai, "GKS" merujuk pada kawasan Gerbangkertosusila (Gresik–Bangkalan–Mojokerto–Surabaya–Sidoarjo–Lamongan).

## 4.4 Tab 3 — Heatmap Peluang

Tab ini menampilkan peta panas (choropleth) indeks peluang.

1. Rumus indeks ditampilkan dalam format LaTeX: `Indeks_Peluang = Volume_Lowongan / Pengangguran_Terbuka`.
2. Peta mewarnai **116 dari 119 wilayah** dengan skala merah–kuning–hijau (RdYlGn).
3. **Hijau** berarti "Lautan Peluang" — jumlah lowongan tinggi relatif terhadap penganggur terbuka.
4. **Merah** berarti "Zona Merah" — persaingan padat, kesempatan kerja tipis.
5. Rentang warna sengaja dipotong pada **kuantil 90%** agar wilayah outlier tidak mendominasi pewarnaan.
6. Peta otomatis memusatkan pandangan ke kota yang sedang dipilih.
7. Jika file GeoJSON tidak ditemukan, aplikasi secara otomatis beralih ke peta kepadatan (density map) sebagai cadangan.

## 4.5 Tab 4 — Statistik Efisiensi

Tab ini berisi tiga komponen:

1. **Scatter plot** — pengangguran terbuka versus volume lowongan, dengan garis tren OLS berwarna biru. Wilayah di atas garis tren menciptakan lapangan kerja lebih banyak dari yang diprediksi beban penganggurnya (performa positif).
2. **Bar chart Top-15 Indeks Kompetitif** — skor di atas 2,5 didominasi posisi manajerial; skor sekitar 1,0–1,5 mengindikasikan pasar kerja kerah biru dan peranan operasional.
3. **Metrik evaluasi model** — Silhouette Score **0,4649** dan Davies-Bouldin Index **0,5294**. Kedua nilai ini dihitung pada pipeline dan sudah diverifikasi melalui reproduksi ulang.

## 4.6 Tab 5 — Laporan Eksekutif

Tab ini menyajikan ringkasan otomatis untuk wilayah terpilih:

1. **Narasi kesimpulan** tiga paragraf — identifikasi klaster, statistik pengangguran terbuka, volume lowongan, dan kesimpulan berdasarkan peringkat.
2. **Dua metrik penilaian** — Rekomendasi dan tingkat Persaingan.
3. **Raw Data Profil** — profil data mentah wilayah.
4. **Tabel peringkat** — "Top 5 Lautan Peluang" dan "Top 5 Zona Merah" untuk seluruh Pulau Jawa.

Logika pemeringkatan: peringkat 10 besar termasuk kategori "Sangat Layak"; 15 terbawah "Berisiko"; zona merah mengesampingkan peringkat lain; wilayah dengan 0 lowongan masuk kategori "Tidak Terperingkat". Narasi dihitung ulang secara dinamis setiap kali wilayah diganti.

---

# Bab 5. Interpretasi Hasil

## 5.1 Arti Warna pada Peta Klaster (Tab 2)

- **Biru (Cluster 0 — Java Mainland Hub)** — aglomerasi utama di koridor daratan Jawa. Mencakup pusat-pusat regional seperti Surabaya, Bandung, Semarang, dan Yogyakarta. Terdiri dari 93 wilayah dengan ±11.978 lowongan.
- **Hijau toska (Cluster 1 — Jabodetabek & Koridor Barat)** — aglomerasi metropolitan dengan densitas lowongan tertinggi. Mencakup Jabodetabek, Serang, Karawang, dan Cilegon. Hanya 22 wilayah, tetapi menampung ±24.078 lowongan. Ini bukti konsentrasi lapangan kerja yang timpang di koridor barat.
- **Abu-abu (Isolated Red Zone)** — wilayah terpencil dengan volume lowongan nyaris nol. Terdiri dari 4 wilayah: Kepulauan Seribu, Kota Banjar, Kota Pekalongan, dan Sumenep.

## 5.2 Lautan Peluang dan Zona Merah (Tab 3)

- **Lautan Peluang (hijau)** — jumlah lowongan tinggi relatif terhadap penganggur terbuka. Wilayah ini direkomendasikan bagi pencari kerja karena peluang tersedia lebih banyak daripada pencari kerja aktif.
- **Zona Merah (merah)** — persaingan padat dan kesempatan kerja tipis dibandingkan penganggur yang benar-benar membutuhkan pekerjaan. Indikasi kejenuhan pasar kerja.

Contoh nyata dari dua wilayah:

| Wilayah | Lowongan | Penganggur Terbuka | Indeks | Status |
|---|---|---|---|---|
| Kota Jakarta Barat | 7.498 | 74.910 | 0,10 (±10 lowongan per 100 penganggur) | Lautan Peluang, "Sangat Layak", "Longgar" |
| Kabupaten Sukabumi | 12 | 110.512 | ±0,0001 | Zona Merah, "Berisiko", "Sengit" |

## 5.3 Arti Metrik Evaluasi Model

- **Silhouette Score 0,4649** — berkisar −1 hingga +1. Nilai ini berarti objek lebih dekat ke klasternya sendiri dibandingkan klaster lain, dalam kategori moderat-baik. Nilai moderat wajar karena aglomerasi Jawa memanjang (elongated), bukan gugus bulat.
- **Davies-Bouldin Index 0,5294** — mendekati 0 berarti baik. Nilai di bawah 1,0 menunjukkan antar-klaster tidak saling tumpang tindih secara spasial.

## 5.4 Keterbatasan Data

1. Data lowongan berasal dari tiga platform (Jobstreet, Glints, Kalibrr) pada satu titik waktu (snapshot April 2026). Belum mencakup seluruh pasar kerja formal maupun lowongan non-digital.
2. Geocoding menggunakan centroid kabupaten/kota, bukan koordinat persis perusahaan.
3. Pengangguran terbuka BPS mencakup seluruh sektor, sementara lowongan hanya sektor formal tercatat.
4. Hasil DBSCAN sensitif terhadap parameter eps dan min_samples.
5. Angka metrik model bersifat tetap (hardcoded) pada versi aplikasi ini, tetapi sudah terverifikasi benar melalui reproduksi ulang dari data.

---

# Bab 6. FAQ (Pertanyaan yang Sering Diajukan)

**1. Mengapa peta kosong atau data tidak muncul?**
Pastikan aplikasi dijalankan dari folder proyek yang benar dan seluruh file di folder `data/` ikut terbawa. File `java_job_market_hubs_final.csv` dan `java_regencies.geojson` harus berada di lokasi yang sama dengan struktur proyek asli.

**2. Mengapa peta choropleth hilang?**
Jika file GeoJSON tidak ditemukan, aplikasi otomatis beralih ke peta kepadatan (density map) sebagai cadangan. Peta tetap tampil, tetapi bentuk visualisasinya berbeda.

**3. Apakah angka metrik model berubah secara langsung saat filter diganti?**
Tidak. Nilai Silhouette (0,4649) dan DBI (0,5294) bersifat tetap karena dihitung pada pipeline dan sudah diverifikasi melalui reproduksi ulang. Yang berubah dinamis adalah narasi, tabel, dan metrik wilayah per filter.

**4. Apakah aplikasi butuh koneksi internet?**
Ya, saat aplikasi pertama dimuat. Logo sidebar (icons8), font Plus Jakarta Sans (Google Fonts), dan tile peta `carto-darkmatter` dimuat dari layanan daring. Setelah halaman termuat, interaksi pada data lokal tidak membutuhkan internet.

**5. Mengapa port 8501 tidak bisa diakses?**
Port 8501 mungkin sudah dipakai aplikasi lain. Jalankan ulang dengan port lain:
```
C:\Users\Falah\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run dashboard.py --server.port 8502
```

**6. Mengapa versi Streamlit Cloud berbeda dengan versi lokal?**
Versi publik di Streamlit Cloud (`persebaran-lowongan-kerja.streamlit.app`) masih versi lama tanpa dark theme. Untuk demonstrasi, gunakan versi lokal sampai versi cloud diperbarui (redeploy).

**7. Dari mana data lowongan diperoleh? Apakah legal?**
Data diambil dari API publik tiga platform (Jobstreet, Glints, Kalibrr). Hanya data publik lowongan (judul, perusahaan, lokasi) yang diambil, bukan data pribadi pengguna.

**8. Bagaimana cara membaca indeks peluang?**
Indeks peluang = volume lowongan dibagi pengangguran terbuka. Contoh: Kota Jakarta Barat 7.498 lowongan dibagi 74.910 penganggur = 0,10, artinya tersedia sekitar 10 lowongan per 100 penganggur terbuka. Nilai ini dimaknai sebagai perbandingan relatif antar-wilayah.

---

# Bab 7. Troubleshooting

## 7.1 Perintah "streamlit is not recognized"

**Penyebab:** interpreter Python yang aktif tidak memiliki Streamlit, atau tidak terdaftar di PATH.

**Solusi:**
1. Gunakan interpreter Python 3.13 penuh dengan perintah persis:
   ```
   C:\Users\Falah\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run dashboard.py
   ```
2. Pastikan dependensi sudah terpasang pada interpreter tersebut.

## 7.2 ModuleNotFoundError: plotly / streamlit

**Penyebab:** paket belum terpasang pada interpreter yang digunakan.

**Solusi:**
1. Pasang seluruh dependensi:
   ```
   pip install -r requirements.txt
   ```
2. Ulangi perintah menjalankan aplikasi.
3. Jika masih gagal, periksa bahwa `pip` yang digunakan milik interpreter Python 3.13, bukan Python lain.

## 7.3 Port 8501 Sudah Dipakai

**Penyebab:** ada proses Streamlit lain yang berjalan, atau port digunakan aplikasi lain.

**Solusi:**
1. Tutup proses Streamlit yang berjalan.
2. Atau jalankan dengan port berbeda:
   ```
   C:\Users\Falah\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run dashboard.py --server.port 8502
   ```

## 7.4 Versi Cloud Lebih Lama dari Versi Lokal

**Penyebab:** aplikasi di Streamlit Cloud belum diperbarui (redeploy).

**Solusi:**
1. Jangan mendemonstrasikan dari cloud sebelum redeploy.
2. Selalu gunakan versi lokal untuk demo.
3. Untuk memperbarui cloud, push versi terbaru ke repositori Git lalu redeploy di Streamlit Cloud.

## 7.5 Peta Tidak Menampilkan Data

**Solusi:**
1. Klik tombol **"Apply Filters"** — seleksi wilayah tidak berefek sampai tombol ini diklik.
2. Pastikan file `data/java_job_market_hubs_final.csv` ada dan berisi 119 baris wilayah.
3. Periksa koneksi internet untuk tile peta `carto-darkmatter`.

---

# Bab 8. Lampiran

## 8.1 Struktur File Proyek

```
clustering-jobs/
├── dashboard.py                  → Aplikasi dashboard utama (Streamlit)
├── requirements.txt              → Daftar paket Python
├── METODOLOGI.md                 → Penjelasan metodologi dan parameter
├── data/
│   ├── java_job_market_hubs_final.csv   → Hasil klastering dan indeks (119 wilayah)
│   ├── java_regencies.geojson           → Batas kabupaten/kota Pulau Jawa
│   └── 38 Provinsi Indonesia - Kabupaten.json → Batas nasional (sumber awal)
├── src/
│   ├── 1_acquisition_jobstreet.py       → Akuisisi data Jobstreet
│   ├── 2_bps_consolidation.py           → Konsolidasi data BPS 6 provinsi
│   ├── 3_geocoding_regencies.py         → Geocoding centroid kabupaten/kota
│   ├── 4_data_integration.py            → Integrasi spasial (fuzzy matching)
│   ├── 5_opportunity_index.py           → Perhitungan indeks peluang
│   ├── 6_spatial_clustering_dbscan.py   → Klastering spasial DBSCAN
│   └── prepare_dashboard_data.py        → Utilitas persiapan data peta
└── archive/                             → Skrip eksplorasi lama (draft)
```

## 8.2 Sumber Data dan Lisensi

| Data | Sumber | Keterangan |
|---|---|---|
| Lowongan kerja | Jobstreet (`JobSearchV6`), Glints (`searchJobsV3`), Kalibrr (`/kjs/job_board/search`) | Data publik lowongan; pengambilan via `curl_cffi` |
| Pengangguran terbuka | BPS 2025 (6 provinsi: Banten, DKI Jakarta, Jawa Barat, Jawa Tengah, DIY, Jawa Timur) | Data resmi statistik |
| Koordinat wilayah | Nominatim (OpenStreetMap) | Centroid kabupaten/kota |
| Tile peta | CARTO (carto-darkmatter) | Ditampilkan pada peta Plotly |

## 8.3 Angka Siap Kutip (Terverifikasi)

| Klaim | Nilai |
|---|---|
| Wilayah analisis | 119 kabupaten/kota Pulau Jawa |
| Lowongan terintegrasi | 36.058 |
| Lowongan mentah | 52.450 (49.928 Jobstreet + 1.525 Glints + 997 Kalibrr) |
| Sumber lowongan | 3 platform (setelah dedup: Jobstreet 33.865; Glints 1.508; Kalibrr 685) |
| Dataset BPS | 6 dataset 2025 |
| Parameter DBSCAN | eps=0,08, min_samples=3, StandardScaler (lat, lon) |
| Silhouette Score | 0,4649 |
| Davies-Bouldin Index | 0,5294 |
| Cluster 0 | 93 wilayah / 11.978 lowongan |
| Cluster 1 | 22 wilayah / 24.078 lowongan |
| Terisolasi | 4 wilayah / 2 lowongan |
| Indeks | Volume Lowongan ÷ Pengangguran Terbuka |
| Top 5 Lautan Peluang | Jakarta Barat (0,1001); Yogyakarta (0,0839); Jakarta Selatan (0,0644); Jakarta Pusat (0,0639); Jakarta Utara (0,0439) |

---

*Manual book ini disusun untuk melengkapi folder 05 (MANUAL BOOK) pada DVD Tugas Akhir. Untuk rincian kode program, merujuk pada lampiran listing program pada dokumen Tugas Akhir. Untuk metodologi lengkap, merujuk pada METODOLOGI.md dan bab metodologi Tugas Akhir.*
