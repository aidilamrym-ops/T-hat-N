# -*- coding: utf-8 -*-
"""Guard for the certified abc census (Q3 v3, exhaustive low-rad)."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from msaf import abc_census as abc

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "msaf" / "abc_census.py"
CERT_RECEIPT = ROOT / "reports" / "abc_census.json"
PREREG_V3 = ROOT / "reports" / "PREREG_Q3_ABC_CENSUS_V3_2026-10-27.md"


def _certified_pairs() -> list[tuple[int, int, int]]:
    data = json.loads(CERT_RECEIPT.read_text(encoding="utf-8"))
    return [tuple(int(x) for x in pair) for pair in data["pairs_a"]]


def _run_campaign(tmp_path: Path, name: str, **kwargs) -> abc.CampaignOutcome:
    return abc.run_campaign(
        abc.GATE_N,
        tmp_path / f"{name}.json",
        progress_path=tmp_path / f"{name}.progress.log",
        checkpoint_path=tmp_path / f"{name}.ckpt.json",
        max_seconds=0,
        echo=False,
        **kwargs,
    )


def test_locked_configuration() -> None:
    rad = abc._rad_sieve(100)
    assert rad[30] == 30
    assert rad[12] == 6
    assert rad[18] == 6


def test_rad_limit_is_conservative() -> None:
    for N in (abc.GATE_N, abc.VALIDATE_N, abc.FULL_N):
        limit = abc._rad_limit(N)
        assert limit**7 > N**5


def test_rad_sieves_agree() -> None:
    limit = 20_000
    rad_a = abc._rad_sieve(limit)
    rad_b = abc._rad_sieve_segmented(limit, segment_size=4096)
    assert list(rad_b) == rad_a


def test_low_rad_builders_agree() -> None:
    N = 20_000
    bound = abc._rad_limit(N)
    rad_a = abc._rad_sieve(N)
    rad_b = abc._rad_sieve_segmented(N, segment_size=4096)
    low_a, is_low_a, by_rad_a, sorted_a = abc._build_low_rad_a(rad_a, N, bound)
    low_b, is_low_b, by_rad_b, sorted_b = abc._build_low_rad_b(rad_b, N, bound)
    assert low_a == low_b
    assert bytes(is_low_a) == bytes(is_low_b)
    assert by_rad_a == by_rad_b
    assert sorted_a == sorted_b


def test_known_abc_hits() -> None:
    result = abc._abc_census_main(abc.GATE_N)
    assert (result.count_a, result.count_b) == (6, 6)
    assert (result.max_gap_a, result.max_gap_b) == (6825, 6825)
    assert result.pairs_a == result.pairs_b == _certified_pairs()
    assert abc.verify_agreement(result)


def test_validation_1e6_counts_eleven() -> None:
    result = abc._abc_census_main(abc.VALIDATE_N)
    assert (result.count_a, result.count_b) == (11, 11)
    assert (result.max_gap_a, result.max_gap_b) == (6825, 6825)
    assert result.pairs_a == result.pairs_b
    assert (5, 177147, 177152) in result.pairs_a
    assert abc.verify_agreement(result)


def test_prereg_hash_is_locked() -> None:
    assert PREREG_V3.exists()
    assert abc._sha256lf(PREREG_V3) == abc.PREREG_SHA256LF


def test_gate_100k_campaign_receipt(tmp_path: Path) -> None:
    outcome = _run_campaign(tmp_path, "gate")
    assert outcome.status == "DONE"
    receipt = outcome.receipt
    assert receipt is not None
    assert receipt["schema"] == abc.SCHEMA
    assert receipt["N"] == abc.GATE_N
    assert receipt["threshold"] == abc.THRESHOLD
    assert receipt["rad_limit"] == abc._rad_limit(abc.GATE_N)
    assert receipt["count"] == 6
    assert receipt["max_gap"] == 6825
    assert receipt["first_triple"] == [3, 125, 128]
    assert [tuple(pair) for pair in receipt["pairs_a"]] == _certified_pairs()
    assert receipt["pairs_a"] == receipt["pairs_b"]
    assert receipt["prereg_sha256lf"] == abc.PREREG_SHA256LF
    assert receipt["module_sha256lf"] == abc._sha256lf(MODULE)
    assert receipt["canonical_sha256"] == abc._canonical_sha256(receipt)
    assert len(receipt["canonical_sha256"]) == 64
    if abc.HAS_SYMPY:
        assert receipt["factorint_verified"] is True
        assert receipt["verdict"] == "ALL PASS"
    else:
        assert receipt["verdict"] == "INCONCLUSIVE"
    assert outcome.receipt_path.exists()
    assert not Path(str(outcome.receipt_path) + ".tmp").exists()
    assert not outcome.checkpoint_path.exists()
    log_text = outcome.progress_path.read_text(encoding="utf-8")
    assert "receipt written" in log_text
    assert "sieve_a scan" in log_text
    assert "sieve_b scan" in log_text


def test_canonical_hash_is_deterministic(tmp_path: Path) -> None:
    first = _run_campaign(tmp_path, "first").receipt
    second = _run_campaign(tmp_path, "second").receipt
    assert first is not None and second is not None
    assert first["canonical_sha256"] == second["canonical_sha256"]
    assert first["pairs_a"] == second["pairs_a"]
    assert first["pairs_b"] == second["pairs_b"]


def test_resume_matches_clean_run(tmp_path: Path) -> None:
    clean = _run_campaign(tmp_path, "clean").receipt
    assert clean is not None

    out = tmp_path / "resumed.json"
    progress = tmp_path / "resumed.progress.log"
    checkpoint = tmp_path / "resumed.ckpt.json"
    chunks = 0
    while True:
        outcome = abc.run_campaign(
            abc.GATE_N,
            out,
            progress_path=progress,
            checkpoint_path=checkpoint,
            max_seconds=0,
            max_c_per_chunk=6000,
            echo=False,
        )
        chunks += 1
        assert chunks < 50
        if outcome.status == "DONE":
            break
        assert outcome.status == "CHUNKED"
        assert checkpoint.exists()

    assert chunks > 1
    assert outcome.receipt is not None
    assert outcome.receipt["canonical_sha256"] == clean["canonical_sha256"]
    assert outcome.receipt["pairs_a"] == clean["pairs_a"]


def test_factorint_only_in_final_verifier() -> None:
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            attrs = {
                child.attr
                for child in ast.walk(node)
                if isinstance(child, ast.Attribute)
            }
            if "factorint" in attrs:
                found.add(node.name)
    assert found == {"_factorint_rad"}


def test_core_has_no_numpy() -> None:
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
            imports.extend(alias.name for alias in node.names)
    assert not any(name == "numpy" or name.startswith("numpy.") for name in imports)


def test_committed_receipt_is_locked() -> None:
    if not CERT_RECEIPT.exists():
        pytest.skip("Receipt file not found")
    data = json.loads(CERT_RECEIPT.read_text(encoding="utf-8"))
    assert data["count"] == 6
    assert data["max_gap"] == 6825
    assert data["count_a"] == 6
    assert data["count_b"] == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
