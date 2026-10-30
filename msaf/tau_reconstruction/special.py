"""Special functions with Arb enclosure for Guinand-Weil matrix."""

from __future__ import annotations

from flint import acb, arb, ctx

__all__ = [
    "digamma_arb",
    "trigamma_arb",
    "sinc_arb",
    "set_precision",
]

def set_precision(bits: int) -> None:
    """Set the global Arb precision."""
    ctx.prec = bits


def digamma_arb(z: acb) -> acb:
    """
    Compute digamma function ψ(z) using Flint's acb.digamma().
    Returns an acb ball enclosure.
    """
    return z.digamma()


def trigamma_arb(z: acb) -> acb:
    """
    Compute trigamma function ψ₁(z) using Flint's acb.polygamma(1, z).
    Returns an acb ball enclosure.
    """
    return z.polygamma(1)


def sinc_arb(x: arb) -> arb:
    """
    Compute sin(x)/x with proper limit at x=0.
    Returns an arb ball enclosure.
    """
    if x == 0:
        return arb(1)
    return x.sin() / x