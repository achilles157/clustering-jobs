# 🎤 NASKAH DEMO — "Persebaran Peluang Kerja di Pulau Jawa" (dashboard.py)

> **Disusun oleh:** Penulis Naskah Demo · **Durasi target:** ± 9–10 menit (7–10 menit sesuai ketentuan)
> **Bahasa:** Indonesia formal-santai, siap ucap langsung
> **Sumber:** subagent_01 (inventori fitur) + subagent_02 (pemeriksaan fakta) + `dashboard.py` + `walkthrough.md` + `METODOLOGI.md`

---

## 📋 Catatan Persiapan (baca sebelum demo — bukan bagian yang dibacakan)

- **Jalankan dari lokal** (wajib): versi di Streamlit Cloud (`persebaran-lowongan-kerja.streamlit.app`) **masih versi lama tanpa dark theme** — jangan demo dari cloud sebelum redeploy.
- **Perintah run persis** (Python default di PATH **tidak** punya plotly/streamlit):
  ```powershell
  C:\Users\Falah\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run dashboard.py
  ```
  (jalankan dari folder proyek, setelah `pip install -r requirements.txt`).
- **Butuh internet saat load**: logo sidebar (icons8), font Plus Jakarta Sans (Google Fonts), tile peta carto-darkmatter. Siapkan koneksi/hotspot.
- **Legenda Tab 2 sudah diperbaiki** menjadi pill navy + teks putih — jangan lupa bisa disebut sebagai salah satu bugfix kualitas kode.
- Angka metrik model (Silhouette 0.4649, DBI 0.5294) memang **hardcoded** di kode, tapi sudah **terverifikasi benar** hasil reproduksi ulang — aman dikutip, tapi jangan diklaim "berubah live".
- Penanda waktu `[mm:ss]` = perkiraan posisi durasi bicara.

---

## 1. Pembukaan — [00:00] · ± 40 detik

> *(Berdiri, pandang penguji, nada tenang.)*

"Assalamu'alaikum warahmatullahi wabarakatuh. Selamat siang, Bapak/Ibu penguji yang saya hormati. Perkenalkan, saya Falah. Pada kesempatan ini, saya akan mempresentasikan hasil penelitian skripsi saya yang berjudul **'Persebaran Peluang Kerja di Pulau Jawa'**.

Tujuan penelitian ini ada dua: **pertama**, mengidentifikasi *hub* ekonomi — pusat-pusat aglomerasi pasar kerja — yang terbentuk secara alami di Pulau Jawa; dan **kedua**, memetakan peluang kerja di 119 kabupaten/kota, menggunakan algoritma **DBSCAN**, yaitu klastering spasial berbasis kepadatan. Untuk mempermudah pemaparan, seluruh hasil analisis saya rangkum dalam sebuah *dashboard* interaktif berbasis Streamlit, dan pada kesempatan ini saya akan mendemonstrasikannya langsung di layar."

---

## 2. Latar Belakang Data & Metode — [00:40] · ± 1 menit 20 detik

> *(Sebelum masuk aplikasi, tetap di halaman terminal/beranda.)*

"Sebelum masuk ke *demo*, saya jelaskan dulu fondasi datanya.

Data lowongan kerja diperoleh dari **tiga platform — Jobstreet, Glints, dan Kalibrr**. Total **52.450 lowongan mentah** berhasil dikumpulkan (49.928 Jobstreet + 1.525 Glints + 997 Kalibrr), dan setelah proses integrasi serta deduplikasi lintas platform, **36.058 di antaranya** berhasil dipetakan ke **119 kabupaten/kota** di Pulau Jawa. Data lowongan ini kemudian dipadukan dengan data sekunder **pengangguran terbuka dari enam dataset BPS 2025**, satu untuk setiap provinsi di Jawa.

*Pipeline* penelitian terdiri dari **enam tahap**: akuisisi data dari tiga platform lowongan kerja; konsolidasi data BPS dan *geocoding* titik pusat wilayah; integrasi spasial dengan *fuzzy matching*; penghitungan indeks peluang; klastering spasial DBSCAN; dan terakhir visualisasi melalui *dashboard* yang akan kita lihat sebentar lagi.

