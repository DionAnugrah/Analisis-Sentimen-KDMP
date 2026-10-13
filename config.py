"""Konfigurasi dan konstanta aplikasi KDMP."""
import os

# Folder tempat app.py berada (juga tempat berkas model dicari)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---- Berkas model
MODEL_SENTIMEN = "model_sentimen_kdmp.joblib"
MODEL_INDOBERT = "indobert_sentimen_kdmp.joblib"   # paket joblib dari notebook IndoBERT
DIR_INDOBERT = "model_indobert_sentimen_kdmp"      # alternatif: folder hasil save_pretrained

# ---- Nama model (tampil di UI)
NAMA_SVM = "SVM (TF-IDF)"
NAMA_BERT = "IndoBERT"

# ---- Sentimen
URUTAN_SENTIMEN = ("positif", "netral", "negatif")

# ---- Nama kolom pada tabel hasil batch
KOL_SVM = "sentimen_svm"
KOL_BERT = "sentimen_indobert"
KOL_KEYAKINAN_BERT = "keyakinan_indobert"
KOL_SAMA = "kedua_model_sama"
KOL_TEKS_BERSIH = "teks_bersih"

# ---- Parameter pemrosesan
BERT_BATCH_SIZE = 32
BERT_MAX_LEN_DEFAULT = 64

BATAS_BARIS_MIN = 100
BATAS_BARIS_BERT = 2000      # IndoBERT di CPU lebih lambat
BATAS_BARIS_SVM = 20000
