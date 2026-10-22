# Pra-registrasi T2-r3 - Orbit figure-eight tervalidasi (three-body, reduced 8x8)

**Status: TERKUNCI SEBELUM KODE.** Dokumen ini di-commit sebelum satu baris
pun kode T2-r3 ditulis. Tidak ada amendemen setelah kode dimulai; bila
ditemukan cacat, jalur baru harus dibuka.

## 0. Garis keturunan dan alasan trek baru

- T1 (`A-2026-0039`) dan T1b (`A-2026-0040`) adalah primitif tervalidasi
  yang **beku**; T2-r3 hanya mengimpor, tidak mengubah.
- T2 (figure-eight, 11-dimensi) ditutup **FAILED** pada commit `1c6a2c8`:
  singularitas translasi-x eksak pada K3; tidak ada registry.
- T2-r2 (reduced 8x8, periode tetap) ditutup **FAILED** pada commit
  `177e274`: K1 dan Newton 8x8 PASS sampai residu
  `4.222845715357847910637323998643523507567862899636295014679650259478241866838e-25`,
  tetapi K2 FAILED karena slack kuadratik beku T1b
  (`KAPPA_NL = 1e18`) pada `R_B = 1e-10`; K3/K4/K5 tidak dievaluasi.
  Registry `A-2026-0041` tidak dibuat.
- T2-r3 adalah **trek baru**, bukan amendemen T2 atau T2-r2. Tujuannya
  sama dengan T2-r2: sertifikasi lokal keberadaan dan keunikan satu orbit
  periodik figure-eight pada periode tetap `T0`, dalam sistem tereduksi
  8x8 setelah translasi/boost dan dua gauge dikunci.
- Titik Newton r2 (`XHAT_R2`, pecahan eksak dari receipt r2) dipakai
  **hanya sebagai seed titik**, bukan sebagai klaim sertifikat r2. T2-r3
  wajib mengevaluasi ulang `G(xh)` dan memenuhi `|G(xh)|_inf <= 1e-24`
  sebelum K2/K3 diterima.

## 1. Sistem, koordinat, dan periode

Tiga massa sama `m = 1`, bidang, Hamiltonian

```
H = 1/2 (|v1|^2 + |v2|^2 + |v3|^2) - 1/|q1-q2| - 1/|q1-q3| - 1/|q2-q3|.
```

Pusat massa dikunci eksak:

```
q1 + q2 + q3 = 0,        v1 + v2 + v3 = 0.
```

Koordinat bebas `x = (q1x,q1y,q2x,q2y,v1x,v1y,v2x,v2y)`. Lift eksak ke
12 dimensi:

```
q3 = -q1 - q2,   v3 = -v1 - v2.
```

Periode tetap:

```
T0 = 632600304 / 10^8 = 6.326003040.
```

Jumlah langkah `H_STEPS = 1536`, langkah eksak `h = T0 / 1536`.

Dua gauge:

```
q1y = 1/5,          I_xy = q1x q1y + q2x q2y + q3x q3y = 0.
```

Return map yang dipakai adalah enam komponen `(q1x, q1y, q2x, q2y, v1x,
v1y)` pada waktu `T0`, ditambah dua gauge. Jadi `G: R^8 -> R^8`:

```
G_i(x) = [proj(Phi_T(x)) - x]_{KEEP_i},  i = 0..5,
G_6(x) = q1y - 1/5,
G_7(x) = I_xy,
KEEP = (0, 1, 3, 4, 5, 6),
```

dengan `Phi_T` adalah flow Hamiltonian penuh yang sudah dilift dan
diproyeksikan. Tidak ada klaim global, stabilitas, spektrum, chaos,
ergodisitas, PDE, RH, fisika, atau prioritas.

## 2. Metode K2 baru: tabung kuadratik lokal, bukan `KAPPA_NL` beku

Kegagalan r2 berasal dari satu angka global `KAPPA_NL = 1e18` yang
memasukkan slack `KAPPA_NL * r^2` pada setiap blok dan umpan-baliknya
meledak. T2-r3 mengganti angka global itu dengan batas **lokal satu
langkah** yang dihitung dengan aritmetika ball eksak dan jet orde dua.

### 2.1 Batas Hessian satu langkah `H_STEP`

