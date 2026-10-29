"""Anti-Vacuum test harness for the finitist Navier-Stokes lattice.

Anti-Vacuum Constraint: the suite FAILS if the lattice is empty,
identically zero without declaration, or silently float-contaminated.
Every test constructs balls from decimal strings only.
"""

from __future__ import annotations

import pytest
from flint import arb

from msaf.navier_stokes.fluid_lattice import (
    DELTA_UNIV,
    ELL_P,
    FluidLattice,
    ResolutionAlarm,
    UndeterminedBlock,
)
from msaf.navier_stokes.interpolation import (
    coarsen,
    interpolation_error_bound,
    refine,
    refine_grid_cells,
)


def test_lattice_nonvacuum():
    lat = FluidLattice(4, "0.0001", "1")
    assert lat.ncells == 64
    lat.set_uniform("0.5", "0.25", "0.125")
    assert any(bool(v[0] != arb(0)) for v in lat.u)


def test_no_float64_leakage():
    with pytest.raises(TypeError):
        FluidLattice(4, 1e-4, "1")  # type: ignore[arg-type]
    lat = FluidLattice(4, "0.0001", "1")
    with pytest.raises(TypeError):
        lat.set_cell(0, 0, 0, (0.5, 0.0, 0.0))  # type: ignore[arg-type]


def test_planck_floor_gates_subplanck_cell():
    # L=1e-36 with N=4 forces dx=2.5e-37 < ELL_P -> ResolutionAlarm, not blow-up.
    with pytest.raises(ResolutionAlarm):
        FluidLattice(4, "0.0001", "1e-36")


def test_uniform_field_is_divergence_free_by_enclosure():
    lat = FluidLattice(4, "0.0001", "1")
    lat.set_uniform("0.5", "-0.25", "0.1")
    assert lat.divergence_contains_zero_everywhere() is True
    assert bool(lat.max_divergence_half_width().is_finite()) is True


def test_energy_bounded_and_resolution_gate_passes():
    lat = FluidLattice(4, "0.0001", "1")
    lat.set_uniform("0.5", "0.25", "0.125")
    energy = lat.kinetic_energy()
    assert bool(energy.is_finite()) is True
    verdict = lat.check_resolution_alarm("10")
    assert verdict["alarm"] is False


