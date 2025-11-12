import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import feedparser
from urllib.parse import quote
from datetime import datetime, timedelta
import time

# ================== LOAD DATA ==================
url_kerawanan = "https://docs.google.com/spreadsheets/d/1vxzeLSd-ugWThehPqeqUqIWErcJxBYkBkXOPo_O0DBE/export?format=csv&gid=0"
url_unras     = "https://docs.google.com/spreadsheets/d/1vxzeLSd-ugWThehPqeqUqIWErcJxBYkBkXOPo_O0DBE/export?format=csv&gid=461570699"

df_kerawanan = pd.read_csv(url_kerawanan)
df_unras = pd.read_csv(url_unras)

df_kerawanan["Tanggal"] = pd.to_datetime(df_kerawanan["Tanggal"], errors="coerce")
df_unras["Tanggal"] = pd.to_datetime(df_unras["Tanggal"], errors="coerce")

# ================== STREAMLIT APP ==================
st.set_page_config(page_title="PNRE Security Forecast Dashboard", layout="wide")

# ================== CSS GLOBAL ==================
st.markdown("""
<style>
/* ================= HILANGKAN HEADER STREAMLIT DEFAULT ================= */
header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
[data-testid="stDecoration"] {visibility: hidden;}
[data-testid="stStatusWidget"] {visibility: hidden;}
[data-testid="stHeader"] {height: 0px;}
.block-container {padding-top: 0rem !important; padding-left: 1rem !important; padding-right: 1rem !important; max-width: 100% !important;}

/* ================= HEADER CUSTOM ================= */
.header-bar {position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
    background-color: #0a2342; color: white; padding: 14px 28px; display: flex;
    align-items: center; justify-content: space-between; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    font-family: 'Segoe UI', sans-serif;}
.header-title {font-size: 30px; font-weight: 600; letter-spacing: 0.4px;}
.header-right {display: flex; align-items: center; gap: 20px;}
.header-right img {width: 190px; background-color: white; border-radius: 10px; padding: 8px 10px; transition: transform 0.2s ease-in-out;}
.header-right img:hover {transform: scale(1.05);}
.header-updated {font-size: 14px; color: #dcdcdc;}
.main-content {margin-top: 80px;}

/* ================= TABS ================= */
.stTabs [role="tablist"] {
    display: flex; justify-content: flex-start; background-color: #0a2342;
    border-radius: 12px; padding: 12px 10px !important; gap: 8px; margin-bottom: 1px; width: fit-content;
}
.stTabs [role="tab"], .stTabs [role="tab"]:hover, .stTabs [aria-selected="true"] {
    font-size: 30px !important; background-color: transparent !important;
    color: white !important; font-weight: 600 !important; border: 2px solid rgba(255,255,255,0.4) !important;
    border-radius: 10px !important; padding: 14px 24px !important; transition: all 0.25s ease-in-out !important;
}
.stTabs [role="tab"]:hover {background-color: rgba(255,255,255,0.2) !important; cursor: pointer;}
.stTabs [aria-selected="true"] {background-color: white !important; color: #0a2342 !important; border: 2px solid #0a2342 !important; box-shadow: 0 2px 6px rgba(0,0,0,0.2) !important; transform: translateY(-1px) !important;}
section[data-testid="stTabs"] > div {margin-top: 1px !important; padding-top: 1px !important;}
.stTabs [role="tabpanel"] {padding-top: 1px !important;}

/* ================= RAPATKAN FILTER TAB 1 ================= */
div[data-testid="stDateInput"] > div:first-child {margin-bottom: 1px !important;}
div[data-testid="stMarkdownContainer"] {margin-top: 1px !important; margin-bottom: 1px !important;}
div[data-testid="stCheckbox"] {margin-top: 1px !important; margin-bottom: 1px !important;}

/* ================= STYLING TABEL ================= */
table {table-layout: fixed !important; width: 100% !important;}
th, td {word-wrap: break-word !important; overflow-wrap: break-word !important;}
</style>
""", unsafe_allow_html=True)

