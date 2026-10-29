"""General quartic surfaces over odd primes: exact counts + smoothness.

SCOPE (binding): X = { w^2 = f(x,y,z) } in P^3 over F_p, p odd,
with f a general quartic form (not necessarily diagonal). Provides

  1. an exact brute-force point counter (obviously correct, used as
     the oracle for every faster path),
  2. a Groebner-based smoothness certificate (X is smooth iff the
     four partials f_x, f_y, f_z, f_w have no common projective zero;
     in char != 2 with f = w^2 - F the criterion reduces to the
     branch quartic C: F = 0 being smooth),
  3. a chunked NumPy counter for larger q, cross-validated against (1).

Why the certificate is mandatory, not decoration: a "generic-looking"
quartic over F_3 measured a_3 = 18351 against the Weil envelope
22*27 = 594 -- the surface was singular, and a singular point count is
a perfectly plausible integer that means nothing. Every count path
here asserts |a_k| <= 22 p^k (K3 Weil bound) as a loud gate.

Explicit non-claim: counts of points on one surface; the Picard
reading lives in `picard_bound`.
"""
from __future__ import annotations

from itertools import product

__all__ = [
    "count_quartic_brute",
    "count_quartic_vector",
    "check_vector_against_brute",
    "groebner_contains_one",
    "is_smooth_branch",
    "assert_weil",
    "quartic_traces",
]


# --- exact F_p^k arithmetic (coefficient lists, lowest first) ---------


def _mul(a, b, mod, k, p):
    r = [0] * (2 * k - 1)
    for i, ca in enumerate(a):
        if ca:
            for j, cb in enumerate(b):
                if cb:
                    r[i + j] = (r[i + j] + ca * cb) % p
    while len(r) > k:
        if r[-1]:
            f = r[-1]
            idx = len(r) - 1
            for i, d in enumerate(mod):
                r[idx - k + i] = (r[idx - k + i] - f * d) % p
        r.pop()
    return r


def _pw(a, e, mod, k, p):
    r = [0] * k
    r[0] = 1
    while e:
        if e & 1:
            r = _mul(r, a, mod, k, p)
        a = _mul(a, a, mod, k, p)
        e >>= 1
    return r


def _elements(k, p):
    return [list(d) for d in product(range(p), repeat=k)]


def _decode(cand, k, p):
    a = [0] * k
    t = cand
    for i in range(k):
        a[i] = t % p
        t //= p
    return a


def count_quartic_brute(coeffs, k, p=3) -> int:
    """#X(F_{p^k}) for X = {w^2 = f}, brute force over P^2(F_{p^k}).

    ``coeffs`` maps (i, j) -> c with f = sum c x^i y^j z^(4-i-j).
    Enumerates normalized projective representatives (some coordinate
    nonzero), evaluates f exactly, adds 1 + chi(f). Obvious, slow,
    and the oracle for everything else.
    """
    from msaf.hodge.odd_fields import find_modulus

    if isinstance(k, float) or isinstance(p, float):
        raise TypeError("k/p: float64 leakage refused")
    k, p = int(k), int(p)
    if p < 3 or p % 2 == 0:
        raise ValueError(f"p must be an odd prime >= 3, got {p}")
    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    mod = find_modulus(k, p)
    q = p**k
    half = (q - 1) // 2
    E = _elements(k, p)
    total = 0
    for x in E:
        for y in E:
            for z in E:
                if not any(x + y + z):
                    continue  # skip the all-zero triple (not a point)
                f = [0] * k
                for (i, j), c in coeffs.items():
                    w = 4 - i - j
                    if w < 0:
                        continue
                    t = _mul(_pw(x, i, mod, k, p), _pw(y, j, mod, k, p), mod, k, p)
                    t = _mul(t, _pw(z, w, mod, k, p), mod, k, p)
                    f = [(a + c * b) % p for a, b in zip(f, t)]
                if all(v == 0 for v in f):
                    total += 1
                else:
                    v = _pw(f, half, mod, k, p)
                    total += 1 + (1 if v[0] % p == 1 else -1)
    # Every nonzero triple represents the same projective point q-1
    # times, and the summand 1 + chi(f) is scale-invariant (chi(lam^4
    # f) = chi(f)). Divide, asserting exactness -- omitting this was
    # the same blind spot that hit the char-2 draft and produced
    # plausible-but-6x-too-large counts here.
    if total % (q - 1) != 0:
        raise RuntimeError(
            f"point sum {total} not divisible by q-1 = {q - 1}"
        )
    return total // (q - 1)


