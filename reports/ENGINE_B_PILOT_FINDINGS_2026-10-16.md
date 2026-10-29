# ENGINE B PILOT FINDINGS -- 2026-10-16

Dated finding/deviation note (append-only). Engine B pilot v1 ran BEFORE the
full verification; raw evidence: `reports/gw_engine_b_pilot_v1.log` and
`reports/gw_engine_b_pilot_v1.json` (script sha256
`0c1b54c310759e5d6c9b962bc2aea252412ed665931f808ec5ccb94b6dbee09f`, recorded in
their headers). The frozen authority remains
`reports/AMENDMENT_FLOOR_SPEC.md` section 5. Nothing below edits any frozen
text; it records measured deviations and PRE-DECLARES the treatment applied
in the full run (spec section 7: deviations are recorded, never patched).

## F1 -- the 10-ulp branch of the frozen OR is not met (engine A noise floor)

Frozen text: "per-bin |B - A| within 1e-9 relative OR 10 ulp". Pilot v1
implemented only the 10-ulp branch as the operative test (a misreading,
declared in the pilot manifest); the frozen text is an OR. Measured (pilot
v1, dim 201, all cells): the relative branch holds everywhere with max
relative deviation 2.43e-13 (cv) and 2.17e-14 (tgt), while the 10-ulp branch
fails for most bins (cv up to ~1.7e3 ulp, tgt up to ~1.9e2 ulp).

Cause (measured, not assumed): engine A evaluates the r2 kernel K and the
smoothing integral in float64 -- `np.arange` fine-grid jitter (measured up to
4.71e-13 over the 2201-edge grid; -2.344791e-13 at edge index 1100),
`np.sin`/`np.exp` at 1 ulp, BLAS reduction order -- so A's own quadrature
noise exceeds 10 ulp of the result. The full run implements the frozen OR
verbatim and reports both branch censuses per bin. No criterion is changed.

## F2 -- chart-L fine-bin edge cluster (enumerated membership disagreements)

Measured (pilot v1, dim 201, chart L, all three sigma_u): 6 of 20 cv bins
per cell fail BOTH branches of the frozen OR. Exact characterization:

- 15 ordered pairs (i, j) among the bottom six levels have engine-B D values
  exponentially tiny negative (-9.56e-30 .. -3.83e-15) and engine-A D values
  exactly 0.0 (float64 collapse); bin_A = 1100, bin_B = 1099 (the exact left
  edge of fine bin 1100 is 0.0; engine A's `np.arange` edge there is
  -2.344791e-13).
- hist delta +15 / -15 between fine bins 1099/1100; cv impact decaying
  cascade over coarse bins 0-5, max |delta cv| = 5.80e-4 absolute.
- Cross-check: binning engine-B's exact D values through engine-A's float64
  edges reproduces engine-A's histogram exactly (0 flips). The disagreement
  is input representation + edge jitter at a discontinuity of the estimator,
  NOT an arithmetic difference in the convolution or target computation.
- Counts unaffected: pilot counts (2000 samples, dim 301) reproduced the
  sealed counts EXACTLY 6/6 cells, including all chart-L cells.
- Chart T: 0 membership disagreements, 0 flips.

## Pre-declared treatment for the full run (frozen before it starts)

1. The frozen OR is implemented verbatim; both branch censuses are reported
   per bin (`within_10ulp`, `within_1e9rel`, `within_frozen_or`).
2. A cv bin failing the frozen OR is excused ONLY IF covered by enumerated
   fine-bin membership disagreements satisfying ALL of:
   a. |bin_A - bin_B| = 1 (adjacent fine bins);
   b. |D_B - edge_exact| <= 1e-9 and |D_A - edge_float| <= 1e-9;
   c. at most 100 members per cell, all enumerated in the artifact;
   d. max |delta cv| over OR-failing bins <= 1e-2 (mechanism-derived bound:
      M * K'_max * width / n <= 100 * 1 * 0.01 / 201 = 5e-3, doubled).
   tgt bins failing the OR are never excused (tgt is histogram-free).
3. Any OR failure not covered by rule 2 -> STOP; record; publish nothing.
4. The full-run artifact labels such cells PASS_ENUMERATED_EDGE_CLUSTER and
   carries the divergence verbatim (within_frozen_or = false on those bins).

Pilot v2 (same day, final script revision) re-validates this treatment at
the sealed 2000-sample scale before the full 20000-sample run starts.

## R1 -- full-run interruption and detached relaunch (2026-10-16 22:11 / 22:20)

The first full run (script sha256 485ab652..., launched 2026-10-16 ~21:02
local) was terminated externally at 22:11:0x local during dim 401
(GUE 1000/20000): the process tree vanished with no error output -- the log
ends mid-progress, stderr carries no traceback, no exit code was recorded,
and the hosting shell died without emitting its final line (the MCP bridge
processes restarted at 22:12:12, consistent with an environment restart).
Partial log preserved verbatim as
`reports/gw_engine_b_verify_interrupted_2026-10-16_2211.log`. No artifact
was written by the interrupted run. No module or instrument change was made
(instrument sha256 unchanged 072910f2...; script sha256 unchanged 485ab652...).
The run was relaunched detached (WMI-created process; launcher
`C:\Users\usER\AppData\Local\Temp\opencode\run_engine_b_full.cmd`) so the
verification process no longer depends on the agent-shell lifetime. The
relaunched log header re-records script sha256 485ab652... and instrument
sha256 072910f2... (both unchanged).

## R2 -- environment restart after completion (2026-10-17)

The relaunched full run COMPLETED before the environment restart. The
launcher exit file (verbatim):

    STARTED 16/10/2026 22:20:26,63
    EXITCODE=0

The log's final line is `wrote D:\Opencode AI Agent\reports\gw_engine_b_verify.json  (9062 s total)`;
the artifact timestamp is 2026-10-17 00:51:30 local. The host was then
restarted (the agent-shell background processes -- including the watcher --
were cancelled by the restart; the user attributes the outage to a power
interruption); the environment was found up again at ~05:39 local. No
verification process was running at that point, no artifact was affected,
and no re-run is needed: the completed log + JSON are the results of
record. Header re-records (unchanged): script sha256 `485ab652...`;
instrument sha256 `072910f2...`.


