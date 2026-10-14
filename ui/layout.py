"""Kerangka halaman satu-halaman: navbar tetap (fixed) dan footer. Navigasi = tautan gulir (#id)."""
from datetime import datetime

import streamlit as st

from ui import theme
from ui.icons import logo
from ui.utils import STRETCH, tulis_html

# (id bagian, label) untuk navbar dan footer
NAV = [("home", "Home"), ("about", "About"), ("technology", "Technology"), ("features", "Features")]
_TEKNOLOGI_FOOTER = ["IndoBERT", "SVM", "TF-IDF", "Streamlit"]


def kontainer(key: str):
    """Container ber-key (memberi class CSS st-key-<key>); Streamlit lama tanpa dukungan key tetap jalan."""
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


def tautan(kunci: str, isi: str, kelas: str) -> str:
    """Tautan gulir ke bagian ber-id ``kunci`` (target _self agar tidak membuka tab baru)."""
    return f'<a class="{kelas}" href="#{kunci}" target="_self">{isi}</a>'


def header() -> None:
    """Navbar tetap di atas (position: fixed).

    Seluruh isinya satu blok HTML (brand di kiri, tautan + Try Now di kanan). Hanya tombol tema yang berupa
    widget Streamlit; CSS menaruhnya secara absolut di ujung kanan, jadi simetri tidak bergantung pada
    kolom internal Streamlit (st.columns).
    """
    dark = theme.is_dark()
    nav = "".join(tautan(k, label, "nav-link") for k, label in NAV) + tautan("coba", "Coba Sekarang", "nav-cta")
    with kontainer("header"):
        tulis_html(
            f'<div class="topbar"><div class="brand">{logo(42, "head")}<div class="brand-txt">'
            f'<div class="brand-name">KDMP Sentiment</div><div class="brand-sub">SVM and IndoBERT Algorithm</div></div></div>'
            f'<nav class="nav">{nav}</nav></div>'
        )
        st.button(
            "Terang" if dark else "Gelap",
            key="theme_toggle",
            icon=":material/light_mode:" if dark else ":material/dark_mode:",
            help="Ganti mode terang / gelap",
            on_click=theme.toggle_dark,
            **STRETCH,
        )


def footer() -> None:
    links = "".join(tautan(k, label, "f-link") for k, label in NAV)
    tech = "".join(f'<span class="f-link">{t}</span>' for t in _TEKNOLOGI_FOOTER)
    tulis_html(
        f"""
        <div class="footer2">
            <div class="f-grid">
                <div>
                    <div class="brand">{logo(38, "foot")}<div class="brand-txt">
                        <div class="brand-name">KDMP Sentiment</div><div class="brand-sub">SVM and IndoBERT Algorithm</div></div></div>
                    <div class="f-desc">Sistem analisis sentimen komentar Koperasi Desa Merah Putih
                    dengan perbandingan model SVM dan IndoBERT.</div>
                </div>
                <div><div class="f-h">Quick Links</div>{links}</div>
                <div><div class="f-h">Technology</div>{tech}</div>
            </div>
            <div class="f-copy">&copy; {datetime.now().year} Koperasi Desa Merah Putih - Sistem Analisis Sentimen</div>
        </div>
        """
    )
