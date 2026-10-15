import Mathlib.Tactic

/-!
# SPECIFICATION, NOT PROOF: xi > 0 on the real axis

## Why this file is outside the audited sources

`msaf/tests/test_lean_axiom_audit.py` requires every declaration in
`lean/*.lean` to depend on nothing beyond propext, Classical.choice and
Quot.sound. The derivation below rests on six declared analytic
obligations, so it cannot live there without breaking a rule that exists
for a reason. It lives here instead, in one file, with every assumption
listed, rather than being woven through the audited sources where it
would be harder to see.

Nothing here is claimed as proved. `#print axioms XiAnalyticSpec.xi_pos_on_reals`
is the receipt: it lists the standard three plus the six below.

## Why the obligations are not already in Mathlib

Measured by searching the pinned Mathlib (rev v4.33.1):

| needed | present? |
|---|---|
| `Real.exp_pos`, `Real.pi_pos` | YES |
| `Real.gamma_pos`                  | NO  -- absent everywhere |
| analytic `Real.zeta`              | NO  -- Mathlib's `zeta` is an arithmetic function |
| `zeta < 0` on `0 < x < 1`        | NO  |
| `zeta > 0` on `1 < x`             | NO  |
| `zeta < 0` on `x < 0`             | NO  |

So closing these is a capability: the eta-series argument for zeta's
sign, and the integral representation for gamma's positivity. That is
B-list work, and it is named as such rather than approximated here.
-/

namespace XiAnalyticSpec

open scoped BigOperators

/-- The Riemann zeta on the real line, as an opaque symbol. The
`Real.zeta` of Mathlib v4.33.1 is an arithmetic function, not the
analytic zeta; reusing that name would have been a false friend. -/
axiom zetaReal : ℝ → ℝ

/-- The Gamma function on the real line, likewise opaque. -/
axiom gammaReal : ℝ → ℝ

/-- OBLIGATION 1 of 6: zeta is negative on the negative axis. -/
axiom zetaReal_neg : ∀ x : ℝ, x < 0 → zetaReal x < 0

/-- OBLIGATION 2 of 6: zeta is negative strictly inside `(0,1)`. This
is the one that needs the eta series (`eta > 0` by the alternating
series test, `zeta = eta / (1 - 2^(1-s))` with the denominator
positive there). It is the whole difficulty of the analytic half. -/
axiom zetaReal_mid : ∀ x : ℝ, 0 < x → x < 1 → zetaReal x < 0

/-- OBLIGATION 3 of 6: zeta is positive above 1, from the absolutely
convergent Euler product or the series with `x > 1`. -/
axiom zetaReal_gt_one : ∀ x : ℝ, 1 < x → 0 < zetaReal x

/-- OBLIGATION 4 of 6: gamma is positive on the positive axis, from its
integral representation. -/
axiom gammaReal_pos : ∀ x : ℝ, 0 < x → 0 < gammaReal x

/-- OBLIGATION 5 of 6: the two removable values, needed because the
shifted product below is `0 * infinity` at `x = 1` and because the
endpoint arithmetic is where a naive sign split fails. -/
axiom zetaReal_zero : zetaReal 0 = -1 / 2
axiom gammaReal_one : gammaReal 1 = 1

/-- xi in the **shifted** form used by the Python kernel: the identity
`s * Gamma(s/2) = 2 * Gamma(1 + s/2)` removes Gamma's pole at zero, which
is exactly the repair of the v1.40.0 defect, carried into Lean. Valid
for every real argument except `1`, where the shifted product is
`0 * infinity`; `xiReal 1` is given separately. -/
noncomputable def xiReal (x : ℝ) : ℝ :=
  gammaReal (1 + x / 2) * (x - 1)
    * Real.exp (-(x / 2) * Real.log Real.pi) * zetaReal x

/-- The value at `1`, where the shifted form is singular. -/
noncomputable def xiReal_one : ℝ := 1 / 2

