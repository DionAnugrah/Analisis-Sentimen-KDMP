# 🔴 Sistem Analisis Sentimen KDMP

Aplikasi web modern untuk analisis sentimen dan klastering topik komentar TikTok Koperasi Desa Merah Putih dengan dukungan **Dark Mode**.

## ✨ Fitur Utama

### 1. Analisis Sentimen
- Klasifikasi otomatis: **Positif**, **Netral**, **Negatif**
- Tingkat keyakinan untuk setiap prediksi
- Visualisasi hasil yang interaktif dengan SVG icons profesional

### 2. Klastering Topik
- Pengelompokan komentar berdasarkan topik
- Ekstraksi kata kunci otomatis per klaster
- Visualisasi distribusi klaster

### 3. Mode Analisis
- **Analisis Tunggal**: Analisis satu komentar dengan hasil detail
- **Analisis Batch**: Proses ribuan komentar dari file CSV
- **Info Klaster**: Eksplorasi kata kunci dan topik

### 4. Dark Mode
- Toggle antara light mode dan dark mode
- Warna dominan **merah dan putih** sesuai branding KDMP
- Design responsif untuk semua ukuran layar

## 🚀 Cara Menjalankan

### Prasyarat
```bash
pip install -r requirements.txt
```

### Menjalankan Aplikasi
```bash
streamlit run app.py
```

Aplikasi akan terbuka di browser pada `http://localhost:8501`

## 📁 Struktur File

```
├── app.py                          # Aplikasi web utama
├── preprocessing.py                # Modul preprocessing teks
├── model_sentimen_kdmp.joblib      # Model klasifikasi sentimen
├── model_klaster_kdmp.joblib       # Model klastering topik
└── requirements.txt                # Dependensi Python
```

## 🎨 Tampilan Modern

Aplikasi ini menampilkan:
- **Design modern** dengan warna dominan **merah dan putih** (branding KDMP)
- **SVG icons profesional** menggantikan emoji untuk tampilan yang lebih profesional
- **Dark Mode support** dengan toggle button di pojok kanan atas
- **Gradient effects** pada header dan components
- **Color palette** yang konsisten:
  - Merah (#dc2626) untuk primary dan negative sentiment
  - Hijau (#10b981) untuk positive sentiment
  - Abu-abu (#6b7280) untuk neutral sentiment
- **Responsive layout** yang optimal di berbagai ukuran layar
- **Interactive components** dengan smooth transitions
- **Professional cards** dengan shadow dan hover effects

## 🔧 Teknologi

- **Streamlit**: Framework web app
- **scikit-learn**: Machine learning models
- **Pandas**: Data processing
- **NumPy**: Numerical computing
- **Joblib**: Model serialization

## 📊 Model

### Model Sentimen
- Algoritma: SVM / Naive Bayes
- Output: Positif, Netral, Negatif
- Feature: TF-IDF vectorization

### Model Klaster
- Algoritma: K-Means clustering
- Feature: TF-IDF + SVD dimensionality reduction
- Normalisasi: L2 normalization

## 📝 Format Data CSV

Untuk analisis batch, file CSV harus memiliki struktur:

```csv
comment
"Komentar pertama di sini"
"Komentar kedua di sini"
...
```

Atau dengan kolom lain:
```csv
id,comment,timestamp
1,"Komentar pertama",2024-01-01
2,"Komentar kedua",2024-01-02
```

## 🎯 Use Cases

1. **Monitoring Brand Sentiment**: Pantau persepsi publik terhadap KDMP
2. **Topic Discovery**: Temukan topik yang sering dibahas
3. **Customer Feedback Analysis**: Analisis feedback pelanggan secara otomatis
4. **Social Media Analytics**: Evaluasi engagement di media sosial

## 📈 Output

### Analisis Tunggal
- Prediksi sentimen dengan confidence score
- Klaster topik dengan kata kunci
- Teks hasil preprocessing

### Analisis Batch
- File CSV dengan kolom tambahan:
  - `sentimen_prediksi`: Label sentimen
  - `klaster`: ID klaster topik
  - `teks_bersih`: Teks setelah preprocessing
- Visualisasi distribusi sentimen dan klaster
- Filter interaktif

## 🔒 Preprocessing

Tahapan preprocessing otomatis:
1. Lowercase conversion
2. Emoji removal/conversion
3. Slang normalization
4. Stopword removal
5. Tokenization
6. Stemming/Lemmatization

---

© 2026 Koperasi Desa Merah Putih
