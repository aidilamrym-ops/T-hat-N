# Pilot Coq — satu lemma jembatan geometrik (2026-10-19)

**Paket:** 4 (pilot formal, scope terkunci)
**Berkas utama:** [`formal_bridge/GeometricBridge.v`](../formal_bridge/GeometricBridge.v)
**Toolchain:** Coq 8.20.1 (OCaml 4.14.2), `/root/.opam/4.14.2/bin/`
**Registry:** `A-2026-0008`

## 1. Ringkasan status

| Blok | Status | Isi |
|---|---|---|
| `[B]` | **CERTIFIED (Coq)** | rumus jumlah parsial geometrik berhingga, eksak |
| `[J]` | **SEBAGIAN** — identitas aljabar tertutup; langkah limit **OPEN** | gap `1/(1-r) − S_n` sama dengan suku ekor `r^n/(1-r)` |
| `[U]` | **tidak diklaim** | deret tak hingga, limit, konvergensi: di luar scope |

Pilot ini membuktikan bahwa toolchain formal bekerja dan satu identitas
jembatan dapat disegel tanpa aksioma proyek. Pilot ini **tidak** membuktikan
konvergensi deret geometrik, dan tidak menyentuh zeta/Weil/RH, P≠NP, atau
klaim fisik apa pun.

## 2. Scope terkunci

Yang diformalkan hanyalah inti aljabar dari lemma L1 di `msaf/bridge.py`:

```text
geom_sum r n           = Σ_{k=0}^{n-1} r^k
geom_sum r n           = (1 − r^n) / (1 − r)          (r ≠ 1)
1/(1−r) − geom_sum r n = r^n / (1 − r)                (suku ekor)
geom_sum r n           ≤ 1/(1−r)                      (0 ≤ r < 1)
```

Yang **tidak** diformalkan dan tidak boleh diklaim dari berkas ini:

- deret tak hingga sebagai limit jumlah parsial;
- keberadaan limit, laju konvergensi, atau kontinuitas;
- lemma analitik lain (L2–L5 di kit), integral, atau zeta;
- pernyataan apa pun tentang RH, P≠NP, atau fisika.

`1/(1−r)` diperlakukan sebagai **bentuk tertutup yang diberikan**, bukan
sebagai limit yang dibuktikan. Inilah sebabnya `[J]` hanya separuh tertutup:
sisi aljabarnya mesin-terverifikasi, sisi analitiknya tetap OPEN.

## 3. Toolchain dan trusted base

- Coq 8.20.1, OCaml 4.14.2, dari switch opam yang di-KEEP (`/root/.opam`).
- `Coq.Reals` di stdlib Coq bersifat **aksiomatik** (formalisasi
  Dedekind real klasik). Karena itu setiap teorema tentang `R` bersandar
  pada aksioma stdlib tersebut. Itu adalah *trusted base*, bukan bukti
  konsistensi.
- `Print Assumptions` untuk kedelapan lemma mencetak tepat dua nama:
  `ClassicalDedekindReals.sig_forall_dec` dan
  `FunctionalExtensionality.functional_extensionality_dep`.
  Tidak ada aksioma proyek, tidak ada `Axiom`/`Parameter`/`Admitted`/`admit`.

## 4. Lemma yang dibuktikan

| # | Lemma | Pernyataan |
|---|---|---|
| 1 | `geom_pow_nonneg` | `0 ≤ r → 0 ≤ r^n` |
| 2 | `geom_sum_mul` | `geom_sum r n * (1−r) = 1 − r^n` |
| 3 | `geom_sum_formula` | `r ≠ 1 → geom_sum r n = (1−r^n)/(1−r)` |
| 4 | `geom_tail_identity` | `r ≠ 1 → 1/(1−r) − geom_sum r n = r^n/(1−r)` |
| 5 | `geom_tail_nonneg` | `0 ≤ r → r < 1 → 0 ≤ r^n/(1−r)` |
| 6 | `geom_sum_le_total` | `0 ≤ r → r < 1 → geom_sum r n ≤ 1/(1−r)` |
| 7 | `geom_sum_half_11` | `geom_sum (1/2) 11 = 2047/1024` |
| 8 | `geom_bridge_half_11` | `1/(1−1/2) − geom_sum (1/2) 11 = 1/1024` |

