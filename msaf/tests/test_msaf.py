"""Regression tests for the MSAF kernel and the core lattice.

Every test exists because a plausible-looking variant of the same code is
silently wrong. A test that merely restates the implementation proves nothing;
each one below pins a specific landmine.

Run with `python -m pytest msaf -q`, or `python -m msaf.tests.test_msaf` for a
pytest-free run.
"""

from __future__ import annotations

import json
import math
import sys
import tempfile
from pathlib import Path

from msaf.precision import DEFAULT_PRECISION_BITS, set_precision

set_precision(DEFAULT_PRECISION_BITS)

from flint import acb, arb, arb_mat, ctx, fmpq  # noqa: E402

from msaf import zeta_inversion as zi  # noqa: E402

import msaf_core_lattice as lattice  # noqa: E402
from msaf.budget import (  # noqa: E402
    lambda_min_estimate,
    manuscript_critical_dimension,
    mantissa_bits,
    measured_critical_dimension,
    measured_entropy,
    underflow_dimension,
)
from msaf.certify import (  # noqa: E402
    contains_zero,
    contains_zero_complex,
    contains_zero_matrix,
    is_exact_zero,
)
from msaf.evolution import (  # noqa: E402
    Genome,
    Ledger,
    NonFiniteMeasurement,
    RootPullGenome,
    evolve_lattice,
    evolve_root_pull,
    measure_fitness,
    mutate,
    replay,
)
from msaf.format import point  # noqa: E402
from msaf.grid import (  # noqa: E402
    decimal_to_fmpq,
    n_steps_exact_rational_parts,
    n_steps_floor,
)
from msaf.guinand import spectral_profile, weil_matrix  # noqa: E402
from msaf.operators import (  # noqa: E402
    CirculantHamiltonian,
    CyclicShift,
    MatrixDimensionViolation,
    commutator_residual,
    identity,
)
from msaf.precision import (  # noqa: E402
    PrecisionLandmine,
    ball_precision,
    log2,
)

P = DEFAULT_PRECISION_BITS


# --------------------------------------------------------------------------
# Precision landmines
# --------------------------------------------------------------------------


def test_arb_second_argument_is_radius_not_digits() -> None:
    """LANDMINE: arb(text, 60) is a radius of 60, not 60 decimal digits."""
    assert arb("1.616255", 60).rad() > arb(1)
    assert arb("1.616255").rad() < arb("1e-70")


def test_log2_e_is_live_at_locked_precision_not_frozen_at_import() -> None:
    """LANDMINE: a module-level log2(e) freezes at the 53-bit import default.

    The kernel runs at 256 bit, so every budget width inherited a 53-bit
    radius and the report printed those widths as 256-bit results. A function
    cannot freeze; this pins the live radius two orders of magnitude tighter
    than the frozen one.
    """
    from msaf.precision import log2_e

    live = log2_e()
    assert live.rad().abs_upper() < arb("1e-70")
    assert log2_e().mid() == live.mid()


def test_derivative_tail_matches_its_documented_identity() -> None:
    """LANDMINE: the tail multiplied the already-differentiated coefficients twice.

    Independent check, not a restatement: evaluate the derivative series at
    exact sample points inside the ball and require the reported enclosure to
    contain every value. A wrong tail (or a wrong radius) breaks containment.
    """
    centre = _first_zero_centre()
    radius = arb("1e-12")
    ball = zi.ball(centre, radius)
    enclosure, _tail = zi.xi_derivative_over_ball(ball)
    # The reference series MUST expand at the identical point the function
    # uses (ball.mid(), not the pre-union centre): union-mid differs from the
    # centre in the last bit, and at these radii that alone breaks containment.
    series = zi.xi_taylor(ball.mid()).derivative().coeffs()
    for offset in (arb(0), radius / 2, -radius / 2):
        value = acb(0)
        power = acb(1)
        for coefficient in series:
            value += coefficient * power
            power *= acb(offset)
        # Project rule (L19): native ball-vs-ball contains() is unreliable,
        # so containment is judged by the circular criterion, never by FLINT.
        assert zi._contains(value, enclosure), f"enclosure misses the series at offset {offset}"


