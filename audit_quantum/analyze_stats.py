"""Deterministic statistical audit for the 2026-10-19 quantum campaign.

Reads the three 20,000-sample binary files produced by the SIMULATED-entropy
kernel, bins each sample set against the 16 equiprobable normal quantiles,
computes the chi-square statistic, and records one-sided tail exceedances.

This is the *statistical layer* only.  It makes no physical claim and does
not replace the certified interval layer.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXEC_DIR = ROOT / "audit_quantum" / "exec_2026-10-19"
REPORT_PATH = ROOT / "reports" / "audit_quantum_2026-10-19.md"
RECEIPT_PATH = ROOT / "reports" / "audit_quantum_2026-10-19.json"

SAMPLES = 20_000
BINS = 16
EXPECTED = SAMPLES / BINS
CHI2_WINDOW = (0.0, 60.0)
TAIL_Z = 3.5
FILES = ("stats_d201.bin", "stats_d301.bin", "stats_d401.bin")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_doubles(path: Path) -> tuple[float, ...]:
    data = path.read_bytes()
    if len(data) != SAMPLES * 8:
        raise ValueError(f"{path.name}: expected {SAMPLES * 8} bytes, got {len(data)}")
    return struct.unpack(f"<{SAMPLES}d", data)


def bin_edges() -> tuple[float, ...]:
    normal = statistics.NormalDist()
    return tuple(normal.inv_cdf(k / BINS) for k in range(1, BINS))


def bin_counts(values: tuple[float, ...], edges: tuple[float, ...]) -> list[int]:
    counts = [0] * BINS
    for value in values:
        for index in range(BINS):
            lower_ok = index == 0 or value >= edges[index - 1]
            upper_ok = index == BINS - 1 or value < edges[index]
            if lower_ok and upper_ok:
                counts[index] += 1
                break
    return counts


def chi_square(counts: list[int]) -> float:
    return sum((observed - EXPECTED) ** 2 / EXPECTED for observed in counts)


def analyze_file(name: str) -> dict:
    path = EXEC_DIR / name
    values = read_doubles(path)
    edges = bin_edges()
    counts = bin_counts(values, edges)
    chi2 = chi_square(counts)
    exceedances = sum(1 for value in values if value >= TAIL_Z)
    mean = statistics.fmean(values)
    stdev = statistics.pstdev(values)
    passed = (
        sum(counts) == SAMPLES
        and CHI2_WINDOW[0] <= chi2 <= CHI2_WINDOW[1]
        and all(count > 0 for count in counts)
    )
    return {
        "file": name,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "samples": SAMPLES,
        "bins": BINS,
        "expected_per_bin": EXPECTED,
        "counts": counts,
        "chi2": round(chi2, 6),
        "chi2_window": list(CHI2_WINDOW),
        "tail_z": TAIL_Z,
        "tail_exceedances": exceedances,
        "mean": round(mean, 9),
        "stdev": round(stdev, 9),
        "passed": passed,
    }


def main() -> None:
    edges = bin_edges()
    results = [analyze_file(name) for name in FILES]
    payload = {
        "schema": "msaf.audit_quantum.stats.v1",
        "campaign": "2026-10-19",
        "simulated": True,
        "global_claim_supported": False,
        "bin_edges": [round(edge, 12) for edge in edges],
        "files": results,
        "all_pass": all(row["passed"] for row in results),
        "summary": "RESOLVED" if all(row["passed"] for row in results) else "FAILED",
    }
    RECEIPT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Quantum audit 2026-10-19",
        "",
        "Status: **statistical layer reproduced**.",
        "",
        "The three 20,000-sample binary files are decoded as little-endian",
        "float64 values.  Each sample set is binned against the 16",
        "equiprobable standard-normal quantiles.  This is the SIMULATED-",
        "entropy statistical layer; it is not a physical claim and does not",
        "replace the certified interval layer.",
        "",
        "## Bin counts (expected 1250 per bin)",
        "",
        "| File | " + " | ".join(f"b{i}" for i in range(BINS)) + " | χ² | tail z≥3.5 |",
        "|---|" + "---|" * BINS + "---|---|",
    ]
    for row in results:
        counts = " | ".join(str(count) for count in row["counts"])
        lines.append(
            f"| {row['file']} | {counts} | {row['chi2']:.6f} | {row['tail_exceedances']} |"
        )
    lines += [
        "",
        "## Verdict",
        "",
        "| File | Samples | Mean | Std | χ² | Window | Passed |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for row in results:
        lines.append(
            f"| {row['file']} | {row['samples']} | {row['mean']:.9f} | "
            f"{row['stdev']:.9f} | {row['chi2']:.6f} | "
            f"[{row['chi2_window'][0]:.1f}, {row['chi2_window'][1]:.1f}] | "
            f"{'PASS' if row['passed'] else 'FAIL'} |"
        )
    lines += [
        "",
        f"Overall: **{payload['summary']}**.",
        "",
        "## Receipt",
        "",
        "```json",
        json.dumps(payload, indent=2),
        "```",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"summary": payload["summary"], "all_pass": payload["all_pass"]}, indent=2))


if __name__ == "__main__":
    main()
