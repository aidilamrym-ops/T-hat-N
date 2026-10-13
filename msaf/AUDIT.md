# MSAF Landmine Register

Every item below is verified by execution on `python-flint 0.9.0` /
`Python 3.14.4`. Nothing here is based on reading the manuscript.

Regression suite: `python -m pytest msaf -q` (67 tests, all passing).
Full report: `python -m msaf.audit --prec 256 --evolve 6 --root-pull 3 --visualize 3 --final-audit`.
Standalone replay: `python -m msaf.evolution --replay ledger/msaf_ledger.jsonl --dimension 16`.

---

## L1. `arb(x, y)` is a RADIUS, not a digit count

    arb("1.616255", 60)   ->  [1.616255 +/- 61.7]      wrecked ball
    arb("1.616255")       ->  [1.616255 +/- 1.3e-77]  tight ball

Every constant written as `arb("x", 60)` is immediately wrong and poisons the
whole analysis. Rule: call `arb(text)` with a single argument and leave the
working precision to the global setting. See `msaf.constants.one_sigma`.

## L2. Containment direction for zero claims

FLINT defines `a.contains(b)` as "b is a subset of a".

    arb(0).contains(residual)   -> False   a point ball cannot hold a wide ball
    residual.contains(arb(0))   -> True    the only admissible form

Rule: zero claims pass only through `msaf.certify.contains_zero`, never
through `== 0` and never through a float comparison.

## L3. A circulant commutator is certified, never exactly zero

At `n = 16`, 256-bit precision, symbol `c[j] = cos(2 pi j / n) + delta_{j0}`:

    [H,T]        -> PASS-BY-ENCLOSURE, max half width ~ 2.4e-77
    T^dag T - I  -> PASS, exact zero (entries are the exact rationals 0 and 1)
    T^n - I      -> PASS, exact zero

`[H,T] = 0` can therefore never be printed as "verified identically in
float". The only admissible statement is "zero lies inside the residual at
precision p". Note also that 32 of the 64 commutator entries are *exactly*
zero and 32 are only enclosure-certified, so the two claim classes must not be
reported under one label.

## L4. `arb.log(b)` and `arb.exp(x)` accept no arguments

Both `arb(2).log(2)` and `arb(-1).exp(1)` raise `TypeError`. Base conversion
goes through `log_base` or division by `log()`. Wrapped in `msaf.precision.log2`.

## L5. `flint.arb` is not an importable submodule

The standing instruction names `flint.arb`, `flint.arb_mat` and `flint.ctx.prec`
as import targets. In python-flint 0.9.0 these are *attributes* of the `flint`
package, not submodules:

    from flint.arb import arb       -> ModuleNotFoundError: No module named 'flint.arb'
    from flint import arb, arb_mat, ctx   -> correct

The import discipline must therefore be `from flint import arb, arb_mat, ctx`,
and `ctx.prec` is the documented precision control. Any code written against
the submodule spelling fails at import time.

## L6. `N_steps` is never an integer

    8.8e26 / 1.616255e-35 = 5.44468544329815837306650e+61

and the exact rational does not divide. Modular arithmetic `T^N = 1` requires an
integer exponent, so the modulus must use `floor(N_steps)`, and the difference
must be recorded rather than rounded away silently.

`log2(N_steps) = 206` bits, so the absolute storage lower bound is `6.8e60`
bytes. Materialising `N x N` is not an optimisation problem but a structurally
impossible one, which is why `T` is stored as a permutation and `H` as a
generator symbol.

## L7. `log(Lambda_d(k) + delta_{k,1})` produces NaN

Measured at pixel `k = 6`:

    manuscript kernel log(Lambda_d + delta) -> nan
    repaired kernel  log(1 + Lambda_d)      -> 0

For every pixel index that is not a prime power, `Lambda_d(k) = 0` and the
argument of the logarithm is exactly zero. The NaN then propagates through the
whole discrete Fourier transform. The repair shipped in
`msaf_core_lattice.von_mangoldt_log_kernel` keeps the whole grid finite, and a
regression test pins both the defect and the repair.

