"""Tab 2: analisis batch dari berkas CSV, dengan perbandingan SVM vs IndoBERT."""
from html import escape

import pandas as pd
import streamlit as st

from config import (
    BATAS_BARIS_BERT, BATAS_BARIS_MIN, BATAS_BARIS_SVM, KOL_BERT, KOL_SAMA, KOL_SVM,
    NAMA_BERT, NAMA_SVM,
)
from core.models import Models
from core.pipeline import jalankan_batch
from ui.components import (
    bar_distribusi_sentimen, notif, progress_html, section, stat_card, tabel_silang,
    urutkan_sentimen,
)
from ui.theme import current_theme, warna
from ui.utils import STRETCH, tulis_html

_SENTIMEN = ["positif", "netral", "negatif"]
_IKON_SENTIMEN = ["plus", "minus", "x"]
_FILTER_SAMA = ["Semua", "Kedua model sama", "Kedua model berbeda"]


def render(models: Models) -> None:
    section("chart", "Analisis Batch (File CSV)",
            "Unggah file CSV untuk menganalisis banyak komentar sekaligus.")

    data = _unggah_csv()
    if data is not None:
        st.markdown("---")
        _form_proses(data, models)

    if "hasil" in st.session_state:
        _tampilkan_hasil(st.session_state["hasil"])


# ---------------------------------------------------------------- unggah
def _unggah_csv():
    col_unggah, col_info = st.columns([2, 1])
    with col_unggah:
        berkas = st.file_uploader(
            "Pilih file CSV",
            type=["csv"],
            help="File CSV harus memiliki kolom yang berisi komentar",
        )
    if berkas is None:
        return None

    try:
        data = pd.read_csv(berkas, dtype=str)
        with col_info:
            st.metric("Total Baris", f"{len(data):,}")
            st.metric("Total Kolom", len(data.columns))
    except Exception as e:
        notif("err", f"Gagal membaca file CSV: {escape(str(e))}")
        st.stop()
    return data


# ---------------------------------------------------------------- proses
def _form_proses(data: pd.DataFrame, models: Models) -> None:
    col1, col2 = st.columns(2)

    with col1:
        default = list(data.columns).index("comment") if "comment" in data.columns else 0
        kolom = st.selectbox("Kolom komentar", data.columns, index=default)

    with col2:
        batas_default = BATAS_BARIS_BERT if models.ada_bert else BATAS_BARIS_SVM
        batas = st.number_input(
            "Batas baris diproses",
            BATAS_BARIS_MIN,
            max(len(data), BATAS_BARIS_MIN),
            max(BATAS_BARIS_MIN, min(len(data), batas_default)),
            step=100,
        )

    if not st.button("Proses Semua Data", type="primary", icon=":material/rocket_launch:", **STRETCH):
        return

    slot = st.empty()
    tulis_html(progress_html(0, "Memulai..."), target=slot)
    hasil = jalankan_batch(
        data, kolom, batas, models,
        progress=lambda persen, teks: tulis_html(progress_html(persen, teks), target=slot),
    )
    st.session_state["hasil"] = hasil
    notif("ok", "Proses berhasil!")


# ---------------------------------------------------------------- hasil
def _model_tersedia(hasil: pd.DataFrame):
    """[(nama model, nama kolom)] untuk model yang ada di tabel hasil."""
    return [(n, k) for n, k in ((NAMA_SVM, KOL_SVM), (NAMA_BERT, KOL_BERT)) if k in hasil]


def _tampilkan_hasil(hasil: pd.DataFrame) -> None:
    tulis_html(
        f'<div class="part-sub">Hasil model bisa saja salah. Cek kembali hasil yang diberikan model</div>'
    )

    st.markdown("---")
    section("trend", "Ringkasan Hasil")
    _kartu_ringkasan(hasil)
    st.markdown("<br>", unsafe_allow_html=True)
    _grafik_perbandingan(hasil)

    st.markdown("---")
    section("table", "Data Hasil")
    _tabel_dan_unduh(hasil)


