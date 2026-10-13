"""Dirichlet L-function campaign: primitive real characters and Hardy Z bracketing.

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

* Only real PRIMITIVE characters (`order() <= 2` and `is_primitive()`) are
  admitted into `DirichletCharacter`. Anything else raises `ValueError`,
  because a complex character has no valid sign ordering for Hardy Z.
* Every enclosure is symmetrically widened (`enc +/- tail`, Minkowski sum)
  before any decision is read from it, so a one-sided radius accounting
  upstream can never silently decide a sign (cf. landmine L33).
* Any enclosure whose real part touches or straddles zero raises
  `RuntimeError` at the point of measurement. An undetermined measurement is
  a failed transaction, never a rounded one. Grid sweeps catch this failure
  per point and record the gap without manufacturing a claim.
* The kernel uses Arb/Acb balls exclusively. No `float`, no `numpy`, no
  `matplotlib`, no `math` anywhere in this file.
"""

from __future__ import annotations

from typing import NamedTuple

from flint import acb, arb, ctx, dirichlet_char

__all__ = [
    "CharacterSpec",
    "DirichletCharacter",
    "RigorousLFunction",
    "ZeroBracket",
    "BracketLevel",
    "multiresolution_bracket_report",
    "write_bracket_report",
    "enumerate_characters",
    "primitive_characters",
    "describe",
    "hardy_enclosure",
    "strict_sign",
    "isolate_sign_changes",
    "working_precision",
]


def working_precision() -> int:
    """Active Arb precision in bits. Reported so every verdict is reproducible."""
    return ctx.prec


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


def _coprime(a: int, b: int) -> bool:
    """Exact Euclidean test, in pure Python integers. No library needed."""
    while b:
        a, b = b, a % b
    return a == 1


def _valid_numbers(modulus: int) -> list[int]:
    """Candidate character numbers: the units modulo q, found by trial.

    The binding raises AssertionError for invalid numbers. Only units
    (gcd(n, q) == 1) are attempted, which matches every observed success, and
    any residual failure is skipped rather than asserted.
    """
    return [n for n in range(1, modulus) if _coprime(n, modulus)]


def character(modulus: int, number: int):
    """Build the raw FLINT character. Raises AssertionError for bad numbers."""
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


class DirichletCharacter:
    """A real primitive Dirichlet character admitted to the campaign.

    The constructor is the gate. A character is admitted if and only if it is
    primitive with order at most 2 (real-valued: principal or quadratic).
    Complex characters are refused with `ValueError` because their Hardy
    function is complex-valued and admits no sign ordering; imprimitive
    characters are refused because their zeros duplicate a smaller conductor;
    invalid numbers are normalised from the binding's AssertionError into the
    same `ValueError` so callers face exactly one failure type.
    """

    __slots__ = ("_chi", "_spec")

    def __init__(self, modulus: int, number: int) -> None:
        try:
            chi = character(int(modulus), int(number))
        except AssertionError as exc:
            raise ValueError(
                f"({modulus}, {number}) is not a valid Dirichlet character"
            ) from exc
        spec = CharacterSpec(
            modulus=int(modulus),
            number=int(number),
            conductor=int(chi.conductor()),
            primitive=bool(chi.is_primitive()),
            parity=int(chi.parity()),
            order=int(chi.order()),
        )
        if not spec.primitive:
            raise ValueError(
                f"{spec.identifier()} is imprimitive (conductor {spec.conductor}); "
                "its zeros duplicate a smaller conductor"
            )
        if not spec.is_real:
            raise ValueError(
                f"{spec.identifier()} has order {spec.order}: complex characters "
                "have no valid sign ordering for Hardy Z"
            )
        self._chi = chi
        self._spec = spec

    @property
    def spec(self) -> CharacterSpec:
        return self._spec

    def hardy_raw(self, t: arb) -> acb:
        """Raw Hardy Z enclosure over an ordinate ball. No decision attached."""
        return self._chi.hardy_z(acb(t))

    def l_raw(self, s: acb) -> acb:
        """Raw Dirichlet L enclosure over a complex ball. No decision attached."""
        return self._chi.l(s)

    def __repr__(self) -> str:
        return f"DirichletCharacter({self._spec.identifier()})"


def _symmetric_pad(radius: arb) -> acb:
    """The symmetric interval [-r, +r] as an Acb ball for Minkowski widening."""
    return acb(radius).union(-acb(radius))


def _component_radius_upper(z: acb) -> arb:
    """Real upper bound on the componentwise radius of an Acb enclosure."""
    return max(z.real.rad().abs_upper(), z.imag.rad().abs_upper())


