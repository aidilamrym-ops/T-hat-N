# -*- coding: utf-8 -*-
"""Guard for the unconditional V4 spec ``lean/spec_v4/XiUnconditional.lean``.

V3 kept the midpoint sign ``hmid`` as an explicit hypothesis of
``xi_pos_on_reals``.  V4 discharges it: ``hmid`` is a closed theorem proved
from Mathlib's ``completedRiemannZeta``, the Mellin representation of
``completedCosZeta (1/2)``, the eta identity for ``cosZeta (1/2)``, and the
analytic continuation of that identity.  The file declares no project axiom
and contains no escape token.

The static tests run everywhere.  The Lean probe runs only when ``lake`` is
available and checks the actual ``#print axioms`` footprint: the three
standard Lean axioms and no ``XiUnconditional`` declarations.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from msaf.tests.test_lean_axiom_audit import LEAN_DIR, _strip_comments

ROOT = Path(__file__).resolve().parents[2]
V4 = ROOT / "lean" / "spec_v4" / "XiUnconditional.lean"
WORKFLOW = ROOT / ".github" / "workflows" / "spec-v4.yml"

STDLIB_AXIOMS = ("propext", "Classical.choice", "Quot.sound")
PROJECT_PREFIX = "XiUnconditional."


def _axiom_lines(text: str) -> list[str]:
    stripped = _strip_comments(text)
    return re.findall(r"^[ \t]*axiom\b.*$", stripped, re.M)


def test_v4_has_no_project_axioms_and_no_escape_tokens() -> None:
    assert V4.is_file(), "missing unconditional V4 source"
    text = V4.read_text(encoding="utf-8")
    stripped = _strip_comments(text)

    assert _axiom_lines(text) == [], "V4 must not declare any axiom"
    assert not re.search(r"\b(sorry|admit|unsafe)\b", stripped), (
        "V4 must not contain escape tokens"
    )

    # hmid is unconditional: a closed theorem, not a parameter.
    assert re.search(
        r"^theorem hmid : ∀ x : ℝ, 0 < x → x < 1 → "
        r"\(completedRiemannZeta \(x : ℂ\)\)\.re < 0",
        stripped,
        re.M,
    ), "hmid must be the unconditional closed theorem"

    # The V4 route must be visible in the source, not assumed.
    for token in (
        "completedCosZeta_half_neg",
        "cosZeta_half_neg",
        "cosZeta_zero",
        "riemannZeta_def_of_ne_zero",
        "eqOn_of_preconnected_of_eventuallyEq",
    ):
        assert token in stripped, "missing V4 ingredient: %s" % token

    # It must use Mathlib's actual completed zeta, not opaque V2 symbols.
    assert "completedRiemannZeta" in stripped
    assert "zetaReal" not in stripped
    assert "gammaReal" not in stripped


def test_v4_workflow_is_scoped_and_fail_closed() -> None:
    assert WORKFLOW.is_file(), "missing V4 workflow"
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "name: Spec V4" in text
    assert "lean-v4" in text
    assert "lean/spec_v4/**" in text
    assert "msaf/tests/test_xi_spec_v4.py" in text
    assert "python -m pytest msaf/tests/test_xi_spec_v4.py -q" in text
    assert "continue-on-error" not in text


def _run_lake_lean_probe(probe_text: str) -> tuple[int, str]:
    probe = LEAN_DIR / "_xi_spec_v4_probe_tmp.lean"
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
def test_v4_axiom_footprint_is_standard_only() -> None:
    source = V4.read_text(encoding="utf-8")
    probe = source + (
        "\n#print axioms hmid\n"
        "#print axioms cosZeta_half_neg\n"
        "#print axioms completedCosZeta_half_neg\n"
        "#print hmid\n"
    )
    rc, out = _run_lake_lean_probe(probe)
    assert rc == 0, "V4 failed to compile:\n%s" % out[:3000]

    axiom_lines = [line for line in out.splitlines() if "depends on axioms:" in line]
    assert len(axiom_lines) == 3, (
        "expected three #print axioms lines, got:\n%s" % out[:3000]
    )
    for line in axiom_lines:
        payload = line.split("depends on axioms:", 1)[1]
        assert PROJECT_PREFIX not in payload, (
            "project declaration leaked into the axiom footprint: %s" % line
        )
        assert "sorryAx" not in payload, "sorryAx leaked into: %s" % line
        for axiom in STDLIB_AXIOMS:
            assert axiom in payload, "missing standard axiom %s in %s" % (axiom, line)

    # The closed theorem type must still spell out the unconditional statement.
    assert "hmid" in out
    assert "completedRiemannZeta" in out
    assert "sorryAx" not in out
