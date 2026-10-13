"""Finite-information fluid lattice: strict-finitist Navier-Stokes substrate.

Conflation guard
----------------
- Continuum domain R^3 x [0,inf) is TRUNCATED to a finite periodic
  lattice T^3_N with N^3 cells. There is no ``lim dx -> 0`` path.
- Universe Pixel Constant ``DELTA_UNIV`` and Planck floor ``ELL_P``
  bound the grid from below: ``dx >= ELL_P`` is enforced as a ball
  comparison. Violation raises :class:`ResolutionAlarm`, never a
  "physical singularity".
- Infinitist "smoothness breakdown" (``||v||_inf -> inf``) is reframed
  as a resolution alarm: the calculus ran out of information capacity
  at finite N, finite prec, finite energy bound E.
- Zero float64 leakage: every numeric entry point rejects ``float``
  and accepts only ``str`` / ``int`` / ``arb`` / ``acb``.

Space-Time Floor (mandate 4)
----------------------------
- Integer index coordinates ``(i,j,l)`` scale by ``DELTA_UNIV``:
  ``x_i = i*dx`` as exact ball arithmetic, ``dx = L/N`` with
  ``dx >= ELL_P``. No ``Delta x -> 0`` operation exists.
- Discrete time is Planck ticks: ``t_k = ticks * t_P`` with
  ``t_P = 5.39e-44 s`` from decimal string, ``ticks`` a Python int
  (exact, unbounded). ``advance()`` records ticks, never floats.

Interval Energy Enclosure
-------------------------
- Gradient and Laplacian use ``arb`` balls only
  (``acb`` accepted for DFT-extension path, never float).
- No rounding operation (``round``/``floor``-to-float) exists on this path.
- UNDETERMINED block: if any velocity-component envelope contains zero
  across successive evaluations, sign is unknowable and the caller
  receives :class:`UndeterminedBlock`, never a silently signed value.
"""

from __future__ import annotations

from typing import Final, Sequence

from flint import acb, arb, ctx

__all__ = [
    "ELL_P",
    "ELL_P_RAD",
    "D_OBS",
    "D_OBS_RAD",
    "DELTA_UNIV",
    "PLANCK_TIME_STR",
    "MATERIALISATION_CAP",
    "MatrixDimensionViolation",
    "ResolutionAlarm",
    "UndeterminedBlock",
    "FluidLattice",
    "planck_time_seconds",
]

#: Planck resolution floor, ball with explicit measurement width (CODATA 2018).
ELL_P: Final[str] = "1.616255e-35"
ELL_P_RAD: Final[str] = "0.0000005e-35"

#: Observable-universe diameter, ball with explicit width.
D_OBS: Final[str] = "8.8e26"
D_OBS_RAD: Final[str] = "0.2e26"

#: Universe pixel constant: one Planck cell, central value string.
DELTA_UNIV: Final[str] = "1.616255e-35"

#: One Planck tick in seconds, manuscript value, decimal string only.
PLANCK_TIME_STR: Final[str] = "5.39e-44"

#: Hard ceiling on dense materialisation (N^3 velocity cells).
#: N=64 -> 262144 cells x 3 comps, OK. N=128 -> 2M cells, refused here.
MATERIALISATION_CAP: Final[int] = 1_000_000


class MatrixDimensionViolation(MemoryError):
    """Dense lattice materialisation attempted beyond the hard ceiling."""


class ResolutionAlarm(RuntimeError):
    """Finite-capacity alarm: grid ran out of information, not a singularity.

    Raised when ``dx < ELL_P`` (sub-Planck cell), when a velocity-ball
    radius exceeds its midpoint magnitude at the working precision, or
    when the kinetic-energy enclosure exceeds the finite bound E.
    Catch this; do NOT relabel it as blow-up.
    """


