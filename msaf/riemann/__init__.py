"""Riemann exclusion campaign: bounded zero-absence certificates.

SCOPE (binding): this package certifies absence of zeta zeros inside
explicit small rectangles, by rigorous ball evaluation of xi. A
rectangle containing (or too close to) a zero can NEVER clear, and is
reported CANNOT-EXCLUDE / INCONCLUSIVE -- loudly, never as a pass.
Finitely many cleared rectangles prove nothing global about RH.
"""
from __future__ import annotations

__all__ = ["exclusion"]


