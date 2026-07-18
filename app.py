"""
Peta Interaktif Keadilan Spasial Akses Bahan Baku PKL Surabaya
================================================================
Dibuat dengan Streamlit + Folium (opsi Low-Code / Python).

Cara pakai:
1. (Opsional, untuk uji coba) jalankan `python generate_sample_data.py`
   untuk membuat data contoh di folder data/.
2. Ganti isi folder data/ dengan hasil export QGIS Anda (format GeoJSON),
   ATAU upload langsung lewat sidebar aplikasi saat dijalankan.
3. Jalankan: streamlit run app.py
"""

import json
import tempfile

import folium
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium

# --------------------------------------------------------------------------
# KONFIGURASI HALAMAN
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Peta Keadilan Spasial PKL Surabaya",
    page_icon="🗺️",
    layout="wide",
)

DATA_DIR = "data"
DEFAULT_FILES = {
    "pasar": f"{DATA_DIR}/pasar.geojson",
    "buffer": f"{DATA_DIR}/buffer_3km.geojson",
    "terlayani": f"{DATA_DIR}/klaster_terlayani.geojson",
    "blank_spot": f"{DATA_DIR}/blank_spot.geojson",
    "rekomendasi": f"{DATA_DIR}/rekomendasi.geojson",
    "jalan": f"{DATA_DIR}/jalan_utama.geojson",
}

CENTER_DEFAULT = [-7.2575, 112.7521]  # titik tengah kasar Surabaya


# --------------------------------------------------------------------------
# FUNGSI BANTUAN
# --------------------------------------------------------------------------
def load_layer(uploaded_file, default_path):
    """Muat layer dari file yang diupload user, atau pakai file default jika
    tidak ada upload. Mengembalikan GeoDataFrame atau None jika gagal."""
    try:
        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(suffix=".geojson", delete=False) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            return gpd.read_file(tmp_path)
        else:
            return gpd.read_file(default_path)
    except Exception as e:
        st.sidebar.warning(f"Gagal memuat layer ({default_path}): {e}")
        return None


def safe_get(props, *keys, default="-"):
    """Ambil nilai pertama yang ada dari beberapa kemungkinan nama kolom."""
    for k in keys:
        if k in props and props[k] not in (None, ""):
            return props[k]
    return default


# --------------------------------------------------------------------------
# SIDEBAR: UPLOAD DATA & RINGKASAN EKSEKUTIF
# --------------------------------------------------------------------------
st.sidebar.header("📂 Sumber Data")
st.sidebar.caption(
    "Kosongkan jika ingin memakai data contoh. Upload GeoJSON hasil export "
    "QGIS Anda (Layer > Export > Save Features As > GeoJSON) untuk memakai "
    "data asli."
)

f_pasar = st.sidebar.file_uploader("Pasar Tradisional (titik)", type=["geojson", "json"])
f_buffer = st.sidebar.file_uploader("Buffer 3 KM (poligon)", type=["geojson", "json"])
f_terlayani = st.sidebar.file_uploader("Klaster PKL Terlayani (poligon)", type=["geojson", "json"])
f_blank = st.sidebar.file_uploader("Blank Spot (poligon)", type=["geojson", "json"])
f_rekom = st.sidebar.file_uploader("Rekomendasi Pasar Satelit (titik)", type=["geojson", "json"])
f_jalan = st.sidebar.file_uploader("Jalan Utama (garis, opsional)", type=["geojson", "json"])

st.sidebar.divider()
st.sidebar.header("📝 Ringkasan Eksekutif")
default_summary = (
    "Analisis spasial menunjukkan terdapat beberapa klaster PKL yang berada "
    "di luar jangkauan buffer 3 km dari pasar tradisional aktif (blank spot). "
    "Lokasi pasar satelit direkomendasikan pada titik yang berada di tengah "
    "klaster-klaster blank spot tersebut untuk memperbaiki keadilan akses "
    "bahan baku bagi para pedagang kaki lima."
)
summary_text = st.sidebar.text_area(
    "Edit ringkasan (akan tampil di bawah judul peta):",
    value=default_summary,
    height=160,
)

