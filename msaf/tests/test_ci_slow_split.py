# -*- coding: utf-8 -*-
"""Guard for the fast/slow CI split (prereg 2026-10-27).

The default CI job must never silently run the figure-eight Arb campaigns
again: `python-tests` has a 60-minute budget, the campaigns need more, and a
timeout would look like a test failure. This guard keeps the split explicit:
the marker is registered, the two campaign tests carry it, the default job
deselects it, and a dedicated scheduled workflow still runs it.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_slow_marker_is_registered():
    text = (ROOT / "pytest.ini").read_text(encoding="utf-8")
    assert re.search(r"^[ \t]*slow:", text, re.M), "marker 'slow' not registered"


def test_default_ci_excludes_the_slow_marker():
    text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert 'python -m pytest msaf -q -m "not slow"' in text, (
        "default CI must deselect the slow marker")


def test_slow_workflow_still_runs_the_campaigns():
    path = ROOT / ".github" / "workflows" / "slow-tests.yml"
    assert path.is_file(), "missing slow-tests workflow"
    text = path.read_text(encoding="utf-8")
    assert "python -m pytest msaf -q -m slow" in text
    assert "schedule:" in text and "workflow_dispatch:" in text
    assert "timeout-minutes: 300" in text


def test_both_campaign_tests_are_marked_slow():
    for rel in ("msaf/tests/test_figure_eight_r5.py",
                "msaf/tests/test_figure_eight_r6.py"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        for name in ("test_campaign", "test_registry_entry"):
            pattern = re.compile(r"@pytest\.mark\.slow\ndef " + name + r"\(")
            assert pattern.search(text), f"{rel}::{name} is not marked slow"
