"""Tema terang/gelap, warna sentimen, dan injeksi CSS."""
from functools import lru_cache
from pathlib import Path

import streamlit as st

from ui.utils import tulis_html

TEMA_TERANG = {
    "bg": "#fffaf8", "surface": "#ffffff", "surface-2": "#fff1f0",
    "border": "#efd5d1", "text": "#1f1717", "muted": "#6b5b5b",
    "primary": "#dc2626", "primary-dark": "#991b1b",
    "primary-soft": "rgba(220,38,38,.09)", "primary-line": "rgba(220,38,38,.28)",
    "shadow": "rgba(153,27,27,.22)",
    "card-shadow": "none",
    "glow1": "rgba(220,38,38,.11)", "glow2": "rgba(244,114,114,.10)",
    "nav-bg": "rgba(255,250,248,.82)",
    "pos": "#16a34a", "neu": "#64748b", "neg": "#dc2626",
    "warn": "#b45309", "info": "#2563eb",
}

TEMA_GELAP = {
    "bg": "#0e0a0a", "surface": "#181112", "surface-2": "#221719",
    "border": "#3a2427", "text": "#f8eeee", "muted": "#b09a9a",
    "primary": "#ef4444", "primary-dark": "#b91c1c",
    "primary-soft": "rgba(239,68,68,.14)", "primary-line": "rgba(239,68,68,.35)",
    "shadow": "rgba(0,0,0,.55)",
    "card-shadow": "none",
    "glow1": "rgba(239,68,68,.16)", "glow2": "rgba(185,28,28,.12)",
    "nav-bg": "rgba(14,10,10,.78)",
    "pos": "#4ade80", "neu": "#94a3b8", "neg": "#f87171",
    "warn": "#fbbf24", "info": "#60a5fa",
}

_CSS_PATH = Path(__file__).with_name("styles.css")


# ---------------------------------------------------------------- state
def init_state() -> None:
    st.session_state.setdefault("dark_mode", False)


def is_dark() -> bool:
    return st.session_state.get("dark_mode", False)


def toggle_dark() -> None:
    st.session_state.dark_mode = not is_dark()


def current_theme() -> dict:
    return TEMA_GELAP if is_dark() else TEMA_TERANG


def warna(sentimen) -> str:
    t = current_theme()
    peta = {"positif": t["pos"], "netral": t["neu"], "negatif": t["neg"]}
    return peta.get(str(sentimen).lower(), t["primary"])


# ---------------------------------------------------------------- CSS
@lru_cache(maxsize=1)
def _baca_css() -> str:
    return _CSS_PATH.read_text(encoding="utf-8")


def _css_dataframe(dark: bool) -> str:
    if dark:
        return "[data-testid='stDataFrame']{filter:invert(.92) hue-rotate(180deg);border-radius:12px;overflow:hidden;}"
    return "[data-testid='stDataFrame']{border:1px solid var(--border);border-radius:12px;overflow:hidden;}"


def inject_css() -> None:
    # color-scheme membuat scrollbar & kontrol bawaan browser ikut gelap/terang
    skema = "dark" if is_dark() else "light"
    variabel = ":root{" + ";".join(f"--{k}:{v}" for k, v in current_theme().items()) + f";color-scheme:{skema}" + "}"
    tulis_html("<style>" + variabel + _baca_css() + _css_dataframe(is_dark()) + "</style>")
