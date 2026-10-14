"""Animasi masuk saat scroll yang berbasis WAKTU, sama seperti animasi hero, dan DIPUTAR ULANG setiap kali sebuah
elemen masuk layar lagi (scroll ke bawah maupun ke atas).

CSS tidak bisa memicu animasi berbasis waktu ketika sebuah elemen masuk layar. Karena itu skrip kecil
(IntersectionObserver) dijalankan lewat ``st.html(..., unsafe_allow_javascript=True)``: skrip berjalan langsung di
halaman utama, tanpa iframe. ``st.components.v1.html`` TIDAK dipakai lagi karena sudah deprecated (Streamlit >= 1.56)
dan dijadwalkan dihapus; ia hanya menjadi pilihan terakhir untuk Streamlit lama (lihat ``pasang``). Ada dua pengamat dengan tugas terpisah:

* ``masuk``  : menambah class ``rv-in`` saat elemen muncul di layar (sedikit di atas tepi bawah, di bawah navbar),
               lalu CSS memainkan animasi ``naik`` / ``dariKiri`` / ``dariKanan`` dengan durasi, easing, dan jeda
               bertahap yang sama dengan hero.
* ``keluar`` : mencabut ``rv-in`` HANYA setelah elemen keluar sepenuhnya dari layar, sehingga elemen kembali ke keadaan
               awal dan animasinya main lagi ketika terlihat berikutnya. Tepi bawah ``masuk`` dibuat lebih sempit
               daripada ``keluar`` agar elemen di tepi layar tidak berkedip (hysteresis).

Hero (``.hero2``) ikut diputar ulang saat kembali ke atas. Bila hero sudah terlihat ketika skrip aktif, ``rv-in``
langsung dipasang agar animasi pembukaan yang sedang berjalan tidak diulang dari awal.

Skrip hanya menyembunyikan elemen SETELAH berhasil mengakses halaman induk. Bila gagal (komponen tidak bisa dimuat,
sandbox tanpa allow-same-origin, dll.), halaman tetap tampil utuh dan CSS memakai animasi scroll-driven sebagai cadangan.
"""

# Harus sama dengan daftar selektor animasi masuk di styles.css
SELEKTOR = (".part, .sec, .grid > *, .status-row, .cap, .footer2 .f-grid > *, "
            ".split > div:first-child, .split > .scard, .st-key-tool_card")
SELEKTOR_HERO = ".hero2"

_SKRIP = """<span id="kdmp-anim" hidden></span><script>
(function () {
  // Di halaman utama (st.html) window.parent === window; di dalam iframe ia menunjuk halaman induk. Skrip yang sama
  // berlaku untuk keduanya.

  var P = window, D = document;
  if (!D.querySelector(".stApp")) {      // bukan halaman app (mis. di dalam iframe): pakai induknya
    try { P = window.parent; D = P.document; D.documentElement; } catch (e) { return; }
}

  var SEL = "__SELEKTOR__", HERO = "__HERO__";
  var lama = P.__rvKdmp;                              // komponen dimuat ulang: lepas pengamat lama
  if (lama) { try { lama.masuk.disconnect(); lama.keluar.disconnect(); lama.mo.disconnect(); } catch (e) {} }
  var ATAS = "-76px";                                 // tinggi navbar: elemen dianggap terlihat setelah muncul di bawahnya
  var masuk = new P.IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) e.target.classList.add("rv-in"); });
  }, { threshold: 0, rootMargin: ATAS + " 0px -8% 0px" });
  var keluar = new P.IntersectionObserver(function (es) {
    es.forEach(function (e) { if (!e.isIntersecting) e.target.classList.remove("rv-in"); });
  }, { threshold: 0, rootMargin: ATAS + " 0px 0px 0px" });
  function amati(el) { masuk.observe(el); keluar.observe(el); }
  // Dipanggil ulang tiap DOM berubah. Inisialisasi hanya sekali per elemen, tetapi SEMUA elemen diamati lagi di setiap
  // pemanggilan (observe() pada target yang sama tidak berefek): bila komponen dimuat ulang, pengamat baru harus
  // tetap memegang elemen yang sudah ditandai, kalau tidak animasi berhenti dan elemen bisa tertahan tersembunyi.
  function tandai() {
    D.querySelectorAll(SEL).forEach(function (el) {
      if (!el.style.getPropertyValue("--d")) {
        var i = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : 0;
        el.style.setProperty("--d", ((i % 4) * 0.12) + "s");   // jeda bertahap antar kartu sebaris
      }
      el.classList.add("rv");
      amati(el);
    });
    D.querySelectorAll(HERO).forEach(function (el) {
      if (!el.classList.contains("rvh")) {
        // BACA posisi dulu, baru tambah class. Membaca layout di antara dua penambahan class memaksa browser menghitung
        // gaya "tersembunyi" di tengah-tengah, yang menghapus animasi pembukaan yang sedang berjalan lalu mengulangnya.
        var r = el.getBoundingClientRect();
        var terlihat = r.bottom > 76 && r.top < P.innerHeight;
        el.classList.add("rvh");
        if (terlihat) el.classList.add("rv-in");      // sudah terlihat: lanjutkan animasi yang berjalan, jangan diulang
      }
      amati(el);
    });
  }
  var t = null;
  var mo = new P.MutationObserver(function () { clearTimeout(t); t = setTimeout(tandai, 60); });
  D.documentElement.classList.add("js-rv");
  tandai();
  mo.observe(D.body, { childList: true, subtree: true });
  P.__rvKdmp = { masuk: masuk, keluar: keluar, mo: mo };
})();
</script>""".replace("__SELEKTOR__", SELEKTOR).replace("__HERO__", SELEKTOR_HERO)


def _via_html() -> None:
    import streamlit as st
    # Streamlit lama: TypeError (st.html belum punya unsafe_allow_javascript) -> lanjut ke cara berikutnya
    st.html(_SKRIP, unsafe_allow_javascript=True)


def _via_iframe() -> None:
    import streamlit as st
    # tinggi 1 (bukan 0) agar lolos validasi ukuran; wadahnya disembunyikan oleh CSS
    st.iframe(_SKRIP, height=1)


def _via_components() -> None:
    import streamlit.components.v1 as components      # deprecated: hanya untuk Streamlit lama
    components.html(_SKRIP, height=0)


def pasang() -> None:
    """Pasang skrip animasi memakai cara pertama yang tersedia di versi Streamlit yang sedang berjalan:

    1. ``st.html(..., unsafe_allow_javascript=True)``  skrip langsung di halaman utama (disarankan)
    2. ``st.iframe(...)``                              skrip di iframe, menjangkau induk lewat ``window.parent``
    3. ``st.components.v1.html(...)``                  Streamlit lama saja (menghasilkan peringatan deprecation)

    Kegagalan apa pun diabaikan; CSS cadangan tetap memberi animasi scroll.
    """
    for cara in (_via_html, _via_iframe, _via_components):
        try:
            cara()
            return
        except Exception:
            continue
