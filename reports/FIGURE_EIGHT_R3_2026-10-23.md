# T2-r3 - Orbit figure-eight tervalidasi (reduced 8x8), verdict INCONCLUSIVE

**Status formal: INCONCLUSIVE.**
K1-K5 lulus penuh, tetapi gerbang K6 no lengkap: mutasi M5
(`SWEEP_SIGNED = False`, reset produk sensitivitas per blok) masih
menghasilkan K2/K3 PASS. Karena itu K6 **no** diklaim PASS, verdict
formal trek r3 adalah **INCONCLUSIVE**, and **no ada** entri registry
`A-2026-0042`. Entri `A-2026-0041` juga tetap no ada.

| Item | Nilai |
|---|---|
| Prereg | `reports/PREREG_FIGURE_EIGHT_R3_2026-10-23.md` |
| Prereg commit | `38d19e8` |
| Prereg SHA-256LF | `23ab24254f13539dddf1bd3cccd87dbbcef01b3398dab1ccf5fb2d75099a6b93` |
| Modul | `msaf/figure_eight_r3.py` |
| Modul SHA-256LF | `8eddc2bb17647d452e15325397e852e224e1af028f055fa4fe41de94af939ec6` |
| Receipt | `reports/figure_eight_r3_2026-10-23.json` |
| Receipt SHA-256LF | `6b0b71e91c9b38a2e8b43e8b2da12dbf2ce273321ffe2c4376e09bbbbdf829c9` |
| T1 SHA-256LF | `c1d9b5d60036a5f0772f7e3f1b8c78969efaa7146a713c762531ddce346251b9` |
| T1b SHA-256LF | `42d196a51c5ae45e3b87b8c1e36319abfeb93df776b3c2317e812f7c2c0b5b97` |
| Verdict | **INCONCLUSIVE** (K1-K5 PASS; K6/M5 non-diskriminatif) |

>

**Batas penting.** `"summary": "ALL PASS"` in receipt adalah status
kampanye **K1-K5** and harus dibaca bersama report ini. Itu bukan klaim
registry and bukan klaim bahwa K6 lulus. Sertifikat matematis lokal
K1-K5 valid secara kondisional; status formal trek tetap INCONCLUSIVE.

## 0. Ringkasan eksekutif

- T2-r2 ditutup FAILED on K2 karena slack kuadratik beku
  `KAPPA_NL = 1e18`; no ada registry.
- T2-r3 adalah trek baru with limit kuadratik lokal `QUAD_STEP` and
  limit turunan sisa Taylor `DR_MAX`, keduanya eksak-ball, tanpa float.
- Titik Newton r2 dipakai hanya sebagai seed titik. R3 mengevaluasi ulang
  `G(xh)` and memperoleh `|G(xh)|_inf <= 1e-24`.
- Kampanye final: K1 PASS, K2 PASS, K3 PASS, K4 PASS, K5 PASS.
- K6: M1 and M2 diskriminatif (FAILED), M3 and M4 diperiksa guard,
  tetapi **M5 no diskriminatif** (tetap ALL PASS). Karena prereg
  mensyaratkan M5 menghasilkan FAILED, K6 no boleh diklaim PASS.
- Konsekuensi: **INCONCLUSIVE; no ada `A-2026-0042`; no ada
  perubahan `FENCE_REGISTRY.md`.**

## 1. Garis keturunan and alasan trek

- T2 (11-dimensi) FAILED on K3 karena singularitas translasi-x.
- T2-r2 (reduced 8x8) FAILED on K2; Newton 8x8 sendiri mencapai residu
  `4.2228457153578479e-25`, tetapi slack kuadratik beku no dapat
  dimasukkan on `R_B = 1e-10`.
- T2-r3 mengganti slack global itu with limit lokal satu step.
  Prereg ditulis and in-commit **sebelum** kode r3 (`38d19e8`).
- R3 no mengubah T1, T1b, `ci.yml`, pin freeze, or artefak r2.

## 2. Sistem, gauge, and konstanta

Tiga massa sama `m = 1`, bidang, Hamiltonian

```
H = 1/2 (|v1|^2 + |v2|^2 + |v3|^2)
    - 1/|q1-q2| - 1/|q1-q3| - 1/|q2-q3|.
```

Pusat massa dikunci eksak: `q1+q2+q3 = 0`, `v1+v2+v3 = 0`.
Koordinat bebas `(q1x,q1y,q2x,q2y,v1x,v1y,v2x,v2y)`;
`q3 = -q1-q2`, `v3 = -v1-v2`.

