# Peta Interaktif Keadilan Spasial Akses Bahan Baku PKL Surabaya

Aplikasi WebGIS low-code (Streamlit + Folium) untuk mempublikasikan hasil
analisis blank spot & rekomendasi lokasi pasar satelit dari QGIS.

## Isi folder
- `app.py` — aplikasi utama Streamlit
- `generate_sample_data.py` — pembuat data CONTOH (dummy), hanya untuk uji coba
- `data/` — folder GeoJSON (isi awal: data contoh)
- `requirements.txt` — daftar library untuk deploy

## 1. Menyiapkan data ASLI dari QGIS
Ganti data contoh dengan hasil analisis Anda sendiri. Di QGIS:

1. Klik kanan layer → **Export → Save Features As...**
2. Format: **GeoJSON**, CRS: **EPSG:4326 (WGS 84)** (wajib, agar sesuai lat/long web)
3. Simpan dengan nama sesuai kebutuhan, lalu taruh di folder `data/` dengan
   menimpa file yang sesuai:

   | Layer | Nama file | Field wajib ada |
   |---|---|---|
   | Pasar Tradisional (titik) | `data/pasar.geojson` | `nama`, `jam_operasional`, `kapasitas` |
   | Buffer 3 KM (poligon) | `data/buffer_3km.geojson` | (bebas) |
   | Klaster PKL Terlayani (poligon) | `data/klaster_terlayani.geojson` | `nama_kawasan`, `jumlah_pkl`, `status_akses` |
   | Blank Spot (poligon) | `data/blank_spot.geojson` | `nama_kawasan`, `jumlah_pkl`, `status_akses` |
   | Rekomendasi Pasar Satelit (titik) | `data/rekomendasi.geojson` | `nama`, `alasan` |
   | Jalan Utama (garis, opsional) | `data/jalan_utama.geojson` | (bebas) |

   Jika nama kolom di data Anda berbeda, cukup sesuaikan nama field pada
   fungsi `safe_get(...)` di `app.py` (baris-baris di bagian popup), atau
   ganti nama kolom di data Anda agar cocok.

   **Alternatif tanpa edit file**: jalankan aplikasinya lalu upload GeoJSON
   langsung lewat panel sidebar — tidak perlu mengganti file di folder `data/`.

## 2. Menjalankan di komputer sendiri
```bash
pip install -r requirements.txt
streamlit run app.py
```
Aplikasi akan terbuka otomatis di browser (`http://localhost:8501`).

## 3. Publikasi gratis ke Streamlit Community Cloud
1. Buat repository baru di GitHub, upload semua isi folder ini
   (`app.py`, `requirements.txt`, folder `data/`, dst).
2. Buka https://share.streamlit.io/ , login dengan akun GitHub.
3. Klik **New app**, pilih repository dan branch Anda, lalu set:
   - **Main file path**: `app.py`
4. Klik **Deploy**. Setelah beberapa menit, Anda akan mendapatkan URL publik
   (formatnya `https://nama-app-anda.streamlit.app`) yang bisa dibagikan ke
   Dinas Koperasi & UMKM / Bappeda dan bisa dibuka langsung dari HP/laptop
   tanpa instalasi QGIS.

## 4. Cara memenuhi tiap poin tugas di aplikasi ini
- **Styling & Simbolisasi**: sudah diatur di `app.py` — pasar (biru),
  buffer (biru muda transparan), klaster terlayani (hijau), blank spot
  (merah), rekomendasi (bintang oranye).
- **Popup Info**: setiap layer punya popup dengan atribut sesuai instruksi
  tugas (nama pasar/jam/kapasitas; nama kawasan/jumlah PKL/status akses;
  alasan rekomendasi).
- **Layer Control**: `folium.LayerControl(collapsed=False)` menampilkan
  checkbox di pojok kanan atas peta untuk tampil/sembunyikan tiap layer,
  termasuk layer "Jalan Utama".
- **Judul, Legenda, Skala**: judul & ringkasan eksekutif ditampilkan di atas
  peta (bisa diedit dari sidebar), legenda berupa kotak putih di pojok kiri
  bawah peta, skala otomatis muncul di pojok kiri bawah peta bawaan Folium
  (`control_scale=True`).
- **Ringkasan Eksekutif**: bisa diedit langsung di sidebar aplikasi
  sebelum dipublikasikan.

## Catatan
- Data di folder `data/` saat ini adalah **data contoh (dummy)** yang
  dihasilkan `generate_sample_data.py`, HARUS diganti dengan hasil analisis
  Anda sendiri sebelum dikumpulkan sebagai tugas.
- Pastikan semua layer memakai CRS **EPSG:4326** saat export dari QGIS,
  supaya posisinya benar saat ditampilkan di peta web.
