# Pre-Registration: De Bruijn-Newman Constant Falsification (2026-11-02)

## Scope
Falsification of the De Bruijn-Newman constant $\Lambda = 0$ (Riemann Hypothesis equivalent) under the Finite Information Lattice framework.

## Mathematical Engine
- **Precision**: 12,000-bit Arb arithmetic (`ctx.prec = 12000`).
- **Operator**: Deformed Guinand-Weil spectral operator matrix $\tau_t$.
- **Modulation**: Von Mangoldt weights $\Lambda_d(k)$ modulated by Fourier deformation kernel $\exp(t \cdot \ln(q)^2)$.
- **Verification**: 5-clause Gate G-M0 cross-checked with Engine B at 100 dps.

## Success/Failure Criteria
- **Pass**: $LDL^T$ factorization remains positive-definite at $t=0$.
- **Critical Failure**: Negative pivot ($n^- > 0$) at $t=0$ under Minkowski widening triggers `RIEMANN-CRITICAL-LINE-DECOUPLED` and a fail-closed `ResolutionAlarm`.