def test_root_pull_outcome_carries_a_typed_incumbent() -> None:
    """LANDMINE FIXED: the outcome promised Fitness but delivered None."""
    from msaf.evolution import RootPullFitness, RootPullOutcome

    with tempfile.TemporaryDirectory() as tmp:
        outcome = evolve_root_pull(RootPullGenome(0, 1, 1), 12, 2, Path(tmp) / "p.jsonl")
    assert isinstance(outcome, RootPullOutcome)
    assert isinstance(outcome.incumbent_fitness, RootPullFitness)
    assert outcome.incumbent_fitness.accepted is True
    assert "accepted=True" in outcome.incumbent_fitness.render()


def test_arb_log_takes_no_base_argument() -> None:
    """LANDMINE: arb.log(base) and arb.exp(x) are unsupported in binding 0.9.0."""
    try:
        arb(2).log(2)
    except TypeError:
        pass
    else:  # pragma: no cover
        raise AssertionError("arb.log(base) is now supported; re-audit required")
    assert log2(arb(1024)).overlaps(arb(10))


def test_containment_direction_is_residual_contains_zero() -> None:
    """LANDMINE: a point ball can never contain a wider ball."""
    residual = arb("1e-30") - arb("1e-30")
    assert not arb(0).contains(residual)
    assert contains_zero(residual)
    assert not is_exact_zero(residual)


def test_precision_lock_rejects_silent_shift() -> None:
    with ball_precision(512):
        assert ctx.prec == 512
    assert ctx.prec == P
    try:
        set_precision(P + 8)
    except PrecisionLandmine:
        return
    raise AssertionError("precision lock failed")


# --------------------------------------------------------------------------
# Core lattice: shift operator
# --------------------------------------------------------------------------


def test_shift_operator_is_genuine_cyclic_matrix() -> None:
    t = lattice.generate_shift_operator(4)
    assert t.nrows() == 4 and t.ncols() == 4
    for i in range(4):
        for j in range(4):
            expected = 1 if (i == (j + 1) % 4) else 0
            assert is_exact_zero(t[i, j] - arb(expected))


def test_shift_unitarity_residual_is_exact_zero() -> None:
    audit = lattice.verify_unitarity(lattice.generate_shift_operator(8))
    assert audit.contains_zero
    assert audit.exact_zero_entries == audit.total_entries
    assert audit.max_half_width == arb(0)


def test_shift_apply_matches_dense_matrix() -> None:
    n = 6
    vector = [arb(i + 1) for i in range(n)]
    permuted = lattice.apply_cyclic_shift(vector)
    matrix = lattice.generate_shift_operator(n)
    dense = [sum(matrix[i, j] * vector[j] for j in range(n)) for i in range(n)]
    assert all(contains_zero(permuted[i] - dense[i]) for i in range(n))


def test_shift_apply_respects_periodicity() -> None:
    n = 5
    vector = [arb(i) for i in range(n)]
    assert lattice.apply_cyclic_shift(vector, steps=n) == vector


def test_shift_materialisation_ceiling_is_enforced() -> None:
    try:
        lattice.generate_shift_operator(1 << 20)
    except lattice.LatticeDimensionViolation:
        return
    raise AssertionError("materialisation ceiling not enforced")


# --------------------------------------------------------------------------
# Core lattice: quantized von Mangoldt
# --------------------------------------------------------------------------


def test_prime_power_classification() -> None:
    prime_powers = [k for k in range(1, 30) if lattice.is_prime_power(k)]
    assert prime_powers == [2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 17, 19, 23, 25, 27, 29]
    assert not lattice.is_prime_power(0)
    assert not lattice.is_prime_power(1)
    assert not lattice.is_prime_power(6)


def test_quantized_von_mangoldt_returns_exact_zero_off_prime_powers() -> None:
    for k in (6, 10, 12, 15, 21):
        value = lattice.quantized_von_mangoldt(k)
        assert value.is_exact()
        assert value.is_zero()


