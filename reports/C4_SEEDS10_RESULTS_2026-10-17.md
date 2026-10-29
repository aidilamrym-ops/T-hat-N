# C4 S10 â€” result ekstensi array robustness (2026-10-17)

Otoritas: `reports/C4_SEEDS10_PREREG_2026-10-17.md` (sha256_lf
`d8dd65cd614f5457a5fe12f7aa24556dc97a4dcda57fed0d01b69f8fb34a0b95`;
commit `657352cc2b47ee8480686c4281664b70a5714c64`, dipush SEBELUM draw
pertama â€” urutan diverifikasi mesin, section 3). Dokumen ini melaporkan
eksekusi penuh perluasan S5 â†’ S10 on sel C4 (dim 301, chart T,
sigma_u 0.5). Tidak ada file tersegel which diubah; no ada angka
which diketik ulang oleh manusia (semua dari ekstraktor/log).

## 1. Yang dieksekusi

- Lima run instrumen baru, seed `20261005..20261009` (dideklarasikan in
  pra-registrasi section 2; aturan pemilihan: lima bilangan bulat
  berurutan berikutnya â€” bukan dipilih dari result), 20000 surrogat per
  seed, instrumen and spektrum identik with batch 2026-10-16:
  `python msaf/gw_h1_floor_refine.py --spectrum reports/gw_spectrum_100_150.json --samples 20000 --seed <s> --log reports/mont_run_20000_s<s>_100_150.txt --tag B_seed<s>`.
- Konkurensi cap-2 rolling queue (pra-registrasi section 3); setiap
  launch/finish tercatat in `reports/c4_seeds10_launch_2026-10-17.log`
  (start 13:47:27 lokal, HEAD check OK in `657352c`; ALL DONE 16:50:33;
  kelima `runner exit=0`).
- Header kelima log memuat instrument sha
  `072910f232b15768ba35e14d7cc6aaf4fe1ee174dc45b65429460f791196e1d5`
  and spectrum sha
  `8fded8394f0ab4e8ed83f537609d313d0d50eef42f09214c30d1cfcd994d161d`;
  36/36 tangkapan eksak per run; stderr 0 byte for kelima run.

| run | seed | elapsed (s) | sha256_lf log |
|---|---|---|---|
| B_seed20261005 | 20261005 | 4126.0 | `8f37dfbfb96d8f4e3f82ebbac5898416abb622a6010e6a000afc4afee10300cb` |
| B_seed20261006 | 20261006 | 4151.7 | `358223f0e72bbe2ab88e19eefc37552d2fede56bdc4290fba6c80887716cff90` |
| B_seed20261007 | 20261007 | 4000.5 | `981311dc0c42d34183b8e51093076fec591e8d77bd6838a64fd77a5e9f0b4d86` |
| B_seed20261008 | 20261008 | 3925.8 | `e750fe7ca3180f29a7386af4582eca2a586757f7d36b53bfba2ba3a9faa3cd27` |
| B_seed20261009 | 20261009 | 2852.0 | `64ec51ee2a0a9d871547c2f16bed020501af81f2426d744029e03ce9c27afbea` |

## 2. Hasil â€” keluaran mesin verbatim

Blok berikut adalah keluaran `msaf/gw_h1_c4_seeds10.py` (fungsi
`render_section`) dari artefak `reports/gw_h1_c4_seeds10.json`; no
ada angka which diketik ulang.