Lemma 1–6 adalah inti umum; lemma 7–8 adalah satu aplikasi konkret
(`r = 1/2`, `n = 11`), konsisten dengan kasus eksak di demo kit.

## 5. Bukti eksekusi (verbatim)

Direkam oleh `formal_bridge/check.sh` (salin sumber ke direktori sementara,
kompilasi, lalu `coqchk` sebagai pemeriksa kernel independen). Capture
dijalankan dua kali dan byte-identik (`DETERMINISTIC`).

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

Gate skill dijalankan pada direktori ini dan hasilnya verbatim:

```text
------------------------------------------------------------------------------
ANTI-CIRCULARITY GATE [check]
  NOT RUN  NO_LEAN_FILES: no .lean input matched
  result: FAIL=0  NOT_RUN=1  SKIP=0
  verdict: TOOL NOT RUN
```

Exit code `2`. Gate tersebut hanya memindai `.lean`/`.smt2`; repo ini tidak
punya Lean, jadi hasil ini **tidak boleh dihitung sebagai sukses** — sesuai
aturan proyek. Kompensasinya adalah bukti Coq-native yang tercatat di §5:
`coqc` exit 0, `coqchk` exit 0 dengan "Modules were successfully checked",
`Print Assumptions` hanya dua aksioma stdlib, dan scan placeholder yang
bersih. Tidak ada klaim bahwa gate skill lulus untuk Coq.

## 7. Uji negatif guard (bukti guard tidak dekoratif)

Guard statis `msaf/tests/test_coq_bridge_pilot.py` diuji terhadap enam
mutasi pada salinan sementara di luar repo. Keenamnya tertangkap:

```text
CAUGHT  placeholder Admitted
CAUGHT  nested comment is not code
CAUGHT  missing Print Assumptions
CAUGHT  log covers fewer lemmas
CAUGHT  non-standard assumption detected
CAUGHT  unterminated comment raises

OK: all 6 mutations caught
```

Uji ini penting karena repo ini pernah punya audit yang melaporkan "PASS"
sambil mengaudit nol deklarasi. Di sini, jumlah `Lemma` di sumber harus sama
dengan jumlah baris `Print Assumptions`, dan log beku harus memuat tepat
satu blok asumsi per lemma.

## 8. Batas

1. **Bukan formalisasi analisis.** Tidak ada limit, tidak ada deret tak
   hingga, tidak ada klaim konvergensi. `[J]` analitik tetap OPEN.
2. **Bukan bukti baru tentang R.** Teorema bersandar pada aksioma stdlib
   `Coq.Reals`; yang diverifikasi adalah bahwa bukti tidak menambah aksioma
   proyek.
3. **Satu lemma, satu aplikasi.** Ini pilot toolchain, bukan port kit
   L2–L5. Memperluas scope butuh pra-registrasi baru.
4. **CI tidak menjalankan Coq.** CI tidak punya toolchain Coq; yang
   dijalankan CI hanyalah guard statis (hash, placeholder, kelengkapan
   audit). Kompilasi ulang adalah langkah lokal yang diperintahkan §9.
5. **Bukan peer review**, bukan klaim eksternal, tidak menyentuh
   zeta/Weil/RH/P≠NP, tidak ada klaim fisik.

## 9. Reproduksi

```bash
# di WSL/Ubuntu dengan switch opam yang di-KEEP
export PATH=/root/.opam/4.14.2/bin:$PATH
cd formal_bridge
./check.sh
```

`check.sh` gagal keras (exit non-zero) bila: tool tidak ada, `coqc` gagal,
`coqchk` gagal, atau ada lemma yang tidak muncul di keluaran pemeriksa
kernel. Versi Coq lain belum diuji; receipt beku adalah rekamannya.

## 10. CI

Guard statis: `python -m pytest msaf/tests/test_coq_bridge_pilot.py -q`
(4 uji). Guard ini mengunci isi berkas dan kelengkapan audit, bukan
menjalankan ulang kernel. Registry `A-2026-0008` memuat sha256LF untuk
sumber, skrip, log kompilasi, receipt, guard, dan laporan ini.
