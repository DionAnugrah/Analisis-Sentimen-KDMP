"""Bagian Technology: kartu teknologi, status model, dan detail preprocessing."""
import glob
import os
from html import escape

import streamlit as st

from config import BASE_DIR, NAMA_BERT, NAMA_SVM
from core import metrik
from core.models import Models
from core.prep import ERR_PREP, clean_text_bert
from ui.components import (
    bagian_judul, card, daftar_html, grafik_grup, grid, matriks_proporsi, notif, section, tabel_kelas, tech_card,
)
from ui.utils import tulis_html


def _status(nama: str, aktif: bool) -> str:
    kelas, teks = ("on", "Aktif") if aktif else ("off", "Tidak aktif")
    return f'<span class="srv"><i class="dot {kelas}"></i>{escape(nama)}<b class="st {kelas}">{teks}</b></span>'


def render(models: Models) -> None:
    bagian_judul(
        "technology", "Technology Stack", 'Teknologi yang <span class="acc">Digunakan</span>',
        "Kombinasi algoritma Machine Learning dan Natural Language Processing "
        "untuk menganalisis sentimen komentar berbahasa Indonesia.",
    )
    tulis_html(grid([
        tech_card("message", "IndoBERT",
                  "Model bahasa berbasis transformer untuk Bahasa Indonesia. Membaca konteks kalimat dan "
                  "menghasilkan probabilitas tiap sentimen.", "NLP Model"),
        tech_card("chart", "SVM",
                  "Support Vector Machine yang bekerja di atas fitur TF-IDF. Ringan dan cepat untuk klasifikasi teks.",
                  "ML Algorithm"),
        tech_card("table", "TF-IDF",
                  "Mengubah teks menjadi representasi numerik berdasarkan bobot kata, dipakai sebagai fitur SVM.",
                  "Feature Extraction"),
        tech_card("layers", "Preprocessing",
                  "Pembersihan teks: normalisasi singkatan, penanganan emoji, tawa, dan sindiran, "
                  "serta penghapusan stopword (khusus SVM).", "Text Cleaning"),
    ], 4))

    tulis_html(f'<div class="status-row">{_status(NAMA_SVM, models.ada_svm)}{_status(NAMA_BERT, models.ada_bert)}</div>')
    if not models.ada_bert:
        _diagnostik_indobert(models)

    _performa()

    with st.expander("Detail preprocessing per model", icon=":material/tune:"):
        tulis_html(grid([
            card("table", NAMA_SVM, daftar_html([
                "Singkatan dan slang dinormalkan (mis. gk menjadi tidak)",
                "Stopword dibuang, kata negasi dipertahankan",
                "Emoji diubah menjadi token teks",
                "Angka dan tanda baca dibuang",
                "Token identik yang berurutan digabung",
            ])),
            card("table", NAMA_BERT, daftar_html([
                "Emoji diubah menjadi kata berbahasa Indonesia",
                "Tawa dinormalkan (wkwkwk menjadi wkwk)",
                "Penanda <b>sindiran</b> ditambahkan bila pola sindiran terdeteksi",
                "Tanda baca dasar dipertahankan",
                "Stopword tidak dibuang",
            ])),
        ]))


def _performa() -> None:
    """Grafik perbandingan SVM vs IndoBERT dari hasil evaluasi (core/metrik.py)."""
    if not metrik.tersedia():
        return
    svm, bert = metrik.EVALUASI[NAMA_SVM], metrik.EVALUASI[NAMA_BERT]

    def seri(ambil):
        return [(NAMA_SVM, "var(--neu)", ambil(svm)), (NAMA_BERT, "var(--primary)", ambil(bert))]

    section("chart", "Perbandingan Performa Model", "Hasil evaluasi kedua model pada data uji.")
    tulis_html(grid([
        grafik_grup("chart", "Metrik Keseluruhan",
                    ["Accuracy", "Macro Precision", "Macro Recall", "Macro F1-score", "Weighted F1"],
                    seri(lambda e: [e["accuracy"], e["macro_precision"], e["macro_recall"], e["macro_f1"], e["weighted_f1"]])),
        grafik_grup("chart", "F1-score per Kelas", [k.title() for k in metrik.KELAS],
                    seri(lambda e: [e["per_kelas"][k][2] for k in metrik.KELAS])),
    ], 2))
    tulis_html(
        f'<div class="cap">Data uji: {NAMA_SVM} {svm["n_uji"]:,} komentar, {NAMA_BERT} {bert["n_uji"]:,} komentar. '
        f'Ukuran data uji berbeda, sehingga angka keduanya tidak sepenuhnya sebanding.</div>'
    )
    with st.expander("Detail per kelas dan confusion matrix", icon=":material/table_chart:"):
        tulis_html(grid([tabel_kelas(NAMA_SVM, svm["per_kelas"]), tabel_kelas(NAMA_BERT, bert["per_kelas"])], 2))
        tulis_html(grid([
            matriks_proporsi(f"Confusion Matrix {NAMA_SVM}", svm["confusion"], metrik.KELAS),
            matriks_proporsi(f"Confusion Matrix {NAMA_BERT}", bert["confusion"], metrik.KELAS),
        ], 2))


def _versi_pustaka(nama: str) -> str:
    try:
        return f"{nama} {__import__(nama).__version__}"
    except Exception as e:
        return f"{nama} GAGAL: {e}"


def _diagnostik_indobert(models: Models) -> None:
    notif("warn", "Model IndoBERT belum aktif, jadi perbandingan model belum tersedia. "
                  f"{escape(models.err_indobert or '')}")
    with st.expander("Diagnostik IndoBERT", icon=":material/bug_report:"):
        ada = sorted(os.path.basename(x) for x in glob.glob(os.path.join(BASE_DIR, "*.joblib")))
        st.code(
            f"folder app.py : {BASE_DIR}\n"
            f"folder kerja  : {os.getcwd()}\n"
            f"joblib di sana: {ada or '(tidak ada)'}\n"
            f"kdmp_prep     : {'OK' if clean_text_bert else ERR_PREP}\n"
            f"{_versi_pustaka('torch')}\n{_versi_pustaka('transformers')}",
            language="text",
        )
