# Coq: penutupan [J] analitik for jembatan geometrik (2026-10-19)

**Paket:** 5 (lanjutan Paket 4; pra-registrasi baru karena scope diperluas)
**Berkas utama:** [`formal_bridge/GeometricLimit.v`](../formal_bridge/GeometricLimit.v)
**Mengimpor (tanpa mengubah):** [`formal_bridge/GeometricBridge.v`](../formal_bridge/GeometricBridge.v), `A-2026-0008`
**Toolchain:** Coq 8.20.1 (OCaml 4.14.2), `/root/.opam/4.14.2/bin/`
**Registry:** `A-2026-0009`

## 1. Ringkasan status

| Blok | Status | Isi |
|---|---|---|
| `[B]` | **CERTIFIED** (warisan `A-2026-0008`) | rumus jumlah parsial geometrik berhingga, eksak |
| `[J]` | **CERTIFIED for kasus geometrik** | `Un_cv (fun n => geom_sum r n) (1/(1âˆ’r))`, Îµ-N |
| `[U]` | **tercapai for kasus geometrik** | limit `1/(1âˆ’r)`; instance `r = 1/2` â†’ `2` |

Pilot Paket 4 meninggalkan step limit OPEN. Paket 5 menutupnya **hanya
for lemma geometrik L1**. Ini **bukan** penutupan `[J]` for studi
periodic-box (`A-2026-0007`): objeknya berbeda and `[J]` in sana tetap
OPEN. Tidak ada klaim zeta/Weil/RH, Pâ‰ NP, or fisik.

## 2. Yang dibuktikan

| # | Hasil | Pernyataan |
|---|---|---|
| 1 | `geom_dist_eq_tail` | `0 â‰¤ r â†’ r < 1 â†’ Rdist (geom_sum r n) (1/(1âˆ’r)) = geom_tail r n` |
| 2 | `geom_sum_cv` | `0 â‰¤ r â†’ r < 1 â†’ Un_cv (fun n => geom_sum r n) (1/(1âˆ’r))` |
| 3 | `geom_sum_cv_half` | `Un_cv (fun n => geom_sum (1/2) n) (1/(1âˆ’1/2))` |
| 4 | `geom_half_limit_value` | `1/(1âˆ’1/2) = 2` |
| 5 | `geom_half_dist_11` | `Rdist (geom_sum (1/2) 11) (1/(1âˆ’1/2)) = 1/1024` |
| 6 | `geom_half_dist_11_lt` | `Rdist (geom_sum (1/2) 11) (1/(1âˆ’1/2)) < 1/100` |

`Un_cv` adalah definisi konvergensi Îµ-N standar dari
`Coq.Reals.Rseries` (with `Rdist`), bukan definisi buatan sendiri.
`pow_lt_1_zero` (stdlib) mengubah suku ekor `r^n/(1âˆ’r)` menjadi saksi
Îµ-N; no ada aksioma or lemma proyek which ditambahkan.

## 3. Bukti eksekusi (verbatim)

Direkam oleh `formal_bridge/check_limit.sh`: menyalin kedua file ke
directory sementara, mengompilasi `GeometricBridge.v` (beku, tanpa
perubahan) lalu `GeometricLimit.v`, and menjalankan `coqchk` sebagai
pemeriksa kernel independen. Capture dua kali, byte-identik.

```text
coqc:   /root/.opam/4.14.2/bin/coqc
coqchk: /root/.opam/4.14.2/bin/coqchk
coqc GeometricBridge exit: 0
coqc GeometricLimit exit: 0
coqchk exit: 0
coqchk final line: Modules were successfully checked
coqchk full log lines: 48137
results in GeometricLimit.v: 6
results checked by coqchk: 6
--- results checked ---
  geom_dist_eq_tail
  geom_half_dist_11
  geom_half_dist_11_lt
  geom_half_limit_value
  geom_sum_cv
  geom_sum_cv_half
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
OK: imported bridge unchanged, limit module kernel-checked
```

## 4. Trusted base

Sama seperti Paket 4: `Print Assumptions` for **6/6** result hanya
mencetak dua aksioma stdlib `Coq.Reals`:

- `ClassicalDedekindReals.sig_forall_dec`
- `FunctionalExtensionality.functional_extensionality_dep`

Tidak ada `Axiom`/`Parameter`/`Admitted`/`admit`; `geom_sum` and
`geom_tail` **no** didefinisikan ulang in file ini â€” guard menolak
redefinisi, sehingga bukti limit selalu memakai aljabar which already
disegel.

## 5. Anti-circularity gate: **TOOL NOT RUN** (bukan sukses)

Gate skill dijalankan lagi on directory ini and hasilnya verbatim:

```text
------------------------------------------------------------------------------
ANTI-CIRCULARITY GATE [check]
  NOT RUN  NO_LEAN_FILES: no .lean input matched
  result: FAIL=0  NOT_RUN=1  SKIP=0
  verdict: TOOL NOT RUN
```

Exit code `2`. Gate itu hanya memindai `.lean`/`.smt2`; repo ini no
punya Lean, jadi result ini **no dihitung sebagai sukses**. Bukti which
dipakai adalah bukti Coq-native in Â§3â€“Â§4, bukan gate tersebut.

## 6. Uji negatif guard

Guard `msaf/tests/test_coq_bridge_limit.py` diuji terhadap tujuh mutasi
on salinan sementara in luar repo; ketujuhnya tertangkap:

```text
CAUGHT  placeholder Admitted
CAUGHT  missing Print Assumptions
CAUGHT  redefinition of geom_sum
CAUGHT  bridge import removed
CAUGHT  non-standard assumption
CAUGHT  receipt covers fewer results
CAUGHT  unterminated comment raises

OK: all 7 mutations caught
```

## 7. Batas

1. **Hanya lemma geometrik L1.** Lemma L2 (p-series), L3 (amplop
   eksponensial), L4 (ekor Gaussian), and L5 (perbandingan integral)
   no diformalkan; masing-masing butuh pra-registrasi and bukti sendiri.
2. **Bukan periodic-box.** `[J]` studi `A-2026-0007` tetap OPEN; result ini
   no boleh dipakai for mengklaim limit ekor citra periodik.
3. **`Coq.Reals` aksiomatik.** Yang disertifikasi adalah no ada aksioma
   proyek tambahan, bukan konsistensi ZFC/Coq.
4. **CI no menjalankan Coq.** Runner no punya toolchain Coq; CI
   hanya menjalankan guard statis (isi, kelengkapan audit, receipt).
   Kompilasi ulang adalah step lokal Â§8.
5. **Bukan peer review**, bukan klaim eksternal.

## 8. Reproduksi

```bash
# in WSL/Ubuntu with switch opam which in-KEEP
export PATH=/root/.opam/4.14.2/bin:$PATH
cd formal_bridge
bash check_limit.sh
```

`check_limit.sh` gagal keras bila salah satu kompilasi gagal, `coqchk`
gagal, or ada result which no muncul in keluaran pemeriksa kernel.

## 9. CI

Guard statis: `python -m pytest msaf/tests/test_coq_bridge_limit.py -q`
(4 uji). Registry `A-2026-0009` memuat sha256LF for source, skrip,
receipt, guard, and report ini. `GeometricBridge.v` and sertifikatnya in
`A-2026-0008` no berubah.