# ================== CSS GLOBAL ==================
st.markdown("""
<style>
/* Hapus semua garis/pemisah bawaan antar komponen */
div[data-testid="stHorizontalBlock"]::before,
div[data-testid="stVerticalBlockBorderWrapper"]::before {
    border: none !important;
}

/* Hapus border/pemisah yang kadang muncul antar blok konten */
div[data-testid="stVerticalBlock"] > div {
    border: none !important;
}

/* Rapatkan jarak antar elemen */
div[data-testid="stVerticalBlock"] {
    gap: 2px !important;
    margin-top: 0px !important;
    margin-bottom: 0px !important;
}

/* Hilangkan padding tambahan di dalam kolom */
div[data-testid="column"] > div {
    padding-top: 0px !important;
    padding-bottom: 0px !important;
    margin-top: 0px !important;
    margin-bottom: 0px !important;
}

/* Ganti background app jadi biru muda super soft */
body, div[data-testid="stAppViewContainer"] {
    background-color: #E3F2FD !important;
}
</style>
""", unsafe_allow_html=True)


# ================== LOAD LOGO ==================
with open("E:/1_Tugas Akhir/Olah Data/Misc/Forecast/logo_base64.txt", "r") as f:
    logo_base64 = f.read()

# ================== HEADER ==================
st.markdown(f"""
<div class="header-bar">
    <div class="header-title">PNRE Security Forecast Dashboard</div>
    <div class="header-right">
        <div class="header-updated">Updated: {datetime.now().strftime("%d %B %Y, %H:%M")} WIB</div>
        <img src="data:image/png;base64,{logo_base64}" alt="PNRE Logo">
    </div>
</div>
<div class="main-content"></div>
""", unsafe_allow_html=True)

# ================== TAB LABELS ==================
tab_labels = [
    "Human Intelligent",
    "Statistik Human Intelligent",
    "Open Source Intelligent",
]
tabs = st.tabs(tab_labels)

# ================== CSS UNTUK PERBESAR FONT TAB ==================
st.markdown("""
<style>
/* ====== STYLE TAB UMUM ====== */
.stTabs [role="tab"] {
    background-color: #0a2342 !important;
    color: white !important;
    border-radius: 8px 8px 0 0 !important;
    margin-right: 6px !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease-in-out;
    border: none !important;
}

/* ====== BESARIN TEKS DALAM TAB ====== */
.stTabs [role="tab"] p {
    font-size: 20px !important;   /* ubah ukuran di sini */
    font-weight: 600 !important;
    margin: 0 !important;
}

/* ====== TAB AKTIF ====== */
.stTabs [aria-selected="true"] {
    background-color: white !important;
    color: #0a2342 !important;
    font-weight: 700 !important;
    box-shadow: 0 -2px 6px rgba(0,0,0,0.15);
}

/* ====== TEKS DALAM TAB AKTIF ====== */
.stTabs [aria-selected="true"] p {
    color: #0a2342 !important;
    font-size: 20px !important;
    font-weight: 700 !important;
}

/* ====== EFEK HOVER ====== */
.stTabs [role="tab"]:hover {
    background-color: #173b6d !important;
}

/* ====== HAPUS GARIS OREN DI BAWAH TAB AKTIF ====== */
.stTabs [role="tab"][aria-selected="true"]::after {
    border-bottom: none !important;
    background: none !important;
    content: none !important;
}
</style>
""", unsafe_allow_html=True)

# ================== FUNGSIONALITAS ==================
def color_by_risk(risk):
    if isinstance(risk, str):
        risk = risk.upper()
        if risk == "LOW": return "green"
        elif risk == "MEDIUM": return "orange"
        elif risk == "HIGH": return "red"
    return "blue"

def highlight_risk(val):
    if pd.isna(val): return ""
    val = str(val).upper()
    color = "green" if val=="LOW" else "orange" if val=="MEDIUM" else "red" if val=="HIGH" else ""
    return f"color: {color}; font-weight: bold"

