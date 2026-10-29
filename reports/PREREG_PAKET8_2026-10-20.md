# Pra-registrasi Paket 8 â€” L5 limit step (bersyarat) for `f_k(x)=x^{-(k+1)}`

**Tanggal:** 2026-10-20
**Status:** scope DIKUNCI sebelum implementasi
**Berkas target:** `formal_bridge/IntegralComparisonLimit.v` (baru)
**Dependensi:** `formal_bridge/IntegralComparison.v` (Paket 7, registry `A-2026-0012`)
**Registry which direncanakan:** `A-2026-0013`

## 1. Latar

Paket 7 membuktikan **finite core** L5 for `f_k(x)=1/x^{k+1}`
(`k >= 1`, `N >= 1`):

```text
whole_val k N M <= sum_{i<M} f_k(N+i)
sum_{i<M} f_k(N+i+1) <= whole_val k N M
```

L5 penuh membutuhkan step limit `M -> infinity`. Paket 8 mengunci
**step limit itu saja**, dalam bentuk bersyarat: ketiga barisan
(integral dari `N`, integral dari `N+1`, and tail sum dari `N+1`)
diasumsikan konvergen. Eksistensi limit **no** dibuktikan in sini;
itu Paket 9.

Pemisahan ini disengaja: section baru which substantif adalah lemma
_order limit_ (`Un_cv_le`), which no tersedia in fragmen stdlib Coq
which dipakai. Dengan mengisolasi step limit, Paket 8 kecil, dapat
diaudit, and menjadi fondasi Paket 9.

## 2. Pernyataan which akan dibuktikan

Definisi:

```coq
Definition HN_succ (N : nat) (HN : (1 <= N)%nat) : (1 <= N + 1)%nat :=
  Nat.le_trans HN (Nat.le_succ_diag_r N).
```

Hasil which dikunci:

1. `Un_cv_le` â€” jika `u_n <= v_n` for semua `n`, `u_n -> lu`, and
   `v_n -> lv`, maka `lu <= lv`.
2. `tail_sum_le_whole` â€” for `k >= 1`, `N >= 1`:
   `sum_upto (fun i => fk k (INR (N+1+i))) M <= whole_val k N M HN`.
3. `whole_succ_le_tail_sum` â€” for `k >= 1`, `N >= 1`:
   `whole_val k (N+1) M (HN_succ N HN)
      <= sum_upto (fun i => fk k (INR (N+1+i))) M`.
4. **Teorema utama** `integral_comparison_power_limit` â€” for
   `k >= 1`, `N >= 1`, and limit `L_N, L_N1, L_S`:

```coq
Un_cv (fun M => whole_val k N M HN) L_N ->
Un_cv (fun M => whole_val k (N + 1) M (HN_succ N HN)) L_N1 ->
Un_cv (fun M => sum_upto (fun i => fk k (INR (N + 1 + i))) M) L_S ->
L_N1 <= L_S /\ L_S <= L_N.
```

Ini adalah L5 dalam bentuk limit bersyarat:

```text
int_{N+1}^inf f_k <= sum_{n>N} f_k(n) <= int_N^inf f_k
```

with ketiga limit diberikan sebagai hipotesis, bukan dibuktikan.

## 3. Metode which dikunci

- Impor **hanya** `IntegralComparison` (Paket 7) and stdlib:
  `Coq.Reals.Reals`, `Coq.Reals.Rseries`, `Coq.micromega.Lia`,
  `Coq.micromega.Lra`.
- `tail_sum_le_whole`: teorema finite Paket 7 on `N`, ditambah
  `sum_upto_ext` for menyamakan indeks `N+1+i` and `N+i+1`.
- `whole_succ_le_tail_sum`: teorema finite Paket 7 on `N+1`.
- `Un_cv_le`: bukti epsilon langsung. Andaikan `lv < lu`; ambil
  `eps = (lu-lv)/2`; for `n` cukup besar, `u_n > (lu+lv)/2` and
  `v_n < (lu+lv)/2`, bertentangan with `u_n <= v_n`.
- Teorema utama: gabungkan kedua ketaksamaan finite with `Un_cv_le`.
- **Tanpa** `Un_cv_crit`, **tanpa** `PseriesL2`, **tanpa** `Rpower`,
  **tanpa** integral tak-hingga, **tanpa** asumsi proyek.

## 4. Kriteria sukses

- `coqc` exit 0; `coqchk` exit 0 "Modules were successfully checked";
  semua result baru muncul in keluaran kernel; receipt deterministik
  (dua capture byte-identik).
- `Print Assumptions` hanya aksioma stdlib `Coq.Reals`. **Jumlah persis
  dicatat.** Ekspektasi: **empat** aksioma which sama with Paket 7
  (`sig_forall_dec`, `sig_not_dec`, `functional_extensionality_dep`,
  `Classical_Prop.classic`), karena `RiemannInt` tetap dipakai lewat
  dependensi. Tidak ada aksioma proyek.
- Guard statis + mutasi negatif; registry `A-2026-0013`; HANDOFF;
  CI hijau (guard statis; CI no punya Coq).
- `freeze.py --verify` tetap OK setelah dokumen/registry diperbarui.

## 5. Kriteria gagal (dicatat, no disembunyikan)

- Bila `Un_cv_le` or step limit ternyata membutuhkan aksioma in
  luar empat aksioma stdlib which tercatat, implementasi berhenti and
  addendum pra-registrasi baru created. Hasil parsial dicatat sebagai
  PARTIAL/negatif, bukan diklaim selesai.
- Bila owner mensyaratkan **literal tiga** aksioma, Paket 8 no
  memenuhi kriteria itu; jalur `RiemannInt` mewarisi
  `Classical_Prop.classic`. Ini keputusan owner, bukan sesuatu which
  disembunyikan.
- Tidak ada klaim "L5 selesai". Paket 8 hanya step limit bersyarat.

## 6. Batas

- **Bersyarat**: eksistensi limit no dibuktikan. Paket 9 akan
  membuktikannya for `f_k` memakai `Un_cv_crit` and
  `pseries_L2_integer` (`A-2026-0010`).
- Hanya `f_k(x)=x^{-(k+1)}`, `k >= 1`; bukan `f` umum, bukan eksponen
  real `p > 1`.
- Bukan L3/L4; bukan penutupan `[J]` periodic-box `A-2026-0007`.
- Tidak menyentuh zeta/Weil/RH/Pâ‰ NP; no ada klaim fisik; bukan peer
  review.


