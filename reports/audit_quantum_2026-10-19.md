# Quantum audit 2026-10-19

Status: **statistical layer reproduced**.

The three 20,000-sample binary files are decoded as little-endian
float64 values.  Each sample set is binned against the 16
equiprobable standard-normal quantiles.  This is the SIMULATED-
entropy statistical layer; it is not a physical claim and does not
replace the certified interval layer.

## Bin counts (expected 1250 per bin)

| File | b0 | b1 | b2 | b3 | b4 | b5 | b6 | b7 | b8 | b9 | b10 | b11 | b12 | b13 | b14 | b15 | Ï‡Â² | tail zâ‰¥3.5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| stats_d201.bin | 1229 | 1233 | 1270 | 1236 | 1237 | 1284 | 1278 | 1279 | 1278 | 1248 | 1241 | 1272 | 1199 | 1250 | 1216 | 1250 | 7.508800 | 2 |
| stats_d301.bin | 1256 | 1203 | 1288 | 1267 | 1263 | 1205 | 1271 | 1220 | 1222 | 1218 | 1291 | 1251 | 1233 | 1277 | 1254 | 1281 | 10.398400 | 4 |
| stats_d401.bin | 1238 | 1252 | 1302 | 1290 | 1225 | 1207 | 1272 | 1276 | 1291 | 1245 | 1242 | 1275 | 1235 | 1232 | 1216 | 1202 | 11.592000 | 3 |

## Verdict

| File | Samples | Mean | Std | Ï‡Â² | Window | Passed |
|---|---:|---:|---:|---:|---|---|
| stats_d201.bin | 20000 | -0.005927863 | 0.997875056 | 7.508800 | [0.0, 60.0] | PASS |
| stats_d301.bin | 20000 | 0.004626308 | 1.005679575 | 10.398400 | [0.0, 60.0] | PASS |
| stats_d401.bin | 20000 | -0.008558951 | 0.995496244 | 11.592000 | [0.0, 60.0] | PASS |

Overall: **RESOLVED**.

## Receipt

```json
{
  "schema": "msaf.audit_quantum.stats.v1",
  "campaign": "2026-10-19",
  "simulated": true,
  "global_claim_supported": false,
  "bin_edges": [
    -1.534120544353,
    -1.150349380376,
    -0.887146559019,
    -0.674489750196,
    -0.488776411115,
    -0.318639363964,
    -0.15731068461,
    0.0,
    0.15731068461,
    0.318639363964,
    0.488776411115,
    0.674489750196,
    0.887146559019,
    1.150349380376,
    1.534120544353
  ],
  "files": [
    {
      "file": "stats_d201.bin",
      "bytes": 160000,
      "sha256": "2dc8f04971c567139923c05bff0f615d168dddb98a8c989671664f635736d126",
      "samples": 20000,
      "bins": 16,
      "expected_per_bin": 1250.0,
      "counts": [
        1229,
        1233,
        1270,
        1236,
        1237,
        1284,
        1278,
        1279,
        1278,
        1248,
        1241,
        1272,
        1199,
        1250,
        1216,
        1250
      ],
      "chi2": 7.5088,
      "chi2_window": [
        0.0,
        60.0
      ],
      "tail_z": 3.5,
      "tail_exceedances": 2,
      "mean": -0.005927863,
      "stdev": 0.997875056,
      "passed": true
    },
    {
      "file": "stats_d301.bin",
      "bytes": 160000,
      "sha256": "9051d995d26d09e2cc57f0dde45995b6a2b6f1644f233bffc1e1a3c441796528",
      "samples": 20000,
      "bins": 16,
      "expected_per_bin": 1250.0,
      "counts": [
        1256,
        1203,
        1288,
        1267,
        1263,
        1205,
        1271,
        1220,
        1222,
        1218,
        1291,
        1251,
        1233,
        1277,
        1254,
        1281
      ],
      "chi2": 10.3984,
      "chi2_window": [
        0.0,
        60.0
      ],
      "tail_z": 3.5,
      "tail_exceedances": 4,
      "mean": 0.004626308,
      "stdev": 1.005679575,
      "passed": true
    },
    {
      "file": "stats_d401.bin",
      "bytes": 160000,
      "sha256": "8d06f3fff31fd60b68826baff421cc876ff13673f8781dbbcf38a193568f94fc",
      "samples": 20000,
      "bins": 16,
      "expected_per_bin": 1250.0,
      "counts": [
        1238,
        1252,
        1302,
        1290,
        1225,
        1207,
        1272,
        1276,
        1291,
        1245,
        1242,
        1275,
        1235,
        1232,
        1216,
        1202
      ],
      "chi2": 11.592,
      "chi2_window": [
        0.0,
        60.0
      ],
      "tail_z": 3.5,
      "tail_exceedances": 3,
      "mean": -0.008558951,
      "stdev": 0.995496244,
      "passed": true
    }
  ],
  "all_pass": true,
  "summary": "RESOLVED"
}
```


