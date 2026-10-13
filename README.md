# 🔴 KDMP - Sistem Analisis Sentimen Komentar TikTok

Aplikasi web modern berbasis Machine Learning dan Deep Learning untuk analisis sentimen komentar publik mengenai **Koperasi Desa Merah Putih (KDMP)**. Sistem ini mengusung pendekatan **Dual Model (SVM & IndoBERT)** untuk memberikan verifikasi silang (cross-verification) prediksi sentimen yang akurat, andal, dan transparan.

Aplikasi web modern untuk analisis sentimen dan klastering topik komentar TikTok Koperasi Desa Merah Putih dengan dukungan **Dark Mode**.

## ✨ Fitur Utama

### 1. Dual Model Prediction
- Menggabungkan dua arsitektur model:
  - **SVM (Support Vector Machine)**: Cepat dan efisien dengan ekstraksi fitur TF-IDF.
  - **IndoBERT**: Model berbasis Transformer mutakhir untuk memahami konteks semantik bahasa Indonesia secara mendalam.
- Hasil prediksi kedua model ditampilkan berdampingan (*side-by-side*) untuk perbandingan langsung.

### 2. Dual Verification & Cross-Analysis
- Indikator otomatis kesepakatan model (*Agree / Disagree*).
- Matriks kesesuaian model (*Cross-tabulation Agreement Matrix*) pada analisis batch untuk melihat korelasi prediksi kedua model.
- Skor keyakinan (*confidence score*) dan distribusi probabilitas tiap kelas sentimen (**Positif**, **Netral**, **Negatif**).

### 3. Dua Mode Analisis
- **Analisis Tunggal (Single)**:
  - Input teks interaktif dengan fitur *Quick Test* (contoh positif, netral, negatif).
  - Inspeksi hasil teks pasca-preprocessing untuk masing-masing model.
  - Tampilan visual kartu sentimen dengan persentase keyakinan.
- **Analisis Batch (CSV)**:
  - Unggah berkas CSV dan pilih kolom komentar secara dinamis.
  - Pengaturan batas baris pemrosesan yang fleksibel.
  - Indikator progress bar pemrosesan real-time.
  - Grafik distribusi sentimen interaktif per model.
  - Filter data hasil berdasarkan sentimen dan kesesuaian model.
  - Ekspor/unduh hasil analisis lengkap ke format CSV.

### 4. Preprocessing Khusus per Model
- **Pipeline SVM (`preprocessing.py`)**:
  - Konversi huruf kecil (*case folding*), pembersihan URL, mention, dan karakter berulang.
  - Normalisasi slang dan singkatan informal bahasa Indonesia.
  - Penghapusan stopword (Sastrawi) dengan mempertahankan kata negasi.
  - Konversi emoji menjadi token representatif teks.
- **Pipeline IndoBERT (`kdmp_prep.py`)**:
  - Menjaga struktur alami kalimat untuk input Transformer.
  - Konversi emoji ke nama/deskripsi bahasa Indonesia (library `emoji`).
  - Normalisasi variasi kata tawa (*wkwk, haha, xixi, dll.*).
  - Deteksi pola penanda sindiran/sarkasme kontekstual.

### 5. Tampilan Modern Single-Page (Dark & Light Mode)
- Desain *one-page* dengan navigasi *smooth scroll*: **Home**, **About**, **Technology**, **Features**, dan **Coba (Try It Now)**.
- Desain profesional bernuansa branding KDMP (Merah & Putih).
- Dukungan tema **Dark Mode** dan **Light Mode** dengan *toggle switch*.
- Visualisasi metrik performa model (Accuracy, Precision, Recall, F1-Score, dan Confusion Matrix).

---

## 📊 Performa Model (Data Uji)

Berdasarkan hasil evaluasi pada notebook pelatihan:

| Metrik | SVM (TF-IDF) | IndoBERT |
| :--- | :---: | :---: |
| **Akurasi** | 85.45% | **98.92%** |
| **Macro Precision** | 85.85% | **98.56%** |
| **Macro Recall** | 87.30% | **98.41%** |
| **Macro F1-Score** | 86.19% | **98.49%** |
| **Weighted F1-Score** | 85.27% | **98.92%** |
| **Jumlah Data Uji** | 14.182 baris | 11.125 baris |

---

## 📁 Struktur Direktori

