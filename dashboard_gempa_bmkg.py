# ===============================================
# 🌋 DASHBOARD GEMPA BMKG - BY ARFAN
# ===============================================
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --------------------------
# Konfigurasi halaman
# --------------------------
st.set_page_config(page_title="Dashboard Gempa Indonesia", layout="wide")
st.title("🌋 Dashboard Interaktif Data Gempa Indonesia")

# --------------------------
# 1️⃣ Baca dan siapkan data
# --------------------------
df = pd.read_excel("laporan_data_gempa.xlsx", header=0)
df.columns = ["Tanggal", "Lintang", "Bujur", "Kedalaman", "Magnitudo"]

# Konversi tipe data
df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
df["Kedalaman"] = pd.to_numeric(df["Kedalaman"], errors="coerce")
df["Magnitudo"] = pd.to_numeric(df["Magnitudo"], errors="coerce")

# --------------------------
# 2️⃣ Sidebar Filter
# --------------------------
st.sidebar.header("⚙️ Pengaturan Tampilan")
min_mag = st.sidebar.slider("Pilih Magnitudo Minimum:", 0.0, 10.0, 3.0, 0.1)
df_filtered = df[df["Magnitudo"] >= min_mag]

# --------------------------
# 3️⃣ Visualisasi Dasar
# --------------------------
st.subheader("📈 Grafik Interaktif: Magnitudo vs Waktu")

fig1 = px.scatter(
    df_filtered,
    x="Tanggal",
    y="Magnitudo",
    color="Kedalaman",
    size="Magnitudo",
    title="Persebaran Magnitudo Gempa Berdasarkan Waktu",
    color_continuous_scale="Turbo",
    hover_data=["Kedalaman"]
)
fig1.update_traces(marker=dict(line=dict(width=0.5, color="DarkSlateGrey")))
st.plotly_chart(fig1, use_container_width=True)

# --------------------------
# 4️⃣ Visualisasi Peta
# --------------------------
st.subheader("🗺️ Peta Sebaran Gempa di Indonesia")

m = folium.Map(location=[-2, 118], zoom_start=4, tiles="CartoDB positron")

# Tambahkan marker untuk setiap data
for _, row in df_filtered.iterrows():
    color = "red" if row["Magnitudo"] >= 5 else "blue"
    folium.CircleMarker(
        location=[row["Lintang"], row["Bujur"]],
        radius=row["Magnitudo"] * 1.8,
        color=color,
        fill=True,
        fill_opacity=0.7,
        popup=(
            f"<b>Tanggal:</b> {row['Tanggal']}<br>"
            f"<b>Magnitudo:</b> {row['Magnitudo']}<br>"
            f"<b>Kedalaman:</b> {row['Kedalaman']} km"
        )
    ).add_to(m)

# Tambahkan legenda manual
legend_html = """
<div style="
    position: fixed; 
    bottom: 50px; left: 50px; width: 180px; height: 90px; 
    background-color: white; 
    border:2px solid grey; 
    z-index:9999; 
    font-size:14px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
    border-radius:8px;
    padding: 8px;">
<b>🔍 Keterangan:</b><br>
<span style="color:red;">●</span> Magnitudo ≥ 5 (Kuat)<br>
<span style="color:blue;">●</span> Magnitudo < 5 (Lemah)
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Tampilkan peta
st_folium(m, width=1200, height=500)

# --------------------------
# 3️⃣b Visualisasi Garis Tren
# --------------------------
st.subheader("📉 Grafik Garis: Tren Magnitudo Gempa dari Waktu ke Waktu")

# Urutkan data berdasarkan waktu biar garisnya rapi
df_line = df_filtered.sort_values("Tanggal")

fig_line = px.line(
    df_line,
    x="Tanggal",
    y="Magnitudo",
    markers=True,
    title="Tren Magnitudo Gempa Berdasarkan Waktu",
    line_shape="spline",  # garis halus
    color_discrete_sequence=["#FF4B4B"]  # warna merah lembut
)

fig_line.update_layout(
    xaxis_title="Tanggal Kejadian",
    yaxis_title="Magnitudo",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(size=14),
)

st.plotly_chart(fig_line, use_container_width=True)


# --------------------------
# 5️⃣ Visualisasi Komparasi
# --------------------------
st.subheader("📊 Rata-rata Magnitudo per Kedalaman (Binned)")

# Buat kategori kedalaman
bins = [0, 50, 100, 200, 500]
labels = ["<50 km", "50-100 km", "100-200 km", ">200 km"]
df_filtered["Kategori Kedalaman"] = pd.cut(df_filtered["Kedalaman"], bins=bins, labels=labels, include_lowest=True)

avg_mag = df_filtered.groupby("Kategori Kedalaman")["Magnitudo"].mean().reset_index()

fig2 = px.bar(
    avg_mag,
    x="Kategori Kedalaman",
    y="Magnitudo",
    color="Magnitudo",
    color_continuous_scale="Inferno",
    title="Rata-rata Magnitudo Berdasarkan Kedalaman",
)
st.plotly_chart(fig2, use_container_width=True)

# --------------------------
# 6️⃣ Footer
# --------------------------
st.markdown("""
---
📡 **Sumber Data:** File Excel `BADAN METEOROLOGI KLIMATOLOGI DAN GEOFISIKA (BMKG)`  
🧠 **Dibuat oleh:** Arfan & Fadhil      
🎨 **Tools:** Python • Streamlit • Plotly • Folium  
""")
