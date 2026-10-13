"""Bagian Coba (Try It Now): kartu alat analisis, tab Tunggal dan Batch."""
import streamlit as st

from core.models import Models
from ui.components import bagian_judul, notif
from ui.layout import kontainer
from ui.tabs import batch, single


def render(models: Models) -> None:
    bagian_judul(
        "coba", "Try It Now", 'Coba <span class="acc">Prediksi Sentimen</span>',
        "Masukkan komentar dalam Bahasa Indonesia dan lihat hasil analisis sentimen dari kedua model AI kami.",
    )
    with kontainer("tool_card"):
        if not models.ada_model:
            notif("err", "Tidak ada file model. Letakkan file <code>.joblib</code> dari notebook "
                         "di folder yang sama dengan <code>app.py</code>, lalu muat ulang halaman.")
            return
        if not models.bisa_bandingkan:
            notif("info", "Perbandingan model membutuhkan <b>kedua</b> model aktif. "
                          "Saat ini hanya satu model yang dipakai.")

        tab_tunggal, tab_batch = st.tabs([
            ":material/chat: Analisis Tunggal",
            ":material/table_chart: Analisis Batch",
        ])
        with tab_tunggal:
            single.render(models)
        with tab_batch:
            batch.render(models)
