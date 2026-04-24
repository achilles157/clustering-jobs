import pandas as pd
from curl_cffi import requests
import json
import time
import random
import os

# --- SECURITY UPDATE ---
# DILARANG MENGUNGGAH SCRIPT INI DENGAN COOKIE/TOKEN ASLI (HARDCODED) KE GITHUB!
# Silakan isi variabel ini secara lokal, atau gunakan Environment Variables (.env)
COOKIES = {
    # 'sol_id': 'YOUR_SOL_ID_HERE',
    # '_ga': 'YOUR_GA_COOKIE_HERE',
    # Isi dengan lengkap sesuai hasil inspeksi browser Anda
}

TOKEN = os.getenv('JOBSTREET_BEARER_TOKEN', 'Bearer ISI_TOKEN_ANDA_DISINI')

HEADERS = {
    'accept': '*/*',
    'accept-language': 'id,en-US;q=0.9,en;q=0.8',
    'authorization': TOKEN,
    'content-type': 'application/json',
    'origin': 'https://id.jobstreet.com',
    'seek-request-brand': 'jobstreet',
    'seek-request-country': 'ID',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    'x-custom-features': 'application/features.seek.all+json',
    'x-seek-ec-sessionid': '68118828-ac73-4ce8-b23f-6e4cb00522ef',
    'x-seek-ec-visitorid': '68118828-ac73-4ce8-b23f-6e4cb00522ef',
    'x-seek-site': 'chalice',
}

GRAPHQL_QUERY = """
query JobSearchV6($params: JobSearchV6QueryInput!, $locale: Locale!, $timezone: Timezone!) {
  jobSearchV6(params: $params) {
    data {
      id
      title
      companyName
      locations { label }
      listingDate { dateTimeUtc }
      salaryLabel
      advertiser { id }
    }
    totalCount
  }
}
"""

REMAINING_CITIES = [
    'Bekasi','Blitar','Blora','Bogor','Bojonegoro','Bondowoso','Boyolali','Brebes',
    'Ciamis','Cianjur','Cilacap','Cirebon','Demak','Garut','Gresik','Grobogan',
    'Gunung Kidul','Indramayu','Jember','Jepara','Jombang','Karanganyar','Karawang',
    'Kebumen','Kediri','Kendal','Kepulauan Seribu','Klaten','Kota Bandung','Kota Banjar',
    'Kota Batu','Kota Bekasi','Kota Blitar','Kota Bogor','Kota Cilegon','Kota Cimahi',
    'Kota Cirebon','Kota Depok','Kota Jakarta Barat','Kota Jakarta Pusat','Kota Jakarta Selatan',
    'Kota Jakarta Timur','Kota Jakarta Utara','Kota Kediri','Kota Madiun','Kota Magelang',
    'Kota Malang','Kota Mojokerto','Kota Pasuruan','Kota Pekalongan','Kota Probolinggo',
    'Kota Salatiga','Kota Semarang','Kota Serang','Kota Sukabumi','Kota Surabaya',
    'Kota Surakarta','Kota Tangerang','Kota Tangerang Selatan','Kota Tasikmalaya',
    'Kota Tegal','Kota Yogyakarta','Kudus','Kulon Progo','Kuningan','Lamongan','Lebak',
    'Lumajang','Madiun','Magelang','Magetan','Majalengka','Malang','Mojokerto',
    'Nganjuk','Ngawi','Pacitan','Pamekasan','Pandeglang','Pangandaran','Pasuruan',
    'Pati','Pekalongan','Pemalang','Ponorogo','Probolinggo','Purbalingga','Purwakarta',
    'Purworejo','Rembang','Sampang','Semarang','Serang','Sidoarjo','Situbondo',
    'Sleman','Sragen','Subang','Sukabumi','Sukoharjo','Sumedang','Sumenep',
    'Tangerang','Tasikmalaya','Tegal','Temanggung','Trenggalek','Tuban',
    'Tulungagung','Wonogiri','Wonosobo'
]

