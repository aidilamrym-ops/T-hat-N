-- Copyright (C) 2026 Muhammad Aidil Amry.
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.

-- ChronoGeometric_Framework – parsed enclosure data from T-hat-N JSON artifacts
-- Mirrors the verified numerical enclosures stored in lean/enclosures/.

import Mathlib.Data.Nat.Basic

/-- Status of one verification gate in a Guinand-Weil bound record.

    Fields are anti-scalar discipline: a gate is never represented by a bare
    string sentinel such as `"PLACEHOLDER"`, because a sentinel makes an
    unimplemented gate indistinguishable from a verified one at the type
    level. -/
inductive GateStatus where
  | verified
  | unavailable
  | failed
  deriving DecidableEq, Repr, Inhabited

/-- Structure for a complex interval enclosure ball. -/
structure ComplexBall where
  real_mid : String
  real_rad : String
  imag_mid : String
  imag_rad : String

/-- Structure for moore_premises.json – three Banach conditions for the first
    Riemann zero. -/
structure MoorePremises where
  verdict : String
  failed_gate : Option String
  maps_to : Bool
  deriv_excludes_zero : Bool
  lipschitz_K : String
  k_below_one : Bool
  scope : String
  real_mid : String
  real_rad : String
  imag_mid : String
  imag_rad : String
  degree : Nat

/-- Structure for derivative_enclosures.json – first and second derivative
    enclosures. -/
structure DerivativeEnclosures where
  box : ComplexBall
  degree : Nat
  first_derivative : ComplexBall
  second_derivative : ComplexBall

/-- Structure for gw_bounds.json – Guinand-Weil gate record for one zero.

    Only the derivative gate is backed by a producing artifact
    (`msaf.zeta_inversion.xi_derivative_over_ball`). The character-sum and
    orthogonality gates have no producing artifact in this repository and are
    therefore recorded as `unavailable`; they are never reported as verified. -/
structure GwBounds where
  index : Nat
  t_center : String
  derivative_status : GateStatus
  derivative_enclosure : String
  derivative_magnitude : String
  derivative_tail : String
  character_sum_status : GateStatus
  character_sum_bound : String
  orthogonality_status : GateStatus
  orthogonality : String
  degree : Nat
  note : String

/-- Static moore premises constant, copied verbatim from
    `lean/enclosures/moore_premises.json`. -/
def moore : MoorePremises := ⟨
  "PREMISES-HOLD",
  none,
  true,
  true,
  "[3.0691468e-9 +/- 5.72e-18]",
  true,
  "complex-ball analogue of NewtonExistence.moore_box premises (invariance, clean derivative, Lipschitz); the C-to-R transfer is unformalized",
  "0.50000000000000000000000000000000000000000000000000",
  "[1.0000011940475977967324183737218845635652542114258e-10 +/- 1.88e-60]",
  "[14.134725141734692854811328288633376359939575195313 +/- 5.00e-49]",
  "[1.0000444927455581778374948953569401055574417114258e-10 +/- 1.88e-60]",
  12
⟩

/-- Static derivative enclosures constant, copied verbatim from
    `lean/enclosures/derivative_enclosures.json`. -/
def derivative : DerivativeEnclosures := ⟨
  ⟨ "0.50000000000000000000000000000000000000000000000000",
    "[1.0000011940475977967324183737218845635652542114258e-10 +/- 1.88e-60]",
    "[14.134725141734692854811328288633376359939575195313 +/- 5.00e-49]",
    "[1.0000444927455581778374948953569401055574417114258e-10 +/- 1.88e-60]" ⟩,
  12,
  ⟨ "[-3.2371970124285254413619746251039808684772136393909e-18 +/- 3.57e-69]",
    "[1.6030706590564644097723911997377399529796093702316e-13 +/- 2.85e-63]",
    "[0.0013827190892162549620131306582493380119558423757553 +/- 1.01e-53]",
    "[4.7624749155083137265035613059499519650330512376968e-18 +/- 1.83e-68]" ⟩,
  ⟨ "[-0.0016029325283442182568938161324467728263698518276215 +/- 4.01e-53]",
    "[1.1132955720550592867632011540024450368946418166161e-13 +/- 4.17e-63]",
    "[-3.3446515441895652774250975335144605193973643953418e-18 +/- 4.47e-68]",
    "[3.0772113471659224520995436213954832282979623414576e-17 +/- 5.37e-68]" ⟩
⟩

/-- Static Guinand-Weil gate record, copied verbatim from
    `lean/enclosures/gw_bounds.json`.

    The derivative enclosure is a rigorous Arb ball for xi' over the whole
    first-zero box. Its real part is the ball with zero midpoint and radius
    1.61e-13, and its imaginary part is the ball `0.0013827190892162556758`
    with radius 3.81e-23, so the enclosed magnitude is `0.0013827190892162556758`
    with radius 4.74e-23. -/
def gw : GwBounds := ⟨
  0,
  "[14.134725141734692854811328288633376359939575195313 +/- 5.00e-49]",
  GateStatus.verified,
  "[+/- 1.61e-13] + [0.0013827190892162556758 +/- 3.81e-23]j",
  "[0.0013827190892162556758 +/- 4.74e-23]",
  "[1.6030038524827087284e-13 +/- 2.71e-34]",
  GateStatus.unavailable,
  "UNAVAILABLE",
  GateStatus.unavailable,
  "UNAVAILABLE",
  12,
  "derivative gate only: xi' enclosed over the whole first-zero box with msaf.zeta_inversion.xi_derivative_over_ball; character-sum and orthogonality gates have no producing artifact in this repo"
⟩

namespace GwBounds

/-- Number of gates this record reports as verified. This is the only numeric
    quantity the geometric encoding may legitimately carry: it counts
    verified gates instead of asserting them. -/
def verifiedGateCount (g : GwBounds) : Nat :=
  (if g.derivative_status = GateStatus.verified then 1 else 0) +
  (if g.character_sum_status = GateStatus.verified then 1 else 0) +
  (if g.orthogonality_status = GateStatus.verified then 1 else 0)

/-- The recorded record has exactly one verified gate. -/
theorem verifiedGateCount_gw : gw.verifiedGateCount = 1 := by
  decide

/-- Every gate of the recorded record is decided, so no gate is silently
    presumed true. -/
theorem gate_status_recorded :
    gw.derivative_status = GateStatus.verified ∧
    gw.character_sum_status = GateStatus.unavailable ∧
    gw.orthogonality_status = GateStatus.unavailable := by
  exact ⟨rfl, rfl, rfl⟩

end GwBounds

/-- Wrapper structure exporting enclosure data.

    The field names deliberately differ from the constant names (`moore`,
    `derivative`, `gw`) because a projection named `moore` would collide with
    the constant `moore` and make every bare mention ambiguous. -/
structure EnclosureData where
  moorePremises : MoorePremises := moore
  derivativeEnclosures : DerivativeEnclosures := derivative
  gwBounds : GwBounds := gw

#check EnclosureData
