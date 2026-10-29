"""Certified abc census - exhaustive low-rad sieves (v3).

The module searches for abc triples (a, b, c) with a + b = c, a < b < c,
gcd(a, b, c) = 1, and quality q = log(c) / log(rad(a*b*c)) > 1.4.

Completeness argument: q > 1.4 implies rad(abc) < c**(5/7) <= N**(5/7), so
every member of a valid triple has rad(n) <= floor(N**(5/7)) + 1. Both sieves
therefore enumerate the low-rad set L_N = {n <= N : rad(n) <= RAD_LIMIT(N)}
instead of restricting to 100-smooth numbers. The old 100-smooth restriction
is incomplete: triples such as (2, 6436341, 6436343) contain prime 109.

Sieve A builds rad with a multiplicative list sieve. Sieve B builds rad with
a segmented sieve over 32-bit unsigned integers, constructs L_N independently,
and re-verifies every final triple with sympy.factorint. factorint is never
called for every integer in 3..N.

Both sieves must agree exactly on count, max_gap, and the sorted list of
triples. Candidate acceptance uses the exact integer test prod**7 < c**5;
the reported q uses float64 math.log and is informational.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from array import array
from bisect import bisect_right
from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import islice
from math import gcd, log
from pathlib import Path

try:
    import sympy

    HAS_SYMPY = True
except ImportError:  # pragma: no cover - sympy is optional in CI
    HAS_SYMPY = False


SCHEMA = "msaf.abc_census.v3"
CHECKPOINT_SCHEMA = "msaf.abc_census.v3.checkpoint"
THRESHOLD = 1.4
GATE_N = 100_000
VALIDATE_N = 1_000_000
FULL_N = 10_000_000
DEFAULT_SEGMENT_SIZE = 1 << 20
PREREG_SHA256LF = (
    "aed8e63cdbb463b58bf207686ddf562ae50114b1d38b40f52174e53f1a6001a2"
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREREG = REPO_ROOT / "reports" / "PREREG_Q3_ABC_CENSUS_V3_2026-10-27.md"
CERTIFIED_RECEIPT = REPO_ROOT / "reports" / "abc_census.json"


@dataclass(frozen=True)
class ABCResult:
    N: int
    count: int
    pairs: list[tuple[int, int, int]]
    max_gap: int
    first_triple: tuple[int, int, int] | None
    last_triple: tuple[int, int, int] | None
    runtime_a: float
    runtime_b: float
    count_a: int
    count_b: int
    max_gap_a: int
    max_gap_b: int
    pairs_a: list[tuple[int, int, int]]
    pairs_b: list[tuple[int, int, int]]


@dataclass
class SieveState:
    """Mutable progress of one sieve inside one chunked campaign."""

    next_index: int = 0
    count: int = 0
    max_gap: int = 0
    last_a: int | None = None
    pairs: list[tuple[int, int, int]] = field(default_factory=list)
    runtime: float = 0.0
    done: bool = False


@dataclass(frozen=True)
class CampaignOutcome:
    status: str
    receipt: dict | None
    receipt_path: Path
    checkpoint_path: Path
    progress_path: Path


def _sha256lf(path: str | os.PathLike[str]) -> str:
    """SHA-256 of a file after normalizing CRLF to LF."""
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def _rad_limit(N: int) -> int:
    """Conservative integer bound floor(N**(5/7)) + 1."""
    return int(N ** (5.0 / 7.0)) + 1


def _rad_sieve(limit: int) -> list[int]:
    """Compute rad(n) for all n up to limit with one multiplicative pass.

    A number i is prime exactly when rad[i] is still 1 when the loop reaches
    it, because every prime factor < i would already have multiplied rad[i].
    """
    if limit < 0:
        raise ValueError("limit must be non-negative")
    rad = [1] * (limit + 1)
    rad[0] = 0
    for i in range(2, limit + 1):
        if rad[i] == 1:  # i is prime
            for j in range(i, limit + 1, i):
                rad[j] *= i
    return rad


def _primes_upto(limit: int) -> list[int]:
    """Return all primes <= limit with a bytearray sieve."""
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    root = int(limit**0.5)
    for p in range(2, root + 1):
        if sieve[p]:
            start = p * p
            count = (limit - start) // p + 1
            sieve[start : limit + 1 : p] = b"\x00" * count
    return [i for i in range(2, limit + 1) if sieve[i]]


def _rad_sieve_segmented(
    limit: int, segment_size: int = DEFAULT_SEGMENT_SIZE
) -> array:
    """Compute rad(n) for all n up to limit with a segmented sieve.

    Values are stored in a 32-bit unsigned array, reducing memory relative to
    a Python list of int objects. This routine is used only by Sieve B and does
    not import any Sieve A helper.
    """
    if limit < 0:
        raise ValueError("limit must be non-negative")
    if segment_size < 1:
        raise ValueError("segment_size must be positive")
    rad = array("I", [1]) * (limit + 1)
    rad[0] = 0
    primes = _primes_upto(limit)
    for lo in range(2, limit + 1, segment_size):
        hi = min(lo + segment_size - 1, limit)
        for p in primes:
            if p > hi:
                break
            start = ((lo + p - 1) // p) * p
            for j in range(start, hi + 1, p):
                rad[j] *= p
    return rad


def _build_low_rad_a(
    rad: list[int], N: int, limit: int
) -> tuple[list[int], bytearray, list[int], list[int]]:
    """Build the low-rad set for Sieve A.

    Returns (low ascending by value, membership bitmap, low sorted by rad,
    rad values aligned with the rad-sorted list).
    """
    low = [n for n in range(1, N + 1) if rad[n] <= limit]
    is_low = bytearray(N + 1)
    for n in low:
        is_low[n] = 1
    low_by_rad = sorted(low, key=rad.__getitem__)
    rad_sorted = [rad[n] for n in low_by_rad]
    return low, is_low, low_by_rad, rad_sorted


def _build_low_rad_b(
    rad: array, N: int, limit: int
) -> tuple[list[int], bytearray, list[int], list[int]]:
    """Build the low-rad set for Sieve B from its own rad array."""
    low: list[int] = []
    is_low = bytearray(N + 1)
    for n in range(1, N + 1):
        if rad[n] <= limit:
            low.append(n)
            is_low[n] = 1
    low_by_rad = sorted(low, key=rad.__getitem__)
    rad_sorted = [rad[n] for n in low_by_rad]
    return low, is_low, low_by_rad, rad_sorted


def _scan_sieve_a(
    low: list[int],
    rad: list[int],
    is_low: bytearray,
    low_by_rad: list[int],
    rad_sorted: list[int],
    state: SieveState,
    *,
    deadline: float | None = None,
    max_c: int | None = None,
    checkpoint_every: int = 512,
    threshold: float = THRESHOLD,
) -> bool:
    """Advance Sieve A until exhaustion, a deadline, or max_c low-rad values.

    Returns True when the sieve reached the end of the low-rad list.
    """
    n = len(low)
    idx = state.next_index
    if idx >= n:
        state.done = True
        return True

    gcd_ = gcd
    log_ = log
    bisect_ = bisect_right
    islice_ = islice
    rad_get = rad.__getitem__
    processed = 0

    while idx < n:
        c = low[idx]
        idx += 1
        state.next_index = idx
        processed += 1

        if c >= 3:
            rc = rad_get(c)
            c5 = c**5
            if rc**7 < c5:
                c_log = log_(c)
                # rad(a) * rad(c) < c**(5/7); +2 absorbs float rounding and
                # the exact integer test below makes the final decision.
                limit_a = int(c ** (5.0 / 7.0) / rc) + 2
                prefix = bisect_(rad_sorted, limit_a)
                for a in islice_(low_by_rad, prefix):
                    if 2 * a >= c:
                        continue
                    b = c - a
                    if not is_low[b]:
                        continue
                    prod = rad_get(a) * rad_get(b) * rc
                    if prod**7 >= c5:
                        continue
                    if gcd_(a, b) != 1:
                        continue
                    if c_log / log_(prod) > threshold:
                        if state.last_a is not None:
                            gap = a - state.last_a
                            if gap > state.max_gap:
                                state.max_gap = gap
                        state.last_a = a
                        state.count += 1
                        state.pairs.append((a, b, c))

        if checkpoint_every and processed % checkpoint_every == 0:
            if max_c is not None and processed >= max_c:
                return False
            if deadline is not None and time.perf_counter() >= deadline:
                return False

    state.done = True
    return True


def _scan_sieve_b(
    low: list[int],
    rad: array,
    is_low: bytearray,
    low_by_rad: list[int],
    rad_sorted: list[int],
    state: SieveState,
    *,
    deadline: float | None = None,
    max_c: int | None = None,
    checkpoint_every: int = 512,
    threshold: float = THRESHOLD,
) -> bool:
    """Advance Sieve B; independent code path from Sieve A.

    Returns True when the sieve reached the end of the low-rad list.
    """
    n = len(low)
    idx = state.next_index
    if idx >= n:
        state.done = True
        return True

    processed = 0

    while idx < n:
        c = low[idx]
        idx += 1
        state.next_index = idx
        processed += 1

        if c >= 3:
            rc = rad[c]
            c5 = c**5
            if rc**7 < c5:
                c_log = log(c)
                bound = int(c ** (5.0 / 7.0) / rc) + 2
                prefix = bisect_right(rad_sorted, bound)
                k = 0
                while k < prefix:
                    a = low_by_rad[k]
                    k += 1
                    if 2 * a >= c:
                        continue
                    b = c - a
                    if not is_low[b]:
                        continue
                    prod = rad[a] * rad[b] * rc
                    if prod**7 >= c5:
                        continue
                    if gcd(a, b) != 1:
                        continue
                    if c_log / log(prod) > threshold:
                        if state.last_a is not None:
                            gap = a - state.last_a
                            if gap > state.max_gap:
                                state.max_gap = gap
                        state.last_a = a
                        state.count += 1
                        state.pairs.append((a, b, c))

        if checkpoint_every and processed % checkpoint_every == 0:
            if max_c is not None and processed >= max_c:
                return False
            if deadline is not None and time.perf_counter() >= deadline:
                return False

    state.done = True
    return True


def _factorint_rad(n: int) -> int:
    """Return rad(n) using sympy.factorint."""
    if n <= 1:
        return 1
    result = 1
    for p in sympy.factorint(n):
        result *= int(p)
    return result


def verify_pairs_with_factorint(
    pairs: list[tuple[int, int, int]], threshold: float = THRESHOLD
) -> bool:
    """Re-verify final triples with sympy.factorint.

    This is the only place where factorint is used. It runs on the final hits,
    not on every integer in 3..N.
    """
    if not HAS_SYMPY:
        return False
    for a, b, c in pairs:
        if a + b != c or a >= b or gcd(a, b) != 1:
            return False
        rabc = _factorint_rad(a * b * c)
        if rabc <= 1:
            return False
        if log(c) / log(rabc) <= threshold:
            return False
    return True


def _canonical_sha256(payload: dict) -> str:
    """Canonical hash excluding runtimes and the hash field itself."""
    core = {
        key: value
        for key, value in payload.items()
        if key not in ("runtime_a", "runtime_b", "canonical_sha256")
    }
    blob = json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _atomic_write_json(path: str | os.PathLike[str], payload: dict) -> None:
    """Write JSON atomically through a sibling .tmp file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + ".tmp")
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, target)