Untuk klastering, saya menggunakan **DBSCAN dengan eps 0,08 dan min_samples 3**, pada fitur latitude dan longitude yang telah distandarisasi dengan *StandardScaler*. Kenapa DBSCAN, bukan K-Means? Karena pola aglomerasi di Pulau Jawa itu **memanjang horizontal mengikuti koridor Trans-Jawa** — bentuknya tidak *spherical*. K-Means mengasumsikan klaster berbentuk bola dan memaksa seluruh wilayah masuk ke salah satu klaster. DBSCAN berbasis kepadatan: tidak perlu menentukan jumlah klaster di awal, dan secara alami mengeluarkan wilayah-wilayah terpencil sebagai *noise*. Hasilnya terbentuk **dua klaster riil plus zona terisolasi** — dan ini yang akan kita lihat langsung di *dashboard*-nya."

---

## 3. Cara Menjalankan — [02:00] · ± 25 detik

> *(Tampilkan command di terminal/proyek.)*

"Sebelum *demo*, saya perlihatkan sebentar cara menjalankan aplikasinya. Setelah seluruh dependensi dari `requirements.txt` terpasang, *dashboard* dijalankan dengan perintah:

```powershell
C:\Users\Falah\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run dashboard.py
```

Perintah ini menggunakan *interpreter* Python 3.13 khusus, karena Python *default* di mesin ini belum memiliki pustaka Plotly dan Streamlit. Setelah perintah ini dijalankan, aplikasi terbuka di browser, dan kita masuk ke halaman utamanya."

> *(Catatan penyaji: jika ditanya soal Streamlit Cloud — jawab jujur: versi publik masih versi lama tanpa dark theme; demo hari ini dari lokal. Detail di Lampiran C.)*

---

## 4. Walkthrough Dashboard per Tab — [02:25] · ± 5 menit 50 detik

### 4.1 Sidebar & Filter (sebelum masuk tab) — [02:25] · ± 40 detik

**APA yang ditampilkan:** sidebar berisi logo, judul, *selectbox* provinsi, *selectbox* kabupaten/kota (bergantung provinsi), tombol `"Apply Filters"`, blok `"Konteks Wilayah (Terpilih)"`, dan caption `v2.0 • DBSCAN Pure Spatial (eps=0.08) • Opsi C (÷Pengangguran)`.

**POIN BICARA:** pola *session state* — seleksi tidak berefek sampai tombol diklik; ini implementasi Activity Diagram 1 & Wireframe skripsi.

> *(Arahkan kursor ke sidebar, gerakkan perlahan dari atas ke bawah.)*

"Baik, sekarang kita masuk ke aplikasinya. Di *sidebar* terdapat filter wilayah: **pertama** kita pilih provinsi, dan daftar kabupaten/kota otomatis menyesuaikan diri dengan provinsi yang dipilih. Satu hal yang perlu diperhatikan: perubahan seleksi **belum langsung mengubah tampilan** — kita harus menekan tombol **'Apply Filters'** terlebih dahulu. Ini sengaja dirancang mengikuti *activity diagram* dan *wireframe* pada skripsi, memakai *session state* agar data yang diproses stabil dan tidak berubah ketika halaman me-*refresh*. Setelah tombol diklik, blok **'Konteks Wilayah (Terpilih)'** memperbarui isinya — provinsi, status wilayah, dan klasifikasi DBSCAN-nya — nanti blok ini selalu kita jadikan rujukan cepat saat berganti kota."

### 4.2 Tab 1 — "🔍 Filter & Parameter" — [03:05] · ± 40 detik

**APA yang ditampilkan:** 4 kartu metrik — `Volume Lowongan`, `Pengangguran Terbuka`, `Indeks Peluang` (5 desimal), `Indeks Kompetitif` (skala /3.0) — lalu `Raw Data Table` berisi judul pekerjaan, perusahaan, lokasi asli.

**POIN BICARA:** jumlah baris lowongan yang tampil vs total 36.058; tabel ini bukti data riil, bukan simulasi.

> *(Klik tab 1. Tunjuk kartu metrik, lalu scroll ke tabel.)*

