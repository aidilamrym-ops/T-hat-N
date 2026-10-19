# -*- coding: utf-8 -*-
"""Static CI guard for the Coq L5 finite-core package
(formal_bridge/IntegralComparison.v).

CI has no Coq toolchain: this guard locks content, statement shape and the
per-result audit map. It does not re-run the kernel. The kernel run is recorded
in ``IntegralComparison.receipt.txt`` and pinned by registry ``A-2026-0012``.

The file is standalone (stdlib only, including ``Coq.Reals.RiemannInt``). It
proves the finite L5 comparison for ``f_k(x) = 1/x^(k+1)``; the infinite
integral, the limit step, general ``f``, real exponents, L3/L4 and the
periodic-box ``[J]`` study are out of scope.

Trusted base: the prereg expected three stdlib axioms, but the Riemann integral
machinery also introduces ``Classical_Prop.classic``. The receipt records four
stdlib axioms, no project axioms. This is a documented deviation, not a scope
change.
"""

from __future__ import annotations

import re
from pathlib import Path

from msaf.tests.test_coq_bridge_pilot import ALLOWED_ASSUMPTIONS, _strip_comments

ROOT = Path(__file__).resolve().parents[2]
BRIDGE_DIR = ROOT / "formal_bridge"
SOURCE = BRIDGE_DIR / "IntegralComparison.v"
RECEIPT = BRIDGE_DIR / "IntegralComparison.receipt.txt"

EXTRA_STDLIB_ASSUMPTIONS = {
    "ClassicalDedekindReals.sig_not_dec",
    "Classical_Prop.classic",
}
ALLOWED_L5_ASSUMPTIONS = ALLOWED_ASSUMPTIONS | EXTRA_STDLIB_ASSUMPTIONS

EXPECTED_RESULTS = [
    "endN_eq_add",
    "endN_succ_eq",
    "le_endN",
    "INR_pos_of_ge1",
    "continuity_pt_fk",
    "sum_upto_le",
    "sum_upto_ext",
    "RiemannInt_degenerate",
    "whole_val_split",
    "whole_val_eq_sum",
    "INR_endN_length",
    "integral_unit_upper",
    "integral_unit_lower",
    "integral_comparison_power_finite",
]

_TWO = {"ClassicalDedekindReals.sig_forall_dec",
        "FunctionalExtensionality.functional_extensionality_dep"}
_FOUR = {
    "ClassicalDedekindReals.sig_not_dec",
    "ClassicalDedekindReals.sig_forall_dec",
    "Classical_Prop.classic",
    "FunctionalExtensionality.functional_extensionality_dep",
}

# Exact per-result audit map, in source order. Three arithmetic helpers are
# closed; the two-axiom entries are the basic Reals lemmas; the four-axiom
# entries are the Riemann-integral results. The final entry is the main theorem.
EXPECTED_AXIOM_MAP = [
    set(),
    set(),
    set(),
    set(_TWO),
    set(_TWO),
    set(_TWO),
    {"ClassicalDedekindReals.sig_forall_dec"},
    set(_FOUR),
    set(_FOUR),
    set(_FOUR),
    set(_TWO),
    set(_FOUR),
    set(_FOUR),
    set(_FOUR),
]

