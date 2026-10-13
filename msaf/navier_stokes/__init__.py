"""Navier-Stokes finitist lattice package (T-hat-N isolated workspace).

Strict-finitist reconstruction: no continuum limit ``lim dx -> 0``,
no float64, no infinitist blow-up. All reals are Arb balls built
from exact decimal strings.
"""

from __future__ import annotations

__all__ = ["fluid_lattice", "interpolation"]