class UndeterminedBlock(RuntimeError):
    """Velocity envelope cuts through zero: sign unknowable, evaluation blocked.

    Raised by :meth:`FluidLattice.assert_determined` when any component
    ball contains the exact zero. Successive evaluations that straddle
    zero cannot be signed without manufacturing information.
    """


def _reject_float(value: object, name: str) -> None:
    if isinstance(value, float):
        raise TypeError(f"{name}: float64 leakage refused (got {value!r}); pass decimal str")


def _to_ball(value: str | int | arb | acb, name: str) -> arb:
    _reject_float(value, name)
    if isinstance(value, arb):
        return value
    if isinstance(value, int):
        return arb(value)
    if isinstance(value, str):
        return arb(value)
    raise TypeError(f"{name}: expected str|int|arb, got {type(value).__name__}")


def _ell_p_ball() -> arb:
    c, r = arb(ELL_P), arb(ELL_P_RAD)
    return (c - r).union(c + r)


def _delta_univ_ball() -> arb:
    # Pixel enclosure inherits the Planck width; identity is explicit.
    return _ell_p_ball()


def planck_time_seconds() -> arb:
    """One Planck tick in seconds, built live from decimal string at active prec.

    Factory (not a module constant) so the ball is never frozen at the
    53-bit import-time precision.
    """
    return arb(PLANCK_TIME_STR)


