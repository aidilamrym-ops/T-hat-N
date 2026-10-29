## C4 robustness array extension (S10) -- dim 301, chart T, sigma_u 0.5

Pre-registration: `reports/C4_SEEDS10_PREREG_2026-10-17.md` (commit 657352cc2b47ee8480686c4281664b70a5714c64; ordering check: PASS).

| seed | k/20000 | p_hat_i | CP95 | segment |
|---|---|---|---|---|
| 20260927 | 1262/20000 | 6.31000e-02 | [5.97690e-02, 6.65587e-02] | S5 (sealed) |
| 20261001 | 960/20000 | 4.80000e-02 | [4.50783e-02, 5.10540e-02] | S5 (sealed) |
| 20261002 | 1289/20000 | 6.44500e-02 | [6.10854e-02, 6.79419e-02] | S5 (sealed) |
| 20261003 | 1021/20000 | 5.10500e-02 | [4.80401e-02, 5.41913e-02] | S5 (sealed) |
| 20261004 | 1345/20000 | 6.72500e-02 | [6.38170e-02, 7.08094e-02] | S5 (sealed) |
| 20261005 | 1164/20000 | 5.82000e-02 | [5.49947e-02, 6.15345e-02] | S10 (new) |
| 20261006 | 1115/20000 | 5.57500e-02 | [5.26100e-02, 5.90199e-02] | S10 (new) |
| 20261007 | 1114/20000 | 5.57000e-02 | [5.25613e-02, 5.89686e-02] | S10 (new) |
| 20261008 | 1022/20000 | 5.11000e-02 | [4.80887e-02, 5.42427e-02] | S10 (new) |
| 20261009 | 1166/20000 | 5.83000e-02 | [5.50921e-02, 6.16371e-02] | S10 (new) |

Pooled (S10, 10 seeds): 11458/200000 (p_hat = 5.72900e-02), CP95 [5.62754e-02, 5.83174e-02]

Homogeneity: Pearson chi2 = 131.2879, df = 9, p = 6.44376e-24

Frozen decision tree classification: **NOT STABLE (homogeneity rejected at alpha = 0.01; dispersion-dominated)**

C4 stays flagged resolution-sensitive per frozen spec section 4; the verdict grid recomputation still uses the canonical 20000 value (number of record).

Number of record (UNCHANGED): 1262/20000 = 6.31000e-02 (canonical seed 20260927).

Old five seeds: re-parsed from the original logs and cross-checked against the sealed artifact (`reports/gw_h1_floor_refine.json`, sha256_lf 4777d94f9ec533712b14cc097b9240e5c961790b3d9025f452b7c21aade6148f); cross-check PASS.


