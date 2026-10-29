# -*- coding: utf-8 -*-
"""Combined T2N core MCP service.

Merges the five role servers (repokeeper, archivist, science, scribe,
watchtower) into one stdio process. Each role module stays authoritative for
its own tool definitions and handlers; this file only composes them, so no
tool schema is duplicated or rewritten here.

Prereg: reports/PREREG_MCP_CONSOLIDATION_2026-10-27.md
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "t2n"))

from core.skeleton import serve_generic
from t2n import archivist, repokeeper, science, scribe, watchtower

ROLES = (repokeeper, archivist, science, scribe, watchtower)
BUILTIN_NAMES = {"ping", "self_check"}

TOOLS = [tool for role in ROLES for tool in role.TOOLS]
HANDLERS = {
    name: handler
    for role in ROLES
    for name, handler in role.HANDLERS.items()
}


def _check_contract() -> None:
    """Fail closed on duplicate or shadowed tool names."""
    names = [tool["name"] for tool in TOOLS]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise RuntimeError(f"t2n_core duplicate tool names: {duplicates}")
    shadowed = sorted(BUILTIN_NAMES.intersection(names))
    if shadowed:
        raise RuntimeError(f"t2n_core role tools shadow builtins: {shadowed}")
    missing = sorted(set(names) - set(HANDLERS))
    if missing:
        raise RuntimeError(f"t2n_core tools without handlers: {missing}")


_check_contract()

DESCRIPTION = (
    "Combined T2N core (repokeeper + archivist + science + scribe + "
    "watchtower): repository status, corpus search, exact arithmetic, "
    "append-only ledgers, and guarded runs. Stateless protocol; writes land "
    "only under T2N_WRITE_ROOTS."
)


def main() -> None:
    serve_generic("t2n_core", DESCRIPTION, TOOLS, HANDLERS)


if __name__ == "__main__":
    main()


