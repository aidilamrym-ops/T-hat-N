# Triage blueprint lima masalah eksperimental (2026-10-20)

**Sumber:** `Five Core Experimental Problem Blueprint.md` (artefak pemilik,
no diubah; 8.197 byte; sha256LF
`016ae7c2d16cafc33c272db9a96f5226222768aa88e9b713e236cd04b40625a9`).
**Status:** **PLANNING ONLY â€” belum ada eksperimen which dijalankan.**
**Peran:** menambahkan lima tantangan ke antrean perencanaan; no
menetapkan result, no mengubah Paket 1â€“9, and no menambah klaim
matematis/fisika.

## 1. Aturan triage

1. Setiap item harus melewati pra-registrasi terpisah sebelum ada
   implementasi: matriks/instance, presisi, kriteria PASS/FAIL, and
   limit klaim dikunci lebih dulu.
2. Tidak ada klaim RH, Pâ‰ NP, kriptografi praktis, or fisika dari
   eksperimen finite mana pun. Item 2 hanya model periodisitas
   spektral, bukan algoritma faktorisasi.
3. Jalur angka memakai exact rational or ball interval; item which
   membutuhkan floating-point biasa ditolak or diberi label
   `SIMULATED`/`INCONCLUSIVE` secara eksplisit.
4. Setiap result harus dapat direproduksi dari instance and seed which
   tercatat, with receipt deterministik and guard CI.
5. Item which no dapat diselesaikan tetap `OPEN`/`INCONCLUSIVE`;
   no ada penyelesaian paksa with menambah asumsi tersembunyi.

## 2. Lima item and status awal

| # | Item | Inti finite which masuk akal | Dependensi/risiko | Status |
|---|---|---|---|---|
| 1 | Guinandâ€“Weil block for karakter Dirichlet non-primitif `Ï‡_{q,n}` | Matriks `Ï„ = W02 âˆ’ WR âˆ’ Wp` on dimensi kecil, entri ball `acb`; uji nol struktural saat `gcd(q_k,q)>1`; inertia interval | Aritmetika karakter, modulus/konduktor, evaluasi digamma/trigamma on presisi tinggi; risiko interpretasi "critical line lock" | `PLANNING` |
| 2 | Struktur permutasi uniter for periodisitas grup `Z_N^Ã—` | Matriks permutasi eksak `U|x> = |a x mod N>`; uji `Uâ€ U=I`, `U^M=I`, eigenvalues root-of-unity | Ruang state harus dibatasi on unit; bukan algoritma faktorisasi; parameter `N,a,M` harus kecil and eksak | `PLANNING` |
| 3 | Operator Laplaceâ€“Beltrami for Selberg zeta | Truncated operator dari trace formula on permukaan hiperbolik; bandingkan eigenvalue with statistik GUE on N kecil | Geometri hiperbolik, panjang geodesik, normalisasi trace formula; risiko tinggi karena domain kontinu | `PLANNING` |
| 4 | Transisi lokalisasi Anderson on random banded matrices | Matriks Hermitian banded with noise interval deterministik; estimator S1/S2; enam titik pra-registrasi | Definisi ensemble/seed, bandwidth, ukuran sampel; harus ada null-model Poisson and kontrol GUE | `PLANNING` |
| 5 | Spectral closure Frobeniusâ€“Perron for sistem kacau | Matriks Ulam non-simetris dari overlaps rasional/ball; `arb_mat.eig`; alarm resolusi 60 iterasi | Amplifikasi kacau, non-simetris, sensitivitas discretization; no ada klaim ergodisitas global | `PLANNING` |

## 3. Urutan kerja which diusulkan

Urutan ini dipilih for meminimalkan dependensi baru and memberi
kemenangan finite lebih awal:

1. **Item 2** â€” paling eksak (permutasi rasional), no membutuhkan
   fungsi transenden, and bisa menjadi uji dasar for exact matrix
   path.
2. **Item 4** â€” memakai infrastruktur statistik/interval which already ada;
   null-model Poisson/GUE harus dikunci sebelum run.
3. **Item 5** â€” memakai `arb_mat.eig` and alarm resolusi; perlu
   penanganan non-simetris and sensitivitas which lebih hati-hati.
4. **Item 1** â€” membutuhkan aritmetika karakter non-primitif and
   evaluasi fungsi aritmetika on presisi tinggi.
5. **Item 3** â€” risiko geometri/kontinu tertinggi; paling akhir and
   membutuhkan pra-registrasi paling rinci.

Urutan ini **no** berarti item 1â€“5 akan dikerjakan sekarang. Setiap
item harus mendapat persetujuan pemilik and pra-registrasi sendiri.

## 4. Definisi "selesai" which diizinkan

- `CERTIFIED-FINITE`: instance eksak/ball tertentu lolos kriteria which
  dikunci, with receipt and guard.
- `INCONCLUSIVE`: result no memisahkan hipotesis or presisi no
  cukup; dicatat, bukan dinaikkan menjadi klaim.
- `FAILED`: kriteria no terpenuhi; dicatat sebagai result negatif.
- `OPEN`: belum dijalankan or membutuhkan source daya in luar sesi.

Tidak ada status `PROVEN` for klaim umum RH/Pâ‰ NP/fisika dari item-item
ini.

## 5. Hubungan with pekerjaan verifikasi saat ini

Lima item ini adalah antrean riset baru and **no** mengubah:

- trusted base Coq empat aksioma stdlib;
- status `lean/spec/` which kondisional (lihat note koreksi spec
  terpisah);
- scope gate anti-circularity on empat file Lean kernel;
- Paket 7â€“9 and report beku.

Pekerjaan verifikasi which dieksekusi lebih dulu adalah infrastruktur
which lebih kecil and already punya jalur reproduksi: audit aksioma Lean,
Coq CI, and koreksi spec. Setelah itu barulah item blueprint dipilih
satu per satu.


