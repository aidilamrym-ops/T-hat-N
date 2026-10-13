"""Dirichlet sign-validity suite: gates, raising measurements, honest brackets.

Every test targets the campaign contract an external auditor would attack:
admission gates, loud failure on straddling enclosures, kernel purity, and
the bracket-vs-localisation distinction. Run with `python -m pytest msaf -q`.
"""

from __future__ import annotations

import sys
from pathlib import Path

from msaf.precision import DEFAULT_PRECISION_BITS, set_precision

set_precision(DEFAULT_PRECISION_BITS)

from flint import acb, arb  # noqa: E402

from msaf.dirichlet import (  # noqa: E402
    DirichletCharacter,
    RigorousLFunction,
    StraddlingEnclosure,
    ZeroBracket,
    describe,
    isolate_sign_changes,
    primitive_characters,
    strict_sign,
)


def test_complex_characters_are_rejected_absolutely() -> None:
    """A complex character has no sign ordering: admission must refuse it."""
    for modulus, number in ((5, 2), (5, 3), (7, 3)):
        try:
            DirichletCharacter(modulus, number)
        except ValueError:
            continue
        raise AssertionError(f"complex chi_{modulus}_{number} was admitted")


def test_imprimitive_characters_are_rejected() -> None:
    """Imprimitive zeros duplicate a smaller conductor: refused."""
    try:
        DirichletCharacter(4, 1)
    except ValueError:
        return
    raise AssertionError("imprimitive chi_4_1 was admitted")


def test_invalid_numbers_raise_value_error_not_assertion() -> None:
    """Callers face one failure type; the binding's AssertionError is normalised."""
    try:
        DirichletCharacter(4, 2)
    except ValueError:
        return
    raise AssertionError("invalid number (4, 2) was admitted")


def test_chi_4_and_chi_8_are_admitted() -> None:
    """The two real primitive workhorses of the campaign."""
    for modulus, number in ((4, 3), (8, 3), (8, 5), (3, 2)):
        character = DirichletCharacter(modulus, number)
        assert character.spec.primitive and character.spec.is_real


def test_certified_sign_matches_strict_sign_on_clean_points() -> None:
    """The raising and non-raising paths agree wherever a sign exists."""
    kernel = RigorousLFunction(DirichletCharacter(4, 3))
    assert kernel.certified_sign(arb("6.0")) == 1
    assert kernel.certified_sign(arb("6.2")) == -1
    assert strict_sign(kernel.hardy(arb("6.0"))) == 1


def test_straddling_enclosure_fails_loudly() -> None:
    """A ball spanning the zero must detonate, never round into a verdict."""
    kernel = RigorousLFunction(DirichletCharacter(4, 3))
    spanning = arb("6.0").union(arb("6.2"))
    try:
        kernel.hardy(spanning)
    except StraddlingEnclosure:
        pass
    else:
        raise AssertionError("straddling Hardy enclosure did not raise")
    assert issubclass(StraddlingEnclosure, RuntimeError)


def test_l_surface_straddle_fails_loudly() -> None:
    """The L-surface obeys the same rule: straddle means failed transaction."""
    kernel = RigorousLFunction(DirichletCharacter(4, 3))
    near_zero = acb(arb("0.5")) + acb(0, 1) * arb("6.0207").union(arb("6.0217"))
    try:
        kernel.l_surface(near_zero)
    except StraddlingEnclosure:
        return
    raise AssertionError("straddling L-surface did not raise")


def test_sweep_records_gaps_without_manufacturing_claims() -> None:
    """Undetermined grid points are recorded gaps; brackets still certify."""
    brackets = isolate_sign_changes(describe(4, 3), "5.5", "7.0", "0.1")
    assert brackets, "expected bracket vanished under the raising kernel"
    first = brackets[0]
    assert first.width() <= arb("0.1") + arb("1e-30")
    assert first.lower.upper() < arb("6.021") and first.upper.lower() > arb("6.020")


