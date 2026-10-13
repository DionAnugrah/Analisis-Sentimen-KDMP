"""Komponen HTML.

Fungsi *builder* (``card``, ``stat_card``, ``bar_card``, ``notif_html``, ``progress_html``,
``tabel_silang``, ``feat_card``, ``tech_card``, dll.) mengembalikan string HTML;
fungsi *renderer* (``section``, ``notif``, ``kartu_sentimen``) langsung menampilkannya lewat Streamlit.
"""
from html import escape
from typing import Iterable, List, Tuple

from config import URUTAN_SENTIMEN
from ui.icons import ic, sentiment_icon
from ui.theme import warna
from ui.utils import tulis_html


# ---------------------------------------------------------------- builder
def card(icon: str, title: str, body: str) -> str:
    return (
        f'<div class="card"><div class="card-title"><span class="i">{ic(icon, 20)}</span>{title}</div>'
        f'{body}</div>'
    )


def stat_card(icon, label, value, fg, bg) -> str:
    return (
        f'<div class="stat"><div class="stat-ico" style="background:{bg};color:{fg};">{ic(icon, 22)}</div>'
        f'<div><div class="stat-lbl">{label}</div><div class="stat-val">{value}</div></div></div>'
    )


def _bar_row(label: str, kanan: str, persen: float, warna_css: str) -> str:
    return (
        f'<div class="bar-row"><div class="bar-head"><span>{escape(str(label))}</span>'
        f'<span class="r">{kanan}</span></div>'
        f'<div class="bar-track"><div class="bar-fill" style="width:{persen:.1f}%;background:{warna_css};"></div></div></div>'
    )


def bar_card(icon: str, title: str, items: Iterable[Tuple[str, int, str]]) -> str:
    """items: (label, jumlah, warna_css)."""
    items = list(items)
    total = sum(c for _, c, _ in items) or 1
    rows = "".join(
        _bar_row(label, f"{c:,} &middot; {c / total * 100:.1f}%", c / total * 100, col)
        for label, c, col in items
    )
    return card(icon, title, rows)


def urutkan_sentimen(label_ada) -> List[str]:
    """Positif, netral, negatif lebih dulu; label lain menyusul."""
    label_ada = list(label_ada)
    urut = [k for k in URUTAN_SENTIMEN if k in label_ada]
    return urut + [k for k in label_ada if k not in urut]


def bar_distribusi_sentimen(judul: str, counts) -> str:
    """``counts``: pandas Series hasil value_counts() dari kolom sentimen."""
    urut = urutkan_sentimen(counts.index)
    return bar_card("chart", judul, [(k.title(), int(counts[k]), warna(k)) for k in urut])


def tabel_silang(judul: str, ct, nama_baris: str, nama_kolom: str) -> str:
    """Matriks kesesuaian dua model. ``ct``: DataFrame (baris & kolom sudah berurutan sama)."""
    kepala = "".join(f"<th>{escape(str(c).title())}</th>" for c in ct.columns)
    baris = ""
    for r in ct.index:
        sel = ""
        for c in ct.columns:
            n = int(ct.loc[r, c])
            kelas = "zero" if n == 0 else ("ok" if r == c else "diff")
            sel += f'<td class="{kelas}">{n:,}</td>'
        baris += f"<tr><th>{escape(str(r).title())}</th>{sel}</tr>"
    sudut = f"{escape(nama_baris)} &darr; &nbsp;/&nbsp; {escape(nama_kolom)} &rarr;"
    tabel = (
        f'<div class="xt-wrap"><table class="xt"><thead><tr><th>{sudut}</th>{kepala}</tr></thead>'
        f"<tbody>{baris}</tbody></table></div>"
    )
    return card("table", judul, tabel)


_IKON_NOTIF = {"ok": "ok", "warn": "warn", "info": "info", "err": "no"}


def notif_html(jenis: str, teks: str) -> str:
    """Notifikasi bertema. jenis: ok | warn | info | err. ``teks`` boleh berisi HTML sederhana."""
    return (
        f'<div class="alert {jenis}"><span class="alert-ico">{ic(_IKON_NOTIF[jenis], 20)}</span>'
        f'<div>{teks}</div></div>'
    )


def progress_html(persen: int, teks: str) -> str:
    persen = max(0, min(100, int(persen)))
    return (
        f'<div class="prog"><div class="prog-head"><span>{escape(teks)}</span><span>{persen}%</span></div>'
        f'<div class="prog-track"><div class="prog-fill" style="width:{persen}%;"></div></div></div>'
    )


# ---------------------------------------------------------------- grafik perbandingan model
def grafik_grup(icon: str, judul: str, kategori, seri, selisih: bool = True) -> str:
    """Batang horizontal berkelompok pada skala 0-100%, mengikuti tema terang/gelap lewat variabel CSS.

    ``seri``: [(nama, warna_css, [nilai 0..1 untuk tiap kategori])]. Bila ada tepat dua seri dan ``selisih``
    True, selisih (poin persentase) ditulis di tiap baris.
    """
    legenda = "".join(
        f'<span class="lg"><i style="background:{warna_css};"></i>{escape(nama)}</span>' for nama, warna_css, _ in seri
    )
    baris = ""
    for i, kat in enumerate(kategori):
        batang = "".join(
            f'<div class="gb-bar" title="{escape(nama)}: {nilai[i] * 100:.2f}%"><div class="gb-track">'
            f'<div class="gb-fill" style="width:{nilai[i] * 100:.2f}%;background:{warna_css};"></div></div>'
            f'<span class="gb-v">{nilai[i] * 100:.2f}%</span></div>'
            for nama, warna_css, nilai in seri
        )
        d = ""
        if selisih and len(seri) == 2:
            (na, _, va), (nb, _, vb) = seri
            delta = (vb[i] - va[i]) * 100
            d = f'<span class="gb-d">{escape(nb if delta >= 0 else na)} +{abs(delta):.2f} poin</span>'
        baris += f'<div class="gb-row"><div class="gb-h"><span class="gb-l">{escape(kat)}</span>{d}</div>{batang}</div>'
    return card(icon, judul, f'<div class="legend">{legenda}</div><div class="gb">{baris}</div>')


