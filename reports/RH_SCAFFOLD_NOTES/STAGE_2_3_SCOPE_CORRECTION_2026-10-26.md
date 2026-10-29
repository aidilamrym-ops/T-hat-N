# Koreksi lingkup Stage 2/3 â€” 2026-10-26

Dokumen ini memperbaiki klaim lingkup for scaffold RH Stage 2 and Stage 3.
Dokumen ini **bukan** bukti RH, bukan bukti tail analitik, and bukan bukti
induksi dimensi. Tujuannya hanya memisahkan tiga hal which sebelumnya tercampur
dalam arsip prompt and registry:

1. prompt arsip 2026-10-25;
2. file Lean which benar-benar dikompilasi sekarang;
3. teorema which benar-benar diperiksa kernel.

## 1. Peta file: arsip versus implementasi aktif

| Stage | Arsip prompt | Implementasi aktif | Isi sebenarnya |
|---|---|---|---|
| 1 | `reports/RH_SCAFFOLD_NOTES/Stage_1_Formalization_Test_Function_Space.lean` | sama | definisi ruang fungsi uji and bentuk kuadratik kontinu; bukan bukti analitik |
| 2 | `reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.lean` | `lean/Stage_2_Tail_Bound.lean` | konstanta truncation archimedean GW nyata and ketaksamaan skalar; **bukan** derivasi tail analitik |
| 3 | `reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.lean` | `lean/Stage_3_Eigenvalue_Locking.lean` | record data for dua run Arb; **bukan** induksi dimensi |
| 4 | `reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof.lean` | sama (already ditulis ulang) | containment LÂ² dari hipotesis polynomial decay; **bukan** containment spektrum zeta |

Berkas arsip Stage 2/3 sengaja dipertahankan sebagai sejarah prompt. Keduanya
hanya berisi placeholder and **no** boleh dikutip sebagai implementasi
Stage 2/3. Berkas aktif ada in directory `lean/`.

Hash SHA-256LF saat koreksi ini ditulis:

```text
2149a89242c3fc010a84d5796c6b4412746a07e6f8c6f8a3ccb917104941f71d  lean/Stage_2_Tail_Bound.lean
551e7e31f73de57ef2c8ee0c9c84fbd7da93295fbde8e6946b5f42db5916155f  lean/Stage_3_Eigenvalue_Locking.lean
5786929a607aa73bc2395481af8f3cb848fff79d3bfff82536b5be88b69a7d61  reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof.lean
cbe01538ea67cb3372e13500735a113d2413072962418f9dae1cf8fdc29b22df  lean/lakefile.toml
```

## 2. Stage 2: apa which dibuktikan and apa which no

`lean/Stage_2_Tail_Bound.lean` memakai konstanta dari `_geom_sums` in
`source_arb_ldlt_certify.py` (checkout eksternal
`oracle-toe/GUINAND_WEIL`):

```text
c = 13, presisi 6000 bit, K = 814
C = 4 / (1 - 13^(-2)) = 169/42
alpha = 2K + 5/2 = 3261/2
rem = C / 13^alpha  ~= 2.0893e-1816
```

Yang diperiksa kernel:

```text
tail_bound_nonneg
gw_dim_eq
gw_lambda_min_pos
gw_tail_bound_lt_of_gt_ten_pow_sixty
gw_tail_bound_lt_lambda_min
gw_dim_257_eq
gw_lambda_min_257_pos
gw_tail_bound_lt_lambda_min_257
```

Yang **no** dibuktikan:

- no ada `|XC(n)| <= C_arch / n`;
- no ada `|XC(n)| <= C_arch / n^2`;
- no ada derivasi Stirling/trigamma;
- no ada `epsilon(N) -> 0`;
- no ada positivity matriks dari ketaksamaan skalar ini.

`rem < lambda_min` adalah perbandingan skalar antara sisa deret geometrik and
citra desimal lower endpoint Arb. Ini bukan propagasi error entry matriks and
bukan pengganti sertifikat `arb_mat.eig`.

### 2.1 Kenapa target `C/n` in prompt no dipakai

Prompt Stage 2 meminta `|XC(n)| <= C_arch / n` sekaligus tail
`epsilon(N) = C_arch L^2 / (pi N)`. Keduanya no konsisten: tail harmonik
`sum 1/n` divergen, sehingga no dapat menjadi limit ekor which menuju nol.

