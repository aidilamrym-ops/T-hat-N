# -*- coding: utf-8 -*-
"""t2n_watchtower -- guarded long runs, witness logs, safe reaping (F2).

Design pillars (born from the r5 four-hour guard window and the pid-reuse
risk):
- `guarded_run` spawns an allowlisted command whose streaming stdout/stderr
  land STRAIGHT into <write-root>/runs/<run_id>.log; the child owns that
  file handle, so the log keeps growing even if the server process dies.
- every run identity is `pid + process-creation-signature`; a later `watch`
  or `reap` refuses to act when the OS recycled the pid (signature
  mismatch), so an innocent fresh process can never be killed by a stale
  run_id. Killing is done ONLY with a verified identity.
- `reap_all_stale` converges the registry with reality and records honest
  verdicts (exited / exited_unknown / pid_reused_stale / reap).
- every state transition emits an event to the shared hash-chained ledger.
"""
from __future__ import annotations

import json
import os
import random
import re
import shlex
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import guard
from core.skeleton import serve_generic

REPO_ROOT = Path(os.environ.get("T2N_REPO_ROOT")
                 or Path(__file__).resolve().parents[2]).resolve()

# --------------------------------------------------------------- allowlist --
_PY_RUN = r"^.+python(?:\.exe)?\s+(?:-u\s+)?-m\s+"
WATCH_PATTERNS = [
    _PY_RUN + r"pytest\b.*-p\s+no:cacheprovider\b",
    _PY_RUN + r"py_compile\s+msaf[/\\]",
    _PY_RUN + r"timeit\b",
]
MAX_RUNNING = 8
DEF_TIMEOUT, MIN_TIMEOUT, MAX_TIMEOUT = 1800, 1, 21600   # 30 min; 1 s; 6 h
_MAX_PARTS, _MAX_PART_CHARS, _MAX_JOINED = 48, 400, 2000


def _allow_regex() -> str:
    custom = os.environ.get("T2N_WATCHTOWER_ALLOW_RE")
    if custom:
        return custom
    return "(?:" + "|".join(WATCH_PATTERNS) + ")"


# ------------------------------------------------------------ audit ledger --
_AUDIT: "guard.Ledger | None" = None


def _audit() -> guard.Ledger:
    global _AUDIT
    if _AUDIT is None:
        _AUDIT = guard.Ledger(os.environ.get("T2N_LEDGER_PATH") or
                              (Path(guard.write_roots()[0]) / "ledger" /
                               "t2n_ledger_v1.jsonl"))
    return _AUDIT


def _event(event: str, payload: dict) -> dict:
    try:
        return _audit().append(event, payload)
    except Exception as exc:
        return {"audit_error": str(exc)[:120]}


def _registry() -> "guard.LockedJson":
    out_root = Path(guard.write_roots()[0])
    return guard.LockedJson(out_root / "runs" / "runs_registry.json")


