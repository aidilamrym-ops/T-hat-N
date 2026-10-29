# -*- coding: utf-8 -*-
"""Guard for V6 ``lean/spec_v6/FiniteLatticeBridge.lean``.

V6 proves the certified bridge from the finite lattice truncation of the
half-kernel theta series to ``completedCosZeta (1/2)``: the alternating tail
bound T1, the explicit Mellin error T2, the sign transfer T3, and the N=1
certificate K1.  The file declares no project axiom and contains no escape
token.

The static tests run everywhere.  The Lean probe runs only when ``lake`` is
available, first materialises the read-only V4 olean required by the V6
import, then checks the actual ``#print axioms`` footprint.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from msaf.tests.test_lean_axiom_audit import LEAN_DIR, _strip_comments

ROOT = Path(__file__).resolve().parents[2]
V6 = ROOT / "lean" / "spec_v6" / "FiniteLatticeBridge.lean"
V4 = ROOT / "lean" / "spec_v4" / "XiUnconditional.lean"
WORKFLOW = ROOT / ".github" / "workflows" / "spec-v6.yml"

STDLIB_AXIOMS = ("propext", "Classical.choice", "Quot.sound")
PROJECT_PREFIX = "FiniteLatticeBridge."


def _axiom_lines(text: str) -> list[str]:
    stripped = _strip_comments(text)
    return re.findall(r"^[ \t]*axiom\b.*$", stripped, re.M)


def test_v6_has_no_project_axioms_and_no_escape_tokens() -> None:
    assert V6.is_file(), "missing finite-lattice bridge V6 source"
    text = V6.read_text(encoding="utf-8")
    stripped = _strip_comments(text)

    assert _axiom_lines(text) == [], "V6 must not declare any axiom"
    assert not re.search(r"\b(sorry|admit|unsafe)\b", stripped), (
        "V6 must not contain escape tokens"
    )

    for token in (
        "theorem abs_kHalf_sub_lattice_le",
        "theorem completedCosZeta_half_lattice_error",
        "theorem completedCosZeta_half_neg_of_lattice_certificate",
        "theorem completedCosZeta_half_neg_of_first_term",
        "def latticeValue",
        "def latticeError",
    ):
        assert token in stripped, "missing V6 declaration: %s" % token

    # V6 must state the explicit error and the conditional sign transfer, and
    # it must not smuggle in the Riemann zeta or a zero-location claim.
    assert "latticeValue N x + latticeError N x < 0" in stripped
    assert "completedRiemannZeta" not in stripped
    assert "zetaReal" not in stripped
    assert "gammaReal" not in stripped
    # The bridge consumes V4's sealed Mellin identity read-only.
    assert "completedCosZeta_half_eq_mellin" in stripped
    assert "import spec_v4.XiUnconditional" in stripped


def test_v6_workflow_is_scoped_and_fail_closed() -> None:
    assert WORKFLOW.is_file(), "missing V6 workflow"
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "name: Spec V6" in text
    assert "lean-v6" in text
    assert "lean/spec_v6/**" in text
    assert "msaf/tests/test_xi_spec_v6.py" in text
    assert "python -m pytest msaf/tests/test_xi_spec_v6.py -q" in text
    assert "continue-on-error" not in text


def _run_lake_lean_probe(probe_text: str) -> tuple[int, str]:
    probe = LEAN_DIR / "_xi_spec_v6_probe_tmp.lean"
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


def _build_v4_olean() -> None:
    """Materialise the read-only V4 olean required by the V6 import."""
    out = LEAN_DIR / ".lake" / "build" / "lib" / "lean" / "spec_v4"
    out.mkdir(parents=True, exist_ok=True)
    target = out / "XiUnconditional.olean"
    if target.is_file() and target.stat().st_mtime >= V4.stat().st_mtime:
        return
    res = subprocess.run(
        "lake env lean -o .lake/build/lib/lean/spec_v4/XiUnconditional.olean "
        "spec_v4/XiUnconditional.lean",
        cwd=str(LEAN_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=True,
    )
    assert res.returncode == 0, (
        "failed to build V4 olean:\n%s"
        % ((res.stdout or "") + (res.stderr or ""))[:3000]
    )


def _axiom_blocks(out: str) -> list[str]:
    """Collect ``depends on axioms`` blocks, joining pretty-printer wraps."""
    blocks: list[str] = []
    current = ""
    for line in out.splitlines():
        if "depends on axioms:" in line:
            if current:
                blocks.append(current)
            current = line
        elif current:
            current += " " + line.strip()
        if current and "]" in current:
            blocks.append(current)
            current = ""
    if current:
        blocks.append(current)
    return blocks


@pytest.mark.skipif(
    shutil.which("lake") is None, reason="Lean toolchain absent"
)
def test_v6_axiom_footprint_is_standard_only() -> None:
    _build_v4_olean()
    source = V6.read_text(encoding="utf-8")
    probe = source + (
        "\n#print axioms FiniteLatticeBridge.abs_kHalf_sub_lattice_le\n"
        "#print axioms FiniteLatticeBridge.completedCosZeta_half_lattice_error\n"
        "#print axioms FiniteLatticeBridge.completedCosZeta_half_neg_of_lattice_certificate\n"
        "#print axioms FiniteLatticeBridge.completedCosZeta_half_neg_of_first_term\n"
    )
    rc, out = _run_lake_lean_probe(probe)
    assert rc == 0, "V6 failed to compile:\n%s" % out[:3000]

    blocks = _axiom_blocks(out)
    assert len(blocks) == 4, (
        "expected four #print axioms blocks, got:\n%s" % out[:3000]
    )
    for block in blocks:
        payload = block.split("depends on axioms:", 1)[1]
        assert PROJECT_PREFIX not in payload, (
            "project declaration leaked into the axiom footprint: %s" % block
        )
        assert "sorryAx" not in payload, "sorryAx leaked into: %s" % block
        for axiom in STDLIB_AXIOMS:
            assert axiom in payload, "missing standard axiom %s in %s" % (
                axiom,
                block,
            )

    # The sign transfer must conclude the cosine completed zeta, not the
    # Riemann zeta, and no zero-location claim may appear.
    assert "completedCosZeta" in out
    assert "sorryAx" not in out


