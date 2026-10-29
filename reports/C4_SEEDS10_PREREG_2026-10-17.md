# C4 robustness array extension -- pre-registration (S5 -> S10)

Date: 2026-10-17 (local). Status: **PRE-REGISTERED BEFORE ANY DRAW.** This
document, the extraction tool it names, and their tests are committed and
pushed BEFORE the first of the five new instrument runs is launched; the git
history (add-commit of this file) and the launcher log
`reports/c4_seeds10_launch_2026-10-17.log` record the time ordering.

## 1. Reference and scope

- Base amendment (FROZEN, unmodified): `reports/AMENDMENT_FLOOR_SPEC.md`
  section 4, sha256
  `3c9958bee3021385b242b84b2ecda136e15f35d5682c16ff690713830efbb917`,
  which froze the five-seed array S5 for the C4 cell.
- This document EXTENDS S5 by five fresh seeds (S10 = S5 + S_plus5). It does
  not edit, supersede or reinterpret the base amendment; the frozen spec
  remains the record of S5, and this document is the record of the
  extension.
- State being extended, as sealed in `reports/gw_h1_floor_refine.json`
  (sha256_lf `4777d94f9ec533712b14cc097b9240e5c961790b3d9025f452b7c21aade6148f`),
  C4 = dim 301 / chart T / sigma_u 0.5:
  k = [1262, 960, 1289, 1021, 1345]; pooled 5877/100000
  (p_hat = 5.87700e-02), CP95 [5.73201e-02, 6.02456e-02];
  homogeneity chi2 = 107.92990453585426, df = 4, p = 2.01096665341861e-22;
  frozen-tree classification: NOT STABLE (homogeneity rejected at
  alpha = 0.01; dispersion-dominated).
- Declared question of this extension (stated before any draw): does the
  dispersion picture persist, weaken or strengthen when the array is
  enlarged to ten seeds? No outcome may be described as "physical"; the
  interpretation limits of the base amendment (section 4) apply verbatim.

## 2. New seed identities (FROZEN, declared now)

- S_plus5 = [20261005, 20261006, 20261007, 20261008, 20261009].
- Selection rule, stated before any draw and with no other criterion: the
  next five consecutive integers in the same declared series after the last
  seed of S5 (20261004). Seeds are labels, not run dates; they were fixed by
  this rule, not chosen, ranked or inspected against anything.

## 3. Protocol (identical to the base amendment; frozen)

- Instrument: sealed `gw_montgomery.py`, sha256
  `072910f232b15768ba35e14d7cc6aaf4fe1ee174dc45b65429460f791196e1d5`
  (frozen; never modified), invoked through `msaf/gw_h1_floor_refine.py`
  (sha256_lf
  `c70a76973e8e4e756642f310af4f7a721c6bbde485c7d8dcb5ab20961e4a5cf2`)
  exactly as in the 2026-10-16 batch:
  `python msaf/gw_h1_floor_refine.py --spectrum reports/gw_spectrum_100_150.json --samples 20000 --seed <s> --log reports/mont_run_20000_s<s>_100_150.txt --tag B_seed<s>`
- Spectrum: `reports/gw_spectrum_100_150.json`, sha256
  `8fded8394f0ab4e8ed83f537609d313d0d50eef42f09214c30d1cfcd994d161d`,
  dim 301 ONLY.
- Draws: EXACTLY 20000 fresh surrogates per seed for the C4 statistic.
- Exact counts: the runner's spy on np.mean of boolean arrays (36 captures
  expected); the C4 count is capture index 6 (0-based: cell T|0.5, kind gue,
  upper tail). Printed 4-decimal p values are never a source of counts.
- Environment: single-threaded per run (OPENBLAS_NUM_THREADS=1,
  OMP_NUM_THREADS=1), recorded in each log header.