"Tab pertama, **'Filter & Parameter'**, menampilkan ringkasan empat parameter untuk wilayah terpilih: **Volume Lowongan** — jumlah posisi yang tersedia; **Pengangguran Terbuka** — dari data BPS; **Indeks Peluang**; dan **Indeks Kompetitif** dengan skala 0 sampai 3. Di bawahnya ada **tabel data mentah lowongan** — judul pekerjaan, perusahaan, dan lokasi asli hasil *scraping* — lengkap dengan jumlah baris yang tampil untuk wilayah ini dari total dataset 36.058 lowongan. Saya tekankan: tabel ini bukan data simulasi, melainkan lowongan nyata yang berhasil dikumpulkan dari tiga platform (Jobstreet, Glints, Kalibrr)."

### 4.3 Tab 2 — "📍 Klaster Ekonomi" (inti demo) — [03:45] · ± 1 menit 30 detik

**APA yang ditampilkan:** `scatter_map` Plotly (3 warna klaster + penanda emas `Lokasi Target`), 3 kartu komposisi, info-box catatan DBSCAN, legenda pill navy (bugfix).

**POIN BICARA:** warna = klaster, ukuran = volume lowongan; komposisi 93/22/4 wilayah dan 11.978/24.078/2 lowongan; contoh kota per klaster; cerita bugfix legenda.

> *(Klik tab 2. Arahkan pointer ke peta: tunjuk penanda emas, lalu satu-dua titik cluster.)*

"Tab kedua — dan ini inti dari penelitian — adalah **'Klaster Ekonomi'**. Ini peta hasil DBSCAN: *scatter map* di mana **warna lingkaran menunjukkan klaster** dan **ukuran lingkaran menunjukkan volume lowongan**. Ada tiga warna. **Biru**, *Cluster 0: Java Mainland Hub* — aglomerasi utama di koridor *mainland* Jawa yang mencakup pusat-pusat regional seperti **Surabaya, Bandung, Semarang, dan Solo**. **Hijau toska**, *Cluster 1: Jabodetabek & Koridor Barat* — aglomerasi metropolitan dengan densitas lowongan tertinggi, mencakup **Jabodetabek, Serang, Karawang, dan Cilegon**. Dan **abu-abu**, *Isolated Red Zone* — 4 wilayah terpencil seperti **Kepulauan Seribu, Kota Banjar, Kota Pekalongan, dan Sumenep** yang volume lowongannya nyaris nol. Penanda **emas** di peta menunjukkan lokasi wilayah yang sedang kita filter, jadi wilayah terpilih selalu mudah ditemukan.

Tiga kartu di bawah peta merangkum komposisinya: **Cluster 0 mencakup 93 wilayah dengan sekitar 11.978 lowongan**; **Cluster 1 hanya 22 wilayah, tetapi menampung sekitar 24.078 lowongan** — ini bukti konsentrasi lapangan kerja yang sangat timpang di koridor barat; dan **zona terisolasi 4 wilayah dengan total hanya sekitar 2 lowongan**.

Satu catatan teknis kecil: legenda peta ini sebelumnya bermasalah — teks putih menyatu dengan latar terang — dan telah saya perbaiki menjadi *pill* navy dengan teks putih agar terbaca jelas. Ini bagian dari perbaikan kualitas aplikasi."

> *(Catatan penyaji: info-box di dashboard juga menyebut "GKS" sebagai contoh Cluster 0 — singkatan tidak terdokumentasi. Jangan sebut "GKS" di depan penguji; jika ditanya, jelaskan sebagai kawasan Gerbangkertosusila (Gresik–Bangkalan–Mojokerto–Surabaya–Sidoarjo–Lamongan).)*

### 4.4 Tab 3 — "🔥 Heatmap Peluang" — [05:15] · ± 1 menit

**APA yang ditampilkan:** rumus LaTeX `Indeks_Peluang = Volume_Lowongan / Pengangguran_Terbuka`, choropleth RdYlGn, info-box panduan interpretasi.

**POIN BICARA:** hijau = Lautan Peluang, merah = Zona Merah; range warna dipotong kuantil 90%; peta memusat ke kota terpilih; fallback density_map bila GeoJSON hilang.

> *(Klik tab 3. Tunjuk rumus dulu, lalu peta.)*

