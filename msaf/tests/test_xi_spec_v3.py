# -*- coding: utf-8 -*-
"""Guard for the faithful spec ``lean/spec_v3/XiAnalyticFaithful.lean``.

Unlike V1/V2, this file defines ``xiReal`` from Mathlib's actual
``completedRiemannZeta``.  The functional equation and the ``x > 1``
positivity are proved.  The only unproved analytic input is ``hmid``, the
sign of completed zeta on ``(0, 1)``; it is an explicit parameter of
``xi_pos_on_reals``, not a global declaration.

The static tests run everywhere.  The Lean probe runs only when ``lake`` is
available and checks the actual ``#print axioms`` footprint: the three
standard Lean axioms and no ``XiAnalyticFaithful`` declarations.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from msaf.tests.test_lean_axiom_audit import LEAN_DIR, _strip_comments

ROOT = Path(__file__).resolve().parents[2]
V3 = ROOT / "lean" / "spec_v3" / "XiAnalyticFaithful.lean"
WORKFLOW = ROOT / ".github" / "workflows" / "spec-v3.yml"

STDLIB_AXIOMS = ("propext", "Classical.choice", "Quot.sound")
PROJECT_PREFIX = "XiAnalyticFaithful."


def _axiom_lines(text: str) -> list[str]:
    stripped = _strip_comments(text)
    return re.findall(r"^[ \t]*axiom\b.*$", stripped, re.M)


def test_v3_has_no_project_axioms_and_one_explicit_hypothesis() -> None:
    assert V3.is_file(), "missing faithful V3 source"
    text = V3.read_text(encoding="utf-8")
    stripped = _strip_comments(text)

    assert _axiom_lines(text) == [], "V3 must not declare any axiom"
    assert not re.search(r"\b(sorry|admit|unsafe)\b", stripped), (
        "V3 must not contain escape tokens"
    )

    # It must use Mathlib's actual completed zeta, not the opaque V2 symbols.
    assert "completedRiemannZeta" in stripped
    assert "zetaReal" not in stripped
    assert "gammaReal" not in stripped

    # The midpoint sign obligation must be an explicit theorem parameter.
    assert re.search(
        r"theorem xi_pos_on_reals\s*\n\s*\(hmid\s*:",
        stripped,
    ), "xi_pos_on_reals must take hmid as an explicit argument"
    assert "hmid" in stripped
    assert "xiReal_one_sub" in stripped
    assert "completedRiemannZeta_one_sub" in stripped

    # The removable endpoints are guarded to 1/2.
    assert "if x = 0 âˆ¨ x = 1 then 1 / 2" in stripped


def test_v3_workflow_is_scoped_and_fail_closed() -> None:
    assert WORKFLOW.is_file(), "missing V3 workflow"
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "name: Spec V3" in text
    assert "lean-v3" in text
    assert "lean/spec_v3/**" in text
    assert "msaf/tests/test_xi_spec_v3.py" in text
    assert "python -m pytest msaf/tests/test_xi_spec_v3.py -q" in text
    assert "continue-on-error" not in text


def _run_lake_lean_probe(probe_text: str) -> tuple[int, str]:
    probe = LEAN_DIR / "_xi_spec_v3_probe_tmp.lean"
    try:
        probe.write_text(probe_text, encoding="utf-8")
        res = subprocess.run(
            "lake env lean " + probe.name,
            cwd=str(LEAN_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=True,
        )
        return res.returncode, (res.stdout or "") + (res.stderr or "")
    finally:
        probe.unlink(missing_ok=True)


@pytest.mark.skipif(
    shutil.which("lake") is None, reason="Lean toolchain absent"
)
def test_v3_axiom_footprint_is_standard_only() -> None:
    source = V3.read_text(encoding="utf-8")
    probe = source + (
        "\n#print axioms XiAnalyticFaithful.xi_pos_on_reals\n"
        "#print axioms XiAnalyticFaithful.xiReal_one_sub\n"
        "#print axioms XiAnalyticFaithful.completedZeta_pos_of_one_lt\n"
        "#print XiAnalyticFaithful.xi_pos_on_reals\n"
    )
    rc, out = _run_lake_lean_probe(probe)
    assert rc == 0, "V3 failed to compile:\n%s" % out[:3000]

    axiom_lines = [line for line in out.splitlines() if "depends on axioms:" in line]
    assert len(axiom_lines) == 3, (
        "expected three #print axioms lines, got:\n%s" % out[:3000]
    )
    for line in axiom_lines:
        payload = line.split("depends on axioms:", 1)[1]
        assert PROJECT_PREFIX not in payload, (
            "project declaration leaked into the axiom footprint: %s" % line
        )
        for axiom in STDLIB_AXIOMS:
            assert axiom in payload, "missing standard axiom %s in %s" % (axiom, line)

    # The theorem type must still expose hmid; it is not discharged by a hidden axiom.
    assert "fun hmid" in out or "hmid" in out
    assert "completedRiemannZeta" in out


