# Pra-registrasi Paket 6 — L2 eksponen bulat (batas dua sisi deret-p)

**Tanggal:** 2026-10-19
**Status:** scope DIKUNCI sebelum implementasi (disiplin paket 4–5)
**Berkas target:** `formal_bridge/PseriesL2.v` (baru; tidak mengubah artefak beku)
**Registry yang direncanakan:** `A-2026-0010`

## 1. Pernyataan yang akan dibuktikan

Untuk setiap `k ≥ 1` (jadi `p = k+1 ≥ 2`) dan `N ≥ 1`:

```
exists L : R,
  Un_cv (fun M => sum_{i=0}^{M} 1 / (INR (N+1+i))^(k+1)) L
  /\
  1 / (INR k * (INR (N+1))^k)  <=  L
  /\
  L  <=  1 / (INR k * (INR N)^k)
```

Ini adalah **L2 kit** (`pseries_tail_bounds`) untuk eksponen bulat `p ≥ 2`,
dua sisi, termasuk langkah limit. Batas bawah dan atas persis bentuk kit:
`1/((p−1)(N+1)^(p−1)) ≤ tail ≤ 1/((p−1)N^(p−1))`.

## 2. Metode yang dikunci

1. **Bernoulli integer** `(1+x)^n ≥ 1 + n x` untuk `x ≥ −1` (induksi, tanpa
   lemma stdlib `Rbernoulli` — tidak ada).
2. **Ketaksamaan langkah** atas dan bawah, keduanya diturunkan dari Bernoulli
   dengan eksponen `k+1` pada `x = ±1/A` (bukan dari integral):
   - atas: `1/n^(k+1) ≤ (1/k)(1/(n−1)^k − 1/n^k)`, `n ≥ 2`;
   - bawah: `1/n^(k+1) ≥ (1/k)(1/n^k − 1/(n+1)^k)`, `n ≥ 1`.
3. **Teleskopik finite** via `sum_f_R0` (lemma teleskopik dibuktikan sendiri).
4. **Eksistensi limit** via `Un_cv_crit` (monoton + terbatas).
5. **Batas atas limit** via lemma urutan-limit (`Un n ≤ B` untuk semua `n`
   ⇒ `limit ≤ B`), dibuktikan dengan ε.
6. **Batas bawah limit** via `sum_incr` (suku tak-negatif: jumlah parsial
   ≤ limit) + `INR_unbounded` untuk mengecilkan sisa `1/(k(N+M+2)^k)`.

## 3. Di luar scope (dilarang melebar tanpa pra-registrasi baru)

- Eksponen real `p > 1` (butuh `Rpower`; **tidak** diklaim).
- L3 (amplop eksponensial), L4 (ekor Gaussian), L5 (perbandingan integral).
- Studi periodic-box `A-2026-0007`; `[J]` di sana tetap OPEN.
- Zeta/Weil/RH, P≠NP, klaim fisik apa pun.
- Klaim bahwa ini menutup semua L2 kit: **hanya** `p ∈ {2,3,4,…}`.

## 4. Kriteria sukses (fail-closed)

- `coqc` exit 0 dan `coqchk` exit 0 ("Modules were successfully checked").
- `Print Assumptions` untuk **setiap** hasil hanya dua aksioma stdlib
  `Coq.Reals` (tidak ada aksioma proyek).
- Tidak ada `Axiom`/`Parameter`/`Admitted`/`admit`.
- Receipt deterministik (dua capture byte-identik).
- Guard statis CI + uji negatif (mutasi harus tertangkap).
- Registry `A-2026-0010` + HANDOFF §2.0ab.

## 5. Kriteria kegagalan (harus dicatat, bukan disembunyikan)

Bila salah satu langkah tidak dapat diformalkan dalam sesi ini, hasilnya
dicatat sebagai **negatif** (bagian mana yang OPEN) dan **tidak** ada
pernyataan yang dilemahkan diam-diam. Tidak boleh mengganti pernyataan
dengan versi yang lebih lemah tanpa pra-registrasi baru.

---

## 6. Addendum pasca-jalan (2026-10-19, sebelum segel)

**Temuan audit.** Kriteria §4 baris kedua ("Print Assumptions ... hanya dua
aksioma stdlib") **tidak terpenuhi secara literal** untuk teorema utama.
`pseries_L2_integer` memakai **tiga** aksioma stdlib: dua aksioma yang sama
seperti Paket 4–5, ditambah `ClassicalDedekindReals.sig_not_dec`. Aksioma
ketiga masuk melalui `Un_cv_crit` (kelengkapan R) yang dipakai untuk
membuktikan eksistensi limit; 19 hasil lainnya tetap hanya dua aksioma.
Tidak ada aksioma proyek.

**Keputusan yang dicatat.** Pernyataan matematis §1 **tidak diubah** dan
**tidak dilemahkan**. Yang berubah hanyalah deskripsi trusted base dalam
kriteria audit. Paket dicatat sebagai **CERTIFIED dengan deviasi audit
tercatat**, bukan sebagai pemenuhan literal kriteria dua-aksioma.
Menghapus `Un_cv_crit` akan memerlukan bukti kelengkapan/konvergensi lain
yang setara dan tidak menambah fakta matematis; itu tidak dilakukan dalam
paket ini. Deviasi ini wajib muncul di laporan, registry, dan HANDOFF.

**Kriteria §4 yang direvisi untuk paket ini.** Setiap hasil hanya memakai
aksioma stdlib `Coq.Reals` (tidak ada aksioma proyek); 19 hasil memakai dua,
teorema utama memakai tiga karena kelengkapan R. Guard statis menolak
aksioma keempat dan menolak penempatan `sig_not_dec` di blok selain
teorema utama.
