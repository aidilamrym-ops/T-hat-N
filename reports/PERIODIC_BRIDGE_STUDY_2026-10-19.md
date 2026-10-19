# Studi Jembatan Kotak Periodik ↔ Ruang Bebas (sisi terbatas [B]; jembatan [J] OPEN)

- **Tanggal:** 2026-10-19
- **Status:** studi kuantitatif sisi-terbatas (internal); **[J] TIDAK ditutup**
- **Berkas:** `msaf/periodic_bridge.py` (mode sum eksak),
  `msaf/tests/test_periodic_bridge.py` (guard),
  `reports/PERIODIC_BRIDGE_STUDY_OUTPUT_2026-10-19.txt` (output verbatim)
- **Registry:** `A-2026-0007`
- **Protokol:** menerapkan `[B]/[J]/[U]` dari `A-2026-0006`
  (`reports/BRIDGE_PROTOCOL_2026-10-19.md`)

## 1. Tujuan

Menguji secara kuantitatif apakah statistik rasio selisih pada kotak
periodik — `q(N) = (v1 - v2) / (v2 - v4)` dengan `v_r = phi_N(r,0,0)` —
mendekati nilai kontinuum ruang-bebas (untuk `1/r` murni, `q = 2`). Ini
adalah pertanyaan yang *tidak* dijawab oleh guard lama
`msaf/tests/test_tail_decay.py`: guard itu menetapkan satu titik N=16 pada
band `1.7 < q < 2.3`, bukan arah limit.

## 2. Model dan metode

Model = model tersegel `msaf/navier_stokes/fluid_lattice.py`: Laplacian
periodik 7-titik pada `T^3_N`, `dx = 1/N`, sumber titik `delta_0 - 1/N^3`
(gauge zero-mean), nilai diambil pada sumbu `(r,0,0)`.

Dua engine independen:

1. **Mode sum langsung** (`msaf/periodic_bridge.py`, O(N^3)/radius):
   `phi_N(x) = -(1/N^3) * sum_{f != 0} e^{2 pi i f.x/N} / lam_f`,
   `lam_f = (2/dx^2)(3 - cos(2 pi f_x/N) - cos(2 pi f_y/N) - cos(2 pi f_z/N))`,
   setiap suku = bola Arb dari `cos_pi` rasional eksak → enclosure rigor.
2. **Solver DFT tersegel** `_spectral_poisson_direct` (O(N^4), berhenti di
   N≈16–32).

Kesesuaian diuji dengan aturan `certify.py`: selisih kedua enclosure harus
**memuat nol eksak** (bukan perbandingan titik-tengah). Guard
`test_mode_sum_agrees_with_sealed_solver` lulus untuk N=8, r=0..4, dengan
radius kedua sisi < 1e-60.

Band valid: shell 1,2,4 memerlukan `r=4 << N/2` → N ≥ 16 (aturan yang sama
dengan record tersegel).

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

**F1 — Reproduksi independen record tersegel.** q(16) = 1.95190443254715846
(vs catatan tersegel `1.9519`); rasio mentah v1/v2 = 2.48682391781416897 dan
v2/v4 = 4.19691724489420821 (vs catatan "2.49 / 4.20"). Dua angka lama
direproduksi oleh engine yang berbeda dan lebih ketat.

**F2 — Monotonisitas rigor.** q(N) menurun tegas di seluruh band
(perbandingan Arb rigor, bukan float): 1.9519 → 1.9305 → 1.9217 → 1.9150 →
1.9127 → 1.9117 → 1.9109 pada N = 16, 20, 24, 32, 40, 48, 64.

**F3 — Increment mengecil.** Selisih q antar titik mengecil tegas
(0.02144 → 0.00880 → 0.00666 → 0.00229 → 0.000997 → 0.000783); pada
interval terakhir yang dua kali lebih lebar (48→64) penurunannya justru
lebih kecil daripada interval 8-lebar sebelumnya.

**F4 — Kesimpulan negatif (inti studi).** Gap `2 - q(64) = 0.0890732860327
± 3.89e-14`: **tidak** menuju nol. Jadi pada N ≤ 64, q(N) bergerak
**menjauh** dari nilai kontinuum 2, bukan mendekatinya. Penyebab yang
konsisten dengan model: citra periodik masih material pada r=4 (koreksi
~1/N pada tiap `g(r)` masuk ke pembilang dan penyebut dengan bobot
berbeda). **q bukan statistik jembatan**; ia tidak boleh dipakai sebagai
bukti konvergensi ke ruang bebas.

Catatan: F4 **tidak** menyalahi guard tersegel — guard itu hanya menetapkan
band satu titik (1.7 < q < 2.3) dan kontaminasi far-field < 2%, keduanya
tetap benar. F4 hanya menetapkan batas interpretasi: band sempit di satu N
bukan bukti limit.

## 5. Blok [B] / [J] / [U]

| Blok | Isi | Status |
|------|-----|--------|
| **[B]** | `phi_N(r,0,0)` untuk N = 16…64, r = 1,2,4; dua engine sepakat (containment nol); radius < 1e-60; q(N) rigor | **CERTIFIED** |
| **[J]** | Identitas jembatan: `phi_inf(r) = phi_N(r) - sum_{m != 0} G_free(r + mN)`; dibutuhkan bound ekor citra seragam pada band shell | **OPEN** — tidak ada bound yang dibuktikan di sini |
| **[U]** | Nilai/limit ruang-bebas, atau laju konvergensi q(N) | **TIDAK DIKLAIM** |

## 6. Batas

- Studi ini **hanya** menyertifikasi sisi terbatas. Tidak ada nilai limit,
  tidak ada laju konvergensi, tidak ada klaim kontinuum (`lim dx → 0` tidak
  pernah diambil; `dx = 1/N` eksak).
- F4 adalah temuan negatif tentang **statistik q**, bukan tentang model:
  model tersegel dan guard lamanya tidak berubah dan tidak disalahkan.
- Tidak menyentuh zeta/Weil/RH/P≠NP; tidak ada klaim fisik; bukan peer
  review.
- Jembatan [J] memerlukan bound ekor citra (pekerjaan terpisah); sampai itu
  ada, status jembatan tetap OPEN dan itu dicatat, bukan disembunyikan.

## 7. Reproduksi

- `python -m pytest msaf/tests/test_periodic_bridge.py -q` → 6 uji.
- Output beku: `reports/PERIODIC_BRIDGE_STUDY_OUTPUT_2026-10-19.txt`
  (capture ganda, deterministik; sha256LF di `A-2026-0007`).
- Guard registry: `python -m pytest msaf/tests/test_fence_registry.py -q`.
