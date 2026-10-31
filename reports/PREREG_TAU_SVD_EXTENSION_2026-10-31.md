# TAU-SVD-EXTENSION -- pre-registration for an enclosed singular-value bracket at dims 401 and 501

Date: 2026-10-31 (local). Status: **PRE-REGISTERED BEFORE ANY 401/501
MATRIX-LEVEL COMPUTATION.**

At the time of this declaration no matrix, no trace enclosure, no Frobenius
enclosure, no Gershgorin disc and no singular-value bracket has been computed
in this repository at dim 401 or dim 501. This file is committed and pushed
before `msaf/chrono_runtime/svd_extension.py` exists and before any 401/501
build is launched; the ordering proof is section 10.

## 1. Scope and authority

- Scope limits (verbatim, unchanged): `{rh_claim: false,
  zero_location_claim: false, weil_positivity_claim: false}`.
- Authority order: `CURRENT_AUTHORITY.md`, `AGENTS.md`,
  `reports/DECISION_LOG.md`, `reports/FENCE_REGISTRY.md`.
- This campaign extends `T-2026-0074` (trace and Frobenius energy at dims
  201/301) to dims 401/501 and adds the first *bracket* on the largest
  singular value of the truncated Guinand-Weil matrix `tau`. It is not a
  claim about the Riemann hypothesis, about zero locations, about Weil
  positivity, or about compactness of any operator.

## 2. What exists at freeze time, and the statement under test

Measured and registered before this document:

| artefact | dims | content |
|---|---|---|
| `reports/TAU_SVD_INSIGHTS.json` (T-2026-0074) | 201, 301 | enclosed `tr tau` and `||tau||_F^2` |
| `reports/CHRONO_RIEMANN_INSIGHTS.json` (T-2026-0073) | 201, 301 | enclosed `sum |lambda_i|`, spectral entropy, exact-zero imaginary leak, circulant defect |
| `reports/TAU_ANATOMY_RESULTS_2026-10-30.md` (T-2026-0072) | 201, 301 | Toeplitz / Hankel residuals |
| `reports/gw_matrix_100_100.json`, `reports/gw_matrix_100_150.json` | 201, 301 | the matrices themselves (`msaf.gw_matrix.v1`, prec 256) |

Not in the repository at freeze time: any dim-401 or dim-501 matrix, any
dim-401/501 trace or Frobenius enclosure, and any enclosed singular value at
any dimension. Two adjacent facts are easy to confuse with this campaign and
are therefore named here:

- the 2026-10-15/16 resolution series did measure a **dim-401 spectrum**
  (`c=100, N=200, dps=400, prec=2048, algorithm=vdhoeven_mourrain`), but
  through a *different* chain (decimal serialization, no `build_arb_tau`)
  and with no committed spectrum file; its statistics live in
  `msaf/mont_run.txt` and `reports/THREE_TASKS_2026-10-15.md`;
- the dim-501 Route-S ladder of 2026-10-17 **aborted** with
  `UNDETERMINED at pivot 446` at 6000 bits
  (`reports/gw_route_s_ladder_c100_n250.json`). That is a positivity
  certificate for an LDL^T decomposition and it does **not** gate this
  campaign, which needs no positivity certificate at all.

Statement under test (falsification framing, frozen):

> **(S)** The singular-value energy of `tau` is concentrated in a small
> number of modes, i.e. a handful of singular values already carry 90% of
> `||tau||_F^2`, and `sigma_max^2 / ||tau||_F^2` stays close to 1 as the
> dimension grows.

The campaign computes a **rigorous upper bound** on `sigma_max^2 /
||tau||_F^2` and a **rigorous lower bound** on the number of singular values
needed to reach 90% of the energy. Both are upper/lower bounds of the right
sign to refute (S) without computing a single individual singular value: if
even the largest possible `sigma_max` cannot hold much of the energy, then no
small set of modes can.

## 3. Frozen definitions

Let `tau` be the matrix returned by

```python
msaf.tau_reconstruction.build.build_arb_tau(c=100, N=N, prec_bits=256)
```

evaluated at `ctx.prec = 256`, so `n = 2N+1`. All arithmetic below is `arb`
ball arithmetic; every reported quantity is an interval enclosure. Indices
run `0 <= i, j < n`.

| id | quantity | definition |
|---|---|---|
| M1 | trace | `T = sum_i tau[i,i]` (left to right) |
| M2 | Frobenius energy | `F = sum_{i,j} abs(tau[i,j])^2` (row-major) |
| M3 | column norms | `c_j = sqrt(sum_i abs(tau[i,j])^2)`, `L_col = max_j c_j` |
| M4 | Gershgorin data of `G` | `G = (tau*tau^T + (tau*tau^T)^T)/2`; `d_i = G[i,i]`, `r_i = sum_{j != i} abs(G[i,j])`; `lam_max_G = max_i (d_i + r_i)`, `lam_min_G = min_i (d_i - r_i)` |
| M5 | singular-value bracket | `L = max(sqrt(F/n), L_col)`, `U = min(sqrt(F), sqrt(lam_max_G), sqrt(nrm1 * nrmI))` with `nrm1 = max_j sum_i abs(tau[i,j])` and `nrmI = max_i sum_j abs(tau[i,j])` |
| M6 | concentration | `rho_lo = L^2/F`, `rho_hi = U^2/F`, and `k90 = ceil(0.9*F / U^2)` |

