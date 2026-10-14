"""Scaffolding: interval-Newton zeta-zero localization + Z3 conformance.

SCOPE (binding): this class localizes individual zeros with ball
arithmetic and cross-checks reported enclosures in Z3. A contained
0.5 inside one zero's enclosure is consistent with the critical line
and proves nothing global about sigma. There is no "universal Scale
Axiom" here: any such axiom would be circular. See
``msaf.zeta_inversion.certify_sigma_one_half`` for the same warning
at the numeric layer. Zeta-backed methods (``localize``,
``check_half_line``, ``z3_confirm_containment``) lazily import
``msaf.zeta_inversion`` and honestly raise ``ModuleNotFoundError``
inside the Navier-Stokes-only isolated workspace; the import gate
itself never depends on it.
"""
from __future__ import annotations

from flint import acb, arb, ctx

__all__ = ["PureRiemannVerify"]


def _reject_float(value, name: str) -> None:
    if isinstance(value, float):
        raise TypeError(f"{name}: float64 leakage refused")


class PureRiemannVerify:
    """Zero-localization harness over exact decimal-string entry points."""

    SCOPE = (
        "local enclosures only; containment of 0.5 is conformance, "
        "not a global proof"
    )

    def __init__(self, prec_bits: int = 256) -> None:
        if isinstance(prec_bits, float):
            raise TypeError("prec_bits: float64 leakage refused")
        if int(prec_bits) <= 0:
            raise ValueError("prec_bits must be positive")
        self.prec_bits = int(prec_bits)

    def _guess(self, re_str: str, im_str: str) -> acb:
        _reject_float(re_str, "re_str")
        _reject_float(im_str, "im_str")
        ctx.prec = self.prec_bits
        re_b = re_str if isinstance(re_str, (arb, acb)) else arb(str(re_str))
        im_b = im_str if isinstance(im_str, (arb, acb)) else arb(str(im_str))
        return acb(re_b, im_b)

    def localize(self, re_str: str, im_str: str, max_iter: int = 20) -> dict:
        """Wrap ``locate_zero``; returns its verdict dict fields as-is.

        ``existence_proven`` is True ONLY for the strict verdict
        ``ZERO-LOCALIZED`` with containment and clean derivative --
        the interval-Newton existence theorem then yields exactly one
        zero in the ball. The ``ZERO-LOCALIZED-AT-PRECISION-FLOOR``
        branch carries no existence claim (it fires on balls that can
        provably contain no zero); callers must check this flag, never
        the verdict prefix alone.
        """
        from msaf.zeta_inversion import locate_zero

        if isinstance(max_iter, float):
            raise TypeError("max_iter: float64 leakage refused")
        result = locate_zero(self._guess(re_str, im_str), int(max_iter))
        return {
            "verdict": result.verdict,
            "iterations": result.iterations,
            "derivative_excludes_zero": result.derivative_excludes_zero,
            "newton_contained": result.newton_contained,
            "existence_proven": bool(
                result.verdict == "ZERO-LOCALIZED"
                and result.newton_contained
                and result.derivative_excludes_zero
            ),
            "global_claim_supported": result.global_claim_supported,
        }

    def check_half_line(self, re_str: str, im_str: str) -> dict:
        """Wrap ``certify_sigma_one_half`` without strengthening its claim."""
        from msaf.zeta_inversion import certify_sigma_one_half

        return certify_sigma_one_half(self._guess(re_str, im_str))

    def z3_confirm_containment(self, re_str: str, im_str: str) -> dict:
        """Double-entry check of the reported real enclosure in Z3.

        Extracts the enclosure's decimal lower/upper bounds (strings
        only, no float) and asks Z3 whether ``lo <= 1/2 <= hi`` holds
        over the Reals. ``sat`` confirms the *reported* enclosure
        contains 0.5; it is a conformance cross-check, not an
        independent proof of anything about zeta zeros.
        """
        import z3
        from msaf.zeta_inversion import locate_zero

        guess = self._guess(re_str, im_str)
        result = locate_zero(guess)
        box = result.sigma_enclosure
        re_box = box.real() if isinstance(box, acb) else box
        lo_s = re_box.lower().str(30, radius=False)
        hi_s = re_box.upper().str(30, radius=False)
        lo, hi = z3.RealVal(lo_s), z3.RealVal(hi_s)
        solver = z3.Solver()
        solver.add(lo <= z3.RealVal("1/2"), z3.RealVal("1/2") <= hi)
        verdict = str(solver.check())
        return {
            "z3_verdict": verdict,
            "contains_half": verdict == "sat",
            "lower": lo_s,
            "upper": hi_s,
            "scope": self.SCOPE,
        }
