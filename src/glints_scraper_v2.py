#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glints Scraper v2 (final) — page-based, butuh cookie session fresh.

Temuan teknis (16-08-2026):
  - Pagination via `offset`/`limit` DIABAIKAN untuk request anonim (offset 0/50/200 -> 50 job sama).
  - Pagination via `page` -> halaman 1 gratis (tanpa login), page>=2 -> 403 "please login".
  - Kesimpulan: untuk crawl penuh butuh cookie session yang VALID (login glints.com).
  - pageSize dihargai dan di-cap di 50.

Cara pakai:
  1. Ambil cookie segar: buka glints.com (login), F12 -> Network -> request api/v2-alc/graphql
     -> Headers -> Request Headers -> copy baris `cookie`.
  2. Simpan cookie ke data/glints_cookies.json (dict), atau set env GLINTS_COOKIE_HEADER.
  3. Jalankan:  python src/glints_scraper_v2.py --target 10000 --out data/glints_jobs_v2.csv

Peningkatan vs glints-scrapping.py:
  - Hapus TARGET_TOTAL cap & pagination wall
  - Retry + exponential backoff; checkpoint/resume (lanjut kalau terputus)
  - Tag workArrangementOption + is_remote + is_in_java (remote TIDAK dibuang di scraper,
    disimpan raw lalu di-exclude di tahap cleaning -> bisa dilaporkan jujur)
  - Output: raw JSONL (semua hasil fetch) + clean CSV (hanya Jawa non-remote)
