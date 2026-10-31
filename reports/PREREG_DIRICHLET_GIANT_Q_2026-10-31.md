# Pre-Registration: Problem 4 — Giant Conductor Dirichlet L-Functions ($q=1000$)

- **Date:** 2026-10-31
- **Registry ID:** T-2026-0087
- **Authority:** `CURRENT_AUTHORITY.md`

## Scope & Constraints
1. **Modulus:** $q = 1000 = 2^3 \cdot 5^3$.
2. **Precision:** Dynamic ramp from 512 bits up to 2048 bits under FLINT `acb`/`arb` structures.
3. **Interval Width Limit:** Maximum allowed interval width for root ordinates $\gamma_m$ set at $1e-20$.
4. **Scope Boundaries:** NO claims of proving the Generalized Riemann Hypothesis (GRH). Strict coefficient-arithmetic and localized ordinate measurement report only.
5. **Anti-Circularity:** Rejects unverified float64 root estimates; enforces exact rational FLINT arithmetic.
