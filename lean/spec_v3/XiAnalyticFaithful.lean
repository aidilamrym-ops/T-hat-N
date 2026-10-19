import Mathlib.NumberTheory.LSeries.RiemannZeta
import Mathlib.NumberTheory.LSeries.Dirichlet
import Mathlib.Analysis.SpecialFunctions.Gamma.Deligne
import Mathlib.Analysis.Complex.Order
import Mathlib.Tactic

/-!
# FAITHFUL SPECIFICATION V3: xi from Mathlib's completed zeta

This file replaces the opaque `zetaReal`/`gammaReal` abstraction of
`lean/spec_v2/XiAnalyticSpecV2.lean` with Mathlib's actual
`completedRiemannZeta`, and proves the functional equation unconditionally.

For `x : ℝ`, `xiReal x` is the real part of

```text
1/2 * x * (x - 1) * completedRiemannZeta (x : ℂ)
```

with the removable points `x = 0` and `x = 1` guarded to `1/2`.  This is the
standard completed-xi expression on the real axis.  The real part is used
because the codomain here is `ℝ`; no separate realness lemma for
`completedRiemannZeta` on the real axis is claimed.

The only unproved analytic input is `hmid`, the sign of completed zeta on
`(0, 1)`.  It is an explicit hypothesis of `xi_pos_on_reals`, not a global
declaration.  Consequently the axiom footprint of the master theorem is
exactly the three standard Lean axioms, with no project-specific axiom.

Limits: this is not a proof of the Riemann hypothesis, not a proof that the
midpoint sign hypothesis holds, and not peer review.  The functional equation
and the `x > 1` positivity are proved from Mathlib.
-/

noncomputable section

open Complex
open scoped ComplexOrder

namespace XiAnalyticFaithful

/-- Deligne's Gamma factor is a positive real on the positive axis. -/
lemma gammaR_pos_of_pos {x : ℝ} (hx : 0 < x) : 0 < Gammaℝ (x : ℂ) := by
  rw [Gammaℝ_def]
  have h1 : 0 < (Real.pi : ℂ) ^ (-(x : ℂ) / 2) := by
    have harg : ((-x / 2 : ℝ) : ℂ) = -(x : ℂ) / 2 := by
      push_cast
      ring
    rw [← harg, ← Complex.ofReal_cpow Real.pi_nonneg]
    rw [Complex.pos_iff]
    constructor
    · simpa using Real.rpow_pos_of_pos Real.pi_pos (-x / 2)
    · simp
  have h2 : 0 < Complex.Gamma ((x : ℂ) / 2) := by
    have harg : (x : ℂ) / 2 = ((x / 2 : ℝ) : ℂ) := by
      push_cast
      ring
    rw [harg, Complex.Gamma_ofReal]
    rw [Complex.pos_iff]
    constructor
    · simpa using Real.Gamma_pos_of_pos (by positivity : (0 : ℝ) < x / 2)
    · simp
  exact mul_pos h1 h2

/-- Completed zeta is a positive complex number for real `x > 1`.

This is proved, not assumed: the Dirichlet zeta is positive above `1`,
`Gammaℝ` is positive on the positive axis, and `completedRiemannZeta` is the
product of the two away from `0`. -/
lemma completedZeta_pos_of_one_lt {x : ℝ} (hx : 1 < x) :
    0 < completedRiemannZeta (x : ℂ) := by
  have hx0 : (0 : ℝ) < x := by linarith
  have hxne : (x : ℂ) ≠ 0 := by exact_mod_cast ne_of_gt hx0
  have hgamma_ne : Gammaℝ (x : ℂ) ≠ 0 :=
    Gammaℝ_ne_zero_of_re_pos (by simpa using hx0)
  have hz : 0 < riemannZeta (x : ℂ) := by
    simpa using riemannZeta_pos_of_one_lt hx
  have hdef := riemannZeta_def_of_ne_zero (s := (x : ℂ)) hxne
  rw [eq_div_iff hgamma_ne] at hdef
  have hcomp : completedRiemannZeta (x : ℂ) =
      Gammaℝ (x : ℂ) * riemannZeta (x : ℂ) := by
    rw [← hdef, mul_comm]
  rw [hcomp]
  exact mul_pos (gammaR_pos_of_pos hx0) hz