- Concurrency (declared): at most TWO instrument runs simultaneously;
  rolling queue in seed order 20261005 -> 20261009; every launch and finish
  is recorded in `reports/c4_seeds10_launch_2026-10-17.log`. Runs are
  deterministic per seed; concurrency affects wall time only.

## 4. Analysis (FROZEN, identical to the base amendment with n = 10 seeds)

- Estimators: per-seed exact counts k_i; pooled p_hat = sum(k_i)/200000;
  95% Clopper-Pearson intervals (same construction, including the k = 0
  bound rule); per-seed CP intervals reported.
- Homogeneity: Pearson chi-square on the 10x2 count table against the
  pooled rate; df = 9; alpha = 0.01.
- Classification: the SAME frozen decision tree, in the SAME order, with
  the SAME thresholds (branch 1: homogeneity rejected -> NOT STABLE
  (dispersion-dominated); branch 2: pooled p_hat < 0.010 -> NOT STABLE;
  branch 3: pooled p_hat in [0.010, 0.045] and every per-seed p_hat_i in
  [0.002, 0.060] -> STABLE OFF-FLOOR; else MIXED).
- Number of record: UNCHANGED -- the canonical 20000-surrogate estimate of
  seed 20260927 (1262/20000 = 6.31000e-02); the S10 pooled result is the
  enlarged robustness statement reported alongside; the 18-cell verdict
  grid recomputation continues to use the canonical value.

## 5. No stopping rules; failure handling

- All five runs are executed and reported regardless of interim or final
  numbers; no seed is added, dropped or replaced in response to results.
- A run interrupted by an infrastructure failure (nonzero exit or missing
  exact counts) is reported as such; the SAME seed may be re-run after the
  issue is fixed; every attempt is logged, and a failed attempt's numbers
  are never used.

## 6. Artifacts and non-modifications

- New run logs (five): `reports/mont_run_20000_s20261005_100_150.txt` ...
  `reports/mont_run_20000_s20261009_100_150.txt`.
- Launcher log: `reports/c4_seeds10_launch_2026-10-17.log`.
- New machine artifact after all five runs: `reports/gw_h1_c4_seeds10.json`
  and `reports/h1_c4_seeds10_section.md`, produced by
  `msaf/gw_h1_c4_seeds10.py` (sha256_lf
  `c65dcc7f2e9e2338a30b5dffaf22284e2c92384b71e77cf1ad6156cedb60124a`;
  arithmetic imported unchanged from the sealed extractor
  `msaf/gw_h1_extract.py`, sha256
  `67fc149775e1b23ff4ea27150c21c727975756893e2e84fac6b98cdb1870f960`).
  The tool re-parses the five original k values from the original logs and
  HARD cross-checks them and every sealed aggregate against
  `reports/gw_h1_floor_refine.json` before aggregating; it also records a
  pre-registration ordering check (every new run's start must be later than
  the add-commit time of this file). Its tests live in
  `msaf/tests/test_gw_h1_c4_seeds10.py` (series lock, seal cross-check,
  artifact self-validation once the new logs exist).
- SEALED ARTIFACTS ARE NOT MODIFIED: `reports/gw_h1_floor_refine.json`,
  `reports/h1_floor_refine_section.md`, `reports/AMENDMENT_FLOOR_SPEC.md`,
  `reports/AMENDMENT_FLOOR_RESULTS.md`, `reports/gw_diagnostic_v5.html` and
  the README machine block stay byte-identical. The S10 result is carried by
  new files plus a dated report and is intended for the consolidated
  dashboard v6 after the campaign extension completes.

## 7. Cost note (measured 2026-10-16, not a promise)

- One dim-301 / 20000-surrogate run measured 68.4-125.2 minutes wall time on
  this 4-logical-core machine (68.4 / 80.2 / 99.1 / 110.6 min for the four
  seeds at rolling 2/3/3/4-run concurrency).
- At rolling cap-2 the five new runs are expected to take roughly 3.5-4.5
  hours total.

Declared by the analysis session on 2026-10-17, before launch.