class StraddlingEnclosure(RuntimeError):
    """An enclosure touches or straddles zero: no sign is measurable.

    Raised at the point of measurement so that an undetermined quantity can
    never be silently rounded into a claim downstream.
    """


class RigorousLFunction:
    """Rigorous evaluation layer over one admitted `DirichletCharacter`.

    Every evaluation returns an enclosure widened symmetrically by its own
    reported radius (`enc +/- tail`, Minkowski sum). The widening is
    containment-preserving by construction: it can only grow the enclosure,
    never shrink it, so no sign decision can be manufactured by a one-sided
    radius accounting upstream (landmine L33 applied as architecture).

    Any enclosure whose real part contains zero raises `StraddlingEnclosure`
    (a `RuntimeError`): the transaction fails loudly at the measurement point
    instead of rounding silently into a verdict.
    """

    __slots__ = ("character",)

    def __init__(self, character: DirichletCharacter) -> None:
        self.character = character

    def remainder_tail(self, value: acb) -> arb:
        """The Euler-Maclaurin remainder as reported: the enclosure radius.

    FLINT evaluates L and Z by Euler-Maclaurin summation internally; the
    radius it reports IS the rigorous remainder of that summation. This
    accessor names it explicitly instead of letting it hide inside the value,
    so the widening below is auditable rather than implicit.
    """
        return _component_radius_upper(value)

    def widen(self, value: acb) -> acb:
        """Symmetric Minkowski widening: `value +/- tail`. Never narrows."""
        return value + _symmetric_pad(self.remainder_tail(value))

    def hardy(self, t: arb) -> acb:
        """Widened Hardy Z enclosure over an ordinate ball. Raises on straddle."""
        widened = self.widen(self.character.hardy_raw(t))
        if not widened.imag.contains(arb(0)):
            raise StraddlingEnclosure(
                f"{self.character.spec.identifier()}: Hardy Z carries a "
                f"non-negligible imaginary part at t = {t.mid().str(12)}; "
                "a real sign cannot be read"
            )
        if widened.real.contains(arb(0)):
            raise StraddlingEnclosure(
                f"{self.character.spec.identifier()}: Hardy Z enclosure straddles "
                f"zero at t = {t.mid().str(12)}; no sign is measurable"
            )
        return widened

    def certified_sign(self, t: arb) -> int:
        """Certified sign of Z(t): +1 or -1. Anything else raises."""
        return 1 if self.hardy(t).real.lower() > 0 else -1

    def l_surface(self, s: acb) -> acb:
        """Widened Dirichlet L enclosure over a complex ball. Raises on straddle."""
        widened = self.widen(self.character.l_raw(s))
        if widened.real.contains(arb(0)):
            raise StraddlingEnclosure(
                f"{self.character.spec.identifier()}: L-surface real part straddles "
                "zero; the evaluation is undetermined, not zero"
            )
        return widened


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
    This is the non-raising convenience form; `RigorousLFunction` is the
    raising form. Both agree on every strictly signed input.
    """
    real, imag = z.real, z.imag
    if real.lower() > 0 and imag.contains(arb(0)):
        return 1
    if real.upper() < 0 and imag.contains(arb(0)):
        return -1
    return 0


class ZeroBracket(NamedTuple):
    """A certified sign-change interval for a real character.

    A bracket proves an ODD number of zeros inside, never exactly one, and
    nothing about zeros off the critical line. The `claim` field carries that
    boundary in the data itself so no downstream consumer can silently upgrade
    a bracket into a localisation.
    """

    character_id: str
    lower: arb
    upper: arb
    claim: str = "odd number of zeros inside; not a localisation"

    def width(self) -> arb:
        return self.upper - self.lower

    def render(self) -> str:
        return (
            f"{self.character_id}: zero bracketed in "
            f"({self.lower.mid().str(12, radius=False)}, "
            f"{self.upper.mid().str(12, radius=False)})"
        )


def isolate_sign_changes(
    spec: CharacterSpec, t_start: str, t_end: str, step: str, strict: bool = False
) -> list[ZeroBracket]:
    """Sweep Z(t) over a grid and collect every certified sign change.

    Real characters only; anything else raises `ValueError`. Each grid point
    is measured through `RigorousLFunction`, so a straddling enclosure raises
    `StraddlingEnclosure` at the point of measurement. The sweep catches that
    failure per point and records the gap by moving on WITHOUT manufacturing
    a claim; with `strict=True` the failure propagates instead. Either way a
    bracket requires two strictly signed endpoints of opposite sign, with no
    exceptions.
    """
    if not spec.is_real:
        raise ValueError(
            f"{spec.identifier()} has order {spec.order}: Z is complex and "
            "sign changes are meaningless"
        )
    kernel = RigorousLFunction(DirichletCharacter(spec.modulus, spec.number))
    start, end, delta = arb(t_start), arb(t_end), arb(step)
    if not (delta > 0):
        raise ValueError(f"step must be positive, got {step!r}")
    brackets: list[ZeroBracket] = []
    point = start
    previous_t, previous_sign = point, _measured_sign(kernel, point, strict)
    while point < end:
        point = point + delta
        if point > end:
            point = end
        sign = _measured_sign(kernel, point, strict)
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


def _measured_sign(
    kernel: RigorousLFunction, point: arb, strict: bool
) -> int:
    """Measure one grid point: +1, -1, or 0 for a failed (straddling) point.

    The 0 is a recorded gap, never a rounded verdict. In strict mode the
    underlying `StraddlingEnclosure` propagates to the caller.
    """
    try:
        return kernel.certified_sign(point)
    except StraddlingEnclosure:
        if strict:
            raise
        return 0


class BracketLevel(NamedTuple):
    """One resolution level of a multi-resolution bracketing dossier."""

    step: str
    bracket: ZeroBracket
    lower_value: str
    lower_radius: str
    lower_sign: int
    upper_value: str
    upper_radius: str
    upper_sign: int

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "lower": self.bracket.lower.mid().str(30, radius=False),
            "upper": self.bracket.upper.mid().str(30, radius=False),
            "lower_z_mid": self.lower_value,
            "lower_z_radius": self.lower_radius,
            "lower_sign": self.lower_sign,
            "upper_z_mid": self.upper_value,
            "upper_z_radius": self.upper_radius,
            "upper_sign": self.upper_sign,
            "width": self.bracket.width().mid().str(12, radius=False),
        }


def multiresolution_bracket_report(
    modulus: int, number: int, t_start: str, t_end: str, steps: list[str]
) -> dict:
    """Narrow a sign-change bracket through successive grid refinements.

    Each level sweeps the CURRENT bracket with a finer step and keeps its
    first certified sign change, so levels nest rigorously: every level's
    interval is contained in the previous one. A level that yields no bracket
    aborts the dossier with `RuntimeError` instead of inventing coordinates.

    The returned mapping contains decimal strings only: midpoints, radii,
    signs, verdicts and method notes. No float ever participates, on any path.
    """
    admitted = DirichletCharacter(modulus, number)
    kernel = RigorousLFunction(admitted)
    spec = admitted.spec
    levels: list[BracketLevel] = []
    lower, upper = arb(t_start), arb(t_end)
    for step in steps:
        found = isolate_sign_changes(
            spec,
            lower.mid().str(30, radius=False),
            upper.mid().str(30, radius=False),
            step,
        )
        if not found:
            raise RuntimeError(
                f"{spec.identifier()}: refinement at step {step} lost the bracket; "
                "dossier aborted rather than extrapolated"
            )
        first = found[0]
        lower_z = kernel.hardy(first.lower)
        upper_z = kernel.hardy(first.upper)
        # Signs are measured from the widened enclosures, never assumed from
        # the previous level: a bracket may run either direction.
        lower_sign = 1 if lower_z.real.lower() > 0 else -1
        upper_sign = 1 if upper_z.real.lower() > 0 else -1
        if lower_sign == upper_sign:
            raise RuntimeError(
                f"{spec.identifier()}: bracket endpoints agree in sign at step "
                f"{step}; the sweep below is inconsistent, dossier aborted"
            )
        levels.append(
            BracketLevel(
                step=step,
                bracket=first,
                lower_value=lower_z.real.mid().str(30, radius=False),
                lower_radius=lower_z.real.rad().mid().str(12, radius=False),
                lower_sign=lower_sign,
                upper_value=upper_z.real.mid().str(30, radius=False),
                upper_radius=upper_z.real.rad().mid().str(12, radius=False),
                upper_sign=upper_sign,
            )
        )
        lower, upper = first.lower, first.upper
    return {
        "character": spec.identifier(),
        "modulus": spec.modulus,
        "number": spec.number,
        "conductor": spec.conductor,
        "primitive": spec.primitive,
        "parity": spec.parity,
        "order": spec.order,
        "search_range": [t_start, t_end],
        "method": "certified Hardy Z sign changes on exact decimal grids; "
                  "each level sweeps the previous bracket with a finer step",
        "claim": "each level brackets an ODD number of zeros; not a localisation; "
                 "says nothing about zeros off the critical line",
        "global_claim_supported": False,
        "working_precision_bits": working_precision(),
        "levels": [level.to_dict() for level in levels],
    }


def write_bracket_report(path, dossier: dict):
    """Serialise a bracketing dossier as indented JSON. Strings only."""
    import json
    from pathlib import Path as _Path

    target = _Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(dossier, indent=2), encoding="utf-8")
    return target