"Tab ketiga, **'Heatmap Peluang'**. Indeks peluang didefinisikan sebagai **volume lowongan dibagi jumlah pengangguran terbuka** — rumusnya tampil di sini dalam format LaTeX. Peta *choropleth* di bawahnya mewarnai **116 dari 119 wilayah** dengan skala merah–kuning–hijau: **hijau berarti 'Lautan Peluang'** — jumlah lowongan tinggi relatif terhadap penganggur terbuka, artinya peluang tersedia lebih banyak daripada pencari kerja aktif, sehingga direkomendasikan bagi pencari kerja; sebaliknya **merah berarti 'Zona Merah'** — persaingan padat, kesempatan kerja tipis dibandingkan penganggur yang benar-benar butuh kerja, indikasi kejenuhan.

Dua hal teknis yang saya ingin sampaikan: **pertama**, rentang warna sengaja dipotong pada kuantil 90 persen, supaya segelintir wilayah *outlier* tidak mendominasi seluruh pewarnaan peta; **kedua**, peta ini otomatis memusatkan pandangan ke kota yang sedang kita pilih — jadi fokus analisis selalu mengikuti wilayah yang difilter."

### 4.5 Tab 4 — "📈 Statistik Efisiensi" — [06:15] · ± 1 menit

**APA yang ditampilkan:** scatter pengangguran terbuka vs volume lowongan + trendline OLS (`#00A6FB`), bar Top-15 Indeks Kompetitif, lalu metrik evaluasi model (Silhouette 0.4649, DBI 0.5294) + caption interpretasi.

**POIN BICARA:** wilayah di atas trendline = penciptaan kerja abnormal positif; skala kompetitif ≥2,5 manajerial vs 1,0–1,5 kerah biru; makna kedua metrik + justifikasi DBSCAN vs K-Means.

> *(Klik tab 4. Tunjuk scatter kiri, lalu scroll ke metrik model.)*

"Tab keempat, **'Statistik Efisiensi'**. Di sebelah kiri ada *scatter plot* antara **pengangguran terbuka** dan **volume lowongan**, dengan garis tren OLS berwarna biru. Wilayah yang berada **di atas garis tren** menciptakan lapangan kerja lebih banyak dari yang diprediksikan beban penganggurnya — ini performa penciptaan kerja yang abnormal secara positif. Di kanan, *bar chart* 15 wilayah dengan indeks kompetitif tertinggi: skor di atas 2,5 didominasi posisi manajerial elit, sementara skor sekitar 1,0 hingga 1,5 mengindikasikan pasar kerja kerah biru dan peranan operasional.

Di bagian bawah ada **metrik evaluasi model spasial**: *Silhouette Score* **0,4649** dan *Davies-Bouldin Index* **0,5294**. Silhouette 0,4649 berada pada kategori moderat-baik — dan ini konsisten dengan karakter aglomerasi Jawa yang memanjang horizontal mengikuti koridor Trans-Jawa, bukan berbentuk *spherical*; justru pada pola seperti inilah DBSCAN lebih tepat dibandingkan K-Means. DBI 0,5294, yang berada di bawah 1,0, menunjukkan pemisahan antar klaster yang baik — artinya Cluster 0 dan Cluster 1 tidak saling tumpang tindih secara spasial."

### 4.6 Tab 5 — "📝 Laporan Eksekutif" — [07:15] · ± 1 menit

**APA yang ditampilkan:** narasi kesimpulan otomatis 3 paragraf, metrik `Rekomendasi` & `Persaingan`, Raw Data Profil, lalu tabel `🌟 Top 5 Lautan Peluang` & `🚨 Top 5 Zona Merah`.

**POIN BICARA:** logika pemeringkatan (Top-10 → Sangat Layak; bottom-15 → Berisiko; Zona Merah override; 0 lowongan → Tidak Terperingkat); narasi berubah otomatis per kota.

> *(Klik tab 5. Tunjuk narasi kiri, metrik kanan, lalu scroll ke dua tabel.)*

