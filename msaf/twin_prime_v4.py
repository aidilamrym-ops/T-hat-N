"""Twinâ€‘prime census v4: exact deterministic count for N = 10^10.

Implements the locked v4 scope from
``reports/PREREG_Q2_TWIN_PRIME_V4_2026-10-30.md``.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from itertools import zip_longest
from pathlib import Path
from typing import Iterator, Sequence

ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = ROOT / "reports" / "PREREG_Q2_TWIN_PRIME_V4_2026-10-30.md"
RECEIPT_PATH = ROOT / "reports" / "twin_prime_v4_2026-10-30.json"
SCHEMA = "msaf.twin_prime_v4.v1"

DEFAULT_N = 10_000_000_000
BASE_LIMIT = 100_000
BLOCK = 1 << 24
SCAN_CHUNK = 1 << 20

CHECKPOINT_REFERENCES = {
    10**6: 8_169,
    10**7: 58_980,
    10**8: 440_312,
    10**9: 3_424_506,
}

def sha256lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()

def canonical_bytes(payload: object) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")

def _base_primes(limit: int) -> list[int]:
    if limit < 2:
        return []
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for v in range(2, math.isqrt(limit) + 1):
        if flags[v]:
            start = v * v
            flags[start : limit + 1 : v] = b"\x00" * (((limit - start) // v) + 1)
    return [v for v in range(2, limit + 1) if flags[v]]

def _positions_both_set(flags: bytearray, stop: int, chunk: int = SCAN_CHUNK) -> Iterator[int]:
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
    if n < 3:
        return
    limit = n + 2
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for v in range(2, math.isqrt(limit) + 1):
        if flags[v]:
            start = v * v
            flags[start : limit + 1 : v] = b"\x00" * (((limit - start) // v) + 1)
    odd = flags[1::2]
    del flags
    stop = (n + 1) // 2
    for k in _positions_both_set(odd, stop):
        yield (2 * k + 1, 2 * k + 3)

def iter_pairs_b(n: int = DEFAULT_N) -> Iterator[tuple[int, int]]:
    if n < 3:
        return
    base = _base_primes(BASE_LIMIT)
    low = 3
    while low <= n:
        high = min(low + BLOCK - 1, n)
        seg_high = high + 2
        segment = bytearray(b"\x01") * (seg_high - low + 1)
        for v in base:
            start = max(v * v, ((low + v - 1) // v) * v)
            if start > seg_high:
                continue
            segment[start - low : seg_high - low + 1 : v] = b"\x00" * (((seg_high - start) // v) + 1)
        odd = segment[0::2]
        stop = (high - low) // 2 + 1
        pos = odd.find(b"\x01")
        while pos != -1 and pos < stop:
            if odd[pos + 1]:
                value = low + 2 * pos
                yield (value, value + 2)
            pos = odd.find(b"\x01", pos + 1)
        low = high + 1

@dataclass
class StreamSummary:
    checkpoints: Sequence[int]
    def __post_init__(self) -> None:
        self.count = 0
        self.max_gap = 0
        self.first: tuple[int, int] | None = None
        self.last: tuple[int, int] | None = None
        self.checkpoint_counts = {p: 0 for p in self.checkpoints}
        self._idx = 0
        self._prev: int | None = None
        self._digest = hashlib.sha256()
    def add(self, pair: tuple[int, int]) -> None:
        p, q = pair
        while self._idx < len(self.checkpoints) and p > self.checkpoints[self._idx]:
            cp = self.checkpoints[self._idx]
            self.checkpoint_counts[cp] = self.count
            self._idx += 1
        if self.first is None:
            self.first = pair
        if self._prev is not None:
            gap = p - self._prev
            if gap > self.max_gap:
                self.max_gap = gap
        self._prev = p
        self.last = pair
        self.count += 1
        self._digest.update(p.to_bytes(8, "big") + q.to_bytes(8, "big"))
    def finish(self) -> "StreamSummary":
        while self._idx < len(self.checkpoints):
            cp = self.checkpoints[self._idx]
            self.checkpoint_counts[cp] = self.count
            self._idx += 1
        self.digest = self._digest.hexdigest()
        return self

def build_payload() -> dict:
    checkpoints = sorted(CHECKPOINT_REFERENCES.keys())
    summary_a = StreamSummary(checkpoints)
    summary_b = StreamSummary(checkpoints)
    mismatches = 0
    for a, b in zip_longest(iter_pairs_a(), iter_pairs_b()):
        if a != b:
            mismatches += 1
        if a is not None:
            summary_a.add(a)
        if b is not None:
            summary_b.add(b)
    summary_a.finish()
    summary_b.finish()
    payload = {
        "schema": SCHEMA,
        "prereg_sha256lf": sha256lf(PREREG_PATH),
        "module_sha256lf": sha256lf(Path(__file__)),
        "count_a": summary_a.count,
        "count_b": summary_b.count,
        "elementwise_mismatches": mismatches,
        "checkpoints": [
            {"x": cp, "reference": CHECKPOINT_REFERENCES[cp], "count_a": summary_a.checkpoint_counts[cp], "count_b": summary_b.checkpoint_counts[cp]}
            for cp in checkpoints
        ],
        "pairs_sha256_a": summary_a.digest,
        "pairs_sha256_b": summary_b.digest,
        "all_pass": mismatches == 0,
        "summary": "ALL PASS" if mismatches == 0 else "FAILED",
        "volatile_fields": [],
    }
    RECEIPT_PATH.write_bytes(canonical_bytes(payload))
    return payload

def main() -> None:
    payload = build_payload()
    RECEIPT_PATH.write_bytes(canonical_bytes(payload))
    print(json.dumps({"summary": payload["summary"], "receipt": str(RECEIPT_PATH)}, indent=2))

if __name__ == "__main__":
    main()


