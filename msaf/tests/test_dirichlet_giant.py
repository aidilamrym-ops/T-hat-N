"""Test suite for the giant-modulus Dirichlet bracket engine (q=1000).

The q=1000 character originally used by this module was complex, and FLINT's
Hardy Z requires a primitive character. The engine now refuses those cases
explicitly instead of reading a meaningless real sign, so this suite pins the
honest statuses:

* complex character -> ``REJECTED_COMPLEX_CHARACTER``;
* real but imprimitive -> ``UNAVAILABLE_NON_PRIMITIVE``;
* real and primitive (q=5) -> real certified brackets.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from msaf.chrono_runtime.dirichlet_giant_q import (
    GiantDirichletEngine,
    first_real_character,
    lift_to_primitive,
    run_giant_analysis,
)


def test_lift_to_primitive() -> None:
    cond, num = lift_to_primitive(1000, 3)
    assert cond > 0


def test_giant_engine_evaluation() -> None:
    engine = GiantDirichletEngine(1000, 3, prec=512)
    assert engine.conductor > 0


def test_giant_engine_refuses_complex_coefficients() -> None:
    engine = GiantDirichletEngine(1000, 3, prec=512)
    with pytest.raises(ValueError):
        engine.evaluate_values(max_n=4)


def test_giant_engine_refuses_complex_hardy_bracket() -> None:
    engine = GiantDirichletEngine(1000, 3, prec=512)
    with pytest.raises(ValueError):
        engine.bracket_hardy(10.0, 12.0, 0.5)


def test_giant_engine_refuses_imprimitive_hardy_bracket() -> None:
    # q=1000, number 249 is real but has conductor 5.
    engine = GiantDirichletEngine(1000, 249, prec=512)
    assert engine.chi.is_real() is True
    assert engine.chi.is_primitive() is False
    with pytest.raises(ValueError):
        engine.bracket_hardy(10.0, 12.0, 0.5)


def test_real_primitive_character_still_brackets(tmp_path: Path) -> None:
    target = tmp_path / "giant_q5.json"
    report = run_giant_analysis(modulus=5, receipt_path=target)
    assert report["modulus"] == 5
    assert report["character_is_real"] is True
    assert report["primitive"] is True
    assert report["status"] == "CERTIFIED"
    assert report["bracket_count"] > 0
    assert json.loads(target.read_text(encoding="utf-8"))["bracket_count"] == (
        report["bracket_count"]
    )


def test_giant_bracket_report_is_honest_for_q1000(tmp_path: Path) -> None:
    target = tmp_path / "giant_q1000.json"
    report = run_giant_analysis(modulus=1000, receipt_path=target)
    assert report["modulus"] == 1000
    assert report["character_is_real"] is True
    assert report["primitive"] is False
    assert report["brackets"] == []
    assert report["bracket_count"] == 0
    assert report["status"] == "UNAVAILABLE_NON_PRIMITIVE"
    assert report["status_reason"]
    assert report["scope_notice"]["rh_claim"] is False
    assert report["scope_notice"]["grh_claim"] is False
    assert report["scope_notice"]["zero_location_claim"] is False
    assert json.loads(target.read_text(encoding="utf-8"))["status"] == (
        "UNAVAILABLE_NON_PRIMITIVE"
    )


def test_giant_report_rejects_explicit_complex_character(tmp_path: Path) -> None:
    target = tmp_path / "giant_complex.json"
    report = run_giant_analysis(modulus=1000, number=3, receipt_path=target)
    assert report["character_is_real"] is False
    assert report["brackets"] == []
    assert report["status"] == "REJECTED_COMPLEX_CHARACTER"
    assert report["status_reason"]


def test_first_real_character_is_primitive_for_q5() -> None:
    number = first_real_character(5)
    engine = GiantDirichletEngine(5, number, prec=512)
    assert engine.chi.is_real() is True
    assert engine.chi.is_primitive() is True
