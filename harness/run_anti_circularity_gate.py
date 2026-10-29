#!/usr/bin/env python3
"""Run the external anti-circularity gate over the Lean kernel sources.

Scope is deliberately narrow and explicit:

* the four ``lean/*.lean`` kernel files are the only inputs to the gate's
  PASS/FAIL verdict;
* ``lean/spec/`` is a conditional specification with nine declared axioms.
  It is run only as an out-of-scope diagnostic, whose expected ``FAIL=9``
  is recorded verbatim and is *not* the kernel verdict;
* ``*.smt2`` inputs are counted. If any appear, the audit sub-gate must be
  extended deliberately; this runner then exits 2 instead of silently
  claiming the Lean-only result covers them.

This runner is local-only. CI does not have the external skill script (and
does not need z3 for the Lean placeholder scan); the CI-side guard is
``msaf/tests/test_anti_circularity_gate.py``. The log written here is
pinned by registry ``A-2026-0015``.

Usage::

    C:\\Python314\\python.exe harness/run_anti_circularity_gate.py
    C:\\Python314\\python.exe harness/run_anti_circularity_gate.py \\
        --gate C:\\path\\to\\anti-circularity\\scripts\\gate.py \\
        --log reports/anti_circularity_gate_2026-10-20.log
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]

# The kernel source set is explicit. Adding a top-level Lean file without
# updating this tuple makes the runner fail (scope drift), rather than
# silently leaving the new file unscanned.
KERNEL_FILES = (
    Path("lean/ComplexMoore.lean"),
    Path("lean/NavierStokesCore.lean"),
    Path("lean/NewtonExistence.lean"),
    Path("lean/XiNoRealZero.lean"),
)
SPEC_DIR = Path("lean/spec")
SPEC_AXIOM_BUDGET = 9
DEFAULT_GATE = Path(
    r"C:\Users\usER\.config\opencode\skills\anti-circularity\scripts\gate.py"
)
DEFAULT_LOG = Path("reports/anti_circularity_gate_2026-10-20.log")


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def strip_lean_comments(text: str) -> str:
    """Blank out Lean comments while preserving newlines and length."""
    out: list[str] = []
    i, n, depth = 0, len(text), 0
    while i < n:
        if depth == 0:
            if text.startswith("--", i):
                while i < n and text[i] != "\n":
                    out.append(" ")
                    i += 1
                continue
            if text.startswith("/-", i):
                depth += 1
                out.append("  ")
                i += 2
                continue
            out.append(text[i])
            i += 1
        else:
            if text.startswith("/-", i):
                depth += 1
                out.append("  ")
                i += 2
                continue
            if text.startswith("-/", i):
                depth -= 1
                out.append("  ")
                i += 2
                continue
            out.append("\n" if text[i] == "\n" else " ")
            i += 1
    return "".join(out)


def spec_axiom_count() -> int:
    total = 0
    for path in sorted(SPEC_DIR.glob("*.lean")):
        text = strip_lean_comments(
            (ROOT / path).read_text(encoding="utf-8")
        )
        total += len(re.findall(r"^[ \t]*axiom\b", text, re.M))
    return total


def smt2_files() -> list[Path]:
    skip = {
        ".lake",
        ".git",
        ".hg",
        ".svn",
        "node_modules",
        "__pycache__",
    }
    found: list[Path] = []
    for root, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in skip)
        for name in sorted(filenames):
            if name.lower().endswith(".smt2"):
                found.append(Path(root) / name)
    return found


def run_gate(python: str, gate: Path, args: Sequence[str]) -> tuple[int, str]:
    cmd = [python, str(gate), *map(str, args)]
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output.rstrip("\n")


def command_line(python: str, gate: Path, args: Sequence[str]) -> str:
    return " ".join([python, str(gate), *map(str, args)])


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the anti-circularity gate over the Lean kernel only."
    )
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    args = parser.parse_args(argv)

    gate = args.gate.resolve()
    if not gate.is_file():
        print("gate not found: %s" % gate, file=sys.stderr)
        return 2

    expected = [p.as_posix() for p in KERNEL_FILES]
    missing = [rel for rel in expected if not (ROOT / rel).is_file()]
    if missing:
        print("missing kernel file(s): %s" % ", ".join(missing), file=sys.stderr)
        return 2

    globbed = sorted(
        p.relative_to(ROOT).as_posix() for p in (ROOT / "lean").glob("*.lean")
    )
    if globbed != expected:
        print(
            "kernel glob drift: found %r; explicit scope is %r"
            % (globbed, expected),
            file=sys.stderr,
        )
        return 2

    spec_axioms = spec_axiom_count()
    smt = smt2_files()

    lean_code, lean_out = run_gate(
        args.python, gate, ["lean", *expected]
    )
    check_code, check_out = run_gate(
        args.python, gate, ["check", *expected]
    )
    spec_code, spec_out = run_gate(
        args.python, gate, ["lean", SPEC_DIR.as_posix()]
    )

    kernel_pass = lean_code == 0 and check_code == 0
    spec_diagnostic_ok = spec_code == 1 and "FAIL=9" in spec_out
    scope_ok = spec_axioms == SPEC_AXIOM_BUDGET and not smt

    if not kernel_pass:
        kernel_verdict = (
            "FAIL" if 1 in (lean_code, check_code) else "TOOL_NOT_RUN"
        )
    else:
        kernel_verdict = "PASS"

    lines: list[str] = [
        "# Anti-circularity gate run -- Lean kernel scope",
        "# generated_by: harness/run_anti_circularity_gate.py",
        "# gate_sha256: %s" % sha256_lf(gate),
        "# python: %s" % sys.version.split()[0],
        "# scope: Lean kernel only (lean/*.lean); lean/spec OUT OF SCOPE; "
        "no SMT audit input",
        "kernel_files=%d" % len(expected),
        "spec_axioms=%d" % spec_axioms,
        "smt2_files=%d" % len(smt),
        "audit_subgate=%s"
        % ("NOT_INVOKED_NO_SMT2" if not smt else "INPUT_PRESENT_NOT_RUN"),
        "",
        "## kernel file hashes (sha256LF)",
    ]
    for rel in expected:
        lines.append("sha256LF %s %s" % (sha256_lf(ROOT / rel), rel))
    lines.extend(
        [
            "",
            "## command: %s"
            % command_line(args.python, gate, ["lean", *expected]),
            lean_out,
            "kernel_lean_exit=%d" % lean_code,
            "",
            "## command: %s"
            % command_line(args.python, gate, ["check", *expected]),
            check_out,
            "kernel_check_exit=%d" % check_code,
            "",
            "## out-of-scope diagnostic: %s"
            % command_line(args.python, gate, ["lean", SPEC_DIR.as_posix()]),
            "# lean/spec is conditional (nine declared axioms). This FAIL=9 is"
            " recorded as a diagnostic, not as the kernel gate verdict.",
            spec_out,
            "spec_diagnostic_exit=%d" % spec_code,
            "spec_diagnostic_expected=FAIL=9",
            "",
            "## verdict",
            "kernel_gate=%s" % kernel_verdict,
            "scope=LEAN_KERNEL_ONLY",
        ]
    )
    log_text = "\n".join(lines) + "\n"

    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(log_text)
    print(log_text, end="")

    if not kernel_pass:
        return 1 if kernel_verdict == "FAIL" else 2
    if not scope_ok:
        return 2
    if not spec_diagnostic_ok:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


