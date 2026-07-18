"""
generate_sample_data.py
------------------------
Membuat data CONTOH (dummy) untuk 6 layer yang dibutuhkan aplikasi WebGIS
"Peta Interaktif Keadilan Spasial Akses Bahan Baku PKL Surabaya".

Jalankan sekali saja: python generate_sample_data.py
Hasilnya masuk ke folder data/ dalam format GeoJSON.

PENTING: Data di sini HANYA CONTOH agar aplikasi bisa langsung dicoba.
Ganti file-file di folder data/ dengan hasil export analisis QGIS Anda
yang sebenarnya (Layer > Export > Save Features As... > format GeoJSON).
Struktur kolom (field) HARUS mengikuti nama yang dipakai di app.py, atau
sesuaikan nama field di app.py dengan data Anda.
"""

import geopandas as gpd
from shapely.geometry import Point, Polygon, LineString
import os

os.makedirs("data", exist_ok=True)

# Pusat kira-kira di Surabaya (hanya acuan koordinat, bukan lokasi riil pasar)
CENTER_LAT, CENTER_LON = -7.2575, 112.7521

# 1. PASAR TRADISIONAL (Titik) -------------------------------------------
pasar = gpd.GeoDataFrame(
    {
        "nama": ["Pasar Contoh A", "Pasar Contoh B", "Pasar Contoh C"],
        "jam_operasional": ["04.00 - 10.00", "05.00 - 11.00", "04.30 - 09.30"],
        "kapasitas": [120, 85, 60],
    },
    geometry=[
        Point(CENTER_LON, CENTER_LAT),
        Point(CENTER_LON + 0.05, CENTER_LAT + 0.03),
        Point(CENTER_LON - 0.06, CENTER_LAT - 0.02),
    ],
    crs="EPSG:4326",
)
pasar.to_file("data/pasar.geojson", driver="GeoJSON")

# 2. BUFFER 3 KM (Poligon transparan) -------------------------------------
# Dibuat dengan buffer sederhana dari titik pasar (dalam derajat, kasar saja
# untuk contoh; di QGIS Anda pakai buffer 3000 m dengan CRS proyeksi yang benar)
buffer_gdf = pasar.copy()
buffer_gdf["geometry"] = buffer_gdf.geometry.buffer(0.03)  # ~3km kasar
buffer_gdf = buffer_gdf[["nama", "geometry"]]
buffer_gdf.to_file("data/buffer_3km.geojson", driver="GeoJSON")

# 3. KLASTER PKL TERLAYANI (Poligon hijau) --------------------------------
terlayani = gpd.GeoDataFrame(
    {
        "nama_kawasan": ["Klaster Jl. Contoh 1", "Klaster Jl. Contoh 2"],
        "jumlah_pkl": [45, 32],
        "status_akses": ["Terlayani", "Terlayani"],
    },
    geometry=[
        Polygon([
            (CENTER_LON + 0.005, CENTER_LAT + 0.005),
            (CENTER_LON + 0.02, CENTER_LAT + 0.005),
            (CENTER_LON + 0.02, CENTER_LAT + 0.02),
            (CENTER_LON + 0.005, CENTER_LAT + 0.02),
        ]),
        Polygon([
            (CENTER_LON - 0.02, CENTER_LAT - 0.01),
            (CENTER_LON - 0.005, CENTER_LAT - 0.01),
            (CENTER_LON - 0.005, CENTER_LAT + 0.005),
            (CENTER_LON - 0.02, CENTER_LAT + 0.005),
        ]),
    ],
    crs="EPSG:4326",
)
terlayani.to_file("data/klaster_terlayani.geojson", driver="GeoJSON")

# 4. BLANK SPOT (Poligon merah) -------------------------------------------
blank_spot = gpd.GeoDataFrame(
    {
        "nama_kawasan": ["Klaster Blank Spot 1", "Klaster Blank Spot 2", "Klaster Blank Spot 3"],
        "jumlah_pkl": [28, 19, 33],
        "status_akses": ["Blank Spot", "Blank Spot", "Blank Spot"],
    },
    geometry=[
        Polygon([
            (CENTER_LON + 0.08, CENTER_LAT - 0.05),
            (CENTER_LON + 0.1, CENTER_LAT - 0.05),
            (CENTER_LON + 0.1, CENTER_LAT - 0.03),
            (CENTER_LON + 0.08, CENTER_LAT - 0.03),
        ]),
        Polygon([
            (CENTER_LON - 0.1, CENTER_LAT - 0.08),
            (CENTER_LON - 0.08, CENTER_LAT - 0.08),
            (CENTER_LON - 0.08, CENTER_LAT - 0.06),
            (CENTER_LON - 0.1, CENTER_LAT - 0.06),
        ]),
        Polygon([
            (CENTER_LON - 0.02, CENTER_LAT + 0.09),
            (CENTER_LON, CENTER_LAT + 0.09),
            (CENTER_LON, CENTER_LAT + 0.11),
            (CENTER_LON - 0.02, CENTER_LAT + 0.11),
        ]),
    ],
    crs="EPSG:4326",
)
blank_spot.to_file("data/blank_spot.geojson", driver="GeoJSON")

# 5. LOKASI REKOMENDASI PASAR SATELIT (Titik bintang) ---------------------
rekomendasi = gpd.GeoDataFrame(
    {
        "nama": ["Rekomendasi Pasar Satelit 1"],
        "alasan": ["Berada di tengah 3 klaster PKL blank spot, akses jalan utama baik"],
    },
    geometry=[Point(CENTER_LON - 0.03, CENTER_LAT + 0.02)],
    crs="EPSG:4326",
)
rekomendasi.to_file("data/rekomendasi.geojson", driver="GeoJSON")

# 6. JALAN UTAMA (Garis, contoh layer yang bisa dimatikan) ----------------
jalan = gpd.GeoDataFrame(
    {"nama_jalan": ["Jalan Utama Contoh"]},
    geometry=[LineString([
        (CENTER_LON - 0.12, CENTER_LAT - 0.1),
        (CENTER_LON, CENTER_LAT),
        (CENTER_LON + 0.12, CENTER_LAT + 0.1),
    ])],
    crs="EPSG:4326",
)
jalan.to_file("data/jalan_utama.geojson", driver="GeoJSON")

print("Selesai. 6 file GeoJSON contoh dibuat di folder data/:")
for f in os.listdir("data"):
    print(" -", f)
