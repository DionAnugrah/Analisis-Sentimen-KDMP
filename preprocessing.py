"""preprocessing.py - fungsi pembersihan teks yang SAMA dengan yang dipakai di notebook.
Pastikan USE_STEMMING sama dengan nilai saat training (default notebook: False)."""
import re, os, joblib
USE_STEMMING = False
STEM_CACHE_PATH = "stem_cache.pkl"

import re, os, joblib, emoji
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# ---- Kamus slang / singkatan bahasa Indonesia -> bentuk baku ----
SLANG = {
    "gk":"tidak","ga":"tidak","gak":"tidak","nggak":"tidak","ngga":"tidak","enggak":"tidak","engga":"tidak",
    "tdk":"tidak","g":"tidak","tak":"tidak","kagak":"tidak","gpp":"tidak apa","gapapa":"tidak apa",
    "yg":"yang","yng":"yang","dgn":"dengan","dg":"dengan","dr":"dari","dri":"dari","utk":"untuk","untk":"untuk",
    "krn":"karena","karna":"karena","krna":"karena","sm":"sama","sama2":"sama","tp":"tapi","tapi":"tapi",
    "jd":"jadi","jdi":"jadi","udh":"sudah","udah":"sudah","sdh":"sudah","dah":"sudah","blm":"belum","belom":"belum",
    "bgt":"banget","bngt":"banget","bgd":"banget","skrg":"sekarang","skrang":"sekarang","sblm":"sebelum",
    "lg":"lagi","lgi":"lagi","lgsg":"langsung","kalo":"kalau","klo":"kalau","kl":"kalau","klw":"kalau",
    "emg":"memang","emang":"memang","mmg":"memang","hrs":"harus","harusny":"harus","bs":"bisa","bsa":"bisa",
    "sy":"saya","aq":"aku","ak":"aku","gw":"aku","gue":"aku","gua":"aku","w":"aku","lu":"kamu","loe":"kamu",
    "km":"kamu","kmu":"kamu","org":"orang","orng":"orang","spt":"seperti","sprti":"seperti","kyk":"seperti",
    "kayak":"seperti","bkn":"bukan","bukannya":"bukan","brp":"berapa","brapa":"berapa",
    "dmn":"dimana","dmna":"dimana","kmn":"kemana","knp":"kenapa","kenapa":"kenapa","gmn":"bagaimana","gimana":"bagaimana",
    "gmna":"bagaimana","bgmn":"bagaimana","emangnya":"memang","pd":"pada","pdhl":"padahal","pdahal":"padahal",
    "hrg":"harga","hrga":"harga","rb":"ribu","rbu":"ribu","jt":"juta","tmn":"teman","tmen":"teman",
    "mksh":"terima kasih","makasih":"terima kasih","thx":"terima kasih","tks":"terima kasih","trims":"terima kasih",
    "mantul":"mantap","mantab":"mantap","mantaap":"mantap","sip":"bagus","oke":"bagus","ok":"bagus","okey":"bagus",
    "bagu":"bagus","top":"bagus","keren":"bagus","joss":"bagus","sukses":"sukses","smoga":"semoga","semoga":"semoga",
    "moga":"semoga","amin":"amin","aamiin":"amin","amiin":"amin","btw":"omong omong","jgn":"jangan","jangn":"jangan",
    "sbg":"sebagai","sbgai":"sebagai","tsb":"tersebut","dll":"dan lain lain","dsb":"dan sebagainya","spy":"supaya",
    "biar":"supaya","cm":"cuma","cuman":"cuma","doang":"saja","aja":"saja","aj":"saja","sj":"saja","saja":"saja",
    "trus":"terus","trs":"terus","terus2":"terus","bnyk":"banyak","banyakk":"banyak","sdikit":"sedikit","skit":"sedikit",
    "lbh":"lebih","lbih":"lebih","mgkn":"mungkin","mungkin":"mungkin","tau":"tahu","tw":"tahu","pke":"pakai","pake":"pakai",
    "bikin":"buat","bkin":"buat","liat":"lihat","lht":"lihat","dpt":"dapat","dapet":"dapat","dpat":"dapat","ttp":"tetap",
    "tetep":"tetap","bru":"baru","baru2":"baru","lama2":"lama","cmn":"cuma","sll":"selalu","slalu":"selalu",
    "pemerintah":"pemerintah","pmrntah":"pemerintah","pemrintah":"pemerintah","pmerintah":"pemerintah",
    "indo":"indonesia","ri":"indonesia","wkwk":"tertawa","wkwkwk":"tertawa","wkwkwkwk":"tertawa","haha":"tertawa",
    "hahaha":"tertawa","hehe":"tertawa","hihi":"tertawa","kwkw":"tertawa","xixi":"tertawa","awokawok":"tertawa",
    "anjir":"kaget","anjay":"kaget","njir":"kaget","astaga":"kaget","astagfirullah":"istighfar",
}

