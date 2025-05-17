import pandas as pd
import plotly.express as px
import streamlit as st

# Konfigurasi Streamlit
st.set_page_config(page_title="Dashboard Data SMK", layout="wide")

# Daftar kategori
kategori_options = ['KELAS', 'DESA', 'KECAMATAN', 'KABUPATEN', 'PROVINSI']

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
required_columns = ['NAMA SISWA', 'KELAS', 'DESA', 'KECAMATAN', 'KABUPATEN', 'PROVINSI']
missing_columns = [col for col in required_columns if col not in data.columns]

if missing_columns:
    st.error(f"Kolom berikut tidak ditemukan dalam file: {', '.join(missing_columns)}")
    st.stop()

# Ganti seluruh baris yang berisi NaN dengan "Lainnya"
data = data.fillna("Lainnya")

# Hapus kolom 'Unnamed' atau 'None'
data = data.loc[:, ~data.columns.str.match('^Unnamed.*|^None$')]


# Sidebar untuk memilih kategori analisis
category = st.sidebar.selectbox("Pilih kategori untuk analisis:", kategori_options)
selected_province = st.sidebar.multiselect("Filter berdasarkan Provinsi:", data['PROVINSI'].unique())

# Filter berdasarkan provinsi
filtered_data = data[data['PROVINSI'].isin(selected_province)] if selected_province else data
selected_kabupaten = st.sidebar.multiselect("Filter berdasarkan Kabupaten:", filtered_data['KABUPATEN'].unique())

# Filter berdasarkan kabupaten
filtered_data = filtered_data[filtered_data['KABUPATEN'].isin(selected_kabupaten)] if selected_kabupaten else filtered_data
selected_kecamatan = st.sidebar.multiselect("Filter berdasarkan Kecamatan:", filtered_data['KECAMATAN'].unique())

# Filter berdasarkan kecamatan
filtered_data = filtered_data[filtered_data['KECAMATAN'].isin(selected_kecamatan)] if selected_kecamatan else filtered_data
selected_desa = st.sidebar.multiselect("Filter berdasarkan Desa:", filtered_data['DESA'].unique())

# Filter berdasarkan desa
filtered_data = filtered_data[filtered_data['DESA'].isin(selected_desa)] if selected_desa else filtered_data
selected_class = st.sidebar.multiselect("Filter berdasarkan Kelas:", filtered_data['KELAS'].unique())

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
columns_to_display = ['No', 'NAMA SISWA', 'KELAS', 'DESA', 'KECAMATAN', 'KABUPATEN', 'PROVINSI']
existing_columns = [col for col in columns_to_display if col in sorted_data.columns]

# Tampilkan tabel data dengan fitur pencarian nama
st.subheader("Data Siswa")

# Input pencarian nama siswa
search_name = st.text_input("Cari Nama Siswa (berdasarkan kandungan nama):")

# Jika ada input pencarian, filter data berdasarkan nama
if search_name:
    # Pencarian berdasarkan kandungan nama (substring search)
    filtered_table_data = sorted_data[sorted_data['NAMA SISWA'].str.contains(search_name, case=False, na=False)]
else:
    filtered_table_data = sorted_data

# Tampilkan data dalam tabel
st.dataframe(filtered_table_data[existing_columns])


# Fungsi untuk membuat grafik bar (horizontal untuk KABUPATEN dan PROVINSI)
def create_bar_chart(data, column_name, color_column=None):
    # Jika ada color_column, maka tampilkan berdasarkan kedua kolom
    if color_column:
        counts = data.groupby([column_name, color_column]).size().reset_index(name='Jumlah')
        # Urutkan data dari jumlah terbesar ke terkecil
        counts = counts.sort_values('Jumlah', ascending=False)
        
        fig = px.bar(
            counts,
            y=column_name,
            x='Jumlah',
            color=color_column,
            orientation='h',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            text='Jumlah',
            title=f"Persebaran Data Berdasarkan {column_name} dan {color_column}"
        )
    else:
        # Jika hanya 1 kolom, tampilkan grafik sederhana
        counts = data[column_name].value_counts().reset_index()
        counts.columns = [column_name, 'Jumlah']
        # Urutkan data dari jumlah terbesar ke terkecil
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

    # Atur posisi teks agar terlihat
    fig.update_traces(textposition='outside', textfont_size=12)

    # Update layout
    fig.update_layout(
        xaxis_title="Jumlah",
        yaxis_title=column_name,
        xaxis_tickangle=0,
        yaxis=dict(showticklabels=True)
    )

    st.plotly_chart(fig, use_container_width=True)


# Tampilkan grafik untuk PROVINSI
st.subheader("Grafik Persebaran Data Berdasarkan Provinsi")
create_bar_chart(sorted_data, "PROVINSI")

# Tampilkan grafik untuk KABUPATEN dan PROVINSI
st.subheader("Grafik Persebaran Data Berdasarkan Kabupaten")
create_bar_chart(sorted_data, "KABUPATEN")




# Tambahkan Treemap
st.subheader("Treemap Persebaran Data Berdasarkan Provinsi, Kabupaten, Kecamatan, dan Desa")
if all(col in sorted_data.columns for col in ['PROVINSI', 'KABUPATEN', 'KECAMATAN', 'DESA']):
    treemap_data = sorted_data.groupby(['PROVINSI', 'KABUPATEN', 'KECAMATAN', 'DESA']).size().reset_index(name='Jumlah')

    fig_treemap = px.treemap(
        treemap_data, 
        path=['PROVINSI', 'KABUPATEN', 'KECAMATAN', 'DESA'], 
        values='Jumlah', 
        color='Jumlah', 
        color_continuous_scale='Viridis',
        title="Treemap Persebaran Siswa Berdasarkan Provinsi, Kabupaten, Kecamatan, dan Desa",
        hover_data={'Jumlah': True}
    )

    # Tambahkan keterangan jumlah langsung
    fig_treemap.update_traces(
        texttemplate='%{label}<br>Jumlah: %{value}',
        textposition='middle center'
    )

    st.plotly_chart(fig_treemap, use_container_width=True)

