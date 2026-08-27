# LAMPIRAN: Kode Dashboard Interaktif (Use Case Only)
**File:** `dashboard.py`  
**Deskripsi:** Dashboard interaktif untuk analisis spasial hub kerja Pulau Jawa  
**Total Baris Kode Use Case:** ~420 baris (tanpa CSS)  
**Framework:** Streamlit + Plotly

---

## 📑 DAFTAR ISI KODE

1. [Import & Konfigurasi](#section-1)
2. [Fungsi Loading Data](#section-2)
3. [Sidebar: Filter & Kontrol](#section-3)
4. [Header & Tab Navigation](#section-4)
5. [Tab 1: Filter & Parameter (UC1)](#section-5)
6. [Tab 2: Peta Klaster Spasial (UC2)](#section-6)
7. [Tab 3: Heatmap Peluang (UC3)](#section-7)
8. [Tab 4: Statistik Efisiensi (UC4)](#section-8)
9. [Tab 5: Laporan Eksekutif (UC5)](#section-9)
10. [Footer](#section-10)

---

<a name="section-1"></a>
## 1️⃣ IMPORT & KONFIGURASI

**Fungsi:** Import library dan setup konfigurasi halaman Streamlit

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import numpy as np

# Set Page Config
st.set_page_config(
    page_title="Analisis Hub Kerja Jawa | Thesis Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

**Penjelasan:**
- Import Streamlit untuk framework web app
- Plotly untuk visualisasi interaktif (scatter map, choropleth)
- Pandas & Numpy untuk manipulasi data
- `set_page_config` untuk mengatur judul, icon, dan layout wide

**Catatan:** Kode CSS styling (130 baris) tidak dilampirkan karena bukan bagian dari logic interaksi user.

---

<a name="section-2"></a>
## 2️⃣ FUNGSI LOADING DATA

**Fungsi:** Cache data loading untuk performa optimal

```python
@st.cache_data
def load_data():
    file_path = os.path.join('data', 'java_job_market_hubs_final.csv')
    if not os.path.exists(file_path):
        file_path = os.path.join('data', 'java_job_market_final_analysis.csv')
    
    df = pd.read_csv(file_path)
    # Pembersihan data & Penanganan NaN
    df['opportunity_index'] = pd.to_numeric(df['opportunity_index'], errors='coerce').replace([np.inf, -np.inf], 0).fillna(0)
    df['competitive_index'] = pd.to_numeric(df['competitive_index'], errors='coerce').fillna(0)
    df['labor_force_num'] = pd.to_numeric(df['labor_force_num'], errors='coerce').fillna(0)
    df['job_volume'] = pd.to_numeric(df['job_volume'], errors='coerce').fillna(0)
    df['cluster_id'] = df['cluster_id'].astype(int) if 'cluster_id' in df.columns else -1
    df['size_for_map'] = df['job_volume'] + 5
    
    # Klasifikasi detail untuk visualisasi peta
    def classify_cluster(row):
        cid = int(row['cluster_id'])
        if cid == -1:
            return "Cluster -1: Isolated Red Zone (Terpencil/Sepi)"
        elif cid == 0:
            return "Cluster 0: Java Mainland Hub (Aglomerasi Utama)"
        elif cid == 1:
            return "Cluster 1: Jabodetabek & Koridor Barat (Aglomerasi Metropolitan)"
        else:
            return f"Cluster {cid}"
            
    df['cluster_display'] = df.apply(classify_cluster, axis=1)
    return df

@st.cache_data
def load_geojson():
    file_path = os.path.join('data', 'java_regencies.geojson')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            g = json.load(f)
            
            # WORKAROUND: Hapus feature dengan geometry: null
            valid_features = []
            for feature in g['features']:
                if feature.get('geometry') is not None:
                    feature['id'] = feature['properties']['clean_name']
                    valid_features.append(feature)
            g['features'] = valid_features
            
            return g
    return None

@st.cache_data
def load_raw_jobs():
    file_path = os.path.join('data', 'integrated_job_market_java_v2.csv')
    if os.path.exists(file_path):
        df_raw = pd.read_csv(file_path)
        return df_raw[['title', 'company', 'location', 'matched_regency', 'Provinsi']]
    return pd.DataFrame()

df = load_data()
geojson = load_geojson()
```

**Penjelasan:**
- `@st.cache_data` untuk caching (tidak load ulang setiap interaction)
- `load_data()`: Load CSV utama + cleaning NaN + klasifikasi cluster
- `load_geojson()`: Load batas wilayah + fix geometry null
- `load_raw_jobs()`: Load data lowongan mentah untuk tabel detail

---

<a name="section-3"></a>
## 3️⃣ SIDEBAR: FILTER & KONTROL

**Fungsi:** Sidebar dengan filter provinsi, kabupaten/kota, dan tombol Apply

```python
st.sidebar.image("https://img.icons8.com/isometric/100/city.png", width=80)
st.sidebar.title("Analisis Hub Kerja")
st.sidebar.markdown("*Skripsi Falah - Pulau Jawa*")
st.sidebar.divider()

# Filter Provinsi & Kabupaten/Kota
provinces = ["Semua Provinsi"] + sorted(df['Provinsi'].unique())
selected_prov = st.sidebar.selectbox("📍 Pilih Provinsi", provinces, index=0)

if selected_prov != "Semua Provinsi":
    filtered_cities = sorted(df[df['Provinsi'] == selected_prov]['matched_regency'].unique())
else:
    filtered_cities = sorted(df['matched_regency'].unique())

selected_city = st.sidebar.selectbox(
    "📍 Pilih Kabupaten/Kota", 
    filtered_cities,
    index=0
)

# Tombol Apply Filters
apply_button = st.sidebar.button("Apply Filters", type="primary")

# Session State Management
if 'applied_city' not in st.session_state:
    st.session_state.applied_city = selected_city
if 'applied_prov' not in st.session_state:
    st.session_state.applied_prov = selected_prov

# Update session state saat tombol diklik
if apply_button:
    st.session_state.applied_city = selected_city
    st.session_state.applied_prov = selected_prov

# Ambil data wilayah terpilih
city_info = df[df['matched_regency'] == st.session_state.applied_city].iloc[0]

st.sidebar.subheader("Konteks Wilayah (Terpilih)")
st.sidebar.write(f"**Provinsi:** {city_info['Provinsi']}")
st.sidebar.write(f"**Status:** {city_info['prosperity_status']}")
if 'cluster_display' in city_info:
    st.sidebar.info(f"**Klasifikasi:** {city_info['cluster_display']}")

st.sidebar.divider()
st.sidebar.caption("v1.5 • DBSCAN Pure Spatial (eps=0.08)")
```

**Penjelasan:**
- Filter bertingkat: Provinsi → Kabupaten/Kota
- Session state untuk menyimpan pilihan user
- Tombol "Apply Filters" untuk konfirmasi eksplisit
- Info konteks wilayah terpilih di sidebar

---

<a name="section-4"></a>
## 4️⃣ HEADER & TAB NAVIGATION

**Fungsi:** Judul halaman dan 5 tab use case

```python
st.title("Analisis Spasial Hub & Peluang Kerja")
st.markdown(f"Wawasan visual untuk pasar kerja di <span class='highlight'>{st.session_state.applied_city}</span>", unsafe_allow_html=True)

# Tab Dashboard (5 Use Cases)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Filter & Parameter",
    "📍 Klaster Ekonomi", 
    "🔥 Heatmap Peluang", 
    "📈 Statistik Efisiensi",
    "📝 Laporan Eksekutif"
])
```

**Penjelasan:**
- Dynamic title dengan nama kota terpilih
- 5 tabs untuk navigasi antar use case

---

<a name="section-5"></a>
## 5️⃣ TAB 1: FILTER & PARAMETER (UC1)

**Fungsi:** Menampilkan parameter global dan tabel data mentah lowongan

```python
with tab1:
    st.subheader("Filter Wilayah & Parameter")
    st.markdown(f"Menampilkan data untuk: **{st.session_state.applied_prov}** - **{st.session_state.applied_city}**")
    
    # Global Parameter Summary
    st.markdown("### 📊 Global Parameter Summary")
    sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
    with sum_col1:
        st.metric("Volume Lowongan", f"{int(city_info['job_volume'])} Posisi")
    with sum_col2:
        val = float(city_info['labor_force_num'])
        st.metric("Angkatan Kerja", f"{int(val):,}" if val > 0 else "Data Kosong")
    with sum_col3:
        st.metric("Indeks Peluang", f"{city_info['opportunity_index']:.5f}")
    with sum_col4:
        comp_idx = city_info.get('competitive_index', 0)
        st.metric("Indeks Kompetitif", f"{comp_idx:.2f}/3.0")
        
    # Raw Data Table
    st.markdown("### 📋 Raw Data Table (Daftar Lowongan Pekerjaan)")
    df_raw = load_raw_jobs()
    if not df_raw.empty:
        # Filter raw data sesuai wilayah
        if st.session_state.applied_prov != "Semua Provinsi":
            filtered_raw = df_raw[(df_raw['Provinsi'] == st.session_state.applied_prov) & 
                                 (df_raw['matched_regency'] == st.session_state.applied_city)]
        else:
            filtered_raw = df_raw[df_raw['matched_regency'] == st.session_state.applied_city]
            
        st.markdown(f"Menampilkan **{len(filtered_raw)}** data lowongan untuk **{st.session_state.applied_city}**")
        
        display_df = filtered_raw[['title', 'company', 'location']].copy()
        display_df.columns = ['Judul Pekerjaan', 'Perusahaan', 'Lokasi Asli']
        st.dataframe(display_df, use_container_width=True, height=350)
    else:
        st.warning("Data mentah lowongan pekerjaan tidak tersedia.")
```

**Penjelasan:**
- 4 metric cards: Volume Lowongan, Angkatan Kerja, Indeks Peluang, Indeks Kompetitif
- Tabel data lowongan yang difilter sesuai wilayah terpilih
- Dynamic counter jumlah lowongan

---

<a name="section-6"></a>
## 6️⃣ TAB 2: PETA KLASTER SPASIAL (UC2)

**Fungsi:** Visualisasi peta interaktif hasil clustering DBSCAN

```python
with tab2:
    st.subheader("Peta Klaster Spasial (Hasil DBSCAN)")
    st.markdown("Peta ini mengidentifikasi 'Hub Ekonomi' berdasarkan kepadatan lowongan dan kedekatan geografis.")
    
    # Scatter Map dengan Plotly
    fig1 = px.scatter_map(
        df, 
        lat="Latitude", 
        lon="Longitude", 
        color="cluster_display",
        size="size_for_map",
        size_max=40,
        hover_name="matched_regency",
        hover_data={"Latitude":False, "Longitude":False, 
                   "cluster_display":True, "job_volume":True, "size_for_map":False},
        zoom=6,
        height=600,
        color_discrete_map={
            "Cluster 0: Java Mainland Hub (Aglomerasi Utama)": "#3A86FF",
            "Cluster 1: Jabodetabek & Koridor Barat (Aglomerasi Metropolitan)": "#00F5D4",
            "Cluster -1: Isolated Red Zone (Terpencil/Sepi)": "#8E9AA6"
        },
        map_style="carto-darkmatter",
        template="plotly_dark",
        labels={"cluster_display": "Klasifikasi Wilayah"}
    )
    
    # Marker lokasi terpilih user
    fig1.add_trace(go.Scattermap(
        lat=[city_info['Latitude']],
        lon=[city_info['Longitude']],
        mode='markers',
        marker=go.scattermap.Marker(size=25, color='#FFD700', opacity=0.9),
        name='Lokasi Target',
        text=[st.session_state.applied_city]
    ))
    
    fig1.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.08)",
            bordercolor="rgba(255,255,255,0.25)",
            borderwidth=1,
            font=dict(size=12, color="#FFFFFF")
        )
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Ringkasan komposisi cluster
    c0 = df[df['cluster_id'] == 0]
    c1 = df[df['cluster_id'] == 1]
    cn = df[df['cluster_id'] == -1]
    comp_col1, comp_col2, comp_col3 = st.columns(3)
    with comp_col1:
        st.metric("Cluster 0 — Mainland Java", f"{len(c0)} wilayah", 
                 f"{int(c0['job_volume'].sum()):,} lowongan")
    with comp_col2:
        st.metric("Cluster 1 — Jabodetabek", f"{len(c1)} wilayah", 
                 f"{int(c1['job_volume'].sum()):,} lowongan")
    with comp_col3:
        st.metric("Cluster -1 — Isolated Zone", f"{len(cn)} wilayah", 
                 f"{int(cn['job_volume'].sum()):,} lowongan")
    
    st.info("""
    **💡 Catatan Analisis DBSCAN:** 
    * **Cluster 0 (Biru):** Aglomerasi pasar kerja koridor mainland Pulau Jawa — Surabaya, Bandung, Semarang, GKS, Solo.
    * **Cluster 1 (Hijau Toska):** Aglomerasi metropolitan Jabodetabek & koridor industri Banten–Jawa Barat (Serang, Karawang, Cilegon).
    * **Cluster -1 (Abu-Abu):** Isolated Red Zone — wilayah terpencil dengan volume lowongan rendah (Madura, Pacitan, Lebak).
    * Ukuran lingkaran = volume lowongan absolut (+ offset 5 agar wilayah 0 lowongan tetap terlihat).
    """)
```

**Penjelasan:**
- Plotly scatter_map dengan color mapping per cluster
- Marker kuning untuk lokasi yang dipilih user
- Legend horizontal responsive
- 3 metric cards ringkasan cluster
- Info box interpretasi DBSCAN

---

<a name="section-7"></a>
## 7️⃣ TAB 3: HEATMAP PELUANG (UC3)

**Fungsi:** Choropleth map untuk visualisasi Opportunity Index

```python
with tab3:
    st.subheader("Heatmap Peluang Kerja (Choropleth)")
    st.markdown(r"Visualisasi **'Lautan Peluang'** (Hijau) vs **'Zona Merah'** (Merah).")
    st.latex(r"Indeks\_Peluang = \frac{Volume\_Pekerjaan}{Angkatan\_Kerja\_Aktif}")
    
    if geojson:
        fig2 = px.choropleth_map(
            df,
            geojson=geojson,
            locations="matched_regency",
            featureidkey="id",
            color="opportunity_index",
            color_continuous_scale="RdYlGn",
            range_color=(df['opportunity_index'].min(), df['opportunity_index'].quantile(0.9)), 
            map_style="carto-darkmatter",
            zoom=6,
            center={"lat": city_info['Latitude'], "lon": city_info['Longitude']},
            opacity=0.7,
            labels={'opportunity_index': 'Indeks Peluang'},
            height=600
        )
        fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig2, use_container_width=True)
        
        st.info("""
        **💡 Panduan Interpretasi Heatmap:**
        * **Hijau (Lautan Peluang):** Wilayah dengan rasio lowongan tinggi per angkatan kerja. Direkomendasikan untuk pencari kerja.
        * **Merah (Zona Merah):** Wilayah padat persaingan — volume kesempatan kerja tipis vs jumlah angkatan kerja (indikasi kejenuhan). 
        """)
    else:
        st.warning("File GeoJSON tidak ditemukan. Menampilkan visualisasi alternatif...")
        fig_alt = px.density_map(
            df, lat='Latitude', lon='Longitude', z='opportunity_index', 
            radius=30, map_style="carto-darkmatter", height=600,
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig_alt, use_container_width=True)
```

**Penjelasan:**
- Choropleth map dengan GeoJSON boundaries
- Color scale RdYlGn (Red-Yellow-Green)
- Formula LaTeX untuk Indeks Peluang
- Fallback ke density_map jika GeoJSON tidak tersedia

---

<a name="section-8"></a>
## 8️⃣ TAB 4: STATISTIK EFISIENSI (UC4)

**Fungsi:** Visualisasi korelasi dan metrik evaluasi model DBSCAN

```python
with tab4:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("a. Efisiensi Pasar Kerja")
        st.markdown("Evaluasi statistik ketersediaan kerja terhadap angkatan kerja.")
        fig4a = px.scatter(
            df, x="labor_force_num", y="job_volume",
            trendline="ols", trendline_color_override="#00A6FB",
            hover_name="matched_regency", color="opportunity_index",
            color_continuous_scale="Viridis",
            labels={"labor_force_num": "Angkatan Kerja (BPS)", "job_volume": "Volume Lowongan"},
            template="plotly_dark", height=500
        )
        st.plotly_chart(fig4a, use_container_width=True)

    with col_b:
        st.subheader("b. Distribusi Indeks Kompetitif")
        st.markdown("Menunjukkan tingkat kualifikasi rata-rata per wilayah.")
        fig4b = px.bar(
            df.sort_values('competitive_index', ascending=False).head(15), 
            x='competitive_index', y='matched_regency',
            orientation='h', color='competitive_index',
            color_continuous_scale="Blues",
            labels={'competitive_index': 'Skor Kualifikasi', 'matched_regency': 'Wilayah'},
            template="plotly_dark", height=500
        )
        st.plotly_chart(fig4b, use_container_width=True)
    
    st.info("""
    **💡 Catatan Analisis:** 
    * Plot kiri: Hubungan linier penciptaan loker vs demografi. Wilayah di atas trendline = performa penciptaan kerja abnormal (positif).
    * Barchart kanan: Indeks ≥2.5 = posisi manajerial elit. Skor ~1.0-1.5 = pasar kerja kerah biru/operasional.
    """)
    
    st.divider()
    st.subheader("c. Metrik Evaluasi Model Spasial (DBSCAN)")
    st.markdown("Evaluasi kualitas clustering (eksklusi noise -1).")
    
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric(
            label="Silhouette Score (Cohesion)", 
            value="0.4649", 
            help="Rentang -1 s/d +1. Mengukur kedekatan objek dengan klasternya sendiri vs klaster lain."
        )
        st.caption("ℹ️ *Score 0.4649 (moderat-baik): aglomerasi Jawa memanjang horizontal mengikuti Trans-Jawa, bukan spherical — DBSCAN lebih tepat vs K-Means.*")
        
    with m_col2:
        st.metric(
            label="Davies-Bouldin Index (DBI - Separasi)", 
            value="0.5294", 
            help="Nilai mendekati 0 semakin baik. Mengukur overlap antar klaster."
        )
        st.caption("ℹ️ *DBI 0.5294 (<1.0) = pemisahan baik — Cluster 0 (Mainland) dan Cluster 1 (Jabodetabek) tidak overlap spasial.*")
```

**Penjelasan:**
- 2 kolom: Scatter plot (efisiensi) + Bar chart (kompetitif)
- Trendline OLS untuk korelasi
- Metrik evaluasi: Silhouette Score & Davies-Bouldin Index

---

<a name="section-9"></a>
## 9️⃣ TAB 5: LAPORAN EKSEKUTIF (UC5)

**Fungsi:** Generate narasi otomatis dan ranking wilayah

```python
with tab5:
    st.subheader(f"Laporan Analisis Wilayah: {st.session_state.applied_city}")
    st.markdown("Ringkasan temuan otomatis dari Machine Learning dan Indeks Peluang.")
    
    # Kalkulasi peringkat (Eksklusi wilayah 0 lowongan)
    df_active = df[df['job_volume'] > 0].copy()
    df_active_sorted = df_active.sort_values(by='opportunity_index', ascending=False).reset_index(drop=True)
    df_sorted = df.sort_values(by='opportunity_index', ascending=False).reset_index(drop=True)
    
    has_jobs = int(city_info['job_volume']) > 0
    
    if has_jobs:
        rank = df_active_sorted[df_active_sorted['matched_regency'] == st.session_state.applied_city].index[0] + 1
        total_active = len(df_active_sorted)
        is_zona_merah = city_info['prosperity_status'] == "Zona Merah"
        
        if is_zona_merah:
            conclusion = f"Wilayah ini mengalami defisit lapangan kerja nyata (**Peringkat {rank}/{total_active}**). Secara absolut pasar kerja formal sangat terbatas ({int(city_info['job_volume'])} posisi)."
            recom_val = "Berisiko"
            comp_val = "Sengit"
        else:
            if rank <= 10:
                conclusion = f"Wilayah ini masuk **Top 10 (Peringkat {rank}/{total_active})** kawasan berekspansi tinggi. Direkomendasikan untuk pencari kerja."
                recom_val = "Sangat Layak"
                comp_val = "Longgar"
            elif rank >= (total_active - 15):
                conclusion = f"Wilayah ini mengalami defisit gawat darurat (**Peringkat {rank}/{total_active}**). Lapangan formal sangat sedikit."
                recom_val = "Berisiko"
                comp_val = "Sengit"
            else:
                conclusion = f"Posisi menengah-stabil (**Peringkat {rank}/{total_active}**). Pasar kerja organik, perputaran karyawan standar."
                recom_val = "Netral"
                comp_val = "Seimbang"
    else:
        rank = "Tidak Terperingkat"
        total_active = len(df_active_sorted)
        conclusion = "Wilayah ini tidak memiliki lowongan kerja formal aktif (0 Lowongan). Defisit lapangan kerja mutlak."
        recom_val = "Berisiko"
        comp_val = "Sangat Sengit"

    col_L1, col_L2 = st.columns([2, 1])
    
    with col_L1:
        st.markdown("#### Narasi Kesimpulan")
        st.write(f"Secara makro-ekonomi, **{st.session_state.applied_city}** diidentifikasi DBSCAN sebagai **{city_info['cluster_display']}** bertaraf {city_info['prosperity_status']}.")
        st.write(f"Angkatan Kerja: **{int(city_info['labor_force_num']):,}** orang. Lowongan tersedia: **{int(city_info['job_volume'])}** posisi. Indeks peluang: **{city_info['opportunity_index']:.5f}**.")
        st.write(conclusion)
            
    with col_L2:
        st.markdown("#### Penilaian Kritis")
        st.metric(label="Rekomendasi", value=recom_val)
        st.metric(label="Persaingan", value=comp_val)
        
    st.divider()
    st.markdown("#### Raw Data Profil")
    st.dataframe(pd.DataFrame(city_info).T, use_container_width=True)

    st.divider()
    st.subheader("Peringkat Aglomerasi & Peluang Kerja Pulau Jawa")
    
    list_col1, list_col2 = st.columns(2)
    
    with list_col1:
        st.markdown("#### 🌟 Top 5 Lautan Peluang")
        top_opportunities = df_sorted[['matched_regency', 'Provinsi', 'job_volume', 'opportunity_index']].head(5)
        top_opportunities.columns = ['Kabupaten/Kota', 'Provinsi', 'Volume Lowongan', 'Indeks Peluang']
        st.dataframe(top_opportunities, use_container_width=True, hide_index=True)
        st.caption("ℹ️ *Wilayah dengan rasio penyerapan kerja tertinggi.*")
        
    with list_col2:
        st.markdown("#### 🚨 Top 5 Zona Merah")
        bottom_opportunities = df_sorted[['matched_regency', 'Provinsi', 'job_volume', 'opportunity_index']].tail(5).iloc[::-1]
        bottom_opportunities.columns = ['Kabupaten/Kota', 'Provinsi', 'Volume Lowongan', 'Indeks Peluang']
        st.dataframe(bottom_opportunities, use_container_width=True, hide_index=True)
        st.caption("ℹ️ *Wilayah dengan tingkat persaingan terpadat.*")
```

**Penjelasan:**
- Logic ranking otomatis (exclude wilayah 0 lowongan)
- Narasi kesimpulan dinamis berdasarkan ranking
- Metric rekomendasi & persaingan
- Top 5 dan Bottom 5 wilayah

---

<a name="section-10"></a>
## 🔟 FOOTER

**Fungsi:** Credit dan sumber data

```python
st.divider()
f_col1, f_col2 = st.columns([2,1])
with f_col1:
    st.caption("Sumber Data: BPS Sosioekonomi 2025 & Jobstreet Indonesia (via GraphQL API).")
with f_col2:
    st.caption("© 2026 Proyek Skripsi Falah.")
```

**Penjelasan:**
- 2 kolom: Sumber data + copyright
- Caption style untuk footer text

---

## ✅ SELESAI

**Total Kode Use Case:** ~420 baris (tanpa CSS)  
**Total Section:** 10 bagian  
**Framework:** Streamlit + Plotly  

---

## 📝 RINGKASAN STRUKTUR

| Section | Konten | Baris | Kategori |
|
---------|--------|-------|----------|
| 1 | Import & Config | ~20 | Setup |
| 2 | Data Loading | ~70 | Infrastructure |
| 3 | Sidebar Filter | ~50 | **Interaksi User** |
| 4 | Header & Tabs | ~10 | Navigation |
| 5 | Tab 1 (UC1) | ~40 | **Use Case** |
| 6 | Tab 2 (UC2) | ~80 | **Use Case** |
| 7 | Tab 3 (UC3) | ~40 | **Use Case** |
| 8 | Tab 4 (UC4) | ~60 | **Use Case** |
| 9 | Tab 5 (UC5) | ~90 | **Use Case** |
| 10 | Footer | ~10 | Closing |

**Total Kode Interaksi Use Case:** ~360 baris (Section 3, 5-9)

---

## 🎯 KEUNGGULAN VERSI INI

✅ **Tanpa CSS** - Fokus pada logic interaksi user, bukan styling  
✅ **Hanya Use Case** - Sesuai kriteria lampiran skripsi  
✅ **Lebih ringkas** - 420 baris vs 553 baris (versi asli)  
✅ **Mudah dijelaskan** - Setiap section = 1 fungsi spesifik  
✅ **Siap lampiran** - Copy-paste langsung ke Word/LaTeX  

---

## 📂 CARA MENGGUNAKAN

**Untuk Word:**
1. Buka file: `LAMPIRAN_FINAL_CLEAN.md`
2. Copy section yang dibutuhkan
3. Paste ke Word dengan font **Consolas 9pt**
4. Aktifkan line numbers

**Untuk LaTeX:**
```latex
\lstinputlisting[language=Python, 
                 caption={Dashboard Interaktif},
                 label={lst:dashboard}]
                {LAMPIRAN_FINAL_CLEAN.md}
```

---

## ✅ SELESAI

**File siap digunakan untuk lampiran skripsi!**

Total: **420 baris** kode use case murni (tanpa CSS styling).
