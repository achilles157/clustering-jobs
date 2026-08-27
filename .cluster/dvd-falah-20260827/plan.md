# Plan: DVD FALAH — Persiapan DVD Tugas Akhir (7 Folder)

## Konteks
- User: Falah Fahrurozi (NPM 202243502165), TA "Persebaran Peluang Karir Berdasarkan Jumlah Angkatan Kerja menggunakan Density Based Clustering (DBSCAN)"
- Aturan pengumuman UNINDRA (dari gambar): DVD wajib berisi 7 folder bernomor 01-07; penamaan folder DVD = NPM_NAMA
- Tujuan: buat folder "DVD FALAH" berisi 7 folder + isi semampu yang tersedia; item yang harus user tambah sendiri dibiarkan + didokumentasikan

## 7 Folder (sesuai pengumuman)
1. 01 - SCAN LEMBAR PENGESAHAN DAN PERSETUJUAN (.JPG/.PDF) — scan pengesahan + persetujuan pembimbing
2. 02 - TUGAS AKHIR (.DOC/.DOCX) — TA bab 1-5 + cover, pernyataan, abstrak s/d lampiran
3. 03 - SOFTWARE PENDUKUNG — browser, XAMPP, NetBeans, emulator, dll
4. 04 - SOFTWARE PROGRAM — project TA + executable (.EXE/.JAR/.APP)
5. 05 - MANUAL BOOK (.DOC/.DOCX) — langkah penggunaan program
6. 06 - USERNAME DAN PASSWORD (.DOC/.DOCX) — kredensial aplikasi
7. 07 - ARTIKEL ILMIAH (.DOC/.DOCX) — artikel + daftar pustaka Mendeley + screenshot bukti submit

## Tahapan
1. **S1 Validasi**: gambar dibaca (7 folder + aturan NPM_NAMA) ✓; workspace diinventarisasi singkat ✓
2. **S2-S3 Dispatch**: 
   - Subagent A "Inventaris Bahan DVD": scan seluruh workspace, petakan file yang tersedia ke 7 folder target (path, ukuran, tanggal, rekomendasi salin) → subagent_01_inventaris.md
   - Subagent B "Pemeriksa Gap & Template": bandingkan aturan 7 folder vs bahan; daftar wajib-isi-user; rancang template dokumen yang perlu dibuat → subagent_02_gap.md
3. **S4 Review**: baca hasil keduanya, tentukan pemetaan final + daftar gap
4. **S5 Delivery**: bangun struktur `DELIVERY/DVD FALAH/` + 7 folder; salin file yang tersedia; buat template (Manual Book, Username-Password, README/checklist); laporan final

## Keputusan Asumsi
- NPM 202243502165, nama "Falah Fahrurozi" → folder DVD root bernama `202243502165_FALAH FAHRUROZI` (folder luar diberi nama "DVD FALAH" sebagai wadah sesuai permintaan user)
- Software Pendukung (installer besar: XAMPP, NetBeans, browser) TIDAK diunduh (lisensi/ukuran/koneksi) → biarkan folder + README penjelasan; user isi sendiri
- Scan lembar pengesahan/persetujuan: hanya user punya fisiknya → folder + README
- Screenshot bukti submit artikel: hanya user punya → folder + README
