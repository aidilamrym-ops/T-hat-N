"""Dirichlet L-function campaign: primitive characters and Hardy Z bracketing.

Scope, stated before any claim. FLINT exposes three operations on Dirichlet
characters: enumeration via `dirichlet_char(q, number)`, evaluation of
`L(chi, s)` on Acb balls, and the Hardy `Z(t)` function. It does NOT expose a
power-series expansion for L, so the Taylor-based rigorous Newton of
`msaf.zeta_inversion` has no analogue here. This module therefore does the one
thing the available API genuinely supports: bracketing zeros of REAL primitive
characters on the critical line through certified sign changes of Z.

For a real character chi, Z(t) is real-valued on the real line. When two
evaluations Z(a) and Z(b) are both strictly signed (their enclosures exclude
zero) and carry opposite signs, the interval (a, b) provably contains an ODD
number of zeros. That is weaker than localisation (it does not say exactly
one, and it says nothing about zeros off the line), and it is reported as
exactly that: a bracket, never a localisation.

Hard boundaries, all enforced in code, not in prose:

* isolation runs only on real characters (`order() <= 2`); complex characters
  have complex Z, where "sign change" is meaningless;
* a grid point whose Z enclosure straddles zero contributes NO claim: the
  scan moves on rather than guessing;
* ordinates enter as decimal strings; the float round-trip landmine (L24)
  applies unchanged.
"""

from __future__ import annotations

from math import gcd
from typing import NamedTuple

from flint import acb, arb, dirichlet_char

__all__ = [
    "CharacterSpec",
    "enumerate_characters",
    "primitive_characters",
    "hardy_enclosure",
    "strict_sign",
    "ZeroBracket",
    "isolate_sign_changes",
]


class CharacterSpec(NamedTuple):
    """Pure data describing one Dirichlet character. No numerical claim."""

    modulus: int
    number: int
    conductor: int
    primitive: bool
    parity: int
    order: int

    def identifier(self) -> str:
        return f"chi_{self.modulus}_{self.number}"

    @property
    def is_real(self) -> bool:
        return self.order <= 2


def _valid_numbers(modulus: int) -> list[int]:
    """Candidate character numbers: the units modulo q, found by trial.

    The binding raises AssertionError for invalid numbers. Only units
    (gcd(n, q) == 1) are attempted, which matches every observed success, and
    any residual failure is skipped rather than asserted.
    """
    return [n for n in range(1, modulus) if gcd(n, modulus) == 1]


def character(modulus: int, number: int):
    """Build the FLINT character, or raise for an invalid number."""
    return dirichlet_char(modulus, number)


def describe(modulus: int, number: int) -> CharacterSpec:
    """Describe one character from live FLINT metadata (methods, not guesses)."""
    chi = character(modulus, number)
    return CharacterSpec(
        modulus=int(modulus),
        number=int(number),
        conductor=int(chi.conductor()),
        primitive=bool(chi.is_primitive()),
        parity=int(chi.parity()),
        order=int(chi.order()),
    )


def enumerate_characters(modulus_max: int) -> list[CharacterSpec]:
    """Enumerate every valid character with modulus up to `modulus_max`."""
    specs: list[CharacterSpec] = []
    for modulus in range(3, int(modulus_max) + 1):
        for number in _valid_numbers(modulus):
            try:
                specs.append(describe(modulus, number))
            except AssertionError:
                continue
    return specs


def primitive_characters(modulus_max: int) -> list[CharacterSpec]:
    """The primitive characters only: the campaign's working set."""
    return [s for s in enumerate_characters(modulus_max) if s.primitive]


def hardy_enclosure(spec: CharacterSpec, t: arb) -> acb:
    """Enclose Z(t) for a character over an ordinate ball.

    `t` must be an Arb ball built from a decimal string. The evaluation stays
    inside Acb for the whole call.
    """
    return character(spec.modulus, spec.number).hardy_z(acb(t))


def strict_sign(z: acb) -> int:
    """Certified sign of a real enclosure: +1, -1, or 0 when undetermined.

    Zero is returned whenever the enclosure straddles zero OR carries a
    non-trivial imaginary part. An undetermined sign is data, not failure.
    """
    real, imag = z.real, z.imag
    if real.lower() > 0 and imag.contains(arb(0)):
        return 1
    if real.upper() < 0 and imag.contains(arb(0)):
        return -1
    return 0


class ZeroBracket(NamedTuple):
    """A certified sign-change interval for a real character."""

    character_id: str
    lower: arb
    upper: arb

    def width(self) -> arb:
        return self.upper - self.lower

    def render(self) -> str:
        return (
            f"{self.character_id}: zero bracketed in "
            f"({self.lower.mid().str(12, radius=False)}, "
            f"{self.upper.mid().str(12, radius=False)})"
        )


def isolate_sign_changes(
    spec: CharacterSpec, t_start: str, t_end: str, step: str
) -> list[ZeroBracket]:
    """Sweep Z(t) over a grid and collect every certified sign change.

    Real characters only; anything else raises. Grid points with undetermined
    sign are skipped silently: a bracket requires two strictly signed
    endpoints of opposite sign, with no exceptions.
    """
    if not spec.is_real:
        raise ValueError(
            f"{spec.identifier()} has order {spec.order}: Z is complex and "
            "sign changes are meaningless"
        )
    chi = character(spec.modulus, spec.number)
    start, end, delta = arb(t_start), arb(t_end), arb(step)
    if not (delta > 0):
        raise ValueError(f"step must be positive, got {step!r}")
    brackets: list[ZeroBracket] = []
    point = start
    previous_t, previous_sign = point, strict_sign(chi.hardy_z(acb(point)))
    while point < end:
        point = point + delta
        if point > end:
            point = end
        sign = strict_sign(chi.hardy_z(acb(point)))
        if sign != 0 and previous_sign != 0 and sign != previous_sign:
            brackets.append(
                ZeroBracket(
                    character_id=spec.identifier(),
                    lower=previous_t,
                    upper=point,
                )
            )
        previous_t, previous_sign = point, sign
    return brackets
