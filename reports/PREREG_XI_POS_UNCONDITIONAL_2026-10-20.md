# Pra-registrasi V5 â€” positivity xi unconditional dari V3 + V4 (glue) â€” 2026-10-20

**Status:** scope DIKUNCI for paket ini; eksekusi in bawah pilihan eksplisit
pemilik "Lean V5 glue (Recommended)" on sesi 2026-10-20.

**Berkas target:** `lean/spec_v5/XiPosUnconditional.lean` (baru).
**Dependensi:** Mathlib v4.33.1; `lean/spec_v3/XiAnalyticFaithful.lean`
(`A-2026-0018`, baca-saja) and `lean/spec_v4/XiUnconditional.lean`
(`A-2026-0019`, baca-saja).
**Registry which direncanakan:** `A-2026-0021`.
**Tidak mengubah:** V1 (`A-2026-0015`), V2 (`A-2026-0017`), V3
(`A-2026-0018`), V4 (`A-2026-0019`), V6 (`A-2026-0020`), `ci.yml`
(`A-2026-0016`), `spec-v3.yml`, `spec-v4.yml`, `spec-v6.yml`, seluruh
report beku, and `lean/lakefile.toml`.

## 1. Latar

V3 membuktikan

```text
XiAnalyticFaithful.xi_pos_on_reals :
  (âˆ€ x, 0 < x â†’ x < 1 â†’ (completedRiemannZeta (x : â„‚)).re < 0) â†’
  âˆ€ x : â„, 0 < XiAnalyticFaithful.xiReal x
```

with hipotesis midpoint `hmid` eksplisit. V4 membuktikan `hmid` sebagai
teorema tertutup:

```text
hmid : âˆ€ x : â„, 0 < x â†’ x < 1 â†’
  (completedRiemannZeta (x : â„‚)).re < 0
```

V5 adalah **glue**: menerapkan `xi_pos_on_reals` V3 ke `hmid` V4. Tidak ada
konten analitik baru, no ada estimasi, no ada kisi, and no ada
parameter numerik.

## 2. Pernyataan target

```text
XiPosUnconditional.xi_pos_on_reals_unconditional :
  âˆ€ x : â„, 0 < XiAnalyticFaithful.xiReal x
```

Rute pembuktian:

```lean
XiAnalyticFaithful.xi_pos_on_reals hmid x
```

Catatan namespace: `hmid` V4 berada in **root namespace**, bukan
`XiUnconditional.hmid`; probe kompilasi already memastikan bentuk ini.

## 3. Pemisahan eksplisit dari jalur lain

Paket ini **bukan**:

- â€œV5 Campaign (H1 + engine-B)â€ â€” itu jalur dashboard/spectral which already
  selesai and beku (`reports/gw_diagnostic_v5.html`, commit `2d7b72c`;
  engine B penuh already `PASS-WITH-ENUMERATED-EXCEPTIONS`).
- â€œV5 via V6 parametersâ€ â€” V6 (`A-2026-0020`) adalah jembatan kisi
  `completedCosZeta (1/2)`, objek which berbeda; V5 no memakai V6.
- Klaim tentang 18-cell grid, 20.000 surrogate, `k_GUE = 1262/20000`,
  dim 301/chart T/Ïƒ_u 0.5, or dim 501. Semua itu artefak H1/spectral,
  bukan input V5.

Koreksi ini dicatat karena prompt â€œOPENING DEFERRED V5 VIA V6 PARAMETERSâ€
mencampur dua jalur with nama â€œV6â€ which sama. V5 which deferred adalah
glue V3+V4 in atas, bukan kampanye numerik.

## 4. Kriteria penerimaan

1. `lake env lean spec_v5/XiPosUnconditional.lean` (dari `lean/`) exit 0.
2. `#print axioms XiPosUnconditional.xi_pos_on_reals_unconditional` hanya
   memuat `propext`, `Classical.choice`, `Quot.sound`; tanpa `sorryAx`,
   tanpa aksioma proyek.
3. Guard `msaf/tests/test_xi_spec_v5.py`: pemindaian statis (tanpa `axiom`,
   tanpa `sorry/admit/unsafe`, tanpa parameter `hmid` on teorema), probe
   `#print axioms` with scratch in luar `lean/`, and pemeriksaan workflow;
   fail-closed.
4. Workflow `.github/workflows/spec-v5.yml` (pola V4/V6), scoped ke
   `lean/spec_v5/**` and guard; tanpa `continue-on-error`; membangun olean
   V3/V4 which diperlukan.
5. Gate log `reports/anti_circularity_gate_v5_2026-10-20.log`; sub-gerbang
   audit SMT tetap `TOOL NOT RUN` (no ada `.smt2`) and no dihitung
   sukses.
6. Registry `A-2026-0021` (5 sertifikat sha256LF), HANDOFF Â§2.0an,
   `test_fence_registry.py` hijau, suite penuh hijau
   (diharapkan 459 + 3 = 462), and freeze-verify OK.

## 5. Batas eksplisit

- V5 hanya menutup hipotesis `hmid` V3 memakai teorema V4. Tidak ada
  pembuktian baru tentang zeta selain glue ini.
- **Bukan** bukti Riemann Hypothesis, bukan klaim lokasi nol, bukan
  derivasi `Ïƒ = 1/2`, bukan peer review, bukan verifikasi SMT.
- Tidak menggunakan V6, H1, engine-B, dashboard, or data numerik apa pun.
- Gate PASS hanya pemindaian placeholder, bukan bukti kebenaran; kernel
  Lean adalah otoritas.

## 6. Rencana artefak

- `lean/spec_v5/XiPosUnconditional.lean`
- `msaf/tests/test_xi_spec_v5.py`
- `.github/workflows/spec-v5.yml`
- `reports/anti_circularity_gate_v5_2026-10-20.log`
- registry `A-2026-0021`
- HANDOFF Â§2.0an


