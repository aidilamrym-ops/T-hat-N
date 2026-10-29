# AMENDMENT-FLOOR-SPEC -- pre-registration for the H1 floor refinement and the dual-engine verification

FROZEN specification. No measurement described in this document has been
executed at freeze time. Any edit after the first execution starts is
FORBIDDEN; changes require a NEW dated amendment document (append-only
culture, same discipline as the defect register).

## 0. Baseline and motivation

Baseline: `a37b50b7dbdd7035cbeedc016e0a4070550557d1` (HEAD at freeze; tag
`v1.40.0-alpha-final-certified-delivery`), tree clean, suite 311 green.

Baseline drift note (for future sessions): briefs may cite commits
`6a69de4` and `14a1588`; verified in this repository, BOTH are ANCESTORS
of the sealed HEAD (intermediate milestones on 2026-10-16: `14a1588`
09:22:52, `6a69de4` 12:29:40). The sealed campaign state is `a37b50b`,
three commits later (`28de2b8`, `86b161f` in between). Execution of this
amendment starts from `a37b50b` or later.

Motivation. The sealed S2 FINAL grid reports `p_GUE = 0.0000` for 17 of
the 18 cells: printed as 0.0000, meaning chi2_obs exceeds the chi2 of ALL
2000 surrogates -- a CENSORED value with resolution 1/2000 = 5e-4. The
single off-floor cell reads 36/2000 = 0.0180 (dim 301, chart T,
sigma_u = 0.5). The first expected expert critique is exactly this floor.
This amendment pre-declares how the floor question and the stability
question for the 0.0180 cell are answered, BEFORE any new run, so that no
analytical choice can drift with results.

## 1. Scope and non-goals

In scope:
(A) surrogate-parameter upgrade 2000 -> exactly 20000 for four declared
    cells: the three chart-T sigma_u = 0.3 cells (dim 201 / 301 / 401) and
    the single 0.0180 cell (dim 301, chart T, sigma_u = 0.5);
(B) multi-seed robustness array for the 0.0180 cell;
(C) specification (architecture only) of the second, independent S2
    verification harness ("engine B").

NOT in scope: new spectra; new resolutions; new statistics; changes to the
S2 estimator, kernel, grid, weights or the 0.05 verdict threshold; changes
to gate G-M0; any global precision/ctx.prec mutation (repository landmine
discipline applies; no-leakage bounds unchanged).

## 2. Frozen target cells (transcribed from sealed artifacts)

Values below are transcription only, from the sealed S2 FINAL grid
(`exports/research_paper.tex` Table 2; canonical logs e.g.
`reports/mont_run_100_150.txt` lines 137-138; cross-checked 18/18).

| # | dim | chart | sigma_u | chi2_obs | k_GUE/2000 | p_GUE (sealed) | p_Pois (sealed) | role |
|---|-----|-------|---------|----------|------------|----------------|-----------------|------|
| C1 | 201 | T | 0.3 | 14621.8788 | 0/2000 | 0.0000 (floor) | 0.9910 | floor refinement |
| C2 | 301 | T | 0.3 | 12448.7407 | 0/2000 | 0.0000 (floor) | 0.9950 | floor refinement |
| C3 | 401 | T | 0.3 | 11639.5769 | 0/2000 | 0.0000 (floor) | 0.9980 | floor refinement |
| C4 | 301 | T | 0.5 | 1393.1679 | 36/2000 | 0.0180 | 0.2390 | robustness array |

Count notes: 36/2000 = 0.0180 exactly (0.018 x 2000 = 36); the floor cells
print 0.0000 meaning chi2_obs exceeds the chi2 of ALL 2000 surrogates
(k = 0), as stated in the sealed manuscript text.

Note (no cherry-picking): ensembles are shared per dimension, so the
20000-ensemble runs also refine every OTHER cell at dims 201/301/401 at
zero extra ensemble cost. The full refined 18-cell grid WILL be emitted
and published as-is; the four cells above are the pre-registered focus,
not the only numbers reported.

## 3. (A) Parameter upgrade protocol

- Surrogates: EXACTLY n = 20000 per ensemble, per dimension.
- Dimensions: 201, 301, 401 (the three sealed resolutions).
- Ensembles: GUE (verdict-bearing primary) and Poisson (verdict-bearing
  primary), matched-N as sealed; GOE reported-only, unchanged status.
- Seed: the canonical declared seed 20260927 (declared before the original
  run and unchanged since; `gw_montgomery.py` line 98). Superset
  consistency with the old 2000 draws is NOT assumed and NOT required;
  both old and refined values are reported side by side.
- Instrument: same script/revision as sealed (`gw_montgomery.py` pipeline);
  the run manifest MUST record the git revision of every script used.
- Output format (frozen): p values printed as EXACT COUNTS `k/20000` AND
  as decimals with at least 6 significant digits. The string "0.0000" is
  RETIRED for these runs. For k = 0 the report must state the claim as
  p_GUE < 1.50e-4 (95% Clopper-Pearson upper bound for 0/20000; exact
  formula 1 - 0.05^(1/n)), labelled as a BOUND, never as a measured zero.
- Reporting rule: for each target cell report the literal integer counts
  (k_GUE/20000, k_Pois/20000) plus 95% Clopper-Pearson intervals.
- Verdict recalculation: UNCHANGED rules (p_GUE >= 0.05 and p_Pois < 0.05
  -> CONSISTENT; p_GUE < 0.05 -> INCONSISTENT; grid consistency required
  or UNSTABLE). The refined verdict grid is published in full. The sealed
  values remain visible; refined values SUPERSEDE for the target cells and
  are annotated as such (old values are never deleted or silently edited).

## 4. (B) Robustness seed array -- the 0.0180 cell (36/2000 events)

