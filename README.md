## Judul Proyek + Deskripsi Singkat

**Superstore BI Dashboard** adalah aplikasi web business intelligence yang dibangun dengan framework Dash untuk menganalisis data penjualan superstore.   Sistem ini menyediakan visualisasi interaktif dan insight analitik untuk performa penjualan, perilaku pelanggan, analisis regional, dan optimasi profit melalui antarmuka web modern dengan koneksi ke data warehouse PostgreSQL.

## Fitur Utama Aplikasi

Berdasarkan analisis struktur aplikasi, dashboard ini memiliki fitur-fitur berikut:

- **Sales Overview Dashboard** - Menampilkan metrik kunci seperti total sales, profit, orders, dan rata-rata diskon 
- **Analisis Regional** - Peta geografis dan breakdown berdasarkan state/city untuk analisis berbasis lokasi
- **Customer Analytics** - Segmentasi pelanggan dan analisis customer lifetime value  
- **Profit Analysis** - Analisis diskon, tracking margin, dan optimasi profitabilitas
- **Navigasi Sidebar Interaktif** - Sistem navigasi dengan 4 halaman utama 
- **Visualisasi Interaktif** - Charts dan grafik menggunakan Plotly untuk analisis data
- **Real-time Data Loading** - Koneksi langsung ke PostgreSQL dengan caching data 

## Struktur Folder Proyek

```
dashboard-superstore/
├── app.py                          # Main application entry point
├── draft.py                        # Alternative self-contained implementation  
├── src/
│   ├── components/
│   │   ├── pages/
│   │   │   ├── overview.py         # Sales overview page
│   │   │   ├── region.py           # Regional analysis page
│   │   │   ├── customer.py         # Customer analytics page
│   │   │   └── profit.py           # Profit analysis page
│   │   └── sidebar.py              # Navigation sidebar component
│   ├── config/
│   │   ├── database.py             # Database connection config
│   │   └── styles.py               # UI styling configuration
│   └── data/
│       └── data_loader.py          # Data loading and ETL functions
```

## Cara Instalasi & Menjalankan Aplikasi

1. **Clone Repository**
   ```bash
   git clone https://github.com/cikinodapz/dashboard-superstore.git
   cd dashboard-superstore
   ```

2. **Install Dependencies**
   ```bash
   pip install dash pandas plotly psycopg2-binary
   ```

3. **Setup Database**
   - Pastikan PostgreSQL sudah terinstall dan running
   - Buat database `dwh_superstore2` dengan tabel dimensi dan fakta yang diperlukan

4. **Konfigurasi Database**
   - Update konfigurasi koneksi database di `src/config/database.py`

5. **Jalankan Aplikasi**
   ```bash
   python app.py
   ```
   
6. **Akses Dashboard**
   - Buka browser dan akses `http://localhost:8050` 

## Teknologi yang Digunakan

### Framework & Library Utama:
- **Dash** - Framework web Python untuk aplikasi analitik 
- **Plotly** - Library visualisasi interaktif 
- **Pandas** - Data manipulation dan analisis 

### Database & Data Processing:
- **PostgreSQL** - Database utama dengan skema star schema
- **psycopg2** - PostgreSQL adapter untuk Python
- **Data Warehouse** - Implementasi dimensional modeling dengan fact dan dimension tables 

### UI & Styling:
- **HTML/CSS** - Custom styling dengan gradient themes
- **Responsive Design** - Layout adaptif menggunakan CSS Grid dan Flexbox

### Arsitektur:
- **Modular Architecture** - Pemisahan komponen berdasarkan fungsi
- **Callback System** - Sistem reaktif Dash untuk update dinamis 
- **ETL Pipeline** - Extract, Transform, Load data dari PostgreSQL ke pandas DataFrames

## Notes

Dashboard ini menggunakan arsitektur modular dengan dua implementasi: `app.py` sebagai implementasi utama yang modular, dan `draft.py` sebagai alternatif self-contained. Sistem menggunakan global variables untuk caching data dan menghindari query database berulang. Aplikasi mendukung mode development dengan debug enabled dan dapat di-deploy untuk production.

