"""Tests for the append-only Chrono execution ledger."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from msaf.chrono_runtime import ledger

ROOT = Path(__file__).resolve().parents[2]


def _record(index: int, status: str = "PASS") -> dict:
    return ledger.make_record(
        rule_id="CHRONO-ADVANCE",
        run_id=f"run-{index}",
        execution_status=status,
        numerical_verdict=f"record {index}",
        payload={"index": index},
        dim=201,
        deviation="synthetic failure" if status == "FAILED" else None,
    )


def test_append_links_the_chain(tmp_path: Path) -> None:
    path = tmp_path / "chrono.jsonl"
    first = ledger.append_record(_record(0), path)
    second = ledger.append_record(_record(1), path)
    third = ledger.append_record(_record(2), path)

    assert first["index"] == 0
    assert first["previous_hash"] == "GENESIS"
    assert second["previous_hash"] == first["record_hash"]
    assert third["previous_hash"] == second["record_hash"]
    assert ledger.verify_chain(path) == []
    assert len(path.read_text(encoding="utf-8").splitlines()) == 3


def test_caller_cannot_forge_the_chain(tmp_path: Path) -> None:
    path = tmp_path / "chrono.jsonl"
    ledger.append_record(_record(0), path)
    forged = _record(1)
    forged["index"] = 99
    forged["previous_hash"] = "deadbeef"
    appended = ledger.append_record(forged, path)

    assert appended["index"] == 1
    assert appended["previous_hash"] != "deadbeef"
    assert ledger.verify_chain(path) == []


def test_failed_record_is_kept_as_an_honest_deviation(tmp_path: Path) -> None:
    path = tmp_path / "chrono.jsonl"
    failed = ledger.append_record(_record(0, status="FAILED"), path)

    assert failed["execution_status"] == "FAILED"
    assert failed["deviation"] == "synthetic failure"
    assert failed["scope"] == {
        "rh_claim": False,
        "zero_location_claim": False,
        "weil_positivity_claim": False,
    }
    assert ledger.verify_chain(path) == []


def test_make_record_rejects_invalid_status() -> None:
    with pytest.raises(ValueError):
        ledger.make_record(
            rule_id="X",
            run_id="r",
            execution_status="CERTIFIED",
            numerical_verdict="no",
            payload={},
        )


def test_failed_record_requires_a_deviation() -> None:
    with pytest.raises(ValueError):
        ledger.make_record(
            rule_id="X",
            run_id="r",
            execution_status="FAILED",
            numerical_verdict="no",
            payload={},
        )


def test_tampering_breaks_the_chain(tmp_path: Path) -> None:
    path = tmp_path / "chrono.jsonl"
    ledger.append_record(_record(0), path)
    ledger.append_record(_record(1), path)

    lines = path.read_text(encoding="utf-8").splitlines()
    payload = json.loads(lines[1])
    payload["numerical_verdict"] = "tampered"
    lines[1] = json.dumps(payload, sort_keys=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    errors = ledger.verify_chain(path)
    assert errors
    assert any("record_hash" in error for error in errors)


def test_committed_ledger_is_valid_and_scoped() -> None:
    path = ROOT / "ledger" / "chrono_execution_ledger.jsonl"
    assert path.is_file(), "ledger/chrono_execution_ledger.jsonl is missing"
    assert ledger.verify_chain(path) == []

    records = ledger.read_records(path)
    assert records, "the committed ledger must contain at least one record"
    for record in records:
        assert record["execution_status"] in {"PASS", "FAILED"}
        assert record["scope"] == {
            "rh_claim": False,
            "zero_location_claim": False,
            "weil_positivity_claim": False,
        }
        assert len(record["payload_sha256"]) == 64
        assert record["previous_hash"] == (
            "GENESIS" if record["index"] == 0 else records[record["index"] - 1]["record_hash"]
        )
