# Scope notice (binding, read first)

A draft title for this file proposed an "adversarial metrological
refutation" of an external party's hydrodynamics. That title is
WITHHELD. This workspace holds no verified source for any external
claim of the form (f != 0, t -> 1-), and finite-lattice measurements
cannot refute continuum claims they do not formalize. This document
therefore reports measured T-hat-N results only, scoped to the
discrete framework that produced them. It refutes no external work.

# Finite-Lattice Hydrodynamics: Measured Metrology Results (v1.7.6)

## 1. What was measured

Pure (f = 0) viscous evolution on periodic T^3_N lattices under 256-bit
ball arithmetic, zero float64, Planck-tick time accounting:

- Sequential Godunov splitting (advect-then-diffuse): kinetic energy
  contracts strictly every step; 125/125 viscous-path tests green.
- Chorin restoring projection (dP = (rho/dt) div u*): divergence balls
  contain exact zero after every step, including violent rotation
  fields with tr(G^2) != 0.
- Adaptive precision ramp: 128-bit jumps past the 1e-72 wire, 1024-bit
  hard cap via ResolutionAlarm. 256-bit rotation run trips cleanly at
  step 3; 384-bit run completes 10 steps with radii at 1e-100.
- Multi-grid pivots: CERTIFIED_POSITIVE on N = 16, 32, 64 (262,144
  cells), half-widths 1.727233714e-77.
- 3-grid convergence: observed order 2.14 -> 2.03 against theory 2.0
  (manufactured periodic solution, N = 4/8/16).
- Inviscid scaling: D(nu) linear at 10.0000x/decade over 1e-1..1e-4;
  nu = 0 refused at construction.
- Periodic-box tails: background-free quotient 1.9519 vs 2.0 theory,
  far-field contamination 0.61%, all radii < 1e-70 over N = 4..64.

## 2. What is NOT claimed

- No claim about global regularity of continuum Navier-Stokes.
- No claim about any third party's results, asymptotic or otherwise.
- The Lean 4 blueprint (`lean/NavierStokesCore.lean`) is a structural
  formalization of the finite lattice, not a regularity proof.

## 3. Reproduction

Suite at seal: main `137 passed`, isolated `34 passed`, exit 0.
Commit range dcae3a2..bb34b52, tags v1.7.5-alpha / v1.7.6-alpha.
