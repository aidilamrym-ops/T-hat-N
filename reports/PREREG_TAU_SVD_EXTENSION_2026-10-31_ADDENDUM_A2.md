# PREREG-TAU-SVD-EXTENSION-2026-10-31 -- ADDENDUM A2 (dated 2026-10-31)

Second append-only amendment to
`reports/PREREG_TAU_SVD_EXTENSION_2026-10-31.md` (commit `16f216e`), after
Addendum A1 (commit `018c82f`). Nothing already frozen is rewritten.

Status: pre-registration pushed, implementation module not yet written, no
401/501 computation executed. The checks below were run on dims 201/301
only, i.e. on already published data, while preparing the implementation.

## A2.1 Finding: the canonical serialization is lossy at 256 bits

`msaf/tau_reconstruction/serialize.py` writes each entry as a midpoint with
**50 significant digits** and a radius with **30 significant digits**
(`arb_to_dict`: `val.mid().str(50)`, `val.rad().str(30)`). A 256-bit ball has
about 77 significant decimal digits, so the decimal midpoint is truncated
roughly 27 digits *below* the precision of the ball, while the radius is
reproduced at full size. The re-parsed ball is therefore **narrower** than
the ball it came from:

| dim | entries failing `reparsed.contains(in_memory)` | max entrywise slack |
|---|---|---|
| 201 | 40401 of 40401 (= 201^2, every entry) | -- |
| 301 | (same mechanism) | `[4.92619747402229269444070341e-50 +/- 2.02e-77]` |

The slack is exactly the decimal truncation of the midpoint, about
`5e-50` in absolute value.

Consequence: the frozen **G-M3** ("the re-parsed matrix must contain the
in-memory matrix entry by entry") is unsatisfiable at `prec_bits = 256`, for
any matrix. It is replaced below, before execution.

## A2.2 Verified replacement: the build chain is bit-reproducible

Running the pinned chain

```python
ctx.prec = 256
tau = msaf.tau_reconstruction.build.build_arb_tau(c=100, N=N, prec_bits=256)
```

and serializing the result with the pinned `serialize.save_matrix_json`
metadata (`schema`, `dim`, `conductor=100`, `block=N`, `prec_bits=256`,
`dps=77`, `build_chain`, `gate_verdict="G-M0 PASS"`) reproduces the committed
matrices **byte for byte**:

| dim | rebuild `sha256lf` | committed `sha256lf` | equal |
|---|---|---|---|
| 201 | `8d2151e5b85c8279cd8bd9e6e88dc10667a193074043faf42c5782c98a04e344` | same | yes |
| 301 | `513b14ef5c8950457f8407a00031296022535cfba9e8167b6e2b7013a1d5cc83` | same | yes |

This is a stronger statement than the original gate wanted: it pins the whole
build chain, not just entrywise containment.

## A2.3 Amendment: G-M3 is replaced by G-M3' (determinism and fingerprint)

Everything else in section 4 stands. G-M3 becomes:

- **G-M3a (committed-artifact reproduction).** For `N = 100` and `N = 150`,
  a fresh build plus canonical serialization must reproduce the committed
  `sha256lf` values above. Verified in this addendum; re-verified by the
  implementation run. Failure is an infrastructure failure.
- **G-M3b (rebuild determinism).** For `N = 200` and `N = 250`, two
  independent builds in the same process must serialize to the same
  `sha256lf`. That value is recorded in the report. Failure is reported as
  the outcome (non-deterministic build), not retried.
- **G-M3c (declared slack).** The report records, per dimension, the maximum
  entrywise serialization slack
  `max_ij ( |mid_ser - mid| + rad_ser - rad )` together with the note that
  the serialization is **lossy**: the fingerprint identifies the build, it is
  not a container for the in-memory matrix. The metrics M1-M6 are computed
  from the in-memory matrix, as frozen in section 3; they are **not**
  computed from the re-parsed serialization.

The dim-401/501 matrix files remain uncommitted (section 8 of the
pre-registration). Their `sha256lf` is now backed by G-M3b, so a third party
can rebuild and compare fingerprints without trusting this session.

## A2.4 What is still frozen

Unchanged: M1-M6 and their definitions, G-M1, G-M2a/b/c (as amended by A1),
the protocol parameters (`c=100`, `N in {200,250}`, `prec_bits=256`, one code
path), the decision rules of section 6, the failure handling of section 7,
the artifact list of section 8, and the ban on trend statements and on
"compact" / "exponential decay" as conclusions.

No 401/501 number has been computed at the time of this addendum.

Declared by the analysis session on 2026-10-31, before implementation.
