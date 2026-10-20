import spec_v3.XiAnalyticFaithful
import spec_v4.XiUnconditional

/-!
# V5: unconditional positivity of xi on the real axis

V3's `XiAnalyticFaithful.xi_pos_on_reals` proves positivity of the completed
xi from an explicit midpoint sign hypothesis `hmid`.  V4's `hmid` closes that
hypothesis unconditionally for Mathlib's `completedRiemannZeta` on `(0, 1)`.
This file applies the two and adds no new analytic content.

This is not a proof of the Riemann hypothesis and says nothing about zero
locations.  The spectral H1/engine-B campaign and the V6 finite-lattice
bridge are separate packages and are not used here.
-/

namespace XiPosUnconditional

/-- **V5.** The completed xi is strictly positive on the whole real axis,
unconditionally: V3's explicit `hmid` hypothesis is discharged by V4. -/
theorem xi_pos_on_reals_unconditional (x : ℝ) : 0 < XiAnalyticFaithful.xiReal x :=
  XiAnalyticFaithful.xi_pos_on_reals hmid x

end XiPosUnconditional
