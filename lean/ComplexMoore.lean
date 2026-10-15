import Mathlib.Data.Complex.Basic
import Mathlib.Tactic

/-!
# Complex Moore / Rouche: architecture, and the one lemma that keeps the sign

## What is proved here, and what is only specified

The running Python kernel (`msaf/riemann/moore_premises.py`) already does
the right thing about widening: it forms the tail enclosure and widens
symmetrically, `acb(tail).union(-acb(tail))`, then asks the *widened*
enclosure whether it contains zero. A containment test on the widened
enclosure cannot be fooled by a large tail: the tail is already inside
the question being asked.

The lemma below is about the shortcut one is tempted to take instead, and
it is the reason the shortcut is banned: a derivative enclosure
`a ± r` widened by a tail budget `T` still excludes zero **iff the budget
is smaller than the distance to zero**. Below that threshold a sign test
is sound; above it, a sign test silently certifies a derivative that may
vanish inside the box. `widen_loses_zero_above_budget` is the exact
statement of the failure, and it is proved, not asserted.

Everything about complex balls themselves is *specified*, not proved.
Mathlib has no complex interval arithmetic in this pin, so the ball
algebra is declared as an interface and the obligations that would
discharge it are written down one by one. A spec that pretended to be a
proof would be exactly the failure mode this program exists to catch.

## The interface a complex-ball development must discharge

  OB-C1  the ball is closed and bounded, with `radius ≥ 0`;
  OB-C2  `centre ∈ ball` (nonempty);
  OB-C3  point containment is decidable and means `|z - c| ≤ r`;
  OB-C4  `add`/`mul` are exact interval extensions -- radius
         non-decreasing, i.e. `radius (x ⊕ y) ≥ |x.r - y.r|`
         (Minkowski) and `≥ x.r` when one factor is a point;
  OB-C5  Symmetric Minkowski widening is a valid enclosure:
         `widen e T ⊇ e` for `T ≥ 0`, and
         `radius (widen e T) = radius e + T`;
  OB-C6  `derivative_excludes_zero e` must be decided on the WIDENED
         enclosure, never on the raw one;
  OB-C7  uniqueness/existence in ℂ needs a completeness argument
         (Moore's theorem in ℂ, or Rouche with a winding number) --
         Mathlib has neither, and `NewtonExistence.moore_test` is real.

OB-C7 is the reason this file cannot finish the job: it is a genuine
theorem, not bookkeeping.
-/

namespace ComplexMoore

open scoped BigOperators

/-! ## Part 1. The sign-budget lemma (fully proved, no axioms) -/

/-- A real enclosure as a closed interval. Complex balls reduce to this
per component once the ball algebra of OB-C4 is in place. -/
def Encl (lo hi : ℝ) : Set ℝ := Set.Icc lo hi

/-- Symmetric Minkowski widening: add the tail budget `T` to both ends.
This is exactly what `acb(tail).union(-acb(tail))` computes in the
Python kernel. -/
def widen (lo hi T : ℝ) : Set ℝ := Set.Icc (lo - T) (hi + T)

/-- **Widening is a valid enclosure, provided the budget is
non-negative.** Sound in one direction only; that is the point of OB-C5. -/
theorem widen_contains (lo hi T x : ℝ) (hT : 0 ≤ T) (hx : x ∈ Encl lo hi) :
    x ∈ widen lo hi T := by
  have h1 : lo - T ≤ lo := by linarith
  have h2 : hi ≤ hi + T := by linarith
  exact ⟨le_trans h1 hx.1, le_trans hx.2 h2⟩

/-- **THE BUDGET THEOREM.** A symmetrically widened enclosure still
excludes zero exactly when the tail budget did not reach the distance to
zero. Every sign-based shortcut in this kernel must cite this lemma or
test containment on the widened enclosure; there is no third option. -/
theorem zero_excluded_iff_budget (lo r T : ℝ) (hr : 0 ≤ r)
    (hlo : 0 < lo - r) :
    0 ∉ widen (lo - r) (lo + r) T ↔ T < lo - r := by
  constructor
  · intro h
    by_contra hnot
    have hT : lo - r ≤ T := le_of_not_gt hnot
    have hmem : (0 : ℝ) ∈ widen (lo - r) (lo + r) T := by
      constructor <;> linarith
    exact h hmem
  · intro h
    intro hmem
    have h1 : lo - r - T ≤ 0 := hmem.1
    linarith

/-- The failure mode, stated so it cannot be rediscovered by accident:
above the budget, zero re-enters the widened enclosure even though the
un-widened one excluded it. -/
theorem widen_loses_zero_above_budget (lo r T : ℝ) (hr : 0 ≤ r)
    (hlo : 0 < lo - r) (hT : lo - r ≤ T) :
    (0 : ℝ) ∈ widen (lo - r) (lo + r) T := by
  constructor <;> linarith

/-- Corollary in the shape the kernel actually needs: a derivative
enclosure `a ± r` whose tail budget `T` is strictly below `a - r` still
excludes zero after symmetric widening. -/
theorem derivative_exclusion_survives_budget (a r T : ℝ) (hr : 0 ≤ r)
    (hT : 0 ≤ T) (hbudget : T < a - r) :
    (0 : ℝ) ∉ widen (a - r) (a + r) T :=
  (zero_excluded_iff_budget a r T hr (by linarith)).mpr hbudget

/-! ## Part 2. The complex-ball interface, specified and not proved -/

/-- A complex ball. Declared as a bare record so the obligations are
visible rather than hidden behind an opaque Mathlib type that does not
exist. -/
structure CplxBall where
  centre : ℂ
  radius : ℝ
  radius_nonneg : 0 ≤ radius

/-- OB-C3, stated: point containment. The intended reading is
`‖z - c‖ ≤ r`, expressed with the norm because the ball algebra itself
is exactly what is missing. -/
def CplxBall.contains (b : CplxBall) (z : ℂ) : Prop :=
  ‖z - b.centre‖ ≤ b.radius

/-- **A ball entirely `δ` above the axis has no real point**, so the real
Moore test cannot be pointed at it. This is the box-level form of the
obstruction proved in `XiNoRealZero`.

Two earlier drafts of this lemma were wrong, and the kernel rejected
both. The first claimed a ball of positive imaginary half-height misses
the axis: false, since a ball centred ON the axis with any positive
radius touches it, and `0 < r` with `0 ≤ r` is not a contradiction. The
second added a separation `r < δ` and was false for a different reason:
`δ` says nothing about where the centre is, and `r = 0` satisfies every
hypothesis while `z.im = 0` holds too. What is true is the separation of
the WHOLE ball from the axis, which is what the winding computation
actually certifies per box. -/
theorem offaxis_ball_avoids_axis {B : Set ℂ} {δ : ℝ} (hδ : 0 < δ)
    (hB : ∀ z ∈ B, δ ≤ z.im) : ∀ z ∈ B, z.im ≠ 0 := by
  intro z hz
  have h := hB z hz
  linarith

end ComplexMoore
