"""Guard for the P2 analytic `XC` tail bound (pre-registered 2026-10-26).

The fast path verifies the recorded JSON only.  It does not rebuild the Arb
trigamma grid; the heavy builder is ``python -m msaf.analytic_tail_bound``.

Scope: this test checks the diagonal ``XC`` grid record and the rational
constants.  It does not assert a full matrix tail, positive definiteness,
zeta spectrum, or the Riemann Hypothesis.
"""

from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path

from msaf.analytic_tail_bound import (
    A_UPPER,
    C,
    CPSI_UPPER,
    L_UPPER,
    N_CHECK,
    OUT,
    PI_LOWER,
    PREC_BITS,
    Q0_UPPER,
    Q1_UPPER,
    RATIO_UPPER,
    check_record,
)

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "reports" / "PREREG_ANALYTIC_TAIL_2026-10-26.md"
LEAN = ROOT / "lean" / "Stage_6_Analytic_Tail.lean"


def _record() -> dict:
    return json.loads(OUT.read_text(encoding="utf-8"))


def test_record_check_passes() -> None:
    data = check_record(OUT)
    assert data["c"] == C
    assert data["n_check"] == N_CHECK
    assert data["prec_bits"] == PREC_BITS
    assert data["verdict"] == "PASS"


def test_max_ratio_is_below_one() -> None:
    data = _record()
    assert Fraction(data["max_ratio_upper"]) < Fraction(RATIO_UPPER)
    assert 1 <= data["n_at_max_ratio"] <= data["n_check"]


def test_constants_are_locked() -> None:
    data = _record()
    assert data["L_upper"] == L_UPPER
    assert data["pi_lower"] == PI_LOWER
    assert data["Cpsi_upper"] == CPSI_UPPER
    assert data["Q0_upper"] == Q0_UPPER
    assert data["Q1_upper"] == Q1_UPPER
    assert Fraction(data["A_upper_bound"]) == Fraction(A_UPPER)
    assert Fraction(A_UPPER) < 1


def test_upper_bounds_are_below_preregistered_caps() -> None:
    data = _record()
    assert Fraction(data["L_upper_arb"]) < Fraction(L_UPPER)
    assert Fraction(data["pi_lower_arb"]) > Fraction(PI_LOWER)
    assert Fraction(data["Q0_upper_arb"]) < Fraction(Q0_UPPER)
    assert Fraction(data["Q1_upper_arb"]) < Fraction(Q1_UPPER)


def test_digest_is_a_sha256_commitment() -> None:
    data = _record()
    assert re.fullmatch(r"[0-9a-f]{64}", data["digest_sha256"])
    assert data["digest_convention"].startswith("sha256 of LF-joined")


def test_scope_is_explicitly_limited() -> None:
    scope = _record()["scope"].lower()
    assert "not a proof" in scope
    assert "positive definiteness" in scope
    assert "full matrix" in scope
    assert "rh" in scope  # named, but only as a disclaimed non-claim


def test_prereg_claim_is_locked() -> None:
    text = PREREG.read_text(encoding="utf-8")
    assert "|XC(n)| < 1/n^2" in text
    assert "epsilon_XC(N)" in text
    assert "= 0.93036 < 1" in text
    assert "Q0 < 0.28" in text
    assert "Q1 < 0.143" in text
    assert "L = log 13 < 2.6" in text
    assert "pi > 3" in text


def test_lean_theorem_names_exist() -> None:
    text = LEAN.read_text(encoding="utf-8")
    for name in (
        "sum_Ico_one_div_sq_le",
        "sum_Ico_abs_le_of_pointwise",
        "epsilon_le_of_pointwise",
        "tendsto_epsilon_majorant",
    ):
        assert re.search(rf"^theorem {name}\b", text, re.M), name


def test_lean_has_no_placeholders() -> None:
    text = LEAN.read_text(encoding="utf-8")
    for token in ("sorry", "admit", "axiom ", "Abort"):
        assert token not in text, token
