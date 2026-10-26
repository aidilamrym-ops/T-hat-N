# Pra-registrasi: batas tail analitik `|XC(n)| < 1/n^2` dan `epsilon_XC(N) -> 0`

**Status:** PRE-REG, dikunci sebelum kode P2.
**Tanggal:** 2026-10-26.
**Basis commit:** `b7b5f2e` (P1).
**Bidang:** Guinand–Weil Stage 2, diagonal archimedean `XC` only.
**Bukan:** bukti RH, bukti Weil positivity, bukti spektrum zeta, bukti
positif-definit matriks, atau kontrol error seluruh matriks.

## 1. Pertanyaan yang dijawab

Implementasi eksternal
`source_arb_ldlt_certify.py` mendefinisikan, untuk `c > 1`, `L = log c`,
`w = 2*pi*n/L`, `c_k = 2k + 1/2`,

```text
gX1(n) = sum_{k>=0} exp(-c_k L) * c_k / (c_k^2 + w^2)
gX2(n) = sum_{k>=0} exp(-c_k L) * (c_k^2 - w^2) / (c_k^2 + w^2)^2
XC(n)  = (1/4) Re psi'(1/4 + i*pi*n/L) - L*gX1(n) - gX2(n)
```

P2 menjawab satu pertanyaan saja: dapatkah `|XC(n)|` dibatasi oleh `1/n^2`
untuk `c = 13` dan semua `n >= 1`, dengan konstanta yang diturunkan secara
analitik (bukan dicocokkan dari data)?

Klaim yang dikunci:

```text
(c = 13, L = log 13)
forall n >= 1:  |XC(n)| < 1/n^2
epsilon_XC(N) := (4/L) * sum_{n=N+1}^inf |XC(n)|  <  2/N
Tendsto epsilon_XC atTop (nhds 0)
```

`epsilon_XC` hanya menjumlahkan kontribusi diagonal `-(2/L) XC(n)` untuk
`n > N` dan `-n < -N`. Ia **bukan** tail penuh matriks: `S(n)`, `Wp`, `W02`,
dan entri off-diagonal tidak termasuk.

## 2. Konstanta dan ketaksamaan yang dikunci

Semua batas berikut dipilih **sebelum** pengukuran P2 dan tidak boleh
dinaikkan setelah melihat hasil.

```text
L = log 13 < 2.6
pi > 3
h(t) = t * exp(-t/4) / (1 - exp(-t)),  t >= 0
Cpsi = h'(0) + integral_0^inf |h''(t)| dt <= 47/12 < 4
Q0 = sum_{k>=0} exp(-c_k L) < 169/(168*3.605) < 0.28
Q1 = sum_{k>=0} c_k exp(-c_k L) < 7267/(14112*3.605) < 0.143
A = (L/(2*pi))^2 * (Cpsi + Q0 + L*Q1)
  < (1/5) * (4 + 0.28 + 2.6*0.143)
  = 0.93036 < 1
```

Alasan `Q0` dan `Q1`: dengan `r = exp(-2L) = 1/169` dan
`exp(-L/2) = 1/sqrt(13)`,

```text
Q0 = exp(-L/2)/(1-r) = 169/(168*sqrt(13))
Q1 = exp(-L/2) * (2r/(1-r)^2 + 1/(2(1-r)))
   = 7267/(14112*sqrt(13))
```

Batas `sqrt(13) > 3.605` diverifikasi dengan mengkuadratkan: `3.605^2 =
12.996025 < 13`. Karena itu `Q0 < 0.28` dan `Q1 < 0.143` adalah aritmetika
rasional, bukan hasil fit.

`Cpsi <= 47/12` dibuktikan di laporan dengan estimasi elementer pada
`u(t) = t/(1-exp(-t))`: `u <= 1+t`, `0 <= u' <= 1`, `0 <= u'' <= 1/6`.
Ini memberi `|h''| <= exp(-t/4)*(2/3 + t/16)` dan
`integral |h''| <= 11/3`, sehingga `Cpsi <= 1/4 + 11/3 = 47/12 < 4`.
Lemma kalkulus ini **tidak** diklaim sebagai hasil kernel Lean.

Batas `(L/(2*pi))^2 < 1/5` berasal dari `L < 2.6` dan `pi > 3`:
`L^2 < 6.76` dan `4*pi^2 > 36`, jadi `L^2/(4*pi^2) < 6.76/36 < 1/5`.

## 3. Derivasi yang dikunci

1. **Representasi integral trigamma** (DLMF 5.15.1):
   untuk `Re z > 0`,

   ```text
   psi'(z) = integral_0^inf t*exp(-z t)/(1-exp(-t)) dt
   ```

2. Dengan `z = 1/4 + i*y`, `y = pi*n/L`, dan `h` seperti di atas,

   ```text
   Re psi'(1/4 + i*y) = integral_0^inf h(t) cos(y t) dt
   ```

   Dua kali integrasi parsial (suku batas di 0 dan infinity) memberi

   ```text
   Re psi'(1/4 + i*y)
     = -h'(0)/y^2 - (1/y^2) * integral_0^inf h''(t) cos(y t) dt
   ```

   sehingga

   ```text
   |Re psi'(1/4 + i*y)| <= Cpsi/y^2
   |(1/4) Re psi'(1/4 + i*y)| <= Cpsi/w^2
   ```

   karena `y = w/2`.

