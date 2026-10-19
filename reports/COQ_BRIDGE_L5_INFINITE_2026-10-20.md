# Coq: L5 infinite (unconditional) — limit integral–deret untuk `f_k(x)=x^{-(k+1)}` (2026-10-20)

**Paket:** 9 (pra-registrasi baru
[`reports/PREREG_PAKET9_2026-10-20.md`](PREREG_PAKET9_2026-10-20.md))
**Berkas utama:** [`formal_bridge/IntegralComparisonInfinite.v`](../formal_bridge/IntegralComparisonInfinite.v)
**Dependensi:** [`formal_bridge/IntegralComparison.v`](../formal_bridge/IntegralComparison.v)
(Paket 7, `A-2026-0012`),
[`formal_bridge/IntegralComparisonLimit.v`](../formal_bridge/IntegralComparisonLimit.v)
(Paket 8, `A-2026-0013`),
[`formal_bridge/PseriesL2.v`](../formal_bridge/PseriesL2.v) (Paket 6,
`A-2026-0010`); ketiganya **tidak diubah**
**Berkas pendamping:** `formal_bridge/check_integral_infinite.sh`,
`formal_bridge/IntegralComparisonInfinite.receipt.txt`,
`msaf/tests/test_coq_bridge_integral_infinite.py`
**Toolchain:** Coq 8.20.1 (OCaml 4.14.2), `/root/.opam/4.14.2/bin/`
**Registry:** `A-2026-0014`

## 1. Ringkasan status

Paket 9 **selesai dan tersegel**. Berkas baru
`IntegralComparisonInfinite.v` membuktikan **17 hasil**, dengan teorema
utama **`integral_comparison_power_infinite`**: untuk `k ≥ 1` dan
`N ≥ 1`, **ketiga limit ada** dan memenuhi

```text
L_{N+1} <= L_S <= L_N,
```

yaitu L5 pilot yang **unconditional** untuk `f_k`:

```text
∫_{N+1}^∞ f_k ≤ Σ_{n>N} f_k(n) ≤ ∫_N^∞ f_k.
```

Limit integral tak-hingga diwakili oleh nilai limit `Un_cv`; tidak ada
definisi baru `∫_N^∞` dan tidak ada klaim untuk `f` umum atau eksponen
real. `coqc` exit 0 untuk keempat modul (tiga dependensi + modul baru);
`coqchk` exit 0 "Modules were successfully checked"; 17/17 hasil muncul
di keluaran kernel; receipt deterministik 178 baris (dua capture
byte-identik), sha256
`39ad870db3b2fec94745ef95a26161e108e8642d2323666bc856da5954fd056d`.

`Print Assumptions` teorema utama menunjukkan **tepat empat aksioma
stdlib** yang sama dengan Paket 7/8: `sig_forall_dec`, `sig_not_dec`,
`functional_extensionality_dep`, `Classical_Prop.classic`. **Tidak ada
aksioma proyek.** Peta per hasil dicatat di §5; beberapa hasil murni
kombinatorik hanya membawa 1–2 aksioma, sedangkan hasil yang menyentuh
`RiemannInt`, `Un_cv_crit`, atau teorema bersyarat Paket 8 membawa
empat.

