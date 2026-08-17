#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jobstreet Scraper v2 — re-scrape tanpa auth, single-pass nasional.

Temuan (16-08-2026):
- endpoint https://id.jobstreet.com/graphql (jobSearchV6) PUBLIK (tanpa bearer/cookie).
- `where` tidak memfilter ketat per kota -> balikin daftar nasional (~20rb) ter-paginasi.
  City-sharding jadi mubazir; cukup paginasi sampai habis dalam satu pass.
- Query lama deklarasi $locale/$timezone tak terpakai -> 400. Fix: query cuma $params.

Output: data/jobstreet_results_v2.csv (id,title,company,location,listingDate,salary)
"""
import argparse
import json
import os
import random
import time

import pandas as pd
from curl_cffi import requests

URL = "https://id.jobstreet.com/graphql"
HEADERS = {
    "accept": "*/*",
    "accept-language": "id,en-US;q=0.9,en;q=0.8",
    "content-type": "application/json",
    "origin": "https://id.jobstreet.com",
    "seek-request-brand": "jobstreet",
    "seek-request-country": "ID",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
    "x-custom-features": "application/features.seek.all+json",
    "x-seek-site": "chalice",
}
QUERY = "query JobSearchV6($params: JobSearchV6QueryInput!){jobSearchV6(params:$params){data{id title companyName locations{label} listingDate{dateTimeUtc} salaryLabel advertiser{id}} totalCount}}"


def fetch(params, retries=3):
    body = {"operationName": "JobSearchV6", "variables": {"params": params}, "query": QUERY}
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(URL, headers=HEADERS, json=body, impersonate="chrome110", timeout=30)
            if r.status_code == 200:
                return r.json()
            print(f"  [RETRY] status={r.status_code} (attempt {attempt})")
        except Exception as e:
            print(f"  [ERR] {e} (attempt {attempt})")
        if attempt < retries:
            time.sleep(4 * attempt + random.uniform(1, 2))
    return None


def parse(resp):
    try:
        s = resp["data"]["jobSearchV6"]
        jobs = s.get("data") or []
        total = s.get("totalCount", 0)
        out = []
        for j in jobs:
            locs = j.get("locations") or []
            out.append({
                "id": str(j.get("id")), "title": j.get("title"),
                "company": j.get("companyName"),
                "location": locs[0].get("label") if locs else "",
                "listingDate": (j.get("listingDate") or {}).get("dateTimeUtc"),
                "salary": j.get("salaryLabel"),
            })
        return out, total
    except Exception:
        return [], 0


def base_params(page, page_size, where):
    p = {
        "channel": "mobileWeb", "locale": "id-ID", "page": page, "pageSize": page_size,
        "siteKey": "ID", "sortMode": "ListedDate", "include": ["seoData"], "source": "FE_SERP",
    }
    if where:
        p["where"] = where
    return p


def load_ckpt(p):
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"page": 0, "ids": [], "total": 0}


def save_ckpt(p, page, ids, total):
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"page": page, "ids": sorted(ids), "total": total}, f)


def crawl(out_csv, where, page_size, max_pages, resume):
    ckpt_path = out_csv.replace(".csv", "_checkpoint.json")
    ckpt = load_ckpt(ckpt_path) if resume else {"page": 0, "ids": [], "total": 0}
    processed = set(ckpt["ids"])
    total_hint = ckpt["total"]
    page = ckpt["page"] + 1

    while page <= max_pages:
        resp = fetch(base_params(page, page_size, where))
        if resp is None:
            print(f"[STOP] page={page} gagal {3}x; simpan checkpoint & berhenti.")
            save_ckpt(ckpt_path, page - 1, processed, total_hint)
            break
        jobs, total = parse(resp)
        if not jobs:
            print(f"[STOP] page={page} kosong. selesai.")
            save_ckpt(ckpt_path, page - 1, processed, total)
            break
        total_hint = total
        new = [j for j in jobs if j["id"] not in processed]
        for j in new:
            processed.add(j["id"])
        if new:
            pd.DataFrame(new).to_csv(out_csv, mode="a", index=False, header=not os.path.exists(out_csv))
        pages_needed = (total // page_size) + (1 if total % page_size else 0)
        print(f"page={page}/{pages_needed}: +{len(new)} | unik={len(processed)} | total={total}")
        save_ckpt(ckpt_path, page, processed, total)
        if page >= pages_needed:
            print("SUDAH HABIS (page >= pages_needed).")
            break
        time.sleep(random.uniform(1.0, 2.5))
        page += 1

    print(f"\nSELESAI. total unik={len(processed)} | {out_csv}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/jobstreet_results_v2.csv")
    ap.add_argument("--where", default="", help="kosongkan = nasional (default)")
    ap.add_argument("--page-size", type=int, default=50)
    ap.add_argument("--max-pages", type=int, default=500)
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    crawl(a.out, a.where, a.page_size, a.max_pages, a.resume)


if __name__ == "__main__":
    main()
