# -*- coding: utf-8 -*-
"""t2n_scribe -- cross-session memory & area-claim entry (F0 skeleton)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.skeleton import serve_generic

DESCRIPTION = ("T-hat-N scribe: hash-chained append-only ledger, resume "
               "briefs, automatic work audits, handoff drafting, exclusive "
               "area claims that expose parallel-session tamper.")

if __name__ == "__main__":
    serve_generic("t2n_scribe", DESCRIPTION)
