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

# --- TEMA PREMIUM (Corporate Blue & Kreatif) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main {
        background-color: #0A1128;
    }
    
    /* Metric Card Styling */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 800;
        color: #00A6FB;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #9DB4C0;
    }

    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px 8px 0 0;
        color: #9DB4C0;
        font-weight: 600;
        padding: 0 24px;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: #004E98 !important;
        color: white !important;
        border-bottom: 3px solid #00A6FB !important;
    }

    h1, h2, h3 {
        color: #FFFFFF;
        font-weight: 800;
    }
    
    .highlight {
        color: #00A6FB;
    }
    
    .stInfo {
        background-color: rgba(0, 166, 251, 0.1);
        color: #FFFFFF;
        border: 1px solid #00A6FB;
    }

    /* Mobile Responsive */
    @media (max-width: 768px) {
        /* Sidebar lebih compact di mobile */
        [data-testid="stSidebar"] {
            min-width: 100% !important;
            width: 100% !important;
        }

        /* Metric cards stack vertikal */
        [data-testid="column"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }

        /* Font title lebih kecil */
        h1 { font-size: 1.4rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1.0rem !important; }

        /* Metric value lebih kecil */
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }

        /* Tab label wrap */
        .stTabs [data-baseweb="tab"] {
            padding: 0 12px !important;
            font-size: 0.8rem !important;
        }

        /* Plotly chart full width */
        [data-testid="stPlotlyChart"] {
            width: 100% !important;
        }

        /* Dataframe scroll horizontal */
        [data-testid="stDataFrame"] {
            overflow-x: auto !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- LOADING DATA ---
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
    
    # Klasifikasi detail untuk visualisasi peta yang lebih presisi
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
            
            # WORKAROUND & BUGFIX: 
            # 1. Hapus feature dengan geometry: null (Menyebabkan MapBox/Maplibre CRASH di JS: Cannot read properties of null reading 'type')
            valid_features = []
            for feature in g['features']:
                if feature.get('geometry') is not None:
                    # 2. Plotly memerlukan parameter 'id' di root level setiap feature
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

# --- SIDEBAR ---
st.sidebar.image("https://img.icons8.com/isometric/100/city.png", width=80)
st.sidebar.title("Analisis Hub Kerja")
st.sidebar.markdown("*Skripsi Falah - Pulau Jawa*")
st.sidebar.divider()

# Filter Provinsi & Kabupaten/Kota (Sesuai Activity Diagram 1 & Wireframe)
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

# Tombol Apply Filters (Sesuai Wireframe)
apply_button = st.sidebar.button("Apply Filters", type="primary")

# Inisialisasi Session State agar data tersimpan saat diklik
if 'applied_city' not in st.session_state:
    st.session_state.applied_city = selected_city
if 'applied_prov' not in st.session_state:
    st.session_state.applied_prov = selected_prov

# Update session state hanya ketika tombol Apply Filters diklik
if apply_button:
    st.session_state.applied_city = selected_city
    st.session_state.applied_prov = selected_prov

# Gunakan data yang telah di-apply untuk sisa program
city_info = df[df['matched_regency'] == st.session_state.applied_city].iloc[0]

st.sidebar.subheader("Konteks Wilayah (Terpilih)")
st.sidebar.write(f"**Provinsi:** {city_info['Provinsi']}")
st.sidebar.write(f"**Status:** {city_info['prosperity_status']}")
if 'cluster_display' in city_info:
    st.sidebar.info(f"**Klasifikasi:** {city_info['cluster_display']}")

st.sidebar.divider()
st.sidebar.caption("v1.5 • DBSCAN Pure Spatial (eps=0.40)")

# --- HEADER UTAMA ---
st.title("Analisis Spasial Hub & Peluang Kerja")
st.markdown(f"Wawasan visual untuk pasar kerja di <span class='highlight'>{st.session_state.applied_city}</span>", unsafe_allow_html=True)

# --- TAB DASHBOARD (5 USE CASES / NAVIGASI) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Filter & Parameter",
    "📍 Klaster Ekonomi", 
    "🔥 Heatmap Peluang", 
    "📈 Statistik Efisiensi",
    "📝 Laporan Eksekutif"
])

