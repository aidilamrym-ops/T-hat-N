"""Discrete time evolution: the Planck clock on the shift execution path.

Each test pins one facet an external auditor would attack: exact integer
bookkeeping, Arb-only physical time, periodicity of the discrete orbit, and
commutation preserved at every step of a locally run time series. Run with
`python -m pytest msaf -q`.
"""

from __future__ import annotations

import sys

from msaf.precision import DEFAULT_PRECISION_BITS, set_precision

set_precision(DEFAULT_PRECISION_BITS)

from flint import arb, arb_mat, fmpq  # noqa: E402

from msaf.certify import contains_zero, contains_zero_matrix  # noqa: E402
from msaf.operators import (  # noqa: E402
    CirculantHamiltonian,
    CyclicShift,
    PlanckClock,
    commutator_residual,
    identity,
)


def test_tick_counter_is_exact_integer() -> None:
    clock = PlanckClock(8)
    vector = [arb(i + 1) for i in range(8)]
    state = clock.advance(vector, 13)
    assert clock.elapsed_ticks() == 13
    assert isinstance(clock.elapsed_ticks(), int)
    assert len(state) == 8


def test_negative_steps_are_refused() -> None:
    clock = PlanckClock(8)
    try:
        clock.advance([arb(1)] * 8, -1)
    except ValueError:
        assert clock.elapsed_ticks() == 0
        return
    raise AssertionError("negative time step was executed")


def test_elapsed_time_is_arb_only() -> None:
    """Physical time without a single float: ticks * t_P as balls."""
    clock = PlanckClock(6)
    clock.advance([arb(1)] * 6, 100)
    elapsed = clock.elapsed_time()
    assert isinstance(elapsed, arb)
    assert contains_zero(elapsed - arb(100) * arb("5.39e-44"))


def test_full_period_returns_the_orbit() -> None:
    """After exactly n ticks the discrete orbit closes: T^n = I on vectors."""
    n = 6
    clock = PlanckClock(n)
    vector = [arb(i + 1) for i in range(n)]
    assert clock.advance(vector, n) == vector
    assert clock.elapsed_ticks() == n


def test_clock_trajectory_matches_dense_powers() -> None:
    """Structural path and dense-matrix path agree at every sampled step."""
    n = 6
    clock = PlanckClock(n)
    shift = CyclicShift(n).to_matrix()
    vector = [arb(i + 1) for i in range(n)]
    state = list(vector)
    power = identity(n)
    for _ in range(1, n + 1):
        state = clock.tick(state)
        power = shift * power
        dense = [sum(power[i, j] * vector[j] for j in range(n)) for i in range(n)]
        assert all(contains_zero(state[i] - dense[i]) for i in range(n))


def test_commutation_holds_at_every_orbit_step() -> None:
    """[H, T^k] = 0 certified by enclosure for each power along the orbit.

    The commutator residual is re-measured (not assumed constant) at every
    discrete time step, for two generator symbols. Any drift would fail here.
    """
    from flint import arb as _arb  # noqa: F401 - pinned binding check

    n = 8
    shift = CyclicShift(n).to_matrix()
    for harmonic in (1, 3):
        symbol = CirculantHamiltonian.from_function(
            n, lambda j, h=harmonic: arb(fmpq(2 * h * j, n)).cos_pi()
        )
        hamiltonian = symbol.to_matrix()
        power = identity(n)
        for _ in range(n):
            power = shift * power
            residual = hamiltonian * power - power * hamiltonian
            assert contains_zero_matrix(residual), (
                f"commutation broke at orbit step for harmonic {harmonic}"
            )
    base = CirculantHamiltonian.from_function(n, lambda j: arb(j + 1))
    assert commutator_residual(base, CyclicShift(n)).certified


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


