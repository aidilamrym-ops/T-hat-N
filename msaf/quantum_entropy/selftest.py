"""Standalone selftest for the Campaign V2 quantum-entropy sub-kernel.

Asserts machinery invariants (K-Q1..K-Q7, L39/L41/L42, D1/D7) with a mini
campaign at dims {8, 9, 10}; it never asserts the campaign verdict itself
(the entropy stream is non-deterministic by design).

Exit code 0 iff zero failure. D7: standalone; no pytest dependency.
"""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

__all__ = ["CHECKS", "main", "run_all"]

CHECKS = []


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn

    return deco


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _exact_det(lam: Fraction, diag: list, off2: list) -> Fraction:
    pp2, pp1 = Fraction(0), Fraction(1)
    for i, d in enumerate(diag):
        t = (lam - d) * pp1
        if i:
            t = t - off2[i - 1] * pp2
        pp2, pp1 = pp1, t
    return pp1


def _exact_det_d(lam: Fraction, diag: list, off2: list) -> Fraction:
    pp2, pp1 = Fraction(0), Fraction(1)
    qp2, qp1 = Fraction(0), Fraction(0)
    for i, d in enumerate(diag):
        b2 = off2[i - 1] if i else Fraction(0)
        q = (lam - d) * qp1 + pp1 - b2 * qp2
        t = (lam - d) * pp1 - b2 * pp2
        pp2, pp1 = pp1, t
        qp2, qp1 = qp1, q
    return qp1


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------


@check("K-Q1: --seed refused with exit code 2 (both forms); absent from parser")
def _t_seed():
    import contextlib
    import io

    from .entropy_source import refuse_seed
    from .runner import _build_parser

    sink = io.StringIO()
    for argv in (["--seed", "1"], ["--seed=1"], ["--outdir", "x", "--seed", "0"]):
        try:
            with contextlib.redirect_stderr(sink):
                refuse_seed(argv)
        except SystemExit as e:
            assert e.code == 2, e.code
        else:
            raise AssertionError("accepted %r" % (argv,))
    assert "SEED REFUSED" in sink.getvalue(), "loud refusal message missing"
    parser = _build_parser()
    opts = [o for a in parser._actions for o in getattr(a, "option_strings", [])]
    assert not any(o == "--seed" or o.startswith("--seed=") for o in opts)


@check("D1/K-Q7: SIMULATED label on module root and entropy descriptor")
def _t_labels():
    from . import SIMULATED_LABEL, global_claim_supported
    from .entropy_source import BLOCK_BYTES, EntropySource

    assert SIMULATED_LABEL == "SIMULATED"
    assert global_claim_supported is False
    assert BLOCK_BYTES == 512
    d = EntropySource().descriptor()
    assert d["label"] == "SIMULATED"
    assert d["block_bits"] == 4096
    assert "NOT a physical quantum measurement" in d["note"]


@check("frozen campaign parameters match the preregistration")
def _t_params():
    from . import chispec, runner as R

    assert R.DIMS == (201, 301, 401)
    assert R.SAMPLES_PER_DIM == 20000 and R.BATCH_SIZE == 500
    assert R.BISECTION_STEPS == 150
    assert R.ENVELOPE == Fraction(1, 250)
    assert R.NOISE_BASE == Fraction(5, 10000)
    assert R.ENVELOPE_FACTOR == 4
    assert R.WIDTH_FLOOR_REL == Fraction(2, 100)
    assert R.NEWTON_ITERS == 60 and R.NEWTON_TARGET == Fraction(1, 10**25)
    assert R.CHI2_MAX == Fraction(60)
    assert R.WALL_CAP_MIN == 30.0
    assert chispec.BINS == 16 and chispec.EXPECTED_FLOOR_MIN == 5
    assert chispec.Z_STAR == "3.5"


@check("L39 intervals: widen / relative width / exact decimal parse")
def _t_intervals():
    from .intervals import parse_decimal, relative_width, widen

    assert parse_decimal("1.5") == Fraction(3, 2)
    assert parse_decimal("-0.5") == Fraction(-1, 2)
    assert parse_decimal("1e-3") == Fraction(1, 1000)
    lo, hi = widen(Fraction(1, 2), Fraction(3, 2), Fraction(4, 1000))
    assert (lo, hi) == (Fraction(496, 1000), Fraction(1504, 1000))
    assert relative_width(Fraction(99, 100), Fraction(101, 100)) == Fraction(2, 100)


