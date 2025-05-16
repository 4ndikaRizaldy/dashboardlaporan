import pandas as pd
import plotly.express as px
import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Konfigurasi Streamlit
st.set_page_config(page_title="Dashboard Data SMK", layout="wide")

# Daftar kategori
kategori_options = ['KELAS', 'DUSUN', 'DESA', 'KECAMATAN', 'KABUPATEN', 'PROVINSI']

# Sidebar untuk unggah file Excel
st.sidebar.title("Filter Data")
uploaded_file = st.sidebar.file_uploader("Unggah File Excel", type=["xlsx"])

# Fungsi untuk memuat data dari file Excel
def load_data_from_file(file):
    try:
        # Baca seluruh sheet, pilih sheet pertama
        xls = pd.ExcelFile(file)
        sheet_name = xls.sheet_names[0]
        data = pd.read_excel(xls, sheet_name=sheet_name)
        return data
    except Exception as e:
        st.error(f"Gagal memuat file: {e}")
        return None

# Periksa apakah ada file yang diunggah
if uploaded_file:
    data = load_data_from_file(uploaded_file)
else:
    st.warning("Silakan unggah file Excel untuk menampilkan data.")
    st.stop()

# Cek kolom wajib
required_columns = ['NAMA SISWA', 'KELAS', 'DESA', 'KECAMATAN', 'KABUPATEN', 'PROVINSI']
missing_columns = [col for col in required_columns if col not in data.columns]

if missing_columns:
    st.error(f"Kolom berikut tidak ditemukan dalam file: {', '.join(missing_columns)}")
    st.stop()

# Tambahkan kolom 'No' sebagai nomor urut
data = data.reset_index(drop=True)
data['No'] = range(1, len(data) + 1)

# Sidebar untuk memilih kategori analisis
category = st.sidebar.selectbox("Pilih kategori untuk analisis:", kategori_options)
selected_province = st.sidebar.multiselect("Filter berdasarkan Provinsi:", data['PROVINSI'].unique())

# Menampilkan Kabupaten berdasarkan Provinsi
filtered_data = data[data['PROVINSI'].isin(selected_province)] if selected_province else data
selected_kabupaten = st.sidebar.multiselect("Filter berdasarkan Kabupaten:", filtered_data['KABUPATEN'].unique())

# Menampilkan Kecamatan berdasarkan Kabupaten
filtered_data = filtered_data[filtered_data['KABUPATEN'].isin(selected_kabupaten)] if selected_kabupaten else filtered_data
selected_kecamatan = st.sidebar.multiselect("Filter berdasarkan Kecamatan:", filtered_data['KECAMATAN'].unique())

# Menampilkan Desa berdasarkan Kecamatan
filtered_data = filtered_data[filtered_data['KECAMATAN'].isin(selected_kecamatan)] if selected_kecamatan else filtered_data
selected_desa = st.sidebar.multiselect("Filter berdasarkan Desa:", filtered_data['DESA'].unique())

# Menampilkan Kelas berdasarkan Desa
filtered_data = filtered_data[filtered_data['DESA'].isin(selected_desa)] if selected_desa else filtered_data
selected_class = st.sidebar.multiselect("Filter berdasarkan Kelas:", filtered_data['KELAS'].unique())

# Filter terakhir berdasarkan kelas
if selected_class:
    filtered_data = filtered_data[filtered_data['KELAS'].isin(selected_class)]

# Hitung jumlah per kategori
category_counts = filtered_data[category].value_counts().reset_index()
category_counts.columns = [category, 'Jumlah']

# Fitur Urutkan Data
st.sidebar.subheader("Urutkan Data Tabel")
sort_column = st.sidebar.selectbox("Pilih kolom untuk diurutkan:", ["No", "NAMA SISWA", category])
sort_order = st.sidebar.radio("Pilih urutan:", ("Ascending", "Descending"))

# Urutkan data berdasarkan pilihan
sorted_data = filtered_data.sort_values(by=sort_column, ascending=(sort_order == "Ascending"))

# Tambahkan kolom nomor urut
sorted_data = sorted_data.reset_index(drop=True)
sorted_data['No'] = range(1, len(sorted_data) + 1)

# Ringkasan Data
total_siswa = len(sorted_data)
total_kategori = category_counts[category].nunique()
kategori_terbesar = category_counts.iloc[0][category] if not category_counts.empty else "Tidak ada data"

# Judul dan ringkasan data
st.title("Dashboard Data SMK")
st.write(f"**Jumlah Siswa Total:** {total_siswa}")
st.write(f"**Jumlah {category} yang Terdaftar:** {total_kategori}")
st.write(f"**Kategori {category} Terbesar:** {kategori_terbesar}")

# Grafik Bar
st.subheader(f"Jumlah Siswa per {category}")
fig_bar = px.bar(
    category_counts,
    x=category,
    y='Jumlah',
    color=category,
    color_discrete_sequence=px.colors.qualitative.Pastel,
    title=f"Jumlah Siswa per {category}",
    text='Jumlah'
)
fig_bar.update_layout(
    xaxis_title=f"{category}",
    yaxis_title="Jumlah Siswa",
    xaxis_tickangle=-45
)
st.plotly_chart(fig_bar, use_container_width=True)

# Grafik Pie
st.subheader(f"Distribusi Siswa per {category}")
fig_pie = px.pie(
    category_counts,
    names=category,
    values='Jumlah',
    color_discrete_sequence=px.colors.qualitative.Pastel,
    hole=0.4,
    title=f"Distribusi Siswa per {category}",
    hover_data={'Jumlah': True}
)
fig_pie.update_traces(textinfo='percent+label')
st.plotly_chart(fig_pie, use_container_width=True)

# Tampilkan Data Table
st.subheader(f"Tabel Data Siswa - {category}")
sorted_data = sorted_data[['No', 'NAMA SISWA', 'KELAS', 'DESA', 'KECAMATAN', 'KABUPATEN', 'PROVINSI']]
st.dataframe(sorted_data)

# Fungsi untuk membuat PDF
def generate_pdf(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Judul PDF
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 50, "Dashboard Data SMK")
    
    # Ringkasan
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Jumlah Siswa Total: {total_siswa}")
    c.drawString(50, height - 120, f"Jumlah {category} yang Terdaftar: {total_kategori}")
    c.drawString(50, height - 140, f"Kategori {category} Terbesar: {kategori_terbesar}")

    # Data Tabel
    start_y = height - 180
    for i, row in data.iterrows():
        text = f"{row['No']} - {row['NAMA SISWA']} - {row['KELAS']} - {row['DESA']} - {row['KECAMATAN']} - {row['KABUPATEN']} - {row['PROVINSI']}"
        c.drawString(50, start_y, text)
        start_y -= 20
        if start_y < 50:
            c.showPage()
            start_y = height - 50

    c.save()
    buffer.seek(0)
    return buffer

# Tombol Download PDF
if st.button("Download PDF"):
    pdf_buffer = generate_pdf(sorted_data)
    st.download_button(
        label="Unduh PDF",
        data=pdf_buffer,
        file_name="Dashboard_Data_SMK.pdf",
        mime="application/pdf"
    )
