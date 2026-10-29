# Sertifikat diagnostik RBM Anderson for estimator S1/S2 â€” 2026-10-20

**Status:** `PASS` (CI run `39451466416`, commit `d629823`, conclusion
`success`). **Paket:** item 4 dari
[`reports/FIVE_CORE_BLUEPRINT_TRIAGE_2026-10-20.md`](FIVE_CORE_BLUEPRINT_TRIAGE_2026-10-20.md).
**Pra-registrasi:** [`reports/PREREG_RBM_ANDERSON_2026-10-20.md`](PREREG_RBM_ANDERSON_2026-10-20.md)
(`sha256LF 62c9940a831a43e70376077d58972c49c7ef686e20751900be681606a595a014`).

## 1. Ringkasan result

Kampanye finite `D = 201` with tiga bandwidth `b = 1, 10, 120`, 64 matriks
per titik, null reference 2000 spectra GUE/Poisson and 64 spectra kalibrasi
independen, memberi verdict **`PASS`** for kriteria which dikunci:

- kalibrasi null S1: **4/4** label benar;
- kalibrasi null S2: **12/12** sel label benar and `p_own >= 0.05`;
- RBM S1: monotonik in kedua chart, `b=1` berlabel `POISSON`, `b=120`
  berlabel `GUE`;
- RBM S2: `b=1` berlabel `POISSON` in **6/6** sel, `b=120` berlabel `GUE`
  in **6/6** sel;
- integritas: tiga spot-check Arb lulus, deviasi eigenvalue maksimum
  `6.22e-14`, semua section imajiner memuat nol.

Verdict ini berarti **estimator S1/S2 dapat membedakan fase RBM secara
relatif on konfigurasi ini**. Ia bukan klaim bahwa RBM `b=1` adalah proses
Poisson eksak, bahwa RBM `b=10` adalah GUE, or bahwa transisi Anderson fisik
telah dibuktikan. Lihat Â§8 for limit and nuansa p-value.

## 2. Konfigurasi and ensemble

| Parameter | Nilai |
|---|---:|
| Dimensi | 201 (`2N+1`, `N=100`) |
| Bandwidth | 1, 10, 120 |
| Matriks RBM per bandwidth | 64 |
| Null reference GUE/Poisson | 2000 masing-masing |
| Null calibration GUE/Poisson | 64 masing-masing |
| Bootstrap | 2000 |
| `Ïƒ_u` | 0.3, 0.5, 1.0 |
| Chart | T (primary), L (secondary) |
| `Ïƒ_e` | 0.5 |
| Grid S2 | 20 bin, `u=0.25..9.75` |
| Seed master | `2430500035454946990` (`0x21badee7a7ddceae`) |

Matriks dibangun dari integer 16-bit `re, im` menjadi
`A_ij = (re_ij + i im_ij)/32768` on band `|i-j| <= b`, lalu
`A â† (A + Aâ€ )/2`. Entri float64 tepat sama with rasional exact karena
penyebutnya pangkat dua. Untuk null GUE dipakai `b = D-1`; null Poisson
memakai cumulative exponential spacings. Chart which dipakai:

```text
s = 1 - min(Î»)
x_L = Î» + s        (minimum 1)
x_T = ln(Î» + s)    (minimum 0)
```

## 3. Kalibrasi null

### 3.1 S1

| null | chart | mean kalibrasi | p dua sisi | label | benar |
|---|---|---:|---:|---|---|
| GUE | T | 0.597335 | 1215/2000 | GUE | ya |
| GUE | L | 0.598110 | 1231/2000 | GUE | ya |
| Poisson | T | 0.381546 | 237/2000 | POISSON | ya |
| Poisson | L | 0.382141 | 330/2000 | POISSON | ya |

Reference S1: GUE `T` mean `0.598785`, sd `0.020705`; GUE `L` mean
`0.599408`, sd `0.020795`; Poisson `T` mean `0.385987`, sd `0.022870`;
Poisson `L` mean `0.386112`, sd `0.022850`.

### 3.2 S2

Dua belas sel kalibrasi (2 null Ã— 3 `Ïƒ_u` Ã— 2 chart) semuanya berlabel benar
and `p_own >= 0.05`. Ringkasan rentang p: GUE `p_GUE` 1410â€“1932/2000;
Poisson `p_Pois` 1087â€“1619/2000. Tidak ada sel which gagal kalibrasi.

## 4. RBM â€” S1

| b | chart | mean | sd | z_GUE | z_Pois | p_GUE | p_Pois | label |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | T | 0.394597 | 0.023972 | -9.862 | 0.376 | 0/2000 | 5/2000 | POISSON |
| 1 | L | 0.394674 | 0.024021 | -9.845 | 0.375 | 0/2000 | 3/2000 | POISSON |
| 10 | T | 0.533731 | 0.022841 | -3.142 | 6.460 | 0/2000 | 0/2000 | GUE |
| 10 | L | 0.533978 | 0.022819 | -3.146 | 6.471 | 0/2000 | 0/2000 | GUE |
| 120 | T | 0.599435 | 0.020022 | 0.031 | 9.333 | 1608/2000 | 0/2000 | GUE |
| 120 | L | 0.600177 | 0.020037 | 0.037 | 9.368 | 1543/2000 | 0/2000 | GUE |