Untuk setiap langkah titik `k` di sepanjang lintasan `xh`, bentuk kotak
diagnostik

```
B_k = [mid_k - HESS_BOX, mid_k + HESS_BOX]   (12 komponen),
HESS_BOX = 1e-12.
```

Definisikan, dengan interval ball atas `B_k`:

```
a_k = max_i sum_j |df_i/dy_j|,
b_k = max_i sum_{j,l} |d^2 f_i/(dy_j dy_l)|,
s_k = max_i sum_j |S_ij|,
```

dengan `S = D Phi_t` adalah produk sensitivitas bertanda dari langkah
`J_eff` (bagian 2.3). Batas Hessian satu langkah dihitung dari
pertidaksamaan variasional orde dua (reset `H = 0` di awal setiap langkah):

```
H_STEP_k = (b_k s_k^2 / a_k) * exp(a_k h) * (exp(a_k h) - 1).
```

`a_k`, `b_k`, dan turunan parsial dihitung dengan kelas jet orde dua
`Dual2` baru di modul r3; bukan `float`, bukan finite difference, bukan
`KAPPA_NL`. `H_STEP_MAX = max_k H_STEP_k`, lalu

```
QUAD_STEP = 4 * H_STEP_MAX * HESS_BOX^2,
QUAD_CAP  = 1e-18.
```

Faktor 4 adalah margin konservatif untuk perbedaan `s_k` titik versus
kotak; tidak ada penyesuaian setelah hasil campaign.

### 2.2 Batas turunan sisa Taylor `DR_MAX`

Sisa Taylor satu langkah adalah `R_k = tail_k * h^(ORDER+1)`. Turunannya
terhadap state awal dibatasi dengan jet orde satu dari koefisien
`ORDER+1`:

```
box_k = [mid_k - HESS_BOX, mid_k + HESS_BOX],
Dtail_k = max_{i,j} |d tail_i / dy_j|   (interval AD atas box_k),
L_f,k = max_i sum_j |df_i/dy_j|         (interval AD atas box_k),
Lambda_k = 2 * exp(h * L_f,k),
DR_k = 2 * Lambda_k * Dtail_k * h^(ORDER+1),
DR_MAX = max_k DR_k,
DR_CAP = 1e-18.
```

`DR_MAX` dimasukkan sebagai pelebaran seragam pada setiap entri Jacobian
langkah:

```
J_eff,k[i,j] = J_taylor,k[i,j] + [-DR_MAX, +DR_MAX].
```

Dengan demikian `J_eff` adalah enclosure turunan **peta langkah penuh**
(polinomial Taylor plus sisa), bukan hanya turunan polinomial. Ini juga
menutup celah pertama pada certificate T1b yang hanya memakai turunan
polinomial.

### 2.3 Pass kotak dan certificate K2

Input box delapan koordinat:

```
B = B(xh, R_B),   R_B = 1e-18,   K_MARGIN = 9/10.
```

Lift radius dependen secara eksak (`q3 = -q1 - q2`, `v3 = -v1 - v2`).
Pada setiap langkah:

```
m_{k+1}, J_k, rem_k = t1b.forward_step(...),
J_eff,k = J_k + [-DR_MAX, +DR_MAX],
c_{k+1} = |J_eff,k| c_k + rem_k + QUAD_STEP + EPS_SLACK.
```

Pada setiap checkpoint blok (96 langkah):

```
c_out, weights = t1b.certificate(
    jacs_eff, rems, [QUAD_STEP] * steps, c_in, upto, lo, 12),
width = 2 * max_i c_out_i.
```

`QUAD_STEP` konstan per langkah; tidak ada umpan-balik `KAPPA_NL`.
K2 PASS jika dan hanya jika:

1. tidak ada `ValidationError`/Picard failure/arithmetic error;
2. `QUAD_STEP <= QUAD_CAP`;
3. `DR_MAX <= DR_CAP`;
4. setiap `width` checkpoint `<= TUBE_CAP = 1e-10`;
5. `HESS_BOX` (1e-12) tetap menjadi batas atas radius tabung yang
   disertifikasi; bila ada `width/2 > HESS_BOX`, K2 FAILED karena batas
   Hessian tidak lagi berlaku.

K2 adalah tabung state tervalidasi untuk semua `x` di `B`. Tidak ada klaim
tabung global di luar `B`.

