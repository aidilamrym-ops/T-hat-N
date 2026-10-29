# Problems Target List

The repository contains a small collection of standalone problem directories under `problems/`.  Each problem is self‑contained (README, Lean source, optional lakefile) and can be **integrated into the MSAF workflow** as a *new target* in the same manner as the ChronoGeometric_Framework.

## Current Problems

| Path | Description |
|------|-------------|
| `problems/theory_137/README.md` | Theory 137 – placeholder for a mathematical conjecture (no Lean code yet). |
| `problems/russells_paradox/README.md` | Russell’s Paradox formalisation. Contains `lean/Russell.lean` and its own `lakefile.toml`. |
| `problems/computational_complexity/README.md` | Overview of computational‑complexity questions (no Lean code). |

## Integration Roadmap (one‑by‑one)

1. **Create pre‑registration** (`reports/PREREG_<PROBLEM>_YYYY-MM-DD.md`) for each problem that will be added to the **FENCE_REGISTRY** as a claim (`T‑<id>` for theorems, `A‑<id>` for audits).
2. **Add Lean source to main repo** (if applicable). For `russells_paradox` copy `lean/` files into the top‑level `lean/` directory, update the main `lakefile.toml` `defaultTargets` list and optionally a dedicated `lean_lib` entry.
3. **Run anti‑circularity gate** on the new Lean files (`make verify`).
4. **Update `reports/FENCE_REGISTRY.md`** with a new entry describing the claim (e.g. `T‑2026‑0064 — Russell’s paradox formalisation`).
5. **Update `reports/DECISION_LOG.md`** with a dated entry noting the addition.
6. **Refresh `reports/AUTHORITY_MANIFEST.json`** hash for `DECISION_LOG.md`.
7. **Push**; CI will verify the new target.

## Prioritisation

- **High priority**: `russells_paradox` – already has Lean code, easy to import and certify.
- **Medium**: `theory_137` – needs new Lean formalisation before registration.
- **Low**: `computational_complexity` – currently documentation only; can become a future research log.

## Next Action (automated)

Create a stub pre‑registration for `russells_paradox` (the only problem with ready Lean code) and add its entry to `reports/FENCE_REGISTRY.md`. The other problems can be added later following the same pattern.
