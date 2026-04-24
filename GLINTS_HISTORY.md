# 🧪 Catatan Eksperimen: Percobaan Dataset Glints

Dokumen ini mencatat percobaan awal akuisisi data menggunakan platform Glints sebelum akhirnya diputuskan untuk menggunakan Jobstreet sebagai sumber data utama skripsi.

## 1. Eksperimen Awal (Glints API)
- **Tujuan**: Mengambil data lowongan yang memiliki koordinat Latitude/Longitude asli.
- **Masalah**: Proteksi firewall Glints (Cloudflare/WAF) sangat ketat terhadap aktivitas scraping otomatis.
- **Hasil**: Meskipun berhasil melakukan bypass awal menggunakan `curl_cffi`, Glints memberlakukan limitasi pada query luas (seperti Pulau Jawa secara utuh) yang menyebabkan data yang didapat tidak saturasi (hanya beberapa ratus baris).

## 2. Alasan Pivot (Perubahan Strategi) ke Jobstreet
- **Volume Data**: Jobstreet menyediakan volume lowongan yang jauh lebih besar untuk wilayah Indonesia (~20.000+ lowongan unik).
- **Aksesibilitas**: Melalui Reverse Engineering pada endpoint GraphQL Jobstreet, data bisa diambil secara lebih masif per wilayah Kabupaten/Kota.
- **Konsistensi**: Parameter pencarian di Jobstreet lebih selaras dengan pembagian administratif (Kabupaten/Kota) yang digunakan oleh BPS, sehingga memudahkan proses validasi.

## 3. Kesimpulan Eksperimen
Meskipun Glints memiliki fitur koordinat asli, keterbatasan jumlah data menjadikannya tidak ideal untuk analisis klastering skala besar. Oleh karena itu, diputuskan untuk menggunakan **Jobstreet** dengan tambahan tahap **Geocoding** manual (Tahap 2.2) untuk mendapatkan koordinat centroid wilayah.