```text
├── .streamlit/
│   └── config.toml               # Konfigurasi server & tema dasar Streamlit
├── core/                         # Modul logika bisnis non-UI
│   ├── __init__.py
│   ├── metrik.py                 # Data metrik evaluasi model dari notebook
│   ├── models.py                 # Pemuatan model SVM & IndoBERT (CPU/GPU fallback)
│   ├── pipeline.py               # Pipeline inferensi analisis tunggal & batch
│   ├── prep.py                   # Wrapper integrasi modul preprocessing
│   └── sentiment.py              # Logika prediksi kelas & distribusi probabilitas
├── createModel/                  # Jupyter Notebook pelatihan model
│   ├── 01_Klasifikasi_SVM.ipynb
│   └── 02_Klasifikasi_IndoBERT.ipynb
├── ui/                           # Antarmuka web pengguna & styling
│   ├── __init__.py
│   ├── components.py             # Komponen UI modular (kartu, bar chart, notifikasi)
│   ├── icons.py                  # Koleksi ikon SVG kustom & favicon
│   ├── layout.py                 # Komponen layout (header navbar, footer, kontainer)
│   ├── styles.css                # File styling CSS kustom (Light & Dark theme)
│   ├── theme.py                  # Manajemen state tema & palet warna
│   ├── utils.py                  # Helper fungsi HTML render & layout Streamlit
│   ├── bagian/                   # Seksi halaman utama (Single Page Scroll)
│   │   ├── home.py               # Hero section & ringkasan akurasi model
│   │   ├── about.py              # Ringkasan sistem & contoh klasifikasi
│   │   ├── technology.py         # Tech stack, status model, & perbandingan performa
│   │   ├── features.py           # Kartu 6 fitur unggulan sistem
│   │   └── coba.py               # Kontainer alat analisis (Try It Now)
│   └── tabs/                     # Tab alat analisis pada seksi Coba
│       ├── single.py             # Tab analisis satu komentar
│       └── batch.py              # Tab analisis berkas CSV batch
├── app.py                        # Entry point aplikasi Streamlit
├── config.py                     # Konfigurasi aplikasi, path model, & parameter batas
├── kdmp_prep.py                  # Modul preprocessing khusus IndoBERT
├── preprocessing.py              # Modul preprocessing khusus SVM (TF-IDF)
├── model_sentimen_kdmp.joblib    # Bobot model klasifikasi SVM terlatih
├── indobert_sentimen_kdmp.joblib # Paket model IndoBERT terlatih (model, tokenizer, config)
├── dataset_komentar.csv          # Contoh dataset komentar
├── requirements.txt              # Daftar dependensi pustaka Python
├── .gitignore                    # Konfigurasi file yang diabaikan oleh Git
└── README.md                     # Dokumentasi proyek
```

---

## 🔧 Teknologi yang Digunakan

- **Framework Web**: [Streamlit](https://streamlit.io/) (>= 1.35.0)
- **Deep Learning / NLP**: [PyTorch](https://pytorch.org/) (`torch`), [Hugging Face Transformers](https://huggingface.co/transformers/) (`transformers`)
- **Machine Learning**: [scikit-learn](https://scikit-learn.org/)
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Text Processing & Preprocessing**: [PySastrawi](https://github.com/harisbc/pysastrawi) (`Sastrawi`), [emoji](https://github.com/carpedm20/emoji)
- **Model Serialization**: [Joblib](https://joblib.readthedocs.io/)

---

## 🚀 Cara Menjalankan Aplikasi

### 1. Prasyarat Lingkungan
Pastikan Anda menggunakan Python **>= 3.9** (disarankan Python 3.10 / 3.11).

Buat dan aktifkan virtual environment (opsional namun disarankan):
```bash
# Membuat virtual environment
python -m venv venv

# Mengaktifkan di Linux/macOS:
source venv/bin/activate

# Mengaktifkan di Windows (PowerShell):
.\venv\Scripts\Activate.ps1
```

### 2. Instalasi Dependensi
Instal seluruh paket dependensi yang dibutuhkan:
```bash
pip install -r requirements.txt
```

### 3. Memastikan File Model Tersedia
Pastikan file model berada pada direktori utama proyek:
- `model_sentimen_kdmp.joblib` (Model SVM)
- `indobert_sentimen_kdmp.joblib` (Paket IndoBERT)

> **Catatan**: Jika file model IndoBERT berukuran besar (> 100MB), pastikan file tersebut telah diunduh atau diekspor dari notebook pelatihan `createModel/02_Klasifikasi_IndoBERT.ipynb` ke root folder proyek.

### 4. Menjalankan Server Web Streamlit
Jalankan perintah berikut pada terminal di folder proyek:
```bash
streamlit run app.py
```

Aplikasi otomatis dapat diakses melalui peramban web pada alamat default:
```
http://localhost:8501
```

---

## 📝 Format Data Analisis Batch (CSV)

### Format Berkas Masukan (Input)
File CSV minimal memiliki 1 kolom yang memuat teks komentar. Nama kolom bebas (sistem dapat mendeteksi otomatis kolom `comment` atau pengguna dapat memilih kolom yang diinginkan dari menu dropdown):

```csv
comment
"Program koperasi merah putih sangat membantu masyarakat desa."
"Pelayanannya lambat dan respon admin kurang memuaskan."
"Berapa harga gas elpiji dan bagaimana cara daftarnya?"
```

### Format Berkas Hasil Unduhan (Output)
Hasil analisis yang diunduh (`hasil_analisis_kdmp.csv`) memuat seluruh kolom asli ditambah dengan:
- `teks_bersih`: Teks setelah melalui tahapan pembersihan.
- `sentimen_svm`: Prediksi label sentimen dari model SVM (`positif`, `netral`, atau `negatif`).
- `sentimen_indobert`: Prediksi label sentimen dari model IndoBERT (`positif`, `netral`, atau `negatif`).
- `keyakinan_indobert`: Nilai tingkat kepercayaan prediksi IndoBERT (0.0000 - 1.0000).
- `kedua_model_sama`: Status kesepakatan kedua model (`True` jika sama, `False` jika berbeda).

---

## ⚖️ Lisensi & Hak Cipta

© 2026 Koperasi Desa Merah Putih (KDMP). Dikembangkan untuk analisis dan pemantauan sentimen opini publik.