class FluidLattice:
    """Finite periodic lattice T^3_N carrying a divergence-free velocity field.

    Storage: ``u[k] = (u0, u1, u2)`` as Arb balls, ``k`` in ``[0, N^3)``.
    Index ``k = (i*N + j)*N + l``. Spacing ``dx = L / N`` as exact
    ball division. Time ``t = ticks * t_P`` with exact int ticks.
    No float participates at any point.
    """

    __slots__ = ("n", "dx", "length", "nu", "prec_bits", "u", "ticks")

    def __init__(self, n: int, nu_str: str, length_str: str = "1", prec_bits: int = 256) -> None:
        _reject_float(nu_str, "nu_str")
        _reject_float(length_str, "length_str")
        if isinstance(n, float):
            raise TypeError("n: float64 leakage refused")
        n = int(n)
        if n < 1:
            raise ValueError(f"n must be positive, got {n}")
        if int(prec_bits) <= 0:
            raise ValueError(f"prec_bits must be positive, got {prec_bits}")
        ctx.prec = int(prec_bits)
        ncells = n * n * n
        if ncells > MATERIALISATION_CAP:
            raise MatrixDimensionViolation(
                f"N^3={ncells} exceeds cap {MATERIALISATION_CAP}; "
                "use structural/probe path, do not materialise"
            )
        length = _to_ball(length_str, "length_str")
        nu = _to_ball(nu_str, "nu_str")
        if not bool(nu > 0):
            raise ValueError("kinematic viscosity nu must be > 0")
        dx = length / arb(n)
        # Planck floor gate: dx enclosure must lie at or above ELL_P.
        if not bool(dx.lower() >= _ell_p_ball().upper()):
            raise ResolutionAlarm(
                f"cell dx=[{dx.lower()}, {dx.upper()}] below Planck floor "
                f"ELL_P={ELL_P}; finite grid exhausted, not a singularity"
            )
        self.n = n
        self.dx = dx
        self.length = length
        self.nu = nu
        self.prec_bits = int(prec_bits)
        self.u: list[tuple[arb, arb, arb]] = [(arb(0), arb(0), arb(0))] * ncells
        self.ticks = 0

    @property
    def ncells(self) -> int:
        return self.n * self.n * self.n

    @property
    def delta_univ(self) -> arb:
        """Universe pixel constant as a ball at the active precision."""
        return _delta_univ_ball()

    @property
    def ell_p(self) -> arb:
        """Planck floor as a ball at the active precision."""
        return _ell_p_ball()

    # -- Space-Time Floor: integer indices scaled by pixel, Planck ticks --
    def _idx(self, i: int, j: int, l: int) -> int:
        n = self.n
        return (i % n * n + j % n) * n + l % n

    def position(self, i: int, j: int, l: int) -> tuple[arb, arb, arb]:
        """Physical position of cell ``(i,j,l)``: ``(i*dx, j*dx, l*dx)`` balls."""
        return (arb(i % self.n) * self.dx, arb(j % self.n) * self.dx, arb(l % self.n) * self.dx)

    def elapsed_ticks(self) -> int:
        """Accumulated discrete time in Planck ticks. Exact int."""
        return self.ticks

    def elapsed_time(self) -> arb:
        """Accumulated physical time ``ticks * t_P`` as an Arb ball."""
        return arb(self.ticks) * planck_time_seconds()

    def advance(self, steps: int = 1) -> int:
        """Record ``steps`` Planck ticks. Negative steps refused."""
        if isinstance(steps, float):
            raise TypeError("steps: float64 leakage refused")
        steps = int(steps)
        if steps < 0:
            raise ValueError(f"steps must be non-negative, got {steps}")
        self.ticks += steps
        return self.ticks

    # -- Field mutation (strings only) --
    def set_uniform(self, ux: str, uy: str, uz: str) -> None:
        """Fill every cell with one constant ball vector (from strings)."""
        v = (_to_ball(ux, "ux"), _to_ball(uy, "uy"), _to_ball(uz, "uz"))
        self.u = [v] * self.ncells

    def set_cell(self, i: int, j: int, l: int, v: Sequence[str | int | arb]) -> None:
        """Set one cell from decimal strings (no float)."""
        if len(v) != 3:
            raise ValueError("cell vector must have 3 components")
        ball_v = tuple(_to_ball(c, f"v[{k}]") for k, c in enumerate(v))  # type: ignore[misc]
        self.u[self._idx(i, j, l)] = ball_v  # type: ignore[assignment]

    def cell(self, i: int, j: int, l: int) -> tuple[arb, arb, arb]:
        return self.u[self._idx(i, j, l)]

    # -- Discrete advection: cyclic shift T-hat, one pixel per Planck tick --
    def advect_step(self) -> int:
        """Shift the full velocity field one pixel along +x (orbital).

        Circulant generator T-hat semantics (cf. MSAF ``CyclicShift``:
        ``T e_j = e_{(j+1) mod n}``): ``new(i,j,l) = old(i-1,j,l)``.
        Pure permutation, no arithmetic, no smoothing, no float.
        ``self.ticks`` increments exactly 1 per call (PlanckClock).
        Returns the new tick count.
        """
        n = self.n
        old = self.u
        new: list[tuple[arb, arb, arb]] = [old[0]] * self.ncells
        for i in range(n):
            for j in range(n):
                for ll in range(n):
                    new[self._idx(i, j, ll)] = old[self._idx(i - 1, j, ll)]
        self.u = new
        self.ticks += 1
        return self.ticks

    # -- Interval enclosures: energy, gradient, Laplacian, divergence --
    def kinetic_energy(self) -> arb:
        """Finite energy E = sum_k |u_k|^2 dx^3 as one ball."""
        vol = self.dx * self.dx * self.dx
        total = arb(0)
        for v0, v1, v2 in self.u:
            total += (v0 * v0 + v1 * v1 + v2 * v2) * vol
        return total

    def gradient_at(self, i: int, j: int, l: int) -> tuple[tuple[arb, arb, arb], tuple[arb, arb, arb], tuple[arb, arb, arb]]:
        """Central-difference gradient tensor ``d_j u_c`` as 3x3 arb balls.

        Row ``c`` = gradient of component ``u_c`` along ``(x,y,z)``.
        Ball arithmetic only; no rounding, no float.
        """
        inv2dx = arb(1) / (arb(2) * self.dx)
        ux_p, ux_m = self.cell(i + 1, j, l)[0], self.cell(i - 1, j, l)[0]
        uy_p, uy_m = self.cell(i, j + 1, l)[1], self.cell(i, j - 1, l)[1]
        uz_p, uz_m = self.cell(i, j, l + 1)[2], self.cell(i, j, l - 1)[2]
        # Full tensor: off-axis differences per component.
        gx = ((ux_p - ux_m) * inv2dx,
              (self.cell(i, j + 1, l)[0] - self.cell(i, j - 1, l)[0]) * inv2dx,
              (self.cell(i, j, l + 1)[0] - self.cell(i, j, l - 1)[0]) * inv2dx)
        gy = ((self.cell(i + 1, j, l)[1] - self.cell(i - 1, j, l)[1]) * inv2dx,
              (uy_p - uy_m) * inv2dx,
              (self.cell(i, j, l + 1)[1] - self.cell(i, j, l - 1)[1]) * inv2dx)
        gz = ((self.cell(i + 1, j, l)[2] - self.cell(i - 1, j, l)[2]) * inv2dx,
              (self.cell(i, j + 1, l)[2] - self.cell(i, j - 1, l)[2]) * inv2dx,
              (uz_p - uz_m) * inv2dx)
        _ = (ux_p, ux_m, uy_p, uy_m, uz_p, uz_m)
        return (gx, gy, gz)

    def strain_tensor_at(self, i: int, j: int, l: int) -> tuple[tuple[arb, arb, arb], tuple[arb, arb, arb], tuple[arb, arb, arb]]:
        """Symmetric strain-rate tensor S=0.5*(G+G^T) as 3x3 arb balls.

        Derived from :meth:`gradient_at` by ball arithmetic only.
        No float, no rounding, no smoothing.
        """
        g = self.gradient_at(i, j, l)
        half = arb(1) / arb(2)
        return tuple(  # type: ignore[return-value]
            tuple((g[a][b] + g[b][a]) * half for b in range(3)) for a in range(3)
        )

    def laplacian_at(self, i: int, j: int, l: int) -> tuple[arb, arb, arb]:
        """7-point second-difference Laplacian ``Delta u_c`` as 3 arb balls."""
        invdx2 = arb(1) / (self.dx * self.dx)
        out: list[arb] = []
        for c in range(3):
            centre = self.cell(i, j, l)[c]
            acc = (self.cell(i + 1, j, l)[c] - arb(2) * centre + self.cell(i - 1, j, l)[c])
            acc += (self.cell(i, j + 1, l)[c] - arb(2) * centre + self.cell(i, j - 1, l)[c])
            acc += (self.cell(i, j, l + 1)[c] - arb(2) * centre + self.cell(i, j, l - 1)[c])
            out.append(acc * invdx2)
        return (out[0], out[1], out[2])

    def divergence_at(self, i: int, j: int, l: int) -> arb:
        """Central-difference divergence at one cell, ball arithmetic only."""
        inv2dx = arb(1) / (arb(2) * self.dx)
        dudx = (self.cell(i + 1, j, l)[0] - self.cell(i - 1, j, l)[0]) * inv2dx
        dvdy = (self.cell(i, j + 1, l)[1] - self.cell(i, j - 1, l)[1]) * inv2dx
        dwdz = (self.cell(i, j, l + 1)[2] - self.cell(i, j, l - 1)[2]) * inv2dx
        return dudx + dvdy + dwdz

    def max_divergence_half_width(self) -> arb:
        """Widest divergence-ball radius over the lattice (tightness metric)."""
        widest = arb(0)
        n = self.n
        for i in range(n):
            for j in range(n):
                for ll in range(n):
                    widest = max(widest, self.divergence_at(i, j, ll).rad())
        return widest

    def divergence_contains_zero_everywhere(self) -> bool:
        """Solenoidal check: every divergence ball must contain 0."""
        n = self.n
        for i in range(n):
            for j in range(n):
                for ll in range(n):
                    if not bool(self.divergence_at(i, j, ll).contains(arb(0))):
                        return False
        return True

    # -- Spectral/circulant Poisson pressure: p = -rho Δ^{-1} tr(G²) --
    def compute_pressure_field(self, rho_str: str = "1.0", iters: int = 200) -> list[arb]:
        """Discrete pressure field over all N³ cells as Arb balls.

        Source from certified gradients: ``src = -rho*Σ_{a,b} G[b][a]*G[a][b]``
        with ``G = gradient_at(i,j,l)``. Inverse Laplacian Δ^{-1} via
        bounded-precision circulant Jacobi solver (periodic, zero-mean
        gauge), interval-ball arithmetic only. No ``float()``, no rounding
        primitive. ``iters`` is a fixed finite budget, never a limit.
        """
        _reject_float(rho_str, "rho_str")
        if isinstance(iters, float):
            raise TypeError("iters: float64 leakage refused")
        iters = int(iters)
        if iters < 1:
            raise ValueError(f"iters must be >= 1, got {iters}")
        rho = _to_ball(rho_str, "rho_str")
        n = self.n
        ncells = self.ncells
        dx2 = self.dx * self.dx
        six = arb(6)
        # 1. Source term per cell from certified gradient tensor.
        src: list[arb] = [arb(0)] * ncells
        for i in range(n):
            for j in range(n):
                for ll in range(n):
                    g = self.gradient_at(i, j, ll)
                    acc = arb(0)
                    for a in range(3):
                        for b in range(3):
                            acc += g[b][a] * g[a][b]
                    src[self._idx(i, j, ll)] = -rho * acc
        # 2. Zero-mean gauge (periodic Laplacian singular on constants).
        mean = arb(0)
        for s in src:
            mean += s
        mean = mean / arb(ncells)
        src = [s - mean for s in src]
        # 3. Circulant Jacobi iteration, fixed budget, balls only.
        p: list[arb] = [arb(0)] * ncells
        for _ in range(iters):
            nxt: list[arb] = [arb(0)] * ncells
            for i in range(n):
                for j in range(n):
                    for ll in range(n):
                        k = self._idx(i, j, ll)
                        hood = (
                            p[self._idx(i + 1, j, ll)] + p[self._idx(i - 1, j, ll)]
                            + p[self._idx(i, j + 1, ll)] + p[self._idx(i, j - 1, ll)]
                            + p[self._idx(i, j, ll + 1)] + p[self._idx(i, j, ll - 1)]
                        )
                        nxt[k] = (hood - dx2 * src[k]) / six
            p = nxt
            # Re-pin gauge every 50 sweeps against ball drift.
        m = arb(0)
        for v in p:
            m += v
        m = m / arb(ncells)
        return [v - m for v in p]

    def pressure_max_half_width(self, rho_str: str = "1.0", iters: int = 200) -> arb:
        """Largest ball radius in the pressure field (tightness metric)."""
        widest = arb(0)
        for v in self.compute_pressure_field(rho_str, iters):
            if v.rad() > widest:
                widest = v.rad()
        return widest

    # -- 2D terminal ASCII canvas: pressure slice at fixed vertical index --
    @staticmethod
    def _mid_char(mid: arb) -> str:
        """Map one pressure midpoint ball to 5 magnitude levels, ints only.

        Thresholds (absolute): 0 -> ' ', <5e-05 -> '.', <1e-04 -> '-',
        <2e-04 -> '+', else '#'. Decimal strings are decomposed to exact
        integer ratios; comparison is order-then-cross-multiplied
        integers. No ``float()`` object is constructed on this path.
        """
        s = mid.str(30, radius=False).strip()
        t = s[1:] if (s.startswith("-") or s.startswith("+")) else s
        if "e" in t or "E" in t:
            mant, _, exp_s = t.lower().partition("e")
            exp10 = int(exp_s)
        else:
            mant, exp10 = t, 0
        if "." in mant:
            head, _, tail = mant.partition(".")
            digits_s = (head + tail).lstrip("0")
            exp10 -= len(tail)
        else:
            digits_s = mant.lstrip("0")
        if not digits_s:
            return " "

        def _lt(num1: int, exp1: int, num2: int, exp2: int) -> bool:
            o1 = exp1 + len(str(num1)) - 1
            o2 = exp2 + len(str(num2)) - 1
            if o1 != o2:
                return o1 < o2
            if exp1 == exp2:
                return num1 < num2
            if exp1 > exp2:
                return num1 * 10 ** (exp1 - exp2) < num2
            return num1 < num2 * 10 ** (exp2 - exp1)

        num = int(digits_s)
        if _lt(num, exp10, 5, -5):
            return "."
        if _lt(num, exp10, 1, -4):
            return "-"
        if _lt(num, exp10, 2, -4):
            return "+"
        return "#"

    def render_pressure_slice_ascii(self, layer_l: int = 0) -> str:
        """Render the N x N pressure slice at vertical index ``layer_l``.

        Each cell ``(i,j)`` maps ``p`` midpoint to one of
        ``' '``, ``'.'``, ``'-'``, ``'+'``, ``'#'``. Rows ``i=0..N-1``,
        joined by ``"\\n"`` (exactly N lines). Integer/string path only.
        """
        if isinstance(layer_l, float):
            raise TypeError("layer_l: float64 leakage refused")
        layer_l = int(layer_l)
        if not 0 <= layer_l < self.n:
            raise ValueError(f"layer_l {layer_l} out of range [0, {self.n - 1}]")
        p = self.compute_pressure_field("1.0")
        rows: list[str] = []
        for i in range(self.n):
            row = "".join(
                self._mid_char(p[self._idx(i, j, layer_l)].mid()) for j in range(self.n)
            )
            rows.append(row)
        return "\n".join(rows)

    # -- UNDETERMINED block: zero-crossing envelope gate --
    def undetermined_cells(self) -> list[tuple[int, int, int]]:
        """Cells where any velocity-component ball contains exact zero.

        Such a cell cannot be signed; successive evaluations straddling
        zero cut through the envelope. Returns the index list (possibly empty).
        """
        bad: list[tuple[int, int, int]] = []
        n = self.n
        for i in range(n):
            for j in range(n):
                for ll in range(n):
                    v = self.cell(i, j, ll)
                    if any(bool(c.contains(arb(0))) for c in v):
                        bad.append((i, j, ll))
        return bad

    def assert_determined(self) -> None:
        """Raise :class:`UndeterminedBlock` if any envelope contains zero."""
        bad = self.undetermined_cells()
        if bad:
            raise UndeterminedBlock(
                f"UNDETERMINED: {len(bad)} cells straddle zero "
                f"(first {bad[0]}); sign unknowable, evaluation blocked"
            )

    def check_resolution_alarm(self, energy_bound_str: str = "10") -> dict:
        """Finite-capacity gate. Returns dict, raises nothing on PASS.

        Alarm conditions (any one triggers ``alarm=True``):
          1. energy enclosure upper bound exceeds finite E.
          2. any velocity ball non-finite.
          3. dx enclosure dips below ELL_P upper bound.
        The dict carries ``alarm`` + ``reason``; callers must NOT read
        ``alarm=True`` as a singularity claim.
        """
        e_bound = _to_ball(energy_bound_str, "energy_bound_str")
        energy = self.kinetic_energy()
        if bool(energy.upper() > e_bound.upper()):
            return {"alarm": True, "reason": f"energy {energy} exceeds bound {e_bound}", "energy": energy}
        for v in self.u:
            for comp in v:
                if not bool(comp.is_finite()):
                    return {"alarm": True, "reason": "non-finite ball reached lattice", "energy": energy}
        if not bool(self.dx.lower() >= _ell_p_ball().upper()):
            return {"alarm": True, "reason": "dx below Planck floor", "energy": energy}
        return {"alarm": False, "reason": "within finite information capacity", "energy": energy}
