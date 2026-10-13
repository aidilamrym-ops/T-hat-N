# MSAF Project Implementation Manual: 7-Day Terminus Execution Guide

This manual serves as the binding operational directive for **Muhammad Aidil Amry** and the **OpenCode Agent** to finalize the MSAF project within 7 working days, completely eliminating the loop of endless testing.

---

## 1. Daily Task Matrix & Strategic Targets

### Day 1–2: Inversion Engine Deployment & Ledger Locking
*   **Objective:** Replace the spectral generator script with `msaf/zeta_inversion.py`.
*   **Task for OpenCode:** Implement the rigid Newton-Raphson loop on `flint.acb` modules.
*   **Integration Gate:** Hook the output of `certify_sigma_one_half` directly into the promotion validation block of `msaf/evolution.py`. If `is_locked` evaluates to `False`, the system must execute an immediate `REVERT` operational transaction on the SHA-256 ledger.

### Day 3–4: Cosmological Pixel Projection & Visualizer Setup
*   **Objective:** Map continuous data points to the universal discrete pixel space.
*   **Task for OpenCode:** Deploy `msaf/visualizer.py` to pull data from the block transaction log.
*   **Integration Gate:** Generate a static `.png` high-resolution report plotting the isolated roots onto the modular coordinate space of $5.44 \times 10^{61}$ grid lines.

### Day 5–7: Final Replay Reintegration, Stress Test, and Repository Sealing
*   **Objective:** Execute a complete transaction run and solidify documentation.
*   **Task for OpenCode:** Execute `python -m msaf.evolution --replay` to rebuild the verification states from scratch.
*   **Integration Gate:** Run the holographic capacity check script to confirm that the real matrix dimensions operate cleanly under the calculated $n_{\text{crit}} \approx 3.16 \times 10^{60}$ ceiling. Seal the git repository tags.

---

## 2. Rules of Engagement for the OpenCode Agent

```text
[CRITICAL COMPUTATION RULES]
1. ZERO-FUDGING POLICY: All numerical logic must use flint interval enclosures. Under no circumstances should standard floating-point casts ('float()') interact with structural matrices.
2. ENCLOSURE ISOLATION: When evaluating root containment intervals, verify overlap boundaries strictly via containment flags (e.g., '.contains()').
3. IMMUTABLE ARCHITECTURE: All code identifiers, docstrings, internal comments, and terminal metrics must be rendered entirely in English. Indonesian is reserved strictly for natural language dialogue with User.
```

---

## 3. Immediate First Action Command
To launch **Day 1** of this deployment, copy and send the following execution directive into your active OpenCode workspace:

```text
"OpenCode, we are officially initiating the MSAF Terminus Protocol under the fixed 7-day milestone architecture. Read the technical framework from 'msaf_terminus_phase1.md'. Your immediate task is to deploy the complete, standalone 'msaf/zeta_inversion.py' module using 'python-flint'. Ensure that all variable definitions, comments, and exception structures are fully documented in English. Report back when the file is written and ready for integration into our evolution.py engine."
```