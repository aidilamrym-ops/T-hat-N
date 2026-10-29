"""Precision budget: mantissa requirements and the critical collapse dimension.

Two calculation paths are provided and both must be reported, because they
differ by many orders of magnitude:

    MANUSCRIPT PATH : H(n) := n                       (a deliberately loose bound)
    MEASURED PATH   : H(n) := 0.5 + 0.5 log2(2(n-1))  (entropy of the real W_n)

The gap originates in the genuine spectrum of the Guinand-Weil family, not in
any algorithmic or numerical choice.
"""

from __future__ import annotations

from typing import NamedTuple

from flint import arb

from .constants import DECAY_A, DECAY_B, N_STEPS
from .precision import log2, log2_e

__all__ = [
    "manuscript_entropy",
    "measured_entropy",
    "mantissa_bits",
    "lambda_min_estimate",
    "underflow_dimension",
    "CriticalDimension",
    "manuscript_critical_dimension",
    "measured_critical_dimension",
]


def manuscript_entropy(n: arb) -> arb:
    """H := n, the assumption of manuscript section 3.3."""
    return n


def measured_entropy(n: arb) -> arb:
    """H := 0.5 + 0.5 log2(2(n-1)), the entropy of the measured W_n spectrum.

    For W_n one has p_0 = 1/2 and p_k = 1/(2(n-1)) for k > 0, hence
    H = 1/2 + 1/2 log2(2(n-1)).
    """
    return arb("0.5") + log2(2 * (n - 1)) / 2


def mantissa_bits(n: arb) -> arb:
    """b > -log2(lambda_min(n)) with lambda_min = A exp(-B n)."""
    return -log2(DECAY_A) + DECAY_B * n * log2_e()


def lambda_min_estimate(n: arb) -> arb:
    """The estimate lambda_min(n) = A exp(-B n), carried as an Arb ball."""
    return (DECAY_B * n).neg().exp() * DECAY_A


def underflow_dimension() -> arb:
    """The n at which |lambda_min(n)| reaches 1e-59, the quoted collapse threshold."""
    exponent = (arb(59) * arb(10).log()) / arb(2).log()
    return exponent / (DECAY_B * log2_e())


class CriticalDimension(NamedTuple):
    label: str
    value: arb

    def render(self) -> str:
        from .format import fmt

        return f"{self.label:<32} = {fmt(self.value)}"


def manuscript_critical_dimension() -> CriticalDimension:
    """Root of B log2(e) n^2 + n log2(1/A) - N_steps = 0.

    Solved analytically, with no numeric iteration whatsoever.
    """
    a = DECAY_B * log2_e()
    b = -log2(DECAY_A)
    c = N_STEPS.neg()
    disc = b * b - 4 * a * c
    return CriticalDimension("n_crit (H := n)", (-b + disc.sqrt()) / (2 * a))


def _budget_product(n: arb) -> arb:
    return measured_entropy(n) * mantissa_bits(n)


def measured_critical_dimension() -> CriticalDimension:
    """Root of H(n) * b(n) = N_steps with H taken from the measured W_n entropy.

    No longer a quadratic. Solved by bisection in n itself: both H and b are
    monotone increasing, so the function is monotone and a bracket always
    exists. Bisection is chosen over Newton because a ball Newton iteration
    can diverge, whereas bisection cannot.
    """
    target = N_STEPS
    low = arb(1)
    high = arb("1e70")
    for _ in range(700):
        mid = (low * high).sqrt()
        if _budget_product(mid) < target:
            low = mid
        else:
            high = mid
    return CriticalDimension("n_crit (H measured)", (low * high).sqrt())

