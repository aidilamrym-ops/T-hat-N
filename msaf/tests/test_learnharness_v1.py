from __future__ import annotations

import hashlib
from pathlib import Path

from msaf import learnharness_v1 as lh

PREREG_SHA = "a443e3ab728d615e36ade81aa16d35c5ddedc08388af769e3b8a621c352be853"


def test_engine_deterministic() -> None:
    payload = lh.build_payload()
    assert payload["all_pass"] is True
    assert payload["trained_samples"] == 4
    assert payload["prediction_sample"] == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    assert payload["prereg_sha256lf"] == PREREG_SHA


def test_no_float_or_numpy() -> None:
    source = Path(lh.__file__).read_text(encoding="utf-8")
    # Remove docstring/comments to avoid false positives
    import re
    code = re.sub(r'""".*?"""', '', source, flags=re.DOTALL)
    # No float literals or calls â€“ simple textual scan
    assert "float" not in code
    # Decimal literals (e.g. 1.23) are also disallowed
    literals = re.findall(r"\b\d+\.\d+\b", code)
    assert not literals
    # Numpy import prohibited
    assert "import numpy" not in code


def test_receipt_hash_matches_file() -> None:
    receipt_path = Path(lh.RECEIPT_PATH)
    assert receipt_path.is_file()
    raw = receipt_path.read_bytes()
    expected = hashlib.sha256(raw).hexdigest()
    # reâ€‘run main to generate receipt again and compare hash
    lh.main()
    new_raw = receipt_path.read_bytes()
    assert hashlib.sha256(new_raw).hexdigest() == expected


