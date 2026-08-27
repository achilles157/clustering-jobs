# Subagent 02 — Laporan Pemeriksaan Gap & Rancangan Template DVD TA Falah

**Tanggal:** 27 Agustus 2026 · **NPM:** 202243502165 · **Nama:** Falah Fahrurozi
**Judul TA:** Persebaran Peluang Karir Berdasarkan Jumlah Angkatan Kerja menggunakan Density Based Clustering (DBSCAN)
**Folder DVD (label):** `202243502165_FALAH FAHRUROZI`

---

## 1. Ringkasan Status per Folder (Tabel Gap)

| Folder DVD | Aturan UNINDRA | Status | Bahan yang ADA di workspace | Gap / yang harus dilengkapi | Diisi oleh |
|---|---|---|---|---|---|
| **01 SCAN LEMBAR PENGESAHAN DAN PERSETUJUAN** | Scan pengesahan + persetujuan pembimbing, .JPG/.PDF | 🔴 **HARUS USER ISI SENDIRI** | Tidak ada scan resmi di workspace (hanya screenshot chat di `.openclaw-attachments/` — bukan dokumen resmi) | Scan lembar pengesahan & persetujuan yang **sudah ditandatangani dosen** (fisik) → .jpg/.pdf | **USER** |
| **02 TUGAS AKHIR** | TA bab 1-5 + cover + pernyataan + abstrak s/d lampiran, .DOC/.DOCX | 🟡 **SEBAGIAN — hampir lengkap, perlu verifikasi & pilih versi final** | `DELIVERY/TA FALAH - zotero field codes FINAL - PELUANG KARIR - FINAL-2D.docx` (9,3 MB, 27/08 10:41 — TERBARU) + PDF; struktur lengkap terverifikasi: Lembar Persetujuan, Pengesahan, Pernyataan, Abstrak, Bab I–V, Daftar Pustaka, Riwayat Hidup, Listing Program; `Lampiran TA.md`, `LAMPIRAN_FINAL_CLEAN.md`; banyak versi lama di root (jangan ikut disalin) | Pastikan versi yang disetujui dosen = FINAL-2D; cek cover, lampiran benar-benar termuat (lampiran kode dashboard ada sebagai listing); lembar pengesahan **bertanda tangan asli** terpisah di folder 01 | **AGENT** (salin versi final) + **USER** (konfirmasi versi yg disetujui) |
| **03 SOFTWARE PENDUKUNG** | Browser, XAMPP, NetBeans, emulator, dll | 🔴 **HARUS USER ISI SENDIRI** | Tidak ada installer di workspace | Unduh installer resmi (Chrome/Edge, XAMPP, NetBeans, Android Studio/emulator dsb.) — AI tidak bisa membuat installer | **USER** (AI siapkan README daftar + link resmi) |
| **04 SOFTWARE PROGRAM** | Project TA + executable .EXE/.JAR/.APP | 🟡 **SEBAGIAN** | Project lengkap: `dashboard.py` (46 KB, Streamlit), `src/1_..6_` (pipeline), `requirements.txt`, `data/` (CSV + GeoJSON), `build_notebook.py`, `spatial_clustering_pipeline.ipynb`, `METODOLOGI.md` | **Executable belum ada** — program berbasis Python/Streamlit, bukan Java/.NET; build .EXE via PyInstaller berisiko (Streamlit exe besar & rapuh). Opsi: (a) sertakan project + launcher `.bat` + panduan run, (b) user/agent coba build exe, (c) konfirmasi dosen apakah web-app diterima | **AGENT** (kemas project + launcher + panduan) + **USER** (keputusan format exe) |
| **05 MANUAL BOOK** | Langkah penggunaan program, .DOC/.DOCX | 🟡 **SEBAGIAN — AI bisa buat draft penuh** | Bahan nyata: `walkthrough.md`, `README.md`, `DELIVERY/naskah-demo-dashboard.md`, `LAMPIRAN_KODE_DASHBOARD.md`, `METODOLOGI.md` | Belum ada file manual book sama sekali → buat .docx dari kerangka §2.a | **AGENT** (buat draft) + **USER** (verifikasi, tambah detail lokal) |
| **06 USERNAME DAN PASSWORD** | Kredensial aplikasi, .DOC/.DOCX | 🟡 **SEBAGIAN — template AI, nilai user** | Tidak ada file kredensial (aman & wajar) | Buat template tabel kosong; **nilai asli hanya user yang tahu** | **AGENT** (template) + **USER** (isi nilai) |
| **07 ARTIKEL ILMIAH** | Artikel .DOC/.DOCX, daftar pustaka **MENDELEY**, + **screenshot bukti submit** | 🟡 **SEBAGIAN** | `DELIVERY/Jurnal Ilmiah - ... - Template Penelitian - FINAL.docx` (27/08 10:46 — TERBARU) + `Template Umum - FINAL-2D.docx` + PDF; `ref-falah/ref-falah.bib` (54 KB); `new-zotero/new-zotero.rdf` | ⚠️ Daftar pustaka jurnal saat ini **pakai field codes ZOTERO (91–99 referensi, 0 Mendeley)** — pengumuman mensyaratkan MENDELEY → perlu konversi/refresh via Mendeley; **screenshot bukti submit artikel TIDAK ADA** | **AGENT** (catatan konversi Mendeley + salin artikel final) + **USER** (impor .bib ke Mendeley, screenshot bukti submit) |

