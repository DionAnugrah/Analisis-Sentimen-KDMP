"""Aplikasi web KDMP: klasifikasi sentimen + klastering komentar.
Jalankan:  streamlit run app.py
"""
import os
import re
from datetime import datetime
from html import escape

import numpy as np
import pandas as pd
import joblib
import streamlit as st
from sklearn.preprocessing import Normalizer

from preprocessing import clean_text

MODEL_SENTIMEN = "model_sentimen_kdmp.joblib"
MODEL_KLASTER = "model_klaster_kdmp.joblib"

# ---------------------------------------------------------------- state tema
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
DARK = st.session_state.dark_mode

# Parameter "lebar penuh" berbeda antar versi Streamlit
_VER = tuple(int(x) for x in re.findall(r"\d+", st.__version__)[:2])
STRETCH = {"width": "stretch"} if _VER >= (1, 50) else {"use_container_width": True}


# ---------------------------------------------------------------- logo & ikon
def buat_favicon():
    """Favicon: lingkaran merah-putih (bendera) dengan bingkai merah."""
    try:
        from PIL import Image, ImageDraw
        s = 256
        im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        box = [10, 10, s - 10, s - 10]
        d.ellipse(box, fill="#ffffff")
        d.pieslice(box, 180, 360, fill="#dc2626")
        d.ellipse(box, outline="#b91c1c", width=14)
        return im
    except Exception:
        return ":material/analytics:"


st.set_page_config(
    page_title="KDMP - Analisis Sentimen",
    page_icon=buat_favicon(),
    layout="wide",
    initial_sidebar_state="expanded",
)


def logo(size=48, uid="a"):
    """Logo KDMP: lingkaran merah-putih."""
    return (
        f'<svg class="logo" width="{size}" height="{size}" viewBox="0 0 48 48" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<defs><clipPath id="clip-{uid}"><circle cx="24" cy="24" r="15"/></clipPath></defs>'
        f'<circle cx="24" cy="24" r="23" fill="#ffffff"/>'
        f'<g clip-path="url(#clip-{uid})"><rect width="48" height="24" fill="#dc2626"/></g>'
        f'<circle cx="24" cy="24" r="15" fill="none" stroke="#b91c1c" stroke-width="2.5"/>'
        f'</svg>'
    )


# Kumpulan ikon (gaya Lucide, stroke)
_ICONS = {
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
    "message": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "key": '<circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6"/><path d="m15.5 7.5 3 3L22 7l-3-3"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/>',
    "table": '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/>',
    "trend": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "cpu": '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9"/><path d="M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2"/>',
    "layers": '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
    "ok": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "no": '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "plus": '<path d="M5 12h14"/><path d="M12 5v14"/>',
    "minus": '<path d="M5 12h14"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "spark": '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>',
}


def ic(name, size=20, color="currentColor", sw=2):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
        f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" '
        f'xmlns="http://www.w3.org/2000/svg">{_ICONS[name]}</svg>'
    )


# ---------------------------------------------------------------- tema warna
if DARK:
    THEME = {
        "bg": "#0e0a0a", "surface": "#181112", "surface-2": "#221719",
        "border": "#3a2427", "text": "#f8eeee", "muted": "#b09a9a",
        "primary": "#ef4444", "primary-dark": "#b91c1c",
        "primary-soft": "rgba(239,68,68,.14)", "primary-line": "rgba(239,68,68,.35)",
        "shadow": "rgba(0,0,0,.55)",
        "pos": "#4ade80", "neu": "#94a3b8", "neg": "#f87171",
    }
else:
    THEME = {
        "bg": "#fdf6f6", "surface": "#ffffff", "surface-2": "#fff1f1",
        "border": "#f3dede", "text": "#1f1717", "muted": "#6b5b5b",
        "primary": "#dc2626", "primary-dark": "#991b1b",
        "primary-soft": "rgba(220,38,38,.09)", "primary-line": "rgba(220,38,38,.28)",
        "shadow": "rgba(153,27,27,.18)",
        "pos": "#16a34a", "neu": "#64748b", "neg": "#dc2626",
    }

COLORS = {"positif": THEME["pos"], "netral": THEME["neu"], "negatif": THEME["neg"]}


def warna(sentimen):
    return COLORS.get(str(sentimen).lower(), THEME["primary"])


