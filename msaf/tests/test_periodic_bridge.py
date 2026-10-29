"""Guard for the periodic-box mode sum (msaf/periodic_bridge.py).

Two independent engines must agree: the fast O(N^3) mode sum defined here and
the sealed O(N^4) separable-DFT solver of ``FluidLattice``. Agreement is
tested with the containment rule of ``msaf/certify.py``: the difference ball
must contain exact zero, which is the only admissible form of "both enclosures
describe the same exact value".

Also pinned: radii stay tiny (certified, never vacuous), the probe quotient is
certified only when its denominator excludes zero, and float inputs are
refused on every numeric entry point.
"""

from __future__ import annotations

import pytest
from flint import arb, ctx

from msaf.navier_stokes.fluid_lattice import FluidLattice
from msaf.periodic_bridge import Probe, axis_value, axis_values, probe


@pytest.fixture(autouse=True)
def _precision():
    old = ctx.prec
    ctx.prec = 256
    yield
    ctx.prec = old


def _sealed_axis_values(n: int, rs: list[int]) -> dict[int, arb]:
    """Axis values from the sealed separable-DFT solver, zero-mean gauge."""
    lat = FluidLattice(n, "0.1", "1")
    src = [arb(0)] * lat.ncells
    src[lat._idx(0, 0, 0)] = arb("1")
    mean = arb(0)
    for s in src:
        mean += s
    src = [s - mean / arb(lat.ncells) for s in src]
    p = lat._spectral_poisson_direct(src)
    return {r: p[lat._idx(r, 0, 0)] for r in rs}


def test_mode_sum_agrees_with_sealed_solver() -> None:
    n = 8
    rs = [0, 1, 2, 3, 4]
    fast = axis_values(n, rs)
    sealed = _sealed_axis_values(n, rs)
    for r in rs:
        diff = fast[r] - sealed[r]
        assert bool(diff.contains(arb(0))), (
            "independent engines disagree at N=%d r=%d: %s vs %s"
            % (n, r, fast[r], sealed[r])
        )
        assert bool(fast[r].rad() < arb("1e-60"))
        assert bool(sealed[r].rad() < arb("1e-60"))


def test_axis_values_are_certified_and_signed() -> None:
    n = 16
    vals = axis_values(n, [1, 2, 4])
    for r, v in vals.items():
        assert bool(v.rad() < arb("1e-60"))
        assert bool(v < 0), "axis Green values must be provably negative at r=%d" % r
    # Magnitude decays along the axis in this shell band (1 -> 4).
    assert bool(abs(vals[4]) < abs(vals[1]))


def test_probe_is_certified() -> None:
    p = probe(16)
    assert isinstance(p, Probe)
    assert bool(p.denominator.rad() < arb("1e-60"))
    assert not bool(p.denominator.contains(arb(0)))
    # Sealed record measured 1.9519 at N=16; the certified ball must bracket it.
    assert bool(arb("1.8") <= p.q)
    assert bool(p.q <= arb("2.1"))


def test_probe_quotient_excludes_zero_denominator() -> None:
    # N=6: v(4) = v(6-4) = v(2) by axis symmetry, so v2 - v4 is exactly zero.
    with pytest.raises(ValueError):
        probe(6)


def test_inputs_rejected() -> None:
    with pytest.raises(TypeError):
        axis_value(8.0, 1)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        axis_value(8, 1.0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        axis_value(8, 1, 1.0)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        axis_value(1, 0)
    with pytest.raises(ValueError):
        axis_value(8, 8)
    with pytest.raises(ValueError):
        axis_value(8, -1)
    with pytest.raises(ValueError):
        axis_value(8, 1, "0")
    with pytest.raises(ValueError):
        axis_value(8, 1, "nan")


def test_deterministic() -> None:
    assert axis_value(8, 3).str(40) == axis_value(8, 3).str(40)


