#!/usr/bin/env python3
"""Campaign V2 freeze tool: build/verify PINS.sha256 + freeze manifest.

Usage::

    python audit_quantum/freeze.py --build [--force]
    python audit_quantum/freeze.py --verify

PINS.sha256 pins the raw bytes (sha256, ``sha  path`` lines, path-sorted) of
the frozen Campaign V2 code and documents. The **Codebase/Manifest Digest**
is defined as ``sha256`` over the raw bytes of PINS.sha256 itself; ``--build``
prints it and FREEZE_MANIFEST_V2.json records it together with the ledger
snapshot at freeze time (path, raw sha256, record count, chain head).

The append-only ledger is intentionally NOT a pinned file: it grows during
the GO-2 campaign run; only its freeze-time snapshot is recorded here.

Deterministic: re-running ``--build`` with unchanged files yields the same
digest. ``--verify`` recomputes every pin and the digest binding and exits 2
on any mismatch (frozen logs/reports are never rewritten).
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

PINS_PATH = HERE / "PINS.sha256"
MANIFEST_PATH = HERE / "FREEZE_MANIFEST_V2.json"
LEDGER_REL = "ledger/quantum_evolution.jsonl"

PINS_FILES = [
    "audit_quantum/freeze.py",
    "msaf/quantum_entropy/__init__.py",
    "msaf/quantum_entropy/chispec.py",
    "msaf/quantum_entropy/dashboard.py",
    "msaf/quantum_entropy/engines.py",
    "msaf/quantum_entropy/entropy_source.py",
    "msaf/quantum_entropy/intervals.py",
    "msaf/quantum_entropy/ledger.py",
    "msaf/quantum_entropy/runner.py",
    "msaf/quantum_entropy/selftest.py",
    "msaf/quantum_entropy/sylvester.py",
    "msaf/tests/test_quantum_entropy.py",
    "reports/AUDIT_QUANTUM_PREREG_2026-10-19.md",
    "reports/REPLAY_CERT_SPEC_V0.2_QUANTUM.md",
]


def sha256_raw(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pins_bytes(files: dict) -> bytes:
    lines = ["%s  %s" % (files[p], p) for p in sorted(files)]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _ledger_snapshot() -> dict:
    path = ROOT / LEDGER_REL
    if not path.exists():
        raise SystemExit(
            "freeze refused: %s missing (run the genesis step first)" % LEDGER_REL
        )
    sys.path.insert(0, str(ROOT))
    from msaf.quantum_entropy.ledger import verify_chain

    chain = verify_chain(path)
    if not chain["ok"]:
        raise SystemExit("freeze refused: ledger chain broken: %s" % chain["error"])
    if chain["count"] < 1:
        raise SystemExit("freeze refused: ledger has no records (genesis missing)")
    return {
        "path": LEDGER_REL,
        "sha256": sha256_raw(path),
        "records": chain["count"],
        "head": chain["head"],
        "note": (
            "snapshot at freeze time; the ledger is append-only and is NOT a "
            "pinned file (it grows during the GO-2 campaign run)"
        ),
    }


def build(force: bool) -> int:
    print("Campaign V2 freeze build (SIMULATED entropy; no physical claim)")
    if MANIFEST_PATH.exists() and not force:
        print(
            "refusing: %s already exists (use --force only for a fresh, "
            "deliberate re-freeze)" % MANIFEST_PATH.name
        )
        return 2
    missing = [p for p in PINS_FILES if not (ROOT / p).exists()]
    if missing:
        for p in missing:
            print("missing pinned file: %s" % p)
        return 2
    files = {p: sha256_raw(ROOT / p) for p in PINS_FILES}
    pins_bytes = _pins_bytes(files)
    PINS_PATH.write_bytes(pins_bytes)
    digest = hashlib.sha256(pins_bytes).hexdigest()
    manifest = {
        "format": "quantum-v2-freeze/1",
        "campaign": "quantum-v2",
        "entropy_label": "SIMULATED",
        "global_claim_supported": False,
        "generated_by": "audit_quantum/freeze.py",
        "created_utc": _utc(),
        "digest_definition": "sha256 over the raw bytes of audit_quantum/PINS.sha256",
        "digest": digest,
        "pins_file": "audit_quantum/PINS.sha256",
        "files": files,
        "ledger_snapshot": _ledger_snapshot(),
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print("pins: %d files -> %s" % (len(files), PINS_PATH.relative_to(ROOT)))
    for p in sorted(files):
        print("  %s  %s" % (files[p], p))
    print("ledger snapshot: %d record(s), head=%s" % (
        manifest["ledger_snapshot"]["records"], manifest["ledger_snapshot"]["head"]))
    print("Codebase/Manifest Digest = sha256(PINS.sha256) = %s" % digest)
    return 0


def verify() -> int:
    if not PINS_PATH.exists():
        print("verify FAILED: %s missing" % PINS_PATH.name)
        return 2
    pins_raw = PINS_PATH.read_bytes()
    listed = {}
    for i, line in enumerate(pins_raw.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            sha, rel = line.split("  ", 1)
        except ValueError:
            print("verify FAILED: bad PINS line %d" % i)
            return 2
        listed[rel] = sha
    bad = 0
    for rel, sha in sorted(listed.items()):
        path = ROOT / rel
        if not path.exists():
            print("verify FAILED: missing %s" % rel)
            bad += 1
            continue
        if sha256_raw(path) != sha:
            print("verify FAILED: sha mismatch %s" % rel)
            bad += 1
    extra = sorted(set(PINS_FILES) - set(listed))
    if extra:
        print("verify FAILED: pins incomplete, missing: %s" % ", ".join(extra))
        bad += 1
    if not MANIFEST_PATH.exists():
        print("verify FAILED: %s missing" % MANIFEST_PATH.name)
        return 2
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    digest = hashlib.sha256(pins_raw).hexdigest()
    if manifest.get("digest") != digest:
        print("verify FAILED: manifest digest != sha256(PINS.sha256)")
        bad += 1
    if manifest.get("files") != listed:
        print("verify FAILED: manifest files table != PINS list")
        bad += 1
    if bad:
        return 2
    print(
        "verify OK: %d pins; Codebase/Manifest Digest = sha256(PINS.sha256) = %s"
        % (len(listed), digest)
    )
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(prog="audit_quantum/freeze.py")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    if args.build == args.verify:
        ap.print_help()
        return 2
    if args.build:
        return build(force=args.force)
    return verify()


if __name__ == "__main__":
    raise SystemExit(main())
