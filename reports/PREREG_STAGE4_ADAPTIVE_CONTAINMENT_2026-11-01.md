# Pre-registration: Stage 4 Adaptive Containment Proof

**Date:** 2026-11-01  
**Artifact:** `msaf/chrono_runtime/stage4_containment_proof.py`  
**Purpose:** Fix Newton-IMAGE-ESCAPED verdict by implementing adaptive initial ball radius that rigorously contains the actual zero given approximate t-values.

## Problem Statement
Current Stage 4 receipt shows `NOT_VERIFIED` with all three test zeros (t=14.134725, 21.022040, 25.010858) returning `NEWTON-IMAGE-ESCAPED`. Root cause: the initial ball radius (5e-13) is orders of magnitude smaller than the offset between approximate t-values and actual zero locations (1.42e-7 to 4.20e-7). The Newton method correctly reports the image escapes because the actual zero lies outside the initial ball.

## Solution
1. Increase initial ball radius from 5e-13 to 1e-6 (covers max offset 4.20e-7 with safety margin).
2. Verify derivative enclosure still excludes zero at larger radius (confirmed: tail ~1e-9 to 1e-12).
3. Newton iteration will then rigorously contract from ~1e-6 to precision floor (~1e-112), achieving `ZERO-LOCALIZED` with `topological_containment_verified = true`.
4. Banach contraction gate already passes (Lipschitz K ~ 1e-7 to 1e-10).
5. Precision ramp from 512 to 1024 bits retained for final verification.

## Acceptance Criteria
1. `reports/chrono_rh_stage4_receipt_2026-11-01.json` shows `status: "CERTIFIED"` with `localized_zeros_count = tested_zeros_count = 3`.
2. All three zero reports show `verdict: "ZERO-LOCALIZED"` and `sigma_is_on_half_line: true`.
3. `topological_containment_verified: true` and `banach_contraction_verified: true`.
4. `max_radius <= 1e-12` (threshold).
5. `python -m pytest msaf/tests/test_containment_proof.py -q` passes.
6. `lake build` passes with zero `sorry`/`unsafe`/`axiom`.

## Boundary
No RH claim. Localization of 3 specific zeros with rigorously certified enclosures only. Does not prove all zeros on critical line.