# --------------------------------------------------------------------------
# MUAT DATA
# --------------------------------------------------------------------------
gdf_pasar = load_layer(f_pasar, DEFAULT_FILES["pasar"])
gdf_buffer = load_layer(f_buffer, DEFAULT_FILES["buffer"])
gdf_terlayani = load_layer(f_terlayani, DEFAULT_FILES["terlayani"])
gdf_blank = load_layer(f_blank, DEFAULT_FILES["blank_spot"])
gdf_rekom = load_layer(f_rekom, DEFAULT_FILES["rekomendasi"])
gdf_jalan = load_layer(f_jalan, DEFAULT_FILES["jalan"])

# Tentukan titik tengah peta dari data pasar jika tersedia
if gdf_pasar is not None and len(gdf_pasar) > 0:
    center = [gdf_pasar.geometry.y.mean(), gdf_pasar.geometry.x.mean()]
else:
    center = CENTER_DEFAULT

# --------------------------------------------------------------------------
# JUDUL & KONTEKS HALAMAN
# --------------------------------------------------------------------------
st.title("🗺️ Peta Interaktif Keadilan Spasial Akses Bahan Baku PKL Surabaya")
st.markdown(
    "Peta ini menampilkan hasil analisis *blank spot* akses pasar dan "
    "rekomendasi lokasi *pasar satelit* bagi Pedagang Kaki Lima (PKL) di "
    "Surabaya, dipublikasikan dari QGIS ke WebGIS agar mudah diakses Dinas "
    "Koperasi & UMKM serta Bappeda tanpa perlu instalasi QGIS."
)
st.info(f"**Ringkasan Eksekutif:** {summary_text}")

# --------------------------------------------------------------------------
# BUAT PETA FOLIUM
# --------------------------------------------------------------------------
m = folium.Map(location=center, zoom_start=13, tiles="CartoDB positron", control_scale=True)

# --- Layer: Jalan Utama (garis, contoh layer yang bisa dimatikan) --------
if gdf_jalan is not None and len(gdf_jalan) > 0:
    folium.GeoJson(
        gdf_jalan,
        name="Jalan Utama",
        style_function=lambda x: {"color": "#555555", "weight": 3, "dashArray": "4,4"},
        tooltip=folium.GeoJsonTooltip(fields=list(gdf_jalan.columns[:1])) if len(gdf_jalan.columns) > 1 else None,
    ).add_to(m)

# --- Layer: Buffer 3 KM (poligon transparan biru muda) -------------------
if gdf_buffer is not None and len(gdf_buffer) > 0:
    folium.GeoJson(
        gdf_buffer,
        name="Buffer 3 KM",
        style_function=lambda x: {
            "fillColor": "#87CEFA",
            "color": "#4682B4",
            "weight": 1,
            "fillOpacity": 0.25,
        },
    ).add_to(m)

# --- Layer: Klaster PKL Terlayani (poligon hijau) -------------------------
if gdf_terlayani is not None and len(gdf_terlayani) > 0:
    fg_terlayani = folium.FeatureGroup(name="Klaster PKL Terlayani")
    for _, row in gdf_terlayani.iterrows():
        props = row.drop("geometry").to_dict()
        nama = safe_get(props, "nama_kawasan", "nama")
        jumlah = safe_get(props, "jumlah_pkl")
        status = safe_get(props, "status_akses", default="Terlayani")
        popup_html = (
            f"<b>{nama}</b><br>"
            f"Jumlah PKL: {jumlah}<br>"
            f"Status Akses: {status}"
        )
        folium.GeoJson(
            row.geometry.__geo_interface__,
            style_function=lambda x: {
                "fillColor": "#2ecc71",
                "color": "#1e8449",
                "weight": 1.5,
                "fillOpacity": 0.5,
            },
            popup=folium.Popup(popup_html, max_width=250),
        ).add_to(fg_terlayani)
    fg_terlayani.add_to(m)