Dimensional note: the manuscript condition `k * l_P == p^m` compares a length
with a dimensionless integer. The only computable reading is that `l_P` is the
unit of the pixel, so the test acts on the integer index itself.

## L8. Weilmatrix spectra do not decay exponentially

The Weil matrix `W[i][j] = cos(2 pi i j / n) - delta_{ij}` has first column
`[0, 1, 1, ..., 1]`, whose DFT evaluates analytically:

    lambda_0 = n - 1,     lambda_k = -1  for k = 1..n-1

Verified numerically for `n = 4, 8, 16, 32`:

    min |lambda| = 1.0000000000000000000000000000 +/- 1e-44   (n = 16)

So the assumption `lambda_min(n) ~ A exp(-B n)` does not hold for the very
matrix family used to motivate it, and the constant `B ~ 0.115` has no measured
source inside the framework. The consequence for the headline number:

    H := n            (manuscript assumption)  ->  n_crit = 1.8e31
    H := 0.5 log2(2n) (measured W_n entropy)   ->  n_crit = 3.16e60

A 29-order-of-magnitude gap that comes from the assumption, not from
arithmetic.

## L9. Underflow is a precision demand, not an existence boundary

    |lambda| = 1e-59  at  n = 1181.33
    relative precision demand at n = 800 is only 142 bits

`1e-59` lies comfortably inside the `float64` range. What occurs at `n = 1181`
is a request for more precision, not an absolute representational limit, and
ball arithmetic with an explicitly locked precision removes the event entirely.
The "holographic bit capacity of the universe" therefore does not act as a
computational boundary.

## L10. Repeated eigenvalues break default isolation

`arb_mat.eig()` without arguments raises
`ValueError: failed to isolate eigenvalues` on the Weil matrix, because `-1`
has multiplicity `n-1`. Either pass `multiple=True`, or, better, diagonalise
structurally through the DFT, which is what `msaf.guinand.weil_spectrum` does.
The evolution fitness function additionally needs `multiple=True` for its
cross-validation pass.

## L11. `[H,T] = 0` is an algebraic tautology and carries no information

`H = sum_j c_j T^j` and every power of a single operator commutes, so the
commutator vanishes identically for *any* symbol `c` and *any* dimension. The
constraint constrains nothing about zeta zeros.

`msaf_core_lattice.verify_commutation` therefore performs a non-triviality gate:
it tests circulant-ness structurally and downgrades the verdict to
`TRIVIAL ... carries no information`, with `carries_information = False`. A bare
PASS would have been a lie by omission.

Measured, at `n = 8`:

    residual contains 0  = True
    structurally trivial = True
    carries_information  = False

## L12. `sigma = 0.5` is imposed, not derived

A Hermitian circulant matrix has real eigenvalues, so the only forced structure
is conjugate pairing `gamma_{N-m} = conj(gamma_m)`. That places no constraint on
`sigma`, which is an independent coordinate. Writing `sigma = 1 - sigma`
therefore does not follow from unitarity of `T`; it is a stipulation. Likewise
the formula `gamma_m = f(exp(2 pi i m / N))` *defines* the spectrum by fiat and
is not a derivation from the zeta function. No code path in this package
certifies `sigma = 0.5`; `msaf.constants.ZETA_SIGMA` is documented as a
postulate.

## L13. `E_trunc = 0` is measurably false as stated

Measured on the actual quantity `l_P * exp(-N_steps)`:

    lower endpoint positive    = True
    relative radius            = 3.09357e-7
    binary64 on the same input = 0.0
    audit verdict              = NOT-ZERO

The Arb exponent is an arbitrary-precision integer, so the quantity survives
with a strictly positive lower endpoint. A `float64` saturates to `0.0` on the
identical input, which is precisely how a clean-looking zero appears without any
mathematics supporting it. `msaf_core_lattice.verify_truncation` refuses to
certify an imposed zero and distinguishes `IDENTICAL-ZERO`, `NOT-ZERO`,
`UNDERDETERMINED` and `NOT-ZERO (external evidence)`.

