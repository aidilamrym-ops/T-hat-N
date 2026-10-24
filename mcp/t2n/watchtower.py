# -*- coding: utf-8 -*-
"""t2n_watchtower -- guarded long runs witness & reaper entry (F0 skeleton)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.skeleton import serve_generic

DESCRIPTION = ("T-hat-N watchtower: guarded subprocess runs with always-on "
               "streaming logs, CPU/output-age watching, safe reaping and a "
               "run history ledger for forensics.")

if __name__ == "__main__":
    serve_generic("t2n_watchtower", DESCRIPTION)
