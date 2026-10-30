"""Append-only hash-chained ledger for Chrono runtime executions.

The chain mirrors ``ledger/msaf_ledger.jsonl``: record 0 carries
``previous_hash = "GENESIS"`` and every later record points at the previous
``record_hash``. The canonical form is sorted-key compact JSON encoded as
UTF-8, with the ``record_hash`` field excluded before hashing.

A failed measurement is appended as ``execution_status = "FAILED"`` with the
exception recorded as a deviation. Failure never raises out of
:func:`append_record` and never becomes a certified registry claim.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

__all__ = [
    "LEDGER_PATH",
    "LEDGER_SCHEMA",
    "canonical_bytes",
    "compute_record_hash",
    "read_records",
    "append_record",
    "verify_chain",
    "make_record",
]

ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = ROOT / "ledger" / "chrono_execution_ledger.jsonl"
LEDGER_SCHEMA = "msaf.chrono_execution.v1"

SCOPE: dict[str, bool] = {
    "rh_claim": False,
    "zero_location_claim": False,
    "weil_positivity_claim": False,
}


def canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def compute_record_hash(record: dict[str, Any]) -> str:
    payload = {key: value for key, value in record.items() if key != "record_hash"}
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def read_records(path: Path = LEDGER_PATH) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            if not line.strip():
                raise ValueError(f"blank line at {path}:{lineno}")
            records.append(json.loads(line))
    return records


def _last_line(path: Path) -> dict[str, Any] | None:
    if not path.is_file() or path.stat().st_size == 0:
        return None
    last = None
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                last = json.loads(line)
    return last


def append_record(
    record: dict[str, Any], path: Path = LEDGER_PATH
) -> dict[str, Any]:
    """Append ``record`` with a valid index and hash link.

    The caller-supplied ``index``, ``previous_hash`` and ``record_hash`` are
    overwritten; the chain, not the caller, decides those fields.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    previous = _last_line(path)
    if previous is None:
        index = 0
        previous_hash = "GENESIS"
    else:
        index = int(previous["index"]) + 1
        previous_hash = str(previous["record_hash"])

    payload = {key: value for key, value in record.items() if key != "record_hash"}
    payload["schema"] = LEDGER_SCHEMA
    payload["index"] = index
    payload["previous_hash"] = previous_hash
    payload["scope"] = dict(SCOPE)
    payload["record_hash"] = compute_record_hash(payload)

    line = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line + "\n")
    return payload


def verify_chain(path: Path = LEDGER_PATH) -> list[str]:
    """Return a list of chain errors; an empty list means valid."""
    if not path.is_file():
        return [f"missing ledger: {path}"]

    errors: list[str] = []
    previous_hash = "GENESIS"
    with path.open(encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            if not line.strip():
                errors.append(f"line {lineno}: blank line")
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {lineno}: invalid JSON ({exc})")
                continue

            index = record.get("index")
            if index != lineno - 1:
                errors.append(
                    f"line {lineno}: index {index!r} != {lineno - 1}"
                )
            if record.get("previous_hash") != previous_hash:
                errors.append(
                    f"line {lineno}: previous_hash {record.get('previous_hash')!r} "
                    f"!= {previous_hash!r}"
                )
            expected = compute_record_hash(record)
            if record.get("record_hash") != expected:
                errors.append(
                    f"line {lineno}: record_hash {record.get('record_hash')!r} "
                    f"!= {expected!r}"
                )
            previous_hash = str(record.get("record_hash"))

    return errors


def make_record(
    *,
    rule_id: str,
    run_id: str,
    execution_status: str,
    numerical_verdict: str,
    payload: object,
    dim: int | None = None,
    deviation: str | None = None,
) -> dict[str, Any]:
    """Build a ledger record before :func:`append_record` links it."""
    if execution_status not in {"PASS", "FAILED"}:
        raise ValueError(
            f"execution_status must be PASS or FAILED, got {execution_status!r}"
        )
    if execution_status == "FAILED" and deviation is None:
        raise ValueError("a FAILED record must carry a deviation")

    record: dict[str, Any] = {
        "schema": LEDGER_SCHEMA,
        "run_id": run_id,
        "rule_id": rule_id,
        "execution_status": execution_status,
        "numerical_verdict": numerical_verdict,
        "payload_sha256": hashlib.sha256(canonical_bytes(payload)).hexdigest(),
        "scope": dict(SCOPE),
    }
    if dim is not None:
        record["dim"] = int(dim)
    if deviation is not None:
        record["deviation"] = deviation
    return record


def iter_records(path: Path = LEDGER_PATH) -> Iterable[dict[str, Any]]:
    yield from read_records(path)