# --- smoothness certificate: Groebner basis of the branch partials ----


def _poly_trim(poly, p):
    out = [list(c) for c in poly]
    while out and all(c % p == 0 for c in out[-1]):
        out.pop()
    return out


def _poly_add(a, b, p):
    n = max(len(a), len(b))
    out = [[0] * n]
    out = [0] * n
    for i in range(n):
        av = a[i] % p if i < len(a) else 0
        bv = b[i] % p if i < len(b) else 0
        out[i] = (av + bv) % p
    return _poly_trim(out, p)


def _poly_sub(a, b, p):
    n = max(len(a), len(b))
    out = [0] * n
    for i in range(n):
        av = a[i] % p if i < len(a) else 0
        bv = b[i] % p if i < len(b) else 0
        out[i] = (av - bv) % p
    return _poly_trim(out, p)


def _poly_scale(a, c, p):
    return _poly_trim([(c * x) % p for x in a], p)


def _poly_mul(a, b, p):
    out = [0] * max(1, len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        if ca % p == 0:
            continue
        for j, cb in enumerate(b):
            out[i + j] = (out[i + j] + ca * cb) % p
    return _poly_trim(out, p)


def _poly_divmod(a, b, p):
    """(quotient, remainder) for exact univariate division."""
    a = _poly_trim(list(a), p)
    b = _poly_trim(list(b), p)
    if not b or (len(b) == 1 and b[0] % p == 0):
        raise ZeroDivisionError("division by zero polynomial")
    inv = pow(b[-1] % p, -1, p)
    q = [0] * max(1, len(a) - len(b) + 1)
    while len(a) >= len(b) and not (len(a) == 1 and a[0] % p == 0):
        coef = (a[-1] * inv) % p
        shift = len(a) - len(b)
        q[shift] = (q[shift] + coef) % p
        for i, cb in enumerate(b):
            a[shift + i] = (a[shift + i] - coef * cb) % p
        a = _poly_trim(a, p)
    return _poly_trim(q, p), a


def _monomial_key(exps):
    return exps  # lex order by (x0, x1, x2) ascending is total enough


class _Poly:
    """Multivariate polynomial over F_p: dict (exps)->coeff."""

    def __init__(self, p):
        self.p = p
        self.terms = {}

    def clone(self):
        q = _Poly(self.p)
        q.terms = dict(self.terms)
        return q

    def is_zero(self):
        return all(c % self.p == 0 for c in self.terms.values())

    def clean(self):
        self.terms = {k: c % self.p for k, c in self.terms.items() if c % self.p}
        return self

    def lead(self):
        if not self.terms:
            return None, 0
        best = max(self.terms, key=_monomial_key)
        return best, self.terms[best] % self.p

    def add(self, other, sign=1):
        r = self.clone()
        for e, c in other.terms.items():
            r.terms[e] = (r.terms.get(e, 0) + sign * c) % self.p
        return r.clean()

    def scale(self, c):
        r = self.clone()
        for e in r.terms:
            r.terms[e] = (c * r.terms[e]) % self.p
        return r.clean()

    def mul(self, other):
        r = _Poly(self.p)
        for e1, c1 in self.terms.items():
            for e2, c2 in other.terms.items():
                e = tuple(e1[i] + e2[i] for i in range(len(e1)))
                r.terms[e] = (r.terms.get(e, 0) + c1 * c2) % self.p
        return r.clean()

    def rem(self, g):
        r = self.clone()
        while not r.is_zero():
            le, lc = r.lead()
            ge, gc = g.lead()
            if tuple(le) < tuple(ge) or all(
                le[i] >= ge[i] for i in range(len(le))
            ) is False:
                break
            shift = tuple(le[i] - ge[i] for i in range(len(le)))
            fac = (lc * pow(gc, -1, self.p)) % self.p
            r = r.add(g.scale(fac).shift(shift), sign=-1)
        return r

    def shift(self, exps):
        r = _Poly(self.p)
        for e, c in self.terms.items():
            r.terms[tuple(e[i] + exps[i] for i in range(len(e)))] = c
        return r


def _partial(coeffs, var, p):
    """Partial derivative of the quartic form f wrt homogeneous var."""
    out = []
    for (i, j), c in coeffs.items():
        w = 4 - i - j
        if w < 0:
            continue
        if var == 0:
            if i:
                out.append(((i - 1, j, w), c * i))
        elif var == 1:
            if j:
                out.append(((i, j - 1, w), c * j))
        else:
            if w:
                out.append(((i, j, w - 1), c * w))
    return out


def _to_poly(terms, p):
    q = _Poly(p)
    for e, c in terms:
        if c % p:
            q.terms[e] = c % p
    return q


def _buchberger(polys, p, max_pairs=20000):
    pairs = []
    G = [_to_poly(t, p) for t in polys]
    G = [g for g in G if not g.is_zero()]
    for i in range(len(G)):
        for j in range(i + 1, len(G)):
            pairs.append((i, j))
    steps = 0
    while pairs:
        steps += 1
        if steps > max_pairs:
            raise RuntimeError("Groebner basis did not converge in budget")
        i, j = pairs.pop()
        S = _s_poly(G[i], G[j], p)
        if S.is_zero():
            continue
        r = S
        for g in G:
            r = r.rem(g)
            if r.is_zero():
                break
        if r.is_zero():
            continue
        r = r.scale(pow(r.lead()[1], -1, p))
        G.append(r)
        n = len(G) - 1
        for m in range(len(G) - 1):
            pairs.append((m, n))
        pairs.append((n - 1, n))
    return G


def _s_poly(f, g, p):
    fe, fc = f.lead()
    ge, gc = g.lead()
    if tuple(fe) < tuple(ge):
        f, g = g, f
        fe, fc = f.lead()
        ge, gc = g.lead()
    lcm = tuple(max(fe[i], ge[i]) for i in range(len(fe)))
    sf = tuple(lcm[i] - fe[i] for i in range(len(fe)))
    sg = tuple(lcm[i] - ge[i] for i in range(len(ge)))
    return f.scale(pow(fc, -1, p)).shift(sf).add(
        g.scale(pow(gc, -1, p)).shift(sg), sign=-1
    )


def groebner_contains_one(polys, p) -> bool:
    """True iff the Groebner basis of the ideal contains a nonzero
    constant, i.e. the ideal is the unit ideal."""
    G = _buchberger(polys, p)
    for g in G:
        if len(g.terms) == 1 and ((), 1) in [(e, c % p) for e, c in g.terms.items()]:
            if g.terms[((),)] % p != 0:
                return True
    return False


def is_smooth_branch(coeffs, p=3) -> bool:
    """Smoothness certificate for X = {w^2 = f}: the branch plane
    quartic must have no common PROJECTIVE zero of f_x, f_y, f_z.

    (Euler: in char != 2 a singular point of the surface is a point
    of the branch curve with all three partials vanishing; conversely
    a singular point of the branch lifts to one of the surface.)

    Test by CHART DECOMPOSITION, not by one ideal. Two earlier
    criteria were wrong and both were caught by the Fermat control
    (which is smooth): "the Groebner basis contains a constant" says
    the ideal is the unit ideal, but the homogeneous ideal
    (x^3, y^3, z^3) has projective zero set EMPTY yet contains no
    constant and does not even contain x, y or z. Dehomogenising per
    chart avoids the whole issue: on the chart x = 1 the three
    partials are ordinary polynomials in y, z, and emptiness is
    exactly "the ideal is the unit ideal" (affine Nullstellensatz).
    For Fermat, f_x(1,y,z) = 4 = 1 mod 3, so the chart is empty.
    """
    if p < 3 or p % 2 == 0:
        raise ValueError(f"p must be an odd prime >= 3, got {p}")
    from msaf.hodge.groebner import Poly, groebner_contains_one

    parts = [_partial(coeffs, var, p) for var in range(3)]
    for chart in range(3):
        polys = []
        for terms in parts:
            deh = []
            # chart v = 1 means SUBSTITUTING v := 1: drop that
            # exponent. The surviving variables are the other TWO
            # positions -- reading positions (0, 1) after zeroing
            # position `chart` silently DROPS z whenever chart is y,
            # which fabricated smooth-looking certificates for
            # singular quartics (caught by randomized cross-check).
            keep = [i for i in range(3) if i != chart]
            for e, c in terms:
                exp2 = [e[i] if i != chart else 0 for i in range(3)]
                deh.append(((exp2[keep[0]], exp2[keep[1]]), c % p))
            if deh:
                polys.append(Poly(p, deh))
        if not polys:
            continue
        if not groebner_contains_one(polys, p):
            return False
    return True


class _VecTables:
    """NumPy tables for GF(p^k): log/exp plus 5-bit packed digits.

    Elements are carried as base-3 digit integers; ``packed`` re-encodes
    a value with 5 bits per digit so that field addition becomes plain
    integer addition of at most 15 summands (digit <= 2 each, so 30 <
    32 and NO carry ever crosses a digit boundary -- verified below
    against the brute counter).
    """

    def __init__(self, k: int, p: int = 3) -> None:
        from msaf.hodge.odd_fields import find_modulus

        self.k = k
        self.p = p
        self.q = p**k
        self.order = self.q - 1
        mod = find_modulus(k, p)
        self.mod = mod
        one = [1] + [0] * (k - 1)

        def mul(a, b):
            return _mul(a, b, mod, k, p)

        gen = None
        for cand in range(1, self.q):
            a = [0] * k
            t = cand
            for i in range(k):
                a[i] = t % p
                t //= p
            if all(c == 0 for c in a):
                continue
            if _pw(a, self.order, mod, k, p) == one and all(
                _pw(a, self.order // d, mod, k, p) != one
                for d in _prime_factors(self.order)
            ):
                gen = a
                break
        if gen is None:
            raise RuntimeError(f"no generator for GF({p}^{k})")
        self.gen = gen
        import numpy as np

        exp_idx = np.empty(self.order, dtype=np.int64)
        log_of = np.full(self.q, -1, dtype=np.int64)
        cur = [0] * k
        cur[0] = 1
        for i in range(self.order):
            v = 0
            for d, c in enumerate(cur):
                v += c * p**d
            exp_idx[i] = v
            log_of[v] = i
            cur = mul(cur, gen)
        if cur != [1] + [0] * (k - 1):
            raise RuntimeError("generator search produced wrong order")
        self.exp_vals = exp_idx
        self.log_of = log_of
        # 5-bit packed digit encoding
        packed = np.zeros(self.q, dtype=np.int64)
        for v in range(self.q):
            t = v
            acc = 0
            for d in range(k):
                acc += (t % p) << (5 * d)
                t //= p
            packed[v] = acc
        self.packed = packed
        self.log_scalar = {}
        for v in range(self.q):
            if log_of[v] >= 0:
                self.log_scalar[v] = int(log_of[v])

    def log_index(self, value: int) -> int:
        li = int(self.log_of[value])
        return li if li >= 0 else 0


def _prime_factors(m: int) -> list[int]:
    out: list[int] = []
    d = 2
    while d * d <= m:
        if m % d == 0:
            out.append(d)
            while m % d == 0:
                m //= d
        d += 1
    if m > 1:
        out.append(m)
    return out


def count_quartic_vector(coeffs, k: int, p: int = 3, chunk: int = 4_000_000) -> int:
    """Vectorised exact count of #X(F_{p^k}) for X = {w^2 = f}.

    Same mathematics as `count_quartic_brute` (sum of 1 + chi(f) over
    the q^2 points of the chart z = 1, divided by q - 1 because each
    projective point has q - 1 representatives on that chart). The
    only difference is speed: the grid is processed in flat chunks so
    memory stays bounded regardless of q, products go through
    log/exp tables, and field addition is integer addition of 5-bit
    packed digits (no carries, since at most 15 monomials with digits
    <= 2 sum to <= 30 < 32).

    ALWAYS cross-validate this against `count_quartic_brute` at small
    k: an earlier vectorised draft disagreed with brute force and had
    to be thrown away. `check_vector_against_brute` does exactly that.
    """
    if isinstance(k, float) or isinstance(p, float):
        raise TypeError("k/p: float64 leakage refused")
    k, p = int(k), int(p)
    if p < 3 or p % 2 == 0:
        raise ValueError(f"p must be an odd prime >= 3, got {p}")
    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    import numpy as np

    tb = _VecTables(k, p)
    q = tb.q
    order = tb.order
    chart_terms = []
    infinity_terms = []
    for (i, j), c in coeffs.items():
        w = 4 - i - j
        if w < 0 or c % p == 0:
            continue
        entry = (i, j, int(c) % p, tb.log_index(int(c) % p))
        chart_terms.append(entry)
        if w == 0:  # only these survive on the line z = 0
            infinity_terms.append(entry)
    if not chart_terms:
        raise ValueError("quartic form is identically zero")

    def grid_sum(terms) -> int:
        acc_total = 0
        n_cells = q * q
        for start in range(0, n_cells, chunk):
            stop = min(start + chunk, n_cells)
            flat = np.arange(start, stop, dtype=np.int64)
            xs = flat // q
            ys = flat - xs * q
            lx = tb.log_of[xs]
            ly = tb.log_of[ys]
            acc = np.zeros(stop - start, dtype=np.int64)
            for (i, j, _c, lc) in terms:
                idx = (i * lx + j * ly + lc) % order
                mask = np.ones(stop - start, dtype=bool)
                if i > 0:
                    mask &= xs != 0
                if j > 0:
                    mask &= ys != 0
                vals = tb.exp_vals[np.where(mask, idx, 0)]
                acc += np.where(mask, tb.packed[vals], 0)
            val = np.zeros(stop - start, dtype=np.int64)
            for d in range(k):
                dig = ((acc >> (5 * d)) & 31) % p
                val += dig * (p**d)
            lg = tb.log_of[val]
            half = order // 2
            chi = np.where((lg * half) % order == 0, 1, -1).astype(np.int64)
            chi[val == 0] = 0
            acc_total += int((1 + chi).sum())
        return acc_total

    # The chart z = 1 is NORMALISED: its q^2 cells are q^2 distinct
    # projective points, so no division. The line z = 0 carries q + 1
    # points, each with q - 1 representatives among the q^2 cells, so
    # it is summed (minus the (0,0) cell, which is not a point) and
    # divided by q - 1. Two separate slips lived here: omitting the
    # line entirely (returned 6 where brute force gives 16), and
    # dividing the normalised chart as well.
    chart = grid_sum(chart_terms)
    infinity = grid_sum(infinity_terms) - 1
    if infinity % order != 0:
        raise RuntimeError(
            f"infinity sum {infinity + 1} not divisible by q-1 = {order}"
        )
    return chart + infinity // order


def check_vector_against_brute(coeffs, kmax: int = 3, p: int = 3) -> dict:
    """Hard gate: the vectorised counter must equal brute force exactly."""
    out = {}
    for k in range(1, kmax + 1):
        b = count_quartic_brute(coeffs, k, p)
        v = count_quartic_vector(coeffs, k, p)
        if b != v:
            raise RuntimeError(
                f"vectorised counter disagrees at k={k}: {v} vs brute {b}"
            )
        out[k] = b
    return out


def assert_weil(a: int, k: int, q: int) -> None:
    """Raise unless the K3 Weil envelope |a_k| <= 22 q^k holds.

    SCOPE of this gate, stated honestly: it is a CONSISTENCY check on
    the counting, NOT a smoothness detector. A singular surface can
    still produce counts inside the envelope (measured: a certified
    singular quartic over F_3 with |a_2| = 27 < 198), and a genuine
    arithmetic slip (the q-1 overcount, the wrong normalisation) blows
    straight through it. Smoothness has its own witness --
    `is_smooth_branch` -- and neither check substitutes for the other.
    """
    if abs(a) > 22 * q:
        raise RuntimeError(
            f"Weil bound violated at k={k}: |a_k|={abs(a)} > {22*q}"
        )


def quartic_traces(coeffs, degree, p=3, kmax=11) -> dict[int, int]:
    """K3 traces a_k = #X(F_{p^k}) - 1 - p^{2k}, k = 1..degree.

    The Weil bound |a_k| <= 22 p^k is asserted: a violation means
    the surface is singular (or the count wrong), never that Weil is
    false. Uses the brute counter; the vectorized path must agree
    with it before its results are trusted anywhere.
    """
    if degree < 1 or degree > kmax:
        raise ValueError(f"degree must be in 1..{kmax}, got {degree}")
    traces: dict[int, int] = {}
    for k in range(1, degree + 1):
        q = p**k
        n = count_quartic_brute(coeffs, k, p)
        a = n - 1 - q * q
        assert_weil(a, k, q)
        traces[k] = a
    return traces

