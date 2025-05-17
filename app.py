import pandas as pd
import plotly.express as px
import streamlit as st

# Konfigurasi Streamlit
st.set_page_config(page_title="Dashboard Data SMK", layout="wide")

# Daftar kategori
kategori_options = ['KELAS', 'DESA', 'DUSUN','KECAMATAN', 'KABUPATEN', 'PROVINSI']

# Sidebar untuk unggah file Excel
st.sidebar.title("Filter Data")
uploaded_file = st.sidebar.file_uploader("Unggah File Excel", type=["xlsx"])

# Fungsi untuk memuat data dari file Excel
def load_data_from_file(file):
    try:
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
required_columns = ['NAMA SISWA', 'KELAS', 'DUSUN', 'DESA', 'KECAMATAN', 'KABUPATEN', 'PROVINSI']
missing_columns = [col for col in required_columns if col not in data.columns]

if missing_columns:
    st.error(f"Kolom berikut tidak ditemukan dalam file: {', '.join(missing_columns)}")
    st.stop()

# Ganti seluruh baris yang berisi NaN dengan "Lainnya"
data = data.fillna("Lainnya")

# Hapus kolom 'Unnamed' atau 'None'
data = data.loc[:, ~data.columns.str.match('^Unnamed.*|^None$')]

# Data untuk bar chart (tidak terpengaruh filter)
bar_chart_data = data.copy()

# Sidebar untuk memilih kategori analisis
category = st.sidebar.selectbox("Pilih kategori untuk analisis:", kategori_options)

# Filter Provinsi
selected_province = st.sidebar.multiselect("Filter berdasarkan Provinsi:", data['PROVINSI'].unique())
filtered_data = data[data['PROVINSI'].isin(selected_province)] if selected_province else data

# Filter Kabupaten (berdasarkan Provinsi yang dipilih)
available_kabupaten = filtered_data['KABUPATEN'].unique()
selected_kabupaten = st.sidebar.multiselect("Filter berdasarkan Kabupaten:", available_kabupaten)
filtered_data = filtered_data[filtered_data['KABUPATEN'].isin(selected_kabupaten)] if selected_kabupaten else filtered_data

# Filter Kecamatan (berdasarkan Kabupaten yang dipilih)
available_kecamatan = filtered_data['KECAMATAN'].unique()
selected_kecamatan = st.sidebar.multiselect("Filter berdasarkan Kecamatan:", available_kecamatan)
filtered_data = filtered_data[filtered_data['KECAMATAN'].isin(selected_kecamatan)] if selected_kecamatan else filtered_data

# Filter Desa (berdasarkan Kecamatan yang dipilih)
available_desa = filtered_data['DESA'].unique()
selected_desa = st.sidebar.multiselect("Filter berdasarkan Desa:", available_desa)
filtered_data = filtered_data[filtered_data['DESA'].isin(selected_desa)] if selected_desa else filtered_data

# Filter Kelas
available_class = filtered_data['DUSUN'].unique()
selected_class = st.sidebar.multiselect("Filter berdasarkan Dusun:", available_class)
filtered_data = filtered_data[filtered_data['DUSUN'].isin(selected_class)] if selected_class else filtered_data


# Filter Kelas
available_class = filtered_data['KELAS'].unique()
selected_class = st.sidebar.multiselect("Filter berdasarkan Kelas:", available_class)
filtered_data = filtered_data[filtered_data['KELAS'].isin(selected_class)] if selected_class else filtered_data

# Filter berdasarkan kelas
if selected_class:
    filtered_data = filtered_data[filtered_data['KELAS'].isin(selected_class)]

# Cek jika data hasil filter kosong
if filtered_data.empty:
    st.warning("Tidak ada data yang sesuai dengan filter yang diterapkan.")
    st.stop()

# Urutkan data berdasarkan 'NAMA SISWA' secara lowercase
sorted_data = filtered_data.sort_values(
    by="NAMA SISWA", 
    key=lambda col: col.str.lower()
).reset_index(drop=True)

# Tambahkan kolom 'No' setelah sorting
sorted_data['No'] = range(1, len(sorted_data) + 1)

