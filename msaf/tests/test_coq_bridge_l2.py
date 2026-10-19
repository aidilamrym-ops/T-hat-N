# -*- coding: utf-8 -*-
"""Static CI guard for the Coq p-series L2 package (formal_bridge/PseriesL2.v).

CI has no Coq toolchain: this guard locks content, statement shape and audit
completeness. It does not re-run the kernel. The kernel run is recorded in
``PseriesL2.receipt.txt`` and pinned by registry ``A-2026-0010``.

The file is standalone (stdlib only): it must not import the geometric
bridge modules. The locked statement is integer ``p = k+1 >= 2`` only; real
exponents remain out of scope.

Trusted base: unlike the earlier packages, the existence step uses
``Un_cv_crit`` (completeness of R), whose proof depends on the standard
Coq.Reals axiom ``ClassicalDedekindReals.sig_not_dec``. The receipt therefore
records *three* stdlib axioms, not two. This is a documented deviation from
the original two-axiom prereg criterion, not a project axiom: the guard
requires ``sig_not_dec`` to appear **only** in the final block (the main
theorem) and rejects any other placement or any fourth assumption.
"""

from __future__ import annotations

import re
from pathlib import Path

from msaf.tests.test_coq_bridge_pilot import ALLOWED_ASSUMPTIONS, _strip_comments

ROOT = Path(__file__).resolve().parents[2]
BRIDGE_DIR = ROOT / "formal_bridge"
SOURCE = BRIDGE_DIR / "PseriesL2.v"
RECEIPT = BRIDGE_DIR / "PseriesL2.receipt.txt"

EXTRA_STDLIB_ASSUMPTIONS = {"ClassicalDedekindReals.sig_not_dec"}
ALLOWED_L2_ASSUMPTIONS = ALLOWED_ASSUMPTIONS | EXTRA_STDLIB_ASSUMPTIONS

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
    r"^Theorem[ \t]+pseries_L2_integer\b(.*?)^Proof\.",
    re.M | re.S,
)


def _results(text: str) -> list[str]:
    return RESULT_RE.findall(_strip_comments(text))


def _prints(text: str) -> list[str]:
    return PRINT_RE.findall(_strip_comments(text))


def _placeholder(text: str) -> re.Match[str] | None:
    return PLACEHOLDERS.search(_strip_comments(text))


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


def _trusted_base_violation(blocks: list[list[str]], n_results: int) -> str | None:
    """Return a human-readable violation, or ``None`` if the audit is locked."""
    if len(blocks) != n_results:
        return "audit has %d blocks for %d results" % (len(blocks), n_results)
    for index, names in enumerate(blocks, start=1):
        if not names:
            return "block %d: empty assumption list" % index
        extra = set(names) - ALLOWED_L2_ASSUMPTIONS
        if extra:
            return "block %d: non-standard assumptions %s" % (index, sorted(extra))
        has_extra_axiom = "ClassicalDedekindReals.sig_not_dec" in names
        if has_extra_axiom != (index == len(blocks)):
            return "block %d: sig_not_dec placement mismatch" % index
    return None


def test_source_has_no_placeholders():
    hit = _placeholder(SOURCE.read_text(encoding="utf-8"))
    assert hit is None, f"{SOURCE.name}: placeholder {hit.group(0)!r}"


def test_every_result_is_audited():
    text = SOURCE.read_text(encoding="utf-8")
    results = _results(text)
    printed = _prints(text)
    assert results, "no result found: the audit would be vacuous"
    assert len(results) == 20, f"expected 20 locked results, got {len(results)}"
    assert sorted(results) == sorted(printed), (
        "Print Assumptions coverage mismatch; results=%r printed=%r"
        % (sorted(results), sorted(printed))
    )


def test_source_is_standalone_and_states_the_locked_bounds():
    code = _strip_comments(SOURCE.read_text(encoding="utf-8"))
    assert "Require Import Coq.Reals.Reals." in code
    assert "Require Import Coq.Reals.Rseries." in code
    assert "GeometricBridge" not in code, "L2 must stay independent of the L1 bridge"
    assert "GeometricLimit" not in code, "L2 must stay independent of the L1 limit"
    assert not re.search(r"^(?:Fixpoint|Definition)\s+geom_sum\b", code, re.M)
    assert not re.search(r"^(?:Fixpoint|Definition)\s+geom_tail\b", code, re.M)

    match = STATEMENT_RE.search(code)
    assert match, "theorem pseries_L2_integer not found"
    statement = " ".join(match.group(1).split())
    assert "exists L : R" in statement
    assert "Un_cv (fun M => psum k N M) L" in statement
    assert "1 / (INR k * (INR ((N + 1)%nat)) ^ k) <= L" in statement
    assert "L <= 1 / (INR k * (INR N) ^ k)" in statement


def test_receipt_records_kernel_success_and_documented_trusted_base():
    log = RECEIPT.read_text(encoding="utf-8")
    for needle in (
        "coqc PseriesL2 exit: 0",
        "coqchk exit: 0",
        "Modules were successfully checked",
        "results in PseriesL2.v: 20",
        "results checked by coqchk: 20",
        "Print Assumptions blocks: 20",
        "OK: pseries L2 module kernel-checked",
    ):
        assert needle in log, f"receipt missing: {needle}"

    results = _results(SOURCE.read_text(encoding="utf-8"))
    blocks = _assumption_blocks(log)
    violation = _trusted_base_violation(blocks, len(results))
    assert violation is None, violation

    for name in results:
        assert re.search(r"^\s+%s$" % re.escape(name), log, re.M), (
            "receipt does not list %s as kernel-checked" % name
        )


def test_guard_rejects_mutations():
    """Negative path: the same detectors must catch tampering."""
    source = SOURCE.read_text(encoding="utf-8")
    receipt = RECEIPT.read_text(encoding="utf-8")
    results = _results(source)
    blocks = _assumption_blocks(receipt)

    # 1. A bare Admitted.
    assert _placeholder(source + "\nAdmitted.\n") is not None

    # 2. A project axiom slipped before a definition.
    assert _placeholder(
        source.replace("Definition pterm", "Axiom cheat : True.\nDefinition pterm", 1)
    ) is not None

    # 3. One Print Assumptions removed.
    first_print = PRINT_RE.search(source)
    assert first_print is not None
    mutated_source = source[: first_print.start()] + source[first_print.end() :]
    assert sorted(_results(mutated_source)) != sorted(_prints(mutated_source))

    # 4. A fourth, project-specific assumption.
    tampered = [set(names) for names in blocks]
    tampered[0].add("MyProject.cheat")
    assert _trusted_base_violation(tampered, len(results)) is not None

    # 5. sig_not_dec moved to a non-final block.
    tampered = [set(names) for names in blocks]
    tampered[0].add("ClassicalDedekindReals.sig_not_dec")
    assert _trusted_base_violation(tampered, len(results)) is not None

    # 6. sig_not_dec silently dropped from the final block.
    tampered = [set(names) for names in blocks]
    tampered[-1].discard("ClassicalDedekindReals.sig_not_dec")
    assert _trusted_base_violation(tampered, len(results)) is not None

    # 7. One audit block removed.
    assert _trusted_base_violation(blocks[:-1], len(results)) is not None

    # 8. Unterminated Coq comment.
    try:
        _strip_comments("(* unterminated")
    except AssertionError:
        pass
    else:
        raise AssertionError("unterminated comment was not rejected")