def _iso(epoch: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


# ------------------------------------------------------- process identity ---
def _probe_pid(pid: int) -> dict:
    """Identity + liveness probe of a foreign pid.

    Returns {"alive": bool|None, "sig": str|None, "exit_code": int|None}.
    `sig` is a stable process-creation signature; a NEW process reusing the
    pid yields a DIFFERENT sig -- this tripwire is what makes reaping safe.
    """
    pid = int(pid)
    if os.name == "nt":
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.OpenProcess.restype = ctypes.c_void_p
        k32.OpenProcess.argtypes = (ctypes.c_uint32, ctypes.c_int,
                                    ctypes.c_uint32)
        k32.GetProcessTimes.restype = ctypes.c_int
        k32.GetProcessTimes.argtypes = (ctypes.c_void_p,
                                        ctypes.POINTER(ctypes.c_ulonglong),
                                        ctypes.POINTER(ctypes.c_ulonglong),
                                        ctypes.POINTER(ctypes.c_ulonglong),
                                        ctypes.POINTER(ctypes.c_ulonglong))
        k32.GetExitCodeProcess.restype = ctypes.c_int
        k32.GetExitCodeProcess.argtypes = (ctypes.c_void_p,
                                           ctypes.POINTER(ctypes.c_ulong))
        k32.CloseHandle.argtypes = (ctypes.c_void_p,)
        handle = k32.OpenProcess(0x1000, False, pid)  # QUERY_LIMITED_INFORMATION
        if not handle:
            return {"alive": False, "sig": None, "exit_code": None}
        try:
            creat, exit_ft, kern, user = (ctypes.c_ulonglong() for _ in range(4))
            if not k32.GetProcessTimes(handle, ctypes.byref(creat),
                                       ctypes.byref(exit_ft),
                                       ctypes.byref(kern),
                                       ctypes.byref(user)):
                return {"alive": None, "sig": None, "exit_code": None}
            sig = "creat%016x" % creat.value
            code = ctypes.c_ulong()
            if not k32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return {"alive": None, "sig": sig, "exit_code": None}
            alive = code.value == 259            # STILL_ACTIVE
            return {"alive": alive, "sig": sig,
                    "exit_code": None if alive else int(code.value)}
        finally:
            k32.CloseHandle(handle)
    # POSIX fallback: /proc identity; the starttime field is used only
    # through equality checks, never as a time value.
    try:
        stat = Path("/proc/%d/stat" % pid).read_text(encoding="utf-8")
    except OSError:
        return {"alive": False, "sig": None, "exit_code": None}
    try:
        fields = stat.split(") ", 1)[1].split()
        return {"alive": True, "sig": "procstart" + fields[19],
                "exit_code": None}
    except (IndexError, ValueError):
        return {"alive": None, "sig": None, "exit_code": None}


def _terminate_pid(pid: int) -> bool:
    """Kill a foreign pid whose identity the CALLER already verified."""
    pid = int(pid)
    if os.name == "nt":
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.OpenProcess.restype = ctypes.c_void_p
        k32.OpenProcess.argtypes = (ctypes.c_uint32, ctypes.c_int,
                                    ctypes.c_uint32)
        k32.TerminateProcess.restype = ctypes.c_int
        k32.TerminateProcess.argtypes = (ctypes.c_void_p, ctypes.c_uint)
        k32.CloseHandle.argtypes = (ctypes.c_void_p,)
        handle = k32.OpenProcess(0x0001, False, pid)   # PROCESS_TERMINATE
        if not handle:
            return False
        try:
            return bool(k32.TerminateProcess(handle, 1))
        finally:
            k32.CloseHandle(handle)
    import signal
    try:
        os.kill(pid, signal.SIGKILL)
        return True
    except OSError:
        return False


# ------------------------------------------------------------------ common --
def _norm_cmd(params: dict) -> list[str]:
    raw = params.get("cmd")
    if isinstance(raw, str):
        argv = shlex.split(raw, posix=False)
    elif isinstance(raw, list):
        argv = [str(a) for a in raw]
    else:
        raise ValueError("cmd: list of strings (or one command string)")
    if len(argv) < 2:
        raise ValueError("cmd: at least interpreter + argument required")
    if len(argv) > _MAX_PARTS:
        raise ValueError("cmd: at most %d parts" % _MAX_PARTS)
    if any(not a for a in argv):
        raise ValueError("cmd: empty argument present")
    for a in argv:
        if len(a) > _MAX_PART_CHARS:
            raise ValueError("cmd: single argument too long")
    joined = " ".join(argv)
    if len(joined) > _MAX_JOINED:
        raise ValueError("cmd: total command string too long")
    if any(ord(c) < 32 for c in joined):
        raise ValueError("cmd: control characters refused")
    guard.assert_allowed_run(argv, pattern=_allow_regex())
    return argv


def _cwd_of(params: dict) -> Path:
    raw = params.get("cwd")
    p = Path(raw) if raw else REPO_ROOT
    p = (p if p.is_absolute() else (REPO_ROOT / p)).resolve(strict=False)
    if p != REPO_ROOT and REPO_ROOT not in p.parents:
        raise PermissionError("run cwd refused (outside T2N_REPO_ROOT): %s" % p)
    return p


def _run_id() -> str:
    return "run_%s_%04x" % (time.strftime("%Y%m%d_%H%M%S"),
                            random.getrandbits(16))


def _find(data: dict, run_id: str) -> dict | None:
    for rec in reversed(data.get("runs", [])):
        if rec.get("run_id") == run_id:
            return rec
    return None


def _log_tail(log_path: Path, n: int, width: int = 400) -> list[str]:
    if n <= 0 or not Path(log_path).is_file():
        return []
    try:
        lines = Path(log_path).read_bytes().decode("utf-8", "replace"
                                                   ).splitlines()
        return [l[:width] for l in lines[-n:]]
    except OSError:
        return []


def _converge(rec: dict, probe: dict, now: float) -> str:
    """Finalise a 'running' record to agree with observed reality."""
    rec["finished_at"] = _iso(now)
    rec["finished_epoch"] = now
    if rec.get("duration_s") is None:
        rec["duration_s"] = round(now - rec["started_epoch"], 3)
    if probe["sig"] is not None and probe["sig"] != rec.get("proc_sig"):
        rec["status"] = "pid_reused_stale"
        rec["exit_code"] = None
    elif probe["exit_code"] is None:
        rec["status"] = "exited_unknown"
    else:
        rec["status"] = "exited"
        rec["exit_code"] = probe["exit_code"]
    return rec["status"]


# ---------------------------------------------------------------- handlers --
def guarded_run(params: dict) -> dict:
    argv = _norm_cmd(params)
    cwd = _cwd_of(params)
    timeout_s = int(params.get("timeout_s") or DEF_TIMEOUT)
    if not MIN_TIMEOUT <= timeout_s <= MAX_TIMEOUT:
        raise ValueError(
            "timeout_s: integer in [%d, %d]" % (MIN_TIMEOUT, MAX_TIMEOUT))
    label = str(params.get("label") or "")[:60]
    run_id = _run_id()
    log_path = guard.make_dirs_writable(
        Path(guard.write_roots()[0]) / "runs" / (run_id + ".log"))
    entry = {"run_id": run_id, "label": label, "cmd": argv,
             "cwd": str(cwd), "started_at": _iso(time.time()),
             "started_epoch": time.time(), "pid": None, "proc_sig": None,
             "timeout_s": timeout_s, "status": "running", "exit_code": None,
             "duration_s": None, "log": str(log_path)}
    with _registry().transaction({"version": 1, "runs": []}) as data:
        runs = data.setdefault("runs", [])
        live = sum(1 for r in runs[-MAX_RUNNING * 8:]
                   if r.get("status") == "running")
        if live >= MAX_RUNNING:
            raise PermissionError(
                "guarded_run refused: %d runs already 'running' (cap %d); "
                "watch/close them first" % (live, MAX_RUNNING))
        runs.append(dict(entry))
        if len(runs) > 256:
            del runs[:len(runs) - 256]
    _spawn_and_monitor(argv, cwd, log_path, entry)
    return {"run_id": run_id, "pid": entry["pid"], "proc_sig": entry["proc_sig"],
            "status": "running", "timeout_s": timeout_s,
            "log": entry["log"], "started_at": entry["started_at"],
            "note": "async run now; poll watch(run_id=...); if this server "
                    "restarts later, reap_all_stale converges the record"}


def _spawn_and_monitor(argv: list[str], cwd: Path, log_path: Path,
                       entry: dict) -> None:
    fh = open(log_path, "wb")
    fh.write(("[watchtower] run_id=%s\n" % entry["run_id"]).encode("utf-8"))
    fh.write(("[watchtower] command=%s\n"
              % json.dumps(argv, ensure_ascii=True)).encode("utf-8"))
    fh.write(("[watchtower] cwd=%s started=%s timeout_s=%d\n"
              % (entry["cwd"], entry["started_at"],
                 entry["timeout_s"])).encode("utf-8"))
    fh.write(b"[watchtower] --- child output below (streamed raw) ---\n")
    fh.flush()
    os.fsync(fh.fileno())
    proc = subprocess.Popen(argv, cwd=str(cwd), stdout=fh, stderr=fh)
    probe = _probe_pid(proc.pid)
    entry["pid"], entry["proc_sig"] = proc.pid, probe["sig"]
    with _registry().transaction({"version": 1, "runs": []}) as data:
        rec = _find(data, entry["run_id"])
        if rec is not None:
            rec["pid"], rec["proc_sig"] = proc.pid, probe["sig"]

    def monitor() -> None:
        try:
            code = proc.wait(timeout=entry["timeout_s"])
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                proc.kill()
            except OSError:
                pass                            # reap_all_stale / watch converge
            code = proc.wait()
        now = time.time()
        final_status = entry["status"]
        with _registry().transaction({"version": 1, "runs": []}) as data:
            rec = _find(data, entry["run_id"])
            if rec is not None:
                rec["finished_at"] = _iso(now)
                rec["finished_epoch"] = now
                rec["duration_s"] = round(now - entry["started_epoch"], 3)
                rec["exit_code"] = int(code) if code is not None else None
                if rec.get("status") == "running":
                    rec["status"] = ("timeout_killed" if timed_out
                                     else ("done" if code == 0 else "failed"))
                final_status = rec["status"]
        try:
            fh.write(("\n[watchtower] finished=%s status=%s exit_code=%s "
                      "duration_s=%s\n"
                      % (_iso(now), final_status,
                         int(code) if code is not None else None,
                         round(now - entry["started_epoch"], 3))).encode("utf-8"))
            fh.flush()
            os.fsync(fh.fileno())
        except OSError:
            pass
        finally:
            fh.close()
        _event("guarded_run_done",
               {"run_id": entry["run_id"], "status": final_status,
                "exit_code": int(code) if code is not None else None,
                "timed_out": timed_out,
                "duration_s": round(now - entry["started_epoch"], 3)})

    threading.Thread(target=monitor, name=entry["run_id"],
                     daemon=True).start()


def watch(params: dict) -> dict:
    run_id = params.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id: string required")
    tail = int(params.get("tail") or 40)
    if not 0 <= tail <= 80:
        raise ValueError("tail: integer in [0, 80]")
    data = _registry().read({"version": 1, "runs": []})
    rec = _find(data, run_id)
    if rec is None:
        raise ValueError("unknown run_id: %s" % run_id)
    result = {k: rec.get(k) for k in ("run_id", "label", "cmd", "cwd",
                                      "status", "exit_code", "started_at",
                                      "finished_at", "duration_s", "log")}
    tail_rows = _log_tail(Path(rec["log"]), tail) \
        if rec.get("log") else []
    now = time.time()
    if rec.get("status") != "running":
        result["tail"] = tail_rows
        return result
    elapsed = round(now - rec["started_epoch"], 3)
    result["elapsed_s"] = elapsed
    result["time_left_s"] = max(0, int(round(
        rec["timeout_s"] - elapsed, 3)))
    result["expired"] = elapsed > rec["timeout_s"]
    if rec.get("pid") is None and rec.get("proc_sig") is None:
        # server died between registry write and spawn hand-off
        result["status"] = "identity_unverified"
        result["advice"] = "no pid/proc_sig recorded; observe the log file"
        return result
    probe = _probe_pid(int(rec["pid"]))
    if probe["sig"] is not None and probe["sig"] != rec.get("proc_sig"):
        final = None
        with _registry().transaction({"version": 1, "runs": []}) as data2:
            rc = _find(data2, run_id)
            if rc is not None and rc.get("status") == "running":
                final = _converge(rc, probe, now)
        if final:
            result["status"] = final
            result["converged"] = True
        else:
            result["status"] = rec.get("status")
        result["tail"] = tail_rows
        return result
    if probe["alive"] is False:
        final = None
        with _registry().transaction({"version": 1, "runs": []}) as data2:
            rc = _find(data2, run_id)
            if rc is not None and rc.get("status") == "running":
                final = _converge(rc, probe, now)
        if final:
            result["status"] = final
            result["converged"] = True
    elif probe["alive"] is None:
        result["converge_pending"] = "os probe failed; try again"
    result["tail"] = tail_rows
    return result


def reap(params: dict) -> dict:
    run_id = params.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id: string required")
    reason = str(params.get("reason") or "unspecified")[:120]
    data = _registry().read({"version": 1, "runs": []})
    rec = _find(data, run_id)
    if rec is None:
        raise ValueError("unknown run_id: %s" % run_id)
    if rec.get("status") != "running":
        raise ValueError("run %s is not running (status=%s); nothing to reap"
                         % (run_id, rec.get("status")))
    if rec.get("pid") is None and rec.get("proc_sig") is None:
        raise RuntimeError(
            "reap refused for %s: no pid/proc_sig recorded "
            "(identity_unverified; never kill an unverifiable target)"
            % run_id)
    probe = _probe_pid(int(rec["pid"]))
    now = time.time()
    verdict: dict[str, object]
    if probe["sig"] is not None and probe["sig"] != rec.get("proc_sig"):
        verdict = {"run_id": run_id, "action": "NO_KILL",
                   "verdict": "pid_reused_stale",
                   "detail": "pid %d now belongs to a different process; "
                             "record converged, kill refused by identity check"
                             % int(rec["pid"])}
        status_final = None
        with _registry().transaction({"version": 1, "runs": []}) as data2:
            rc = _find(data2, run_id)
            if rc is not None and rc.get("status") == "running":
                status_final = _converge(rc, probe, now)
        if status_final:
            verdict["converged_to"] = status_final
        _event("guarded_run_reap_refused", {"run_id": run_id,
                                            "verdict": verdict["verdict"]})
        verdict["audited"] = True
        return verdict
    if probe["alive"] is False or (probe["alive"] is None
                                   and probe["exit_code"] is not None):
        converged = None
        with _registry().transaction({"version": 1, "runs": []}) as data2:
            rc = _find(data2, run_id)
            if rc is not None and rc.get("status") == "running":
                converged = _converge(rc, probe, now)
        verdict = {"run_id": run_id, "action": "NO_KILL",
                   "verdict": ("already_exit" if converged else "converge_pending"),
                   "detail": "process no longer alive; record converged "
                             "(exit_code=%s)" % probe["exit_code"]}
        _event("guarded_run_reap_refused", {"run_id": run_id,
                                            "verdict": "already_exit"})
        return verdict
    killed = _terminate_pid(int(rec["pid"]))
    if not killed:
        verdict = {"run_id": run_id, "action": "KILL_FAILED",
                   "verdict": "terminate refused by OS",
                   "detail": "identity matched; OS denied TerminateProcess; "
                             "retry or use reap_all_stale"}
        _event("guarded_run_reap_failed", {"run_id": run_id})
        return verdict
    final = None
    with _registry().transaction({"version": 1, "runs": []}) as data2:
        rc = _find(data2, run_id)
        if rc is not None and rc.get("status") == "running":
            rc["status"] = "reaped"
            rc["finished_at"] = _iso(now)
            rc["finished_epoch"] = now
            rc["duration_s"] = round(now - rc["started_epoch"], 3)
            rc["reap_reason"] = reason
            final = True
    _event("guarded_run_reaped",
           {"run_id": run_id, "pid": rec["pid"], "reason": reason})
    return {"run_id": run_id, "action": "KILLED", "verdict": "reaped",
            "detail": "process terminated by reason '%s'; monitor thread "
                      "will finalise exit code + duration" % reason,
            "registry_updated": bool(final)}


def reap_all_stale(params: dict) -> dict:
    data = _registry().read({"version": 1, "runs": []})
    running_ids = [r.get("run_id") for r in reversed(data.get("runs", []))
                   if r.get("status") == "running"]
    if len(running_ids) > MAX_RUNNING:
        running_ids = running_ids[-MAX_RUNNING:]
    summary = {"scanned": len(running_ids), "reaped": [], "converged": {},
               "left_running": []}
    for run_id in running_ids:
        rec = _find({**data}, run_id)
        if rec is None:
            continue
        now = time.time()
        elapsed = now - rec["started_epoch"]
        expired = elapsed > rec["timeout_s"]
        outcome = reap({"run_id": run_id,
                        "reason": "reap_all_stale: expired=%s" % expired})
        verdict = outcome.get("verdict") or outcome.get("action")
        if verdict == "reaped":
            summary["reaped"].append(run_id)
        elif verdict in ("already_exit", "pid_reused_stale"):
            summary["converged"][run_id] = verdict
        else:
            summary["left_running"].append(run_id)
    _event("reap_all_stale",
           {"scanned": summary["scanned"], "reaped": len(summary["reaped"]),
            "converged": len(summary["converged"]),
            "left_running": len(summary["left_running"])})
    return summary


def probe_alive_still(rec: dict) -> bool:
    """Best-effort liveness for summaries only (never kill here)."""
    if rec.get("pid") is None and rec.get("proc_sig") is None:
        return False
    probe = _probe_pid(int(rec["pid"]))
    if probe["sig"] is not None and probe["sig"] != rec.get("proc_sig"):
        return False
    return bool(probe["alive"])


def run_history(params: dict) -> dict:
    limit = int(params.get("limit") or 20)
    if not 1 <= limit <= 100:
        raise ValueError("limit: integer in [1, 100]")
    status_filter = params.get("status")
    if status_filter is not None and not isinstance(status_filter, str):
        raise ValueError("status: string or None")
    runs = _registry().read({"version": 1, "runs": []}).get("runs", [])
    if status_filter:
        runs = [r for r in runs if r.get("status") == status_filter]
    runs = sorted(runs, key=lambda r: r.get("started_epoch", 0),
                  reverse=True)[:limit]
    out = []
    counts: dict[str, int] = {}
    all_runs = _registry().read({"version": 1, "runs": []}).get("runs", [])
    for r in all_runs:
        counts[r.get("status", "?")] = counts.get(r.get("status", "?"), 0) + 1
    for r in runs:
        row = {k: r.get(k) for k in ("run_id", "label", "status",
                                     "exit_code", "started_at",
                                     "finished_at", "duration_s", "log")}
        row["cmd"] = r.get("cmd_joined") or " ".join(r.get("cmd", []))
        row = _row_trim(row)
        lp = r.get("log")
        if lp and Path(lp).is_file() and r.get("status") not in ("running",
                                                                "spawn_pending"):
            try:
                row["log_sha256lf"] = guard.sha256lf(lp)
                row["log_bytes"] = Path(lp).stat().st_size
            except OSError:
                pass
        out.append(row)
    return {"registry": str(_registry().path), "runs_total": len(all_runs),
            "status_counts": counts, "returned": len(out), "runs": out}


def _row_trim(row: dict) -> dict:
    return {k: v for k, v in row.items() if v is not None}


TOOLS = [
    {"name": "guarded_run",
     "description": ("Spawn an ALLOWLISTED command (python -m pytest / "
                     "py_compile / timeit) asynchronously. Streaming log "
                     "lands in <write-root>/runs/<run_id>.log and survives "
                     "server death. Returns run_id, pid, creation "
                     "signature. Identity-verified: never kill beyond "
                     "watch/reap checks."),
     "inputSchema": {"type": "object",
                     "properties": {"cmd": {},
                                    "cwd": {"type": "string"},
                                    "timeout_s": {"type": "integer"},
                                    "label": {"type": "string"}},
                     "required": ["cmd"], "additionalProperties": False}},
    {"name": "watch",
     "description": ("Watch a run: identity-verified liveness (pid + "
                     "creation signature), elapsed vs its timeout, "
                     "optional log tail; converges the record when the pid "
                     "vanished or was recycled."),
     "inputSchema": {"type": "object",
                     "properties": {"run_id": {"type": "string"},
                                    "tail": {"type": "integer"}},
                     "required": ["run_id"], "additionalProperties": False}},
    {"name": "reap",
     "description": ("Terminate a running run ONLY after identity "
                     "verification; pid reuse refuses the kill and "
                     "converges the record instead (audited)."),
     "inputSchema": {"type": "object",
                     "properties": {"run_id": {"type": "string"},
                                    "reason": {"type": "string"}},
                     "required": ["run_id"], "additionalProperties": False}},
    {"name": "reap_all_stale",
     "description": ("Sweep every 'running' record: reap only those whose "
                     "identity still verifies; converge dead/reused ones; "
                     "summary audited to the ledger."),
     "inputSchema": {"type": "object", "properties": {},
                     "additionalProperties": False}},
    {"name": "run_history",
     "description": ("Recent runs from the registry: run_id, command, "
                     "status, exit code, duration, log path and "
                     "log hash (sha256lf) for finished runs."),
     "inputSchema": {"type": "object",
                     "properties": {"limit": {"type": "integer"},
                                    "status": {"type": "string"}},
                     "additionalProperties": False}},
]

HANDLERS = {
    "guarded_run": guarded_run,
    "watch": watch,
    "reap": reap,
    "reap_all_stale": reap_all_stale,
    "run_history": run_history,
}

DESCRIPTION = (
    "T-hat-N watchtower (F2): allowlisted async runs with always-written "
    "streaming logs, pid+creation-time identity verification, safe reaping "
    "and audited run history. Writes land only under mcp/out/runs/.")

if __name__ == "__main__":
    serve_generic("t2n_watchtower", DESCRIPTION, TOOLS, HANDLERS)


