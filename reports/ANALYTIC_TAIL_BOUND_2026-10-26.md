# Batas tail diagonal `XC`: `|XC(n)| < 1/nÂ²` and `epsilon_XC(N) -> 0`

**Tanggal:** 2026-10-26.
**Status:** P2 selesai for klaim diagonal `XC` which dikunci.
**Pra-registrasi:** `reports/PREREG_ANALYTIC_TAIL_2026-10-26.md`
(commit `fc33084`, sebelum kode P2; amendment tanggal 2026-10-26 ada in Â§9
dokumen itu).
**Basis kode:** `b7b5f2e` (P1).
**Bukan:** bukti RH, bukti Weil positivity, bukti spektrum zeta, bukti
positif-definit matriks, or kontrol tail seluruh matriks Guinandâ€“Weil.

## 1. Klaim which dibuktikan

Untuk `c = 13`, `L = log 13`, and `n â‰¥ 1`:

```text
|XC(n)| < 1/nÂ²
epsilon_XC(N) := (4/L) * sum_{n>N} |XC(n)| < 2/N
Tendsto epsilon_XC atTop (nhds 0)
```

with `XC` didefinisikan oleh implementasi eksternal
`source_arb_ldlt_certify.py`:

```text
c_k = 2k + 1/2
w   = 2*pi*n/L
gX1(n) = sum_{k>=0} exp(-c_k L) * c_k / (c_kÂ² + wÂ²)
gX2(n) = sum_{k>=0} exp(-c_k L) * (c_kÂ² - wÂ²) / (c_kÂ² + wÂ²)Â²
XC(n)  = (1/4) Re psi'(1/4 + i*pi*n/L) - L*gX1(n) - gX2(n)
```

`epsilon_XC` hanya menjumlahkan kontribusi diagonal `-(2/L) XC(n)` for
`n > N` and `-n < -N`. Ia **bukan** tail penuh matriks: `S(n)`, `Wp`, `W02`,
and entri off-diagonal no termasuk.

## 2. Representasi integral trigamma

DLMF 5.15.1 memberi, for `Re z > 0`,

```text
psi'(z) = integral_0^inf t * exp(-z t) / (1 - exp(-t)) dt.
```

Dengan `z = 1/4 + i y`, `y = pi*n/L`, section realnya adalah

```text
Re psi'(1/4 + i y) = integral_0^inf h(t) cos(y t) dt,
h(t) = t * exp(-t/4) / (1 - exp(-t)),  t >= 0.
```

Fungsi `h` kontinu in `0` (nilai `1`), and turun eksponensial saat
`t -> inf`, begitu pula `h'`. Karena itu dua integrasi parsial berikut sah
(semua suku limit in `0` and `inf` hilang or dihitung eksplisit):

```text
integral h cos(y t) dt
  = -(1/y) integral h' sin(y t) dt
  = -h'(0)/yÂ² - (1/yÂ²) integral h'' cos(y t) dt.
```

Jadi

```text
|Re psi'(1/4 + i y)| <= Cpsi / yÂ²,
Cpsi := h'(0) + integral_0^inf |h''(t)| dt.
```

Karena `w = 2y`,

```text
|(1/4) Re psi'(1/4 + i y)| <= Cpsi / wÂ².
```

## 3. Konstanta `Cpsi <= 47/12`

Tulis `u(t) = t/(1 - exp(-t))`, sehingga `h(t) = u(t) exp(-t/4)` and

```text
h'(0) = u'(0) - u(0)/4 = 1/2 - 1/4 = 1/4,
h''(t) = exp(-t/4) * (u''(t) - u'(t)/2 + u(t)/16).
```

Estimasi elementer for `u`:

1. `u(t) <= 1 + t`. Karena `exp(t) >= 1 + t`, maka
   `1 - exp(-t) >= t/(1+t)`, sehingga `u(t) <= 1+t`.
2. `0 <= u'(t) <= 1`. Turunannya
   `u' = (1 - (1+t)exp(-t))/(1-exp(-t))Â²`; pembilang nonnegatif dari
   `exp(t) >= 1+t`, and `u' <= 1` ekuivalen with `t + exp(-t) >= 1`, which
   benar karena sisi kiri naik dari `1` in `t=0`.