def sentiment_icon(sentiment, size=56):
    color = warna(sentiment)
    if sentiment == "positif":
        path = "M8 14C8 14 9.5 16 12 16C14.5 16 16 14 16 14M9 9H9.01M15 9H15.01"
    elif sentiment == "netral":
        path = "M9 9H9.01M15 9H15.01M9 14H15"
    else:
        path = "M9 9H9.01M15 9H15.01M8 16C8 16 9.5 14 12 14C14.5 14 16 16 16 16"
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
        f'<circle cx="12" cy="12" r="10" fill="{color}" opacity="0.15"/>'
        f'<path d="{path}" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="12" cy="12" r="10" stroke="{color}" stroke-width="2"/></svg>'
    )


def tulis_html(s):
    """Render HTML tanpa baris kosong/indentasi agar tidak dibaca sebagai blok kode markdown."""
    st.markdown(re.sub(r"\n\s*", "", s.strip()), unsafe_allow_html=True)


# ---------------------------------------------------------------- CSS
VARS = ":root{" + ";".join(f"--{k}:{v}" for k, v in THEME.items()) + "}"

if DARK:
    DF_CSS = "[data-testid='stDataFrame']{filter:invert(.92) hue-rotate(180deg);border-radius:12px;overflow:hidden;}"
else:
    DF_CSS = "[data-testid='stDataFrame']{border:1px solid var(--border);border-radius:12px;overflow:hidden;}"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

.stApp, button, input, textarea { font-family: 'Plus Jakarta Sans', 'Source Sans Pro', system-ui, sans-serif; }
.stApp { background: var(--bg); color: var(--text); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] button, [data-testid="stSidebarCollapseButton"] button,
[data-testid="stExpandSidebarButton"] { color: var(--text) !important; }
.block-container { padding-top: 2.2rem; max-width: 1200px; }
hr { border-color: var(--border) !important; }

[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }
.stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
[data-testid="stWidgetLabel"] p { color: var(--text); }

/* ---------- Hero ---------- */
.hero { position: relative; overflow: hidden; display: flex; align-items: center; flex-wrap: wrap;
  gap: 1.25rem; padding: 1.8rem 2.2rem; border-radius: 24px; margin: .25rem 0 1.6rem;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 45%, #991b1b 100%);
  box-shadow: 0 22px 44px -18px rgba(153,27,27,.65); }
.hero::before { content: ""; position: absolute; right: -70px; top: -80px; width: 260px; height: 260px;
  border-radius: 50%; background: rgba(255,255,255,.13); }
.hero::after { content: ""; position: absolute; right: 90px; bottom: -110px; width: 220px; height: 220px;
  border-radius: 50%; background: rgba(255,255,255,.08); }
.hero .logo { flex: 0 0 auto; filter: drop-shadow(0 8px 14px rgba(0,0,0,.28)); position: relative; z-index: 1; }
.hero-body { position: relative; z-index: 1; }
.hero-title { color: #fff !important; font-size: 2.2rem; font-weight: 800; line-height: 1.15; letter-spacing: -.02em; }
.hero-sub { color: rgba(255,255,255,.92) !important; font-size: 1rem; margin-top: .35rem; }
.hero-chips { display: flex; gap: .5rem; flex-wrap: wrap; margin-top: .9rem; }
.hero-chip { display: inline-flex; align-items: center; gap: .4rem; padding: .3rem .8rem; border-radius: 999px;
  background: rgba(255,255,255,.18); color: #fff !important; font-size: .78rem; font-weight: 600;
  border: 1px solid rgba(255,255,255,.28); backdrop-filter: blur(4px); }

/* ---------- Judul seksi ---------- */
.sec { display: flex; align-items: center; gap: .75rem; margin: 1.1rem 0 .3rem; }
.sec-ico { width: 40px; height: 40px; border-radius: 12px; background: var(--primary-soft);
  color: var(--primary); display: grid; place-items: center; flex: 0 0 auto; }
.sec-title { font-size: 1.3rem; font-weight: 800; color: var(--text); letter-spacing: -.01em; }
.sec-sub { color: var(--muted); margin: 0 0 1rem 0; font-size: .95rem; }

/* ---------- Kartu ---------- */
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 20px; padding: 1.4rem 1.5rem;
  box-shadow: 0 14px 30px -20px var(--shadow); margin-bottom: 1rem; }