```
## C4 robustness array extension (S10) -- dim 301, chart T, sigma_u 0.5

Pre-registration: `reports/C4_SEEDS10_PREREG_2026-10-17.md` (commit 657352cc2b47ee8480686c4281664b70a5714c64; ordering check: PASS).

| seed | k/20000 | p_hat_i | CP95 | segment |
|---|---|---|---|---|
| 20260927 | 1262/20000 | 6.31000e-02 | [5.97690e-02, 6.65587e-02] | S5 (sealed) |
| 20261001 | 960/20000 | 4.80000e-02 | [4.50783e-02, 5.10540e-02] | S5 (sealed) |
| 20261002 | 1289/20000 | 6.44500e-02 | [6.10854e-02, 6.79419e-02] | S5 (sealed) |
| 20261003 | 1021/20000 | 5.10500e-02 | [4.80401e-02, 5.41913e-02] | S5 (sealed) |
| 20261004 | 1345/20000 | 6.72500e-02 | [6.38170e-02, 7.08094e-02] | S5 (sealed) |
| 20261005 | 1164/20000 | 5.82000e-02 | [5.49947e-02, 6.15345e-02] | S10 (new) |
| 20261006 | 1115/20000 | 5.57500e-02 | [5.26100e-02, 5.90199e-02] | S10 (new) |
| 20261007 | 1114/20000 | 5.57000e-02 | [5.25613e-02, 5.89686e-02] | S10 (new) |
| 20261008 | 1022/20000 | 5.11000e-02 | [4.80887e-02, 5.42427e-02] | S10 (new) |
| 20261009 | 1166/20000 | 5.83000e-02 | [5.50921e-02, 6.16371e-02] | S10 (new) |

Pooled (S10, 10 seeds): 11458/200000 (p_hat = 5.72900e-02), CP95 [5.62754e-02, 5.83174e-02]

Homogeneity: Pearson chi2 = 131.2879, df = 9, p = 6.44376e-24

Frozen decision tree classification: **NOT STABLE (homogeneity rejected at alpha = 0.01; dispersion-dominated)**

C4 stays flagged resolution-sensitive per frozen spec section 4; the verdict grid recomputation still uses the canonical 20000 value (number of record).

Number of record (UNCHANGED): 1262/20000 = 6.31000e-02 (canonical seed 20260927).

Old five seeds: re-parsed from the original logs and cross-checked against the sealed artifact (`reports/gw_h1_floor_refine.json`, sha256_lf 4777d94f9ec533712b14cc097b9240e5c961790b3d9025f452b7c21aade6148f); cross-check PASS.
```

## 3. Verifikasi (mesin + independen)

- `--write` ekstraktor dijalankan 2026-10-17 16:52:38 lokal on HEAD
  `657352c` (pra-registrasi; result mentah dikomit setelahnya):
  - cross-check keras 5 seed lama vs artefak tersegel: **PASS**
    (9/9 check: `k_match`, `pooled_k_match`, `pooled_n_match`,
    `p_hat_match`, `homogeneity_stat_match`, `homogeneity_p_match`,
    `classification_match`, `pooled_cp95_match`, `per_seed_cp95_match`).
  - guard log baru 5/5 lolos (samples = 20000; seed cocok; instrument
    sha cocok; spectrum sha cocok; exit = 0; 36 tangkapan; 6 sel
    terparsing; sel C4 ada; ukuran tangkapan = 20000).
  - ordering pra-registrasi: **PASS** â€” commit pra-registrasi
    2026-10-17T13:45:32 lokal < start run baru pertama
    2026-10-17T13:47:32 lokal (anti-cocoklogi).
- Verifikasi footer independen oleh sesi ini (bukan section ekstraktor):
  kelima log dibaca ulang and dicocokkan per-field
  (samples/seed/sha instrumen/sha spektrum/exit/captures) â€” 5/5 PASS;
  stdout per seed memuat `captures=36, exit=0`; stderr 0 byte.
- Kepatuhan tanpa stopping rule: kelima run dieksekusi penuh and
  dilaporkan; no ada seed ditambah, dibuang, or diganti.

## 4. Klasifikasi and pembacaan (limit beku diulang)

