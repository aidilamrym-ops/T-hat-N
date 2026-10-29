# Coq: L5 infinite (unconditional) â€” limit integralâ€“deret for `f_k(x)=x^{-(k+1)}` (2026-10-20)

**Paket:** 9 (pra-registrasi baru
[`reports/PREREG_PAKET9_2026-10-20.md`](PREREG_PAKET9_2026-10-20.md))
**Berkas utama:** [`formal_bridge/IntegralComparisonInfinite.v`](../formal_bridge/IntegralComparisonInfinite.v)
**Dependensi:** [`formal_bridge/IntegralComparison.v`](../formal_bridge/IntegralComparison.v)
(Paket 7, `A-2026-0012`),
[`formal_bridge/IntegralComparisonLimit.v`](../formal_bridge/IntegralComparisonLimit.v)
(Paket 8, `A-2026-0013`),
[`formal_bridge/PseriesL2.v`](../formal_bridge/PseriesL2.v) (Paket 6,
`A-2026-0010`); ketiganya **no diubah**
**Berkas pendamping:** `formal_bridge/check_integral_infinite.sh`,
`formal_bridge/IntegralComparisonInfinite.receipt.txt`,
`msaf/tests/test_coq_bridge_integral_infinite.py`
**Toolchain:** Coq 8.20.1 (OCaml 4.14.2), `/root/.opam/4.14.2/bin/`
**Registry:** `A-2026-0014`

## 1. Ringkasan status

Paket 9 **selesai and tersegel**. Berkas baru
`IntegralComparisonInfinite.v` membuktikan **17 result**, with teorema
utama **`integral_comparison_power_infinite`**: for `k â‰¥ 1` and
`N â‰¥ 1`, **ketiga limit ada** and memenuhi

```text
L_{N+1} <= L_S <= L_N,
```

yaitu L5 pilot which **unconditional** for `f_k`:

```text
âˆ«_{N+1}^âˆž f_k â‰¤ Î£_{n>N} f_k(n) â‰¤ âˆ«_N^âˆž f_k.
```

Limit integral tak-hingga diwakili oleh nilai limit `Un_cv`; no ada
definisi baru `âˆ«_N^âˆž` and no ada klaim for `f` umum or eksponen
real. `coqc` exit 0 for keempat modul (tiga dependensi + modul baru);
`coqchk` exit 0 "Modules were successfully checked"; 17/17 result muncul
in keluaran kernel; receipt deterministik 178 baris (dua capture
byte-identik), sha256
`39ad870db3b2fec94745ef95a26161e108e8642d2323666bc856da5954fd056d`.

`Print Assumptions` teorema utama menunjukkan **tepat empat aksioma
stdlib** which sama with Paket 7/8: `sig_forall_dec`, `sig_not_dec`,
`functional_extensionality_dep`, `Classical_Prop.classic`. **Tidak ada
aksioma proyek.** Peta per result dicatat in Â§5; beberapa result murni
kombinatorik hanya membawa 1â€“2 aksioma, sedangkan result which menyentuh
`RiemannInt`, `Un_cv_crit`, or teorema bersyarat Paket 8 membawa
empat.

## 2. Pernyataan which dibuktikan

```coq
Definition tail_sum (k N M : nat) : R :=
  sum_upto (fun i => fk k (INR (N + 1 + i))) M.

Lemma tail_sum_cv :
  forall (k N : nat),
    (1 <= k)%nat -> (1 <= N)%nat ->
    exists L : R, Un_cv (fun M => tail_sum k N M) L.

Lemma whole_val_cv :
  forall (k N : nat) (HN : (1 <= N)%nat),
    (1 <= k)%nat ->
    exists L : R, Un_cv (fun M => whole_val k N M HN) L.

Theorem integral_comparison_power_infinite :
  forall (k N : nat) (HN : (1 <= N)%nat),
    (1 <= k)%nat ->
    exists L_N L_N1 L_S : R,
      Un_cv (fun M => whole_val k N M HN) L_N /\
      Un_cv (fun M => whole_val k (N + 1) M (HN_succ N HN)) L_N1 /\
      Un_cv (fun M => tail_sum k N M) L_S /\
      L_N1 <= L_S /\ L_S <= L_N.
```

## 3. Metode