.card-title { display: flex; align-items: center; gap: .55rem; font-weight: 700; font-size: .95rem;
  color: var(--text); margin-bottom: .6rem; }
.card-title .i { color: var(--primary); display: inline-flex; }

.sent-card { text-align: center; border-radius: 22px; padding: 1.8rem 1.5rem; margin-bottom: 1rem;
  border: 2px solid; box-shadow: 0 16px 34px -22px var(--shadow); transition: transform .25s ease; }
.sent-card:hover { transform: translateY(-3px); }
.sent-label { font-size: .78rem; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; margin-top: .6rem; }
.sent-value { font-size: 2.4rem; font-weight: 800; letter-spacing: -.02em; line-height: 1.1; }

.big-value { font-size: 2rem; font-weight: 800; color: var(--text); letter-spacing: -.02em; }

/* ---------- Stat ---------- */
.stat { display: flex; align-items: center; gap: .9rem; background: var(--surface); border: 1px solid var(--border);
  border-radius: 18px; padding: 1.05rem 1.2rem; box-shadow: 0 14px 30px -22px var(--shadow); }
.stat-ico { width: 46px; height: 46px; border-radius: 14px; display: grid; place-items: center; flex: 0 0 auto; }
.stat-lbl { font-size: .72rem; text-transform: uppercase; letter-spacing: .08em; color: var(--muted); font-weight: 700; }
.stat-val { font-size: 1.7rem; font-weight: 800; line-height: 1.1; color: var(--text); }

/* ---------- Bar ---------- */
.bar-row { margin: .8rem 0; }
.bar-head { display: flex; justify-content: space-between; font-size: .85rem; font-weight: 600;
  color: var(--text); margin-bottom: .35rem; }
.bar-head .r { color: var(--muted); font-weight: 600; }
.bar-track { height: 10px; border-radius: 999px; background: var(--surface-2); overflow: hidden;
  border: 1px solid var(--border); }
.bar-fill { height: 100%; border-radius: 999px; }

/* ---------- Kata kunci ---------- */
.kw { display: inline-block; padding: .35rem .85rem; margin: .22rem .3rem .22rem 0; border-radius: 999px;
  background: var(--primary-soft); color: var(--primary); border: 1px solid var(--primary-line);
  font-weight: 600; font-size: .85rem; }

.cl-head { display: flex; align-items: center; gap: .75rem; margin-bottom: .7rem; }
.cl-n { width: 38px; height: 38px; border-radius: 12px; display: grid; place-items: center; color: #fff;
  font-weight: 800; background: linear-gradient(135deg, var(--primary), var(--primary-dark)); }
.cl-title { font-weight: 800; font-size: 1.1rem; color: var(--text); }

/* ---------- Sidebar ---------- */
.brand { display: flex; align-items: center; gap: .75rem; padding: .2rem 0 1rem; }
.brand-name { font-weight: 800; font-size: 1.15rem; color: var(--text); line-height: 1.1; }
.brand-sub { font-size: .72rem; color: var(--muted); }
.side-title { display: flex; align-items: center; gap: .5rem; font-weight: 800; font-size: .8rem;
  text-transform: uppercase; letter-spacing: .1em; color: var(--muted); margin: .4rem 0 .8rem; }
.side-title .i { color: var(--primary); display: inline-flex; }

.status { display: flex; align-items: center; gap: .8rem; padding: .85rem 1rem; background: var(--surface-2);
  border: 1px solid var(--border); border-radius: 16px; margin-bottom: .7rem; }
.status-badge { width: 38px; height: 38px; border-radius: 12px; display: grid; place-items: center; flex: 0 0 auto; }
.status.on .status-badge { background: rgba(22,163,74,.15); color: var(--pos); }
.status.off .status-badge { background: rgba(220,38,38,.15); color: var(--neg); }
.status-t { font-weight: 700; font-size: .9rem; color: var(--text); }
.status-s { font-size: .72rem; color: var(--muted); word-break: break-all; }
.status-pill { margin-left: auto; font-size: .68rem; font-weight: 800; padding: .2rem .6rem; border-radius: 999px; }
.status.on .status-pill { background: rgba(22,163,74,.15); color: var(--pos); }
.status.off .status-pill { background: rgba(220,38,38,.15); color: var(--neg); }

