"""Prediksi sentimen: SVM (TF-IDF) dan IndoBERT."""
from typing import Callable, List, NamedTuple, Optional

import numpy as np

from config import BERT_BATCH_SIZE
from core.prep import clean_text, clean_text_bert


class Prediksi(NamedTuple):
    pred: np.ndarray        # label per komentar
    prob: np.ndarray        # keyakinan per kelas (n_komentar x n_kelas)
    kelas: List[str]
    bersih: List[str]       # teks hasil preprocessing
    kosong: np.ndarray      # True bila teks kosong setelah preprocessing


def _tandai_kosong(bersih) -> np.ndarray:
    return np.array([len(b.split()) == 0 for b in bersih])


def skor_sentimen(model, teks_bersih) -> np.ndarray:
    """Matriks 'keyakinan' per kelas (probabilitas / softmax skor SVM)."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(teks_bersih)
    s = model.decision_function(teks_bersih)
    e = np.exp(s - s.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


def prediksi_svm(model, komentar) -> Prediksi:
    bersih = [clean_text(k) for k in komentar]
    return Prediksi(
        pred=model.predict(bersih),
        prob=skor_sentimen(model, bersih),
        kelas=list(model.classes_),
        bersih=bersih,
        kosong=_tandai_kosong(bersih),
    )


def prediksi_indobert(
    paket, komentar, progress: Optional[Callable[[float], None]] = None, batch: int = BERT_BATCH_SIZE
) -> Prediksi:
    """Prediksi sentimen dengan IndoBERT. ``progress`` menerima pecahan 0..1."""
    import torch
    tok, mdl = paket["tokenizer"], paket["model"]
    labels, max_len = list(paket["labels"]), paket["max_len"]
    bersih = [clean_text_bert(k) for k in komentar]
    kosong = _tandai_kosong(bersih)
    if not bersih:
        return Prediksi(np.array([]), np.zeros((0, len(labels))), labels, bersih, kosong)

    hasil = []
    for i in range(0, len(bersih), batch):
        enc = tok(bersih[i:i + batch], truncation=True, max_length=max_len,
                  padding=True, return_tensors="pt")
        with torch.no_grad():
            hasil.append(torch.softmax(mdl(**enc).logits, dim=-1).cpu().numpy())
        if progress:
            progress(min(1.0, (i + batch) / len(bersih)))
    prob = np.vstack(hasil)
    pred = np.array([labels[j] for j in prob.argmax(1)])
    return Prediksi(pred, prob, labels, bersih, kosong)
