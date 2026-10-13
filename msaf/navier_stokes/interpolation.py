"""Finite-volume interpolation between lattice resolutions (no continuum limit).

Rule: refinement is an INTEGER map N -> k*N (k>=2). There is no
``lim dx -> 0``. A fine cell's ball must CONTAIN its coarse parent's
ball (enclosure preservation); otherwise the refinement manufactured
information. Coarsening takes the union (hull) of children, never a
float average. Non-circular: refine/coarsen copy or hull existing
balls; they never solve, bound, or assert the Navier-Stokes residual.
The UNSAT gates live in ``z3_tribunal/`` over fixed encoded bounds and
are neither imported nor re-proved here.
"""

from __future__ import annotations

from flint import arb

from .fluid_lattice import FluidLattice, _to_ball  # noqa: F401  (shared no-float ctor)

__all__ = [
    "refine",
    "refine_grid_cells",
    "coarsen",
    "interpolation_error_bound",
]


def _check_factor(factor: int) -> int:
    if isinstance(factor, float):
        raise TypeError("factor: float64 leakage refused")
    factor = int(factor)
    if factor < 2:
        raise ValueError(f"refinement factor must be >= 2, got {factor}")
    return factor


def refine_grid_cells(lattice: FluidLattice, factor: int = 2) -> FluidLattice:
    """Map coarse grid N to fine grid k*N with parent-ball containment.

    Each fine cell EQUALS its coarse parent ball, hence trivially
    contains it. No averaging, no float smoothing, no invented
    information. Viscosity/length re-derived from parent midpoints
    via exact printing, never via float. Ticks carried over exactly.
    Integer factor k>=2 only; no lim dx->0 path exists.
    """
    factor = _check_factor(factor)
    n_fine = lattice.n * factor
    nu_s = lattice.nu.mid().str(30, radius=False)
    l_s = lattice.length.mid().str(30, radius=False)
    fine = FluidLattice(n_fine, nu_s, l_s, lattice.prec_bits)
    for i in range(lattice.n):
        for j in range(lattice.n):
            for l in range(lattice.n):
                parent = lattice.cell(i, j, l)
                for di in range(factor):
                    for dj in range(factor):
                        for dl in range(factor):
                            fine.u[fine._idx(i * factor + di, j * factor + dj, l * factor + dl)] = parent
    fine.ticks = lattice.ticks
    return fine


def refine(coarse: FluidLattice, factor: int = 2) -> FluidLattice:
    """Backward-compatible alias of refine_grid_cells."""
    return refine_grid_cells(coarse, factor)


def coarsen(fine: FluidLattice, factor: int = 2) -> FluidLattice:
    """Coarsen N -> N/factor via ball union (hull) of children."""
    factor = _check_factor(factor)
    if fine.n % factor != 0:
        raise ValueError(f"N={fine.n} not divisible by factor={factor}")
    n_c = fine.n // factor
    nu_s = fine.nu.mid().str(30, radius=False)
    l_s = fine.length.mid().str(30, radius=False)
    coarse = FluidLattice(n_c, nu_s, l_s, fine.prec_bits)
    for i in range(n_c):
        for j in range(n_c):
            for l in range(n_c):
                hull0 = hull1 = hull2 = None
                for di in range(factor):
                    for dj in range(factor):
                        for dl in range(factor):
                            c = fine.cell(i * factor + di, j * factor + dj, l * factor + dl)
                            hull0 = c[0] if hull0 is None else hull0.union(c[0])
                            hull1 = c[1] if hull1 is None else hull1.union(c[1])
                            hull2 = c[2] if hull2 is None else hull2.union(c[2])
                assert hull0 is not None and hull1 is not None and hull2 is not None
                coarse.u[coarse._idx(i, j, l)] = (hull0, hull1, hull2)
    coarse.ticks = fine.ticks
    return coarse


def interpolation_error_bound(dx: arb, strain_rate_bound: arb) -> arb:
    """Rigorous bound: |u_fine - u_coarse| <= strain_rate_bound * dx.

    Tight interval product; both inputs are balls. No Taylor remainder
    through float, no hidden ``O(dx^2)`` constant asserted without a ball.
    P_narrative = 0: returns the enclosure only.
    """
    if isinstance(dx, float) or isinstance(strain_rate_bound, float):
        raise TypeError("float64 leakage refused in error bound")
    return strain_rate_bound * dx
