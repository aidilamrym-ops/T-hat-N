"""Giant Conductor Dirichlet L-Functions runtime engine.

This module carries two layers:

1. the original q=1000 Hardy-Z bracket engine, now restricted to **real**
   characters (Hardy Z is complex for a complex character, so a real sign
   change is meaningless there);
2. a conductor sweep that audits exact Dirichlet coefficients over primitive
   and imprimitive characters.

The sweep is an arithmetic audit, not an L-function theorem. For every
admitted (real) character and every tested ``n`` it enforces

    chi(n) in {-1, 0, +1}                         (exact fmpz)
    chi(n) = 0  <=>  gcd(n, q) > 1                (structural-zero gate)

and transports the resulting exact block into
:class:`~msaf.chrono_runtime.laurent_bridge_operator.LaurentLogicBridgeEngine`.
Complex characters (order > 2) are reported as rejected; they are never
rounded or coerced into integers.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from math import gcd
from pathlib import Path
from typing import Any, Iterable

from flint import acb, arb, ctx, dirichlet_char, fmpq, fmpz

from msaf.chrono_runtime.laurent_bridge_operator import (
    LaurentLogicBridgeEngine,
    StructuralIntegrityViolation,
)
from msaf.dirichlet import strict_sign

ADMISSIBLE_INTEGER_VALUES: frozenset[int] = frozenset({-1, 0, 1})

# Frozen sweep described in
# reports/PREREG_CHRONO_MULTI_TRACK_2026-11-01.md.
DEFAULT_SWEEP_MODULI: tuple[int, ...] = tuple(range(1, 61)) + (
    72, 84, 120, 180, 210, 360, 420, 840, 1000,
)
DEFAULT_MAX_N: int = 128


def _divisors(n: int) -> list[int]:
    divs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def _unit_numbers(modulus: int) -> list[int]:
    """Character labels for one modulus: the units modulo q, found exactly."""
    if modulus < 1:
        raise ValueError(f"modulus must be >= 1, got {modulus!r}")
    return [n for n in range(1, modulus + 1) if gcd(n, modulus) == 1]


def first_real_character(modulus: int, *, non_principal: bool = True) -> int:
    """Smallest valid character number that is real (order <= 2)."""
    for number in _unit_numbers(modulus):
        chi = dirichlet_char(modulus, number)
        if chi.is_real() and (not non_principal or int(chi.order()) > 1):
            return number
    kind = "non-principal real" if non_principal else "real"
    raise ValueError(f"modulus {modulus} has no {kind} character")


def lift_to_primitive(modulus: int, number: int) -> tuple[int, int]:
    """Lift character chi mod q to primitive chi* mod f using exact FLINT structures."""
    chi_q = dirichlet_char(modulus, number)
    cond = int(chi_q.conductor())
    if chi_q.is_primitive():
        return cond, number

    for f in _divisors(modulus):
        if modulus % f != 0:
            continue
        for num_f in range(1, f + 1):
            try:
                chi_f = dirichlet_char(f, num_f)
                if not chi_f.is_primitive():
                    continue
                return f, num_f
            except Exception:
                continue
    return cond, number


class GiantDirichletEngine:
    """Evaluate one Dirichlet character and, for real characters, Hardy Z.

    The original engine accepted any character. Hardy Z of a complex
    character is complex-valued, so this class now refuses to bracket a
    complex character instead of reading a meaningless real sign from it.
    """

    def __init__(self, modulus: int = 1000, number: int = 3, prec: int = 512) -> None:
        ctx.prec = prec
        self.modulus = modulus
        self.number = number
        self.chi = dirichlet_char(modulus, number)
        self.conductor = int(self.chi.conductor())

    def evaluate_values(self, max_n: int = 2000) -> list[int]:
        """Exact integer values for a real character; complex is refused."""
        if not self.chi.is_real():
            raise ValueError(
                f"chi_{self.modulus}_{self.number} has order "
                f"{int(self.chi.order())}: coefficients are not integers"
            )
        values: list[int] = []
        for n in range(1, max_n + 1):
            z = self.chi(n)
            if not z.imag.is_zero() or not z.real.is_exact():
                raise StructuralIntegrityViolation(
                    f"chi_{self.modulus}_{self.number}({n}) is not an exact "
                    "real integer"
                )
            values.append(int(z.real.fmpz()))
        return values

    def bracket_hardy(
        self,
        t_start: float = 10.0,
        t_end: float = 50.0,
        step: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Certified Hardy-Z sign-change brackets. Real characters only.

        A bracket proves an ODD number of zeros inside. It is not a
        localisation and says nothing about zeros off the critical line.
        """
        if not self.chi.is_real():
            raise ValueError(
                f"chi_{self.modulus}_{self.number} has order "
                f"{int(self.chi.order())}: Hardy Z is complex, so real sign "
                "changes cannot be read"
            )
        if not self.chi.is_primitive():
            raise ValueError(
                f"chi_{self.modulus}_{self.number} is imprimitive "
                f"(conductor {self.conductor}): FLINT Hardy Z requires a "
                "primitive character"
            )
        if step <= 0:
            raise ValueError(f"step must be positive, got {step!r}")

        brackets: list[dict[str, Any]] = []
        t = arb(t_start)
        t_max = arb(t_end)
        dt = arb(step)

        prev_z = self.chi.hardy_z(acb(t))
        prev_s = strict_sign(prev_z)
        curr_t = t + dt

        while curr_t <= t_max:
            z = self.chi.hardy_z(acb(curr_t))
            s = strict_sign(z)
            if prev_s != 0 and s != 0 and prev_s != s:
                brackets.append(
                    {
                        "t_low": float(curr_t - dt),
                        "t_high": float(curr_t),
                        "certified": True,
                    }
                )
            prev_z = z
            prev_s = s
            curr_t = curr_t + dt
        return brackets


