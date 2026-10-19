import Mathlib.Tactic

/-!
# SPECIFICATION V2, NOT PROOF: xi > 0 on the real axis

This file repairs the abstract specification without rewriting the
historical `lean/spec/XiAnalyticSpec.lean` (pinned by registry
`A-2026-0015`). The historical file is inconsistent: its global axiom
`xiReal_sub_one` together with `xiReal 1 = 0` and `xiReal 0 = 1/2`
lets Lean prove `False`. V2 changes the abstraction boundary:

* `xiReal` is guarded at the removable point `x = 1`, so
  `xiReal 1 = 1/2` instead of `0`;
* `xiReal_sub_one` is stated only for `x < 0`, which is the domain the
  reflection step actually uses (`1 - x > 1`);
* the false and unused `zetaReal_neg` axiom is not carried over.

Remaining limits: `zetaReal` and `gammaReal` are still opaque symbols.
The product form is **not** claimed to be a faithful total model at
negative even integers, where the classical Gamma factor has poles.
This file proves a conditional statement. It is not a proof of the
Riemann hypothesis, not a proof about the actual zeta and Gamma
functions, and not peer review.
-/

namespace XiAnalyticSpecV2

/-- Opaque real zeta symbol. The sign obligations are the assumptions. -/
axiom zetaReal : ℝ → ℝ

/-- Opaque real Gamma symbol. Positivity on the positive axis is assumed. -/
axiom gammaReal : ℝ → ℝ

/-- OBLIGATION: zeta is negative strictly inside `(0,1)`. -/
axiom zetaReal_mid : ∀ x : ℝ, 0 < x → x < 1 → zetaReal x < 0

/-- OBLIGATION: zeta is positive above 1. -/
axiom zetaReal_gt_one : ∀ x : ℝ, 1 < x → 0 < zetaReal x

/-- OBLIGATION: gamma is positive on the positive axis. -/
axiom gammaReal_pos : ∀ x : ℝ, 0 < x → 0 < gammaReal x

/-- OBLIGATION: the removable value at zero. -/
axiom zetaReal_zero : zetaReal 0 = -1 / 2

/-- OBLIGATION: the removable value at one. -/
axiom gammaReal_one : gammaReal 1 = 1

/-- The shifted xi form, total by guarding the removable point `x = 1`.
At `x = 1` the product form would be `0 * gammaReal 0`, so the value is
given separately; V2 makes that guard part of the definition. -/
noncomputable def xiReal (x : ℝ) : ℝ :=
  if x = 1 then 1 / 2
  else
    gammaReal (1 + x / 2) * (x - 1)
      * Real.exp (-(x / 2) * Real.log Real.pi) * zetaReal x

/-- OBLIGATION: the functional equation on the negative axis, where the
reflection step maps `x` to `1 - x > 1`. The statement is deliberately
not global: the historical global form was inconsistent at `x = 0`. -/
axiom xiReal_sub_one : ∀ x : ℝ, x < 0 → xiReal (1 - x) = xiReal x

/-- The `x > 1` region, where every factor is positive. -/
theorem xi_pos_gt_one (x : ℝ) (hx1 : 1 < x) : 0 < xiReal x := by
  have hx_ne : x ≠ 1 := by linarith
  simp only [xiReal, if_neg hx_ne]
  have h_g : 0 < gammaReal (1 + x / 2) := gammaReal_pos _ (by linarith)
  have h_z : 0 < zetaReal x := zetaReal_gt_one x hx1
  have h_e : 0 < Real.exp (-(x / 2) * Real.log Real.pi) := Real.exp_pos _
  have h_xm : 0 < x - 1 := by linarith
  have h1 : 0 < gammaReal (1 + x / 2) * (x - 1) := mul_pos h_g h_xm
  have h2 : 0 < gammaReal (1 + x / 2) * (x - 1)
      * Real.exp (-(x / 2) * Real.log Real.pi) := mul_pos h1 h_e
  exact mul_pos h2 h_z

/-- **MASTER THEOREM, conditional on the obligations above.**
`xi` is strictly positive on the whole real axis, with the `x < 0`
branch closed by reflection to `1 - x > 1`. -/
theorem xi_pos_on_reals (x : ℝ) : 0 < xiReal x := by
  by_cases hx1 : x = 1
  · rw [hx1]
    simp [xiReal]
  · rcases lt_trichotomy x 0 with hlt | hzero | hpos
    · have h_gt : 1 < 1 - x := by linarith
      have h_ref : xiReal x = xiReal (1 - x) := by
        rw [xiReal_sub_one x hlt]
      rw [h_ref]
      exact xi_pos_gt_one (1 - x) h_gt
    · subst hzero
      simp [xiReal, zetaReal_zero, gammaReal_one]
      norm_num
    · rcases lt_or_ge x 1 with hbelow | hge
      · have hx_ne : x ≠ 1 := by linarith
        simp only [xiReal, if_neg hx_ne]
        have h_g : 0 < gammaReal (1 + x / 2) := gammaReal_pos _ (by linarith)
        have h_z : zetaReal x < 0 := zetaReal_mid x hpos hbelow
        have h_e : 0 < Real.exp (-(x / 2) * Real.log Real.pi) :=
          Real.exp_pos _
        have h_xm : x - 1 < 0 := by linarith
        have hm1 : 0 < -(x - 1) := by linarith
        have hm2 : 0 < -zetaReal x := by linarith
        have h_pair : 0 < (x - 1) * zetaReal x := by
          simpa only [neg_mul_neg] using mul_pos hm1 hm2
        have h_GZ : 0 < gammaReal (1 + x / 2) * ((x - 1) * zetaReal x) :=
          mul_pos h_g h_pair
        have h_all : 0 < (gammaReal (1 + x / 2) * ((x - 1) * zetaReal x))
            * Real.exp (-(x / 2) * Real.log Real.pi) := mul_pos h_GZ h_e
        have h_id : gammaReal (1 + x / 2) * (x - 1)
              * Real.exp (-(x / 2) * Real.log Real.pi) * zetaReal x
            = (gammaReal (1 + x / 2) * ((x - 1) * zetaReal x))
              * Real.exp (-(x / 2) * Real.log Real.pi) := by
          ring
        rw [h_id]
        exact h_all
      · rcases lt_or_eq_of_le hge with h_gt | h_eq
        · exact xi_pos_gt_one x h_gt
        · exact absurd h_eq.symm hx1

end XiAnalyticSpecV2
