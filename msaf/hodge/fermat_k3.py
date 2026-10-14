"""Fermat-quartic K3 over F_5: exact traces and the Picard bound.

Runs the FULL degree-22 Newton reconstruction from exact integer
counts (Davenport-Hasse lifted Jacobi sums) and reports the van
Luijk bound. For F_3 the bound was vacuous (22 = b_2, the surface
is supersingular there); over F_5 the structure is non-degenerate,
and this pipeline measures what it actually gives.

Scope (binding): bounded, per-prime statements about ONE concrete
K3 surface (the Fermat quartic) over ONE finite field. Nothing
about K3 surfaces in general, and nothing about the Hodge
conjecture: a Picard-rank upper bound of the Weil-polynomial
type is what van Luijk's method delivers, nothing stronger.
"""
from flint import ctx

from msaf.hodge.gauss_exact import fermat_quartic_projective_exact
from msaf.hodge.picard_bound import char_poly_from_traces, picard_bound

__all__ = ["fermat_k3_traces", "fermat_k3_picard", "fermat_k3_report"]


def fermat_k3_traces(p: int, degree: int = 11, prec_bits: int = 256) -> dict:
    """Frobenius traces a_k = #X(F_p^k) - 1 - p^(2k), k = 1..degree.

    Exact integer arithmetic throughout (no balls): the counts come
    from lifted Jacobi sums, the traces are integers by definition
    of the cohomology formula #X(F_q) = 1 + q^2 + a_1. The Weil
    bound |a_k| <= 22 p^k is asserted: a violation would mean the
    count pipeline is wrong, not that zeta breaks Weil.
    """
    ctx.prec = int(prec_bits)
    traces: dict[int, int] = {}
    for k in range(1, degree + 1):
        q = p**k
        proj = fermat_quartic_projective_exact(k, p)["projective"]
        a = proj - 1 - q * q
        if abs(a) > 22 * q:
            raise RuntimeError(
                f"Weil bound violated at k={k}: |a_k|={abs(a)} > {22*q}"
            )
        traces[k] = a
    return traces


def fermat_k3_picard(p: int, degree: int = 11) -> dict:
    """Newton + FE (dim_x=2) + Moebius multiplicity over F_p."""
    traces = fermat_k3_traces(p, degree)
    poly = char_poly_from_traces(traces, 22, p, 1, dim_x=2)
    if poly is None:
        raise RuntimeError("functional equation refused sign +1")
    out = picard_bound(traces, 22, p, dim_x=2)
    out["traces"] = traces
    out["leading_coeff"] = str(poly[-1])
    out["picard_upper_bound"] = out["bound"]
    out["vacuous"] = out["bound"] >= 22
    return out


def fermat_k3_report(prime: int, degree: int = 11) -> dict:
    """Human-facing summary: counts, traces, bound, honesty flags."""
    counts = {
        k: fermat_quartic_projective_exact(k, prime)["projective"]
        for k in range(1, min(degree, 7) + 1)
    }
    out = fermat_k3_picard(prime, degree)
    lines = [f"Fermat quartic K3 over F_{prime} (exact integer pipeline)"]
    lines.append("projective counts n=1..7: " + ", ".join(
        f"{k}:{v}" for k, v in counts.items()))
    lines.append(
        "traces a_1..a_11: "
        + ", ".join(str(out["traces"][k]) for k in sorted(out["traces"]))
    )
    lines.append(f"Picard rank upper bound (van Luijk): {out['picard_upper_bound']}")
    lines.append(
        "vacuous (bound = b_2 = 22): " + ("YES" if out["vacuous"] else "NO")
    )
    lines.append(
        "non-claim: one concrete K3 over one field; no statement about "
        "K3 surfaces in general or about the Hodge conjecture."
    )
    return {"text": "\n".join(lines), "detail": out}