## 3. K3: Krawczyk pada `G` terreduksi

- `G(xh)` dan `DG(xh)` dari pass titik `c = 0`; `G` adalah enclosure
  interval, bukan nilai float.
- `W = invers midpoint dari DG(xh)`; bila singular, K3 FAILED.
- `DG(B)` dari pass kotak 8x8 dengan `J_eff` dan gauge interval pada
  `xh +/- R_B`.
- Krawczyk:

```
K(B) = xh - W G(xh) + (I - W DG(B)) (B - xh).
```

K3 PASS jika dan hanya jika:

1. `|G(xh)|_inf <= 1e-24`;
2. `kappa_inf = ||I - W DG(B)||_inf <= KAPPA_MAX = 1/2`;
3. untuk setiap baris `i`,
   `|(W G(xh))_i| + kappa_i * R_B <= K_MARGIN * R_B`,
   dengan `kappa_i = sum_j |I - W DG(B)|_{ij}`.

Bila ketiga syarat lulus, Krawczyk memberi keberadaan dan **keunikan
lokal** satu nol `G` di `B`. Karena `W` invertible, nol `G` adalah orbit
periodik dengan periode tetap `T0` dan gauge terkunci. Tidak ada klaim
keunikan global atau orbit lain di luar `B`.

## 4. K1, K4, K5, K6

### K1 - integritas dan bahasa
- AST scan modul r3: tidak ada literal float, `float(...)`, `math`,
  `numpy`, `scipy`, `random`, `time`, atau import terlarang.
- Hash SHA-256LF pra-registrasi ini harus sama dengan pin `PREREG_SHA` di
  modul r3.
- Hash modul T1 dan T1b harus sama dengan pin r2/T1b:
  `T1 = c1d9b5d60036a5f0772f7e3f1b8c78969efaa7146a713c762531ddce346251b9`,
  `T1B = 42d196a51c5ae45e3b87b8c1e36319abfeb93df776b3c2317e812f7c2c0b5b97`.

### K4 - determinan/kondisi Gauss
- `DG(xh)` tidak memuat nol pada determinan interval;
- `|det|_lower >= 1e-6`;
- `cond_inf = ||W||_inf * ||DG(B)||_inf <= 1e6`.
Tidak ada klaim spektrum, stabilitas, atau eigenvalue orbit.

### K5 - deskriptor koreografi
Enam relasi fase-independent pada grid `T0/3 = 512h` dan
`2T0/3 = 1024h`:

```
q1(T/3)=q2(0), q2(T/3)=q3(0), q3(T/3)=q1(0),
q1(2T/3)=q3(0), q2(2T/3)=q1(0), q3(2T/3)=q2(0).
```

Defect dihitung dari lintasan titik `xh` ditambah radius tabung konservatif
`C_TUBE` (maksimum radius berjalan/checkpoint K2); toleransi
`CHOREO_TOL = 1e-6`. K5 hanya deskriptor koreografi di dalam tabung; bukan
klaim stabilitas atau klasifikasi global.

### K6 - mutasi
- **M1:** `REMAINDER_FACTOR = 1e70` harus menghasilkan FAILED, bukan PASS.
- **M2:** `T0 -> T0 + 1/10` (dan `H_GRID` menyesuaikan) harus menghasilkan
  K3 FAILED, bukan PASS.
- **M3:** satu byte receipt yang diubah harus terdeteksi oleh guard
  hash/payload.
- **M4:** injeksi literal float atau `float(...)` ke sumber harus
  menghasilkan AST hit.
- **M5:** `SWEEP_SIGNED = False` (reset produk sensitivitas per blok)
  harus menghasilkan K2/K3 FAILED, bukan PASS.
Efek aktual setiap mutasi dicatat apa adanya di receipt; bila mutasi tidak
diskriminatif, K6 tidak boleh diklaim PASS.

## 5. Konstanta dan gerbang yang dikunci

| Nama | Nilai |
|---|---|
| `T0` | `632600304 / 10^8` |
| `H_STEPS` | `1536` |
| `BLOCK_STEPS` | `96` |
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
| `REMAINDER_FACTOR` | `1` (M1: `1e70`) |
| `SWEEP_SIGNED` | `True` (M5: `False`) |

