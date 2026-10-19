# Triage blueprint lima masalah eksperimental (2026-10-20)

**Sumber:** `Five Core Experimental Problem Blueprint.md` (artefak pemilik,
tidak diubah; 8.197 byte; sha256LF
`016ae7c2d16cafc33c272db9a96f5226222768aa88e9b713e236cd04b40625a9`).
**Status:** **PLANNING ONLY — belum ada eksperimen yang dijalankan.**
**Peran:** menambahkan lima tantangan ke antrean perencanaan; tidak
menetapkan hasil, tidak mengubah Paket 1–9, dan tidak menambah klaim
matematis/fisika.

## 1. Aturan triage

1. Setiap item harus melewati pra-registrasi terpisah sebelum ada
   implementasi: matriks/instance, presisi, kriteria PASS/FAIL, dan
   batas klaim dikunci lebih dulu.
2. Tidak ada klaim RH, P≠NP, kriptografi praktis, atau fisika dari
   eksperimen finite mana pun. Item 2 hanya model periodisitas
   spektral, bukan algoritma faktorisasi.
3. Jalur angka memakai exact rational atau ball interval; item yang
   membutuhkan floating-point biasa ditolak atau diberi label
   `SIMULATED`/`INCONCLUSIVE` secara eksplisit.
4. Setiap hasil harus dapat direproduksi dari instance dan seed yang
   tercatat, dengan receipt deterministik dan guard CI.
5. Item yang tidak dapat diselesaikan tetap `OPEN`/`INCONCLUSIVE`;
   tidak ada penyelesaian paksa dengan menambah asumsi tersembunyi.

## 2. Lima item dan status awal

| # | Item | Inti finite yang masuk akal | Dependensi/risiko | Status |
|---|---|---|---|---|
| 1 | Guinand–Weil block untuk karakter Dirichlet non-primitif `χ_{q,n}` | Matriks `τ = W02 − WR − Wp` pada dimensi kecil, entri ball `acb`; uji nol struktural saat `gcd(q_k,q)>1`; inertia interval | Aritmetika karakter, modulus/konduktor, evaluasi digamma/trigamma pada presisi tinggi; risiko interpretasi "critical line lock" | `PLANNING` |
| 2 | Struktur permutasi uniter untuk periodisitas grup `Z_N^×` | Matriks permutasi eksak `U|x> = |a x mod N>`; uji `U†U=I`, `U^M=I`, eigenvalues root-of-unity | Ruang state harus dibatasi pada unit; bukan algoritma faktorisasi; parameter `N,a,M` harus kecil dan eksak | `PLANNING` |
| 3 | Operator Laplace–Beltrami untuk Selberg zeta | Truncated operator dari trace formula pada permukaan hiperbolik; bandingkan eigenvalue dengan statistik GUE pada N kecil | Geometri hiperbolik, panjang geodesik, normalisasi trace formula; risiko tinggi karena domain kontinu | `PLANNING` |
| 4 | Transisi lokalisasi Anderson pada random banded matrices | Matriks Hermitian banded dengan noise interval deterministik; estimator S1/S2; enam titik pra-registrasi | Definisi ensemble/seed, bandwidth, ukuran sampel; harus ada null-model Poisson dan kontrol GUE | `PLANNING` |
| 5 | Spectral closure Frobenius–Perron untuk sistem kacau | Matriks Ulam non-simetris dari overlaps rasional/ball; `arb_mat.eig`; alarm resolusi 60 iterasi | Amplifikasi kacau, non-simetris, sensitivitas discretization; tidak ada klaim ergodisitas global | `PLANNING` |

## 3. Urutan kerja yang diusulkan

Urutan ini dipilih untuk meminimalkan dependensi baru dan memberi
kemenangan finite lebih awal:

1. **Item 2** — paling eksak (permutasi rasional), tidak membutuhkan
   fungsi transenden, dan bisa menjadi uji dasar untuk exact matrix
   path.
2. **Item 4** — memakai infrastruktur statistik/interval yang sudah ada;
   null-model Poisson/GUE harus dikunci sebelum run.
3. **Item 5** — memakai `arb_mat.eig` dan alarm resolusi; perlu
   penanganan non-simetris dan sensitivitas yang lebih hati-hati.
4. **Item 1** — membutuhkan aritmetika karakter non-primitif dan
   evaluasi fungsi aritmetika pada presisi tinggi.
5. **Item 3** — risiko geometri/kontinu tertinggi; paling akhir dan
   membutuhkan pra-registrasi paling rinci.

Urutan ini **tidak** berarti item 1–5 akan dikerjakan sekarang. Setiap
item harus mendapat persetujuan pemilik dan pra-registrasi sendiri.

## 4. Definisi "selesai" yang diizinkan

- `CERTIFIED-FINITE`: instance eksak/ball tertentu lolos kriteria yang
  dikunci, dengan receipt dan guard.
- `INCONCLUSIVE`: hasil tidak memisahkan hipotesis atau presisi tidak
  cukup; dicatat, bukan dinaikkan menjadi klaim.
- `FAILED`: kriteria tidak terpenuhi; dicatat sebagai hasil negatif.
- `OPEN`: belum dijalankan atau membutuhkan sumber daya di luar sesi.

Tidak ada status `PROVEN` untuk klaim umum RH/P≠NP/fisika dari item-item
ini.

## 5. Hubungan dengan pekerjaan verifikasi saat ini

Lima item ini adalah antrean riset baru dan **tidak** mengubah:

- trusted base Coq empat aksioma stdlib;
- status `lean/spec/` yang kondisional (lihat catatan koreksi spec
  terpisah);
- scope gate anti-circularity pada empat berkas Lean kernel;
- Paket 7–9 dan laporan beku.

Pekerjaan verifikasi yang dieksekusi lebih dulu adalah infrastruktur
yang lebih kecil dan sudah punya jalur reproduksi: audit aksioma Lean,
Coq CI, dan koreksi spec. Setelah itu barulah item blueprint dipilih
satu per satu.
