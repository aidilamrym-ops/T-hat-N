# Coq: L2 bersyarat dua aksioma â€” limit deret-p tanpa `Un_cv_crit` (2026-10-20)

**Paket:** 6b (pra-registrasi baru
[`reports/PREREG_PAKET6B_2026-10-20.md`](PREREG_PAKET6B_2026-10-20.md);
scope dikunci sebelum implementasi)
**Berkas utama:** [`formal_bridge/PseriesL2Bounds.v`](../formal_bridge/PseriesL2Bounds.v)
**Berkas pendamping:** `formal_bridge/check_bounds.sh`,
`formal_bridge/PseriesL2Bounds.receipt.txt`,
`msaf/tests/test_coq_bridge_bounds.py`
**Toolchain:** Coq 8.20.1 (OCaml 4.14.2), `/root/.opam/4.14.2/bin/`
**Registry:** `A-2026-0011`

## 1. Ringkasan status

Paket 6b **selesai and tersegel**. Satu teorema baru,
`pseries_L2_integer_bounds`, membuktikan **limit dua sisi L2 secara
kondisional**: jika limit ekor deret-p already diketahui ada (hipotesis
`Un_cv`), maka `1/(k(N+1)^k) â‰¤ L â‰¤ 1/(k N^k)` berlaku â€” and pembuktiannya
memakai **tepat dua aksioma stdlib** (`sig_forall_dec`,
`functional_extensionality_dep`), **tanpa** `sig_not_dec`.

Ini melengkapi peta trusted base Paket 6 (`A-2026-0010`): aksioma ketiga
(`sig_not_dec`, kelengkapan R) hanya diperlukan for **eksistensi** limit
(`Un_cv_crit`), bukan for limit-batasnya. Berkas Paket 1â€“6 **no
diubah**; paket ini menambah file baru and mengimpor modul beku
`PseriesL2.v` apa adanya.

## 2. Pernyataan which dibuktikan

```coq
Theorem pseries_L2_integer_bounds :
  forall (k N : nat) (L : R),
    (1 <= k)%nat -> (1 <= N)%nat ->
    Un_cv (fun M => psum k N M) L ->
    (1 / (INR k * (INR ((N + 1)%nat)) ^ k) <= L) /\
    (L <= 1 / (INR k * (INR N) ^ k)).
```

`pterm` and `psum` diimpor dari modul beku (bukan didefinisikan ulang):

```coq
Definition pterm (k n : nat) : R := 1 / (INR n) ^ (S k).
Definition psum (k N M : nat) : R :=
  sum_f_R0 (fun i => pterm k (N + 1 + i)) M.
```

Perhatikan: **no ada** `exists L` on pernyataan ini â€” eksistensi
adalah hipotesis, bukan klaim. Ini which membuat aksioma ketiga no
terpakai.

## 3. Metode

1. Impor `PseriesL2.v` beku; pakai ulang `Un_cv_le_const`, `psum_upper`,
   `psum_lower_sharp`, `tail_term_small`, `lt_sub_pos`, `sub_le_swap`,
   `pterm_nonneg`, and `sum_incr` (stdlib).
2. Batas atas: `Un_cv_le_const` with `psum_upper`.
3. Batas bawah: argumen Îµ which sama seperti `A-2026-0010`
   (`tail_term_small` + `psum_lower_sharp` + `sum_incr`), tetapi `Hcv`
   datang dari hipotesis â€” **tanpa** `Un_cv_crit`.
4. Guard statis menolak secara eksplisit setiap kemunculan `Un_cv_crit`
   or `pseries_L2_integer` in dalam kode (in luar komentar), sehingga
   isolasi no bisa bocor tanpa CI gagal.

## 4. Bukti eksekusi (verbatim)

`formal_bridge/check_bounds.sh` menjalankan: `coqc` for `PseriesL2.v`
(beku) lalu `PseriesL2Bounds.v`, kemudian `coqchk` (kernel independen)
for modul baru. Receipt **deterministik**: dua capture byte-identik,
23 baris.

```text
coqc:   /root/.opam/4.14.2/bin/coqc
coqchk: /root/.opam/4.14.2/bin/coqchk
coqc PseriesL2 exit: 0
coqc PseriesL2Bounds exit: 0
coqchk exit: 0
coqchk final line: Modules were successfully checked
coqchk full log lines: 48144
results in PseriesL2Bounds.v: 1
results checked by coqchk: 1
Print Assumptions blocks: 1
audit axiom names: ClassicalDedekindReals.sig_forall_dec FunctionalExtensionality.functional_extensionality_dep 
--- results checked ---
  pseries_L2_integer_bounds
--- coqc audit log (Print Assumptions) ---
Axioms:
ClassicalDedekindReals.sig_forall_dec :
  forall P : nat -> Prop,
  (forall n : nat, {P n} + {~ P n}) ->
  {n : nat | ~ P n} + {forall n : nat, P n}
FunctionalExtensionality.functional_extensionality_dep :
  forall (A : Type) (B : A -> Type) (f g : forall x : A, B x),
  (forall x : A, f x = g x) -> f = g
OK: conditional bounds module kernel-checked; exactly two stdlib axioms; no sig_not_dec
```

