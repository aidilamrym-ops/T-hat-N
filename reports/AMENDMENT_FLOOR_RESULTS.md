# AMANDEMEN LANTAI H1 -- hasil terukur (2026-10-16)

Otoritas: `reports/AMENDMENT_FLOOR_SPEC.md` (DIBEKUKAN; sha256
`3c9958bee3021385b242b84b2ecda136e15f35d5682c16ff690713830efbb917`). Bagian (A) grid refined
20000 surrogat dan (B) array robustness 5-seed: **SELESAI**. Bagian
(C) engine B: sesi berikutnya (spec bagian 5; tidak pernah
verdict-bearing).

Dokumen ini dihasilkan mesin oleh `msaf/gw_h1_report.py` dari
`reports/gw_h1_floor_refine.json` + 7 log run + tabel extractor;
tidak ada angka yang diketik ulang oleh manusia. Tabel di bagian 2
adalah keluaran extractor verbatim.

## 1. Yang dieksekusi

- (A) 20000 surrogat per ensemble, dim 201/301/401, seed kanonik
  20260927 -> grid refined 18 sel; target pra-registrasi C1-C4
  ditandai di tabel.
- (B) Array 5-seed S5 pada C4 (dim 301, chart T, sigma_u 0.5): seed
  20260927 (kanonik; entri ini diambil dari run A dim 301 --
  komputasi identik, tanpa duplikasi) + seed 20261001..20261004
  (4 run baru).
- Instrumen: `gw_montgomery.py` revisi `b0af0f519ae25f19178bc3eda4f288970cb49374` (2026-10-06),
  sha256 `072910f232b15768ba35e14d7cc6aaf4fe1ee174dc45b65429460f791196e1d5`, TIDAK dimodifikasi;
  hash on-disk == header ketujuh log. Injeksi seed via override
  modul (instrumen tidak punya flag `--seed`). Hitungan eksak: spy
  read-only `np.mean` (instrumen mencetak p pada %.4f; spec bagian
  3 mempensiunkan string "0.0000").
- Lingkungan: python 3.14.4 + numpy 2.5.2 + scipy 1.18.0;
  OPENBLAS_NUM_THREADS:1 OMP_NUM_THREADS:1 (recorded for the manifest). Catatan operasional: cap
  thread murni kinerja -- rerun capped mereproduksi log tersegel
  persis (bagian 4).
- Tujuh run (semua exit 0; 36/36 tangkapan eksak per run):

| run | seed | samples | elapsed (s) | sha256 log |
|---|---|---|---|---|
| A dim 201 | 20260927 | 20000 | 3115.4 | `b1e4f37d747862a9ce00979f5f7de7df0cf89ace0bbe192c7598d8112ccc90b5` |
| A dim 301 | 20260927 | 20000 | 7514.3 | `a234929ea657d50d61780444576e5275d38c902d94e565da7bae5113ddcb378d` |
| A dim 401 | 20260927 | 20000 | 10443.3 | `369f0d36bdc5c98cc49ccd256701b77731f39034f71350934d658f8a269b86b7` |
| B seed 20261001 | 20261001 | 20000 | 6636.1 | `cf92df3d3516ebf468274ab1bbc9771de12de8977cf6796b2e30ab01c6b52ac1` |
| B seed 20261002 | 20261002 | 20000 | 5947.4 | `f412dadbc4d2915f323b805ff13080888867b7dddc841fbd565c418d59b71a6d` |
| B seed 20261003 | 20261003 | 20000 | 4812.3 | `54acf7b6bc82c7dbfa6c735cacd1512e05a95fc96cf965bd50c950bb4845fb68` |
| B seed 20261004 | 20261004 | 20000 | 4106.2 | `b4d82953f8fed94c61c5ec72d3fa944920da4a44c0144e9234d2edbc8f58c0d2` |

## 2. Grid refined (A) + array robustness (B) -- keluaran mesin
verbatim

## Refined grid (A) -- 20000 surrogates per ensemble, seed 20260927

Target cells (pre-registered, spec section 2): C1 = 201|T|0.3, C2 = 301|T|0.3, C3 = 401|T|0.3, C4 = 301|T|0.5. For these four cells the refined values SUPERSEDE the sealed values; sealed columns remain visible, never edited.