3. `0 <= u''(t) <= 1/6`. Dengan `x = t/2`, `u = x + x*coth(x)`, sehingga

   ```text
   u'' = (x*cosh(x) - sinh(x)) / (2*sinh(x)Â³).
   ```

   Pembilangnya adalah
   `sum_{n>=1} 2n*x^(2n+1)/(2n+1)! >= 0`. Untuk limit atas, gunakan
   `sinh(x)Â³ = (sinh(3x) - 3*sinh(x))/4`; perbandingan koefisien deret
   memberi

   ```text
   3*(x*cosh(x) - sinh(x))
     = sum_{n>=1} 6n*x^(2n+1)/(2n+1)!
   sinh(x)Â³
     = sum_{n>=1} (3^(2n+1)-3)/4 * x^(2n+1)/(2n+1)!.
   ```

   Koefisien `6n <= (3^(2n+1)-3)/4` ekuivalen with
   `24n <= 3^(2n+1)-3`, which benar for semua `n>=1` (sama besar in
   `n=1`, lalu tumbuh jauh lebih cepat). Jadi `u'' <= 1/6`.

Dari ketiga estimasi:

```text
u'' - u'/2 + u/16 <= 1/6 + (1+t)/16 = 11/48 + t/16 <= 2/3 + t/16,
u'' - u'/2 + u/16 >= -u'/2 >= -1/2 >= -(2/3 + t/16),
```

karena `2/3 + t/16 >= 2/3 > 1/2`. Maka

```text
|h''(t)| <= exp(-t/4) * (2/3 + t/16),
integral_0^inf |h''| dt
  <= (2/3)*4 + (1/16)*16 = 8/3 + 1 = 11/3.
```

Karena itu

```text
Cpsi <= 1/4 + 11/3 = 47/12 < 4.
```

Lemma kalkulus ini adalah bukti kertas; ia **no** diformalkan in Lean.
Yang diformalkan in Lean hanyalah step tail finit and limit in Â§7.

## 4. Suku geometrik `Q0` and `Q1`

Dengan `r = exp(-2L) = 1/169` and `exp(-L/2) = 1/sqrt(13)`:

```text
Q0 = sum_{k>=0} exp(-c_k L)
   = exp(-L/2)/(1-r)
   = 169/(168*sqrt(13)),

Q1 = sum_{k>=0} c_k exp(-c_k L)
   = exp(-L/2) * (2r/(1-r)Â² + 1/(2(1-r)))
   = 7267/(14112*sqrt(13)).
```

Batas `sqrt(13) > 3.605` diverifikasi with mengkuadratkan:
`3.605Â² = 12.996025 < 13`. Karena itu

```text
Q0 < 169/(168*3.605) < 0.28,
Q1 < 7267/(14112*3.605) < 0.143.
```

Untuk setiap `n`:

```text
|gX1(n)| <= Q1/wÂ²,   |gX2(n)| <= Q0/wÂ²,
```

karena `c_kÂ² + wÂ² >= wÂ²` and `|c_kÂ² - wÂ²| <= c_kÂ² + wÂ²`.

## 5. Batas pointwise `|XC(n)| < 1/nÂ²`

Gabungkan Â§2â€“Â§4:

```text
|XC(n)| <= (Cpsi + Q0 + L*Q1)/wÂ²
        < (4 + 0.28 + 2.6*0.143)/wÂ².
```

Dengan `wÂ² = 4*piÂ²*nÂ²/LÂ²` and `L < 2.6`, `pi > 3`:

```text
LÂ²/(4*piÂ²) < 6.76/36 < 1/5,
1/wÂ² < (1/5)/nÂ².
```

Maka

```text
|XC(n)| < (1/5)*(4 + 0.28 + 2.6*0.143)/nÂ²
        = (23259/25000)/nÂ²
        = 0.93036/nÂ²
        < 1/nÂ².
```

Tidak ada eksponen which in-fit; `0.93036` adalah aritmetika rasional dari
limit-limit which dikunci sebelum pengukuran.

## 6. Tail and limit

Untuk `N >= 1`,

```text
sum_{n>N} 1/nÂ² < sum_{n>N} 1/(n(n-1)) = 1/N.
```

Karena itu

```text
epsilon_XC(N) = (4/L) * sum_{n>N} |XC(n)|
             < (4/L) * (1/N)
             = 4/(L*N)
             < 2/N,
```

karena `L = log 13 > 2` (dari `exp(2) < 9 < 13`). Jadi
`epsilon_XC(N) -> 0`.

## 7. Artefak Lean `Stage_6_Analytic_Tail.lean`

File: `lean/Stage_6_Analytic_Tail.lean`. Empat deklarasi which diperiksa
kernel:

| Deklarasi | Isi |
|---|---|
| `sum_Ico_one_div_sq_le` | `âˆ‘_{n=N+1}^{M} 1/nÂ² â‰¤ 1/N` for `1 â‰¤ N` |
| `sum_Ico_abs_le_of_pointwise` | limit pointwise `|x n| â‰¤ 1/nÂ²` lewat ke jumlah tail finit |
| `epsilon_le_of_pointwise` | perkalian with `4/L` (with `0 < L`) mempertahankan limit |
| `tendsto_epsilon_majorant` | `(4/L)/N â†’ 0` saat `N â†’ âˆž` |

