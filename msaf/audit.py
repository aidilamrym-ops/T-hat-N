"""MSAF audit report. Single execution entry point.

The precision-setting order here is unique and deterministic: environment
check, precision lock, and only then the numeric imports that depend on it.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from .precision import (
    DEFAULT_PRECISION_BITS,
    audit_precision_landmines,
    require_pure_precision_environment,
    set_precision,
)

DIGITS = 40


def _block(title: str, lines: list[str]) -> str:
    return "\n".join([title, "-" * len(title), *lines, ""])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="msaf", description="MSAF audit under rigid ball arithmetic"
    )
    parser.add_argument("--prec", type=int, default=DEFAULT_PRECISION_BITS)
    parser.add_argument("--skip-env-check", action="store_true")
    parser.add_argument("--regression-n", type=int, default=16)
    parser.add_argument("--evolve", type=int, default=0, help="proposals for the evolution campaign")
    parser.add_argument("--root-pull", type=int, default=0, help="proposals for the root-pull campaign")
    parser.add_argument("--skip-zeta", action="store_true")
    parser.add_argument("--ledger", type=Path, default=Path("ledger/msaf_ledger.jsonl"),
                        help="workspace-local evolution ledger (never in Temp)")
    parser.add_argument("--visualize", type=int, default=0,
                        help="localise N zeros and write the rigid pixel report")
    parser.add_argument("--report-dir", type=Path, default=Path("reports"),
                        help="workspace-local report directory")
    parser.add_argument("--final-audit", action="store_true",
                        help="replay every ledger and check holographic capacity")
    parser.add_argument("--capacity-dims", type=int, nargs="*", default=[16, 400, 800])
    args = parser.parse_args(argv)

    if not args.skip_env_check:
        require_pure_precision_environment()
    set_precision(args.prec)

    # Anchor relative artifact paths to the workspace root (the directory
    # holding this file's parent), never to the caller's working directory.
    # A report invoked from any other CWD previously scattered ledgers across
    # the filesystem with no error and no warning.
    workspace = Path(__file__).resolve().parent.parent
    if not args.ledger.is_absolute():
        args.ledger = workspace / args.ledger
    if not args.report_dir.is_absolute():
        args.report_dir = workspace / args.report_dir

    from flint import acb, arb, fmpq

    import msaf_core_lattice as core

    from .budget import (
        lambda_min_estimate,
        manuscript_critical_dimension,
        mantissa_bits,
        measured_critical_dimension,
        underflow_dimension,
    )
    from .certify import certify_matrix, report
    from .constants import D_OBS, ELL_P, N_STEPS
    from .format import fmt, point, relwidth
    from .grid import SPEC
    from .guinand import spectral_profile
    from .operators import (
        CirculantHamiltonian,
        CyclicShift,
        commutator_residual,
        identity,
        structural_commutation,
    )

    n = args.regression_n
    blocks: list[str] = []
    tail_exponent = -(ELL_P.mid().log() + arb("5.444685443298158e61"))
    tail = ELL_P * tail_exponent.exp()
    tail_audit = core.verify_truncation(tail, positive_evidence=tail_exponent)

    zeta_rows: list[str] = []
    if not args.skip_zeta:
        from .zeta_inversion import ball, certify_sigma_one_half, certify_zero_exclusion

        known_gammas = (
            "14.1347251417346937904572519835624702707842571156992431756856",
            "21.02203963877155499262847859365322868355831014555688873653706",
            "25.01085758014568876323819580351344750643689903657150740114664",
        )
        imaginary_unit = acb(0, 1)
        for k, gamma in enumerate(known_gammas, start=1):
            centre = acb("0.5") + imaginary_unit * acb(gamma)
            zeta_report = certify_sigma_one_half(ball(centre, "1e-12"), max_iter=12)
            reference = acb.zeta_zero(k)
            zeta_rows.append(
                f"rho_{k}: verdict={zeta_report['verdict']}, "
                f"on_half={zeta_report['sigma_is_on_half_line']}, "
                f"Re radius={zeta_report['final_radius_real']}, "
                f"gamma separation from FLINT reference = "
                f"{point(reference.imag - acb(gamma).real, 6)}"
            )
        excluded = certify_zero_exclusion(ball(acb("0.5") + imaginary_unit * acb("30.5"), "1e-6"))
        zeta_rows.append("")
        zeta_rows.append(f"zero excluded near t = 30.5 : {excluded}")
        zeta_rows.append(f"global claim supported      : False (always)")

    blocks.append(
        _block(
            "0. PRECISION KERNEL",
            [
                f"python            = {sys.version.split()[0]}",
                "python-flint      = 0.9.0",
                f"arb precision     = {args.prec} bit",
                f"global mutators   = {audit_precision_landmines() or 'none'}",
            ],
        )
    )

    blocks.append(
        _block(
            "1. INFORMATION GRID",
            [
                f"l_P               = {point(ELL_P)} m",
                f"D_obs             = {point(D_OBS)} m",
                f"N_steps           = {point(N_STEPS)}",
                f"N_steps integer?  = {SPEC.is_integer}",
                f"floor(N_steps)    = {SPEC.n_floor}",
                f"log2(N_steps)     = {SPEC.bit_length} bit",
                f"storage minimum   = {SPEC.storage_bytes} byte",
                f"relative error    = {relwidth(N_STEPS)}",
                f"ball N_steps      = {fmt(N_STEPS, 3)}",
            ],
        )
    )

    shift = CyclicShift(n)
    symbol = CirculantHamiltonian.from_function(
        n, lambda j: arb(fmpq(2 * j, n)).cos_pi() + (1 if j == 0 else 0)
    )
    shift_matrix = shift.to_matrix()
    hamiltonian = symbol.to_matrix()
    certs = [
        commutator_residual(symbol, shift),
        certify_matrix(
            f"T^dag T - I  (n={n})", shift_matrix.transpose() * shift_matrix - identity(n)
        ),
        certify_matrix(f"H^dag - H     (n={n})", hamiltonian.transpose() - hamiltonian),
        certify_matrix(f"T^n - I       (n={n})", shift_matrix**n - identity(n)),
    ]
    blocks.append(_block(f"2. OPERATOR CERTIFICATES (n={n})", [report(certs).render()]))
    blocks.append(_block("   THEORETICAL NOTE", [structural_commutation()]))

    profile = spectral_profile(n)
    blocks.append(
        _block(
            "3. GUINAND-WEIL SPECTRUM",
            [
                f"n                     = {n}",
                f"min |lambda|          = {fmt(profile.min_magnitude)}",
                f"H_spectral            = {fmt(profile.entropy_bits)} bit",
                "",
                "Structural form: the first column of W is [0, 1, ..., 1], so its",
                "DFT is exactly (n-1) at k = 0 and -1 at k > 0. Hence min |lambda| = 1",
                "and there is NO exponential decay in this matrix family.",
            ],
        )
    )

    budget_rows = []
    for m in (100, 400, 800, 1181):
        mn = arb(m)
        budget_rows.append(
            f"n = {m:<5} b = {fmt(mantissa_bits(mn), 20)} bit   "
            f"lambda_min ~ {fmt(lambda_min_estimate(mn), 12)}"
        )
    blocks.append(_block("4. PRECISION BUDGET (under A e^(-B n))", budget_rows))

    blocks.append(
        _block(
            "5. CRITICAL DIMENSION",
            [
                manuscript_critical_dimension().render(),
                measured_critical_dimension().render(),
                "",
                "The two values differ because of the assumption H := n versus the",
                "measured entropy H := 0.5 + 0.5 log2(2(n-1)), not because of any",
                "numerical error.",
            ],
        )
    )

    blocks.append(
        _block(
            "6. UNDERFLOW THRESHOLD",
            [
                "The assumption lambda_min ~ e^(-B n) reaches 1e-59 at",
                f"n = {fmt(underflow_dimension(), 20)}",
                "The measured Guinand-Weil matrices show no decay at all.",
            ],
        )
    )

    blocks.append(
        _block(
            "7. CORE LATTICE (von Mangoldt kernel)",
            [
                "pixel k=6, not a prime power:",
                f"  manuscript kernel log(Lambda_d + delta) -> {core.manuscript_log_kernel(6)}",
                f"  repaired kernel  log(1 + Lambda_d)      -> {core.von_mangoldt_log_kernel(6)}",
                "",
                "pixel k=8 = 2^3, a prime power:",
                f"  Lambda_d(8)                                = {core.quantized_von_mangoldt(8).mid().str(12, radius=False)}",
                "",
                "truncation residual l_P * exp(-N_steps):",
                f"  lower endpoint positive    = {tail.lower() > 0}",
                f"  relative radius            = {point(tail.rad() / tail.mid(), 6)}",
                f"  binary64 on the same input = {math.exp(-5.444685443298158e61)}",
                f"  audit verdict              = {tail_audit.verdict}",
            ],
        )
    )

    blocks.append(
        _block(
            "8. RIGOROUS ZETA INVERSION (interval Newton on xi)",
            [
                *zeta_rows,
            ],
        )
    )

    if args.root_pull > 0:
        from .evolution import RootPullGenome, evolve_root_pull

        pull = evolve_root_pull(
            RootPullGenome(0, 1, 1), n, args.root_pull, args.ledger.with_name("rootpull.jsonl")
        )
        decisions = [f"{r.decision}({r.tilt})" for r in pull.ledger.records]
        intact, first_bad = pull.ledger.verify_chain()
        blocks.append(
            _block(
                "9. ROOT-PULL CAMPAIGN",
                [
                    f"proposals          = {args.root_pull}",
                    f"promoted           = {len(pull.promoted)}",
                    f"reverted           = {len(pull.rejected)}",
                    f"decisions          = {', '.join(decisions)}",
                    f"incumbent          = {pull.incumbent_genome}",
                    f"incumbent fitness  = {pull.incumbent_fitness.render()}",
                    f"hash chain intact  = {intact} (first bad index {first_bad})",
                ],
            )
        )

    if args.evolve > 0:
        from .evolution import Genome, evolve_lattice, replay

        outcome = evolve_lattice(Genome(0, 11, "0.5"), n, args.evolve, args.ledger)
        intact, first_bad = outcome.ledger.verify_chain()
        reproduced, bad_index = replay(outcome.ledger, n)
        blocks.append(
            _block(
                "10. EVOLUTION CAMPAIGN",
                [
                    f"proposals          = {args.evolve}",
                    f"promoted           = {len(outcome.promoted)}",
                    f"rejected           = {len(outcome.rejected)}",
                    f"incumbent          = {outcome.incumbent_genome}",
                    f"incumbent fitness  = {outcome.incumbent_fitness.render()}",
                    f"hash chain intact  = {intact} (first bad index {first_bad})",
                    f"ledger reproduced  = {reproduced} (first bad index {bad_index})",
                    f"ledger path        = {args.ledger}",
                ],
            )
        )

    if args.visualize > 0:
        from .visualizer import (
            build_density_report,
            collect_first_zeros,
            render_png,
            write_json_report,
        )

        gammas, verdicts = collect_first_zeros(args.visualize)
        density = build_density_report(gammas, verdicts, n)
        json_path = write_json_report(density, args.report_dir / "spectral_density.json")
        png_path = render_png(density, args.report_dir / "spectral_density.png")
        blocks.append(
            _block(
                "11. DISCRETE SPECTRAL MAP (rigid pixel projection)",
                [
                    f"zeros localised    = {len(gammas)}",
                    f"locked             = {density.locked_count()}/{len(gammas)}",
                    f"pixels             = {', '.join(str(p.pixel)[:24] + '..' for p in density.projections)}",
                    f"json report        = {json_path}",
                    f"png rendering      = {png_path}",
                    "projection is pure Arb/integer; only certified integers reach the plotter",
                ],
            )
        )

    if args.final_audit:
        from .final_audit import run_final_audit

        ledgers = [args.ledger]
        sibling = args.ledger.with_name("rootpull.jsonl")
        if sibling.exists():
            ledgers.append(sibling)
        seal = run_final_audit(ledgers, args.capacity_dims, n)
        blocks.append(_block("12. FINAL AUDIT (ledger replay + capacity)", [seal.render()]))

    sys.stdout.write("\n".join(blocks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())