# Pre-Registration Framework: Stage 3 — Spectral Evaluation and Operator-Level Critical Line Lock

Date: 2026-11-01
Registry ID: T-2026-0091
Authority: CURRENT_AUTHORITY.md / AGENTS.md

## 1. Matrix-Tau Projection Loop Definition
The matrix-tau projection maps continuous boundary residues isolated in Stage 2 onto a truncated Guinand-Weil block via:
$$\tau = W_{02} - W_R - W_p$$
where:
- $W_{02}$ = Archimedean Dirichlet / Digamma block
- $W_R$ = Guinand-Weil kernel matrix
- $W_p$ = Prime-summation remainder term

## 2. Frozen Decision Gates
- **Discrete Symmetric Boundary Conditions**: $0 \in [L_{\text{Im}}]$ must hold under 512-bit ball arithmetic. Any interval excluding zero immediately aborts execution.
- **SVD Energy Profiling Lower Bound ($k_{90}$)**: If $k_{90} < 10$, dimension state is flagged as `UNDECIDED` to prevent false compactness assertions.
- **Precision**: Initial evaluation precision locked at 512 bits via `python-flint` (`ctx.prec = 512`), scaling dynamically to 1024 bits upon `ResolutionAlarm`.
- **Frobenius Norm Radius Cap**: Maximum permitted enclosure expansion radius for $\|\tau\|_F^2$ strictly capped at $1e-12$.
- **Momentum Cross-Check Gate ($G$-M0)**: Tolerance enforced at $1e-300$.

## 3. Standing Scope Limits
- `rh_global_proof_claim`: `false`
- `universal_zero_free_zone_claim`: `false`
- `compact_operator_derivation`: `false`
Output is strictly restricted to localized sign and magnitude certificate of a finite, truncated deterministic matrix under a frozen CFL condition.
