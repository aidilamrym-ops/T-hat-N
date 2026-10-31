# Chrono Encoding – laporan implementasi 2026-10-30

**Status:** target 1, 2, 3, 5 dari `reports/PREREG_CHRONO_ENCODING_2026-10-30.md`
dikerjakan; target 4 (SAT) sudah ada dan dipertahankan; target 6 (CI) baru
sebagian; target 7 (registry) diisi terpisah.

**Bukan klaim RH, bukan Weil positivity, bukan positivity matriks, bukan
spektrum zeta.** Laporan ini hanya mencatat apa yang benar-benar dihasilkan
artefak numerik dan apa yang benar-benar diperiksa kernel Lean.

## 1. Ringkasan jujur: apa yang berubah dari revisi sebelumnya

Revisi sebelumnya mengklaim tiga teorema "encoding correctness"
(`zeta_step_encoding_correct`, `riemann_encoding_correct`, `sat_encoding_correct`).
Setelah diperiksa, ketiganya **tidak membawa isi numerik**:

- `Shape` (`ChronoNat.lean`) tidak punya payload: konstruktornya hanya
  `point`, `line`, `plane`, `space`. Tidak ada string, tidak ada ball, tidak ada
  bilangan. Jadi tidak ada encoding ke `Shape` yang information-preserving
  untuk string enclosure.
- Akibatnya `zeta_step_encoding_correct` berbentuk
  `ZetaBoundCorrect n ↔ <collapse = point>`, dengan ruas kanan **selalu benar**
  (sifat struktural `collapse_to_harmony`) dan ruas kiri konstanta placeholder.
  Itu `True ↔ True` dengan nama yang menyesatkan.

**Tindakan:** nama-nama itu dihapus, bukan dipertahankan. Penggantinya adalah
pernyataan yang punya isi dan bisa difalsifikasi (bagian 4).

## 2. Target 5 – GW bounds integration (data nyata)

`ChronoGeometric_Framework/python/export_enclosures.py::export_gw_bounds`
sekarang menghasilkan `gw_bounds.json` dari komputasi Arb nyata:

```text
sumber            msaf.zeta_inversion.xi_derivative_over_ball
box               moore_premises.json (mid/rad direkonstruksi, dilebarkan konservatif)
degree            12
```

Hasil verbatim `ChronoGeometric_Framework/lean/enclosures/gw_bounds.json`:

```text
derivative_status      VERIFIED
derivative_enclosure   [+/- 1.61e-13] + [0.0013827190892162556758 +/- 3.81e-23]j
derivative_magnitude   [0.0013827190892162556758 +/- 4.74e-23]
derivative_tail        [1.6030038524827087284e-13 +/- 2.71e-34]
character_sum_status   UNAVAILABLE
character_sum_bound    UNAVAILABLE
orthogonality_status   UNAVAILABLE
orthogonality          UNAVAILABLE
```

**Kenapa dua gate terakhir `UNAVAILABLE` dan bukan angka.** Tidak ada artefak
di repo ini yang menghasilkan bound character-sum atau sertifikat orthogonality
untuk box critical line:

- `reports/gw_character_arithmetic_2026-10-21.json` menyatakan sendiri
  `critical_line_claim: false`, `guinand_weil_matrix_constructed: false`,
  `rh_claim: false`; isinya aritmetika karakter, bukan bound analitik.
- `reports/gw_char_adhoc_2026-10-21.json` dan `gw_char_block_2026-10-21.json`
  berisi inersia matriks dan status `INCONCLUSIVE` / `CANDIDATE NOT POSITIVE
  DEFINITE`, bukan bound.
- `msaf/hodge/run_weil_search_offline.py` menjalankan uji lingkaran Weil untuk
  kuartik halus atas `F_3` (`search_a11`); itu objek yang berbeda, bukan bound
  zeta pada critical line.

