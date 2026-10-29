# -*- coding: utf-8 -*-
"""Combined T2N visualization/materials MCP service.

Merges the illumina renderers (F5/F6) and the Materials Project client into
one stdio process. Both source modules stay authoritative for their own tool
definitions and handlers.

Prereg: reports/PREREG_MCP_CONSOLIDATION_2026-10-27.md
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "t2n"))

from core.skeleton import serve_generic
from t2n.illumina import HANDLERS as I_HANDLERS
from t2n.illumina import TOOL_DEFS as I_TOOLS
from t2n.materials import HANDLERS as M_HANDLERS
from t2n.materials import TOOL_DEFS as M_TOOLS

BUILTIN_NAMES = {"ping", "self_check"}

TOOLS = list(I_TOOLS) + list(M_TOOLS)
HANDLERS = {**I_HANDLERS, **M_HANDLERS}


def _check_contract() -> None:
    """Fail closed on duplicate or shadowed tool names."""
    names = [tool["name"] for tool in TOOLS]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise RuntimeError(f"t2n_viz duplicate tool names: {duplicates}")
    shadowed = sorted(BUILTIN_NAMES.intersection(names))
    if shadowed:
        raise RuntimeError(f"t2n_viz tools shadow builtins: {shadowed}")
    missing = sorted(set(names) - set(HANDLERS))
    if missing:
        raise RuntimeError(f"t2n_viz tools without handlers: {missing}")


_check_contract()

DESCRIPTION = (
    "Combined T2N visualization and materials service: SVG receipt labels, "
    "dependency maps, orbit plots, HTML dashboards, and the Materials Project "
    "query client. Stateless, stdlib only, writes to the T2N write roots."
)


def main() -> None:
    serve_generic("t2n_viz", DESCRIPTION, TOOLS, HANDLERS)


if __name__ == "__main__":
    main()


