from __future__ import annotations

import hashlib
from pathlib import Path

from msaf import bsd_v3 as bsd

PREREG_SHA = "4e45fc096dff53854de40ee885717037920d371480c39328a10e8232f2999566"

def test_bsd_v3_placeholder() -> None:
    payload = bsd.run_campaign()
    assert isinstance(payload, dict)
    assert payload["summary"] == "ALL PASS"


