"""Alur analisis end-to-end (tanpa kode tampilan), dipakai oleh tab Tunggal dan Batch.

Semua model yang tersedia dijalankan sekaligus sehingga hasilnya langsung bisa dibandingkan.
"""
from typing import Callable, List, NamedTuple, Optional

import numpy as np
import pandas as pd

from config import (
    KOL_BERT, KOL_KEYAKINAN_BERT, KOL_SAMA, KOL_SVM, KOL_TEKS_BERSIH, NAMA_BERT, NAMA_SVM,
)
from core.models import Models
from core.prep import clean_text
from core.sentiment import prediksi_indobert, prediksi_svm

ProgressFn = Callable[[int, str], None]      # (persen 0..100, teks)


# ---------------------------------------------------------------- analisis tunggal
class HasilSentimen(NamedTuple):
    nama: str
    label: str
    kelas: List[str]
    prob: np.ndarray        # probabilitas satu komentar

    @property
    def keyakinan(self) -> float:
        return float(np.max(self.prob))


class HasilTunggal(NamedTuple):
    bersih_svm: Optional[List[str]]         # preprocessing SVM (None bila SVM tidak aktif)
    bersih_bert: Optional[List[str]]        # preprocessing IndoBERT (None bila tidak aktif)
    sentimen: List[HasilSentimen]           # satu entri per model aktif
    ada_kosong: bool                        # teks kosong setelah preprocessing

    @property
    def sepakat(self) -> Optional[bool]:
        """True/False bila dua model dibandingkan; None bila hanya satu model."""
        if len(self.sentimen) < 2:
            return None
        return self.sentimen[0].label == self.sentimen[1].label


def analisis_tunggal(teks: str, models: Models) -> HasilTunggal:
    bersih_svm = bersih_bert = None
    hasil: List[HasilSentimen] = []
    ada_kosong = False

    if models.ada_svm:
        p = prediksi_svm(models.sentimen, [teks])
        bersih_svm = p.bersih
        hasil.append(HasilSentimen(NAMA_SVM, p.pred[0], p.kelas, p.prob[0]))
        ada_kosong = ada_kosong or bool(p.kosong[0])

    if models.ada_bert:
        p = prediksi_indobert(models.indobert, [teks])
        bersih_bert = p.bersih
        hasil.append(HasilSentimen(NAMA_BERT, p.pred[0], p.kelas, p.prob[0]))
        ada_kosong = ada_kosong or bool(p.kosong[0])

    return HasilTunggal(bersih_svm, bersih_bert, hasil, ada_kosong)


# ---------------------------------------------------------------- analisis batch
def jalankan_batch(
    data: pd.DataFrame,
    kolom: str,
    batas: int,
    models: Models,
    progress: ProgressFn = lambda persen, teks: None,
) -> pd.DataFrame:
    """Proses ``batas`` baris pertama dengan semua model aktif; kembalikan DataFrame hasil."""
    d = data.head(int(batas)).copy()
    d[kolom] = d[kolom].fillna("").astype(str)

    hasil = d.copy()
    bersih = [clean_text(k) for k in d[kolom]]
    progress(20, "Preprocessing selesai...")

    if models.ada_svm:
        hasil[KOL_SVM] = models.sentimen.predict(bersih)
        progress(40, f"Analisis sentimen ({NAMA_SVM}) selesai...")

    if models.ada_bert:
        def _lapor(f):
            progress(int(40 + 40 * f), f"Analisis sentimen ({NAMA_BERT})... {f * 100:.0f}%")

        p = prediksi_indobert(models.indobert, d[kolom].tolist(), progress=_lapor)
        hasil[KOL_BERT] = p.pred
        hasil[KOL_KEYAKINAN_BERT] = p.prob.max(axis=1).round(4)
        progress(80, f"Analisis sentimen ({NAMA_BERT}) selesai...")

    if models.bisa_bandingkan:
        hasil[KOL_SAMA] = hasil[KOL_SVM] == hasil[KOL_BERT]

    hasil[KOL_TEKS_BERSIH] = bersih
    progress(100, "Selesai!")
    return hasil
