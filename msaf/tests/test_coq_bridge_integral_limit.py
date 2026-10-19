# -*- coding: utf-8 -*-
"""Static CI guard for the Coq L5 limit-step package
(formal_bridge/IntegralComparisonLimit.v).

CI has no Coq toolchain: this guard locks content, statement shape and the
per-result audit map. It does not re-run the kernel. The kernel run is
recorded in ``IntegralComparisonLimit.receipt.txt`` and pinned by registry
``A-2026-0013``.

The module imports the sealed Paket 7 finite-core module
(``IntegralComparison.v``, registry ``A-2026-0012``). It proves the L5 limit
comparison **conditionally**: the three ``Un_cv`` limits are hypotheses.
Existence of the limits (the unconditional L5 for ``f_k``) is Paket 9 and is
out of scope here.

Trusted base: the same four stdlib axioms as Paket 7
(``sig_forall_dec``, ``sig_not_dec``, ``functional_extensionality_dep``,
``Classical_Prop.classic``). No project axioms.
"""

from __future__ import annotations

import re
from pathlib import Path

from msaf.tests.test_coq_bridge_pilot import ALLOWED_ASSUMPTIONS, _strip_comments
from msaf.tests.test_coq_bridge_integral import _audit_sections

ROOT = Path(__file__).resolve().parents[2]
BRIDGE_DIR = ROOT / "formal_bridge"
SOURCE = BRIDGE_DIR / "IntegralComparisonLimit.v"
RECEIPT = BRIDGE_DIR / "IntegralComparisonLimit.receipt.txt"

EXPECTED_RESULTS = [
    "Un_cv_le",
    "tail_sum_le_whole",
    "whole_succ_le_tail_sum",
    "integral_comparison_power_limit",
]

_TWO = {
    "ClassicalDedekindReals.sig_forall_dec",
    "FunctionalExtensionality.functional_extensionality_dep",
}
_FOUR = {
    "ClassicalDedekindReals.sig_not_dec",
    "ClassicalDedekindReals.sig_forall_dec",
    "Classical_Prop.classic",
    "FunctionalExtensionality.functional_extensionality_dep",
}

# Exact per-result audit map, in source order.  Un_cv_le is a pure
# order-limit lemma (two Reals axioms); the two finite bounds and the main
# theorem go through RiemannInt and therefore carry the four-axiom set.
EXPECTED_AXIOM_MAP = [
    set(_TWO),
    set(_FOUR),
    set(_FOUR),
    set(_FOUR),
]

ALLOWED_IMPORTS = {
    "Coq.Reals.Reals",
    "Coq.Reals.Rseries",
    "Coq.micromega.Lia",
    "Coq.micromega.Lra",
    "IntegralComparison",
}

PLACEHOLDERS = re.compile(r"\b(admit|Admitted|Axiom|Parameter|Hypothesis|Abort)\b")
RESULT_RE = re.compile(
    r"^(?:Lemma|Theorem|Corollary|Remark|Proposition)[ \t]+"
    r"([A-Za-z_][A-Za-z0-9_]*)",
    re.M,
)
PRINT_RE = re.compile(
    r"^\s*Print\s+Assumptions\s+([A-Za-z_][A-Za-z0-9_]*)\s*\.", re.M
)
STATEMENT_RE = re.compile(
    r"^Theorem[ \t]+integral_comparison_power_limit\b(.*?)^Proof\.",
    re.M | re.S,
)
AUDIT_MARKER = "--- coqc audit log (Print Assumptions) ---"

FORBIDDEN_NAMES = (
    "Un_cv_crit",
    "pseries_L2_integer",
    "PseriesL2",
    "Rpower",
    "FTC_Riemann",
    "C1_fun",
    "GeometricBridge",
    "GeometricLimit",
)


def _results(text: str) -> list[str]:
    return RESULT_RE.findall(_strip_comments(text))


def _prints(text: str) -> list[str]:
    return PRINT_RE.findall(_strip_comments(text))


def _placeholder(text: str) -> re.Match[str] | None:
    return PLACEHOLDERS.search(_strip_comments(text))


