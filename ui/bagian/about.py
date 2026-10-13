"""Bagian About: penjelasan sistem (daftar keunggulan + kartu contoh klasifikasi)."""
from html import escape

from core.models import Models
from ui.components import bagian_judul
from ui.icons import ic
from ui.theme import warna
from ui.utils import tulis_html

_BUTIR = [
    ("layers", "Dual Model Prediction",
     "Menggunakan dua algoritma, SVM dan IndoBERT, sehingga prediksi bisa dibandingkan dan diperiksa silang."),
    ("spark", "Analisis Langsung",
     "Tempel satu komentar atau unggah file CSV, hasil sentimen dan tingkat keyakinan langsung ditampilkan."),
    ("table", "Preprocessing Sesuai Model",
     "Teks dibersihkan sesuai kebutuhan tiap model, termasuk singkatan, emoji, tawa, dan pola sindiran."),
]
# (label, ikon, kunci warna, keterangan, komentar contoh) - komentar hanya ilustrasi
_CONTOH = [
    ("Positif", "check", "positif", "Sentimen positif", "Programnya sangat membantu warga desa, semoga terus berjalan."),
    ("Negatif", "x", "negatif", "Sentimen negatif", "Pelayanannya lambat dan tidak sesuai harapan."),
    ("Netral", "minus", "netral", "Sentimen netral", "Ada yang tahu jadwal rapat anggota koperasi desa?"),
]


def _butir(ikon: str, judul: str, desk: str) -> str:
    return (f'<div class="li-item"><div class="sq">{ic(ikon, 22)}</div>'
            f'<div><div class="li-t">{judul}</div><div class="li-d">{desk}</div></div></div>')


def _baris_contoh(label, ikon, kunci, ket, komentar) -> str:
    c = warna(kunci)
    return (f'<div class="srow"><div class="srow-top">'
            f'<div class="srow-ic" style="background:{c}22;color:{c};">{ic(ikon, 16, sw=2.5)}</div>'
            f'<div><div class="srow-n">{label}</div><div class="srow-s">{ket}</div></div>'
            f'<span class="srow-dot" style="background:{c};"></span></div>'
            f'<div class="srow-q">&ldquo;{escape(komentar)}&rdquo;</div></div>')


def render(models: Models) -> None:
    bagian_judul(
        "about", "Tentang Sistem", 'Analisis Sentimen dengan <span class="acc">AI</span>',
        "Sistem analisis sentimen berbasis Machine Learning yang memakai dua model berbeda, "
        "sehingga hasilnya bisa dibandingkan dan diperiksa silang.",
    )
    kiri = "".join(_butir(*b) for b in _BUTIR)
    kanan = "".join(_baris_contoh(*c) for c in _CONTOH)
    tulis_html(
        f'<div class="split"><div>{kiri}</div>'
        f'<div class="scard"><div class="scard-t">Klasifikasi Sentimen</div>{kanan}'
        f'<div class="scard-cap">Komentar di atas hanya contoh ilustrasi.</div></div></div>'
    )
