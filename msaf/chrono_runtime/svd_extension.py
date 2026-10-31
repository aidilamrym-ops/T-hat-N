"""Enclosed singular-value bracket for the truncated Guinand-Weil matrix tau.

Authority
---------
``reports/PREREG_TAU_SVD_EXTENSION_2026-10-31.md`` and its addenda A1, A2, A3
(commits ``16f216e``, ``018c82f``, ``c86ea8f``, ``13f7b58``).  The definitions,
gates, parameters and decision rules implemented here are frozen in those
documents; this module adds no measurement of its own.

Scope limits (unchanged): ``{rh_claim: false, zero_location_claim: false,
weil_positivity_claim: false}``.  Nothing here is an enclosed singular-value
spectrum: the campaign reports a rigorous bracket ``[L, U]`` on ``sigma_max``
and a rigorous lower bound ``k90`` on the number of singular values needed to
carry 90% of the Frobenius energy.  No individual singular value is computed.

Usage
-----
    python -m msaf.chrono_runtime.svd_extension \
        --out reports/TAU_SVD_INSIGHTS_EXTENDED.json
"""

from __future__ import annotations

import os

# Declared single-threaded environment (pre-registration section 5).  Set
# before the numeric imports so the whole process sees the same setting.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from flint import arb, ctx

from msaf.chrono_runtime.svd_analysis import load_matrix
from msaf.tau_reconstruction import build, serialize

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"

CONDUCTOR = 100
ENCLOSURE_PREC = 256
REPRODUCTION_PREC = 53
K90_THRESHOLD = 10

# dim -> (committed file, block N)
COMMITTED = {
    201: ("gw_matrix_100_100.json", 100),
    301: ("gw_matrix_100_150.json", 150),
}
# dim -> block N (new dimensions, not committed)
NEW = {401: 200, 501: 250}

SCOPE = {
    "rh_claim": False,
    "zero_location_claim": False,
    "weil_positivity_claim": False,
}


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def sha256lf_bytes(data: bytes) -> str:
    """SHA-256 with CRLF normalised to LF (checkout-stable hashing)."""
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def sha256lf_path(path: Path) -> str:
    return sha256lf_bytes(Path(path).read_bytes())


def _git_head() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(ROOT),
            capture_output=True,
            check=True,
        )
        return out.stdout.decode("ascii").strip()
    except Exception:  # pragma: no cover - only on a broken checkout
        return "UNKNOWN"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _int_ceil(value: arb) -> int:
    """Exact integer ceiling of an exact arb point."""
    return int(value.ceil().unique_fmpz())


# ---------------------------------------------------------------------------
# M1/M2 -- trace and Frobenius energy (identical accumulation to T-2026-0074)
# ---------------------------------------------------------------------------

def trace_and_frobenius(mat):
    """Return (trace, sum tau_ij^2, sum |tau_ij|^2).

    The accumulation order (``diag += mat[i, i]`` then the inner row loop,
    row-major) and the ``val * val`` product reproduce
    ``msaf/chrono_runtime/svd_analysis.py`` exactly, which is what G-M2a
    checks.  ``sum |tau_ij|^2`` is the frozen M2 definition; for a real matrix
    it must equal the square sum, and the report records that they do.
    """
    n = mat.nrows()
    diag_sum = arb(0)
    frob_sq = arb(0)
    frob_abs_sq = arb(0)
    for i in range(n):
        diag_sum += mat[i, i]
        for j in range(n):
            val = mat[i, j]
            frob_sq += val * val
            frob_abs_sq += abs(val) ** 2
    return diag_sum, frob_sq, frob_abs_sq


# ---------------------------------------------------------------------------
# M3-M6 -- column norms, Gershgorin data, bracket, concentration
# ---------------------------------------------------------------------------

