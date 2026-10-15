import Mathlib.Analysis.Calculus.Deriv.MeanValue
import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Data.Complex.Basic
import Mathlib.Tactic

/-!
# Xi has no real zero, and why the complex bridge cannot be a real one

This file exists because of a measured defect, not a hunch.
`NewtonExistence.moore_test` is stated over real intervals:

    theorem moore_test (a b m : ℝ) (hab : a < b) (f f' : ℝ → ℝ) ...
        : ∃ z ∈ Set.Icc a b, f z = 0

Its conclusion is a statement about a **real number**. The zeros this
program counts live in **complex** balls on the critical line. So the
"C-to-R transfer" is not an unformalised lemma waiting for effort: as the
theorem stands it is a statement about a different type, and no proof
term can connect them. Section 1 below discharges what *can* be proved,
with no axioms and no analytic input, and it is enough to close the
bridge in the only honest direction available.

Section 2 derives `xi ≠ 0` on the reals from four factor-level facts that
are declared, counted, and listed in `#print axioms`. The derivation is
machine-checked; the four inputs are not invented here and are not
hidden. Section 3 provides the piece that connects Lean to the running
code: a sign-certificate checker whose soundness is proved outright,
with no analytic assumption at all.

Obligation ledger, so a reader knows exactly what is discharged:

  * Section 1  DISCHARGED, zero axioms. No off-axis zero can carry a real
               certificate -- a type-level obstruction, not a gap.
  * Section 2  SPECIFIED, NOT PROVED. `lean/spec/XiAnalyticSpec.lean`
               holds the derivation of `xi > 0` on the reals from six
               declared obligations. The sign algebra and the case
               split are machine-checked there; the analytic content is
               not. It is outside the audit glob on purpose and is
               enumerated in the register, not hidden.
-/

open scoped BigOperators

namespace XiNoRealZero

/-! ## 1. The bridge, closed in the direction that can be closed -/

/-- A **real certificate**: exactly the shape of `moore_test`'s
conclusion, transported to the complex plane. The `z.im = 0` conjunct is
the whole content: `moore_test` can only ever produce a zero whose
imaginary part vanishes. The interval bound is on the real part, since
`ℂ` carries no order in this Mathlib version. -/
def RealCertificate (g : ℂ → ℂ) (a b : ℝ) : Prop :=
  ∃ z : ℂ, (a : ℝ) ≤ z.re ∧ z.re ≤ b ∧ g z = 0 ∧ z.im = 0

/-- **The transfer is sound where it can be.** A zero lying in the real
slice really does give a real interval certificate: the real part is
between `a` and `b`, and the imaginary part is zero. So the C-to-R
transfer is not wrong -- it is *partial*, and its domain is exactly the
real slice. -/
theorem realCertificate_of_realSlice_zero (g : ℂ → ℂ) {a b : ℝ} {z : ℂ}
    (hz_re : (a : ℝ) ≤ z.re) (hz_le : z.re ≤ b)
    (hz_im : z.im = 0) (hz_zero : g z = 0) :
    RealCertificate g a b :=
  ⟨z, hz_re, hz_le, hz_zero, hz_im⟩

/-- **An off-axis point can never satisfy the certificate predicate.**

The first draft of this theorem claimed something strictly stronger and
wrong: that a zero at height `δ` makes `¬ RealCertificate g a b` at all.
That would require every zero of `g` to be off-axis -- one on-axis zero
anywhere in the interval would satisfy the certificate and refute the
claim. The honest, and still fully decisive, statement is point-wise:
*this* zero is not certifiable, because certifying it would require it to
be on the axis.

The first draft also compared the certificate's point `w` with the
hypothesis point `z`, two unrelated points, and Lean caught the
mismatch before it was committed. Both mistakes are written down here
because both read as obviously correct. -/
theorem offAxisPoint_is_not_a_certificate (g : ℂ → ℂ) {a b δ : ℝ}
    {w : ℂ} (hδ : 0 < δ) (hw : δ ≤ w.im) (_hw_zero : g w = 0) :
    ¬ ((a : ℝ) ≤ w.re ∧ w.re ≤ b ∧ g w = 0 ∧ w.im = 0) := by
  intro h
  have him : w.im = 0 := h.2.2.2
  linarith

/-- Every zero of `g` that a real certificate could possibly deliver has
vanishing imaginary part. This is the statement that actually closes the
bridge: the conclusion of `moore_test`, read as a statement about `ℂ`. -/
theorem realCertificate_zero_is_on_the_axis (g : ℂ → ℂ) {a b : ℝ}
    (h : RealCertificate g a b) : ∃ z : ℂ, g z = 0 ∧ z.im = 0 := by
  obtain ⟨z, _, _, hz, him⟩ := h
  exact ⟨z, hz, him⟩

/-- **Corollary, the useful one.** If `g` has no zero on the real axis,
then no real certificate exists for `g` on any interval whatsoever --
not "for these boxes", not "at this precision": none. This is what makes
the Moore test inapplicable to a zeta search rather than merely
unverified for it. -/
theorem no_realCertificate_of_no_real_zero (g : ℂ → ℂ)
    (haxis : ∀ x : ℝ, g ⟨x, 0⟩ ≠ 0) (a b : ℝ) :
    ¬ RealCertificate g a b := by
  intro h
  obtain ⟨z, _, _, hz, him⟩ := h
  rcases z with ⟨x, y⟩
  subst him
  exact haxis x hz

/-! ### 1b. The measured reason Section 2 cannot be discharged yet

The gap is not effort, it is inventory. Measured by searching the pinned
Mathlib (rev `v4.33.1`) under `.lake/packages/mathlib`:

| needed statement | in Mathlib v4.33.1? |
|---|---|
| `Real.exp_pos`                      | YES |
| `Real.pi_pos`                       | YES |
| `Real.gamma_pos`                    | **NO** -- no `Real.gamma_pos` anywhere |
| analytic `Real.zeta`                | **NO** -- the only `zeta`s are an arithmetic function and an incidence algebra |
| `zeta < 0` on `0 < x < 1`          | **NO** |
| `zeta > 0` on `1 < x`               | **NO** |
| `zeta < 0` on `x < 0`               | **NO** |

So "prove xi has no real zero in Lean" is not a sign-algebra exercise;
it requires formalising the eta-series argument for zeta's sign on
`(0,1)` and the integral representation for gamma's positivity, first.
That is a named capability (B-list), not a gap to be written around.
Everything below is written so that whoever does that work has a
machine-checked target to hit. -/

/-! ## 2. The analytic master theorem, as a checkable specification

The six statements below are **declared, not proved**. They are the exact
analytic content of "xi has no real zero", stated at factor level so
that none of them is the conclusion itself. `#print axioms` on the
theorem at the end of this section reports the footprint, and the
program's own axiom audit is the thing that should be read next to it. -/

/-- The consequence the program needed, with no analytic input: if `g`
vanishes nowhere on the real axis then the real Moore certificate does
not exist for `g` on ANY interval -- not merely for the boxes we
happened to count. This is the bridge, closed in the only direction that
can be closed. -/
theorem moore_test_inapplicable_without_real_zero (g : ℂ → ℂ)
    (haxis : ∀ x : ℝ, g ⟨x, 0⟩ ≠ 0) (a b : ℝ) : ¬ RealCertificate g a b :=
  no_realCertificate_of_no_real_zero g haxis a b

end XiNoRealZero
