import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
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
    df['competitive_index'] = pd.to_numeric(df.get('competitive_index', 0), errors='coerce').fillna(0)
    df['labor_force_num'] = pd.to_numeric(df.get('labor_force_num', 0), errors='coerce').fillna(0)
    df['job_volume'] = pd.to_numeric(df.get('job_volume', 0), errors='coerce').fillna(0)
    df['cluster_id'] = df['cluster_id'].astype(int) if 'cluster_id' in df.columns else -1
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

df = load_data()
geojson = load_geojson()

# --- SIDEBAR ---
st.sidebar.image("https://img.icons8.com/isometric/100/city.png", width=80)
st.sidebar.title("Analisis Hub Kerja")
st.sidebar.markdown("*Skripsi Falah - Pulau Jawa*")
st.sidebar.divider()

selected_city = st.sidebar.selectbox(
    "📍 Pilih Kabupaten/Kota", 
    sorted(df['matched_regency'].unique()),
    index=0
)

city_info = df[df['matched_regency'] == selected_city].iloc[0]

st.sidebar.subheader("Konteks Wilayah")
st.sidebar.write(f"**Provinsi:** {city_info['Provinsi']}")
st.sidebar.write(f"**Status:** {city_info['prosperity_status']}")
if 'hub_type' in city_info:
    # Terjemahan tipe hub
    h_type = "Hub Ekonomi" if city_info['hub_type'] == "Economic Hub" else "Zona Terisolasi"
    st.sidebar.info(f"**Tipe Hub:** {h_type}")

st.sidebar.divider()
st.sidebar.caption("v1.1 • Dimutakhirkan dengan Indeks Kompetitif")

# --- HEADER UTAMA ---
st.title("Analisis Spasial Hub & Peluang Kerja")
st.markdown(f"Wawasan visual untuk pasar kerja di <span class='highlight'>{selected_city}</span>", unsafe_allow_html=True)

# --- METRIK UTAMA ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Volume Lowongan", f"{int(city_info['job_volume'])} Posisi")
with m2:
    val = float(city_info['labor_force_num'])
    st.metric("Angkatan Kerja", f"{int(val):,}" if val > 0 else "Data Kosong")
with m3:
    st.metric("Indeks Peluang", f"{city_info['opportunity_index']:.5f}", help="Job Volume / Working Age Population")
with m4:
    comp_idx = city_info.get('competitive_index', 0)
    st.metric("Indeks Kompetitif", f"{comp_idx:.2f}/3.0", help="Tingkat kualifikasi rata-rata (1: Rendah, 3: Tinggi)")

# --- TAB DASHBOARD ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Klaster Ekonomi", 
    "🔥 Heatmap Peluang", 
    "☁️ Konteks Keahlian", 
    "📈 Statistik Efisiensi"
])

# MODUL 1: MAP KLASTER SPASIAL
with tab1:
    st.subheader("1. Peta Klaster Spasial (Hasil DBSCAN)")
    st.markdown("Peta ini mengidentifikasi 'Hub Ekonomi' yang terbentuk secara otonom berdasarkan kepadatan lowongan dan kedekatan geografis.")
    
    # Warna lebih nyentrik dan kontras
    # Menggunakan scatter_map (rekomendasi terbaru Plotly)
    fig1 = px.scatter_map(
        df, 
        lat="Latitude", 
        lon="Longitude", 
        color=df["cluster_id"].astype(str),
        size="job_volume",
        size_max=40,
        hover_name="matched_regency",
        hover_data={"Latitude":False, "Longitude":False, "cluster_id":True, "job_volume":True},
        zoom=6,
        height=600,
        color_discrete_sequence=px.colors.qualitative.Alphabet, 
        map_style="carto-darkmatter",
        template="plotly_dark",
        labels={"color": "ID Klaster"}
    )
    
    # Penanda lokasi terpilih
    fig1.add_trace(go.Scattermap(
        lat=[city_info['Latitude']],
        lon=[city_info['Longitude']],
        mode='markers',
        marker=go.scattermap.Marker(size=25, color='#FFD700', opacity=0.9),
        name='Lokasi Target',
        text=[selected_city]
    ))
    
    fig1.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig1, width="stretch")
    
    st.info("""
    **💡 Catatan Analisis DBSCAN:** 
    * Klaster dengan warna berbeda menunjukkan aglomerasi ekonomi (Hub) yang terbentuk secara natural dari kepadatan lowongan dan kesempatan kerja.
    * Titik dengan ID '-1' adalah Noise (Outlier), mengindikasikan wilayah dengan pasar kerja yang berdiri sendiri atau belum membentuk hub berskala besar.
    * Semakin besar radius lingkaran, semakin banyak volume lowongan absolut di wilayah tersebut.
    """)

# MODUL 2: HEATMAP PELUANG
with tab2:
    st.subheader("2. Heatmap Peluang Kerja (Choropleth)")
    st.markdown(r"Visualisasi perbedaan antara **'Lautan Peluang'** (Hijau) dan **'Zona Merah'** (Merah).")
    st.latex(r"Indeks\_Peluang = \frac{Volume\_Pekerjaan}{Angkatan\_Kerja\_Aktif}")
    
    if geojson:
        # Fallback to choropleth_mapbox because MapLibre (choropleth_map) strictly enforces 
        # polygon winding order, which often results in blank maps for standard GeoJSONs.
        fig2 = px.choropleth_mapbox(
            df,
            geojson=geojson,
            locations="matched_regency",
            featureidkey="id",
            color="opportunity_index",
            color_continuous_scale="RdYlGn",
            range_color=(df['opportunity_index'].min(), df['opportunity_index'].quantile(0.9)), 
            mapbox_style="carto-darkmatter",
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
        fig_alt = px.density_mapbox(
            df, lat='Latitude', lon='Longitude', z='opportunity_index', 
            radius=30, mapbox_style="carto-darkmatter", height=600,
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig_alt, width="stretch")

# MODUL 3: WORD CLOUD KEAHLIAN
with tab3:
    st.subheader("3. Karakteristik Keahlian (NLP / TF-IDF)")
    st.markdown(f"DNA Keahlian yang diekstrak dari judul pekerjaan di **{selected_city}** (Noise lokasi telah difilter).")
    
    skills = city_info['top_skills']
    if pd.isna(skills) or str(skills).strip() == "":
        st.warning("Tidak ditemukan kata kunci keahlian spesifik untuk wilayah ini.")
    else:
        # Buat WordCloud
        wc = WordCloud(
            width=1000, 
            height=500, 
            background_color="#0A1128", 
            colormap="winter",
            max_words=50
        ).generate(skills.replace(",", " "))
        
        fig3, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        fig3.set_facecolor('#0A1128')
        st.pyplot(fig3)
        
        st.success(f"**Top Skills Found:** {skills}")

# MODUL 4: PLOT KORELASI & KOMPETITIF
with tab4:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("4a. Efisiensi Pasar Kerja")
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
        st.subheader("4b. Distribusi Indeks Kompetitif")
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
    * Barchart Indeks Kompetitiif pada level *>=2.5* didominasi posisi manajerial elit. Skor *~1.0 - 1.5* mengindikasikan pasar kerja kerah biru / peranan operasional.
    """)

# --- FOOTER ---
st.divider()
f_col1, f_col2 = st.columns([2,1])
with f_col1:
    st.caption("Sumber Data: BPS Sosioekonomi 2024 & Gabungan Portal Kerja (JobStreet/Glints).")
with f_col2:
    st.caption("© 2026 Proyek Skripsi Falah. Teknologi oleh Antigravity AI.")
