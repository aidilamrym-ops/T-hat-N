# Adversarial Triage: Three Bridges Under Attack (2026-10-15)

A red-team analysis named three load-bearing joints as the places a
serious adversary would strike: (1) the Leanâ†”Python correspondence,
(2) the Z3 tribunal encodings, (3) the N_steps floor/modulus. Each
was investigated against the code (not against the claims about the
code). Verdicts below are evidence-linked; fixes are in the tree.

## Attack 1: correspondence gap â€” CONFIRMED (with a live instance)

The Standing Disclosure (README:452) already admits correspondence is
locked only where measured. Investigation found the gap is REAL and
instantiated, not theoretical:

- `lean/NewtonExistence.lean` (`moore_test` docstring) claimed to be
  "the complete formal counterpart of the Python counter's soundness
  gate". The counter (`msaf/riemann/counter.py`) counts zeros in
  COMPLEX balls; every theorem in the Lean file is stated over REAL
  intervals. A complex-ball gate has no formal counterpart there.
- `msaf/riemann/moore_premises.py` claimed to verify "the exact
  premises" of `moore_box` while checking them on `acb` balls with
  circular containment. Same â„‚-vs-â„ gap (the Banach principle
  transfers across complete metric spaces, but that transfer is
  itself unformalized).

Neither gap affects any computed number (counts rest on ball
arithmetic + the winding cross-check), but both docstrings asserted
a transfer that does not exist. Fixed at the root:

- `moore_test` docstring now states real-interval analogue status
  with the complex-ball gate explicitly OPEN.
- `verify_moore_premises` returns a `scope` key on every path
  (asserted by `test_moore_premises.py`): complex-ball analogue,
  transfer unformalized.
- Register: MOORE-PREM reclassified to analogue status;
  CORR-MOORE-COMPLEX recorded OPEN (analogue only).
- The closable hard item is mapped, not pretended shut: formalize
  the complex-ball single-step gate (or the â„‚-transfer) in Lean.
  Until then the inventory above is the locked position.

## Attack 2: Z3 loose encoding â€” DEFLECTED (fenced before the attack)

The only Z3 use in this repo is `z3_confirm_containment`
(`msaf/milenium_frontier/pure_rh_strengthen.py`): it asks whether
printed bounds straddle 1/2 and reports `contains_half`, consumed
only by a test asserting the flag plus the scope string. Nothing
treats `sat` as proof of anything (six layers: docstring, SCOPE
constant, dict scope key, test scope assert, frontier-only module,
honest skip in T-hat-N). The cited instance (`anti_turing_tribunal.py)
belongs to another repo and is scope-fenced there.

One genuine imprecision found and fixed while checking: the
docstring said "decimal lower/upper bounds" but `.lower()/.upper()`
return balls and `.str(30, radius=False)` prints midpoints -- the
strings are 30-digit approximations, flippable within ~1e-30 of the
boundary. Consequence of a flip: a conformance flag, never a proof.
Docstring corrected to say exactly that.

## Attack 3: N_steps floor/modulus â€” DEFLECTED (dead code, exact floor)

- The `mod N_steps` branch the analysis fears lives in a REJECTED
  Phase-2 blueprint (AUDIT.md L26-L29, L322-L337), not in this tree:
  `int(numpy.floor(N_steps))` overflows, the branch never executes,
  and our visualizer keeps everything in Arb with certified pixels
  or loud `AmbiguousPixel`s.
- In this tree `floor(N_steps)` is computed by EXACT rational
  arithmetic (`fmpz` numerator//denominator, `test_msaf.py:421`
  pins it) -- no float remainder is dropped by rounding; the
  non-integer remainder simply isn't used as a modulus anywhere
  because NOTHING takes mod floor(N): N_STEPS is consumed only as a
  ball (capacity equations, entropy comparisons, display, log2
  ratios). Grep-verified: no cyclic/modular operator on n_floor
  exists in `msaf/`.
- The `mod 2^32` in the pixel report is display quantization with
  full 206-bit addresses carried in JSON -- exact integer `mod`,
  no spectral content claimed.

## Standing rule this triage enforces

Bridges get per-item inventory (locked-by-test vs open-analogue),
never blanket correspondence claims. The next bridge to close by
construction is the complex-ball Moore gate in Lean; everything else
above is sealed by documentation + executable scope keys.


