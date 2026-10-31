"""Consistency checks for the Chrono Geometric enclosure artifacts.

Three independent guards, all cheap:

1. schema: every field the Lean ``EnclosureData`` relies on is present, and no
   gate is reported as verified unless a producing artifact exists;
2. drift: every literal recorded in ``lean/enclosures/*.json`` still appears
   verbatim in ``lean/EnclosureData.lean``, so the Lean constants cannot silently
   diverge from the JSON they claim to mirror;
3. re-verification: the recorded derivative enclosure is recomputed from
   scratch with ``msaf.zeta_inversion`` and must overlap the recorded ball.

Nothing here asserts a critical-line or Riemann-hypothesis claim; the gate
statuses encode exactly how far the artifacts reach.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_LEAN_DIR = Path(__file__).resolve().parent.parent / "lean"
_ENCLOSURES = _LEAN_DIR / "enclosures"
_REPO_ROOT = _LEAN_DIR.parent.parent

if (_REPO_ROOT / "msaf").is_dir() and str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:  # optional heavy dependency; the schema and drift guards work without it
    from flint import acb, arb

    from msaf import zeta_inversion  # noqa: F401

    HAS_ARB = True
except ImportError:  # pragma: no cover - standalone checkout
    HAS_ARB = False

GW_FIELDS = {
    "index",
    "t_center",
    "derivative_status",
    "derivative_enclosure",
    "derivative_magnitude",
    "derivative_tail",
    "character_sum_status",
    "character_sum_bound",
    "orthogonality_status",
    "orthogonality",
    "note",
    "provenance",
    "scope",
}

VALID_STATUS = {"VERIFIED", "UNAVAILABLE", "FAILED"}


def _load(name: str) -> dict:
    return json.loads((_ENCLOSURES / name).read_text(encoding="utf-8"))


def _lean_source() -> str:
    return (_LEAN_DIR / "EnclosureData.lean").read_text(encoding="utf-8")


def _split_ball(text: str) -> tuple["arb", "arb"]:
    """Split an Arb ball string into ``(mid, radius)``.

    ``[1.0e-10 +/- 2.0e-12]`` becomes ``(arb("1.0e-10"), arb("2.0e-12"))``;
    a bare value becomes ``(value, 0)``.
    """
    core = text.strip()
    if core.startswith("[") and core.endswith("]"):
        core = core[1:-1]
    if "+/-" in core:
        mid_text, rad_text = core.split("+/-", 1)
        return arb(mid_text.strip()), abs(arb(rad_text.strip()))
    return arb(core), arb(0)


def test_gw_bounds_schema() -> None:
    gw = _load("gw_bounds.json")
    assert GW_FIELDS <= set(gw), GW_FIELDS - set(gw)
    for key in ("derivative_status", "character_sum_status", "orthogonality_status"):
        assert gw[key] in VALID_STATUS, (key, gw[key])


def test_gw_bounds_does_not_overclaim() -> None:
    """A gate may only be VERIFIED when a producing artifact exists.

    The character-sum and orthogonality gates have no producer in this
    repository, so reporting them as VERIFIED would be a fabricated claim.
    """
    gw = _load("gw_bounds.json")
    assert gw["derivative_status"] == "VERIFIED"
    assert gw["character_sum_status"] == "UNAVAILABLE"
    assert gw["orthogonality_status"] == "UNAVAILABLE"
    assert gw["scope"]["rh_claim"] is False
    assert gw["scope"]["weil_positivity_claim"] is False
    assert gw["scope"]["critical_line_claim"] is False


def test_gw_bounds_literals_mirrored_in_lean() -> None:
    """Every recorded literal must appear verbatim in the Lean constants."""
    gw = _load("gw_bounds.json")
    source = _lean_source()
    for key in (
        "t_center",
        "derivative_enclosure",
        "derivative_magnitude",
        "derivative_tail",
        "character_sum_bound",
        "orthogonality",
        "note",
    ):
        literal = str(gw[key])
        assert literal in source, (
            f"{key} literal drifted out of EnclosureData.lean: {literal!r}"
        )
    assert source.count("GateStatus.unavailable") >= 2


def test_moore_literals_mirrored_in_lean() -> None:
    moore = _load("moore_premises.json")
    source = _lean_source()
    for key in ("verdict", "lipschitz_K", "scope"):
        assert str(moore[key]) in source, f"moore.{key} drifted out of EnclosureData.lean"
    assert f"  {moore['degree']}\n" in source
    for key in ("real_mid", "real_rad", "imag_mid", "imag_rad"):
        assert moore["box"][key] in source, f"moore.box.{key} drifted out of EnclosureData.lean"


def test_derivative_enclosure_literals_mirrored_in_lean() -> None:
    derivs = _load("derivative_enclosures.json")
    source = _lean_source()
    for block in ("box", "first_derivative", "second_derivative"):
        for key in ("real_mid", "real_rad", "imag_mid", "imag_rad"):
            assert derivs[block][key] in source, f"derivative.{block}.{key} drifted out"


@pytest.mark.skipif(not HAS_ARB, reason="msaf.zeta_inversion / flint not importable")
def test_recorded_derivative_enclosure_recomputes() -> None:
    """Recompute xi' over the same box and require overlap with the record."""
    from msaf.zeta_inversion import xi_derivative_over_ball

    moore = _load("moore_premises.json")
    gw = _load("gw_bounds.json")
    box_rec = moore["box"]

    real_mid, real_rad = _split_ball(box_rec["real_mid"])[0], _split_ball(box_rec["real_rad"])[1]
    imag_mid, imag_rad = _split_ball(box_rec["imag_mid"])[0], _split_ball(box_rec["imag_rad"])[1]
    box = acb(
        (real_mid - real_rad).union(real_mid + real_rad),
        (imag_mid - imag_rad).union(imag_mid + imag_rad),
    )

    enclosure, _tail = xi_derivative_over_ball(box, moore["degree"])

    recorded = gw["derivative_enclosure"]
    assert "] + [" in recorded, recorded
    real_text, imag_text = recorded.split("] + [", 1)
    imag_text = imag_text.rstrip("*I")
    imag_mid_rec, imag_rad_rec = _split_ball(imag_text)
    recorded_imag = (imag_mid_rec - imag_rad_rec).union(imag_mid_rec + imag_rad_rec)

    assert recorded_imag.overlaps(enclosure.imag), (
        "recorded imaginary part no longer overlaps the recomputed enclosure: "
        f"recorded {recorded_imag.str(20)} vs recomputed {enclosure.imag.str(20)}"
    )

    magnitude_mid, magnitude_rad = _split_ball(gw["derivative_magnitude"])
    assert magnitude_mid > 0
    assert magnitude_rad < arb("1e-15"), "magnitude enclosure is far too wide to be useful"
