"""Pemuatan model sentimen: SVM (TF-IDF) dan IndoBERT."""
import glob
import io
import os
from dataclasses import dataclass
from typing import Any, Optional, Tuple

import joblib
import streamlit as st

from config import BASE_DIR, BERT_MAX_LEN_DEFAULT, DIR_INDOBERT, MODEL_INDOBERT, MODEL_SENTIMEN
from core.prep import ERR_PREP, clean_text_bert


@dataclass
class Models:
    """Model sentimen yang berhasil dimuat (None bila tidak tersedia)."""
    sentimen: Any = None                      # SVM (TF-IDF)
    indobert: Any = None                      # paket IndoBERT
    err_indobert: Optional[str] = None

    @property
    def ada_svm(self) -> bool:
        return self.sentimen is not None

    @property
    def ada_bert(self) -> bool:
        return self.indobert is not None

    @property
    def ada_model(self) -> bool:
        return self.ada_svm or self.ada_bert

    @property
    def bisa_bandingkan(self) -> bool:
        return self.ada_svm and self.ada_bert


# ---------------------------------------------------------------- SVM
@st.cache_resource(show_spinner="Memuat model...")
def muat_model(path):
    return joblib.load(path) if os.path.exists(path) else None


# ---------------------------------------------------------------- IndoBERT
def cari_indobert() -> Optional[str]:
    """Cari berkas .joblib / folder IndoBERT di folder app.py, lalu di folder kerja saat ini."""
    folders = [BASE_DIR] + ([os.getcwd()] if os.getcwd() != BASE_DIR else [])
    for f in folders:
        p = os.path.join(f, MODEL_INDOBERT)
        if os.path.exists(p):
            return p
    for f in folders:                                  # nama lain, mis. indobert_apa_saja.joblib
        c = sorted(glob.glob(os.path.join(f, "*indobert*.joblib")))
        if c:
            return c[0]
    for f in folders:
        p = os.path.join(f, DIR_INDOBERT)
        if os.path.isdir(p):
            return p
    return None


def _muat_folder_hf(path) -> dict:
    """Muat model dari folder hasil save_pretrained."""
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(path)
    mdl = AutoModelForSequenceClassification.from_pretrained(path).to("cpu").eval()
    labels = [mdl.config.id2label[i] for i in range(mdl.config.num_labels)]
    return {"model": mdl, "tokenizer": tok, "labels": labels, "max_len": BERT_MAX_LEN_DEFAULT}


def _muat_joblib_cpu(path):
    """joblib.load; bila model disimpan di GPU tetapi dimuat di komputer tanpa GPU, paksa ke CPU."""
    import torch
    try:
        return joblib.load(path)
    except Exception as e:
        if "cuda" not in str(e).lower():
            raise

    def _ke_cpu(b):
        try:
            return torch.load(io.BytesIO(b), map_location="cpu", weights_only=False)
        except TypeError:
            return torch.load(io.BytesIO(b), map_location="cpu")

    torch.storage._load_from_bytes = _ke_cpu
    return joblib.load(path)


def _muat_paket_joblib(path) -> dict:
    paket = _muat_joblib_cpu(path)
    if not isinstance(paket, dict):
        raise ValueError("isi joblib bukan paket {model, tokenizer, labels, max_len}; "
                         "simpan ulang dengan kode paket dari notebook")
    for k in ("model", "tokenizer"):
        if k not in paket:
            raise ValueError(f"kunci '{k}' tidak ada di dalam joblib")
    mdl = paket["model"].to("cpu").eval()
    paket["model"] = mdl
    paket.setdefault("max_len", BERT_MAX_LEN_DEFAULT)
    paket.setdefault("labels", [mdl.config.id2label[i] for i in range(mdl.config.num_labels)])
    return paket


@st.cache_resource(show_spinner="Memuat model IndoBERT...")
def _muat_paket_indobert(path):
    """Gagal -> raise. Hasil gagal tidak di-cache, jadi cukup refresh setelah masalah diperbaiki."""
    return _muat_folder_hf(path) if os.path.isdir(path) else _muat_paket_joblib(path)


def muat_indobert() -> Tuple[Optional[dict], Optional[str]]:
    """Kembalikan (paket, pesan_error)."""
    if clean_text_bert is None:
        return None, ERR_PREP
    path = cari_indobert()
    if path is None:
        return None, f"{MODEL_INDOBERT} tidak ditemukan di {BASE_DIR}"
    try:
        return _muat_paket_indobert(path), None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"[:220]


def muat_semua() -> Models:
    paket, err = muat_indobert()
    return Models(
        sentimen=muat_model(MODEL_SENTIMEN),
        indobert=paket,
        err_indobert=err,
    )
