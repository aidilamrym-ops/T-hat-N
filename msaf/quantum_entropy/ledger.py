"""Append-only hash-chained ledger for Campaign V2 (K-Q6).

Format ``msaf-hashchain-1``: one canonical JSON object per LF-terminated
line; ``record_hash = sha256(previous_hash + "\\n" + canonical_json)`` where
canonical JSON sorts keys, uses compact separators and keeps non-ASCII
characters. The genesis record uses ``previous_hash = "GENESIS"``.

K-Q6: a reproduction failure of a recorded block is recorded as a REVERT
record (never as a fitness REJECT). The record type REJECT is refused by
construction.

CLI (L42: paths are caller-provided; nothing anchors to the CWD):

    python -m msaf.quantum_entropy.ledger --genesis PATH
    python -m msaf.quantum_entropy.ledger --verify PATH
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys

from .entropy_source import refuse_seed

__all__ = [
    "ALLOWED_TYPES",
    "GENESIS_PREV",
    "append_record",
    "canonical_bytes",
    "make_genesis",
    "make_revert",
    "read_last_hash",
    "record_hash",
    "verify_chain",
]

ALLOWED_TYPES = ("GENESIS", "BLOCK", "STATS", "VERDICT", "REVERT")
GENESIS_PREV = "GENESIS"


def canonical_bytes(rec: dict) -> bytes:
    return json.dumps(
        rec, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def record_hash(prev_hash: str, rec: dict) -> str:
    h = hashlib.sha256()
    h.update(prev_hash.encode("utf-8"))
    h.update(b"\n")
    h.update(canonical_bytes(rec))
    return h.hexdigest()


def _check_type(rec: dict) -> None:
    t = rec.get("type")
    if t == "REJECT" or "REJECT" in {str(v) for v in rec.values()}:
        raise ValueError("K-Q6: REJECT is forbidden; use REVERT for failed reproductions")
    if t not in ALLOWED_TYPES:
        raise ValueError("record type %r not in %r" % (t, ALLOWED_TYPES))


def read_last_hash(path) -> str:
    try:
        with open(path, "rb") as f:
            lines = [ln for ln in f.read().split(b"\n") if ln.strip()]
    except FileNotFoundError:
        return GENESIS_PREV
    if not lines:
        return GENESIS_PREV
    rec = json.loads(lines[-1].decode("utf-8"))
    return rec["record_hash"]


def append_record(path, rec: dict) -> dict:
    """Append one record, wiring previous_hash/record_hash; returns the record."""
    _check_type(rec)
    prev = read_last_hash(path)
    rec = dict(rec)
    rec["previous_hash"] = prev
    rec["record_hash"] = record_hash(prev, rec)
    line = canonical_bytes(rec) + b"\n"
    with open(path, "ab") as f:
        f.write(line)
    return rec


def make_genesis(spec_path: str, prereg_path: str, created_utc: str) -> dict:
    return {
        "type": "GENESIS",
        "ledger_format": "msaf-hashchain-1",
        "campaign": "quantum-v2",
        "version": "0.2-quantum",
        "created_utc": created_utc,
        "entropy_label": "SIMULATED",
        "global_claim_supported": False,
        "spec": spec_path,
        "prereg": prereg_path,
    }


def make_revert(dim, reason: str, evidence: str, created_utc: str) -> dict:
    """K-Q6: failed reproduction of a block -> REVERT, never REJECT."""
    return {
        "type": "REVERT",
        "campaign": "quantum-v2",
        "dim": dim,
        "reason": reason,
        "evidence": evidence,
        "created_utc": created_utc,
    }


def verify_chain(path) -> dict:
    """Verify the full chain; returns {ok, count, head, error}."""
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except FileNotFoundError:
        return {"ok": False, "count": 0, "head": None, "error": "missing file"}
    lines = [ln for ln in raw.split(b"\n") if ln.strip()]
    prev = GENESIS_PREV
    for n, line in enumerate(lines):
        try:
            rec = json.loads(line.decode("utf-8"))
        except UnicodeDecodeError as e:
            return {"ok": False, "count": n, "head": prev, "error": "line %d: %s" % (n, e)}
        stored = rec.pop("record_hash", None)
        if rec.get("previous_hash") != prev:
            return {
                "ok": False,
                "count": n,
                "head": prev,
                "error": "line %d: previous_hash mismatch" % n,
            }
        recomputed = record_hash(prev, rec)
        if stored != recomputed:
            return {
                "ok": False,
                "count": n,
                "head": prev,
                "error": "line %d: record_hash mismatch" % n,
            }
        prev = stored
    return {"ok": True, "count": len(lines), "head": prev, "error": None}


def _main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    refuse_seed(argv)
    ap = argparse.ArgumentParser(prog="msaf.quantum_entropy.ledger")
    ap.add_argument("--genesis", metavar="PATH")
    ap.add_argument("--verify", metavar="PATH")
    args = ap.parse_args(argv)
    if args.genesis:
        import datetime

        existing = read_last_hash(args.genesis)
        if existing != GENESIS_PREV:
            sys.stderr.write("refusing: ledger already has records\n")
            return 1
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        rec = make_genesis(
            "reports/REPLAY_CERT_SPEC_V0.2_QUANTUM.md",
            "reports/AUDIT_QUANTUM_PREREG_2026-10-19.md",
            now,
        )
        rec = append_record(args.genesis, rec)
        print("genesis appended: %s" % rec["record_hash"])
        return 0
    if args.verify:
        res = verify_chain(args.verify)
        if res["ok"]:
            print("chain OK: %d records; head=%s" % (res["count"], res["head"]))
            return 0
        print("chain FAIL: %s" % res["error"])
        return 1
    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(_main())


