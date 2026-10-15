"""Analytic periods side of the Hodge program (measurement only).

The combinatorial side lives in ``msaf/milenium_frontier``. Nothing
here proves anything about the Hodge conjecture: this package
encloses period ratios of concrete elliptic curves, cross-checked
against independent implementations. Scope: real ordered branch
points only (principal real square roots, no branch ambiguity).
"""
from __future__ import annotations

__all__ = [
    "periods",
    "point_count",
    "finite_fields",
    "odd_fields",
    "picard_bound",
    "gauss_exact",
    "fermat_k3",
    "crt_combine",
    "weil_search",
]
