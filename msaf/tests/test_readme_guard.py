# -*- coding: utf-8 -*-
"""CI guard: README.md Section 7 must equal a fresh render from the sealed
artefacts (msaf/gw_readme.py).

Drift means one of: a hand-edited number inside the generated block, a stale
diagram, or a changed artefact that was not propagated into the README. All
three must fail CI, never pass silently.
"""

from __future__ import annotations

import re

from msaf import gw_readme


def _collect():
    try:
        return gw_readme.collect()
    except SystemExit as exc:
        raise AssertionError("gw_readme.collect() refused: %s" % exc)


def _blocks(text: str) -> list:
    return re.findall(re.escape(gw_readme.BEGIN) + r".*?"
                      + re.escape(gw_readme.END), text, re.DOTALL)


def test_readme_sealed_block_matches_generator() -> None:
    text = gw_readme.README.read_text(encoding="utf-8")
    blocks = _blocks(text)
    assert len(blocks) == 1, (
        "README.md must carry exactly one generated sealed-status block, "
        "found %d" % len(blocks))
    fresh = gw_readme.render_segment(_collect())
    assert blocks[0] == fresh, (
        "README.md sealed-status block drifted from the sealed artefacts; "
        "re-run: python msaf/gw_readme.py --write")


def test_readme_diagrams_match_generator() -> None:
    ctx = _collect()
    pairs = ((gw_readme.SVG_WORKFLOW, gw_readme.render_workflow_svg(ctx)),
             (gw_readme.SVG_TRUSTCHAIN,
              gw_readme.render_trustchain_svg(ctx)))
    for path, fresh in pairs:
        assert path.exists(), "missing diagram: %s" % path
        assert path.read_text(encoding="utf-8") == fresh, (
            "%s drifted from the sealed artefacts; re-run: "
            "python msaf/gw_readme.py --write" % path.name)


def test_readme_references_diagrams_and_block() -> None:
    text = gw_readme.README.read_text(encoding="utf-8")
    assert "docs/math/readme_workflow.svg" in text
    assert "docs/math/readme_trustchain.svg" in text
    assert text.count(gw_readme.BEGIN) == 1
    assert text.count(gw_readme.END) == 1
    assert "#section-7-sealed-status-workflow-and-verification-chain" in text