def _result_violation(text: str) -> str | None:
    results = _results(text)
    prints = _prints(text)
    if results != EXPECTED_RESULTS:
        return "locked result list/order mismatch; got %r" % (results,)
    if prints != results:
        return "Print Assumptions coverage/order mismatch; results=%r printed=%r" % (
            results,
            prints,
        )
    return None


def _forbidden_uses(code: str) -> list[str]:
    hits = []
    for name in FORBIDDEN_NAMES:
        if re.search(r"\b%s\b" % re.escape(name), code):
            hits.append(name)
    return hits


def _imports_violation(code: str) -> str | None:
    imports = re.findall(r"^Require Import ([A-Za-z0-9_.]+)\.", code, re.M)
    extra = set(imports) - ALLOWED_IMPORTS
    if extra:
        return "non-allowlisted import(s): %s" % sorted(extra)
    for needle in (
        "Coq.Reals.Reals",
        "Coq.Reals.Rseries",
        "Coq.micromega.Lia",
        "Coq.micromega.Lra",
        "IntegralComparison",
    ):
        if needle not in imports:
            return "missing required import: %s" % needle
    return None


def _statement_violation(text: str) -> str | None:
    match = STATEMENT_RE.search(_strip_comments(text))
    if not match:
        return "theorem integral_comparison_power_limit not found"
    statement = " ".join(match.group(1).split())
    for needle in (
        "forall (k N : nat) (HN : (1 <= N)%nat) (Hk : (1 <= k)%nat)",
        "(L_N L_N1 L_S : R)",
        "Un_cv (fun M => whole_val k N M HN) L_N",
        "Un_cv (fun M => whole_val k (N + 1) M (HN_succ N HN)) L_N1",
        "Un_cv (fun M => sum_upto (fun i => fk k (INR (N + 1 + i))) M) L_S",
        "L_N1 <= L_S",
        "L_S <= L_N",
    ):
        if needle not in statement:
            return "statement lost %r" % needle
    for banned in ("exists", "Un_cv_crit", "PseriesL2", "Rpower", "int_"):
        if banned in statement:
            return "statement contains banned %r" % banned
    return None


def _trusted_base_violation(sections: list[list[str]]) -> str | None:
    """Exactly one section per locked result, with the exact axiom map."""
    if len(sections) != len(EXPECTED_RESULTS):
        return "audit has %d sections for %d results" % (
            len(sections),
            len(EXPECTED_RESULTS),
        )
    for index, (names, expected) in enumerate(zip(sections, EXPECTED_AXIOM_MAP), 1):
        got = set(names)
        if got != expected:
            return "section %d (%s): axiom set %s != %s" % (
                index,
                EXPECTED_RESULTS[index - 1],
                sorted(got),
                sorted(expected),
            )
    if set(sections[-1]) != _FOUR:
        return "final section is not the exact four-axiom stdlib set"
    return None


def test_source_has_no_placeholders():
    hit = _placeholder(SOURCE.read_text(encoding="utf-8"))
    assert hit is None, f"{SOURCE.name}: placeholder {hit.group(0)!r}"


def test_every_result_is_audited_in_source_order():
    text = SOURCE.read_text(encoding="utf-8")
    violation = _result_violation(text)
    assert violation is None, violation
    assert len(EXPECTED_RESULTS) == 4


def test_source_locks_the_conditional_limit_statement():
    code = _strip_comments(SOURCE.read_text(encoding="utf-8"))
    violation = _imports_violation(code)
    assert violation is None, violation
    assert _forbidden_uses(code) == [], (
        "forbidden names in code: %s" % _forbidden_uses(code)
    )
    for needle in (
        "Definition HN_succ (N : nat) (HN : (1 <= N)%nat) : (1 <= N + 1)%nat",
        "Lemma Un_cv_le",
        "Lemma tail_sum_le_whole",
        "Lemma whole_succ_le_tail_sum",
        "Theorem integral_comparison_power_limit",
    ):
        assert needle in code, "missing locked definition/statement: %r" % needle
    violation = _statement_violation(code)
    assert violation is None, violation


