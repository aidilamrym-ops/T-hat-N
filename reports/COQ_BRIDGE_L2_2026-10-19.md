# Coq: L2 deret-p eksponen bulat â€” limit dua sisi + limit (2026-10-19)

**Paket:** 6 (pra-registrasi baru; scope dikunci in
[`reports/PREREG_PAKET6_2026-10-19.md`](PREREG_PAKET6_2026-10-19.md))
**Berkas utama:** [`formal_bridge/PseriesL2.v`](../formal_bridge/PseriesL2.v)
**Berkas pendamping:** `formal_bridge/check_pseries.sh`,
`formal_bridge/PseriesL2.receipt.txt`,
`msaf/tests/test_coq_bridge_l2.py`
**Toolchain:** Coq 8.20.1 (OCaml 4.14.2), `/root/.opam/4.14.2/bin/`
**Registry:** `A-2026-0010`

## 1. Ringkasan status

| Blok | Status | Isi |
|---|---|---|
| `[B]` | **CERTIFIED** | aljabar step Bernoulli + teleskopik finite for `p = k+1 â‰¥ 2` |
| `[J]` | **CERTIFIED for `p` bulat â‰¥ 2** | eksistensi limit via `Un_cv_crit` (monoton + terbatas) |
| `[U]` | **CERTIFIED for `p` bulat â‰¥ 2** | limit dua sisi `1/(k(N+1)^k) â‰¤ L â‰¤ 1/(k N^k)` |

Ini adalah **L2 kit** (`pseries_tail_bounds`) for **eksponen bulat**
`p = k+1 â‰¥ 2` saja. Eksponen real `p > 1` (which membutuhkan `Rpower`),
L3â€“L5, studi periodic-box `A-2026-0007`, zeta/Weil/RH, Pâ‰ NP, and klaim fisik
**in luar scope**. Tidak ada klaim bahwa ini menutup seluruh L2 kit.

## 2. Pernyataan which dibuktikan

Dengan `pterm k n = 1/(INR n)^(S k)` and
`psum k N M = sum_{i=0}^{M} pterm k (N+1+i)`:

```coq
Theorem pseries_L2_integer :
  forall (k N : nat),
    (1 <= k)%nat -> (1 <= N)%nat ->
    exists L : R,
      Un_cv (fun M => psum k N M) L /\
      (1 / (INR k * (INR ((N + 1)%nat)) ^ k) <= L) /\
      (L <= 1 / (INR k * (INR N) ^ k)).
```

`Un_cv` adalah definisi Îµ-N standar `Coq.Reals.Rseries`; `sum_f_R0` adalah
jumlah finite standar. Untuk `p = k+1`, batasnya persis
`1/((pâˆ’1)(N+1)^(pâˆ’1)) â‰¤ tail â‰¤ 1/((pâˆ’1)N^(pâˆ’1))`.

Hasil antara which menjadi tulang bukti (total **20** result):

| # | Hasil | Peran |
|---|---|---|
| 1 | `bernoulli_int` | `(1+x)^n â‰¥ 1 + n x` for `x â‰¥ âˆ’1` |
| 2 | `pterm_upper_step` | `1/(S m)^(k+1) â‰¤ (1/k)(1/m^k âˆ’ 1/(S m)^k)`, `m â‰¥ 1` |
| 3 | `pterm_lower_step` | `(1/k)(1/n^k âˆ’ 1/(S n)^k) â‰¤ 1/n^(k+1)`, `n â‰¥ 1` |
| 4 | `telescope` | `Î£_{i=0}^{M} (g(a+i) âˆ’ g(a+i+1)) = g a âˆ’ g(a+M+1)` |
| 5 | `psum_upper` | `psum â‰¤ 1/(k N^k)` |
| 6 | `psum_lower_sharp` | `(1/k)(1/(N+1)^k âˆ’ 1/(N+M+2)^k) â‰¤ psum` |
| 7 | `Un_cv_le_const` | `(âˆ€n, Un n â‰¤ B) â†’ limit â‰¤ B` |
| 8 | `tail_term_small` | sisa `(1/k)/(N+M+2)^k` bisa created `< Îµ` |
| 9 | `pseries_L2_integer` | eksistensi + limit dua sisi |

Sisanya adalah lemma bantu: `one_le_pow`, `pow_ge_self`,
`prod_pow_neq_0`, `pterm_nonneg`, `sum_f_R0_le_all`,
`sum_f_R0_const_mul`, `psum_upper_sharp`, `div_mul_cancel`, `mul_neq_0`,
`sub_le_swap`, `lt_sub_pos`.

## 3. Metode