3. **Suku geometrik.** Karena `c_k^2 + w^2 >= w^2`,

   ```text
   |gX1(n)| <= (1/w^2) * sum exp(-c_k L) c_k = Q1/w^2
   |gX2(n)| <= (1/w^2) * sum exp(-c_k L)     = Q0/w^2
   ```

4. **Gabungan.**

   ```text
   |XC(n)| <= (Cpsi + Q0 + L*Q1)/w^2
           < (4 + 0.28 + 2.6*0.143) * (1/5) / n^2
           = 0.93036/n^2
           < 1/n^2
   ```

5. **Tail.**

   ```text
   epsilon_XC(N) <= (4/L) * sum_{n>N} 1/n^2
                 < (4/L) * (1/N)
                 < 2/N          (karena L > 2)
   ```

   `L > 2` karena `e^2 < 9 < 13`. Jadi `epsilon_XC(N) -> 0`.

## 4. Artefak yang akan dibuat

### 4.1 `msaf/analytic_tail_bound.py`

- Mengimpor `arb_closed_forms` dari checkout eksternal
  `C:/Users/usER/oracle-toe/GUINAND_WEIL/source_arb_ldlt_certify.py`
  melalui `GW_DIR` (dapat di-override).
- Menghitung `XC(n)` untuk `n = 1..N_CHECK` pada `PREC_BITS`, dengan
  `N_CHECK = 512` dan `PREC_BITS = 512`.
- Untuk setiap `n`, memeriksa batas atas ball `n^2 * |XC(n)| < 1`; mencatat
  `max_ratio_upper` dan `n_at_max`.
- Memeriksa konstanta `L < 2.6`, `pi > 3`, `Q0 < 0.28`, `Q1 < 0.143`,
  `A_upper = (1/5)*(4 + 0.28 + 2.6*0.143) < 1` dengan aritmetika Arb/rasional.
- Menulis `reports/analytic_tail_bound_c13.json` berisi parameter, batas
  konstanta, `max_ratio_upper`, `n_checked`, digest `sha256` dari dump
  kanonik `(n, mid, rad)`, dan `verdict`.
- Menyediakan `--check` yang memverifikasi JSON tanpa membangun ulang
  perhitungan trigamma (jalur cepat CI).

### 4.2 `lean/Stage_6_Analytic_Tail.lean`

Deklarasi yang harus diperiksa kernel:

```text
sum_Icc_one_div_sq_le
sum_Icc_abs_le_of_pointwise
epsilon_le_of_pointwise
tendsto_epsilon_majorant
```

Bentuk yang dikunci:

```text
sum_Icc_one_div_sq_le
    (N M : Nat) (hN : 1 <= N) :
    sum_{n=N+1}^{M} 1/n^2 <= 1/N

sum_Icc_abs_le_of_pointwise
    (x : Nat -> Real)
    (hx : forall n, 1 <= n -> |x n| <= 1/n^2)
    (N M : Nat) (hN : 1 <= N) :
    sum_{n=N+1}^{M} |x n| <= 1/N

epsilon_le_of_pointwise
    (x : Nat -> Real) (hx : ...)
    (L : Real) (hL : 0 < L) (N M : Nat) (hN : 1 <= N) :
    (4/L) * sum_{n=N+1}^{M} |x n| <= (4/L) * (1/N)

tendsto_epsilon_majorant
    (L : Real) (hL : 0 < L) :
    Tendsto (fun N : Nat => (4/L)/(N : Real)) atTop (nhds 0)
```

File Lean **tidak** memformalkan representasi integral trigamma, fungsi
`psi'`, atau deret `gX1/gX2`. Ia memformalkan langkah tail: jumlah parsial
`1/n^2`, implikasi batas pointwise ke batas tail, dan limit mayoran.
Batas pointwise `|XC(n)| < 1/n^2` adalah input analitik dari laporan dan
sertifikat numerik, bukan hasil kernel Lean.

### 4.3 Registry dan laporan

- Entri baru `T-2026-0052`, **bukan** penulisan ulang `T-2026-0051`.
- `reports/ANALYTIC_TAIL_BOUND_2026-10-26.md` memuat derivasi lengkap,
  konstanta, output `#print axioms`, hasil builder, dan batas klaim.
- `msaf/tests/test_analytic_tail_bound.py` adalah guard cepat `--check`.
- Update `TARGET_STATUS_2026-10-25.md` untuk Stage 6/P2.
- Update `lean/lakefile.toml` dan `msaf/tests/test_anti_circularity_gate.py`
  agar Stage 6 terdaftar.

## 5. Kriteria penerimaan

P2 dianggap PASS hanya jika semua ini benar:

1. `python -m msaf.analytic_tail_bound` exit 0 dan JSON menunjukkan
   `max_ratio_upper < 1`, `A_upper < 1`, `Q0 < 0.28`, `Q1 < 0.143`,
   `L < 2.6`, `pi > 3`;
2. `python -m msaf.analytic_tail_bound --check` exit 0;
3. `cd lean; lake build` exit 0;
4. `cd lean; lake env lean Stage_6_Analytic_Tail.lean` exit 0;
5. `#print axioms` untuk keempat deklarasi hanya memuat
   `propext`, `Classical.choice`, `Quot.sound` (atau subset);
6. anti-circularity gate `check` Stage 2, 3, 4, 5, 6 memberi PASS dengan
   `FAIL=0 NOT_RUN=0 SKIP=0`;
7. `msaf/tests/test_analytic_tail_bound.py`,
   `msaf/tests/test_fence_registry.py`, dan
   `msaf/tests/test_lean_axiom_audit.py` lulus;
8. tidak ada `sorry`/`admit`/`axiom` di berkas Lean baru;
9. laporan menyebut batas klaim secara eksplisit.

## 6. Kriteria falsifikasi

P2 **FAILED** jika salah satu terjadi:

- ada `n` yang diperiksa dengan `n^2 * |XC(n)| >= 1` (batas atas ball);
- `A_upper >= 1`, `Q0 >= 0.28`, `Q1 >= 0.143`, `L >= 2.6`, atau `pi <= 3`;
- teorema Lean bergantung pada `sorryAx` atau aksioma proyek;
- hash registry tidak cocok;
- laporan menyebut hasil ini sebagai bukti RH, Weil positivity, spektrum
  zeta, positif-definit matriks, atau kontrol tail seluruh matriks;
- laporan mengklaim bahwa representasi integral trigamma sudah
  diformalkan di Lean, padahal belum.

Jika checkout eksternal tidak tersedia, builder mengembalikan
`INCONCLUSIVE`, bukan `PASS`.

## 7. Yang tidak diklaim

- Tidak ada klaim RH, Weil positivity, lokasi nol zeta, atau `sigma = 1/2`.
- Tidak ada klaim bahwa Lean membuktikan representasi integral trigamma,
  `psi'`, atau deret `gX1/gX2`.
- Tidak ada kontrol tail untuk `S(n)`, `Wp`, `W02`, entri off-diagonal, atau
  seluruh matriks Guinand–Weil.
- Tidak ada klaim bahwa `epsilon_XC(N)` lebih kecil dari `lambda_min(N)`;
  itu perbandingan terpisah dan tidak dibuktikan di sini.
- `XC` adalah kuantitas diagonal archimedean dari implementasi eksternal;
  `|XC(n)| < 1/n^2` adalah bound diagonal, bukan bound operator.

## 8. Urutan eksekusi

1. Commit dan push dokumen ini **sebelum** menulis kode P2.
2. Implementasi `msaf/analytic_tail_bound.py` dan JSON.
3. Implementasi `lean/Stage_6_Analytic_Tail.lean`; kompilasi dan audit aksioma.
4. Guard test, gate, registry, laporan.
5. Commit kode + artefak + registry; push.

Dokumen ini tidak boleh diubah setelah kode P2 dimulai, kecuali dengan
amendment bertanggal yang menjelaskan penyimpangan dan alasannya.

## 9. Amendment 2026-10-26 (setelah kode P2 dimulai)

Dua penyimpangan implementasi dicatat di sini; **tidak ada** konstanta,
klaim, atau kriteria penerimaan yang dilonggarkan.

1. **Nama dan bentuk indeks Lean.** Mathlib v4.33.1 yang dipin tidak
   menyediakan `Finset.sum_Icc_eq_sum_range`. Implementasi memakai
   `Finset.Ico (N + 1) (M + 1)`, yang merupakan himpunan bilangan bulat
   `N+1, ..., M` yang sama dengan `Icc (N+1) M`. Karena itu deklarasi
   bernama `sum_Ico_one_div_sq_le`, `sum_Ico_abs_le_of_pointwise`,
   `epsilon_le_of_pointwise`, dan `tendsto_epsilon_majorant`; pernyataan
   matematikanya tidak berubah. `tendsto_epsilon_majorant` memakai binder
   `_hL` (tidak dipakai) dengan tipe `0 < L`; tipe dan kesimpulannya sama.

2. **Grid diperbesar.** §4.1 menulis `N_CHECK = 512`; implementasi memakai
   `N_CHECK = 4096` pada `PREC_BITS = 512`. Ini memperluas cakupan uji
   numerik, bukan mengubah ambang: kriteria tetap `max n^2|XC(n)| < 1` dan
   `A_upper < 1`. Nilai `n_check = 4096` tercatat di
   `reports/analytic_tail_bound_c13.json`.

Tidak ada perubahan pada `Cpsi <= 47/12 < 4`, `Q0 < 0.28`, `Q1 < 0.143`,
`L < 2.6`, `pi > 3`, `A = 23259/25000 = 0.93036 < 1`, atau batas
`epsilon_XC(N) < 2/N`.