`z_GUE`/`z_Pois` adalah jarak mean RBM ke mean reference dalam unit SD
reference (bukan standard error mean). `p_GUE`/`p_Pois` adalah p dua sisi dari
bootstrap mean berukuran 64. Kemonotonan `r_bar(1) < r_bar(10) < r_bar(120)`
terpenuhi in kedua chart with selisih minimum terkecil `0.0657` (jauh in atas
ambang pra-registrasi `0.01`).

Catatan penting: titik `b=1` lebih dekat ke Poisson secara relatif, tetapi p
dua sisinya kecil (`3â€“5/2000`) karena mean `0.3946` masih bergeser `+0.0086`
dari reference Poisson `0.3860`; jadi ini adalah **near-Poisson finite-size**,
bukan Poisson eksak. Titik `b=10` berada in antara kedua null and no
seragam secara statistik; labelnya hanya menyatakan jarak ternormalisasi which
lebih dekat ke GUE.

## 5. RBM â€” S2

`p_GUE = P[chi2_GUE_boot >= chi2_obs]` (upper tail).
`p_Pois = P[chi2_Pois_boot <= chi2_obs]` (lower tail, sesuai konvensi
pra-registrasi/README). Karena itu `p_Pois` which mendekati 1 berarti jarak ke
rata-rata Poisson **lebih besar** dari biasanya, bukan p-value konsistensi
dua sisi. Label fase memakai jarak chi-square ternormalisasi terhadap
rerata bootstrap masing-masing null.

| b | sigma_u | chart | chi2_GUE | p_GUE | chi2_Pois | p_Pois | label |
|---:|---:|---|---:|---:|---:|---:|---|
| 1 | 0.3 | T | 145534.582 | 0/2000 | 65.981 | 1997/2000 | POISSON |
| 1 | 0.3 | L | 158366.122 | 0/2000 | 73.285 | 1999/2000 | POISSON |
| 1 | 0.5 | T | 79032.536 | 0/2000 | 55.759 | 1996/2000 | POISSON |
| 1 | 0.5 | L | 83064.557 | 0/2000 | 55.568 | 1995/2000 | POISSON |
| 1 | 1.0 | T | 45081.059 | 0/2000 | 51.699 | 1981/2000 | POISSON |
| 1 | 1.0 | L | 45904.812 | 0/2000 | 54.468 | 1983/2000 | POISSON |
| 10 | 0.3 | T | 2984.014 | 0/2000 | 3944.641 | 2000/2000 | GUE |
| 10 | 0.3 | L | 3356.936 | 0/2000 | 3893.065 | 2000/2000 | GUE |
| 10 | 0.5 | T | 2535.361 | 0/2000 | 3354.366 | 2000/2000 | GUE |
| 10 | 0.5 | L | 2762.964 | 0/2000 | 3359.035 | 2000/2000 | GUE |
| 10 | 1.0 | T | 2261.019 | 0/2000 | 3117.618 | 2000/2000 | GUE |
| 10 | 1.0 | L | 2309.095 | 0/2000 | 3124.974 | 2000/2000 | GUE |
| 120 | 0.3 | T | 19.320 | 871/2000 | 5259.783 | 2000/2000 | GUE |
| 120 | 0.3 | L | 24.498 | 530/2000 | 5275.395 | 2000/2000 | GUE |
| 120 | 0.5 | T | 6.205 | 1890/2000 | 4943.286 | 2000/2000 | GUE |
| 120 | 0.5 | L | 6.251 | 1876/2000 | 5024.017 | 2000/2000 | GUE |
| 120 | 1.0 | T | 7.075 | 1924/2000 | 4747.958 | 2000/2000 | GUE |
| 120 | 1.0 | L | 6.702 | 1926/2000 | 4779.028 | 2000/2000 | GUE |

Interpretasi terpisah dari label:

- `b=1`: S2 sangat jauh dari GUE (`p_GUE=0`) and jauh lebih dekat ke Poisson;
  tetapi `chi2_Pois` 51.7â€“73.3 masih in atas rentang tipikal Poisson, sehingga
  ini tetap **near-Poisson finite-size**, bukan kecocokan Poisson sempurna.
- `b=10`: kedua tail p in lantai (`p_GUE=0`, `p_Pois=2000/2000`); titik ini
  adalah regime antara, and label `GUE` hanya berarti jarak ternormalisasi
  lebih dekat ke GUE daripada Poisson.
