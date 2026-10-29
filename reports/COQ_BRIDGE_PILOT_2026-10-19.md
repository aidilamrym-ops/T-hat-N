# Pilot Coq â€” satu lemma jembatan geometrik (2026-10-19)

**Paket:** 4 (pilot formal, scope terkunci)
**Berkas utama:** [`formal_bridge/GeometricBridge.v`](../formal_bridge/GeometricBridge.v)
**Toolchain:** Coq 8.20.1 (OCaml 4.14.2), `/root/.opam/4.14.2/bin/`
**Registry:** `A-2026-0008`

## 1. Ringkasan status

| Blok | Status | Isi |
|---|---|---|
| `[B]` | **CERTIFIED (Coq)** | rumus jumlah parsial geometrik berhingga, eksak |
| `[J]` | **SEBAGIAN** â€” identitas aljabar tertutup; step limit **OPEN** | gap `1/(1-r) âˆ’ S_n` sama with suku ekor `r^n/(1-r)` |
| `[U]` | **no diklaim** | deret tak hingga, limit, konvergensi: in luar scope |

Pilot ini membuktikan bahwa toolchain formal bekerja and satu identitas
jembatan dapat disegel tanpa aksioma proyek. Pilot ini **no** membuktikan
konvergensi deret geometrik, and no menyentuh zeta/Weil/RH, Pâ‰ NP, or
klaim fisik apa pun.

## 2. Scope terkunci

Yang diformalkan hanyalah inti aljabar dari lemma L1 in `msaf/bridge.py`:

```text
geom_sum r n           = Î£_{k=0}^{n-1} r^k
geom_sum r n           = (1 âˆ’ r^n) / (1 âˆ’ r)          (r â‰  1)
1/(1âˆ’r) âˆ’ geom_sum r n = r^n / (1 âˆ’ r)                (suku ekor)
geom_sum r n           â‰¤ 1/(1âˆ’r)                      (0 â‰¤ r < 1)
```

Yang **no** diformalkan and no boleh diklaim dari file ini:

- deret tak hingga sebagai limit jumlah parsial;
- keberadaan limit, laju konvergensi, or kontinuitas;
- lemma analitik lain (L2â€“L5 in kit), integral, or zeta;
- pernyataan apa pun tentang RH, Pâ‰ NP, or fisika.

`1/(1âˆ’r)` diperlakukan sebagai **bentuk tertutup which diberikan**, bukan
sebagai limit which dibuktikan. Inilah sebabnya `[J]` hanya separuh tertutup:
sisi aljabarnya mesin-terverifikasi, sisi analitiknya tetap OPEN.

## 3. Toolchain and trusted base

- Coq 8.20.1, OCaml 4.14.2, dari switch opam which in-KEEP (`/root/.opam`).
- `Coq.Reals` in stdlib Coq bersifat **aksiomatik** (formalisasi
  Dedekind real klasik). Karena itu setiap teorema tentang `R` bersandar
  on aksioma stdlib tersebut. Itu adalah *trusted base*, bukan bukti
  konsistensi.
- `Print Assumptions` for kedelapan lemma mencetak tepat dua nama:
  `ClassicalDedekindReals.sig_forall_dec` and
  `FunctionalExtensionality.functional_extensionality_dep`.
  Tidak ada aksioma proyek, no ada `Axiom`/`Parameter`/`Admitted`/`admit`.

## 4. Lemma which dibuktikan

| # | Lemma | Pernyataan |
|---|---|---|
| 1 | `geom_pow_nonneg` | `0 â‰¤ r â†’ 0 â‰¤ r^n` |
| 2 | `geom_sum_mul` | `geom_sum r n * (1âˆ’r) = 1 âˆ’ r^n` |
| 3 | `geom_sum_formula` | `r â‰  1 â†’ geom_sum r n = (1âˆ’r^n)/(1âˆ’r)` |
| 4 | `geom_tail_identity` | `r â‰  1 â†’ 1/(1âˆ’r) âˆ’ geom_sum r n = r^n/(1âˆ’r)` |
| 5 | `geom_tail_nonneg` | `0 â‰¤ r â†’ r < 1 â†’ 0 â‰¤ r^n/(1âˆ’r)` |
| 6 | `geom_sum_le_total` | `0 â‰¤ r â†’ r < 1 â†’ geom_sum r n â‰¤ 1/(1âˆ’r)` |
| 7 | `geom_sum_half_11` | `geom_sum (1/2) 11 = 2047/1024` |
| 8 | `geom_bridge_half_11` | `1/(1âˆ’1/2) âˆ’ geom_sum (1/2) 11 = 1/1024` |

