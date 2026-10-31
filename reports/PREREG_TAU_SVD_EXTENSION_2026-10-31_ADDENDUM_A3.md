# PREREG-TAU-SVD-EXTENSION-2026-10-31 -- ADDENDUM A3 (dated 2026-10-31)

Third append-only amendment to
`reports/PREREG_TAU_SVD_EXTENSION_2026-10-31.md` (commit `16f216e`), after
Addendum A1 (`018c82f`) and Addendum A2 (`c86ea8f`). Nothing already frozen
is rewritten.

Status: pre-registration pushed, implementation module
`msaf/chrono_runtime/svd_extension.py` **does not exist yet**, no 401/501
matrix, trace, Frobenius enclosure, Gershgorin disc or singular-value bracket
has been computed. The checks below were run on dims 201/301 only, i.e. on
already published data, while preparing the implementation.

## A3.1 Finding: G-M2c (rebuild containment) is unsatisfiable

Addendum A1 froze **G-M2c**: "the enclosures obtained from a matrix rebuilt by
`build_arb_tau` at the same `c`, `N`, `prec` must be contained in the 256-bit
enclosures of G-M2b."

G-M2b computes its enclosures from the **committed** matrix file, whose
entries are the canonical 50-digit/30-digit serialization (A2.1). The rebuilt
matrix carries the full 256-bit midpoints. Measured on both published
dimensions:

| dim | entries not even *overlapping* the rebuilt matrix | max entrywise shift |
|---|---|---|
| 201 | 40401 of 40401 (= 201^2, every entry) | `[4.92619747402229269444070341e-50 +/- 2.02e-77]` |
| 301 | 90601 of 90601 (= 301^2, every entry) | `[4.92619747402229269444070341e-50 +/- 2.02e-77]` |

The balls have radius of order `10^-73` while their midpoints differ by
`4.93e-50`, so the committed ball and the rebuilt ball are disjoint
everywhere. Containment in the direction G-M2c demanded is therefore
impossible for any matrix written by `msaf/tau_reconstruction/serialize.py` at
`prec_bits = 256`; this is the same lossiness that A2.1 established, now seen
from the rebuild side rather than the re-parse side.

The gate as frozen would have aborted a correct campaign. It is replaced
below, before execution.

## A3.2 Amendment: G-M2c is replaced by G-M2c' (canonical round-trip identity)

Everything else in section 4 stands. G-M2c becomes:

- **G-M2c' (round-trip identity).** For `N = 100` and `N = 150`, take the
  rebuilt in-memory matrix, serialize it with the canonical
  `msaf.gw_matrix.v1` metadata, re-parse the serialization at
  `ctx.prec = 256`, and compute M1 and M2 from the re-parsed matrix. Both
  strings must equal, **character for character**, the G-M2b strings computed
  from the committed file. Failure is an infrastructure failure and aborts
  the campaign.
- **G-M2d (declared shift).** The report records, per dimension, the maximum
  entrywise shift `max_ij |mid_rebuilt - mid_committed|` together with the
  statement that the committed file is the canonical serialization of the
  rebuild and is narrower than it by exactly this amount. The shift is a
  declaration, not a pass/fail condition.

Why this is at least as strong as the original gate: G-M3a already pins the
committed `sha256lf`, and byte equality of the serialization makes the
round-trip identity a re-derivation of the committed numbers from the rebuild
alone. The original containment would additionally have required the
serializer to be lossless, which it is not.

## A3.3 What is still frozen

Unchanged: M1-M6 and their definitions, G-M1, G-M2a, G-M2b, G-M3a, G-M3b,
G-M3c, the protocol parameters (`c = 100`, `N in {200, 250}`,
`prec_bits = 256`, one code path for all four dimensions), the decision rules
of section 6, the failure handling of section 7, the artifact list of section
8, and the ban on trend statements and on "compact" / "exponential decay" as
conclusions.

No 401/501 number has been computed at the time of this addendum.

Declared by the analysis session on 2026-10-31, before implementation.
