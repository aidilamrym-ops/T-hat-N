-- New arithmetic type: myNat – unary natural numbers

inductive MyNat where
  | zero : MyNat
  | succ : MyNat → MyNat
  deriving Repr, Inhabited

namespace MyNat

-- addition defined by recursion on second argument

@[simp]
def add : MyNat → MyNat → MyNat
  | a, zero => a
  | a, succ b => succ (add a b)

instance : HAdd MyNat MyNat MyNat := ⟨add⟩

@[simp] theorem add_zero (a : MyNat) : a + zero = a := rfl
@[simp] theorem zero_add (a : MyNat) : zero + a = a := by
  induction a with
  | zero => rfl
  | succ a ih =>
    rw [show zero + succ a = succ (zero + a) by rfl]
    rw [ih]
    <;> rfl

end MyNat
