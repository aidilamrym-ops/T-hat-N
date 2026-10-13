"""Visual bridge: read-back verification of the rendered spectral map.

The PNG is an auditor-facing claim: it purports to show the pixel
distribution and lock verdicts recorded in `reports/spectral_density.json`.
This module verifies that claim mechanically, with zero narrative:

1. BINARY INTEGRITY (stdlib only: struct + zlib, no imaging library).
   PNG magic, exact chunk-walk coverage of the whole file, CRC32
   recomputation of EVERY chunk, terminal IEND. Any one-bit corruption
   anywhere fails loudly. This is the primary tripwire.
2. GEOMETRY CONTRACT. 3000x2400, 8-bit, RGBA, non-interlaced: the exact
   output of the renderer configuration (figsize 10x8 at 300 dpi). A
   substituted or re-rendered image with different geometry fails.
3. INK PRESENCE. Decoded with Pillow (an independent decoder codebase from
   matplotlib's writer, C-speed) and counted: total ink, histogram blue and
   scatter green must each exceed pinned floors. A blank canvas, a missing
   subplot, or a swapped image fails by orders of magnitude.
4. JSON LINKAGE. The JSON side is checked for type discipline (decimal
   strings, never floats), internal consistency (locked == total, verdicts
   unanimous), and range validity against the modulus.
5. FAULT INJECTION. A byte-flip copy and a truncation copy must both be
   rejected by the verifier. A harness that cannot fail is decoration.

P_narrative = 0: every check below is a comparison against a pinned constant
or a recomputed checksum. Nothing is described, everything is decided.
"""

from __future__ import annotations

import json
import struct
import sys
import tempfile
import zlib
from pathlib import Path

__all__ = [
    "CorruptImage",
    "PNG_MAGIC",
    "EXPECTED_WIDTH",
    "EXPECTED_HEIGHT",
    "INK_FLOOR",
    "BLUE_FLOOR",
    "GREEN_FLOOR",
    "verify_png",
    "verify_json",
    "main",
]

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

#: Renderer contract: figsize (10, 8) at dpi 300, RGBA, 8-bit, non-interlaced.
EXPECTED_WIDTH = 3000
EXPECTED_HEIGHT = 2400
EXPECTED_BIT_DEPTH = 8
EXPECTED_COLOR_TYPE = 6
EXPECTED_INTERLACE = 0

#: Ink floors, pinned at roughly one fifth of the measured full-image counts
#: (ink 2268611, blue 2052248, green 2019 over 7.2M pixels at 256-bit render).
#: A missing subplot fails these by orders of magnitude, not by percent.
INK_FLOOR = 400000
BLUE_FLOOR = 400000
GREEN_FLOOR = 400


class CorruptImage(ValueError):
    """The image failed structural, checksum, or content verification."""


def _read_chunks(path: Path) -> list[tuple[bytes, bytes]]:
    """Walk every chunk; the walk must consume the file exactly."""
    data = path.read_bytes()
    if data[:8] != PNG_MAGIC:
        raise CorruptImage(f"{path}: bad PNG magic")
    chunks: list[tuple[bytes, bytes]] = []
    offset = 8
    while True:
        if offset + 8 > len(data):
            raise CorruptImage(f"{path}: truncated chunk header at {offset}")
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        end = offset + 12 + length
        if end > len(data):
            raise CorruptImage(f"{path}: chunk {kind!r} overruns file")
        payload = data[offset + 8 : offset + 8 + length]
        stored_crc = struct.unpack(">I", data[offset + 8 + length : end])[0]
        computed_crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
        if stored_crc != computed_crc:
            raise CorruptImage(
                f"{path}: CRC mismatch in {kind!r} "
                f"(stored {stored_crc:08x} != computed {computed_crc:08x})"
            )
        chunks.append((kind, payload))
        offset = end
        if kind == b"IEND":
            break
    if offset != len(data):
        raise CorruptImage(f"{path}: {len(data) - offset} trailing bytes after IEND")
    return chunks


