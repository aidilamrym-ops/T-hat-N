# -*- coding: utf-8 -*-
"""CI guard: reports/FENCE_REGISTRY.md is a fail-closed certificate ledger.

Every ``sha256LF <hex> <path>`` line in the registry is re-verified against
the working tree: the path must exist and the sha256 over LF-normalised
bytes (CRLF collapsed to LF) must equal the recorded digest, so the check
is byte-stable on Windows and on CI Linux. Every entry whose Status is
CERTIFIED must carry at least one certificate line, and every entry
heading must match the registry schema. Any violation fails CI, never
passes silently.

LF normalisation note: the recorded digests are defined over LF-normalised
content (see the schema section of the registry), so line-ending policy of
the checkout cannot produce false failures of this guard.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "reports" / "FENCE_REGISTRY.md"

CERT_RE = re.compile(r"^\s*sha256LF\s+([0-9a-f]{64})\s+(\S.*?)\s*$", re.M)
ENTRY_HEAD_RE = re.compile(r"^### [TFRA]-\d{4}-\d{4}\b")
STATUS_RE = re.compile(
    r"\*\*Status:\*\* (PROPOSED|RECON|PRE-REG|RUNNING|CERTIFIED|FAILED|RETRACTED|INCONCLUSIVE)\b"
)
MIN_ENTRIES = 6  # the six initial entries; entries are retracted, never deleted


def _sha_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _text() -> str:
    assert REGISTRY.is_file(), "missing registry file: reports/FENCE_REGISTRY.md"
    return REGISTRY.read_text(encoding="utf-8")


def _entries(text: str) -> list:
    entries = []
    current = None
    for line in text.splitlines():
        if line.startswith("### "):
            assert ENTRY_HEAD_RE.match(line), (
                "entry heading does not match registry schema: %r" % line)
            current = []
            entries.append(current)
        elif current is not None:
            current.append(line)
    return entries


def test_registry_certificates_verify() -> None:
    text = _text()
    failures = []
    checked = 0
    for m in CERT_RE.finditer(text):
        digest, rel = m.group(1), m.group(2)
        checked += 1
        lineno = text.count("\n", 0, m.start()) + 1
        path = ROOT / rel
        if not path.is_file():
            failures.append("line %d: missing file %s" % (lineno, rel))
            continue
        actual = _sha_lf(path)
        if actual != digest:
            failures.append(
                "line %d: hash drift for %s (recorded %s, actual %s)"
                % (lineno, rel, digest, actual))
    assert checked > 0, "registry carries no sha256LF certificate lines"
    assert not failures, (
        "FENCE_REGISTRY certificate failures:\n" + "\n".join(failures))


def test_registry_entries_are_wellformed() -> None:
    entries = _entries(_text())
    assert len(entries) >= MIN_ENTRIES, (
        "registry must keep at least the %d initial entries, found %d"
        % (MIN_ENTRIES, len(entries)))
    for body in entries:
        joined = "\n".join(body)
        m = STATUS_RE.search(joined)
        assert m, (
            "registry entry without a schema-conforming **Status:** line; "
            "first line of entry: %r" % (body[0] if body else ""))
        if m.group(1) == "CERTIFIED":
            assert CERT_RE.search(joined), (
                "CERTIFIED entry without a certificate line: %r"
                % (body[0] if body else ""))
