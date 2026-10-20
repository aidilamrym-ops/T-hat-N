# -*- coding: utf-8 -*-
"""Guard for V5 ``lean/spec_v5/XiPosUnconditional.lean``.

V5 is the glue between the sealed V3 and V4 packages.  V3's
``xi_pos_on_reals`` keeps the midpoint sign ``hmid`` as an explicit
hypothesis; V4 proves ``hmid`` unconditionally.  V5 applies the former to the
latter and therefore adds no new analytic content.

The static tests run everywhere.  The Lean probe runs only when ``lake`` is
available, materialises the read-only V3 and V4 oleans required by the V5
imports, and checks the actual ``#print axioms`` footprint.  The probe file is
created outside ``lean/`` so the tracked tree is never touched.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from msaf.tests.test_lean_axiom_audit import LEAN_DIR, _strip_comments

ROOT = Path(__file__).resolve().parents[2]
V5 = ROOT / "lean" / "spec_v5" / "XiPosUnconditional.lean"
V3 = ROOT / "lean" / "spec_v3" / "XiAnalyticFaithful.lean"
V4 = ROOT / "lean" / "spec_v4" / "XiUnconditional.lean"
WORKFLOW = ROOT / ".github" / "workflows" / "spec-v5.yml"

STDLIB_AXIOMS = ("propext", "Classical.choice", "Quot.sound")
PROJECT_PREFIX = "XiPosUnconditional."


def _axiom_lines(text: str) -> list[str]:
    stripped = _strip_comments(text)
    return re.findall(r"^[ \t]*axiom\b.*$", stripped, re.M)


def test_v5_has_no_project_axioms_and_no_escape_tokens() -> None:
    assert V5.is_file(), "missing unconditional V5 source"
    text = V5.read_text(encoding="utf-8")
    stripped = _strip_comments(text)

    assert _axiom_lines(text) == [], "V5 must not declare any axiom"
    assert not re.search(r"\b(sorry|admit|unsafe)\b", stripped), (
        "V5 must not contain escape tokens"
    )

    # The V5 theorem must be unconditional: no `hmid` parameter.
    assert re.search(
        r"^theorem xi_pos_on_reals_unconditional \(x : ℝ\) :\s*"
        r"0 < XiAnalyticFaithful\.xiReal x :=",
        stripped,
        re.M,
    ), "V5 must state the unconditional xi positivity theorem"

    # The glue route must be visible in the source, not assumed.
    assert "import spec_v3.XiAnalyticFaithful" in stripped
    assert "import spec_v4.XiUnconditional" in stripped
    assert "XiAnalyticFaithful.xi_pos_on_reals hmid x" in stripped

    # V5 is not the spectral H1/engine-B package and is not V6.
    for token in (
        "RiemannHypothesis",
        "riemannZeta",
        "completedRiemannZeta",
        "completedCosZeta",
        "zetaReal",
        "gammaReal",
    ):
        assert token not in stripped, "V5 must not mention %s" % token


def test_v5_workflow_is_scoped_and_fail_closed() -> None:
    assert WORKFLOW.is_file(), "missing V5 workflow"
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "name: Spec V5" in text
    assert "lean-v5" in text
    assert "lean/spec_v5/**" in text
    assert "msaf/tests/test_xi_spec_v5.py" in text
    assert "python -m pytest msaf/tests/test_xi_spec_v5.py -q" in text
    assert "continue-on-error" not in text
    assert "spec_v3/XiAnalyticFaithful.lean" in text
    assert "spec_v4/XiUnconditional.lean" in text


def _build_olean(source: Path, module_dir: str, target_name: str) -> None:
    """Materialise a read-only V3/V4 olean required by the V5 imports."""
    out = LEAN_DIR / ".lake" / "build" / "lib" / "lean" / module_dir
    out.mkdir(parents=True, exist_ok=True)
    target = out / target_name
    if target.is_file() and target.stat().st_mtime >= source.stat().st_mtime:
        return
    rel_out = target.relative_to(LEAN_DIR).as_posix()
    rel_src = source.relative_to(LEAN_DIR).as_posix()
    res = subprocess.run(
        ["lake", "env", "lean", "-o", rel_out, rel_src],
        cwd=str(LEAN_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert res.returncode == 0, (
        "failed to build %s:\n%s"
        % (target_name, ((res.stdout or "") + (res.stderr or ""))[:3000])
    )


def _build_dependencies() -> None:
    _build_olean(V3, "spec_v3", "XiAnalyticFaithful.olean")
    _build_olean(V4, "spec_v4", "XiUnconditional.olean")


def _run_lake_lean_probe(probe_text: str) -> tuple[int, str]:
    """Compile a probe from a temporary directory outside ``lean/``."""
    with tempfile.TemporaryDirectory(prefix="xi_spec_v5_probe_") as tmp:
        probe = Path(tmp) / "probe.lean"
        probe.write_text(probe_text, encoding="utf-8")
        res = subprocess.run(
            ["lake", "env", "lean", str(probe)],
            cwd=str(LEAN_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return res.returncode, (res.stdout or "") + (res.stderr or "")


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
def test_v5_axiom_footprint_is_standard_only() -> None:
    _build_dependencies()
    source = V5.read_text(encoding="utf-8")
    probe = source + (
        "\n#print axioms XiPosUnconditional.xi_pos_on_reals_unconditional\n"
    )
    rc, out = _run_lake_lean_probe(probe)
    assert rc == 0, "V5 failed to compile:\n%s" % out[:3000]
    assert "unknown constant" not in out, "V5 probe left a name unresolved:\n%s" % out[:3000]

    blocks = _axiom_blocks(out)
    assert len(blocks) == 1, (
        "expected one #print axioms block, got:\n%s" % out[:3000]
    )
    payload = blocks[0].split("depends on axioms:", 1)[1]
    assert PROJECT_PREFIX not in payload, (
        "project declaration leaked into the axiom footprint: %s" % blocks[0]
    )
    assert "sorryAx" not in payload, "sorryAx leaked into: %s" % blocks[0]
    assert "XiAnalyticFaithful." not in payload, (
        "V3 theorem leaked into the axiom footprint: %s" % blocks[0]
    )
    for axiom in STDLIB_AXIOMS:
        assert axiom in payload, "missing standard axiom %s in %s" % (
            axiom,
            blocks[0],
        )

    assert "XiPosUnconditional.xi_pos_on_reals_unconditional" in out
    assert "sorryAx" not in out