Mengisi dua field itu dengan angka dari artefak tersebut akan menjadi fabrikasi
dan melanggar aturan "jangan klaim melebihi artefak". Karena itu statusnya
eksplisit `UNAVAILABLE`.

**Efek pada Lean.** Predikat kuat `ZetaBoundCorrect` sekarang **terbantah**
oleh data, bukan diasumsikan benar:

```lean
theorem zeta_gates_incomplete : ¬ ZetaBoundCorrect gw.index
theorem GwBounds.verifiedGateCount_gw : gw.verifiedGateCount = 1
theorem GwBounds.gate_status_recorded :
    gw.derivative_status = GateStatus.verified ∧
    gw.character_sum_status = GateStatus.unavailable ∧
    gw.orthogonality_status = GateStatus.unavailable
```

## 3. Target 1/2 – data enclosure dan encoding yang memakai data

`GateStatus` (`verified` / `unavailable` / `failed`) menggantikan sentinel
string `"PLACEHOLDER"`. Alasannya: sentinel membuat gate yang belum
diimplementasikan tidak bisa dibedakan dari gate yang terverifikasi pada level
tipe. Field `GwBounds` sekarang:

```text
index, t_center,
derivative_status, derivative_enclosure, derivative_magnitude, derivative_tail,
character_sum_status, character_sum_bound,
orthogonality_status, orthogonality,
degree, note
```

Encoding sekarang **membaca data**, bukan hardcode:

```lean
def ZetaStep (n : MyNat) : Shape :=
  Shape.space (List.replicate (n.toNat + gw.verifiedGateCount) Shape.point)

def sign_budget_shape (n : MyNat) : Shape :=
  Shape.space (List.replicate (n.toNat + moore.degree) Shape.point)
```

`gw.verifiedGateCount` dihitung dari status gate (saat ini 1), dan
`moore.degree` adalah 12 dari artefak. Jadi bila artefak berubah, panjang shape
ikut berubah.

## 4. Yang benar-benar dibuktikan kernel

```text
MyNat.toNat_injective              injeksi unary naturals ke Nat
ZetaStep_is_space                  ZetaStep n selalu Shape.space
ZetaStep_length                    ZetaStep n = space (replicate (n.toNat + 1) point)
ZetaStep_injective                 indeks berbeda → shape berbeda
chrono_boundary_harmony            collapse menghasilkan point (struktural)
zeta_gates_incomplete              ¬ ZetaBoundCorrect gw.index (hasil negatif)
ZetaBoundCorrect.{index_eq,derivative,character_sum,orthogonality}
                                   proyeksi predikat
sign_budget_shape_is_space         sign_budget_shape n selalu Shape.space
sign_budget_shape_length           panjang = n.toNat + 12
sign_budget_shape_injective        indeks berbeda → shape berbeda
riemann_instant_reduction          collapse menghasilkan point (struktural)
riemann_premises_hold              tiga premis Moore terbaca true dari artefak
riemann_record_degree              moore.degree = 12
sat_instant_reduction              collapse SAT state → point (struktural)
formulaToShape_is_space            formulaToShape selalu Shape.space
```

Batas yang harus dibaca bersama daftar ini:

- `ZetaStep_injective` / `sign_budget_shape_injective` adalah **faithfulness
  indeks**, bukan faithfulness numerik. Dua record dengan string berbeda tetapi
  indeks sama akan menghasilkan shape yang sama.
- `chrono_boundary_harmony` dan `riemann_instant_reduction` adalah sifat
  `collapse_to_harmony`, bukan pernyataan tentang ξ atau tentang bound GW.
- `riemann_premises_hold` menyatakan artefak merekam tiga premis `true` untuk
  satu box di sekitar nol pertama (`t ≈ 14.1347`). Ia tidak menyatakan premis
  itu berlaku untuk nol lain, dan tidak menyatakan RH.

## 5. Temuan drift (dan perbaikannya)

Guard baru `ChronoGeometric_Framework/python/test_enclosure_consistency.py`
membandingkan literal JSON dengan literal Lean. Guard itu menemukan dua drift
yang sudah ada sebelum pekerjaan ini:

