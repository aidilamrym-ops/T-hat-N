# Batas tail diagonal `XC`: `|XC(n)| < 1/n²` dan `epsilon_XC(N) -> 0`

**Tanggal:** 2026-10-26.
**Status:** P2 selesai untuk klaim diagonal `XC` yang dikunci.
**Pra-registrasi:** `reports/PREREG_ANALYTIC_TAIL_2026-10-26.md`
(commit `fc33084`, sebelum kode P2; amendment tanggal 2026-10-26 ada di §9
dokumen itu).
**Basis kode:** `b7b5f2e` (P1).
**Bukan:** bukti RH, bukti Weil positivity, bukti spektrum zeta, bukti
positif-definit matriks, atau kontrol tail seluruh matriks Guinand–Weil.

## 1. Klaim yang dibuktikan

Untuk `c = 13`, `L = log 13`, dan `n ≥ 1`:

```text
|XC(n)| < 1/n²
epsilon_XC(N) := (4/L) * sum_{n>N} |XC(n)| < 2/N
Tendsto epsilon_XC atTop (nhds 0)
```

dengan `XC` didefinisikan oleh implementasi eksternal
`source_arb_ldlt_certify.py`:

```text
c_k = 2k + 1/2
w   = 2*pi*n/L
gX1(n) = sum_{k>=0} exp(-c_k L) * c_k / (c_k² + w²)
gX2(n) = sum_{k>=0} exp(-c_k L) * (c_k² - w²) / (c_k² + w²)²
XC(n)  = (1/4) Re psi'(1/4 + i*pi*n/L) - L*gX1(n) - gX2(n)
```

`epsilon_XC` hanya menjumlahkan kontribusi diagonal `-(2/L) XC(n)` untuk
`n > N` dan `-n < -N`. Ia **bukan** tail penuh matriks: `S(n)`, `Wp`, `W02`,
dan entri off-diagonal tidak termasuk.

## 2. Representasi integral trigamma

DLMF 5.15.1 memberi, untuk `Re z > 0`,

```text
psi'(z) = integral_0^inf t * exp(-z t) / (1 - exp(-t)) dt.
```

Dengan `z = 1/4 + i y`, `y = pi*n/L`, bagian realnya adalah

```text
Re psi'(1/4 + i y) = integral_0^inf h(t) cos(y t) dt,
h(t) = t * exp(-t/4) / (1 - exp(-t)),  t >= 0.
```

Fungsi `h` kontinu di `0` (nilai `1`), dan turun eksponensial saat
`t -> inf`, begitu pula `h'`. Karena itu dua integrasi parsial berikut sah
(semua suku batas di `0` dan `inf` hilang atau dihitung eksplisit):

```text
integral h cos(y t) dt
  = -(1/y) integral h' sin(y t) dt
  = -h'(0)/y² - (1/y²) integral h'' cos(y t) dt.
```

Jadi

```text
|Re psi'(1/4 + i y)| <= Cpsi / y²,
Cpsi := h'(0) + integral_0^inf |h''(t)| dt.
```

Karena `w = 2y`,

```text
|(1/4) Re psi'(1/4 + i y)| <= Cpsi / w².
```

## 3. Konstanta `Cpsi <= 47/12`

Tulis `u(t) = t/(1 - exp(-t))`, sehingga `h(t) = u(t) exp(-t/4)` dan

```text
h'(0) = u'(0) - u(0)/4 = 1/2 - 1/4 = 1/4,
h''(t) = exp(-t/4) * (u''(t) - u'(t)/2 + u(t)/16).
```

Estimasi elementer untuk `u`:

1. `u(t) <= 1 + t`. Karena `exp(t) >= 1 + t`, maka
   `1 - exp(-t) >= t/(1+t)`, sehingga `u(t) <= 1+t`.
2. `0 <= u'(t) <= 1`. Turunannya
   `u' = (1 - (1+t)exp(-t))/(1-exp(-t))²`; pembilang nonnegatif dari
   `exp(t) >= 1+t`, dan `u' <= 1` ekuivalen dengan `t + exp(-t) >= 1`, yang
   benar karena sisi kiri naik dari `1` di `t=0`.
