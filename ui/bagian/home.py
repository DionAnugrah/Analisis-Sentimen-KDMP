"""Bagian Home: hero dua kolom (teks + kartu akurasi model) dan statistik singkat."""
from config import NAMA_BERT, NAMA_SVM
from core import metrik
from core.models import Models
from ui.icons import ic
from ui.layout import tautan
from ui.utils import tulis_html

# Satu string: tulis_html membuang pergantian baris tanpa menyisakan spasi.
_LEAD = ("Sistem analisis sentimen berbasis Machine Learning dengan dual model prediction (SVM &amp; IndoBERT) "
         "untuk mengklasifikasikan komentar publik tentang Koperasi Desa Merah Putih.")
_STATISTIK = [("2", "AI Models"), ("3", "Sentiments"), ("CSV", "Batch Analysis")]


def _baris_model(nama: str, aktif: bool, akurasi) -> str:
    if not aktif:
        nilai, kelas, lebar = "Tidak aktif", "off", 0
    elif akurasi is None:
        nilai, kelas, lebar = "Belum tersedia", "na", 0
    else:
        nilai, kelas, lebar = f"{akurasi:.2f}%", "on", akurasi
    return (
        f'<div class="hrow"><div class="hrow-top"><span class="mpill">{nama}</span>'
        f'<span class="hval {kelas}">{nilai}</span></div>'
        f'<div class="hbar"><i style="width:{lebar:.2f}%"></i></div></div>'
    )


def render(models: Models) -> None:
    stat = "".join(f'<div><div class="hs-n">{n}</div><div class="hs-l">{label}</div></div>' for n, label in _STATISTIK)
    tulis_html(
        f"""
        <div id="home" class="anchor"></div>
        <div class="hero2">
            <div>
                <span class="badge">{ic("star", 14)} AI-Powered Technology</span>
                <div class="h1">Analisis Sentimen <span class="acc">KDMP</span> Indonesia</div>
                <div class="lead">{_LEAD}</div>
                <div class="cta">
                    {tautan("coba", "Coba Sekarang " + ic("arrow", 18), "btn solid")}
                    {tautan("about", "Pelajari Lebih Lanjut", "btn white")}
                </div>
                <div class="hstats">{stat}</div>
            </div>
            <div class="hcard">
                <div class="hcard-t">Akurasi Model</div>
                {_baris_model("SVM Model", models.ada_svm, metrik.akurasi_persen(NAMA_SVM))}
                {_baris_model("IndoBERT", models.ada_bert, metrik.akurasi_persen(NAMA_BERT))}
                <div class="hlive">
                    <div class="hlive-l">Contoh Hasil</div>
                    <div class="hlive-b">
                        <div class="hlive-ic">{ic("ok", 22)}</div>
                        <div><div class="hlive-t">Kedua model sepakat</div>
                        <div class="hlive-s">Contoh ilustrasi alur hasil, bukan hasil nyata</div></div>
                    </div>
                </div>
            </div>
        </div>
        """
    )
