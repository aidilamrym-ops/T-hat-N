# Coq: penutupan [J] analitik untuk jembatan geometrik (2026-10-19)

**Paket:** 5 (lanjutan Paket 4; pra-registrasi baru karena scope diperluas)
**Berkas utama:** [`formal_bridge/GeometricLimit.v`](../formal_bridge/GeometricLimit.v)
**Mengimpor (tanpa mengubah):** [`formal_bridge/GeometricBridge.v`](../formal_bridge/GeometricBridge.v), `A-2026-0008`
**Toolchain:** Coq 8.20.1 (OCaml 4.14.2), `/root/.opam/4.14.2/bin/`
**Registry:** `A-2026-0009`

## 1. Ringkasan status

| Blok | Status | Isi |
|---|---|---|
| `[B]` | **CERTIFIED** (warisan `A-2026-0008`) | rumus jumlah parsial geometrik berhingga, eksak |
| `[J]` | **CERTIFIED untuk kasus geometrik** | `Un_cv (fun n => geom_sum r n) (1/(1−r))`, ε-N |
| `[U]` | **tercapai untuk kasus geometrik** | limit `1/(1−r)`; instance `r = 1/2` → `2` |

Pilot Paket 4 meninggalkan langkah limit OPEN. Paket 5 menutupnya **hanya
untuk lemma geometrik L1**. Ini **bukan** penutupan `[J]` untuk studi
periodic-box (`A-2026-0007`): objeknya berbeda dan `[J]` di sana tetap
OPEN. Tidak ada klaim zeta/Weil/RH, P≠NP, atau fisik.

## 2. Yang dibuktikan

| # | Hasil | Pernyataan |
|---|---|---|
| 1 | `geom_dist_eq_tail` | `0 ≤ r → r < 1 → Rdist (geom_sum r n) (1/(1−r)) = geom_tail r n` |
| 2 | `geom_sum_cv` | `0 ≤ r → r < 1 → Un_cv (fun n => geom_sum r n) (1/(1−r))` |
| 3 | `geom_sum_cv_half` | `Un_cv (fun n => geom_sum (1/2) n) (1/(1−1/2))` |
| 4 | `geom_half_limit_value` | `1/(1−1/2) = 2` |
| 5 | `geom_half_dist_11` | `Rdist (geom_sum (1/2) 11) (1/(1−1/2)) = 1/1024` |
| 6 | `geom_half_dist_11_lt` | `Rdist (geom_sum (1/2) 11) (1/(1−1/2)) < 1/100` |

`Un_cv` adalah definisi konvergensi ε-N standar dari
`Coq.Reals.Rseries` (dengan `Rdist`), bukan definisi buatan sendiri.
`pow_lt_1_zero` (stdlib) mengubah suku ekor `r^n/(1−r)` menjadi saksi
ε-N; tidak ada aksioma atau lemma proyek yang ditambahkan.

## 3. Bukti eksekusi (verbatim)

Direkam oleh `formal_bridge/check_limit.sh`: menyalin kedua berkas ke
direktori sementara, mengompilasi `GeometricBridge.v` (beku, tanpa
perubahan) lalu `GeometricLimit.v`, dan menjalankan `coqchk` sebagai
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

Sama seperti Paket 4: `Print Assumptions` untuk **6/6** hasil hanya
mencetak dua aksioma stdlib `Coq.Reals`:

- `ClassicalDedekindReals.sig_forall_dec`
- `FunctionalExtensionality.functional_extensionality_dep`

Tidak ada `Axiom`/`Parameter`/`Admitted`/`admit`; `geom_sum` dan
`geom_tail` **tidak** didefinisikan ulang di berkas ini — guard menolak
redefinisi, sehingga bukti limit selalu memakai aljabar yang sudah
disegel.

## 5. Anti-circularity gate: **TOOL NOT RUN** (bukan sukses)

Gate skill dijalankan lagi pada direktori ini dan hasilnya verbatim:

```text
------------------------------------------------------------------------------
ANTI-CIRCULARITY GATE [check]
  NOT RUN  NO_LEAN_FILES: no .lean input matched
  result: FAIL=0  NOT_RUN=1  SKIP=0
  verdict: TOOL NOT RUN
```

Exit code `2`. Gate itu hanya memindai `.lean`/`.smt2`; repo ini tidak
punya Lean, jadi hasil ini **tidak dihitung sebagai sukses**. Bukti yang
dipakai adalah bukti Coq-native di §3–§4, bukan gate tersebut.

## 6. Uji negatif guard

Guard `msaf/tests/test_coq_bridge_limit.py` diuji terhadap tujuh mutasi
pada salinan sementara di luar repo; ketujuhnya tertangkap:

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
   eksponensial), L4 (ekor Gaussian), dan L5 (perbandingan integral)
   tidak diformalkan; masing-masing butuh pra-registrasi dan bukti sendiri.
2. **Bukan periodic-box.** `[J]` studi `A-2026-0007` tetap OPEN; hasil ini
   tidak boleh dipakai untuk mengklaim batas ekor citra periodik.
3. **`Coq.Reals` aksiomatik.** Yang disertifikasi adalah tidak ada aksioma
   proyek tambahan, bukan konsistensi ZFC/Coq.
4. **CI tidak menjalankan Coq.** Runner tidak punya toolchain Coq; CI
   hanya menjalankan guard statis (isi, kelengkapan audit, receipt).
   Kompilasi ulang adalah langkah lokal §8.
5. **Bukan peer review**, bukan klaim eksternal.

## 8. Reproduksi

```bash
# di WSL/Ubuntu dengan switch opam yang di-KEEP
export PATH=/root/.opam/4.14.2/bin:$PATH
cd formal_bridge
bash check_limit.sh
```

`check_limit.sh` gagal keras bila salah satu kompilasi gagal, `coqchk`
gagal, atau ada hasil yang tidak muncul di keluaran pemeriksa kernel.

## 9. CI

Guard statis: `python -m pytest msaf/tests/test_coq_bridge_limit.py -q`
(4 uji). Registry `A-2026-0009` memuat sha256LF untuk sumber, skrip,
receipt, guard, dan laporan ini. `GeometricBridge.v` dan sertifikatnya di
`A-2026-0008` tidak berubah.
