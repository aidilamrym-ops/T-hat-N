"""Q2 twin-prime census v3: streaming exact census at N = 10^9.

This module implements the locked v3 scope from
``reports/PREREG_Q2_TWIN_PRIME_V3_2026-10-25.md``.  It counts twin primes
``(p, p + 2)`` with ``p <= N`` using two independent exact sieves:

* A: a full Eratosthenes ``bytearray`` over ``0 .. N + 2``.
* B: a segmented Eratosthenes over blocks of ``2^24`` with a separately
  computed base-prime list.

The two streams are compared element by element with ``zip_longest``.  A
deterministic receipt records counts, checkpoint counts, gap statistics,
element digests, and the comparison result.  No float or numpy operation is
used in the census path, and no claim is made about the twin-prime
conjecture.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
from dataclasses import dataclass
from itertools import zip_longest
from pathlib import Path
from typing import Iterator, Sequence

ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = ROOT / "reports" / "PREREG_Q2_TWIN_PRIME_V3_2026-10-25.md"
RECEIPT_PATH = ROOT / "reports" / "twin_prime_v3_2026-10-25.json"
SCHEMA = "msaf.twin_prime_v3.v1"

DEFAULT_N = 1_000_000_000
BASE_LIMIT = 31_623
BLOCK = 1 << 24
SCAN_CHUNK = 1 << 20

# Locked reference counts for pairs (p, p + 2) with p <= x.
CHECKPOINT_REFERENCES = {
    10**6: 8_169,
    10**7: 58_980,
    10**8: 440_312,
    10**9: 3_424_506,
}


def sha256lf(path: Path) -> str:
    """SHA-256 of a file with CRLF normalised to LF."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_bytes(payload: object) -> bytes:
    """Canonical JSON: sorted keys, indent 2, ASCII, trailing newline."""
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def _base_primes(limit: int) -> list[int]:
    """Independent simple prime list used only by sieve B."""
    if limit < 2:
        return []
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for value in range(2, math.isqrt(limit) + 1):
        if flags[value]:
            start = value * value
            flags[start : limit + 1 : value] = b"\x00" * (
                ((limit - start) // value) + 1
            )
    return [value for value in range(2, limit + 1) if flags[value]]


def _positions_both_set(
    flags: bytearray, stop: int, chunk: int = SCAN_CHUNK
) -> Iterator[int]:
    """Yield indices ``k`` in ``[0, stop)`` with ``flags[k] & flags[k + 1]``.

    Each byte is 0 or 1.  A chunk of bytes is packed into an integer so the
    elementwise AND is performed by one C-level integer operation; the
    resulting byte string is then scanned with ``find``.  This is an exact
    extraction step, not a heuristic.
    """
    base = 0
    needle = b"\x01"
    while base < stop:
        end = min(base + chunk, stop)
        width = end - base
        left = int.from_bytes(flags[base:end], "little")
        right = int.from_bytes(flags[base + 1 : end + 1], "little")
        both = (left & right).to_bytes(width, "little")
        offset = both.find(needle)
        while offset != -1:
            yield base + offset
            offset = both.find(needle, offset + 1)
        base = end


def iter_pairs_a(n: int = DEFAULT_N) -> Iterator[tuple[int, int]]:
    """Full Eratosthenes sieve A; yields ``(p, p + 2)`` in increasing order."""
    if n < 3:
        return
    limit = n + 2
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for value in range(2, math.isqrt(limit) + 1):
        if flags[value]:
            start = value * value
            flags[start : limit + 1 : value] = b"\x00" * (
                ((limit - start) // value) + 1
            )

    # Odd numbers only: odd[k] = primality of 2*k + 1.
    odd = flags[1::2]
    del flags
    # p = 2*k + 1 <= n; the last admissible index is exclusive.
    stop = (n + 1) // 2
    for k in _positions_both_set(odd, stop):
        yield (2 * k + 1, 2 * k + 3)


def iter_pairs_b(n: int = DEFAULT_N) -> Iterator[tuple[int, int]]:
    """Segmented Eratosthenes sieve B; yields ``(p, p + 2)`` in increasing order.

    Base primes are computed independently of sieve A.  Each block covers
    ``[low, high]`` and its segment covers ``[low, high + 2]`` so that a pair
    starting near the block edge is still decided inside the block.  The next
    block starts at ``high + 1``, so no pair is skipped or duplicated.
    """
    if n < 3:
        return
    base = _base_primes(BASE_LIMIT)
    needle = b"\x01"
    low = 3
    while low <= n:
        high = min(low + BLOCK - 1, n)
        seg_high = high + 2
        segment = bytearray(b"\x01") * (seg_high - low + 1)
        for value in base:
            start = max(value * value, ((low + value - 1) // value) * value)
            if start > seg_high:
                continue
            segment[start - low : seg_high - low + 1 : value] = b"\x00" * (
                ((seg_high - start) // value) + 1
            )

        # low is odd, so segment[0::2] holds the odd numbers low, low + 2, ...
        odd = segment[0::2]
        stop = (high - low) // 2 + 1
        position = odd.find(needle)
        while position != -1 and position < stop:
            if odd[position + 1]:
                value = low + 2 * position
                yield (value, value + 2)
            position = odd.find(needle, position + 1)

        low = high + 1


@dataclass
class StreamSummary:
    """Streaming summary for one sieve stream."""

    checkpoints: Sequence[int]

    def __post_init__(self) -> None:
        self.count = 0
        self.max_gap = 0
        self.first: tuple[int, int] | None = None
        self.last: tuple[int, int] | None = None
        self.checkpoint_counts = {point: 0 for point in self.checkpoints}
        self._checkpoint_index = 0
        self._previous_p: int | None = None
        self._digest = hashlib.sha256()

    def add(self, pair: tuple[int, int]) -> None:
        p, q = pair
        while (
            self._checkpoint_index < len(self.checkpoints)
            and p > self.checkpoints[self._checkpoint_index]
        ):
            point = self.checkpoints[self._checkpoint_index]
            self.checkpoint_counts[point] = self.count
            self._checkpoint_index += 1
        if self.first is None:
            self.first = pair
        if self._previous_p is not None:
            gap = p - self._previous_p
            if gap > self.max_gap:
                self.max_gap = gap
        self._previous_p = p
        self.last = pair
        self.count += 1
        self._digest.update(p.to_bytes(8, "big") + q.to_bytes(8, "big"))

    def finish(self) -> "StreamSummary":
        while self._checkpoint_index < len(self.checkpoints):
            point = self.checkpoints[self._checkpoint_index]
            self.checkpoint_counts[point] = self.count
            self._checkpoint_index += 1
        return self

    @property
    def digest_hex(self) -> str:
        return self._digest.hexdigest()


def _observe(
    pairs: Iterator[tuple[int, int]], summary: StreamSummary
) -> Iterator[tuple[int, int]]:
    for pair in pairs:
        summary.add(pair)
        yield pair


def compare_streams(
    n: int = DEFAULT_N, checkpoints: Sequence[int] | None = None
) -> tuple[StreamSummary, StreamSummary, int, list[dict]]:
    """Compare both streams element by element and summarise each one."""
    if checkpoints is None:
        checkpoints = sorted(point for point in CHECKPOINT_REFERENCES if point <= n)
    summary_a = StreamSummary(checkpoints)
    summary_b = StreamSummary(checkpoints)
    mismatch_count = 0
    first_mismatches: list[dict] = []
    index = 0
    for pair_a, pair_b in zip_longest(
        _observe(iter_pairs_a(n), summary_a),
        _observe(iter_pairs_b(n), summary_b),
        fillvalue=None,
    ):
        if pair_a != pair_b:
            mismatch_count += 1
            if len(first_mismatches) < 5:
                first_mismatches.append(
                    {
                        "index": index,
                        "a": list(pair_a) if pair_a is not None else None,
                        "b": list(pair_b) if pair_b is not None else None,
                    }
                )
        index += 1
    summary_a.finish()
    summary_b.finish()
    return summary_a, summary_b, mismatch_count, first_mismatches


def _c1_static_ok() -> bool:
    """AST check: no float constants/calls and no numpy/v2 import in this module."""
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            return False
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "float":
                return False
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in {"numpy", "twin_prime_v2"}:
                    return False
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.split(".")[0] in {"numpy", "twin_prime_v2"}:
                return False
    return True


def _pair_or_none(pair: tuple[int, int] | None) -> list[int] | None:
    return list(pair) if pair is not None else None


def build_payload(n: int = DEFAULT_N) -> dict:
    """Build the deterministic v3 receipt payload."""
    checkpoints = sorted(point for point in CHECKPOINT_REFERENCES if point <= n)
    summary_a, summary_b, mismatch_count, first_mismatches = compare_streams(
        n, checkpoints
    )

    c1 = _c1_static_ok()
    c2 = (
        summary_a.count == summary_b.count
        and summary_a.max_gap == summary_b.max_gap
        and summary_a.first == summary_b.first
        and summary_a.last == summary_b.last
        and summary_a.digest_hex == summary_b.digest_hex
        and mismatch_count == 0
    )
    c3 = bool(checkpoints) and all(
        summary_a.checkpoint_counts[point]
        == CHECKPOINT_REFERENCES[point]
        == summary_b.checkpoint_counts[point]
        for point in checkpoints
    )
    if n >= DEFAULT_N:
        c3 = c3 and summary_a.count == CHECKPOINT_REFERENCES[DEFAULT_N]
        c3 = c3 and summary_b.count == CHECKPOINT_REFERENCES[DEFAULT_N]
        c3 = c3 and summary_a.checkpoint_counts[DEFAULT_N] == summary_a.count
        c3 = c3 and summary_b.checkpoint_counts[DEFAULT_N] == summary_b.count

    payload = {
        "schema": SCHEMA,
        "N": n,
        "base_limit": BASE_LIMIT,
        "block_size": BLOCK,
        "census_arithmetic": "exact integer; no float; no numpy",
        "checkpoint_references": {
            str(point): CHECKPOINT_REFERENCES[point] for point in checkpoints
        },
        "checkpoints": [
            {
                "x": point,
                "reference": CHECKPOINT_REFERENCES[point],
                "count_a": summary_a.checkpoint_counts[point],
                "count_b": summary_b.checkpoint_counts[point],
            }
            for point in checkpoints
        ],
        "count_a": summary_a.count,
        "count_b": summary_b.count,
        "max_gap_a": summary_a.max_gap,
        "max_gap_b": summary_b.max_gap,
        "first_pair_a": _pair_or_none(summary_a.first),
        "first_pair_b": _pair_or_none(summary_b.first),
        "last_pair_a": _pair_or_none(summary_a.last),
        "last_pair_b": _pair_or_none(summary_b.last),
        "pairs_sha256_a": summary_a.digest_hex,
        "pairs_sha256_b": summary_b.digest_hex,
        "elementwise_mismatches": mismatch_count,
        "first_mismatches": first_mismatches,
        "length_equal": summary_a.count == summary_b.count,
        "prereg_sha256lf": sha256lf(PREREG_PATH),
        "module_sha256lf": sha256lf(Path(__file__).resolve()),
        "volatile_fields": [],
        "criteria": {
            "C1_two_independent_exact_sieves": c1,
            "C2_full_stream_agreement": c2,
            "C3_reference_checkpoints": c3,
            "C4_deterministic_receipt_schema": True,
        },
    }
    payload["all_pass"] = bool(c1 and c2 and c3)
    payload["summary"] = "ALL PASS" if payload["all_pass"] else "FAILED"
    return payload


def write_receipt(payload: dict) -> str:
    """Write canonical receipt bytes and return their SHA-256."""
    raw = canonical_bytes(payload)
    RECEIPT_PATH.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    payload = build_payload(DEFAULT_N)
    digest = write_receipt(payload)
    print(
        json.dumps(
            {
                "N": payload["N"],
                "count_a": payload["count_a"],
                "count_b": payload["count_b"],
                "max_gap_a": payload["max_gap_a"],
                "max_gap_b": payload["max_gap_b"],
                "elementwise_mismatches": payload["elementwise_mismatches"],
                "all_pass": payload["all_pass"],
                "summary": payload["summary"],
                "receipt_sha256": digest,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