def test_quantized_von_mangoldt_returns_log_of_the_base_prime() -> None:
    for k in (2, 3, 5, 8, 27, 49):
        prime = {2: 2, 3: 3, 5: 5, 8: 2, 27: 3, 49: 7}[k]
        assert contains_zero(lattice.quantized_von_mangoldt(k) - arb(prime).log())


def test_manuscript_kernel_is_nan_on_non_prime_power_pixels() -> None:
    """LANDMINE: log(Lambda_d + delta) evaluates log(0) and returns NaN."""
    assert lattice.manuscript_log_kernel(6).is_nan()


def test_repaired_kernel_is_finite_on_every_pixel() -> None:
    for k in range(1, 64):
        value = lattice.von_mangoldt_log_kernel(k)
        assert value.is_finite()
        assert not value.is_nan()


# --------------------------------------------------------------------------
# Core lattice: commutation audit
# --------------------------------------------------------------------------


def _weil_symbol(n: int) -> CirculantHamiltonian:
    return CirculantHamiltonian.from_function(
        n, lambda j: arb(fmpq(2 * j, n)).cos_pi() + (1 if j == 0 else 0)
    )


def test_commutation_is_certified_but_not_exact_for_inexact_symbols() -> None:
    n = 8
    audit = lattice.verify_commutation(_weil_symbol(n).to_matrix(), lattice.generate_shift_operator(n))
    assert audit.contains_zero
    assert audit.exact_zero_entries < audit.total_entries
    assert audit.max_half_width > arb(0)


def test_commutation_on_a_non_circulant_matrix_is_reported_as_failure() -> None:
    n = 4
    h = arb_mat(n, n)
    for i in range(n):
        for j in range(n):
            h[i, j] = arb(1) if (i, j) == (0, 1) else arb(0)
    audit = lattice.verify_commutation(h, lattice.generate_shift_operator(n))
    assert not audit.contains_zero
    assert audit.verdict.startswith("FAIL")


def test_circulant_commutation_is_downgraded_to_trivial() -> None:
    """LANDMINE: [H,T]=0 holds for every circulant H and proves nothing."""
    n = 8
    audit = lattice.verify_commutation(_weil_symbol(n).to_matrix(), lattice.generate_shift_operator(n))
    assert audit.structurally_guaranteed
    assert not audit.carries_information
    assert audit.verdict.startswith("TRIVIAL")


def test_truncation_bound_is_strictly_positive_and_representable() -> None:
    """MEASURED: l_P * exp(-N_steps) keeps a positive lower endpoint in Arb.

    The Arb exponent is arbitrary precision, so a quantity around 1e-23645968437
    stays fully representable with roughly 21 bits of relative accuracy. A
    float64 underflows to zero on the same quantity, which is exactly how a
    clean-looking zero can appear without any mathematics supporting it.
    """
    exponent = -(lattice.ELL_P.mid().log() + arb("5.444685443298158e61"))
    bound = lattice.ELL_P * exponent.exp()
    assert bound.lower() > 0
    assert not bound.is_zero()
    relative_radius = bound.rad() / bound.mid()
    assert relative_radius < arb("1e-6")
    audit = lattice.verify_truncation(bound, positive_evidence=exponent)
    assert audit.verdict.startswith("NOT-ZERO")
    assert not audit.is_identically_zero
    assert not audit.underdetermined


def test_float64_underflows_where_arb_does_not() -> None:
    """LANDMINE: binary64 saturates to 0.0 on the very same exponent."""
    assert math.exp(-5.444685443298158e61) == 0.0
    exponent = -(lattice.ELL_P.mid().log() + arb("5.444685443298158e61"))
    assert not (lattice.ELL_P * exponent.exp()).is_zero()


def test_truncation_audit_reports_underdetermined_enclosures() -> None:
    """A ball that contains zero without being zero certifies neither outcome."""
    undetermined = arb(0).union(arb("1e30"))
    audit = lattice.verify_truncation(undetermined)
    assert audit.underdetermined
    assert audit.contains_zero
    assert not audit.is_identically_zero
    assert audit.verdict.startswith("UNDERDETERMINED")


