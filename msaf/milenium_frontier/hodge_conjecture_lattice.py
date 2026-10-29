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

    def compute_exact_gram_matrix(
        self, cycles: list[list[int]]
    ) -> list[list[Fraction]]:
        """Exact Gram matrix of finite Hodge cycles over QQ.

        Each entry G[k][m] = <c_k, c_m> is the bilinear inner product
        against ``self.pairing``, computed in ``fractions.Fraction``
        only. Any ``float`` coefficient raises ``TypeError`` before any
        arithmetic runs. The input list is validated, never mutated,
        and stored cycles are untouched (no side effects).
        """
        vecs: list[tuple[Fraction, ...]] = []
        for row in cycles:
            vec = tuple(_to_frac(c) for c in row)
            if len(vec) != self.rank:
                raise ValueError(f"cycle needs {self.rank} coefficients")
            vecs.append(vec)
        gram: list[list[Fraction]] = []
        for ck in vecs:
            out_row: list[Fraction] = []
            for cm in vecs:
                total = Fraction(0)
                for a in range(self.rank):
                    for b in range(self.rank):
                        total += ck[a] * self.pairing[a][b] * cm[b]
                out_row.append(total)
            gram.append(out_row)
        return gram

    @staticmethod
    def _exact_det(mat: list[list[Fraction]]) -> Fraction:
        """Exact determinant via Fraction elimination with row swaps.

        Bareiss without pivoting was rejected here: a zero mid-path
        pivot with nonzero determinant would have faked a zero minor.
        Partial pivoting (sign-tracked swaps) keeps every zero verdict
        exact and every nonzero verdict sign-correct.
        """
        n = len(mat)
        if n == 0:
            return Fraction(1)
        a = [row[:] for row in mat]
        sign = Fraction(1)
        for k in range(n):
            piv = next((i for i in range(k, n) if a[i][k] != 0), None)
            if piv is None:
                return Fraction(0)
            if piv != k:
                a[k], a[piv] = a[piv], a[k]
                sign = -sign
            for i in range(k + 1, n):
                factor = a[i][k] / a[k][k]
                for j in range(k, n):
                    a[i][j] -= factor * a[k][j]
        det = sign
        for k in range(n):
            det *= a[k][k]
        return det

    def verify_hodge_cycle_definiteness(self) -> dict:
        """Sylvester sign test over the stored cycles' Gram matrix.

        Leading principal minors are exact ``Fraction`` determinants
        (pivoted elimination). Any zero minor -> ``UNDETERMINED`` (loud: the sign
        is unknowable, never defaulted). All-positive -> 
        ``POSITIVE_DEFINITE``; strict alternation from negative ->
        ``NEGATIVE_DEFINITE``; otherwise ``INDEFINITE``. Empty cycle
        list raises ``ValueError`` (no vacuous verdict).
        """
        if not self.cycles:
            raise ValueError("no cycles stored; definiteness vacuous, refused")
        gram = self.compute_exact_gram_matrix([list(c) for c in self.cycles])
        minors: list[Fraction] = []
        for k in range(1, len(gram) + 1):
            minors.append(self._exact_det([row[:k] for row in gram[:k]]))
        if any(m == 0 for m in minors):
            status = "UNDETERMINED"
        elif all(m > 0 for m in minors):
            status = "POSITIVE_DEFINITE"
        elif all((m > 0) == (k % 2 == 0) for k, m in enumerate(minors, start=1)):
            status = "NEGATIVE_DEFINITE"
        else:
            status = "INDEFINITE"
        return {
            "status": status,
            "dim": len(gram),
            "leading_minors": [str(m) for m in minors],
            "scope": self.SCOPE,
        }


