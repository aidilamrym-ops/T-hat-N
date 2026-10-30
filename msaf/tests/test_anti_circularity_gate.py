# -*- coding: utf-8 -*-
"""CI guard for the scoped anti-circularity gate run (registry A-2026-0015).

The external gate is a local skill script; CI does not have it. This guard
therefore does three things and nothing more:

* mirrors the gate's placeholder patterns over the four Lean kernel sources;
* freezes the conditional spec at its nine declared axioms, with no
  ``sorry``/``admit``/``Abort`` in code;
* locks the recorded run log and report to the kernel-only scope, so a log
  edit cannot silently turn the SMT or spec sub-gates into a claimed PASS.

It never claims the external gate ran in CI, and it never claims a Lean
theorem is proved.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

from msaf.tests.test_lean_axiom_audit import _lean_sources, _strip_comments

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "reports" / "anti_circularity_gate_2026-10-20.log"
REPORT = ROOT / "reports" / "ANTI_CIRCULARITY_GATE_RUN_2026-10-20.md"
RUNNER = ROOT / "harness" / "run_anti_circularity_gate.py"
SPEC_DIR = ROOT / "lean" / "spec"

KERNEL = (
    "lean/ComplexMoore.lean",
    "lean/EnclosureData.lean",
    "lean/NavierStokesCore.lean",
    "lean/NewtonExistence.lean",
    "lean/Russell.lean",
    "lean/Stage_2_Tail_Bound.lean",
    "lean/Stage_3_Eigenvalue_Locking.lean",
    "lean/Stage_5_EntryError_Perturbation.lean",
    "lean/Stage_6_Analytic_Tail.lean",
    "lean/Stage_7_Tail_Extension.lean",
    "lean/Theory137.lean",
    "lean/XiNoRealZero.lean",
)

# Stage 2/3/5/6 are finite scaffold modules added after the 2026-10-20 gate
# run.  The recorded log still describes its four-file kernel-only scope;
# these four files are checked for placeholders here but are NOT retroactively
# folded into that historical log.
SCAFFOLD = ()

SPEC_AXIOM_BUDGET = 9

# Same four patterns as the external gate's PLACEHOLDERS table.
PLACEHOLDERS = (
    (re.compile(r"\bsorry\b"), "sorry"),
    (re.compile(r"\badmit\b"), "admit"),
    (re.compile(r"^[ \t]*axiom\b", re.M), "axiom"),
    (re.compile(r"\bAbort\b"), "Abort"),
)


def _placeholders(text: str) -> list[tuple[str, int]]:
    """Return ``(label, line)`` for each gate placeholder in code."""
    stripped = _strip_comments(text)
    hits: list[tuple[str, int]] = []
    for pattern, label in PLACEHOLDERS:
        for match in pattern.finditer(stripped):
            hits.append((label, stripped.count("\n", 0, match.start()) + 1))
    return hits


def _scope_violation(kernel: tuple[str, ...]) -> str | None:
    actual = sorted(
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / "lean").glob("*.lean")
    )
    expected = sorted(kernel)
    if actual != expected:
        return "kernel scope drift: glob=%r explicit=%r" % (actual, expected)
    for rel in kernel:
        if not (ROOT / rel).is_file():
            return "missing kernel file: %s" % rel
    return None


def _spec_budget_violation(texts: list[str]) -> str | None:
    axioms = 0
    other: list[tuple[str, int]] = []
    for text in texts:
        for label, line in _placeholders(text):
            if label == "axiom":
                axioms += 1
            else:
                other.append((label, line))
    if axioms != SPEC_AXIOM_BUDGET:
        return "spec axiom budget %d != %d" % (axioms, SPEC_AXIOM_BUDGET)
    if other:
        return "non-axiom placeholder in spec: %r" % (other,)
    return None


def _log_violation(log: str) -> str | None:
    for needle in (
        "kernel_files=4",
        "spec_axioms=9",
        "smt2_files=0",
        "audit_subgate=NOT_INVOKED_NO_SMT2",
        "kernel_lean_exit=0",
        "kernel_check_exit=0",
        "spec_diagnostic_exit=1",
        "spec_diagnostic_expected=FAIL=9",
        "kernel_gate=PASS",
        "scope=LEAN_KERNEL_ONLY",
    ):
        if needle not in log:
            return "log missing %r" % needle
    if log.count("ANTI-CIRCULARITY GATE [lean]") != 2:
        return "expected two [lean] sections (kernel + spec diagnostic)"
    if log.count("ANTI-CIRCULARITY GATE [check]") != 1:
        return "expected one [check] section"
    if log.count("result: FAIL=0  NOT_RUN=0  SKIP=0") != 2:
        return "expected two clean PASS result lines"
    if log.count("result: FAIL=9  NOT_RUN=0  SKIP=0") != 1:
        return "expected one spec diagnostic FAIL=9 line"
    if log.count("verdict: PASS") != 2:
        return "expected exactly two PASS verdicts"
    if log.count("verdict: FAIL") != 1:
        return "expected exactly one diagnostic FAIL verdict"
    for banned in (
        "kernel_gate=FAIL",
        "kernel_gate=TOOL_NOT_RUN",
        "audit_subgate=PASS",
        "SMT audit PASS",
        "spec_diagnostic_exit=0",
    ):
        if banned in log:
            return "log contains forbidden claim %r" % banned
    return None


def _report_violation(report: str) -> str | None:
    low = report.lower()
    for needle in (
        "pass for scope source lean kernel",
        "lean/spec/",
        "out of scope",
        "9 aksioma deklaratif",
        "sub-gate audit",
        "no dipanggil",
        "verifikasi ulang paket 8/9",
        "tool not run",
    ):
        if needle not in low:
            return "report missing scope needled %r" % needle
    for banned in (
        "rh terbukti",
        "pâ‰ np terbukti",
        "smt audit pass",
        "semua teorema lean terbukti",
        "coq sekarang lean-verified",
    ):
        if banned in low:
            return "report contains forbidden claim %r" % banned
    return None


def test_kernel_sources_are_placeholder_free() -> None:
    violation = _scope_violation(KERNEL + SCAFFOLD)
    assert violation is None, violation
    sources = _lean_sources()
    assert len(sources) == 12, "expected kernel + scaffold + Russell + Theory137 + EnclosureData Lean sources"
    for path in sources:
        hits = _placeholders(path.read_text(encoding="utf-8"))
        assert not hits, "%s: placeholders %r" % (path.name, hits)


def test_spec_budget_is_frozen_and_spec_is_conditional() -> None:
    spec_files = sorted(SPEC_DIR.glob("*.lean"))
    assert len(spec_files) == 3, "expected three spec Lean files"
    texts = [p.read_text(encoding="utf-8") for p in spec_files]
    violation = _spec_budget_violation(texts)
    assert violation is None, violation
    analytic = (SPEC_DIR / "XiAnalyticSpec.lean").read_text(encoding="utf-8")
    assert "SPECIFICATION, NOT PROOF" in analytic
    assert "Nothing here is claimed as proved" in analytic


def test_recorded_log_is_kernel_only_pass() -> None:
    violation = _log_violation(LOG.read_text(encoding="utf-8"))
    assert violation is None, violation


def test_runner_and_report_lock_the_same_scope() -> None:
    spec = importlib.util.spec_from_file_location(
        "run_anti_circularity_gate", RUNNER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert tuple(p.as_posix() for p in module.KERNEL_FILES) == KERNEL
    assert module.SPEC_AXIOM_BUDGET == SPEC_AXIOM_BUDGET
    violation = _report_violation(REPORT.read_text(encoding="utf-8"))
    assert violation is None, violation


def test_guard_rejects_mutations() -> None:
    log = LOG.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")

    # 1-3. Each gate placeholder is caught.
    assert _placeholders("theorem bad : True := by sorry")
    assert _placeholders("axiom cheat : True")
    assert _placeholders("theorem bad : True := by Abort")

    # 4. A kernel file silently dropped from the explicit scope.
    assert _scope_violation(KERNEL[:-1]) is not None

    # 5. The spec axiom budget grows.
    ten_axioms = "\n".join("axiom a%d : True" % i for i in range(10))
    assert _spec_budget_violation([ten_axioms]) is not None

    # 6. A non-axiom placeholder appears in the spec.
    assert _spec_budget_violation(["theorem bad : True := by sorry"]) is not None

    # 7-10. Log edits that would change the verdict or scope.
    assert _log_violation(log.replace("kernel_gate=PASS", "kernel_gate=FAIL"))
    assert _log_violation(log.replace("smt2_files=0", "smt2_files=1"))
    assert _log_violation(log.replace("spec_axioms=9", "spec_axioms=8"))
    assert _log_violation(
        log.replace("spec_diagnostic_exit=1", "spec_diagnostic_exit=0")
    )

    # 11. A forged SMT PASS.
    assert _log_violation(log + "\nSMT audit PASS\n")

    # 12. A forged RH claim in the report.
    assert _report_violation(report + "\nRH terbukti\n")