@check("L41: engine A lock, drift guard, a_ball containment precheck")
def _t_engine_a():
    from flint import ctx

    from .engines import EngineDrift, a_ball, a_frac, det_sign_a, lock_engine_a

    lock_engine_a()
    b = a_ball(Fraction(1, 3), Fraction(2, 3))
    assert b.contains(a_frac(Fraction(1, 3))), "lower endpoint lost"
    assert b.contains(a_frac(Fraction(2, 3))), "upper endpoint lost"
    assert float(2 * b.rad()) < 0.34, "unexpectedly wide construction"
    ctx.prec = 4096
    try:
        try:
            det_sign_a(Fraction(1, 2), [a_frac(Fraction(2))], [])
        except EngineDrift:
            pass
        else:
            raise AssertionError("precision drift not detected")
    finally:
        lock_engine_a()


@check("engines: det + derivative, dual containment vs exact rational")
def _t_det():
    from .engines import (
        a_det,
        a_det_d,
        a_frac,
        b_det,
        b_det_d,
        b_point,
        b_sign,
        det_sign_exact,
        lock_engine_a,
        mpf_to_fraction,
    )

    lock_engine_a()
    diag = [Fraction(1), Fraction(2), Fraction(3)]
    off2 = [Fraction(1, 2), Fraction(1, 3)]
    lam = Fraction(3, 2)
    val = _exact_det(lam, diag, off2)
    dval = _exact_det_d(lam, diag, off2)
    s_exact = det_sign_exact(lam, diag, off2)
    assert s_exact == (1 if val > 0 else -1), "exact recurrence wrong"

    diag_a = [a_frac(d) for d in diag]
    off2_a = [a_frac(d) for d in off2]
    dA = a_det(a_frac(lam), diag_a, off2_a)
    assert dA.contains(a_frac(val)), "engine A det ball misses exact value"
    if s_exact != 0:
        assert (dA > 0) == (s_exact > 0)
    dA2 = a_det_d(a_frac(lam), diag_a, off2_a)
    assert dA2.contains(a_frac(dval)), "engine A derivative ball misses exact value"

    diag_b = [b_point(d) for d in diag]
    off2_b = [b_point(d) for d in off2]
    dB = b_det(b_point(lam), diag_b, off2_b)
    assert mpf_to_fraction(dB.lo) <= val <= mpf_to_fraction(dB.hi), "engine B det"
    if s_exact != 0:
        assert b_sign(dB) == s_exact
    dB2 = b_det_d(b_point(lam), diag_b, off2_b)
    assert mpf_to_fraction(dB2.lo) <= dval <= mpf_to_fraction(dB2.hi), "engine B d'"


@check("K-Q2: sylvester PD / fence / negative on both engines")
def _t_sylvester():
    from .engines import a_ball, a_frac, b_ball, b_point, lock_engine_a
    from .sylvester import sylvester_a, sylvester_b

    lock_engine_a()
    n = 5
    d0 = Fraction(2)
    eps = Fraction(4, 1000)
    diag = [a_ball(d0 - eps, d0 + eps) for _ in range(n)]
    off2_a = [a_frac(Fraction(1)) for _ in range(n - 1)]
    db = [b_ball(d0 - eps, d0 + eps) for _ in range(n)]
    off2_b = [b_point(Fraction(1)) for _ in range(n - 1)]

    assert sylvester_a(diag, off2_a)["status"] == "CERTIFIED_PD"
    assert sylvester_b(db, off2_b)["status"] == "CERTIFIED_PD"

    fence_a = [a_ball(Fraction(-1, 1000), Fraction(1, 1000))] + diag[1:]
    assert sylvester_a(fence_a, off2_a)["status"] == "FENCE_ZERO"
    fence_b = [b_ball(Fraction(-1, 1000), Fraction(1, 1000))] + db[1:]
    assert sylvester_b(fence_b, off2_b)["status"] == "FENCE_ZERO"

    neg_a = [a_ball(Fraction(-2), Fraction(-19, 10))] + diag[1:]
    assert sylvester_a(neg_a, off2_a)["status"] == "NEGATIVE_PIVOT"
    neg_b = [b_ball(Fraction(-2), Fraction(-19, 10))] + db[1:]
    assert sylvester_b(neg_b, off2_b)["status"] == "NEGATIVE_PIVOT"