def test_strict_sweep_propagates_failure() -> None:
    """Strict mode converts a silent gap into a loud, attributable failure."""
    from msaf.dirichlet import DirichletCharacter, RigorousLFunction, _measured_sign

    kernel = RigorousLFunction(DirichletCharacter(4, 3))
    spanning = arb("6.0").union(arb("6.2"))
    assert _measured_sign(kernel, spanning, strict=False) == 0
    try:
        _measured_sign(kernel, spanning, strict=True)
    except StraddlingEnclosure:
        return
    raise AssertionError("strict measurement swallowed a straddling point")


def test_bracket_carries_its_epistemic_boundary() -> None:
    """A ZeroBracket can never be mistaken for a ZeroLocalization downstream."""
    bracket = ZeroBracket(character_id="chi_4_3", lower=arb("6.0"), upper=arb("6.1"))
    assert "odd" in bracket.claim
    assert "localisation" in bracket.claim
    assert "odd number of zeros" in bracket.claim
    assert not hasattr(bracket, "global_claim_supported")


def test_kernel_is_free_of_float_numpy_and_math() -> None:
    """External-auditor purity gate: no escape hatches in the kernel source."""
    import re

    source = Path(__file__).parent.parent.joinpath("dirichlet.py").read_text(
        encoding="utf-8"
    )
    # Prose mentions in docstrings are allowed; executable references are not.
    # Hence attribute-access and import forms, never bare words.
    for pattern in (
        r"^\s*(import|from)\s+(numpy|matplotlib|math)\b",
        r"\b(?:numpy|matplotlib|math)\.\w+",
        r"\bfloat\s*\(",
    ):
        assert not re.search(pattern, source, re.M), f"kernel contains {pattern}"


def test_primitive_enumeration_is_stable() -> None:
    """The working set to mod 8 is fixed data, not a moving target."""
    identifiers = [s.identifier() for s in primitive_characters(8)]
    assert "chi_4_3" in identifiers and "chi_8_3" in identifiers
    assert all(s.primitive for s in primitive_characters(8))


def test_multiresolution_dossier_nests_and_measures_signs() -> None:
    """Each refinement level re-measures; nesting and opposition are checked."""
    from msaf.dirichlet import multiresolution_bracket_report

    dossier = multiresolution_bracket_report(4, 3, "6.0", "6.1", ["0.01", "0.001"])
    assert dossier["global_claim_supported"] is False
    assert "odd" in dossier["claim"].lower() and "localisation" in dossier["claim"]
    levels = dossier["levels"]
    assert len(levels) == 2
    outer, inner = levels[0], levels[1]
    # Exact decimal comparison: ball-vs-ball <= is False on overlapping balls
    # (L14), so nesting is checked on the exact decimal strings themselves.
    from decimal import Decimal

    assert Decimal(outer["lower"]) <= Decimal(inner["lower"])
    assert Decimal(inner["upper"]) <= Decimal(outer["upper"])
    for level in levels:
        assert level["lower_sign"] != level["upper_sign"]
    assert outer["lower_sign"] == 1 and outer["upper_sign"] == -1


def test_dossier_serialises_strings_only() -> None:
    """An auditor must never have to guess a number's type."""
    import json

    from msaf.dirichlet import multiresolution_bracket_report

    dossier = multiresolution_bracket_report(4, 3, "6.0", "6.1", ["0.01"])

    def check(node) -> None:
        if isinstance(node, dict):
            for value in node.values():
                check(value)
        elif isinstance(node, list):
            for value in node:
                check(value)
        elif isinstance(node, bool):
            pass
        else:
            assert isinstance(node, (str, int)), f"non-string leaf: {node!r}"

    check(dossier)
    assert isinstance(dossier["levels"][0]["width"], str)


def main() -> int:
    failures = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"FAIL {name}: {type(exc).__name__}: {exc}")
        else:
            print(f"ok   {name}")
    print(f"\n{failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
