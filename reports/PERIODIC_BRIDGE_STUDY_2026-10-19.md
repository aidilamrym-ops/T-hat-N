# Studi Jembatan Kotak Periodik â†” Ruang Bebas (sisi terbatas [B]; jembatan [J] OPEN)

- **Tanggal:** 2026-10-19
- **Status:** studi kuantitatif sisi-terbatas (internal); **[J] TIDAK ditutup**
- **Berkas:** `msaf/periodic_bridge.py` (mode sum eksak),
  `msaf/tests/test_periodic_bridge.py` (guard),
  `reports/PERIODIC_BRIDGE_STUDY_OUTPUT_2026-10-19.txt` (output verbatim)
- **Registry:** `A-2026-0007`
- **Protokol:** menerapkan `[B]/[J]/[U]` dari `A-2026-0006`
  (`reports/BRIDGE_PROTOCOL_2026-10-19.md`)

## 1. Tujuan

Menguji secara kuantitatif apakah statistik rasio selisih on kotak
periodik â€” `q(N) = (v1 - v2) / (v2 - v4)` with `v_r = phi_N(r,0,0)` â€”
mendekati nilai kontinuum ruang-bebas (for `1/r` murni, `q = 2`). Ini
adalah question which *no* dijawab oleh guard lama
`msaf/tests/test_tail_decay.py`: guard itu menetapkan satu titik N=16 on
band `1.7 < q < 2.3`, bukan arah limit.

## 2. Model and metode

Model = model tersegel `msaf/navier_stokes/fluid_lattice.py`: Laplacian
periodik 7-titik on `T^3_N`, `dx = 1/N`, source titik `delta_0 - 1/N^3`
(gauge zero-mean), nilai diambil on sumbu `(r,0,0)`.

Dua engine independen:

1. **Mode sum langsung** (`msaf/periodic_bridge.py`, O(N^3)/radius):
   `phi_N(x) = -(1/N^3) * sum_{f != 0} e^{2 pi i f.x/N} / lam_f`,
   `lam_f = (2/dx^2)(3 - cos(2 pi f_x/N) - cos(2 pi f_y/N) - cos(2 pi f_z/N))`,
   setiap suku = bola Arb dari `cos_pi` rasional eksak â†’ enclosure rigor.
2. **Solver DFT tersegel** `_spectral_poisson_direct` (O(N^4), berhenti in
   Nâ‰ˆ16â€“32).

Kesesuaian diuji with aturan `certify.py`: selisih kedua enclosure harus
**memuat nol eksak** (bukan perbandingan titik-tengah). Guard
`test_mode_sum_agrees_with_sealed_solver` lulus for N=8, r=0..4, with
radius kedua sisi < 1e-60.

Band valid: shell 1,2,4 memerlukan `r=4 << N/2` â†’ N â‰¥ 16 (aturan which sama
with record tersegel).

## 3. Hasil (verbatim)

```text
PERIODIC-BOX BRIDGE STUDY -- bounded side only ([B]); [J] OPEN
arb precision: 256
model: sealed 7-point periodic Laplacian T^3_N, dx = 1/N, zero-mean gauge
statistic: q(N) = (v1 - v2) / (v2 - v4), v_r = phi_N(r,0,0)

N     v1                        v2                        v4                        q(N)                      q.rad()                   dq (prev - this)         2 - q
16    [-0.000281266961104 +/- 4.13e-16] [-0.000113102885608 +/- 7.51e-17] [-2.69490387845e-5 +/- 1.58e-17] [1.95190443254715846 +/- 4.93e-18] [2.99e-73 +/- 2.16e-77]                             [0.0480956 +/- 3.26e-8]
20    [-0.000187003548235 +/- 1.89e-16] [-7.92246095693e-5 +/- 2.52e-17] [-2.33940709735e-5 +/- 4.05e-17] [1.93046568019302865 +/- 1.12e-18] [7.09e-73 +/- 4.38e-76]   [0.0214388 +/- 4.77e-8]   [0.0695343 +/- 1.99e-8]
24    [-0.000133110846270 +/- 2.31e-16] [-5.82176521427e-5 +/- 2.20e-17] [-1.92445236797e-5 +/- 9.23e-18] [1.92166236277617725 +/- 4.62e-18] [1.11e-72 +/- 4.07e-75]   [0.00880332 +/- 2.59e-9]  [0.0783376 +/- 3.73e-8]
32    [-7.71630574051e-5 +/- 3.94e-17] [-3.50149319514e-5 +/- 2.87e-17] [-1.30054500131e-5 +/- 1.11e-17] [1.91499852526242432 +/- 4.81e-19] [2.54e-72 +/- 3.68e-75]   [0.00666384 +/- 2.49e-9]  [0.0850015 +/- 2.53e-8]
40    [-5.02643735262e-5 +/- 4.24e-17] [-2.32848816713e-5 +/- 3.81e-17] [-9.17948043577e-6 +/- 1.97e-18] [1.91270644516489779 +/- 1.22e-18] [5.00e-72 +/- 2.13e-75]   [0.00229208 +/- 9.77e-11] [0.0872936 +/- 4.52e-8]
48    [-3.53135357687e-5 +/- 1.95e-17] [-1.65763414008e-5 +/- 2.37e-17] [-6.77506527975e-6 +/- 1.32e-18] [1.91170967294877183 +/- 2.83e-18] [8.13e-72 +/- 3.83e-75]   [0.000996772 +/- 2.17e-10] [0.0882903 +/- 2.71e-8]
64    [-2.01506965356e-5 +/- 4.85e-17] [-9.61038439467e-6 +/- 4.14e-18] [-4.09457258257e-6 +/- 4.36e-18] [1.91092671396726121 +/- 1.75e-18] [2.05e-71 +/- 4.00e-74]   [0.000782959 +/- 1.86e-11] [0.0890733 +/- 1.40e-8]

q(N) strictly decreasing over band (rigorous): True
increments strictly shrinking (rigorous)    : True
last certified gap 2 - q(64)                : [0.0890732860327 +/- 3.89e-14]

naive ratios at N=16 (NOT bridge-valid: gauge + image background):
  v1/v2 = [2.48682391781416897 +/- 3.14e-18]   (continuum 1/r would give 2)
  v2/v4 = [4.19691724489420821 +/- 3.76e-18]   (continuum 1/r would give 2)

sealed record (test_tail_decay.py, N=16): q = 1.9519; far-field < 2% (0.61%)
band rule: shells 1,2,4 require r=4 << N/2 (N >= 16 here)
no rate claimed; no limit value claimed; continuum limit NOT taken
```

