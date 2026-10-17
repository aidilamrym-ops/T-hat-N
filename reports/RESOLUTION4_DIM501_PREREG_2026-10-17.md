# Resolution series, fourth point -- pre-registration (dim 501)

Date: 2026-10-17 (local). Status: **PRE-REGISTERED BEFORE ANY 501
COMPUTATION.** At the time of this declaration no 501 eigenvalue, no 501
ladder build and no 501 statistic has been computed. This document and the
new runner it names are committed and pushed BEFORE Stage L of the fourth
point is launched; the git history (add-commit of this file) and the launcher
log `reports/res4_dim501_launch_2026-10-17.log` record the time ordering.

## 1. Reference and scope

- Series so far (measured 2026-10-16, protocol identical at all points):
  dims 201 / 301 / 401, machine-extracted in `reports/THREE_TASKS_2026-10-15.md`
  sections 4-5 (generated marker blocks GW-DELTA / GW-DELTA-3). Quoted test
  version result: S2 FINAL = INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION
  at all three points; across the 18 grid cells the maximum p_GUE = 0.0180,
  none reaching the 0.05 threshold -- the deviation does not shrink toward
  consistency on the available resolutions; S1 FINAL = CHART-DEPENDENT ->
  INCONCLUSIVE at all three.
- With one matrix per resolution the three-point series is explicitly NOT a
  trend statement, and its asymptotic direction remains open by construction.
- The remaining declared lever is a wider block N (README section 6.7,
  roadmap item 2). This document pre-registers the FOURTH point of the
  finite series: dim 501 (c=100, N=250), same instrument and protocol.
- Declared question (frozen): under the SAME instrument rules (#1001630 /
  #1001631 as printed by the instrument, thresholds/grid/bins/seed
  unchanged), what are the S1 verdicts, the S2 p_GUE / p_Pois distribution
  and the S2 FINAL verdict for the dim-501 system, and what does the
  instrument's own RESOLUTION CEILING block print at N=501? No outcome may
  be described as a trend or as a physical statement.
- Scope limits (verbatim, unchanged): statistics of ONE finite constructed
  matrix per resolution; NOT Montgomery's theorem, NOT evidence for RH, NOT
  Weil positivity, NOT prime counting, NOT factorisation.

## 2. Protocol (frozen; identical to series points 1-3; three sequential stages)

- Stage L -- Route S sign ladder, 6000 bit, dim 501:
  `python msaf/gw_route_s_ladder.py --c 100 --ladder 250 --prec 6000 --out reports/gw_route_s_ladder_c100_n250.json`,
  stdout captured to `reports/gw_route_s_ladder_c100_n250.log`.
  Tool `msaf/gw_route_s_ladder.py`, sha256_lf
  `cc09ed5a35ac90b581cf2ef5660f3db903704843909b8a80b7fb21bf036a5b20`
  (unmodified). New output file; the existing series ladder
  `reports/gw_route_s_ladder_c100.json` (N=100,150) is NOT written to.
  Expected (not a promise): CERTIFIED POSITIVE DEFINITE, n_pos = 501,
  n_neg = 0; whatever it prints is reported as-is.
- Stage C -- full arb capture, G-M0 gated:
  `python msaf/capture_spectrum_201.py --c 100 --n 250 --prec 6000`,
  stdout captured to `reports/gw_capture_100_250.log`; artifact
  `reports/gw_spectrum_100_250.json`. Tool
  `msaf/capture_spectrum_201.py`, sha256_lf
  `c41f7b8b4bb0611dbb31d9a2da38fa463f9f8ad175d0a43fb6a77a012460ad9e`
  (unmodified). Chain identical to points 2 and 3 (arb, no decimal
  serialization): external `source_arb_ldlt_certify.build_arb_tau(100, 250, 6000)`
  (`C:/Users/usER/oracle-toe/GUINAND_WEIL/source_arb_ldlt_certify.py`, sha256
  `33617ce64b0e052c07873b196a3744f2f5142a4aaf7b4cfbe9e3de43d17c27bb`)
  -> `arb_mat.eig(algorithm=vdhoeven_mourrain)` at ctx.prec=6000. G-M0 remains
  the publication gate: any FAIL aborts statistics for this point and is
  reported as the outcome (no retry with different parameters).
