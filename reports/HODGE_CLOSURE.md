# Hodge Program Closure (measured, v1.34.0-alpha)

This document closes the Hodge/Picard branch of the program with the
numbers actually measured by the code. It is a status record, not a
claim: nothing here touches the Hodge conjecture.

## 1. What is closed (machine-verified)

| Item | Result |
|---|---|
| Period enclosures | AGM tau, triple-validated (i, j-match, lambda-orbit) |
| Fermat quartic counts | 7 / 16 / 0 over F2 / F3 / F5 (chart-split exact) |
| char-2 degeneracy retraction | x^4+y^4+z^4+w^4 = (x+y+z+w)^4 in char 2 -> K3 claims fenced to odd p |
| F_{2^n} / F_{3^n} machinery | counts 16/280/784, smoothness gates, dual-norm check |
| Jacobi trace machinery | ball-certified integers, closed form e = 2 locked to n = 9 |
| Exact counts via lifting | Davenport-Hasse in Z[zeta_{4p}], all F_5 counts, matches the ball sweep n = 1..7, reaches n = 12 |
| Fermat K3 over F_3 | traces a_1..a_11, char poly (1-3T)^12 (1+3T)^10, bound 22 = b_2 (vacuous) |
| Fermat K3 over F_5 | traces a_1..a_11 exact, bound 20 (non-vacuous vs 22) |
| Fermat K3, other primes | bound 20 for p = 5,13,17,29,37,41 -- family at its geometric ceiling |
| General quartic over F_3 | Groebner smoothness witness, exact brute counter, Weil gate |
| Vectorised counter | exact vs brute at k <= 3; Fermat 16/154/784 three-way locked; k = 8 in 70 s |

## 2. Why the branch closes here (the honest part)

**The Fermat family is exhausted, provably.** Its geometric Picard
rank is 20 = b_2 - 2, so the van Luijk bound cannot go below 20 for
any prime. Six primes were measured; all give 20. An informative
bound (< 20) requires a K3 of LOW geometric Picard rank.

**For general quartics the wall is arithmetic, not algorithmic
clean-up.** The degree-22 Newton reconstruction needs traces
a_1..a_11, i.e. point counts over F_{3^k} for k up to 11. Measured
cost of the validated vectorised counter on a smooth quartic:

    k = 6: 0.7 s    k = 7: 7.1 s    k = 8: 70 s
    k = 9: ~12 min  k = 10: ~2 h     k = 11: ~19 h

Pure-Python/NumPy therefore reaches k = 9 comfortably and k = 10 as an
offline job; k = 11 is out of reach. This is exactly the situation
Couveignes-Henocq was designed for (counts only to k ~ 7, Frobenius
mod l by baby-step giant-step, CRT against Weil bounds).

**Chaotic surface construction failed on a real obstruction.** In
characteristic 2 the naive Artin-Schreier double cover
w^2 + w = F(x,y,z) is singular at z = 0 (W^2 + x^6 = (W + x^3)^2,
inseparable), and the separable replacement w^2 + wH + G needs a
different counting scheme. Not shipped half-verified.

## 3. Bugs caught while closing (each by cross-check, not by review)

- Functional-equation exponent conflated variety dimension with
  polynomial degree; the API now takes `dim_x` explicitly.
- A single squarefree GCD counts DISTINCT roots, not multiplicity.
- The FE "self-check" was dead code (lhs built from the same rhs).
- Jacobi hot loop rebuilt transcendentals per element (288 s -> 2.6 s
  once tabulated, and a trace-form bug that silently corrupted even k).
- Galois sums need Z[zeta_{4p}], not Z[i] (non-integral counts said so).
- Smoothness certificates: naive "basis contains 1" fails for
  homogeneous forms; chart dehomogenisation once dropped a variable and
  fabricated smooth certificates for singular quartics.
- Point counting: projective overcount by q - 1; the line at infinity
  dropped; a normalised chart divided again.

## 4. Explicit non-claims

- No statement about K3 surfaces in general, over any family.
- No statement about the Hodge conjecture. Finite-field Picard-rank
  bounds carry no content about it.
- Agreement of counts with theory is CONSISTENCY, not proof.
- The Weil gate checks counting consistency; it does NOT certify
  smoothness (a certified singular quartic still landed inside the
  envelope -- measured, documented).

## 5. What remains mapped open

- `HODGE-CH`: Couveignes-Henocq for the last trace(s) of a smooth
  quartic, with the ten known traces as its oracle. **EXECUTED: a_11 =
  354294 uniquely isolated; CRT combiner (M > 2B), oracle gate HOLD,
  leave-one-out rehearsal (10/10 PASS), circle test PASS.**
- Informative bound (< 20) requires a low-rank K3 plus that method.