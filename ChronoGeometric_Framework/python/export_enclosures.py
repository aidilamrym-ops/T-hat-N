"""Export verified enclosure data from T-hat-N msaf.zeta_inversion
to JSON for consumption by ChronoGeometric_Framework Lean modules.

This bridges the gap: verified Arb computations → Lean encoding predicates.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Add parent (T-hat-N root) to path for msaf import
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from msaf.zeta_inversion import (
        DEFAULT_TAYLOR_DEGREE,
        evaluate_xi,
        interval_newton_step,
        xi_taylor,
    )
    from flint import acb, arb
    HAS_MSAF = True
except ImportError:
    HAS_MSAF = False
    acb = arb = None  # type: ignore


def _acb_to_dict(ball: 'acb') -> dict[str, str]:
    """Convert flint acb to JSON-serializable dict with mid/rad as strings."""
    return {
        "real_mid": ball.real.mid().str(50),
        "real_rad": ball.real.rad().str(50),
        "imag_mid": ball.imag.mid().str(50),
        "imag_rad": ball.imag.rad().str(50),
    }


def _arb_to_str(x: 'arb') -> str:
    return x.str(50)


def export_moore_premises(box: 'acb', degree: int = DEFAULT_TAYLOR_DEGREE) -> dict[str, Any]:
    """Export the three Moore premises verification gates as JSON."""
    if not HAS_MSAF:
        return {"error": "msaf.zeta_inversion not available"}

    from ChronoGeometric_Framework.python.moore_premises import verify_moore_premises as verify
    result = verify(box, degree)

    return {
        "verdict": result["verdict"],
        "failed_gate": result["failed_gate"],
        "maps_to": result["maps_to"],
        "deriv_excludes_zero": result["deriv_excludes_zero"],
        "lipschitz_K": result["lipschitz_K"],
        "k_below_one": result["k_below_one"],
        "scope": result["scope"],
        "box": _acb_to_dict(box),
        "degree": degree,
    }


def export_derivative_enclosure(box: 'acb', degree: int = DEFAULT_TAYLOR_DEGREE) -> dict[str, Any]:
    """Export ξ', ξ'' enclosures for the box."""
    if not HAS_MSAF:
        return {"error": "msaf.zeta_inversion not available"}

    # First derivative
    deriv_ball = interval_newton_step(box, degree).derivative

    # Second derivative (mirrors xi_derivative_over_ball pattern)
    centre = box.mid()
    radius = max(box.real.rad().abs_upper(), box.imag.rad().abs_upper())
    coeffs = xi_taylor(centre, int(degree)).derivative().derivative().coeffs()

    if not coeffs:
        second_deriv = acb(0)
        tail = arb(0)
    else:
        second_deriv = coeffs[0]
        tail = arb(0)
        for k in range(1, len(coeffs)):
            c = coeffs[k]
            mag = c.real.abs_upper() + c.imag.abs_upper()
            tail += mag * radius**k
        pad = acb(tail).union(-acb(tail))
        second_deriv += pad

    return {
        "box": _acb_to_dict(box),
        "degree": degree,
        "first_derivative": _acb_to_dict(deriv_ball),
        "second_derivative": _acb_to_dict(second_deriv),
        "tail_bound": _arb_to_str(tail),
    }


def export_gw_bounds(n: int, t_center: float) -> dict[str, Any]:
    """Export GW character arithmetic bounds for index n at height t_center.

    Placeholder -- requires msaf.gw_* modules to be importable.
    """
    return {
        "index": n,
        "t_center": t_center,
        "derivative_bound": "PLACEHOLDER",
        "character_sum_bound": "PLACEHOLDER",
        "orthogonality": "PLACEHOLDER",
        "note": "Requires msaf.gw_* import; implement when available",
    }


def main():
    """Demo: export premises for a sample box on critical line."""
    if not HAS_MSAF:
        print("msaf not available -- skipping export")
        return

    # Sample box on critical line: s = 1/2 + i*t, t ≈ 14.1347 (first zero)
    # Small box around it for demonstration
    t0 = arb("14.134725141734693790")
    box = acb(arb("0.5"), t0)
    # Radius ~ 1e-10
    box = acb(
        (box.real - arb("1e-10")).union(box.real + arb("1e-10")),
        (box.imag - arb("1e-10")).union(box.imag + arb("1e-10")),
    )

    out_dir = Path(__file__).parent.parent / "lean" / "enclosures"
    out_dir.mkdir(exist_ok=True)

    # Export Moore premises
    premises = export_moore_premises(box, DEFAULT_TAYLOR_DEGREE)
    (out_dir / "moore_premises.json").write_text(json.dumps(premises, indent=2))
    print(f"Exported Moore premises to {out_dir / 'moore_premises.json'}")

    # Export derivative enclosures
    derivs = export_derivative_enclosure(box, DEFAULT_TAYLOR_DEGREE)
    (out_dir / "derivative_enclosures.json").write_text(json.dumps(derivs, indent=2))
    print(f"Exported derivative enclosures to {out_dir / 'derivative_enclosures.json'}")

    # Export GW bounds (placeholder)
    gw = export_gw_bounds(0, float(t0.mid()))
    (out_dir / "gw_bounds.json").write_text(json.dumps(gw, indent=2))
    print(f"Exported GW bounds (placeholder) to {out_dir / 'gw_bounds.json'}")

    print("\nDone. Next steps:")
    print("1. Import these JSON files in Lean (using Lake's data file support or IO)")
    print("2. Replace placeholder `verified_condition_from_enclosure` with actual JSON parsing")
    print("3. Define `sign_budget_shape` / `ZetaStep` from real enclosure data")
    print("4. Prove the encoding correctness theorems (currently `sorry`)")


if __name__ == "__main__":
    main()