3. `0 <= u''(t) <= 1/6`. Dengan `x = t/2`, `u = x + x*coth(x)`, sehingga

   ```text
   u'' = (x*cosh(x) - sinh(x)) / (2*sinh(x)³).
   ```

   Pembilangnya adalah
   `sum_{n>=1} 2n*x^(2n+1)/(2n+1)! >= 0`. Untuk batas atas, gunakan
   `sinh(x)³ = (sinh(3x) - 3*sinh(x))/4`; perbandingan koefisien deret
   memberi

   ```text
   3*(x*cosh(x) - sinh(x))
     = sum_{n>=1} 6n*x^(2n+1)/(2n+1)!
   sinh(x)³
     = sum_{n>=1} (3^(2n+1)-3)/4 * x^(2n+1)/(2n+1)!.
   ```

   Koefisien `6n <= (3^(2n+1)-3)/4` ekuivalen dengan
   `24n <= 3^(2n+1)-3`, yang benar untuk semua `n>=1` (sama besar di
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

Lemma kalkulus ini adalah bukti kertas; ia **tidak** diformalkan di Lean.
Yang diformalkan di Lean hanyalah langkah tail finit dan limit di §7.

## 4. Suku geometrik `Q0` dan `Q1`

Dengan `r = exp(-2L) = 1/169` dan `exp(-L/2) = 1/sqrt(13)`:

```text
Q0 = sum_{k>=0} exp(-c_k L)
   = exp(-L/2)/(1-r)
   = 169/(168*sqrt(13)),

Q1 = sum_{k>=0} c_k exp(-c_k L)
   = exp(-L/2) * (2r/(1-r)² + 1/(2(1-r)))
   = 7267/(14112*sqrt(13)).
```

Batas `sqrt(13) > 3.605` diverifikasi dengan mengkuadratkan:
`3.605² = 12.996025 < 13`. Karena itu

```text
Q0 < 169/(168*3.605) < 0.28,
Q1 < 7267/(14112*3.605) < 0.143.
```

Untuk setiap `n`:

```text
|gX1(n)| <= Q1/w²,   |gX2(n)| <= Q0/w²,
```

karena `c_k² + w² >= w²` dan `|c_k² - w²| <= c_k² + w²`.

## 5. Batas pointwise `|XC(n)| < 1/n²`

Gabungkan §2–§4:

```text
|XC(n)| <= (Cpsi + Q0 + L*Q1)/w²
        < (4 + 0.28 + 2.6*0.143)/w².
```

Dengan `w² = 4*pi²*n²/L²` dan `L < 2.6`, `pi > 3`:

```text
L²/(4*pi²) < 6.76/36 < 1/5,
1/w² < (1/5)/n².
```

Maka

```text
|XC(n)| < (1/5)*(4 + 0.28 + 2.6*0.143)/n²
        = (23259/25000)/n²
        = 0.93036/n²
        < 1/n².
```

Tidak ada eksponen yang di-fit; `0.93036` adalah aritmetika rasional dari
batas-batas yang dikunci sebelum pengukuran.

## 6. Tail dan limit

Untuk `N >= 1`,

```text
sum_{n>N} 1/n² < sum_{n>N} 1/(n(n-1)) = 1/N.
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

File: `lean/Stage_6_Analytic_Tail.lean`. Empat deklarasi yang diperiksa
kernel:

| Deklarasi | Isi |
|---|---|
| `sum_Ico_one_div_sq_le` | `∑_{n=N+1}^{M} 1/n² ≤ 1/N` untuk `1 ≤ N` |
| `sum_Ico_abs_le_of_pointwise` | batas pointwise `|x n| ≤ 1/n²` lewat ke jumlah tail finit |
| `epsilon_le_of_pointwise` | perkalian dengan `4/L` (dengan `0 < L`) mempertahankan batas |
| `tendsto_epsilon_majorant` | `(4/L)/N → 0` saat `N → ∞` |

Bentuk Lean memakai `Finset.Ico (N + 1) (M + 1)`; himpunan ini sama dengan
`{N+1, ..., M}`. Alasannya: Mathlib v4.33.1 tidak menyediakan
`Finset.sum_Icc_eq_sum_range`. Amendment §9 di pra-registrasi mencatat
perubahan nama ini.

### 7.1 Kernel check

```text
cd lean; lake build
...
✔ [8720/8721] Built Stage_6_Analytic_Tail (41s)
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

Tidak ada `sorryAx`, tidak ada aksioma proyek.

**Batas penting:** Lean **tidak** memformalkan representasi integral
trigamma, fungsi `psi'`, atau deret `gX1`/`gX2`. Batas pointwise
`|XC(n)| < 1/n²` adalah input analitik dari §2–§5 plus grid Arb di §8.
Lean hanya memformalkan langkah tail finit dan limit mayoran.

## 8. Grid Arb dan record

Builder: `msaf/analytic_tail_bound.py`.
Record: `reports/analytic_tail_bound_c13.json`.

```text
c            = 13
n_check      = 4096
prec_bits    = 512
max n²|XC(n)|= 0.066182476504849187296396389939538378949125278042115325783127886359808924952477117
n_at_max     = 1
A_upper      = 23259/25000 = 0.93036
verdict      = PASS
digest       = bd9378d9249372bfc08e39063b5a42c182e7d31d9f8818ff48b98227a91ab857
```

Semua `n = 1..4096` memenuhi `n²|XC(n)| < 1` dengan batas atas ball Arb.
Ini adalah verifikasi implementasi pada grid, **bukan** bukti analitik;
bukti analitik untuk semua `n ≥ 1` ada di §2–§6.

Perintah cepat:

```text
python -m msaf.analytic_tail_bound --check
PASS analytic XC tail: max n^2|XC(n)|=0.0661824765... (n=1) < 1; A_upper=0.93036 < 1
```

## 9. Yang tidak diklaim

- Tidak ada klaim RH, Weil positivity, lokasi nol zeta, atau `sigma = 1/2`.
- Tidak ada klaim bahwa Lean membuktikan representasi integral trigamma,
  `psi'`, atau deret `gX1`/`gX2`.
- Tidak ada kontrol tail untuk `S(n)`, `Wp`, `W02`, entri off-diagonal, atau
  seluruh matriks Guinand–Weil. `S(n) -> pi/4` untuk `n` besar, sehingga tail
  off-diagonal memerlukan analisis terpisah.
- Tidak ada klaim bahwa `epsilon_XC(N)` lebih kecil dari `lambda_min(N)`;
  perbandingan itu tidak dibuktikan di sini.
- `|XC(n)| < 1/n²` adalah bound diagonal, bukan bound operator.

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

Gate dijalankan 2026-10-26 dan memberi `PASS` dengan
`FAIL=0 NOT_RUN=0 SKIP=0`. Anti-circularity gate adalah pemindaian
placeholder/klaim, bukan bukti kebenaran teorema.
