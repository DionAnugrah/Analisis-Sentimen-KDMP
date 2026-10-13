"""Bagian Features: enam fitur unggulan sebagai kartu."""
from core.models import Models
from ui.components import bagian_judul, feat_card, grid
from ui.utils import tulis_html

_FITUR = [
    ("message", "Analisis Komentar Tunggal",
     "Masukkan satu komentar dan lihat sentimennya beserta tingkat keyakinan model."),
    ("check", "Dual Verification",
     "Hasil SVM dan IndoBERT dibandingkan, dan sistem menandai kapan keduanya sepakat atau berbeda."),
    ("chart", "Confidence Score",
     "Setiap prediksi dilengkapi tingkat keyakinan untuk tiap kelas sentimen."),
    ("table", "Model Comparison",
     "Matriks kesesuaian menunjukkan di mana SVM dan IndoBERT sepaham dan di mana berselisih."),
    ("layers", "Analisis Batch CSV",
     "Unggah banyak komentar sekaligus, pilih kolom komentar, lalu proses semuanya."),
    ("upload", "Unduh Hasil",
     "Tabel hasil bisa difilter menurut sentimen dan kesesuaian, lalu diunduh sebagai CSV."),
]


def render(models: Models) -> None:
    bagian_judul(
        "features", "Fitur Unggulan", 'Mengapa Memilih <span class="acc">Sistem Ini?</span>',
        "Fitur-fitur yang membuat analisis sentimen komentar lebih mudah dan bisa diperiksa silang.",
    )
    tulis_html(grid([feat_card(*f) for f in _FITUR], 3))
