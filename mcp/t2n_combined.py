# -*- coding: utf-8 -*-
"""Combined T2N MCP service.
Merges illumina visualizers and materials API client into a single
MCP process. Keeps original modules untouched.
"""
import sys
from pathlib import Path

# Ensure module path includes directory of this file
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import original MCP modules
from t2n.illumina import TOOL_DEFS as I_TOOL_DEFS, HANDLERS as I_HANDLERS, DESCRIPTION as I_DESC
from t2n.materials import TOOL_DEFS as M_TOOL_DEFS, HANDLERS as M_HANDLERS, DESCRIPTION as M_DESC
from core.skeleton import serve_generic

# Merge tool definitions
TOOL_DEFS = I_TOOL_DEFS + M_TOOL_DEFS

# Merge handlers
HANDLERS = {**I_HANDLERS, **M_HANDLERS}

# Combined description
DESCRIPTION = (
    "Combined T2N MCP (illumina + materials). "
    "Provides SVG/HTML visualizers and Materials Project API client. "
    "Stateless, stdlib only, writes to allowlist roots."
)

if __name__ == "__main__":
    serve_generic("t2n_combined", DESCRIPTION, TOOL_DEFS, HANDLERS)
