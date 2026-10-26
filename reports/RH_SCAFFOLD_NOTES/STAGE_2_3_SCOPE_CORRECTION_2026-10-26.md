# Koreksi lingkup Stage 2/3 — 2026-10-26

Dokumen ini memperbaiki klaim lingkup untuk scaffold RH Stage 2 dan Stage 3.
Dokumen ini **bukan** bukti RH, bukan bukti tail analitik, dan bukan bukti
induksi dimensi. Tujuannya hanya memisahkan tiga hal yang sebelumnya tercampur
dalam arsip prompt dan registry:

1. prompt arsip 2026-10-25;
2. berkas Lean yang benar-benar dikompilasi sekarang;
3. teorema yang benar-benar diperiksa kernel.

## 1. Peta berkas: arsip versus implementasi aktif

| Stage | Arsip prompt | Implementasi aktif | Isi sebenarnya |
|---|---|---|---|
| 1 | `reports/RH_SCAFFOLD_NOTES/Stage_1_Formalization_Test_Function_Space.lean` | sama | definisi ruang fungsi uji dan bentuk kuadratik kontinu; bukan bukti analitik |
| 2 | `reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.lean` | `lean/Stage_2_Tail_Bound.lean` | konstanta truncation archimedean GW nyata dan ketaksamaan skalar; **bukan** derivasi tail analitik |
| 3 | `reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.lean` | `lean/Stage_3_Eigenvalue_Locking.lean` | record data untuk dua run Arb; **bukan** induksi dimensi |
| 4 | `reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof.lean` | sama (sudah ditulis ulang) | containment L² dari hipotesis polynomial decay; **bukan** containment spektrum zeta |

Berkas arsip Stage 2/3 sengaja dipertahankan sebagai sejarah prompt. Keduanya
hanya berisi placeholder dan **tidak** boleh dikutip sebagai implementasi
Stage 2/3. Berkas aktif ada di direktori `lean/`.

Hash SHA-256LF saat koreksi ini ditulis:

```text
2149a89242c3fc010a84d5796c6b4412746a07e6f8c6f8a3ccb917104941f71d  lean/Stage_2_Tail_Bound.lean
551e7e31f73de57ef2c8ee0c9c84fbd7da93295fbde8e6946b5f42db5916155f  lean/Stage_3_Eigenvalue_Locking.lean
5786929a607aa73bc2395481af8f3cb848fff79d3bfff82536b5be88b69a7d61  reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof.lean
cbe01538ea67cb3372e13500735a113d2413072962418f9dae1cf8fdc29b22df  lean/lakefile.toml
```

## 2. Stage 2: apa yang dibuktikan dan apa yang tidak

`lean/Stage_2_Tail_Bound.lean` memakai konstanta dari `_geom_sums` di
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

Yang **tidak** dibuktikan:

- tidak ada `|XC(n)| <= C_arch / n`;
- tidak ada `|XC(n)| <= C_arch / n^2`;
- tidak ada derivasi Stirling/trigamma;
- tidak ada `epsilon(N) -> 0`;
- tidak ada positivity matriks dari ketaksamaan skalar ini.

`rem < lambda_min` adalah perbandingan skalar antara sisa deret geometrik dan
citra desimal lower endpoint Arb. Ini bukan propagasi error entry matriks dan
bukan pengganti sertifikat `arb_mat.eig`.

### 2.1 Kenapa target `C/n` di prompt tidak dipakai

Prompt Stage 2 meminta `|XC(n)| <= C_arch / n` sekaligus tail
`epsilon(N) = C_arch L^2 / (pi N)`. Keduanya tidak konsisten: tail harmonik
`sum 1/n` divergen, sehingga tidak dapat menjadi batas ekor yang menuju nol.

Target asimtotik yang benar adalah `|XC(n)| <= C / n^2`. Pengukuran 1000-bit
(1000 bit, `_geom_sums`/`arb_closed_forms`) memberikan `n^2 * XC(n)` yang stabil
di sekitar `-0.05621508517` dari `n = 10` sampai `n = 10^6`. Itu **bukti
numerik**, bukan bukti. Derivasi analitiknya adalah pekerjaan P2 dan belum
diklaim.

## 3. Stage 3: kenapa induksi dimensi tidak valid

Prompt Stage 3 meminta induksi positif-definit dari `A_N` ke `A_{N+1}`.
Cauchy interlacing memberikan arah yang berlawanan:

```text
lambda_min(A_{N+1}) <= lambda_min(A_N)
```

Jadi positivity `A_N` tidak otomatis naik ke `A_{N+1}`. Bahkan jika semua
`lambda_min(A_N)` positif, batas bawahnya dapat menurun; diperlukan kontrol
entry error atau bukti positif langsung untuk setiap dimensi.

`lean/Stage_3_Eigenvalue_Locking.lean` karena itu hanya mendefinisikan record
data:

```text
EigenvalueLock c N
  dim, dim_eq : dim = 2N + 1
  lam_min, lam_min_pos
  bound_from_tail : exists tb : TailBound c, tb.C / c^tb.alpha < lam_min
```

Dua record nyata diisi untuk `(c=13, N=160, dim=321)` dan
`(c=13, N=128, dim=257)`. Record ini **tidak** membuktikan bahwa Lean
mendiagonalisasi matriks, tidak membuktikan positif-definit untuk semua N,
dan tidak membuktikan spektrum berada di garis kritis. Sertifikat matriksnya
tetap run Arb eksternal dengan `all_exclude_zero = true`.

## 4. Stage 4: batas yang tetap berlaku

`reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof.lean` membuktikan
`test_function_l2_containment`: polynomial decay `|f x| <= C/x` untuk `x >= 1`
mengakibatkan `f^2` terintegralkan pada `(0, infinity)`. Teorema ini tidak
menyentuh spektrum zeta, Weil positivity, atau hipotesis RH.

## 5. Audit aksioma

Perintah yang dijalankan dari `lean/`:

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

Tidak ada `sorryAx`, tidak ada aksioma proyek, dan tidak ada placeholder di
berkas aktif. Anti-circularity gate: PASS (`FAIL=0 NOT_RUN=0 SKIP=0`).

## 6. Batas klaim

Dokumen ini tidak menaikkan status apa pun. Stage 2 tetap belum punya tail
analitik; Stage 3 tetap belum punya induksi; Stage 4 tetap hanya containment L².
Registry `T-2026-0050` harus dibaca dengan koreksi ini.
