# -*- coding: utf-8 -*-
"""t2n_illumina -- context-aware visualization role entry (F0 skeleton)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.skeleton import serve_generic

DESCRIPTION = ("T-hat-N illumina: renders gate trees from receipts, "
               "dependency maps from git history, knowledge graphs, "
               "spectrum ladders and orbit plots as standalone HTML/SVG "
               "written only to the write-roots allowlist.")

if __name__ == "__main__":
    serve_generic("t2n_illumina", DESCRIPTION)
