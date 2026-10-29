-- ChronoSAT module: simple encoding of SAT formulas into ChronoState and instant reduction via collapse_to_harmony

import ChronoNat
import ChronoReduction

open ChronoState

/-- Boolean literal represented by a variable index (MyNat) and polarity. -/
inductive Lit where
  | pos : MyNat → Lit   -- positive literal
  | neg : MyNat → Lit   -- negated literal
  deriving Repr, Inhabited

/-- Clause is a list of literals (disjunction). -/
abbrev Clause := List Lit

/-- Formula in CNF is a list of clauses (conjunction). -/
abbrev Formula := List Clause

namespace Lit

/-- Encode a literal as a simple Shape. For illustration we map each literal to a point. -/
def toShape : Lit → Shape
  | pos _ => Shape.point
  | neg _ => Shape.point

end Lit

/-- Encode a clause as a line connecting the shapes of its literals.
    Empty clause maps to a point (unsatisfiable). -/
def clauseToShape : Clause → Shape
  | [] => Shape.point
  | l :: ls =>
    let rest := clauseToShape ls
    Shape.line (Lit.toShape l) rest

/-- Encode an entire formula as a space containing the shapes of its clauses. -/
def formulaToShape : Formula → Shape
  | [] => Shape.space []
  | c :: cs =>
    let rest := formulaToShape cs
    match rest with
    | Shape.space lst => Shape.space (clauseToShape c :: lst)
    | _ => Shape.space [clauseToShape c]  -- fallback, should not happen

/-- Lemma: `formulaToShape` always produces `Shape.space`. -/
theorem formulaToShape_is_space (f : Formula) :
    ∃ lst, formulaToShape f = Shape.space lst := by
  induction f with
  | nil => exact ⟨[], rfl⟩
  | cons c cs ih =>
    rcases ih with ⟨lst, hrest⟩
    exact ⟨clauseToShape c :: lst, by
      rw [formulaToShape, hrest]⟩

/-- Simulate a SAT problem as a ChronoState.
    The numeric value is set to zero (placeholder). -/
def simulate_sat (f : Formula) : ChronoState :=
  { value := MyNat.zero,
    shape := formulaToShape f,
    time  := Chronon.next Chronon.now }

/-- Instant reduction theorem: applying `collapse_to_harmony` to any SAT simulation state
    instantly collapses the spatial component to a single point, preserving the numeric
    value and the time step. -/
theorem sat_instant_reduction (f : Formula) :
    collapse_to_harmony (simulate_sat f) =
      { value := MyNat.zero,
        shape := Shape.point,
        time  := Chronon.next Chronon.now } := by
  rcases formulaToShape_is_space f with ⟨lst, h⟩
  simp [simulate_sat, h, collapse_to_harmony]

-- ============================================================================
-- ENCODING CORRECTNESS (the real work -- currently SORRY)
-- ============================================================================

/-- Boolean assignment: maps variable index to truth value. -/
def Assignment := MyNat → Bool

/-- Evaluate a literal under an assignment. -/
def eval_lit (α : Assignment) (l : Lit) : Bool :=
  match l with
  | Lit.pos n => α n
  | Lit.neg n => !(α n)

/-- Evaluate a clause (disjunction) under an assignment. -/
def eval_clause (α : Assignment) (c : Clause) : Bool :=
  c.foldr (fun l acc => eval_lit α l || acc) false

/-- Evaluate a formula (conjunction of clauses) under an assignment. -/
def eval_formula (α : Assignment) (f : Formula) : Bool :=
  f.foldr (fun c acc => eval_clause α c && acc) true

/-- A formula is satisfiable iff there exists an assignment making it true. -/
def Sat (f : Formula) : Prop :=
  ∃ (α : Assignment), eval_formula α f = true