# --- Layer: Blank Spot (poligon merah) ------------------------------------
if gdf_blank is not None and len(gdf_blank) > 0:
    fg_blank = folium.FeatureGroup(name="Blank Spot")
    for _, row in gdf_blank.iterrows():
        props = row.drop("geometry").to_dict()
        nama = safe_get(props, "nama_kawasan", "nama")
        jumlah = safe_get(props, "jumlah_pkl")
        status = safe_get(props, "status_akses", default="Blank Spot")
        popup_html = (
            f"<b>{nama}</b><br>"
            f"Jumlah PKL: {jumlah}<br>"
            f"Status Akses: {status}"
        )
        folium.GeoJson(
            row.geometry.__geo_interface__,
            style_function=lambda x: {
                "fillColor": "#e74c3c",
                "color": "#922b21",
                "weight": 1.5,
                "fillOpacity": 0.5,
            },
            popup=folium.Popup(popup_html, max_width=250),
        ).add_to(fg_blank)
    fg_blank.add_to(m)

# --- Layer: Pasar Tradisional (titik hijau/biru) --------------------------
if gdf_pasar is not None and len(gdf_pasar) > 0:
    fg_pasar = folium.FeatureGroup(name="Pasar Tradisional (Aktif Pagi)")
    for _, row in gdf_pasar.iterrows():
        props = row.drop("geometry").to_dict()
        nama = safe_get(props, "nama")
        jam = safe_get(props, "jam_operasional")
        kap = safe_get(props, "kapasitas")
        popup_html = (
            f"<b>{nama}</b><br>"
            f"Jam Operasional: {jam}<br>"
            f"Kapasitas: {kap}"
        )
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=8,
            color="#1565C0",
            fill=True,
            fill_color="#42A5F5",
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=nama,
        ).add_to(fg_pasar)
    fg_pasar.add_to(m)

# --- Layer: Rekomendasi Pasar Satelit (bintang emas) ----------------------
if gdf_rekom is not None and len(gdf_rekom) > 0:
    fg_rekom = folium.FeatureGroup(name="Rekomendasi Pasar Satelit")
    for _, row in gdf_rekom.iterrows():
        props = row.drop("geometry").to_dict()
        nama = safe_get(props, "nama")
        alasan = safe_get(props, "alasan")
        popup_html = f"<b>{nama}</b><br>Alasan: {alasan}"
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            icon=folium.Icon(color="orange", icon="star", prefix="fa"),
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=nama,
        ).add_to(fg_rekom)
    fg_rekom.add_to(m)

# --- Layer Control (checkbox tampil/sembunyikan layer) --------------------
folium.LayerControl(collapsed=False).add_to(m)

# --- Legenda kustom (HTML overlay) ---------------------------------------
legend_html = """
{% macro html(this, kwargs) %}
<div style="
    position: fixed;
    bottom: 30px;
    left: 30px;
    z-index: 9999;
    background-color: white;
    padding: 10px 14px;
    border: 2px solid #666;
    border-radius: 6px;
    font-size: 13px;
    line-height: 1.6;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
">
<b>Legenda</b><br>
<span style="color:#1565C0;">●</span> Pasar Tradisional (Aktif Pagi)<br>
<span style="color:#4682B4;">▬</span> Buffer 3 KM<br>
<span style="color:#1e8449;">■</span> Klaster PKL Terlayani<br>
<span style="color:#922b21;">■</span> Blank Spot<br>
<span style="color:orange;">★</span> Rekomendasi Pasar Satelit<br>
<span style="color:#555555;">- - -</span> Jalan Utama
</div>
{% endmacro %}
"""
from branca.element import MacroElement, Template

legend = MacroElement()
legend._template = Template(legend_html)
m.get_root().add_child(legend)

# --------------------------------------------------------------------------
# TAMPILKAN PETA DI STREAMLIT
# --------------------------------------------------------------------------
st_folium(m, width=None, height=650, use_container_width=True)

st.caption(
    "Sumber data: hasil analisis spasial QGIS (blank spot & rekomendasi lokasi "
    "pasar satelit). Data ditampilkan dalam format GeoJSON."
)
