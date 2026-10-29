# -*- coding: utf-8 -*-
"""t2n_scribe -- cross-session memory & work coordination (F2).

Tools land on three duties:
- shared audit-ledger ACCESS (append/tail/audit state) so any session can
  leave tamper-evident notes and read the truth back;
- EXCLUSIVE work-area claims with TTLs held in a two-tier-locked JSON
  store, so parallel sessions cannot silently collide;
- compiled resume briefs and handoff drafts (outbox only; reports/ sealed).
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import guard
from core.skeleton import serve_generic

REPO_ROOT = Path(os.environ.get("T2N_REPO_ROOT")
                 or Path(__file__).resolve().parents[2]).resolve()

_EVENT_RE = re.compile(r"^[a-z0-9_]{1,40}$")
_AREA_RE = re.compile(r"^[A-Za-z0-9_\-]{1,64}(?:/[A-Za-z0-9_\-]{1,64}){0,3}$")
_SESSION_RE = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")
_MAX_PAYLOAD_CHARS = 6000
_MAX_NOTE_CHARS = 400
_TTL_MIN, _TTL_MAX, _TTL_DEF = 60, 172800, 3600   # 1 min .. 48 h, default 1 h


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


def _areas() -> "guard.LockedJson":
    out_root = Path(guard.write_roots()[0])
    return guard.LockedJson(out_root / "handoff" / "areas.json")


def _iso(epoch: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


def _safe(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_\- ]", "_", str(text))[:80].strip()


# ---------------------------------------------------------------- ledger --
def ledger_append(params: dict) -> dict:
    event = params.get("event")
    if not isinstance(event, str) or not _EVENT_RE.fullmatch(event):
        raise ValueError("event: 1-40 chars, lowercase [a-z0-9_] required")
    payload = params.get("payload") if params.get("payload") is not None else {}
    if not isinstance(payload, dict):
        raise ValueError("payload: JSON object required")
    if len(json.dumps(payload, ensure_ascii=True)) > _MAX_PAYLOAD_CHARS:
        raise ValueError(
            f"payload too large: serialised payload must stay under "
            f"{_MAX_PAYLOAD_CHARS} chars")
    session = params.get("session") or "unknown"
    if not isinstance(session, str) or not _SESSION_RE.fullmatch(session):
        raise ValueError("session: [A-Za-z0-9_-], max 64 chars")
    record = _audit().append(event, {**payload, "session": session})
    return {"recorded": True, "seq": record["seq"], "ts": record["ts"],
            "prev_sha": record["prev_sha"], "self_sha": record["self_sha"]}


def ledger_tail(params: dict) -> dict:
    n = int(params.get("n") or 20)
    if not 1 <= n <= 200:
        raise ValueError("n: integer in [1, 200]")
    event_filter = params.get("event_filter")
    if event_filter is not None and not isinstance(event_filter, str):
        raise ValueError("event_filter: string prefix or None")
    rows = _audit().tail(n * 4 if event_filter else n)
    if event_filter:
        rows = [r for r in rows if str(r.get("event", "")).startswith(event_filter)]
        rows = rows[-n:]
    out = []
    for r in rows:
        blob = json.dumps(r.get("payload", {}), ensure_ascii=True, sort_keys=True)
        out.append({"seq": r.get("seq"), "ts": r.get("ts"),
                    "event": r.get("event"),
                    "payload": r.get("payload") if len(blob) <= 240
                               else f"<truncated, {len(blob)} chars>",
                    "self_sha": r.get("self_sha")})
    return {"rows": out, "returned": len(out)}


def audit_state(params: dict) -> dict:
    path = _audit().path
    check = guard.verify_ledger(path)
    rows = guard._read_rows(path) if check["exists"] else []
    head = rows[-1] if rows else None
    return {"ledger": str(path), "exists": check["exists"],
            "chain_ok": check["chain_ok"], "rows": check["rows"],
            "head": {"seq": head.get("seq"), "ts": head.get("ts"),
                     "event": head.get("event"), "self_sha": head.get("self_sha")}
                    if head else None,
            "note": "chain_ok False means TAMPER OR CORRUPTION: stop writing, "
                    "preserve the file, investigate before further use"}


# ---------------------------------------------------------------- claims --
def area_claim(params: dict) -> dict:
    area = params.get("area")
    if not isinstance(area, str) or not _AREA_RE.fullmatch(area):
        raise ValueError("area: 1-64 chars [A-Za-z0-9_-] (up to 4 '/parts')")
    session = params.get("session")
    if not isinstance(session, str) or not _SESSION_RE.fullmatch(session):
        raise ValueError("session: [A-Za-z0-9_-], max 64 chars")
    note = str(params.get("note") or "")[:_MAX_NOTE_CHARS]
    ttl_s = int(params.get("ttl_s") or _TTL_DEF)
    if not _TTL_MIN <= ttl_s <= _TTL_MAX:
        raise ValueError(f"ttl_s: integer in [{_TTL_MIN}, {_TTL_MAX}]")

    now = time.time()
    defer_error: dict | None = None
    with _areas().transaction({"version": 1, "claims": {}}) as data:
        claims = data.setdefault("claims", {})
        for key in [k for k, c in claims.items() if c["expires_at"] <= now]:
            del claims[key]                       # expired holdings free space
        held = claims.get(area)
        if held is not None and held["session"] != session:
            defer_error = {"area": area, "held_by": held["session"],
                           "holder_note": held.get("note", ""),
                           "claimed_at": held["claimed_at"],
                           "seconds_left": max(
                               0, int(round(held["expires_at"] - now))),
                           "advice": "wait for expiry, or contact the holder; "
                                     "forced takeover is an area_release(force=true)"}
        else:
            first = held is None
            held = held or {}
            held.update({"session": session, "note": note, "ttl_s": ttl_s,
                         "claimed_at": held.get("claimed_at") or _iso(now),
                         "last_renewed": _iso(now),
                         "renewed": 0 if first else int(held.get("renewed", 0)) + 1,
                         "expires_at": now + ttl_s})
            claims[area] = held
    if defer_error is not None:
        raise PermissionError(json.dumps(defer_error, sort_keys=True))
    outcome = _areas().read().get("claims", {}).get(area, {})
    _event("area_renewed" if outcome.get("renewed") else "area_claimed",
           {"area": area, "session": session, "ttl_s": ttl_s})
    return {"area": area, "status": "ACTIVE", "claim": outcome}


def area_release(params: dict) -> dict:
    area = params.get("area")
    if not isinstance(area, str) or not _AREA_RE.fullmatch(area):
        raise ValueError("area: same format as area_claim")
    session = params.get("session")
    if not isinstance(session, str) or not _SESSION_RE.fullmatch(session):
        raise ValueError("session: [A-Za-z0-9_-], max 64 chars")
    force = bool(params.get("force", False))
    now = time.time()
    defer_error: dict | None = None
    with _areas().transaction({"version": 1, "claims": {}}) as data:
        claims = data.setdefault("claims", {})
        held = claims.get(area)
        if held is None:
            defer_error = {"error": "no active claim", "area": area}
        elif held["session"] != session and not force:
            defer_error = {"error": "not the holder", "area": area,
                           "held_by": held["session"],
                           "advice": "holder calls area_release, or you must "
                                     "pass force=true (audited loudly)"}
        else:
            claims.pop(area)
    if defer_error is not None:
        raise PermissionError(json.dumps(defer_error, sort_keys=True))
    _event("area_released", {"area": area, "session": session, "force": force})
    return {"area": area, "status": "RELEASED", "forced": force}


def areas_list(params: dict) -> dict:
    claims = _areas().read().get("claims", {})
    now = time.time()
    active = []
    for area, held in sorted(claims.items()):
        if held.get("expires_at", 0) <= now:
            continue                             # stale rows purged on next write
        active.append({"area": area, "session": held["session"],
                       "note": held.get("note", ""),
                       "claimed_at": held["claimed_at"],
                       "last_renewed": held.get("last_renewed"),
                       "ttl_s": held.get("ttl_s"),
                       "expires_in_s": max(0, int(round(held["expires_at"] - now)))})
    return {"active": active, "count": len(active)}


# ---------------------------------------------------------------- briefs --
def _brief_rows(n: int) -> list[dict]:
    out = []
    for r in _audit().tail(n):
        out.append({"seq": r.get("seq"), "ts": r.get("ts"), "event": r.get("event")})
    return out


def resume_brief(params: dict) -> dict:
    n = int(params.get("n") or 12)
    if not 1 <= n <= 50:
        raise ValueError("n: integer in [1, 50]")
    rows = _brief_rows(n)
    state = audit_state({})
    return {"generated_at": _iso(time.time()),
            "ledger_head_seq": state["head"]["seq"] if state["head"] else None,
            "chain_ok": state["chain_ok"], "ledger_rows": state["rows"],
            "recent_events": rows,
            "active_area_claims": areas_list({})["active"],
            "pointers": {
                "registry_claims": "t2n_repokeeper.registry_state",
                "receipt_trust": "t2n_repokeeper.receipt_verify",
                "repo_state": "t2n_repokeeper.repo_status",
                "corpus": "t2n_archivist.corpus_search"}}


def handoff_draft(params: dict) -> dict:
    title = str(params.get("title") or "untitled")
    body = str(params.get("body") or "")
    session = params.get("session") or "unknown"
    if not isinstance(session, str) or not _SESSION_RE.fullmatch(session):
        raise ValueError("session: [A-Za-z0-9_-], max 64 chars")
    n = int(params.get("n") or 12)
    if not 1 <= n <= 50:
        raise ValueError("n: integer in [1, 50]")
    brief = resume_brief({"n": n})

    lines = [f"# HANDOFF DRAFT : {title}",
             "",
             f"- compiled at : {_iso(time.time())} by session `{session}`",
             f"- ledger head : seq {brief['ledger_head_seq']} "
             f"(chain_ok={brief['chain_ok']}, rows={brief['ledger_rows']})",
             f"- status      : DRAFT (outbox) -- applying to reports/ is "
             f"still an owner-gated manual step",
             "",
             "## Recent ledger events\n"]
    for row in brief["recent_events"]:
        lines.append(f"- seq {row['seq']} {row['ts']} `{row['event']}`")
    lines += ["", "## Active area claims\n"]
    claims = brief["active_area_claims"]
    if claims:
        for c in claims:
            lines.append(f"- `{c['area']}` held by `{c['session']}` "
                         f"(expires in {c['expires_in_s']}s)")
    else:
        lines.append("- (none active)")
    lines += ["", "## Session notes\n"]
    if body.strip():
        lines.append(body.rstrip() + "\n")
    else:
        lines.append("(empty)\n")
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out_root = Path(guard.write_roots()[0])
    path = guard.make_dirs_writable(
        out_root / "handoff" / f"draft_{_safe(title).replace(' ', '_')}_"
                               f"{stamp}.md")
    path.write_text("\n".join(lines), encoding="utf-8", errors="replace")
    _event("handoff_draft",
           {"title": title, "session": session, "path": str(path)})
    return {"draft": str(path), "bytes": path.stat().st_size,
            "sha256lf": guard.sha256lf(path),
            "note": "outbox only; reports/ stays sealed for MCP writes"}


TOOLS = [
    {"name": "ledger_append",
     "description": "Append a validated event to the shared hash-chained "
                    "audit ledger (mcp/out/ledger/t2n_ledger_v1.jsonl). "
                    "Returns seq + chain shas.",
     "inputSchema": {"type": "object",
                     "properties": {"event": {"type": "string"},
                                    "payload": {"type": "object"},
                                    "session": {"type": "string"}},
                     "required": ["event"], "additionalProperties": False}},
    {"name": "ledger_tail",
     "description": "Read the last n ledger rows (payloads >~240 chars "
                    "summarised), optionally filtered by event-name prefix.",
     "inputSchema": {"type": "object",
                     "properties": {"n": {"type": "integer"},
                                    "event_filter": {"type": "string"}},
                     "additionalProperties": False}},
    {"name": "audit_state",
     "description": "Verify the whole ledger hash chain (fail-closed view) "
                    "and report row count plus the chain head.",
     "inputSchema": {"type": "object", "properties": {},
                     "additionalProperties": False}},
    {"name": "area_claim",
     "description": ("Exclusive work-area claim (TTL, default 3600s; "
                     "min 60, max 172800). Re-claim by the same session "
                     "renews; a foreign holder refuses the call with its "
                     "identity and time left."),
     "inputSchema": {"type": "object",
                     "properties": {"area": {"type": "string"},
                                    "session": {"type": "string"},
                                    "ttl_s": {"type": "integer"},
                                    "note": {"type": "string"}},
                     "required": ["area", "session"],
                     "additionalProperties": False}},
    {"name": "area_release",
     "description": ("Release an area claim by the holder; another session "
                     "must pass force=true, which is recorded as a forced "
                     "release in the ledger."),
     "inputSchema": {"type": "object",
                     "properties": {"area": {"type": "string"},
                                    "session": {"type": "string"},
                                    "force": {"type": "boolean"}},
                     "required": ["area", "session"],
                     "additionalProperties": False}},
    {"name": "areas_list",
     "description": "List non-expired work-area claims with time left.",
     "inputSchema": {"type": "object", "properties": {},
                     "additionalProperties": False}},
    {"name": "resume_brief",
     "description": ("Compile a resume brief: ledger head/chain state, the "
                     "last n events, active area claims, and pointers to "
                     "registry/receipt tools."),
     "inputSchema": {"type": "object", "properties": {"n": {"type": "integer"}},
                     "additionalProperties": False}},
    {"name": "handoff_draft",
     "description": ("Compile a handoff draft (outbox mcp/out/handoff/*.md) "
                     "from live ledger + claims state plus optional session "
                     "notes; reports/ stays sealed."),
     "inputSchema": {"type": "object",
                     "properties": {"title": {"type": "string"},
                                    "body": {"type": "string"},
                                    "session": {"type": "string"},
                                    "n": {"type": "integer"}},
                     "required": ["title"], "additionalProperties": False}},
]

HANDLERS = {
    "ledger_append": ledger_append,
    "ledger_tail": ledger_tail,
    "audit_state": audit_state,
    "area_claim": area_claim,
    "area_release": area_release,
    "areas_list": areas_list,
    "resume_brief": resume_brief,
    "handoff_draft": handoff_draft,
}

DESCRIPTION = (
    "T-hat-N scribe (F2): append/read/audit the shared hash-chained ledger, "
    "exclusive TTL work-area claims for parallel sessions, resume briefs and "
    "handoff drafts (outbox only). Writes land only under mcp/out/.")

if __name__ == "__main__":
    serve_generic("t2n_scribe", DESCRIPTION, TOOLS, HANDLERS)