# Daftar kolom yang ingin ditampilkan
columns_to_display = ['No', 'NAMA SISWA', 'KELAS','DUSUN', 'DESA', 'KECAMATAN', 'KABUPATEN', 'PROVINSI']
existing_columns = [col for col in columns_to_display if col in sorted_data.columns]

# Tampilkan tabel data dengan fitur pencarian nama
st.subheader("Data Siswa")

# Input pencarian nama siswa
search_name = st.text_input("Cari Nama Siswa (berdasarkan kandungan nama):")

# Jika ada input pencarian, filter data berdasarkan nama
if search_name:
    filtered_table_data = sorted_data[sorted_data['NAMA SISWA'].str.contains(search_name, case=False, na=False)]
else:
    filtered_table_data = sorted_data

# Tampilkan data dalam tabel
st.dataframe(filtered_table_data[existing_columns])

# Fungsi untuk membuat grafik bar chart
def create_bar_chart(data, column_name, color_column=None):
    counts = data[column_name].value_counts().reset_index()
    counts.columns = [column_name, 'Jumlah']
    counts = counts.sort_values('Jumlah', ascending=False)

    fig = px.bar(
        counts,
        y=column_name,
        x='Jumlah',
        color=column_name,
        orientation='h',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        text='Jumlah',
        title=f"Persebaran Data Berdasarkan {column_name}"
    )

    fig.update_traces(textposition='outside', textfont_size=12)
    fig.update_layout(
        xaxis_title="Jumlah",
        yaxis_title=column_name,
        xaxis_tickangle=0
    )

    st.plotly_chart(fig, use_container_width=True)

# Grafik Bar Chart yang tidak terpengaruh oleh filter
st.subheader("Grafik Persebaran Data Berdasarkan Provinsi")
create_bar_chart(bar_chart_data, "PROVINSI")

st.subheader("Grafik Persebaran Data Berdasarkan Kabupaten")
create_bar_chart(bar_chart_data, "KABUPATEN")

# Treemap menggunakan filtered_data
st.subheader("Treemap Persebaran Data Berdasarkan Provinsi, Kabupaten, Kecamatan, dan Desa")
if all(col in sorted_data.columns for col in ['PROVINSI', 'KABUPATEN', 'KECAMATAN', 'DESA', 'DUSUN']):
    # Melakukan groupby berdasarkan beberapa kolom
    treemap_data = sorted_data.groupby(['PROVINSI', 'KABUPATEN', 'KECAMATAN', 'DESA', 'DUSUN']).size().reset_index(name='Jumlah')
    
    # Membuat treemap
    fig_treemap = px.treemap(
        treemap_data, 
        path=['PROVINSI', 'KABUPATEN', 'KECAMATAN', 'DESA', 'DUSUN'], 
        values='Jumlah', 
        color='Jumlah', 
        color_continuous_scale='Viridis',
        title="Treemap Persebaran Siswa Berdasarkan Provinsi, Kabupaten, Kecamatan, dan Desa",
        hover_data={'Jumlah': True}
    )

    fig_treemap.update_traces(
        texttemplate='%{label}<br>Jumlah: %{value}',
        textposition='middle center'
    )

    st.plotly_chart(fig_treemap, use_container_width=True)

# Pilih kategori untuk Pie Chart
st.subheader("Grafik Pie Chart Berdasarkan Filter")
pie_column = st.selectbox(
    "Pilih Kategori untuk Pie Chart:", 
    kategori_options,
    index=0
)

# Buat Pie Chart berdasarkan filtered_data
def create_pie_chart(data, column_name):
    counts = data[column_name].value_counts().reset_index()
    counts.columns = [column_name, 'Jumlah']

    fig = px.pie(
        counts, 
        names=column_name, 
        values='Jumlah', 
        title=f"Distribusi Data Berdasarkan {column_name}",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    # Tambahkan persentase di dalam chart
    fig.update_traces(textposition='inside', textinfo='percent+label')

    st.plotly_chart(fig, use_container_width=True)

# Tampilkan Pie Chart berdasarkan pilihan pengguna
if not filtered_data.empty:
    create_pie_chart(filtered_data, pie_column)
else:
    st.warning("Tidak ada data untuk menampilkan Pie Chart berdasarkan filter.")
