# Coq: L5 finite core â€” perbandingan integralâ€“deret for `f_k(x)=x^{-(k+1)}` (2026-10-20)

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

Paket 7 **selesai and tersegel**. Berkas baru
`IntegralComparison.v` membuktikan **14 result**, with teorema utama
**`integral_comparison_power_finite`**: for `k â‰¥ 1`, `N â‰¥ 1`, and
`M` sembarang, integral Riemann finite `âˆ«_N^{N+M} x^{-(k+1)} dx` berada
in antara jumlah bawah `Î£_{i=0}^{M-1} (N+i)^{-(k+1)}` and jumlah atas
`Î£_{i=0}^{M-1} (N+i+1)^{-(k+1)}`.

Ini adalah **finite core** dari L5 kit. Integral tak-hingga, step
limit, `f` umum, eksponen real, L3/L4, and penutupan `[J]` periodic-box
**no** termasuk. `coqc` exit 0; `coqchk` exit 0
"Modules were successfully checked"; 14/14 result muncul in keluaran
kernel; receipt deterministik 128 baris (dua capture byte-identik).

`Print Assumptions` teorema utama menunjukkan **tepat empat aksioma
stdlib**: `sig_forall_dec`, `sig_not_dec`,
`functional_extensionality_dep`, and `Classical_Prop.classic`. Tiga which
pertama diperkirakan pra-registrasi; which keempat masuk melalui mesin
integral Riemann stdlib. **Tidak ada aksioma proyek.** Deviasi ini
dicatat in addendum, report ini, registry, and HANDOFF.

## 2. Pernyataan which dibuktikan

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
`RiemannInt` atas satu interval unit `[endN N i, endN N (S i)]`, and
`whole_val k N M` adalah `RiemannInt` atas `[N, endN N M]`. Helper
`endN N M` didefinisikan rekursif on `M` agar titik split
`endN N M` and endpoint berikutnya `endN N (S M)` align secara
definitional; secara matematis `endN N M = N + M` (lemma
`endN_eq_add`).

Catatan: hipotesis `(1 <= k)%nat` dipertahankan sesuai pra-registrasi.
Argumen finite ini secara teknis juga berlaku for `k = 0`; pernyataan
which disertifikasi tetap which terkunci, yaitu `k â‰¥ 1`.

## 3. Metode

1. **Integrabilitas.** `fk_int` membangun
   `Riemann_integrable (fk k) a b` dari
   `continuity_implies_RiemannInt`; kontinuitas `fk` on `x > 0`
   diperoleh dari `derivable_pt_pow` + `derivable_continuous_pt` +
   `continuity_pt_inv`. Positivitas interval datang dari `N â‰¥ 1` and
   `endN N i â‰¥ N`.
2. **Batas atas per unit.** `RiemannInt_P19` membandingkan `fk` with
   konstanta `fk k (N+i)` on interval unit; `RiemannInt_P15`
   menghitung integral konstanta, and panjang interval adalah 1
   (`INR_endN_length`). Hasil: `unit_val k N i â‰¤ fk k (N+i)`.
3. **Batas bawah per unit.** `RiemannInt_P19` with konstanta
   `fk k (N+i+1)`; result: `fk k (N+i+1) â‰¤ unit_val k N i`. Arah
   ketaksamaan memakai `Rinv_le_contravar` and `pow_incr`.
4. **Aditivitas.** `RiemannInt_P25` (Chasles) on
   `[N, endN N M]` and `[endN N M, endN N (S M)]` menghasilkan
   `whole_val_split`; `whole_val_eq_sum` lalu membuktikan
   `whole_val k N M = Î£_{i<M} unit_val k N i` with induksi.
5. **Teorema utama.** Induksi on `M`: pakai `whole_val_split`,
   hipotesis induksi, and limit unit atas/bawah; gabungkan with
   `Rplus_le_compat`.

Tidak dipakai: `FTC_Riemann`, `C1_fun`, `Rpower`, integral tak-hingga,
`Un_cv`, or limit integral. Tidak ada impor modul proyek.

## 4. Bukti eksekusi (verbatim, potongan)

`formal_bridge/check_integral.sh` menyalin source ke directory
sementara, menjalankan `coqc -Q . "" IntegralComparison.v` and
`coqchk -Q . "" IntegralComparison`, lalu memeriksa result kernel and
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

(Baris `audit axiom names:` and `final audit block` in receipt memuat
satu spasi trailing dari `tr`; isi hash receipt adalah byte which
tersegel, bukan teks which dipoles.)

## 5. Peta trusted base per result

