import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

"""
TAHAP 2.2: GEOCODING KABUPATEN/KOTA
Penulis: Antigravity AI (Falah's Thesis Assistant)
Deskripsi: Script ini mengambil koordinat (Latitude & Longitude) pusat wilayah 
           untuk 119 Kabupaten/Kota di Pulau Jawa menggunakan OpenStreetMap (Nominatim).
"""

def main():
    print("Memulai Proses Geocoding...")
    
    # 1. Membaca daftar kota yang sudah disiapkan dari BPS
    try:
        with open('java_cities_list.txt', 'r') as f:
            cities = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: file java_cities_list.txt tidak ditemukan.")
        return

    # 2. Inisialisasi Geolocator
    geolocator = Nominatim(user_agent="skripsi_clustering_java")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    results = []
    
    print(f"Mengambil koordinat untuk {len(cities)} wilayah...")
    for city in cities:
        # Menambahkan konteks agar pencarian lebih akurat
        search_query = f"{city}, Indonesia"
        try:
            location = geocode(search_query)
            if location:
                results.append({
                    "City_Name": city,
                    "Latitude": location.latitude,
                    "Longitude": location.longitude
                })
                print(f"[OK] {city}: {location.latitude}, {location.longitude}")
            else:
                print(f"[FAILED] {city}: Tidak ditemukan.")
        except Exception as e:
            print(f"[ERROR] {city}: {str(e)}")
            time.sleep(2) # Backoff jika ada error jaringan

    # 3. Simpan ke CSV
    output_df = pd.DataFrame(results)
    output_file = 'java_regency_coordinates.csv'
    output_df.to_csv(output_file, index=False)
    
    print(f"\nProses Selesai! Koordinat disimpan di: {output_file}")

if __name__ == "__main__":
    main()
