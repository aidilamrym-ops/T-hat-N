"""3-grid convergence-order regression (R-NS-SPEC, partial closure).

Manufactured periodic solution p* = cos2pxÂ·cos2py + cycl., src = -8pi^2Â·p*.
The spectral kernel inverts the DISCRETE 7-point Laplacian, so the
midpoint error vs the analytic field is pure truncation O(dx^2).
Locks observed order in [1.7, 2.5] on N = 4/8/16 at 256-bit.
"""
import math


def _grid_error(N):
    from flint import arb, ctx

    from msaf.navier_stokes.fluid_lattice import FluidLattice

    ctx.prec = 256
    lat = FluidLattice(N, "0.1", "1")
    pi = arb.pi()
    two_pi = arb(2) * pi
    src = [arb(0)] * lat.ncells
    ptru = [arb(0)] * lat.ncells
    for i in range(N):
        cx = (two_pi * arb(i) * lat.dx).cos()
        for j in range(N):
            cy = (two_pi * arb(j) * lat.dx).cos()
            for ll in range(N):
                cz = (two_pi * arb(ll) * lat.dx).cos()
                p = cx * cy + cy * cz + cz * cx
                k = lat._idx(i, j, ll)
                ptru[k] = p
                src[k] = arb(-8) * pi * pi * p
    mean = arb(0)
    for s in src:
        mean += s
    src = [s - mean / arb(lat.ncells) for s in src]
    pmean = arb(0)
    for p in ptru:
        pmean += p
    pmean = pmean / arb(lat.ncells)
    psol = lat._spectral_poisson_direct(src)
    emax = 0.0
    rmax = arb(0)
    for k in range(lat.ncells):
        d = psol[k] - (ptru[k] - pmean)
        m = abs(float(d.mid()))
        if m > emax:
            emax = m
        if bool(d.rad() > rmax):
            rmax = d.rad()
    return emax, rmax


def test_convergence_order_second_order():
    from flint import arb

    e4, r4 = _grid_error(4)
    e8, r8 = _grid_error(8)
    e16, r16 = _grid_error(16)
    o1 = math.log2(e4 / e8)
    o2 = math.log2(e8 / e16)
    assert 1.7 < o1 < 2.5
    assert 1.7 < o2 < 2.5
    assert abs(o2 - 2.0) < abs(o1 - 2.0)  # refining toward theory
    for r in (r4, r8, r16):
        assert bool(r < arb("1e-70")) is True  # radii honest, far below error


