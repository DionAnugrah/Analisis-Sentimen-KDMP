"""
kdmp_prep.py
Preprocessing teks komentar TikTok (KDMP) untuk IndoBERT / IndoBERTweet.

Identik dengan bagian 3 notebook 04_Klasifikasi_IndoBERT.ipynb, sehingga teks
baru diproses PERSIS seperti saat model dilatih.

Kebutuhan : pip install emoji   (versi >= 2.0, untuk demojize bahasa Indonesia)

Pemakaian :
    from kdmp_prep import clean_text, clean_series
    clean_text("mantap banget wkwkwkwk 🤣🤣")
    df["text_full"] = clean_series(df["comment"])
"""

import re

import emoji

# --------------------------------------------------------------------------
# 1. Emoji -> kata
# --------------------------------------------------------------------------
EMOJI_GROUPS = {
    "tertawa":      "😂🤣😹😆",
    "senyum lebar": "😁😄😃😀😝😜🤪",
    "canggung":     "😅😳🥲",
    "sinis":        "😏🙄🗿🤭😌",
    "menangis":     "😭",
    "sedih":        "😢🥺😩😫😔🥹😞😿",
    "marah":        "😡🤬😠😤",
    "suka":         "👍🔥✅💪👏",
    "cinta":        "🥰❤😍😘💕💖",
    "doa":          "🙏🤲",
    "berpikir":     "🤔",
    "senyum":       "😊☺🙂😇",
}
EMOJI_MAP = {
    ch: name
    for name, chars in EMOJI_GROUPS.items()
    for ch in chars
    if ch != "\ufe0f"
}
# warna kulit, variation selector, zero-width joiner
_MODIFIER = re.compile("[\U0001F3FB-\U0001F3FF\uFE0F\u200d]")


def _emoji_repl(e, data=None):
    key = _MODIFIER.sub("", e)
    name = EMOJI_MAP.get(key)
    if name is None:  # emoji lain -> nama dalam bahasa Indonesia
        name = (
            emoji.demojize(key, language="id", delimiters=("", ""))
            .replace("_", " ")
            .strip()
        )
        if not name or name == key:
            return " "
    return f" emoji {name} "


# --------------------------------------------------------------------------
# 2. Tawa & pola sindiran
# --------------------------------------------------------------------------
def normalize_laughter(t):
    t = re.sub(r"\b[wk]{4,}\b", "wkwk", t)          # wkwkwk, kwkwkw, ...
    t = re.sub(r"\b(?:ha){2,}h?\b", "haha", t)
    t = re.sub(r"\b(?:he){2,}h?\b", "hehe", t)
    t = re.sub(r"\b(?:xi){2,}x?\b", "xixi", t)
    t = re.sub(r"\bn?gakak\w*\b", "ngakak", t)
    return t


CUE_RE = re.compile(
    r"\b(katanya|padahal|ternyata|mana (ada|mungkin|bisa)|ya ?kali|"
    r"(emang|memang) (bisa|boleh|ada)|(oh|owh) (ya|iya)|sok|pura pura)\b"
)
POS_WORD_RE = re.compile(
    r"\b(mantap|hebat|bagus|keren|pintar|pinter|top|wow|luar biasa)\b"
)
LAUGH_RE = re.compile(
    r"\b(wkwk|haha|hehe|xixi|ngakak)\b|"
    r"emoji (tertawa|menangis|sinis|canggung|senyum lebar)"
)


def has_cue(t):
    return bool(CUE_RE.search(t)) or (
        bool(POS_WORD_RE.search(t)) and bool(LAUGH_RE.search(t))
    )


# --------------------------------------------------------------------------
# 3. Fungsi utama
# --------------------------------------------------------------------------
def clean_text(text, use_features=True):
    """
    use_features=True  -> pipeline lengkap (emoji + tawa + sindiran). Dipakai model.
    use_features=False -> pembanding tanpa fitur tsb (untuk ablasi).
    """
    t = str(text).lower()
    t = re.sub(r"\[[^\]]*\]", " ", t)                # [Sticker], [Foto], dsb.
    t = re.sub(r"http\S+|www\.\S+", " httpurl ", t)
    t = re.sub(r"@\w+", " @user ", t)
    t = t.replace("\r", " ").replace("\n", " ")
    t = re.sub(r"(.)\1{2,}", r"\1\1", t)             # karakter berulang > 2
    if use_features:
        t = emoji.replace_emoji(t, replace=_emoji_repl)
        t = normalize_laughter(t)
    else:
        t = emoji.replace_emoji(t, replace=" ")
    t = re.sub(r"[^a-z0-9\s.,!?@']", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if use_features and has_cue(t):
        t += " sindiran"
    return t


def clean_series(series, use_features=True):
    """Terapkan clean_text ke pandas Series; nilai kosong (NaN) menjadi string kosong."""
    return series.fillna("").map(lambda x: clean_text(x, use_features))


if __name__ == "__main__":
    demo = [
        "Pak kamu di bohongi, mana ada gas elpiji 16rb 😂😅",
        "Mantap banget wkwkwkwkwk 🤣🤣🤣🤣",
        "katanya buat rakyat kecil, padahal malah mematikan warung 😭🙏🏻",
        "[Sticker] semoga sukses kopdes https://tiktok.com/xyz",
    ]
    for d in demo:
        print("ASLI  :", d)
        print("BERSIH:", clean_text(d))
        print()