@check("K-Q4/K-Q5: chispec exactness + dashboard self-containment")
def _t_chispec_dashboard():
    from . import chispec
    from .dashboard import assert_self_contained, render_report

    knots = [float(s) for s in chispec.KNOTS]
    assert knots == sorted(knots), "knots not ascending"
    assert chispec.KNOTS[7] == "0"
    for k in range(7):
        assert chispec.KNOTS[k] == "-" + chispec.KNOTS[14 - k], "knot asymmetry"

    counts = chispec.counts_from([0.0] * 160)
    assert sum(counts) == 160 and counts[8] == 160
    exp = chispec.expected_counts(160)
    kept, dropped = chispec.floor_rule(exp)
    assert len(kept) == 16 and dropped == []
    chi2 = chispec.chi2_exact(counts, exp, kept)
    assert chi2 == Fraction(2400), "exact chi2 mismatch: %s" % chi2

    kept16, dropped16 = chispec.floor_rule(chispec.expected_counts(16))
    assert kept16 == [] and len(dropped16) == 16
    assert chispec.chi2_exact(counts[:16], chispec.expected_counts(16), kept16) is None
    assert chispec.exceedances([3.4, 3.5, 4.0, 0.0]) == 2

    page = render_report(
        {
            "campaign": "t",
            "created_utc": "x",
            "entropy": {"label": "SIMULATED", "backend": "b", "block_bits": 4096},
            "verdict": {"status": "RESOLVED", "exit_code": 0, "reasons": []},
            "dims": [],
        }
    )
    assert_self_contained(page)
    try:
        assert_self_contained(page.replace("SIMULATED", "PLAIN"))
    except AssertionError:
        pass
    else:
        raise AssertionError("page without the SIMULATED label passed K-Q5")


@check("frozen constants: knots and p* fidelity at dps 70")
def _t_constants():
    import mpmath as mp

    from . import chispec

    mp.mp.dps = 70

    def Phi(x):
        return mp.erfc(-x / mp.sqrt(2)) / 2

    def inv(p):
        lo, hi = mp.mpf(-12), mp.mpf(12)
        for _ in range(300):
            mid = (lo + hi) / 2
            if Phi(mid) < p:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    for k in (1, 4, 7, 9, 12, 15):
        q = Fraction(chispec.KNOTS[k - 1])
        ref = inv(mp.mpf(k) / 16)
        got = mp.mpf(q.numerator) / mp.mpf(q.denominator)
        assert abs(got - ref) <= mp.mpf("1e-40"), "knot %d fidelity" % k
    ps = Fraction(chispec.P_STAR)
    ref = 1 - Phi(mp.mpf("3.5"))
    got = mp.mpf(ps.numerator) / mp.mpf(ps.denominator)
    assert abs(got - ref) <= mp.mpf("1e-40"), "p* fidelity"


@check("entropy stream: block probe, batch digest, uniforms, normals")
def _t_entropy():
    import math

    from .entropy_source import BLOCK_BYTES, EntropySource

    src = EntropySource()
    assert len(src.probe_block()) == BLOCK_BYTES
    src.begin_batch()
    buf = src._draw(16)
    meta = src.end_batch()
    assert meta["digest"] == hashlib.sha256(buf).hexdigest()
    assert meta["bytes"] == 16 and meta["label"] == "SIMULATED"
    us = src.uniforms(1000)
    assert len(us) == 1000 and all(0.0 <= u < 1.0 for u in us)
    xs = src.normals(401)
    assert len(xs) == 401 and all(math.isfinite(x) for x in xs)
    assert abs(sum(xs) / len(xs)) < 1.0  # ~10 sigma; no verdict use


@check("K-Q6: ledger chain, REVERT vocabulary, tamper detection")
def _t_ledger(tmp_note=None):
    import tempfile

    from .ledger import (
        append_record,
        make_genesis,
        make_revert,
        verify_chain,
    )

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "l.jsonl"
        g = append_record(p, make_genesis("s", "p", "2026-10-19T00:00:00Z"))
        v = verify_chain(p)
        assert v["ok"] and v["count"] == 1 and v["head"] == g["record_hash"]
        r = append_record(p, make_revert(8, "reproduced failure", "ev", "2026-10-19T00:00:01Z"))
        v = verify_chain(p)
        assert v["ok"] and v["count"] == 2 and v["head"] == r["record_hash"]
        try:
            append_record(p, {"type": "REJECT", "fitness_verdict": "REJECT"})
        except ValueError:
            pass
        else:
            raise AssertionError("REJECT record was accepted (K-Q6)")
        raw = p.read_bytes().replace(b'"SIMULATED"', b'"SIMULATEN"')
        q = Path(td) / "tampered.jsonl"
        q.write_bytes(raw)
        assert not verify_chain(q)["ok"], "tamper not detected"


