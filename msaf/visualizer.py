"""Cosmological lattice projection and spectral density reporting.

A continuous ordinate gamma_m cannot be plotted on a continuous canvas inside
MSAF. It is projected onto the modular pixel index

    k_m = floor(gamma_m / (2 pi) * log2(N_steps)) mod N_steps

with N_steps = 5.44468544329815837306650e61. The modulo is taken against the
exact integer floor(N_steps), which is the documented modulus of the grid.

Zero-fudging boundary, stated explicitly. The blueprint for this module
(`msaf_terminus_phase2.md`) computes the projection with `float()`,
`numpy.log2`, `numpy.floor` and branches on `sys.maxsize`. Every one of those
is a hand-off out of the enclosure: a 77-digit gamma collapses to 16 digits,
the floor of the rounded value is then asserted as the pixel, and the
uncertainty is silently deleted. Here the projection stays inside Arb until
the final integer pixel, and an ambiguous floor (lower and upper endpoints
rounding to different integers) is REPORTED rather than resolved by fiat.

The render boundary: matplotlib receives only Python integers that were
already certified inside the enclosure. No float produced by the computation
ever reaches the plotter. A JSON report is always written; the PNG is an
optional rendering of the same integer data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from flint import acb, arb, fmpz

from .constants import N_STEPS
from .grid import n_steps_floor
from .precision import log2

__all__ = [
    "PixelProjection",
    "AmbiguousPixel",
    "project_gamma_to_pixel",
    "projection_scale",
    "SpectralDensityReport",
    "build_density_report",
    "write_json_report",
    "render_png",
]

#: Scale factor gamma -> pixel, kept as a ball: log2(N_steps) / (2 pi).
SCALE_BITS: Final[int] = 256


class AmbiguousPixel(ValueError):
    """The gamma enclosure straddles a pixel boundary and has no single pixel."""


@dataclass(frozen=True)
class PixelProjection:
    gamma_midpoint: str
    gamma_radius: str
    pixel: fmpz
    modulus: fmpz
    unambiguous: bool


def projection_scale() -> arb:
    """The gamma-to-pixel scale log2(N_steps) / (2 pi), as an Arb ball."""
    return log2(N_STEPS) / (2 * arb.pi())


def project_gamma_to_pixel(gamma: arb) -> PixelProjection:
    """Project an ordinate enclosure onto its modular pixel index.

    The floor is taken on the whole ball. When lower and upper endpoints share
    one integer the pixel is unambiguous and certified. Otherwise
    `AmbiguousPixel` is raised with both endpoint floors attached: the caller,
    not this function, decides whether to refine the enclosure or to record
    the ambiguity.
    """
    scaled = gamma * projection_scale()
    floored = scaled.floor()
    modulus = n_steps_floor()
    if bool(floored.is_integer()) and bool(floored.is_exact()):
        return PixelProjection(
            gamma_midpoint=gamma.mid().str(30, radius=False),
            gamma_radius=gamma.rad().mid().str(12, radius=False),
            pixel=floored.fmpz() % modulus,
            modulus=modulus,
            unambiguous=True,
        )
    raise AmbiguousPixel(
        f"gamma enclosure {gamma.mid().str(12)} spans pixels "
        f"{scaled.lower().floor().fmpz()}..{scaled.upper().floor().fmpz()}; "
        "refine the enclosure before projecting"
    )


@dataclass(frozen=True)
class SpectralDensityReport:
    dimension: int
    projections: tuple[PixelProjection, ...]
    verdicts: tuple[str, ...]

    def locked_count(self) -> int:
        return sum(1 for v in self.verdicts if "LOCALIZED" in v)

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "modulus": str(self.projections[0].modulus) if self.projections else None,
            "pixels": [str(p.pixel) for p in self.projections],
            "gammas": [p.gamma_midpoint for p in self.projections],
            "gamma_radii": [p.gamma_radius for p in self.projections],
            "verdicts": list(self.verdicts),
            "locked": self.locked_count(),
            "total": len(self.projections),
            "note": "gammas are enclosure midpoints; gamma_radii are the certified radii; "
                    "pixels are exact integers, never rounded floats",
        }


def build_density_report(
    gammas: list[arb], verdicts: list[str], dimension: int
) -> SpectralDensityReport:
    """Assemble a density report from certified ordinates and their verdicts.

    Every gamma is projected through the rigid path. An ambiguous pixel aborts
    the report: a density map with silently rounded coordinates would be a
    fabrication, not a measurement.
    """
    if len(gammas) != len(verdicts):
        raise ValueError(
            f"gammas ({len(gammas)}) and verdicts ({len(verdicts)}) disagree"
        )
    return SpectralDensityReport(
        dimension=dimension,
        projections=tuple(project_gamma_to_pixel(g) for g in gammas),
        verdicts=tuple(verdicts),
    )


def write_json_report(report: SpectralDensityReport, path: Path) -> Path:
    """Write the report as JSON. Pixel integers serialise as decimal strings."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    return path


def render_png(report: SpectralDensityReport, path: Path):
    """Render the integer pixel data as a static PNG.

    Only Python integers cross into matplotlib. The histogram bins and the
    lock scatter are computed with the standard library, never with numpy, so
    that no float64 rounding can enter between the certified pixel and the ink.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pixels = [int(str(p.pixel)) for p in report.projections]
    # Decimate to a plottable range WITHOUT touching the certified values:
    # the axis shows pixel mod 2**32, labelled as such, while the JSON report
    # carries the full 206-bit addresses.
    shown = [v % (2**32) for v in pixels]
    locked = [1 if "LOCALIZED" in v else 0 for v in report.verdicts]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=False)
    ax1.hist(shown, bins=min(50, max(1, len(shown))), color="blue", edgecolor="black", alpha=0.7)
    ax1.set_title("MSAF Discrete Spectral Distribution Map (pixel mod 2^32; full addresses in JSON)")
    ax1.set_xlabel("Lattice Pixel Index Address (k) mod 2^32")
    ax1.set_ylabel("Resonance Multiplicity Count")
    ax1.grid(True, linestyle="--", alpha=0.5)

    ax2.scatter(range(len(locked)), locked, color="green", marker="o")
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(["ANOMALY", "LOCKED (0.5)"])
    ax2.set_title("Critical Line Stability Rigidity Check (sigma = 0.5)")
    ax2.set_xlabel("Isolated Root Identifier Index (m)")
    ax2.set_ylabel("Hermitian Status")
    ax2.grid(True, linestyle=":", alpha=0.5)

    plt.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)
    return path


def collect_first_zeros(count: int) -> tuple[list[arb], list[str]]:
    """Localise the first `count` zeros and return their ordinates + verdicts.

    The ordinate returned is the imaginary midpoint of the localised ball, and
    the verdict is the kernel verdict. Both come straight from
    `msaf.zeta_inversion` with no intermediate rounding.
    """
    from .zeta_inversion import ball, locate_zero

    gammas: list[arb] = []
    verdicts: list[str] = []
    for index in range(1, count + 1):
        reference = acb.zeta_zero(index)
        result = locate_zero(ball(reference.mid(), "1e-12"), max_iter=12)
        gammas.append(result.final_ball.imag)
        verdicts.append(result.verdict)
    return gammas, verdicts