1. **Bernoulli integer** dibuktikan with induksi (tanpa lemma
   `Rbernoulli` which no ada in stdlib).
2. **Ketaksamaan step** atas and bawah diturunkan dari Bernoulli on
   `x = Â±1/A`; keduanya adalah ketaksamaan aljabar murni, bukan integral.
3. **Teleskopik finite** dibuktikan sendiri in atas `sum_f_R0`.
4. **Eksistensi limit** dari `Un_cv_crit`: barisan `psum` naik
   (`Un_growing`) and terbatas in atas (`bound (EUn ...)`).
5. **Batas atas limit** lewat `Un_cv_le_const` which dibuktikan with Îµ.
6. **Batas bawah limit** lewat `sum_incr` (suku tak-negatif: jumlah parsial
   â‰¤ limit) and `INR_unbounded` for mengecilkan sisa
   `(1/k)/(N+M+2)^k`. Lemma `pow_ge_self` mengubah
   `1/(N+M+2)^k â‰¤ 1/(N+M+2)`.

Sakhi Îµ-N and urutan memakai lemma stdlib; no ada `Axiom`, `Parameter`,
`Admitted`, or `admit` in file.

## 4. Bukti eksekusi (verbatim)

Direkam oleh `formal_bridge/check_pseries.sh`: menyalin `PseriesL2.v` ke
directory sementara, mengompilasi with `coqc -Q . ""`, lalu menjalankan
`coqchk` sebagai pemeriksa kernel independen. Dua capture berturut-turut
**byte-identik** (193 baris).

```text
coqc:   /root/.opam/4.14.2/bin/coqc
coqchk: /root/.opam/4.14.2/bin/coqchk
coqc PseriesL2 exit: 0
coqchk exit: 0
coqchk final line: Modules were successfully checked
coqchk full log lines: 48137
results in PseriesL2.v: 20
results checked by coqchk: 20
Print Assumptions blocks: 20
--- results checked ---
  Un_cv_le_const
  bernoulli_int
  div_mul_cancel
  lt_sub_pos
  mul_neq_0
  one_le_pow
  pow_ge_self
  prod_pow_neq_0
  pseries_L2_integer
  psum_lower_sharp
  psum_upper
  psum_upper_sharp
  pterm_lower_step
  pterm_nonneg
  pterm_upper_step
  sub_le_swap
  sum_f_R0_const_mul
  sum_f_R0_le_all
  tail_term_small
  telescope
```

Blok audit `Print Assumptions` berjumlah 20, satu per result. **19 blok**
hanya memuat dua aksioma stdlib:

```text
Axioms:
ClassicalDedekindReals.sig_forall_dec :
  forall P : nat -> Prop,
  (forall n : nat, {P n} + {~ P n}) ->
  {n : nat | ~ P n} + {forall n : nat, P n}
FunctionalExtensionality.functional_extensionality_dep :
  forall (A : Type) (B : A -> Type) (f g : forall x : A, B x),
  (forall x : A, f x = g x) -> f = g
```

**Blok ke-20** â€” teorema utama â€” memuat aksioma ketiga:

```text
Axioms:
ClassicalDedekindReals.sig_not_dec : forall P : Prop, {~ ~ P} + {~ P}
ClassicalDedekindReals.sig_forall_dec :
  forall P : nat -> Prop,
  (forall n : nat, {P n} + {~ P n}) ->
  {n : nat | ~ P n} + {forall n : nat, P n}
FunctionalExtensionality.functional_extensionality_dep :
  forall (A : Type) (B : A -> Type) (f g : forall x : A, B x),
  (forall x : A, f x = g x) -> f = g
OK: pseries L2 module kernel-checked; audit block count matches results
```

## 5. Trusted base and deviasi audit

**Tidak ada aksioma proyek.** Namun kriteria pra-registrasi Â§4 (â€œhanya dua
aksioma stdlibâ€) **no terpenuhi secara literal** for teorema utama:
`pseries_L2_integer` memakai **tiga** aksioma stdlib. Aksioma ketiga,
`ClassicalDedekindReals.sig_not_dec`, masuk melalui `Un_cv_crit`
(kelengkapan R) which dipakai for membuktikan eksistensi limit. Probe
terpisah mengonfirmasi:

```text
Print Assumptions Un_cv_crit.
Axioms:
ClassicalDedekindReals.sig_not_dec : forall P : Prop, {~ ~ P} + {~ P}
ClassicalDedekindReals.sig_forall_dec : ...
FunctionalExtensionality.functional_extensionality_dep : ...
```