```
T0 = 632600304 / 10^8 = 6.326003040
H_STEPS = 1536
h = T0 / 1536
BLOCK_STEPS = 96
```

Gauge:

```
q1y = 1/5,
I_xy = q1x q1y + q2x q2y + q3x q3y = 0.
```

Return map `G: R^8 -> R^8` memakai enam komponen
`(q1x,q1y,q2x,q2y,v1x,v1y)` on `T0` plus dua gauge. Enam baris itu
adalah `KEEP = (0,1,3,4,5,6)`; baris which dibuang adalah `(2,7)`.

Konstanta terkunci:

| Nama | Nilai |
|---|---|
| `R_B` | `1e-18` |
| `K_MARGIN` | `9/10` |
| `KAPPA_MAX` | `1/2` |
| `POINT_TARGET` | `1e-24` |
| `HESS_BOX` | `1e-12` |
| `QUAD_SAFETY` | `4` |
| `QUAD_CAP` | `1e-18` |
| `DR_CAP` | `1e-18` |
| `TUBE_CAP` | `1e-10` |
| `GAUSS_DET_MIN` | `1e-6` |
| `GAUSS_COND_MAX` | `1e6` |
| `CHOREO_TOL` | `1e-6` |

## 3. Metode r3 and koreksi soundness

### 3.1 Batas Hessian satu step

Untuk setiap step, `a_k`, `b_k` adalah limit norma pertama and kedua
dari RHS tiga-benda, dihitung with jet orde dua `Dual2`. `s_k` adalah
limit produk sensitivitas bertanda dari step-step sebelumnya.
Batas Hessian satu step:

```
H_STEP_k = (b_k s_k^2 / a_k) * exp(a_k h) * (exp(a_k h) - 1)
H_STEP_MAX = max_k H_STEP_k
QUAD_STEP = 4 * H_STEP_MAX * HESS_BOX^2.
```

`QUAD_STEP` konstan per step; no ada umpan-balik `KAPPA_NL`.

### 3.2 Koreksi path box (wajib)

Implementasi awal mengevaluasi `a_k`, `b_k`, and gradien tail on bola
`mid_k +/- HESS_BOX` in **titik awal** step. Itu no memuat jalur
solusi satu step: posisi bergerak sekitar `v*h ~ 0.01`, sementara
`HESS_BOX = 1e-12`. Batas Hessian/remainder dari bola awal karena itu
**no sound**; receipt ALL PASS pra-koreksi ditarik.

Perbaikan: `_step_with_box` adalah salinan baris-per-baris step T1b
which mengembalikan **Picard path box tervalidasi**. Kotak itu memuat
seluruh jalur solusi on step, bukan hanya titik awal. `_local_bounds`
mengevaluasi `a_k`, `b_k`, `Dtail`, and `L_f` on path box which
diperluas `2*HESS_BOX` (for menampung tabung box-pass). T1b tetap beku;
hanya modul r3 which memiliki salinan ini.

Ini diperlakukan sebagai **koreksi soundness implementasi pra-verdict**,
bukan amendemen prereg: formula `H_STEP`, `QUAD_STEP`, `DR_MAX`,
konstanta, and kriteria no berubah. Prereg no diubah. Karena verdict
akhir INCONCLUSIVE and no ada registry, koreksi ini dicatat in sini
tanpa mengklaim amendemen. Bila pembaca menilai perubahan domain ini
sebagai perubahan metode, maka r3 harus dibaca sebagai INCONCLUSIVE and
perlu trek r4; report ini no menyembunyikannya.

### 3.3 Batas turunan sisa Taylor

```
Dtail_k = max |d tail / dy| on path box
L_f,k   = max_i sum_j |df_i/dy_j|
Lambda_k = 2 * exp(h * L_f,k)
DR_k = 2 * Lambda_k * Dtail_k * h^(ORDER+1)
DR_MAX = max_k DR_k.
```

`DR_MAX` ditambahkan secara seragam ke setiap entri Jacobian step:

```
J_eff = J_taylor + [-DR_MAX, +DR_MAX].
```

Dengan demikian `J_eff` meng-enclose turunan peta step penuh
(polinomial Taylor plus sisa), bukan hanya turunan polinomial.

### 3.4 K2 box pass

Input delapan koordinat: `B = B(xh, R_B)`, `R_B = 1e-18`.
Lift radius eksak. Setiap step:

```
m_next, J, rem, path_box = _step_with_box(...)
J_eff = J + [-DR_MAX, +DR_MAX]
c_next = |J_eff| c + rem + QUAD_STEP + EPS_SLACK.
```