(Baris `audit axiom names:` memuat satu spasi trailing dari `tr`; isi
hash receipt adalah byte which tersegel, bukan teks which dipoles.)

## 5. Trusted base: isolasi aksioma ketiga

| Bagian | Aksioma stdlib | Sumber |
|---|---|---|
| Eksistensi limit (`pseries_L2_integer`) | **3** â€” `sig_forall_dec`, `functional_extensionality_dep`, `sig_not_dec` | `A-2026-0010` |
| Batas bersyarat (`pseries_L2_integer_bounds`) | **2** â€” `sig_forall_dec`, `functional_extensionality_dep` | Paket 6b (entri ini) |

- `sig_not_dec` masuk lewat `Un_cv_crit` (kelengkapan R) on step
  eksistensi; korolari ini no menyentuhnya â€” terbukti dari keluaran
  `Print Assumptions` in atas.
- Tidak ada aksioma proyek, `Axiom`, `Parameter`, `Admitted`, or
  `admit` in file baru (dijaga guard).
- `Coq.Reals` tetap aksiomatik: ini pernyataan tentang trusted base
  relatif, bukan bukti konsistensi.

## 6. Anti-circularity gate: **TOOL NOT RUN** (bukan sukses)

Perintah (skill anti-circularity, gate lokal):

```text
C:\Python314\python.exe C:\Users\usER\.config\opencode\skills\anti-circularity\scripts\gate.py check formal_bridge reports\PREREG_PAKET6B_2026-10-20.md
```

Keluaran verbatim:

```text
ANTI-CIRCULARITY GATE [check]
  NOT RUN  NO_LEAN_FILES: no .lean input matched
  result: FAIL=0  NOT_RUN=1  SKIP=0
  verdict: TOOL NOT RUN
```

Verdict = `TOOL NOT RUN` (exit 2 menurut kontrak `gate.py`;
harness menampilkan semua kode non-nol sebagai 1 â€” diverifikasi with
`python -c "raise SystemExit(2)"`). Gate **no berlaku** for artefak
Coq (no ada `.lean`/`.smt2`) and **no dihitung sebagai sukses**.
Kompensasi: `coqchk` (kernel independen) + `Print Assumptions` + guard
statis with mutasi negatif (Â§7).

## 7. Uji negatif guard

`python -m pytest msaf/tests/test_coq_bridge_bounds.py -q` â€” **6 uji**,
semuanya hijau; **11 mutasi negatif** tertangkap:

1. `Admitted.` polos;
2. `Axiom cheat : True.` sebelum teorema;
3. satu baris `Print Assumptions` dihapus;
4. `Un_cv_crit` diselundupkan kembali;
5. `pseries_L2_integer` (teorema eksistensi beku) dipakai;
6. pernyataan dilemahkan (`<=` â†’ `<` on limit bawah);
7. `exists L` diselundupkan ke pernyataan kondisional;
8. aksioma proyek keempat in blok audit;
9. salah satu dari dua aksioma bersama dihapus;
10. `sig_not_dec` diselundupkan ke blok audit;
11. komentar Coq tak tertutup.

Guard juga verifying: impor `PseriesL2` ada, `pterm`/`psum` no
didefinisikan ulang, statement lock persis, receipt memuat exit 0 kedua
`coqc`, `coqchk` sukses, 1/1 result, 1 blok audit, and **no** memuat
`ClassicalDedekindReals.sig_not_dec`.

## 8. Batas

- **Hanya kondisional**: `Un_cv` adalah hipotesis; eksistensi limit no
  dibuktikan in sini (itu `A-2026-0010`, tiga aksioma).
- Hanya eksponen bulat `p = k+1 â‰¥ 2`; eksponen real `p > 1` (`Rpower`),
  L3, L4, L5 no diformalkan.
- **Bukan** penutupan `[J]` studi periodic-box `A-2026-0007` (tetap
  OPEN; objek berbeda).
- CI no punya toolchain Coq: which dijalankan CI hanya guard statis,
  bukan kernel.
- Tidak menyentuh zeta/Weil/RH/Pâ‰ NP; no ada klaim fisik; bukan peer
  review.

## 9. Reproduksi

```bash
# in WSL/Ubuntu with switch opam 4.14.2
bash formal_bridge/check_bounds.sh
```

Skrip menyalin kedua file source ke directory sementara, menjalankan
`coqc` (dua file, berurutan) and `coqchk`, lalu **fail-closed**: exit 0
hanya jika kedua kompilasi sukses, kernel menerima modul, result tunggal
muncul in keluaran kernel, blok audit tepat satu with tepat dua aksioma
which diizinkan, and `sig_not_dec` absen.

## 10. CI and registry

- Guard statis berjalan in CI (`python -m pytest`), tanpa Coq.
- Registry `A-2026-0011` memuat 6 sertifikat sha256LF: source, skrip
  reproduksi, receipt, guard, report ini, and pra-registrasi.
- HANDOFF Â§2.0ac; entri registry ke-16.
- Berkas beku Paket 1â€“6 no diubah; `freeze.py --verify` tetap OK.


