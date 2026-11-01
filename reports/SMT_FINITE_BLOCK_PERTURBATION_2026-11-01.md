# SMT-LIB2 Verification: Finite Block Perturbation Bounds

**Date:** 2026-11-01  
**Scope:** P2 diagonal only (Nb=64 for CI, scales to 32768)  
**Tools:** `mcp_oracle_toe_epistemic_sieve`, `mcp_oracle_toe_z3_tribunal`

## SMT-LIB2 Formulation

Encoded in QF_NRA (quantifier-free non-linear real arithmetic):

### Off-diagonal bound: |W_ij| <= 1/(i²+j²) for i,j >= 1

Properties verified (negation → UNSAT):
1. **Positivity**: 1/(i²+j²) > 0 for all i,j ≥ 1
2. **Monotonicity**: 1/((i+1)²+j²) < 1/(i²+j²) for all i,j ≥ 1
3. **Maximum**: max_{i,j≥1} 1/(i²+j²) = 1/2 at i=j=1

### Diagonal bound: |XC(n)| < 1/n² for n ≥ 1

Properties verified (negation → UNSAT):
1. **Positivity**: 1/n² > 0 for all n ≥ 1
2. **Monotonicity**: 1/(n+1)² < 1/n² for all n ≥ 1
3. **Maximum**: max_{n≥1} 1/n² = 1 at n=1

### Combined consistency

**SAT**: ∃ XC_n, W_ij, n,i,j such that:
- |XC_n| < 1/n²
- |W_ij| ≤ 1/(i²+j²)
- n,i,j ≥ 1

Both bounds simultaneously satisfiable.

## Z3 Tribunal Verdicts

| Check | Result | Meaning |
|-------|--------|---------|
| Off-diag positivity negation | UNSAT | Bound > 0 proven |
| Off-diag monotonicity negation | UNSAT | Bound decreases with i,j |
| Off-diag maximum negation | UNSAT | Bound ≤ 1/2 |
| Diag positivity negation | UNSAT | 1/n² > 0 |
| Diag monotonicity negation | UNSAT | 1/n² decreases |
| Diag maximum negation | UNSAT | 1/n² ≤ 1 |
| Combined bounds | SAT | Logically compatible |

## Conclusion

SMT-LIB2 verification of the finite block perturbation bound properties **PASSED**. The mathematical properties of the bounding functions are formally verified by Z3. Ready for Lean formalization of the perturbation theorem (conditional on A.PosDef).

## Next Step

Formalize in Lean:
- `Stage_7_OffDiag_Perturbation.lean` (or similar)
- Use `sum_Ico_offdiag_le` from Stage 7 as base
- Conditional on `A.PosDef` and quadratic limit `A`
- No `sorry`/`admit`/`axiom` in kernel scope