"""Lean axiom audit: real, non-vacuous, fast.

SCOPE (binding): every top-level theorem/lemma in `lean/*.lean` must
(a) contain no placeholder token, and (b) depend on no axiom beyond
propext, Classical.choice, Quot.sound.

This is the audit the register CLAIMED but never executed. An earlier
revision reported "PASS" while auditing ZERO declarations, because
`lake build` does not compile the generated audit files (unknown
targets) and the appended `#print axioms` lines sat outside the
closed namespace, so every name resolved to "unknown constant". Both
traps are now asserted against:

  * the number of declarations audited must EQUAL the number found in
    the sources -- an audit that covers nothing FAILS, loudly;
  * the namespace is re-opened so the names resolve;
  * the printed axioms are parsed from real compiler output.

The audit imports the built libraries (olean reuse), so it costs
seconds instead of recompiling the 2000-line kernel; if the oleans
are missing it falls back to compiling the sources directly.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
ROOT = Path(__file__).resolve().parents[2]
LEAN_DIR = ROOT / "lean"
BUILD_LIB = LEAN_DIR / ".lake" / "build" / "lib" / "lean"


def _lean_sources() -> list[Path]:
    return sorted(p for p in LEAN_DIR.glob("*.lean"))


def _declarations(text: str) -> list[str]:
    return [
        m.group(2)
        for m in re.finditer(
            r"^(theorem|lemma)\s+([A-Za-z_][A-Za-z0-9_'.]*)", text, re.M
        )
    ]


def _namespace(text: str) -> str:
    m = re.search(r"^namespace\s+([A-Za-z_][A-Za-z0-9_.]*)", text, re.M)
    return m.group(1) if m else ""


def test_no_placeholders_in_lean_sources():
    sources = _lean_sources()
    if not sources:
        pytest.skip("no Lean sources in this workspace (isolated mirror)")
    forbidden = re.compile(r"\b(sorry|admit|unsafe|native_decide)\b")
    for path in sources:
        text = path.read_text(encoding="utf-8")
        stripped = "\n".join(
            re.sub(r"--.*$", "", line) for line in text.splitlines()
        )
        hit = forbidden.search(stripped)
        assert hit is None, f"{path.name}: placeholder {hit.group(0)!r}"


@pytest.mark.skipif(
    shutil.which("lake") is None, reason="Lean toolchain absent"
)
def test_every_declaration_uses_standard_axioms_only(tmp_path: Path):
    sources = _lean_sources()
    if not sources:
        pytest.skip(
            "no Lean sources in this workspace (isolated mirror); "
            "the audit runs in the full repository, never silently"
        )
    has_lakefile = any(
        (LEAN_DIR / name).exists()
        for name in ("lakefile.lean", "lakefile.toml")
    )
    if not has_lakefile:
        pytest.skip(
            "Lean sources present but no lakefile: cannot resolve Mathlib"
        )
    jobs = []
    expected = 0
    for path in sources:
        text = path.read_text(encoding="utf-8")
        names = _declarations(text)
        if not names:
            continue
        expected += len(names)
        jobs.append((path.stem, _namespace(text), names))

    if expected == 0:
        pytest.fail("no Lean declarations found: the audit would be vacuous")

    # Two forms: prefer importing the built oleans (seconds), else
    # recompile the sources (slow but works in a fresh checkout).
    # The audit file must live INSIDE the Lean package: running
    # `lake env` from elsewhere loses the Mathlib search path and the
    # import form dies with "unknown module prefix 'Mathlib'".
    have_oleans = all(
        (BUILD_LIB / f"{stem}.olean").exists() for stem, _, _ in jobs
    )
    audit = LEAN_DIR / "_axiom_audit_tmp.lean"
    try:
        if have_oleans:
            parts = [f"import {stem}\n" for stem, _, _ in jobs]
            for _stem, ns, names in jobs:
                parts.append(f"namespace {ns}\n")
                parts.extend(f"#print axioms {ns}.{n}\n" for n in names)
                parts.append(f"end {ns}\n")
        else:
            parts = []
            for path in sources:
                text = path.read_text(encoding="utf-8")
                names = _declarations(text)
                if not names:
                    continue
                ns = _namespace(text)
                parts.append(text + f"\n\nnamespace {ns}\n")
                parts.extend(f"#print axioms {n}\n" for n in names)
                parts.append(f"end {ns}\n")
        audit.write_text("".join(parts), encoding="utf-8")
        res = subprocess.run(
            "lake env lean " + audit.name,
            cwd=str(LEAN_DIR),
            capture_output=True,
            text=True,
            shell=True,
        )
        out = (res.stdout or "") + (res.stderr or "")
    finally:
        audit.unlink(missing_ok=True)
    assert res.returncode == 0, f"audit failed to compile:\n{out[:3000]}"

    found = re.findall(
        r"'([A-Za-z_][A-Za-z0-9_.]*)' depends on axioms: \[([^\]]*)\]",
        out,
    )
    assert len(found) == expected, (
        f"audit covered {len(found)} of {expected} declarations -- "
        "an incomplete audit is a failure, not a pass"
    )
    observed: set[str] = set()
    for _name, axlist in found:
        observed |= {x.strip() for x in axlist.split(",") if x.strip()}
    extra = observed - ALLOWED
    assert not extra, f"non-standard axioms: {sorted(extra)}"


def _env_with_lean_path() -> dict:
    import os

    env = dict(os.environ)
    env["LEAN_PATH"] = str(BUILD_LIB) + os.pathsep + env.get("LEAN_PATH", "")
    return env