def _exact_real_value(chi: Any, modulus: int, n: int) -> fmpz:
    """Extract one exact integer value and enforce both frozen gates."""
    z = chi(n)
    if not z.imag.is_zero():
        raise StructuralIntegrityViolation(
            f"chi_{modulus}_{chi.number()}({n}) has a non-zero imaginary part"
        )
    if not z.real.is_exact():
        raise StructuralIntegrityViolation(
            f"chi_{modulus}_{chi.number()}({n}) is an inexact ball"
        )
    value = z.real.fmpz()
    if int(value) not in ADMISSIBLE_INTEGER_VALUES:
        raise StructuralIntegrityViolation(
            f"chi_{modulus}_{chi.number()}({n}) = {value} is outside "
            "{-1, 0, +1}"
        )
    expected_zero = gcd(n, modulus) > 1
    if (int(value) == 0) != expected_zero:
        raise StructuralIntegrityViolation(
            f"structural-zero gate failed at q={modulus}, n={n}: "
            f"chi(n)={value}, gcd(n,q)>1={expected_zero}"
        )
    return value


def _character_block(chi: Any, modulus: int, max_n: int) -> tuple[fmpz, ...]:
    return tuple(_exact_real_value(chi, modulus, n) for n in range(1, max_n + 1))


def _coefficient_digest(block: Iterable[fmpz]) -> str:
    payload = json.dumps([int(value) for value in block],
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _transport_to_bridge(block: tuple[fmpz, ...]) -> dict[str, Any]:
    """Feed one exact fmpz block to the active Laurent bridge engine."""
    engine = LaurentLogicBridgeEngine(list(block), p=1)
    result = engine.enclose_residues()
    return {
        "bridge_residue": str(result["residue"]),
        "bridge_status": str(result["status"]),
        "bridge_coefficient_count": len(engine.coefficients),
    }


@dataclass(frozen=True)
class CharacterCoefficientAudit:
    """One character's exact-coefficient audit record (JSON-safe)."""

    modulus: int
    number: int
    conductor: int
    primitive: bool
    order: int
    parity: int
    real: bool
    admitted: bool
    structural_zero_gate: bool | None
    exact_integer_gate: bool | None
    coefficients: tuple[int, ...] | None
    coefficient_sha256: str | None
    bridge_residue: str | None
    bridge_status: str | None
    rejection_reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "modulus": self.modulus,
            "number": self.number,
            "conductor": self.conductor,
            "primitive": self.primitive,
            "order": self.order,
            "parity": self.parity,
            "real": self.real,
            "admitted": self.admitted,
            "structural_zero_gate": self.structural_zero_gate,
            "exact_integer_gate": self.exact_integer_gate,
            "coefficient_count": 0 if self.coefficients is None else len(self.coefficients),
            "coefficients": None if self.coefficients is None else list(self.coefficients),
            "coefficient_sha256": self.coefficient_sha256,
            "bridge_residue": self.bridge_residue,
            "bridge_status": self.bridge_status,
            "rejection_reason": self.rejection_reason,
        }