"""
import argparse
import json
import os
import random
import sys
import time

import pandas as pd
from curl_cffi import requests

URL = "https://glints.com/api/v2-alc/graphql"
HEADERS = {
    "accept": "*/*", "accept-language": "en", "content-type": "application/json",
    "origin": "https://glints.com",
    "referer": "https://glints.com/id/en/opportunities/jobs/explore?country=ID&locationName=All%20Cities%2FProvinces",
    "x-glints-country-code": "ID",
}
JAVA_BOUNDS = {"lat_min": -9.0, "lat_max": -5.8, "lon_min": 105.0, "lon_max": 115.0}
PAGE_SIZE = 50

GRAPHQL_QUERY = """
query searchJobsV3($data: JobSearchConditionInput!) {
  searchJobsV3(data: $data) {
    jobsInPage {
      id title workArrangementOption status createdAt updatedAt isHot educationLevel type
      company { ...CompanyFields __typename }
      city { ...CityFields __typename }
      country { ...CountryFields __typename }
      location { ...LocationFields __typename }
      minYearsOfExperience maxYearsOfExperience
      hierarchicalJobCategory { id level name __typename }
      skills { skill { id name __typename } mustHave __typename }
      __typename
    }
    expInfo hasMore __typename
  }
}
fragment CompanyFields on Company { id name brandName status isVIP IndustryId industry { id name __typename } __typename }
fragment CityFields on City { id name __typename }
fragment CountryFields on Country { code name __typename }
fragment LocationFields on HierarchicalLocation {
  id name administrativeLevelName formattedName level slug latitude longitude
  parents { id name administrativeLevelName formattedName level slug __typename }
  __typename
}
"""


def load_cookies(cookie_file=None):
    # 1) file JSON
    for p in ([cookie_file] if cookie_file else []) + ["data/glints_cookies.json"]:
        if p and os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    # 2) env header: GLINTS_COOKIE_HEADER = "k1=v1; k2=v2; ..."
    hdr = os.environ.get("GLINTS_COOKIE_HEADER", "")
    if hdr:
        return {p.split("=", 1)[0].strip(): p.split("=", 1)[1].strip()
                for p in hdr.split(";") if "=" in p}
    return {}


def is_in_java(lat, lon):
    if lat is None or lon is None:
        return False
    return JAVA_BOUNDS["lat_min"] <= lat <= JAVA_BOUNDS["lat_max"] and JAVA_BOUNDS["lon_min"] <= lon <= JAVA_BOUNDS["lon_max"]


def fetch_page(page, sort_by, cookies, retries=4, base_delay=5.0):
    payload = {
        "operationName": "searchJobsV3",
        "variables": {"data": {
            "CountryCode": "ID", "includeExternalJobs": True,
            "pageSize": PAGE_SIZE, "page": page, "sortBy": sort_by,
        }},
        "query": GRAPHQL_QUERY,
    }
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(URL, params={"op": "searchJobsV3"}, json=payload,
                                 headers=HEADERS, cookies=cookies, impersonate="chrome124", timeout=30)
            if resp.status_code == 200:
                return resp.json()
            txt = resp.text.lower()
            if "login" in txt or "challenge" in txt or "captcha" in txt or resp.status_code in (403, 429):
                print(f"  [BLOCK] status={resp.status_code} page={page}: {resp.text[:90]}")
                return None
            print(f"  [RETRY] status={resp.status_code} page={page} (attempt {attempt})")
        except Exception as e:
            print(f"  [ERR] page={page}: {e} (attempt {attempt})")
        if attempt < retries:
            wait = base_delay * (2 ** (attempt - 1)) + random.uniform(1, 3)
            print(f"  [WAIT] {wait:.1f}s sebelum retry...")
            time.sleep(wait)
    return None


def parse_jobs(data):
    if not data or "data" not in data or not data["data"].get("searchJobsV3"):
        return []
    out = []
    for j in data["data"]["searchJobsV3"]["jobsInPage"] or []:
        company = j.get("company") or {}
        city = j.get("city") or {}
        loc = j.get("location") or {}
        lat, lon = loc.get("latitude"), loc.get("longitude")
        wa = (j.get("workArrangementOption") or "").upper()
        is_remote = wa in ("REMOTE", "HYBRID") or (lat is None or lon is None)
        out.append({
            "id": j.get("id"), "title": j.get("title"), "company": company.get("name"),
            "city": city.get("name"), "lat": lat, "lon": lon,
            "work_arrangement": wa, "is_remote": is_remote, "is_in_java": is_in_java(lat, lon),
            "source": "glints", "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
    return out


def load_checkpoint(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"ids": [], "pages": {}}


def save_checkpoint(path, ids, pages):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"ids": sorted(ids), "pages": pages}, f)


def crawl(target, out_csv, max_pages_per_mode, resume, cookies):
    raw_path = out_csv.replace(".csv", "_raw.jsonl")
    ckpt_path = out_csv.replace(".csv", "_checkpoint.json")
    ckpt = load_checkpoint(ckpt_path) if resume else {"ids": [], "pages": {}}
    processed = set(ckpt["ids"])
    pages_done = ckpt["pages"]
    total_remote = 0

    for mode in ["RELEVANCE", "LATEST"]:
        if len(processed) >= target:
            break
        page = pages_done.get(mode, 0) + 1
        print(f"\n=== MODE: {mode} (mulai halaman {page}) ===")
        has_more = True
        while has_more and len(processed) < target and page <= max_pages_per_mode:
            data = fetch_page(page, mode, cookies)
            if data is None:
                print(f"[STOP MODE] block di halaman {page}. State tersimpan (--resume).")
                save_checkpoint(ckpt_path, processed, pages_done)
                break
            sj = data.get("data", {}).get("searchJobsV3", {})
            has_more = bool(sj.get("hasMore"))
            jobs = parse_jobs(data)
            if not jobs:
                print(f"halaman {page}: kosong -> mode selesai.")
                break
            new_clean = []
            with open(raw_path, "a", encoding="utf-8") as rf:
                for jb in jobs:
                    jid = jb["id"]
                    if jid in processed:
                        continue
                    processed.add(jid)
                    rf.write(json.dumps(jb, ensure_ascii=False) + "\n")
                    if jb["is_remote"]:
                        total_remote += 1
                    elif jb["is_in_java"]:
                        new_clean.append(jb)
            if new_clean:
                df = pd.DataFrame(new_clean)
                hdr = not os.path.exists(out_csv)
                df.to_csv(out_csv, mode="a", index=False, header=hdr)
            pages_done[mode] = page
            save_checkpoint(ckpt_path, processed, pages_done)
            print(f"[OK] {mode} halaman={page}: +{len(new_clean)} Jawa non-remote | unik={len(processed)} | remote={total_remote} | hasMore={has_more}")
            if not has_more:
                print(f"hasMore=false -> mode {mode} tuntas.")
                break
            time.sleep(random.uniform(2.5, 5.5))
            page += 1

    print("\n" + "=" * 60)
    print(f"SELESAI. unik={len(processed)} | remote/hybrid={total_remote} | clean={out_csv}")
    print("=" * 60)


def main():
    ap = argparse.ArgumentParser(description="Glints Scraper v2 (page-based + cookie)")
    ap.add_argument("--target", type=int, default=10000)
    ap.add_argument("--out", default="data/glints_jobs_v2.csv")
    ap.add_argument("--max-pages", type=int, default=500)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--cookie-file", default=None)
    args = ap.parse_args()

    cookies = load_cookies(args.cookie_file)
    if not cookies:
        print("PERINGATAN: cookie kosong. Halaman 1 mungkin masih bisa, page>=2 akan 403.")
        print("Isi data/glints_cookies.json (dict) atau set env GLINTS_COOKIE_HEADER.")
    else:
        print(f"Cookie dimuat ({len(cookies)} key), session={'session' in cookies}.")
    crawl(args.target, args.out, args.max_pages, args.resume, cookies)


if __name__ == "__main__":
    main()