# MODUL 1: FILTER & PARAMETER (UC1)
with tab1:
    st.subheader("Filter Wilayah & Parameter")
    st.markdown(f"Menampilkan data untuk: **{st.session_state.applied_prov}** - **{st.session_state.applied_city}**")
    
    # 1. Global Parameter Summary
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
        
    # 2. Raw Data Table
    st.markdown("### 📋 Raw Data Table (Daftar Lowongan Pekerjaan)")
    df_raw = load_raw_jobs()
    if not df_raw.empty:
        # Filter raw data
        if st.session_state.applied_prov != "Semua Provinsi":
            filtered_raw = df_raw[(df_raw['Provinsi'] == st.session_state.applied_prov) & (df_raw['matched_regency'] == st.session_state.applied_city)]
        else:
            filtered_raw = df_raw[df_raw['matched_regency'] == st.session_state.applied_city]
            
        st.markdown(f"Menampilkan **{len(filtered_raw)}** data lowongan pekerjaan untuk **{st.session_state.applied_city}** dari total dataset.")
        
        display_df = filtered_raw[['title', 'company', 'location']].copy()
        display_df.columns = ['Judul Pekerjaan', 'Perusahaan', 'Lokasi Asli']
        st.dataframe(display_df, use_container_width=True, height=350)
    else:
        st.warning("Data mentah lowongan pekerjaan tidak tersedia.")

