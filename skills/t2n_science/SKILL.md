---
name: t2n_science
description: Guinand-Weil tau matrix analysis, spectral enclosures, anatomical testing, and enclosed SVD runtime.
---

# t2n_science Skill

## Sub-commands & Programmatic Usage

1. **Build Arb Tau Matrices**
   - Command: `python -m msaf.chrono_runtime.build_arb_tau`
   - Description: Generates enclosed Guinand-Weil tau matrices and exports binary/JSON enclosures.

2. **Anatomy Test**
   - Command: `python -m msaf.chrono_runtime.anatomy_test`
   - Description: Measures maximum residuals against Toeplitz and Hankel structures using Arb ball arithmetic.

3. **Enclosed SVD Analysis**
   - Command: `python -m msaf.chrono_runtime.svd_analysis`
   - Description: Computes enclosed spectral metrics, trace, and Frobenius norms over tau matrices, writing to `reports/TAU_SVD_INSIGHTS.json`.