"Tab terakhir, **'Laporan Eksekutif'**. Ini ringkasan otomatis untuk wilayah terpilih: **narasi kesimpulan** tiga paragraf yang ditarik langsung dari hasil DBSCAN dan indeks peluang — identifikasi klaster, statistik pengangguran terbuka, volume lowongan, dan kesimpulan berdasarkan peringkat; plus **penilaian kritis** berupa dua metrik, **Rekomendasi** dan tingkat **Persaingan**. Di bawahnya ada profil data mentah wilayah, lalu dua tabel peringkat seluruh Pulau Jawa: **'Top 5 Lautan Peluang'** — wilayah dengan rasio lowongan tertinggi terhadap penganggur terbuka — dan **'Top 5 Zona Merah'** — wilayah dengan tingkat persaingan terpadat atau ketersediaan lapangan kerja terkecil. Semua narasi ini **dihitung ulang secara dinamis** setiap kali kita mengganti wilayah — dan itu akan saya tunjukkan sekarang."

---

## 5. Contoh Skenario Demo: Dua Wilayah yang Berbeda — [08:15] · ± 1 menit

**POIN BICARA:** bukti output berubah mengikuti input; kontras "Lautan Peluang" vs "Zona Merah" (kota besar vs kabupaten).

> *(Langkah layar: Sidebar → pilih provinsi **DKI Jakarta** → pilih **Kota Jakarta Barat** → klik `Apply Filters` → tunjukkan Tab 5.)*

"Supaya lebih jelas bagaimana *output* berubah mengikuti wilayah, mari bandingkan dua wilayah. **Pertama**, saya pilih **Kota Jakarta Barat**. *(klik)* Di laporan eksekutif, Jakarta Barat menempati **peringkat 1 dari 116 wilayah aktif**, dengan **7.498 lowongan** untuk **74.910 penganggur terbuka** — rasio indeks peluang **0,10**, artinya tersedia sekitar **10 lowongan per 100 penganggur**. Rekomendasi **'Sangat Layak'**, persaingan **'Longgar'** — ini 'Lautan Peluang' sejati.

**Kedua**, saya ganti ke **Kabupaten Sukabumi**. *(klik: Provinsi Jawa Barat → Sukabumi → Apply Filters, kembali ke Tab 5.)* Perhatikan kontrasnya: Sukabumi hanya memiliki **12 lowongan** untuk **110.512 penganggur terbuka** — rasio indeks peluang nyaris **0,0001**. Sistem mengklasifikasikannya sebagai **'Zona Merah'**, dengan rekomendasi **'Berisiko'** dan persaingan **'Sengit'**. Dua wilayah di pulau yang sama, dua nasib pasar kerja yang sangat berbeda — dan semuanya terlihat hanya dengan mengganti filter. Inilah nilai guna *dashboard* ini: pengambil keputusan dan pencari kerja bisa langsung membaca kondisi suatu wilayah tanpa membaca laporan panjang."

---

## 6. Penutup — [09:15] · ± 40 detik

> *(Tutup tab ke Tab 2 atau beranda, hadap penguji kembali.)*

"Sebagai penutup, penelitian ini berhasil mencapai dua hal. **Pertama**, mengidentifikasi **dua hub ekonomi utama** di Pulau Jawa — aglomerasi *mainland* dan aglomerasi Jabodetabek beserta koridor industri barat — yang terbentuk secara otonom dari kepadatan lowongan, tanpa mengikuti batas administrasi provinsi. **Kedua**, memetakan **sebaran peluang kerja** di 119 kabupaten/kota melalui indeks peluang. Implikasi kebijakannya: desentralisasi penciptaan lapangan kerja perlu diarahkan ke wilayah-wilayah 'Lautan Peluang' yang suplai tenaga kerjanya belum terpenuhi, sementara wilayah 'Zona Merah' membutuhkan intervensi penciptaan lapangan kerja formal. Seluruh temuan ini berbasis **data BPS Sosioekonomi 2025** dan **lowongan dari tiga platform (Jobstreet, Glints, Kalibrr)** yang diambil melalui API.

Demikian presentasi saya. Saya persilakan Bapak/Ibu penguji untuk memberikan pertanyaan dan masukan. Terima kasih."

---

## Lampiran

### A. 📌 Angka "Siap Kutip" (terverifikasi)