def _state_to_json(state: SieveState) -> dict:
    return {
        "next_index": state.next_index,
        "count": state.count,
        "max_gap": state.max_gap,
        "last_a": state.last_a,
        "pairs": [list(pair) for pair in state.pairs],
        "runtime": state.runtime,
        "done": state.done,
    }


def _state_from_json(data: dict) -> SieveState:
    pairs = [tuple(int(x) for x in pair) for pair in data.get("pairs", [])]
    last_a = data.get("last_a")
    return SieveState(
        next_index=int(data.get("next_index", 0)),
        count=int(data.get("count", 0)),
        max_gap=int(data.get("max_gap", 0)),
        last_a=None if last_a is None else int(last_a),
        pairs=pairs,
        runtime=float(data.get("runtime", 0.0)),
        done=bool(data.get("done", False)),
    )


def _save_checkpoint(
    path: str | os.PathLike[str],
    N: int,
    prereg_hash: str,
    state_a: SieveState,
    state_b: SieveState,
) -> None:
    payload = {
        "schema": CHECKPOINT_SCHEMA,
        "N": N,
        "threshold": THRESHOLD,
        "rad_limit": _rad_limit(N),
        "prereg_sha256lf": prereg_hash,
        "sieves": {
            "a": _state_to_json(state_a),
            "b": _state_to_json(state_b),
        },
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _atomic_write_json(path, payload)


class _ProgressLog:
    def __init__(self, path: str | os.PathLike[str], echo: bool = True) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.path.open("a", encoding="utf-8", newline="\n")
        self.echo = echo

    def log(self, message: str) -> None:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        line = f"{stamp} {message}"
        self._fh.write(line + "\n")
        self._fh.flush()
        if self.echo:
            print(line, flush=True)

    def close(self) -> None:
        self._fh.close()

    def __enter__(self) -> "_ProgressLog":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def _build_receipt(
    N: int,
    state_a: SieveState,
    state_b: SieveState,
    prereg_hash: str,
    module_hash: str,
    factorint_verified: bool,
    threshold: float,
) -> dict:
    pairs_a = [list(pair) for pair in state_a.pairs]
    pairs_b = [list(pair) for pair in state_b.pairs]
    agree = (
        state_a.count == state_b.count
        and state_a.max_gap == state_b.max_gap
        and state_a.pairs == state_b.pairs
    )
    if not agree:
        verdict = "FAILED"
    elif not factorint_verified:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "ALL PASS"

    receipt = {
        "schema": SCHEMA,
        "N": N,
        "threshold": threshold,
        "rad_limit": _rad_limit(N),
        "candidate_rule": "low-rad enumeration; exact prod**7 < c**5",
        "quality_bound": "exact integer prod**7 < c**5; q reported via float64 math.log",
        "count": state_a.count,
        "max_gap": state_a.max_gap,
        "first_triple": pairs_a[0] if pairs_a else None,
        "last_triple": pairs_a[-1] if pairs_a else None,
        "count_a": state_a.count,
        "count_b": state_b.count,
        "max_gap_a": state_a.max_gap,
        "max_gap_b": state_b.max_gap,
        "pairs_a": pairs_a,
        "pairs_b": pairs_b,
        "runtime_a": state_a.runtime,
        "runtime_b": state_b.runtime,
        "prereg_sha256lf": prereg_hash,
        "module_sha256lf": module_hash,
        "factorint_verified": bool(factorint_verified),
        "verdict": verdict,
    }
    receipt["canonical_sha256"] = _canonical_sha256(receipt)
    return receipt


def run_campaign(
    N: int,
    out: str | os.PathLike[str],
    *,
    progress_path: str | os.PathLike[str] | None = None,
    checkpoint_path: str | os.PathLike[str] | None = None,
    max_seconds: float | None = 900.0,
    resume: bool = True,
    segment_size: int = DEFAULT_SEGMENT_SIZE,
    threshold: float = THRESHOLD,
    checkpoint_every: int = 512,
    max_c_per_chunk: int | None = None,
    prereg_path: str | os.PathLike[str] | None = DEFAULT_PREREG,
    echo: bool = True,
) -> CampaignOutcome:
    """Run or resume one chunk of the abc census campaign.

    A checkpoint is written when the chunk stops before both sieves finish.
    The receipt is written atomically only after both sieves finish. Resume
    produces the same canonical hash as a clean run.
    """
    if N < 3:
        raise ValueError("N must be at least 3")
    if threshold != THRESHOLD:
        raise ValueError(f"threshold is locked to {THRESHOLD}")

    out_path = Path(out)
    if out_path.resolve() == CERTIFIED_RECEIPT.resolve():
        raise ValueError(
            "refusing to overwrite reports/abc_census.json (A-2026-0032)"
        )
    progress = (
        Path(progress_path)
        if progress_path is not None
        else out_path.with_name(out_path.stem + ".progress.log")
    )
    checkpoint = (
        Path(checkpoint_path)
        if checkpoint_path is not None
        else out_path.with_name(out_path.stem + ".ckpt.json")
    )

    if prereg_path is None:
        raise ValueError("a locked preregistration file is required")
    prereg_hash = _sha256lf(prereg_path)
    if prereg_hash != PREREG_SHA256LF:
        raise ValueError(
            "preregistration hash mismatch: "
            f"expected {PREREG_SHA256LF}, got {prereg_hash}"
        )
    module_hash = _sha256lf(Path(__file__))

    state_a = SieveState()
    state_b = SieveState()
    if resume and checkpoint.exists():
        data = json.loads(checkpoint.read_text(encoding="utf-8"))
        if data.get("schema") != CHECKPOINT_SCHEMA:
            raise ValueError("checkpoint schema mismatch")
        if int(data.get("N", -1)) != N:
            raise ValueError("checkpoint N mismatch")
        if data.get("prereg_sha256lf") != prereg_hash:
            raise ValueError("checkpoint prereg hash mismatch")
        state_a = _state_from_json(data["sieves"]["a"])
        state_b = _state_from_json(data["sieves"]["b"])
    elif checkpoint.exists():
        checkpoint.unlink()

    limit = _rad_limit(N)

    with _ProgressLog(progress, echo=echo) as log:
        log.log(
            f"campaign start N={N} rad_limit={limit} out={out_path} "
            f"resume={resume} state_a={state_a.next_index}/{state_a.count} "
            f"state_b={state_b.next_index}/{state_b.count}"
        )

        deadline = None
        if max_seconds is not None and max_seconds > 0:
            deadline = time.perf_counter() + max_seconds

        if not state_a.done:
            started = time.perf_counter()
            rad_a = _rad_sieve(N)
            low_a, is_low_a, by_rad_a, rad_sorted_a = _build_low_rad_a(
                rad_a, N, limit
            )
            prep_a = time.perf_counter() - started
            state_a.runtime += prep_a
            log.log(
                f"sieve_a prep low={len(low_a)} seconds={prep_a:.3f}"
            )
            started = time.perf_counter()
            done_a = _scan_sieve_a(
                low_a,
                rad_a,
                is_low_a,
                by_rad_a,
                rad_sorted_a,
                state_a,
                deadline=deadline,
                max_c=max_c_per_chunk,
                checkpoint_every=checkpoint_every,
                threshold=threshold,
            )
            scan_a = time.perf_counter() - started
            state_a.runtime += scan_a
            log.log(
                f"sieve_a scan done={done_a} next={state_a.next_index} "
                f"count={state_a.count} seconds={scan_a:.3f}"
            )
            del rad_a, low_a, is_low_a, by_rad_a, rad_sorted_a
            if not done_a:
                _save_checkpoint(checkpoint, N, prereg_hash, state_a, state_b)
                log.log(f"checkpoint saved path={checkpoint}")
                return CampaignOutcome(
                    "CHUNKED", None, out_path, checkpoint, progress
                )

        if not state_b.done:
            started = time.perf_counter()
            rad_b = _rad_sieve_segmented(N, segment_size)
            low_b, is_low_b, by_rad_b, rad_sorted_b = _build_low_rad_b(
                rad_b, N, limit
            )
            prep_b = time.perf_counter() - started
            state_b.runtime += prep_b
            log.log(
                f"sieve_b prep low={len(low_b)} seconds={prep_b:.3f}"
            )
            started = time.perf_counter()
            done_b = _scan_sieve_b(
                low_b,
                rad_b,
                is_low_b,
                by_rad_b,
                rad_sorted_b,
                state_b,
                deadline=deadline,
                max_c=max_c_per_chunk,
                checkpoint_every=checkpoint_every,
                threshold=threshold,
            )
            scan_b = time.perf_counter() - started
            state_b.runtime += scan_b
            log.log(
                f"sieve_b scan done={done_b} next={state_b.next_index} "
                f"count={state_b.count} seconds={scan_b:.3f}"
            )
            del rad_b, low_b, is_low_b, by_rad_b, rad_sorted_b
            if not done_b:
                _save_checkpoint(checkpoint, N, prereg_hash, state_a, state_b)
                log.log(f"checkpoint saved path={checkpoint}")
                return CampaignOutcome(
                    "CHUNKED", None, out_path, checkpoint, progress
                )

        verified = verify_pairs_with_factorint(state_b.pairs, threshold)
        receipt = _build_receipt(
            N,
            state_a,
            state_b,
            prereg_hash,
            module_hash,
            verified,
            threshold,
        )
        _atomic_write_json(out_path, receipt)
        if checkpoint.exists():
            checkpoint.unlink()
        log.log(
            f"receipt written path={out_path} verdict={receipt['verdict']} "
            f"count={receipt['count']} canonical={receipt['canonical_sha256']}"
        )
        return CampaignOutcome("DONE", receipt, out_path, checkpoint, progress)


def _abc_census_main(
    N: int,
    *,
    segment_size: int = DEFAULT_SEGMENT_SIZE,
    threshold: float = THRESHOLD,
) -> ABCResult:
    """Run both sieves in one process and return the agreement result."""
    limit = _rad_limit(N)

    state_a = SieveState()
    started = time.perf_counter()
    rad_a = _rad_sieve(N)
    low_a, is_low_a, by_rad_a, rad_sorted_a = _build_low_rad_a(rad_a, N, limit)
    state_a.runtime += time.perf_counter() - started
    started = time.perf_counter()
    if not _scan_sieve_a(
        low_a,
        rad_a,
        is_low_a,
        by_rad_a,
        rad_sorted_a,
        state_a,
        checkpoint_every=0,
        threshold=threshold,
    ):
        raise RuntimeError("sieve A stopped unexpectedly")
    state_a.runtime += time.perf_counter() - started
    del rad_a, low_a, is_low_a, by_rad_a, rad_sorted_a

    state_b = SieveState()
    started = time.perf_counter()
    rad_b = _rad_sieve_segmented(N, segment_size)
    low_b, is_low_b, by_rad_b, rad_sorted_b = _build_low_rad_b(rad_b, N, limit)
    state_b.runtime += time.perf_counter() - started
    started = time.perf_counter()
    if not _scan_sieve_b(
        low_b,
        rad_b,
        is_low_b,
        by_rad_b,
        rad_sorted_b,
        state_b,
        checkpoint_every=0,
        threshold=threshold,
    ):
        raise RuntimeError("sieve B stopped unexpectedly")
    state_b.runtime += time.perf_counter() - started
    del rad_b, low_b, is_low_b, by_rad_b, rad_sorted_b

    if HAS_SYMPY and not verify_pairs_with_factorint(state_b.pairs, threshold):
        raise RuntimeError("factorint verification failed")

    pairs = state_a.pairs
    return ABCResult(
        N=N,
        count=state_a.count,
        pairs=pairs,
        max_gap=state_a.max_gap,
        first_triple=pairs[0] if pairs else None,
        last_triple=pairs[-1] if pairs else None,
        runtime_a=state_a.runtime,
        runtime_b=state_b.runtime,
        count_a=state_a.count,
        count_b=state_b.count,
        max_gap_a=state_a.max_gap,
        max_gap_b=state_b.max_gap,
        pairs_a=state_a.pairs,
        pairs_b=state_b.pairs,
    )


def abc_census_certified(
    N: int = 1_000_000, segment_size: int = DEFAULT_SEGMENT_SIZE
) -> ABCResult:
    """Run the certified abc census up to N."""
    return _abc_census_main(N, segment_size=segment_size)


def verify_agreement(result: ABCResult) -> bool:
    """Check if both sieves agree exactly."""
    return (
        result.count_a == result.count_b
        and result.max_gap_a == result.max_gap_b
        and result.pairs_a == result.pairs_b
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Certified abc census v3")
    parser.add_argument("--N", type=int, default=VALIDATE_N)
    parser.add_argument("--out", default=None)
    parser.add_argument("--progress", default=None)
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--max-seconds", type=float, default=900.0)
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--segment-size", type=int, default=DEFAULT_SEGMENT_SIZE)
    parser.add_argument("--prereg", default=str(DEFAULT_PREREG))
    parser.add_argument("--checkpoint-every", type=int, default=512)
    parser.add_argument("--max-c-per-chunk", type=int, default=None)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    out = (
        Path(args.out)
        if args.out
        else REPO_ROOT / "reports" / f"abc_census_v3_{args.N}.json"
    )
    outcome = run_campaign(
        args.N,
        out,
        progress_path=args.progress,
        checkpoint_path=args.checkpoint,
        max_seconds=args.max_seconds,
        resume=not args.no_resume,
        segment_size=args.segment_size,
        checkpoint_every=args.checkpoint_every,
        max_c_per_chunk=args.max_c_per_chunk,
        prereg_path=args.prereg,
        echo=not args.quiet,
    )
    if outcome.status == "DONE":
        receipt = outcome.receipt or {}
        print(
            f"status=DONE verdict={receipt.get('verdict')} "
            f"count={receipt.get('count')} max_gap={receipt.get('max_gap')} "
            f"canonical={receipt.get('canonical_sha256')}"
        )
        return 0 if receipt.get("verdict") == "ALL PASS" else 1
    print(f"status=CHUNKED checkpoint={outcome.checkpoint_path}")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())


