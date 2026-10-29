"""Lean-Python correspondence: central-difference SBP as ball enclosure.

The Lean kernel proves summation-by-parts for its forward/backward
pair. This harness checks the matching TRUE identity of the Python
kernel's CENTRAL operators: per axis,
  sum_cells u_c * d_c(p) + sum_cells div(u) * p  contains  0,
with d_c the central difference along axis c. (The second-order
pairing <7pt-Laplacian, central-gradient> is FALSE in general --
delta counterexample gives -2 vs -1/2 -- and is NOT asserted here.)
"""
from flint import arb, ctx

from msaf.navier_stokes.fluid_lattice import FluidLattice


def _scalar_field(lat, func):
    n = lat.n
    return [func(i, j, ll) for i in range(n) for j in range(n) for ll in range(n)]


def _sbp_residual(lat, p):
    n = lat.n
    inv2dx = arb(1) / (arb(2) * lat.dx)
    gx = arb(0)
    gy = arb(0)
    gz = arb(0)
    div = arb(0)
    for i in range(n):
        for j in range(n):
            for ll in range(n):
                k = lat._idx(i, j, ll)
                ux, uy, uz = lat.cell(i, j, ll)
                kx_p = lat._idx(i + 1, j, ll)
                kx_m = lat._idx(i - 1, j, ll)
                ky_p = lat._idx(i, j + 1, ll)
                ky_m = lat._idx(i, j - 1, ll)
                kz_p = lat._idx(i, j, ll + 1)
                kz_m = lat._idx(i, j, ll - 1)
                gx += ux * (p[kx_p] - p[kx_m]) * inv2dx
                gy += uy * (p[ky_p] - p[ky_m]) * inv2dx
                gz += uz * (p[kz_p] - p[kz_m]) * inv2dx
                div += lat.divergence_at(i, j, ll) * p[k]
    return gx + gy + gz + div


def _rotation_lat(n):
    lat = FluidLattice(n, "0.0001", "1")
    for i in range(n):
        for j in range(n):
            for ll in range(n):
                lat.set_cell(i, j, ll, (f"{5 - j}e-1", f"{-25 + 10 * i}e-2", "0.1"))
    return lat


def test_sbp_central_n4():
    ctx.prec = 256
    lat = _rotation_lat(4)
    p = _scalar_field(
        lat, lambda i, j, ll: arb(f"{i + 2 * j + 3 * ll + 1}e-1")
    )
    res = _sbp_residual(lat, p)
    assert bool(res.contains(arb(0))) is True
    assert bool(res.rad() < arb("1e-70")) is True


def test_sbp_central_n8():
    ctx.prec = 256
    lat = _rotation_lat(8)
    p = _scalar_field(
        lat, lambda i, j, ll: arb(f"{(i * j + ll) % 7 + 1}e-1")
    )
    res = _sbp_residual(lat, p)
    assert bool(res.contains(arb(0))) is True
    assert bool(res.rad() < arb("1e-70")) is True