**Kesimpulan singkat:** dari 7 folder → 2 folder tinggal salin+verifikasi (02, 04), 2 folder bisa AI buat draft penuh (05, sebagian 06), 2 folder sepenuhnya user (01, 03), 1 folder campuran (07). Item yang **fisik hanya di tangan user**: scan tanda tangan dosen, installer software, screenshot bukti submit jurnal, nilai kredensial asli, dan DVD fisiknya.

---

## 2. Rancangan Template

### 2.a Manual Book (Folder 05) — Kerangka .DOCX

> Bahan dasar (sudah dibaca, diringkas): `walkthrough.md` (pipeline 5 fase), `naskah-demo-dashboard.md` (skrip demo per tab), `README.md` (cara run), `LAMPIRAN_KODE_DASHBOARD.md` (struktur 11 seksi kode).

**Judul:** MANUAL BOOK — Aplikasi Dashboard Persebaran Peluang Kerja di Pulau Jawa (DBSCAN)

1. **Pendahuluan**
   - 1.1 Tujuan aplikasi: identifikasi hub ekonomi + pemetaan peluang kerja 119 kab/kota Pulau Jawa via DBSCAN
   - 1.2 Lingkup: data Jobstreet (~49.928), Glints (~1.525), Kalibrr (~997) → 36.058 lowongan terintegrasi; BPS 2025 (6 provinsi); snapshot April 2026
   - 1.3 Parameter model: DBSCAN eps=0,08, min_samples=3, StandardScaler(lat, lon); Indeks Peluang = Volume Lowongan ÷ Pengangguran Terbuka

2. **Kebutuhan Sistem**
   - OS Windows 10/11; Python 3.13 (di mesin user: `C:\Users\Falah\AppData\Local\Programs\Python\Python313`); pip
   - Paket (`requirements.txt`): streamlit, plotly, pandas, numpy, scikit-learn, rapidfuzz, curl_cffi, dll.
   - Internet dibutuhkan saat load (font Plus Jakarta Sans/Google Fonts, tile peta carto-darkmatter, logo sidebar)

3. **Instalasi**
   - 3.1 Copy folder project → `C:\...\clustering-jobs\`
   - 3.2 `pip install -r requirements.txt`
   - 3.3 Jalankan: `python -m streamlit run dashboard.py` (dari folder proyek; interpreter khusus yang punya plotly/streamlit)
   - 3.4 Verifikasi: browser terbuka ke `http://localhost:8501`

