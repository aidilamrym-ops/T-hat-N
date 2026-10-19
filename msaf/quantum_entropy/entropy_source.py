"""SIMULATED entropy stream (K-Q1).

Contract (frozen in reports/REPLAY_CERT_SPEC_V0.2_QUANTUM.md):

* raw draws are 4096-bit (512-byte) blocks from the OS CSPRNG (``secrets``);
* no seed argument exists; a ``--seed`` occurrence refuses with exit code 2;
* every descriptor carries the SIMULATED label and a plain-language note
  that this is NOT a physical quantum measurement (D1);
* raw blocks are NOT retained: non-invertibility is accepted by design
  (K-Q1); per-batch digests of the consumed byte stream are recorded in the
  ledger.

Stream-to-normal transform (statistical layer, float64 by design): 53-bit
uniforms from 8-byte big-endian chunks (top 53 bits), then Box-Muller pairs.
"""

from __future__ import annotations

import hashlib
import math
import secrets
import sys

from . import SIMULATED_LABEL

__all__ = ["BLOCK_BYTES", "BATCH_NOTE", "EntropySource", "refuse_seed"]

BLOCK_BYTES = 512  # 4096 bits per block (campaign requirement)

BATCH_NOTE = (
    "raw entropy blocks are not retained (non-invertibility accepted by "
    "design, K-Q1); per-batch digests of the consumed byte stream are "
    "recorded in the ledger"
)

DESCRIPTOR_NOTE = (
    "simulated entropy stream from the operating-system CSPRNG; NOT a "
    "physical quantum measurement (D1)"
)


def refuse_seed(argv) -> None:
    """K-Q1: refuse any ``--seed`` occurrence loudly; exit code 2."""
    for arg in argv:
        if arg == "--seed" or str(arg).startswith("--seed="):
            sys.stderr.write(
                "K-Q1 SEED REFUSED: --seed is forbidden; the run is driven "
                "by the SIMULATED entropy stream only\n"
            )
            raise SystemExit(2)


class EntropySource:
    """SIMULATED non-deterministic stream. NOT a quantum measurement (D1)."""

    def __init__(self) -> None:
        self.label = SIMULATED_LABEL
        self.blocks = 0
        self.bytes_consumed = 0
        self._buf = b""
        self._batch_hasher = None
        self._batch_bytes = 0

    def descriptor(self) -> dict:
        return {
            "label": SIMULATED_LABEL,
            "backend": "os.csprng:secrets.token_bytes",
            "block_bits": BLOCK_BYTES * 8,
            "note": DESCRIPTOR_NOTE,
            "retention": BATCH_NOTE,
        }

    def probe_block(self) -> bytes:
        """One 4096-bit block straight from the OS CSPRNG (rehearsal probe)."""
        b = secrets.token_bytes(BLOCK_BYTES)
        self.blocks += 1
        return b

    def _draw(self, n: int) -> bytes:
        while len(self._buf) < n:
            self._buf += secrets.token_bytes(BLOCK_BYTES)
            self.blocks += 1
        out, self._buf = self._buf[:n], self._buf[n:]
        self.bytes_consumed += n
        if self._batch_hasher is not None:
            self._batch_hasher.update(out)
            self._batch_bytes += n
        return out

    def begin_batch(self) -> None:
        if self._batch_hasher is not None:
            raise RuntimeError("nested entropy batch not allowed")
        self._batch_hasher = hashlib.sha256()
        self._batch_bytes = 0

    def end_batch(self) -> dict:
        if self._batch_hasher is None:
            raise RuntimeError("no open entropy batch")
        meta = {
            "digest": self._batch_hasher.hexdigest(),
            "bytes": self._batch_bytes,
            "label": SIMULATED_LABEL,
            "retention": BATCH_NOTE,
        }
        self._batch_hasher = None
        self._batch_bytes = 0
        return meta

    def uniforms(self, n: int) -> list:
        """``n`` uniforms in [0, 1) from 53-bit chunks (8-byte, big-endian)."""
        buf = self._draw(8 * n)
        out = []
        for i in range(n):
            chunk = int.from_bytes(buf[8 * i:8 * i + 8], "big") >> 11
            out.append(chunk / float(1 << 53))
        return out

    def normals(self, n: int) -> list:
        """``n`` standard normals by Box-Muller on float64 (statistical layer)."""
        if n < 0:
            raise ValueError("n must be >= 0")
        need = (n + 1) // 2
        us = self.uniforms(2 * need)
        out = []
        for i in range(need):
            u1 = us[2 * i]
            if u1 == 0.0:  # probability 2**-53; keep log finite
                u1 = 1.0 / float(1 << 53)
            u2 = us[2 * i + 1]
            r = math.sqrt(-2.0 * math.log(u1))
            th = 2.0 * math.pi * u2
            out.append(r * math.cos(th))
            out.append(r * math.sin(th))
        return out[:n]
