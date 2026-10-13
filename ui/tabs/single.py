"""Tab 1: analisis satu komentar, hasil kedua model ditampilkan berdampingan."""
from html import escape

import streamlit as st

from core.models import Models
from core.pipeline import HasilTunggal, analisis_tunggal
from ui.components import kartu_sentimen, notif, section
from ui.utils import STRETCH, tulis_html


# (key tombol, label, contoh komentar) untuk Quick Test
_CONTOH = [
    ("qt_pos", "😊 Positif", "Programnya sangat membantu warga desa, semoga terus berjalan dengan baik"),
    ("qt_net", "😐 Netral", "Ada yang tahu jadwal rapat anggota koperasi desa bulan ini?"),
    ("qt_neg", "😡 Negatif", "Pelayanannya lambat dan tidak sesuai harapan, sangat mengecewakan"),
]


def _isi_contoh(teks: str) -> None:
    """on_click: dijalankan sebelum skrip dirender ulang, jadi boleh mengubah isi text_area."""
    st.session_state["komentar"] = teks


def render(models: Models) -> None:
    teks = st.text_area(
        "Input Komentar / Review",
        key="komentar",
        height=130,
        placeholder="Contoh: programnya bagus, pelayanan memuaskan...",
    )

    tulis_html('<div class="qt-label">Quick Test - Auto Fill:</div>')
    for kol, (key, label, contoh) in zip(st.columns(len(_CONTOH)), _CONTOH):
        with kol:
            st.button(label, key=key, on_click=_isi_contoh, args=(contoh,), **STRETCH)

    if not st.button("Analisis Sentimen", key="btn_analisis", type="primary",
                     icon=":material/auto_awesome:", **STRETCH):
        return
    if not teks.strip():
        notif("warn", "Silakan masukkan komentar terlebih dahulu.")
        return

    with st.spinner("Sedang menganalisis..."):
        hasil = analisis_tunggal(teks, models)

    st.markdown("---")
    section("trend", "Hasil Analisis")

    if hasil.ada_kosong:
        notif("warn", "Teks menjadi kosong setelah preprocessing. Hasil mungkin kurang akurat.")

    _tampilkan_kesimpulan(hasil)

    for kol, h in zip(st.columns(len(hasil.sentimen)), hasil.sentimen):
        with kol:
            kartu_sentimen(h)

    _tampilkan_preprocessing(hasil)


def _tampilkan_kesimpulan(hasil: HasilTunggal) -> None:
    if hasil.sepakat is None:
        return
    a, b = hasil.sentimen
    if hasil.sepakat:
        notif("ok", f"Kedua model sepakat: <b>{escape(str(a.label)).upper()}</b>.")
    else:
        notif("warn", f"Kedua model memberi label berbeda: {escape(a.nama)} = <b>{escape(str(a.label))}</b>, "
                      f"{escape(b.nama)} = <b>{escape(str(b.label))}</b>.")


def _tampilkan_preprocessing(hasil: HasilTunggal) -> None:
    with st.expander("Lihat Teks Hasil Preprocessing", icon=":material/manage_search:"):
        if hasil.bersih_svm is not None:
            st.caption("Preprocessing SVM:")
            st.code(hasil.bersih_svm[0] or "(kosong)", language="text")
        if hasil.bersih_bert is not None:
            st.caption("Preprocessing IndoBERT (emoji, tawa, dan sindiran dipertahankan):")
            st.code(hasil.bersih_bert[0] or "(kosong)", language="text")