| Klaim | Nilai | Catatan |
|---|---|---|
| Jumlah wilayah analisis | **119 kabupaten/kota** Pulau Jawa | 119 baris CSV + 119 features GeoJSON |
| Lowongan terintegrasi | **36.058** | dipakai semua analisis & tabel dashboard |
| Lowongan mentah hasil scrape | **52.450** (49.928 Jobstreet + 1.525 Glints + 997 Kalibrr) | hanya untuk cerita akuisisi; jangan dicampur dengan 36.058 |
| Sumber lowongan | **3 platform**: Jobstreet, Glints, Kalibrr | setelah dedup: Jobstreet 33.865; Glints 1.508; Kalibrr 685 |
| Dataset BPS | **6 dataset 2025** (Banten, DIY, DKI, Jabar, Jateng, Jatim) | footer dashboard: "BPS Sosioekonomi 2025" |
| Parameter DBSCAN | **eps=0.08, min_samples=3**, fitur Latitude/Longitude di-*StandardScaler* | label sidebar: "DBSCAN Pure Spatial" |
| Silhouette Score | **0,4649** (moderat-baik; -1 s/d +1) | hasil reproduksi ulang persis |
| Davies-Bouldin Index | **0,5294** (mendekati 0 = baik; <1 = tidak overlap) | hasil reproduksi ulang persis |
| Komposisi klaster | Cluster 0: **93 wilayah / 11.978 lowongan**; Cluster 1: **22 wilayah / 24.078 lowongan**; Terisolasi: **4 wilayah / 2 lowongan** | jumlah = 2 klaster + zona terisolasi |
| Formula indeks | Indeks Peluang = Volume Lowongan / Pengangguran Terbuka (Opsi C) | sama di kode, pipeline, & METODOLOGI |
| Contoh Cluster 0 | Surabaya, Bandung, Semarang, Yogyakarta (+ Sidoarjo, Sleman) | "GKS" ambigu → hindari |
| Contoh Cluster 1 | Jakarta Barat, Jakarta Selatan, Jakarta Utara, Jakarta Pusat, Tangerang, Bekasi | terverifikasi dari anggota aktual |
| Contoh Terisolasi | Kepulauan Seribu, Kota Banjar, Kota Pekalongan, Sumenep | Kep. Seribu (2 loker); sisanya 0 loker |
| Top 5 Lautan Peluang (live) | Kota Jakarta Barat (0,1001), Kota Yogyakarta (0,0839), Kota Jakarta Selatan (0,0644), Kota Jakarta Pusat (0,0639), Kota Jakarta Utara (0,0439) | referensi jika penguji bertanya isi tabel |
| Akuisisi | Jobstreet `JobSearchV6` (publik), Glints `searchJobsV3`, Kalibrr `/kjs/job_board/search` via `curl_cffi`; geocoding centroid Nominatim (OSM) | cerita teknis pipeline |

### B. 🚫 Jangan Dikuitp Presenter (salah/stale — sudah diverifikasi)

1. ❌ **"eps=0.45"** / **"radius ±50 km"** → salah; yang benar eps=0.08 pada koordinat ter-*standardisasi* (eps bukan satuan kilometer).
2. ❌ **"fuzzy match 88,8%"** → tidak relevan lagi (multi-platform); cukup katakan "threshold kecocokan ≥ 80".
3. ❌ **Silhouette 0,4722 / DBI 0,5136** (versi narasi TA & jurnal lama) → gunakan **0,4649 / 0,5294** (terbukti benar, data 3 platform).
4. ❌ **"koridor Surabaya–Malang"** → Kota Malang sekarang **masuk Cluster 0** (465 lowongan); koridor yang tepat: Surabaya–Sidoarjo–Malang Raya.
5. ❌ **"Madura seluruhnya isolated"** → Bangkalan, Sampang, Pamekasan masuk Cluster 0; hanya **Sumenep** yang terisolasi (0 lowongan).
6. ❌ **"17 wilayah noise"** → aktual **4 wilayah terisolasi** (Kep. Seribu + Banjar + Pekalongan + Sumenep).
7. ❌ **"3 klaster"** → hanya **2 klaster riil** (0 & 1); label -1 adalah zona terisolasi, bukan klaster.
8. ❌ **"GKS"** sebagai contoh wilayah → singkatan tidak terdokumentasi (kemungkinan Gerbangkertosusila, tapi bukan satu wilayah administratif).
9. ⚠️ Jangan klaim "angka metrik berubah live" — hardcoded namun benar; katakan "dihitung pada pipeline dan sudah direproduksi ulang".
10. ⚠️ Glints & Kalibrr **SUDAH** jadi sumber dashboard (3 platform) — jangan bilang "hanya Jobstreet".

