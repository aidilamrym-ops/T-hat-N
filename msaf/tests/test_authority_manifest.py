# -*- coding: utf-8 -*-
"""CI guard for the durable authority layer.

``reports/AUTHORITY_MANIFEST.json`` is the machine-readable index of the
current authority. It carries ``sha256LF`` digests of the four human-readable
authority documents, so an edit that bypasses ``reports/DECISION_LOG.md`` and
``CURRENT_AUTHORITY.md`` fails CI instead of passing silently.

When an authority document changes, recompute its LF-normalised digest and
update the matching ``sha256lf`` field in the manifest **in the same commit**.
Superseded paths may remain on disk, but they must be named here with an
explicit state; they may never be presented as active authority.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "reports" / "AUTHORITY_MANIFEST.json"

ACTIVE_PATHS = {
    "agents": "AGENTS.md",
    "current_authority": "CURRENT_AUTHORITY.md",
    "decision_log": "reports/DECISION_LOG.md",
    "archive_tombstones": "reports/ARCHIVE_TOMBSTONES.md",
}
ALLOWED_SUPERSEDED_STATES = {
    "historical",
    "stub-pending",
    "tombstone-pending",
    "tombstoned",
    "stubbed",
}


def _sha_lf(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n")
    ).hexdigest()


def _load() -> dict:
    assert MANIFEST.is_file(), (
        "missing authority manifest: reports/AUTHORITY_MANIFEST.json")
    with MANIFEST.open(encoding="utf-8") as fh:
        return json.load(fh)


def test_active_authority_hashes_match_manifest() -> None:
    data = _load()
    assert data.get("schema_version") == 1, (
        "unsupported authority manifest schema: %r"
        % data.get("schema_version"))
    active = data.get("active")
    assert isinstance(active, dict), "manifest active section must be an object"
    assert set(active) == set(ACTIVE_PATHS), (
        "manifest active keys drifted: %r" % sorted(active))

    seen = set()
    for key, rel in ACTIVE_PATHS.items():
        entry = active[key]
        assert entry.get("path") == rel, (
            "manifest active[%r].path must be %r, got %r"
            % (key, rel, entry.get("path")))
        assert rel not in seen, "duplicate active authority path: %s" % rel
        seen.add(rel)
        path = ROOT / rel
        assert path.is_file(), "missing active authority file: %s" % rel
        recorded = entry.get("sha256lf")
        assert isinstance(recorded, str) and len(recorded) == 64, (
            "active authority %s has no 64-hex sha256lf digest" % rel)
        actual = _sha_lf(path)
        assert actual == recorded, (
            "%s drifted from reports/AUTHORITY_MANIFEST.json "
            "(recorded %s, actual %s); update the manifest in the same commit"
            % (rel, recorded, actual))


def test_superseded_and_protected_entries_are_explicit() -> None:
    data = _load()
    active_paths = set(ACTIVE_PATHS.values())

    superseded = data.get("superseded") or []
    assert superseded, "manifest must name at least reports/HANDOFF.md"
    paths = [entry.get("path") for entry in superseded]
    assert len(paths) == len(set(paths)), "duplicate superseded path"
    assert "reports/HANDOFF.md" in paths, (
        "reports/HANDOFF.md must be named as superseded/historical")
    for entry in superseded:
        assert entry.get("state") in ALLOWED_SUPERSEDED_STATES, (
            "unknown superseded state: %r" % entry.get("state"))
        assert entry.get("replacement"), (
            "superseded entry without replacement: %r" % entry.get("path"))
        assert len(entry.get("recovery_commit", "")) >= 7, (
            "superseded entry without recovery commit: %r"
            % entry.get("path"))
        assert entry["path"] not in active_paths, (
            "path is listed as both active and superseded: %s" % entry["path"])

    for entry in data.get("historical_artifacts") or []:
        rel = entry.get("path")
        assert rel and (ROOT / rel).is_file(), (
            "historical artifact must stay on disk: %r" % rel)
        assert len(entry.get("recovery_commit", "")) >= 7, (
            "historical artifact without recovery commit: %r" % rel)

    for entry in data.get("protected") or []:
        rel = entry.get("path")
        assert rel and (ROOT / rel).is_file(), (
            "protected path must stay on disk: %r" % rel)
        assert entry.get("reason"), (
            "protected path without a reason: %r" % rel)


def test_authority_documents_keep_scope_limits() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "CURRENT_AUTHORITY.md" in agents
    assert "Prereg sebelum kode" in agents

    current = (ROOT / "CURRENT_AUTHORITY.md").read_text(encoding="utf-8")
    assert "diagonal `XC`" in current, (
        "CURRENT_AUTHORITY.md must keep the P2 diagonal-XC scope")
    assert "T-2026-0052" in current
    assert "Tidak ada klaim RH" in current, (
        "CURRENT_AUTHORITY.md must keep the no-RH-claim boundary")

    log = (ROOT / "reports" / "DECISION_LOG.md").read_text(encoding="utf-8")
    assert "0b0a32c" in log, "decision log must name the P2 commit"
    assert "Authority layer aditif" in log, (
        "decision log must record the additive authority-layer decision")

    tombstones = (ROOT / "reports" / "ARCHIVE_TOMBSTONES.md").read_text(
        encoding="utf-8")
    # D1 (2026-10-27): tombstone already dieksekusi on commit 995576c, sehingga
    # ledger wajib mencantumkannya and no lagi boleh berklaim "belum ada
    # tombstone which dieksekusi". Lihat entri DECISION_LOG bertanggal sama.
    assert "Belum ada tombstone which dieksekusi." not in tombstones, (
        "tombstone ledger still claims that no removal was executed; "
        "sync it with reports/ARCHIVE_TOMBSTONES.md and DECISION_LOG")
    executed = tombstones.partition("## Tombstone which already dieksekusi")[2]
    executed = executed.partition("## Kandidat which disetujui pemilik")[0]
    assert "995576c" in executed, (
        "executed tombstone rows must cite the execution commit 995576c")
    assert "tombstoned" in executed and "stubbed" in executed, (
        "executed tombstone rows must cover tombstoned and stubbed entries")


def test_r6_registry_gap_is_closed() -> None:
    registry = (ROOT / "reports" / "FENCE_REGISTRY.md").read_text(
        encoding="utf-8")
    assert "### A-2026-0047" in registry, (
        "r6 is certified by the owner but the ledger entry is missing")
    start = registry.index("### A-2026-0047")
    end = registry.find("\n### ", start + 4)
    section = registry[start:end if end != -1 else len(registry)]
    assert "**Status:** CERTIFIED" in section
    assert "reports/figure_eight_r6_2026-10-25.json" in section

    receipt_path = ROOT / "reports" / "figure_eight_r6_2026-10-25.json"
    digest = _sha_lf(receipt_path)
    assert (
        "sha256LF %s reports/figure_eight_r6_2026-10-25.json" % digest
    ) in section, "the r6 certificate line does not match the receipt on disk"

    data = _load()
    claims = data.get("certified_claims") or []
    matches = [c for c in claims if c.get("id") == "A-2026-0047"]
    assert len(matches) == 1, (
        "manifest must carry exactly one A-2026-0047 certified claim")
    assert matches[0].get("status") == "CERTIFIED"

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt.get("all_pass") is True
    assert receipt.get("summary") == "ALL PASS"

    current = (ROOT / "CURRENT_AUTHORITY.md").read_text(encoding="utf-8")
    assert "A-2026-0047" in current, (
        "CURRENT_AUTHORITY.md must list the owner-confirmed r6 claim")


def test_manifest_baseline_is_p2() -> None:
    baseline = _load().get("baseline") or {}
    assert baseline.get("p2_commit", "").startswith("0b0a32c"), (
        "manifest baseline must pin the P2 commit")
    assert baseline.get("p2_prereg_commit", "").startswith("fc33084"), (
        "manifest baseline must pin the P2 prereg commit")
    assert baseline.get("p1_prereg_commit", "").startswith("34ee072"), (
        "manifest baseline must pin the P1 prereg commit")
    assert baseline.get("p2_ci_result") == "success", (
        "manifest baseline records a non-green P2 CI result")

    precedence = _load().get("authority_precedence") or []
    assert precedence[:1] == ["CURRENT_AUTHORITY.md"], (
        "CURRENT_AUTHORITY.md must be first in the authority precedence")