def test_positive_evidence_overrules_an_underdetermined_enclosure() -> None:
    """The logarithm stays representable even when the value degenerates."""
    undetermined = arb(0).union(arb("1e30"))
    audit = lattice.verify_truncation(undetermined, positive_evidence=arb("5"))
    assert audit.underdetermined
    assert audit.verdict.startswith("NOT-ZERO (external evidence)")


def test_truncation_audit_refuses_to_certify_an_imposed_zero() -> None:
    """LANDMINE: a strictly positive bound must never be certified as vanishing."""
    audit = lattice.verify_truncation(arb("1e-30"))
    assert not audit.is_identically_zero
    assert not audit.contains_zero
    assert audit.verdict.startswith("NOT-ZERO")
    assert not audit.underdetermined


def test_truncation_audit_accepts_a_genuine_identical_zero() -> None:
    audit = lattice.verify_truncation(arb(0))
    assert audit.is_identically_zero
    assert audit.verdict.startswith("IDENTICAL-ZERO")


def test_truncation_audit_accepts_a_genuine_identical_zero() -> None:
    audit = lattice.verify_truncation(arb(0))
    assert audit.is_identically_zero
    assert audit.verdict.startswith("IDENTICAL-ZERO")


# --------------------------------------------------------------------------
# Kernel landmines carried over from the original audit
# --------------------------------------------------------------------------


def test_commutator_residual_is_certified_but_not_exact() -> None:
    cert = commutator_residual(_weil_symbol(8), CyclicShift(8))
    assert cert.certified
    assert not cert.exact


def test_internal_shift_unitarity_is_exact() -> None:
    n = 8
    t = CyclicShift(n).to_matrix()
    unitarity = t.transpose() * t - identity(n)
    assert all(is_exact_zero(unitarity[i, j]) for i in range(n) for j in range(n))
    assert contains_zero_matrix(t**n - identity(n))


def test_internal_materialisation_cap_is_enforced() -> None:
    try:
        CyclicShift(1 << 20).to_matrix()
    except MatrixDimensionViolation:
        return
    raise AssertionError("materialisation cap not enforced")


def test_weil_matrix_smallest_magnitude_is_unit() -> None:
    profile = spectral_profile(16)
    assert contains_zero(profile.min_magnitude - arb(1))
    assert point(profile.min_magnitude, 8).startswith("1.0000000")


def test_weil_first_column_structure() -> None:
    w = weil_matrix(8)
    assert all(contains_zero(w[i, 0] - (0 if i == 0 else 1)) for i in range(8))


def test_measured_entropy_matches_closed_form() -> None:
    n = arb(1024)
    assert contains_zero(measured_entropy(n) - (arb("0.5") + log2(2 * (n - 1)) / 2))


def test_manuscript_critical_dimension_matches_the_manuscript() -> None:
    value = manuscript_critical_dimension().value
    assert arb("1.7e31") < value < arb("1.9e31")


def test_measured_critical_dimension_is_far_larger() -> None:
    assert measured_critical_dimension().value > arb("1e60")
    assert measured_critical_dimension().value > manuscript_critical_dimension().value


def test_mantissa_budget_and_underflow_dimension() -> None:
    assert point(mantissa_bits(arb(100)), 6).startswith("16.591")
    assert point(mantissa_bits(arb(800)), 6).startswith("132.728")
    assert arb(1181) < underflow_dimension() < arb(1182)
    assert point(lambda_min_estimate(arb(1181)), 5).startswith("1.0382e-59")


def test_decimal_parser_handles_scientific_notation() -> None:
    assert fmpq(decimal_to_fmpq("8.8e26")) == fmpq(88, 1) * fmpq(10) ** 25
    numerator, denominator = n_steps_exact_rational_parts()
    assert isinstance(numerator, int) and isinstance(denominator, int)
    assert numerator // denominator == int(n_steps_floor())