Target asimtotik which benar adalah `|XC(n)| <= C / n^2`. Pengukuran 1000-bit
(1000 bit, `_geom_sums`/`arb_closed_forms`) memberikan `n^2 * XC(n)` which stabil
in sekitar `-0.05621508517` dari `n = 10` sampai `n = 10^6`. Itu **bukti
numerik**, bukan bukti. Derivasi analitiknya adalah pekerjaan P2 and belum
diklaim.

## 3. Stage 3: kenapa induksi dimensi no valid

Prompt Stage 3 meminta induksi positif-definit dari `A_N` ke `A_{N+1}`.
Cauchy interlacing memberikan arah which berlawanan:

```text
lambda_min(A_{N+1}) <= lambda_min(A_N)
```

Jadi positivity `A_N` no otomatis naik ke `A_{N+1}`. Bahkan jika semua
`lambda_min(A_N)` positif, limit bawahnya dapat menurun; diperlukan kontrol
entry error or bukti positif langsung for setiap dimensi.

`lean/Stage_3_Eigenvalue_Locking.lean` karena itu hanya mendefinisikan record
data:

```text
EigenvalueLock c N
  dim, dim_eq : dim = 2N + 1
  lam_min, lam_min_pos
  bound_from_tail : exists tb : TailBound c, tb.C / c^tb.alpha < lam_min
```

Dua record nyata diisi for `(c=13, N=160, dim=321)` and
`(c=13, N=128, dim=257)`. Record ini **no** membuktikan bahwa Lean
mendiagonalisasi matriks, no membuktikan positif-definit for semua N,
and no membuktikan spektrum berada in garis kritis. Sertifikat matriksnya
tetap run Arb eksternal with `all_exclude_zero = true`.

## 4. Stage 4: limit which tetap berlaku

`reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof.lean` membuktikan
`test_function_l2_containment`: polynomial decay `|f x| <= C/x` for `x >= 1`
mengakibatkan `f^2` terintegralkan on `(0, infinity)`. Teorema ini no
menyentuh spektrum zeta, Weil positivity, or hipotesis RH.

## 5. Audit aksioma

Perintah which dijalankan dari `lean/`:

```powershell
@'
import Stage_2_Tail_Bound
import Stage_3_Eigenvalue_Locking
#print axioms tail_bound_nonneg
#print axioms gw_dim_eq
#print axioms gw_lambda_min_pos
#print axioms gw_tail_bound_lt_of_gt_ten_pow_sixty
#print axioms gw_tail_bound_lt_lambda_min
#print axioms gw_dim_257_eq
#print axioms gw_lambda_min_257_pos
#print axioms gw_tail_bound_lt_lambda_min_257
#print axioms eigenvalue_min_positive
'@ | Set-Content _axiom_audit.lean
lake env lean _axiom_audit.lean
Remove-Item _axiom_audit.lean
```

Keluaran:

```text
'tail_bound_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]
'gw_dim_eq' depends on axioms: [propext]
'gw_lambda_min_pos' depends on axioms: [propext, Classical.choice, Quot.sound]
'gw_tail_bound_lt_of_gt_ten_pow_sixty' depends on axioms: [propext, Classical.choice, Quot.sound]
'gw_tail_bound_lt_lambda_min' depends on axioms: [propext, Classical.choice, Quot.sound]
'gw_dim_257_eq' depends on axioms: [propext]
'gw_lambda_min_257_pos' depends on axioms: [propext, Classical.choice, Quot.sound]
'gw_tail_bound_lt_lambda_min_257' depends on axioms: [propext, Classical.choice, Quot.sound]
'eigenvalue_min_positive' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Tidak ada `sorryAx`, no ada aksioma proyek, and no ada placeholder in
file aktif. Anti-circularity gate: PASS (`FAIL=0 NOT_RUN=0 SKIP=0`).

## 6. Batas klaim

Dokumen ini no menaikkan status apa pun. Stage 2 tetap belum punya tail
analitik; Stage 3 tetap belum punya induksi; Stage 4 tetap hanya containment LÂ².
Registry `T-2026-0050` harus dibaca with koreksi ini.


