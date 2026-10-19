# -*- coding: utf-8 -*-
"""Static CI guard for the Coq conditional L2 bounds (formal_bridge/PseriesL2Bounds.v).

CI has no Coq toolchain: this guard locks content, statement shape and the
two-axiom audit. It does not re-run the kernel; the kernel run is recorded in
``PseriesL2Bounds.receipt.txt`` and pinned by registry ``A-2026-0011``.

``PseriesL2Bounds.v`` imports the frozen ``PseriesL2.v`` (``A-2026-0010``)
and proves the *conditional* bounds: given ``Un_cv`` convergence of the
p-series tail, the two-sided bound holds. It must NOT use the frozen
existence theorem ``pseries_L2_integer`` and must NOT use ``Un_cv_crit``:
the point of the package is to isolate the third stdlib axiom
(``ClassicalDedekindReals.sig_not_dec``, completeness of R) to the existence
step, so the conditional bounds rest on exactly the two stdlib axioms shared
by the other results of the frozen package.
"""

from __future__ import annotations

import re
from pathlib import Path

from msaf.tests.test_coq_bridge_pilot import ALLOWED_ASSUMPTIONS, _strip_comments

ROOT = Path(__file__).resolve().parents[2]
BRIDGE_DIR = ROOT / "formal_bridge"
SOURCE = BRIDGE_DIR / "PseriesL2Bounds.v"
RECEIPT = BRIDGE_DIR / "PseriesL2Bounds.receipt.txt"

RESULT_NAME = "pseries_L2_integer_bounds"

PLACEHOLDERS = re.compile(r"\b(admit|Admitted|Axiom|Parameter|Hypothesis|Abort)\b")
RESULT_RE = re.compile(
    r"^(?:Lemma|Theorem|Corollary|Remark|Proposition)[ \t]+"
    r"([A-Za-z_][A-Za-z0-9_]*)",
    re.M,
)
PRINT_RE = re.compile(
    r"^\s*Print\s+Assumptions\s+([A-Za-z_][A-Za-z0-9_]*)\s*\.", re.M
)
ASSUMPTION_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.']*)\s*:", re.M)
NON_ASSUMPTION_NAMES = {"OK", "Axioms", "coqc", "coqchk", "results", "Print"}
STATEMENT_RE = re.compile(
    r"^Theorem[ \t]+pseries_L2_integer_bounds\b(.*?)^Proof\.",
    re.M | re.S,
)


def _results(text: str) -> list[str]:
    return RESULT_RE.findall(_strip_comments(text))


def _prints(text: str) -> list[str]:
    return PRINT_RE.findall(_strip_comments(text))


def _placeholder(text: str) -> re.Match[str] | None:
    return PLACEHOLDERS.search(_strip_comments(text))


def _coverage_violation(text: str) -> str | None:
    results = _results(text)
    printed = _prints(text)
    if not results:
        return "no result found: the audit would be vacuous"
    if sorted(results) != sorted(printed):
        return "Print Assumptions coverage mismatch; results=%r printed=%r" % (
            sorted(results),
            sorted(printed),
        )
    return None


def _forbidden_uses(code: str) -> list[str]:
    """Names the conditional package must not touch (isolation of sig_not_dec)."""
    hits = []
    if re.search(r"\bUn_cv_crit\b", code):
        hits.append("Un_cv_crit")
    if re.search(r"\bpseries_L2_integer\b", code):
        hits.append("pseries_L2_integer")
    return hits


def _statement_violation(text: str) -> str | None:
    match = STATEMENT_RE.search(_strip_comments(text))
    if not match:
        return "theorem %s not found" % RESULT_NAME
    statement = " ".join(match.group(1).split())
    for needle in (
        "forall (k N : nat) (L : R),",
        "(1 <= k)%nat -> (1 <= N)%nat ->",
        "Un_cv (fun M => psum k N M) L ->",
        "1 / (INR k * (INR ((N + 1)%nat)) ^ k) <= L",
        "L <= 1 / (INR k * (INR N) ^ k)",
    ):
        if needle not in statement:
            return "statement lost %r" % needle
    if "exists L" in statement:
        return "statement must stay conditional (found 'exists L')"
    return None


