# Envelope error entry dan teorema perturbasi finit — 2026-10-26

Status: **P1 finit, PASS**. Dokumen ini **bukan** bukti Riemann Hypothesis,
bukan bukti Weil positivity, bukan bukti tail analitik, dan bukan bukti bahwa
Lean mendiagonalisasi matriks Guinand–Weil.

Pra-registrasi: `reports/PREREG_ENTRY_ERROR_ENVELOPE_2026-10-26.md`
(dikomit dan dipush sebagai `34ee072` **sebelum** kode P1 ditulis).
Basis kode: `5fea118` (P0) + `34ee072` (prereg).

## 1. Ringkasan konstanta

| Item | Nilai |
|---|---|
| Konduktor | `c = 13` |
| Block half-width | `N = 160` |
| Dimensi | `dim = 321` |
| Presisi Arb | 6000 bit |
| Entry | 103041 = 321² |
| Envelope entry | `epsilon = 10^-100` |
| `delta = dim * epsilon` | `3.21 * 10^-98` |
| `lambda_min` | `3.123458832662237e-59` |
| `max_entry_radius_upper` | `7.1914155376658473965293017526957343044333917984215755378759885908592866832516155956378392624582265061519137723422577365087585735710678120654e-1714` |
| `max_entry_radius_plus_slack` | `1.000...e-120` (slack serialisasi mendominasi) |
| Digest dump kanonik | `69e5986e605b56f174541a8c3c1647cf4079af0b2042518894f142c5a659b84f` |
| Verdict | `PASS` |

Sumber angka: `reports/entry_error_envelope_c13_n160.json`, dibangun oleh
`msaf/entry_error_envelope.py` dari
`build_arb_tau(c=13, N=160, prec=6000)` di checkout eksternal
`C:/Users/usER/oracle-toe/GUINAND_WEIL/source_arb_ldlt_certify.py`.

`epsilon = 10^-100` dipilih **sebelum** pengukuran. Radius entry aktual
sekitar `7.19e-1714`, jauh di bawah threshold; `1e-120` adalah slack
serialisasi desimal per entry, sehingga batas konservatif yang dipakai adalah
`1e-120`, bukan `7.19e-1714`. Keduanya di bawah `10^-100`.

## 2. Ketaksamaan eksak

Yang diperiksa:

```text
delta = 321 * 10^-100 = 3.21 * 10^-98
lambda = 3123458832662237 / 10^74
delta < lambda
```

Perbandingan ini eksak dalam `ℚ` (tidak ada float64 di jalur keputusan).
Di Lean, `gw_entry_delta_lt_lambda_min` membuktikannya dengan `norm_num`
atas numeral rasional. Secara silang:

```text
321 * 10^74 < 3123458832662237 * 10^100
321          < 3123458832662237 * 10^26
```

## 3. Teorema Lean

Berkas: `lean/Stage_5_EntryError_Perturbation.lean`.
Deklarasi yang diperiksa kernel:

```text
qform
qform_add
abs_qform_le_of_entrywise
posDef_add_of_quadratic_bound
gw_entry_delta_lt_lambda_min
gw_entry_perturbation_posDef
```

Teorema inti:

```text
posDef_add_of_quadratic_bound
    (A E : Matrix n n ℝ) (lam delta : ℝ)
    (hA : A.PosDef)
    (hAquad : ∀ x, lam * qform 1 x ≤ qform A x)
    (hEquad : ∀ x, |qform E x| ≤ delta * qform 1 x)
    (hdelta : delta < lam) (hlam : 0 < lam)
    (hE : E.IsHermitian) :
    (A + E).PosDef
```

Estimasi entrywise:

```text
abs_qform_le_of_entrywise
    (E : Matrix n n ℝ) (ε : ℝ) (hε : 0 ≤ ε)
    (hE : ∀ i j, |E i j| ≤ ε) (x : n → ℝ) :
    |qform E x| ≤ (Fintype.card n : ℝ) * ε * qform 1 x
```

Bukti memakai `|∑_ij x_i E_ij x_j| ≤ ε (∑_i |x_i|)²` dan
`(∑_i |x_i|)² ≤ dim · ∑_i x_i²` (Cauchy–Schwarz).

Instansiasi konkret:

```text
gw_entry_perturbation_posDef
    (A E : Matrix (Fin gw_dim) (Fin gw_dim) ℝ)
    (hA : A.PosDef)
    (hAquad : ∀ x, gw_lambda_min * qform 1 x ≤ qform A x)
    (hEentry : ∀ i j, |E i j| ≤ gw_epsilon)
    (hE : E.IsHermitian) :
    (A + E).PosDef
```