# MODUL 2: MAP KLASTER SPASIAL (UC2)
with tab2:
    st.subheader("Peta Klaster Spasial (Hasil DBSCAN)")
    st.markdown("Peta ini mengidentifikasi 'Hub Ekonomi' yang terbentuk secara otonom berdasarkan kepadatan lowongan dan kedekatan geografis.")
    
    # Warna lebih nyentrik dan kontras
    # Menggunakan scatter_map (rekomendasi terbaru Plotly)
    fig1 = px.scatter_map(
        df, 
        lat="Latitude", 
        lon="Longitude", 
        color="cluster_display",
        size="size_for_map",
        size_max=40,
        hover_name="matched_regency",
        hover_data={"Latitude":False, "Longitude":False, "cluster_display":True, "job_volume":True, "size_for_map":False},
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
    
    # Penanda lokasi terpilih
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
    st.plotly_chart(fig1, width="stretch")
    
    # Ringkasan komposisi cluster
    c0 = df[df['cluster_id'] == 0]
    c1 = df[df['cluster_id'] == 1]
    cn = df[df['cluster_id'] == -1]
    comp_col1, comp_col2, comp_col3 = st.columns(3)
    with comp_col1:
        st.metric("Cluster 0 — Mainland Java", f"{len(c0)} wilayah", f"{int(c0['job_volume'].sum()):,} lowongan")
    with comp_col2:
        st.metric("Cluster 1 — Jabodetabek", f"{len(c1)} wilayah", f"{int(c1['job_volume'].sum()):,} lowongan")
    with comp_col3:
        st.metric("Isolated Zone (Noise)", f"{len(cn)} wilayah", f"{int(cn['job_volume'].sum()):,} lowongan")
    
    st.info("""
    **💡 Catatan Analisis DBSCAN:** 
    * **Cluster 0 (Biru):** Aglomerasi pasar kerja koridor mainland Pulau Jawa yang terhubung secara kontigu — mencakup pusat regional seperti Surabaya, Bandung, Semarang, GKS, dan Solo.
    * **Cluster 1 (Hijau Toska):** Aglomerasi metropolitan Jabodetabek beserta koridor industri Banten–Jawa Barat bagian barat (Serang, Karawang, Cilegon, dll) dengan densitas lowongan tertinggi.
    * **Cluster -1 (Abu-Abu):** Isolated Red Zone — wilayah terpencil dengan volume lowongan rendah/nihil yang tidak membentuk kelompok aglomerasi dengan tetangganya (contoh: Madura, Pacitan, Lebak).
    * Ukuran lingkaran menunjukkan volume lowongan absolut di wilayah tersebut (ditambah offset 5 agar wilayah 0 lowongan tetap terlihat di peta).
    """)

# MODUL 3: HEATMAP PELUANG (UC3)
with tab3:
    st.subheader("Heatmap Peluang Kerja (Choropleth)")
    st.markdown(r"Visualisasi perbedaan antara **'Lautan Peluang'** (Hijau) dan **'Zona Merah'** (Merah).")
    st.latex(r"Indeks\_Peluang = \frac{Volume\_Pekerjaan}{Angkatan\_Kerja\_Aktif}")
    
    if geojson:
        # Fallback to choropleth_mapbox because MapLibre (choropleth_map) strictly enforces 
        # polygon winding order, which often results in blank maps for standard GeoJSONs.
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
        st.plotly_chart(fig2, width="stretch")
        
        st.info("""
        **💡 Panduan Intepretasi Heatmap (Choropleth):**
        * **Hijau (Lautan Peluang):** Wilayah berpotensi dengan porsi lowongan yang tinggi per satuan angkatan kerja nyata. Sangat direkomendasikan bagi talenta pencari kerja (suplai kerja lokal belum memenuhi demand).
        * **Merah (Zona Merah):** Wilayah padat persaingan dimana volume kesempatan kerja relatif tipis berbanding dengan membludaknya jumlah angkatan kerja (indikasi kejenuhan). 
        """)
    else:
        st.warning("File batas GeoJSON tidak ditemukan. Menampilkan visualisasi alternatif...")
        fig_alt = px.density_map(
            df, lat='Latitude', lon='Longitude', z='opportunity_index', 
            radius=30, map_style="carto-darkmatter", height=600,
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig_alt, width="stretch")


# MODUL 4: PLOT KORELASI & KOMPETITIF
with tab4:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("a. Efisiensi Pasar Kerja")
        st.markdown("Evaluasi statistik ketersediaan kerja terhadap jumlah angkatan kerja.")
        fig4a = px.scatter(
            df, x="labor_force_num", y="job_volume",
            trendline="ols", trendline_color_override="#00A6FB",
            hover_name="matched_regency", color="opportunity_index",
            color_continuous_scale="Viridis",
            labels={"labor_force_num": "Angkatan Kerja (BPS)", "job_volume": "Volume Lowongan"},
            template="plotly_dark", height=500
        )
        st.plotly_chart(fig4a, width="stretch")

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
        st.plotly_chart(fig4b, width="stretch")
    
    st.info("""
    **💡 Catatan Analisis Kuadran & Kualifikasi:** 
    * Plot sebelah kiri memvalidasi seberapa linier hubungan penciptaan loker terhadap beban demografi (angkatan kerja). Wilayah yang melesat ke atas dari *trendline* menunjukkan performa penciptaan kerja yang abnormal (positif).
    * Barchart Indeks Kompetitif pada level *>=2.5* didominasi posisi manajerial elit. Skor *~1.0 - 1.5* mengindikasikan pasar kerja kerah biru / peranan operasional.
    """)
    
    st.divider()
    st.subheader("c. Metrik Evaluasi Model Spasial (DBSCAN)")
    st.markdown("Evaluasi kualitas klastering yang terbentuk (eksklusi titik noise -1 untuk mencegah distorsi bias).")
    
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric(
            label="Silhouette Score (Cohesion)", 
            value="0.4737", 
            help="Rentang -1 s/d +1. Mengukur seberapa dekat suatu objek dengan klasternya sendiri dibandingkan dengan klaster lain."
        )
        st.caption("ℹ️ *Silhouette score 0.4737 (moderat-baik) mencerminkan bahwa aglomerasi spasial Pulau Jawa memanjang horizontal mengikuti koridor Trans-Jawa, bukan berbentuk spherical — DBSCAN lebih tepat untuk pola ini dibanding K-Means.*")
        
    with m_col2:
        st.metric(
            label="Davies-Bouldin Index (DBI - Separasi)", 
            value="0.5126", 
            help="Nilai mendekati 0 semakin baik. Mengukur tingkat tumpang tindih (overlap) antar klaster."
        )
        st.caption("ℹ️ *Nilai DBI 0.5126 (di bawah 1.0) menunjukkan pemisahan antar klaster yang baik — Cluster 0 (Mainland) dan Cluster 1 (Jabodetabek) tidak saling tumpang tindih secara spasial.*")

# MODUL 5: LAPORAN EKSEKUTIF (SUMMARY) (UC5)
with tab5:
    st.subheader(f"Laporan Analisis Wilayah: {st.session_state.applied_city}")
    st.markdown("Ringkasan temuan otomatis yang ditarik dari hasil *Machine Learning* dan Indeks Peluang untuk mempermudah perumusan kesimpulan skripsi.")
    
    # Kalkulasi peringkat aktif (Eksklusi Wilayah dengan 0 Lowongan - Sesuai Logika 3)
    df_active = df[df['job_volume'] > 0].copy()
    df_active_sorted = df_active.sort_values(by='opportunity_index', ascending=False).reset_index(drop=True)
    df_sorted = df.sort_values(by='opportunity_index', ascending=False).reset_index(drop=True) # Tetap digunakan untuk list tabel di bawah
    
    has_jobs = int(city_info['job_volume']) > 0
    
    if has_jobs:
        rank = df_active_sorted[df_active_sorted['matched_regency'] == st.session_state.applied_city].index[0] + 1
        total_active = len(df_active_sorted)
        
        # Validasi apakah wilayah masuk Zona Merah secara demografis/volume lowongan
        is_zona_merah = city_info['prosperity_status'] == "Zona Merah"
        
        if is_zona_merah:
            conclusion = f"Bisa dikatakan wilayah ini mengalami defisit lapangan kerja nyata (**Peringkat {rank} dari {total_active} wilayah aktif**). Meskipun secara indeks relatif berada di papan tengah, secara absolut pasar kerja formal sangat terbatas ({int(city_info['job_volume'])} posisi) untuk menampung populasinya."
            recom_val = "Berisiko"
            comp_val = "Sengit"
        else:
            if rank <= 10:
                conclusion = f"Wilayah ini masuk ke dalam **Top 10 (Peringkat {rank} dari {total_active} wilayah aktif)** kawasan berekspansi tinggi. Direkomendasikan sebagai destinasi utama pencari kerja."
                recom_val = "Sangat Layak"
                comp_val = "Longgar"
            elif rank >= (total_active - 15):
                conclusion = f"Bisa dikatakan wilayah ini mengalami defisit gawat darurat (**Peringkat {rank} dari {total_active} wilayah aktif**). Lapangan formal sangat sedikit dibandingkan populasinya."
                recom_val = "Berisiko"
                comp_val = "Sengit"
            else:
                conclusion = f"Menempati posisi menengah-stabil di **Peringkat {rank} dari {total_active} wilayah aktif**. Memiliki pasar kerja organik namun perputaran karyawannya standar."
                recom_val = "Netral"
                comp_val = "Seimbang"
    else:
        rank = "Tidak Terperingkat"
        total_active = len(df_active_sorted)
        conclusion = "Wilayah ini tidak memiliki lowongan kerja formal yang aktif (0 Lowongan), sehingga tidak masuk dalam pemeringkatan peluang kerja aktif. Wilayah ini mengalami defisit lapangan kerja mutlak."
        recom_val = "Berisiko"
        comp_val = "Sangat Sengit"

    col_L1, col_L2 = st.columns([2, 1])
    
    with col_L1:
        st.markdown("#### Narasi Kesimpulan")
        st.write(f"Secara makro-ekonomi, **{st.session_state.applied_city}** diidentifikasi oleh sistem *DBSCAN* sebagai **{city_info['cluster_display']}** bertaraf {city_info['prosperity_status']}.")
        st.write(f"Dengan Angkatan Kerja sebesar **{int(city_info['labor_force_num']):,}** orang dan ketersediaan **{int(city_info['job_volume'])}** spesifikasi pekerjaan lintas digital, rasio indeks peluang membujur di angka **{city_info['opportunity_index']:.5f}**.")
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
        st.markdown("#### 🌟 Top 5 Lautan Peluang (Episentrum Terbaik)")
        # Tampilkan 5 teratas berdasarkan opportunity_index tertinggi
        top_opportunities = df_sorted[['matched_regency', 'Provinsi', 'job_volume', 'opportunity_index']].head(5)
        top_opportunities.columns = ['Kabupaten/Kota', 'Provinsi', 'Volume Lowongan', 'Indeks Peluang']
        st.dataframe(top_opportunities, use_container_width=True, hide_index=True)
        st.caption("ℹ️ *Wilayah dengan rasio penyerapan kerja tertinggi terhadap jumlah angkatan kerja aktif.*")
        
    with list_col2:
        st.markdown("#### 🚨 Top 5 Zona Merah (Defisit Lapangan Kerja)")
        # Tampilkan 5 terbawah berdasarkan opportunity_index terendah (dibalik agar yang paling parah di atas)
        bottom_opportunities = df_sorted[['matched_regency', 'Provinsi', 'job_volume', 'opportunity_index']].tail(5).iloc[::-1]
        bottom_opportunities.columns = ['Kabupaten/Kota', 'Provinsi', 'Volume Lowongan', 'Indeks Peluang']
        st.dataframe(bottom_opportunities, use_container_width=True, hide_index=True)
        st.caption("ℹ️ *Wilayah dengan tingkat persaingan terpadat atau ketersediaan lapangan kerja terkecil.*")

# --- FOOTER ---
st.divider()
f_col1, f_col2 = st.columns([2,1])
with f_col1:
    st.caption("Sumber Data: BPS Sosioekonomi 2025 & Jobstreet Indonesia (via GraphQL API).")
with f_col2:
    st.caption("© 2026 Proyek Skripsi Falah. Teknologi oleh Antigravity AI.")