def tabel_kelas(judul: str, per_kelas) -> str:
    """per_kelas: {kelas: (precision, recall, f1, support)}."""
    baris = "".join(
        f"<tr><td>{escape(k.title())}</td><td>{p:.4f}</td><td>{r:.4f}</td><td>{f:.4f}</td><td>{n:,}</td></tr>"
        for k, (p, r, f, n) in per_kelas.items()
    )
    kepala = "<tr><th>Kelas</th><th>Precision</th><th>Recall</th><th>F1</th><th>Support</th></tr>"
    return card("table", escape(judul),
                f'<div class="xt-wrap"><table class="dt"><thead>{kepala}</thead><tbody>{baris}</tbody></table></div>')


def matriks_proporsi(judul: str, cm, kelas) -> str:
    """Confusion matrix sebagai proporsi per kelas aktual (baris = aktual, kolom = prediksi)."""
    kepala = "".join(f"<th>{escape(c.title())}</th>" for c in kelas)
    baris = ""
    for i, nama_baris in enumerate(kelas):
        total = sum(cm[i]) or 1
        sel = ""
        for j in range(len(kelas)):
            p = cm[i][j] / total
            jenis = "ok" if i == j else ("diff" if p >= 0.05 else "zero")
            sel += f'<td class="{jenis}" title="{cm[i][j]:,} komentar">{p * 100:.1f}%</td>'
        baris += f"<tr><th>{escape(nama_baris.title())}</th>{sel}</tr>"
    tabel = (f'<div class="xt-wrap"><table class="xt"><thead><tr><th>Aktual &darr; / Prediksi &rarr;</th>{kepala}</tr></thead>'
             f"<tbody>{baris}</tbody></table></div>")
    return card("table", escape(judul), tabel)


# ---------------------------------------------------------------- builder konten halaman
def grid(items: Iterable[str], kolom: int = 0) -> str:
    """Susun kartu dalam grid. ``kolom`` 3/4 mengunci jumlah kolom di layar lebar; 0 = menyesuaikan lebar otomatis.
    Di layar sempit jumlah kolom otomatis berkurang."""
    kelas = f"grid g{kolom}" if kolom else "grid"
    return f'<div class="{kelas}">' + "".join(items) + "</div>"


def feat_card(icon: str, title: str, text: str) -> str:
    return (
        f'<div class="card feat"><div class="sq">{ic(icon, 22)}</div>'
        f'<div class="feat-title">{title}</div><div class="feat-text">{text}</div></div>'
    )


def tech_card(icon: str, title: str, text: str, tag: str) -> str:
    return (
        f'<div class="card feat"><div class="sq">{ic(icon, 22)}</div>'
        f'<div class="feat-title">{title}</div><div class="feat-text">{text}</div>'
        f'<span class="tag">{tag}</span></div>'
    )


def daftar_html(items: Iterable[str]) -> str:
    return '<ul class="plain">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


# ---------------------------------------------------------------- renderer
def section(icon, title, sub=None) -> None:
    tulis_html(
        f'<div class="sec"><div class="sec-ico">{ic(icon, 22)}</div><div class="sec-title">{title}</div></div>'
    )
    if sub:
        tulis_html(f'<div class="sec-sub">{sub}</div>')


def bagian_judul(kunci: str, eyebrow: str, judul: str, sub: str = "") -> None:
    """Judul bagian utama halaman. ``kunci`` menjadi id jangkar yang dituju tombol navigasi (#kunci)."""
    sub_html = f'<div class="part-sub">{sub}</div>' if sub else ""
    tulis_html(
        f'<div id="{kunci}" class="anchor"></div>'
        f'<div class="part"><div class="part-eyebrow">{eyebrow}</div>'
        f'<div class="part-title">{judul}</div>{sub_html}</div>'
    )


def notif(jenis: str, teks: str) -> None:
    tulis_html(notif_html(jenis, teks))


def kartu_sentimen(h) -> None:
    """Kartu hasil satu model (``h``: HasilSentimen) + bar tingkat keyakinan per kelas."""
    wl = warna(h.label)
    tulis_html(
        f"""
        <div class="sent-card" style="border-color:{wl};background:linear-gradient(180deg,{wl}22,var(--surface));">
            <div style="display:flex;justify-content:center;">{sentiment_icon(h.label)}</div>
            <div class="sent-label" style="color:{wl};">Sentimen Terdeteksi &middot; {escape(h.nama)}</div>
            <div class="sent-value" style="color:{wl};">{escape(str(h.label)).upper()}</div>
            <div class="sent-conf">Keyakinan {h.keyakinan * 100:.1f}%</div>
        </div>
        """
    )
    rows = "".join(
        _bar_row(str(k).title(), f"{float(h.prob[i]) * 100:.1f}%", float(h.prob[i]) * 100, warna(k))
        for i, k in enumerate(h.kelas)
    )
    tulis_html(card("chart", "Tingkat Keyakinan", rows))
