# -*- coding: utf-8 -*-
"""T2N MCP suite -- integrity guard.

Conventions this project hardened across 2026-10 sessions:
- writes land ONLY under T2N_WRITE_ROOTS (allowlist);
- logs/ledgers are APPEND-ONLY and hash-chained (tamper is detectable);
- sha256lf = sha256 over LF-normalised text (the repo's registry convention).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable

try:
    import msvcrt            # Windows byte-range locks (primary on win32)
except ImportError:          # pragma: no cover
    msvcrt = None
try:
    import fcntl             # POSIX advisory locks (fallback)
except ImportError:          # pragma: no cover
    fcntl = None

_THREAD_LOCKS: dict[str, threading.Lock] = {}
_THREAD_LOCKS_MUX = threading.Lock()


def _thread_lock(path_key: str) -> threading.Lock:
    """One in-process lock per ledger path (threads of the same process)."""
    with _THREAD_LOCKS_MUX:
        lock = _THREAD_LOCKS.get(path_key)
        if lock is None:
            lock = threading.Lock()
            _THREAD_LOCKS[path_key] = lock
        return lock


# ---------------------------------------------------------------- roots ----
def write_roots() -> list[Path]:
    raw = os.environ.get("T2N_WRITE_ROOTS", "")
    roots: list[Path] = []
    for chunk in raw.split(";"):
        chunk = chunk.strip()
        if chunk:
            roots.append(Path(chunk).resolve())
    if roots:
        return roots
    # fail closed: no allowlist configured -> default to the temp dir only
    fallback = Path(os.environ.get("T2N_LOG_DIR",
                                   Path.home() / "AppData" / "Local" / "Temp" / "opencode"))
    fallback.resolve()
    return [fallback]


def assert_writable(path: str | os.PathLike) -> Path:
    target = Path(path).resolve(strict=False)
    for root in write_roots():
        if root == target or root in target.parents:
            return target
    raise PermissionError(
        f"write refused: '{target}' is outside T2N_WRITE_ROOTS {write_roots()}")


def make_dirs_writable(path: str | os.PathLike) -> Path:
    target = assert_writable(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


# ---------------------------------------------------------------- hashes ---
def sha256lf(path: str | os.PathLike, *, raw: bool = False) -> str:
    data = Path(path).read_bytes()
    if not raw:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(payload: object) -> bytes:
    text = json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2)
    return text.encode("utf-8") + b"\n"


# ------------------------------------------------------------ hash chain ---
def _safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_\-]", "_", text)[:64]


class Ledger:
    """Append-only, hash-chained JSONL (tamper-evident by construction).

    Concurrency discipline:
    - same-process threads serialise on a per-path threading.Lock;
    - cross-process appends serialise on an OS byte-range lock file
      (<path>.lock, one locked byte);
    - the prev-sha/seq are re-read FRESH inside the lock, so concurrent
      writers can never inherit a stale chain head;
    - readers verify the whole chain, so even a torn interleaved write is
      DETECTED, never silently accepted.
    """

    def __init__(self, path: str | os.PathLike, *, create_ok: bool = True) -> None:
        self.path = make_dirs_writable(path) if create_ok else Path(path)
        self.lock_path = Path(str(self.path) + ".lock")
        self._tlock = _thread_lock(str(self.path))
        last = self._last()
        self._prev_sha = last["self_sha"] if last else "GENESIS"

    def _last(self) -> dict | None:
        rows = _read_rows(self.path)
        return rows[-1] if rows else None

    @contextmanager
    def _os_lock(self):
        fh = open(self.lock_path, "a+b")
        locked = False
        try:
            if msvcrt is not None:
                msvcrt.locking(fh.fileno(), msvcrt.LK_LOCK, 1)
                locked = True
            elif fcntl is not None:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
                locked = True
            yield
        finally:
            if locked and msvcrt is not None:
                try:
                    fh.seek(0)
                    msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass  # released automatically on close anyway
            fh.close()

    def ensure_chain(self) -> None:
        """Fail closed: raise unless every row hashes and links correctly."""
        if self.path.exists() and not _chain_ok(self.path):
            raise RuntimeError(f"ledger chain broken: {self.path}")

    def append(self, event: str, payload: dict | None = None) -> dict:
        with self._tlock:
            with self._os_lock():
                upper = self._last()                      # fresh read under lock
                record = {
                    "seq": (upper["seq"] + 1) if upper else 1,
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%S") + time.strftime("%z"),
                    "event": event,
                    "payload": payload or {},
                    "prev_sha": upper["self_sha"] if upper else "GENESIS",
                }
                body = json.dumps(record, ensure_ascii=True, sort_keys=True,
                                  separators=(",", ":"))
                record["self_sha"] = hashlib.sha256(
                    body.encode("utf-8")).hexdigest()
                with open(self.path, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(record, ensure_ascii=True,
                                        sort_keys=True) + "\n")
                self._prev_sha = record["self_sha"]
        return record

    def tail(self, n: int = 20) -> list[dict]:
        if not self.path.exists():
            return []
        rows = _read_rows(self.path)
        return rows[-max(0, n):]


def _read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _chain_ok(path: Path) -> bool:
    prev = "GENESIS"
    for row in _read_rows(path):
        body = {k: v for k, v in row.items() if k != "self_sha"}
        body = {k: body[k] for k in ("seq", "ts", "event", "payload", "prev_sha")}
        digest = hashlib.sha256(json.dumps(
            body, ensure_ascii=True, sort_keys=True, separators=(",", ":")
        ).encode()).hexdigest()
        if digest != row.get("self_sha") or row.get("prev_sha") != prev:
            return False
        prev = row["self_sha"]
    return True


def verify_ledger(path: str | os.PathLike) -> dict:
    p = Path(path)
    if not p.exists():
        return {"exists": False, "chain_ok": True, "rows": 0}
    rows = _read_rows(p)
    return {"exists": True, "chain_ok": _chain_ok(p), "rows": len(rows)}


# ------------------------------------------------- safe command allowlist ---
DEFAULT_CMD_ALLOW = re.compile(
    r"^(python(?:\.exe)?|py)\s+-u\s+-m\s+pytest\b|"
    r"^(python(?:\.exe)?|py)\s+-u\s+[\"']?.+\.py[\"']?\s*$",
    re.IGNORECASE,
)


def assert_allowed_run(cmd: Iterable[str],
                       *, pattern: str | None = None) -> list[str]:
    argv = [str(part) for part in cmd]
    joined = " ".join(argv)
    regex = pattern if pattern is not None else (
        os.environ.get("T2N_RUN_ALLOW_RE") or DEFAULT_CMD_ALLOW.pattern)
    if not re.match(regex, joined, re.IGNORECASE):
        raise PermissionError(
            f"guarded_run refused (not on allowlist): {joined[:160]}")
    return argv
