"""Scaffolding: finite combinatorial Hodge cycles over exact rationals.

SCOPE (binding): a continuous Hodge cycle on a complex algebraic
manifold is cut down here to a finite integer-linear combination of
cell basis elements carrying rational (p, p) bidegrees. The pairing
matrix is exact over QQ (``fractions.Fraction``). This combinatorial
shadow proves nothing about the Hodge conjecture; it is the finite
object the conjecture's algebraic side would need to hit.
"""
from __future__ import annotations

from fractions import Fraction

__all__ = ["HodgeLattice"]


def _reject_float(value, name: str) -> None:
    if isinstance(value, float):
        raise TypeError(f"{name}: float64 leakage refused")


def _to_frac(value) -> Fraction:
    if isinstance(value, float):
        raise TypeError("coefficient: float64 leakage refused")
    if isinstance(value, Fraction):
        return value
    return Fraction(str(value))


class HodgeLattice:
    """Finite cell complex with rational (p, p)-graded cycle lattice."""

    SCOPE = "finite rational shadow only; proves nothing about Hodge"

    def __init__(self, rank: int, degree_p: int) -> None:
        if isinstance(rank, float) or isinstance(degree_p, float):
            raise TypeError("rank/degree_p: float64 leakage refused")
        rank, degree_p = int(rank), int(degree_p)
        if rank < 1 or degree_p < 0:
            raise ValueError("rank >= 1 and degree_p >= 0 required")
        self.rank = rank
        self.degree_p = degree_p
        self.cycles: list[tuple[Fraction, ...]] = []
        # Exact intersection pairing: identity over QQ by default.
        self.pairing: list[list[Fraction]] = [
            [Fraction(1) if a == b else Fraction(0) for b in range(rank)]
            for a in range(rank)
        ]

    def add_cycle(self, coeffs) -> int:
        """Append one finite Hodge cycle; returns its index."""
        vec = tuple(_to_frac(c) for c in coeffs)
        if len(vec) != self.rank:
            raise ValueError(f"cycle needs {self.rank} coefficients")
        self.cycles.append(vec)
        return len(self.cycles) - 1

    def pairing_value(self, k: int, m: int) -> Fraction:
        """Exact bilinear pairing <c_k, c_m> over QQ."""
        ck, cm = self.cycles[k], self.cycles[m]
        total = Fraction(0)
        for a in range(self.rank):
            for b in range(self.rank):
                total += ck[a] * self.pairing[a][b] * cm[b]
        return total

    def is_rational_hodge_class(self, k: int) -> bool:
        """By construction every stored cycle is a rational (p,p) class."""
        _ = self.cycles[k]
        return True