# ---- Stopword: Sastrawi + tambahan; kata negasi DIPERTAHANKAN karena penting untuk sentimen ----
NEGASI = {"tidak","bukan","belum","jangan","tanpa","kurang","tak","nggak","gak","ga"}
STOPWORDS = set(StopWordRemoverFactory().get_stop_words())
STOPWORDS |= {"nya","sih","deh","dong","lah","kah","pun","tuh","nih","ya","yah","kan","kok","lho","loh","mah","nah","wah",
              "mas","bang","bg","kak","kakak","sis","bro","min","pak","bapak","bu","ibu","om","tante","mba","mbak","mbk",
              "eh","oh","ah","hehe","hmm","aja","saja","ada","adalah","sih","tertawa","lho","gitu","gini","begitu","begini",
              "banget","sekali","sangat","juga","lagi","udah","sudah","aku","kamu","saya","kita","kami","mereka","dia","nya",
              "kalau","jadi","buat","apa","sama","semua","dulu","terus","tahu","dapat","biar","gitu","display_"}
STOPWORDS -= NEGASI
STOPWORDS -= {"tidak","bukan","belum","jangan","tanpa","kurang"}

# ---- Kata topik yang muncul di hampir semua komentar (tidak membedakan apa-apa) ----
DOMAIN_STOPWORDS = {"koperasi","koprasi","kopdes","kdmp","kmp","merah","putih","desa","kelurahan"}
STOPWORDS |= DOMAIN_STOPWORDS

URL_RE      = re.compile(r"(https?://\S+|www\.\S+)")
MENTION_RE  = re.compile(r"@[\w\.]+")
BRACKET_RE  = re.compile(r"\[[^\]]{1,25}\]")            # [Sticker], [laughwithtears], dll.
SKIN_RE     = re.compile(r"_(medium_light|medium_dark|light|medium|dark)_skin_tone")
REPEAT_RE   = re.compile(r"(.)\1{2,}")                   # 3+ karakter/emoji berulang -> 1

stemmer = StemmerFactory().create_stemmer() if USE_STEMMING else None
stem_cache = joblib.load(STEM_CACHE_PATH) if (USE_STEMMING and os.path.exists(STEM_CACHE_PATH)) else {}

NO_STEM = {"pemerintah", "presiden", "rakyat", "menteri"}   # Sastrawi keliru menstem kata ini (mis. pemerintah -> perintah)

def stem_word(w):
    if w in NO_STEM:
        return w
    if w not in stem_cache:
        stem_cache[w] = stemmer.stem(w)
    return stem_cache[w]

def clean_text(text):
    t = str(text)
    t = re.sub(r"\\r\\n|\\n|\\r", " ", t)                 # \r\n yang tertulis literal
    t = re.sub(r"[\r\n\t]+", " ", t)                      # newline sungguhan
    t = t.lower()
    t = URL_RE.sub(" ", t)
    t = MENTION_RE.sub(" ", t)
    t = BRACKET_RE.sub(" ", t)
    t = t.replace("#", " ")
    t = REPEAT_RE.sub(r"\1", t)                           # 'mantaaaap' -> 'mantap', 😂😂😂 -> 😂
    t = emoji.demojize(t, delimiters=(" emo_", " "))      # emoji -> token teks (tetap membawa sentimen)
    t = t.lower()
    t = SKIN_RE.sub("", t)
    t = re.sub(r"[^a-z_\s]", " ", t)                      # buang angka, tanda baca, simbol
    tokens = t.split()

    out = []
    for w in tokens:
        for x in SLANG.get(w, w).split():
            if x.startswith("emo_"):
                out.append(x)
                continue
            if x in STOPWORDS or len(x) < 2:
                continue
            if USE_STEMMING:
                x = stem_word(x)
            if x in STOPWORDS or len(x) < 2:
                continue
            out.append(x)
    # hilangkan token identik yang berurutan
    out = [w for i, w in enumerate(out) if i == 0 or w != out[i-1]]
    return " ".join(out)