## 4. Temuan

**F1 â€” Reproduksi independen record tersegel.** q(16) = 1.95190443254715846
(vs note tersegel `1.9519`); rasio mentah v1/v2 = 2.48682391781416897 and
v2/v4 = 4.19691724489420821 (vs note "2.49 / 4.20"). Dua angka lama
direproduksi oleh engine which berbeda and lebih ketat.

**F2 â€” Monotonisitas rigor.** q(N) menurun tegas in seluruh band
(perbandingan Arb rigor, bukan float): 1.9519 â†’ 1.9305 â†’ 1.9217 â†’ 1.9150 â†’
1.9127 â†’ 1.9117 â†’ 1.9109 on N = 16, 20, 24, 32, 40, 48, 64.

**F3 â€” Increment mengecil.** Selisih q antar titik mengecil tegas
(0.02144 â†’ 0.00880 â†’ 0.00666 â†’ 0.00229 â†’ 0.000997 â†’ 0.000783); on
interval terakhir which dua kali lebih lebar (48â†’64) penurunannya justru
lebih kecil daripada interval 8-lebar sebelumnya.

**F4 â€” Kesimpulan negatif (inti studi).** Gap `2 - q(64) = 0.0890732860327
Â± 3.89e-14`: **no** menuju nol. Jadi on N â‰¤ 64, q(N) bergerak
**menjauh** dari nilai kontinuum 2, bukan mendekatinya. Penyebab which
konsisten with model: citra periodik masih material on r=4 (koreksi
~1/N on tiap `g(r)` masuk ke pembilang and penyebut with bobot
berbeda). **q bukan statistik jembatan**; ia no boleh dipakai sebagai
bukti konvergensi ke ruang bebas.

Catatan: F4 **no** menyalahi guard tersegel â€” guard itu hanya menetapkan
band satu titik (1.7 < q < 2.3) and kontaminasi far-field < 2%, keduanya
tetap benar. F4 hanya menetapkan limit interpretasi: band sempit in satu N
bukan bukti limit.

## 5. Blok [B] / [J] / [U]

| Blok | Isi | Status |
|------|-----|--------|
| **[B]** | `phi_N(r,0,0)` for N = 16â€¦64, r = 1,2,4; dua engine sepakat (containment nol); radius < 1e-60; q(N) rigor | **CERTIFIED** |
| **[J]** | Identitas jembatan: `phi_inf(r) = phi_N(r) - sum_{m != 0} G_free(r + mN)`; dibutuhkan bound ekor citra seragam on band shell | **OPEN** â€” no ada bound which dibuktikan in sini |
| **[U]** | Nilai/limit ruang-bebas, or laju konvergensi q(N) | **TIDAK DIKLAIM** |

## 6. Batas

- Studi ini **hanya** menyertifikasi sisi terbatas. Tidak ada nilai limit,
  no ada laju konvergensi, no ada klaim kontinuum (`lim dx â†’ 0` no
  pernah diambil; `dx = 1/N` eksak).
- F4 adalah temuan negatif tentang **statistik q**, bukan tentang model:
  model tersegel and guard lamanya no berubah and no disalahkan.
- Tidak menyentuh zeta/Weil/RH/Pâ‰ NP; no ada klaim fisik; bukan peer
  review.
- Jembatan [J] memerlukan bound ekor citra (pekerjaan terpisah); sampai itu
  ada, status jembatan tetap OPEN and itu dicatat, bukan disembunyikan.

## 7. Reproduksi

- `python -m pytest msaf/tests/test_periodic_bridge.py -q` â†’ 6 uji.
- Output beku: `reports/PERIODIC_BRIDGE_STUDY_OUTPUT_2026-10-19.txt`
  (capture ganda, deterministik; sha256LF in `A-2026-0007`).
- Guard registry: `python -m pytest msaf/tests/test_fence_registry.py -q`.