| Hasil | Aksioma stdlib |
|---|---|
| `endN_eq_add`, `endN_succ_eq`, `le_endN` | **0** (closed) |
| `INR_pos_of_ge1`, `continuity_pt_fk`, `sum_upto_le`, `INR_endN_length` | **2** â€” `sig_forall_dec`, `functional_extensionality_dep` |
| `sum_upto_ext` | **1** â€” `sig_forall_dec` |
| `RiemannInt_degenerate`, `whole_val_split`, `whole_val_eq_sum`, `integral_unit_upper`, `integral_unit_lower`, `integral_comparison_power_finite` | **4** â€” `sig_forall_dec`, `sig_not_dec`, `functional_extensionality_dep`, `Classical_Prop.classic` |

Total 14 result: 3 closed + 4 result dua aksioma + 1 result satu aksioma +
6 result empat aksioma.

## 6. Trusted base: deviasi empat aksioma (bukan tiga)

- Pra-registrasi Â§4 memperkirakan **tiga** aksioma: `sig_forall_dec`,
  `sig_not_dec`, `functional_extensionality_dep`. Hasil aktual
  menambahkan **`Classical_Prop.classic`**, which masuk melalui mesin
  integral Riemann stdlib (`Coq.Reals.RiemannInt`), bukan melalui
  asumsi proyek.
- Ini **bukan** perluasan scope: pernyataan teorema no berubah and
  no dilemahkan. Ini deviasi trusted base which dicatat in
  `reports/PREREG_PAKET7_ADDENDUM_2026-10-20.md`.
- Jika pemilik mensyaratkan literal tiga aksioma, Paket 7 **no**
  memenuhi syarat itu; jalur finite integral Riemann no dapat
  menghindari klasisitas stdlib tanpa mengganti mesin integral.
  Keputusan itu milik owner and no disembunyikan.
- Tidak ada `Axiom`, `Parameter`, `Admitted`, or `admit` in file
  baru (dijaga guard). `Coq.Reals` tetap aksiomatik: ini pernyataan
  tentang trusted base relatif, bukan bukti konsistensi.

## 7. Anti-circularity gate: **TOOL NOT RUN** (bukan sukses)

Gate anti-circularity lokal no menemukan file `.lean`/`.smt2`:

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
statis with mutasi negatif.

## 8. Uji negatif guard

`python -m pytest msaf/tests/test_coq_bridge_integral.py -q` â€” **5 uji**,
semuanya hijau; **16 mutasi negatif** tertangkap:

1. `Admitted.` polos;
2. `Axiom cheat : True.` sebelum definisi;
3. satu baris `Print Assumptions` dihapus;
4. `FTC_Riemann` diselundupkan;
5. `Rpower` diselundupkan;
6. `Un_cv_crit` diselundupkan;
7. impor `PseriesL2` diselundupkan;
8. result terkunci in-rename;
9. limit atas dilemahkan (`<=` â†’ `<`);
10. hipotesis `(1 <= k)` dihapus;
11. aksioma proyek keempat in blok audit;
12. `Classical_Prop.classic` dihapus dari blok final;
13. `sig_not_dec` dipindah ke blok closed;
14. satu section audit dihapus;
15. blok final ditukar with blok closed;
16. komentar Coq tak tertutup.

Guard juga verifying impor stdlib which diizinkan, definisi/statement
lock, 14 result dalam urutan source, 14 `Print Assumptions`, receipt
14/14, peta aksioma per result persis, and no ada nama aksioma proyek.

## 9. Batas

- **Hanya finite core**: integral on `[N, N+M]`, bukan
  `âˆ«_N^âˆž`; no ada step limit or `Un_cv` for integral.
- Hanya `f_k(x) = x^{-(k+1)}` with `k â‰¥ 1`; `f` umum and eksponen real
  `p > 1` (`Rpower`) no diformalkan. L3/L4 no diformalkan.
- **Bukan** penutupan `[J]` periodic-box `A-2026-0007` (tetap OPEN;
  objek berbeda).
- CI no punya toolchain Coq: which dijalankan CI hanya guard statis,
  bukan kernel.
- Tidak menyentuh zeta/Weil/RH/Pâ‰ NP; no ada klaim fisik; bukan peer
  review.

## 10. Reproduksi and registry

```bash
# in WSL/Ubuntu with switch opam 4.14.2
bash formal_bridge/check_integral.sh
python -m pytest msaf/tests/test_coq_bridge_integral.py -q
python -m pytest msaf/tests/test_fence_registry.py -q
```

Registry `A-2026-0012` memuat **7 sertifikat sha256LF**: source, skrip
reproduksi, receipt, guard, report ini, pra-registrasi, and addendum.
HANDOFF Â§2.0ad; entri registry ke-17. Berkas Paket 1â€“6b no diubah;
`freeze.py --verify` tetap OK.

## 11. Langkah berikutnya

L5 infinite limit, `f` umum, eksponen real `p > 1`, L3/L4, and
penutupan `[J]` memerlukan pra-registrasi baru and green-light owner.
Paket 7 no mengklaim penutupan L5 penuh; ia hanya menutup finite core
for instance pangkat bulat.


