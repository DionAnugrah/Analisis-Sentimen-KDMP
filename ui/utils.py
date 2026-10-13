"""Utilitas tampilan: kompatibilitas versi Streamlit dan render HTML."""
import re

import streamlit as st

# Parameter "lebar penuh" berbeda antar versi Streamlit
_VER = tuple(int(x) for x in re.findall(r"\d+", st.__version__)[:2])
STRETCH = {"width": "stretch"} if _VER >= (1, 50) else {"use_container_width": True}


def tulis_html(s: str, target=st) -> None:
    """Render HTML tanpa baris kosong/indentasi agar tidak dibaca sebagai blok kode markdown.

    ``target`` boleh berupa placeholder ``st.empty()`` agar isinya bisa diperbarui.
    """
    target.markdown(re.sub(r"\n\s*", "", s.strip()), unsafe_allow_html=True)
