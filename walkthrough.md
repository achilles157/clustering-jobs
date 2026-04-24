# Master Walkthrough: Spatial Job Market Clustering

This document serves as the complete, definitive guide to the pipeline executed in this project, from data acquisition to the final interactive dashboard.

## 🚀 Phase 1: Data Acquisition
* **Target:** Scraped real-world job posting data from Jobstreet Indonesia.
* **Mechanism:** Bypassed WAF protections using `curl_cffi` to query the undocumented `JobSearchV6` GraphQL endpoint.
* **Output:** Gathered over 19,000 raw job listings.

## 🧩 Phase 2: BPS Integration & Geocoding
* **Socio-Economic Data:** Merged 6 separate provincial datasets from BPS (Badan Pusat Statistik) containing Labor Force numbers for 119 regencies in Java.
* **Centroid Mapping:** Since job listings lack exact micro-coordinates, we appended the Lat/Lon centroid of the respective Regency (Kabupaten/Kota) to each job node.

## 🧬 Phase 3: NLP & Market Engineering
* **Opportunity Index:** Calculated the ratio of available jobs compared to the active labor force in each region to determine market saturation.
* **TF-IDF NLP:** Processed the `skills` strings across all jobs per region to extract the dominant industrial skills (Bi-Grams).
* **Fuzzy Matching:** Achieved an **88.8%** match rate connecting Jobstreet territory names to BPS official territory names using `rapidfuzz`.

## 📍 Phase 4: Spatial DBSCAN Clustering
* **Algorithm:** Applied `DBSCAN` with `eps=0.45` (approx 50KM radius) across the coordinate space of Java.
* **Result:** Successfully detected organic "Economic Hubs" (e.g., the massive Jabodetabek agglomeration and the Surabaya-Malang corridor) purely based on job density, ignoring artificial province borders.

## 📊 Phase 5: Streamlit Dashboard
The culmination of the project is an interactive dashboard demonstrating the findings:
1. **Interactive Spatial Map:** Visualizes the DBSCAN hubs and the opportunity index choropleth.
2. **Scatter Correlation:** Maps the disparity between population size and job availability.
3. **Dynamic Skill Context:** Generates WordClouds on-the-fly when a specific region is selected.

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
