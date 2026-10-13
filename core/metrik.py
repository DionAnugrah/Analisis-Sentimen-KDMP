"""Hasil evaluasi kedua model pada data uji (disalin dari output notebook).

Perbarui angka di sini bila model dilatih ulang. Kartu akurasi di Home dan grafik perbandingan di
bagian Technology membaca dari sini, jadi tidak ada angka lain yang perlu diubah.
"""
from typing import Optional

from config import NAMA_BERT, NAMA_SVM

KELAS = ("negatif", "netral", "positif")

# per_kelas: kelas -> (precision, recall, f1, support)
# confusion: baris = kelas aktual, kolom = kelas prediksi (urutan KELAS)
EVALUASI = {
    NAMA_SVM: {
        "n_uji": 14182,
        "accuracy": 0.8545, "macro_precision": 0.8585, "macro_recall": 0.8730, "macro_f1": 0.8619, "weighted_f1": 0.8527,
        "per_kelas": {
            "negatif": (0.9038, 0.7577, 0.8244, 6200),
            "netral": (0.8184, 0.9287, 0.8701, 6200),
            "positif": (0.8532, 0.9327, 0.8912, 1782),
        },
        "confusion": [[4698, 1224, 278], [434, 5758, 8], [66, 54, 1662]],
    },
    NAMA_BERT: {
        "n_uji": 11125,
        "accuracy": 0.9892, "macro_precision": 0.9856, "macro_recall": 0.9841, "macro_f1": 0.9849, "weighted_f1": 0.9892,
        "per_kelas": {
            "negatif": (0.9904, 0.9893, 0.9898, 4878),
            "netral": (0.9922, 0.9951, 0.9937, 4878),
            "positif": (0.9743, 0.9679, 0.9711, 1369),
        },
        "confusion": [[4826, 23, 29], [18, 4854, 6], [29, 15, 1325]],
    },
}


def _pecahan(v) -> bool:
    """Angka 0..1 (bukan bool/NaN), format metrik dari notebook."""
    return isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 1


def _bulat(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def _model_valid(e) -> bool:
    """Semua angka yang dipakai grafik lengkap dan bertipe benar; bila tidak, grafik disembunyikan (bukan error)."""
    try:
        if not all(_pecahan(e[k]) for k in ("accuracy", "macro_precision", "macro_recall", "macro_f1", "weighted_f1")):
            return False
        if not (_bulat(e["n_uji"]) and e["n_uji"] > 0):
            return False
        for k in KELAS:
            p, r, f, n = e["per_kelas"][k]
            if not (_pecahan(p) and _pecahan(r) and _pecahan(f) and _bulat(n)):
                return False
        cm = e["confusion"]
        return len(cm) == len(KELAS) and all(len(b) == len(KELAS) and all(_bulat(x) for x in b) for b in cm)
    except (KeyError, TypeError, ValueError):
        return False


def tersedia() -> bool:
    """True bila hasil evaluasi kedua model lengkap dan valid, sehingga grafik perbandingan bisa ditampilkan."""
    return all(nama in EVALUASI and _model_valid(EVALUASI[nama]) for nama in (NAMA_SVM, NAMA_BERT))


def akurasi_persen(nama: str) -> Optional[float]:
    """Akurasi model dalam persen (2 desimal), atau None bila belum ada / tidak valid."""
    v = EVALUASI.get(nama, {}).get("accuracy")
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not (0 < v <= 1):
        return None
    return round(v * 100, 2)