Tidak ada konstanta yang boleh diubah setelah campaign pertama. Bila
`QUAD_STEP`, `DR_MAX`, atau lebar tabung melewati gerbang, verdict adalah
FAILED/INCONCLUSIVE yang jujur, bukan penyesuaian ambang.

## 6. Artefak dan registry

Artefak trek r3:

- `reports/PREREG_FIGURE_EIGHT_R3_2026-10-23.md` (dokumen ini, di-commit
  lebih dulu);
- `msaf/figure_eight_r3.py`;
- `msaf/tests/test_figure_eight_r3.py`;
- `reports/figure_eight_r3_2026-10-23.json`;
- `reports/FIGURE_EIGHT_R3_2026-10-23.md`.

Registry `A-2026-0042` **hanya** dibuat bila K1-K6 semuanya PASS dan
`freeze.py --verify` lulus tanpa mengubah pin beku. Bila FAILED/
INCONCLUSIVE, tidak ada registry dan `FENCE_REGISTRY.md` tidak diubah.
`A-2026-0041` tetap tidak dibuat (guard r2 menguncinya).

## 7. Batas klaim

T2-r3 hanya mengklaim:

- keberadaan satu orbit periodik figure-eight di dalam box `B` pada
  periode tetap `T0`;
- keunikan lokal orbit itu di dalam `B`, modulo gauge yang dikunci;
- deskriptor koreografi di dalam tabung yang disertifikasi.

Tidak ada klaim: keunikan global, orbit lain di luar `B`, stabilitas
linear/nonlinear, spektrum, chaos, ergodisitas, KAM, PDE, RH, fisika,
prioritas, Lean/Coq, atau penyelesaian masalah three-body secara umum.

## 8. Diagnostik pra-registrasi (bukan sertifikat)

Sebelum dokumen ini, hanya probe di direktori temp yang dijalankan; tidak
ada kode r3 di repo. Probe memakai modul r2 yang sudah gagal sebagai
sumber titik dan rutin bantu, bukan sebagai klaim.

- Probe `R_B = 1e-20` dan `1e-21` dengan `KAPPA_NL = 1e18` tetap gagal K2
  (`2.58e-7` pada langkah 288 dan `6.89e6` pada langkah 480); ini
  mengonfirmasi bahwa memperkecil `R_B` saja tidak cukup.
- Probe jet orde dua di `xh`, `HESS_BOX = 1e-12`:
  `max_a ~ 15.7289575`, `max_b ~ 203.562315`, `max_s ~ 130.362484`,
  `max_H_STEP ~ 12695.9001`, `max_QUAD ~ 1.269590e-20`,
  `max_DR ~ 7.566834e-51`, `max_gradtail ~ 7.61241972e8`.
- Probe kotak dengan slack pengganti kecil pada `R_B = 1e-18`:
  lebar K2 maksimum `~3.141357719e-16`; K4 `det ~ -7.62`,
  `cond ~ 29649.6`; K5 defect `~2.10937857e-16`; collision lower bound
  `~0.68081344`. K3 probe itu memakai `G` kotak, bukan `G(xh)`, sehingga
  angka K3-nya **tidak valid** dan tidak akan dipakai.
- Probe ini hanya menetapkan skala; angka final harus berasal dari
  campaign r3 tersertifikasi dan receipt.

## 9. Determinisme dan integritas

- Semua perhitungan tersertifikasi memakai `arb`/`Fraction`/`arb_mat`
  dengan presisi T1 (`PREC = 256`).
- Tidak ada float, waktu, random, atau input eksternal di jalur
  tersertifikasi.
- Dua campaign penuh harus menghasilkan receipt byte-identik (LF) sebelum
  verdict dirilis.
- Modul T1/T1b, `ci.yml`, pin freeze, dan artefak r2/T2 tidak diubah.
- Bila implementasi menemukan bug, bug harus dilaporkan dan diperbaiki
  hanya bila tidak mengubah kriteria/konstanta yang dikunci; bila
  perbaikan mengubah metode, jalur baru harus dibuka.

**Kriteria verdict:** `ALL PASS` hanya bila K1, K2, K3, K4, K5, dan K6
semuanya PASS. `INCONCLUSIVE` bila K3 PASS tetapi K4/K5/K6 tidak. `FAILED`
bila K1/K2/K3 gagal. Hanya `ALL PASS` yang boleh menambah registry.
