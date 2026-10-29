#!/usr/bin/env python3
"""Render README display equations to self-contained SVG files.

GitHub does not typeset LaTeX in Markdown, and external render services
(codecogs, latex.codecogs) are a longevity liability for a permanent archive.
This generator uses matplotlib's built-in mathtext engine (no network, no
TeX installation) so every formula in the README is a versioned local asset
under docs/math/. Re-run after editing FORMULAS:

    python3 harness/render_math.py
"""

from __future__ import annotations

import sys
from pathlib import Path

FORMULAS: dict[str, str] = {
    "partition": r"$\Delta_1 = 0.5 - 0 = 0.5, \quad \Delta_2 = 1 - 0.5 = 0.5$",
    "nsteps": r"$N_{\mathrm{steps}} = \dfrac{D_{\mathrm{obs}}}{\ell_P}"
              r" \approx 5.44 \times 10^{61}$",
    "chebyshev": r"$\psi_d(k) = \sum_{j \leq k} \Lambda_d(j)$",
    "xi": r"$\xi(s) = \dfrac{1}{2}\, s (s-1)\, \pi^{-s/2}\,"
          r"\Gamma(s/2)\, \zeta(s)$",
    "commutator": r"$[\hat{H}, \hat{T}]"
                  r" = \hat{H}\hat{T} - \hat{T}\hat{H} = 0$",
    "sigma": r"$\sigma_m = 1 - \sigma_m"
             r" \;\Rightarrow\; 2\sigma_m = 1"
             r" \;\Rightarrow\; \mathbf{\sigma_m = 0.5}$",
    "pixel": r"$k_m = \left\lfloor \dfrac{\gamma_m}{2\pi}"
             r" \cdot \log_2(N_{\mathrm{steps}}) \right\rfloor"
             r" \;\mathrm{mod}\; N_{\mathrm{steps}}$",
    "entropy": r"$H(n) = -\sum_k p_k\, \log_2(p_k)$",
    "lambda_min": r"$\lambda_{\min}(n) \sim \mathcal{A}\,"
                  r"e^{-\mathcal{B}\, n}$",
    "ncrit": r"$\mathcal{B}\,\log_2(e)\, n^2"
             r" + n\,\log_2(1/\mathcal{A}) - N_{\mathrm{steps}} = 0$",
    "gw_tau": r"$\tau = W_{02} - W_R - W_p, \qquad \dim\tau = 2N+1$",
    "gw_kernel": r"$R_2(u) = 1 - \left( \dfrac{\sin(\pi u)}{\pi u}"
                 r" \right)^{2}, \qquad R_2(0) = 0$",
    "gw_ratio": r"$s_i = x_{i+1} - x_i, \qquad r_i ="
                r" \dfrac{\min(s_i,\, s_{i+1})}{\max(s_i,\, s_{i+1})},"
                r" \qquad \bar{r} = \dfrac{1}{D-2}"
                r" \sum_{i=1}^{D-2} r_i$",
    "gw_unfold": r"$x_k = \sum_m \Phi\left("
                 r" \dfrac{y_k - y_m}{\sigma_u\, h_m} \right)$",
    "gw_estimator": r"$R_2^{\mathrm{est}}(u) = \dfrac{1}{D}"
                    r" \sum_{i \neq j} G_{\sigma_e}\left("
                    r" u - (x_i - x_j) \right)$",
    "gw_chisq": r"$\chi^2_{\mathrm{obs}} = \sum_{E_b \geq 5}"
                r" \dfrac{\left( c_b - T_{\sigma_e}(u_b) \right)^{2}}"
                r"{\mathrm{Var}_{\mathrm{GUE}}(b)}$",
    "gw_pvals": r"$p_{\mathrm{GUE}} = P\left[ \chi^2_{\mathrm{GUE}}"
                r" \geq \chi^2_{\mathrm{obs}} \right], \qquad"
                r" p_{\mathrm{Pois}} = P\left[ \chi^2_{\mathrm{Pois}}"
                r" \leq \chi^2_{\mathrm{obs}} \right]$",
    "gw_gate": r"$\dfrac{\left| \sum_k \lambda_k"
               r" - \mathrm{tr}(M) \right|}{\left| \mathrm{tr}(M) \right|}"
               r" < 10^{-300}, \qquad"
               r" \dfrac{\left| \sum_k \lambda_k^2 - \Vert M \Vert_F^2 \right|}"
               r"{\Vert M \Vert_F^2} < 10^{-300}$",
}

INK = "#1f2328"


def render_all(out_dir: Path) -> list[Path]:
    import matplotlib

    matplotlib.use("SVG")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, latex in FORMULAS.items():
        fig = plt.figure(figsize=(8, 1.4), dpi=200)
        fig.patch.set_alpha(0.0)
        fig.text(0.02, 0.5, latex, fontsize=22, color=INK)
        target = out_dir / f"{name}.svg"
        fig.savefig(target, bbox_inches="tight", transparent=True)
        plt.close(fig)
        written.append(target)
    return written


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    written = render_all(root / "docs" / "math")
    for path in written:
        print(f"rendered {path.relative_to(root)} ({path.stat().st_size} bytes)")
    missing = [n for n in FORMULAS if not (root / "docs" / "math" / f"{n}.svg").exists()]
    if missing:
        print(f"MISSING: {missing}", file=sys.stderr)
        return 1
    print(f"{len(written)} formulas rendered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


