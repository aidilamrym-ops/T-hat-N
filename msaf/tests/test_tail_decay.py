"""Periodic-box tail regression (R3 tails closure, last OPEN item).

A point source on the N=16 periodic lattice probes the lattice Green
function. Raw radial ratios are NOT asserted: the zero-mean gauge plus
periodic images add a smooth background that distorts naive p(r)/p(2r)
(measured 2.49 / 4.20 vs free-space 2.0), and raw cross-N comparison is
invalid because a discrete delta carries dx^2 normalization (naive
N=8-vs-16 diff reached 73% of signal: a scaling artifact, not tails).

Locked instead, both background-free and gauge-honest:
(a) difference quotient (v1-v2)/(v2-v4) cancels any locally constant
    background (gauge + smooth image field); free-space 1/r gives
    exactly 2.0, measured 1.9519;
(b) far-field contamination (spread over axis shell r=6,7,8 relative
    to peak) bounded below 2%, measured 0.61%;
(c) every solution radius below 1e-70: tails certified, never vacuous.
Shells are required at r << N/2 (here 1,2,4 vs N/2=8); the N=8 analog
fails the band because its outer shell sits on the zero-crossing.
"""
from flint import arb, ctx

from msaf.navier_stokes.fluid_lattice import FluidLattice


def test_periodic_tail_structure():
    ctx.prec = 256
    lat = FluidLattice(16, "0.1", "1")
    src = [arb(0)] * lat.ncells
    src[lat._idx(0, 0, 0)] = arb("1")
    mean = arb(0)
    for s in src:
        mean += s
    src = [s - mean / arb(lat.ncells) for s in src]
    p = lat._spectral_poisson_direct(src)
    v = [float(p[lat._idx(r, 0, 0)].mid()) for r in range(9)]
    assert v[1] < 0 and v[2] < 0 and v[4] < 0  # shells inside the well
    q = (v[1] - v[2]) / (v[2] - v[4])
    assert 1.7 < q < 2.3
    far = [v[6], v[7], v[8]]
    assert (max(far) - min(far)) / abs(v[0]) < 0.02
    for cell in p:
        assert bool(cell.rad() < arb("1e-70")) is True


