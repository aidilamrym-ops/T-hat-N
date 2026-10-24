# -*- coding: utf-8 -*-
"""T2N MCP suite -- shared protocol core (stdio, newline-delimited JSON-RPC).

Framework conventions (mirrors the working shp_mcp_bridge pattern):
- stdout is reserved for the protocol; ALL diagnostics go to a log file.
- Each message is exactly one line of JSON (newline-delimited, no Content-Length).
- Tools are declared as dicts: {"name", "description", "inputSchema"}.
- handlers[name](params: dict) -> dict  (a plain JSON-serialisable result).
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path
from typing import Callable

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SUPPORTED_PROTOCOLS = ("2025-06-18", "2024-11-05")
SERVER_VERSION = "0.1.0"


def _log_path(name: str) -> Path:
    # strip a redundant "t2n_" prefix (server names are already t2n_<role>)
    if name.startswith("t2n_"):
        name = name[4:]
    base = os.environ.get(
        "T2N_LOG_DIR",
        str(Path.home() / "AppData" / "Local" / "Temp" / "opencode"),
    )
    log_dir = Path(base)
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return Path(base) / "t2n_mcp_unwritable.log"
    return log_dir / f"t2n_{name}.log"


def _log(name: str, line: str) -> None:
    try:
        path = _log_path(name)
        with open(path, "a", encoding="utf-8", errors="replace") as fh:
            fh.write(line.rstrip("\n") + "\n")
    except OSError:
        pass  # logging must never break the protocol stream


class Server:
    """Minimal MCP stdio server. role-name drives naming/logging only."""

    def __init__(self, name: str, description: str, tools: list[dict],
                 handlers: dict[str, Callable[[dict], dict]]) -> None:
        self.name = name
        self.description = description
        self.tools = tools
        self.handlers = handlers
        self._log = lambda line: _log(self.name, line)
        self.initialized = False

    # -- protocol helpers -------------------------------------------------
    def _send(self, payload: dict) -> None:
        sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
        sys.stdout.flush()

    def _result(self, req_id: int, result: dict) -> None:
        self._send({"jsonrpc": "2.0", "id": req_id, "result": result})

    def _error(self, req_id: int, code: int, message: str) -> None:
        self._send({"jsonrpc": "2.0", "id": req_id,
                    "error": {"code": code, "message": message}})

    def _tool_text(self, value: dict, req_id: int) -> None:
        """Wrap a tool result dict into MCP content (bounded for context)."""
        text = json.dumps(value, ensure_ascii=True, sort_keys=True)
        if len(text) > 100000:
            text = json.dumps({"truncated_chars": len(text),
                               "head": text[:100000]}, ensure_ascii=True)
        self._result(req_id, {
            "content": [{"type": "text", "text": text}],
            "isError": False,
        })

    # -- dispatch ----------------------------------------------------------
    def _dispatch(self, request: dict) -> None:
        method = request.get("method")
        req_id = request.get("id")
        params = request.get("params") or {}

        if method == "initialize":
            requested = params.get("protocolVersion") or "2024-11-05"
            self._result(req_id, {
                "protocolVersion": requested if requested in SUPPORTED_PROTOCOLS
                                  else SUPPORTED_PROTOCOLS[-1],
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": self.name, "version": SERVER_VERSION},
            })
            self._log(f"TERSE INISIALISASI oleh client; ver={requested}")
            return

        if method == "notifications/initialized":
            self.initialized = True
            return

        if method == "ping":
            if req_id is not None:
                self._result(req_id, {})
            return

        if method == "tools/list":
            self._result(req_id, {"tools": self.tools})
            return

        if method == "tools/call":
            tool_name = params.get("name")
            handler = self.handlers.get(tool_name)
            if handler is None:
                if req_id is not None:
                    self._error(req_id, -32602, f"unknown tool: {tool_name}")
                return
            try:
                value = handler(params.get("arguments") or {})
            except Exception as exc:  # one tool failing must not kill the server
                detail = "".join(traceback.format_exception_only(type(exc), exc)).strip()
                self._log(f"TOOLS/CALL GAGAL {tool_name}: {detail}")
                if req_id is not None:
                    self._result(req_id, {
                        "content": [{"type": "text",
                                     "text": json.dumps({"error": detail}, sort_keys=True)}],
                        "isError": True,
                    })
                return
            if req_id is not None:
                self._tool_text(value, req_id)
            return

        if req_id is not None:
            self._error(req_id, -32601, f"method not found: {method}")

    # -- main loop ----------------------------------------------------------
    def serve(self) -> None:
        self._log(f"server start pid={os.getpid()} role={self.name}")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
            except json.JSONDecodeError as exc:
                self._log(f"SALAH FRAME: {exc}")
                continue
            try:
                self._dispatch(request)
            except Exception as exc:  # never crash mid-protocol
                self._log("DISPATCH CRASH: %s" % traceback.format_exc())
                req_id = request.get("id")
                if req_id is not None and isinstance(request.get("method"), str):
                    self._error(req_id, -32603, f"internal error: {exc}")
        self._log(f"server exit pid={os.getpid()}")