def test_receipt_records_kernel_success_and_exact_audit_map():
    log = RECEIPT.read_text(encoding="utf-8")
    for needle in (
        "coqc IntegralComparison (dependency) exit: 0",
        "coqc IntegralComparisonLimit exit: 0",
        "coqchk exit: 0",
        "Modules were successfully checked",
        "results in IntegralComparisonLimit.v: 4",
        "results checked by coqchk: 4",
        "Print Assumptions sections: 4 (4 Axioms, 0 Closed)",
        "OK: L5 limit-step module kernel-checked",
    ):
        assert needle in log, f"receipt missing: {needle}"
    sections = _audit_sections(log)
    violation = _trusted_base_violation(sections)
    assert violation is None, violation
    for name in EXPECTED_RESULTS:
        assert re.search(r"^\s{2}%s$" % re.escape(name), log, re.M), (
            "receipt does not list %s as kernel-checked" % name
        )
    assert "Classical_Prop.classic" in log
    assert "MyProject" not in log


def test_guard_rejects_mutations():
    """Negative path: the same detectors must catch tampering."""
    source = SOURCE.read_text(encoding="utf-8")
    log = RECEIPT.read_text(encoding="utf-8")
    sections = _audit_sections(log)

    # 1. A bare Admitted.
    assert _placeholder(source + "\nAdmitted.\n") is not None

    # 2. A project axiom slipped before the definitions.
    assert _placeholder(
        source.replace("Definition HN_succ", "Axiom cheat : True.\nDefinition HN_succ", 1)
    ) is not None

    # 3. One Print Assumptions line removed.
    first_print = PRINT_RE.search(source)
    assert first_print is not None
    mutated_source = source[: first_print.start()] + source[first_print.end() :]
    assert _result_violation(mutated_source) is not None

    # 4. A forbidden completeness shortcut.
    assert _forbidden_uses(source + "\nCheck Un_cv_crit.\n") != []

    # 5. A forbidden frozen-module import.
    assert _forbidden_uses(source + "\nRequire Import PseriesL2.\n") != []

    # 6. A locked result renamed (coverage/order mismatch).
    renamed = source.replace("Lemma Un_cv_le", "Lemma Un_cv_leq", 1)
    assert _result_violation(renamed) is not None

    # 7. Main statement weakened: the lower bound loses its non-strict form.
    weakened = source.replace("L_N1 <= L_S", "L_N1 < L_S", 1)
    assert _statement_violation(weakened) is not None

    # 8. The k >= 1 hypothesis removed from the main statement.
    unguarded = source.replace("(Hk : (1 <= k)%nat)", "(Hk : True)", 1)
    assert _statement_violation(unguarded) is not None

    # 9. The statement claims existence (unconditional L5 would be Paket 9).
    overclaimed = source.replace(
        "L_N1 <= L_S /\\ L_S <= L_N.",
        "exists L, Un_cv (fun M => whole_val k N M HN) L.",
        1,
    )
    assert _statement_violation(overclaimed) is not None

    # 10. A fourth, project-specific assumption in the final block.
    tampered = [set(names) for names in sections]
    tampered[-1].add("MyProject.cheat")
    assert _trusted_base_violation(tampered) is not None

    # 11. Classical_Prop.classic silently dropped from the final block.
    tampered = [set(names) for names in sections]
    tampered[-1].discard("Classical_Prop.classic")
    assert _trusted_base_violation(tampered) is not None

    # 12. sig_not_dec moved into a closed section.
    tampered = [set(names) for names in sections]
    tampered[0].add("ClassicalDedekindReals.sig_not_dec")
    assert _trusted_base_violation(tampered) is not None

    # 13. One audit section removed.
    assert _trusted_base_violation(sections[:-1]) is not None

    # 14. Final section swapped with the two-axiom section.
    assert _trusted_base_violation([sections[-1]] + sections[1:-1] + [sections[0]]) is not None

    # 15. Unterminated Coq comment.
    try:
        _strip_comments("(* unterminated")
    except AssertionError:
        pass
    else:
        raise AssertionError("unterminated comment was not rejected")

    # 16. Missing dependency import.
    no_dep = re.sub(
        r"^Require Import IntegralComparison\.\n", "", source, count=1, flags=re.M
    )
    assert _imports_violation(_strip_comments(no_dep)) is not None