def _symmetrised_gram(mat):
    """G = (tau*tau^T + (tau*tau^T)^T)/2, built entrywise.

    Each entry ``(M[i, j] + M[j, i]) / 2`` contains the corresponding entry of
    the true symmetric Gram matrix, because both computed intervals contain
    the same true value and the average of two intervals contains the average
    of any selection.
    """
    n = mat.nrows()
    prod = mat * mat.transpose()
    half = arb("0.5")
    gram = [[(prod[i, j] + prod[j, i]) * half for j in range(n)]
            for i in range(n)]
    return gram


def singular_value_bracket(mat, frob_abs_sq):
    """Compute M3-M6.

    Returns a dict with interval strings, the bracket endpoints used for the
    decision, the Gershgorin looseness indicator, and ``k90``.
    """
    n = mat.nrows()

    # M3 -- column norms c_j = sqrt(sum_i |tau_ij|^2), L_col = max_j c_j.
    l_col = None
    col_sq_norms = []
    for j in range(n):
        acc = arb(0)
        for i in range(n):
            acc += abs(mat[i, j]) ** 2
        col_sq_norms.append(acc)
        norm = acc.sqrt()
        l_col = norm if l_col is None else l_col.max(norm)

    # M4 -- Gershgorin data of the symmetrised Gram matrix.
    gram = _symmetrised_gram(mat)
    lam_max_g = None
    lam_min_g = None
    for i in range(n):
        diag = gram[i][i]
        radius = arb(0)
        for j in range(n):
            if j != i:
                radius += abs(gram[i][j])
        disc_hi = diag + radius
        disc_lo = diag - radius
        lam_max_g = disc_hi if lam_max_g is None else lam_max_g.max(disc_hi)
        lam_min_g = disc_lo if lam_min_g is None else lam_min_g.min(disc_lo)

    # Schur test data: ||tau||_1 (max column sum) and ||tau||_inf (max row sum).
    nrm_1 = None
    for j in range(n):
        acc = arb(0)
        for i in range(n):
            acc += abs(mat[i, j])
        nrm_1 = acc if nrm_1 is None else nrm_1.max(acc)
    nrm_inf = None
    for i in range(n):
        acc = arb(0)
        for j in range(n):
            acc += abs(mat[i, j])
        nrm_inf = acc if nrm_inf is None else nrm_inf.max(acc)

    # M5 -- bracket [L, U] on sigma_max.
    #   L: sigma_max >= ||tau e_j|| = c_j for every j, and
    #      F = sum sigma_i^2 <= n * sigma_max^2.
    #   U: sigma_max^2 <= lam_max(tau tau^T) <= lam_max_G (Gershgorin),
    #      sigma_max^2 <= F, and sigma_max^2 <= ||tau||_1 * ||tau||_inf.
    l_ball = (frob_abs_sq / n).sqrt().max(l_col)
    u_ball = (
        frob_abs_sq.sqrt()
        .min(lam_max_g.sqrt())
        .min((nrm_1 * nrm_inf).sqrt())
    )

    f_lo = frob_abs_sq.lower()
    f_hi = frob_abs_sq.upper()
    l_lo = l_ball.lower()
    u_hi = u_ball.upper()

    # M6 -- concentration.  k90 is the ceiling of a *lower* bound on
    # 0.9 F / U^2, so it is a rigorous lower bound on the number of modes.
    ratio_lower = (arb("0.9") * f_lo) / (u_hi * u_hi)
    k90 = _int_ceil(ratio_lower.lower())

    rho_lo = (l_lo * l_lo) / f_hi
    rho_hi = (u_hi * u_hi) / f_lo

    return {
        "M3_column_norm_max_L_col": str(l_col),
        "M4_gershgorin": {
            "lambda_max_G": str(lam_max_g),
            "lambda_min_G_looseness_only": str(lam_min_g),
        },
        "M5_bracket": {
            "L": str(l_ball),
            "U": str(u_ball),
            "L_lower_endpoint": str(l_lo),
            "U_upper_endpoint": str(u_hi),
            "nrm_1": str(nrm_1),
            "nrm_inf": str(nrm_inf),
        },
        "M6_concentration": {
            "rho_lo": str(rho_lo),
            "rho_hi": str(rho_hi),
            "k90": k90,
            "k90_threshold": K90_THRESHOLD,
            "verdict": "FEW-MODES-REFUTED" if k90 >= K90_THRESHOLD else "UNDECIDED",
        },
        "_frobenius_lower": f_lo,
        "_frobenius_upper": f_hi,
    }


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------

