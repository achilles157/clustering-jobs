import requests
import json
import os

def download_and_filter_geojson():
    url = "https://raw.githubusercontent.com/TheMaggieSimpson/IndonesiaGeoJSON/main/kota-kabupaten.json"
    print(f"Fetching GeoJSON from {url}...")
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch GeoJSON. Status code: {response.status_code}")
        return

    data = response.json()
    
    java_provinces = [
        "Jawa Barat", "Jawa Tengah", "Jawa Timur", 
        "Banten", "Jakarta Raya", "Yogyakarta"
    ]
    
    # Filter features based on NAME_1
    filtered_features = []
    for feature in data['features']:
        prov = feature['properties'].get('NAME_1', '')
        if prov in java_provinces:
            filtered_features.append(feature)
            
    filtered_data = {
        "type": "FeatureCollection",
        "features": filtered_features
    }
    
    with open('java_regencies.geojson', 'w') as f:
        json.dump(filtered_data, f)
        
    print(f"Successfully saved {len(filtered_features)} regencies to java_regencies.geojson")

if __name__ == "__main__":
    download_and_filter_geojson()
