"""Unit tests for the C4 seeds10 extension tool.

Pre-registration: reports/C4_SEEDS10_PREREG_2026-10-17.md (seed identities
20261005..20261009 and the frozen analysis rules, declared before any draw).

Locks: (1) the declared series S10 = S5 + NEW_SEEDS; (2) the sealed
cross-check -- re-parsing the five original logs reproduces every number of
the frozen artifact; (3) once the five new logs exist, the committed S10
artifact equals a fresh extraction (self-validation of the machine artifact):
exact on counts/labels, relative tolerance 1e-12 on floats.

Amendment note (2026-10-17, disclosed; see
reports/C4_SEEDS10_RESULTS_2026-10-17.md): lock (3) originally demanded
bit-exact float equality. CI run 39019056454 showed that scipy's beta.ppf is
not platform-bit-identical (Linux Python 3.14.8 vs Windows Python 3.14.4,
scipy 1.18.0 pinned on both): per_seed_cp95 differed by ~1 ULP while every
count, seed label, pooled statistic and classification string was identical.
The comparator below uses the same tolerance policy as the extractor's own
_close (rel_tol=1e-12).
"""

import json
import os

import pytest

from msaf.gw_h1_extract import S5
from msaf.gw_h1_c4_seeds10 import (NEW_SEEDS, S10, S10_JSON, build,
                                   crosscheck_old5, new_log_path)


def _tolerant_equal(a, b, rel_tol=1e-12):
    """Recursive equal for JSON-like trees: exact except float leaves.

    Ints, strings and bools must match exactly; floats may differ by up to
    rel_tol (same policy as gw_h1_c4_seeds10._close). Transcendental values
    (scipy beta.ppf) are not bit-identical across platforms and compilers,
    so bit-exact float equality is not a recoverable claim to test.
    """
    if isinstance(a, float) and isinstance(b, float):
        scale = max(abs(a), abs(b), 1e-300)
        return abs(a - b) <= rel_tol * scale
    if isinstance(a, dict):
        return (isinstance(b, dict) and a.keys() == b.keys()
                and all(_tolerant_equal(a[k], b[k], rel_tol) for k in a))
    if isinstance(a, list):
        return (isinstance(b, list) and len(a) == len(b)
                and all(_tolerant_equal(x, y, rel_tol)
                        for x, y in zip(a, b)))
    return a == b


def test_declared_seed_series():
    assert NEW_SEEDS == [20261005, 20261006, 20261007, 20261008, 20261009]
    assert S10 == list(S5) + NEW_SEEDS
    assert len(S10) == 10 and len(set(S10)) == 10


def test_sealed_crosscheck_passes():
    cc = crosscheck_old5()
    failed = {k: v for k, v in cc["checks"].items() if not v}
    assert cc["all_match"], "sealed cross-check failed: %s" % failed


def test_tolerant_comparator_semantics():
    assert _tolerant_equal(11458, 11458)
    assert not _tolerant_equal(11458, 11459)
    assert not _tolerant_equal("NOT STABLE", "NOT STABLE (edited)")
    one_ulp = 1.0 + 2.0 ** -52
    assert _tolerant_equal(1.0, one_ulp)
    assert not _tolerant_equal(1.0, 1.0 + 1e-6)
    assert _tolerant_equal([1, [2.0, "x"]], [1, [2.0 + 1e-15, "x"]])
    assert not _tolerant_equal([1, [2.0, "x"]], [1, [2.0, "y"]])
    assert not _tolerant_equal({"a": 1}, {"a": 1, "b": 2})
    assert _tolerant_equal({"k": [1262, 960], "p": 0.05729},
                           {"k": [1262, 960], "p": 0.05729})


def test_committed_artifact_equals_fresh_extraction():
    if not all(os.path.exists(new_log_path(s)) for s in NEW_SEEDS):
        pytest.skip("new run logs not present yet (pre-registration state)")
    with open(S10_JSON, encoding="utf-8") as fh:
        committed = json.load(fh)
    fresh = build()
    assert _tolerant_equal(committed["extension"], fresh["extension"])
    assert committed["preregistration"]["doc"] == fresh["preregistration"]["doc"]
    assert committed["base"]["reparse_crosscheck"]["all_match"] is True