## L14. Ball comparison stalls on identical measurements

`candidate >= incumbent` returns False when two balls merely overlap, even when
they are the same measurement. A naive promotion gate would reject every mutant
and the campaign would never progress. `msaf.evolution._is_provably_worse`
requires strict separation of the enclosures instead, which is the only
comparison ball arithmetic can settle unambiguously.

## L15. `log2(0)` poisons fitness with infinities

An exactly zero commutator residual makes `log2(width)` evaluate to an
infinity, which propagates to `nan` once summed. `_certificate_bits` caps the
score at twice the working precision instead, and `Ledger.append` refuses any
non-finite measurement outright, so a failed experiment can never be
laundered into a signed historical record.

---

# Part II: landmines found in the Newton-zeta directive

The directive `instruksi_lanjutan_newton_arb.md` supplies a code blueprint.
Every item below was verified by executing that blueprint or its closest
correct spelling. The directive's mathematics is sound; several of its API
assumptions are not, and two of its conclusions would have been overclaims.

## L16. `arb(x, y)` and `acb(x, y)` mean opposite things

    arb(mid, rad)    ->  a BALL with the given radius
    acb(real, imag)  ->  a COMPLEX NUMBER with the given imaginary part

    arb(1, 60).rad()        ->  60
    acb("0.5", 1e-18)       ->  the point 0.5 + 1e-18 i, radius 0

The same positional signature, two completely different constructions. A
directive that writes `acb(2, prec=prec)` is not merely mistyped: it builds the
complex number `2 + prec i`. Every enclosure built that way is a point, so the
"interval" arithmetic degenerates silently while still looking well formed.

Enclosures must be constructed through `msaf.zeta_inversion.ball`, which unions
two displaced points and therefore always produces a genuine superset.

## L17. `acb(x).complex_rad()` returns an Acb, not an Arb

Using it as a real exponent silently promotes every subsequent accumulator
into the complex domain. In the derivative tail bound it produced a "tail" of
`16.22 +/- 4.89e-3` instead of a negligible quantity, which made the Newton
division meaningless and the iteration appear to diverge while the underlying
mathematics was perfectly well behaved.

## L18. `s.real` is the real VALUE of the ball, not its radius

The worst of the three, and the one that cost the most debugging time. In the
Taylor tail bound, `_component_radius_upper` was written as
`max(s.real.abs_upper(), s.imag.abs_upper())`, which returns approximately 0.5,
the real part of the point, rather than the radius. The tail was then computed
with r ~ 0.5 instead of r ~ 1e-55.

Measured effect: derivative enclosure radius 3.2e-21 at ball radius 1e-18, and
the next Newton image escaped. After the fix the enclosure tightens with the
ball and the contraction is clean. The rule is `s.real.rad().abs_upper()`.

## L19. Acb is RECTANGULAR, so componentwise containment gives false negatives

A ball built as `(c + r) union (c - r)` has a circular radius of r while its
imaginary component stays exact to a hundred digits. A componentwise inclusion
test therefore rejects a ball that is plainly contained, which would abort
every Newton contraction.

The circular criterion is used instead:

    inner subset of outer   <=>   |mid_in - mid_out| + rad_in < rad_out

evaluated with exact endpoints on both sides.

## L20. `arb < arb` is False for overlapping balls

Already recorded as L14, but it recurs inside the inversion kernel, where an
inclusion test built from direct endpoint comparison produced an answer that
depended on the rounding representation rather than on the mathematics. Every
comparison in the kernel is now between exact quantities with a strict
inequality.

## L21. Returning `0` at `s = 0` and `s = 1` fabricates roots

The blueprint guards the removable singularities of the zeta factor with

    if s.is_zero() or (s - acb(1)).is_zero(): return acb(0)

But xi is perfectly regular there: xi(0) = xi(1) = 1/2. Returning zero injects
two spurious roots at the exact points a zero finder inspects. A zero-finding
kernel that manufactures roots is the single most damaging defect available
here. The singularity is handled analytically instead, by the series form,
which is regular.