def audit_character(modulus: int, number: int, max_n: int = DEFAULT_MAX_N) -> CharacterCoefficientAudit:
    """Audit one character. Real -> exact block; complex -> rejected record."""
    if max_n < 1:
        raise ValueError(f"max_n must be >= 1, got {max_n!r}")
    chi = dirichlet_char(modulus, number)
    order = int(chi.order())
    real = bool(chi.is_real())
    base = {
        "modulus": int(modulus),
        "number": int(number),
        "conductor": int(chi.conductor()),
        "primitive": bool(chi.is_primitive()),
        "order": order,
        "parity": int(chi.parity()),
        "real": real,
    }

    if not real:
        return CharacterCoefficientAudit(
            **base,
            admitted=False,
            structural_zero_gate=None,
            exact_integer_gate=None,
            coefficients=None,
            coefficient_sha256=None,
            bridge_residue=None,
            bridge_status=None,
            rejection_reason=(
                f"complex character of order {order}: coefficients are roots "
                "of unity, not elements of {-1, 0, +1}; rejected, not coerced"
            ),
        )

    block = _character_block(chi, modulus, max_n)
    bridge = _transport_to_bridge(block)
    return CharacterCoefficientAudit(
        **base,
        admitted=True,
        structural_zero_gate=True,
        exact_integer_gate=True,
        coefficients=tuple(int(value) for value in block),
        coefficient_sha256=_coefficient_digest(block),
        bridge_residue=bridge["bridge_residue"],
        bridge_status=bridge["bridge_status"],
        rejection_reason=None,
    )


def sweep_modulus(modulus: int, max_n: int = DEFAULT_MAX_N) -> dict[str, Any]:
    """Audit every valid character of one modulus (primitive and imprimitive)."""
    records = [
        audit_character(modulus, number, max_n).to_dict()
        for number in _unit_numbers(modulus)
    ]
    admitted = [record for record in records if record["admitted"]]
    real_records = [record for record in records if record["real"]]
    return {
        "modulus": int(modulus),
        "characters_total": len(records),
        "primitive_count": sum(1 for record in records if record["primitive"]),
        "imprimitive_count": sum(1 for record in records if not record["primitive"]),
        "real_count": len(real_records),
        "complex_count": sum(1 for record in records if not record["real"]),
        "primitive_real_count": sum(
            1 for record in real_records if record["primitive"]
        ),
        "imprimitive_real_count": sum(
            1 for record in real_records if not record["primitive"]
        ),
        "admitted_count": len(admitted),
        "rejected_count": len(records) - len(admitted),
        "coefficient_count_per_admitted": max_n,
        "characters": records,
    }


def sweep_conductors(
    moduli: Iterable[int] | None = None,
    max_n: int = DEFAULT_MAX_N,
) -> dict[str, Any]:
    """Run the frozen conductor sweep and return a JSON-safe audit report."""
    if max_n < 1:
        raise ValueError(f"max_n must be >= 1, got {max_n!r}")
    selected = tuple(DEFAULT_SWEEP_MODULI if moduli is None else moduli)
    if not selected:
        raise ValueError("at least one modulus is required")
    if any(modulus < 1 for modulus in selected):
        raise ValueError("every modulus must be >= 1")

    previous_precision = ctx.prec
    ctx.prec = max(previous_precision, 128)
    try:
        per_modulus = [sweep_modulus(modulus, max_n) for modulus in selected]

        all_records = [
            record
            for entry in per_modulus
            for record in entry["characters"]
        ]
        admitted = [record for record in all_records if record["admitted"]]
        blockers = [
            record
            for record in all_records
            if record["admitted"]
            and not (
                record["exact_integer_gate"]
                and record["structural_zero_gate"]
                and record["bridge_status"] == "CERTIFIED"
            )
        ]
        primitive_admitted = sum(1 for record in admitted if record["primitive"])
        imprimitive_admitted = sum(1 for record in admitted if not record["primitive"])
        primitive_real_total = sum(
            1 for record in all_records if record["real"] and record["primitive"]
        )
        imprimitive_real_total = sum(
            1 for record in all_records if record["real"] and not record["primitive"]
        )

        gates_pass = bool(admitted) and not blockers
        return {
            "schema": "msaf.dirichlet_conductor_sweep.v1",
            "date": "2026-11-01",
            "engine": "dirichlet_giant_q.sweep_conductors",
            "precision_bits": ctx.prec,
            "moduli": list(selected),
            "max_n": int(max_n),
            "modulus_count": len(selected),
            "characters_total": len(all_records),
            "primitive_total": sum(1 for record in all_records if record["primitive"]),
            "imprimitive_total": sum(1 for record in all_records if not record["primitive"]),
            "real_total": sum(1 for record in all_records if record["real"]),
            "complex_total": sum(1 for record in all_records if not record["real"]),
            "primitive_real_total": primitive_real_total,
            "imprimitive_real_total": imprimitive_real_total,
            "admitted_total": len(admitted),
            "primitive_admitted": primitive_admitted,
            "imprimitive_admitted": imprimitive_admitted,
            "rejected_total": len(all_records) - len(admitted),
            "coefficient_values_total": len(admitted) * int(max_n),
            "gate_blockers": [record["coefficient_sha256"] for record in blockers],
            "gates": {
                "exact_integer_gate": not blockers,
                "structural_zero_gate": not blockers,
                "complex_rejected_not_coerced": all(
                    record["coefficients"] is None
                    for record in all_records
                    if not record["real"]
                ),
                "bridge_transport_gate": not blockers,
            },
            "status": "CERTIFIED" if gates_pass else "FAILED",
            "scope_notice": {
                "rh_claim": False,
                "grh_claim": False,
                "weil_positivity_claim": False,
                "zero_location_claim": False,
                "l_function_global_claim": False,
                "meaning": (
                    "Exact algebraic coefficient audit for real characters. "
                    "No statement about L-function zeros, GRH, or RH."
                ),
            },
            "per_modulus": per_modulus,
        }
    finally:
        ctx.prec = previous_precision