| cell | dim | chart | sigma_u | chi2_obs | k_GUE/20000 | p_GUE | CP95 GUE | k_Pois/20000 | CP95 Pois | verdict | sealed k/2000 | sealed p_GUE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 201 | T | 0.3 | 14419.1614 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 19827/20000 | [9.89968e-01, 9.92587e-01] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
|  | 201 | T | 0.5 | 2140.7335 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 16287/20000 | [8.08891e-01, 8.19718e-01] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
|  | 201 | T | 1.0 | 600.0785 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 611/20000 | [2.82084e-02, 3.30294e-02] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
|  | 201 | L | 0.3 | 47376.9180 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 20000/20000 | [9.99816e-01, 1.00000e+00] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
|  | 201 | L | 0.5 | 10085.3753 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 20000/20000 | [9.99816e-01, 1.00000e+00] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
|  | 201 | L | 1.0 | 4191.0836 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 20000/20000 | [9.99816e-01, 1.00000e+00] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
| C2 | 301 | T | 0.3 | 12154.5726 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 19878/20000 | [9.92721e-01, 9.94932e-01] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
| C4 | 301 | T | 0.5 | 1367.6160 | 1262/20000 | 1262/20000 (6.31000e-02) | [5.97690e-02, 6.65587e-02] | 4807/20000 | [2.34441e-01, 2.46334e-01] | NO DISCRIMINATION AT N=401 | 36/2000 | 0.0180 |
|  | 301 | T | 1.0 | 858.7248 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 1736/20000 | [8.29334e-02, 9.07872e-02] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
|  | 301 | L | 0.3 | 102823.8252 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 20000/20000 | [9.99816e-01, 1.00000e+00] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
|  | 301 | L | 0.5 | 14957.3700 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 20000/20000 | [9.99816e-01, 1.00000e+00] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
|  | 301 | L | 1.0 | 5752.5886 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 20000/20000 | [9.99816e-01, 1.00000e+00] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
| C3 | 401 | T | 0.3 | 11743.7710 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 19933/20000 | [9.95748e-01, 9.97403e-01] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
|  | 401 | T | 0.5 | 1723.5222 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 10544/20000 | [5.20252e-01, 5.34140e-01] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
|  | 401 | T | 1.0 | 820.1678 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 163/20000 | [6.95087e-03, 9.49522e-03] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
|  | 401 | L | 0.3 | 140300.8482 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 20000/20000 | [9.99816e-01, 1.00000e+00] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
|  | 401 | L | 0.5 | 19148.9036 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 20000/20000 | [9.99816e-01, 1.00000e+00] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |
|  | 401 | L | 1.0 | 6355.3766 | 0/20000 | 0/20000 (p < 1.49775e-04, 95% CP upper bound) | [0.00000e+00, 1.49775e-04] | 20000/20000 | [9.99816e-01, 1.00000e+00] | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | 0/2000 | 0.0000 |

## Robustness array (B) -- C4 (dim 301, chart T, sigma_u 0.5), 5 seeds

| seed | k/20000 | p_hat_i | CP95 |
|---|---|---|---|
| 20260927 | 1262/20000 | 6.31000e-02 | [5.97690e-02, 6.65587e-02] |
| 20261001 | 960/20000 | 4.80000e-02 | [4.50783e-02, 5.10540e-02] |
| 20261002 | 1289/20000 | 6.44500e-02 | [6.10854e-02, 6.79419e-02] |
| 20261003 | 1021/20000 | 5.10500e-02 | [4.80401e-02, 5.41913e-02] |
| 20261004 | 1345/20000 | 6.72500e-02 | [6.38170e-02, 7.08094e-02] |

Pooled: 5877/100000 (p_hat = 5.87700e-02), CP95 [5.73201e-02, 6.02456e-02]; homogeneity chi2 = 107.9299, p = 2.01097e-22

Frozen decision tree classification: **NOT STABLE (homogeneity rejected at alpha = 0.01; dispersion-dominated)**

C4 flagged resolution-sensitive per frozen spec section 4; the verdict grid recomputation still uses the canonical 20000 value (number of record).

## 3. Kepatuhan format beku (spec bagian 3)

- "0.0000" pensiun; k=0 dilaporkan sebagai BOUND: p_GUE <
  1.49775e-04 (rumus beku 1 - 0.05^(1/n), n = 20000), tidak pernah
  sebagai nol terukur.
- 17 dari 18 sel grid refined: k_GUE = 0/20000 (bound). Satu sel
  off-floor: C4 = 1262/20000 = 6.31000e-02.
- Verdict refined dihitung ulang dari k eksak dengan aturan yang
  TIDAK berubah; 18/18 cocok dengan verdict tercetak di log.