`M5`/`M6` are rigorous for the following reasons, and only these are claimed:

- for every unit vector `v`, `||tau v||_2 <= sigma_max`; with `v = e_j` this
  gives `sigma_max >= c_j`, hence `sigma_max >= L_col`;
- `F = sum_i sigma_i^2 <= n * sigma_max^2`, hence `sigma_max >= sqrt(F/n)`;
- `sigma_max^2 = lam_max(tau*tau^T)`. The true `tau*tau^T` is symmetric and
  is contained entry by entry in `G` as constructed (each off-diagonal
  interval of `G` is the symmetric average of the two computed intervals,
  which both contain the same true entry), so every Gershgorin disc of `G`
  holds the corresponding true eigenvalue and `sigma_max^2 <= lam_max_G`;
- `sigma_max^2 <= F`, and `sigma_max^2 <= nrm1 * nrmI` (Schur test);
- if `U^2 >= sigma_max^2`, then any set of `k` singular values carries at
  most `k * U^2` of the energy, so at least `k90` modes are needed for 90%.

`lam_min_G` is recorded as a looseness indicator only. It is **not** used as
a lower bound for `sigma_min`, because `tau*tau^T` is positive semidefinite
and `lam_min_G` can legitimately be negative through Gershgorin slack.

M1-M6 are computed for `n in {201, 301, 401, 501}` by **one code path**, so
the four dimensions are directly comparable.

## 4. Gates

- **G-M1 (build finiteness).** Every entry of `tau` is finite
  (`arb.is_finite()`); no NaN and no infinite ball. A failure ends the
  dimension.
- **G-M2 (reproduction of T-2026-0074).**
  - G-M2a: for `n = 201` and `n = 301`, M1 and M2 computed from the
    committed `reports/gw_matrix_100_100.json` and
    `reports/gw_matrix_100_150.json` must reproduce the strings in
    `reports/TAU_SVD_INSIGHTS.json` **character for character**. A failure
    is an infrastructure failure (wrong matrix, wrong code path, wrong
    precision) and aborts the campaign.
  - G-M2b: the enclosures from the rebuilt matrix (same `c`, `N`, `prec`
    through `build_arb_tau`) must be contained in the committed ones. A
    failure is reported as the outcome (build instability), not retried.
- **G-M3 (serialization round-trip).** The canonical `msaf.gw_matrix.v1`
  decimal serialization of `tau`, re-parsed into `arb` at 256 bits, must
  contain the in-memory matrix entry by entry. The `sha256lf` of that
  serialization is recorded in the report; the file itself is **not**
  committed (declared deviation, section 8).

## 5. Protocol (frozen)

- **Stage 1 (reproduction).** Load the two committed matrices; compute
  M1-M6; check G-M2a.
- **Stage 2 (extension).** For `N = 200` and `N = 250`: build `tau` at
  `c = 100, prec_bits = 256`; check G-M1; compute M1-M6; check G-M3; record
  wall-clock timings.
- **Stage 3 (emit).** Write `reports/TAU_SVD_INSIGHTS_EXTENDED.json`
  containing, per dimension: the build chain, `prec_bits`, M1-M6 as
  interval strings, the G-M1/G-M2/G-M3 verdicts, the serialization
  `sha256lf`, and the timing. Header carries the tool `sha256lf`, the
  repository HEAD, the scope block and the UTC timestamp.
- Single invocation:
  `python -m msaf.chrono_runtime.svd_extension --out reports/TAU_SVD_INSIGHTS_EXTENDED.json`.
- Environment: single-threaded (`OPENBLAS_NUM_THREADS=1`,
  `OMP_NUM_THREADS=1`), recorded in the report header.
- **Declared deviation from the `RESOLUTION4_DIM501_PREREG_2026-10-17.md`
  style:** that document pinned the runner's `sha256lf` inside the
  pre-registration and therefore had to commit the runner together with it.
  Here the pre-registration freezes the *definitions, gates, parameters and
  decision rules* only; the implementation module is created in a later
  commit and its `sha256lf` is pinned in the report header, not here. This
  keeps "pre-registration commit strictly before implementation commit"
  literally true.

## 6. Decision rules (frozen)

For each dimension independently:

| label | condition | meaning |
|---|---|---|
| `FEW-MODES-REFUTED` | `k90 >= 10` | at least 10 singular values are needed to carry 90% of the energy; statement (S) is refuted at this dimension |
| `UNDECIDED` | `k90 < 10` | the bracket is too wide to refute (S) at this dimension |

- The threshold `10` is fixed here, before any number exists, and is an
  order-of-magnitude statement, not a tuned one.
- No trend statement across dimensions. Two new points plus two old ones are
  four separate measurements; the report prints them side by side and says
  nothing about an asymptote.
- The report never uses the words "compact", "compact operator" or
  "exponential decay" as a conclusion. It reports brackets.