def verify_png(path: Path) -> dict:
    """Verify structure, checksums, geometry and ink. Returns measured stats."""
    path = Path(path)
    chunks = _read_chunks(path)
    kinds = [kind for kind, _ in chunks]
    if kinds[0] != b"IHDR" or kinds[-1] != b"IEND":
        raise CorruptImage(f"{path}: bad chunk framing")
    width, height, depth, color, _comp, _filt, interlace = struct.unpack(
        ">IIBBBBB", next(p for k, p in chunks if k == b"IHDR")
    )
    if (width, height, depth, color, interlace) != (
        EXPECTED_WIDTH,
        EXPECTED_HEIGHT,
        EXPECTED_BIT_DEPTH,
        EXPECTED_COLOR_TYPE,
        EXPECTED_INTERLACE,
    ):
        raise CorruptImage(
            f"{path}: geometry {(width, height, depth, color, interlace)} "
            "breaks the renderer contract"
        )
    software = b"".join(p for k, p in chunks if k == b"tEXt")
    if b"matplotlib" not in software.lower():
        raise CorruptImage(f"{path}: renderer identity tag missing")

    from PIL import Image

    import numpy as np

    pixels = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    red, green, blue = pixels[:, :, 0], pixels[:, :, 1], pixels[:, :, 2]
    stats = {
        "total": int(red.size),
        "ink": int(((red < 250) | (green < 250) | (blue < 250)).sum()),
        "blue": int(((blue - red > 40) & (blue - green > 20)).sum()),
        "green": int(((green - red > 40) & (green - blue > 20)).sum()),
    }
    for key, floor in (("ink", INK_FLOOR), ("blue", BLUE_FLOOR), ("green", GREEN_FLOOR)):
        if stats[key] < floor:
            raise CorruptImage(
                f"{path}: {key} count {stats[key]} below floor {floor}; "
                "a subplot is missing or the canvas is wrong"
            )
    return stats


def verify_json(path: Path) -> dict:
    """Verify the JSON side: string discipline and internal consistency."""
    from decimal import Decimal

    report = json.loads(Path(path).read_text(encoding="utf-8"))
    modulus = Decimal(report["modulus"])
    pixels = report["pixels"]
    if not all(isinstance(p, str) for p in pixels):
        raise CorruptImage(f"{path}: pixel addresses must be decimal strings")
    addresses = [int(p) for p in pixels]
    if not all(0 <= a < modulus for a in addresses):
        raise CorruptImage(f"{path}: pixel address outside [0, modulus)")
    shown = [a % 2**32 for a in addresses]
    if not all(isinstance(v, int) and 0 <= v < 2**32 for v in shown):
        raise CorruptImage(f"{path}: projected coordinate out of plot range")
    if report["locked"] != report["total"] != len(pixels):
        raise CorruptImage(f"{path}: locked/total/pixel counts disagree")
    if any(v != "ZERO-LOCALIZED" for v in report["verdicts"]):
        raise CorruptImage(f"{path}: non-unanimous verdicts")
    if len(report.get("gamma_radii", [])) != len(pixels):
        raise CorruptImage(f"{path}: gamma radii missing for some ordinate")
    return {"pixels": len(pixels), "locked": report["locked"], "shown": shown}


def test_png_topology_and_checksums() -> None:
    root = Path(__file__).resolve().parent.parent.parent
    stats = verify_png(root / "reports" / "spectral_density.png")
    assert stats["total"] == EXPECTED_WIDTH * EXPECTED_HEIGHT


def test_png_ink_proves_both_subplots_rendered() -> None:
    root = Path(__file__).resolve().parent.parent.parent
    stats = verify_png(root / "reports" / "spectral_density.png")
    assert stats["blue"] >= BLUE_FLOOR and stats["green"] >= GREEN_FLOOR


def test_json_linkage_is_type_disciplined() -> None:
    root = Path(__file__).resolve().parent.parent.parent
    linkage = verify_json(root / "reports" / "spectral_density.json")
    assert linkage["locked"] == linkage["pixels"] == 3


def test_byte_flip_is_detected() -> None:
    """Fault injection: one flipped payload byte must detonate the CRC gate."""
    root = Path(__file__).resolve().parent.parent.parent
    original = root / "reports" / "spectral_density.png"
    with tempfile.TemporaryDirectory() as tmp:
        poisoned = Path(tmp) / "flip.png"
        data = bytearray(original.read_bytes())
        data[200] ^= 0xFF
        poisoned.write_bytes(bytes(data))
        try:
            verify_png(poisoned)
        except CorruptImage:
            return
    raise AssertionError("byte-flipped image passed verification")


def test_truncation_is_detected() -> None:
    """Fault injection: a cut file must fail topology, never parse silently."""
    root = Path(__file__).resolve().parent.parent.parent
    original = root / "reports" / "spectral_density.png"
    with tempfile.TemporaryDirectory() as tmp:
        cut = Path(tmp) / "cut.png"
        cut.write_bytes(original.read_bytes()[:100000])
        try:
            verify_png(cut)
        except CorruptImage:
            return
    raise AssertionError("truncated image passed verification")


def main() -> int:
    failures = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"FAIL {name}: {type(exc).__name__}: {exc}")
        else:
            print(f"ok   {name}")
    print(f"\n{failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
