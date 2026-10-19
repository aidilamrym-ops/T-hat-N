# Coq: L5 finite core — perbandingan integral–deret untuk `f_k(x)=x^{-(k+1)}` (2026-10-20)

**Paket:** 7 (pra-registrasi baru
[`reports/PREREG_PAKET7_2026-10-20.md`](PREREG_PAKET7_2026-10-20.md);
addendum trusted base
[`reports/PREREG_PAKET7_ADDENDUM_2026-10-20.md`](PREREG_PAKET7_ADDENDUM_2026-10-20.md))
**Berkas utama:** [`formal_bridge/IntegralComparison.v`](../formal_bridge/IntegralComparison.v)
**Berkas pendamping:** `formal_bridge/check_integral.sh`,
`formal_bridge/IntegralComparison.receipt.txt`,
`msaf/tests/test_coq_bridge_integral.py`
**Toolchain:** Coq 8.20.1 (OCaml 4.14.2), `/root/.opam/4.14.2/bin/`
**Registry:** `A-2026-0012`

## 1. Ringkasan status

Paket 7 **selesai dan tersegel**. Berkas baru
`IntegralComparison.v` membuktikan **14 hasil**, dengan teorema utama
**`integral_comparison_power_finite`**: untuk `k ≥ 1`, `N ≥ 1`, dan
`M` sembarang, integral Riemann finite `∫_N^{N+M} x^{-(k+1)} dx` berada
di antara jumlah bawah `Σ_{i=0}^{M-1} (N+i)^{-(k+1)}` dan jumlah atas
`Σ_{i=0}^{M-1} (N+i+1)^{-(k+1)}`.

Ini adalah **finite core** dari L5 kit. Integral tak-hingga, langkah
limit, `f` umum, eksponen real, L3/L4, dan penutupan `[J]` periodic-box
**tidak** termasuk. `coqc` exit 0; `coqchk` exit 0
"Modules were successfully checked"; 14/14 hasil muncul di keluaran
kernel; receipt deterministik 128 baris (dua capture byte-identik).

`Print Assumptions` teorema utama menunjukkan **tepat empat aksioma
stdlib**: `sig_forall_dec`, `sig_not_dec`,
`functional_extensionality_dep`, dan `Classical_Prop.classic`. Tiga yang
pertama diperkirakan pra-registrasi; yang keempat masuk melalui mesin
integral Riemann stdlib. **Tidak ada aksioma proyek.** Deviasi ini
dicatat di addendum, laporan ini, registry, dan HANDOFF.

## 2. Pernyataan yang dibuktikan

```coq
Definition fk (k : nat) (x : R) : R := / (x ^ S k).

Theorem integral_comparison_power_finite :
  forall (k N M : nat) (HN : (1 <= N)%nat),
    (1 <= k)%nat ->
    whole_val k N M HN
      <= sum_upto (fun i => fk k (INR (N + i))) M /\
    sum_upto (fun i => fk k (INR (N + i + 1))) M
      <= whole_val k N M HN.
```

Dengan:

```coq
Fixpoint sum_upto (g : nat -> R) (M : nat) : R :=
  match M with
  | 0%nat => 0
  | S m => sum_upto g m + g m
  end.
```

`sum_upto g M = g(0) + ... + g(M-1)`. `unit_val k N i` adalah
`RiemannInt` atas satu interval unit `[endN N i, endN N (S i)]`, dan
`whole_val k N M` adalah `RiemannInt` atas `[N, endN N M]`. Helper
`endN N M` didefinisikan rekursif pada `M` agar titik split
`endN N M` dan endpoint berikutnya `endN N (S M)` align secara
definitional; secara matematis `endN N M = N + M` (lemma
`endN_eq_add`).

Catatan: hipotesis `(1 <= k)%nat` dipertahankan sesuai pra-registrasi.
Argumen finite ini secara teknis juga berlaku untuk `k = 0`; pernyataan
yang disertifikasi tetap yang terkunci, yaitu `k ≥ 1`.

## 3. Metode

1. **Integrabilitas.** `fk_int` membangun
   `Riemann_integrable (fk k) a b` dari
   `continuity_implies_RiemannInt`; kontinuitas `fk` pada `x > 0`
   diperoleh dari `derivable_pt_pow` + `derivable_continuous_pt` +
   `continuity_pt_inv`. Positivitas interval datang dari `N ≥ 1` dan
   `endN N i ≥ N`.
