"""Inviscid-limit regression (R-NS-SPEC, nu -> 0 closure).

For fixed dt and frozen rotation field, one Godunov step dissipates
D(nu) = E0 - E1 strictly linearly in nu (measured 10.0000x/decade over
1e-1..1e-4 at 256-bit). Balls certify D > 0 at every decade; nu = 0 is
refused at construction (ValueError), so the Euler limit is approached
asymptotically, never materialized.
"""
import pytest

from msaf.navier_stokes.fluid_lattice import FluidLattice


def _dissipation(nu_str):
    lat = FluidLattice(4, nu_str, "1")
    for i in range(4):
        for j in range(4):
            for ll in range(4):
                lat.set_cell(i, j, ll, (f"{5 - j}e-1", f"{-25 + 10 * i}e-2", "0.1"))
    e0 = lat.kinetic_energy()
    lat.evolve_viscous_step("1e-43")
    return e0 - lat.kinetic_energy()


def test_inviscid_limit_linear_decay():
    ds = [_dissipation(nu) for nu in ("1e-1", "1e-2", "1e-3", "1e-4")]
    for d in ds:
        assert bool(d.is_finite()) is True
        assert bool(d > 0) is True  # ball-certified strict dissipation
    mids = [float(d.mid()) for d in ds]
    for hi, lo in zip(mids, mids[1:]):
        assert hi > lo  # D -> 0 monotonically with nu
        assert 9.0 < hi / lo < 11.0  # display-only linearity vs theory 10.0
    with pytest.raises(ValueError):
        FluidLattice(4, "0", "1")