Pada setiap checkpoint 96 step, `t1b.certificate` (signed continuous
sweep) menghitung `c_out`. K2 PASS bila no ada error, `QUAD_STEP <=
1e-18`, `DR_MAX <= 1e-18`, lebar setiap checkpoint `<= 1e-10`, and
radius tabung berjalan `<= HESS_BOX = 1e-12` (syarat berlakunya limit
Hessian).

### 3.5 K3 Krawczyk

`W = invers midpoint DG(xh)`. Untuk setiap baris:

```
K(B) = xh - W G(xh) + (I - W DG(B)) (B - xh)
```

K3 PASS bila `|G(xh)|_inf <= 1e-24`, `kappa_inf <= 1/2`, and setiap baris
`|W G(xh)|_i + kappa_i R_B <= (9/10) R_B`. Ini memberi keberadaan and
**keunikan lokal** satu nol `G` in `B`; no ada klaim global.

## 4. Hasil K1-K5 (final, path-box sound)

Receipt final dihasilkan oleh **dua kampanye penuh byte-identik**
(`6b0b71e9...`). Angka in bawah adalah midpoint/ball dari receipt.

### K1 - integritas

- AST scan: no ada literal float, `float(...)`, `math`, `numpy`,
  `scipy`, `random`, `time`, or import terlarang.
- Prereg SHA-256LF cocok; T1/T1b SHA-256LF cocok.
- **PASS.**

### K2 - tabung lokal

| Besaran | Nilai |
|---|---|
| `a_max` | `19.1040999676022635...` |
| `b_max` | `391.8839505946359348...` |
| `s_max` | `163.8618045317627307...` |
| `H_STEP_MAX` | `47368.22455934667354...` |
| `QUAD_STEP` | `1.894728982373866941...e-19` |
| `DR_MAX` | `1.114186167976259912...e-42` |
| lebar K2 maksimum | `4.375764330275093479...e-14` |
| radius berjalan maksimum | `8.164954245581349658...e-14` |
| jumlah checkpoint | 16 |

`QUAD_STEP <= 1e-18`, `DR_MAX <= 1e-18`, lebar `<= 1e-10`, and radius
berjalan `<= 1e-12`. **PASS.**

### K3 - Krawczyk

| Besaran | Nilai |
|---|---|
| `|G(xh)|_inf` | `4.222845715357847910...e-25` |
| `point_ok` | `True` |
| `w_max` | `51.92421404453306048...` |
| `kappa_inf` | `3.376789173614763082...e-4` |
| budget per baris | `9.000...e-19` |
| baris Krawczyk | 8/8 `ok` |

`|G(xh)| <= 1e-24`, `kappa <= 1/2`, semua baris masuk margin
`(9/10)R_B`. **PASS.**

### K4 - determinan/kondisi Gauss

| Besaran | Nilai |
|---|---|
| `det DG(xh)` | `-7.623407555838881166...` |
| `det_contains_zero` | `False` |
| `cond_inf` | `29649.63760391575706...` |

`|det|` jauh in atas `1e-6`; `cond <= 1e6`. **PASS.**
Tidak ada klaim eigenvalue, spektrum, or stabilitas.

### K5 - deskriptor koreografi

Enam relasi fase-independent on `T/3` and `2T/3`; defect maksimum:

```
1.212132602582212128...e-14 <= 1e-6.
```

**PASS.** Ini hanya deskriptor in dalam tabung, bukan klasifikasi global.

### Catatan tabrakan (internal, bukan gerbang)

- limit bawah jarak pasangan: `0.680813440006505927...`
- gerak setengah step: `0.009721352271552947...`
- radius tabung maksimum: `8.164954245581349658...e-14`

Jarak tetap in atas `1/2`; ini note internal, bukan bukti bebas
tabrakan global.

## 5. K6 - result mutasi and mengapa verdict INCONCLUSIVE

| Mutasi | Efek aktual | Diskriminatif? |
|---|---|---|
| M1 `REMAINDER_FACTOR = 1e70` | FAILED; K2 abort step 2 (`Picard enclosure failed`); K3/K4/K5 no lulus | Ya |
| M2 `T0 -> T0 + 1/10` | FAILED; K2 PASS, K3 FAILED (`|G| ~ 1.011e-1`), K5 FAILED | Ya |
| M3 satu byte receipt diubah | guard mendeteksi payload/hash berbeda | Ya (guard) |
| M4 injeksi float literal/`float(...)` | AST scan menghasilkan hit | Ya (guard) |
| M5 `SWEEP_SIGNED = False` | **ALL PASS K1-K5**; K2/K3 tetap PASS | **Tidak** |

