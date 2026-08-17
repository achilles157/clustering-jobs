#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper: ubah cURL/cookie hasil paste dari user -> data/glints_cookies.json

Pemakaian:
  1. User paste cURL (Copy as cURL) atau baris `cookie:` ke data/glints_cookie_raw.txt
  2. python src/glints_cookie_setup.py
  3. Output: data/glints_cookies.json (dict cookie) + preview termaskir
"""
import json
import os
import re
import sys

RAW_PATH = "data/glints_cookie_raw.txt"
OUT_PATH = "data/glints_cookies.json"


def parse_cookie_dict(text):
    """Ambil pasangan key=value cookie dari cURL atau raw header."""
    # pola -H 'cookie: ...' atau -b '...' atau baris 'cookie: ...'
    m = re.search(r"(?:-H\s+['\"]?cookie:\s*|--header\s+['\"]?cookie:\s*|^-b\s+['\"]?|^cookie:\s*)", text, re.I | re.M)
    cookie_str = None
    if m:
        cookie_str = text[m.end():].split("'")[0].split('"')[0].strip()
        # hentikan pada tanda kutip berikutnya / baris baru
        cookie_str = re.split(r"['\"\n]", cookie_str)[0].strip()
    else:
        # fallback: seluruh teks dianggap header cookie
        cookie_str = text.strip()
    cookies = {}
    for part in cookie_str.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            k, v = k.strip(), v.strip()
            if k:
                cookies[k] = v
    return cookies


def mask(v):
    if v is None:
        return "(kosong)"
    if len(v) <= 8:
        return v[:2] + "..." + v[-2:]
    return v[:4] + "..." + v[-4:]


def main():
    if not os.path.exists(RAW_PATH):
        print(f"File {RAW_PATH} tidak ditemukan. Paste cURL/cookie dulu ke file itu.")
        sys.exit(1)
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    cookies = parse_cookie_dict(text)
    if not cookies:
        print("Gagal mem-parse cookie dari file. Pastikan isinya cURL atau baris cookie:.")
        sys.exit(1)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2)
    print(f"OK. {len(cookies)} key cookie disimpan ke {OUT_PATH}")
    print("Preview (termaskir):")
    for k, v in cookies.items():
        print(f"  {k:24s} = {mask(v)}")
    has_session = "session" in cookies
    print(f"\nstatus: session cookie {'ADA' if has_session else 'TIDAK ADA'} — "
          f"{'siap crawl' if has_session else 'periksa lagi, pastikan login & copy cookie lengkap'}")


if __name__ == "__main__":
    main()
