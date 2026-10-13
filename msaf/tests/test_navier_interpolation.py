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