def test_n_steps_is_never_integer() -> None:
    numerator, denominator = n_steps_exact_rational_parts()
    assert numerator % denominator != 0


# --------------------------------------------------------------------------
# Evolution, mutation and ledger
# --------------------------------------------------------------------------


def test_fitness_is_measured_not_asserted() -> None:
    fitness = measure_fitness(Genome(0, 1, "1"), 8)
    assert fitness.certificate_passed
    assert fitness.certificate_bits > arb(0)
    assert contains_zero(
        fitness.total - (fitness.certificate_bits + fitness.spectral_agreement_bits)
    )


def test_mutation_is_deterministic() -> None:
    seed = Genome(0, 1, "1")
    assert mutate(seed, 3) == mutate(seed, 3)
    assert mutate(seed, 3) != mutate(seed, 4)


def test_campaign_promotes_only_non_regressing_genomes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        outcome = evolve_lattice(Genome(0, 11, "0.5"), 8, 6, path)
        totals = [arb(r.fitness_total) for r in outcome.ledger.records]
        best = arb(0)
        for record, total in zip(outcome.ledger.records, totals):
            if record.decision == "PROMOTE":
                assert total >= best
                best = max(best, total)
            else:
                assert not contains_zero(total - best) or total < best


def test_ledger_chain_is_intact_and_reproducible() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        evolve_lattice(Genome(0, 11, "0.5"), 8, 5, path)
        reloaded = Ledger(path).load()
        assert reloaded.verify_chain() == (True, -1)
        assert replay(reloaded, 8) == (True, -1)


