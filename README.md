# Java Job Market Clustering Dashboard

This repository contains Falah's thesis project for analyzing spatial job market clusters in Java using DBSCAN and NLP.

## 📁 Project Structure

- `dashboard.py`: Main interactive dashboard (Streamlit).
- `requirements.txt`: Python package dependencies.
- `data/`: Processed data and geographic boundaries.
  - `java_job_market_hubs_final.csv`: Result of clustering and NLP.
  - `java_regencies.geojson`: Java kabupaten/kota boundaries.
  - `38 Provinsi Indonesia - Kabupaten.json`: Original national boundaries.
- `src/`: Data processing and analysis scripts.
  - `1_acquisition_jobstreet.py` to `6_spatial_clustering_dbscan.py`: Pipeline utama.
  - `prepare_dashboard_data.py`: Utilities for dashboard map preparation.
- `archive/`: Direktori penyimpanan script eksplorasi dan testing lama (Draft Phase).

## 🚀 How to Run the Project

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Data Pipeline (if starting from scratch):
   Jalankan file di dalam direktori `src/` secara berurutan dari `1_` sampai dengan `6_`.
   *Lihat `METODOLOGI.md` untuk penjelasan tiap parameter.*

3. Launch the Dashboard:
   ```bash
   streamlit run dashboard.py
   ```

## 📊 Dashboard Modules

1. **Economic Hubs**: Spatial clusters identified by DBSCAN.
2. **Opportunity Heatmap**: Choropleth visualization of job accessibility.
3. **Skill Context**: NLP-derived skill patterns per region.
4. **Market Efficiency**: Statistical correlation between population and job volume.

---
*Developed by Antigravity (Falah's AI Assistant)*
