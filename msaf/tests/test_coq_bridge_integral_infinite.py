# -*- coding: utf-8 -*-
"""Static CI guard for the Coq L5 infinite (unconditional) package
(formal_bridge/IntegralComparisonInfinite.v).

CI has no Coq toolchain: this guard locks content, statement shape and the
per-result audit map. It does not re-run the kernel. The kernel run is
recorded in ``IntegralComparisonInfinite.receipt.txt`` and pinned by registry
``A-2026-0014``.

The module imports the sealed Paket 7 finite-core module
(``IntegralComparison.v``, ``A-2026-0012``), the sealed Paket 8 conditional
limit module (``IntegralComparisonLimit.v``, ``A-2026-0013``) and the sealed
p-series module (``PseriesL2.v``, ``A-2026-0010``). It proves existence of the
three limits for ``f_k`` and combines them with Paket 8, giving the
unconditional pilot L5 statement.

Trusted base: stdlib axioms only. The expected per-result map is recorded
below; the main theorem carries the same four stdlib axioms as Paket 7/8
(``sig_forall_dec``, ``sig_not_dec``, ``functional_extensionality_dep``,
``Classical_Prop.classic``). No project axioms.
"""

from __future__ import annotations

import re
from pathlib import Path

from msaf.tests.test_coq_bridge_pilot import _strip_comments
from msaf.tests.test_coq_bridge_integral import _audit_sections

ROOT = Path(__file__).resolve().parents[2]
BRIDGE_DIR = ROOT / "formal_bridge"
SOURCE = BRIDGE_DIR / "IntegralComparisonInfinite.v"
RECEIPT = BRIDGE_DIR / "IntegralComparisonInfinite.receipt.txt"

EXPECTED_RESULTS = [
    "sum_f_R0_eq_sum_upto",
    "sum_f_R0_ext",
    "pterm_eq_fk",
    "psum_eq_sum_f_R0_fk",
    "psum_eq_tail_sum_succ",
    "Un_cv_ext_local",
    "Un_cv_tail_shift",
    "Un_cv_shift_succ",
    "tail_sum_cv",
    "fk_nonneg",
    "unit_val_nonneg",
    "whole_val_growing",
    "upper_sum_succ",
    "upper_sum_bound",
    "whole_val_bound",
    "whole_val_cv",
    "integral_comparison_power_infinite",
]

_ONE = {"ClassicalDedekindReals.sig_forall_dec"}
_TWO = {
    "ClassicalDedekindReals.sig_forall_dec",
    "FunctionalExtensionality.functional_extensionality_dep",
}
_THREE = {
    "ClassicalDedekindReals.sig_not_dec",
    "ClassicalDedekindReals.sig_forall_dec",
    "FunctionalExtensionality.functional_extensionality_dep",
}
_FOUR = {
    "ClassicalDedekindReals.sig_not_dec",
    "ClassicalDedekindReals.sig_forall_dec",
    "Classical_Prop.classic",
    "FunctionalExtensionality.functional_extensionality_dep",
}

# Exact per-result audit map, in source order.  Pure combinatorics on
# sums carry two Reals axioms; tail_sum_cv adds sig_not_dec through the
# p-series existence result; results that touch RiemannInt, Un_cv_crit
# or the Paket 8 conditional theorem carry the four-axiom set.
EXPECTED_AXIOM_MAP = [
    set(_TWO),    # sum_f_R0_eq_sum_upto
    set(_ONE),    # sum_f_R0_ext
    set(_TWO),    # pterm_eq_fk
    set(_TWO),    # psum_eq_sum_f_R0_fk
    set(_TWO),    # psum_eq_tail_sum_succ
    set(_TWO),    # Un_cv_ext_local
    set(_TWO),    # Un_cv_tail_shift
    set(_TWO),    # Un_cv_shift_succ
    set(_THREE),  # tail_sum_cv
    set(_TWO),    # fk_nonneg
    set(_FOUR),   # unit_val_nonneg
    set(_FOUR),   # whole_val_growing
    set(_TWO),    # upper_sum_succ
    set(_TWO),    # upper_sum_bound
    set(_FOUR),   # whole_val_bound
    set(_FOUR),   # whole_val_cv
    set(_FOUR),   # integral_comparison_power_infinite
]

ALLOWED_IMPORTS = {
    "Coq.Reals.Reals",
    "Coq.Reals.Rseries",
    "Coq.micromega.Lia",
    "Coq.micromega.Lra",
    "IntegralComparison",
    "IntegralComparisonLimit",
    "PseriesL2",
}

REQUIRED_NAMES = (
    "Un_cv_crit",
    "pseries_L2_integer",
    "sum_incr",
    "Un_growing",
    "bound",
    "tail_sum",
)

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
    r"^Theorem[ \t]+integral_comparison_power_infinite\b(.*?)^Proof\.",
    re.M | re.S,
)
AUDIT_MARKER = "--- coqc audit log (Print Assumptions) ---"

FORBIDDEN_NAMES = (
    "Rpower",
    "FTC_Riemann",
    "C1_fun",
    "RiemannInt_P",
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


def _missing_required(code: str) -> list[str]:
    return [
        name
        for name in REQUIRED_NAMES
        if not re.search(r"\b%s\b" % re.escape(name), code)
    ]


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
        "IntegralComparisonLimit",
        "PseriesL2",
    ):
        if needle not in imports:
            return "missing required import: %s" % needle
    return None