Measured: `xi(0)` and `xi(1)` now enclose 1/2, and neither is zero.

## L22. `VERIFIED_BY_CONFORMANCE` verifies nothing

The blueprint declares the critical line once a ball of radius below 2^-128
overlaps 0.5. That criterion is satisfied by every converged zero, including a
hypothetical zero at 0.5 + 1e-10, and it places no constraint on sigma at all.

Replaced by a separation measurement: the certified offset between the
enclosure of Re(rho) and the point 0.5. Measured for the first three zeros:

    rho_1: Re(rho) = 0.5 +/- 7.5e-71,  offset enclosure contains 0.5
    rho_2: Re(rho) = 0.5 +/- 8.7e-78,  offset enclosure contains 0.5
    rho_3: Re(rho) = 0.5 +/- 4.7e-71,  offset enclosure contains 0.5

That is consistent with the critical line. It is not evidence for it, and
`certify_sigma_one_half` carries `global_claim_supported = False` on every code
path so that no caller can silently drop it.

## L23. `acb.zeta_zero` presupposes the critical line

FLINT's `acb.zeta_zero(n)` locates zeros along the critical line by argument
principle and returns a real part that prints as exactly 0.5. It is therefore
NOT independent evidence for sigma = 0.5 and must never be cited as such. It
is, however, an excellent independent source for the ordinates gamma, and this
kernel cross-validates against it: the imaginary parts agree to better than
1e-24, a genuine agreement between two unrelated implementations.

## L24. Python float literals bake binary64 rounding into every ball

    acb(1e-18).real.mid()  !=  acb("1e-18").real.mid()

The literal 1e-18 is the nearest double, 1.0000000000000000715...e-18, and that
is what enters the ball. Every constant crossing the API must be a decimal
string. The Newton seed radii in the root-pull campaign are passed as strings
for exactly this reason.

## L25. Convergence must be declared at the precision floor, not on escape

Once the enclosure radius reaches the rounding level, the next Newton image
necessarily wanders outside, because the arithmetic rather than the
mathematics has run out of room. A kernel that treats escape as failure
rejects successful localisations. `locate_zero` declares convergence when the
radius reaches 2^-(prec/2) and records `ZERO-LOCALIZED-AT-PRECISION-FLOOR`
when the floor is reached without a strictly contained image.

---

# Part III: landmines found in the Terminus Phase 2/3 blueprints

## L26. Phase 2 blueprint computes pixels in float64

`project_frequency_to_pixel` calls `float(gamma_arb.mid())`, `numpy.log2`,
`numpy.floor` and branches on `sys.maxsize`. A 77-digit certified ordinate
collapses to 16 digits before the floor is taken, and the uncertainty is
deleted without a trace. Worse, `int(numpy.floor(N_steps))` overflows the
platform integer range, so the `mod N_steps` branch is dead code on every
real machine and the pixel is never actually modular.

`msaf.visualizer.project_gamma_to_pixel` keeps the whole computation in Arb
and takes the floor on the ball itself. When both endpoints share one integer
the pixel is certified; otherwise `AmbiguousPixel` names both endpoint floors
and the caller must refine. Measured: gamma_1 -> pixel 461..., gamma_2 ->
686..., gamma_3 -> 816.... Only certified integers cross the matplotlib
boundary, and the axis is explicitly labelled `mod 2^32` while the JSON report
carries the full 206-bit addresses.

## L27. Phase 3 blueprint recomputes the chain with a foreign genesis

The blueprint verifies hashes against `"0" * 64` as the previous hash of the
first block and rebuilds the digest from `index + root_string +
previous_hash`, fields this ledger never wrote. Applied as-is it would declare
every existing ledger forged. The canonical chain (`GENESIS` origin, SHA-256
over the full sorted body) is defined once in `Ledger` and reused by
`final_audit.verify_ledger`, never reimplemented.

## L28. Phase 3 entropy check runs in float and numpy

