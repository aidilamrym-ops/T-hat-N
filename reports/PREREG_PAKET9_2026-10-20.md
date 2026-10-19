# Pra-registrasi Paket 9 — L5 infinite (unconditional) untuk `f_k(x)=x^{-(k+1)}`

**Tanggal:** 2026-10-20
**Status:** scope DIKUNCI sebelum implementasi
**Berkas target:** `formal_bridge/IntegralComparisonInfinite.v` (baru)
**Dependensi:** `formal_bridge/IntegralComparison.v` (Paket 7, `A-2026-0012`),
`formal_bridge/IntegralComparisonLimit.v` (Paket 8, `A-2026-0013`),
`formal_bridge/PseriesL2.v` (Paket 6, `A-2026-0010`)
**Registry yang direncanakan:** `A-2026-0014`

## 1. Latar

Paket 7 membuktikan finite core L5; Paket 8 membuktikan langkah limit
**bersyarat** dengan tiga hipotesis `Un_cv`. Paket 9 menutup celah
eksistensi untuk instance pilot `f_k(x)=x^{-(k+1)}` (`k >= 1`,
`N >= 1`):

- limit tail sum `Σ_{i<M} f_k(N+1+i)` diperoleh dari
  `pseries_L2_integer` (`A-2026-0010`) setelah bridging `psum` ke
  `tail_sum`;
- limit integral `∫_N^{N+M} f_k` diperoleh dari `Un_cv_crit`
  (monoton + terbatas), dengan batas `f_k(N) + L_S`;
- kedua hasil digabung dengan teorema bersyarat Paket 8.

Hasilnya adalah L5 penuh untuk `f_k`:

```text
∫_{N+1}^∞ f_k ≤ Σ_{n>N} f_k(n) ≤ ∫_N^∞ f_k
```

dalam bentuk eksistensi limit dan ketaksamaan dua sisi.

## 2. Pernyataan yang akan dibuktikan

Definisi bantu:

```coq
Definition tail_sum (k N M : nat) : R :=
  sum_upto (fun i => fk k (INR (N + 1 + i))) M.
```

Hasil kunci:

1. `tail_sum_cv` — untuk `k >= 1`, `N >= 1`:
   `exists L, Un_cv (fun M => tail_sum k N M) L`.
2. `whole_val_cv` — untuk `k >= 1`, `N >= 1`:
   `exists L, Un_cv (fun M => whole_val k N M HN) L`.
3. **Teorema utama** `integral_comparison_power_infinite` — untuk
   `k >= 1`, `N >= 1`:

```coq
exists L_N L_N1 L_S : R,
  Un_cv (fun M => whole_val k N M HN) L_N /\
  Un_cv (fun M => whole_val k (N + 1) M (HN_succ N HN)) L_N1 /\
  Un_cv (fun M => tail_sum k N M) L_S /\
  L_N1 <= L_S /\ L_S <= L_N.
```

Ini adalah L5 pilot yang **unconditional** untuk `f_k`: ketiga limit
dibuktikan ada, dan limit integral `N+1` ≤ limit tail sum ≤ limit
integral `N`.

## 3. Metode yang dikunci

- Impor hanya stdlib yang diperlukan, `IntegralComparison`,
  `IntegralComparisonLimit`, dan `PseriesL2` (modul beku).
- **Bridging sum:** `sum_f_R0 g M = sum_upto g (S M)`,
  `pterm k n = fk k (INR n)`, dan `psum k N M = tail_sum k N (S M)`.
  `Un_cv (psum)` dari `pseries_L2_integer` diubah menjadi
  `Un_cv (tail_sum)` dengan lemma shift `Un_cv_tail_shift`.
- **Monotonisitas integral:** `whole_val k N (S M) =
  whole_val k N M + unit_val ...`; `unit_val >= 0` dari
  `integral_unit_lower` dan positivitas `fk`.
- **Batas integral:** teorema finite Paket 7 pada `N` memberi
  `whole_val k N M <= Σ_{i<M} f_k(N+i)`; identitas
  `Σ_{i<M} f_k(N+i) = f_k(N) + tail_sum k N (M-1)` dan
  `sum_incr` memberi batas `f_k(N) + L_S`. Jadi `Un_cv_crit` berlaku.
- **Teorema utama:** gabungkan `whole_val_cv` untuk `N` dan `N+1`,
  `tail_sum_cv`, dan `integral_comparison_power_limit` (Paket 8).
- **Tanpa** `Rpower`, **tanpa** `f` umum, **tanpa** integral tak-hingga
  sebagai definisi baru (limit diwakili oleh `Un_cv`), **tanpa** asumsi
  proyek.

## 4. Kriteria sukses

- `coqc` exit 0 (dependensi-dependensi + modul baru); `coqchk` exit 0
  "Modules were successfully checked"; semua hasil baru muncul di
  keluaran kernel; receipt deterministik (dua capture byte-identik).
- `Print Assumptions` hanya aksioma stdlib. **Jumlah persis dicatat.**
  Ekspektasi: **empat** aksioma yang sama dengan Paket 7/8
  (`sig_forall_dec`, `sig_not_dec`, `functional_extensionality_dep`,
  `Classical_Prop.classic`), karena `RiemannInt` tetap dipakai lewat
  dependensi. Tidak ada aksioma proyek.
- Guard statis + mutasi negatif; registry `A-2026-0014`; HANDOFF;
  CI hijau (guard statis; CI tidak punya Coq).
- `freeze.py --verify` tetap OK setelah dokumen/registry diperbarui.

## 5. Kriteria gagal (dicatat, tidak disembunyikan)

- Bila `Un_cv_crit`, `pseries_L2_integer`, atau bridging sum membutuhkan
  aksioma di luar empat aksioma stdlib yang tercatat, implementasi
  berhenti dan addendum pra-registrasi baru dibuat. Hasil parsial
  dicatat sebagai PARTIAL/negatif, bukan diklaim selesai.
- Bila owner mensyaratkan **literal tiga** aksioma, Paket 9 tidak
  memenuhi kriteria itu; jalur `RiemannInt` mewarisi
  `Classical_Prop.classic`. Ini keputusan owner, bukan sesuatu yang
  disembunyikan.
- Tidak ada klaim L5 untuk `f` umum atau eksponen real; hanya instance
  pilot `f_k` dengan `k >= 1`.

## 6. Batas

- Hanya `f_k(x)=x^{-(k+1)}`, `k >= 1`, `N >= 1`; bukan `f` umum, bukan
  eksponen real `p > 1` (`Rpower`).
- Bukan L3/L4; bukan penutupan `[J]` periodic-box `A-2026-0007`.
- Tidak menyentuh zeta/Weil/RH/P≠NP; tidak ada klaim fisik; bukan peer
  review.
- Gate anti-circularity tetap `TOOL NOT RUN` sampai jalur Lean/SMT
  disusun setelah paket-paket ini selesai; gate itu tidak dihitung
  sebagai sukses.
