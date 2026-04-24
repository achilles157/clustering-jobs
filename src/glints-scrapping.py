import pandas as pd
from curl_cffi import requests
import json
import time
import random
import os

# --- CONFIGURATION ---
# Pastikan cookie ini masih valid (bisa diambil dari Network tab di browser jika error 403 berlanjut)
COOKIES = {
    '_ga': 'GA1.1.1328477191.1757320700',
    '_tt_enable_cookie': '1',
    '_ttp': '01K4M7KR2T1D2ZZEJ4QEWRR9HQ_.tt.1',
    'device_id': '28f9c5ad-ce22-40f6-892e-7a18f92e0754',
    'session': 'Fe26.2**b89deca7cf137d23ec2ef497c60ad08f621b6d6e887f98780c2b64bd4cce1cc2*kkHrIr7Wk9_ggsXnAHovqg*AJ4WxhZCuZf1GBTp2dHq-gizuG6G67Cy1rEJjN6xJilnvea7uu4tBz0Z0rga1FBk**4d47cb9068861434bc2f6d18ecf0433815c945000a5b52e05ab8c5c7a3adfcec*n3H9n6mgEmudXxiRKC2SMRjwgKOvEc-UeW6tDZDU9kg',
    'glints_tracking_id': '99934d5b-7c49-495e-8e19-989513ffc727',
}

HEADERS = {
    'accept': '*/*',
    'accept-language': 'en',
    'content-type': 'application/json',
    'origin': 'https://glints.com',
    'referer': 'https://glints.com/id/en/opportunities/jobs/explore?country=ID&locationName=All%20Cities%2FProvinces',
    'x-glints-country-code': 'ID',
}

# --- GEOGRAPHICAL FILTER (Pulau Jawa) ---
# Batas koordinat kasar Pulau Jawa (Bounding Box)
JAVA_BOUNDS = {
    'lat_min': -9.0,
    'lat_max': -5.8,
    'lon_min': 105.0,
    'lon_max': 115.0
}

def is_in_java(lat, lon):
    """Mengecek apakah koordinat berada di range Pulau Jawa."""
    if lat is None or lon is None:
        return False
    return (JAVA_BOUNDS['lat_min'] <= lat <= JAVA_BOUNDS['lat_max'] and 
            JAVA_BOUNDS['lon_min'] <= lon <= JAVA_BOUNDS['lon_max'])

GRAPHQL_QUERY = """
query searchJobsV3($data: JobSearchConditionInput!) {
  searchJobsV3(data: $data) {
    jobsInPage {
      id
      title
      workArrangementOption
      status
      createdAt
      updatedAt
      isHot
      isApplied
      shouldShowSalary
      educationLevel
      type
      fraudReportFlag
      salaryEstimate {
        minAmount
        maxAmount
        CurrencyCode
        __typename
      }
      company {
        ...CompanyFields
        __typename
      }
      citySubDivision {
        id
        name
        __typename
      }
      city {
        ...CityFields
        __typename
      }
      country {
        ...CountryFields
        __typename
      }
      salaries {
        ...SalaryFields
        __typename
      }
      location {
        ...LocationFields
        __typename
      }
      minYearsOfExperience
      maxYearsOfExperience
      source
      jobSource
      type
      hierarchicalJobCategory {
        id
        level
        name
        children {
          name
          level
          id
          __typename
        }
        parents {
          id
          level
          name
          __typename
        }
        __typename
      }
      skills {
        skill {
          id
          name
          __typename
        }
        mustHave
        __typename
      }
      traceInfo
      __typename
    }
    expInfo
    hasMore
    __typename
  }
}

fragment CompanyFields on Company {
  id
  name
  brandName
  logo
  status
  isVIP
  IndustryId
  industry {
    id
    name
    __typename
  }
  verificationTier {
    type
    userName
    __typename
  }
  __typename
}

fragment CityFields on City {
  id
  name
  __typename
}

fragment CountryFields on Country {
  code
  name
  __typename
}

fragment SalaryFields on JobSalary {
  id
  salaryType
  salaryMode
  maxAmount
  minAmount
  CurrencyCode
  __typename
}

fragment LocationFields on HierarchicalLocation {
  id
  name
  administrativeLevelName
  formattedName
  level
  slug
  latitude
  longitude
  parents {
    id
    name
    administrativeLevelName
    formattedName
    level
    slug
    CountryCode: countryCode
    parents {
      level
      formattedName
      slug
      __typename
    }
    __typename
  }
  __typename
}
"""