/-- OBLIGATION 6 of 6: the functional equation of xi. Without it the
case `x < 0` cannot be closed by sign algebra at all, because Gamma on
the negative axis alternates sign and no single case covers it. This is
exactly why the Python kernel reflects to `1 - s` instead of evaluating
at negative arguments. -/
axiom xiReal_sub_one : ∀ x : ℝ, xiReal (1 - x) = xiReal x

/-- xi as a total function, with the removable point filled in. -/
noncomputable def xiRealAt (x : ℝ) : ℝ := if x = 1 then xiReal_one else xiReal x

/-- The `x > 1` region, where every factor is positive. Split out so the
trichotomy below reads as a sign table rather than as arithmetic. -/
theorem xi_pos_gt_one (x : ℝ) (hx1 : 1 < x) : 0 < xiReal x := by
  have h_g : 0 < gammaReal (1 + x / 2) := gammaReal_pos _ (by linarith)
  have h_z : 0 < zetaReal x := zetaReal_gt_one x hx1
  have h_e : 0 < Real.exp (-(x / 2) * Real.log Real.pi) := Real.exp_pos _
  have h_xm : 0 < x - 1 := by linarith
  have h1 : 0 < gammaReal (1 + x / 2) * (x - 1) := mul_pos h_g h_xm
  have h2 : 0 < gammaReal (1 + x / 2) * (x - 1)
      * Real.exp (-(x / 2) * Real.log Real.pi) := mul_pos h1 h_e
  exact mul_pos h2 h_z

/-- **THE MASTER THEOREM, conditional on the six obligations.**
`xi` is strictly positive on the whole real axis.

Machine-checked here: the shifted definition, the case split into
`x < 0`, `x = 0`, `0 < x < 1`, `x = 1`, `x > 1`, the sign algebra of a
product carrying two negative factors, and the endpoint arithmetic
`xi(0) = 1/2`. Assumed: exactly the six declarations above. None of them
is the conclusion. -/
theorem xi_pos_on_reals (x : ℝ) : 0 < xiRealAt x := by
  by_cases hx1 : x = 1
  · rw [hx1]
    simp only [xiRealAt, xiReal_one]
    norm_num
  · rcases lt_trichotomy x 0 with hlt | hzero | hpos
    · -- x < 0: sign algebra cannot close this case, because Gamma
      -- alternates sign on the negative axis. Reflect to 1 - x > 1 with
      -- the functional equation, exactly as the Python kernel does.
      have hx_ne : 1 - x ≠ 1 := by linarith
      have h_gt : 1 < 1 - x := by linarith
      have h_ref : xiRealAt x = xiReal (1 - x) := by
        simp only [xiRealAt, if_neg hx1, if_neg hx_ne, xiReal_sub_one]
      rw [h_ref]
      exact xi_pos_gt_one (1 - x) h_gt
    · subst hzero
      -- No fact about `log π` is needed: the exponent is `-(0/2) * log π`,
      -- which vanishes because of the zero coefficient, not because of π.
      simp [xiRealAt, xiReal, zetaReal_zero, gammaReal_one, Real.exp_zero]
      norm_num
    · rcases lt_or_ge x 1 with hbelow | hge
      · -- 0 < x < 1. Sign table: gamma > 0, exp > 0, (x-1) < 0,
        -- zeta < 0. Group the two negatives together first, so only
        -- `mul_pos` is ever applied to a positive pair.
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
        have h_id : xiReal x
            = (gammaReal (1 + x / 2) * ((x - 1) * zetaReal x))
              * Real.exp (-(x / 2) * Real.log Real.pi) := by
          simp only [xiReal]
          ring
        rw [xiRealAt, if_neg hx1, h_id]
        exact h_all
      · -- 1 <= x: every factor positive
        rcases lt_or_eq_of_le hge with h_gt | h_eq
        · have h := xi_pos_gt_one x h_gt
          simp only [xiRealAt, if_neg hx1]
          exact h
        · exact absurd h_eq.symm hx1

end XiAnalyticSpec
