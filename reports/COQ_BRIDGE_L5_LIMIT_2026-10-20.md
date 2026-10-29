# Coq: L5 limit step (bersyarat) â€” perbandingan limit integralâ€“deret for `f_k(x)=x^{-(k+1)}` (2026-10-20)

**Paket:** 8 (pra-registrasi baru
[`reports/PREREG_PAKET8_2026-10-20.md`](PREREG_PAKET8_2026-10-20.md))
**Berkas utama:** [`formal_bridge/IntegralComparisonLimit.v`](../formal_bridge/IntegralComparisonLimit.v)
**Dependensi:** [`formal_bridge/IntegralComparison.v`](../formal_bridge/IntegralComparison.v)
(Paket 7, registry `A-2026-0012`; no diubah)
**Berkas pendamping:** `formal_bridge/check_integral_limit.sh`,
`formal_bridge/IntegralComparisonLimit.receipt.txt`,
`msaf/tests/test_coq_bridge_integral_limit.py`
**Toolchain:** Coq 8.20.1 (OCaml 4.14.2), `/root/.opam/4.14.2/bin/`
**Registry:** `A-2026-0013`

## 1. Ringkasan status

Paket 8 **selesai and tersegel**. Berkas baru
`IntegralComparisonLimit.v` membuktikan **4 result**, with teorema utama
**`integral_comparison_power_limit`**: for `k â‰¥ 1`, `N â‰¥ 1`, and limit
`L_N, L_{N+1}, L_S` which diberikan sebagai hipotesis `Un_cv`, berlaku

```text
L_{N+1} <= L_S <= L_N,
```

yaitu L5 dalam bentuk limit:

```text
int_{N+1}^inf f_k <= sum_{n>N} f_k(n) <= int_N^inf f_k.
```

Eksistensi ketiga limit **no** dibuktikan in paket ini; itu Paket 9.
`coqc` exit 0 (dependensi and modul baru); `coqchk` exit 0
"Modules were successfully checked"; 4/4 result muncul in keluaran kernel;
receipt deterministik 57 baris (dua capture byte-identik), sha256
`af90fb87a9f4344e9f3d03741d8de8e0993363f59eeea14b6cff21b632a3faf4`.

`Print Assumptions` teorema utama menunjukkan **tepat empat aksioma
stdlib** which sama with Paket 7: `sig_forall_dec`, `sig_not_dec`,
`functional_extensionality_dep`, and `Classical_Prop.classic`. **Tidak ada
aksioma proyek.** Deviasi trusted-base 4-aksioma diwarisi dari dependensi
`RiemannInt`; ini dicatat, bukan ditemukan baru in Paket 8.

## 2. Pernyataan which dibuktikan

```coq
Definition HN_succ (N : nat) (HN : (1 <= N)%nat) : (1 <= N + 1)%nat :=
  Nat.le_trans 1%nat N (N + 1)%nat HN (Nat.le_add_r N 1).

Lemma Un_cv_le :
  forall (u v : nat -> R) (lu lv : R),
    Un_cv u lu ->
    Un_cv v lv ->
    (forall n : nat, u n <= v n) ->
    lu <= lv.

Lemma tail_sum_le_whole :
  forall (k N M : nat) (HN : (1 <= N)%nat),
    (1 <= k)%nat ->
    sum_upto (fun i => fk k (INR (N + 1 + i))) M
      <= whole_val k N M HN.

Lemma whole_succ_le_tail_sum :
  forall (k N M : nat) (HN : (1 <= N)%nat),
    (1 <= k)%nat ->
    whole_val k (N + 1) M (HN_succ N HN)
      <= sum_upto (fun i => fk k (INR (N + 1 + i))) M.

Theorem integral_comparison_power_limit :
  forall (k N : nat) (HN : (1 <= N)%nat) (Hk : (1 <= k)%nat)
         (L_N L_N1 L_S : R),
    Un_cv (fun M => whole_val k N M HN) L_N ->
    Un_cv (fun M => whole_val k (N + 1) M (HN_succ N HN)) L_N1 ->
    Un_cv (fun M => sum_upto (fun i => fk k (INR (N + 1 + i))) M) L_S ->
    L_N1 <= L_S /\ L_S <= L_N.
```