def gate_m1_finite(mat):
    """G-M1: every entry is a finite ball."""
    n = mat.nrows()
    for i in range(n):
        for j in range(n):
            if not mat[i, j].is_finite():
                return False, {"first_bad_entry": [i, j], "value": str(mat[i, j])}
    return True, {"entries_checked": n * n}


def gate_m2a_reproduction(insights):
    """G-M2a: 53-bit reproduction of T-2026-0074, character for character."""
    ctx.prec = REPRODUCTION_PREC
    detail = {}
    ok = True
    for dim, (name, _block) in COMMITTED.items():
        mat = load_matrix(REPORTS / name)
        trace, _sq, frob = trace_and_frobenius(mat)
        expected = insights[Path(name).stem]
        row = {
            "dimension": dim,
            "prec_bits": REPRODUCTION_PREC,
            "trace_computed": str(trace),
            "trace_committed": expected["trace"],
            "trace_equal": str(trace) == expected["trace"],
            "frobenius_computed": str(frob),
            "frobenius_committed": expected["frobenius_norm_sq"],
            "frobenius_equal": str(frob) == expected["frobenius_norm_sq"],
        }
        ok = ok and row["trace_equal"] and row["frobenius_equal"]
        detail[str(dim)] = row
    return ok, detail


def gate_m2b_containment(insights):
    """G-M2b: 256-bit enclosures are contained in the 53-bit committed ones."""
    ctx.prec = ENCLOSURE_PREC
    detail = {}
    ok = True
    values = {}
    for dim, (name, _block) in COMMITTED.items():
        mat = load_matrix(REPORTS / name)
        trace, _sq, frob = trace_and_frobenius(mat)
        values[dim] = (str(trace), str(frob))
        expected = insights[Path(name).stem]
        t_ok = arb(expected["trace"]).contains(trace)
        f_ok = arb(expected["frobenius_norm_sq"]).contains(frob)
        detail[str(dim)] = {
            "dimension": dim,
            "prec_bits": ENCLOSURE_PREC,
            "trace": str(trace),
            "frobenius_sq": str(frob),
            "trace_contained": t_ok,
            "frobenius_contained": f_ok,
        }
        ok = ok and t_ok and f_ok
    return ok, detail, values


def canonical_serialization(mat, block):
    """Serialize ``mat`` with the canonical ``msaf.gw_matrix.v1`` metadata."""
    build_chain = (
        "msaf.tau_reconstruction.build_arb_tau"
        f"(c={CONDUCTOR},N={block},prec={ENCLOSURE_PREC}) "
        f"at ctx.prec={ENCLOSURE_PREC}"
    )
    tmpdir = Path(tempfile.mkdtemp(prefix="tau_svd_extension_"))
    path = tmpdir / f"gw_matrix_{CONDUCTOR}_{block}.json"
    serialize.save_matrix_json(
        mat,
        path,
        conductor=CONDUCTOR,
        block=block,
        prec_bits=ENCLOSURE_PREC,
        build_chain=build_chain,
        gate_verdict="G-M0 PASS",
    )
    return path


