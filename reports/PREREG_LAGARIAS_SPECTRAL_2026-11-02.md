# Pre-Registration: Lagarias Spectral Criterion (2026-11-02)

## Scope
Map the Lagarias harmonic inequality $\sum_{d|n} d \le H_n + e^{H_n} \ln(H_n)$ onto the Finite Information Lattice near macro cutoff $N_{\text{steps}} \approx 5.44 \times 10^{61}$.

## Execution Plan
1. Write validation script `msaf/problems/lagarias_lattice.py` using 512-bit Arb arithmetic.
2. Scan for discrete edge anomalies or enclosure radius expansion on massive prime addresses.
3. Enforce fail-closed verification via `reports/FENCE_REGISTRY.md`.