## 3. Metode

1. **Batas bawah tail sum.** Teorema finite Paket 7 on `N` memberikan
   `Î£_{i<M} f_k(N+i+1) â‰¤ whole_val k N M`. Lemma `sum_upto_ext` menyamakan
   indeks `N+1+i` and `N+i+1` (keduanya sama secara aritmetika nat).
   Hasil: `tail_sum_le_whole`.
2. **Batas atas integral dari `N+1`.** Teorema finite Paket 7 on `N+1`
   memberikan `whole_val k (N+1) M â‰¤ Î£_{i<M} f_k(N+1+i)`. Hasil:
   `whole_succ_le_tail_sum`.
3. **Order limit.** `Un_cv_le` dibuktikan with epsilon: andaikan
   `lv < lu`; ambil `eps = (lu-lv)/2`; for `n` cukup besar,
   `u_n > (lu+lv)/2` and `v_n < (lu+lv)/2`, bertentangan with
   `u_n â‰¤ v_n`.
4. **Teorema utama.** Gabungkan kedua ketaksamaan finite with
   `Un_cv_le` (dua kali).

Tidak dipakai: `Un_cv_crit`, `PseriesL2`, `Rpower`, `FTC_Riemann`,
`C1_fun`, integral tak-hingga, or aksioma proyek. Dependensi
`IntegralComparison.v` diimpor apa adanya; file Paket 7 no diubah.

## 4. Bukti eksekusi (verbatim, potongan)

`formal_bridge/check_integral_limit.sh` menyalin kedua source ke directory
sementara, menjalankan `coqc` for dependensi and modul baru, lalu
`coqchk -Q . "" IntegralComparisonLimit`. Receipt deterministik: dua
capture byte-identik, 57 baris, sha256
`af90fb87a9f4344e9f3d03741d8de8e0993363f59eeea14b6cff21b632a3faf4`.

```text
coqc:   /root/.opam/4.14.2/bin/coqc
coqchk: /root/.opam/4.14.2/bin/coqchk
coqc IntegralComparison (dependency) exit: 0
coqc IntegralComparisonLimit exit: 0
coqchk exit: 0
coqchk final line: Modules were successfully checked
coqchk full log lines: 48146
results in IntegralComparisonLimit.v: 4
results checked by coqchk: 4
Print Assumptions sections: 4 (4 Axioms, 0 Closed)
audit axiom names: ClassicalDedekindReals.sig_forall_dec ClassicalDedekindReals.sig_not_dec Classical_Prop.classic FunctionalExtensionality.functional_extensionality_dep
final audit block (main theorem): ClassicalDedekindReals.sig_forall_dec ClassicalDedekindReals.sig_not_dec Classical_Prop.classic FunctionalExtensionality.functional_extensionality_dep
```

(Baris `audit axiom names:` and `final audit block` in receipt memuat satu
spasi trailing dari `tr`; isi hash receipt adalah byte which tersegel,
bukan teks which dipoles.)

## 5. Peta trusted base per result

| Hasil | Aksioma stdlib |
|---|---|
| `Un_cv_le` | **2** â€” `sig_forall_dec`, `functional_extensionality_dep` |
| `tail_sum_le_whole` | **4** â€” `sig_forall_dec`, `sig_not_dec`, `functional_extensionality_dep`, `Classical_Prop.classic` |
| `whole_succ_le_tail_sum` | **4** â€” himpunan which sama |
| `integral_comparison_power_limit` | **4** â€” himpunan which sama |

