# -*- coding: utf-8 -*-
"""Regression tests for the v5 dashboard generator and the v4/v3 seals.

Guards:
  * the v3 seal -- reports/gw_diagnostic_v3.html must stay byte-identical
    (sha256 89c7d5f9...);
  * the v4 seal -- reports/gw_diagnostic_v4.html must stay byte-identical
    (sha256 c9ec2621...); the v5 page embeds this hash and the guard
    fails if either the base page or the generator drifts;
  * v5 generation -- the generator reads the H1 stage A+B artefact and
    the engine-B stage C artefacts, the rendered HTML is deterministic
    (byte-stable across reruns), carries no JavaScript / external URLs /
    xmlns, and contains the sealed key numbers;
  * the committed HTML equals a fresh render (no drift between the
    committed artefact and the generator).
"""

import hashlib

from msaf import gw_dashboard_v5 as v5

V3_SHA = "89c7d5f948626bd51de06f37534bdc4941d3793353dcb80b8557e10e2bed7322"
V4_SHA = "c9ec26217f516a1a73527bc098addbc11a4935f6965d905d38a7dbeb7d95a8b6"

NEEDLES = (
    "1262/20000",
    "6.31000e-02",
    "5.87700e-02",
    "2.01097e-22",
    "1.49775e-04",
    "PASS-WITH-ENUMERATED-EXCEPTIONS",
    "3.299020e-59",
    "666/720",
    "NO DISCRIMINATION AT N=401",
    "NOT STABLE",
    "dim 321 not yet run",
    "float64 underflow",
    V4_SHA,
    V3_SHA,
)


def test_v3_seal_unchanged():
    p = v5.ROOT / "reports" / "gw_diagnostic_v3.html"
    assert p.exists()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == V3_SHA


def test_v4_seal_unchanged():
    assert v5.V4.exists()
    assert v5.v4.full_hash(v5.V4) == V4_SHA


def test_v5_render_deterministic_and_clean():
    h1 = v5.build()
    h2 = v5.build()
    assert h1 == h2  # byte-stable in memory
    low = h1.lower()
    assert "<script" not in low
    assert "://" not in h1
    assert "xmlns" not in low
    assert "onclick" not in low
    # sealed key numbers must appear (machine-extracted at build time)
    for needle in NEEDLES:
        assert needle in h1, needle
    # the pre-correction radius wording must not survive anywhere
    # (correction measured 2026-10-17: registry 0.0 is a float64
    # underflow, not an exact point)
    assert "radius exactly 0" not in h1
    assert "enclosure radius = 0.0" not in h1
    assert h1.count('class="eq"') == 9
    assert h1.count("<svg") == 5
    assert h1.count('class="panel"') == 9
    assert "<footer>" in h1


def test_v5_committed_html_matches_generator():
    assert v5.OUT.exists()
    assert v5.OUT.read_text(encoding="utf-8") == v5.build()


