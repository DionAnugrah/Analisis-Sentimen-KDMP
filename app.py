"""Aplikasi web KDMP: klasifikasi sentimen (SVM vs IndoBERT), satu halaman dengan navigasi gulir.
Jalankan:  streamlit run app.py   (dari folder ini)

Struktur:
    config.py         konstanta & nama berkas model
    core/             logika non-UI (model, prediksi, pipeline)
    ui/               tema, komponen HTML, navbar & footer
    ui/bagian/        bagian halaman, berurutan: Home, About, Technology, Features, Coba
    ui/tabs/          alat analisis di bagian Coba
"""
import streamlit as st

from core.models import muat_semua
from ui import theme
from ui.bagian import about, coba, features, home, technology
from ui.icons import buat_favicon
from ui.layout import footer, header


def main() -> None:
    st.set_page_config(
        page_title="KDMP - Analisis Sentimen",
        page_icon=buat_favicon(),
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    theme.init_state()
    theme.inject_css()

    models = muat_semua()

    header()
    for bagian in (home, about, technology, features, coba):     # urutan = urutan scroll
        bagian.render(models)
    footer()


main()