def _assumption_blocks(log: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    for chunk in log.split("Axioms:")[1:]:
        names = [
            name
            for name in ASSUMPTION_RE.findall(chunk)
            if name not in NON_ASSUMPTION_NAMES
        ]
        blocks.append(names)
    return blocks


def _trusted_base_violation(blocks: list[list[str]]) -> str | None:
    """Exactly one audit block, exactly the two shared stdlib axioms."""
    if len(blocks) != 1:
        return "audit has %d blocks for 1 result" % len(blocks)
    names = set(blocks[0])
    if not names:
        return "block 1: empty assumption list"
    if names != ALLOWED_ASSUMPTIONS:
        return "block 1: assumption set mismatch %s" % sorted(names)
    return None


def test_source_has_no_placeholders():
    hit = _placeholder(SOURCE.read_text(encoding="utf-8"))
    assert hit is None, f"{SOURCE.name}: placeholder {hit.group(0)!r}"


def test_single_result_is_audited():
    text = SOURCE.read_text(encoding="utf-8")
    violation = _coverage_violation(text)
    assert violation is None, violation
    assert _results(text) == [RESULT_NAME], (
        "expected exactly [%r], got %r" % (RESULT_NAME, _results(text))
    )


def test_source_imports_frozen_module_and_isolates_completeness():
    code = _strip_comments(SOURCE.read_text(encoding="utf-8"))
    assert "Require Import PseriesL2." in code, "must import the frozen module"
    assert not re.search(r"^(?:Definition|Fixpoint)\s+(?:pterm|psum)\b", code, re.M), (
        "pterm/psum must come from the frozen module, not be redefined"
    )
    assert _forbidden_uses(code) == [], (
        "conditional bounds must not use %s" % _forbidden_uses(code)
    )


def test_statement_is_locked_conditional_bounds():
    violation = _statement_violation(SOURCE.read_text(encoding="utf-8"))
    assert violation is None, violation


def test_receipt_records_kernel_success_and_two_axiom_audit():
    log = RECEIPT.read_text(encoding="utf-8")
    for needle in (
        "coqc PseriesL2 exit: 0",
        "coqc PseriesL2Bounds exit: 0",
        "coqchk exit: 0",
        "Modules were successfully checked",
        "results in PseriesL2Bounds.v: 1",
        "results checked by coqchk: 1",
        "Print Assumptions blocks: 1",
        "OK: conditional bounds module kernel-checked",
    ):
        assert needle in log, f"receipt missing: {needle}"
    assert "ClassicalDedekindReals.sig_not_dec" not in log, (
        "the conditional bounds must not need sig_not_dec"
    )
    violation = _trusted_base_violation(_assumption_blocks(log))
    assert violation is None, violation
    assert re.search(r"^\s+%s$" % re.escape(RESULT_NAME), log, re.M), (
        "receipt does not list %s as kernel-checked" % RESULT_NAME
    )


def test_guard_rejects_mutations():
    """Negative path: the same detectors must catch tampering."""
    source = SOURCE.read_text(encoding="utf-8")
    receipt = RECEIPT.read_text(encoding="utf-8")
    blocks = _assumption_blocks(receipt)

    # 1. A bare Admitted.
    assert _placeholder(source + "\nAdmitted.\n") is not None

    # 2. A project axiom slipped before the theorem.
    assert _placeholder(
        source.replace(
            "Theorem pseries_L2_integer_bounds",
            "Axiom cheat : True.\nTheorem pseries_L2_integer_bounds",
            1,
        )
    ) is not None

    # 3. The Print Assumptions line removed.
    first_print = PRINT_RE.search(source)
    assert first_print is not None
    mutated_source = source[: first_print.start()] + source[first_print.end() :]
    assert _coverage_violation(mutated_source) is not None

    # 4. Completeness sneaks back in through Un_cv_crit.
    assert _forbidden_uses(source + "\nCheck Un_cv_crit.\n") != []

    # 5. The frozen existence theorem pulled in.
    assert _forbidden_uses(source + "\nCheck pseries_L2_integer.\n") != []

    # 6. Statement weakened (lower bound loses its equality case).
    weakened = source.replace("<= L", "< L", 1)
    assert _statement_violation(weakened) is not None

    # 7. Existence smuggled into the conditional statement.
    widened = source.replace(
        "Un_cv (fun M => psum k N M) L ->",
        "exists L : R, Un_cv (fun M => psum k N M) L ->",
        1,
    )
    assert _statement_violation(widened) is not None

    # 8. A fourth, project-specific assumption in the audit.
    tampered = [set(names) for names in blocks]
    tampered[0].add("MyProject.cheat")
    assert _trusted_base_violation(tampered) is not None

    # 9. One of the two shared axioms silently dropped.
    tampered = [set(names) for names in blocks]
    tampered[0].discard("ClassicalDedekindReals.sig_forall_dec")
    assert _trusted_base_violation(tampered) is not None

    # 10. sig_not_dec smuggled into the audit block.
    tampered = [set(names) for names in blocks]
    tampered[0].add("ClassicalDedekindReals.sig_not_dec")
    assert _trusted_base_violation(tampered) is not None

    # 11. Unterminated Coq comment.
    try:
        _strip_comments("(* unterminated")
    except AssertionError:
        pass
    else:
        raise AssertionError("unterminated comment was not rejected")
