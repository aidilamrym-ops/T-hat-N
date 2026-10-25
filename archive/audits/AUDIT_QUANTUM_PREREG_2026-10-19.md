# Campaign V2 — quantum entropy kernel: PRE-REGISTRATION (FROZEN)

## Replay Record RR-2026-02 — pre-registration (frozen)

- Frozen: 2026-10-19 (this file + the frozen package/tooling/spec are committed
  together BEFORE the first campaign command; git history is the ordering
  proof). Planned record: **RR-2026-02**; planned registry entry
  **A-2026-0005** (post-execution, owner-gated).
- Companion spec: `reports/REPLAY_CERT_SPEC_V0.2_QUANTUM.md` (frozen, same
  commit). Frozen code: `msaf/quantum_entropy/` package, CI guard
  `msaf/tests/test_quantum_entropy.py`, freeze tool `audit_quantum/freeze.py`;
  `audit_quantum/PINS.sha256` + `FREEZE_MANIFEST_V2.json` carry the pins and
  the Codebase/Manifest Digest.
- This campaign makes **no physical-quantum claim** and no claim about the
  Riemann zeta zeros (K-Q7). The entropy stream is a **SIMULATED** surrogate
  (D1). The model operator is a finite tridiagonal model instance, explicitly
  not a zeta claim.

## 1. Workflow (D6): two-GO discipline

- **GO-1 (this freeze):** assemble and freeze the spec, this preregistration,
  the package, the CI guard, the freeze tooling, the genesis ledger line;
  selftest must reach ZERO FAILURE at freeze time; commit + push + public CI
  green; print the Codebase/Manifest Digest (= sha256 of PINS.sha256 raw
  bytes) to the console and report it.
- **GO-2 (execution, owner-gated):** run the frozen campaign
  (`python -m msaf.quantum_entropy.runner`) over dims 201/301/401 with the
  frozen parameters; append the run to the ledger; produce the dashboard and
  stats files; report the outcome. **No campaign command runs before the
  freeze commit is pushed and CI is green.**

## 2. Objectives and the claim under test

Null-model diagnostic: replace the deterministic PRNG paths *inside the V2
sub-kernel only* with a non-deterministic (SIMULATED) entropy stream and test,
at four spectral coordinates per dim, whether:

1. the model-instance eigenvalues λ_k can be certified by two independent
   interval engines to a definite bracket and endpoint count certificate
   (deterministic layer), and
2. the surrogate statistic z built from the entropy stream passes the frozen
   χ² window over 16 quantile bins (statistical layer, float64 by design).

The two layers never mix (D3). The campaign outcome is a fact about this
finite pipeline instance, not about quantum mechanics or zeta zeros.

## 3. Frozen parameters (single source of truth: the frozen code)

