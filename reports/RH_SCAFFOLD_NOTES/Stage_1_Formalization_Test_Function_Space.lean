import Mathlib.Analysis.Calculus.Deriv.Basic
import Mathlib.Topology.ContinuousMap.Bounded.Basic
import Mathlib.MeasureTheory.Integral.Lebesgue.Basic
import Mathlib.MeasureTheory.Integral.Bochner.Basic
import Mathlib.MeasureTheory.Measure.Lebesgue.Basic
import Mathlib.Order.Interval.Set.Defs

open MeasureTheory Real Filter Set

-- Define the rigid Hilbert subtype for the Guinand-Weil continuous domain

def MSAFTestFunctionSpace : Type :=
  { f : ℝ → ℝ // Continuous f ∧ f 0 = 0 ∧ Tendsto f atTop (nhds 0) }

-- Construct the framework contract for the continuous quadratic form operator
noncomputable def continuous_quadratic_form (K : ℝ → ℝ → ℝ) (f : MSAFTestFunctionSpace) : ℝ :=
  ∫ x in Ioi 0, ∫ y in Ioi 0, f.val x * K x y * f.val y