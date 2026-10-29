# -*- coding: utf-8 -*-
"""Regression tests for the v4 dashboard generator and the v3 seal.

Guards:
  * the v3 seal -- reports/gw_diagnostic_v3.html must stay byte-identical
    (sha256 89c7d5f9...);
  * v4 generation -- the generator reads the canonical artefacts, the
    rendered HTML is deterministic (byte-stable across reruns), carries
    no JavaScript / external URLs, and contains the sealed key numbers;
  * the committed HTML equals a fresh render (no drift between the
    committed artefact and the generator).
"""

import hashlib

from msaf import gw_dashboard_v4 as v4

V3_SHA = "89c7d5f948626bd51de06f37534bdc4941d3793353dcb80b8557e10e2bed7322"


def test_v3_seal_unchanged():
    p = v4.V3
    assert p.exists()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == V3_SHA


def test_v4_render_deterministic_and_clean():
    ctx = v4.collect()
    h1 = v4.render(ctx)
    h2 = v4.render(ctx)
    assert h1 == h2  # byte-stable in memory
    low = h1.lower()
    assert "<script" not in low
    assert "://" not in h1
    assert "onclick" not in low
    # sealed key numbers must appear (machine-extracted at build time)
    for needle in ("14621.8788",
                   "1.7372701741044778e-294",
                   "0.0180",
                   "0.620526",
                   "20260927",
                   V3_SHA):
        assert needle in h1, needle
    assert h1.count('class="eq"') == 7
    assert h1.count("<svg") == 3
    assert h1.count('class="panel"') == 7


def test_v4_committed_html_matches_generator():
    assert v4.OUT.exists()
    ctx = v4.collect()
    assert v4.OUT.read_text(encoding="utf-8") == v4.render(ctx)


