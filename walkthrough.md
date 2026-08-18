# Master Walkthrough: Spatial Job Market Clustering

This document serves as the complete, definitive guide to the pipeline executed in this project, from data acquisition to the final interactive dashboard.

## 🚀 Phase 1: Data Acquisition
* **Target:** Scraped real-world job postings from Jobstreet Indonesia + Glints Indonesia + Kalibrr Indonesia.
* **Mechanism:** Queried the **public** `JobSearchV6` GraphQL endpoint of Jobstreet (no auth/cookie required), the Glints `searchJobsV3` GraphQL API, and the Kalibrr `/kjs/job_board/search` JSON API (cookie `kb` + `kb-csrf` header) via `curl_cffi`.
* **Output:** ~50,000 raw Jobstreet listings (national, filtered to Java at integration) + ~1,500 Glints listings (Java, on-site) + ~1,000 Kalibrr listings (Indonesia, on-site).

## 🧩 Phase 2: BPS Integration & Geocoding
* **Socio-Economic Data:** Merged 6 separate provincial datasets from BPS (Badan Pusat Statistik) containing Labor Force numbers for 119 regencies in Java.
* **Centroid Mapping:** Since job listings lack exact micro-coordinates, we appended the Lat/Lon centroid of the respective Regency (Kabupaten/Kota) to each job node.

## 🧬 Phase 3: Market Engineering
* **Opportunity Index (Opsi C):** `opportunity_index = observed vacancies ÷ open unemployment` (BPS "Angkatan Kerja Pengangguran - Jumlah"). TPT (unemployment ÷ labor force × 100) is kept as a context metric — the index measures job availability relative to those who actually need work.
* **Fuzzy Matching:** Jobstreet location strings are fuzzy-matched (with a rescue cache) to BPS territory names using `rapidfuzz` (threshold ≥ 80); a non-Java province filter removes non-Java listings before matching. Glints jobs are mapped via nearest-regency centroid (lat/lon). Cross-platform duplicates are dropped on (company, title, regency).

## 📍 Phase 4: Spatial DBSCAN Clustering
* **Algorithm:** Applied `DBSCAN` with `eps=0.40` and `min_samples=3` on StandardScaler-normalized coordinates (Latitude/Longitude) of Java.
* **Result:** Successfully detected organic "Economic Hubs" (e.g., the Jabodetabek–Banten–Koridor Utara agglomeration and the Trans-Java mainland corridor covering Surabaya, Bandung, Semarang, and Yogyakarta) purely based on job density, ignoring artificial province borders.

## 📊 Phase 5: Streamlit Dashboard
The culmination of the project is an interactive dashboard demonstrating the findings:
1. **Interactive Spatial Map:** Visualizes the DBSCAN hubs and the opportunity index choropleth.
2. **Scatter Correlation:** Maps the disparity between population size and job availability.

---

# 📦 Git & GitHub Integration Guide

If you need to backup or share this project on GitHub, follow these exact steps in your terminal (PowerShell).

**Step 1: Initialize Git**
```powershell
git init
```

**Step 2: Add Files & Commit**
This adds everything (including the data, as requested), ignoring files listed in `.gitignore`.
*(Catatan Keamanan: File `.env` sudah dilindungi oleh `.gitignore` sehingga aman untuk tidak ter-upload.)*
```powershell
git add .
git commit -m "Initial commit for Thesis Project: Data, Pipeline & Dashboard"
```

**Step 3: Push to GitHub**
1. Create a new empty repository at [github.com/new](https://github.com/new). Do not add a README or `.gitignore`.
2. Run these commands (replace `YOUR_USERNAME` with your real username):
```powershell
git remote add origin https://github.com/YOUR_USERNAME/clustering-jobs.git
git branch -M main
git push -u origin main
```

> [!TIP]
> If a file like `jobstreet_results.csv` becomes too large for GitHub (>100MB), you will need to run `git lfs install` followed by `git lfs track "*.csv"` before committing.