Sebagai minimalisasi, lemma urutan `Un_cv_le_const` **no** memakai
`Rle_or_lt`; ia memakai `Rnot_lt_le` which hanya bergantung on
`sig_forall_dec`. Tetapi eksistensi limit tetap membutuhkan
`Un_cv_crit`, which membawa `sig_not_dec`. Menghapusnya akan memerlukan
bukti kelengkapan/konvergensi lain which setara; itu no dilakukan dalam
paket ini.

Deviasi ini dicatat in **addendum Â§6 pra-registrasi**, in report ini, in
registry `A-2026-0010`, and in HANDOFF Â§2.0ab. Paket berstatus
**CERTIFIED with deviasi audit tercatat** â€” bukan pemenuhan literal
kriteria dua-aksioma. Yang disertifikasi adalah **no ada aksioma proyek
tambahan**, bukan konsistensi ZFC/Coq.

## 6. Anti-circularity gate: **TOOL NOT RUN** (bukan sukses)

Gate dijalankan on `formal_bridge/PseriesL2.v`; result verbatim:

```text
------------------------------------------------------------------------------
ANTI-CIRCULARITY GATE [check]
  NOT RUN  NO_LEAN_FILES: no .lean input matched
  NOT RUN  NO_CLAIM_FILES: no claim-bearing input matched
  result: FAIL=0  NOT_RUN=2  SKIP=0
  verdict: TOOL NOT RUN
```

Exit code `2`. Gate hanya memindai `.lean`/`.smt2`; repo ini no punya
Lean/SMT2, jadi result ini **no dihitung sebagai sukses**. Bukti which
dipakai adalah Coq-native (Â§4â€“Â§5), bukan gate tersebut.

## 7. Uji negatif guard

Guard `msaf/tests/test_coq_bridge_l2.py` menjalankan 5 uji pytest: empat
uji positif (placeholder, kelengkapan audit, standalone + statement lock,
receipt/trusted base) and satu uji mutasi in-memory. Uji mutasi menangkap
**8/8** mutasi:

```text
CAUGHT  placeholder Admitted
CAUGHT  project Axiom
CAUGHT  missing Print Assumptions
CAUGHT  fourth/project assumption
CAUGHT  sig_not_dec moved to a non-final block
CAUGHT  sig_not_dec silently dropped from the final block
CAUGHT  one audit block removed
CAUGHT  unterminated Coq comment
```

Guard menolak aksioma keempat and menolak penempatan `sig_not_dec` in blok
selain teorema utama. Statement lock memastikan teorema tetap berbunyi
`exists L` + `Un_cv (psum) L` + limit bawah/atas which dikunci.

## 8. Batas

1. **Hanya eksponen bulat** `p = k+1 â‰¥ 2`. Eksponen real `p > 1`
   (`Rpower`) **no** diformalkan and no diklaim.
2. **L3â€“L5 no diformalkan** (amplop eksponensial, ekor Gaussian,
   perbandingan integral). Masing-masing butuh pra-registrasi and bukti
   sendiri.
3. **Bukan periodic-box.** `[J]` studi `A-2026-0007` tetap **OPEN**;
   result ini no boleh dipakai for mengklaim limit ekor citra periodik.
4. **`Coq.Reals` aksiomatik.** 19 result memakai dua aksioma stdlib; teorema
   utama memakai tiga (`sig_not_dec` dari kelengkapan R). Tidak ada aksioma
   proyek, tetapi ini **bukan** bukti konsistensi ZFC/Coq.
5. **CI no menjalankan Coq.** Runner no punya toolchain Coq; CI hanya
   menjalankan guard statis (isi, kelengkapan audit, receipt). Kompilasi
   ulang adalah step lokal Â§9.
6. **Bukan peer review**, bukan klaim eksternal; no ada klaim
   zeta/Weil/RH/Pâ‰ NP/fisika.

## 9. Reproduksi

```bash
# in WSL/Ubuntu with switch opam which in-KEEP
export PATH=/root/.opam/4.14.2/bin:$PATH
cd formal_bridge
bash check_pseries.sh
```

`check_pseries.sh` gagal keras bila kompilasi gagal, `coqchk` gagal, ada
result which no muncul in keluaran pemeriksa kernel, jumlah blok audit
no sama with jumlah result, or `Print Assumptions` no lengkap.

## 10. CI and registry

Guard statis: `python -m pytest msaf/tests/test_coq_bridge_l2.py -q`
(5 uji). Registry `A-2026-0010` memuat sha256LF for source, skrip,
receipt, guard, report ini, and pra-registrasi. Artefak Paket 1â€“5
(`A-2026-0006` â€¦ `A-2026-0009`) no diubah. HANDOFF Â§2.0ab mencatat
status, deviasi audit, and limit paket.


