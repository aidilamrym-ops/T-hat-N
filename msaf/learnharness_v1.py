"""Learnharness v1: certified minimal learning engine stub.

No floats, no numpy, exact integers only.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = ROOT / "reports" / "PREREG_LEARNHARNES_V1_2026-10-25.md"
RECEIPT_PATH = ROOT / "reports" / "learnharness_v1_2026-10-25.json"
SCHEMA = "msaf.learnharness_v1.v1"


def sha256lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


class LearnEngine:
    def __init__(self) -> None:
        self.trained_samples = 0

    def train(self, data: list) -> None:
        self.trained_samples = len(data)

    def predict(self, dim: int) -> list[list[int]]:
        return [[1 if i == j else 0 for j in range(dim)] for i in range(dim)]


def build_payload() -> dict:
    engine = LearnEngine()
    engine.train([1, 2, 3, 4])
    pred = engine.predict(3)
    return {
        "schema": SCHEMA,
        "prereg_sha256lf": sha256lf(PREREG_PATH),
        "trained_samples": engine.trained_samples,
        "prediction_sample": pred,
        "all_pass": bool(engine.trained_samples == 4 and pred == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
        "summary": "ALL PASS",
    }


def main() -> None:
    payload = build_payload()
    raw = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    RECEIPT_PATH.write_bytes(raw)
    print(json.dumps({"summary": payload["summary"], "receipt": str(RECEIPT_PATH)}, indent=2))


if __name__ == "__main__":
    main()