@check("coordinates at D=8: bracket, envelope, numpy cross-check, Newton")
def _t_coords():
    from .engines import lock_engine_a
    from . import runner as R

    lock_engine_a()
    D = 8
    mat = R._build_matrices(D)
    import numpy as np

    h = 1.0 / (D + 1)
    M = np.zeros((D, D))
    for i in range(D):
        M[i, i] = 2.0 + ((i + 1) ** 2) * (h**4)
        if i + 1 < D:
            M[i, i + 1] = M[i + 1, i] = -1.0
    ev = np.linalg.eigvalsh(M)

    for k in sorted({D // 4, D // 2, (3 * D) // 4, D}):
        br = R.certified_bracket(k, mat)
        lo, hi = br["lo"], br["hi"]
        assert hi - lo <= Fraction(41, 10) / 2**150, "bracket wider than contracted"
        assert br["stats"]["disagree"] == 0, "engine disagreement at D=8"
        e_lo, e_hi = lo - R.ENVELOPE, hi + R.ENVELOPE
        assert R.endpoint_certificate(mat, e_lo, e_hi, k)["ok"], "endpoint cert k=%d" % k
        lam = Fraction(ev[k - 1])
        assert e_lo < lam < e_hi, "numpy eigenvalue outside certified envelope"
        mid = (lo + hi) / 2
        na = R.a_newton(
            mid - R.NEWTON_START_HALF,
            mid + R.NEWTON_START_HALF,
            mat["diag_a"],
            mat["off2_a"],
            R.NEWTON_ITERS,
            R.NEWTON_TARGET,
        )
        assert na["status"] == "CONTRACTED", "engine A newton k=%d: %s" % (k, na["status"])
        nb = R.b_newton(
            mid - R.NEWTON_START_HALF,
            mid + R.NEWTON_START_HALF,
            mat["diag_b"],
            mat["off2_b"],
            R.NEWTON_ITERS,
            R.NEWTON_TARGET,
        )
        assert nb["status"] == "CONTRACTED", "engine B newton k=%d: %s" % (k, nb["status"])


@check("mini campaign end-to-end (temp ledger/outdir, dims 8/9/10)")
def _t_mini():
    import tempfile

    from . import runner as R
    from .dashboard import assert_self_contained
    from .engines import lock_engine_a
    from .ledger import append_record, make_genesis, verify_chain

    lock_engine_a()
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        ledger = td / "ledger.jsonl"
        append_record(ledger, make_genesis("s", "p", "2026-10-19T00:00:00Z"))
        res = R.run_campaign(
            dims=(8, 9, 10),
            samples=160,
            batch=80,
            outdir=td / "out",
            ledger_path=ledger,
            html_path=td / "dash.html",
            time_cap_min=5.0,
            quiet=True,
        )
        assert res["status"] in ("RESOLVED", "NOT_RESOLVED", "UNDETERMINED")
        assert res["exit_code"] in (0, 1, 2)
        v = verify_chain(ledger)
        assert v["ok"], "mini ledger chain broken: %s" % v["error"]
        types = []
        with open(ledger, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    types.append(json.loads(line)["type"])
        assert types.count("BLOCK") == 6, types
        assert types.count("STATS") == 3, types
        assert types.count("VERDICT") == 4, types
        for D in (8, 9, 10):
            assert (td / "out" / ("stats_d%d.bin" % D)).exists()
        for r in res["dims"]:
            assert r["expected"][0] == Fraction(10), "mini E_b should be 10"
            assert r["samples"] <= 160
        page = (td / "dash.html").read_text(encoding="utf-8")
        assert_self_contained(page)


@check("freeze PINS verification (conditional: runs once PINS.sha256 exists)")
def _t_pins():
    root = Path(__file__).resolve().parents[2]
    pins = root / "audit_quantum" / "PINS.sha256"
    if not pins.exists():
        print("    [info] PINS.sha256 not built yet (pre-freeze rehearsal)")
        return
    n = 0
    for line in pins.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        sha, rel = line.split("  ", 1)
        data = (root / rel).read_bytes()
        assert hashlib.sha256(data).hexdigest() == sha, "PINS mismatch: %s" % rel
        n += 1
    assert n > 0, "empty PINS"


# ---------------------------------------------------------------------------
# harness
# ---------------------------------------------------------------------------


def run_all(verbose: bool = True) -> int:
    from .engines import lock_engine_a

    lock_engine_a()  # L41: before any dependent computation
    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
        except Exception as e:  # noqa: BLE001 - selftest reports everything
            failures += 1
            import traceback

            print("FAIL %s" % name)
            traceback.print_exc()
        else:
            if verbose:
                print("PASS %s" % name)
    print(
        "SELFTEST: %d checks, %d failure(s)%s"
        % (len(CHECKS), failures, " -> ZERO FAILURE" if failures == 0 else "")
    )
    return failures


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    from .entropy_source import refuse_seed

    refuse_seed(argv)
    return 0 if run_all() == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())


