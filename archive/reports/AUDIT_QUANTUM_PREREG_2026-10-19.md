# Campaign V2 â€” quantum entropy kernel: PRE-REGISTRATION (FROZEN)

## Replay Record RR-2026-02 â€” pre-registration (frozen)

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

1. the model-instance eigenvalues Î»_k can be certified by two independent
   interval engines to a definite bracket and endpoint count certificate
   (deterministic layer), and
2. the surrogate statistic z built from the entropy stream passes the frozen
   Ï‡Â² window over 16 quantile bins (statistical layer, float64 by design).

The two layers never mix (D3). The campaign outcome is a fact about this
finite pipeline instance, not about quantum mechanics or zeta zeros.

## 3. Frozen parameters (single source of truth: the frozen code)

| Item | Value |
|---|---|
| dims | 201, 301, 401 |
| coordinates per dim | K(D) = {D//4, D//2, 3D//4, D} |
| model diagonal | a_i = 2 + (i+1)Â²Â·hâ´, h = 1/(D+1); off-diagonal âˆ’1 (exact rationals) |
| bisection range | [0, 41/10]; 150 exact-rational steps |
| bracket width bound | â‰¤ (41/10)/2Â¹âµâ° â‰ˆ 2.9e-45 |
| envelope Îµ | 1/250 = 0.004 = NOISE_BASE 0.0005 Ã— 4 |
| resolution floor | envelope relative width â‰¤ 0.02 |
| engines | A: Arb 6000 bits; B: mpf dps 50 (â‰ˆ169 bits), directed rounding |
| decision variable | interval Sturm count (#positive LDL pivots of midÂ·I âˆ’ A) |
| exact fallback | `pivot_sign_counts`; allowed rate â‰¤ 5% per coordinate |
| endpoint certificate | cnt(e_lo) â‰¤ kâˆ’1 and cnt(e_hi) â‰¥ k on BOTH engines |
| Newton ball half-width | 5e-10; iters 60; target 1e-25 |
| samples | 20000 per dim, batches of 500 |
| channel weights | v_i = (i+1)/D; w_i = 0.0005Â·(1+(i+1)/D) â‰¤ 0.001 |
| z statistic | z = (Î£ v_i w_i x_i)/Ïƒ0, x iid N(0,1) (Boxâ€“Muller, 53-bit uniforms) |
| envelope diagnostic | samples with max|x_i| > 4 counted (`envelope_exceeded`) |
| Ï‡Â² spec | 16 bins at frozen Î¦â»Â¹(k/16) knots; E_b = S/16 exact; floor 5; accept 0 â‰¤ Ï‡Â² â‰¤ 60 |
| exceedance diagnostic | z â‰¥ 3.5 vs frozen P_STAR literal (no p-value decision) |
| wall cap | 30 minutes total |
| verdicts | RESOLVED / NOT_RESOLVED / UNDETERMINED; precedence U(2) > NR(1) > R(0) |

## 4. Frozen controls (K-Q series)

* **K-Q1 â€” no seeds.** No `--seed` argument exists anywhere; any `--seed`
  occurrence is refused loudly with exit code 2 (`--seed N` and `--seed=N`).
* **K-Q2 â€” Sylvester/P.D. protocol.** Interval LDL^T of the model block in both
  engines: CERTIFIED_PD / FENCE_ZERO (loud fence â†’ UNDETERMINED, exit 2) /
  NEGATIVE_PIVOT (NOT_RESOLVED, exit 1). See the structural note in section 6.
* **K-Q3 â€” decision protocol.** Interval Sturm count per bisection midpoint;
  both engines definite and equal; disagreements counted (must be 0); exact
  fallback allowed â‰¤ 5%; exact eigenvalue hit collapses the bracket to a point.
* **K-Q4 â€” statistics.** Frozen knots, exact expected counts, floor rule
  (drop cells with E < 5, recorded), exact-rational Ï‡Â² in [0, 60], exceedance
  count vs Z_STAR = 3.5; wall cap 30 min.
* **K-Q5 â€” dashboard.** Standalone single-file HTML report; self-containment
  asserted (no script/links/URLs) and SIMULATED label required.
* **K-Q6 â€” ledger discipline.** Append-only hash chain (`msaf-hashchain-1`);
  failed reproduction = REVERT record; the type REJECT is refused by
  construction; chain verified before and after the run.
* **K-Q7 â€” non-claims.** `global_claim_supported` hardcoded `False`;
  SIMULATED label in every record; no zeta/physical/complexity claims.

## 5. Landmine notes

* **L39 â€” interval widening.** Symmetric Minkowski widening only; widths never
  shrunk; exact-decimal rational parsing (no float path in the certified
  layer); Îµ = NOISE_BASE Ã— 4 exact.
* **L40 â€” pixel gloss.** "1 pixel â‰¡ 1 t_P" is an abstract gloss only; it is
  recorded here as prose and is never a functional variable in the runtime.
  (D4.)
* **L41 â€” engine lock order.** Engine A locked first at 6000 bits; `_b_env()`
  resets dps inside every B call; A's precision is guarded against drift.
* **L42 â€” no CWD anchoring.** All paths caller-provided or ROOT-anchored
  (ROOT resolved from the module file); the ledger CLI takes an explicit path;
  nothing depends on the working directory.

## 6. Decision protocol details and the K-Q2 interpretation

**Count-based decisions (K-Q3, supersedes the pre-freeze det-sign draft).**
The bisection decision variable is cnt(Î») = #{model eigenvalues < Î»},
computed as the number of strictly positive LDL pivots of Î»Â·I âˆ’ A
(Sylvester inertia; exact at a rational point). Both engines must return
definite, equal counts per midpoint. The det-sign parity rule was discarded
during freeze rehearsal because its sign flip tracks the nearest root of the
truncated leading block (even-size parity; probe 7), while the Sturm count
pins the requested index k directly. The endpoint certificate uses the same
counts at e_lo = lo âˆ’ Îµ and e_hi = hi + Îµ; equality of the two counts is not
required (gaps can be smaller than 2Îµ); the two inequalities pin k.

**K-Q2 model-block interpretation (frozen).** The Sylvester protocol certifies
positive-definiteness of the model block itself (exact rational data, both
engines). Structural note: an entry-wise Îµ-box around the model block (every
entry perturbed by at most Îµ = 0.004) contains non-positive-definite members
already at D â‰³ 80 because Î»_min(A0) â‰ˆ (Ï€/(D+1))Â² < Îµ; therefore NO claim is
made that every Îµ-perturbed member is positive definite. The perturbation
statement is the Weyl envelope: a per-channel diagonal perturbation with
entries bounded by v_iÂ·w_iÂ·4 â‰¤ Îµ has spectral norm â‰¤ Îµ and shifts Î»_k by at
most Îµ (covering the certified envelope).

**Newton diagnostic (frozen values).** Start ball half-width 5e-10, 60
iterations, target 1e-25. Rationale (all three constraints recorded in the
spec Â§3.4): clears every leading-minor eigenvalue (interlace â‰¥ ~3e-7 at
D=401); keeps the derivative enclosure sign-definite at every coordinate
(chaotic pivot-orbit amplification measured ~1e10 at the worst coordinate,
D=401 k=300; â‰¥100Ã— margin at 5e-10); still shows quadratic contraction from
1e-9 width to below 1e-25. Both engines use the pivot-product derivative form
f' = (Î _{i<n} v_i)Â·(v_n' + v_nÂ·Î£_{i<n} v_i'/v_i) (never dividing by the last
pivot); the naive side-by-side recurrence was rejected (width growth râ‚Šâ¿,
râ‚Š â‰ˆ 1.94; straddles up to Â±2.3e+148 measured).

## 7. Decision notes (D1â€“D7)

* **D1** SIMULATED label locked in every code line, ledger record, report and
  the HTML dashboard; no physical-quantum claim.
* **D2** entropy source: operating-system CSPRNG surrogate
  (`secrets.token_bytes`), 4096-bit blocks; no seeds; raw blocks not retained;
  per-batch digests only (batch byte counts recorded).
* **D3** statistical layer float64 (documented); certified layer
  exact-rational/ball; the layers never mix.
* **D4** "1 pixel â‰¡ 1 t_P" appears only as the abstract gloss above (L40);
  never as a functional variable.
* **D5** additive scope: sealed V1 paths stay byte-identical; V2 adds the new
  package, the new ledger and new reports only.
* **D6** two-GO workflow (section 1): no campaign execution before the freeze
  commit is pushed with green CI.
* **D7** repo-style CI guard kept separate: the runner is standalone;
  `msaf/tests/test_quantum_entropy.py` runs the frozen selftest inside the
  repository CI.

## 8. Pre-freeze validation evidence (recorded before this commit)

* Selftest: **14 checks, 0 failures â†’ ZERO FAILURE**, exit code 0
  (`python -m msaf.quantum_entropy.selftest`), including the end-to-end mini
  campaign on dims 8/9/10 with a temp ledger/outdir.
* Deep-coordinate rehearsal (all 12 campaign coordinates, frozen code path;
  probe 10): 150/150 dual decisions per coordinate, 0 exact fallbacks, 0
  engine disagreements, endpoint certificates `ok`, numpy `eigvalsh`
  cross-check inside the envelope, both engines CONTRACTED to final widths
  ~1e-46..1e-51; wall-clock â‰ˆ 1.4â€“3.0 s per coordinate (deterministic layer
  â‰² 30 s â€” far below the 30-minute cap).
* Engine-B derivative debugging chain (fixed during freeze rehearsal, on the
  record): lexicographic min/max on raw mpf tuples â†’ numeric min/max; naive
  determinant recurrence width amplification â†’ pivot-product form; last-pivot
  straddle at the root-containing ball â†’ never divide by the last pivot;
  Newton start half 5e-6 and 5e-8 collided with chaotic-orbit derivative
  enclosure widths â†’ frozen at 5e-10.

## 9. Expected artifacts and record counts of GO-2

* Ledger `ledger/quantum_evolution.jsonl` (append-only; genesis from GO-1):
  expected new records = 40 BLOCK Ã— 3 dims + 3 STATS + 3 dim VERDICT +
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
spec (Â§2â€“3) and the artifact hashes are claimed.


