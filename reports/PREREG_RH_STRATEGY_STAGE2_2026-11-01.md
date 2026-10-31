# Pre-Registration: Stage 2 Proof Extraction (Analytic Tail Bound Derivation via Laurent Operator)

Date: 2026-11-01
Author: Chrono-Runtime Subsystem
Authority: CURRENT_AUTHORITY.md / AGENTS.md

## Objective
Re-initiate Stage 2 proof extraction for truncated Guinand-Weil operator tail error bound using exact FLINT `arb`/`acb`/`fmpq` arithmetic and Digamma ($\psi$) pole isolation.

## Decision Gates & Parameters
- **Maximum Permitted Enclosure Expansion Width**: $1e-12$.
- **Precision**: FLINT arb/acb exact ball arithmetic.
- **Scope Limits**: 
  - `rh_global_claim`: `false`
  - `compact_operator_classification`: `false`
- **Quiet Runtime**: Suppress JSON-RPC token serialization loops, limit terminal print buffer, silence intermediate interval array streaming to stdout.

## Python Class Setup Confirmation
- `LaurentLogicBridgeEngine`: Validates exact rational coefficients (`fmpq`), suppresses float64 (`StructuralIntegrityViolation`), evaluates Laurent series expansions $\sum c_k \epsilon^k$ over exact acb intervals, and applies symmetric Minkowski widening.
- `Stage2TailBoundEngine`: Computes rigorous tail bound $|E_N| \le \frac{1}{N} \left( |\psi(N+1) - \psi(1)| + \frac{1}{2N} \right)$, isolating Digamma poles at non-positive integers with strict radius threshold enforcement ($\le 1e-12$).
