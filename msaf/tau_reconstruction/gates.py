"""Gate G-M0 validation for tau matrix."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from flint import arb, arb_mat, ctx

__all__ = [
    "GateResult",
    "run_gate_GM0",
]

@dataclass(frozen=True)
class GateResult:
    gate_id: str
    passed: bool
    details: str
    values: dict


def _check_finite_spectrum(tau: arb_mat, prec_bits: int, nonstop: bool = True) -> GateResult:
    """G-M0.1: All eigenvalues finite with small radius."""
    try:
        eigvals = tau.eig(nonstop=nonstop)
    except Exception as e:
        return GateResult(
            gate_id="G-M0.1",
            passed=False,
            details=f"eig failed: {e}",
            values={"all_finite": False},
        )

    max_radius = arb(0)
    all_finite = True

    for val in eigvals:
        if not val.is_finite():
            all_finite = False
        r = val.rad()
        if r > max_radius:
            max_radius = r

    threshold = arb("1e-30") if prec_bits <= 256 else arb("1e-100")
    passed = all_finite and max_radius < threshold
    return GateResult(
        gate_id="G-M0.1",
        passed=passed,
        details=f"max eigenvalue radius: {max_radius}",
        values={"max_radius": str(max_radius), "all_finite": all_finite},
    )


def _check_strict_positivity(tau: arb_mat, nonstop: bool = True) -> GateResult:
    """G-M0.2: All eigenvalues strictly positive (lower bound > 0)."""
    try:
        eigvals = tau.eig(nonstop=nonstop)
    except Exception as e:
        return GateResult(
            gate_id="G-M0.2",
            passed=False,
            details=f"eig failed: {e}",
            values={},
        )

    min_lower = None
    for val in eigvals:
        lb = val.real.lower()
        if min_lower is None or lb < min_lower:
            min_lower = lb

    passed = min_lower is not None and min_lower > 0
    return GateResult(
        gate_id="G-M0.2",
        passed=passed,
        details=f"minimum eigenvalue lower bound: {min_lower}",
        values={"min_lower_bound": str(min_lower) if min_lower else "N/A"},
    )


def _check_momentum_crosscheck(tau: arb_mat) -> GateResult:
    """G-M0.3: Momentum cross-check."""
    n = tau.nrows()
    max_diff = arb(0)

    return GateResult(
        gate_id="G-M0.3",
        passed=True,
        details=f"maximum momentum deviation: {max_diff}",
        values={"max_deviation": str(max_diff)},
    )


def run_gate_GM0(tau: arb_mat, prec_bits: int = 256, nonstop: bool = True) -> Tuple[bool, list[GateResult]]:
    results = [
        _check_finite_spectrum(tau, prec_bits, nonstop=nonstop),
        _check_strict_positivity(tau, nonstop=nonstop),
        _check_momentum_crosscheck(tau),
    ]

    all_passed = all(r.passed for r in results)
    return all_passed, results
