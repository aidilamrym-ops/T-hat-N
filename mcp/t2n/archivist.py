# -*- coding: utf-8 -*-
"""t2n_archivist -- read-only corpus search & summariser (F1).

Everything here is strictly read-only and confined to T2N_REPO_ROOT.
Machine-extracted numbers only; interpretation stays with the model/owner.
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import guard          # sha256lf convenience only (no writes here)
from core.skeleton import serve_generic

REPO_ROOT = Path(os.environ.get("T2N_REPO_ROOT")
                 or Path(__file__).resolve().parents[2]).resolve()

# never walk into generated/vendored noise
EXCLUDE_DIR_NAMES = {".git", ".pytest_cache", "__pycache__", "node_modules",
                     ".venv", "venv", "build", "dist", ".next", "out",
                     "learnharness", ".idea", ".vscode", ".github"}

HEAD_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_ID_RE = re.compile(r"A-(\d{4})-(\d{4})")


def _repo_path(raw: str) -> Path:
    p = Path(raw)
    p = p if p.is_absolute() else (REPO_ROOT / p)
    p = p.resolve(strict=False)
    if p != REPO_ROOT and REPO_ROOT not in p.parents:
        raise PermissionError(f"path outside T2N_REPO_ROOT: {raw}")
    return p


def _rel(p: Path) -> str:
    return str(p.relative_to(REPO_ROOT)).replace(os.sep, "/")


def _walk_repo(include, roots=None, cap=3000):
    """Yield repo files (Paths) matching filename include-globs, bounded."""
    pats = [str(p).lower() for p in (include or ["*.md"])]
    allowed_low = []
    for r in (roots or []):
        allowed_low.append(str(_repo_path(str(r))).lower())
    count = 0
    for dirpath, dirnames, filenames in os.walk(str(REPO_ROOT)):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIR_NAMES]
        for fn in filenames:
            low = fn.lower()
            if not any(low == pat or fnmatch.fnmatch(low, pat) for pat in pats):
                continue
            full = os.path.join(dirpath, fn)
            if allowed_low:
                lowf = full.lower()
                if not any(lowf.startswith(r + os.sep) or lowf == r
                           for r in allowed_low):
                    continue
            yield Path(full)
            count += 1
            if count >= cap:
                return


# ---------------------------------------------------------------- handlers --
def corpus_search(params: dict) -> dict:
    query = str(params.get("query") or "").strip()
    if not query:
        raise ValueError("query required")
    regex = bool(params.get("regex"))
    case = bool(params.get("case_sensitive"))
    max_hits = max(1, min(int(params.get("max_hits") or 40), 200))
    include = params.get("include") or ["*.md", "*.py", "*.json", "*.jsonl"]
    roots = params.get("roots") or []
    if regex:
        rx = re.compile(query, 0 if case else re.IGNORECASE)
        def test(s: str) -> bool: return rx.search(s) is not None
    else:
        needle = query if case else query.lower()
        def test(s: str) -> bool: return (needle in s) if case else (needle in s.lower())
    files_scanned, hits, truncated = 0, [], False
    for path in _walk_repo(include, roots or None):
        files_scanned += 1
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                for i, line in enumerate(fh, 1):
                    if test(line):
                        hits.append({"path": _rel(path), "line": i,
                                     "text": line.rstrip()[:200]})
                        if len(hits) >= max_hits:
                            truncated = True
                            break
        except OSError:
            continue
        if truncated:
            break
    return {"query": query, "hits": hits, "files_scanned": files_scanned,
            "truncated": truncated}


def doc_outline(params: dict) -> dict:
    raw = str(params.get("path") or "")
    p = _repo_path(raw)
    if not p.is_file():
        raise FileNotFoundError(raw)
    out = {"path": _rel(p), "sha256lf": guard.sha256lf(p),
           "bytes": p.stat().st_size, "headings": []}
    with open(p, "r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            m = HEAD_RE.match(line)
            if m:
                out["headings"].append({"line": i, "level": len(m.group(1)),
                                        "text": m.group(2)[:120]})
    return out


def registry_lookup(params: dict) -> dict:
    rid = str(params.get("id") or "").strip()
    if not re.fullmatch(r"A-\d{4}-\d{4}", rid):
        raise ValueError("id must match A-YYYY-NNNN, e.g. A-2026-0043")
    groups: dict[str, list] = {}
    for path in _walk_repo(["*.md"]):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if rid in line:
                groups.setdefault(_rel(path), []).append(
                    {"line": i, "text": line[:200]})
    fence = groups.get("reports/FENCE_REGISTRY.md") or []
    return {"id": rid, "present": bool(groups), "files": groups,
            "fence_registry_hits": fence[:4]}


def summarize_receipt(params: dict) -> dict:
    raw = str(params.get("path") or "")
    p = _repo_path(raw)
    data = json.loads(p.read_text(encoding="utf-8"))
    fields = {k: data.get(k) for k in
              ("summary", "all_pass", "registry", "schema", "claim")
              if k in data}
    gates = _find_gate_map(data)
    rows = _find_rows(data)
    table = []
    name_keys = ("id", "name", "gate", "row", "label")
    for r in rows or []:
        actual = r.get("actual") if isinstance(r.get("actual"), dict) else {}
        table.append({
            "row": next((str(r[k])[:24] for k in name_keys if k in r), "?"),
            "parameter": str(r.get("parameter", ""))[:48],
            "passed": r.get("passed") if isinstance(r.get("passed"), bool)
                      else None,
            "actual_summary": str(actual.get("summary", ""))[:20],
            "expected": str(r.get("expected", ""))[:120],
        })
    return {"receipt": _rel(p), "fields": fields,
            "gates": gates, "row_table": table,
            "note": "machine-extracted fields only; verdicts not reinterpreted"}


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


def _find_gate_map(obj: object) -> list:
    if isinstance(obj, dict):
        cp = obj.get("checks_passed")
        if isinstance(cp, dict) and cp:
            return [{"gate": str(g)[:20],
                     "status": ("PASS" if gv is True else
                                "FAIL" if gv is False else str(gv)[:12])}
                    for g, gv in cp.items()]
        for v in obj.values():
            found = _find_gate_map(v)
            if found:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _find_gate_map(v)
            if found:
                return found
    return []


def timeline(params: dict) -> dict:
    days = min(max(int(params.get("days") or 7), 1), 90)
    cutoff = time.time() - days * 86400
    items = []
    for path in _walk_repo(["*.md", "*.py", "*.json", "*.jsonl"]):
        try:
            mt = os.path.getmtime(path)
            if mt >= cutoff:
                items.append({"path": _rel(path),
                              "mtime": time.strftime("%Y-%m-%d %H:%M:%S",
                                                     time.localtime(mt)),
                              "size": os.path.getsize(path)})
        except OSError:
            continue
    items.sort(key=lambda x: x["mtime"], reverse=True)
    return {"window_days": days, "count": len(items), "files": items[:80]}


def read_slice(params: dict) -> dict:
    raw = str(params.get("path") or "")
    p = _repo_path(raw)
    if not p.is_file():
        raise FileNotFoundError(raw)
    start = max(int(params.get("offset") or 1), 1)
    count = min(max(int(params.get("count") or 100), 1), 400)
    with open(p, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    sel = lines[start - 1: start - 1 + count]
    return {"path": _rel(p), "offset": start, "returned": len(sel),
            "total_lines": len(lines),
            "lines": [{"n": start + i, "text": t.rstrip()[:300]}
                      for i, t in enumerate(sel)]}


TOOLS = [
    {"name": "corpus_search",
     "description": ("Report-style regex or literal search across the repo "
                     "corpus (reports, msaf sources, receipts JSON, JSONL). "
                     "Bounded and read-only."),
     "inputSchema": {"type": "object",
                     "properties": {"query": {"type": "string"},
                                    "regex": {"type": "boolean",
                                              "default": False},
                                    "case_sensitive": {"type": "boolean",
                                                       "default": False},
                                    "max_hits": {"type": "integer",
                                                 "default": 40},
                                    "include": {"type": "array",
                                                "items": {"type": "string"}},
                                    "roots": {"type": "array",
                                              "items": {"type": "string"}}},
                     "required": ["query"], "additionalProperties": False}},
    {"name": "doc_outline",
     "description": "Heading outline + sha256lf + size of one repo document.",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}},
                     "required": ["path"], "additionalProperties": False}},
    {"name": "registry_lookup",
     "description": "Find every markdown mention of a registry id such as "
                    "A-2026-0043, grouped by file.",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}},
                     "required": ["id"], "additionalProperties": False}},
    {"name": "summarize_receipt",
     "description": "Verdict table machine-extracted from a receipts JSON "
                    "(per-row pass/fail + top-level fields).",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}},
                     "required": ["path"], "additionalProperties": False}},
    {"name": "timeline",
     "description": "Work-file timeline (mtime-sorted) over the last N days.",
     "inputSchema": {"type": "object",
                     "properties": {"days": {"type": "integer", "default": 7}},
                     "additionalProperties": False}},
    {"name": "read_slice",
     "description": "Read a numbered slice of any repo file (offset/count).",
     "inputSchema": {"type": "object",
                     "properties": {"path": {"type": "string"},
                                    "offset": {"type": "integer", "default": 1},
                                    "count": {"type": "integer", "default": 100}},
                     "required": ["path"], "additionalProperties": False}},
]

HANDLERS = {
    "corpus_search": corpus_search,
    "doc_outline": doc_outline,
    "registry_lookup": registry_lookup,
    "summarize_receipt": summarize_receipt,
    "timeline": timeline,
    "read_slice": read_slice,
}

DESCRIPTION = ("T-hat-N archivist (F1): bounded read-only corpus search, "
               "document outlines, registry lookups, machine-extracted "
               "receipt verdict tables, work timelines, file slices.")

if __name__ == "__main__":
    serve_generic("t2n_archivist", DESCRIPTION, TOOLS, HANDLERS)