- Stage M -- canonical measurement:
  `python msaf/gw_series_run.py --spectrum reports/gw_spectrum_100_250.json --samples 2000 --seed 20260927 --log reports/mont_run_100_250.txt --tag RES4_dim501`.
  New runner `msaf/gw_series_run.py`, sha256_lf
  `548c415a97a5d3a78dab7c0d15bb83fbe7277e52a690cd6617a2f9368b3e3f65`;
  it does not modify the instrument. Instrument: sealed `gw_montgomery.py`,
  sha256 `072910f232b15768ba35e14d7cc6aaf4fe1ee174dc45b65429460f791196e1d5`
  (external folder `D:\THE ASYMMETRIC WAGER\guinand-weil-rigorous-numerics-main`;
  frozen, never modified). Draws: EXACTLY 2000 matched-N surrogates per
  ensemble; declared seed 20260927, injected as module SEED (equals the
  instrument default used by points 1-3, so the invocation is
  bit-equivalent to the direct series invocation).
- Provenance wrapper (declared deviation, additive only): the points 1-3
  measurement logs carried only the instrument banner; this point's log
  additionally carries a provenance header (spectrum / instrument / runner
  sha256, instrument git revision, python version, threading environment,
  declared seed and samples, wall-clock start/end) and an observation-only
  spy recording exact counts k/2000 for every np.mean of a boolean array
  (values returned unchanged; printed numbers and verdicts bit-identical;
  expected captures: 36 = 6 cells x 3 kinds x 2 tails). The instrument text
  and numbers are untouched. The Stage M log pins the sha256 of the
  spectrum that Stage C creates (unknowable at pre-registration time by
  construction; its provenance is fully determined by Stage C's pinned
  tool, parameters and G-M0 gate).
- Runner validation (declared): before this pre-registration the new runner
  was exercised once against the EXISTING dim-201 spectrum with
  `--samples 3`, log written outside the repository (temp dir), captures
  36/36; that smoke produced no numbers for the 501 point and is not part
  of any series.
- Environment: single-threaded (OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1),
  recorded in the measurement log header and the launcher log. Stages run
  sequentially, one at a time; no other campaign run overlaps the 501 point.

## 3. Reading rules (FROZEN)

- Quoted verbatim in the report: the instrument's pre-registered rules block
  as printed, S1 per chart (T and L), S2 p_GUE / p_Pois at all 6 grid cells,
  the stability verdict, S2 FINAL, and the RESOLUTION CEILING block.
- Frozen vocabulary note (declared before the run): one instrument verdict
  label contains the literal string "NO DISCRIMINATION AT N=401"; that is
  part of the frozen rule vocabulary written at N=401 and is quoted as
  printed even at N=501 -- the actual N of the run is recorded in the same
  log (banner and ceiling block). Neither is edited.
- Counts: exact integer k/2000 from the spy are the count source; the
  printed %.4f p values are exact at 5e-4 granularity at 2000 samples and
  are reported alongside. No 4-decimal-only counting is used for anything.
- Cross-N raw chi^2 is NOT comparable (pair counts ~N^2/2); the comparable
  statistic remains the matched-N Monte-Carlo p value, exactly as in the
  three-point series.
- All numbers in any report are machine-extracted from the logs; none
  retyped by hand.

## 4. No stopping rules; failure handling

- Every stage is executed and reported whatever it produces; no parameter
  (c, N, prec, samples, seed, thresholds, grid, bins) is changed in response
  to any interim or final result.
- An infrastructure failure (nonzero exit, missing artifact, missing 36
  captures) is reported as such; the SAME stage may be re-run with
  IDENTICAL parameters after the issue is fixed; every attempt is logged;
  numbers from a failed attempt are never used.
- A G-M0 FAIL or a non-PD ladder is NOT an infrastructure failure: it is
  the outcome, reported as-is, and it ends the statistics of this point.

## 5. Artifacts and non-modifications

