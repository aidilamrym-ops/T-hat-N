# Pra-registrasi Paket 8 — L5 limit step (bersyarat) untuk `f_k(x)=x^{-(k+1)}`

**Tanggal:** 2026-10-20
**Status:** scope DIKUNCI sebelum implementasi
**Berkas target:** `formal_bridge/IntegralComparisonLimit.v` (baru)
**Dependensi:** `formal_bridge/IntegralComparison.v` (Paket 7, registry `A-2026-0012`)
**Registry yang direncanakan:** `A-2026-0013`

## 1. Latar

Paket 7 membuktikan **finite core** L5 untuk `f_k(x)=1/x^{k+1}`
(`k >= 1`, `N >= 1`):

```text
whole_val k N M <= sum_{i<M} f_k(N+i)
sum_{i<M} f_k(N+i+1) <= whole_val k N M
```

L5 penuh membutuhkan langkah limit `M -> infinity`. Paket 8 mengunci
**langkah limit itu saja**, dalam bentuk bersyarat: ketiga barisan
(integral dari `N`, integral dari `N+1`, dan tail sum dari `N+1`)
diasumsikan konvergen. Eksistensi limit **tidak** dibuktikan di sini;
itu Paket 9.

Pemisahan ini disengaja: bagian baru yang substantif adalah lemma
_order limit_ (`Un_cv_le`), yang tidak tersedia di fragmen stdlib Coq
yang dipakai. Dengan mengisolasi langkah limit, Paket 8 kecil, dapat
diaudit, dan menjadi fondasi Paket 9.

## 2. Pernyataan yang akan dibuktikan

Definisi:

```coq
Definition HN_succ (N : nat) (HN : (1 <= N)%nat) : (1 <= N + 1)%nat :=
  Nat.le_trans HN (Nat.le_succ_diag_r N).
```

Hasil yang dikunci:

1. `Un_cv_le` — jika `u_n <= v_n` untuk semua `n`, `u_n -> lu`, dan
   `v_n -> lv`, maka `lu <= lv`.
2. `tail_sum_le_whole` — untuk `k >= 1`, `N >= 1`:
   `sum_upto (fun i => fk k (INR (N+1+i))) M <= whole_val k N M HN`.
3. `whole_succ_le_tail_sum` — untuk `k >= 1`, `N >= 1`:
   `whole_val k (N+1) M (HN_succ N HN)
      <= sum_upto (fun i => fk k (INR (N+1+i))) M`.
4. **Teorema utama** `integral_comparison_power_limit` — untuk
   `k >= 1`, `N >= 1`, dan limit `L_N, L_N1, L_S`:

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

dengan ketiga limit diberikan sebagai hipotesis, bukan dibuktikan.

## 3. Metode yang dikunci

- Impor **hanya** `IntegralComparison` (Paket 7) dan stdlib:
  `Coq.Reals.Reals`, `Coq.Reals.Rseries`, `Coq.micromega.Lia`,
  `Coq.micromega.Lra`.
- `tail_sum_le_whole`: teorema finite Paket 7 pada `N`, ditambah
  `sum_upto_ext` untuk menyamakan indeks `N+1+i` dan `N+i+1`.
- `whole_succ_le_tail_sum`: teorema finite Paket 7 pada `N+1`.
- `Un_cv_le`: bukti epsilon langsung. Andaikan `lv < lu`; ambil
  `eps = (lu-lv)/2`; untuk `n` cukup besar, `u_n > (lu+lv)/2` dan
  `v_n < (lu+lv)/2`, bertentangan dengan `u_n <= v_n`.
- Teorema utama: gabungkan kedua ketaksamaan finite dengan `Un_cv_le`.
- **Tanpa** `Un_cv_crit`, **tanpa** `PseriesL2`, **tanpa** `Rpower`,
  **tanpa** integral tak-hingga, **tanpa** asumsi proyek.

## 4. Kriteria sukses

- `coqc` exit 0; `coqchk` exit 0 "Modules were successfully checked";
  semua hasil baru muncul di keluaran kernel; receipt deterministik
  (dua capture byte-identik).
- `Print Assumptions` hanya aksioma stdlib `Coq.Reals`. **Jumlah persis
  dicatat.** Ekspektasi: **empat** aksioma yang sama dengan Paket 7
  (`sig_forall_dec`, `sig_not_dec`, `functional_extensionality_dep`,
  `Classical_Prop.classic`), karena `RiemannInt` tetap dipakai lewat
  dependensi. Tidak ada aksioma proyek.
- Guard statis + mutasi negatif; registry `A-2026-0013`; HANDOFF;
  CI hijau (guard statis; CI tidak punya Coq).
- `freeze.py --verify` tetap OK setelah dokumen/registry diperbarui.

## 5. Kriteria gagal (dicatat, tidak disembunyikan)

- Bila `Un_cv_le` atau langkah limit ternyata membutuhkan aksioma di
  luar empat aksioma stdlib yang tercatat, implementasi berhenti dan
  addendum pra-registrasi baru dibuat. Hasil parsial dicatat sebagai
  PARTIAL/negatif, bukan diklaim selesai.
- Bila owner mensyaratkan **literal tiga** aksioma, Paket 8 tidak
  memenuhi kriteria itu; jalur `RiemannInt` mewarisi
  `Classical_Prop.classic`. Ini keputusan owner, bukan sesuatu yang
  disembunyikan.
- Tidak ada klaim "L5 selesai". Paket 8 hanya langkah limit bersyarat.

## 6. Batas

- **Bersyarat**: eksistensi limit tidak dibuktikan. Paket 9 akan
  membuktikannya untuk `f_k` memakai `Un_cv_crit` dan
  `pseries_L2_integer` (`A-2026-0010`).
- Hanya `f_k(x)=x^{-(k+1)}`, `k >= 1`; bukan `f` umum, bukan eksponen
  real `p > 1`.
- Bukan L3/L4; bukan penutupan `[J]` periodic-box `A-2026-0007`.
- Tidak menyentuh zeta/Weil/RH/P≠NP; tidak ada klaim fisik; bukan peer
  review.