## 2. Pernyataan yang dibuktikan

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
   unit_val ...`; `unit_val >= 0` dari `integral_unit_lower` dan
   positivitas `fk`; hasilnya `whole_val_growing`.
3. **Batas integral.** Teorema finite Paket 7 pada `N`:
   `whole_val k N M ≤ Σ_{i<M} f_k(N+i)`. Identitas
   `Σ_{i<M} f_k(N+i) = f_k(N) + tail_sum k N (M-1)` dan `sum_incr`
   memberi batas seragam `f_k(N) + L_S`; jadi `Un_cv_crit` berlaku dan
   `whole_val_cv` terbukti.
4. **Teorema utama.** Gabungkan `whole_val_cv` untuk `N` dan `N+1`,
   `tail_sum_cv`, lalu teorema bersyarat Paket 8
   `integral_comparison_power_limit`.

Tidak dipakai: `Rpower`, `FTC_Riemann`, `C1_fun`, `RiemannInt_P`,
integral tak-hingga sebagai definisi, atau aksioma proyek. Dependensi
Paket 7/8/6 diimpor apa adanya; berkas-berkas itu tidak diubah.

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

(Baris `audit axiom names:` dan `final audit block` di receipt memuat satu
spasi trailing dari `tr`; isi hash receipt adalah byte yang tersegel.)

## 5. Peta trusted base per hasil

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

Semua 17 blok adalah `Axioms` (tidak ada `Closed`). Himpunan empat
aksioma final sama dengan Paket 7/8. `sum_f_R0_ext` hanya memerlukan
`sig_forall_dec`; `tail_sum_cv` menambahkan `sig_not_dec` lewat
`pseries_L2_integer`; hasil yang menyentuh `RiemannInt`/`Un_cv_crit`
membawa `Classical_Prop.classic`.

## 6. Trusted base: deviasi empat aksioma (diwarisi)

- Paket 9 memakai `RiemannInt` lewat dependensi Paket 7/8; karena itu
  empat aksioma stdlib tetap muncul. Ini **diwarisi**, bukan aksioma baru.
- Jika owner mensyaratkan literal tiga aksioma, Paket 9 **tidak**
  memenuhi syarat itu; jalur integral Riemann ini tidak dapat
  menghindari `Classical_Prop.classic`.
- Tidak ada `Axiom`, `Parameter`, `Admitted`, atau `admit` di berkas baru
  (dijaga guard). `Coq.Reals` tetap aksiomatik: ini pernyataan tentang
  trusted base relatif, bukan bukti konsistensi.

## 7. Anti-circularity gate: **TOOL NOT RUN** (bukan sukses)

Gate anti-circularity lokal tetap tidak menemukan berkas `.lean`/`.smt2`:

```text
ANTI-CIRCULARITY GATE [check]
  NOT RUN  NO_LEAN_FILES: no .lean input matched
  result: FAIL=0  NOT_RUN=1  SKIP=0
  verdict: TOOL NOT RUN
```

Verdict = `TOOL NOT RUN` (exit 2 menurut kontrak `gate.py`; harness
menampilkan semua kode non-nol sebagai 1). Gate **tidak berlaku** untuk
artefak Coq dan **tidak dihitung sebagai sukses**. Kompensasi:
`coqchk` (kernel independen) + `Print Assumptions` per hasil + guard
statis dengan mutasi negatif. Jalur agar gate benar-benar berjalan
disusun setelah paket-paket ini selesai.

## 8. Uji negatif guard

`python -m pytest msaf/tests/test_coq_bridge_integral_infinite.py -q` —
**5 uji**, semuanya hijau; **18 mutasi negatif** tertangkap:

1. `Admitted.` polos;
2. `Axiom cheat : True.`;
3. satu baris `Print Assumptions` dihapus;
4. `Rpower` diselundupkan;
5. `FTC_Riemann` diselundupkan;
6. hasil terkunci di-rename;
7. batas lunak dilemahkan (`<=` → `<`);
8. hipotesis `(1 <= k)` dihapus dari statement utama;
9. eksistensi tiga limit diciutkan menjadi satu;
10. `Rpower` dimasukkan ke statement;
11. aksioma proyek keempat di blok audit;
12. `Classical_Prop.classic` dihapus dari blok final;
13. `sig_not_dec` dipindah ke section yang seharusnya hanya 2 aksioma;
14. satu section audit dihapus;
15. blok final ditukar dengan blok dua-aksioma;
16. komentar Coq tak tertutup;
17. impor `PseriesL2` dihapus;
18. `Un_cv_crit` dihapus (bukan sekadar di-rename).

Guard juga memverifikasi impor yang diizinkan, definisi/statement lock,
17 hasil dalam urutan sumber, 17 `Print Assumptions`, receipt 17/17, peta
aksioma per hasil persis, dan tidak ada nama aksioma proyek.

## 9. Batas

- **Unconditional hanya untuk `f_k`**: `k ≥ 1`, `N ≥ 1`; bukan `f`
  umum, bukan eksponen real `p > 1` (`Rpower`).
- Limit tak-hingga diwakili oleh `Un_cv`; tidak ada definisi integral
  tak-hingga baru dan tidak ada klaim tentang nilai eksplisit limit.
- Bukan L3/L4; bukan penutupan `[J]` periodic-box `A-2026-0007` (tetap
  OPEN; objek berbeda).
- CI tidak punya toolchain Coq: yang dijalankan CI hanya guard statis,
  bukan kernel.
- Tidak menyentuh zeta/Weil/RH/P≠NP; tidak ada klaim fisik; bukan peer
  review.

## 10. Reproduksi dan registry

```bash
# di WSL/Ubuntu dengan switch opam 4.14.2
bash formal_bridge/check_integral_infinite.sh
python -m pytest msaf/tests/test_coq_bridge_integral_infinite.py -q
python -m pytest msaf/tests/test_fence_registry.py -q
```

Registry `A-2026-0014` memuat **6 sertifikat sha256LF**: sumber, skrip
reproduksi, receipt, guard, laporan ini, dan pra-registrasi.