`gw_epsilon = 1 / 10^100`, `gw_entry_delta = 321 * gw_epsilon`,
`gw_lambda_min = 3123458832662237 / 10^74` (dari
`lean/Stage_2_Tail_Bound.lean`).

## 4. Audit aksioma

Perintah (berkas sementara di `lean/`, dihapus setelah dijalankan):

```powershell
@'
import Stage_5_EntryError_Perturbation

#print axioms qform_add
#print axioms abs_qform_le_of_entrywise
#print axioms posDef_add_of_quadratic_bound
#print axioms gw_entry_delta_lt_lambda_min
#print axioms gw_entry_perturbation_posDef
'@ | Set-Content _p1_axiom_audit_tmp.lean
lake env lean _p1_axiom_audit_tmp.lean
```

Keluaran:

```text
'qform_add' depends on axioms: [propext, Classical.choice, Quot.sound]
'abs_qform_le_of_entrywise' depends on axioms: [propext, Classical.choice, Quot.sound]
'posDef_add_of_quadratic_bound' depends on axioms: [propext, Classical.choice, Quot.sound]
'gw_entry_delta_lt_lambda_min' depends on axioms: [propext, Classical.choice, Quot.sound]
'gw_entry_perturbation_posDef' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Tidak ada `sorryAx` dan tidak ada aksioma proyek.

## 5. Verifikasi yang dijalankan

| Perintah | Hasil |
|---|---|
| `cd lean; lake build` | 3258 jobs, exit 0 |
| `cd lean; lake env lean Stage_5_EntryError_Perturbation.lean` | exit 0, tanpa diagnostic |
| `python -m msaf.entry_error_envelope --check` | PASS |
| `python -m pytest msaf/tests/test_entry_error_envelope.py -q` | 8 passed |
| `python -m pytest msaf/tests/test_lean_axiom_audit.py -q` | 2 passed |
| `python -m pytest msaf/tests/test_fence_registry.py -q` | lihat laporan commit P1 |
| anti-circularity gate `check` Stage 2, 3, 4, 5 | PASS, `FAIL=0 NOT_RUN=0 SKIP=0` |

Rebuild penuh envelope (bukan jalur CI):

```powershell
python -m msaf.entry_error_envelope
```

Rebuild ini memerlukan checkout eksternal `oracle-toe/GUINAND_WEIL` dan
membangun matriks 321×321 pada 6000 bit. Jalur `--check` hanya membaca JSON
dan memverifikasi konstanta serta ketaksamaan; ia tidak membangun ulang
matriks.

## 6. Batas klaim

1. **Bukan bukti RH.** Tidak ada klaim tentang zero zeta, spektrum zeta, atau
   Weil positivity.
2. **Bukan bukti positif-definit matriks Arb.** `hA : A.PosDef` dan
   `hAquad` adalah hipotesis teorema. Otoritas untuk positivity matriks tetap
   run `arb_mat.eig` eksternal (`all_exclude_zero = true`); Lean tidak
   mendiagonalisasi matriks dan tidak membuktikan `hAquad`.
3. **Bukan kontrol error penuh.** `epsilon` adalah batas radius entry, bukan
   propagasi ball penuh ke eigenvalue. Teorema hanya memakai batas kuadratik
   `|xᵀEx| ≤ delta‖x‖²` sebagai hipotesis; hubungan antara batas entry dan
   batas kuadratik dibuktikan di Lean, tetapi hubungan antara matriks Arb dan
   `A.PosDef`/`hAquad` tidak.
4. **Bukan tail analitik.** Tidak ada klaim `|XC(n)| = O(1/n²)` dan tidak ada
   klaim `epsilon(N) → 0`. Itu pekerjaan P2.
5. **`delta < lambda` adalah aritmetika skalar.** Ia tidak membuktikan bahwa
   error entry aktual sama dengan `delta`; `delta` adalah pagar konservatif
   yang dipilih sebelum pengukuran.
6. **Digest adalah komitmen.** `digest_sha256` adalah hash dari dump kanonik
   `(i, j, mid, rad)`; dump penuh tidak disimpan di repo. Reproduksi
   memerlukan rebuild matriks, bukan hanya membaca JSON.

## 7. Berkas terkait

- `reports/PREREG_ENTRY_ERROR_ENVELOPE_2026-10-26.md` — pra-registrasi
  terkunci.
- `msaf/entry_error_envelope.py` — builder dan checker.
- `reports/entry_error_envelope_c13_n160.json` — record envelope.
- `lean/Stage_5_EntryError_Perturbation.lean` — teorema finit.
- `msaf/tests/test_entry_error_envelope.py` — guard cepat.
- `reports/FENCE_REGISTRY.md` — entri `T-2026-0051`.
- `reports/AUDIT_2026-10-24_26_REVIEW.md` — audit P0 yang menemukan masalah
  lingkup Stage 2/3.
