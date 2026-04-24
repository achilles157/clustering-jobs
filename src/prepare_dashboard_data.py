import json
import os
import pandas as pd

def filter_java_geojson():
    """
    Filters the national GeoJSON for Java provinces and cleans property names.
    Uses 'WADMKK' as the identifier for Kabupaten/Kota.
    """
    input_path = os.path.join('data', '38 Provinsi Indonesia - Kabupaten.json')
    output_path = os.path.join('data', 'java_regencies.geojson')
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    print(f"Reading national GeoJSON from {input_path}...")
    with open(input_path, 'r') as f:
        data = json.load(f)

    java_provinces = [
        "Jawa Barat", "Jawa Tengah", "Jawa Timur", 
        "Banten", "DKI Jakarta", "Daerah Istimewa Yogyakarta"
    ]
    
    # Filter features based on WADMPR
    filtered_features = []
    seen_regencies = set()
    
    for feature in data['features']:
        props = feature.get('properties', {})
        prov = props.get('WADMPR', '')
        regency = props.get('WADMKK', '')
        
        if prov and any(p in prov for p in java_provinces):
            if regency:
                # Better matching logic:
                # "KABUPATEN BANDUNG" -> "Bandung"
                # "KOTA BANDUNG" -> "Kota Bandung"
                regency = regency.upper()
                if 'JAKARTA' in regency:
                    # "KOTA ADMINISTRASI JAKARTA SELATAN" -> "Kota Jakarta Selatan"
                    clean_name = regency.replace('ADMINISTRASI', '').replace('  ', ' ').strip().title()
                elif regency.startswith('KABUPATEN'):
                    # Formal: "Kabupaten Bandung"
                    clean_name = regency.strip().title()
                elif regency.startswith('KOTA'):
                    clean_name = regency.strip().title()
                else:
                    clean_name = regency.strip().title()
                
                feature['properties']['clean_name'] = clean_name
                filtered_features.append(feature)
                seen_regencies.add(clean_name)
            
    filtered_data = {
        "type": "FeatureCollection",
        "features": filtered_features
    }
    
    with open(output_path, 'w') as f:
        json.dump(filtered_data, f)
        
    print(f"Successfully saved {len(filtered_features)} features to {output_path}")
    print(f"Unique Regencies found: {len(seen_regencies)}")

if __name__ == "__main__":
    filter_java_geojson()
