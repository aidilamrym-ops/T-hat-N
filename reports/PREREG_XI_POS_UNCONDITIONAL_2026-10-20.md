# Pra-registrasi V5 — positivity xi unconditional dari V3 + V4 (glue) — 2026-10-20

**Status:** scope DIKUNCI untuk paket ini; eksekusi di bawah pilihan eksplisit
pemilik "Lean V5 glue (Recommended)" pada sesi 2026-10-20.

**Berkas target:** `lean/spec_v5/XiPosUnconditional.lean` (baru).
**Dependensi:** Mathlib v4.33.1; `lean/spec_v3/XiAnalyticFaithful.lean`
(`A-2026-0018`, baca-saja) dan `lean/spec_v4/XiUnconditional.lean`
(`A-2026-0019`, baca-saja).
**Registry yang direncanakan:** `A-2026-0021`.
**Tidak mengubah:** V1 (`A-2026-0015`), V2 (`A-2026-0017`), V3
(`A-2026-0018`), V4 (`A-2026-0019`), V6 (`A-2026-0020`), `ci.yml`
(`A-2026-0016`), `spec-v3.yml`, `spec-v4.yml`, `spec-v6.yml`, seluruh
laporan beku, dan `lean/lakefile.toml`.

## 1. Latar

V3 membuktikan

```text
XiAnalyticFaithful.xi_pos_on_reals :
  (∀ x, 0 < x → x < 1 → (completedRiemannZeta (x : ℂ)).re < 0) →
  ∀ x : ℝ, 0 < XiAnalyticFaithful.xiReal x
```

dengan hipotesis midpoint `hmid` eksplisit. V4 membuktikan `hmid` sebagai
teorema tertutup:

```text
hmid : ∀ x : ℝ, 0 < x → x < 1 →
  (completedRiemannZeta (x : ℂ)).re < 0
```

V5 adalah **glue**: menerapkan `xi_pos_on_reals` V3 ke `hmid` V4. Tidak ada
konten analitik baru, tidak ada estimasi, tidak ada kisi, dan tidak ada
parameter numerik.

## 2. Pernyataan target

```text
XiPosUnconditional.xi_pos_on_reals_unconditional :
  ∀ x : ℝ, 0 < XiAnalyticFaithful.xiReal x
```

Rute pembuktian:

```lean
XiAnalyticFaithful.xi_pos_on_reals hmid x
```

Catatan namespace: `hmid` V4 berada di **root namespace**, bukan
`XiUnconditional.hmid`; probe kompilasi sudah memastikan bentuk ini.

## 3. Pemisahan eksplisit dari jalur lain

Paket ini **bukan**:

- “V5 Campaign (H1 + engine-B)” — itu jalur dashboard/spectral yang sudah
  selesai dan beku (`reports/gw_diagnostic_v5.html`, commit `2d7b72c`;
  engine B penuh sudah `PASS-WITH-ENUMERATED-EXCEPTIONS`).
- “V5 via V6 parameters” — V6 (`A-2026-0020`) adalah jembatan kisi
  `completedCosZeta (1/2)`, objek yang berbeda; V5 tidak memakai V6.
- Klaim tentang 18-cell grid, 20.000 surrogate, `k_GUE = 1262/20000`,
  dim 301/chart T/σ_u 0.5, atau dim 501. Semua itu artefak H1/spectral,
  bukan input V5.

Koreksi ini dicatat karena prompt “OPENING DEFERRED V5 VIA V6 PARAMETERS”
mencampur dua jalur dengan nama “V6” yang sama. V5 yang deferred adalah
glue V3+V4 di atas, bukan kampanye numerik.

## 4. Kriteria penerimaan

1. `lake env lean spec_v5/XiPosUnconditional.lean` (dari `lean/`) exit 0.
2. `#print axioms XiPosUnconditional.xi_pos_on_reals_unconditional` hanya
   memuat `propext`, `Classical.choice`, `Quot.sound`; tanpa `sorryAx`,
   tanpa aksioma proyek.
3. Guard `msaf/tests/test_xi_spec_v5.py`: pemindaian statis (tanpa `axiom`,
   tanpa `sorry/admit/unsafe`, tanpa parameter `hmid` pada teorema), probe
   `#print axioms` dengan scratch di luar `lean/`, dan pemeriksaan workflow;
   fail-closed.
4. Workflow `.github/workflows/spec-v5.yml` (pola V4/V6), scoped ke
   `lean/spec_v5/**` dan guard; tanpa `continue-on-error`; membangun olean
   V3/V4 yang diperlukan.
5. Gate log `reports/anti_circularity_gate_v5_2026-10-20.log`; sub-gerbang
   audit SMT tetap `TOOL NOT RUN` (tidak ada `.smt2`) dan tidak dihitung
   sukses.
6. Registry `A-2026-0021` (5 sertifikat sha256LF), HANDOFF §2.0an,
   `test_fence_registry.py` hijau, suite penuh hijau
   (diharapkan 459 + 3 = 462), dan freeze-verify OK.

## 5. Batas eksplisit

- V5 hanya menutup hipotesis `hmid` V3 memakai teorema V4. Tidak ada
  pembuktian baru tentang zeta selain glue ini.
- **Bukan** bukti Riemann Hypothesis, bukan klaim lokasi nol, bukan
  derivasi `σ = 1/2`, bukan peer review, bukan verifikasi SMT.
- Tidak menggunakan V6, H1, engine-B, dashboard, atau data numerik apa pun.
- Gate PASS hanya pemindaian placeholder, bukan bukti kebenaran; kernel
  Lean adalah otoritas.

## 6. Rencana artefak

- `lean/spec_v5/XiPosUnconditional.lean`
- `msaf/tests/test_xi_spec_v5.py`
- `.github/workflows/spec-v5.yml`
- `reports/anti_circularity_gate_v5_2026-10-20.log`
- registry `A-2026-0021`
- HANDOFF §2.0an