- Pertanyaan pra-registrasi section 1 ("dispersi bertahan, melemah, or
  menguat on sepuluh seed?") â€” terukur: **bertahan**. NOT STABLE
  (homogeneity rejected; dispersion-dominated) tetap bertahan on
  n = 10 with p = 6.44376e-24.
- Konteks warisan (base spec Â§4, falsifikasi tercatat 2026-10-16):
  9/10 seed `p_hat_i >= 0.05` (which in bawah hanya 20261001 =
  4.80000e-02); pooled S10 = 5.72900e-02 masih >= 0.05 â€” no ada
  tambal-menambal, no ada reinterpretasi base spec.
- **Angka of record TIDAK berubah:** kanonik `1262/20000` =
  6.31000e-02; pooled S10 adalah pernyataan robustness which diperluas,
  bukan pengganti.
- Batas (beku): NOT STABLE; bukan "physical"; statistik dari matriks
  deterministik berhingga on presisi/keputusan which dinyatakan; bukan
  teorema Montgomery, bukan bukti RH, bukan Weil positivity, bukan
  prime counting. Seri resolusi keempat (dim 501) tetap tersisa.

## 5. Insiden CI â€” dicatat, no disembunyikan

- Run `39019056454` (commit `19fe938`): `python-tests` GAGAL in
  `msaf/tests/test_gw_h1_c4_seeds10.py::test_committed_artifact_equals_fresh_extraction`.
  Asersi menuntut kesetaraan float **bit-exact** antara artefak
  terkomit (created in Windows) and ekstraksi segar (CI Linux). Dari log
  run: hanya `per_seed_cp95` which berbeda, ~1 ULP (contoh
  `0.05976897156794577` vs `0.05976897156794578`); SEMUA count, seed,
  `p_hat`, `pooled_cp95`, `homogeneity_stat`, `homogeneity_p`, and
  string klasifikasi identik. Akar: `scipy.stats.beta.ppf`
  (Clopper-Pearson) no bit-identik lintas platform/kompilasi
  (kedua sisi scipy 1.18.0; Python 3.14.8 CI vs 3.14.4 lokal).
- Perbaikan in akar (commit `15f767f`): komparator toleransi â€”
  int/string/bool harus eksak; float `rel_tol = 1e-12` (kebijakan
  `_close` which already dipakai ekstraktor for field which sama) â€” plus
  tes pengunci semantik komparator (1 ULP lolos; 1e-6 gagal; struktur
  salah gagal). Tidak ada artefak, log, angka, or ekstraktor which
  disentuh (`gw_h1_c4_seeds10.py` tetap sha `c65dcc7f...`).
- Hasil: CI hijau run `39019664353` (`python-tests` 352 passed +
  1 skipped; 1 skip kondisi which sama seperti run-run CI sebelumnya;
  `lean-kernel` hijau). Suite lokal (Windows): 353 passed.
- Angka insiden (verbatim dari log CI): run gagal `1 failed, 350
  passed, 1 skipped in 44.89s`; run hijau `352 passed, 1 skipped in
  44.84s`.

## 6. Manifest

- Rantai commit: `657352c` (pra-registrasi, CI hijau `39007483985`) â†’
  `19fe938` (result mentah: 5 log run + launcher + stdout/stderr +
  artefak + section; CI GAGAL `39019056454`) â†’ `15f767f` (perbaikan
  tes, disklosur; CI hijau `39019664353`) â†’ report ini + pembaruan
  HANDOFF/README.
- sha256_lf: pra-registrasi `d8dd65cd...`; artefak
  `b57e1c7af5eac363543a3aee74cdd09829a9babfe5812fd2addad8db0a741419`;
  section `55fc90f5688f399db44a79bf2c698c9a6e3cf8952f9d433da25e8f3f5ada87d2`;
  launcher log `3e5ff247dd9b1596e88bdaaa483813fc60a2f03bb242979b54c578fb57b261c5`;
  5 log run: lihat tabel section 1; ekstraktor `c65dcc7f...`; tes
  (pasca-perbaikan) `b38a41bb88112d553a27dcb2615488ed993838fe87a36e8883043112f560afc6`;
  instrumen `072910f2...`; spektrum `8fded839...`; base tersegel
  `4777d94f...`.
- `manifest.repo_head` artefak = `657352c` (ekstraksi berjalan on
  HEAD pra-registrasi), `generated` = 2026-10-17T16:52:38;
  `prereg_order_check` = PASS.
- Berkas mentah which dikomit in `19fe938`: 5 log
  `reports/mont_run_20000_s2026100[5-9]_100_150.txt`, 5Ã—2
  stdout/stderr launcher, `reports/c4_seeds10_launch_2026-10-17.log`,
  `reports/gw_h1_c4_seeds10.json`, `reports/h1_c4_seeds10_section.md`.

## 7. Batas (baca harfiah)

Semua verdict in dokumen ini adalah pernyataan tentang satu matriks
deterministik berhingga on presisi and aturan keputusan which
dinyatakan â€” enclosure, bukan kebenaran absolut. Tidak ada klaim
universal/infinite; no ada klaim dampak. Seri resolusi keempat
(dim 501) tetap menjadi step berikutnya.


