"""Ball rendering with an explicit, locked digit count.

Note: `arb.str(n)` prints only digits that are guaranteed correct. For a wide
ball the output automatically shrinks to a single significant digit. That is
epistemically correct behaviour, so the audit report additionally prints the
midpoint on its own, letting the reader still see the nominal value of a
constant without the report ever claiming a precision it does not have.
"""

from __future__ import annotations

from flint import arb

__all__ = ["DEFAULT_DIGITS", "fmt", "point", "relwidth"]

DEFAULT_DIGITS = 40


def fmt(x: arb, digits: int = DEFAULT_DIGITS) -> str:
    """Full ball with radius, restricted to digits that are guaranteed correct."""
    return x.str(digits, radius=True)


def point(x: arb, digits: int = 24) -> str:
    """Ball midpoint with no radius claim, for nominal constant values."""
    return x.mid().str(digits, radius=False)


def relwidth(x: arb, digits: int = 8) -> str:
    """Relative interval width of a ball, as a relative uncertainty measure."""
    if x.mid().is_zero():
        return "0"
    return ((x.upper() - x.lower()) / x.mid()).str(digits, radius=True)