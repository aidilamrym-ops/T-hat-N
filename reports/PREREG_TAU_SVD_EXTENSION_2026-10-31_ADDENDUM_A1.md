# PREREG-TAU-SVD-EXTENSION-2026-10-31 -- ADDENDUM A1 (dated 2026-10-31)

Append-only amendment to `reports/PREREG_TAU_SVD_EXTENSION_2026-10-31.md`
(commit `16f216e`). Nothing in that document is rewritten; the two changes
below are added before any implementation code exists and before any 401/501
computation is executed.

Status at the time of this addendum: the pre-registration is pushed, the
implementation module `msaf/chrono_runtime/svd_extension.py` does not exist
yet, and no 401/501 build has been launched. The addendum was prompted by a
check performed *while preparing* the implementation, i.e. on already
published dim-201/301 data only.

## A1.1 Finding: T-2026-0074 is a 53-bit computation, not a 256-bit one

`msaf/chrono_runtime/svd_analysis.py` (the tool named in registry entry
T-2026-0074) never sets `ctx.prec`; it therefore runs at the python-flint
default of 53 bits. Recomputing both matrices at 53 bits reproduces the
committed strings exactly:

| dim | committed (`reports/TAU_SVD_INSIGHTS.json`) | recomputed at `ctx.prec = 53` |
|---|---|---|
| 201 trace | `[425.1897200764 +/- 1.30e-11]` | identical |
| 201 Frobenius^2 | `[2060.9091085 +/- 9.85e-9]` | identical |
| 301 trace | `[758.9564527274 +/- 5.59e-11]` | identical |
| 301 Frobenius^2 | `[3781.0796611 +/- 2.68e-8]` | identical |

Recomputing the same matrices at 256 bits gives, for example,

```text
trace(201)      [425.189720076409736082989267128797521061462120728134562 +/- 2.02e-71]
frobenius^2(201) [2060.909108506543244009701800058552457127969898240227258 +/- 7.63e-70]
```

so the committed 53-bit intervals are correct but roughly sixty digits wider
than the matrices allow. This is a precision statement about T-2026-0074, not
an error in it: at 53 bits the enclosures still contain the exact value of
the stored matrix, which is all that entry claims.

Consequence for this campaign: section 4 of the pre-registration demanded
character-for-character reproduction of T-2026-0074 while the protocol runs
at `ctx.prec = 256`. Those two requirements are mutually exclusive, and the
gate as frozen would have aborted a correct campaign. It is corrected here,
before execution.

## A1.2 Amendment: G-M2 is split into a reproduction gate and a containment gate

Replacing section 4, item **G-M2**, by the following three checks. Everything
else in the pre-registration -- M1-M6, G-M1, G-M3, the protocol parameters,
the decision rules of section 6, the failure handling of section 7 and the
artifact list of section 8 -- is unchanged.

- **G-M2a (53-bit reproduction).** At `ctx.prec = 53`, M1 and M2 computed
  from the committed `reports/gw_matrix_100_100.json` and
  `reports/gw_matrix_100_150.json` must reproduce the four strings in
  `reports/TAU_SVD_INSIGHTS.json` **character for character**. Failure is an
  infrastructure failure and aborts the campaign.
- **G-M2b (256-bit containment).** At `ctx.prec = 256`, the M1 and M2
  enclosures computed from the same two committed matrices must be
  **contained in** the 53-bit committed intervals (`arb.contains` on the
  pair). Failure is an infrastructure failure and aborts the campaign: it
  would mean the loader, the accumulation order or the precision control has
  drifted.
- **G-M2c (rebuild containment).** The enclosures obtained from a matrix
  rebuilt by `build_arb_tau` at the same `c`, `N`, `prec` must be contained
  in the 256-bit enclosures of G-M2b. Failure is reported as the outcome
  (build instability), not retried.

## A1.3 Amendment: the report must carry the precision of every row

Section 5, Stage 3, is extended by one field: each per-dimension record must
carry `prec_bits` **and** the pair `(reproduction_prec_bits, enclosure_prec_bits)`
for the two reproduction rows, so that no reader can mistake a 53-bit
interval for a 256-bit one. `README.md` section 3.1 already reports the
T-2026-0074 values without a precision label; the implementation commit adds
the label "(T-2026-0074, 53 bits)" to that table, which is a correction of
wording, not of numbers.

## A1.4 What is still frozen

- No parameter changes: `c = 100`, `N in {200, 250}`, `prec_bits = 256`,
  single code path for all four dimensions.
- No change to the decision rule (`k90 >= 10` -> `FEW-MODES-REFUTED`, else
  `UNDECIDED`) and no change to the ban on trend statements and on the words
  "compact" / "exponential decay" as conclusions.
- No 401/501 number has been computed at the time of this addendum, so the
  pre-registration remains genuine for the two new dimensions.

Declared by the analysis session on 2026-10-31, before implementation.