| Lokasi | JSON (benar) | Lean salinan subproject (salah) |
|---|---|---|
| `moore.scope` | `...NewtonExistence.moore_box premises (invariance, ...` | `...NewtonExistence.moore_box (invariance, ...` (kata `premises` hilang) |
| `second_derivative.imag_rad` | `[3.0772113471659224520995436213954832282979623414576e-17 +/- 5.37e-68]` | `[1.1132955720550592867632011540024450368946418166161e-13 +/- 4.17e-63]` (nilai `real_rad` tersalin ke `imag_rad`) |

Keduanya diperbaiki di salinan subproject. **Salinan top-level
`lean/EnclosureData.lean` masih memuat dua literal yang sama-sama salah** dan
sengaja **tidak** disentuh di sini karena file itu tersertifikasi `T-2026-0065`
dengan baris `sha256LF`. Perbaikan file itu memerlukan entri registry baru atau
amendment atas keputusan pemilik.

## 6. Perintah verifikasi dan hasil

```text
cd ChronoGeometric_Framework && pwsh -File verify.ps1
  → lake build: Build completed successfully (3020 jobs)
  → enclosure consistency: 6 passed
  → verify: PASS

python -m pytest msaf/tests/test_authority_manifest.py \
                  msaf/tests/test_fence_registry.py \
                  msaf/tests/test_lean_axiom_audit.py \
                  msaf/tests/test_anti_circularity_gate.py \
                  ChronoGeometric_Framework/python/test_enclosure_consistency.py -q
  → 20 passed
```

Catatan proses: `reports/anti_circularity_gate_2026-10-20.log` sempat tertimpa
oleh run harness sesi sebelumnya (drift `sha256LF`). File itu dipulihkan dengan
`git restore` sebelum suite dijalankan; baris sertifikatnya kembali cocok.

## 7. Falsifier yang masih berlaku

- `gw_bounds.json` kembali memuat `PLACEHOLDER` atau gate `VERIFIED` tanpa
  produser → `test_gw_bounds_does_not_overclaim` gagal.
- Literal JSON dan literal Lean berbeda → guard drift gagal.
- Enclosure derivatif tidak lagi overlap dengan hasil hitung ulang Arb →
  `test_recorded_derivative_enclosure_recomputes` gagal.
- Ada `sorry` / `admit` / `unsafe` / `axiom` di file Lean subproject → sensor CI
  menolak.
- Ada yang menyebut laporan ini sebagai bukti RH, Weil positivity, atau kontrol
  tail seluruh matriks → klaim itu di luar lingkup dan harus ditolak.

## 8. Sisa pekerjaan (target 6/7 prereg)

1. ~~`Makefile` subproject masih memakai glob salah dan karakter rusak~~ —
   sudah diganti. `verify.ps1` adalah entry point terverifikasi
   (`lake build` + suite konsistensi + pemindaian placeholder) dan
   `Makefile` mencerminkan target yang sama untuk runner POSIX. `make` tidak
   terpasang di box Windows ini, jadi klaim "verified" hanya berlaku untuk
   `verify.ps1`.
2. Entri registry `T-2026-0066`, `T-2026-0067`, `A-2026-0053` sudah ditulis di
   `reports/FENCE_REGISTRY.md`.
3. Salinan top-level `lean/EnclosureData.lean` perlu keputusan pemilik sebelum
   dua literal drift diperbaiki (menyentuh `T-2026-0065`).
4. Gate character-sum dan orthogonality tetap `UNAVAILABLE` sampai ada produser
   yang benar-benar menghitungnya.
5. `README.md` subproject sempat mengklaim `make verify` menghasilkan
   "ANTI-CIRCULARITY GATE PASS" padahal `make` tidak ada dan gate eksternal
   tidak dipanggil dari subproject; bagian itu sudah ditulis ulang dan diberi
   catatan lingkup encoding.