.steps { display: flex; flex-direction: column; gap: 1rem; padding: 1.1rem 1.1rem; border-radius: 18px;
  background: linear-gradient(160deg, #ef4444 0%, #b91c1c 100%); box-shadow: 0 16px 30px -18px rgba(153,27,27,.7); }
.step { display: flex; gap: .8rem; align-items: flex-start; }
.step-n { flex: 0 0 auto; width: 28px; height: 28px; border-radius: 50%; background: #fff; color: #b91c1c;
  font-weight: 800; font-size: .8rem; display: grid; place-items: center; }
.step-t { display: block; font-size: .9rem; font-weight: 700; color: #fff; }
.step-d { display: block; font-size: .78rem; color: rgba(255,255,255,.85); }

.footer { text-align: center; padding: 1.6rem 0 .6rem; color: var(--muted); font-size: .85rem; }
.footer .logo { margin-bottom: .4rem; }
.footer small { display: block; margin-top: .25rem; font-size: .75rem; opacity: .85; }

/* ---------- Widget Streamlit ---------- */
.stTextArea textarea, .stTextInput input, [data-testid="stNumberInput"] input {
  background: var(--surface) !important; color: var(--text) !important; }
[data-baseweb="textarea"], [data-baseweb="input"], [data-baseweb="base-input"] {
  background: var(--surface) !important; border-color: var(--border) !important; border-radius: 14px !important; }
[data-baseweb="textarea"]:focus-within, [data-baseweb="input"]:focus-within {
  border-color: var(--primary) !important; box-shadow: 0 0 0 3px var(--primary-soft) !important; }
[data-baseweb="select"] > div { background: var(--surface) !important; border-color: var(--border) !important;
  border-radius: 14px !important; }
[data-baseweb="select"] * { color: var(--text); }
[data-baseweb="popover"] ul, [data-baseweb="popover"] [data-baseweb="menu"] { background: var(--surface) !important; }
[data-baseweb="popover"] li { background: var(--surface) !important; color: var(--text) !important; }
[data-baseweb="popover"] li:hover, [data-baseweb="popover"] li[aria-selected="true"] {
  background: var(--primary-soft) !important; }
[data-baseweb="tag"] { background: var(--primary) !important; border-radius: 999px !important; }
[data-baseweb="tag"] * { color: #fff !important; }
[data-testid="stNumberInput"] button { background: var(--surface-2) !important; color: var(--text) !important; }

.stButton > button, .stDownloadButton > button,
button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {
  border-radius: 14px; font-weight: 700; padding: .65rem 1.2rem;
  background: var(--surface) !important; color: var(--text) !important;
  border: 1px solid var(--border) !important; transition: all .25s ease; }
.stButton > button:hover, .stDownloadButton > button:hover,
button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover {
  background: var(--primary-soft) !important; border-color: var(--primary) !important;
  color: var(--primary) !important; transform: translateY(-2px); }
.stButton button p, .stDownloadButton button p, .stButton button span, .stDownloadButton button span {
  color: inherit !important; }
button[kind="primary"], button[data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
  color: #fff !important; border: none !important; box-shadow: 0 12px 24px -12px var(--shadow); }
.stButton > button[kind="primary"]:hover, button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
  color: #fff !important; filter: brightness(1.08); transform: translateY(-2px); }

[data-baseweb="tab-list"] { gap: .35rem; background: var(--surface); padding: .35rem; border-radius: 16px;
  border: 1px solid var(--border); }
button[data-baseweb="tab"] { border-radius: 12px; padding: .6rem 1.2rem; height: auto; background: transparent; }
button[data-baseweb="tab"] p { color: var(--muted) !important; font-weight: 700; }
button[data-baseweb="tab"][aria-selected="true"] {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark)); }
button[data-baseweb="tab"][aria-selected="true"] p { color: #fff !important; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }

[data-testid="stExpander"] { background: var(--surface); border: 1px solid var(--border) !important;
  border-radius: 16px; overflow: hidden; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * { color: var(--text) !important; }

[data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--border);
  border-left: 4px solid var(--primary); border-radius: 16px; padding: .9rem 1.2rem; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * { color: var(--text) !important; font-weight: 800; }
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * { color: var(--muted) !important; }

[data-testid="stFileUploaderDropzone"] { background: var(--surface); border: 2px dashed var(--primary-line);
  border-radius: 18px; }
[data-testid="stFileUploaderDropzone"] * { color: var(--muted); }
[data-testid="stFileUploaderDropzone"] button { background: var(--surface-2) !important;
  border: 1px solid var(--border) !important; color: var(--text) !important; border-radius: 12px; }
[data-testid="stFileUploaderDropzone"] button * { color: var(--text) !important; }

[data-testid="stAlert"] { background: var(--surface) !important; border: 1px solid var(--border);
  border-left: 4px solid var(--primary); border-radius: 16px; }
[data-testid="stAlert"] * { color: var(--text) !important; }

[data-testid="stCode"], [data-testid="stCode"] pre { background: var(--surface-2) !important;
  border-radius: 14px; }
[data-testid="stCode"] code, [data-testid="stCode"] span { color: var(--text) !important; }

[data-testid="stProgress"] p { color: var(--text) !important; }
"""

tulis_html("<style>" + VARS + CSS + DF_CSS + "</style>")


# ---------------------------------------------------------------- komponen HTML
def section(icon, title, sub=None):
    tulis_html(
        f'<div class="sec"><div class="sec-ico">{ic(icon, 22)}</div><div class="sec-title">{title}</div></div>'
    )
    if sub:
        tulis_html(f'<div class="sec-sub">{sub}</div>')


def stat_card(icon, label, value, fg, bg):
    return (
        f'<div class="stat"><div class="stat-ico" style="background:{bg};color:{fg};">{ic(icon, 22)}</div>'
        f'<div><div class="stat-lbl">{label}</div><div class="stat-val">{value}</div></div></div>'
    )


def bar_card(icon, title, items):
    """items: list of (label, jumlah, warna_css)."""
    total = sum(c for _, c, _ in items) or 1
    rows = "".join(
        f'<div class="bar-row"><div class="bar-head"><span>{escape(str(l))}</span>'
        f'<span class="r">{c:,} &middot; {c / total * 100:.1f}%</span></div>'
        f'<div class="bar-track"><div class="bar-fill" style="width:{c / total * 100:.1f}%;background:{col};"></div></div></div>'
        for l, c, col in items
    )
    return (
        f'<div class="card"><div class="card-title"><span class="i">{ic(icon, 20)}</span>{title}</div>{rows}</div>'
    )


def keyword_tags(keywords):
    return " ".join(f"<span class='kw'>{escape(str(k))}</span>" for k in keywords)


def status_card(judul, berkas, aktif):
    kelas = "on" if aktif else "off"
    ikon = ic("ok" if aktif else "no", 20)
    pill = "AKTIF" if aktif else "TIDAK AKTIF"
    tulis_html(
        f'<div class="status {kelas}"><div class="status-badge">{ikon}</div>'
        f'<div><div class="status-t">{judul}</div><div class="status-s">{berkas}</div></div>'
        f'<span class="status-pill">{pill}</span></div>'
    )


# ---------------------------------------------------------------- memuat model
@st.cache_resource(show_spinner="Memuat model...")
def muat_model(path):
    return joblib.load(path) if os.path.exists(path) else None


model_sent = muat_model(MODEL_SENTIMEN)
model_klas = muat_model(MODEL_KLASTER)


# ---------------------------------------------------------------- fungsi inti
def skor_sentimen(model, teks_bersih):
    """Kembalikan matriks 'keyakinan' per kelas (probabilitas / softmax skor SVM)."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(teks_bersih)
    s = model.decision_function(teks_bersih)
    e = np.exp(s - s.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


def prediksi_sentimen(komentar):
    bersih = [clean_text(k) for k in komentar]
    kosong = np.array([len(b.split()) == 0 for b in bersih])
    pred = model_sent.predict(bersih)
    prob = skor_sentimen(model_sent, bersih)
    kelas = list(model_sent.classes_)
    return pred, prob, kelas, bersih, kosong


def prediksi_klaster(bersih):
    X = model_klas["tfidf"].transform(bersih)
    ada = X.getnnz(axis=1) > 0
    Z = Normalizer().fit_transform(model_klas["svd"].transform(X))
    lab = model_klas["kmeans"].predict(Z)
    return lab, ada


@st.cache_data(show_spinner=False)
def kata_kunci_klaster(_m, n=8):
    """Kata kunci tiap klaster dari pusat klaster (diproyeksikan kembali ke ruang kata)."""
    pusat = _m["kmeans"].cluster_centers_ @ _m["svd"].components_
    terms = np.array(_m["tfidf"].get_feature_names_out())
    return {i: terms[np.argsort(pusat[i])[::-1][:n]].tolist() for i in range(len(pusat))}


# ---------------------------------------------------------------- tampilan
# Tombol ganti tema
_, col_toggle = st.columns([4, 1])
with col_toggle:
    if st.button(
        "Mode Terang" if DARK else "Mode Gelap",
        key="theme_toggle",
        icon=":material/light_mode:" if DARK else ":material/dark_mode:",
        help="Ganti mode terang / gelap",
        **STRETCH,
    ):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# Header
tulis_html(
    f"""
    <div class="hero">
        {logo(72, "hero")}
        <div class="hero-body">
            <div class="hero-title">Analisis Sentimen KDMP</div>
            <div class="hero-sub">Sistem Analisis Sentimen dan Klastering Topik - Koperasi Desa Merah Putih</div>
            <div class="hero-chips">
                <span class="hero-chip">{ic("message", 14)} Klasifikasi Sentimen</span>
                <span class="hero-chip">{ic("target", 14)} Klastering Topik</span>
                <span class="hero-chip">{ic("layers", 14)} Analisis Batch</span>
            </div>
        </div>
    </div>
    """
)

# Sidebar
with st.sidebar:
    tulis_html(
        f'<div class="brand">{logo(42, "side")}<div><div class="brand-name">KDMP</div>'
        f'<div class="brand-sub">Merah Putih Analytics</div></div></div>'
    )

    tulis_html(f'<div class="side-title"><span class="i">{ic("cpu", 16)}</span>Status Sistem</div>')
    status_card("Model Sentimen", MODEL_SENTIMEN, bool(model_sent))
    status_card("Model Klaster", MODEL_KLASTER, bool(model_klas))

    st.markdown("---")

    tulis_html(f'<div class="side-title"><span class="i">{ic("layers", 16)}</span>Alur Kerja</div>')
    tulis_html(
        """
        <div class="steps">
            <div class="step"><div class="step-n">1</div><div>
                <span class="step-t">Preprocessing</span>
                <span class="step-d">Pembersihan teks, normalisasi</span></div></div>
            <div class="step"><div class="step-n">2</div><div>
                <span class="step-t">Feature Extraction</span>
                <span class="step-d">TF-IDF vectorization</span></div></div>
            <div class="step"><div class="step-n">3</div><div>
                <span class="step-t">Prediksi</span>
                <span class="step-d">Klasifikasi sentimen &amp; clustering</span></div></div>
        </div>
        """
    )

if model_sent is None and model_klas is None:
    st.error(
        "Tidak ada file model. Letakkan file `.joblib` dari notebook di folder yang sama dengan `app.py`.",
        icon=":material/error:",
    )
    st.stop()

kunci = kata_kunci_klaster(model_klas) if model_klas is not None else {}

# Tabs
tab1, tab2, tab3 = st.tabs([
    ":material/chat: Analisis Tunggal",
    ":material/table_chart: Analisis Batch",
    ":material/hub: Info Klaster",
])

# ---------------------------------------------------------------- TAB 1
with tab1:
    section("message", "Analisis Komentar Tunggal",
            "Masukkan satu komentar untuk menganalisis sentimen dan topiknya.")

    teks = st.text_area(
        "Komentar",
        height=130,
        placeholder="Tulis atau tempel komentar di sini untuk dianalisis...",
    )

    if st.button("Analisis Sekarang", type="primary", icon=":material/bolt:", **STRETCH):
        if not teks.strip():
            st.warning("Silakan masukkan komentar terlebih dahulu.", icon=":material/warning:")
        else:
            with st.spinner("Sedang menganalisis..."):
                pred, prob, kelas, bersih, kosong = prediksi_sentimen([teks])

            st.markdown("---")
            section("trend", "Hasil Analisis")

            c1, c2 = st.columns([1, 1])

            if model_sent is not None:
                with c1:
                    lab = pred[0]
                    if kosong[0]:
                        st.warning(
                            "Teks menjadi kosong setelah preprocessing. Hasil mungkin kurang akurat.",
                            icon=":material/warning:",
                        )

                    wl = warna(lab)
                    tulis_html(
                        f"""
                        <div class="sent-card" style="border-color:{wl};background:linear-gradient(180deg,{wl}22,var(--surface));">
                            <div style="display:flex;justify-content:center;">{sentiment_icon(lab)}</div>
                            <div class="sent-label" style="color:{wl};">Sentimen Terdeteksi</div>
                            <div class="sent-value" style="color:{wl};">{escape(str(lab)).upper()}</div>
                        </div>
                        """
                    )

                    items = [(str(k).title(), float(prob[0][i]), warna(k)) for i, k in enumerate(kelas)]
                    rows = "".join(
                        f'<div class="bar-row"><div class="bar-head"><span>{l}</span>'
                        f'<span class="r">{p * 100:.1f}%</span></div>'
                        f'<div class="bar-track"><div class="bar-fill" style="width:{p * 100:.1f}%;background:{col};"></div></div></div>'
                        for l, p, col in items
                    )
                    tulis_html(
                        f'<div class="card"><div class="card-title"><span class="i">{ic("chart", 20)}</span>'
                        f'Tingkat Keyakinan</div>{rows}</div>'
                    )

            if model_klas is not None:
                with c2:
                    kl, ada = prediksi_klaster(bersih)
                    nilai = f"Klaster {int(kl[0])}" if ada[0] else "N/A"
                    tulis_html(
                        f'<div class="card"><div class="card-title"><span class="i">{ic("target", 20)}</span>'
                        f'Klaster Topik</div><div class="big-value">{nilai}</div></div>'
                    )

                    if ada[0]:
                        tulis_html(
                            f'<div class="card"><div class="card-title"><span class="i">{ic("key", 20)}</span>'
                            f'Kata Kunci Klaster</div><div>{keyword_tags(kunci[int(kl[0])])}</div></div>'
                        )
                    else:
                        st.info("Kata-kata tidak ditemukan dalam kosakata model.", icon=":material/info:")

            with st.expander("Lihat Teks Hasil Preprocessing", icon=":material/manage_search:"):
                st.code(bersih[0] or "(kosong)", language="text")

# ---------------------------------------------------------------- TAB 2
with tab2:
    section("chart", "Analisis Batch (File CSV)",
            "Unggah file CSV untuk menganalisis banyak komentar sekaligus.")

    col_upload1, col_upload2 = st.columns([2, 1])

    with col_upload1:
        berkas = st.file_uploader(
            "Pilih file CSV",
            type=["csv"],
            help="File CSV harus memiliki kolom yang berisi komentar",
        )

    if berkas is not None:
        try:
            data = pd.read_csv(berkas, dtype=str)

            with col_upload2:
                st.metric("Total Baris", f"{len(data):,}")
                st.metric("Total Kolom", len(data.columns))

        except Exception as e:
            st.error(f"Gagal membaca file CSV: {e}", icon=":material/error:")
            st.stop()

        st.markdown("---")

        col_config1, col_config2 = st.columns(2)

        with col_config1:
            default = list(data.columns).index("comment") if "comment" in data.columns else 0
            kolom = st.selectbox("Kolom komentar", data.columns, index=default)

        with col_config2:
            batas = st.number_input(
                "Batas baris diproses",
                100,
                max(len(data), 100),
                max(100, min(len(data), 20000)),
                step=100,
            )

        if st.button("Proses Semua Data", type="primary", icon=":material/rocket_launch:", **STRETCH):
            d = data.head(int(batas)).copy()
            d[kolom] = d[kolom].fillna("").astype(str)

            progress_bar = st.progress(0, text="Memulai...")

            hasil = d.copy()
            bersih_semua = [clean_text(k) for k in d[kolom]]
            progress_bar.progress(33, text="Preprocessing selesai...")

            if model_sent is not None:
                pred = model_sent.predict(bersih_semua)
                hasil["sentimen_prediksi"] = pred
                progress_bar.progress(66, text="Analisis sentimen selesai...")

            if model_klas is not None:
                kl, ada = prediksi_klaster(bersih_semua)
                hasil["klaster"] = np.where(ada, kl.astype(str), "tidak ada")
                progress_bar.progress(90, text="Clustering selesai...")

            hasil["teks_bersih"] = bersih_semua
            progress_bar.progress(100, text="Selesai!")

            st.session_state["hasil"] = hasil
            st.success("Proses berhasil!", icon=":material/check_circle:")

    if "hasil" in st.session_state:
        hasil = st.session_state["hasil"]

        st.markdown("---")
        section("trend", "Ringkasan Hasil")

        # Kartu ringkasan
        metric_cols = st.columns(4)
        with metric_cols[0]:
            tulis_html(stat_card("users", "Total Diproses", f"{len(hasil):,}",
                                 "var(--primary)", "var(--primary-soft)"))

        if "sentimen_prediksi" in hasil:
            sentimen_counts = hasil["sentimen_prediksi"].value_counts()
            for col, nama, ikon in zip(metric_cols[1:], ["positif", "netral", "negatif"], ["plus", "minus", "x"]):
                with col:
                    c = warna(nama)
                    tulis_html(stat_card(ikon, nama.title(), f"{int(sentimen_counts.get(nama, 0)):,}", c, f"{c}22"))

        st.markdown("<br>", unsafe_allow_html=True)

        # Grafik distribusi
        chart_cols = st.columns(2)
        if "sentimen_prediksi" in hasil:
            with chart_cols[0]:
                urut = [k for k in ["positif", "netral", "negatif"] if k in sentimen_counts.index]
                urut += [k for k in sentimen_counts.index if k not in urut]
                tulis_html(bar_card("chart", "Distribusi Sentimen",
                                    [(k.title(), int(sentimen_counts[k]), warna(k)) for k in urut]))

        if "klaster" in hasil:
            with chart_cols[1]:
                kc = hasil["klaster"].value_counts()
                urut_k = sorted(kc.index, key=lambda k: (not str(k).isdigit(), int(k) if str(k).isdigit() else 0, str(k)))
                tulis_html(bar_card(
                    "target", "Distribusi Klaster",
                    [(f"Klaster {k}" if str(k).isdigit() else str(k).title(), int(kc[k]),
                      "linear-gradient(90deg,var(--primary),var(--primary-dark))") for k in urut_k],
                ))

        st.markdown("---")
        section("table", "Data Hasil")

        # Filter
        f = st.multiselect(
            "Filter berdasarkan sentimen",
            sorted(hasil["sentimen_prediksi"].unique()) if "sentimen_prediksi" in hasil else [],
            help="Pilih sentimen untuk memfilter data",
        )

        tampil = hasil[hasil["sentimen_prediksi"].isin(f)] if f else hasil

        st.dataframe(tampil, height=400, **STRETCH)

        # Unduh
        csv = hasil.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Unduh Hasil Lengkap (CSV)",
            csv,
            "hasil_analisis_kdmp.csv",
            "text/csv",
            icon=":material/download:",
            **STRETCH,
        )

# ---------------------------------------------------------------- TAB 3
with tab3:
    if model_klas is None:
        st.info("Model klaster tidak tersedia.", icon=":material/info:")
    else:
        section(
            "target",
            "Informasi Klaster Topik",
            f"Model membagi komentar ke dalam <b>{len(kunci)} klaster</b> berdasarkan topik yang dibahas. "
            "Kata kunci dihitung dari pusat setiap klaster menggunakan analisis TF-IDF.",
        )

        for i, keywords in kunci.items():
            tulis_html(
                f"""
                <div class="card">
                    <div class="cl-head"><div class="cl-n">{i}</div><div class="cl-title">Klaster {i}</div></div>
                    <div>{keyword_tags(keywords)}</div>
                </div>
                """
            )

        with st.expander("Lihat dalam bentuk tabel", icon=":material/table_rows:"):
            st.dataframe(
                pd.DataFrame({
                    "Klaster": list(kunci.keys()),
                    "Kata Kunci": [", ".join(v) for v in kunci.values()],
                }),
                hide_index=True,
                **STRETCH,
            )

# ---------------------------------------------------------------- footer
st.markdown("---")
tulis_html(
    f"""
    <div class="footer">
        {logo(34, "foot")}
        <div>&copy; {datetime.now().year} Koperasi Desa Merah Putih - Sistem Analisis Sentimen &amp; Klastering</div>
        <small>Powered by Machine Learning &amp; Natural Language Processing</small>
    </div>
    """
)