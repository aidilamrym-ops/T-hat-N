"""Bridge from Lean ``Shape`` to the MSAF circulant lattice operators.

Scope warning, locked by the pre-registration: the bridge builds a *model*
layer. ``H_hat = I + J`` and ``T_hat`` is the cyclic shift, so they commute by
construction. The commutation certificate is labelled ``CONSTRUCTION-GUARD``
and must never be reported as empirical evidence about the Guinand-Weil
matrix or about the zeta function.

The artifact-level test lives in ``msaf.chrono_runtime.riemann_operator`` and
is a refutation-only pairing test on the recorded spectrum.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flint import arb, fmpq

from msaf.chrono_runtime.shape_ops import (
    DftCertificate,
    Matrix,
    Shape,
    dft_certificate,
    leaf_count,
    mul,
    shape_operators,
    transpose,
)

__all__ = [
    "LatticeOperators",
    "CommutationCertificate",
    "build_operators",
    "verify_commutation",
]

OFF_DIAGONAL_GUARD = arb(fmpq(1, 10**40))


@dataclass(frozen=True)
class LatticeOperators:
    dim: int
    h_hat: Matrix
    t_hat: Matrix
    h_is_symmetric: bool
    t_is_permutation: bool
    commutes_exactly: bool
    dft_h: DftCertificate
    dft_t: DftCertificate


def _is_permutation(matrix: Matrix) -> bool:
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        return False
    for row in matrix:
        if sorted(row) != [0] * (n - 1) + [1]:
            return False
    for j in range(n):
        if sum(matrix[i][j] for i in range(n)) != 1:
            return False
    return True


def build_operators(shape: Shape) -> LatticeOperators:
    """Build ``(H_hat, T_hat)`` and the DFT certificate for a shape."""
    n = leaf_count(shape)
    if n == 0:
        raise ValueError("empty Shape has no operator: 0x0 is not defined")

    h_hat, t_hat = shape_operators(shape)
    return LatticeOperators(
        dim=n,
        h_hat=h_hat,
        t_hat=t_hat,
        h_is_symmetric=h_hat == transpose(h_hat),
        t_is_permutation=_is_permutation(t_hat),
        commutes_exactly=mul(h_hat, t_hat) == mul(t_hat, h_hat),
        dft_h=dft_certificate(h_hat),
        dft_t=dft_certificate(t_hat),
    )


@dataclass(frozen=True)
class CommutationCertificate:
    dim: int
    commutes_exactly: bool
    commutation_residual_is_zero: bool
    h_is_symmetric: bool
    t_is_permutation: bool
    h_off_diagonal_upper: arb
    t_off_diagonal_upper: arb
    h_diagonal_deviation: arb
    t_unit_modulus_deviation: arb
    off_diagonal_guard: arb
    dft_guard_passed: bool
    kind: str
    tautological_by_construction: bool
    lean_decl: str | None
    anchor_status: str
    anchor_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "dim": self.dim,
            "commutes_exactly": self.commutes_exactly,
            "commutation_residual_is_zero": self.commutation_residual_is_zero,
            "h_is_symmetric": self.h_is_symmetric,
            "t_is_permutation": self.t_is_permutation,
            "h_off_diagonal_upper": self.h_off_diagonal_upper.str(20),
            "t_off_diagonal_upper": self.t_off_diagonal_upper.str(20),
            "h_diagonal_deviation": self.h_diagonal_deviation.str(20),
            "t_unit_modulus_deviation": self.t_unit_modulus_deviation.str(20),
            "off_diagonal_guard": self.off_diagonal_guard.str(20),
            "dft_guard_passed": self.dft_guard_passed,
            "kind": self.kind,
            "tautological_by_construction": self.tautological_by_construction,
            "lean_decl": self.lean_decl,
            "anchor_status": self.anchor_status,
            "anchor_reason": self.anchor_reason,
        }


def verify_commutation(shape: Shape) -> CommutationCertificate:
    """Return a certificate that the constructed operators commute.

    The residual is exactly the zero matrix because both operands are
    circulants. That is a construction guard, not a measurement.
    """
    operators = build_operators(shape)
    n = operators.dim

    h_deviation = abs(operators.dft_h.diagonal[0] - (n + 1))
    for j in range(1, n):
        h_deviation += abs(operators.dft_h.diagonal[j] - 1)

    t_deviation = arb(0)
    for entry in operators.dft_t.diagonal:
        t_deviation += abs(abs(entry) - 1)

    dft_ok = (
        operators.dft_h.off_diagonal_sum_upper.upper() < OFF_DIAGONAL_GUARD
        and operators.dft_t.off_diagonal_sum_upper.upper() < OFF_DIAGONAL_GUARD
        and h_deviation.upper() < OFF_DIAGONAL_GUARD
        and t_deviation.upper() < OFF_DIAGONAL_GUARD
    )

    return CommutationCertificate(
        dim=n,
        commutes_exactly=operators.commutes_exactly,
        commutation_residual_is_zero=operators.commutes_exactly,
        h_is_symmetric=operators.h_is_symmetric,
        t_is_permutation=operators.t_is_permutation,
        h_off_diagonal_upper=operators.dft_h.off_diagonal_sum_upper,
        t_off_diagonal_upper=operators.dft_t.off_diagonal_sum_upper,
        h_diagonal_deviation=h_deviation,
        t_unit_modulus_deviation=t_deviation,
        off_diagonal_guard=OFF_DIAGONAL_GUARD,
        dft_guard_passed=dft_ok,
        kind="CONSTRUCTION-GUARD",
        tautological_by_construction=True,
        lean_decl=None,
        anchor_status="UNANCHORED",
        anchor_reason=(
            "circulant linear-algebra construction; the vendored Lean subtree "
            "has no declaration for H_hat/T_hat and must not be modified"
        ),
    )