/-- The completed-xi expression on the real axis, with removable points
guarded.  At `x = 0` and `x = 1` the value is `1/2`. -/
noncomputable def xiReal (x : ℝ) : ℝ :=
  if x = 0 ∨ x = 1 then 1 / 2
  else (1 / 2 : ℝ) * x * (x - 1) * (completedRiemannZeta (x : ℂ)).re

/-- The functional equation, proved from Mathlib's completed-zeta symmetry
`completedRiemannZeta (1 - s) = completedRiemannZeta s`. -/
lemma xiReal_one_sub (x : ℝ) : xiReal (1 - x) = xiReal x := by
  by_cases hx0 : x = 0
  · subst hx0
    simp [xiReal]
  by_cases hx1 : x = 1
  · subst hx1
    simp [xiReal]
  have h1x_not : ¬ (1 - x = 0 ∨ 1 - x = 1) := by
    rintro (h | h)
    · have : x = 1 := by linarith
      exact hx1 this
    · have : x = 0 := by linarith
      exact hx0 this
  have hx_not : ¬ (x = 0 ∨ x = 1) := by
    rintro (h | h) <;> contradiction
  have hc : completedRiemannZeta ((1 - x : ℝ) : ℂ) =
      completedRiemannZeta (x : ℂ) := by
    have h := completedRiemannZeta_one_sub (x : ℂ)
    simpa using h
  simp only [xiReal, if_neg h1x_not, if_neg hx_not]
  rw [hc]
  ring

/-- Positivity above `1`, where every factor is positive. -/
lemma xi_pos_gt_one (x : ℝ) (hx : 1 < x) : 0 < xiReal x := by
  have hx_not : ¬ (x = 0 ∨ x = 1) := by
    rintro (h | h) <;> linarith
  simp only [xiReal, if_neg hx_not]
  have hpre : 0 < (1 / 2 : ℝ) * x * (x - 1) := by positivity
  have hcomp : 0 < (completedRiemannZeta (x : ℂ)).re :=
    (Complex.pos_iff.mp (completedZeta_pos_of_one_lt hx)).1
  exact mul_pos hpre hcomp

/-- Positivity strictly inside `(0, 1)`, conditional on the explicit midpoint
sign hypothesis. -/
lemma xi_pos_below_one
    (hmid : ∀ x : ℝ, 0 < x → x < 1 →
      (completedRiemannZeta (x : ℂ)).re < 0)
    (x : ℝ) (hx0 : 0 < x) (hx1 : x < 1) : 0 < xiReal x := by
  have hx_not : ¬ (x = 0 ∨ x = 1) := by
    rintro (h | h) <;> linarith
  simp only [xiReal, if_neg hx_not]
  have hpre_neg : (1 / 2 : ℝ) * x * (x - 1) < 0 := by nlinarith
  have hcomp_neg : (completedRiemannZeta (x : ℂ)).re < 0 := hmid x hx0 hx1
  have h1 : 0 < -((1 / 2 : ℝ) * x * (x - 1)) := neg_pos.mpr hpre_neg
  have h2 : 0 < -(completedRiemannZeta (x : ℂ)).re := neg_pos.mpr hcomp_neg
  have hprod : 0 < (-((1 / 2 : ℝ) * x * (x - 1))) *
      (-(completedRiemannZeta (x : ℂ)).re) := mul_pos h1 h2
  simpa [neg_mul_neg] using hprod

/-- **MASTER THEOREM (conditional on one explicit midpoint sign input).**
The completed xi is strictly positive on the whole real axis.

The `x < 0` branch is reflected to `1 - x > 1` by `xiReal_one_sub`; the
endpoints are guarded; the `x > 1` branch is proved from Mathlib.
-/
theorem xi_pos_on_reals
    (hmid : ∀ x : ℝ, 0 < x → x < 1 →
      (completedRiemannZeta (x : ℂ)).re < 0)
    (x : ℝ) : 0 < xiReal x := by
  rcases lt_trichotomy x 0 with hlt | hzero | hpos
  · have hgt : 1 < 1 - x := by linarith
    rw [← xiReal_one_sub x]
    exact xi_pos_gt_one (1 - x) hgt
  · subst hzero
    simp [xiReal]
  · rcases lt_trichotomy x 1 with hlt1 | heq1 | hgt1
    · exact xi_pos_below_one hmid x hpos hlt1
    · subst heq1
      simp [xiReal]
    · exact xi_pos_gt_one x hgt1

end XiAnalyticFaithful
