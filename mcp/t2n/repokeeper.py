# -*- coding: utf-8 -*-
"""t2n_repokeeper -- repo integrity & guarded operations (F1).

Read-only inspections of T2N_REPO_ROOT plus writes that land only inside
T2N_WRITE_ROOTS (the mcp/out outbox). No git-mutating subcommand is on the
allowlist; commits/pushes stay owner-gated by repo protocol.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import guard
from core.skeleton import serve_generic

REPO_ROOT = Path(os.environ.get("T2N_REPO_ROOT")
                 or Path(__file__).resolve().parents[2]).resolve()

_ID_RE = re.compile(r"A-(\d{4})-(\d{4})")

# read-only git subcommands only (argv-based: no shell, no injection surface)
GIT_ALLOW = re.compile(r"^git(?:\.exe)?\s+(status|branch|log|diff|rev-list|show)\b")
PYTEST_ALLOW = re.compile(
    r"^.+python(?:\.exe)?\s+-u\s+-m\s+pytest\b.*-p\s+no:cacheprovider\b")


def _repo_path(raw: str) -> Path:
    """Resolve and confine any path to the repo root (read side)."""
    p = Path(raw)
    p = p if p.is_absolute() else (REPO_ROOT / p)
    p = p.resolve(strict=False)
    if p != REPO_ROOT and REPO_ROOT not in p.parents:
        raise PermissionError(f"path outside T2N_REPO_ROOT: {raw}")
    return p


def _safe(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_\-]", "_", str(text))[:80]


# --------------------------------------------------------- audit ledger --
_AUDIT: "guard.Ledger | None" = None


def _audit() -> guard.Ledger:
    """Lazy singleton audit ledger; env override for alternate homes."""
    global _AUDIT
    if _AUDIT is None:
        _AUDIT = guard.Ledger(os.environ.get("T2N_LEDGER_PATH") or
                              (Path(guard.write_roots()[0]) / "ledger" /
                               "t2n_ledger_v1.jsonl"))
    return _AUDIT


def _event(event: str, payload: dict) -> dict:
    """Audit trail for state-affecting calls; ledger failure never breaks."""
    try:
        return _audit().append(event, payload)
    except Exception as exc:
        return {"audit_error": str(exc)[:120]}


def _git(args: list[str], timeout: float = 30.0) -> subprocess.CompletedProcess:
    cmd = ["git", *args]
    guard.assert_allowed_run(cmd, pattern=GIT_ALLOW.pattern)
    return subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=timeout)


# ---------------------------------------------------------------- handlers --
def repo_status(params: dict) -> dict:
    res: dict = {"repo_root": str(REPO_ROOT), "branch": None,
                 "aheadbehind": None, "last_commit": None,
                 "porcelain": [], "untracked_entries": []}
    br = _git(["branch", "--show-current"])
    if br.returncode == 0:
        res["branch"] = br.stdout.strip() or None
    st = _git(["status", "--porcelain"])
    lines = [l for l in st.stdout.splitlines() if l.strip()]
    res["porcelain"] = lines
    res["untracked_entries"] = sorted({
        l[3:].strip().rstrip("/").replace("\\", "/").split("/", 1)[0]
        for l in lines if l.startswith("??")})
    ab = _git(["rev-list", "--left-right", "--count", "HEAD...@{upstream}"])
    if ab.returncode == 0:
        parts = ab.stdout.split()
        if len(parts) == 2:
            res["aheadbehind"] = {"ahead": int(parts[0]),
                                  "behind": int(parts[1])}
    lc = _git(["log", "-1", "--format=%H %cs %s"])
    if lc.returncode == 0:
        res["last_commit"] = lc.stdout.strip()
    return res


def hash_artifact(params: dict) -> dict:
    paths = params.get("paths")
    if not isinstance(paths, list) or not paths:
        raise ValueError("paths: non-empty list of file paths required")
    if len(paths) > 64:
        raise ValueError("paths: at most 64 files per call")

    out = []
    for raw in paths:
        p = _repo_path(str(raw))
        if not p.is_file():
            raise FileNotFoundError(str(raw))
        out.append({"path": str(p.relative_to(REPO_ROOT)),
                    "sha256lf": guard.sha256lf(p),
                    "bytes": p.stat().st_size})
    return {"artifacts": out}


def registry_state(params: dict) -> dict:
    reg = REPO_ROOT / "reports" / "FENCE_REGISTRY.md"
    if not reg.is_file():
        raise FileNotFoundError("reports/FENCE_REGISTRY.md")
    text = reg.read_text(encoding="utf-8", errors="replace")
    ids: list[str] = []
    for m in _ID_RE.finditer(text):
        idv = f"A-{m.group(1)}-{m.group(2)}"
        if idv not in ids:
            ids.append(idv)

    def idkey(s: str) -> tuple[int, int]:
        y, n = s.split("-")[1], s.split("-")[2]
        return (int(y), int(n))

    latest = max(ids, key=idkey) if ids else None
    nxt = None
    if latest:
        year, num = latest.split("-")[1], int(latest.split("-")[2])
        nxt = f"A-{year}-{num + 1:04d}"
    return {"registry_file": "reports/FENCE_REGISTRY.md",
            "sha256lf": guard.sha256lf(reg),
            "ids_in_file_order": ids[-8:],
            "total_distinct": len(ids),
            "latest": latest,
            "next_slot_hint": nxt,
            "latest_rule": "numeric maximum across ids (file order is not "
                           "chronological)",
            "note": "hint only -- an id exists only after its preregistration "
                    "is locked before code"}


def receipt_verify(params: dict) -> dict:
    raw = params.get("path")
    if not raw:
        raise ValueError("path required, e.g. receipts/figure_eight_r4_2026-10-23.json")
    p = _repo_path(str(raw))
    data = json.loads(p.read_text(encoding="utf-8"))
    rel = str(p.relative_to(REPO_ROOT)).replace(os.sep, "/")
    problems: list[str] = []
    warnings: list[str] = []
    all_pass = data.get("all_pass")
    summary = data.get("summary")
    if isinstance(all_pass, bool) and isinstance(summary, str):
        sup = summary.upper()
        coherent = (("FAIL" not in sup) if all_pass
                    else ("FAIL" in sup or "INCOMPLETE" in sup))
        if not coherent:
            problems.append(
                f"summary '{summary}' disagrees with all_pass={all_pass}")
    reg = data.get("registry")
    regid = None
    if isinstance(reg, str):
        regid = reg.strip()
    elif isinstance(reg, dict):
        regid = reg.get("id") or reg.get("registry")
    if regid is not None:
        if not isinstance(regid, str) or not re.fullmatch(r"A-\d{4}-\d{4}", regid):
            problems.append(f"registry id format wrong: {regid!r}")
        else:
            fence = REPO_ROOT / "reports" / "FENCE_REGISTRY.md"
            fence_text = (fence.read_text(encoding="utf-8", errors="replace")
                          if fence.is_file() else "")
            if not re.search(re.escape(regid), fence_text):
                problems.append(
                    f"registry id {regid} NOT found in reports/FENCE_REGISTRY.md")
            else:
                lines = [ln for ln in fence_text.splitlines() if regid in ln]
                reg_words = set(re.findall(r"[a-z0-9]+", " ".join(lines).lower()))
                r_words = _artifact_words(data, rel)
                overlap = r_words & reg_words
                if not lines:
                    warnings.append(f"registry id {regid} absent from line scan")
                elif len(r_words) < 2:
                    warnings.append("too few recognizable artifact words; "
                                    "corroboration skipped")
                elif len(overlap) < 2:
                    warnings.append(
                        "REGISTRY CORROBORATION MISS: registry lines for "
                        f"{regid} share fewer than 2 artifact words with "
                        "this receipt (possible mis-attribution)")
    elif regid is None and all_pass is True:
        warnings.append("all_pass=true with registry null/absent "
                        "(repo protocol: ALL PASS must mint a registry entry)")

    # recompute every recorded artifact hash (sha256lf convention).
    # repo receipts pair "<stem>" with "<stem>_sha256lf" (e.g. module
    # <-> module_sha256lf) or carry {"path": ..., "sha256lf": ...} objects.
    paired: list[tuple[str, str, str]] = []
    unpaired: list[str] = []
    _walk_hash_pairs(data, paired, unpaired)
    seen: set[tuple[str, str]] = set()
    checked, mismatched = 0, []
    for pathv, hexv, why in paired:
        key = (str(pathv).lower(), hexv.lower())
        if key in seen:
            continue
        seen.add(key)
        try:
            q = _repo_path(str(pathv))
            if q.is_file():
                checked += 1
                if guard.sha256lf(q).lower() != hexv.lower():
                    mismatched.append(f"{pathv} ({why})")
            else:
                problems.append(f"artifact missing: {pathv} ({why})")
        except (PermissionError, OSError) as exc:
            problems.append(f"artifact unreadable: {pathv}: {exc}")
    if mismatched:
        problems.append("hash mismatch (sha256lf): "
                        + ", ".join(sorted(set(mismatched))))
    if unpaired:
        warnings.append("recorded hashes without an adjacent path (not "
                        "recomputed): " + ", ".join(sorted(set(unpaired))))
    rows = _find_rows(data)
    row_stats = None
    if rows:
        inconcl = sum(1 for r in rows if isinstance(r, dict)
                      and isinstance(r.get("actual"), dict)
                      and str(r["actual"].get("summary", "")).upper()
                      == "INCONCLUSIVE")
        row_stats = {"rows": len(rows),
                     "true": sum(1 for r in rows
                                 if isinstance(r, dict) and r.get("passed") is True),
                     "false": sum(1 for r in rows
                                  if isinstance(r, dict) and r.get("passed") is False),
                     "actual_inconclusive": inconcl}
    result = {"receipt": rel, "claimed_registry": regid,
              "all_pass": all_pass,
              "summary": summary if isinstance(summary, str) else str(summary),
              "problems": problems, "warnings": warnings,
              "hash_checks": {"recomputed": checked},
              "row_stats": row_stats,
              "verdict": ("CONSISTENCY/TAMPER PROBLEM" if problems
                          else "consistent under applied checks")}
    audit = _event("receipt_verdict",
                   {"receipt": rel, "verdict": result["verdict"],
                    "problems": len(problems), "warnings": len(warnings)})
    if audit and "audit_error" not in audit:
        result["audit_seq"] = audit.get("seq")
    return result


_PATHISH = re.compile(r"\.(py|md|json|jsonl|txt|svg|html)$", re.I)
_HEX64 = re.compile(r"[0-9a-f]{64}", re.I)
_STEM = len("_sha256lf")


def _pathlike(v: object) -> bool:
    return (isinstance(v, str) and _PATHISH.search(v) is not None
            and ("/" in v or "\\" in v))


def _artifact_words(data: dict, receipt_rel: str) -> set[str]:
    """Word set over receipt artifact names for registry cross-checking.

    'figure_eight_r4' yields {figure, eight, r4}; the FENCE heading
    'Figure-eight ... r4' normalises to the same word family.
    """
    words: set[str] = set()

    def add(text: str) -> None:
        name = str(text).replace("\\", "/").split("/")[-1].lower()
        stem = re.sub(r"_\d{4}-\d{2}-\d{2}$", "", name.rsplit(".", 1)[0])
        for w in re.split(r"[^a-z0-9]+", stem):
            if len(w) >= 2:
                words.add(w)

    add(receipt_rel)

    def walk(v: object) -> None:
        if isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
        elif isinstance(v, str) and _pathlike(v):
            add(v)

    walk(data)
    return words


def _walk_hash_pairs(obj: object, paired: list, unpaired: list) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and _HEX64.fullmatch(v.strip()):
                if k.endswith("_sha256lf"):
                    stem = k[:-_STEM]
                    if isinstance(obj.get(stem), str) and _pathlike(obj[stem]):
                        paired.append((obj[stem], v, f"{stem}~{k}"))
                    else:
                        unpaired.append(k)
                elif k in ("sha256lf", "sha256", "hash", "sha"):
                    sib = next((obj[c] for c in ("path", "file", "artifact")
                                if _pathlike(obj.get(c))), None)
                    if sib is not None:
                        paired.append((sib, v, f"{k}@path-object"))
                    else:
                        unpaired.append(k)
        for v in obj.values():
            _walk_hash_pairs(v, paired, unpaired)
    elif isinstance(obj, list):
        for v in obj:
            _walk_hash_pairs(v, paired, unpaired)


def _find_rows(obj: object):
    if isinstance(obj, dict):
        for k in ("rows", "k_rows", "gates"):
            b = obj.get(k)
            if isinstance(b, list) and b and all(isinstance(x, dict) for x in b):
                return b
        for v in obj.values():
            found = _find_rows(v)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _find_rows(v)
            if found is not None:
                return found
    return None


def pytest_run(params: dict) -> dict:
    targets = params.get("targets")
    if not isinstance(targets, list) or not targets:
        raise ValueError("targets: list of pytest paths required, "
                         "e.g. ['msaf/tests/test_prime_integration.py']")
    if len(targets) > 16:
        raise ValueError("targets: at most 16 paths per run")
    timeout_ms = int(params.get("timeout_ms") or 600000)
    extra = [p.strip().replace("\\", "/").strip("/")
             for p in os.environ.get("T2N_PYTEST_EXTRA_ROOTS", "").split(";")
             if p.strip()]
    allowed = ["msaf/tests"] + extra
    revp = []
    for t in targets:
        norm = str(t).replace("\\", "/")
        if not any(norm == pre or norm.startswith(pre + "/") for pre in allowed):
            raise PermissionError(
                f"pytest_run restricted to {allowed}; refused: {t}")
        p = _repo_path(str(t))
        if not p.exists():
            raise FileNotFoundError(str(t))
        revp.append(str(t) if not Path(str(t)).is_absolute() else str(p))
    roots = guard.write_roots()
    log_path = guard.make_dirs_writable(
        Path(roots[0]) / "runs" / ("pytest_%s.log" % time.strftime("%Y%m%d_%H%M%S")))
    cmd = [sys.executable, "-u", "-m", "pytest", "-q",
           "-p", "no:cacheprovider", *revp]
    guard.assert_allowed_run(cmd, pattern=PYTEST_ALLOW.pattern)
    _event("pytest_run_started", {"targets": revp})
    proc = subprocess.Popen(cmd, cwd=str(REPO_ROOT), stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True,
                            encoding="utf-8", errors="replace")
    timed_out = False
    try:
        out, _ = proc.communicate(timeout=max(1.0, timeout_ms / 1000.0))
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.kill()
        out, _ = proc.communicate()
    log_path.write_text(out or "", encoding="utf-8", errors="replace")
    tail = "\n".join((out or "").splitlines()[-40:])
    _event("pytest_run_done", {"targets": revp, "exit": proc.returncode,
                               "timed_out": timed_out, "log": log_path.name})
    return {"targets": revp, "exit": proc.returncode,
            "timed_out": timed_out, "log": str(log_path), "tail": tail}


def handoff_queue(params: dict) -> dict:
    section = str(params.get("section") or "untitled")
    body = str(params.get("body") or "")
    if not body.strip():
        raise ValueError("body: non-empty markdown required")
    out_root = Path(guard.write_roots()[0])
    stamp = time.strftime("%Y%m%d_%H%M%S")
    p = guard.make_dirs_writable(
        out_root / "handoff" / f"handoff_{_safe(section)}_{stamp}.md")
    p.write_text(
        f"# HANDOFF OUTBOX : {section}\n\n"
        f"- queued at  : {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"- status     : DRAFT (outbox) -- NOT yet applied to reports/HANDOFF.md\n"
        f"- protocol   : owner reviews; applying stays an owner-gated manual step\n\n"
        f"## Draft body\n\n{body}\n", encoding="utf-8")
    _event("handoff_queued", {"section": section, "path": str(p)})
    return {"queued": str(p), "bytes": p.stat().st_size,
            "sha256lf": guard.sha256lf(p),
            "note": "outbox only; reports/ is sealed for MCP writes by design"}


TOOLS = [
    {"name": "repo_status",
     "description": ("Git state of T2N_REPO_ROOT: branch, ahead/behind vs "
                     "upstream, porcelain entries, untracked top-level "
                     "entries, last commit. Read-only."),
     "inputSchema": {"type": "object", "properties": {},
                     "additionalProperties": False}},
    {"name": "hash_artifact",
     "description": "sha256lf (LF-normalised sha256, registry convention) "
                    "for repo files, bounded to T2N_REPO_ROOT.",
     "inputSchema": {"type": "object",
                     "properties": {"paths": {"type": "array",
                                              "items": {"type": "string"},
                                              "minItems": 1}},
                     "required": ["paths"], "additionalProperties": False}},
    {"name": "receipt_verify",
     "description": ("Anti-forgery consistency check of a receipts JSON: "
                     "summary-vs-all_pass coherence, registry id format and "
                     "presence in reports/FENCE_REGISTRY.md, recorded "
                     "artifact hashes recomputed via sha256lf."),
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}},
                     "required": ["path"], "additionalProperties": False}},
    {"name": "pytest_run",
     "description": ("Run pytest targets with fixed flags "
                     "(-q -p no:cacheprovider), cwd=repo root, output archived "
                     "under <write-root>/runs/*.log; returns exit + tail."),
     "inputSchema": {"type": "object",
                     "properties": {"targets": {"type": "array",
                                                "items": {"type": "string"},
                                                "minItems": 1},
                                    "timeout_ms": {"type": "integer",
                                                   "default": 600000}},
                     "required": ["targets"], "additionalProperties": False}},
    {"name": "registry_state",
     "description": ("Parse reports/FENCE_REGISTRY.md: ordered distinct "
                     "A-YYYY-NNNN ids, latest id, next-slot hint, file hash."),
     "inputSchema": {"type": "object", "properties": {},
                     "additionalProperties": False}},
    {"name": "handoff_queue",
     "description": ("Queue a HANDOFF section draft into outbox "
                     "<write-root>/handoff/*.md (reports/ stays sealed; "
                     "applying is owner-gated)."),
     "inputSchema": {"type": "object",
                     "properties": {"section": {"type": "string"},
                                    "body": {"type": "string"}},
                     "required": ["section", "body"],
                     "additionalProperties": False}},
]

HANDLERS = {
    "repo_status": repo_status,
    "hash_artifact": hash_artifact,
    "receipt_verify": receipt_verify,
    "pytest_run": pytest_run,
    "registry_state": registry_state,
    "handoff_queue": handoff_queue,
}

DESCRIPTION = ("T-hat-N repo keeper (F1): git status, artifact hashing, "
               "receipt anti-forgery checks, guarded pytest runs, registry "
               "state, handoff outbox queue. Writes allowed only to the "
               "mcp/out allowlist root.")

if __name__ == "__main__":
    serve_generic("t2n_repokeeper", DESCRIPTION, TOOLS, HANDLERS)
