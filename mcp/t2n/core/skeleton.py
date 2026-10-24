# -*- coding: utf-8 -*-
"""T2N skeleton server: ping + self_check built in; roles extend with tools."""
from __future__ import annotations

import os
import sys
import time

from .protocol import Server
from .guard import write_roots


def _ping_handler(name: str):
    def handler(params: dict) -> dict:
        return {"server": name, "status": "ok", "phase": "F0",
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    return handler


def _self_check_handler(name: str):
    def handler(params: dict) -> dict:
        return {
            "ok": True,
            "role": name,
            "pid": os.getpid(),
            "python": sys.version.split()[0],
            "repo_root": os.environ.get("T2N_REPO_ROOT") or None,
            "write_roots": [str(r) for r in write_roots()],
            "note": "F0 skeleton: ping/self_check only; role tools arrive in F1+",
        }
    return handler


def serve_generic(name: str, description: str,
                  tools: list | None = None, handlers: dict | None = None) -> None:
    builtin_tools = [
        {
            "name": "ping",
            "description": f"Liveness probe for {name}. Returns ok + timestamp.",
            "inputSchema": {"type": "object", "properties": {},
                            "additionalProperties": False},
        },
        {
            "name": "self_check",
            "description": (f"Environment self-diagnosis for {name}: write-roots, "
                            "repo root, python version."),
            "inputSchema": {"type": "object", "properties": {},
                            "additionalProperties": False},
        },
    ]
    builtin_handlers = {
        "ping": _ping_handler(name),
        "self_check": _self_check_handler(name),
    }
    all_tools = builtin_tools + list(tools or [])
    all_handlers = {**builtin_handlers, **(handlers or {})}
    Server(name, description, all_tools, all_handlers).serve()
