import Mathlib.Data.Set.Basic

open Set

/-- Naïve definition of Russell set – leads to inconsistency. -/

def Russell : Set (Set (Set ℕ)) :=
  {s | s ∉ s}

#check Russell
