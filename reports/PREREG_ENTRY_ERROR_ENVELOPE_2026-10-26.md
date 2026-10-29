# Pra-registrasi: entry-error envelope and teorema perturbasi finit

**Status:** PRE-REG, dikunci sebelum kode P1.
**Tanggal:** 2026-10-26.
**Basis commit:** `5fea118` (P0).
**Bidang:** Guinandâ€“Weil Stage 2/3, finite perturbation only.
**Bukan:** bukti RH, bukti Weil positivity, bukti tail analitik, or bukti
bahwa Lean mendiagonalisasi matriks.

## 1. Pertanyaan which dijawab

Diberikan matriks ball Arb `A` dari `build_arb_tau(c=13, N=160, prec=6000)`
and limit bawah eigenvalue `lambda_min` which already tersertifikasi, dapatkah
kita:

1. menghitung envelope error entry `epsilon` sebagai limit atas radius ball
   setiap entry, with serialisasi desimal (bukan float64);
2. membuktikan in kernel Lean bahwa jika `A0` positif-definit with limit
   kuadratik `lambda`, and `E` adalah perturbasi simetris with
   `|E_ij| <= epsilon`, maka `A0 + E` positif-definit selama
   `dim * epsilon < lambda`;
3. menginstansiasi ketaksamaan aritmetiknya for `dim = 321`,
   `epsilon = 10^-100`, and `lambda = gw_lambda_min`.

Jawaban which diklaim hanya for tiga hal in atas. Matriks Arb itu sendiri
tetap disertifikasi oleh run `arb_mat.eig` eksternal, bukan oleh Lean.

## 2. Konstanta which dikunci sebelum pengukuran

Threshold entry envelope **dipilih sebelum** menjalankan `build_arb_tau`:

```text
epsilon = 10^-100
dim     = 321
delta   = dim * epsilon = 321 * 10^-100 = 3.21 * 10^-98
lambda  = gw_lambda_min = 3123458832662237 / 10^74
```

Alasan: presisi 6000 bit memberi radius relatif sekitar `10^-1800`; `10^-100`
jauh in atas noise numerik tetapi masih jauh in bawah `lambda ~ 3.12e-59`.
Threshold no boleh dinaikkan setelah melihat result. Jika ada entry with
radius `> 10^-100`, kampanye P1 **FAILED** and no boleh mengklaim envelope.

## 3. Artefak which akan created

### 3.1 `msaf/entry_error_envelope.py`

- Mengimpor `build_arb_tau` dari checkout eksternal
  `C:/Users/usER/oracle-toe/GUINAND_WEIL/source_arb_ldlt_certify.py`
  melalui `GW_DIR`, with path which dapat in-override.
- Membangun `A, dim = build_arb_tau(13, 160, 6000)`.
- Untuk setiap `(i,j)`, mencatat `mid` and `rad` sebagai **string desimal**
  with presisi cukup; no menggunakan `float()` for radius.
- Menghitung `max_rad` and `max_rad + serialization_slack`, with
  `serialization_slack = 10^-120` per entry.
- Gagal (`exit 1`) jika `dim != 321`, `max_rad + slack > 10^-100`, or ada
  entry non-finite.
- Menulis `reports/entry_error_envelope_c13_n160.json` berisi:
  `c`, `N`, `dim`, `prec_bits`, `epsilon`, `delta`, `lambda_min`,
  `max_entry_radius_upper`, `max_entry_radius_plus_slack`, `n_entries`,
  `digest_sha256` dari dump kanonik `(i,j,mid,rad)`, and `verdict`.
- Menyediakan mode `--check` which verifying JSON which already ada tanpa
  membangun ulang matriks (for CI/test cepat).

### 3.2 `lean/Stage_5_EntryError_Perturbation.lean`

Teorema which harus diperiksa kernel:

```text
qform_add
abs_qform_le_of_entrywise
posDef_add_of_quadratic_bound
gw_entry_delta_lt_lambda_min
gw_entry_perturbation_posDef
```

`posDef_add_of_quadratic_bound` berbentuk:

```text
A.PosDef ->
(forall x, lambda * (x^T x) <= x^T A x) ->
(forall x, |x^T E x| <= delta * (x^T x)) ->
delta < lambda -> 0 < lambda -> E.IsHermitian ->
(A + E).PosDef
```

`gw_entry_perturbation_posDef` menginstansiasi `dim = 321`,
`epsilon = 10^-100`, `delta = 321 * 10^-100`, and `lambda = gw_lambda_min`.
Teorema ini **menerima** `A.PosDef` and limit kuadratik `A` sebagai hipotesis;
ia no mengklaim membuktikan premis matriks Arb dari Lean.

### 3.3 Registry

Entri baru `T-2026-0051`, bukan penulisan ulang `T-2026-0050`. Entri harus
memuat limit klaim, perintah verifikasi, hash `sha256LF`, and relasi ke
`T-2026-0050` serta `reports/GW_TAIL_CONSTANTS_2026-10-26.md`.

### 3.4 Laporan

`reports/ENTRY_ERROR_ENVELOPE_2026-10-26.md` memuat:
- angka `max_rad`, `epsilon`, `delta`, `lambda`;
- bukti bahwa `delta < lambda` (aritmetik eksak);
- output `#print axioms`;
- limit klaim which eksplisit.

## 4. Kriteria penerimaan

P1 dianggap PASS hanya jika semua ini benar:

1. `lake build` in `lean/` exit 0;
2. `lake env lean ../reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof.lean`
   exit 0 (regresi);
3. `#print axioms` for kelima deklarasi baru hanya memuat
   `propext`, `Classical.choice`, `Quot.sound` (or subset);
4. anti-circularity gate `check` memberi PASS with
   `FAIL=0 NOT_RUN=0 SKIP=0`;
5. `msaf/tests/test_entry_error_envelope.py` lulus dalam mode `--check`;
6. `msaf/tests/test_fence_registry.py` lulus and hash `T-2026-0051` cocok;
7. JSON envelope menunjukkan `max_rad + slack <= 10^-100` and
   `delta < lambda_min`;
8. no ada `sorry`/`admit`/`axiom` in file Lean baru.

## 5. Kriteria falsifikasi

P1 **FAILED** jika salah satu terjadi:

- ada entry Arb with `rad > 10^-100` (setelah slack serialisasi);
- `delta >= lambda_min`;
- teorema bergantung on `sorryAx` or aksioma proyek;
- hash registry no cocok;
- envelope dihitung with `float64` for radius;
- report menyebut result ini sebagai bukti RH, Weil positivity, tail analitik,
  or positivity seluruh matriks Guinandâ€“Weil.

## 6. Yang no diklaim

- Tidak ada klaim bahwa `A0` (matriks center) benar-benar positif-definit
  berdasarkan Lean; premisnya berasal dari sertifikat Arb eksternal.
- Tidak ada propagasi error entry ke eigenvalue selain melalui limit
  kuadratik which menjadi hipotesis teorema.
- Tidak ada klaim `|XC(n)| = O(1/n^2)`; itu P2.
- Tidak ada klaim tentang spektrum zeta, zeros, or RH.
- `epsilon = 10^-100` adalah limit entry, bukan limit tail analitik.

## 7. Urutan eksekusi

1. Commit and push dokumen ini **sebelum** menulis kode P1.
2. Implementasi `msaf/entry_error_envelope.py` and JSON.
3. Implementasi Lean and kompilasi.
4. Audit aksioma, gate, registry, test.
5. Commit kode + artefak + registry; push.

Dokumen ini no boleh diubah setelah kode P1 dimulai, kecuali with
amendment bertanggal which menjelaskan penyimpangan and alasannya.


