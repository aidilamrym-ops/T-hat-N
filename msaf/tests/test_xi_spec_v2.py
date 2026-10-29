# -*- coding: utf-8 -*-
"""Guard for the repaired abstract spec ``lean/spec_v2/XiAnalyticSpecV2.lean``.

The historical ``lean/spec/XiAnalyticSpec.lean`` (pinned by registry
``A-2026-0015``) is inconsistent: its global ``xiReal_sub_one`` plus the
product definition at ``x = 1`` lets Lean prove ``False``. It is kept
byte-identical as history. V2 narrows the abstraction boundary:

* ``xiReal`` is guarded at ``x = 1``;
* ``xiReal_sub_one`` is stated only for ``x < 0``;
* the false, unused ``zetaReal_neg`` axiom is gone.

These tests are static when the Lean toolchain is absent, and execute
real ``lake env lean`` probes when it is present. A passed probe is an
axiom-footprint check, not a proof of the actual Riemann xi function.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from msaf.tests.test_lean_axiom_audit import LEAN_DIR, _strip_comments

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "lean" / "spec_v2" / "XiAnalyticSpecV2.lean"
OLD_SPEC = ROOT / "lean" / "spec" / "XiAnalyticSpec.lean"
SPEC_README = ROOT / "lean" / "spec" / "README.md"

EXPECTED_AXIOMS = (
    "XiAnalyticSpecV2.gammaReal",
    "XiAnalyticSpecV2.gammaReal_one",
    "XiAnalyticSpecV2.gammaReal_pos",
    "XiAnalyticSpecV2.xiReal_sub_one",
    "XiAnalyticSpecV2.zetaReal",
    "XiAnalyticSpecV2.zetaReal_gt_one",
    "XiAnalyticSpecV2.zetaReal_mid",
    "XiAnalyticSpecV2.zetaReal_zero",
)

OLD_CONTRADICTION = """

namespace XiAnalyticSpecV2

theorem old_contradiction_still_works : False := by
  have h := xiReal_sub_one 0
  have h' : xiReal 1 = xiReal 0 := by simpa using h
  have h1 : xiReal 1 = 1 / 2 := by simp [xiReal]
  have h0 : xiReal 0 = 1 / 2 := by
    simp [xiReal, zetaReal_zero, gammaReal_one]
    norm_num
  rw [h1, h0] at h'
  norm_num at h'

end XiAnalyticSpecV2
"""


def _axiom_lines(text: str) -> list[str]:
    stripped = _strip_comments(text)
    return re.findall(r"^[ \t]*axiom\b.*$", stripped, re.M)


def test_v2_has_eight_axioms_and_no_false_negative_axiom() -> None:
    text = V2.read_text(encoding="utf-8")
    lines = _axiom_lines(text)
    assert len(lines) == 8, "V2 must declare exactly eight axioms, got %d" % len(lines)
    assert "zetaReal_neg" not in _strip_comments(text)
    assert "SPECIFICATION V2, NOT PROOF" in text
    assert "x < 0 â†’ xiReal (1 - x) = xiReal x" in text
    assert "if x = 1 then 1 / 2" in text


def test_historical_spec_is_present_and_marked_superseded() -> None:
    assert OLD_SPEC.is_file(), "historical spec must stay byte-identical"
    assert SPEC_README.is_file(), "spec README pointer is missing"
    low = SPEC_README.read_text(encoding="utf-8").lower()
    assert "inconsistent" in low
    assert "xianalyticspecv2" in low.replace("/", "")


def _run_lake_lean_probe(probe_text: str) -> tuple[int, str]:
    probe = LEAN_DIR / "_xi_spec_v2_probe_tmp.lean"
    try:
        probe.write_text(probe_text, encoding="utf-8")
        res = subprocess.run(
            "lake env lean " + probe.name,
            cwd=str(LEAN_DIR),
            capture_output=True,
            text=True,
            shell=True,
        )
        return res.returncode, (res.stdout or "") + (res.stderr or "")
    finally:
        probe.unlink(missing_ok=True)


@pytest.mark.skipif(
    shutil.which("lake") is None, reason="Lean toolchain absent"
)
def test_v2_axiom_footprint_and_old_contradiction_is_blocked() -> None:
    source = V2.read_text(encoding="utf-8")
    rc, out = _run_lake_lean_probe(
        source + "\n#print axioms XiAnalyticSpecV2.xi_pos_on_reals\n"
    )
    assert rc == 0, "V2 failed to compile:\n%s" % out[:3000]
    for name in EXPECTED_AXIOMS:
        assert name in out, "missing axiom dependency %s" % name
    assert "zetaReal_neg" not in out, "removed axiom still in the footprint"
    assert "depends on axioms" in out

    rc_old, out_old = _run_lake_lean_probe(source + OLD_CONTRADICTION)
    assert rc_old != 0, "the old contradiction proof must not compile against V2"
    assert "0 < 0" in out_old, (
        "expected the old proof to be blocked by the x < 0 hypothesis, got:\n%s"
        % out_old[:2000]
    )


