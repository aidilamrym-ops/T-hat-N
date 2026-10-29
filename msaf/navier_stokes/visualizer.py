"""Hermetic 2D slice renderer for the finite hydrodynamic lattice.

Display-only boundary: lattice state is never mutated and no rendered
float ever flows back into ball arithmetic. All ``float(...)``
conversions happen at the matplotlib edge via ``arb.mid()`` snapshots.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from msaf.navier_stokes.fluid_lattice import FluidLattice

__all__ = ["generate_fluid_state_plots", "generate_fluid_state_3d_render"]


def generate_fluid_state_plots(
    lattice: FluidLattice,
    layer_l: int = 1,
    output_path: str = "reports/fluid_state_evolution.png",
) -> str:
    """Render side-by-side velocity-quiver + pressure-map for one XY slice.

    Slice ``layer_l`` is extracted with exact integer indices; arrow
    coordinates use pure index scaling ``(i*dx, j*dx)`` balls snapshotted
    to display floats only. Pressure comes from the Chorin restoring
    solver ``compute_restoring_pressure("1.0", "1e-43")``. Output is
    written at 3000x2400 px (10x8 in @ 300 dpi).
    """
    if isinstance(layer_l, float):
        raise TypeError("layer_l: float64 leakage refused")
    if isinstance(output_path, (bytes, bytearray)):
        raise TypeError("output_path: bytes path refused")
    layer_l = int(layer_l)
    n = int(lattice.n)
    if not 0 <= layer_l < n:
        raise ValueError(f"layer_l out of range [0,{n}), got {layer_l}")

    # Local import: keep matplotlib isolated to the render boundary.
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from flint import arb

    # Chorin restoring pressure on the frozen field (ball arithmetic only).
    pressures = lattice.compute_restoring_pressure("1.0", "1e-43")

    xs: list[list[float]] = []
    ys: list[list[float]] = []
    us: list[list[float]] = []
    vs: list[list[float]] = []
    pmap: list[list[float]] = []
    for j in range(n):
        xrow: list[float] = []
        yrow: list[float] = []
        urow: list[float] = []
        vrow: list[float] = []
        prow: list[float] = []
        for i in range(n):
            # Pure integer-index scaling; snapshot to float for display only.
            xb = arb(i) * lattice.dx
            yb = arb(j) * lattice.dx
            cell = lattice.cell(i, j, layer_l)
            pball = pressures[lattice._idx(i, j, layer_l)]
            xrow.append(float(xb.mid()))
            yrow.append(float(yb.mid()))
            urow.append(float(cell[0].mid()))
            vrow.append(float(cell[1].mid()))
            prow.append(float(pball.mid()))
        xs.append(xrow)
        ys.append(yrow)
        us.append(urow)
        vs.append(vrow)
        pmap.append(prow)

    fig, axs = plt.subplots(1, 2, figsize=(10, 8))
    # (a) Velocity vector field.
    axs[0].quiver(xs, ys, us, vs)
    axs[0].set_title(f"Velocity field (quiver), layer l={layer_l}")
    axs[0].set_xlabel("x = i*dx")
    axs[0].set_ylabel("y = j*dx")
    axs[0].set_aspect("equal")
    # (b) Pressure contour map.
    im = axs[1].imshow(pmap, origin="lower", aspect="equal")
    axs[1].set_title(f"Restoring pressure (imshow), layer l={layer_l}")
    axs[1].set_xlabel("i")
    axs[1].set_ylabel("j")
    fig.colorbar(im, ax=axs[1], shrink=0.8)
    fig.tight_layout()

    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    # 10in x 8in @ 300dpi = 3000x2400 px geometric contract.
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def generate_fluid_state_3d_render(
    lattice: FluidLattice,
    output_path: str = "reports/fluid_state_3d.png",
) -> str:
    """Render 3D velocity structure over the full N^3 volume.

    All ``(i, j, ll)`` cells are snapshotted via ``.mid()`` to display
    floats only; lattice state is never mutated. Uses
    ``ax = fig.add_subplot(111, projection='3d')`` with 3D ``quiver``
    for vortex structures. Output at 3000x2400 px (10x8 in @ 300 dpi).
    """
    if isinstance(output_path, (bytes, bytearray)):
        raise TypeError("output_path: bytes path refused")
    output_path = str(output_path)
    n = int(lattice.n)

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from flint import arb

    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    us: list[float] = []
    vs: list[float] = []
    ws: list[float] = []
    for ll in range(n):
        zb = arb(ll) * lattice.dx
        zf = float(zb.mid())
        for j in range(n):
            yb = arb(j) * lattice.dx
            yf = float(yb.mid())
            for i in range(n):
                xb = arb(i) * lattice.dx
                cell = lattice.cell(i, j, ll)
                xs.append(float(xb.mid()))
                ys.append(yf)
                zs.append(zf)
                us.append(float(cell[0].mid()))
                vs.append(float(cell[1].mid()))
                ws.append(float(cell[2].mid()))

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.quiver(xs, ys, zs, us, vs, ws, length=0.1, normalize=True)
    ax.set_title(f"3D velocity structures (N={n}, {n**3} cells)")
    ax.set_xlabel("x = i*dx")
    ax.set_ylabel("y = j*dx")
    ax.set_zlabel("z = l*dx")
    fig.tight_layout()

    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


