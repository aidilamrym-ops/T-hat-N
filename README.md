# T-hat-N: Matrix-constraint Spectral Analysis Framework (MSAF)

A rigid computational kernel for finite-lattice spectral analysis, built by
**Muhammad Aidil Amry** (ORCID 0009-0002-9718-9710).
Every number reported in this repository is an interval enclosure computed
with [python-flint](https://github.com/fredrik-johansson/python-flint) ball
arithmetic (`arb` / `acb` / `arb_mat`, version 0.9.0). No floating-point value
ever touches the numeric path, and no zero claim is ever certified by
equality: only by containment.

---

## SECTION 1: EPISTEMOLOGICAL FOUNDATION & COGNITIVE LOGIC

### 1.1 The Actual Infinity Paradox on $[0 \to 0.5 \to 1]$

Classical analysis founded on ZFC postulates the continuum: between any two
distinct points lies an actual infinity of further points. Applied to the
unit interval, the innocent-looking equidistant partition

$$\Delta_1 = 0.5 - 0 = 0.5, \qquad \Delta_2 = 1 - 0.5 = 0.5$$

conceals an illegitimate object. Under Zeno's argument, traversing the segment
$[0, 0.5]$ requires completing an actually infinite sequence of informational
stages $(X_0, X_1, \dots \to \infty)$. If the number of stages is actually
infinite, the first step can never logically begin, and the exact coordinates
$0.5$ and $1$ can never be reached, confirmed, or computed by any causal
information system. The continuum is therefore not a neutral background: it
is a paradox smuggled into the foundations wherever a computation must
terminate.

### 1.2 The Universe-Information Quantisation Cut

MSAF removes the paradox by binding the computational domain to the two
absolute physical cut-offs of observable reality. The macro cut-off is the
diameter of the observable universe, mapped onto the unit interval:

$$D_{\mathrm{obs}} \approx 8.8 \times 10^{26}\ \mathrm{m}, \qquad
\text{coordinate } 0.5 \equiv \tfrac{1}{2} D_{\mathrm{obs}}.$$

The micro cut-off is the Planck length, below which localisation of
information collapses:

$$\ell_P = \sqrt{\hbar G / c^3} \approx 1.616255 \times 10^{-35}\ \mathrm{m}.$$

Their ratio is the total number of addressable information pixels, and it is
finite:

$$N_{\mathrm{steps}} = \frac{D_{\mathrm{obs}}}{\ell_P}
  \approx 5.44468544329815837306650 \times 10^{61}\ \text{steps}.$$

The continuum is thereby cut into a **Finite Information Lattice**. Every
staircase object of the theory, e.g. the discrete Chebyshev function
$\psi_d(k) = \sum_{j \le k} \Lambda_d(j)$ with the quantised von Mangoldt
weight $\Lambda_d(k) = \ln p$ iff the pixel index $k$ is a prime power
$p^m$ (and $0$ otherwise), executes as discrete modular arithmetic over pixel
addresses $k \in \{1, \dots, N_{\mathrm{steps}}\}$. There is no actual
infinity left to traverse, so Zeno's objection dissolves: every coordinate is
a finite integer address.

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
the cut-off line is executed, and everything below it is an enclosure.

---

## SECTION 2: THE SPECTRUM MECHANICS & CRITICAL LINE LOCK

### 2.1 Perfect Commutation $[\hat{H}, \hat{T}] = 0$

On a finite-dimensional space $\mathbb{C}^N$, the Planck time-shift operator
acts as the unitary cyclic shift matrix ($T e_j = e_{(j+1)\bmod N}$,
$T^\dagger T = \mathbb{I}$, $T^N = \mathbb{I}$). The spectral Hamiltonian
$\hat{H}$ carries the zeta-root frequencies as its eigenvalues and is
required to satisfy the perfect commutation constraint

$$[\hat{H}, \hat{T}] = \hat{H}\hat{T} - \hat{T}\hat{H} = 0.$$

Because every circulant Hamiltonian factors as $H = \sum_j c_j T^j$ over
powers of a single generator, and $T^a T^b = T^{a+b}$, the commutator vanishes
as an algebraic identity for any generator symbol $c$ and any dimension $N$.
Both operators therefore share one eigenbasis, delivered by the Discrete
Fourier Transform: the eigenvalues of $T$ lock onto the $N$-th roots of unity
$e^{i2\pi m/N}$, and the spectrum $\gamma_m = f(e^{i2\pi m/N})$ is quantised
by that geometry. Under the unitary projection, the functional symmetry
$\xi(s) = \xi(1-s)$ becomes the Hermitian rigidity $\hat{H}^\dagger =
\hat{H}$, and invariance of the spectral Shannon entropy under causal
reversal forces the real coordinate of every eigenvalue to the fixed point of
$\sigma_m = 1 - \sigma_m$:

$$\sigma_m = 0.5.$$

### 2.2 Verification Status (audited, not asserted)

Two audit findings qualify the mechanism above, and both are enforced in
code rather than in prose:

* The commutation identity holds for **every** circulant $H$, so a bare PASS
  would be evidence of nothing. `verify_commutation` performs a structural
  circulant test and downgrades such verdicts to
  `TRIVIAL ... carries no information` (landmine L11).
* A Hermitian circulant matrix has real eigenvalues; the only forced
  structure is conjugate pairing $\gamma_{N-m} = \overline{\gamma_m}$.
  The coordinate $\sigma = 0.5$ is therefore carried in this repository as an
  explicit **postulate** (`ZETA_SIGMA`), while the ordinates $\gamma_m$ are
  genuinely measured by interval Newton contraction (landmine L12).

### 2.3 Rigid 256-bit Measurement Table

All values below are Arb/Acb enclosures at 256-bit working precision
(`python-flint` 0.9.0, `ctx.prec = 256`).

| # | Quantity | Measured enclosure |
|---|---|---|
| 1 | $N_{\mathrm{steps}} = D_{\mathrm{obs}} / \ell_P$ | `5.44468544329815837306650e+61`, non-integer |
| 2 | `floor(N_steps)` (modulus of $T^N = I$) | `54446853992717733278474003174004102075476951347404957757284586` |
| 3 | $\log_2(N_{\mathrm{steps}})$ | 206 bit; storage lower bound `6805856749089716659809250396750512759434618918425619719660574` byte |
| 4 | $[H,T]$ residual, $n = 16$ | contains zero (PASS-BY-ENCLOSURE), max half-width `2.35950e-77` |
| 5 | $T^\dagger T - I$, $T^n - I$ | exact zero at every entry (rational 0/1, no rounding) |
| 6 | Weil minimum $\|\lambda_{\min}\|$, $n = 16$ | `1.00000000000000000000000000000000` (no exponential decay) |
| 7 | Spectral entropy $H(n=16)$ | `2.95344529780425926466202918672` bit |
| 8 | $\mathrm{Re}(\rho_1)$ enclosure radius | `3.77221946277e-71`, offset ball contains 0.5 |
| 9 | $\mathrm{Re}(\rho_2)$ enclosure radius | `8.68430320525e-78`, offset ball contains 0.5 |
| 10 | $\mathrm{Re}(\rho_3)$ enclosure radius | `1.16898354764e-71`, offset ball contains 0.5 |
| 11 | $n_{\mathrm{crit}}$, manuscript path ($H := n$) | `1.8e31` |
| 12 | $n_{\mathrm{crit}}$, measured path ($H := 0.5 + 0.5\log_2(2(n-1))$) | `3.16e60` |
| 13 | $\chi_{4,3}$ first Hardy bracket | $(6.0,\ 6.1)$, endpoints strictly $+1$/$-1$ |
| 14 | Pixel projection $\rho_{1,2,3}$ | `461`, `686`, `816` (exact integers mod $N_{\mathrm{steps}}$) |

Rows 11-12 differ by 29 orders of magnitude because of the entropy
assumption, not because of arithmetic: the manuscript arithmetic reproduces
exactly, its premise $H \equiv n$ does not survive measurement.

---

## SECTION 3: STEP-BY-STEP REPRODUCIBILITY MANUAL (HOW TO RUN AUDIT)

### 3.1 Prerequisites

```bash
python --version          # 3.14+ required
pip install "python-flint==0.9.0" matplotlib pytest
```

`python-flint` provides the Arb/Acb ball arithmetic; `matplotlib` renders
only already-certified integers (no float produced by any computation ever
reaches the plotter); `pytest` runs the regression suite.

### 3.2 Regression Suite (67 -> 71 tests, every landmine pinned)

```bash
python -m pytest msaf -q
# Asserts the precision kernel, the lattice operators, the von Mangoldt map,
# the commutation certificates, the Newton inversion, both evolution lineages,
# the Dirichlet bracketing, and every landmine L1-L37.
```

A pytest-free runner with identical coverage is included:

```bash
python -m msaf.tests.test_msaf
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
`--visualize` localises $N$ zeros and writes the pixel report;
`--final-audit` replays every ledger and checks capacity;
`--dirichlet` enumerates primitive characters and brackets $\chi_{4,3}$.

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

### 3.6 Reading `ledger/` - the Evidence Books

Each `.jsonl` line is one immutable record: `index`, `generation`,
`genome_id`, `decision` (`SEED` / `PROMOTE` / `REJECT` / `REVERT`),
serialised-ball fields as decimal strings, `previous_hash`, and `record_hash`
(SHA-256 over the canonical body). `REVERT` is a safety event (no
certificate), distinct from `REJECT` (a fitness comparison). Verify with the
replay commands of Sec.3.4; trust nothing from runtime memory.

---

## SECTION 4: RECENT AUDIT KERNEL AMENDMENTS (LANDMINES L31-L35)

Found by adversarial self-audit: every module re-read under the assumption
that the green suite is lying, then measured. Full text in
[`msaf/AUDIT.md`](msaf/AUDIT.md), Parts IV-V.

**L31 - Frozen $\log_2 e$ constant.** A module-level `LOG2_E` was evaluated
once at import under the 53-bit default (`[1.442695040888963 +/- 8.70e-16]`)
while the kernel ran at 256 bit, so every budget width was secretly a 53-bit
radius. Replaced by a `log2_e()` function evaluated at the active precision
on every call; a function cannot freeze.

**L32 - Double-counted differentiation factor.** The derivative tail summed
$(k+1)\lvert d_k\rvert r^k$ over already-differentiated coefficients. Still a
valid (looser) bound, but contradicting the documented identity. Now exactly
$\sum \lvert d_k\rvert r^k$, pinned by a test evaluating the series at exact
sample points inside the ball.

**L33 - One-sided widening let genuine derivatives escape (UNSOUND).**
The enclosure `union(enc, enc + 2*tail)` widens only upward when the tail is
one-sided positive, while the true correction $d_1 h$ points either way
(measured $-8.01\times 10^{-16}$ in the real part at $h = +r/2$, below the
lower edge). Certificates reported success regardless; results survived only
because Newton division is dominated by the imaginary component - luck, not
rigor. Replaced by symmetric Minkowski widening `enclosure + ([-t, +t])`,
which cannot miss either side. Verdicts and seal unchanged after the fix.

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

## Proven vs Postulated (standing disclosure)

Proven by execution: the grid arithmetic, the operator certificates, the
Weil spectrum in closed form, three localised zeros with certified
enclosures, the Dirichlet brackets, the hash chains and their independent
replay. Postulated, not derived: $\sigma = 0.5$ as a universal statement
(every result carries `global_claim_supported = False`); the decay law
$\lambda_{\min} \sim A e^{-Bn}$ with $\mathcal{B} \approx 0.115$ (both
entropy paths reported side by side).

Session memory and Terminus log: [`brain.md`](brain.md).
Landmine register L1-L37: [`msaf/AUDIT.md`](msaf/AUDIT.md).

## License

MIT - see [LICENSE](LICENSE).