Bentuk Lean memakai `Finset.Ico (N + 1) (M + 1)`; himpunan ini sama with
`{N+1, ..., M}`. Alasannya: Mathlib v4.33.1 no menyediakan
`Finset.sum_Icc_eq_sum_range`. Amendment Â§9 in pra-registrasi mencatat
perubahan nama ini.

### 7.1 Kernel check

```text
cd lean; lake build
...
âœ” [8720/8721] Built Stage_6_Analytic_Tail (41s)
Build completed successfully (8721 jobs).
```

```text
cd lean; lake env lean Stage_6_Analytic_Tail.lean
(exit 0, no output)
```

### 7.2 Axiom audit

```text
#print axioms sum_Ico_one_div_sq_le
#print axioms sum_Ico_abs_le_of_pointwise
#print axioms epsilon_le_of_pointwise
#print axioms tendsto_epsilon_majorant
```

output:

```text
'sum_Ico_one_div_sq_le' depends on axioms: [propext, Classical.choice, Quot.sound]
'sum_Ico_abs_le_of_pointwise' depends on axioms: [propext, Classical.choice, Quot.sound]
'epsilon_le_of_pointwise' depends on axioms: [propext, Classical.choice, Quot.sound]
'tendsto_epsilon_majorant' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Tidak ada `sorryAx`, no ada aksioma proyek.

**Batas penting:** Lean **no** memformalkan representasi integral
trigamma, fungsi `psi'`, or deret `gX1`/`gX2`. Batas pointwise
`|XC(n)| < 1/nÂ²` adalah input analitik dari Â§2â€“Â§5 plus grid Arb in Â§8.
Lean hanya memformalkan step tail finit and limit mayoran.

## 8. Grid Arb and record

Builder: `msaf/analytic_tail_bound.py`.
Record: `reports/analytic_tail_bound_c13.json`.

```text
c            = 13
n_check      = 4096
prec_bits    = 512
max nÂ²|XC(n)|= 0.066182476504849187296396389939538378949125278042115325783127886359808924952477117
n_at_max     = 1
A_upper      = 23259/25000 = 0.93036
verdict      = PASS
digest       = bd9378d9249372bfc08e39063b5a42c182e7d31d9f8818ff48b98227a91ab857
```

Semua `n = 1..4096` memenuhi `nÂ²|XC(n)| < 1` with limit atas ball Arb.
Ini adalah verifikasi implementasi on grid, **bukan** bukti analitik;
bukti analitik for semua `n â‰¥ 1` ada in Â§2â€“Â§6.

Perintah cepat:

```text
python -m msaf.analytic_tail_bound --check
PASS analytic XC tail: max n^2|XC(n)|=0.0661824765... (n=1) < 1; A_upper=0.93036 < 1
```

## 9. Yang no diklaim

- Tidak ada klaim RH, Weil positivity, lokasi nol zeta, or `sigma = 1/2`.
- Tidak ada klaim bahwa Lean membuktikan representasi integral trigamma,
  `psi'`, or deret `gX1`/`gX2`.
- Tidak ada kontrol tail for `S(n)`, `Wp`, `W02`, entri off-diagonal, or
  seluruh matriks Guinandâ€“Weil. `S(n) -> pi/4` for `n` besar, sehingga tail
  off-diagonal memerlukan analisis terpisah.
- Tidak ada klaim bahwa `epsilon_XC(N)` lebih kecil dari `lambda_min(N)`;
  perbandingan itu no dibuktikan in sini.
- `|XC(n)| < 1/nÂ²` adalah bound diagonal, bukan bound operator.

## 10. Perintah verifikasi

```text
python -m msaf.analytic_tail_bound --check
python -m pytest msaf/tests/test_analytic_tail_bound.py -q
python -m pytest msaf/tests/test_fence_registry.py -q
python -m pytest msaf/tests/test_lean_axiom_audit.py -q
cd lean; lake build
cd lean; lake env lean Stage_6_Analytic_Tail.lean
python C:/Users/usER/.config/opencode/skills/anti-circularity/scripts/gate.py \
  check lean/Stage_2_Tail_Bound.lean lean/Stage_3_Eigenvalue_Locking.lean \
  reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof.lean \
  lean/Stage_5_EntryError_Perturbation.lean lean/Stage_6_Analytic_Tail.lean
```

Gate dijalankan 2026-10-26 and memberi `PASS` with
`FAIL=0 NOT_RUN=0 SKIP=0`. Anti-circularity gate adalah pemindaian
placeholder/klaim, bukan bukti kebenaran teorema.