Question (frozen): is 36/2000 = 0.0180 a stable, small off-floor property
of cell C4 at the tested resolutions, or an ensemble-level fluctuation of
one seed? (Neither branch is permitted to call the cell "physical"; see
the interpretation limits below.)

- Seed array (FROZEN, arbitrary-but-declared-now; precedent for declaring
  seeds before any draw: `gw_s2_ceiling.py`):
  S5 = [20260927, 20261001, 20261002, 20261003, 20261004].
  Five independent runs of the full instrument on dim 301 ONLY, each with
  EXACTLY 20000 fresh GUE surrogates for the C4 statistic.
- Estimators: per-seed counts k_i; pooled p_hat = sum(k_i)/100000 with a
  95% Clopper-Pearson interval; per-seed CP intervals reported.
- Homogeneity: Pearson chi-square test on the 5x2 count table against the
  pooled rate; its p-value is reported.
- Classification rule (FROZEN decision tree, applied in this ORDER):
  1. If homogeneity rejected at alpha = 0.01 -> NOT STABLE
     (dispersion-dominated; report the raw table).
  2. Else if pooled p_hat < 0.010 -> NOT STABLE (no persistent off-floor
     signal at this scale).
  3. Else if pooled p_hat in [0.010, 0.045] AND every per-seed p_hat_i in
     [0.002, 0.060] -> STABLE OFF-FLOOR.
  4. Else -> MIXED (raw per-seed table governs; no classification claim).
- Number of record (frozen): after this amendment, the C4 value of record
  is the 20000 canonical-seed estimate, comparable to C1-C3; the pooled
  five-seed result is the robustness statement reported alongside. If the
  decision tree lands on NOT STABLE or MIXED, BOTH numbers are reported
  and C4 is flagged resolution-sensitive; the verdict grid recomputation
  still uses the canonical 20000 value under the unchanged rules.
- Interpretation limits (frozen): even STABLE OFF-FLOOR does NOT make C4
  "physical"; it only states that the cell carries a stable, small
  p_GUE < 0.05 at the tested resolutions. Under the pre-declared bands,
  every branch leaves C4 below the 0.05 verdict threshold.
- Cost note (not a promise): surrogate generation scales linearly in
  ensemble count; expect multi-hour single-machine wall time.

## 5. (C) Dual-engine specification -- second independent S2 verification harness

Engine A (canonical): the sealed `gw_montgomery.py` chain; verdict-bearing.

Engine B (verification only): never verdict-bearing; a second, independent
implementation used to verify engine A's arithmetic and I/O.

- B1 -- Separate string parsing path: every numeric field of the spectra
  is read from JSON with decimal-exact parsing only: `decimal.Decimal` for
  every string field (re, re_rad, etc.); NO binary64 conversion anywhere
  (landmine L24). Fail-fast refusal if any field parses to 0.0 while its
  source string carries a nonzero significand (the fake-zero trap).
- B2 -- Independent summation loop: no vectorized/numpy accumulation; same
  mathematical definitions as sealed, but (i) compensated summation
  (Kahan/Neumaier) for every bin accumulator; (ii) a fixed iteration order
  independent of engine A's order; (iii) independently coded Gaussian
  kernel evaluation via mpmath at a fixed declared precision (dps frozen
  in the B run manifest; proposed default mpmath dps = 50).
- B3 -- Gate re-verification: B recomputes G-M0a/b/c (finite / inertia /
  strict at decimal midpoints) and G-M0d/e (trace / Frobenius) in exact
  decimal arithmetic and must reproduce PASS on all three spectra.
- B4 -- Agreement criteria (frozen): per-bin |B - A| within 1e-9 relative
  OR 10 ulp (declared tighter-of before the run); final counts k_GUE and
  k_Pois must agree EXACTLY with engine A's. Any larger discrepancy: STOP;
  record as divergence; publish nothing until resolved.
- B5 -- Output: `reports/gw_engine_b_verify.json` (per-bin comparison
  table, counts, script revisions) as a sealed artifact.
- B6 -- Scope: B verifies arithmetic and I/O of A; it cannot change any
  verdict, and it is not a new instrument.
- Implementation timing: a LATER session. This document freezes only the
  architecture, so that implementation choices cannot drift with results.

## 6. Execution order (frozen)

1. (A) 20000-ensemble refinement at dims 201/301/401, canonical seed ->
   refined 18-cell grid; the four target cells flagged.
2. (B) Five-seed array on C4 exactly as specified in section 4.
3. (C) Engine B built, then verified against the refined run (section 5).
4. Reporting: `reports/gw_diagnostic_v3.html` is NEVER mutated (it stays
   byte-stable at sha256 89C7D5F9...). Refinement results go to a NEW
   artifact (new dated report/section + the manuscript's amendment
   section); sealed numbers remain visible everywhere.
5. Session records: HANDOFF updated with a seal row carrying the exact
   counts; commit + push + CI green as usual.

## 7. Anti-tuning rails

- No cell may be dropped, averaged, re-weighted or re-ordered after
  results are seen.
- Every produced number is reported (including the full refined grid and
  the full per-seed table); classification follows ONLY the frozen rules.
- Any deviation from this specification during execution MUST be recorded
  as a dated deviation note in the output report (style: the defect
  register), never silently patched.
- No global precision state may be mutated by any step; per-run local
  precision only, with the no-leakage bounds verified by the existing
  suite.

## 8. Freeze and integrity

- FROZEN at first commit: identified by the git commit that first carries
  this file; the file's sha256 is recorded in `reports/HANDOFF.md`
  section 1.
- Editing after execution #1 starts is FORBIDDEN; revisions require a new
  dated amendment document.
- As of freeze: no measurement described here has been executed.


