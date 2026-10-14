[i] OPERATIONAL STATUS (live; historical snapshots removed):
- lean/NavierStokesCore.lean: machine-checked kernel 1D/2D/3D/cubic +
  central variant (`lake build` green, 0 sorry/admit/unsafe).
- T-hat-N: 39 passed, 1 honest skip, exit 0. Main: 143 passed, exit 0.
- Source of truth for code: the files themselves, not this register.
  (A stale verbatim copy of an early 163-line Lean draft lived here;
  removed: it described architecture the machine-checked kernel
  superseded.)

[!] SENSOR TOKEN INTEGRITY SCAN:
- File: lean/NavierStokesCore.lean (2091+ lines at last audit)
- Forbidden keywords (sorry/admit/unsafe): 0 hits.
- `#print axioms` on all energy theorems: propext, Classical.choice,
  Quot.sound only.
- Status: CLEAN (machine-verified, not prose-verified).

[ R ] RESIDUAL REGISTER UPDATE:
| ID | status |
|---|---|
| R-NS-FULL | CLOSED |
| R-NS-REST | CLOSED |
| F17-NS6 | CLOSED |
| Enclosure reconditioning | CLOSED (ramp + guard demo validated) |
| BAB 3.0 (benchmarks, uniform-field UndeterminedBlock) | CLOSED |
| BAB 3.1 (radius inflation 42×, ramp data) | CLOSED |
| BAB 3.2 (MATERIALISATION_CAP = 1_000_000, N=128 guard) | CLOSED |
| VIS renderer (msaf/navier_stokes/visualizer.py, 86 lines, 3000x2400) | CLOSED |
| VIS-3D renderer (generate_fluid_state_3d_render, 139 lines, N^3 quiver) | CLOSED |
| CONV-ORDER 3-grid N=4/8/16: 2.14 -> 2.03 (theory 2.0), radii < 1e-70 | CLOSED |
| NU-LIMIT D(nu) linear 10.0000x/decade 1e-1..1e-4, nu=0 refused | CLOSED |
| TAILS quotient 1.9519 (theory 2.0), far-field 0.61%, radii < 1e-70 | CLOSED |
| FRONTIER milenium_frontier/ (RH scaffold + Hodge scaffold, lazy zeta) | CLOSED |
| FRONTIER-DEPTH z3 sat first zero; T-hat-N honest skip | CLOSED |
| LEAN-MOORE-MVT Lipschitz from deriv bound, subtype theorem | CLOSED |
| LEAN-BROUWER fixed point on Icc via IVT + Moore-image vocabulary | CLOSED |
| HODGE-GRAM exact Sylvester (pos/neg/undet), pivoted det | CLOSED |
| F17-LN1 Lean kernel 1D+2D+3D (lake build GREEN, axioms: propext/choice/Quot only) | CLOSED |
| LEAN-CENTRAL wide-Laplacian estimate + machine-checked no-go | CLOSED |
| LEAN-CUBIC N^3 direct instance (1-step + horizon) | CLOSED |
| LEAN-MOORE interval-Newton existence (Banach, standard axioms) | CLOSED |
| BAB 4.0-4.2 (Lean estimates, no-go, correspondence limits) | CLOSED |
| LONG-RUN 20 steps clean at 384-bit, 42x/step locked, ~25-step horizon | CLOSED |
| N128-CAP refusal instant via MatrixDimensionViolation | CLOSED |
| CORR-SBP central SBP enclosure N=4/N=8, radii < 1e-70 | CLOSED |
| CI GitHub Actions green (pytest 143 + lake build + sensor) | CLOSED |
| RH-EXCL exclusion sweep msaf/riemann/ (absent/inconclusive honest) | CLOSED |
| RH-COUNT certified count 2 on [10,24.5], strict-existence only | CLOSED |
| RH-COUNT-10 exactly ten zeros on [0,50] (COMPLETE, 0 stuck) | CLOSED |
| MOORE-PREM all 3 Banach premises hold on halo-lifted gamma1 box | CLOSED |
| VERDICT-GAP floor-branch never counts (pinned, no-zero-ball demo) | CLOSED |
| ALL NAVIER-STOKES RESIDUALS | CLOSED (frontier: scaffolding only, no proofs) |

Suites at seal: isolated `39 passed, 1 skipped`; main `156 passed`; `exit 0`.