| Item | Value |
|---|---|
| dims | 201, 301, 401 |
| coordinates per dim | K(D) = {D//4, D//2, 3D//4, D} |
| model diagonal | a_i = 2 + (i+1)²·h⁴, h = 1/(D+1); off-diagonal −1 (exact rationals) |
| bisection range | [0, 41/10]; 150 exact-rational steps |
| bracket width bound | ≤ (41/10)/2¹⁵⁰ ≈ 2.9e-45 |
| envelope ε | 1/250 = 0.004 = NOISE_BASE 0.0005 × 4 |
| resolution floor | envelope relative width ≤ 0.02 |
| engines | A: Arb 6000 bits; B: mpf dps 50 (≈169 bits), directed rounding |
| decision variable | interval Sturm count (#positive LDL pivots of mid·I − A) |
| exact fallback | `pivot_sign_counts`; allowed rate ≤ 5% per coordinate |
| endpoint certificate | cnt(e_lo) ≤ k−1 and cnt(e_hi) ≥ k on BOTH engines |
| Newton ball half-width | 5e-10; iters 60; target 1e-25 |
| samples | 20000 per dim, batches of 500 |
| channel weights | v_i = (i+1)/D; w_i = 0.0005·(1+(i+1)/D) ≤ 0.001 |
| z statistic | z = (Σ v_i w_i x_i)/σ0, x iid N(0,1) (Box–Muller, 53-bit uniforms) |
| envelope diagnostic | samples with max|x_i| > 4 counted (`envelope_exceeded`) |
| χ² spec | 16 bins at frozen Φ⁻¹(k/16) knots; E_b = S/16 exact; floor 5; accept 0 ≤ χ² ≤ 60 |
| exceedance diagnostic | z ≥ 3.5 vs frozen P_STAR literal (no p-value decision) |
| wall cap | 30 minutes total |
| verdicts | RESOLVED / NOT_RESOLVED / UNDETERMINED; precedence U(2) > NR(1) > R(0) |

## 4. Frozen controls (K-Q series)

* **K-Q1 — no seeds.** No `--seed` argument exists anywhere; any `--seed`
  occurrence is refused loudly with exit code 2 (`--seed N` and `--seed=N`).
* **K-Q2 — Sylvester/P.D. protocol.** Interval LDL^T of the model block in both
  engines: CERTIFIED_PD / FENCE_ZERO (loud fence → UNDETERMINED, exit 2) /
  NEGATIVE_PIVOT (NOT_RESOLVED, exit 1). See the structural note in section 6.
* **K-Q3 — decision protocol.** Interval Sturm count per bisection midpoint;
  both engines definite and equal; disagreements counted (must be 0); exact
  fallback allowed ≤ 5%; exact eigenvalue hit collapses the bracket to a point.
* **K-Q4 — statistics.** Frozen knots, exact expected counts, floor rule
  (drop cells with E < 5, recorded), exact-rational χ² in [0, 60], exceedance
  count vs Z_STAR = 3.5; wall cap 30 min.
* **K-Q5 — dashboard.** Standalone single-file HTML report; self-containment
  asserted (no script/links/URLs) and SIMULATED label required.
* **K-Q6 — ledger discipline.** Append-only hash chain (`msaf-hashchain-1`);
  failed reproduction = REVERT record; the type REJECT is refused by
  construction; chain verified before and after the run.
* **K-Q7 — non-claims.** `global_claim_supported` hardcoded `False`;
  SIMULATED label in every record; no zeta/physical/complexity claims.

## 5. Landmine notes

* **L39 — interval widening.** Symmetric Minkowski widening only; widths never
  shrunk; exact-decimal rational parsing (no float path in the certified
  layer); ε = NOISE_BASE × 4 exact.
* **L40 — pixel gloss.** "1 pixel ≡ 1 t_P" is an abstract gloss only; it is
  recorded here as prose and is never a functional variable in the runtime.
  (D4.)
* **L41 — engine lock order.** Engine A locked first at 6000 bits; `_b_env()`
  resets dps inside every B call; A's precision is guarded against drift.
* **L42 — no CWD anchoring.** All paths caller-provided or ROOT-anchored
  (ROOT resolved from the module file); the ledger CLI takes an explicit path;
  nothing depends on the working directory.

## 6. Decision protocol details and the K-Q2 interpretation

**Count-based decisions (K-Q3, supersedes the pre-freeze det-sign draft).**
The bisection decision variable is cnt(λ) = #{model eigenvalues < λ},
computed as the number of strictly positive LDL pivots of λ·I − A
(Sylvester inertia; exact at a rational point). Both engines must return
definite, equal counts per midpoint. The det-sign parity rule was discarded
during freeze rehearsal because its sign flip tracks the nearest root of the
truncated leading block (even-size parity; probe 7), while the Sturm count
pins the requested index k directly. The endpoint certificate uses the same
counts at e_lo = lo − ε and e_hi = hi + ε; equality of the two counts is not
required (gaps can be smaller than 2ε); the two inequalities pin k.

**K-Q2 model-block interpretation (frozen).** The Sylvester protocol certifies
positive-definiteness of the model block itself (exact rational data, both
engines). Structural note: an entry-wise ε-box around the model block (every
entry perturbed by at most ε = 0.004) contains non-positive-definite members
already at D ≳ 80 because λ_min(A0) ≈ (π/(D+1))² < ε; therefore NO claim is
made that every ε-perturbed member is positive definite. The perturbation
statement is the Weyl envelope: a per-channel diagonal perturbation with
entries bounded by v_i·w_i·4 ≤ ε has spectral norm ≤ ε and shifts λ_k by at
most ε (covering the certified envelope).

**Newton diagnostic (frozen values).** Start ball half-width 5e-10, 60
iterations, target 1e-25. Rationale (all three constraints recorded in the
spec §3.4): clears every leading-minor eigenvalue (interlace ≥ ~3e-7 at
D=401); keeps the derivative enclosure sign-definite at every coordinate
(chaotic pivot-orbit amplification measured ~1e10 at the worst coordinate,
D=401 k=300; ≥100× margin at 5e-10); still shows quadratic contraction from
1e-9 width to below 1e-25. Both engines use the pivot-product derivative form
f' = (Π_{i<n} v_i)·(v_n' + v_n·Σ_{i<n} v_i'/v_i) (never dividing by the last
pivot); the naive side-by-side recurrence was rejected (width growth r₊ⁿ,
r₊ ≈ 1.94; straddles up to ±2.3e+148 measured).

## 7. Decision notes (D1–D7)

* **D1** SIMULATED label locked in every code line, ledger record, report and
  the HTML dashboard; no physical-quantum claim.
* **D2** entropy source: operating-system CSPRNG surrogate
  (`secrets.token_bytes`), 4096-bit blocks; no seeds; raw blocks not retained;
  per-batch digests only (batch byte counts recorded).
* **D3** statistical layer float64 (documented); certified layer
  exact-rational/ball; the layers never mix.
* **D4** "1 pixel ≡ 1 t_P" appears only as the abstract gloss above (L40);
  never as a functional variable.
* **D5** additive scope: sealed V1 paths stay byte-identical; V2 adds the new
  package, the new ledger and new reports only.
* **D6** two-GO workflow (section 1): no campaign execution before the freeze
  commit is pushed with green CI.
* **D7** repo-style CI guard kept separate: the runner is standalone;
  `msaf/tests/test_quantum_entropy.py` runs the frozen selftest inside the
  repository CI.

## 8. Pre-freeze validation evidence (recorded before this commit)

* Selftest: **14 checks, 0 failures → ZERO FAILURE**, exit code 0
  (`python -m msaf.quantum_entropy.selftest`), including the end-to-end mini
  campaign on dims 8/9/10 with a temp ledger/outdir.
* Deep-coordinate rehearsal (all 12 campaign coordinates, frozen code path;
  probe 10): 150/150 dual decisions per coordinate, 0 exact fallbacks, 0
  engine disagreements, endpoint certificates `ok`, numpy `eigvalsh`
  cross-check inside the envelope, both engines CONTRACTED to final widths
  ~1e-46..1e-51; wall-clock ≈ 1.4–3.0 s per coordinate (deterministic layer
  ≲ 30 s — far below the 30-minute cap).
* Engine-B derivative debugging chain (fixed during freeze rehearsal, on the
  record): lexicographic min/max on raw mpf tuples → numeric min/max; naive
  determinant recurrence width amplification → pivot-product form; last-pivot
  straddle at the root-containing ball → never divide by the last pivot;
  Newton start half 5e-6 and 5e-8 collided with chaotic-orbit derivative
  enclosure widths → frozen at 5e-10.

## 9. Expected artifacts and record counts of GO-2

* Ledger `ledger/quantum_evolution.jsonl` (append-only; genesis from GO-1):
  expected new records = 40 BLOCK × 3 dims + 3 STATS + 3 dim VERDICT +
  1 campaign VERDICT = **127** (final chain 128 records), assuming a complete
  run with no REVERT.
* Stats files: `audit_quantum/exec_<date>/stats_d{201,301,401}.bin` (float64)
  with sha256 recorded in the STATS records.
* Dashboard: `reports/gw_quantum_diagnostic_v1.html` (standalone).
* Campaign outcome: RESOLVED / NOT_RESOLVED / UNDETERMINED with campaign
  precedence UNDETERMINED (exit 2) > NOT_RESOLVED (exit 1) > RESOLVED (0).

## 10. Reproduction (GO-2)

    python -m msaf.quantum_entropy.selftest
    python audit_quantum/freeze.py --verify
    python -m msaf.quantum_entropy.ledger --verify ledger/quantum_evolution.jsonl
    python -m msaf.quantum_entropy.runner          # dims 201,301,401; 20000 samples; batch 500

## 11. Non-claims

No physical-quantum-entropy claim; no Riemann-zeta statement; no arithmetic
Weil-form statement; no complexity-theoretic statement. The model matrix is a
finite model instance; the entropy stream is a SIMULATED surrogate; the
statistical layer is a diagnostic. Only the machine-checked statements in the
spec (§2–3) and the artifact hashes are claimed.