Karena M5 no menghasilkan FAILED, K6 **no boleh diklaim PASS**
sesuai prereg section 4. Verdict formal r3 adalah **INCONCLUSIVE**;
`A-2026-0042` no created. Mutasi M1/M2 tetap menunjukkan bahwa gerbang
K2/K3 dapat menolak input which salah; M5 hanya menunjukkan bahwa envelope
unsigned masih cukup lebar for lolos on tabung r3 which sangat ketat.

M5 bukan kegagalan matematis K1-K5. Ia adalah keterbatasan **falsifier
K6** which dikunci. Kami no mengubah ambang, no memperkuat mutasi
setelah melihat result, and no menambah registry.

## 6. Pengungkapan bug and receipt which ditarik

Tiga hal ditemukan sebelum receipt final:

1. **Domain limit Hessian no sound.** Implementasi awal memakai bola
   start-centered `mid_k +/- HESS_BOX`; jalur satu step keluar dari
   bola itu. Diperbaiki with `_step_with_box` (Picard path box T1b).
   Receipt ALL PASS sebelum koreksi ditarik.
2. **Koefisien Hessian `Dual2.sqrt` salah.** Koefisien awal
   `-g_i g_j inv2^3 / 2` terlalu kecil; bentuk which benar adalah
   `-g_i g_j / (4 a^(3/2))`. Ini membuat `b_k` underestimated. Setelah
   perbaikan, `b_max` naik dari sekitar `220.9` ke `391.9` and
   `H_STEP_MAX` dari sekitar `26633` ke `47368`; semua masih in bawah cap.
3. **Clamp `smax >= 1`.** Ditambahkan agar limit Hessian no memakai
   produk sensitivitas global which kebetulan in bawah 1 on awal
   step; ini hanya dapat memperbesar limit, bukan mengecilkannya.

Receipt final `6b0b71e9...` berasal dari kode setelah ketiga koreksi.
Dua kampanye final identik byte. Tidak ada angka probe which dipakai
sebagai sertifikat.

## 7. Batas klaim

K1-K5 secara matematis memberikan, **kondisional on kode/receipt in
atas**, keberadaan and keunikan lokal satu orbit periodik figure-eight
in dalam box `B` on periode tetap `T0`, modulo gauge which dikunci.
Namun status formal trek r3 adalah **INCONCLUSIVE** karena K6/M5, and
no ada registry.

Tidak ada klaim: keunikan global, orbit lain in luar `B`, stabilitas
linear/nonlinear, spektrum, chaos, ergodisitas, KAM, PDE, RH, fisika,
prioritas, Lean/Coq, or penyelesaian masalah three-body secara umum.

## 8. Verifikasi

Perintah which harus lulus sebelum artefak r3 in-commit:

```
python -m pytest msaf/tests/test_figure_eight_r3.py -q
python audit_quantum/freeze.py --verify
python -m pytest msaf/tests -q
```

Guard r3 memeriksa receipt byte-identik, hash modul/prereg/T1/T1b,
K1-K5, path box, M1-M5, no adanya `A-2026-0042`, and verdict
INCONCLUSIVE in report.

Hasil eksekusi final:

- Guard r3: `10 passed in 3378.24s (0:56:18)`.
- Freeze: `verify OK: 14 pins; Codebase/Manifest Digest =
  sha256(PINS.sha256) =
  f6352884d85bab5a68c01a4e1d4a73618304464fd300d56bce1f8cc2f62baa25`.
- Full suite: `650 passed, 1 skipped in 9501.97s (2:38:21)`.
  Bila guard, freeze, or full suite gagal, artefak no boleh
  diklaim final.

## 9. Langkah berikutnya

- **Jika registry `A-2026-0042` diinginkan:** buka trek baru (r4) with
  pra-registrasi baru **sebelum kode**, which mendefinisikan falsifier K6
  which benar-benar diskriminatif. Jangan mengubah M5 secara retrospektif
  and jangan mengamendemen r3.
- **Jika sertifikat matematis K1-K5 cukup:** gunakan report ini sebagai
  note INCONCLUSIVE; jangan menambah registry. Klaim lokal harus
  selalu menyertakan caveat K6/M5.
- R3 ditutup sebagai **INCONCLUSIVE**, bukan FAILED matematis and bukan
  ALL PASS formal.