def _statement_violation(text: str) -> str | None:
    match = STATEMENT_RE.search(_strip_comments(text))
    if not match:
        return "theorem integral_comparison_power_infinite not found"
    statement = " ".join(match.group(1).split())
    for needle in (
        "forall (k N : nat) (HN : (1 <= N)%nat)",
        "(1 <= k)%nat ->",
        "exists L_N L_N1 L_S : R",
        "Un_cv (fun M => whole_val k N M HN) L_N",
        "Un_cv (fun M => whole_val k (N + 1) M (HN_succ N HN)) L_N1",
        "Un_cv (fun M => tail_sum k N M) L_S",
        "L_N1 <= L_S",
        "L_S <= L_N",
    ):
        if needle not in statement:
            return "statement lost %r" % needle
    for banned in ("Rpower", "int_", "FTC_Riemann", "RiemannInt_P", "forall L_N"):
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
    assert len(EXPECTED_RESULTS) == 17


def test_source_locks_the_unconditional_l5_statement():
    code = _strip_comments(SOURCE.read_text(encoding="utf-8"))
    violation = _imports_violation(code)
    assert violation is None, violation
    assert _forbidden_uses(code) == [], (
        "forbidden names in code: %s" % _forbidden_uses(code)
    )
    assert _missing_required(code) == [], (
        "missing required ingredients: %s" % _missing_required(code)
    )
    for needle in (
        "Definition tail_sum (k N M : nat) : R",
        "Lemma tail_sum_cv",
        "Lemma whole_val_cv",
        "Theorem integral_comparison_power_infinite",
    ):
        assert needle in code, "missing locked definition/statement: %r" % needle
    violation = _statement_violation(code)
    assert violation is None, violation


def test_receipt_records_kernel_success_and_exact_audit_map():
    log = RECEIPT.read_text(encoding="utf-8")
    for needle in (
        "coqc PseriesL2 (dependency) exit: 0",
        "coqc IntegralComparison (dependency) exit: 0",
        "coqc IntegralComparisonLimit (dependency) exit: 0",
        "coqc IntegralComparisonInfinite exit: 0",
        "coqchk exit: 0",
        "Modules were successfully checked",
        "results in IntegralComparisonInfinite.v: 17",
        "results checked by coqchk: 17",
        "Print Assumptions sections: 17 (17 Axioms, 0 Closed)",
        "OK: L5 infinite module kernel-checked",
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
        source.replace(
            "Definition tail_sum", "Axiom cheat : True.\nDefinition tail_sum", 1
        )
    ) is not None

    # 3. One Print Assumptions line removed.
    first_print = PRINT_RE.search(source)
    assert first_print is not None
    mutated_source = source[: first_print.start()] + source[first_print.end() :]
    assert _result_violation(mutated_source) is not None

    # 4. A forbidden analytic shortcut.
    assert _forbidden_uses(source + "\nCheck Rpower.\n") != []

    # 5. A forbidden integral shortcut.
    assert _forbidden_uses(source + "\nCheck FTC_Riemann.\n") != []

    # 6. A locked result renamed (coverage/order mismatch).
    renamed = source.replace("Lemma tail_sum_cv", "Lemma tail_sum_conv", 1)
    assert _result_violation(renamed) is not None

    # 7. Main statement weakened: the lower bound loses its non-strict form.
    weakened = source.replace("L_N1 <= L_S", "L_N1 < L_S", 1)
    assert _statement_violation(weakened) is not None

    # 8. The k >= 1 hypothesis removed from the main statement.
    unguarded = source.replace(
        "(1 <= k)%nat ->\n    exists L_N L_N1 L_S : R",
        "exists L_N L_N1 L_S : R",
        1,
    )
    assert _statement_violation(unguarded) is not None

    # 9. The three-limit existential collapsed to one.
    collapsed = source.replace("exists L_N L_N1 L_S : R", "exists L : R", 1)
    assert _statement_violation(collapsed) is not None

    # 10. Rpower smuggled into the statement.
    smuggled = source.replace(
        "Un_cv (fun M => tail_sum k N M) L_S",
        "Un_cv (fun M => Rpower (tail_sum k N M) 1) L_S",
        1,
    )
    assert _statement_violation(smuggled) is not None

    # 11. A fourth, project-specific assumption in the final block.
    tampered = [set(names) for names in sections]
    tampered[-1].add("MyProject.cheat")
    assert _trusted_base_violation(tampered) is not None

    # 12. Classical_Prop.classic silently dropped from the final block.
    tampered = [set(names) for names in sections]
    tampered[-1].discard("Classical_Prop.classic")
    assert _trusted_base_violation(tampered) is not None

    # 13. sig_not_dec appears in a section that should not carry it.
    tampered = [set(names) for names in sections]
    tampered[0].add("ClassicalDedekindReals.sig_not_dec")
    assert _trusted_base_violation(tampered) is not None

    # 14. One audit section removed.
    assert _trusted_base_violation(sections[:-1]) is not None

    # 15. Final section swapped with the two-axiom section.
    assert (
        _trusted_base_violation([sections[-1]] + sections[1:-1] + [sections[0]])
        is not None
    )

    # 16. Unterminated Coq comment.
    try:
        _strip_comments("(* unterminated")
    except AssertionError:
        pass
    else:
        raise AssertionError("unterminated comment was not rejected")

    # 17. Missing dependency import.
    no_dep = re.sub(
        r"^Require Import PseriesL2\.\n", "", source, count=1, flags=re.M
    )
    assert _imports_violation(_strip_comments(no_dep)) is not None

    # 18. The explicit convergence criterion removed.
    no_crit = source.replace("Un_cv_crit", "ConvergenceCriterion")
    assert _missing_required(_strip_comments(no_crit)) != []
