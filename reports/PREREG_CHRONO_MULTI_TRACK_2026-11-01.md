# Pre-Registration: Chrono-RH Track 2 (Knowledge Graph) and Track 3 (Dirichlet Coefficient Audit)

Date: 2026-11-01
Registry ID: T-2026-0095 (unified multi-track record)
Authority: `CURRENT_AUTHORITY.md` / `AGENTS.md`

## 1. Purpose and scope

This pre-registration covers two tooling/arithmetic tracks and one consolidated
receipt. Neither track is a new analytic proof of RH, a Weil-positivity result,
a zero-localisation claim, or a matrix-positivity certificate.

### Track 3 - exact Dirichlet coefficient audit

Extend `msaf/chrono_runtime/dirichlet_giant_q.py` with a conductor sweep that:

1. enumerates characters for every modulus in a frozen sweep set;
2. classifies each character as primitive or imprimitive and as real or
   complex;
3. admits only real characters into the exact-integer coefficient path;
4. extracts every admitted value as a strict `fmpz` and enforces
   `chi(n) in {-1, 0, +1}`;
5. enforces the structural-zero gate
   `chi(n) = 0  <=>  gcd(n, q) > 1` for every admitted character and every
   tested `n`;
6. transports each admitted exact block into `LaurentLogicBridgeEngine` as
   exact rational coefficients;
7. records complex characters as `rejected_not_coerced`, never as integers.

Frozen sweep set (default): every modulus `1..60`, plus the stress moduli
`72, 84, 120, 180, 210, 360, 420, 840, 1000`. Frozen `n`-range: `1..128`.
The exact block length, modulus, conductor, primitive flag, and rejection
reasons are recorded in the Track 3 receipt.

### Track 2 - knowledge graph and self-contained renderers

Extend `mcp/t2n/illumina.py` with a real `render_gate_tree_svg` tool and make
the existing dependency and orbit renderers capable of layered and
root-pulling layouts. Add `scripts/chrono_knowledge_graph.py`, which:

1. derives the multi-stage dependency graph from the actual repository
   artefacts (Stage 1-4 modules, tests, pre-registrations, receipts, and
   ledger record IDs);
2. renders a layered dependency map, a root-pulling orbit, a functional gate
   tree, receipt labels, and a compiled HTML dashboard;
3. writes every generated artefact strictly below `mcp/out/` (the untracked
   staging zone) using the existing `guard.write_roots()` allowlist;
4. embeds no external CDN, remote font, remote script, or network reference.

## 2. Frozen decision gates

- **Integer gate:** every admitted character value is an exact `fmpz` in
  `{-1, 0, +1}`. A non-integer, an inexact ball, or a non-zero imaginary part
  on an admitted real character is a hard failure.
- **Structural-zero gate:** for admitted characters, the exact zero pattern
  must equal the exact `gcd(n, q) > 1` pattern. A mismatch is a hard failure.
- **Complex-character gate:** characters with `order > 2` are excluded from the
  integer path and reported as rejected. They are not rounded, projected, or
  coerced.
- **Bridge gate:** every admitted block must construct a
  `LaurentLogicBridgeEngine` without a `StructuralIntegrityViolation`; a float
  coefficient must trigger `StructuralIntegrityViolation` (negative control).
- **Write-zone gate:** all Track 2 generated files stay below `mcp/out/`.
  `reports/` receives only the pre-registered JSON/Markdown receipts.
- **Render gate:** every SVG/HTML artefact is self-contained; no `http://`,
  `https://`, `//cdn`, `src=`, or remote `@import` is permitted in generated
  markup.
- **Honesty gate:** the consolidated receipt reports measured statuses. A
  failing or unrun check is recorded as `FAIL`/`NOT_RUN`, never silently
  upgraded. The pre-existing `FENCE_REGISTRY` drift is reported as it is; this
  pre-registration does not authorise rewriting certified registry entries.

## 3. Deliverables

- `msaf/chrono_runtime/dirichlet_giant_q.py` (extended)
- `msaf/tests/test_dirichlet_sweep.py`
- `mcp/t2n/illumina.py` (extended, including `render_gate_tree_svg`)
- `scripts/chrono_knowledge_graph.py`
- `msaf/tests/test_t2n_illumina.py`
- `reports/chrono_rh_dirichlet_sweep_2026-11-01.json`
- `reports/chrono_rh_multi_track_receipt_2026-11-01.json`
- one append-only record in `ledger/chrono_execution_ledger.jsonl` under
  `T-2026-0095`

## 4. Verification commands

```sh
python -m pytest msaf/tests/test_dirichlet.py msaf/tests/test_dirichlet_giant.py \
  msaf/tests/test_dirichlet_sweep.py -q
python -m pytest msaf/tests/test_t2n_illumina.py msaf/tests/test_mcp_servers.py -q
python -m pytest msaf/tests/test_laurent_bridge.py msaf/tests/test_spectral_lock.py \
  msaf/tests/test_containment_proof.py -q
python scripts/chrono_knowledge_graph.py
cd lean && lake build -q
```

The full `python -m pytest msaf -q -m "not slow"` result is recorded verbatim
in the consolidated receipt. If `msaf/tests/test_fence_registry.py` still fails
on pre-existing hash drift, the receipt must say so and must not claim a
flawless green suite.

## 5. Standing scope limits

- `rh_claim`: `false`
- `weil_positivity_claim`: `false`
- `zero_location_claim`: `false`
- `grh_claim`: `false`
- `stage4_containment_status`: `NOT_VERIFIED` (unchanged; 0 of 3 scaffold
  zeros localized)
- Track 2 is tooling; Track 3 is exact coefficient arithmetic. Neither adds a
  mathematical claim about the Riemann zeta spectrum or the Guinand-Weil
  operator.