Lemma 1â€“6 adalah inti umum; lemma 7â€“8 adalah satu aplikasi konkret
(`r = 1/2`, `n = 11`), konsisten with kasus eksak in demo kit.

## 5. Bukti eksekusi (verbatim)

Direkam oleh `formal_bridge/check.sh` (salin source ke directory sementara,
kompilasi, lalu `coqchk` sebagai pemeriksa kernel independen). Capture
dijalankan dua kali and byte-identik (`DETERMINISTIC`).

```text
coqc:   /root/.opam/4.14.2/bin/coqc
coqchk: /root/.opam/4.14.2/bin/coqchk
coqc exit: 0
coqchk exit: 0
coqchk final line: Modules were successfully checked
coqchk full log lines: 48125
lemmas in source: 8
lemmas checked by coqchk: 10
--- lemmas checked ---
  geom_bridge_half_11
  geom_pow_nonneg
  geom_sum
  geom_sum_formula
  geom_sum_half_11
  geom_sum_le_total
  geom_sum_mul
  geom_tail
  geom_tail_identity
  geom_tail_nonneg
--- coqc audit log (Print Assumptions) ---
Axioms:
ClassicalDedekindReals.sig_forall_dec :
  forall P : nat -> Prop,
  (forall n : nat, {P n} + {~ P n}) ->
  {n : nat | ~ P n} + {forall n : nat, P n}
FunctionalExtensionality.functional_extensionality_dep :
  forall (A : Type) (B : A -> Type) (f g : forall x : A, B x),
  (forall x : A, f x = g x) -> f = g
Axioms:
ClassicalDedekindReals.sig_forall_dec :
  forall P : nat -> Prop,
  (forall n : nat, {P n} + {~ P n}) ->
  {n : nat | ~ P n} + {forall n : nat, P n}
FunctionalExtensionality.functional_extensionality_dep :
  forall (A : Type) (B : A -> Type) (f g : forall x : A, B x),
  (forall x : A, f x = g x) -> f = g
Axioms:
ClassicalDedekindReals.sig_forall_dec :
  forall P : nat -> Prop,
  (forall n : nat, {P n} + {~ P n}) ->
  {n : nat | ~ P n} + {forall n : nat, P n}
FunctionalExtensionality.functional_extensionality_dep :
  forall (A : Type) (B : A -> Type) (f g : forall x : A, B x),
  (forall x : A, f x = g x) -> f = g
Axioms:
ClassicalDedekindReals.sig_forall_dec :
  forall P : nat -> Prop,
  (forall n : nat, {P n} + {~ P n}) ->
  {n : nat | ~ P n} + {forall n : nat, P n}
FunctionalExtensionality.functional_extensionality_dep :
  forall (A : Type) (B : A -> Type) (f g : forall x : A, B x),
  (forall x : A, f x = g x) -> f = g
Axioms:
ClassicalDedekindReals.sig_forall_dec :
  forall P : nat -> Prop,
  (forall n : nat, {P n} + {~ P n}) ->
  {n : nat | ~ P n} + {forall n : nat, P n}
FunctionalExtensionality.functional_extensionality_dep :
  forall (A : Type) (B : A -> Type) (f g : forall x : A, B x),
  (forall x : A, f x = g x) -> f = g
Axioms:
ClassicalDedekindReals.sig_forall_dec :
  forall P : nat -> Prop,
  (forall n : nat, {P n} + {~ P n}) ->
  {n : nat | ~ P n} + {forall n : nat, P n}
FunctionalExtensionality.functional_extensionality_dep :
  forall (A : Type) (B : A -> Type) (f g : forall x : A, B x),
  (forall x : A, f x = g x) -> f = g
Axioms:
ClassicalDedekindReals.sig_forall_dec :
  forall P : nat -> Prop,
  (forall n : nat, {P n} + {~ P n}) ->
  {n : nat | ~ P n} + {forall n : nat, P n}
FunctionalExtensionality.functional_extensionality_dep :
  forall (A : Type) (B : A -> Type) (f g : forall x : A, B x),
  (forall x : A, f x = g x) -> f = g
Axioms:
ClassicalDedekindReals.sig_forall_dec :
  forall P : nat -> Prop,
  (forall n : nat, {P n} + {~ P n}) ->
  {n : nat | ~ P n} + {forall n : nat, P n}
FunctionalExtensionality.functional_extensionality_dep :
  forall (A : Type) (B : A -> Type) (f g : forall x : A, B x),
  (forall x : A, f x = g x) -> f = g
OK: compiled and kernel-checked
```