`entropy_load = float(n) * (log2(1.0) + 0.115 * float(n) * log2(e))` saturates
and rounds on exactly the magnitudes this project cares about. Replaced by
`holographic_capacity_check` in Arb on both entropy paths. Measured at n = 16:
manuscript load 42.47 bit, measured load 7.84 bit, capacity 5e61 bit ->
`SAFE-COMPUTATION` on both paths.

## L29. The replay CLI must lock the campaign precision

Serialised ball radii are precision-dependent, so replaying a 256-bit ledger
at the 53-bit default reports every block as a mismatch. The CLI takes
`--prec` (default 256) and locks it before loading. Replaying at a deliberately
wrong precision exits 1 with `V(L) = False`; that behaviour is pinned by a
regression test so a silent false pass can never be introduced.

## L30. A mid-file `__main__` guard executes before later definitions

`if __name__ == "__main__": raise SystemExit(main())` sat in the middle of
`msaf/evolution.py`, ahead of the `RootPull*` definitions. In-process tests
passed because imports complete the module; the real CLI entry died with
`NameError` on any root-pull ledger. The guard is now the last statement of
the file, and a subprocess regression test runs the actual CLI against a
root-pull ledger so the two execution paths can never diverge again.

---

# Part IV: blind spots found by adversarial self-audit (2026-10-13)

These were not reported by any failing test. They were found by re-reading
every module with the assumption that the test suite is lying, then measuring.

## L31. `LOG2_E` froze at the 53-bit import default while the kernel ran 256-bit

Measured: import-time ball `[1.442695040888963 +/- 8.70e-16]`, live 256-bit
ball `[1.4426950408889634074 +/- 4.01e-20]`. Every budget quantity inherited a
53-bit radius that the report printed as a 256-bit result (e.g. mantissa
`[16.59099297022308 +/- 6.60e-15]`). The constant is now a function `log2_e()`
evaluated at the active precision on every call; a function cannot freeze.
Module-level Arb constants derived from anything but exact input are henceforth
treated as suspects, not assets.

## L32. The derivative tail double-counted the differentiation factor

`xi_derivative_over_ball` iterated over the DIFFERENTIATED coefficients
`d_j = (j+1) c_{j+1}` and multiplied by `(k+1)` a second time. The bound stayed
valid (a looser upper bound is still an upper bound) but contradicted the
documented identity and inflated every reported tail. Removed; the tail is now
exactly `sum |d_j| r^j`, pinned by an independent test that evaluates the
series at exact sample points inside the ball.

## L33. One-sided widening let genuine derivatives escape the enclosure (UNSOUND)

The critical one. The enclosure was built as `union(enc, enc + 2*tail)`. When
the tail ball is one-sided positive, that widens only UPWARD. The true
correction `d_1*h` points either way; measured `-8.01e-16` in the real part at
`h = +r/2`, below the enclosure's lower edge. The enclosure therefore did NOT
contain the true derivative, while every certificate reported success. The
localisation results survived only because the Newton division is dominated by
the imaginary component: luck, not rigor. Replaced by symmetric Minkowski
widening `enclosure + ([-t, +t])`, which cannot miss either side. The same
investigation proved the new test had to use the circular `_contains`
criterion (L19): native `contains()` reports False on mathematically contained
balls.

## L34. Root-pull outcome promised `Fitness` and delivered `None`

`evolve_root_pull` returned `EvolutionOutcome` with
`incumbent_fitness=None  # type: ignore`, a typed lie burried under a
suppression comment. Unused today, fatal the first day a caller trusts the
annotation. Replaced by `RootPullOutcome` carrying the real `RootPullFitness`,
now rendered in the audit report. In the same pass the `dimension` parameter
of the root-pull path was renamed to `newton_max_iter`: it never was a matrix
dimension, it always was the Newton iteration cap. Positional call
compatibility preserved, so every existing ledger still replays byte-identical.

## L35. Artifact paths were relative to the caller's working directory

`--ledger` and `--report-dir` defaulted to CWD-relative paths, so invoking the
audit from any other directory silently scattered ledgers across the
filesystem. Both are now anchored to the workspace root derived from the
module's own location. Ledgers can no longer escape the project.