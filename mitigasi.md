# 🛡️ Mitigasi Bias & Keterbatasan Data (Thesis Reference)

Dokumen ini mendokumentasikan analisis kritis terhadap keterwakilan (*representativeness*) dataset lowongan kerja daring (Jobstreet) yang dibandingkan dengan data makro Angkatan Kerja BPS. Dokumen ini dapat digunakan secara langsung sebagai referensi penulisan **Bab Batasan Penelitian** dan **Saran** pada naskah skripsi.

---

## 1. Analisis Kritis Keterbatasan Data (Data Bias)

Meskipun sistem berhasil mengolah dan mengklasterkan **18.182 lowongan kerja**, data ini memiliki beberapa bentuk bias yang harus diakui secara ilmiah:

### a. Bias Sektor Formal (Informality Bias)
- **Kondisi**: Portal lowongan kerja online (Jobstreet) mayoritas mempublikasikan pekerjaan sektor formal, profesional, korporasi, dan kerah putih (*white-collar* seperti IT, Administrasi, Finansial, dan Sales).
- **Implikasi**: Sektor ekonomi informal (seperti pertanian, perkebunan, UMKM mikro, buruh harian, dan perdagangan tradisional) tidak terwakili dalam dataset ini, padahal sektor-sektor tersebut menyerap sebagian besar angkatan kerja riil di Pulau Jawa.

### b. Kesenjangan Digital Geografis (Digital Divide Bias)
- **Kondisi**: Perusahaan-perusahaan di kawasan metropolitan (Jabodetabek, Surabaya Raya, dan Bandung Raya) memiliki tingkat adopsi digital yang jauh lebih tinggi untuk mengiklankan lowongan secara daring.
- **Implikasi**: Terjadi akumulasi lowongan kerja yang sangat ekstrim di kota-kota besar pada peta visualisasi. Daerah pedesaan (*rural area*) terlihat memiliki peluang yang sangat rendah atau kosong, yang mencerminkan bias adopsi teknologi portal kerja online, bukan ketiadaan aktivitas ekonomi riil secara offline.

### c. Batasan Temporal (Snapshot Bias)
- **Kondisi**: Data lowongan kerja merupakan *snapshot* (potret kondisi aktif) pada periode pengambilan data (April 2026), sedangkan data kependudukan BPS merupakan hasil survei tahunan (Sakernas 2025).

---

## 2. Rumusan Argumentasi Akademis (Untuk Sidang Skripsi)

Saat dosen penguji mempertanyakan keabsahan *Opportunity Index* yang membandingkan 18 ribu loker dengan jutaan angkatan kerja BPS, Anda dapat menggunakan argumentasi berikut:

1. **Konsep Proxy Data**:
   > *"Penelitian ini tidak berasumsi bahwa portal daring mencakup seluruh pasar kerja di Indonesia. Lowongan dari portal kerja daring digunakan sebagai **proxy (pendekatan/representasi)** untuk menganalisis dinamika **pasar kerja formal berbasis digital** di Pulau Jawa."*
2. **Definisi Konseptual Indeks**:
   > *"Skor 'Opportunity Index' dalam penelitian ini sebaiknya didefinisikan sebagai **'Rasio ketersediaan loker formal daring per satuan angkatan kerja wilayah'**. Indeks ini berguna untuk menunjukkan tingkat digitalisasi dan daya tarik ekonomi modern antar-wilayah secara relatif, bukan peluang kerja total secara mutlak."*

---

## 3. Rekomendasi Penulisan Naskah TA

### A. Draf untuk Bab I / Bab III (Batasan Masalah)
> *"Ruang lingkup ketersediaan peluang karir dalam penelitian ini dibatasi pada lowongan kerja sektor formal yang terpublikasikan secara daring melalui portal Jobstreet pada periode pengambilan data (April 2026)."*

### B. Draf untuk Bab V (Saran untuk Penelitian Selanjutnya)
> *"1. Untuk mengurangi bias platform, penelitian selanjutnya disarankan menggunakan pendekatan multi-source (OSINT) dengan mengintegrasikan portal kerja lain seperti LinkedIn, Glints, dan Kalibrr menggunakan data pipeline terstandardisasi."*
>
> *"2. Disarankan untuk berkolaborasi dengan instansi pemerintah terkait (Disnaker) guna mengintegrasikan data lowongan kerja offline (*low-skilled/informal jobs*) agar peta persebaran peluang kerja dapat menangkap realitas ekonomi secara menyeluruh."*
