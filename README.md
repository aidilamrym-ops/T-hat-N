# T-hat-N: Matrix-constraint Spectral Analysis Framework (MSAF)

A rigid computational kernel for finite-lattice spectral analysis, built by
**Muhammad Aidil Amry** (ORCID 0009-0002-9718-9710).
Every number reported in this repository is an interval enclosure computed
with [python-flint](https://github.com/fredrik-johansson/python-flint) ball
arithmetic (`arb` / `acb` / `arb_mat`, version 0.9.0). No floating-point value
ever touches the numeric path, and no zero claim is ever certified by
equality: only by containment.

- Permanent archive: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23338272.svg)](https://doi.org/10.5281/zenodo.23338272)
- Sealed release: [v1.1.0](https://github.com/aidilamrym-ops/T-hat-N/releases/tag/v1.1.0) (archive) · [v1.8.5-alpha](https://github.com/aidilamrym-ops/T-hat-N/releases/tag/v1.8.5-alpha) (current: 139 passed)
- License: MIT - see [LICENSE](LICENSE)

Display equations below are versioned local SVG assets under
[`docs/math/`](docs/math/), rendered offline by
[`harness/render_math.py`](harness/render_math.py) with no network and no TeX
installation, so the archive stays self-contained forever.

## Contents

- [Section 1: Epistemological Foundation and Cognitive Logic](#section-1-epistemological-foundation--cognitive-logic)
- [Section 2: Spectrum Mechanics and Critical Line Lock](#section-2-the-spectrum-mechanics--critical-line-lock)
- [Section 3: Step-by-Step Reproducibility Manual](#section-3-step-by-step-reproducibility-manual-how-to-run-audit)
- [Section 4: Recent Audit Kernel Amendments (Landmines L31-L35)](#section-4-recent-audit-kernel-amendments-landmines-l31-l35)
- [Section 5: Finite Hydrodynamic Lattice & Millennium Frontier](#section-5-finite-hydrodynamic-lattice--millennium-frontier)
- [Symbol Glossary](#symbol-glossary)
- [Proven vs Postulated](#proven-vs-postulated-standing-disclosure)
- [Repository Layout](#repository-layout)
- [Citation](#citation)

---

## SECTION 1: EPISTEMOLOGICAL FOUNDATION & COGNITIVE LOGIC

### 1.1 The Actual Infinity Paradox on [0, 0.5, 1]

Classical analysis founded on ZFC postulates the continuum: between any two
distinct points lies an actual infinity of further points. Applied to the
unit interval, the innocent-looking equidistant partition

<p align="center"><img src="docs/math/partition.svg" alt="Delta_1 = 0.5 - 0 = 0.5, Delta_2 = 1 - 0.5 = 0.5"></p>

conceals an illegitimate object. Under Zeno's argument, traversing the segment
[0, 0.5] requires completing an actually infinite sequence of informational
stages (X0, X1, ... -> infinity). If the number of stages is actually
infinite, the first step can never logically begin, and the exact coordinates
0.5 and 1 can never be reached, confirmed, or computed by any causal
information system. The continuum is therefore not a neutral background: it
is a paradox smuggled into the foundations wherever a computation must
terminate.

### 1.2 The Universe-Information Quantisation Cut

MSAF removes the paradox by binding the computational domain to the two
absolute physical cut-offs of observable reality. The macro cut-off is the
diameter of the observable universe, mapped onto the unit interval:
D_obs ~= 8.8e26 m, so coordinate 0.5 identically equals half that diameter.
The micro cut-off is the Planck length l_P ~= 1.616255e-35 m, below which
localisation of information collapses. Their ratio is the total number of
addressable information pixels, and it is finite:

<p align="center"><img src="docs/math/nsteps.svg" alt="N_steps = D_obs / l_P approx 5.44 x 10^61"></p>

The continuum is thereby cut into a **Finite Information Lattice**. Every
staircase object of the theory, e.g. the discrete Chebyshev function

<p align="center"><img src="docs/math/chebyshev.svg" alt="psi_d(k) = sum_{j <= k} Lambda_d(j)"></p>

with the quantised von Mangoldt weight Lambda_d(k) = ln p iff the pixel
index k is a prime power p^m (and 0 otherwise), executes as discrete modular
arithmetic over pixel addresses k = 1..N_steps. There is no actual infinity
left to traverse, so Zeno's objection dissolves: every coordinate is a finite
integer address.

### 1.3 Logic-Flow Map: Continuous Zeta Functionals to the Unitary Lattice

```text
  CONTINUOUS DOMAIN (abstraction layer, non-executable)
  ========================================================
  Riemann zeta zeta(s), s in C
        |
        | completed function  xi(s) = 1/2 s(s-1) pi^(-s/2) Gamma(s/2) zeta(s)
        v
  xi(s) = xi(1 - s)   [functional symmetry, analytic statement]
        |
        | INFORMATION CUTOFF  (D_obs above, l_P below)
        v
  FINITE LATTICE (executable layer, N_steps = 5.44e61 pixels)
  ========================================================
  pixel addresses k = 1..N_steps  -->  von Mangoldt weights Lambda_d(k)
        |
        | Planck clock: one pixel shift = one tick t_P  -->  T e_j = e_{(j+1) mod N}
        v
  UNITARY SHIFT OPERATOR  T^dag T = I,  T^N = I        [exact rational entries]
        |
        | circulant Hamiltonians H = sum_j c_j T^j share the DFT eigenbasis
        v
  COMMUTATION CONSTRAINT  [H, T] = HT - TH  -->  certified by enclosure
        |
        | interval Newton on xi(s) over Acb balls (zeros pulled, not postulated)
        v
  MEASURED SPECTRUM  gamma_m  -->  pixel projection  k_m = floor(gamma_m / 2pi
                     . log2(N_steps)) mod N_steps  -->  reports/spectral_density.json
```

The downward arrows are the entire content of the framework: nothing above
the cut-off line is executed, and everything below it is an enclosure. The
completed zeta function driving the inversion kernel is:

<p align="center"><img src="docs/math/xi.svg" alt="xi(s) = 1/2 s(s-1) pi^(-s/2) Gamma(s/2) zeta(s)"></p>

---

## SECTION 2: THE SPECTRUM MECHANICS & CRITICAL LINE LOCK

### 2.1 Perfect Commutation [H, T] = 0

On a finite-dimensional space C^N, the Planck time-shift operator acts as the
unitary cyclic shift matrix (T e_j = e_((j+1) mod N), T^dag T = I, T^N = I).
The spectral Hamiltonian H carries the zeta-root frequencies as its
eigenvalues and is required to satisfy the perfect commutation constraint

<p align="center"><img src="docs/math/commutator.svg" alt="[H,T] = HT - TH = 0"></p>

Because every circulant Hamiltonian factors as H = sum_j c_j T^j over powers
of a single generator, and T^a T^b = T^(a+b), the commutator vanishes as an
algebraic identity for any generator symbol c and any dimension N. Both
operators therefore share one eigenbasis, delivered by the Discrete Fourier
Transform: the eigenvalues of T lock onto the N-th roots of unity
e^(i 2 pi m / N), and the spectrum gamma_m = f(e^(i 2 pi m / N)) is quantised
by that geometry. Under the unitary projection, the functional symmetry
xi(s) = xi(1-s) becomes the Hermitian rigidity H^dag = H, and invariance of
the spectral Shannon entropy

<p align="center"><img src="docs/math/entropy.svg" alt="H(n) = -sum_k p_k log_2(p_k)"></p>

under causal reversal forces the real coordinate of every eigenvalue to the
fixed point of sigma_m = 1 - sigma_m:

<p align="center"><img src="docs/math/sigma.svg" alt="sigma_m = 1 - sigma_m implies sigma_m = 0.5"></p>

### 2.2 Verification Status (audited, not asserted)

Two audit findings qualify the mechanism above, and both are enforced in
code rather than in prose:

* The commutation identity holds for **every** circulant H, so a bare PASS
  would be evidence of nothing. `verify_commutation` performs a structural
  circulant test and downgrades such verdicts to
  `TRIVIAL ... carries no information` (landmine L11).
* A Hermitian circulant matrix has real eigenvalues; the only forced
  structure is conjugate pairing gamma_(N-m) = conj(gamma_m). The coordinate
  sigma = 0.5 is therefore carried in this repository as an explicit
  **postulate** (`ZETA_SIGMA`), while the ordinates gamma_m are genuinely
  measured by interval Newton contraction (landmine L12).

The assumed eigenvalue decay law under test is:

<p align="center"><img src="docs/math/lambda_min.svg" alt="lambda_min(n) ~ A e^(-B n)"></p>

and the critical-dimension equation solved on both entropy paths is:

<p align="center"><img src="docs/math/ncrit.svg" alt="B log_2(e) n^2 + n log_2(1/A) - N_steps = 0"></p>

### 2.3 Rigid 256-bit Measurement Table

All values below are Arb/Acb enclosures at 256-bit working precision
(`python-flint` 0.9.0, `ctx.prec = 256`), re-measured against the sealed
kernel with zero drift.

| # | Quantity | Measured enclosure |
|---|---|---|
| 1 | N_steps = D_obs / l_P | `5.44468544329815837306650e+61`, non-integer |
| 2 | floor(N_steps) (modulus of T^N = I) | `54446853992717733278474003174004102075476951347404957757284586` |
| 3 | log2(N_steps) | 206 bit; storage lower bound `6805856749089716659809250396750512759434618918425619719660574` byte |
| 4 | [H,T] residual, n = 16 | contains zero (PASS-BY-ENCLOSURE), max half-width `2.35950e-77` |
| 5 | T^dag T - I, T^n - I | exact zero at every entry (rational 0/1, no rounding) |
| 6 | Weil minimum |lambda_min|, n = 16 | `1.00000000000000000000000000000000` (no exponential decay) |
| 7 | Spectral entropy H(n=16) | `2.95344529780425926466202918672` bit |
| 8 | Re(rho_1) enclosure radius | `3.77221946277e-71`, offset ball contains 0.5 |
| 9 | Re(rho_2) enclosure radius | `8.68430320525e-78`, offset ball contains 0.5 |
| 10 | Re(rho_3) enclosure radius | `1.16898354764e-71`, offset ball contains 0.5 |
| 11 | n_crit, manuscript path (H := n) | `1.8e31` |
| 12 | n_crit, measured path (H := 0.5 + 0.5 log2(2(n-1))) | `3.16e60` |
| 13 | chi_4_3 first Hardy bracket | `(6.0, 6.1)`, endpoints strictly +1/-1 |
| 14 | Pixel projection rho_1,2,3 | `461`, `686`, `816` (exact integers mod N_steps) |
| 15 | Ledger replay V(L), both ledgers | True (hash chain intact, every block reproduced) |
| 16 | Final holographic seal, n in {16, 400, 800} | `SAFE-COMPUTATION` on both entropy paths |

Rows 11-12 differ by 29 orders of magnitude because of the entropy
assumption, not because of arithmetic: the manuscript arithmetic reproduces
exactly, its premise H = n does not survive measurement. The pixel map is:

<p align="center"><img src="docs/math/pixel.svg" alt="k_m = floor(gamma_m / 2pi log_2(N_steps)) mod N_steps"></p>

---

## SECTION 3: STEP-BY-STEP REPRODUCIBILITY MANUAL (HOW TO RUN AUDIT)

### 3.1 Prerequisites

```bash
python --version          # 3.14+ required
pip install "python-flint==0.9.0" matplotlib pytest
```

`python-flint` provides the Arb/Acb ball arithmetic; `matplotlib` renders
only already-certified integers (no float produced by any computation ever
reaches the plotter) and typesets the equations in `docs/math/`;
`pytest` runs the regression suite.

### 3.2 Regression Suite (139 tests, every landmine pinned)

```bash
python -m pytest msaf -q
# Asserts the precision kernel, the lattice operators, the von Mangoldt map,
# the commutation certificates, the Newton inversion, both evolution lineages,
# the Dirichlet bracketing, and every landmine L1-L38.
```

A pytest-free runner with identical coverage is included:

```bash
python -m msaf.tests.test_msaf
python -m msaf.tests.test_dirichlet
```

### 3.3 Full Audit and Evolution Campaigns

```bash
# Complete audit: operator certificates, spectrum, budgets, lattice kernels,
# Newton inversion of rho_1..rho_3, root-pull + symbol evolution, pixel map,
# ledger replay and holographic capacity seal.
python -m msaf.audit --prec 256 --evolve 6 --root-pull 3 \
    --visualize 3 --final-audit --dirichlet 8
```

Flag annotations: `--prec` locks the global Arb precision exactly once;
`--evolve` runs symbol-mutation proposals; `--root-pull` runs proposals
pulled from certified zeta zeros (failures recorded as `REVERT`);
`--visualize` localises N zeros and writes the pixel report;
`--final-audit` replays every ledger and checks capacity;
`--dirichlet` enumerates primitive characters and brackets chi_4_3.

### 3.4 Independent SHA-256 Ledger Replay

```bash
python -m msaf.evolution --replay ledger/msaf_ledger.jsonl --dimension 16
python -m msaf.evolution --replay ledger/rootpull.jsonl --dimension 16 --prec 256
# Exit 0 with V(L) = True means: hash chain intact AND every block reproduced
# from scratch. Any other outcome exits 1. The replay precision (--prec) and
# the Newton budget (--dimension for root-pull lines) MUST equal the campaign
# values; a mismatch of a single bit fails loudly (landmine L29).
```

### 3.5 Reading `reports/` - the 206-bit Pixel Report

`reports/spectral_density.json` carries the full 206-bit pixel addresses as
**decimal strings** (never JSON numbers: a binary64 round-trip could collapse
a small radius onto exactly `0.0` and fabricate a zero):

```json
{
  "dimension": 16,
  "modulus": "54446853...57784586",
  "pixels": ["461", "686", "816"],
  "gammas": ["14.1347251417346937904572519836", "..."],
  "gamma_radii": ["...", "...", "..."],
  "verdicts": ["ZERO-LOCALIZED", "ZERO-LOCALIZED", "ZERO-LOCALIZED"],
  "locked": 3, "total": 3
}
```

`gammas` are enclosure midpoints; `gamma_radii` are the certified radii that
qualify them. `reports/spectral_density.png` renders the same integer data
with the axis explicitly labelled `mod 2^32` for plottability.
`reports/GRH_BRACKET_REPORT.json` is the Dirichlet counterpart: the
multi-resolution sign-change dossier for chi_4_3 over (6.0, 6.1), with
per-level endpoints, Hardy values, radii, measured signs and the odd-count
claim boundary.

### 3.6 Reading `ledger/` - the Evidence Books

Each `.jsonl` line is one immutable record: `index`, `generation`,
`genome_id`, `decision` (`SEED` / `PROMOTE` / `REJECT` / `REVERT`),
serialised-ball fields as decimal strings, `previous_hash`, and `record_hash`
(SHA-256 over the canonical body). `REVERT` is a safety event (no
certificate), distinct from `REJECT` (a fitness comparison). Verify with the
replay commands of Section 3.4; trust nothing from runtime memory.

---

## SECTION 4: RECENT AUDIT KERNEL AMENDMENTS (LANDMINES L31-L35)

Found by adversarial self-audit: every module re-read under the assumption
that the green suite is lying, then measured. L36-L38 extend the register to
the Dirichlet kernel. Full text in [`msaf/AUDIT.md`](msaf/AUDIT.md), Parts
IV-VI.

**L31 - Frozen log2(e) constant.** A module-level `LOG2_E` was evaluated
once at import under the 53-bit default, while the kernel ran at 256 bit, so
every budget width was secretly a 53-bit radius. Replaced by a `log2_e()`
function evaluated at the active precision on every call; a function cannot
freeze.

**L32 - Double-counted differentiation factor.** The derivative tail summed
(k+1)|d_k|r^k over already-differentiated coefficients. Still a valid
(looser) bound, but contradicting the documented identity. Now exactly the
differentiated-coefficient sum, pinned by a test evaluating the series at
exact sample points inside the ball.

**L33 - One-sided widening let genuine derivatives escape (UNSOUND).**
The enclosure `union(enc, enc + 2*tail)` widens only upward when the tail is
one-sided positive, while the true correction points either way. Certificates
reported success regardless; results survived only because Newton division is
dominated by the imaginary component - luck, not rigor. Replaced by symmetric
Minkowski widening, which cannot miss either side. Verdicts and seal
unchanged after the fix.

**L34 - Root-pull outcome promised `Fitness`, delivered `None`.** A typed lie
under a `type: ignore` comment, one caller away from detonation. Replaced by a
dedicated `RootPullOutcome` carrying the real fitness; the `dimension`
parameter (always a Newton iteration cap, never a matrix dimension) renamed
to `newton_max_iter` with positional compatibility preserved, so existing
ledgers replay byte-identical.

**L35 - CWD-relative artifact paths.** Ledgers could silently scatter across
the filesystem when invoked from another directory. All artifact paths are
now anchored to the workspace root derived from the module location.

---

## SECTION 5: FINITE HYDRODYNAMIC LATTICE & MILLENNIUM FRONTIER

Sealed through `v1.8.5-alpha` (main `139 passed`, isolated `35 passed +
1 honest skip`, exit 0). Full derivations in
[`reports/finite_hydrodynamic_lattices.md`](reports/finite_hydrodynamic_lattices.md)
(Chapters 1-3) and the machine-checked Lean kernel in [`lean/NavierStokesCore.lean`](lean/NavierStokesCore.lean)
(`lake build` green: 1D channel + 2D periodic + 3D energy estimates,
0 `sorry` / `admit` / `unsafe`, `#print axioms`:
propext + Classical.choice + Quot.sound only).

### 5.1 Fractional-step Navier-Stokes loop (`msaf/navier_stokes/`)

- Sequential Godunov splitting (advect-then-diffuse) with Planck-tick
  time accounting; kinetic energy contracts strictly every step.
- Chorin restoring projection (`dP = (rho/dt) div u*`): divergence
  balls contain exact zero after every step, including rotation fields
  with non-zero `tr(G^2)`.
- Adaptive precision ramp: +128-bit jumps past the 1e-72 wire, 1024-bit
  hard cap via `ResolutionAlarm` (256-bit run trips cleanly at step 3;
  384-bit run holds 10 steps at 1e-100 radii).
- Hermetic 2D + 3D renderers (`visualizer.py`, 3000x2400 px,
  display-only floats, lattice never mutated).

### 5.2 Measured metrology (256-bit unless noted)

| Quantity | Measured |
|---|---|
| Multi-grid pivots N = 16 / 32 / 64 (262,144 cells) | `CERTIFIED_POSITIVE`, half-width `1.73e-77` |
| 3-grid convergence order (N = 4/8/16) | `2.14 -> 2.03` vs theory `2.0` |
| Inviscid scaling D(nu), nu = 1e-1..1e-4 | linear `10.0000x`/decade; nu = 0 refused |
| Periodic-box tails (N = 16) | background-free quotient `1.9519` vs `2.0`; far-field `0.61%`; radii `< 1e-70` |
| Z3 double-entry, first zero | `sat`, `[0.5, 0.5]` at 30 decimals (conformance, not proof) |
| Hodge Gram, exact QQ Sylvester | `POSITIVE/NEGATIVE_DEFINITE`, `UNDETERMINED` on zero minor |

### 5.3 Frontier scaffolding (`msaf/milenium_frontier/`, proofs: none)

- `PureRiemannVerify`: interval-Newton localization + Z3 conformance
  cross-check. Containment of 0.5 is conformance, never a global claim
  (same warning as `certify_sigma_one_half`).
- `HodgeLattice`: finite rational (p,p) cycles, exact `Fraction` Gram
  pairing, pivoted Sylvester definiteness with loud `UNDETERMINED`.
- Standing scope: scaffolding only. No Millennium result is claimed.

### 5.4 What is NOT claimed

No global Navier-Stokes regularity, no refutation of any third party's
work, no Riemann or Hodge proof. See `PROVEN VS POSTULATED` above and
[`reports/OPENAI_NS_REFUTATION_PRESS_RELEASE.md`](reports/OPENAI_NS_REFUTATION_PRESS_RELEASE.md)
(scope notice binding).

---

## SYMBOL GLOSSARY

| Symbol | Meaning | Defined |
|---|---|---|
| N_steps | Total information pixels, D_obs / l_P | Sec. 1.2 |
| l_P, D_obs | Planck length; observable-universe diameter | Sec. 1.2 |
| T (T-hat) | Unitary Planck time-shift, cyclic permutation | Sec. 1.3 |
| H (H-hat) | Circulant spectral Hamiltonian | Sec. 2.1 |
| c | Circulant generator symbol, H = sum_j c_j T^j | Sec. 2.1 |
| gamma_m | m-th spectral ordinate (imaginary part) | Sec. 2.1 |
| sigma_m | Real part of m-th eigenvalue; postulated 0.5 | Sec. 2.2 |
| rho_m | m-th non-trivial zero, sigma_m + i gamma_m | Sec. 2.3 |
| k_m | Modular pixel projection of gamma_m | Sec. 2.3 |
| psi_d, Lambda_d | Discrete Chebyshev step; quantised von Mangoldt weight | Sec. 1.2 |
| xi(s) | Completed zeta function (Newton target) | Sec. 1.3 |
| lambda_min | Smallest eigenvalue magnitude under test law | Sec. 2.2 |
| H(n) | Spectral Shannon entropy in bits | Sec. 2.1 |
| V(L) | Ledger verification identity (chain + replay) | Sec. 3.4 |
| chi_q_n | Dirichlet character, modulus q, number n | Sec. 2.3 |
| Z(t) | Hardy Z-function of a real character | Sec. 2.3 |

## PROVEN VS POSTULATED (STANDING DISCLOSURE)

Proven by execution: the grid arithmetic, the operator certificates, the
Weil spectrum in closed form, three localised zeros with certified
enclosures, the Dirichlet brackets, the hash chains and their independent
replay. Postulated, not derived: sigma = 0.5 as a universal statement
(every result carries `global_claim_supported = False`); the decay law with
B ~= 0.115 (both entropy paths reported side by side).

Session memory and Terminus log: [`brain.md`](brain.md).
Landmine register L1-L38: [`msaf/AUDIT.md`](msaf/AUDIT.md).

## REPOSITORY LAYOUT

- `msaf/` - kernel: precision, constants, grid, certificates, operators,
  Guinand-Weil matrices, budget, zeta inversion, evolution, visualizer,
  Dirichlet bracketing, final audit
- `msaf/navier_stokes/` - finite hydrodynamic lattice: Godunov loop,
  restoring projection, adaptive precision, 2D/3D renderers, multi-grid check
- `msaf/milenium_frontier/` - scaffolding only: RH localization + Z3
  conformance, rational Hodge cycles (no proofs claimed)
- `msaf/tests/` - regression suite (139 tests)
- `lean/` - Lean 4 finite-lattice blueprint (`NavierStokesCore.lean`)
- `msaf_core_lattice.py` - the four mandated entry points
- `msaf/tests/` - regression suite (139 tests)
- `docs/math/` - versioned equation renderings plus [`render script`](harness/render_math.py)
- `harness/` - release gate and math renderer
- `ledger/` - append-only evidence chains; `reports/` - integer pixel reports

## CITATION

```text
Amry, Muhammad Aidil. T-hat-N: Matrix-constraint Spectral Analysis Framework.
v1.1.0. Zenodo. https://doi.org/10.5281/zenodo.23338272
```

## LICENSE

MIT - see [LICENSE](LICENSE).
