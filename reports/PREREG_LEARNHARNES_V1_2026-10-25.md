# Pra-registrasi Learnharness v1 — simple deterministic stub

**Status:** PRE‑REG, locked before any code.  Intended to replace the prototype with a minimal, certified learning engine that does not use floats, numpy, or external ML libraries.  The engine stores the length of training data and returns an identity matrix of appropriate size on `predict`.  No claim of real‑world performance; only deterministic behavior.

## Locked parameters

- **Model:** deterministic `LearnEngine` (no randomness).
- **Arithmetics:** exact integer/`Fraction` only.
- **No imports:** `numpy`, `torch`, `scipy`, `float` literals or calls.
- **Receipt schema:** `msaf.learnharness_v1.v1`.
- **Registry slot:** `A-2026-0050` (next free after existing entries).

## Files

| Path | Role |
|---|---|
| `msaf/learnharness_v1.py` | implementation |
| `msaf/tests/test_learnharness_v1.py` | guard |
| `reports/learnharness_v1_2026-10-25.json` | receipt |
| `reports/PREREG_LEARNHARNES_V1_2026-10-25.md` | prereg file |

All hashes will be recorded in the receipt and later in `FENCE_REGISTRY.md`.
