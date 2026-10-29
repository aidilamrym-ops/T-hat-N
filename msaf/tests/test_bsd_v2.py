from __future__ import annotations

import hashlib
from pathlib import Path

from msaf import bsd_v2

ROOT = Path(__file__).resolve().parents[2]
PREREG_PATH = ROOT / "reports" / "PREREG_Q1_BSD_V2_2026-10-30.md"


def test_bsd_v2_all_curves_pass() -> None:
    payload = bsd_v2.build_payload()
    assert payload["all_pass"] is True
    assert payload["summary"] == "ALL PASS"
    assert len(payload["curves"]) == 5


def test_no_float_or_numpy_in_bsd_v2() -> None:
    source = (ROOT / "msaf" / "bsd_v2.py").read_text(encoding="utf-8")
    assert "numpy" not in source
    assert "float" not in source


