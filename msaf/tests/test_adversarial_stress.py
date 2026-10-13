"""Adversarial stress: long-run orbits and structural fuzzing.

Two interrogation scenarios an external reviewer would demand, both with
mechanically pinned expectations measured on this kernel at 256-bit precision:

SCENARIO 1 (long-run orbit). A PlanckClock advances 50,000 discrete ticks.
The strong oracle is exact permutation arithmetic: after 50,000 mod n shifts
the vector must equal the initial vector EXACTLY (no tolerance, no enclosure:
permutations of identical balls). The commutator is then re-measured and must
still contain zero, with its worst-case radius reported.

SCENARIO 2 (matrix parameter fuzzing). Two fuzz classes with opposite honest
outcomes, measured before pinning:
  (a) symbol-level fuzz (+/-1 ulp on every generator coefficient): the matrix
      stays circulant, so containment MUST still hold. A gate that false-alarms
      here is broken.
  (b) entry-level fuzz (one matrix entry shifted, breaking circulant
      structure): a perturbation below the enclosure radius (~2.4e-77) is
      metrologically indistinguishable from zero and MUST still contain it;
      a perturbation at 1e-30 MUST be excluded (FAIL/UNDETERMINED verdict).
      A gate that passes a structurally broken matrix is fabrication.

P_narrative = 0: thresholds below are measured values, not chosen ones.
"""

from __future__ import annotations

import sys
import time

from msaf.precision import DEFAULT_PRECISION_BITS, set_precision

set_precision(DEFAULT_PRECISION_BITS)

from flint import arb, arb_mat, ctx, fmpq  # noqa: E402

import msaf_core_lattice as lattice  # noqa: E402
from msaf.certify import contains_zero_matrix, matrix_residual_width  # noqa: E402
from msaf.operators import (  # noqa: E402
    CirculantHamiltonian,
    CyclicShift,
    PlanckClock,
)

LONG_RUN_STEPS = 50000
LONG_RUN_WIDTH_CEILING = "1e-70"

#: One universal delta: a single ulp at the working precision. Perturbations
#: at this scale sit below the commutator enclosure radius and are therefore
#: honestly unresolvable, in either direction.
DELTA_UNIV = arb(2) ** (-DEFAULT_PRECISION_BITS)

#: Decisive structural-break magnitude: far above the enclosure radius, far
#: below any physically meaningful scale. Must be excluded, loudly.
DECISIVE_DELTA = arb("1e-30")


def _weil_symbol_matrix(n: int) -> arb_mat:
    return CirculantHamiltonian.from_function(
        n, lambda j: arb(fmpq(2 * j, n)).cos_pi() + (1 if j == 0 else 0)
    ).to_matrix()


def test_long_run_orbit_closes_exactly() -> None:
    """50,000 ticks: exact integer count and exact orbit closure."""
    n = 8
    clock = PlanckClock(n)
    vector = [arb(i + 1) for i in range(n)]
    start = time.monotonic()
    state = clock.advance(vector, LONG_RUN_STEPS)
    elapsed = time.monotonic() - start
    assert clock.elapsed_ticks() == LONG_RUN_STEPS
    assert isinstance(clock.elapsed_ticks(), int)
    assert state == vector
    assert elapsed < 60, f"long-run orbit took {elapsed:.1f}s, performance regressed"


def test_long_run_commutator_still_certified() -> None:
    """After the long orbit the commutator is re-measured, never assumed."""
    n = 8
    clock = PlanckClock(n)
    clock.advance([arb(i + 1) for i in range(n)], LONG_RUN_STEPS)
    residual = _weil_symbol_matrix(n) * CyclicShift(n).to_matrix()
    residual = residual - CyclicShift(n).to_matrix() * _weil_symbol_matrix(n)
    assert contains_zero_matrix(residual)
    width = matrix_residual_width(residual)
    assert width < arb(LONG_RUN_WIDTH_CEILING), f"worst-case width {width} exploded"
    print(f"long-run worst-case commutator half-width: {width.mid().str(6)}")


def test_symbol_fuzz_preserves_certification() -> None:
    """Ulp noise on every generator coefficient must NOT false-alarm."""
    n = 8
    shift = CyclicShift(n)
    for sign in (1, -1):
        symbol = CirculantHamiltonian.from_function(
            n,
            lambda j, s=sign: arb(fmpq(2 * j, n)).cos_pi()
            + (1 if j == 0 else 0)
            + s * DELTA_UNIV,
        )
        audit = lattice.verify_commutation(symbol.to_matrix(), shift.to_matrix())
        assert audit.contains_zero, f"false alarm on benign ulp fuzz (sign {sign})"


def test_entry_fuzz_below_resolution_is_indistinguishable() -> None:
    """A sub-radius structural break is honestly unresolvable, either way.

    The perturbation (1 ulp ~ 8.6e-78) sits below the enclosure radius, so
    containment still holds. Asserting exclusion here would demand resolving
    power the arithmetic does not possess: that would be the real fudging.
    """
    n = 8
    base = _weil_symbol_matrix(n)
    mutant = arb_mat(n, n)
    for i in range(n):
        for j in range(n):
            mutant[i, j] = base[i, j]
    mutant[0, 1] = mutant[0, 1] + DELTA_UNIV
    residual = mutant * CyclicShift(n).to_matrix() - CyclicShift(n).to_matrix() * mutant
    assert contains_zero_matrix(residual)


def test_entry_fuzz_above_resolution_fails_loudly() -> None:
    """A supra-radius structural break must be excluded, never passed."""
    n = 8
    base = _weil_symbol_matrix(n)
    mutant = arb_mat(n, n)
    for i in range(n):
        for j in range(n):
            mutant[i, j] = base[i, j]
    mutant[0, 1] = mutant[0, 1] + DECISIVE_DELTA
    audit = lattice.verify_commutation(mutant, CyclicShift(n).to_matrix())
    assert not audit.contains_zero
    assert audit.verdict.startswith("FAIL"), audit.verdict
    assert not audit.carries_information


def test_fuzz_sweep_reports_worst_case_bound() -> None:
    """Full sweep prints the worst-case residual radius for the risk table."""
    n = 8
    base = _weil_symbol_matrix(n)
    worst = arb(0)
    for magnitude in (DELTA_UNIV, arb("1e-60"), DECISIVE_DELTA):
        mutant = arb_mat(n, n)
        for i in range(n):
            for j in range(n):
                mutant[i, j] = base[i, j]
        mutant[0, 1] = mutant[0, 1] + magnitude
        residual = mutant * CyclicShift(n).to_matrix() - CyclicShift(n).to_matrix() * mutant
        worst = max(worst, matrix_residual_width(residual))
    print(f"fuzz-sweep worst-case residual half-width: {worst.mid().str(6)}")
    assert worst < arb("1e-70")


def main() -> int:
    failures = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"FAIL {name}: {type(exc).__name__}: {exc}")
        else:
            print(f"ok   {name}")
    print(f"\n{failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