def test_tampering_with_the_ledger_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        evolve_lattice(Genome(0, 11, "0.5"), 8, 4, path)
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        record = json.loads(lines[-1])
        record["fitness_total"] = "999999999999"
        lines[-1] = json.dumps(record, sort_keys=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        assert Ledger(path).load().verify_chain()[0] is False


def test_replay_detects_a_fabricated_fitness() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        evolve_lattice(Genome(0, 11, "0.5"), 8, 4, path)
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        record = json.loads(lines[1])
        record["fitness_total"] = "1"
        record["record_hash"] = Ledger(path).load().records[1].record_hash
        lines[1] = json.dumps(record, sort_keys=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        assert replay(Ledger(path).load(), 8)[0] is False


def test_non_finite_measurements_are_refused() -> None:
    ledger = Ledger(Path(tempfile.gettempdir()) / "msaf_refused_ledger.jsonl")
    bad = measure_fitness(Genome(0, 1, "1"), 8)
    broken = bad._replace(total=arb("nan"))
    try:
        ledger.append(Genome(0, 1, "1"), broken, "PROMOTE")
    except NonFiniteMeasurement:
        return
    raise AssertionError("non-finite measurement was written to the ledger")


# --------------------------------------------------------------------------
# Constructor landmines, and the rigorous zeta inversion kernel
# --------------------------------------------------------------------------

IMAGINARY_UNIT = acb(0, 1)
GAMMA_1 = "14.1347251417346937904572519835624702707842571156992431756856"


def _first_zero_centre() -> acb:
    return acb("0.5") + IMAGINARY_UNIT * acb(GAMMA_1)


def test_arb_and_acb_second_arguments_mean_different_things() -> None:
    """LANDMINE: arb(mid, rad) is a ball, acb(real, imag) is a complex number."""
    assert arb(1, 60).rad() > arb(1)
    assert acb("0.5", 0.25) == acb("0.5") + IMAGINARY_UNIT * acb("0.25")
    # acb("0.5", 1e-18) is the point 0.5 + 1e-18 i, NOT a ball of radius 1e-18
    assert acb("0.5", 1e-18).real == acb("0.5").real
    assert contains_zero(acb("0.5", 1e-18).imag - acb(1e-18).real)


def test_python_floats_bake_binary64_rounding_into_balls() -> None:
    """LANDMINE: pass decimal strings; a float literal is not the decimal you typed."""
    from_float = acb(1e-18)
    from_string = acb("1e-18")
    assert from_float.real.mid() != from_string.real.mid()
    assert not contains_zero(from_float.real - from_string.real)


def test_ball_helper_builds_a_real_enclosure() -> None:
    centre = _first_zero_centre()
    enclosure = zi.ball(centre, 1e-18)
    assert enclosure.contains(centre)
    assert enclosure.complex_rad().abs_lower() >= arb("1e-18")


def test_series_path_refuses_points_outside_its_certified_strip() -> None:
    try:
        zi.xi_taylor(acb("1.5") + IMAGINARY_UNIT * acb(GAMMA_1))
    except ValueError:
        return
    raise AssertionError("series domain guard did not fire")


def test_xi_at_the_first_zero_is_small_and_almost_real() -> None:
    """A correct xi implementation must not impose a zero.

    Evaluating at a decimal literal for gamma_1 cannot return an exact zero:
    the literal carries only about 77 digits, so xi legitimately evaluates to a
    small NON-zero enclosure. A blueprint that returned 0 here would be
    fabricating a root rather than measuring one.
    """
    value = zi.evaluate_xi(_first_zero_centre())
    assert not value.is_zero()
    assert value.abs_upper() < arb("1e-40")
    assert contains_zero(value.imag)


def test_xi_is_regular_at_zero_and_one() -> None:
    """LANDMINE FIXED: the blueprint returned 0 at s = 0 and s = 1; xi = 1/2 there."""
    for point in (acb(0), acb(1)):
        value = zi.evaluate_xi(point)
        assert contains_zero_complex(value - acb("0.5"))
        assert not value.is_zero()


def test_derivative_enclosure_brackets_the_true_derivative() -> None:
    enclosure, tail = zi.xi_derivative_over_ball(zi.ball(_first_zero_centre(), 1e-18))
    assert not contains_zero(enclosure)
    assert tail.abs_upper() < arb("1e-16")
    refinement, tighter_tail = zi.xi_derivative_over_ball(
        zi.ball(_first_zero_centre(), 1e-40)
    )
    assert tighter_tail.abs_upper() < tail.abs_upper()
    assert refinement.abs_upper() > arb("1e-3")


def test_zero_exclusion_is_certified_away_from_zeros() -> None:
    assert zi.certify_zero_exclusion(zi.ball(acb("0.5") + IMAGINARY_UNIT * acb("30.5"), 1e-6))
    assert not zi.certify_zero_exclusion(zi.ball(_first_zero_centre(), 1e-6))


def test_localisation_certifies_a_zero_and_nothing_more() -> None:
    result = zi.locate_zero(zi.ball(_first_zero_centre(), 1e-12), max_iter=12)
    assert result.verdict.startswith("ZERO-LOCALIZED")
    assert result.derivative_excludes_zero
    assert contains_zero(result.offset_from_half)
    assert not result.global_claim_supported
    assert "cannot establish the universal statement" in result.claim_note


def test_localisation_matches_the_flint_reference_imaginary_part() -> None:
    """Cross-validation: two independent implementations must agree on gamma."""
    result = zi.locate_zero(zi.ball(_first_zero_centre(), 1e-12), max_iter=12)
    reference = acb.zeta_zero(1)
    separation = (result.final_ball.imag - reference.imag).abs_upper()
    assert separation < arb("1e-40")


def test_certify_sigma_one_half_never_claims_a_global_result() -> None:
    report = zi.certify_sigma_one_half(zi.ball(_first_zero_centre(), 1e-12), max_iter=12)
    assert report["global_claim_supported"] is False
    assert report["sigma_is_on_half_line"] is True
    assert report["verdict"].startswith("ZERO-LOCALIZED")


def test_root_pull_promotes_only_certified_zeros() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "pull.jsonl"
        outcome = evolve_root_pull(RootPullGenome(0, 1, 1), 12, 3, path)
        assert len(outcome.promoted) == 3
        assert all(r.decision == "PROMOTE" for r in outcome.ledger.records[1:])
        assert outcome.ledger.verify_chain()[0] is True


def test_root_pull_serialises_radius_without_binary64_rounding() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "pull.jsonl"
        evolve_root_pull(RootPullGenome(0, 1, 1), 12, 1, path)
        first = json.loads(path.read_text(encoding="utf-8").strip().splitlines()[0])
        assert isinstance(first["fitness_total"], str)
        assert arb(first["fitness_total"]) > arb(0)


# --------------------------------------------------------------------------
# Phase 2/3: rigid visualizer, final audit, ledger replay CLI
# --------------------------------------------------------------------------


def test_pixel_projection_is_pure_integer_arithmetic() -> None:
    from flint import fmpz

    from msaf.visualizer import project_gamma_to_pixel

    projection = project_gamma_to_pixel(acb.zeta_zero(1).imag)
    assert projection.unambiguous
    assert isinstance(projection.pixel, fmpz)
    assert 0 <= projection.pixel < projection.modulus


def test_pixel_projection_rejects_ambiguous_enclosures() -> None:
    from msaf.visualizer import AmbiguousPixel, project_gamma_to_pixel

    wide = arb("460.5").union(arb("461.5"))
    assert wide.lower().floor().fmpz() != wide.upper().floor().fmpz()
    try:
        project_gamma_to_pixel(wide)
    except AmbiguousPixel:
        return
    raise AssertionError("ambiguous pixel was silently resolved")


def test_density_report_round_trips_through_json() -> None:
    import json as _json

    from msaf.visualizer import build_density_report, collect_first_zeros

    gammas, verdicts = collect_first_zeros(2)
    report = build_density_report(gammas, verdicts, 16)
    with tempfile.TemporaryDirectory() as tmp:
        from msaf.visualizer import write_json_report

        path = write_json_report(report, Path(tmp) / "density.json")
        loaded = _json.loads(Path(path).read_text(encoding="utf-8"))
    assert loaded["total"] == 2
    assert all(isinstance(p, str) for p in loaded["pixels"])
    assert loaded["locked"] == 2
    assert len(loaded["gamma_radii"]) == 2
    assert all(isinstance(g, str) for g in loaded["gamma_radii"])


def test_holographic_capacity_uses_arb_not_float() -> None:
    from msaf.final_audit import holographic_capacity_check

    verdict = holographic_capacity_check(16)
    assert verdict.verdict == "SAFE-COMPUTATION"
    assert verdict.manuscript_safe and verdict.measured_safe
    doomed = holographic_capacity_check(10**62)
    assert doomed.verdict == "HOLOGRAPHIC-OVERFLOW-COLLAPSE"


def test_capacity_paths_can_disagree_and_say_so() -> None:
    from msaf.final_audit import holographic_capacity_check

    found = None
    for dim in (10**30, 10**32, 10**40, 10**50, 10**55):
        verdict = holographic_capacity_check(dim)
        if verdict.verdict.startswith("PATH-DISAGREEMENT"):
            found = dim
            break
    assert found is not None, "expected a dimension where the two paths disagree"


def test_replay_handles_root_pull_ledgers() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "pull.jsonl"
        evolve_root_pull(RootPullGenome(0, 1, 1), 12, 2, path)
        assert replay(Ledger(path).load(), 12) == (True, -1)


def test_replay_cli_rebuilds_states_from_scratch() -> None:
    import io
    from contextlib import redirect_stdout

    from msaf.evolution import main as replay_main

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        evolve_lattice(Genome(0, 11, "0.5"), 8, 3, path)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = replay_main(["--replay", str(path), "--dimension", "8"])
        assert code == 0
        assert "V(L)                = True" in buffer.getvalue()


def test_replay_cli_defines_all_names_before_main_runs() -> None:
    """LANDMINE: a mid-file `if __name__ == '__main__'` executes before later definitions.

    `replay()` dispatched to `RootPullGenome`, which was defined AFTER the
    guard, so `python -m msaf.evolution --replay` on a root-pull ledger died
    with NameError while every in-process test passed. The guard must be the
    last statement of the module. This test runs the real CLI entry point.
    """
    import subprocess

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "pull.jsonl"
        evolve_root_pull(RootPullGenome(0, 1, 1), 12, 1, path)
        completed = subprocess.run(
            [sys.executable, "-m", "msaf.evolution", "--replay", str(path),
             "--dimension", "12"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )
    assert completed.returncode == 0, completed.stderr
    assert "V(L)                = True" in completed.stdout


def test_replay_cli_refuses_precision_mismatch() -> None:
    """A replay at the wrong precision must fail loudly, never pass silently."""
    import subprocess

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        evolve_lattice(Genome(0, 11, "0.5"), 8, 2, path)
        completed = subprocess.run(
            [sys.executable, "-m", "msaf.evolution", "--replay", str(path),
             "--dimension", "8", "--prec", "128"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )
    assert completed.returncode == 1
    assert "V(L)                = False" in completed.stdout


# --------------------------------------------------------------------------
# Dirichlet campaign: primitive characters and Hardy Z bracketing
# --------------------------------------------------------------------------


def test_chi_4_classification_is_primitive_odd_real() -> None:
    from msaf.dirichlet import describe

    spec = describe(4, 3)
    assert (spec.conductor, spec.primitive, spec.parity, spec.order) == (4, True, 1, 2)
    assert spec.is_real


def test_isolation_refuses_complex_characters() -> None:
    from msaf.dirichlet import describe, isolate_sign_changes

    try:
        isolate_sign_changes(describe(5, 2), "5", "7", "0.1")
    except ValueError:
        return
    raise AssertionError("sign isolation ran on a complex-valued Z")


def test_chi_4_first_bracket_is_certified_and_tight() -> None:
    from msaf.dirichlet import describe, isolate_sign_changes, strict_sign, hardy_enclosure

    spec = describe(4, 3)
    brackets = isolate_sign_changes(spec, "5.5", "7.0", "0.1")
    assert brackets, "no bracket found where the zero is known to be"
    first = brackets[0]
    assert first.width() <= arb("0.1") + arb("1e-30")
    assert strict_sign(hardy_enclosure(spec, first.lower)) == 1
    assert strict_sign(hardy_enclosure(spec, first.upper)) == -1
    assert first.lower.upper() < arb("6.021") and first.upper.lower() > arb("6.020")


def test_undetermined_sign_contributes_no_claim() -> None:
    from msaf.dirichlet import strict_sign

    assert strict_sign(acb("0 +/- 1")) == 0
    # A narrow imaginary enclosure around zero does not veto a strict real
    # sign; Z of a real character at a real ordinate is exactly real anyway.
    assert strict_sign(acb("1 +/- 0.001") + acb(0, 1) * acb("0 +/- 0.001")) == 1
    assert strict_sign(acb("2 +/- 0.001")) == 1
    assert strict_sign(acb("-2 +/- 0.001")) == -1


def test_final_audit_seals_only_fully_safe_campaigns() -> None:
    from msaf.final_audit import run_final_audit

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        evolve_lattice(Genome(0, 11, "0.5"), 8, 3, path)
        seal = run_final_audit([path], [16], 8)
        assert seal.sealed is True
        for verdict in seal.ledgers:
            assert verdict.identity_holds


def test_readme_equation_assets_resolve() -> None:
    """Every docs/math image referenced by the README must exist on disk.

    GitHub renders no LaTeX; a dangling img src degrades silently into an
    empty box in front of every auditor. This pins the README-to-asset link.
    """
    import re

    root = Path(__file__).resolve().parent.parent.parent
    readme = (root / "README.md").read_text(encoding="utf-8")
    refs = re.findall(r"docs/math/([a-z_]+\.svg)", readme)
    assert refs, "README references no equation assets"
    for ref in refs:
        target = root / "docs" / "math" / ref
        assert target.exists(), f"missing equation asset: {ref}"
        assert target.stat().st_size > 1000, f"suspiciously small asset: {ref}"


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