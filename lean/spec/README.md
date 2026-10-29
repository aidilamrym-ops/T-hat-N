# Historical Lean spec -- do not use as a sound basis

`XiAnalyticSpec.lean` is pinned as history by registry `A-2026-0015`.
It is **inconsistent**: its global axiom `xiReal_sub_one` plus the
product definition at `x = 1` lets Lean prove `False` (a temporary probe
proved `False` from `xiReal_sub_one 0`, `zetaReal_zero` and
`gammaReal_one`). The false and unused `zetaReal_neg` axiom is another
defect: zeta is zero at `-2` and positive at `-3`.

The repaired abstract specification is
[`../spec_v2/XiAnalyticSpecV2.lean`](../spec_v2/XiAnalyticSpecV2.lean).
That file still treats `zetaReal`/`gammaReal` as opaque symbols and is
**not** a proof about the actual zeta and Gamma functions; it only keeps
the conditional derivation internally consistent and blocks the old
contradiction.