4. **Cara Pakai Fitur** (mengikuti alur demo asli, per tab)
   - 4.1 Sidebar & Filter Wilayah: pilih Provinsi → Kabupaten/Kota (cascading) → klik **Apply Filters** (session-state: seleksi belum berefek sampai tombol diklik) → blok *Konteks Wilayah (Terpilih)*
   - 4.2 Tab 1 — Filter & Parameter: 4 kartu metrik (Volume Lowongan, Pengangguran Terbuka, Indeks Peluang 5 desimal, Indeks Kompetitif /3.0) + tabel data mentah lowongan
   - 4.3 Tab 2 — Klaster Ekonomi (inti): scatter map 3 warna (Cluster 0 Java Mainland Hub — 93 wilayah/±11.978 lowongan; Cluster 1 Jabodetabek & Koridor Barat — 22 wilayah/±24.078 lowongan; Isolated Red Zone — 4 wilayah/±2 lowongan), penanda emas = lokasi terpilih, ukuran lingkaran = volume lowongan, legenda pill navy
   - 4.4 Tab 3 — Heatmap Peluang: rumus Indeks Peluang (LaTeX), choropleth RdYlGn (hijau = "Lautan Peluang", merah = "Zona Merah"), pemotongan kuantil 90%, auto-fokus ke kota terpilih, fallback density_map bila GeoJSON hilang
   - 4.5 Tab 4 — Statistik Efisiensi: scatter pengangguran vs lowongan + trendline OLS, bar Top-15 Indeks Kompetitif, metrik evaluasi (Silhouette 0,4649; DBI 0,5294 — terverifikasi, hardcoded)
   - 4.6 Tab 5 — Laporan Eksekutif (UC5): ringkasan otomatis per wilayah terpilih

5. **Interpretasi Hasil**: arti warna klaster, zona merah vs lautan peluang, peringatan "GKS = Gerbangkertosusila", keterbatasan (snapshot April 2026, bukan real-time)

6. **FAQ**
   - Peta kosong / data tidak muncul → cek jalankan dari folder proyek & file `data/` ikut terbawa
   - Peta hilang saat GeoJSON tidak ditemukan → fallback otomatis ke density map
   - Angka metrik model bisa berubah? → hardcoded tapi sudah diverifikasi reproduksi ulang
   - Perlu internet? → ya saat load (font, tile peta, logo)

7. **Troubleshooting**
   - `streamlit is not recognized` → pakai interpreter Python 3.13 penuh
   - `ModuleNotFoundError: plotly/streamlit` → `pip install -r requirements.txt`
   - Port 8501 dipakai → `streamlit run dashboard.py --server.port 8502`
   - Versi Streamlit Cloud lama (tanpa dark theme) → jangan demo dari cloud sebelum redeploy

8. **Lampiran**: struktur file project, sumber data & lisensi, rujukan `LAMPIRAN_KODE_DASHBOARD.md`

### 2.b Username & Password (Folder 06) — Kerangka Tabel (.DOCX)

> Template dibuat AI, **nilai dikosongkan** — hanya user yang mengisi (keamanan: jangan pernah dibagikan ke AI/chat).

| No | Aplikasi/Layanan | Username / Email | Password | Role | Keterangan |
|---|---|---|---|---|---|
| 1 | (contoh) Akun Google/Email | _isi user_ | _isi user_ | Umum | Untuk akses Gmail/Drive/Streamlit Cloud |
| 2 | Zotero / Mendeley | _isi user_ | _isi user_ | Referensi | Daftar pustaka artikel (folder 07) |
| 3 | GitHub | _isi user_ | _isi user_ | Repo | Backup project (`clustering-jobs`) |
| 4 | Streamlit Cloud | _isi user_ | _isi user_ | Deployment | `persebaran-lowongan-kerja.streamlit.app` |
| 5 | Akun job platform (Jobstreet/Glints/Kalibrr) | _isi user_ | _isi user_ | Scraping | Jika dipakai ulang |
| 6 | Database/aplikasi lain | _isi user_ | _isi user_ | — | Tambahkan baris sesuai kebutuhan |

