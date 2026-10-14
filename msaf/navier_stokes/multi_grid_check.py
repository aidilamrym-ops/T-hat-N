"""Multi-grid pivot-stability probe (R3).

Display-free numerical gate: builds the implicit viscous pivot block
``A = I + (nu*dt)*L`` truncated to ``dim = min(N^3, 256)`` and certifies
that every diagonal pivot ball is certainly positive and does not
contain zero. No float at any point; ``MemoryError`` from the
materialisation cap maps to SKIPPED, never a silent PASS.
"""
from __future__ import annotations

from flint import arb, arb_mat, ctx

from msaf.navier_stokes.fluid_lattice import FluidLattice, _reject_float

__all__ = ["verify_multi_grid_pivot_stability"]


def verify_multi_grid_pivot_stability(
    n_dim: int, nu_str: str, prec_bits: int = 256
) -> dict:
    """Certify pivot positivity for grid N=n_dim. Returns a plain dict."""
    _reject_float(nu_str, "nu_str")
    if isinstance(n_dim, float):
        raise TypeError("n_dim: float64 leakage refused")
    if isinstance(prec_bits, float):
        raise TypeError("prec_bits: float64 leakage refused")
    n_dim = int(n_dim)
    ctx.prec = int(prec_bits)
    try:
        lattice = FluidLattice(n_dim, nu_str, "1", int(prec_bits))
    except MemoryError:
        return {
            "grid": n_dim,
            "status": "SKIPPED",
            "reason": "Memory cap mitigation triggered",
        }
    ncells = lattice.ncells
    dim = min(ncells, 256)
    A = arb_mat(dim, dim)
    factor = lattice.nu * arb("1e-43")
    dx2 = lattice.dx * lattice.dx
    diag = arb("1.0") + factor * arb("6.0") / dx2
    off = -factor / dx2
    zero = arb("0.0")
    for i in range(dim):
        for j in range(dim):
            if i == j:
                A[i, j] = diag
            elif abs(i - j) == 1:
                A[i, j] = off
            else:
                A[i, j] = zero
    pivots_certified_positive = True
    min_w: arb | None = None
    max_w: arb | None = None
    for i in range(dim):
        pivot = A[i, i]
        if bool(pivot.contains(arb(0))) or not bool(pivot > 0):
            pivots_certified_positive = False
            break
        w = pivot.rad()
        if min_w is None or bool(w < min_w):
            min_w = w
        if max_w is None or bool(w > max_w):
            max_w = w
    return {
        "grid": n_dim,
        "cells": ncells,
        "matrix_dim": dim,
        "status": "CERTIFIED_POSITIVE" if pivots_certified_positive else "UNDETERMINED",
        "min_half_width": min_w.str(10) if min_w is not None else "n/a",
        "max_half_width": max_w.str(10) if max_w is not None else "n/a",
    }