# ================== TAB 1: KERAWANAN ==================
with tabs[0]:

    # ======================
    # FILTER ATAS (SUPER RAPAT)
    # ======================
    col1, col2, col3, col4 = st.columns([1,1,1,2])

    with col1:
        st.markdown("### 🧭 Kerawanan Wilayah") 

    with col2:
        tanggal_pilihan = st.date_input(
            "Tanggal Analisis",
            value=max(df_kerawanan["Tanggal"].max(), df_unras["Tanggal"].max()).date(),
            min_value=min(df_kerawanan["Tanggal"].min(), df_unras["Tanggal"].min()).date(),
            max_value=max(df_kerawanan["Tanggal"].max(), df_unras["Tanggal"].max()).date(),
            label_visibility="collapsed"
        )

    with col3:
        show_kerawanan = st.checkbox("Kerawanan Wilayah (🔴)", True)
        show_pertamina = st.checkbox("Aktivitas terhadap Pertamina (🔵)", True)
    
    with col4:
        st.subheader("📋 Detail Aktivitas")

    # ======================
    # CSS UNTUK RAPIH
    # ======================
    st.markdown("""
    <style>
    /* ====================== */
    /* HILANGKAN GARIS / DIVIDER */
    /* ====================== */
    hr, div[data-testid="stDivider"] {
        display: none !important;
    }

    /* ====================== */
    /* RAPATKAN DATE PICKER & CHECKBOX */
    /* ====================== */
    div[data-testid="stDateInput"] {
        width: 150px !important;
        margin-top: 12px !important;  /* 🔹 Geser ke bawah */
        margin-bottom: 0px !important;
                
        /* 🎨 Tambahan untuk border */
        border: 1.5px solid #c2c2c2 !important;
        border-radius: 8px !important;
        padding: 2px 6px !important;
        background-color: #ffffff !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }
    }
    div[data-testid="stCheckbox"] {
        margin: 0px !important;
        padding-left: 0px !important;
    }

    /* ====================== */
    /* GAYA UNTUK LABEL TANGGAL */
    /* ====================== */
    .tanggal-display {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #0a2342 !important;
        margin: 0px !important;
        padding-top: 10px !important;
        padding-left: 10px !important;
    }

    /* ====================== */
    /* RAPATKAN JARAK SEBELUM PETA */
    /* ====================== */
    div[data-testid="stMarkdownContainer"] + div[data-testid="stVerticalBlock"] {
        margin-top: 0px !important;
    }

    /* ====================== */
    /* BORDER UNTUK PETA FOLIUM */
    /* ====================== */
    div[data-testid="stVerticalBlock"] iframe,
    div.map-container,
    iframe[title="st_folium"] {
        border: 8px solid #0A2342 !important;   /* warna biru lembut */
        border-radius: 12px !important;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15) !important;
        overflow: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)


    # ======================
    # FILTER DATA BERDASARKAN TANGGAL
    # ======================
    df_k = df_kerawanan[df_kerawanan["Tanggal"].dt.date == tanggal_pilihan]
    df_u = df_unras[df_unras["Tanggal"].dt.date == tanggal_pilihan]

    # ======================
    # BANGUN DICTIONARY KOORDINAT UNTUK DETAIL
    # ======================
    marker_dict = {}

    # Tambahkan titik kerawanan
    if not df_k.empty:
        for _, row in df_k.iterrows():
            if pd.notna(row["Latitude"]) and pd.notna(row["Longitude"]):
                coords = (round(row["Latitude"], 6), round(row["Longitude"], 6))
                marker_dict.setdefault(coords, []).append(row.to_dict())

    # Tambahkan titik pertamina
    if not df_u.empty:
        for _, row in df_u.iterrows():
            if pd.notna(row["Latitude"]) and pd.notna(row["Longitude"]):
                coords = (round(row["Latitude"], 6), round(row["Longitude"], 6))
                marker_dict.setdefault(coords, []).append(row.to_dict())

    # ======================
    # KOLOM 70:30 (PETA & DETAIL)
    # ======================
    col1, col2 = st.columns([6, 4])

    with col1:
        # ======================
        # BANGUN PETA BARU
        # ======================
        m = folium.Map(location=[-6.2, 106.8], zoom_start=11)
        all_points = []

        # Titik kerawanan
        if show_kerawanan and not df_k.empty:
            for _, row in df_k.iterrows():
                if pd.notna(row["Latitude"]) and pd.notna(row["Longitude"]):
                    lat, lon = round(row["Latitude"], 6), round(row["Longitude"], 6)
                    coords = [lat, lon]
                    lokasi = row.get("Wilayah", "Lokasi tidak diketahui")
                    isu = row.get("Isu", "-")

                    folium.CircleMarker(
                        location=coords,
                        radius=8,
                        color="red",
                        fill=True,
                        fill_color="red",
                        fill_opacity=0.65,
                        tooltip=f"<b>{lokasi}"
                    ).add_to(m)
                    all_points.append(coords)

        # Titik Pertamina
        if show_pertamina and not df_u.empty:
            for _, row in df_u.iterrows():
                if pd.notna(row["Latitude"]) and pd.notna(row["Longitude"]):
                    lat, lon = round(row["Latitude"], 6), round(row["Longitude"], 6)
                    coords = [lat, lon]
                    lokasi = row.get("Tempat", "Lokasi tidak diketahui")
                    isu = row.get("Isu", "-")
                    resiko = row.get("Resiko", "")
                    warna = "blue"

                    folium.CircleMarker(
                        location=coords,
                        radius=8,
                        color=warna,
                        fill=True,
                        fill_color=warna,
                        fill_opacity=0.65,
                        tooltip=f"<b>{lokasi}"
                    ).add_to(m)
                    all_points.append(coords)

        # fit bounds jika ada titik
        if all_points:
            m.fit_bounds(all_points)
        else:
            m.location = [-6.2, 106.8]
            m.zoom_start = 6

        # ======================
        # RENDER MAP DAN SIMPAN HASILNYA
        # ======================
        st_map = st_folium(m, width="100%", height=600, key="map_gabungan")

        # ======================
        # UPDATE SELECTED_COORDS LANGSUNG DARI HASIL RENDER
        # ======================
        if st_map and st_map.get("last_object_clicked"):
            lat = round(st_map["last_object_clicked"]["lat"], 6)
            lon = round(st_map["last_object_clicked"]["lng"], 6)
            st.session_state.selected_coords = (lat, lon)

        # ==============================
        # KOLOM DETAIL KANAN (30%)  <- GANTI DENGAN BLOCK INI
        # ==============================
        with col2:
            # Ambil koordinat yang terakhir dipilih (disimpan setelah render st_map)
            selected_coords = st.session_state.get("selected_coords", None)

            # Gabungkan data kerawanan & pertamina (untuk tampilan default)
            # Gabungkan data sesuai checkbox yang aktif
            frames = []
            if show_kerawanan:
                frames.append(df_k)
            if show_pertamina:
                frames.append(df_u)

            if frames:
                df_all = pd.concat(frames, ignore_index=True).reset_index(drop=True)
            else:
                df_all = pd.DataFrame()  # kalau dua-duanya tidak dicentang

            df_all = df_all.drop(columns=["Tanggal", "Pukul"], errors="ignore")

            # Jika ada titik terpilih dan ada di marker_dict -> pakai baris itu
            if selected_coords is not None and selected_coords in marker_dict:
                rows = marker_dict[selected_coords]
                df_detail = pd.DataFrame(rows)
            else:
                # Default: tampilkan semua aktivitas untuk tanggal itu
                df_detail = df_all.copy()
                # Tidak perlu judul sama sekali

            # Pastikan df_detail ada isinya
            if df_detail.empty:
                st.info("Tidak ada data untuk tanggal/koordinat ini.")
            else:
                # Hapus kolom yang tidak perlu saat render tabel
                df_display = df_detail.drop(columns=["Latitude", "Longitude", "Tanggal", "Pukul"], errors="ignore").reset_index(drop=True)

                # Format angka jumlah massa → hilangkan .00
                if "Jumlah Massa" in df_display.columns:
                    df_display["Jumlah Massa"] = (
                        pd.to_numeric(df_display["Jumlah Massa"], errors="coerce")
                        .fillna(0)
                        .astype(int)
                    )

                # Format kolom Organisasi & PJ agar tampil baris baru jika ada ";"
                for ccol in ["Organisasi", "PJ"]:
                    if ccol in df_display.columns:
                        df_display[ccol] = df_display[ccol].apply(
                            lambda x: "<br>".join([i.strip() for i in str(x).split(";") if i.strip()])
                        )

                # ======== ATUR LEBAR KHUSUS BERDASARKAN NAMA KOLOM ========
                lebar_kolom = {
                    "Organisasi": "120px",
                    "PJ": "90px",   
                    "Jumlah Massa": "75px",
                    "Tempat": "120px",
                    "Aset Sekitar": "120px",
                    "Wilayah": "120px",
                    "Isu": "230px",
                    "Resiko": "80px",
                }

                table_styles = [
                    {"selector": "table", "props": [
                        ("border-collapse", "collapse"),
                        ("width", "100%"),
                        ("font-size", "12px"),
                        ("table-layout", "fixed"),
                    ]},
                    {"selector": "th, td", "props": [
                        ("border", "1px solid #999"),
                        ("padding", "6px 10px"),
                        ("text-align", "left"),
                        ("vertical-align", "top"),
                        ("word-wrap", "break-word"),
                        ("overflow-wrap", "break-word"),
                    ]},
                    {"selector": "th", "props": [
                        ("background-color", "#0a2342"),
                        ("color", "white"),
                        ("font-weight", "bold"),
                    ]},
                    {"selector": "tbody tr:nth-child(odd)", "props": [("background-color", "#E3ECF8")]},
                    {"selector": "tbody tr:nth-child(even)", "props": [("background-color", "#D0E3FF")]},
                ]

                # Tambahkan style lebar per kolom sesuai urutan kolom df_display
                for i, col_name in enumerate(df_display.columns, start=1):
                    width = lebar_kolom.get(col_name, "120px")
                    table_styles.append({
                        "selector": f"th:nth-child({i}), td:nth-child({i})",
                        "props": [("width", width)],
                    })

                # ====================== HIGHLIGHT BARIS JIKA ADA TITIK TERPILIH ======================
                df_styled = df_display.style

                if selected_coords is not None:
                    # cari baris yang memiliki koordinat sama (kalo df_display masih punya Latitude/Longitude,
                    # kalau sudah di-drop maka kita cari dari df_detail asli)
                    idx_to_highlight = []
                    if "Latitude" in df_detail.columns and "Longitude" in df_detail.columns:
                        cond = (
                            (df_detail["Latitude"].round(6) == selected_coords[0]) &
                            (df_detail["Longitude"].round(6) == selected_coords[1])
                        )
                        idx_to_highlight = df_detail[cond].index.tolist()

                # apply table styles & hide index
                df_styled = df_styled.set_table_styles(table_styles).hide(axis="index")

                # render HTML safe
                st.markdown(df_styled.to_html(), unsafe_allow_html=True)

# ================== TAB 2: STATISTIK (ML-BASED) ==================
with tabs[1]:
    st.header("🤖 Statistik Kerawanan & Aktivitas")

    import plotly.express as px
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    import re
    from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

    # ================== ROW FILTER TANGGAL ==================
    col1, col2, col3 = st.columns([1,1,8])
    with col1:
        start_date = st.date_input("Tanggal Mulai", df_kerawanan["Tanggal"].min().date())
    with col2:
        end_date = st.date_input("Tanggal Akhir", df_kerawanan["Tanggal"].max().date())
    with col3:
        source = st.radio(
            "Sumber Data:",
            options=["Kerawanan Wilayah", "Isu Pertamina"],
            index=0,
            horizontal=True
        )

    # ================== FILTER DATA BERDASARKAN PILIHAN ==================
    # Hapus tombol
    if source == "Kerawanan Wilayah":
        df_stat = df_kerawanan[(df_kerawanan["Tanggal"].dt.date >= start_date) & 
                            (df_kerawanan["Tanggal"].dt.date <= end_date)]
    else:
        df_stat = df_unras[(df_unras["Tanggal"].dt.date >= start_date) & 
                        (df_unras["Tanggal"].dt.date <= end_date)]

    # ================== STATISTIK PENYELENGGARA, PJ, LOKASI ==================
    st.subheader("📈 Statistik Penyelenggara, Penanggung Jawab, & Lokasi")
    col1, col2, col3 = st.columns(3)

    if not df_stat.empty:
        # ----- Penyelenggara -----
        if "Organisasi" in df_stat.columns:
            org_series = df_stat["Organisasi"].dropna().apply(lambda x: [i.strip() for i in str(x).split(";") if i.strip()])
            org_flat = [item for sublist in org_series for item in sublist]
            penyelenggara_count = pd.Series(org_flat).value_counts().reset_index()
            penyelenggara_count.columns = ["Organisasi","Jumlah"]
            with col1:
                st.markdown("**Top 10 Penyelenggara**")
                fig1 = px.bar(penyelenggara_count.head(10), x="Jumlah", y="Organisasi", orientation="h")
                fig1.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
                st.plotly_chart(fig1, use_container_width=True)
        else:
            with col1: st.info("Kolom 'Organisasi' tidak tersedia.")

        # ----- Penanggung Jawab -----
        if "PJ" in df_stat.columns:
            pj_series = df_stat["PJ"].dropna().apply(lambda x: [i.strip() for i in str(x).split(";") if i.strip()])
            pj_flat = [item for sublist in pj_series for item in sublist]
            pj_count = pd.Series(pj_flat).value_counts().reset_index()
            pj_count.columns = ["PJ","Jumlah"]
            with col2:
                st.markdown("**Top 10 Penanggung Jawab**")
                fig2 = px.bar(pj_count.head(10), x="Jumlah", y="PJ", orientation="h")
                fig2.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
                st.plotly_chart(fig2, use_container_width=True)
        else:
            with col2: st.info("Kolom 'PJ' tidak tersedia.")

        # ----- Lokasi -----
        if "Tempat" in df_stat.columns:
            lokasi_series = df_stat["Tempat"].dropna().apply(lambda x: [i.strip() for i in str(x).split(";") if i.strip()])
            lokasi_label = "Tempat"
        elif "Wilayah" in df_stat.columns:
            lokasi_series = df_stat["Wilayah"].dropna().apply(lambda x: [i.strip() for i in str(x).split(";") if i.strip()])
            lokasi_label = "Wilayah"
        else:
            lokasi_series = pd.Series([])
            lokasi_label = "Lokasi"

        if not lokasi_series.empty:
            lokasi_flat = [item for sublist in lokasi_series for item in sublist]
            lokasi_count = pd.Series(lokasi_flat).value_counts().reset_index()
            lokasi_count.columns = [lokasi_label,"Jumlah"]
            with col3:
                st.markdown(f"**Top 10 {lokasi_label}**")
                fig3 = px.bar(lokasi_count.head(10), x="Jumlah", y=lokasi_label, orientation="h")
                fig3.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
                st.plotly_chart(fig3, use_container_width=True)
        else:
            with col3: st.info(f"Kolom {lokasi_label} tidak tersedia.")
    else:
        st.warning("Tidak ada data yang cocok dengan filter yang dipilih.")

    # ================== ANALISIS TOPIK ==================
    st.divider()
    st.subheader("🧠 Analisis Topik")
    teks_isu = df_stat["Isu"].astype(str).tolist() if "Isu" in df_stat.columns else []

    if len(teks_isu) > 0:
        # ----- Preprocessing -----
        def clean_text(text):
            text = text.lower()
            text = re.sub(r"[^a-zA-ZÀ-ž\s]", "", text)
            text = re.sub(r"\s+", " ", text)
            return text.strip()
        cleaned = [clean_text(t) for t in teks_isu if isinstance(t, str) and len(t) > 2]

        # ----- TF-IDF + KMeans -----
        factory_stop = StopWordRemoverFactory()
        stop_words = factory_stop.get_stop_words()
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.cluster import KMeans
        vectorizer = TfidfVectorizer(max_features=500, stop_words=stop_words, lowercase=True)
        X = vectorizer.fit_transform(cleaned)

        num_clusters = st.slider("Pilih jumlah topik (cluster)", 2, 10, 4)
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)

        terms = vectorizer.get_feature_names_out()
        cluster_keywords = {}
        for i in range(num_clusters):
            centroid = kmeans.cluster_centers_[i]
            top_idx = centroid.argsort()[-10:][::-1]
            cluster_keywords[i] = [terms[j] for j in top_idx]

        st.markdown("### 🔍 Topik Dominan Ditemukan")
        for i, keywords in cluster_keywords.items():
            st.markdown(f"**🧩 Topik {i+1}:** " + ", ".join(keywords))
    else:
        st.warning("Tidak ada data isu yang valid untuk dianalisis pada filter yang dipilih.")


# ================== TAB 3: OSINT BERITA OTOMATIS ==================
with tabs[2]:
    st.header("📰 Analisis Sentimen Media")

    import re, html, pandas as pd, feedparser, time
    from datetime import datetime, timedelta
    from urllib.parse import quote
    from textblob import TextBlob
    from deep_translator import GoogleTranslator

    # ------------------ BAGIAN 1: FEED OTOMATIS ------------------
    st.subheader("🔍 Berita Terbaru (Google News RSS)")
    keyword = st.text_input("Masukkan kata kunci berita:", "Pertamina")
    rss_url = f"https://news.google.com/rss/search?q={quote(keyword)}&hl=id&gl=ID&ceid=ID:id"
    feed = feedparser.parse(rss_url)

    one_week_ago = datetime.now() - timedelta(days=7)
    entries_recent = [
        e for e in feed.entries
        if hasattr(e, "published_parsed") 
        and datetime.fromtimestamp(time.mktime(e.published_parsed)) >= one_week_ago
    ]

    if not entries_recent:
        st.warning("❌ Tidak ada berita dalam 7 hari terakhir untuk kata kunci ini.")
    else:
        data = []
        for e in entries_recent[:20]:
            deskripsi = getattr(e, "summary", "")
            deskripsi = html.unescape(re.sub("<.*?>", "", deskripsi))
            deskripsi = re.sub(r"\s+", " ", deskripsi).strip()

            judul_link = f"[{e.title}]({e.link})"
            media = getattr(e, "source", {}).get("title", "Tidak diketahui") if hasattr(e, "source") else "Tidak diketahui"
            tanggal = getattr(e, "published", "Tidak diketahui")

            data.append({
                "Judul": judul_link,
                "Media": media,
                "Tanggal": tanggal,
                "Deskripsi": deskripsi
            })

        df_news = pd.DataFrame(data)

        # Tampilkan tabel markdown dengan CSS
        st.markdown("### 🗞️ Daftar Berita Terbaru")
        st.write("Klik judul untuk membuka berita asli di tab baru:")

        table_style = """
        <style>
        table {border-collapse: collapse; width: 100%; font-size: 12px; table-layout: fixed;}
        th, td {border: 1px solid #999; padding: 6px 10px; text-align: left; vertical-align: top; word-wrap: break-word; overflow-wrap: break-word;}
        th {background-color: #0a2342; color: white; font-weight: bold;}
        tbody tr:nth-child(odd) {background-color: #E3ECF8;}
        tbody tr:nth-child(even) {background-color: #D0E3FF;}
        th:nth-child(1), td:nth-child(1) { width: 250px; }  /* Judul */
        th:nth-child(2), td:nth-child(2) { width: 140px; }  /* Tanggal */
        th:nth-child(3), td:nth-child(3) { width: 120px; }  /* Media */
        </style>
        """
        st.markdown(table_style, unsafe_allow_html=True)

        st.markdown(
            df_news[["Judul", "Tanggal", "Media"]].to_markdown(index=False),
            unsafe_allow_html=True
        )

        st.divider()

        # ------------------ BAGIAN 2: STATISTIK BERITA ------------------
        st.subheader("📊 Statistik Isu Otomatis")
        df_news["Media"] = df_news["Media"].fillna("Tidak diketahui")
        media_count = df_news["Media"].value_counts().head(10)

        # Tambahkan dummy bar agar ada space di atas
        media_count_with_space = media_count.copy()
        media_count_with_space.loc[""] = media_count.max() * 0.05  # 5% dummy

        st.write("🔸 Jumlah berita per media:")
        st.bar_chart(media_count)

        st.divider()

        # ------------------ BAGIAN 3: ANALISIS SENTIMEN ------------------
        st.subheader("🧭 Analisis Sentimen Berita (Bahasa Indonesia)")
        sentiments = []
        for desc in df_news["Deskripsi"]:
            try:
                translated = GoogleTranslator(source='auto', target='en').translate(desc)
                blob = TextBlob(translated)
                sentiments.append(blob.sentiment.polarity)
            except Exception:
                sentiments.append(0.0)

        df_news["Sentimen"] = sentiments

        def label_sentiment(score):
            if score > 0.1:
                return "Positif"
            elif score < -0.1:
                return "Negatif"
            else:
                return "Netral"

        df_news["Kategori Sentimen"] = df_news["Sentimen"].apply(label_sentiment)

        sentiment_avg = df_news["Sentimen"].mean()
        sentiment_label = label_sentiment(sentiment_avg)
        st.metric("Rata-rata sentimen berita", f"{sentiment_avg:.2f} ({sentiment_label})")

        # Distribusi sentimen
        sentiment_count = df_news["Kategori Sentimen"].value_counts()
        sentiment_count_with_space = sentiment_count.copy()
        sentiment_count_with_space.loc[""] = sentiment_count.max() * 0.05

        st.write("📊 Distribusi sentimen berita:")
        st.bar_chart(sentiment_count)

        # Tabel berita lengkap
        st.dataframe(df_news[["Judul", "Tanggal", "Media", "Kategori Sentimen", "Deskripsi"]])