2. **Batas atas per unit.** `RiemannInt_P19` membandingkan `fk` dengan
   konstanta `fk k (N+i)` pada interval unit; `RiemannInt_P15`
   menghitung integral konstanta, dan panjang interval adalah 1
   (`INR_endN_length`). Hasil: `unit_val k N i ≤ fk k (N+i)`.
3. **Batas bawah per unit.** `RiemannInt_P19` dengan konstanta
   `fk k (N+i+1)`; hasil: `fk k (N+i+1) ≤ unit_val k N i`. Arah
   ketaksamaan memakai `Rinv_le_contravar` dan `pow_incr`.
4. **Aditivitas.** `RiemannInt_P25` (Chasles) pada
   `[N, endN N M]` dan `[endN N M, endN N (S M)]` menghasilkan
   `whole_val_split`; `whole_val_eq_sum` lalu membuktikan
   `whole_val k N M = Σ_{i<M} unit_val k N i` dengan induksi.
5. **Teorema utama.** Induksi pada `M`: pakai `whole_val_split`,
   hipotesis induksi, dan batas unit atas/bawah; gabungkan dengan
   `Rplus_le_compat`.

Tidak dipakai: `FTC_Riemann`, `C1_fun`, `Rpower`, integral tak-hingga,
`Un_cv`, atau limit integral. Tidak ada impor modul proyek.

## 4. Bukti eksekusi (verbatim, potongan)

`formal_bridge/check_integral.sh` menyalin sumber ke direktori
sementara, menjalankan `coqc -Q . "" IntegralComparison.v` dan
`coqchk -Q . "" IntegralComparison`, lalu memeriksa hasil kernel dan
audit. Receipt **deterministik**: dua capture byte-identik, 128 baris,
sha256 `e11d07f5dcb5b835da1af418ddf45b9a0fa5d6845869420e90a940805931d2e2`.

```text
coqc:   /root/.opam/4.14.2/bin/coqc
coqchk: /root/.opam/4.14.2/bin/coqchk
coqc IntegralComparison exit: 0
coqchk exit: 0
coqchk final line: Modules were successfully checked
coqchk full log lines: 48135
results in IntegralComparison.v: 14
results checked by coqchk: 14
Print Assumptions sections: 14 (11 Axioms, 3 Closed)
audit axiom names: ClassicalDedekindReals.sig_forall_dec ClassicalDedekindReals.sig_not_dec Classical_Prop.classic FunctionalExtensionality.functional_extensionality_dep
final audit block (main theorem): ClassicalDedekindReals.sig_forall_dec ClassicalDedekindReals.sig_not_dec Classical_Prop.classic FunctionalExtensionality.functional_extensionality_dep
```

(Baris `audit axiom names:` dan `final audit block` di receipt memuat
satu spasi trailing dari `tr`; isi hash receipt adalah byte yang
tersegel, bukan teks yang dipoles.)

## 5. Peta trusted base per hasil

| Hasil | Aksioma stdlib |
|---|---|
| `endN_eq_add`, `endN_succ_eq`, `le_endN` | **0** (closed) |
| `INR_pos_of_ge1`, `continuity_pt_fk`, `sum_upto_le`, `INR_endN_length` | **2** — `sig_forall_dec`, `functional_extensionality_dep` |
| `sum_upto_ext` | **1** — `sig_forall_dec` |
| `RiemannInt_degenerate`, `whole_val_split`, `whole_val_eq_sum`, `integral_unit_upper`, `integral_unit_lower`, `integral_comparison_power_finite` | **4** — `sig_forall_dec`, `sig_not_dec`, `functional_extensionality_dep`, `Classical_Prop.classic` |

Total 14 hasil: 3 closed + 4 hasil dua aksioma + 1 hasil satu aksioma +
6 hasil empat aksioma.

## 6. Trusted base: deviasi empat aksioma (bukan tiga)