def fetch_jobstreet_graphql(city_name, page=1):
    print(f"Fetching {city_name} (Page {page})...")
    track_id = '68118828-ac73-4ce8-b23f-6e4cb00522ef'
    sol_id = '557804bc-2c1e-4931-8681-c5cef48a8616'
    json_data = {
        'operationName': 'JobSearchV6',
        'variables': {
            'params': {
                'channel': 'mobileWeb', 'locale': 'id-ID', 'page': page, 'pageSize': 50,
                'siteKey': 'ID', 'where': city_name, 'sortMode': 'ListedDate',
                'eventCaptureSessionId': track_id, 'eventCaptureUserId': track_id,
                'userSessionId': track_id, 'solId': sol_id, 'include': ['seoData', 'gptTargeting'],
                'source': 'FE_SERP', 'queryHints': ['spellingCorrection'],
                'userQueryId': 'd751713988987e9331980363e24189ce-5980839'
            },
            'locale': 'id-ID', 'timezone': 'Asia/Jakarta',
        },
        'query': GRAPHQL_QUERY,
    }
    try:
        response = requests.post('https://id.jobstreet.com/graphql', cookies=COOKIES, headers=HEADERS, json=json_data, impersonate="chrome110", timeout=30)
        if response.status_code == 200: return response.json()
        elif response.status_code == 403: return "BLOCKED"
        return None
    except: return None

def parse(resp_json):
    if not resp_json or "errors" in resp_json: return [], 0
    try:
        s = resp_json.get('data', {}).get('jobSearchV6', {})
        if not s: return [], 0
        jobs = s.get('data', [])
        total = s.get('totalCount', 0)
        parsed = []
        for j in jobs:
            loc = j.get('locations', [])
            label = loc[0].get('label') if loc else ""
            parsed.append({
                "id": str(j.get('id')), "title": j.get('title'),
                "company": j.get('companyName'), "location": label,
                "listingDate": j.get('listingDate', {}).get('dateTimeUtc'),
                "salary": j.get('salaryLabel'), "advertiser_id": j.get('advertiser', {}).get('id')
            })
        return parsed, total
    except: return [], 0

def main():
    CSV = "jobstreet_results.csv"
    processed = set()
    if os.path.exists(CSV):
        try:
            df_existing = pd.read_csv(CSV)
            # FORCE CLEAN EXISTING ON START
            df_existing.drop_duplicates(subset=['id'], keep='first', inplace=True)
            df_existing.to_csv(CSV, index=False)
            processed = set(df_existing['id'].astype(str).tolist())
            print(f"Loaded and verified {len(processed)} unique existing jobs.")
        except: pass

    for city in REMAINING_CITIES:
        print(f"\nRESUMING: {city}")
        page = 1
        has_more = True
        while has_more:
            resp = fetch_jobstreet_graphql(city, page)
            if resp == "BLOCKED": 
                print("BLOCKED - Stopping.")
                return
            if not resp: break
            jobs, total = parse(resp)
            if not jobs: break
            
            # STRICT DEDUPLICATION: Memory filter
            new_jobs = [j for j in jobs if j['id'] not in processed]
            
            if new_jobs:
                df_new = pd.DataFrame(new_jobs)
                # STRICT DEDUPLICATION: Batch filter
                df_new.drop_duplicates(subset=['id'], keep='first', inplace=True)
                
                df_new.to_csv(CSV, mode='a', index=False, header=not os.path.exists(CSV))
                for j in new_jobs: processed.add(j['id'])
                print(f"[NEW] Page {page}: Saved {len(df_new)} (Total Unique: {len(processed)})")
            else:
                print(f"[SKIP] Page {page}: No new data.")
            
            pages_needed = (total // 50) + (1 if total % 50 > 0 else 0)
            if page >= pages_needed or page >= 40: has_more = False
            else:
                time.sleep(random.uniform(3, 7))
                page += 1

if __name__ == "__main__":
    main()