+ Baris **catatan keamanan**: jangan simpan password asli di file yang ikut ter-upload; boleh placeholder bila ragu.
+ Catatan: aplikasi dashboard utama **tidak memiliki login sendiri** (web lokal Streamlit) — bagian ini untuk kredensial akun pendukung.

### 2.c README / Checklist DVD (Folder root DVD) — Kerangka

1. Identitas: NPM 202243502165 — Falah Fahrurozi; judul TA; prodi Teknik Informatika, Universitas Indraprasta PGRI
2. **Tabel daftar isi 7 folder + status:**

| Folder | Isi | Status (diisi agent) | Cek (user) |
|---|---|---|---|
| 01 SCAN LEMBAR PENGESAHAN DAN PERSETUJUAN | Scan .jpg/.pdf | [USER] | ☐ |
| 02 TUGAS AKHIR | TA FINAL-2D .docx + .pdf | [ISI] | ☐ |
| 03 SOFTWARE PENDUKUNG | Installer (XAMPP, NetBeans, browser, emulator) | [USER] | ☐ |
| 04 SOFTWARE PROGRAM | Project + dashboard.py + launcher | [ISI] | ☐ |
| 05 MANUAL BOOK | Manual book .docx | [ISI] | ☐ |
| 06 USERNAME DAN PASSWORD | Template kredensial .docx | [ISI TEMPLATE, USER ISI NILAI] | ☐ |
| 07 ARTIKEL ILMIAH | Artikel .docx/.pdf + .bib + bukti submit | [SEBAGIAN — USER: screenshot] | ☐ |

3. **Instruksi burn DVD:**
   - Label folder DVD: **`202243502165_FALAH FAHRUROZI`**
   - Gunakan **DVD-RW berlogo UNINDRA** (sesuai pengumuman)
   - Burn sebagai **data DVD** (jangan audio/video); tulis label di badan DVD dengan spidol CD/DVD (label NPM_NAMA)
   - Setelah burn: **verifikasi baca ulang** (read-back) semua folder 01–07 terbuka di komputer lain
   - Simpan salinan cadangan folder DVD di flashdisk/Drive sebelum menyerahkan

### 2.d Catatan Mendeley (Folder 07) — Temuan & Kerangka Panduan

**Temuan audit (fakta dari file):**
- Jurnal final (`Template Penelitian - FINAL.docx` & `Template Umum - FINAL-2D.docx`): **91–99 rujukan Zotero field codes, 0 rujukan Mendeley** → belum memenuhi syarat "daftar pustaka pakai MENDELEY" dari pengumuman.
- Tersedia `ref-falah/ref-falah.bib` (54 KB, export Zotero, 16 file referensi) dan `new-zotero/new-zotero.rdf` → bisa diimpor ke Mendeley.

**Kerangka panduan (akan jadi dokumen di folder 07 atau README):**
1. Buka Mendeley Desktop/Reference Manager → Import `ref-falah.bib` (File → Import → BibTeX)
2. Di Word: install plugin **Mendeley Cite** (References → Mendeley Cite)
3. Hapus field codes Zotero pada dokumen jurnal (Ctrl+A → Ctrl+Shift+F9 pada area sitasi, atau gunakan "Unlink Citations" di Zotero) lalu **insert ulang sitasi via Mendeley Cite**
4. Cek format daftar pustaka sesuai template jurnal (JRAMI Rev 2023 / Template Penelitian)
5. Simpan versi final baru → `.docx` → konversi `.pdf`
6. Setelah submit ke jurnal: **foto/screenshot bukti submit** (email konfirmasi / halaman OJS / status "submitted") → taruh di folder 07 (wajib user)

