# Konstanta tail Guinand–Weil untuk Stage 2/3 — penggantian data sintetis

Ditulis 2026-10-26. Status: penggantian konstanta sintetis dengan data nyata
dari implementasi Guinand–Weil; **bukan** bukti RH, bukan Weil positivity,
bukan klaim tentang spektrum zeta.

## 1. Mengapa contoh sintetis harus diganti

Entri registry `T-2026-0050` sebelumnya memakai contoh aritmetika

```text
N = 100, C = 5, α = 1, λ_min = 0.1
```

dan menandainya sendiri sebagai **sintetis**. Contoh itu membuktikan bahwa
struktur Lean dapat diinstansiasi, tetapi tidak ada hubungannya dengan
matriks Guinand–Weil. Pertanyaan berikutnya adalah apakah `C`, `α`, dan
`λ_min` yang nyata dapat dimasukkan.

Jawaban jujurnya: **tidak dalam bentuk `C / N^α` yang semula dibayangkan.**
Implementasi Guinand–Weil tidak menghasilkan bound tail polinomial dalam
konduktor. Yang dihasilkannya adalah sisa deret geometrik archimedean yang
eksponensial dalam indeks truncation. Memaksakan bentuk `C / c^α` dengan
`α` yang di-fit dari tangga `λ_min` akan menjadi fabrikasi: skrip
`msaf/lambda_min_eig_ladder.py` menolak memfit eksponen, dan datanya memang
tidak mengikuti hukum pangkat konstan.

## 2. Tail yang benar-benar ada di implementasi

Sumber eksternal: `C:/Users/usER/oracle-toe/GUINAND_WEIL/source_arb_ldlt_certify.py`,
fungsi `_geom_sums`. Deret yang dipakai adalah

```text
rho(x) = Σ_{k=0}^∞ exp(-(2k + 1/2) x).
```

Implementasi memotong deret setelah indeks terakhir `K` dan menambahkan
remainder geometrik

```text
rem(c, K) = 4 * c^(-(2K + 5/2)) / (1 - c^(-2)),    c > 1,
```

karena `exp(-L) = 1/c` dengan `L = log c`. Untuk `c = 13`, presisi 6000 bit,
loop berhenti di `K = 814`, sehingga

```text
C     = 4 / (1 - 13^(-2)) = 169/42 ≈ 4.023809523809524
α     = 2 * 814 + 5/2     = 3261/2 = 1630.5
rem   = C / 13^α          ≈ 2.0893032408096597e-1816.
```

Nilai `rem` dari ball Arb memiliki radius sekitar `2.0e-3618` (`rem.rad()`);
upper bound ball-nya masih jauh di bawah `λ_min` yang dipakai (lihat §3). Jadi
bound `C / 13^α` bukan sekadar midpoint: upper bound ball-nya juga di bawah
`λ_min`. Angka `+/-` pada `rem.str(20)` adalah galat pembulatan tampilan 20
digit, bukan radius ball; gunakan `rem.rad()`.

**Batas semantik.** `α = 1630.5` adalah **indeks truncation**, bukan eksponen
decay dalam konduktor. `C = 169/42` adalah koefisien deret geometrik, bukan
konstanta tail polinomial. Tidak ada `C`, `α` polinomial nyata yang dapat
dikutip dari implementasi ini.

## 3. Data `λ_min` yang tersertifikasi

Tangga magnitudo `c = 13`, presisi 6000 bit, dari
`reports/lambda_min_eig_ladder_dim321.json`,
`reports/lambda_min_eig_ladder_big.json`, dan README §6.4:

| dim (N) | λ_min_lo (float64 image) | verdict |
|---:|---:|---|
| 17 (8) | `7.674392556360189e-23` | CERTIFIED, all eigenvalues strictly positive |
| 33 (16) | `8.568627478072444e-35` | CERTIFIED, all eigenvalues strictly positive |
| 65 (32) | `2.2589311905740533e-49` | CERTIFIED, all eigenvalues strictly positive |
| 129 (64) | `6.321351409477261e-59` | CERTIFIED, all eigenvalues strictly positive |
| 257 (128) | `3.2990200597971055e-59` | CERTIFIED, all eigenvalues strictly positive |
| 321 (160) | `3.123458832662237e-59` | CERTIFIED, all eigenvalues strictly positive |

Dua rung yang dipakai di Lean:

```text
c = 13, N = 160, dim = 321, λ_min_lo = 3.123458832662237e-59
c = 13, N = 128, dim = 257, λ_min_lo = 3.2990200597971055e-59
```

Angka `λ_min_lo` adalah citra float64 dari lower endpoint Arb
(`float(lo.lower())`), sehingga digit terakhirnya dapat berbeda dari endpoint
eksak hingga satu ulp (~1e-16 relatif). Margin `rem` terhadap angka itu
sekitar 1750 orde, jauh melebihi satu ulp; sertifikat tetap enclosure Arb,
bukan digit desimal Lean.