- New files (this point): `reports/gw_route_s_ladder_c100_n250.json`,
  `reports/gw_route_s_ladder_c100_n250.log`,
  `reports/gw_capture_100_250.log`, `reports/gw_spectrum_100_250.json`,
  `reports/mont_run_100_250.txt`, `reports/res4_dim501_launch_2026-10-17.log`,
  `msaf/gw_series_run.py`; a dated report (`reports/GW_RESOLUTION4_DIM501_<date>.md`)
  after the run, plus HANDOFF/README updates.
- Series documentation is APPEND-ONLY and post-result: the generated blocks
  GW-DELTA and GW-DELTA-3 in `reports/THREE_TASKS_2026-10-15.md` must remain
  byte-identical (same inputs); if the fourth point is published there it
  appears in a NEW appended block, and any generator change is proposed
  separately after the numbers exist.
- SEALED ARTIFACTS NOT MODIFIED (sha256, raw bytes): series logs/artifacts
  `reports/gw_spectrum_100_100.json`
  `c645c590e54717cf793a31ecd941640adbbca162caf15108f56dde1da993f75d`,
  `reports/gw_spectrum_100_150.json`
  `8fded8394f0ab4e8ed83f537609d313d0d50eef42f09214c30d1cfcd994d161d`,
  `reports/gw_route_s_ladder_c100.json`
  `674a50d3057aa19ce51e28841bef6dcde93fff91ec3adbb945611a9059574558`,
  `reports/gw_capture_100_100.log`
  `0908b3dfc124431ca553ee516f12c9a05eeaa262d3c2e2a980ac48ee7f69f6dd`,
  `reports/gw_capture_100_150.log`
  `f2e2ffa2cbcc2554139743481ab7cf52351d0124f6577a35a45b1345528a1e26`,
  `reports/mont_run_100_100.txt`
  `811a9dcc055acc1d649ebce1d8fec45b56c4fc26b81060de2f90746e058dfe4d`,
  `reports/mont_run_100_150.txt`
  `faecc52318b729be13c624b589e9d1ed4a332f5da8b2af316957b67f0bf7f017`,
  `msaf/mont_run.txt`
  `eb072757c3b1b18e502ab25dc1bff329d115b7d6c2c74baec89e279340b54b10`;
  plus the sealed campaign artifacts named in the C4 pre-registration
  (`reports/gw_h1_floor_refine.json` sha256_lf
  `4777d94f9ec533712b14cc097b9240e5c961790b3d9025f452b7c21aade6148f`,
  `reports/AMENDMENT_FLOOR_SPEC.md` sha256_lf
  `3c9958bee3021385b242b84b2ecda136e15f35d5682c16ff690713830efbb917`,
  the dashboards v3/v4/v5 and the README machine block) and
  `msaf/gw_h1_floor_refine.py` sha256_lf
  `c70a76973e8e4e756642f310af4f7a721c6bbde485c7d8dcb5ab20961e4a5cf2`.

## 6. Cost note (measured anchors, not a promise)

- Stage L: ladder at N=150 (dim 301) measured build 619.74 s + LDL^T 57.1 s
  (`THREE_TASKS` section 5.1); at N=250 expected of order 30-45 min on this
  machine (build ~dim^2, LDL^T ~dim^3).
- Stage C: eig history dims 201 / 301 / 401 = 825.7 s / 3137.6 s / 1862.2 s
  (non-monotone, conditioning-dependent; dim 401 used the older chain). At
  dim 501, eig alone expected of order 1.5-4.5 h plus build ~0.5 h; total
  Stage C of order 2-5 h.
- Stage M: of order 0.5-1.5 h at dim 501 / 2000 samples (scaled from
  dim-301 measurements, single-threaded).
- Total stage of order 3.5-7.5 h wall time; machine-dependent.

## 7. Ordering proof

- This file and `msaf/gw_series_run.py` are committed and pushed BEFORE
  Stage L is launched. The launcher log records: the repository HEAD sha at
  launch (must be the add-commit of this file or a later commit), the
  environment, and per-stage launch/finish timestamps. Every stage start
  time must be later than the add-commit time of this file.

Declared by the analysis session on 2026-10-17, before launch.
