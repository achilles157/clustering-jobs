import pandas as pd
import glob
import os

"""
TAHAP 2.1: KONSOLIDASI DATA BPS
Penulis: Antigravity AI (Falah's Thesis Assistant)
Deskripsi: Script ini menggabungkan 6 file CSV sosio-ekonomi dari tingkat provinsi 
           menjadi satu dataset master Kabupaten/Kota se-Pulau Jawa.
"""

def main():
    print("Memulai Konsolidasi Data BPS...")
    
    # Path folder data mentah
    data_path = 'data-bps/*.csv'
    files = glob.glob(data_path)
    
    all_data = []
    
    for f in files:
        # Mengambil nama provinsi dari nama file
        provinsi = os.path.basename(f).split('di Provinsi ')[-1].split(',')[0].strip()
        print(f"Memproses Provinsi: {provinsi}")
        
        # Membaca data dengan encoding yang sesuai
        df = pd.read_csv(f)
        df['Provinsi'] = provinsi
        all_data.append(df)
    
    # Menggabungkan semua data
    master_df = pd.concat(all_data, ignore_index=True)
    
    # Pembersihan Nama Kabupaten/Kota (Menghilangkan angka awalan jika ada)
    # Beberapa data BPS memiliki format [3171] Kota Jakarta Pusat
    def clean_name(name):
        if not isinstance(name, str): return name
        import re
        return re.sub(r'\[.*?\]\s*', '', name).strip()

    master_df['Kabupaten/Kota'] = master_df['Kabupaten/Kota'].apply(clean_name)
    
    # Simpan ke Master CSV
    output_file = 'master_bps_socioeconomic.csv'
    master_df.to_csv(output_file, index=False)
    
    print(f"Berhasil! Master data BPS disimpan di: {output_file}")
    print(f"Total baris data: {len(master_df)}")

if __name__ == "__main__":
    main()