- Pra-registrasi §4 memperkirakan **tiga** aksioma: `sig_forall_dec`,
  `sig_not_dec`, `functional_extensionality_dep`. Hasil aktual
  menambahkan **`Classical_Prop.classic`**, yang masuk melalui mesin
  integral Riemann stdlib (`Coq.Reals.RiemannInt`), bukan melalui
  asumsi proyek.
- Ini **bukan** perluasan scope: pernyataan teorema tidak berubah dan
  tidak dilemahkan. Ini deviasi trusted base yang dicatat di
  `reports/PREREG_PAKET7_ADDENDUM_2026-10-20.md`.
- Jika pemilik mensyaratkan literal tiga aksioma, Paket 7 **tidak**
  memenuhi syarat itu; jalur finite integral Riemann tidak dapat
  menghindari klasisitas stdlib tanpa mengganti mesin integral.
  Keputusan itu milik owner dan tidak disembunyikan.
- Tidak ada `Axiom`, `Parameter`, `Admitted`, atau `admit` di berkas
  baru (dijaga guard). `Coq.Reals` tetap aksiomatik: ini pernyataan
  tentang trusted base relatif, bukan bukti konsistensi.

## 7. Anti-circularity gate: **TOOL NOT RUN** (bukan sukses)

Gate anti-circularity lokal tidak menemukan berkas `.lean`/`.smt2`:

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
statis dengan mutasi negatif.

## 8. Uji negatif guard

`python -m pytest msaf/tests/test_coq_bridge_integral.py -q` — **5 uji**,
semuanya hijau; **16 mutasi negatif** tertangkap:

1. `Admitted.` polos;
2. `Axiom cheat : True.` sebelum definisi;
3. satu baris `Print Assumptions` dihapus;
4. `FTC_Riemann` diselundupkan;
5. `Rpower` diselundupkan;
6. `Un_cv_crit` diselundupkan;
7. impor `PseriesL2` diselundupkan;
8. hasil terkunci di-rename;
9. batas atas dilemahkan (`<=` → `<`);
10. hipotesis `(1 <= k)` dihapus;
11. aksioma proyek keempat di blok audit;
12. `Classical_Prop.classic` dihapus dari blok final;
13. `sig_not_dec` dipindah ke blok closed;
14. satu section audit dihapus;
15. blok final ditukar dengan blok closed;
16. komentar Coq tak tertutup.

Guard juga memverifikasi impor stdlib yang diizinkan, definisi/statement
lock, 14 hasil dalam urutan sumber, 14 `Print Assumptions`, receipt
14/14, peta aksioma per hasil persis, dan tidak ada nama aksioma proyek.

## 9. Batas

- **Hanya finite core**: integral pada `[N, N+M]`, bukan
  `∫_N^∞`; tidak ada langkah limit atau `Un_cv` untuk integral.
- Hanya `f_k(x) = x^{-(k+1)}` dengan `k ≥ 1`; `f` umum dan eksponen real
  `p > 1` (`Rpower`) tidak diformalkan. L3/L4 tidak diformalkan.
- **Bukan** penutupan `[J]` periodic-box `A-2026-0007` (tetap OPEN;
  objek berbeda).
- CI tidak punya toolchain Coq: yang dijalankan CI hanya guard statis,
  bukan kernel.
- Tidak menyentuh zeta/Weil/RH/P≠NP; tidak ada klaim fisik; bukan peer
  review.

## 10. Reproduksi dan registry

```bash
# di WSL/Ubuntu dengan switch opam 4.14.2
bash formal_bridge/check_integral.sh
python -m pytest msaf/tests/test_coq_bridge_integral.py -q
python -m pytest msaf/tests/test_fence_registry.py -q
```

Registry `A-2026-0012` memuat **7 sertifikat sha256LF**: sumber, skrip
reproduksi, receipt, guard, laporan ini, pra-registrasi, dan addendum.
HANDOFF §2.0ad; entri registry ke-17. Berkas Paket 1–6b tidak diubah;
`freeze.py --verify` tetap OK.

## 11. Langkah berikutnya

L5 infinite limit, `f` umum, eksponen real `p > 1`, L3/L4, dan
penutupan `[J]` memerlukan pra-registrasi baru dan green-light owner.
Paket 7 tidak mengklaim penutupan L5 penuh; ia hanya menutup finite core
untuk instance pangkat bulat.
