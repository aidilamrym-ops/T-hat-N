# Pra-registrasi Paket 6b â€” limit L2 bersyarat with dua aksioma

**Tanggal:** 2026-10-20
**Status:** scope DIKUNCI sebelum implementasi (disiplin paket 4â€“6)
**Berkas target:** `formal_bridge/PseriesL2Bounds.v` (baru; mengimpor
`PseriesL2.v` which beku `A-2026-0010`, no mengubahnya)
**Registry which direncanakan:** `A-2026-0011`

## 1. Latar

`A-2026-0010` membuktikan `pseries_L2_integer` (eksistensi limit + limit dua
sisi) with tiga aksioma stdlib: `sig_forall_dec`,
`functional_extensionality_dep`, and `sig_not_dec` (masuk lewat `Un_cv_crit`,
kelengkapan R). 19 result lainnya hanya dua aksioma. Paket 6b memisahkan
secara eksplisit section mana which memerlukan aksioma ketiga.

## 2. Pernyataan which akan dibuktikan

```coq
Theorem pseries_L2_integer_bounds :
  forall (k N : nat) (L : R),
    (1 <= k)%nat -> (1 <= N)%nat ->
    Un_cv (fun M => psum k N M) L ->
    (1 / (INR k * (INR ((N + 1)%nat)) ^ k) <= L) /\
    (L <= 1 / (INR k * (INR N) ^ k)).
```

yaitu: **jika** limit `L` dari ekor deret-p already ada (hipotesis `Un_cv`),
**maka** limit dua sisi berlaku. Ini section "limit" dari L2 kit for
eksponen bulat; section "eksistensi" tetap milik `A-2026-0010`.

## 3. Metode which dikunci

1. Impor `PseriesL2.v` beku; pakai ulang `Un_cv_le_const`, `psum_upper`,
   `psum_lower_sharp`, `tail_term_small`, `lt_sub_pos`, `sub_le_swap`,
   `pterm_nonneg`, and `sum_incr` (stdlib).
2. **Tidak** memakai `pseries_L2_integer` and **no** memakai `Un_cv_crit`.
3. Batas bawah memakai argumen Îµ which sama seperti `A-2026-0010`, tetapi
   `Hcv` datang dari hipotesis, bukan dari kelengkapan R.

## 4. Kriteria sukses

- `coqc` exit 0 for `PseriesL2.v` (beku) and `PseriesL2Bounds.v`;
  `coqchk` exit 0 "Modules were successfully checked".
- `Print Assumptions pseries_L2_integer_bounds` hanya dua aksioma stdlib:
  `ClassicalDedekindReals.sig_forall_dec` and
  `FunctionalExtensionality.functional_extensionality_dep`; **tanpa**
  `sig_not_dec`, tanpa aksioma proyek.
- Receipt deterministik (dua capture byte-identik); guard statis + uji
  negatif; registry `A-2026-0011`; HANDOFF; CI hijau.

## 5. Kriteria gagal (dicatat negatif, no disembunyikan)

Bila korolari ternyata masih menyeret `sig_not_dec` (misalnya lewat lemma
stdlib which dipakai ulang), hasilnya dicatat sebagai negatif: section mana
which tetap butuh tiga aksioma, and no ada klaim "dua aksioma" which created.

## 6. Batas

- Hanya **kondisional**: `Un_cv` adalah hipotesis; eksistensi limit no
  dibuktikan in sini (itu `A-2026-0010`, tiga aksioma).
- Hanya eksponen bulat `p = k+1 â‰¥ 2`; real `p > 1`, L3â€“L5, periodic-box
  `[J]` tetap in luar scope.
- Tidak ada klaim baru tentang zeta/Weil/RH/Pâ‰ NP/fisika.