def fetch_glints_jobs(page=1, page_size=30, sort_by="RELEVANCE"):
    """
    Mengambil data lowongan dari Glints menggunakan curl_cffi untuk melewati Cloudflare.
    """
    url = 'https://glints.com/api/v2-alc/graphql'
    
    payload = {
        'operationName': 'searchJobsV3',
        'variables': {
            'data': {
                'CountryCode': 'ID',
                'includeExternalJobs': True,
                'pageSize': page_size,
                'page': page,
                'sortBy': sort_by
            },
        },
        'query': GRAPHQL_QUERY
    }

    params = {'op': 'searchJobsV3'}

    try:
        # Menggunakan impersonate="chrome110" untuk meniru sidik jari browser Chrome
        response = requests.post(
            url, 
            params=params, 
            json=payload, 
            headers=HEADERS, 
            cookies=COOKIES,
            impersonate="chrome110",
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Gagal mengambil data! Status: {response.status_code}")
            if "challenge" in response.text or "captcha" in response.text.lower():
                print("Terdeteksi tantangan Cloudflare (CAPTCHA). Coba perbarui cookie Anda.")
            return None
    except Exception as e:
        print(f"Terjadi kesalahan saat request: {e}")
        return None

def parse_jobs(data):
    """
    Memproses raw JSON menjadi list dictionary yang rapi.
    """
    if not data or 'data' not in data or not data['data']['searchJobsV3']:
        return []
        
    jobs_raw = data['data']['searchJobsV3']['jobsInPage']
    parsed_jobs = []
    
    for job in jobs_raw:
        skills = [s['skill']['name'] for s in job.get('skills', []) if s and s.get('skill')]
        
        company = job.get('company') or {}
        city = job.get('city') or {}
        location = job.get('location') or {}
        salaryEstimate = job.get('salaryEstimate') or {}
        
        parsed_jobs.append({
            "id": job.get('id'),
            "title": job.get('title'),
            "company": company.get('name'),
            "city": city.get('name'),
            "lat": location.get('latitude'),
            "lon": location.get('longitude'),
            "min_exp": job.get('minYearsOfExperience'),
            "skills": ", ".join(skills),
            "salary_min": salaryEstimate.get('minAmount') if salaryEstimate else 0
        })
    return parsed_jobs

def main():
    TARGET_TOTAL = 1500
    CSV_FILE = "glints_jobs_results.csv"
    PAGE_SIZE = 30
    SORT_MODES = ["RELEVANCE", "LATEST", "SALARY_DESC"]
    
    # Hapus file lama jika ada (Clean Start)
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
        print(f"File {CSV_FILE} lama dihapus. Mulai dari nol.")

    processed_ids = set()
    java_jobs_count = 0
    
    print(f"Memulai Scraping Target ~{TARGET_TOTAL} lowongan di Pulau Jawa menggunakan Sort Sharding...")
    
    for mode in SORT_MODES:
        if java_jobs_count >= TARGET_TOTAL:
            break
            
        print(f"\n" + "="*20)
        print(f"SHARDING MODE: {mode}")
        print("="*20)
        
        current_page = 1
        has_more = True
        
        while has_more and java_jobs_count < TARGET_TOTAL:
            print(f"--- {mode} | Halaman {current_page} ---")
            raw_data = fetch_glints_jobs(page=current_page, page_size=PAGE_SIZE, sort_by=mode)
            
            if not raw_data:
                print("Gagal mengambil data atau terkena blokir. Lanjut ke mode sort berikutnya.")
                break
                
            # Update has_more dari API
            has_more = raw_data.get('data', {}).get('searchJobsV3', {}).get('hasMore', False)
            
            jobs_list = parse_jobs(raw_data)
            if not jobs_list:
                print("Halaman ini kosong. Lanjut ke mode sort berikutnya.")
                break
                
            # Filter unik dan masuk Pulau Jawa
            new_java_jobs = []
            for job in jobs_list:
                job_id = job.get('id')
                lat = job.get('lat')
                lon = job.get('lon')
                if job_id not in processed_ids and is_in_java(lat, lon):
                    processed_ids.add(job_id)
                    new_java_jobs.append(job)
            
            if new_java_jobs:
                df_page = pd.DataFrame(new_java_jobs)
                
                # Save incrementally (Append Mode)
                file_exists = os.path.isfile(CSV_FILE)
                df_page.to_csv(CSV_FILE, mode='a', index=False, header=not file_exists)
                
                java_jobs_count = len(processed_ids)
                
                print(f"[OK] Ditemukan {len(new_java_jobs)} data baru di Jawa.")
                print(f"Progress Unique Jawa: {java_jobs_count} / {TARGET_TOTAL}")
            else:
                print(f"Halaman {current_page}: Tidak ada data baru yang unik di Pulau Jawa.")

            if not has_more or current_page >= 33: # Stop pada pagination wall
                print(f"Batas pagination untuk mode {mode} tercapai.")
                break

            # Stealth Delay
            delay = random.uniform(4.0, 9.0)
            print(f"Menunggu {delay:.2f} detik (Stealth Mode)...")
            time.sleep(delay)
            
            current_page += 1

    print("\n" + "="*40)
    print(f"Scraping Selesai!")
    print(f"Total Data Unik Jawa Tersimpan: {java_jobs_count}")
    print(f"File: {CSV_FILE}")
    print("="*40)

if __name__ == "__main__":
    main()