## 6. Anti-circularity gate: **TOOL NOT RUN** (bukan sukses)

Gate skill dijalankan on directory ini and hasilnya verbatim:

```text
------------------------------------------------------------------------------
ANTI-CIRCULARITY GATE [check]
  NOT RUN  NO_LEAN_FILES: no .lean input matched
  result: FAIL=0  NOT_RUN=1  SKIP=0
  verdict: TOOL NOT RUN
```

Exit code `2`. Gate tersebut hanya memindai `.lean`/`.smt2`; repo ini no
punya Lean, jadi result ini **no boleh dihitung sebagai sukses** â€” sesuai
aturan proyek. Kompensasinya adalah bukti Coq-native which tercatat in Â§5:
`coqc` exit 0, `coqchk` exit 0 with "Modules were successfully checked",
`Print Assumptions` hanya dua aksioma stdlib, and scan placeholder which
bersih. Tidak ada klaim bahwa gate skill lulus for Coq.

## 7. Uji negatif guard (bukti guard no dekoratif)

Guard statis `msaf/tests/test_coq_bridge_pilot.py` diuji terhadap enam
mutasi on salinan sementara in luar repo. Keenamnya tertangkap:

```text
CAUGHT  placeholder Admitted
CAUGHT  nested comment is not code
CAUGHT  missing Print Assumptions
CAUGHT  log covers fewer lemmas
CAUGHT  non-standard assumption detected
CAUGHT  unterminated comment raises

OK: all 6 mutations caught
```

Uji ini penting karena repo ini pernah punya audit which melaporkan "PASS"
sambil mengaudit nol deklarasi. Di sini, jumlah `Lemma` in source harus sama
with jumlah baris `Print Assumptions`, and log beku harus memuat tepat
satu blok asumsi per lemma.

## 8. Batas

1. **Bukan formalisasi analisis.** Tidak ada limit, no ada deret tak
   hingga, no ada klaim konvergensi. `[J]` analitik tetap OPEN.
2. **Bukan bukti baru tentang R.** Teorema bersandar on aksioma stdlib
   `Coq.Reals`; which diverifikasi adalah bahwa bukti no menambah aksioma
   proyek.
3. **Satu lemma, satu aplikasi.** Ini pilot toolchain, bukan port kit
   L2â€“L5. Memperluas scope butuh pra-registrasi baru.
4. **CI no menjalankan Coq.** CI no punya toolchain Coq; which
   dijalankan CI hanyalah guard statis (hash, placeholder, kelengkapan
   audit). Kompilasi ulang adalah step lokal which diperintahkan Â§9.
5. **Bukan peer review**, bukan klaim eksternal, no menyentuh
   zeta/Weil/RH/Pâ‰ NP, no ada klaim fisik.

## 9. Reproduksi

```bash
# in WSL/Ubuntu with switch opam which in-KEEP
export PATH=/root/.opam/4.14.2/bin:$PATH
cd formal_bridge
./check.sh
```

`check.sh` gagal keras (exit non-zero) bila: tool no ada, `coqc` gagal,
`coqchk` gagal, or ada lemma which no muncul in keluaran pemeriksa
kernel. Versi Coq lain belum diuji; receipt beku adalah rekamannya.

## 10. CI

Guard statis: `python -m pytest msaf/tests/test_coq_bridge_pilot.py -q`
(4 uji). Guard ini mengunci isi file and kelengkapan audit, bukan
menjalankan ulang kernel. Registry `A-2026-0008` memuat sha256LF for
source, skrip, log kompilasi, receipt, guard, and report ini.


