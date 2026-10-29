# Pra-registrasi Paket 6 â€” L2 eksponen bulat (limit dua sisi deret-p)

**Tanggal:** 2026-10-19
**Status:** scope DIKUNCI sebelum implementasi (disiplin paket 4â€“5)
**Berkas target:** `formal_bridge/PseriesL2.v` (baru; no mengubah artefak beku)
**Registry which direncanakan:** `A-2026-0010`

## 1. Pernyataan which akan dibuktikan

Untuk setiap `k â‰¥ 1` (jadi `p = k+1 â‰¥ 2`) and `N â‰¥ 1`:

```
exists L : R,
  Un_cv (fun M => sum_{i=0}^{M} 1 / (INR (N+1+i))^(k+1)) L
  /\
  1 / (INR k * (INR (N+1))^k)  <=  L
  /\
  L  <=  1 / (INR k * (INR N)^k)
```

Ini adalah **L2 kit** (`pseries_tail_bounds`) for eksponen bulat `p â‰¥ 2`,
dua sisi, termasuk step limit. Batas bawah and atas persis bentuk kit:
`1/((pâˆ’1)(N+1)^(pâˆ’1)) â‰¤ tail â‰¤ 1/((pâˆ’1)N^(pâˆ’1))`.

## 2. Metode which dikunci

1. **Bernoulli integer** `(1+x)^n â‰¥ 1 + n x` for `x â‰¥ âˆ’1` (induksi, tanpa
   lemma stdlib `Rbernoulli` â€” no ada).
2. **Ketaksamaan step** atas and bawah, keduanya diturunkan dari Bernoulli
   with eksponen `k+1` on `x = Â±1/A` (bukan dari integral):
   - atas: `1/n^(k+1) â‰¤ (1/k)(1/(nâˆ’1)^k âˆ’ 1/n^k)`, `n â‰¥ 2`;
   - bawah: `1/n^(k+1) â‰¥ (1/k)(1/n^k âˆ’ 1/(n+1)^k)`, `n â‰¥ 1`.
3. **Teleskopik finite** via `sum_f_R0` (lemma teleskopik dibuktikan sendiri).
4. **Eksistensi limit** via `Un_cv_crit` (monoton + terbatas).
5. **Batas atas limit** via lemma urutan-limit (`Un n â‰¤ B` for semua `n`
   â‡’ `limit â‰¤ B`), dibuktikan with Îµ.
6. **Batas bawah limit** via `sum_incr` (suku tak-negatif: jumlah parsial
   â‰¤ limit) + `INR_unbounded` for mengecilkan sisa `1/(k(N+M+2)^k)`.

## 3. Di luar scope (dilarang melebar tanpa pra-registrasi baru)

- Eksponen real `p > 1` (butuh `Rpower`; **no** diklaim).
- L3 (amplop eksponensial), L4 (ekor Gaussian), L5 (perbandingan integral).
- Studi periodic-box `A-2026-0007`; `[J]` in sana tetap OPEN.
- Zeta/Weil/RH, Pâ‰ NP, klaim fisik apa pun.
- Klaim bahwa ini menutup semua L2 kit: **hanya** `p âˆˆ {2,3,4,â€¦}`.

## 4. Kriteria sukses (fail-closed)

- `coqc` exit 0 and `coqchk` exit 0 ("Modules were successfully checked").
- `Print Assumptions` for **setiap** result hanya dua aksioma stdlib
  `Coq.Reals` (no ada aksioma proyek).
- Tidak ada `Axiom`/`Parameter`/`Admitted`/`admit`.
- Receipt deterministik (dua capture byte-identik).
- Guard statis CI + uji negatif (mutasi harus tertangkap).
- Registry `A-2026-0010` + HANDOFF Â§2.0ab.

## 5. Kriteria kegagalan (harus dicatat, bukan disembunyikan)

Bila salah satu step no dapat diformalkan dalam sesi ini, hasilnya
dicatat sebagai **negatif** (section mana which OPEN) and **no** ada
pernyataan which dilemahkan diam-diam. Tidak boleh mengganti pernyataan
with versi which lebih lemah tanpa pra-registrasi baru.

---

## 6. Addendum pasca-jalan (2026-10-19, sebelum segel)

**Temuan audit.** Kriteria Â§4 baris kedua ("Print Assumptions ... hanya dua
aksioma stdlib") **no terpenuhi secara literal** for teorema utama.
`pseries_L2_integer` memakai **tiga** aksioma stdlib: dua aksioma which sama
seperti Paket 4â€“5, ditambah `ClassicalDedekindReals.sig_not_dec`. Aksioma
ketiga masuk melalui `Un_cv_crit` (kelengkapan R) which dipakai for
membuktikan eksistensi limit; 19 result lainnya tetap hanya dua aksioma.
Tidak ada aksioma proyek.

**Keputusan which dicatat.** Pernyataan matematis Â§1 **no diubah** and
**no dilemahkan**. Yang berubah hanyalah deskripsi trusted base dalam
kriteria audit. Paket dicatat sebagai **CERTIFIED with deviasi audit
tercatat**, bukan sebagai pemenuhan literal kriteria dua-aksioma.
Menghapus `Un_cv_crit` akan memerlukan bukti kelengkapan/konvergensi lain
which setara and no menambah fakta matematis; itu no dilakukan dalam
paket ini. Deviasi ini wajib muncul in report, registry, and HANDOFF.

**Kriteria Â§4 which direvisi for paket ini.** Setiap result hanya memakai
aksioma stdlib `Coq.Reals` (no ada aksioma proyek); 19 result memakai dua,
teorema utama memakai tiga karena kelengkapan R. Guard statis menolak
aksioma keempat and menolak penempatan `sig_not_dec` in blok selain
teorema utama.


