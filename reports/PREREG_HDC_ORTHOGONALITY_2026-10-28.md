# Preregistration of HDC Orthogonality Note

**Date:** 2026-10-28  
**Commit SHA:** 717be15  
**Note location:** C:\Users\usER\AppData\Local\Temp\opencode\hdc_note_2026-10-28\HDC_Orthogonality_Note.md  

This entry records the preregistration of the HDC Orthogonality note prior to any Lean formalization. The note provides a rigorous replacement for the dissertation's hand‑wavy "hyperdimensional orthogonality" claim, including a full probabilistic proof, Chernoff/MGF derivation, Hoeffding form, sharpness proposition, corollaries, scope fence, corrected paragraph, Lean formalization plan, numerical audit, and references.

**Key numerical conclusions:**  
- For independent uniform bipolar vectors \(x,y \in \{\pm1\}^d\):  
  \(P(|\langle x,y\rangle| \ge \varepsilon d) \le 2\exp(-\varepsilon^2 d/2)\).  
- At \(d=10{,}000\):  
  - \(\varepsilon=0.05\) → exact tail \(6.01\times10^{-7}\), bound \(7.45\times10^{-6}\).  
  - \(\varepsilon=0.10\) → exact tail \(1.55\times10^{-23}\), bound \(3.86\times10^{-22}\).  
- For \(N\) pairs:  
  - \(N=10^6\) → \(\varepsilon=0.091046\) (δ = 10⁻⁶).  
  - \(N=10^9\) → \(\varepsilon=0.105130\).  
- Worst grid slack: \(\text{bound/exact}=1.213\) at \((d,\varepsilon)=(1,1)\).

**Next steps:**  
- Approve promotion to `lean/HDC_Orthogonality.lean` via dated prereg commit.  
- Run `gh workflow run slow-tests.yml --repo aidilamrym-ops/T-hat-N --ref main` to certify r6.  
- Revoke GitHub PAT exposed in `opencode.log` and run `gh auth login`.

*Prepared by the agent on 2026‑10‑28.*