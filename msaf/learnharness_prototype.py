"""Minimal learnharness prototype for MSAF.

This is intentionally a stub.  It does not train a real model and must never
be used as a substitute for a certificate.  Its only purpose is to provide a
stable, testable API surface for future campaign integration.
"""

from __future__ import annotations

from typing import Iterable


class LearnEngine:
    """Stub engine with a deterministic 8x8 identity K-matrix."""

    def __init__(self) -> None:
        self.model: int | None = None

    def train(self, data: Iterable[object]) -> int:
        """Record the number of training rows and return it."""
        self.model = len(list(data))
        return self.model

    def predict(self, state: object | None = None) -> list[list[int]]:
        """Return a deterministic 8x8 identity matrix."""
        return [[1 if i == j else 0 for j in range(8)] for i in range(8)]
