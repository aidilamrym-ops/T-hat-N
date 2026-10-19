# -*- coding: utf-8 -*-
"""Static CI guard for the Coq geometric-limit pilot (formal_bridge/GeometricLimit.v).

CI has no Coq toolchain: this guard locks content and audit completeness,
it does not re-run the kernel. The kernel run is recorded in
``GeometricLimit.receipt.txt`` and pinned by registry ``A-2026-0009``.

The imported bridge file (``GeometricBridge.v``, A-2026-0008) is frozen and
must not be redefined here: the guard rejects a local ``geom_sum`` or
``geom_tail`` definition, so the limit proof always consumes the sealed
algebra instead of a private copy.
"""

from __future__ import annotations

import re
from pathlib import Path

from msaf.tests.test_coq_bridge_pilot import ALLOWED_ASSUMPTIONS, _strip_comments

ROOT = Path(__file__).resolve().parents[2]
BRIDGE_DIR = ROOT / "formal_bridge"
SOURCE = BRIDGE_DIR / "GeometricLimit.v"
RECEIPT = BRIDGE_DIR / "GeometricLimit.receipt.txt"

PLACEHOLDERS = re.compile(r"\b(admit|Admitted|Axiom|Parameter|Hypothesis|Abort)\b")
RESULT_RE = re.compile(
    r"^(?:Lemma|Theorem|Corollary|Remark|Proposition)[ \t]+"
    r"([A-Za-z_][A-Za-z0-9_]*)",
    re.M,
)
PRINT_RE = re.compile(
    r"^\s*Print\s+Assumptions\s+([A-Za-z_][A-Za-z0-9_]*)\s*\.", re.M
)
ASSUMPTION_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.']*)\s*:$", re.M)


def _results() -> list[str]:
    return RESULT_RE.findall(SOURCE.read_text(encoding="utf-8"))


def test_source_has_no_placeholders():
    stripped = _strip_comments(SOURCE.read_text(encoding="utf-8"))
    hit = PLACEHOLDERS.search(stripped)
    assert hit is None, f"{SOURCE.name}: placeholder {hit.group(0)!r}"


def test_every_result_is_audited():
    results = _results()
    printed = PRINT_RE.findall(SOURCE.read_text(encoding="utf-8"))
    assert results, "no result found: the audit would be vacuous"
    assert sorted(results) == sorted(printed), (
        "Print Assumptions coverage mismatch; results=%r printed=%r"
        % (sorted(results), sorted(printed))
    )


def test_imports_bridge_and_does_not_redefine_it():
    code = _strip_comments(SOURCE.read_text(encoding="utf-8"))
    assert re.search(r"^Require Import GeometricBridge\.$", code, re.M), (
        "GeometricLimit.v must import the sealed bridge module"
    )
    assert not re.search(
        r"^(?:Fixpoint|Definition)\s+geom_sum\b", code, re.M
    ), "geom_sum must not be redefined in the limit file"
    assert not re.search(
        r"^(?:Fixpoint|Definition)\s+geom_tail\b", code, re.M
    ), "geom_tail must not be redefined in the limit file"


def test_receipt_records_kernel_success_and_only_stdlib_axioms():
    log = RECEIPT.read_text(encoding="utf-8")
    assert "coqc GeometricBridge exit: 0" in log
    assert "coqc GeometricLimit exit: 0" in log
    assert "coqchk exit: 0" in log
    assert "Modules were successfully checked" in log

    blocks = [ASSUMPTION_RE.findall(chunk) for chunk in log.split("Axioms:")[1:]]
    results = _results()
    assert len(blocks) == len(results), (
        "frozen receipt covers %d of %d results -- an incomplete audit is "
        "a failure, not a pass" % (len(blocks), len(results))
    )
    for index, names in enumerate(blocks, start=1):
        assert names, f"block {index}: empty assumption list (audit not real)"
        extra = set(names) - ALLOWED_ASSUMPTIONS
        assert not extra, f"block {index}: non-standard assumptions {sorted(extra)}"

    for name in results:
        assert re.search(r"^\s+%s$" % re.escape(name), log, re.M), (
            "receipt does not list %s as kernel-checked" % name
        )
