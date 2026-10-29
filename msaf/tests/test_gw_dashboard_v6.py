# -*- coding: utf-8 -*-
"""Regression tests for the v6 dashboard generator and the v3/v4/v5 seals.

Guards:
  * the v3 seal -- reports/gw_diagnostic_v3.html must stay byte-identical
    (sha256 89c7d5f9...);
  * the v4 seal -- reports/gw_diagnostic_v4.html must stay byte-identical
    (sha256 c9ec2621...);
  * the v5 seal -- reports/gw_diagnostic_v5.html must stay byte-identical
    (sha256 0e99571b...); the v6 page embeds this hash and the guard fails
    if either the v5 base page or the generator drifts;
  * v6 generation -- the generator reads the C4 S10 artefact, the dim-321
    lambda_min rung and the dim-501 (res4) artefacts, applies 13
    once-only patches to the v5 base, and the result is deterministic
    (byte-stable across reruns), with no JavaScript / external URLs /
    xmlns, and contains the sealed key numbers of panels 9 and 10 plus
    the recorded scope notes;
  * the committed HTML equals a fresh render (no drift between the
    committed artefact and the generator).
"""

import hashlib

from msaf import gw_dashboard_v5 as v5
from msaf import gw_dashboard_v6 as v6

V3_SHA = "89c7d5f948626bd51de06f37534bdc4941d3793353dcb80b8557e10e2bed7322"
V4_SHA = "c9ec26217f516a1a73527bc098addbc11a4935f6965d905d38a7dbeb7d95a8b6"
V5_SHA = "0e99571b887f17b95180edc478af7bf887cce861edfbc9fd2ac3b1a2798d4259"

NEEDLES = (
    # panel 9: C4 S10 extension (machine-extracted from the artefact)
    "11458/200000",
    "5.72900e-02",
    "6.44376e-24",
    "131.2879",
    "C4 S10 (10 seeds)",
    "pooled (10 \u00d7 20000)",
    "20261009",
    "ordering PASS",
    # panel 10: dim-501 outcome
    "UNDETERMINED at pivot 446",
    "dim 501 (Route S, N=250)",
    "1790.13",
    # dim-321 rung corrections (measured 2026-10-17)
    "3.123459e-59",
    "-0.000854",
    # recorded scope notes (owner decision 2026-10-18)
    "analytic justification at t=0 remains external",
    "Scope notes recorded in v6",
    # preserved seals quoted inside the page
    V5_SHA,
    V4_SHA,
    V3_SHA,
    "Rendered by msaf/gw_dashboard_v6.py",
)


def test_v3_seal_unchanged():
    p = v6.ROOT / "reports" / "gw_diagnostic_v3.html"
    assert p.exists()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == V3_SHA


def test_v4_seal_unchanged():
    assert v5.V4.exists()
    assert v5.v4.full_hash(v5.V4) == V4_SHA


def test_v5_seal_unchanged():
    assert v5.OUT.exists()
    assert v5.v4.full_hash(v5.OUT) == V5_SHA


def test_v6_render_deterministic_and_clean():
    h1 = v6.build()
    h2 = v6.build()
    assert h1 == h2  # byte-stable in memory
    low = h1.lower()
    assert "<script" not in low
    assert "://" not in h1
    assert "xmlns" not in low
    assert "onclick" not in low
    # sealed key numbers must appear (machine-extracted at build time)
    for needle in NEEDLES:
        assert needle in h1, needle
    # the pre-correction captions must not survive (dim-321 was measured
    # 2026-10-17; the v5 page is preserved separately, byte-identical)
    assert "dim 321 not yet run" not in h1
    assert "remains not run" not in h1
    assert h1.count('class="eq"') == 10
    assert h1.count("<svg") == 7
    assert h1.count('class="panel"') == 11
    assert h1.count("<footer>") == 1


def test_v6_committed_html_matches_generator():
    assert v6.OUT.exists()
    assert v6.OUT.read_text(encoding="utf-8") == v6.build()


