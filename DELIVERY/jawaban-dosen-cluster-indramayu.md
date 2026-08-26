# Jawaban Pertanyaan Dosen — Mengapa Cluster 1 Sampai ke Indramayu?

Referensi defensif untuk sidang. Semua angka dihitung ulang dari `data/java_job_market_final_analysis.csv` (116 wilayah ber-lowongan), `DBSCAN(eps=0.08, min_samples=3)` pada `Latitude/Longitude` ter-StandardScaler.

## Inti konsep: eps BUKAN radius klaster

DBSCAN menumbuhkan klaster lewat **density-reachability (rantai kepadatan)**:
- Titik A disebut **core point** jika punya ≥ `min_samples` (=3) tetangga dalam radius `eps`.
- Titik **border** = punya <3 tetangga, tapi masih dalam eps dari sebuah core point.
- Klaster = semua titik yang **saling tersambung melalui core point** (transitif).

Akibatnya klaster bisa **memanjang sejauh rantainya**, bukan dibatasi radius eps. eps=0.08 hanya membatasi **tiap lompatan lokal**, bukan panjang total klaster.

## Konversi eps ke km (penting)

StandardScaler men-z-score tiap sumbu: `std_lat ≈ 0,60° (≈66,6 km)`, `std_lon ≈ 2,27° (≈251,6 km)`.
- eps=0.08 ⇒ ± **27 km (arah utara–selatan)** dan ± **100 km (arah timur–barat)**.
- Karena pulau Jawa memanjang timur–barat, lingkungan efektifnya "lonjong" — wajar untuk rantai koridor Pantura/Trans-Jawa.

## Rantai nyata ke Indramayu (semua lompatan ≤ 0.40)

| Lompatan | Jarak z-score | ≤ eps? |
|---|---|---|
| Jakarta Timur → Kota Bekasi | 0.068 | ✅ |
| Kota Bekasi → Karawang | 0.198 | ✅ |
| Karawang → Kota Jakarta Timur | 0.241 | ✅ |
| (Kota Bogor →) Bogor → Purwakarta | 0.192 | ✅ |
| Bogor → Subang | 0.332 | ✅ |
| Purwakarta → Subang | 0.213 | ✅ |
| Subang → Indramayu | 0.216 | ✅ |

**Indramayu = border point** (hanya **1** tetangga, yaitu Subang). Jadi Indramayu **bukan pusat aglomerasi mandiri** — ia *ekor* yang menempel ke Subang (core), yang terhubung ke inti Jabodetabek via Purwakarta–Bogor–Bekasi.

## Mengapa berhenti di Indramayu

| Lompatan | Jarak | Akibat |
|---|---|---|
| Indramayu → Kota Cirebon | 0.484 (>0.40) | rantai PUTUS |
| Indramayu → Cirebon | 0.547 | PUTUS |
| Indramayu → Majalengka | 0.611 | PUTUS |

Cirebon (core, 5 tetangga) tersambung ke mainland → masuk Cluster 0, bukan Cluster 1.

## Mengapa Surabaya/Bandung/Semarang TIDAK jadi klaster sendiri

Mereka justru **satu klaster (Cluster 0)** karena tersambung rantai kontinu di mainland:
Bandung → Sumedang → Cirebon → … → Semarang → … → Surakarta → … → Surabaya (tanpa gap ≥ eps).
DBSCAN **tidak memecah berdasarkan "kota besar"**, tapi berdasarkan **kesinambungan kepadatan**. Koridor Trans-Jawa/pantura padat-merata ⇒ seluruhnya melebur jadi satu klaster memanjang.

## Mengapa Cluster 1 (Jakarta) terpisah dari Cluster 0 (mainland)

Ada **gap kepadatan** di zona pegunungan Priangan (lowongan rendah):

| Pasangan batas | Jarak | 
|---|---|
| Purwakarta (C1) → Sumedang (C0) | **0.445** (>0.40) ← gap terpendek |
| Purwakarta → Bandung Barat | 0.511 |
| Bogor → Cianjur | 0.849 |

Karena gap terpendek (0.445) tetap > eps (0.40), tidak ada jembatan yang menyambung Jakarta ke mainland ⇒ keduanya jadi dua klaster terpisah. Ini bukti DBSCAN justru **berhasil** memisahkan aglomerasi yang terpisah oleh sabuk pegunungan.

## Jawaban siap pakai (parafrase bebas)

"eps=0.08 bukan batas jarak maksimum klaster, melainkan radius ketetanggaan lokal. DBSCAN menumbuhkan klaster melalui rantai kepadatan (density-reachability): dua titik terhubung bila ada rantai titik yang tiap lompatannya dalam eps. Indramayu masuk karena tersambung rantai kontinu Jakarta–Bekasi–Karawang–Purwakarta/Bogor–Subang–Indramayu (tiap lompatan ≤ 0.40), dan Indramayu hanya border point — ekor aglomerasi, bukan pusat mandiri (volumenya 43 vs Jakarta Barat 7.498). Rantai berhenti di Indramayu karena jarak ke Cirebon 0.484 > eps, dan Cirebon tersambung ke koridor mainland. Sebaliknya Surabaya–Semarang–Bandung tidak membentuk klaster terpisah karena mereka justru saling tersambung kontinu di mainland sehingga melebur jadi satu klaster (Cluster 0). Jakarta terpisah dari mainland karena ada sabuk pegunungan Priangan yang memutus rantai (gap terpendek 0.445 > eps)."
