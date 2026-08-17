#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kalibrr Scraper v2 — via API /kjs/job_board/search.

Temuan (16-08-2026):
- Endpoint JSON: https://jobseeker.kalibrr.com/kjs/job_board/search
- Auth: cookie `kb` (JWT candidate session) + header `kb-csrf` + `cf_clearance`.
- Query: country=Indonesia, limit/offset (pagination via offset).
- Lokasi: google_location.address_components {city, region, country}.
- Flag remote: is_work_from_home / is_hybrid.

Output: data/kalibrr_jobs_v2.csv (id,title,company,location,city,region,function,
        is_work_from_home,is_hybrid,salary,source,scraped_at)
"""
import argparse
import json
import time
import random
from datetime import datetime, timezone

import pandas as pd
from curl_cffi import requests

BASE = "https://jobseeker.kalibrr.com/kjs/job_board/search"


def load_cfg(path="data/kalibrr_cookies.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def headers(cfg):
    return {
        "accept": "application/json, text/plain, */*",
        "accept-language": "id,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "kb-csrf": cfg.get("kb_csrf", ""),
        "referer": "https://jobseeker.kalibrr.com/job-board/i/it-and-software/1",
        "user-agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Mobile Safari/537.36",
    }


def cookies(cfg):
    c = {"kb": cfg.get("kb", "")}
    if cfg.get("cf_clearance"):
        c["cf_clearance"] = cfg["cf_clearance"]
    if cfg.get("__zlcmid"):
        c["__zlcmid"] = cfg["__zlcmid"]
    return c


def fetch(cfg, params, retries=3):
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(BASE, headers=headers(cfg), cookies=cookies(cfg),
                             params=params, impersonate="chrome110", timeout=30)
            if r.status_code == 200:
                return r.json()
            print(f"  [RETRY] offset={params.get('offset')} status={r.status_code} (attempt {attempt})")
        except Exception as e:
            print(f"  [ERR] offset={params.get('offset')}: {e} (attempt {attempt})")
        if attempt < retries:
            time.sleep(3 * attempt + random.uniform(1, 2))
    return None


def parse(job):
    gl = job.get("google_location") or {}
    ac = gl.get("address_components") or {}
    city = ac.get("city") or ""
    region = ac.get("region") or ""
    loc = ", ".join([x for x in [city, region] if x])
    return {
        "id": str(job.get("id")),
        "title": job.get("name") or job.get("title") or "",
        "company": job.get("company_name") or ((job.get("company") or {}).get("name") or ""),
        "location": loc,
        "city": city,
        "region": region,
        "function": job.get("function"),
        "is_work_from_home": bool(job.get("is_work_from_home")),
        "is_hybrid": bool(job.get("is_hybrid")),
        "salary": job.get("base_salary"),
        "source": "kalibrr",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/kalibrr_jobs_v2.csv")
    ap.add_argument("--limit", type=int, default=15)
    a = ap.parse_args()

    cfg = load_cfg()
    rows = []
    seen = set()
    offset = 0
    total = None

    while True:
        params = {"country": "Indonesia", "limit": a.limit, "offset": offset}
        d = fetch(cfg, params)
        if d is None:
            print("[STOP] fetch gagal berulang; simpan hasil sementara.")
            break
        if total is None:
            total = d.get("count", 0)
            print(f"Total lowongan Kalibrr Indonesia: {total}")
        jobs = d.get("jobs") or []
        if not jobs:
            break
        new = 0
        for j in jobs:
            p = parse(j)
            if p["id"] in seen:
                continue
            seen.add(p["id"])
            rows.append(p)
            new += 1
        print(f"offset={offset}: +{new} | unik={len(seen)}")
        if offset + a.limit >= total:
            break
        offset += a.limit
        time.sleep(random.uniform(0.4, 1.2))

    if rows:
        pd.DataFrame(rows).to_csv(a.out, index=False)
        print(f"\nSELESAI. total unik={len(rows)} -> {a.out}")
    else:
        print("Tidak ada data.")


if __name__ == "__main__":
    main()
