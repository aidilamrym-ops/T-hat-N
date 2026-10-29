"""Enclosed periods of real elliptic curves via AGM.

Convention (canonical basis, empirically pinned): for ordered real
branch points e1 > e2 > e3,
  w1 = pi / agm(sqrt(e1-e3), sqrt(e1-e2)),
  w2 = i*pi / agm(sqrt(e1-e3), sqrt(e2-e3)),
  tau = w2 / w1.
The swapped axis choice is an equally valid basis (SL(2,Z)-related)
but leaves the fundamental domain; the convention above keeps
|tau| >= 1 and is locked by the lambda-orbit test (1/4, not 3/4).
Validation: square curve tau contains exactly i; lambda=4 curve
satisfies j(tau) containing the algebraic j AND lambda(tau)
containing 1/4, via flint's independent modular implementations.
"""
from __future__ import annotations

from flint import acb, arb, ctx

__all__ = ["elliptic_periods", "algebraic_j"]


def _reject_float(value, name: str) -> None:
    if isinstance(value, float):
        raise TypeError(f"{name}: float64 leakage refused")


def algebraic_j(lam_str: str) -> arb:
    """Closed-form j for Legendre curves y^2 = x(x-1)(x-lam)."""
    _reject_float(lam_str, "lam_str")
    lam = arb(str(lam_str))
    return arb(256) * (lam**2 - lam + 1) ** 3 / (lam**2 * (lam - 1) ** 2)


def elliptic_periods(
    e1_str: str, e2_str: str, e3_str: str, prec_bits: int = 256
) -> dict:
    """Enclose (w1, w2, tau) for strictly ordered real branch points."""
    for name, val in (
        ("e1_str", e1_str),
        ("e2_str", e2_str),
        ("e3_str", e3_str),
    ):
        _reject_float(val, name)
    if isinstance(prec_bits, float):
        raise TypeError("prec_bits: float64 leakage refused")
    ctx.prec = int(prec_bits)
    e1, e2, e3 = arb(str(e1_str)), arb(str(e2_str)), arb(str(e3_str))
    if not bool(e1 > e2) or not bool(e2 > e3):
        raise ValueError("branch points must be strictly ordered e1 > e2 > e3")
    a0 = (e1 - e3).sqrt()
    b0 = (e1 - e2).sqrt()
    c0 = (e2 - e3).sqrt()
    m1 = a0.agm(b0)
    m2 = a0.agm(c0)
    w1 = acb.pi() / m1
    w2 = acb(0, 1) * acb.pi() / m2
    tau = w2 / w1
    return {
        "omega1": w1,
        "omega2": w2,
        "tau": tau,
        "j_of_tau": tau.modular_j(),
        "lambda_of_tau": tau.modular_lambda(),
    }