Keduanya berasal dari `arb_mat.eig` (Route A2) dan memiliki
`all_exclude_zero = true`. Field `lambda_min_rad = 0.0` dan
`imag_leak_upper = 0.0` di JSON adalah artefak underflow float64, **bukan**
nol literal; koreksinya tercatat di
`reports/GW_RADIUS_REGISTRY_CORRECTION_2026-10-17.md`.

## 4. Formalization Lean

`lean/Stage_2_Tail_Bound.lean` sekarang mendefinisikan:

```text
TailBound c          -- K, C, α, α = 2K + 5/2, C ≥ 0, α > 1/2, c > 1
gw_conductor = 13
gw_block     = 160
gw_dim       = 321
gw_tail_K    = 814
gw_tail_C    = 169/42
gw_tail_alpha= 3261/2
gw_lambda_min= 3123458832662237 / 10^74
```

dan membuktikan:

```text
tail_bound_nonneg
gw_dim_eq : 321 = 2*160 + 1
gw_lambda_min_pos
gw_tail_bound_lt_lambda_min
gw_tail_bound_lt_lambda_min_257
```

Ketaksamaan dibuktikan dengan bound kasar `13^(3261/2) > 13^102 > 10^60`;
tidak perlu mengevaluasi pangkat 1600 digit. Hasilnya:

```text
C / 13^α  <  3.123458832662237e-59
C / 13^α  <  3.2990200597971055e-59
```

`lean/Stage_3_Eigenvalue_Locking.lean` mendefinisikan record
`EigenvalueLock c N` dengan field `dim`, `dim_eq`, `lam_min`,
`lam_min_pos`, dan `bound_from_tail`. Dua record nyata diisi:

```text
gw_eigenvalue_lock     : EigenvalueLock 13 160
gw_eigenvalue_lock_257 : EigenvalueLock 13 128
```

## 5. Apa yang tidak diklaim

1. **Bukan bukti RH.** Tidak ada spektrum zeta, Weil positivity, atau
   prime counting di sini.
2. **Bukan bukti bahwa Lean menghitung eigenvalue.** `λ_min` adalah batas
   bawah yang dicatat dari run Arb eksternal. Lean hanya memeriksa
   positivitasnya dan ketaksamaan skalar terhadap remainder archimedean.
3. **Bukan bound error entry penuh.** `rem` adalah bound per-deret untuk
   sisa geometrik. Kombinasi linier entry matriks dan propagasi ball penuh
   ditangani oleh Arb di dalam run; sertifikat eksternalnya adalah
   `all_exclude_zero = true`. Perbandingan `rem < λ_min` adalah syarat
   konsistensi, bukan pengganti sertifikat matriks penuh.
4. **Bukan tail polinomial.** Tidak ada `C / c^α` polinomial yang nyata.
   `α = 1630.5` adalah indeks truncation. Menyebutnya "decay exponent"
   akan menyesatkan.
5. **Tidak ada `sorry`/`admit`/`axiom`** di ketiga berkas Lean; gate
   anti-sirkularitas PASS dengan `FAIL=0 NOT_RUN=0 SKIP=0`.

## 6. Perintah reproduksi

```powershell
# numerik: K, C, α, rem
@'
from flint import arb, ctx
ctx.prec = 6000
c = 13
L = arb(c).log()
thr = arb(2) ** (-(6000 + 24))
k = 0
while True:
    ck = arb(2*k) + arb('0.5')
    e = (-ck * L).exp()
    if e < thr and k > 2:
        break
    k += 1
c_next = arb(2*(k+1)) + arb('0.5')
rem = arb(4) * ((-c_next*L).exp() / (1 - (-2*L).exp()))
print('K', k, 'c_next', c_next.str(20))
print('C', (arb(4)/(1 - arb(c)**(-2))).str(20))
print('alpha', (2*k + arb('2.5')).str(20))
print('rem', rem.str(20))
print('rem.rad', rem.rad().str(20))
print('rem upper < lambda_min(321)',
      bool(rem.upper() < arb('3.123458832662237e-59')))
print('rem upper < lambda_min(257)',
      bool(rem.upper() < arb('3.2990200597971055e-59')))
'@ | C:\Python314\python.exe -

# Lean
cd lean
lake build
lake env lean ..\reports\RH_SCAFFOLD_NOTES\Stage_4_Containment_Proof.lean
cd ..

# gate + registry
C:\Python314\python.exe C:\Users\usER\.config\opencode\skills\anti-circularity\scripts\gate.py check `
  lean\Stage_2_Tail_Bound.lean lean\Stage_3_Eigenvalue_Locking.lean `
  reports\RH_SCAFFOLD_NOTES\Stage_4_Containment_Proof.lean
python -m pytest msaf/tests/test_fence_registry.py -q
```
