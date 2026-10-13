"""Fungsi preprocessing teks.

- ``clean_text``       : preprocessing SVM (berkas preprocessing.py, tidak diubah)
- ``clean_text_bert``  : preprocessing IndoBERT, emoji/tawa/sindiran dipertahankan (kdmp_prep.py).
                         Bernilai ``None`` bila berkas tidak dapat dimuat; alasannya ada di ``ERR_PREP``.
"""
from preprocessing import clean_text

try:
    from kdmp_prep import clean_text as clean_text_bert
    ERR_PREP = None
except Exception as e:
    clean_text_bert = None
    ERR_PREP = f"kdmp_prep.py tidak dapat dimuat: {e}"

__all__ = ["clean_text", "clean_text_bert", "ERR_PREP"]