---

## 3. Rekomendasi Prioritas

### A. Dikerjakan otomatis oleh agent utama (prioritas tinggi, bisa langsung)

1. **Bangun struktur DVD** `DELIVERY/DVD FALAH/202243502165_FALAH FAHRUROZI/` + 7 folder bernomor (01–07) + README/checklist di root DVD.
2. **Salin bahan final ke folder 02, 04, 07** (pilih versi terbaru, jangan salin semua versi lama):
   - 02: `TA FALAH - zotero field codes FINAL - PELUANG KARIR - FINAL-2D.docx` + PDF terkini
   - 04: `dashboard.py`, `src/` (1–6), `requirements.txt`, `data/` (CSV + GeoJSON), `METODOLOGI.md`, launcher `.bat` (python -m streamlit run dashboard.py), `spatial_clustering_pipeline.ipynb`
   - 07: `Jurnal Ilmiah - ... - Template Penelitian - FINAL.docx` (+ PDF), `ref-falah.bib`, catatan Mendeley
3. **Buat Manual Book .docx** (kerangka §2.a) — isi draft penuh dari bahan nyata (walkthrough, naskah demo, README).
4. **Buat template Username & Password .docx** (kerangka §2.b) — nilai kosong.
5. **Buat README/checklist DVD** (§2.c) + **catatan Mendeley** (§2.d).
6. **README isi folder 01 & 03** berisi instruksi persis untuk user (scan → jpg/pdf; daftar installer + link resmi resmi) agar folder tidak kosong saat diserahkan.
7. *(Opsional, diskusikan dulu)* coba build `.exe` PyInstaller untuk `dashboard.py` — **risiko tinggi** (Streamlit exe besar/rapuh); rekomendasi: tawarkan, jangan default.

### B. WAJIB dikerjakan user manual (tidak bisa AI) — instruksi singkat

1. **Scan lembar pengesahan & persetujuan** (folder 01): scan lembar yang **sudah ditandatangani dosen pembimbing** menggunakan scanner/ponsel (≥200 dpi) → simpan sebagai `.jpg` atau `.pdf`, beri nama `PENGESAHAN.jpg` / `PERSETUJUAN.jpg`, taruh di folder 01.
2. **Unduh installer software pendukung** (folder 03): unduh dari situs resmi — browser (Chrome/Edge), XAMPP (`apachefriends.org`), NetBeans (`netbeans.apache.org`), emulator (Android Studio `developer.android.com`) → simpan installer di folder 03.
3. **Screenshot bukti submit artikel** (folder 07): setelah artikel diterima sistem jurnal (OJS/email), screenshot halaman konfirmasi/status "Submitted" + email balasan → simpan `.jpg/.png` di folder 07.
4. **Isi nilai asli Username & Password** (folder 06): buka template, isi akun yang benar-benar dipakai (email, Zotero/Mendeley, GitHub, Streamlit Cloud, dll.).
5. **Sinkronkan daftar pustaka ke Mendeley** (folder 07): impor `ref-falah.bib` ke Mendeley, ganti field codes Zotero dengan Mendeley Cite di Word (panduan §2.d), simpan versi baru.
6. **Konfirmasi versi final TA**: pastikan `TA FINAL-2D` adalah versi yang disetujui dosen pembimbing (bukan versi pra-revisi).
7. **Burn & verifikasi DVD**: burn ke **DVD-RW berlogo UNINDRA** dengan label `202243502165_FALAH FAHRUROZI`, lalu cek semua folder terbaca di komputer lain.

### Urutan eksekusi yang disarankan
1. Agent: struktur + salin + template (A1–A6) → 2. User: isi/scan/unduh/screenshot (B1–B4) → 3. User: Mendeley + konfirmasi versi (B5–B6) → 4. User: burn + verifikasi (B7). Item B yang belum selesai tidak memblokir pengumpulan struktur awal; folder tetap ada dengan README instruksi.
