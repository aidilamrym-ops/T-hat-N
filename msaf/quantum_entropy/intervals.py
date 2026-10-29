"""Interval-domain policy helpers for Campaign V2 (import-light).

All numeric objects in this campaign are intervals (balls). This module owns
the parts that need no heavy numeric import, so that ``--seed`` refusal (K-Q1)
and the freeze tooling can run before any precision-heavy machinery loads:

* exact decimal parsing (``Fraction``; no float path anywhere);
* symmetric Minkowski widening (landmine L39) as a policy function;
* the resolution-policy exceptions (alarm / refusal / label checks).

The arithmetic engines live in ``engines.py`` (Engine A: Arb, 6000 bits;
Engine B: mpmath, dps 50 with directed rounding).
"""

from __future__ import annotations

from fractions import Fraction

__all__ = [
    "EntropyLabelMismatch",
    "ResolutionAlarm",
    "SeedRefused",
    "parse_decimal",
    "relative_width",
    "widen",
]


class ResolutionAlarm(RuntimeError):
    """Raised when an enclosure fails the frozen resolution-floor policy."""


class SeedRefused(SystemExit):
    """Raised on any ``--seed`` occurrence (K-Q1). Exit code 2."""


class EntropyLabelMismatch(RuntimeError):
    """Raised when an artifact is missing the SIMULATED label (D1)."""


def parse_decimal(text: str) -> Fraction:
    """Exact decimal-string -> Fraction. ``float`` never touches this path."""
    return Fraction(str(text))


def widen(lo: Fraction, hi: Fraction, radius: Fraction) -> tuple[Fraction, Fraction]:
    """Symmetric Minkowski widening (L39): [lo - r, hi + r], r = envelope."""
    if radius < 0:
        raise ValueError("widening radius must be >= 0")
    return lo - radius, hi + radius


def relative_width(lo: Fraction, hi: Fraction) -> Fraction:
    """Relative width of a rational interval; raises if it straddles zero."""
    mid = (lo + hi) / 2
    if mid == 0:
        if lo == hi:
            return Fraction(0)
        raise ResolutionAlarm("relative width undefined: interval straddles 0")
    return (hi - lo) / abs(mid)


