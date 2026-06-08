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
    
    # Pembersihan kolom sosio-ekonomi (numerik)
    def clean_bps_val(val):
        import re
        if pd.isna(val):
            return 0
        val_str = str(val).strip()
        
        # Hapus catatan kaki seperti " (a)"
        val_str = re.sub(r'\s*\(.*?\)', '', val_str)
        if not val_str or val_str.lower() == 'nan':
            return 0
            
        # Periksa format tanggal Excel (seperti 1/7/90 atau 1/20/62)
        if '/' in val_str:
            parts = val_str.split('/')
            if len(parts) == 3:
                millions = parts[0]
                thousands = parts[1].zfill(3)
                units = parts[2].zfill(3)
                return float(f"{millions}{thousands}{units}")
                
        # Hapus tanda koma
        val_str = val_str.replace(',', '')
        
        # Periksa separator titik
        if '.' in val_str:
            parts = val_str.split('.')
            if len(parts) > 2:
                # Titik ganda seperti 1.007.090
                return float("".join(parts))
            elif len(parts) == 2:
                # Titik tunggal seperti 569.654 atau 385.8
                if len(parts[1]) == 3:
                    return float("".join(parts))
                elif len(parts[1]) < 3:
                    # Desimal ribuan seperti 385.8 -> 385800
                    padded_right = parts[1].ljust(3, '0')
                    return float(f"{parts[0]}{padded_right}")
                else:
                    return float("".join(parts))
        else:
            try:
                val_float = float(val_str)
                # Koreksi untuk nilai integer bulat kecil (seperti 133 untuk Kota Probolinggo)
                # yang dibulatkan oleh Excel dari ribuan murni (133.000 -> 133)
                if 0 < val_float < 5000:
                    return val_float * 1000
                return val_float
            except ValueError:
                return 0

    # Terapkan pembersihan numerik ke semua kolom kecuali nama wilayah dan provinsi
    for col in master_df.columns:
        if col not in ['Kabupaten/Kota', 'Provinsi']:
            master_df[col] = master_df[col].apply(clean_bps_val)
    
    # Simpan ke Master CSV (di folder data)
    os.makedirs('data', exist_ok=True)
    output_file = os.path.join('data', 'master_bps_socioeconomic.csv')
    master_df.to_csv(output_file, index=False)
    
    print(f"Berhasil! Master data BPS disimpan di: {output_file}")
    print(f"Total baris data: {len(master_df)}")

if __name__ == "__main__":
    main()