- `b=120`: `p_GUE` 530â€“1926/2000 (semua `>= 0.05`) and `p_Pois=2000/2000`,
  konsisten with fase delokalisasi which jauh dari Poisson and no dapat
ditolak dari GUE on sel-sel ini.

## 6. Integritas

| b | matrix SHA-256 (exact integer payload) | max eigenvalue diff | imajiner memuat 0 | pass |
|---:|---|---:|---|---|
| 1 | `2dd3e193bea9c9e12f6498933f1134ad5bc71841f915eea6a7f817b79a63b312` | `1.088e-14` | ya | ya |
| 10 | `b7fe37c0dbd4406018be6caa6c909bb9ebb2637dd9627d29708bf13f6c823175` | `2.309e-14` | ya | ya |
| 120 | `926d3cc4ee5fbed407816d8a633ae195785b09cf6b97f45a9494f49e1dc4af71` | `6.217e-14` | ya | ya |

Spot-check memakai `acb_mat.eig` on presisi 128 bit dari entri rasional
exact; float64 hanya dipakai for membandingkan midpoint. Ini bukan
sertifikasi interval for seluruh statistik S1/S2.

## 7. Verdict

| Kriteria | Hasil | Status |
|---|---|---|
| Kalibrasi S1 | 4/4 label benar | PASS |
| Kalibrasi S2 | 12/12 label benar + `p_own>=0.05` | PASS |
| S1 monotonik + ekstrem | kedua chart; `b=1` Poisson, `b=120` GUE | PASS |
| S2 ekstrem | `b=1` 6/6 Poisson; `b=120` 6/6 GUE | PASS |
| Integritas | 3/3 spot-check + hash | PASS |
| **Total** | receipt `verdict = PASS` | **PASS** |

## 8. Batas eksplisit

- Satu dimensi `D=201`; no ada ekstrapolasi thermodynamic limit.
- Tiga bandwidth; bukan kurva fase kontinu.
- Statistik S1/S2 adalah lapisan float64 setelah entri exact; hanya
  spot-check matriks which memakai Arb.
- Label fase adalah **jarak relatif** ke null; bukan bukti kesamaan
  distribusi. Khususnya `b=1` bukan Poisson eksak and `b=10` bukan GUE eksak.
- Tidak ada klaim transisi Anderson fisik, universalitas RMT, or fisika.
- Tidak ada klaim kriptografi, faktorisasi, RSA/ECC, RH, lokasi nol, or
  `Ïƒ=1/2`.
- `PASS` in sini adalah validasi estimator on konfigurasi ini, bukan
  peer review or klaim eksternal.

## 9. Artefak and verifikasi

- Modul: `msaf/rbm_anderson.py` â€” `sha256LF ea3cce26480d06b55269865e1e18cde86e2c60510abc31159d9400695e6d73f8`
- Guard: `msaf/tests/test_rbm_anderson.py` â€” `sha256LF 5105bc429bbc1dda2a6abfd1f91039edd4423463ef981636cb0f125d162f68ba`
- Prereg: `reports/PREREG_RBM_ANDERSON_2026-10-20.md` â€” `sha256LF 62c9940a831a43e70376077d58972c49c7ef686e20751900be681606a595a014`
- Receipt: `reports/rbm_anderson_2026-10-20.json` â€” `sha256LF 4ff31e634f6250174aad30c12354f152fd8919d195b9d0883844c0f7c66c3257`
- Receipt canonical hash: `3744cbe92546256f8cb9c25c0dabb16a98921838ebfa026c07c60e5c4892bca3`
- Runtime kampanye penuh lokal: **153.74 s** (termasuk tiga spot-check Arb).
- Guard baru: **9 tests**, lulus `1.97 s`.
- Suite penuh: **480 passed** dalam **239.64 s**.
- Freeze: `verify OK: 14 pins`; digest
  `f6352884d85bab5a68c01a4e1d4a73618304464fd300d56bce1f8cc2f62baa25`.
- CI: run **39451466416** (commit `d629823`) **success**:
  `python-tests` 1m16s, `coq-kernel` 1m45s, `lean-kernel` 2m31s.
- Registry: `A-2026-0023` (5 sertifikat sha256LF).

Perintah reproduksi:

```bash
python -m msaf.rbm_anderson --out reports/rbm_anderson_2026-10-20.json
python -m pytest msaf/tests/test_rbm_anderson.py -q
python -m pytest msaf -q
python audit_quantum/freeze.py --verify
```

## 10. Hubungan with item 2

Item 2 (`A-2026-0022`) adalah sertifikat exact for permutation `Z_N^Ã—`.
Item 4 ini adalah benchmark statistik finite for estimator S1/S2; no ada
dependensi logis dari item 2, and no ada klaim baru tentang `Z_N^Ã—`,
RSA/ECC, or period-finding. Keduanya hanya berbagi disiplin pra-registrasi,
receipt deterministik, and pemisahan tegas antara inti exact and lapisan
diagnostik.


