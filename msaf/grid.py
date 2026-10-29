"""Finite information grid: quantisation of N_steps and its arithmetic fallout.

N_steps is not an integer. Modular arithmetic of the form T^N = 1 requires an
integer exponent, so the value must be floored before use. This module records
that consequence explicitly instead of rounding silently.

Arithmetic note: `fmpq` rejects scientific notation, so decimal strings are
decomposed and carried as exact integer ratios. No `float` ever participates.
"""

from __future__ import annotations

import re
from typing import Final, NamedTuple

from flint import arb, fmpq, fmpz

from .constants import N_STEPS

__all__ = [
    "GridSpec",
    "SPEC",
    "decimal_to_fmpq",
    "n_steps_exact_rational_parts",
    "n_steps_exact_rational",
    "n_steps_ball",
    "n_steps_floor",
    "n_steps_exact_integer",
    "n_steps_bit_length",
    "storage_bytes_lower_bound",
]

_DECIMAL = re.compile(
    r"^(?P<sign>-?)(?P<int>\d+)(?:\.(?P<frac>\d+))?[eE](?P<exp>[+-]?\d+)$"
)


class GridSpec(NamedTuple):
    """Audited, already-rounded summary of the grid quantities."""

    ball: arb            #: N_steps as a ball; never an integer
    is_integer: bool     #: False for every measured range of D_obs / l_P
    n_floor: fmpz        #: floor(N_steps), the exponent of the modulus T^N = I
    bit_length: int      #: log2(N_steps), rounded up
    storage_bytes: fmpz  #: one bit per pixel is the absolute lower bound


def _decimal_to_ratio(text: str) -> tuple[int, int]:
    """Convert scientific decimal notation to an exact integer ratio.

    Decomposition by string plus exact power of ten. No floating point
    intermediate is constructed at any point.
    """
    match = _DECIMAL.match(text)
    if match is None:
        raise ValueError(f"not a scientific decimal literal: {text!r}")
    digits = match["int"] + (match["frac"] or "")
    exponent = int(match["exp"]) - len(match["frac"] or "")
    sign = -1 if match["sign"] else 1
    magnitude = int(digits)
    if exponent >= 0:
        return sign * magnitude * 10**exponent, 1
    return sign * magnitude, 10**(-exponent)


def decimal_to_fmpq(text: str) -> fmpq:
    """Convert scientific decimal notation to `fmpq` exactly."""
    numerator, denominator = _decimal_to_ratio(text)
    return fmpq(fmpz(numerator), fmpz(denominator))


def n_steps_exact_rational_parts() -> tuple[int, int]:
    """N_steps as an exact (numerator, denominator) integer pair.

    Python integer arithmetic is exact and never crosses the floating point
    path, so it is safe as the grid's source of truth.
    """
    top = _decimal_to_ratio("8.8e26")
    bottom = _decimal_to_ratio("1.616255e-35")
    return top[0] * bottom[1], top[1] * bottom[0]


def n_steps_exact_rational() -> fmpq:
    """N_steps as an exact rational, from the central values of the constants."""
    numerator, denominator = n_steps_exact_rational_parts()
    return fmpq(fmpz(numerator), fmpz(denominator))


def n_steps_ball() -> arb:
    return N_STEPS


def n_steps_floor() -> fmpz:
    """floor(N_steps) as an exact integer.

    Computed from exact rational arithmetic rather than `arb.floor()`: an Arb
    ball around a non-integer value can never be converted to `fmpz` exactly.
    """
    numerator, denominator = n_steps_exact_rational_parts()
    return fmpz(numerator // denominator)


def n_steps_exact_integer() -> bool:
    return bool(N_STEPS.is_integer())


def n_steps_bit_length() -> int:
    """Bit length of floor(N_steps), from exact integer arithmetic."""
    numerator, denominator = n_steps_exact_rational_parts()
    return (numerator // denominator).bit_length()


def storage_bytes_lower_bound(n: fmpz) -> fmpz:
    """Storage lower bound for n bits, in bytes, rounded up."""
    return (n + 7) // 8


def build_spec() -> GridSpec:
    n = n_steps_floor()
    return GridSpec(
        ball=N_STEPS,
        is_integer=n_steps_exact_integer(),
        n_floor=n,
        bit_length=n_steps_bit_length(),
        storage_bytes=storage_bytes_lower_bound(n),
    )


SPEC: Final[GridSpec] = build_spec()

