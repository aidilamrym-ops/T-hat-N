# Pra-registrasi: entry-error envelope dan teorema perturbasi finit

**Status:** PRE-REG, dikunci sebelum kode P1.
**Tanggal:** 2026-10-26.
**Basis commit:** `5fea118` (P0).
**Bidang:** Guinand–Weil Stage 2/3, finite perturbation only.
**Bukan:** bukti RH, bukti Weil positivity, bukti tail analitik, atau bukti
bahwa Lean mendiagonalisasi matriks.

## 1. Pertanyaan yang dijawab

Diberikan matriks ball Arb `A` dari `build_arb_tau(c=13, N=160, prec=6000)`
dan batas bawah eigenvalue `lambda_min` yang sudah tersertifikasi, dapatkah
kita:

1. menghitung envelope error entry `epsilon` sebagai batas atas radius ball
   setiap entry, dengan serialisasi desimal (bukan float64);
2. membuktikan di kernel Lean bahwa jika `A0` positif-definit dengan batas
   kuadratik `lambda`, dan `E` adalah perturbasi simetris dengan
   `|E_ij| <= epsilon`, maka `A0 + E` positif-definit selama
   `dim * epsilon < lambda`;
3. menginstansiasi ketaksamaan aritmetiknya untuk `dim = 321`,
   `epsilon = 10^-100`, dan `lambda = gw_lambda_min`.

Jawaban yang diklaim hanya untuk tiga hal di atas. Matriks Arb itu sendiri
tetap disertifikasi oleh run `arb_mat.eig` eksternal, bukan oleh Lean.

## 2. Konstanta yang dikunci sebelum pengukuran

Threshold entry envelope **dipilih sebelum** menjalankan `build_arb_tau`:

```text
epsilon = 10^-100
dim     = 321
delta   = dim * epsilon = 321 * 10^-100 = 3.21 * 10^-98
lambda  = gw_lambda_min = 3123458832662237 / 10^74
```

Alasan: presisi 6000 bit memberi radius relatif sekitar `10^-1800`; `10^-100`
jauh di atas noise numerik tetapi masih jauh di bawah `lambda ~ 3.12e-59`.
Threshold tidak boleh dinaikkan setelah melihat hasil. Jika ada entry dengan
radius `> 10^-100`, kampanye P1 **FAILED** dan tidak boleh mengklaim envelope.

## 3. Artefak yang akan dibuat

### 3.1 `msaf/entry_error_envelope.py`

- Mengimpor `build_arb_tau` dari checkout eksternal
  `C:/Users/usER/oracle-toe/GUINAND_WEIL/source_arb_ldlt_certify.py`
  melalui `GW_DIR`, dengan path yang dapat di-override.
- Membangun `A, dim = build_arb_tau(13, 160, 6000)`.
- Untuk setiap `(i,j)`, mencatat `mid` dan `rad` sebagai **string desimal**
  dengan presisi cukup; tidak menggunakan `float()` untuk radius.
- Menghitung `max_rad` dan `max_rad + serialization_slack`, dengan
  `serialization_slack = 10^-120` per entry.
- Gagal (`exit 1`) jika `dim != 321`, `max_rad + slack > 10^-100`, atau ada
  entry non-finite.
- Menulis `reports/entry_error_envelope_c13_n160.json` berisi:
  `c`, `N`, `dim`, `prec_bits`, `epsilon`, `delta`, `lambda_min`,
  `max_entry_radius_upper`, `max_entry_radius_plus_slack`, `n_entries`,
  `digest_sha256` dari dump kanonik `(i,j,mid,rad)`, dan `verdict`.
- Menyediakan mode `--check` yang memverifikasi JSON yang sudah ada tanpa
  membangun ulang matriks (untuk CI/test cepat).

### 3.2 `lean/Stage_5_EntryError_Perturbation.lean`

Teorema yang harus diperiksa kernel:

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
`epsilon = 10^-100`, `delta = 321 * 10^-100`, dan `lambda = gw_lambda_min`.
Teorema ini **menerima** `A.PosDef` dan batas kuadratik `A` sebagai hipotesis;
ia tidak mengklaim membuktikan premis matriks Arb dari Lean.

### 3.3 Registry

Entri baru `T-2026-0051`, bukan penulisan ulang `T-2026-0050`. Entri harus
memuat batas klaim, perintah verifikasi, hash `sha256LF`, dan relasi ke
`T-2026-0050` serta `reports/GW_TAIL_CONSTANTS_2026-10-26.md`.

### 3.4 Laporan

`reports/ENTRY_ERROR_ENVELOPE_2026-10-26.md` memuat:
- angka `max_rad`, `epsilon`, `delta`, `lambda`;
- bukti bahwa `delta < lambda` (aritmetik eksak);
- output `#print axioms`;
- batas klaim yang eksplisit.

## 4. Kriteria penerimaan

P1 dianggap PASS hanya jika semua ini benar:

1. `lake build` di `lean/` exit 0;
2. `lake env lean ../reports/RH_SCAFFOLD_NOTES/Stage_4_Containment_Proof.lean`
   exit 0 (regresi);
3. `#print axioms` untuk kelima deklarasi baru hanya memuat
   `propext`, `Classical.choice`, `Quot.sound` (atau subset);
4. anti-circularity gate `check` memberi PASS dengan
   `FAIL=0 NOT_RUN=0 SKIP=0`;
5. `msaf/tests/test_entry_error_envelope.py` lulus dalam mode `--check`;
6. `msaf/tests/test_fence_registry.py` lulus dan hash `T-2026-0051` cocok;
7. JSON envelope menunjukkan `max_rad + slack <= 10^-100` dan
   `delta < lambda_min`;
8. tidak ada `sorry`/`admit`/`axiom` di berkas Lean baru.

## 5. Kriteria falsifikasi

P1 **FAILED** jika salah satu terjadi:

- ada entry Arb dengan `rad > 10^-100` (setelah slack serialisasi);
- `delta >= lambda_min`;
- teorema bergantung pada `sorryAx` atau aksioma proyek;
- hash registry tidak cocok;
- envelope dihitung dengan `float64` untuk radius;
- laporan menyebut hasil ini sebagai bukti RH, Weil positivity, tail analitik,
  atau positivity seluruh matriks Guinand–Weil.

## 6. Yang tidak diklaim

- Tidak ada klaim bahwa `A0` (matriks center) benar-benar positif-definit
  berdasarkan Lean; premisnya berasal dari sertifikat Arb eksternal.
- Tidak ada propagasi error entry ke eigenvalue selain melalui batas
  kuadratik yang menjadi hipotesis teorema.
- Tidak ada klaim `|XC(n)| = O(1/n^2)`; itu P2.
- Tidak ada klaim tentang spektrum zeta, zeros, atau RH.
- `epsilon = 10^-100` adalah batas entry, bukan batas tail analitik.

## 7. Urutan eksekusi

1. Commit dan push dokumen ini **sebelum** menulis kode P1.
2. Implementasi `msaf/entry_error_envelope.py` dan JSON.
3. Implementasi Lean dan kompilasi.
4. Audit aksioma, gate, registry, test.
5. Commit kode + artefak + registry; push.

Dokumen ini tidak boleh diubah setelah kode P1 dimulai, kecuali dengan
amendment bertanggal yang menjelaskan penyimpangan dan alasannya.