### C. 🎓 Kemungkinan Pertanyaan Penguji & Jawaban Singkat

**1. Mengapa memilih DBSCAN, bukan K-Means?**
> "Pola aglomerasi pasar kerja di Jawa memanjang horizontal mengikuti koridor Trans-Jawa — bentuknya tidak spherical. K-Means mengasumsikan klaster berbentuk bola dan mewajibkan penentuan jumlah k di awal, serta memaksa semua titik masuk klaster. DBSCAN berbasis kepadatan: tidak perlu menentukan jumlah klaster, menemukan klaster bentuk bebas, dan secara natural mengeluarkan wilayah-wilayah terpencil sebagai zona terisolasi. Hasil klaster yang terbentuk pun terverifikasi masuk akal secara geografis — Jabodetabek dan koridor barat menjadi satu kesatuan."

**2. Apa arti Silhouette 0,4649 dan DBI 0,5294?**
> "Silhouette berkisar -1 sampai +1; 0,4649 berarti objek lebih dekat ke klasternya sendiri daripada klaster lain — kategori moderat-baik. Nilai ini moderat karena memang aglomerasi Jawa memanjang (elongated), bukan gugus bulat — justru alasan DBSCAN lebih tepat. DBI dihitung dengan eksklusi noise agar tidak bias; 0,5294 di bawah 1,0 menunjukkan antar-klaster tidak saling tumpang tindih. Kedua angka dihitung pada pipeline dan saya reproduksi ulang persis dari data."

**3. Bagaimana data diperoleh, dan apakah legal/etis?**
> "Lowongan diambil dari tiga platform — Jobstreet (GraphQL `JobSearchV6`, endpoint publik), Glints (GraphQL `searchJobsV3`), dan Kalibrr (API `/kjs/job_board/search` dengan cookie sesi) — melalui `curl_cffi`. Yang diambil hanya data publik lowongan (judul, perusahaan, lokasi), bukan data pribadi pengguna. Total 52.450 lowongan mentah; setelah integrasi, fuzzy matching `rapidfuzz` (threshold ≥ 80) ke wilayah BPS, deduplikasi lintas platform, dan filter ke Pulau Jawa, tersisa 36.058 lowongan terintegrasi. Penyebut indeks adalah pengangguran terbuka dari enam dataset BPS 2025. Geocoding memakai centroid kabupaten/kota via Nominatim (OpenStreetMap)."

**4. Bagaimana membaca nilai indeks peluang?**
> "Indeks peluang didefinisikan sebagai jumlah lowongan terobservasi dibagi jumlah penganggur terbuka — bukan seluruh angkatan kerja. Contoh Kota Jakarta Barat: 7.498 lowongan dibagi 74.910 penganggur = 0,10, artinya tersedia sekitar 10 lowongan per 100 penganggur terbuka. Nilai ini dimaknai sebagai ukuran perbandingan relatif antar-wilayah — makanya divisualisasikan lewat peringkat dan peta, bukan nilai absolut — dan rentang warna peta dipotong di kuantil 90% karena distribusinya miring ke kanan (Jakarta Barat sebagai outlier)."

**5. Apa batasan penelitian ini?**
> "Ada beberapa: pertama, data lowongan dari tiga platform (Jobstreet, Glints, Kalibrr) pada satu titik waktu, sehingga belum menangkap seluruh pasar kerja formal maupun lowongan non-digital. Kedua, geocoding memakai centroid kabupaten/kota, bukan koordinat persis perusahaan. Ketiga, pengangguran terbuka BPS mencakup seluruh sektor, sementara lowongan hanya sektor formal tercatat. Keempat, hasil DBSCAN sensitif terhadap parameter eps dan min_samples — perlu studi sensitivitas. Kelima, fuzzy matching tidak sempurna. Saran pengembangan: data panel waktu, geocoding lebih presisi, dan validasi sensitivitas parameter."

---

*Naskah disusun oleh subagent "Penulis Naskah Demo" berdasarkan subagent_01, subagent_02, dashboard.py, walkthrough.md, dan METODOLOGI.md — diperbarui 2026-08-17. Semua angka telah diverifikasi ulang dari reproduksi komputasi aktual (data 3 platform, indeks Opsi C).*