def serialization_slack(mat, path):
    """max_ij (|mid_ser - mid| + rad_ser - rad) and the max midpoint shift."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data["matrix"]
    n = mat.nrows()
    worst = None
    for i in range(n):
        for j in range(n):
            cell = rows[i][j]
            mid = arb(cell["mid"])
            rad = arb(cell["rad"])
            gap = abs(mid - mat[i, j].mid()) + rad - mat[i, j].rad()
            if worst is None or gap > worst:
                worst = gap
    return worst


def gate_m3a_committed_reproduction():
    """G-M3a: a fresh build + canonical serialization reproduces the commits."""
    detail = {}
    ok = True
    rebuilt = {}
    for dim, (name, block) in COMMITTED.items():
        mat = build.build_arb_tau(c=CONDUCTOR, N=block, prec_bits=ENCLOSURE_PREC)
        ctx.prec = ENCLOSURE_PREC
        path = canonical_serialization(mat, block)
        digest = serialize.compute_sha256lf(path)
        committed = serialize.compute_sha256lf(REPORTS / name)
        equal = digest == committed
        detail[str(dim)] = {
            "dimension": dim,
            "block": block,
            "rebuilt_sha256lf": digest,
            "committed_sha256lf": committed,
            "equal": equal,
        }
        ok = ok and equal
        rebuilt[dim] = (mat, path)
    return ok, detail, rebuilt


def gate_m2c_roundtrip(rebuilt, m2b_values):
    """G-M2c': rebuild -> serialize -> re-parse reproduces the G-M2b strings."""
    ctx.prec = ENCLOSURE_PREC
    detail = {}
    ok = True
    for dim, (mat, path) in rebuilt.items():
        reparsed = load_matrix(Path(path))
        trace, _sq, frob = trace_and_frobenius(reparsed)
        t_expected, f_expected = m2b_values[dim]
        t_ok = str(trace) == t_expected
        f_ok = str(frob) == f_expected
        detail[str(dim)] = {
            "dimension": dim,
            "trace_reparsed": str(trace),
            "trace_equal": t_ok,
            "frobenius_reparsed": str(frob),
            "frobenius_equal": f_ok,
        }
        ok = ok and t_ok and f_ok
    return ok, detail


def gate_m2d_shift(rebuilt):
    """G-M2d: declared entrywise shift between rebuild and committed file."""
    ctx.prec = ENCLOSURE_PREC
    detail = {}
    for dim, (mat, _path) in rebuilt.items():
        name, _block = COMMITTED[dim]
        data = json.loads((REPORTS / name).read_text(encoding="utf-8"))
        rows = data["matrix"]
        n = mat.nrows()
        worst = None
        for i in range(n):
            for j in range(n):
                shift = abs(arb(rows[i][j]["mid"]) - mat[i, j].mid())
                if worst is None or shift > worst:
                    worst = shift
        detail[str(dim)] = {
            "dimension": dim,
            "max_entrywise_midpoint_shift": str(worst),
            "note": (
                "the committed file is the canonical serialization of this "
                "rebuild; it is narrower than the in-memory ball by this "
                "shift, so entrywise containment cannot hold (Addendum A3)"
            ),
        }
    return detail


# ---------------------------------------------------------------------------
# per-dimension record
# ---------------------------------------------------------------------------

def dimension_record(dim, block, mat, source, timings):
    t0 = time.time()
    finite_ok, finite_detail = gate_m1_finite(mat)
    trace, frob_sq, frob_abs_sq = trace_and_frobenius(mat)
    metrics = singular_value_bracket(mat, frob_abs_sq)
    metrics_s = time.time() - t0

    record = {
        "dimension": dim,
        "block": block,
        "conductor": CONDUCTOR,
        "prec_bits": ENCLOSURE_PREC,
        "matrix_source": source,
        "M1_trace": str(trace),
        "M2_frobenius_sq": str(frob_abs_sq),
        "M2_square_sum": str(frob_sq),
        "M2_square_and_abs_square_identical": str(frob_sq) == str(frob_abs_sq),
        "gates": {
            "G-M1_build_finiteness": {
                "pass": finite_ok,
                **finite_detail,
            },
        },
        "timing_s": dict(timings, metrics=round(metrics_s, 3)),
    }
    for key, value in metrics.items():
        if key.startswith("_"):
            continue
        record[key] = value
    return record


# ---------------------------------------------------------------------------
# main campaign
# ---------------------------------------------------------------------------

