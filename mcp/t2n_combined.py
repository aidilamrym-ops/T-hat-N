# -*- coding: utf-8 -*-
"""Deprecated alias for :mod:`t2n_viz` (illumina + materials).

Kept so older configurations that point at this file keep working. The
canonical entry point is ``mcp/t2n_viz.py``; this module only re-exports its
merged tool table and serves the same process.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import t2n_viz

TOOL_DEFS = t2n_viz.TOOLS
HANDLERS = t2n_viz.HANDLERS
DESCRIPTION = t2n_viz.DESCRIPTION

if __name__ == "__main__":
    t2n_viz.main()