- If a dimension's `U` is so loose that `k90 < 10`, that is reported as
  `UNDECIDED`; the campaign does not then compute eigenvalues of
  `tau*tau^T` to tighten it. A full enclosed singular-value spectrum is a
  separate campaign with its own pre-registration.

## 7. Failure handling

- Nonzero exit, missing metric, or a missing file: **infrastructure
  failure**. The same stage may be re-run with identical parameters after
  the cause is fixed; every attempt is logged; numbers from a failed attempt
  are never used.
- G-M1 fail, G-M2b fail, or G-M3 fail: **the outcome**, reported as-is for
  that dimension. No parameter (`c`, `N`, `prec`) is changed in response to
  any interim or final result.
- The aborted dim-501 Route-S ladder of 2026-10-17 is not an infrastructure
  failure of this campaign and is not repaired here.

## 8. Artifacts and non-modifications

New in the implementation commit:

- `msaf/chrono_runtime/svd_extension.py` (new module; the existing
  `msaf/chrono_runtime/svd_analysis.py` is **not** edited, so T-2026-0074
  stays byte-reproducible);
- `reports/TAU_SVD_INSIGHTS_EXTENDED.json` (the report);
- one new `T` entry for the report and one new `A` entry for the execution
  audit in `reports/FENCE_REGISTRY.md`, with `sha256LF` lines;
- a dated section in `README.md` section 3 (and the regenerated
  sealed-status block if and only if the generator demands it).

**Not committed, declared deviation:** the dim-401 and dim-501 matrix
serializations (`msaf.gw_matrix.v1` would be about 23 MB and 36 MB of JSON).
They are reproducible in well under two minutes from the pinned chain, and
their `sha256lf` values are recorded in the report, so the claim can be
re-derived without carrying the bytes in git. This is the only place where
this campaign departs from the "commit the artifact" habit of T-2026-0074.

Not modified (`sha256lf` recorded here so drift is detectable):

```text
sha256LF 8d2151e5b85c8279cd8bd9e6e88dc10667a193074043faf42c5782c98a04e344 reports/gw_matrix_100_100.json
sha256LF 513b14ef5c8950457f8407a00031296022535cfba9e8167b6e2b7013a1d5cc83 reports/gw_matrix_100_150.json
sha256LF 9d9bb5f8f744e9b68ce29c55d1aca85ce88321b98c1aa7323aa4af7ade3b761f reports/TAU_SVD_INSIGHTS.json
sha256LF d6024166921f018791fec59ff70aeee15e9f28a7bb176bdd4fcf04fec4df89e0 reports/CHRONO_RIEMANN_INSIGHTS.json
sha256LF c8ca4b4d9a1f210792b553e16c2051468ca72c038fbb46014ff14ef9973cf8f2 reports/CHRONO_SPECTRUM_GRADIENT_2026-10-30.json
sha256LF ad43363dcc08e02538747dfdbc9ad69ff26bc6a22e2fb86da8f680cf33979425 reports/TAU_ANATOMY_RESULTS_2026-10-30.md
sha256LF 3a0668d3085caf61c47e275d68df85fe17db216522100d46e25fba143dd4f8e3 msaf/tau_reconstruction/build.py
sha256LF 8287bbd76133b49295ab33f8f2930fae527dcdb8f4ff823ae818bb03a30e58c5 msaf/chrono_runtime/svd_analysis.py
```

External builder, pinned by raw `sha256` (frozen, never modified):
`C:/Users/usER/oracle-toe/GUINAND_WEIL/source_arb_ldlt_certify.py`
`33617ce64b0e052c07873b196a3744f2f5142a4aaf7b4cfbe9e3de43d17c27bb`
(identical to the hash pinned in `RESOLUTION4_DIM501_PREREG_2026-10-17.md`
section 5). `GW_DIR` may resolve to either of the two identical trees on this
machine; the hash is the authority, not the path.

## 9. Cost anchors (measured 2026-10-31, not a promise)

Measured on this machine at `prec_bits = 256`, with `N <= 100` only, so no
401/501 quantity is implied:

| probe | measured |
|---|---|
| `build_arb_tau(100, 50, 256)` (dim 101) | 1.55 s |
| `build_arb_tau(100, 100, 256)` (dim 201) | 6.16 s |
| `tau * tau^T` at dim 201 | 0.22 s |
| one Gershgorin pass at dim 201 | 0.05 s |

Fitting `build ~ dim^1.85` and `tau*tau^T ~ dim^3` gives, as an order of
magnitude only: dim 401 build about 25 s, dim 501 build about 40 s, and a
whole campaign of a few minutes. The campaign is therefore not
resource-bound, which is exactly why the decision rules can be frozen
without a budget clause.

## 10. Ordering proof

- This file is added in its own commit, pushed, and only then is
  `msaf/chrono_runtime/svd_extension.py` written.
- The report header records the repository HEAD at execution time, the tool
  `sha256lf`, and UTC start/finish stamps, so the ordering is checkable from
  the artefacts alone.
- The `sha256LF` of this file is pinned in the `A` registry entry of the
  implementation commit.

Declared by the analysis session on 2026-10-31, before implementation.
