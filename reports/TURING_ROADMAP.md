# Turing Roadmap: From Certified Counting to Bounded Verification

## Status: measurement complete, proof machinery mapped (OPEN)

### 1. Measured N(T) (certified counts, 256-bit)

| T | N(T) measured | Main term `(T/2π)log(T/2πe)+7/8` | Implied S(T) |
|---|---|---|---|
| 10 | 0 (COMPLETE, 2845 evals) | 0.0231 | ≈ -0.02 |
| 25 | 2 (COMPLETE, 5173 evals) | 2.3909 | ≈ -0.39 |
| 50 | 10 (COMPLETE, 7041 evals) | 9.4228 | ≈ +0.58 |

(Main-term values via display-only float arithmetic; counts are
ball-certified. Agreement is CONSISTENCY, not verification: nothing
here bounds S(T).)

### 2. What Turing's method requires (gap analysis)

A full Turing verification "RH true up to T" needs, beyond counting:

- (G1) **Argument-principle cross-check**: an independent count of
  zeros in the rectangle (e.g., via variation of arg xi along the
  boundary) agreeing with the Newton count. Guards against a zero
  missed by BOTH Newton and exclusion (e.g., multiple close zeros
  defeating isolation). Status: OPEN, unmapped in code.
- (G2) **Explicit S(T) bounds** (Backlund/Trudgian type): a proven
  inequality `|S(T)| ≤ B(T)` to compare against `N(T) - main(T)`.
  Without it, agreement in the table above constrains nothing.
  Status: OPEN, pure analysis research.
- (G3) **Off-line zeros**: our rectangles cover sigma ∈ [0.49, 0.51].
  A Turing claim needs the FULL critical strip (or a functional-equation
  reduction argument made explicit). Status: OPEN by design scope.

### 3. What is already closed

- Certified counting with completeness-in-rectangle (`msaf/riemann/`,
  `RH-COUNT`, `RH-COUNT-10`).
- Moore-test existence+uniqueness, machine-checked
  (`lean/NewtonExistence.lean`).
- Verdict-gap fencing (floor branch never counts).

### 4. Explicit non-claims

No bound on S(T) is proven here. No statement is made about zeros
outside computed rectangles. Agreement with the main term is
expected behavior of a correct counter, not evidence for RH.
