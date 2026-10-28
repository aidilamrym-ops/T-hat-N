-- ChronoRiemann module: integrates collapse_to_harmony with a simplified Riemann sign‑budget model

import ChronoNat
import ChronoReduction

open ChronoState

/-- Simplified sign‑budget representation: for each natural number n we produce a list of signs
    (+1) and (‑1) alternating, encoded as a `Shape.space` containing points.
    This mimics the alternating sign behaviour in the Riemann‑Moore boundary analysis. -/

def sign_budget_shape : MyNat → Shape
| MyNat.zero => Shape.space []
| MyNat.succ n =>
    let prev := sign_budget_shape n
    match prev with
    | Shape.space lst => Shape.space (Shape.point :: lst)  -- add a point representing next sign
    | _ => Shape.space [Shape.point]  -- fallback

/-- Simulate a Riemann‑Moore style problem as a ChronoState.
    The numeric component carries the index, the spatial component encodes the sign budget,
    and the time is set to the first successor. -/
def simulate_riemann (n : MyNat) : ChronoState :=
  { value := n,
    shape := sign_budget_shape n,
    time  := Chronon.next Chronon.now }

/-- Instant reduction theorem for the Riemann‑Moore sign‑budget simulation.
    Applying `collapse_to_harmony` collapses the complex sign‑budget shape to a single point
    while preserving the numeric index and the time step. -/

theorem riemann_instant_reduction (n : MyNat) :
    collapse_to_harmony (simulate_riemann n) =
      { value := n,
        shape := Shape.point,
        time  := Chronon.next Chronon.now } :=
  rfl
