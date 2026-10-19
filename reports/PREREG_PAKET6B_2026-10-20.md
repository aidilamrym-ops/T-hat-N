# Pra-registrasi Paket 6b — batas L2 bersyarat dengan dua aksioma

**Tanggal:** 2026-10-20
**Status:** scope DIKUNCI sebelum implementasi (disiplin paket 4–6)
**Berkas target:** `formal_bridge/PseriesL2Bounds.v` (baru; mengimpor
`PseriesL2.v` yang beku `A-2026-0010`, tidak mengubahnya)
**Registry yang direncanakan:** `A-2026-0011`

## 1. Latar

`A-2026-0010` membuktikan `pseries_L2_integer` (eksistensi limit + batas dua
sisi) dengan tiga aksioma stdlib: `sig_forall_dec`,
`functional_extensionality_dep`, dan `sig_not_dec` (masuk lewat `Un_cv_crit`,
kelengkapan R). 19 hasil lainnya hanya dua aksioma. Paket 6b memisahkan
secara eksplisit bagian mana yang memerlukan aksioma ketiga.

## 2. Pernyataan yang akan dibuktikan

```coq
Theorem pseries_L2_integer_bounds :
  forall (k N : nat) (L : R),
    (1 <= k)%nat -> (1 <= N)%nat ->
    Un_cv (fun M => psum k N M) L ->
    (1 / (INR k * (INR ((N + 1)%nat)) ^ k) <= L) /\
    (L <= 1 / (INR k * (INR N) ^ k)).
```

yaitu: **jika** limit `L` dari ekor deret-p sudah ada (hipotesis `Un_cv`),
**maka** batas dua sisi berlaku. Ini bagian "batas" dari L2 kit untuk
eksponen bulat; bagian "eksistensi" tetap milik `A-2026-0010`.

## 3. Metode yang dikunci

1. Impor `PseriesL2.v` beku; pakai ulang `Un_cv_le_const`, `psum_upper`,
   `psum_lower_sharp`, `tail_term_small`, `lt_sub_pos`, `sub_le_swap`,
   `pterm_nonneg`, dan `sum_incr` (stdlib).
2. **Tidak** memakai `pseries_L2_integer` dan **tidak** memakai `Un_cv_crit`.
3. Batas bawah memakai argumen ε yang sama seperti `A-2026-0010`, tetapi
   `Hcv` datang dari hipotesis, bukan dari kelengkapan R.

## 4. Kriteria sukses

- `coqc` exit 0 untuk `PseriesL2.v` (beku) dan `PseriesL2Bounds.v`;
  `coqchk` exit 0 "Modules were successfully checked".
- `Print Assumptions pseries_L2_integer_bounds` hanya dua aksioma stdlib:
  `ClassicalDedekindReals.sig_forall_dec` dan
  `FunctionalExtensionality.functional_extensionality_dep`; **tanpa**
  `sig_not_dec`, tanpa aksioma proyek.
- Receipt deterministik (dua capture byte-identik); guard statis + uji
  negatif; registry `A-2026-0011`; HANDOFF; CI hijau.

## 5. Kriteria gagal (dicatat negatif, tidak disembunyikan)

Bila korolari ternyata masih menyeret `sig_not_dec` (misalnya lewat lemma
stdlib yang dipakai ulang), hasilnya dicatat sebagai negatif: bagian mana
yang tetap butuh tiga aksioma, dan tidak ada klaim "dua aksioma" yang dibuat.

## 6. Batas

- Hanya **kondisional**: `Un_cv` adalah hipotesis; eksistensi limit tidak
  dibuktikan di sini (itu `A-2026-0010`, tiga aksioma).
- Hanya eksponen bulat `p = k+1 ≥ 2`; real `p > 1`, L3–L5, periodic-box
  `[J]` tetap di luar scope.
- Tidak ada klaim baru tentang zeta/Weil/RH/P≠NP/fisika.