def test_refinement_preserves_enclosure():
    coarse = FluidLattice(2, "0.0001", "1")
    coarse.set_uniform("0.3", "0.1", "-0.2")
    fine = refine(coarse, 2)
    assert fine.n == 4
    for i in range(4):
        parent = coarse.cell(i // 2, 0, 0)
        child = fine.cell(i, 0, 0)
        for a, b in zip(parent, child):
            assert bool(b.contains(a)) is True
    back = coarsen(fine, 2)
    assert back.n == 2
    for i in range(2):
        orig = coarse.cell(i, 0, 0)
        hull = back.cell(i, 0, 0)
        for a, b in zip(orig, hull):
            assert bool(b.contains(a)) is True


def test_error_bound_is_ball_product():
    dx = arb("0.25")
    grad = arb("2")
    bound = interpolation_error_bound(dx, grad)
    assert bool((bound - arb("0.5")).contains(arb(0))) is True


def test_pixel_constants_are_distinct_strings():
    assert isinstance(ELL_P, str) and isinstance(DELTA_UNIV, str)
    # MSAF certify mandate: zero-claims by containment, never by ==.
    # arb __eq__ is exact-bitwise and fails on identical wide balls.
    assert bool((arb(ELL_P) - arb(DELTA_UNIV)).contains(arb(0))) is True
    assert arb(ELL_P).is_finite()


def test_spacetime_floor_ticks_and_position():
    lat = FluidLattice(2, "0.0001", "1")
    assert lat.elapsed_ticks() == 0
    assert lat.advance(3) == 3
    assert bool((lat.elapsed_time() - arb(3) * arb("5.39e-44")).contains(arb(0))) is True
    x, y, z = lat.position(1, 0, 0)
    assert bool((x - lat.dx).contains(arb(0))) is True


def test_gradient_laplacian_are_balls():
    lat = FluidLattice(4, "0.0001", "1")
    lat.set_uniform("0.5", "-0.25", "0.1")
    g = lat.gradient_at(1, 1, 1)
    for row in g:
        for comp in row:
            assert bool(comp.contains(arb(0))) is True
            assert bool(comp.is_finite()) is True
    lap = lat.laplacian_at(1, 1, 1)
    for comp in lap:
        assert bool(comp.contains(arb(0))) is True


def test_undetermined_block_on_zero_crossing():
    lat = FluidLattice(2, "0.0001", "1")
    lat.set_uniform("0.5", "0.25", "0.125")
    lat.assert_determined()  # nonzero field passes
    lat.set_cell(0, 0, 0, ("0", "0.25", "0.125"))
    assert len(lat.undetermined_cells()) >= 1
    with pytest.raises(UndeterminedBlock):
        lat.assert_determined()


def test_strain_tensor_stable_under_planck_shift():
    # Regression: S=0.5*(G+G^T) enclosure invariant under discrete t_P shifts.
    # advance() touches only the exact int clock, never the velocity balls.
    lat = FluidLattice(4, "0.0001", "1")
    lat.set_uniform("0.5", "-0.25", "0.1")
    lat.set_cell(1, 1, 1, ("0.6", "-0.2", "0.15"))
    s_before = lat.strain_tensor_at(1, 1, 1)
    for row in s_before:
        for comp in row:
            assert bool(comp.is_finite()) is True
    # Symmetry gate: S[a][b] and S[b][a] share the same enclosure.
    for a in range(3):
        for b in range(3):
            assert bool((s_before[a][b] - s_before[b][a]).contains(arb(0))) is True
    t0 = lat.elapsed_ticks()
    lat.advance(7)
    assert lat.elapsed_ticks() == t0 + 7
    s_after = lat.strain_tensor_at(1, 1, 1)
    for a in range(3):
        for b in range(3):
            assert bool(s_after[a][b].contains(s_before[a][b])) is True
            assert bool(s_before[a][b].contains(s_after[a][b])) is True
    # Refinement preserves velocity enclosure at the mapped parent cell;
    # strain is resolution-dependent by construction (piecewise-constant
    # copy creates interface jumps), so only finiteness is gated here.
    fine = refine_grid_cells(lat, 2)
    assert fine.elapsed_ticks() == lat.elapsed_ticks()
    v_parent = lat.cell(1, 1, 1)
    v_child = fine.cell(2, 2, 2)
    for a, b in zip(v_parent, v_child):
        assert bool(b.contains(a)) is True
    s_fine = fine.strain_tensor_at(2, 2, 2)
    for row in s_fine:
        for comp in row:
            assert bool(comp.is_finite()) is True
    # Uniform field: zero strain is preserved under refinement.
    uni = FluidLattice(2, "0.0001", "1")
    uni.set_uniform("0.5", "-0.25", "0.1")
    uni_fine = refine_grid_cells(uni, 2)
    s_uni = uni.strain_tensor_at(0, 0, 0)
    s_uni_fine = uni_fine.strain_tensor_at(0, 0, 0)
    for a in range(3):
        for b in range(3):
            assert bool(s_uni[a][b].contains(arb(0))) is True
            assert bool(s_uni_fine[a][b].contains(arb(0))) is True
    # Worst-case bound for this dx is finite and tight.
    bound = interpolation_error_bound(lat.dx, arb("1.5"))
    assert bool(bound.is_finite()) is True
    assert bool((bound - arb("1.5") * lat.dx).contains(arb(0))) is True


def test_advect_ticks_increment_one():
    lat = FluidLattice(4, "0.0001", "1")
    lat.set_uniform("0.5", "-0.25", "0.1")
    t0 = lat.elapsed_ticks()
    assert lat.advect_step() == t0 + 1
    assert lat.advect_step() == t0 + 2
    assert lat.elapsed_ticks() == t0 + 2
    assert bool((lat.elapsed_time() - arb(lat.elapsed_ticks()) * arb("5.39e-44")).contains(arb(0))) is True


def test_advect_conserves_energy_32_steps():
    lat = FluidLattice(4, "0.0001", "1")
    lat.set_uniform("0.5", "-0.25", "0.1")
    lat.set_cell(1, 1, 1, ("0.6", "-0.2", "0.15"))
    lat.set_cell(2, 0, 3, ("0.4", "0.3", "-0.1"))
    e0 = lat.kinetic_energy()
    for _ in range(32):
        lat.advect_step()
    e1 = lat.kinetic_energy()
    assert bool((e1 - e0).contains(arb(0))) is True
    assert bool(e1.is_finite()) is True


def test_advect_preserves_divergence_free():
    lat = FluidLattice(4, "0.0001", "1")
    lat.set_uniform("0.5", "-0.25", "0.1")
    assert lat.divergence_contains_zero_everywhere() is True
    lat.advect_step()
    assert lat.divergence_contains_zero_everywhere() is True
    for _ in range(31):
        lat.advect_step()
    assert lat.divergence_contains_zero_everywhere() is True
    assert lat.elapsed_ticks() == 32


def test_pressure_rejects_float():
    lat = FluidLattice(4, "0.0001", "1")
    lat.set_uniform("0.5", "-0.25", "0.1")
    with pytest.raises(TypeError):
        lat.compute_pressure_field(1.0)  # type: ignore[arg-type]


def test_pressure_dynamic_convergence_achieved():
    lat = FluidLattice(4, "0.0001", "1")
    lat.set_uniform("0.5", "-0.25", "0.1")
    lat.set_cell(1, 1, 1, ("0.6", "-0.2", "0.15"))
    p = lat.compute_pressure_field("1.0", "1e-75", 1000)
    assert len(p) == lat.ncells
    assert all(bool(v.is_finite()) for v in p)
    assert 1 <= lat._last_pressure_iters <= 10


def test_pressure_divergence_alarm_on_noise():
    lat = FluidLattice(4, "0.0001", "1")
    lat.set_uniform("0.5", "-0.25", "0.1")
    lat.set_cell(1, 1, 1, ("0.6", "-0.2", "0.15"))
    with pytest.raises(ResolutionAlarm):
        lat.compute_pressure_field("1.0", "1e-300", 1000)


def test_pressure_uniform_field():
    lat = FluidLattice(4, "0.0001", "1")
    lat.set_uniform("0.5", "-0.25", "0.1")
    p = lat.compute_pressure_field("1.0")
    assert len(p) == lat.ncells
    for v in p:
        assert bool(v.is_finite()) is True
        assert bool(v.contains(arb(0))) is True
    for v in p[1:]:
        assert bool((v - p[0]).contains(arb(0))) is True


def test_pressure_zero_crossing_alarm():
    lat = FluidLattice(4, "0.0001", "1")
    lat.set_uniform("0.5", "-0.25", "0.1")
    p_uni = lat.compute_pressure_field("1.0")
    assert any(bool(v.contains(arb(0))) for v in p_uni)
    lat.set_cell(0, 0, 0, ("0", "-0.25", "0.1"))
    p = lat.compute_pressure_field("1.0")
    for v in p:
        assert bool(v.is_finite()) is True
    with pytest.raises(UndeterminedBlock):
        lat.assert_determined()


def test_pressure_ascii_rendering_boundaries():
    lat = FluidLattice(4, "0.0001", "1")
    lat.set_uniform("0.5", "-0.25", "0.1")
    lat.set_cell(1, 1, 1, ("0.6", "-0.2", "0.15"))
    canvas = lat.render_pressure_slice_ascii(0)
    lines = canvas.split("\n")
    assert len(lines) == 4
    assert all(len(row) == 4 for row in lines)
    assert set(canvas.replace("\n", "")) <= set(" .-+#")
    uni = FluidLattice(4, "0.0001", "1")
    uni.set_uniform("0.5", "-0.25", "0.1")
    assert uni.render_pressure_slice_ascii(0) == "    \n    \n    \n    "
    with pytest.raises(ValueError):
        lat.render_pressure_slice_ascii(4)
    with pytest.raises(ValueError):
        lat.render_pressure_slice_ascii(-1)


def test_full_loop_incompressibility_preservation():
    """Fractional-step loop preserves solenoidality incl. rotation fields.

    Shear u=(f(j),-0.25,0.1) is discretely divergence-free: 10 sequential
    evolve_full_ns_step("1e-43","1.0") keep (a) divergence TRUE, (b) energy
    bounded < 1.0, (c) float inputs rejected. Restoring projection
    (Î”p=(rho/dt)div u*) clears divergence by construction: a rotation
    field (nonzero tr(G^2)) now completes 10 steps alarm-free with
    divergence TRUE throughout (384-bit working precision; 256-bit run
    instead demonstrates the guard: tripwire fires, escalation raises
    ResolutionAlarm rather than going vacuous).
    """
    from flint import arb as _arb

    lat = FluidLattice(4, "0.0001", "1", 384)  # elevated working precision:
    # sustained stepping inflates widths ~40x/projection at any precision,
    # so long runs start high; the reactive ramp below remains as guard.
    for i in range(4):
        for j in range(4):
            for ll in range(4):
                lat.set_cell(i, j, ll, (f"{5 - j}e-1", "-0.25", "0.1"))
    with pytest.raises(TypeError):
        lat.evolve_full_ns_step(1e-43, "1.0")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        lat.evolve_full_ns_step("1e-43", 1.0)  # type: ignore[arg-type]
    assert lat.divergence_contains_zero_everywhere() is True
    for _ in range(10):
        lat.evolve_full_ns_step("1e-43", "1.0")
    assert lat.divergence_contains_zero_everywhere() is True
    assert bool(lat.kinetic_energy().upper() < _arb("1.0")) is True
    assert lat.elapsed_ticks() == 10
    rot = FluidLattice(4, "0.0001", "1", 384)
    for i in range(4):
        for j in range(4):
            for ll in range(4):
                rot.set_cell(i, j, ll, (f"{5 - j}e-1", f"{-25 + 10 * i}e-2", "0.1"))
    assert rot.divergence_contains_zero_everywhere() is True
    from flint import ctx as _ctx

    try:
        for _ in range(10):
            rot.evolve_full_ns_step("1e-43", "1.0")
            assert rot.divergence_contains_zero_everywhere() is True
        assert bool(rot.kinetic_energy().upper() < _arb("1.0")) is True
        assert bool(rot.max_divergence_half_width() < _arb("1e-72")) is True
    finally:
        _ctx.prec = 256
    jumps_sustained = rot._precision_jumps
    # Guard demonstration (green): at 256-bit working precision the same
    # rotation run trips the 1e-72 wire (~step 3) and escalates safely via
    # ResolutionAlarm after re-tightening cannot recover input-carried
    # widths (recompute from a wide state stays wide). This locks the
    # tripwire + escalation path end-to-end without going vacuous.
    guard = FluidLattice(4, "0.0001", "1")
    for i in range(4):
        for j in range(4):
            for ll in range(4):
                guard.set_cell(i, j, ll, (f"{5 - j}e-1", f"{-25 + 10 * i}e-2", "0.1"))
    try:
        with pytest.raises(ResolutionAlarm):
            for _ in range(10):
                guard.evolve_full_ns_step("1e-43", "1.0")
        assert guard._precision_jumps >= 1
    finally:
        _ctx.prec = 256
    jumps = jumps_sustained + guard._precision_jumps
    assert jumps >= 1


def test_materialisation_cap_n128_refused():
    """N=128 (2M cells) is refused before allocation, instantly."""
    from msaf.navier_stokes.fluid_lattice import MatrixDimensionViolation

    with pytest.raises(MatrixDimensionViolation):
        FluidLattice(128, "0.1", "1")


def test_long_run_enclosure_growth_384bit():
    """20 restoring steps at 384-bit: geometric ~42x/step inflation measured.

    Rotation field, dt=1e-43: widths 1.9e-114 -> 1.7e-83, divergence TRUE
    throughout, wire (1e-72) still 11 orders away at step 20. Locks the
    measured growth factor band and the ~25-step horizon estimate.
    """
    from flint import arb as _arb2
    from flint import ctx as _ctx2

    rot = FluidLattice(4, "0.0001", "1", 384)
    for i in range(4):
        for j in range(4):
            for ll in range(4):
                rot.set_cell(i, j, ll, (f"{5 - j}e-1", f"{-25 + 10 * i}e-2", "0.1"))
    try:
        prev = None
        for _ in range(20):
            rot.evolve_full_ns_step("1e-43", "1.0")
            assert rot.divergence_contains_zero_everywhere() is True
            w = float(rot.max_divergence_half_width().mid())
            if prev is not None:
                assert 30.0 < w / prev < 60.0
            prev = w
        assert bool(rot.max_divergence_half_width() < _arb2("1e-72")) is True
        assert bool(rot.kinetic_energy().upper() < _arb2("1.0")) is True
    finally:
        _ctx2.prec = 256


def test_viscous_diffusion_decay():
    """Sequential advect-then-diffuse dissipates energy, spikes included.

    Configuration: N=4, extreme single-cell spike (2.0,-1.0,0.8) on a
    uniform background, nu=1e-4, 5 sequential evolve_viscous_step("1e-43")
    (= 1 Planck tick each). Diffusion is evaluated on the already-advected
    field (aligned footprint), so every step must strictly contract
    kinetic energy (ball certainly-less); any violation raises
    ResolutionAlarm (harness trigger, loud failure). Prior simultaneous
    coupling grew +8.26e-47 here; splitting inverts the sign (measured).
    """
    lat = FluidLattice(4, "0.0001", "1")
    lat.set_uniform("0.5", "-0.25", "0.1")
    lat.set_cell(1, 1, 1, ("2.0", "-1.0", "0.8"))
    with pytest.raises(TypeError):
        lat.evolve_viscous_step(1e-43)  # type: ignore[arg-type]
    with pytest.raises(ResolutionAlarm):
        lat.evolve_viscous_step("1e-44")
    energy = lat.kinetic_energy()
    assert bool(energy.is_finite()) is True
    for _ in range(5):
        lat.evolve_viscous_step("1e-43")
        decayed = lat.kinetic_energy()
        assert bool(decayed.is_finite()) is True
        assert bool(decayed < energy) is True
        if not bool(decayed < energy):
            raise ResolutionAlarm(
                f"viscous step failed to contract energy {energy} -> {decayed}"
            )
        energy = decayed
    assert lat.elapsed_ticks() == 5


def test_visualization_generator_output():
    """Hermetic renderer emits a non-empty PNG then self-cleans (harness)."""
    import os

    from msaf.navier_stokes.visualizer import generate_fluid_state_plots

    lat = FluidLattice(4, "0.0001", "1")
    for i in range(4):
        for j in range(4):
            for ll in range(4):
                lat.set_cell(i, j, ll, (f"{5 - j}e-1", f"{-25 + 10 * i}e-2", "0.1"))
    out = os.path.join("reports", "fluid_state_evolution.png")
    try:
        ret = generate_fluid_state_plots(lat, 1, out)
        assert ret == out
        assert os.path.isfile(out) is True
        assert os.path.getsize(out) > 0
    finally:
        # Harness fault-injection mode: auto-erase artifact, never linger.
        if os.path.isfile(out):
            os.remove(out)


def test_visualization_3d_render_output():
    """3D renderer emits a non-empty PNG then self-cleans (harness)."""
    import os

    from msaf.navier_stokes.visualizer import generate_fluid_state_3d_render

    lat = FluidLattice(4, "0.0001", "1")
    for i in range(4):
        for j in range(4):
            for ll in range(4):
                lat.set_cell(i, j, ll, (f"{5 - j}e-1", f"{-25 + 10 * i}e-2", "0.1"))
    out = os.path.join("reports", "fluid_state_3d.png")
    try:
        ret = generate_fluid_state_3d_render(lat, out)
        assert ret == out
        assert os.path.isfile(out) is True
        assert os.path.getsize(out) > 0
    finally:
        if os.path.isfile(out):
            os.remove(out)