Total 4 result, semuanya blok `Axioms` (no ada which `Closed`).
`Classical_Prop.classic` hanya muncul on result which melewati
`RiemannInt` (tiga result terakhir); lemma order-limit murni `Un_cv_le`
no memerlukannya.

## 6. Trusted base: deviasi empat aksioma (diwarisi, bukan baru)

- Pra-registrasi Â§4 memperkirakan empat aksioma stdlib which sama with
  Paket 7; result aktual **tepat empat**, sesuai ekspektasi.
- Ini tetap deviasi terhadap target awal "literal tiga" which muncul in
  Paket 7. Jalur `RiemannInt` no dapat menghindari
  `Classical_Prop.classic`. Jika owner mensyaratkan literal tiga aksioma,
  Paket 8 **no** memenuhi syarat itu; jalur limit with mesin
  integral ini no memenuhinya.
- Tidak ada `Axiom`, `Parameter`, `Admitted`, or `admit` in file baru
  (dijaga guard). `Coq.Reals` tetap aksiomatik: ini pernyataan tentang
  trusted base relatif, bukan bukti konsistensi.

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
statis with mutasi negatif. Jalur agar gate benar-benar berjalan akan
disusun setelah Paket 9 selesai.

## 8. Uji negatif guard

`python -m pytest msaf/tests/test_coq_bridge_integral_limit.py -q` â€”
**5 uji**, semuanya hijau; **16 mutasi negatif** tertangkap:

1. `Admitted.` polos;
2. `Axiom cheat : True.` sebelum definisi;
3. satu baris `Print Assumptions` dihapus;
4. `Un_cv_crit` diselundupkan;
5. impor `PseriesL2` diselundupkan;
6. result terkunci in-rename;
7. limit lunak dilemahkan (`<=` â†’ `<`);
8. hipotesis `(1 <= k)` dihapus dari statement utama;
9. statement mengklaim eksistensi (`exists L`) â€” in luar scope Paket 8;
10. aksioma proyek keempat in blok audit;
11. `Classical_Prop.classic` dihapus dari blok final;
12. `sig_not_dec` dipindah ke section lain;
13. satu section audit dihapus;
14. blok final ditukar with blok dua-aksioma;
15. komentar Coq tak tertutup;
16. impor `IntegralComparison` dihapus.

Guard juga verifying impor which diizinkan, definisi/statement lock,
4 result dalam urutan source, 4 `Print Assumptions`, receipt 4/4, peta
aksioma per result persis, and no ada nama aksioma proyek.

## 9. Batas

- **Bersyarat**: eksistensi limit adalah hipotesis `Un_cv`; Paket 8 no
  membuktikan `âˆ«_N^âˆž f_k` or `Î£_{n>N} f_k(n)` ada. Paket 9 which
  membuktikannya for `f_k` (memakai `Un_cv_crit` + `pseries_L2_integer`
  `A-2026-0010`).
- Hanya `f_k(x) = x^{-(k+1)}` with `k â‰¥ 1`, `N â‰¥ 1`; `f` umum and
  eksponen real `p > 1` (`Rpower`) no diformalkan. L3/L4 no
  diformalkan.
- **Bukan** penutupan `[J]` periodic-box `A-2026-0007` (tetap OPEN;
  objek berbeda).
- CI no punya toolchain Coq: which dijalankan CI hanya guard statis,
  bukan kernel.
- Tidak menyentuh zeta/Weil/RH/Pâ‰ NP; no ada klaim fisik; bukan peer
  review.

## 10. Reproduksi and registry

```bash
# in WSL/Ubuntu with switch opam 4.14.2
bash formal_bridge/check_integral_limit.sh
python -m pytest msaf/tests/test_coq_bridge_integral_limit.py -q
python -m pytest msaf/tests/test_fence_registry.py -q
```

Registry `A-2026-0013` memuat **6 sertifikat sha256LF**: source, skrip
reproduksi, receipt, guard, report ini, and pra-registrasi.


