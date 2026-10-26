# -*- coding: utf-8 -*-
"""Guard for the consolidated T2N MCP servers (prereg 2026-10-27).

Every check drives a real stdio subprocess, the same path OpenCode uses:
newline-delimited JSON-RPC in, one JSON line out. Server modules are never
imported here, so an import-time ``NameError`` or a tool without a handler
fails the guard instead of hiding behind a successful import.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MCP = ROOT / "mcp"

PROTOCOLS = {"2025-06-18", "2024-11-05"}

# Contract K2/K3: 6 + 6 + 3 + 8 + 5 role tools + ping + self_check.
CORE_TOOLS = {
    # repokeeper
    "repo_status", "hash_artifact", "receipt_verify", "pytest_run",
    "registry_state", "handoff_queue",
    # archivist
    "corpus_search", "doc_outline", "registry_lookup", "summarize_receipt",
    "timeline", "read_slice",
    # science
    "iv_eval", "frac_compare", "ast_float_scan",
    # scribe
    "ledger_append", "ledger_tail", "audit_state", "area_claim",
    "area_release", "areas_list", "resume_brief", "handoff_draft",
    # watchtower
    "guarded_run", "watch", "reap", "reap_all_stale", "run_history",
    # builtins from serve_generic
    "ping", "self_check",
}

# Contract K4: 3 SVG renderers + HTML dashboard + mp_query + 2 builtins.
VIZ_TOOLS = {
    "render_receipt_svg", "render_dependency_svg", "render_orbit_svg",
    "render_html_dashboard", "mp_query", "ping", "self_check",
}


def _session(script: Path, write_root: Path, calls=()):
    """Run one server to EOF and return ({id: message}, stderr)."""
    assert script.is_file(), f"missing server script: {script}"
    env = os.environ.copy()
    env.update({
        "T2N_REPO_ROOT": str(ROOT),
        "T2N_WRITE_ROOTS": str(write_root),
        "T2N_LOG_DIR": str(write_root / "logs"),
        "T2N_LEDGER_PATH": str(write_root / "audit.jsonl"),
        "PYTHONIOENCODING": "utf-8",
    })
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05",
                    "clientInfo": {"name": "mcp-guard", "version": "0"}}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    ]
    for request_id, (name, arguments) in enumerate(calls, start=3):
        requests.append({
            "jsonrpc": "2.0", "id": request_id, "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        })
    payload = "".join(json.dumps(item) + "\n" for item in requests)
    proc = subprocess.run(
        [sys.executable, "-u", str(script)],
        cwd=str(ROOT), env=env, input=payload, capture_output=True,
        text=True, encoding="utf-8", timeout=180,
    )
    responses = {}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        message = json.loads(line)
        if "id" in message:
            responses[message["id"]] = message
    return responses, proc.stderr


def _result(responses, request_id, stderr=""):
    message = responses.get(request_id)
    assert message is not None, (
        f"no response for id={request_id}; stderr tail: {stderr[-2000:]}")
    assert "result" in message, (
        f"JSON-RPC error id={request_id}: {message}; "
        f"stderr tail: {stderr[-2000:]}")
    return message["result"]


def _tool_names(responses, stderr):
    result = _result(responses, 2, stderr)
    return [tool["name"] for tool in result["tools"]]


def _tool_payload(result, stderr=""):
    assert result.get("isError") is False, (
        f"tool reported an error: {result}; stderr tail: {stderr[-2000:]}")
    return json.loads(result["content"][0]["text"])


def test_core_lists_exactly_the_contracted_tools(tmp_path):
    responses, stderr = _session(MCP / "t2n_core.py", tmp_path)
    init = _result(responses, 1, stderr)
    assert init["serverInfo"]["name"] == "t2n_core"
    assert init["protocolVersion"] in PROTOCOLS

    names = _tool_names(responses, stderr)
    assert len(names) == 30, (len(names), sorted(names), stderr[-2000:])
    assert len(names) == len(set(names)), "duplicate tool names"
    assert set(names) == CORE_TOOLS


def test_core_ping_returns_ok(tmp_path):
    responses, stderr = _session(
        MCP / "t2n_core.py", tmp_path, calls=[("ping", {})])
    payload = _tool_payload(_result(responses, 3, stderr), stderr)
    assert payload["status"] == "ok"
    assert payload["server"] == "t2n_core"


def test_core_unknown_tool_is_a_jsonrpc_error(tmp_path):
    responses, stderr = _session(
        MCP / "t2n_core.py", tmp_path, calls=[("no_such_tool", {})])
    message = responses.get(3)
    assert message is not None, stderr[-2000:]
    assert message["error"]["code"] == -32602


def test_viz_lists_exactly_the_contracted_tools(tmp_path):
    responses, stderr = _session(MCP / "t2n_viz.py", tmp_path)
    init = _result(responses, 1, stderr)
    assert init["serverInfo"]["name"] == "t2n_viz"

    names = _tool_names(responses, stderr)
    assert len(names) == 7, (len(names), sorted(names), stderr[-2000:])
    assert len(names) == len(set(names)), "duplicate tool names"
    assert set(names) == VIZ_TOOLS


def test_viz_dashboard_writes_html_inside_allowlist(tmp_path):
    responses, stderr = _session(
        MCP / "t2n_viz.py", tmp_path,
        calls=[("render_html_dashboard", {
            "title": "Guard Dashboard",
            "sections": [{"header": "Alpha", "content": "beta"}],
        })],
    )
    payload = _tool_payload(_result(responses, 3, stderr), stderr)
    path = Path(payload["path"])
    assert path.is_file(), payload
    assert path.parent.name == "illumina"
    assert tmp_path.resolve() in path.resolve().parents
    text = path.read_text(encoding="utf-8")
    assert "<h1>Guard Dashboard</h1>" in text
    assert "<h2>Alpha</h2>" in text


def test_combined_shim_serves_the_viz_contract(tmp_path):
    responses, stderr = _session(MCP / "t2n_combined.py", tmp_path)
    init = _result(responses, 1, stderr)
    assert init["serverInfo"]["name"] == "t2n_viz"
    assert set(_tool_names(responses, stderr)) == VIZ_TOOLS


@pytest.mark.skipif(
    sys.platform != "win32",
    reason="workspace config holds absolute Windows paths for this machine")
def test_opencode_config_declares_only_two_t2n_servers():
    text = (ROOT / "opencode.jsonc").read_text(encoding="utf-8")
    stripped = "\n".join(
        line for line in text.splitlines()
        if not line.lstrip().startswith("//"))
    config = json.loads(stripped)
    servers = config["mcp"]["servers"]
    assert set(servers) == {"t2n_core", "t2n_viz"}
    for name, entry in servers.items():
        assert entry["type"] == "local", name
        command = entry["command"]
        assert command[0].endswith("python.exe") or command[0].endswith("python"), name
        # The config uses absolute Windows paths; resolve by basename so the
        # guard also runs on the Linux CI runner.
        script_name = Path(command[-1]).name
        script = MCP / script_name
        assert script.is_file(), f"{name} points at a missing script: {script}"
        assert entry["environment"]["T2N_REPO_ROOT"] == str(ROOT), name