def run_dirichlet_sweep(
    moduli: Iterable[int] | None = None,
    max_n: int = DEFAULT_MAX_N,
    receipt_path: str | Path = "reports/chrono_rh_dirichlet_sweep_2026-11-01.json",
) -> dict[str, Any]:
    """Execute the sweep and write its detailed JSON receipt (silent)."""
    report = sweep_conductors(moduli=moduli, max_n=max_n)
    target = Path(receipt_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def run_giant_analysis(
    modulus: int = 1000,
    number: int | None = None,
    t_start: float = 10.0,
    t_end: float = 50.0,
    step: float = 0.5,
    receipt_path: str | Path = "reports/GRH_GIANT_Q_BRACKET_REPORT.json",
) -> dict[str, Any]:
    """Legacy q=1000 bracket report, corrected to a real character.

    `number=None` selects the first non-principal real character. The report
    states the real-character restriction explicitly; it is a bracket
    certificate, never a zero localisation and never a GRH/RH claim.
    """
    selected = first_real_character(modulus) if number is None else int(number)
    engine = GiantDirichletEngine(modulus, selected, prec=512)

    if not engine.chi.is_real():
        brackets: list[dict[str, Any]] = []
        status = "REJECTED_COMPLEX_CHARACTER"
        status_reason = (
            "Hardy Z of a complex character is complex; real sign changes "
            "are meaningless. The character is rejected, not coerced."
        )
    elif not engine.chi.is_primitive():
        brackets = []
        status = "UNAVAILABLE_NON_PRIMITIVE"
        status_reason = (
            f"chi has conductor {engine.conductor} < modulus {modulus}; "
            "FLINT Hardy Z requires a primitive character. No bracket is "
            "manufactured."
        )
    else:
        brackets = engine.bracket_hardy(t_start, t_end, step)
        status = "CERTIFIED" if brackets else "NO_BRACKETS"
        status_reason = None

    report = {
        "schema": "msaf.dirichlet_giant_bracket.v2",
        "date": "2026-11-01",
        "modulus": int(modulus),
        "number": int(selected),
        "conductor": engine.conductor,
        "primitive": bool(engine.chi.is_primitive()),
        "order": int(engine.chi.order()),
        "character_is_real": bool(engine.chi.is_real()),
        "precision_bits": ctx.prec,
        "search_range": [float(t_start), float(t_end)],
        "step": float(step),
        "brackets": brackets,
        "bracket_count": len(brackets),
        "status_reason": status_reason,
        "claim": (
            "each bracket contains an ODD number of critical-line zeros of a "
            "REAL PRIMITIVE character; not a localisation; says nothing about "
            "zeros off the critical line"
        ),
        "status": status,
        "scope_notice": {
            "rh_claim": False,
            "grh_claim": False,
            "zero_location_claim": False,
        },
    }
    out_path = Path(receipt_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    run_dirichlet_sweep()
    run_giant_analysis()
