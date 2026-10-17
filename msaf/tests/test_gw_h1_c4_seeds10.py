"""Unit tests for the C4 seeds10 extension tool.

Pre-registration: reports/C4_SEEDS10_PREREG_2026-10-17.md (seed identities
20261005..20261009 and the frozen analysis rules, declared before any draw).

Locks: (1) the declared series S10 = S5 + NEW_SEEDS; (2) the sealed
cross-check -- re-parsing the five original logs reproduces every number of
the frozen artifact; (3) once the five new logs exist, the committed S10
artifact equals a fresh extraction (self-validation of the machine artifact).
"""

import json
import os

import pytest

from msaf.gw_h1_extract import S5
from msaf.gw_h1_c4_seeds10 import (NEW_SEEDS, S10, S10_JSON, build,
                                   crosscheck_old5, new_log_path)


def test_declared_seed_series():
    assert NEW_SEEDS == [20261005, 20261006, 20261007, 20261008, 20261009]
    assert S10 == list(S5) + NEW_SEEDS
    assert len(S10) == 10 and len(set(S10)) == 10


def test_sealed_crosscheck_passes():
    cc = crosscheck_old5()
    failed = {k: v for k, v in cc["checks"].items() if not v}
    assert cc["all_match"], "sealed cross-check failed: %s" % failed


def test_committed_artifact_equals_fresh_extraction():
    if not all(os.path.exists(new_log_path(s)) for s in NEW_SEEDS):
        pytest.skip("new run logs not present yet (pre-registration state)")
    with open(S10_JSON, encoding="utf-8") as fh:
        committed = json.load(fh)
    fresh = build()
    assert committed["extension"] == fresh["extension"]
    assert committed["preregistration"]["doc"] == fresh["preregistration"]["doc"]
    assert committed["base"]["reparse_crosscheck"]["all_match"] is True