ALLOWED_IMPORTS = {
    "Coq.Reals.Reals",
    "Coq.Reals.RiemannInt",
    "Coq.Reals.Ranalysis1",
    "Coq.Reals.Rfunctions",
    "Coq.micromega.Lia",
    "Coq.micromega.Lra",
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
ASSUMPTION_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.']*)\s*:", re.M)
NON_ASSUMPTION_NAMES = {"OK", "Axioms", "coqc", "coqchk", "results", "Print"}
STATEMENT_RE = re.compile(
    r"^Theorem[ \t]+integral_comparison_power_finite\b(.*?)^Proof\.",
    re.M | re.S,
)
AUDIT_MARKER = "--- coqc audit log (Print Assumptions) ---"


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
    for name in (
        "FTC_Riemann",
        "C1_fun",
        "Rpower",
        "Un_cv_crit",
        "pseries_L2_integer",
        "PseriesL2",
        "GeometricBridge",
        "GeometricLimit",
    ):
        if re.search(r"\b%s\b" % re.escape(name), code):
            hits.append(name)
    return hits


def _imports_violation(code: str) -> str | None:
    imports = re.findall(r"^Require Import ([A-Za-z0-9_.]+)\.", code, re.M)
    extra = set(imports) - ALLOWED_IMPORTS
    if extra:
        return "non-stdlib import(s): %s" % sorted(extra)
    for needle in (
        "Coq.Reals.Reals",
        "Coq.Reals.RiemannInt",
        "Coq.Reals.Ranalysis1",
        "Coq.Reals.Rfunctions",
    ):
        if needle not in imports:
            return "missing stdlib import: %s" % needle
    return None


def _statement_violation(text: str) -> str | None:
    match = STATEMENT_RE.search(_strip_comments(text))
    if not match:
        return "theorem integral_comparison_power_finite not found"
    statement = " ".join(match.group(1).split())
    for needle in (
        "forall (k N M : nat) (HN : (1 <= N)%nat),",
        "(1 <= k)%nat ->",
        "whole_val k N M HN",
        "whole_val k N M HN <= sum_upto (fun i => fk k (INR (N + i))) M",
        "sum_upto (fun i => fk k (INR (N + i + 1))) M <= whole_val k N M HN",
    ):
        if needle not in statement:
            return "statement lost %r" % needle
    for banned in ("Un_cv", "Rpower", "exists L", "int_"):
        if banned in statement:
            return "statement contains banned %r" % banned
    return None


def _audit_sections(log: str) -> list[list[str]]:
    """Parse the receipt's audit log into one section per result.

    A section is either an empty list (Coq reported "Closed under the global
    context") or the list of axiom names in an "Axioms:" block. The source's
    Print Assumptions order defines the association.
    """
    if AUDIT_MARKER not in log:
        return []
    body = log.split(AUDIT_MARKER, 1)[1]
    lines = body.splitlines()
    sections: list[list[str]] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line == "Closed under the global context":
            sections.append([])
            i += 1
            continue
        if line == "Axioms:":
            i += 1
            block: list[str] = []
            while i < len(lines):
                inner = lines[i].strip()
                if inner in ("Axioms:", "Closed under the global context"):
                    break
                match = re.match(r"^([A-Za-z_][A-Za-z0-9_.']*)\s*:", lines[i])
                if match and match.group(1) not in NON_ASSUMPTION_NAMES:
                    block.append(match.group(1))
                i += 1
            sections.append(block)
            continue
        i += 1
    return sections


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
    if set(sections[-1]) != ALLOWED_L5_ASSUMPTIONS:
        return "final section is not the exact four-axiom stdlib set"
    return None


def test_source_has_no_placeholders():
    hit = _placeholder(SOURCE.read_text(encoding="utf-8"))
    assert hit is None, f"{SOURCE.name}: placeholder {hit.group(0)!r}"


def test_every_result_is_audited_in_source_order():
    text = SOURCE.read_text(encoding="utf-8")
    violation = _result_violation(text)
    assert violation is None, violation
    assert len(EXPECTED_RESULTS) == 14


def test_source_is_standalone_and_locks_the_finite_statement():
    code = _strip_comments(SOURCE.read_text(encoding="utf-8"))
    violation = _imports_violation(code)
    assert violation is None, violation
    assert _forbidden_uses(code) == [], (
        "forbidden names in code: %s" % _forbidden_uses(code)
    )
    for needle in (
        "Definition fk (k : nat) (x : R) : R := / (x ^ S k).",
        "Fixpoint sum_upto (g : nat -> R) (M : nat) : R :=",
        "Fixpoint endN (N M : nat) : nat :=",
        "Definition unit_val (k N i : nat) (HN : (1 <= N)%nat) : R :=",
        "Definition whole_val (k N M : nat) (HN : (1 <= N)%nat) : R :=",
        "Theorem integral_comparison_power_finite",
    ):
        assert needle in code, "missing locked definition/statement: %r" % needle
    violation = _statement_violation(code)
    assert violation is None, violation


def test_receipt_records_kernel_success_and_exact_audit_map():
    log = RECEIPT.read_text(encoding="utf-8")
    for needle in (
        "coqc IntegralComparison exit: 0",
        "coqchk exit: 0",
        "Modules were successfully checked",
        "results in IntegralComparison.v: 14",
        "results checked by coqchk: 14",
        "Print Assumptions sections: 14 (11 Axioms, 3 Closed)",
        "OK: L5 finite-core module kernel-checked",
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
        source.replace("Definition fk", "Axiom cheat : True.\nDefinition fk", 1)
    ) is not None

    # 3. One Print Assumptions line removed.
    first_print = PRINT_RE.search(source)
    assert first_print is not None
    mutated_source = source[: first_print.start()] + source[first_print.end() :]
    assert _result_violation(mutated_source) is not None

    # 4. A forbidden integral shortcut.
    assert _forbidden_uses(source + "\nCheck FTC_Riemann.\n") != []

    # 5. A forbidden real-exponent shortcut.
    assert _forbidden_uses(source + "\nCheck Rpower.\n") != []

    # 6. A forbidden completeness shortcut.
    assert _forbidden_uses(source + "\nCheck Un_cv_crit.\n") != []

    # 7. A forbidden frozen-module import.
    assert _forbidden_uses(source + "\nRequire Import PseriesL2.\n") != []

    # 8. A locked result renamed (coverage/order mismatch).
    renamed = source.replace("Lemma sum_upto_ext", "Lemma sum_upto_extra", 1)
    assert _result_violation(renamed) is not None

    # 9. Statement weakened: the upper bound loses its non-strict form.
    weakened = source.replace(
        "<= sum_upto (fun i => fk k (INR (N + i))) M",
        "< sum_upto (fun i => fk k (INR (N + i))) M",
        1,
    )
    assert _statement_violation(weakened) is not None

    # 10. The k >= 1 hypothesis removed.
    unguarded = source.replace("(1 <= k)%nat ->", "", 1)
    assert _statement_violation(unguarded) is not None

    # 11. A fourth, project-specific assumption in the final block.
    tampered = [set(names) for names in sections]
    tampered[-1].add("MyProject.cheat")
    assert _trusted_base_violation(tampered) is not None

    # 12. Classical_Prop.classic silently dropped from the final block.
    tampered = [set(names) for names in sections]
    tampered[-1].discard("Classical_Prop.classic")
    assert _trusted_base_violation(tampered) is not None

    # 13. sig_not_dec moved into a closed section.
    tampered = [set(names) for names in sections]
    tampered[0].add("ClassicalDedekindReals.sig_not_dec")
    assert _trusted_base_violation(tampered) is not None

    # 14. One audit section removed.
    assert _trusted_base_violation(sections[:-1]) is not None

    # 15. Final section swapped with a closed section.
    assert _trusted_base_violation([sections[-1]] + sections[1:-1] + [sections[0]]) is not None

    # 16. Unterminated Coq comment.
    try:
        _strip_comments("(* unterminated")
    except AssertionError:
        pass
    else:
        raise AssertionError("unterminated comment was not rejected")
