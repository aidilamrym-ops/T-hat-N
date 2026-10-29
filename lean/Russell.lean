import Mathlib.Data.Set.Basic

open Set

/-- Naïve definition of Russell set – leads to inconsistency. -/

def Russell : Set ℕ := {n | n = 0}

#check Russell