- Validasi spy: 36/36 tangkapan per run; cocok dengan p tercetak
  pada n=10, pada n=2000 (repro tersegel), dan pada sel positive-k
  n=20000 (1262/20000 <-> 0.0631; 960/20000 <-> 0.0480).
- Nilai tersegel tetap terlihat di semua tempat (kolom sealed);
  refined SUPERSEDE untuk C1-C4 dan dianotasi; dashboard tersegel
  `reports/gw_diagnostic_v3.html` TIDAK disentuh (spec bagian 6.4).

## 4. Bukti reproduktibilitas (commit 993b0e8)

- REPRO CHECK PASS: rerun dim 201 @ 2000 sampel (capped 1-thread)
  mereproduksi log tersegel pada SEMUA field yang dibandingkan
  (chi2, p, verdict, S1/S2 final, r_bar) -- identik. Thread count
  bukan efek numerik.
- Benchmark mesin ini: capped 1-thread ~2x lebih cepat dari default
  (eigvalsh n=301: 20.6 vs 39.6 ms) -- threading murni overhead.
- Instrumen tidak berubah selama kampanye (sha256 on-disk ==
  header semua run).

## 5. Array robustness C4 -- klasifikasi beku (spec bagian 4)

- Pohon keputusan beku, urutan diterapkan: cabang 1. Klasifikasi:
  **NOT STABLE (homogeneity rejected at alpha = 0.01; dispersion-dominated)**.
- Homogenitas Pearson chi2 = 107.9299 (df = 4), p = 2.01097e-22 --
  ditolak pada alpha = 0.01.
- Angka of record: kanonik 20000 = 1262/20000 = 6.31000e-02; pooled
  5-seed = 5877/100000 = 5.87700e-02. C4 ditandai
  resolution-sensitive; verdict grid tetap memakai nilai kanonik
  20000.
- Ekspektasi pra-registrasi yang TERFALSIFIKASI (dicatat, tidak
  dipatch): spec bagian 4 menyatakan "setiap cabang meninggalkan
  C4 di bawah ambang verdict 0.05". Terukur: pooled p_hat = 5.87700e-02;
  4 dari 5 seed >= 0.05 (yang di bawah: 20261001 = 4.80000e-02);
  verdict kanonik = NO DISCRIMINATION (bukan INCONSISTENT).
- Batas interpretasi (beku): bahkan STABLE tidak menjadikan C4
  "physical"; klasifikasi di sini NOT STABLE. Statistik dari
  matriks deterministik berhingga; bukan teorema Montgomery, bukan
  bukti RH.

## 6. Manifest

- repo HEAD saat ekstraksi: `32ac8dca72df60b2f5fa1807798d31b13840e6fb`; ekstraksi: 2026-10-16T19:41:06
- extractor sha256: `67fc149775e1b23ff4ea27150c21c727975756893e2e84fac6b98cdb1870f960`; spec sha256: `3c9958bee3021385b242b84b2ecda136e15f35d5682c16ff690713830efbb917`
- sha256 log refined:
  - A_201: `b1e4f37d747862a9ce00979f5f7de7df0cf89ace0bbe192c7598d8112ccc90b5`
  - A_301: `a234929ea657d50d61780444576e5275d38c902d94e565da7bae5113ddcb378d`
  - A_401: `369f0d36bdc5c98cc49ccd256701b77731f39034f71350934d658f8a269b86b7`
  - B_20261001: `cf92df3d3516ebf468274ab1bbc9771de12de8977cf6796b2e30ab01c6b52ac1`
  - B_20261002: `f412dadbc4d2915f323b805ff13080888867b7dddc841fbd565c418d59b71a6d`
  - B_20261003: `54acf7b6bc82c7dbfa6c735cacd1512e05a95fc96cf965bd50c950bb4845fb68`
  - B_20261004: `b4d82953f8fed94c61c5ec72d3fa944920da4a44c0144e9234d2edbc8f58c0d2`
- sha256 log tersegel (baseline):
  - 201: `811a9dcc055acc1d649ebce1d8fec45b56c4fc26b81060de2f90746e058dfe4d`
  - 301: `faecc52318b729be13c624b589e9d1ed4a332f5da8b2af316957b67f0bf7f017`
  - 401: `eb072757c3b1b18e502ab25dc1bff329d115b7d6c2c74baec89e279340b54b10`

## 7. Catatan deviasi

Tidak ada deviasi prosedural dari spec yang tercatat selama
eksekusi ini. Dua catatan operasional direkam, bukan dipatch
diam-diam: cap thread kinerja (bagian 1) dan reuse entri kanonik
S5 dari run A dim 301 (bagian 1).
