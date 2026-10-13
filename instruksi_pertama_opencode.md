# INSTRUKSI PEMROGRAMAN PERTAMA: SIMULASI SIRKULAN MSAF

Salin teks di bawah ini dan berikan kepada OpenCode sebagai pesan pertama setelah Anda menyematkan System Prompt.

---

Halo OpenCode. Saya Muhammad Aidil Amry. Berdasarkan System Prompt MSAF yang telah dikunci pada sesi ini, mari kita mulai tugas pemrograman pertama.

### Batasan Kerja
- Seluruh kode, fungsi, variabel, docstring, dan komentar wajib ditulis dalam **Bahasa Inggris** yang universal dan rigid.
- Penjelasan dan diskusi Anda dengan saya di chat wajib menggunakan **Bahasa Indonesia** yang formal dan teknis.
- Gunakan `python-flint` (`flint.arb`, `flint.arb_mat`) untuk memastikan komputasi interval rigid.

### Tugas: `msaf_core_lattice.py`
Buatlah sebuah modul bernama `msaf_core_lattice.py` yang mengimplementasikan arsitektur dasar berikut:

1. **Initialization of Precision:** Skema pengaturan presisi kontekstual yang aman untuk mencegah landmine `mpmath` global reset, menggunakan penyetelan bit eksplisit melalui `flint.ctx.prec`.
2. **Unitary Cyclic Shift Matrix Generator (`generate_shift_operator(n)`):** Fungsi untuk membangun matriks pergeseran siklik uniter $\hat{T}$ berukuran $n \times n$ asli menggunakan tipe data `flint.arb_mat`.
3. **Discrete Von Mangoldt Lattice Mapping (`quantized_von_mangoldt(k)`):** Fungsi untuk mengevaluasi $\Lambda_d(k)$ yang mengembalikan nilai interval `flint.arb` logaritma prima jika $k \cdot \ell_P$ bersesuaian dengan kekuatan bilangan prima berhingga, dan nol untuk piksel lainnya.
4. **Commutative Constraint Audit (`verify_commutation(h_matrix, t_matrix)`):** Fungsi penjamin rigid untuk menghitung $[\hat{H}, \hat{T}] = \hat{H}\hat{T} - \hat{T}\hat{H}$ dan memastikan ketidakpastian intervalnya memuat nol secara sempurna (Zero-Fudging Verification).

Sediakan arsitektur kode yang efisien, kaku, dan siap diuji.
