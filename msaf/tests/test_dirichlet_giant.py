"""Test suite for giant modulus Dirichlet L-functions at q=1000."""

from __future__ import annotations

import json
from pathlib import Path

from msaf.chrono_runtime.dirichlet_giant_q import GiantDirichletEngine, lift_to_primitive, run_giant_analysis


def test_lift_to_primitive() -> None:
    cond, num = lift_to_primitive(1000, 3)
    assert cond > 0


def test_giant_engine_evaluation() -> None:
    engine = GiantDirichletEngine(1000, 3, prec=512)
    assert engine.conductor > 0


def test_giant_bracket_report() -> None:
    report = run_giant_analysis()
    assert report["modulus"] == 1000
    assert report["status"] == "CERTIFIED"
    assert Path("reports/GRH_GIANT_Q_BRACKET_REPORT.json").exists()