1. **Tail sum dari p-series.** `pseries_L2_integer` (`A-2026-0010`)
   memberi `Un_cv (fun M => psum k N M) L`. Bridging:
   `pterm k n = fk k (INR n)`, `psum k N M = tail_sum k N (S M)`.
   Lemma shift `Un_cv_tail_shift` mengubah konvergensi barisan
   `tail_sum (S M)` menjadi `tail_sum M`; hasilnya `tail_sum_cv`.
2. **Monotonisitas integral.** `whole_val k N (S M) = whole_val k N M +
   unit_val ...`; `unit_val >= 0` dari `integral_unit_lower` and
   positivitas `fk`; hasilnya `whole_val_growing`.
3. **Batas integral.** Teorema finite Paket 7 on `N`:
   `whole_val k N M â‰¤ Î£_{i<M} f_k(N+i)`. Identitas
   `Î£_{i<M} f_k(N+i) = f_k(N) + tail_sum k N (M-1)` and `sum_incr`
   memberi limit seragam `f_k(N) + L_S`; jadi `Un_cv_crit` berlaku and
   `whole_val_cv` terbukti.
4. **Teorema utama.** Gabungkan `whole_val_cv` for `N` and `N+1`,
   `tail_sum_cv`, lalu teorema bersyarat Paket 8
   `integral_comparison_power_limit`.

Tidak dipakai: `Rpower`, `FTC_Riemann`, `C1_fun`, `RiemannInt_P`,
integral tak-hingga sebagai definisi, or aksioma proyek. Dependensi
Paket 7/8/6 diimpor apa adanya; file-file itu no diubah.

## 4. Bukti eksekusi (verbatim, potongan)

```text
coqc:   /root/.opam/4.14.2/bin/coqc
coqchk: /root/.opam/4.14.2/bin/coqchk
coqc PseriesL2 (dependency) exit: 0
coqc IntegralComparison (dependency) exit: 0
coqc IntegralComparisonLimit (dependency) exit: 0
coqc IntegralComparisonInfinite exit: 0
coqchk exit: 0
coqchk final line: Modules were successfully checked
coqchk full log lines: 48198
results in IntegralComparisonInfinite.v: 17
results checked by coqchk: 17
Print Assumptions sections: 17 (17 Axioms, 0 Closed)
audit axiom names: ClassicalDedekindReals.sig_forall_dec ClassicalDedekindReals.sig_not_dec Classical_Prop.classic FunctionalExtensionality.functional_extensionality_dep
final audit block (main theorem): ClassicalDedekindReals.sig_forall_dec ClassicalDedekindReals.sig_not_dec Classical_Prop.classic FunctionalExtensionality.functional_extensionality_dep
```

(Baris `audit axiom names:` and `final audit block` in receipt memuat satu
spasi trailing dari `tr`; isi hash receipt adalah byte which tersegel.)

## 5. Peta trusted base per result

| # | Hasil | Aksioma stdlib |
|---|---|---|
| 1 | `sum_f_R0_eq_sum_upto` | 2 |
| 2 | `sum_f_R0_ext` | 1 |
| 3 | `pterm_eq_fk` | 2 |
| 4 | `psum_eq_sum_f_R0_fk` | 2 |
| 5 | `psum_eq_tail_sum_succ` | 2 |
| 6 | `Un_cv_ext_local` | 2 |
| 7 | `Un_cv_tail_shift` | 2 |
| 8 | `Un_cv_shift_succ` | 2 |
| 9 | `tail_sum_cv` | 3 |
| 10 | `fk_nonneg` | 2 |
| 11 | `unit_val_nonneg` | 4 |
| 12 | `whole_val_growing` | 4 |
| 13 | `upper_sum_succ` | 2 |
| 14 | `upper_sum_bound` | 2 |
| 15 | `whole_val_bound` | 4 |
| 16 | `whole_val_cv` | 4 |
| 17 | `integral_comparison_power_infinite` | **4** |

Semua 17 blok adalah `Axioms` (no ada `Closed`). Himpunan empat
aksioma final sama with Paket 7/8. `sum_f_R0_ext` hanya memerlukan
`sig_forall_dec`; `tail_sum_cv` menambahkan `sig_not_dec` lewat
`pseries_L2_integer`; result which menyentuh `RiemannInt`/`Un_cv_crit`
membawa `Classical_Prop.classic`.