def _kartu_ringkasan(hasil: pd.DataFrame) -> None:
    n = len(hasil)
    kolom = st.columns(4)
    with kolom[0]:
        tulis_html(stat_card("users", "Total Diproses", f"{n:,}", "var(--primary)", "var(--primary-soft)"))

    if KOL_SAMA in hasil:                                   # mode perbandingan
        sama = int(hasil[KOL_SAMA].sum())
        beda = n - sama
        pos, warn = warna("positif"), current_theme()["warn"]
        kartu = [
            ("check", "Kesesuaian Model", f"{sama / n * 100 if n else 0:.1f}%", "var(--primary)", "var(--primary-soft)"),
            ("ok", "Label Sama", f"{sama:,}", pos, f"{pos}22"),
            ("warn", "Label Berbeda", f"{beda:,}", warn, f"{warn}22"),
        ]
        for kol, args in zip(kolom[1:], kartu):
            with kol:
                tulis_html(stat_card(*args))
        return

    tersedia = _model_tersedia(hasil)                       # hanya satu model aktif
    if not tersedia:
        return
    counts = hasil[tersedia[0][1]].value_counts()
    for kol, nama, ikon in zip(kolom[1:], _SENTIMEN, _IKON_SENTIMEN):
        with kol:
            c = warna(nama)
            tulis_html(stat_card(ikon, nama.title(), f"{int(counts.get(nama, 0)):,}", c, f"{c}22"))


def _grafik_perbandingan(hasil: pd.DataFrame) -> None:
    tersedia = _model_tersedia(hasil)
    if not tersedia:
        return

    for kol, (nama, kolom) in zip(st.columns(len(tersedia)), tersedia):
        with kol:
            tulis_html(bar_distribusi_sentimen(f"Distribusi Sentimen &middot; {escape(nama)}", hasil[kolom].value_counts()))

    if KOL_SAMA in hasil:
        urut = urutkan_sentimen(dict.fromkeys([*hasil[KOL_SVM].unique(), *hasil[KOL_BERT].unique()]))
        ct = (pd.crosstab(hasil[KOL_SVM], hasil[KOL_BERT])
              .reindex(index=urut, columns=urut, fill_value=0))
        tulis_html(tabel_silang("Matriks Kesesuaian Model", ct, NAMA_SVM, NAMA_BERT))


def _tabel_dan_unduh(hasil: pd.DataFrame) -> None:
    tersedia = _model_tersedia(hasil)

    col_a, col_b = st.columns(2)
    with col_a:
        label = sorted({v for _, k in tersedia for v in hasil[k].unique()})
        pilihan = st.multiselect(
            "Filter berdasarkan sentimen",
            label,
            help="Tampilkan baris yang diprediksi sentimen terpilih oleh salah satu model",
        )
    with col_b:
        kesesuaian = (st.selectbox("Filter kesesuaian model", _FILTER_SAMA)
                      if KOL_SAMA in hasil else _FILTER_SAMA[0])

    tampil = hasil
    if pilihan:
        cocok = pd.Series(False, index=tampil.index)
        for _, k in tersedia:
            cocok |= tampil[k].isin(pilihan)
        tampil = tampil[cocok]
    if kesesuaian == _FILTER_SAMA[1]:
        tampil = tampil[tampil[KOL_SAMA]]
    elif kesesuaian == _FILTER_SAMA[2]:
        tampil = tampil[~tampil[KOL_SAMA]]

    st.caption(f"Menampilkan {len(tampil):,} dari {len(hasil):,} baris")
    st.dataframe(tampil, height=400, **STRETCH)

    st.download_button(
        "Unduh Hasil Lengkap (CSV)",
        hasil.to_csv(index=False).encode("utf-8-sig"),
        "hasil_analisis_kdmp.csv",
        "text/csv",
        icon=":material/download:",
        **STRETCH,
    )
