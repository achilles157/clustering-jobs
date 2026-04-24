import pandas as pd
import os
import glob

def extract_cities():
    bps_dir = "data-bps"
    files = glob.glob(os.path.join(bps_dir, "*.csv"))
    
    all_cities = []
    
    for file in files:
        print(f"Processing {os.path.basename(file)}...")
        # BPS files usually have Kabupaten/Kota in the first column
        # and sometimes have a total row at the end (e.g. "Banten").
        try:
            df = pd.read_csv(file)
            column_name = df.columns[0]
            cities = df[column_name].tolist()
            
            # Clean results:
            # 1. Remove the last row if it matches the province name (total row)
            # 2. Strip whitespace
            prov_name = os.path.basename(file).split("Provinsi ")[1].split(",")[0]
            cities = [c.strip() for c in cities if isinstance(c, str) and prov_name not in c]
            
            all_cities.extend(cities)
        except Exception as e:
            print(f"Error reading {file}: {e}")
            
    # Deduplicate and sort
    all_cities = sorted(list(set(all_cities)))
    
    with open("java_cities_list.txt", "w") as f:
        for city in all_cities:
            f.write(f"{city}\n")
            
    print(f"Extracted {len(all_cities)} unique cities/regencies to java_cities_list.txt")

if __name__ == "__main__":
    extract_cities()
