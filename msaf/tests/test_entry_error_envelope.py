"""Guard for the P1 entry-error envelope (pre-registered 2026-10-26).

The fast path verifies the recorded JSON only; it does not rebuild the
103041-entry Arb matrix.  The heavy builder is
``python -m msaf.entry_error_envelope`` and is intentionally not run in CI.

Scope: this test checks an entry-radius envelope and a scalar inequality.
It does not assert positive definiteness of the matrix, a zeta spectrum, or
the Riemann Hypothesis.
"""

from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path

from msaf.entry_error_envelope import (
    DIM,
    EPSILON,
    LAMBDA_MIN,
    OUT,
    check_envelope,
)

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "reports" / "PREREG_ENTRY_ERROR_ENVELOPE_2026-10-26.md"
LEAN = ROOT / "lean" / "Stage_5_EntryError_Perturbation.lean"


def _record() -> dict:
    return json.loads(OUT.read_text(encoding="utf-8"))


def test_envelope_check_passes() -> None:
    data = check_envelope(OUT)
    assert data["dim"] == DIM
    assert data["n_entries"] == DIM * DIM
    assert data["verdict"] == "PASS"


def test_radius_is_below_preregistered_epsilon() -> None:
    data = _record()
    assert Fraction(data["epsilon"]) == Fraction(EPSILON)
    assert Fraction(data["max_entry_radius_plus_slack"]) <= Fraction(EPSILON)
    assert Fraction(data["max_entry_radius_upper"]) <= Fraction(EPSILON)


def test_delta_is_dim_times_epsilon_and_below_lambda() -> None:
    data = _record()
    assert Fraction(data["delta"]) == DIM * Fraction(data["epsilon"])
    assert Fraction(data["delta"]) < Fraction(data["lambda_min"])
    assert Fraction(data["lambda_min"]) == Fraction(LAMBDA_MIN)


def test_digest_is_a_sha256_commitment() -> None:
    data = _record()
    assert re.fullmatch(r"[0-9a-f]{64}", data["digest_sha256"])
    assert data["digest_convention"].startswith("sha256 of LF-joined")


def test_scope_is_explicitly_limited() -> None:
    scope = _record()["scope"].lower()
    assert "not a proof" in scope
    assert "rh" in scope  # named, but only as a disclaimed non-claim
    assert "positive definiteness" in scope


def test_prereg_constants_are_locked() -> None:
    text = PREREG.read_text(encoding="utf-8")
    assert "epsilon = 10^-100" in text
    assert "delta   = dim * epsilon = 321 * 10^-100 = 3.21 * 10^-98" in text
    assert "lambda  = gw_lambda_min = 3123458832662237 / 10^74" in text


def test_lean_theorem_names_exist() -> None:
    text = LEAN.read_text(encoding="utf-8")
    for name in (
        "qform_add",
        "abs_qform_le_of_entrywise",
        "posDef_add_of_quadratic_bound",
        "gw_entry_delta_lt_lambda_min",
        "gw_entry_perturbation_posDef",
    ):
        assert re.search(rf"^theorem {name}\b", text, re.M), name


def test_lean_has_no_placeholders() -> None:
    text = LEAN.read_text(encoding="utf-8")
    for token in ("sorry", "admit", "axiom ", "Abort"):
        assert token not in text, token


