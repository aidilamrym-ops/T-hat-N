# Matrix-constraint Spectral Analysis Framework (MSAF)

Rigid computational kernel for the MSAF programme by
**Muhammad Aidil Amry** (ORCID 0009-0002-9718-9710).
Every number in this repository is an interval enclosure computed with
[python-flint](https://github.com/fredrik-johansson/python-flint) ball
arithmetic. No floating-point value ever touches the numeric path.

## Reproduce everything

```bash
pip install python-flint matplotlib   # Python 3.14+
python -m pytest msaf -q              # 67 regression tests
python -m msaf.audit --prec 256 --evolve 6 --root-pull 3 --visualize 3 --final-audit
python -m msaf.evolution --replay ledger/msaf_ledger.jsonl --dimension 16
```

The audit writes `ledger/*.jsonl` (SHA-256 chained evidence) and
`reports/spectral_density.{json,png}`. All paths are anchored to the
repository root; nothing escapes to Temp.

## Measured results (256-bit working precision)

| Quantity | Value |
|---|---|
| `N_steps = D_obs / l_P` | `5.44468544329815837306650e+61` (never an integer) |
| `[H,T]` residual, n=16 | contains zero, half-width ~2.4e-77 |
| `T^dag T - I`, `T^n - I` | exact zero (rational 0/1 entries) |
| Weil spectrum `min\|λ\|` | exactly 1 (no exponential decay) |
| `n_crit`, manuscript path `H:=n` | `1.8e31` |
| `n_crit`, measured path | `3.16e60` |
| `ρ₁, ρ₂, ρ₃` real parts | `0.5` ± (3.8e-71, 8.7e-78, 1.2e-71) |
| Ledger replay `V(L)` | True, both ledgers |
| Final seal | True |

## What is proven vs what is postulated

Proven by execution: the grid arithmetic, the operator certificates, the
Weil spectrum in closed form, the three localised zeros with certified
enclosures, the ledger hash chains and their independent replay.

Postulated, not derived: `σ = 0.5` as a universal statement (a finite number
of localised zeros cannot establish it — every result carries
`global_claim_supported = False`); the decay law
`λ_min ~ A·e^(−Bn)` with `B ≈ 0.115` (no measured source inside the
framework; both entropy paths are reported side by side).

See [`msaf/AUDIT.md`](msaf/AUDIT.md) (landmines L1–L35, each executable and
pinned by a test) and [`brain.md`](brain.md) (session memory and Terminus log).

## Layout

- `msaf/` — kernel: precision, constants, grid, certificates, operators,
  Guinand–Weil matrices, budget, zeta inversion, evolution, visualizer,
  Dirichlet bracketing, final audit
- `msaf_core_lattice.py` — the four mandated entry points
- `msaf/tests/` — regression suite
- `ledger/` — append-only evidence chains · `reports/` — integer pixel reports
- `*.md` (root) — manuscript, directives, execution manual, this memory file

## License

MIT — see [LICENSE](LICENSE).