def run(out_path: Path) -> dict:
    started = _utc_now()
    t_start = time.time()

    insights = json.loads(
        (REPORTS / "TAU_SVD_INSIGHTS.json").read_text(encoding="utf-8")
    )

    # Stage 1 -- reproduction of T-2026-0074 at dims 201/301.
    m2a_ok, m2a_detail = gate_m2a_reproduction(insights)
    if not m2a_ok:
        raise SystemExit(
            "G-M2a FAIL: 53-bit reproduction of T-2026-0074 is not "
            "character-for-character; aborting before any new dimension."
        )

    m2b_ok, m2b_detail, m2b_values = gate_m2b_containment(insights)
    if not m2b_ok:
        raise SystemExit(
            "G-M2b FAIL: 256-bit enclosures are not contained in the 53-bit "
            "committed intervals; aborting before any new dimension."
        )

    m3a_ok, m3a_detail, rebuilt = gate_m3a_committed_reproduction()
    if not m3a_ok:
        raise SystemExit(
            "G-M3a FAIL: a fresh build no longer reproduces the committed "
            "matrix sha256lf; aborting before any new dimension."
        )

    m2c_ok, m2c_detail = gate_m2c_roundtrip(rebuilt, m2b_values)
    if not m2c_ok:
        raise SystemExit(
            "G-M2c' FAIL: the serialized rebuild does not reproduce the "
            "G-M2b enclosures; aborting before any new dimension."
        )

    m2d_detail = gate_m2d_shift(rebuilt)

    # Committed dimensions: metrics from the committed matrices (256 bits).
    ctx.prec = ENCLOSURE_PREC
    records = {}
    for dim, (name, block) in COMMITTED.items():
        mat = load_matrix(REPORTS / name)
        records[str(dim)] = dimension_record(
            dim,
            block,
            mat,
            source=f"committed {name}",
            timings={},
        )
        records[str(dim)]["gates"]["G-M2c_prime_roundtrip"] = m2c_detail[str(dim)]
        records[str(dim)]["gates"]["G-M2d_declared_shift"] = m2d_detail[str(dim)]
        slack = serialization_slack(rebuilt[dim][0], rebuilt[dim][1])
        records[str(dim)]["G-M3c_serialization_slack"] = str(slack)
        records[str(dim)]["serialization_sha256lf"] = m3a_detail[str(dim)][
            "rebuilt_sha256lf"
        ]

    # Stage 2 -- new dimensions 401 and 501.
    for dim, block in NEW.items():
        t0 = time.time()
        mat = build.build_arb_tau(c=CONDUCTOR, N=block, prec_bits=ENCLOSURE_PREC)
        ctx.prec = ENCLOSURE_PREC
        build_s = time.time() - t0

        # G-M3b: two independent builds must serialize identically.
        t1 = time.time()
        path_a = canonical_serialization(mat, block)
        digest_a = serialize.compute_sha256lf(path_a)
        serialize_s = time.time() - t1

        t2 = time.time()
        mat_b = build.build_arb_tau(c=CONDUCTOR, N=block, prec_bits=ENCLOSURE_PREC)
        ctx.prec = ENCLOSURE_PREC
        path_b = canonical_serialization(mat_b, block)
        digest_b = serialize.compute_sha256lf(path_b)
        second_build_s = time.time() - t2

        record = dimension_record(
            dim,
            block,
            mat,
            source="in-memory build_arb_tau",
            timings={
                "build": round(build_s, 3),
                "serialize": round(serialize_s, 3),
                "second_build_and_serialize": round(second_build_s, 3),
            },
        )
        record["gates"]["G-M3b_rebuild_determinism"] = {
            "sha256lf_build_1": digest_a,
            "sha256lf_build_2": digest_b,
            "pass": digest_a == digest_b,
        }
        record["serialization_sha256lf"] = digest_a
        t3 = time.time()
        record["G-M3c_serialization_slack"] = str(serialization_slack(mat, path_a))
        record["timing_s"]["slack"] = round(time.time() - t3, 3)
        records[str(dim)] = record

    finished = _utc_now()
    total_s = time.time() - t_start

    report = {
        "schema": "msaf.tau_svd_extension.v1",
        "campaign": "TAU-SVD-EXTENSION (PREREG 2026-10-31 + addenda A1-A3)",
        "generated_utc": finished,
        "started_utc": started,
        "repo_head": _git_head(),
        "tool": {
            "path": "msaf/chrono_runtime/svd_extension.py",
            "sha256lf": sha256lf_path(Path(__file__)),
        },
        "authority": {
            "prereg": {
                "path": "reports/PREREG_TAU_SVD_EXTENSION_2026-10-31.md",
                "sha256lf": sha256lf_path(
                    REPORTS / "PREREG_TAU_SVD_EXTENSION_2026-10-31.md"
                ),
            },
            "addendum_A1": {
                "path": "reports/PREREG_TAU_SVD_EXTENSION_2026-10-31_ADDENDUM_A1.md",
                "sha256lf": sha256lf_path(
                    REPORTS
                    / "PREREG_TAU_SVD_EXTENSION_2026-10-31_ADDENDUM_A1.md"
                ),
            },
            "addendum_A2": {
                "path": "reports/PREREG_TAU_SVD_EXTENSION_2026-10-31_ADDENDUM_A2.md",
                "sha256lf": sha256lf_path(
                    REPORTS
                    / "PREREG_TAU_SVD_EXTENSION_2026-10-31_ADDENDUM_A2.md"
                ),
            },
            "addendum_A3": {
                "path": "reports/PREREG_TAU_SVD_EXTENSION_2026-10-31_ADDENDUM_A3.md",
                "sha256lf": sha256lf_path(
                    REPORTS
                    / "PREREG_TAU_SVD_EXTENSION_2026-10-31_ADDENDUM_A3.md"
                ),
            },
        },
        "scope": SCOPE,
        "environment": {
            "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
            "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "precision": {
            "enclosure_prec_bits": ENCLOSURE_PREC,
            "reproduction_prec_bits": REPRODUCTION_PREC,
        },
        "parameters": {
            "conductor": CONDUCTOR,
            "blocks": {str(dim): block for dim, block in {**COMMITTED, **NEW}.items()},
            "prec_bits": ENCLOSURE_PREC,
        },
        "gates": {
            "G-M1_build_finiteness": "per dimension",
            "G-M2a_53bit_reproduction": {
                "pass": m2a_ok,
                "detail": m2a_detail,
            },
            "G-M2b_256bit_containment": {
                "pass": m2b_ok,
                "detail": m2b_detail,
            },
            "G-M2c_prime_roundtrip": {
                "pass": m2c_ok,
                "detail": m2c_detail,
            },
            "G-M2d_declared_shift": m2d_detail,
            "G-M3a_committed_reproduction": {
                "pass": m3a_ok,
                "detail": m3a_detail,
            },
        },
        "decision_rule": {
            "FEW-MODES-REFUTED": "k90 >= %d" % K90_THRESHOLD,
            "UNDECIDED": "k90 < %d" % K90_THRESHOLD,
            "note": (
                "per-dimension only; no trend statement across dimensions, "
                "and no compactness or decay conclusion"
            ),
        },
        "dimensions": records,
        "total_wall_clock_s": round(total_s, 3),
        "not_claimed": [
            "no enclosed singular-value spectrum",
            "no individual singular value",
            "no compactness or exponential-decay conclusion",
            "no statement about the Riemann hypothesis, zero locations or "
            "Weil positivity",
        ],
    }
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=REPORTS / "TAU_SVD_INSIGHTS_EXTENDED.json",
        help="report path (default: reports/TAU_SVD_INSIGHTS_EXTENDED.json)",
    )
    args = parser.parse_args(argv)

    report = run(args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, indent=1, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(f"wrote {args.out}")
    for dim, record in report["dimensions"].items():
        m6 = record["M6_concentration"]
        print(
            "dim %s  k90=%d  rho_hi=%s  verdict=%s"
            % (dim, m6["k90"], m6["rho_hi"][:24], m6["verdict"])
        )
    print("total %.1f s" % report["total_wall_clock_s"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
