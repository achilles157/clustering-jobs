import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

"""
TAHAP 7: VISUALISASI SPASIAL (PETA PELUANG KERJA JAVA)
Penulis: Antigravity AI (Falah's Thesis Assistant)
Deskripsi: Script ini menghasilkan visualisasi peta Pulau Jawa berdasarkan 
           hasil klastering DBSCAN dan Indeks Peluang Kerja.
"""

def main():
    print("Menghasilkan Visualisasi Peta Spasial...")
    
    # 1. Memuat Data Final
    df = pd.read_csv('java_job_market_hubs_final.csv')
    
    # 2. Setup Plot
    plt.figure(figsize=(15, 8))
    sns.set_style("whitegrid")
    
    # 3. Plot Titik Wilayah
    # Warna berdasarkan Clustering, Ukuran berdasarkan Volume Lowongan
    scatter = plt.scatter(
        df['Longitude'], 
        df['Latitude'], 
        c=df['cluster_id'], 
        s=df['job_volume'] * 0.1, # Scaling ukuran titik
        cmap='viridis', 
        alpha=0.6, 
        edgecolors='w', 
        linewidth=0.5,
        label='Wilayah'
    )
    
    # 4. Tambahkan Label untuk Hub Utama
    top_hubs = df.groupby('cluster_id').first().reset_index()
    for _, row in top_hubs.iterrows():
        if row['cluster_id'] == -1: continue
        plt.text(
            row['Longitude'], 
            row['Latitude'], 
            f"Hub {row['cluster_id']}", 
            fontsize=12, 
            fontweight='bold',
            bbox=dict(facecolor='white', alpha=0.5, edgecolor='none')
        )
    
    # 5. Dekorasi Peta
    plt.title('Pemetaan Hub Ekonomi Spasial Pulau Jawa (Hasil DBSCAN)', fontsize=16, pad=20)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    
    # Tambahkan Legend Manual untuk Konteks
    plt.figtext(0.15, 0.2, "* Ukuran titik = Volume Lowongan\n* Warna = Identitas Klaster (Hub)", 
                fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
    
    # 6. Simpan Gambar
    output_image = r'c:\Users\Falah\Documents\clustering-jobs\peta_spasial_java_final.png'
    plt.savefig(output_image, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Visualisasi berhasil disimpan di: {output_image}")

if __name__ == "__main__":
    main()