## 6. Trusted base: deviasi empat aksioma (diwarisi)

- Paket 9 memakai `RiemannInt` lewat dependensi Paket 7/8; karena itu
  empat aksioma stdlib tetap muncul. Ini **diwarisi**, bukan aksioma baru.
- Jika owner mensyaratkan literal tiga aksioma, Paket 9 **no**
  memenuhi syarat itu; jalur integral Riemann ini no dapat
  menghindari `Classical_Prop.classic`.
- Tidak ada `Axiom`, `Parameter`, `Admitted`, or `admit` in file baru
  (dijaga guard). `Coq.Reals` tetap aksiomatik: ini pernyataan tentang
  trusted base relatif, bukan bukti konsistensi.

## 7. Anti-circularity gate: **TOOL NOT RUN** (bukan sukses)

Gate anti-circularity lokal tetap no menemukan file `.lean`/`.smt2`:

```text
ANTI-CIRCULARITY GATE [check]
  NOT RUN  NO_LEAN_FILES: no .lean input matched
  result: FAIL=0  NOT_RUN=1  SKIP=0
  verdict: TOOL NOT RUN
```

Verdict = `TOOL NOT RUN` (exit 2 menurut kontrak `gate.py`; harness
menampilkan semua kode non-nol sebagai 1). Gate **no berlaku** for
artefak Coq and **no dihitung sebagai sukses**. Kompensasi:
`coqchk` (kernel independen) + `Print Assumptions` per result + guard
statis with mutasi negatif. Jalur agar gate benar-benar berjalan
disusun setelah paket-paket ini selesai.

## 8. Uji negatif guard

`python -m pytest msaf/tests/test_coq_bridge_integral_infinite.py -q` â€”
**5 uji**, semuanya hijau; **18 mutasi negatif** tertangkap:

1. `Admitted.` polos;
2. `Axiom cheat : True.`;
3. satu baris `Print Assumptions` dihapus;
4. `Rpower` diselundupkan;
5. `FTC_Riemann` diselundupkan;
6. result terkunci in-rename;
7. limit lunak dilemahkan (`<=` â†’ `<`);
8. hipotesis `(1 <= k)` dihapus dari statement utama;
9. eksistensi tiga limit diciutkan menjadi satu;
10. `Rpower` dimasukkan ke statement;
11. aksioma proyek keempat in blok audit;
12. `Classical_Prop.classic` dihapus dari blok final;
13. `sig_not_dec` dipindah ke section which seharusnya hanya 2 aksioma;
14. satu section audit dihapus;
15. blok final ditukar with blok dua-aksioma;
16. komentar Coq tak tertutup;
17. impor `PseriesL2` dihapus;
18. `Un_cv_crit` dihapus (bukan sekadar in-rename).

Guard juga verifying impor which diizinkan, definisi/statement lock,
17 result dalam urutan source, 17 `Print Assumptions`, receipt 17/17, peta
aksioma per result persis, and no ada nama aksioma proyek.

## 9. Batas

- **Unconditional hanya for `f_k`**: `k â‰¥ 1`, `N â‰¥ 1`; bukan `f`
  umum, bukan eksponen real `p > 1` (`Rpower`).
- Limit tak-hingga diwakili oleh `Un_cv`; no ada definisi integral
  tak-hingga baru and no ada klaim tentang nilai eksplisit limit.
- Bukan L3/L4; bukan penutupan `[J]` periodic-box `A-2026-0007` (tetap
  OPEN; objek berbeda).
- CI no punya toolchain Coq: which dijalankan CI hanya guard statis,
  bukan kernel.
- Tidak menyentuh zeta/Weil/RH/Pâ‰ NP; no ada klaim fisik; bukan peer
  review.

## 10. Reproduksi and registry

```bash
# in WSL/Ubuntu with switch opam 4.14.2
bash formal_bridge/check_integral_infinite.sh
python -m pytest msaf/tests/test_coq_bridge_integral_infinite.py -q
python -m pytest msaf/tests/test_fence_registry.py -q
```

Registry `A-2026-0014` memuat **6 sertifikat sha256LF**: source, skrip
reproduksi, receipt, guard, report ini, and pra-registrasi.


