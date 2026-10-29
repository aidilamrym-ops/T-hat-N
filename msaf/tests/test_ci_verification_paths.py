# -*- coding: utf-8 -*-
"""Static guard for the real CI verification paths.

Two paths were added on 2026-10-20:

* ``lean-kernel`` runs the per-declaration ``#print axioms`` audit after
  ``lake build`` (``msaf/tests/test_lean_axiom_audit.py``);
* a new ``coq-kernel`` job runs the pinned Coq 8.20.1 checks for
  Paket 8/9 with Docker, instead of relying on the runner's apt Coq.

The guard is deliberately textual: CI YAML is the artifact under test,
and a missing step must fail loudly rather than being skipped.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CI = ROOT / ".github" / "workflows" / "ci.yml"
COQ_IMAGE_SHA = (
    "sha256:18ebf3da56e60e3ddfd7d4e51f4c53d10241a129f34e93dacbc71562dd43c57a"
)


def _ci_text() -> str:
    return CI.read_text(encoding="utf-8")


def _lean_audit_violation(text: str) -> str | None:
    needle = "test_every_declaration_uses_standard_axioms_only"
    if "lake build" not in text:
        return "missing 'lake build'"
    if needle not in text:
        return "missing per-declaration axiom audit step"
    if text.index("lake build") > text.index(needle):
        return "axiom audit step appears before 'lake build'"
    if "python -m pip install" not in text.split(needle)[0]:
        return "axiom audit step does not install pytest first"
    return None


def _coq_job_violation(text: str) -> str | None:
    pinned = "coqorg/coq:8.20.1@" + COQ_IMAGE_SHA
    for needle in (
        "coq-kernel:",
        pinned,
        "coqc --version",
        "check_integral_limit.sh",
        "check_integral_infinite.sh",
    ):
        if needle not in text:
            return "missing Coq CI needle %r" % needle
    if text.index("check_integral_limit.sh") > text.index(
        "check_integral_infinite.sh"
    ):
        return "Paket 9 check runs before Paket 8; expected sequential order"
    return None


def _soft_fail_violation(text: str) -> str | None:
    if "continue-on-error" in text:
        return "verification job contains 'continue-on-error'"
    return None


def _spec_v2_sensor_violation(text: str) -> str | None:
    if "--exclude-dir=spec_v2" not in text:
        return "kernel escape-token sensor does not exclude lean/spec_v2"
    if 'spec_v2 axiom budget: $n / 8' not in text:
        return "missing spec_v2 axiom-budget announcement"
    if text.count('test "$n" -eq 8') != 1:
        return "spec_v2 axiom budget is not locked to exactly eight"
    if "spec_v2 (placeholders banned" not in text:
        return "missing spec_v2 placeholder sensor"
    return None


def test_lean_kernel_audits_axioms_after_build() -> None:
    violation = _lean_audit_violation(_ci_text())
    assert violation is None, violation


def test_coq_kernel_job_is_pinned_and_ordered() -> None:
    violation = _coq_job_violation(_ci_text())
    assert violation is None, violation


def test_verification_steps_are_not_soft_failed() -> None:
    violation = _soft_fail_violation(_ci_text())
    assert violation is None, violation


def test_spec_v2_sensor_budget_is_locked() -> None:
    violation = _spec_v2_sensor_violation(_ci_text())
    assert violation is None, violation


def test_guard_rejects_mutations() -> None:
    text = _ci_text()
    needle = "test_every_declaration_uses_standard_axioms_only"
    assert _lean_audit_violation(text.replace(needle, "no_audit"))
    assert _lean_audit_violation(
        text.replace("lake build", "noop_build")
    )
    assert _coq_job_violation(text.replace("coqorg/coq:8.20.1", "coq:latest"))
    assert _coq_job_violation(
        text.replace(COQ_IMAGE_SHA, "sha256:" + "0" * 64)
    )
    assert _coq_job_violation(
        text.replace("check_integral_infinite.sh", "no_infinite_check.sh")
    )
    assert _soft_fail_violation(text + "\ncontinue-on-error: true\n")
    assert _spec_v2_sensor_violation(
        text.replace(" --exclude-dir=spec_v2", "")
    )
    assert _spec_v2_sensor_violation(text.replace('test "$n" -eq 8', 'test "$n" -eq 9'))


