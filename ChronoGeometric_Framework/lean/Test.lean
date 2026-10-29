-- Test file: imports all Chrono modules and runs compile-time checks.
-- Build with: lake build Test
--
-- Runtime equality checks are written as `example : lhs = rhs := rfl`
-- so the kernel verifies them at compile time (no BEq instances needed;
-- Shape contains function constructors and cannot derive BEq/DecidableEq).

import NewArithmetic
import ChronoNat
import ChronoReduction
import ChronoBridge
import ChronoSAT
import ChronoRiemann

open MyNat
open ChronoState

-- ============================================================================
-- MyNat arithmetic (kernel-checked)
-- ============================================================================

example : (succ (succ zero) + succ zero : MyNat) = succ (succ (succ zero)) := rfl  -- 2 + 1 = 3
example : (zero + succ (succ zero) : MyNat) = succ (succ zero) := rfl              -- 0 + 2 = 2
example (a : MyNat) : a + zero = a := add_zero a
example (a : MyNat) : zero + a = a := zero_add a

-- ============================================================================
-- ChronoState dynamics (kernel-checked)
-- ============================================================================

def test_state : ChronoState :=
  { value := succ zero,
    shape := Shape.space [Shape.point, Shape.line Shape.point Shape.point],
    time  := Chronon.next Chronon.now }

-- collapse_to_harmony reduces space + next → point, preserving value/time
example : (collapse_to_harmony test_state).shape = Shape.point := rfl
example : (collapse_to_harmony test_state).value = succ zero := rfl
example : (collapse_to_harmony test_state).time = Chronon.next Chronon.now := rfl

-- collapse_to_harmony on a non-space shape is the identity
def test_point_state : ChronoState :=
  { value := succ zero, shape := Shape.point, time := Chronon.next Chronon.now }
example : (collapse_to_harmony test_point_state) = test_point_state := rfl

-- advance grows the shape and steps time
def test_advanced : ChronoState := advance test_state
example : test_advanced.shape = Shape.line test_state.shape Shape.point := rfl
example : test_advanced.time = Chronon.next test_state.time := rfl

-- chrono_add_zero: adding zero preserves value, extends shape/time structurally
example : test_state + (0 : ChronoState) =
  { value := test_state.value,
    shape := Shape.line test_state.shape Shape.point,
    time  := Chronon.next (Chronon.next test_state.time) } := rfl

-- ============================================================================
-- SAT encoding (kernel-checked)
-- ============================================================================

def test_formula : Formula :=
  [ [Lit.pos (succ zero), Lit.neg (succ (succ zero))],
    [Lit.pos (succ (succ zero))],
    [Lit.neg (succ (succ (succ zero)))] ]

def test_sat_state : ChronoState := simulate_sat test_formula
example : (collapse_to_harmony test_sat_state).shape = Shape.point := rfl
example : (collapse_to_harmony test_sat_state).time = Chronon.next Chronon.now := rfl

-- formulaToShape always produces Shape.space
example : ∃ lst, formulaToShape test_formula = Shape.space lst :=
  formulaToShape_is_space test_formula
example : ∃ lst, formulaToShape [] = Shape.space lst :=
  formulaToShape_is_space ([] : Formula)

-- ============================================================================
-- Riemann sign budget (kernel-checked)
-- ============================================================================

def test_riemann_state : ChronoState := simulate_riemann (succ (succ (succ zero)))
example : (collapse_to_harmony test_riemann_state).shape = Shape.point := rfl
example : (collapse_to_harmony test_riemann_state).value = succ (succ (succ zero)) := rfl

example : ∃ lst, sign_budget_shape (succ zero) = Shape.space lst :=
  sign_budget_shape_is_space (succ zero)

-- ============================================================================
-- ZetaStep bridge (kernel-checked)
-- ============================================================================

example : ∃ lst, ZetaStep zero = Shape.space lst := ZetaStep_is_space zero
example : ∃ lst, ZetaStep (succ (succ zero)) = Shape.space lst :=
  ZetaStep_is_space (succ (succ zero))
example := chrono_boundary_harmony (succ (succ zero))

-- ============================================================================
-- Theorem term checks: each named theorem is inhabited (kernel-checked)
-- ============================================================================

example := instant_reduction_theorem (succ zero) [Shape.point]
example := sat_instant_reduction test_formula
example := riemann_instant_reduction (succ (succ zero))
example := collapse_to_harmony_eq [Shape.point] Chronon.now (succ zero)

-- ============================================================================
-- Runtime smoke tests (Repr printouts)
-- ============================================================================

#eval (collapse_to_harmony test_state).shape        -- expect: Shape.point
#eval (simulate_sat test_formula |> collapse_to_harmony).shape
#eval (ZetaStep (succ (succ zero)))                  -- expect: Shape.space [point, point]

#eval IO.println "✓ All Chrono-Geometric Framework tests passed."