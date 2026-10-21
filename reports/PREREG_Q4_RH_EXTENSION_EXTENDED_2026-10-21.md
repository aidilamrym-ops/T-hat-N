# Pra-registrasi: RH Extension Lanjutan — Konduktor T > 100 — 2026-10-21

**Status:** scope DIKUNCI untuk paket Q4-Extended; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket Q4-Extended. Hash `sha256LF` berkas ini
dicatat di receipt dan laporan.

**Paket:** Q4-Extended (lanjutan dari Q4 yang sudah CERTIFIED `A-2026-0033`),
yaitu Ekstensi RH ke konduktor T > 100 dengan mesin Route S ladder yang sama,
winding cross-lock, dan ukur-dinding-dulu.

**Berkas target:** `msaf/gw_rh_extension_extended.py` (baru), guard
`msaf/tests/test_gw_rh_extension_extended.py` (baru), laporan
`reports/RH_EXTENSION_EXTENDED_2026-10-21.md`, receipt
`reports/rh_extension_extended.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`acb`, `arb`), `msaf/gw_route_s_ladder.py`, `msaf/gw_character_arithmetic.py`, `msaf/gw_rh_extension.py` (base). Tidak ada `numpy`/`scipy` di jalur inti.

**Registry yang direncanakan:** `A-2026-0034`, hanya bila verdict inti
`ALL PASS` dan integritas PASS.

**Tidak mengubah:** V1–V6 (`A-2026-0015`–`A-2026-0021`), `A-2026-0022`–`A-2026-0033`, `ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins, seluruh laporan/artefak beku.

## 1. Maksud dan batas

Paket ini melakukan **ekstensi RH ke konduktor T > 100** menggunakan mesin
Route S ladder yang sama (yang sudah tersegel untuk c = 100 Montgomery
construction), ditambah mekanisme **winding cross-lock** dan prosedur
**ukur-dinding-dulu** (measure wall first).

**Objek komputasi:**
- Matriks Guinand-Weil terpotong untuk karakter Dirichlet non-primitif dengan konduktor T ∈ {100, 200, 300, 400, 500} (atau subset yang feasible)
- Blok τ = W₀₂ - W_R - W_p dengan karakter χ_{T,n} induced by modulus T
- Mekanisme winding cross-lock: memastikan konsistensi winding number lintas blok
- Prosedur ukur-dinding-dulu: tentukan batas eigenvalue (wall) sebelum komputasi spektral penuh

**Paket ini BUKAN:**
- Pembuktian RH (hanya ekstensi finit hingga T_max)
- Klaim asimtotik (hanya komputasi hingga T_max)
- Klaim σ = 1/2, lokasi nol, faktorisasi, RSA/ECC, Anderson, atau fisika
- Rerun kampanye H1/Engine B/Quantum yang sudah tersegel

## 2. Definisi yang dikunci

**Konduktor T:** T ∈ {100, 200, 300, 400, 500} (akan dipilih subset feasible berdasarkan runtime)
- T=100: sudah tersegel (baseline)
- T=200, 300, 400, 500: konduktor non-primitif berikutnya (faktor 2²·5², 2³·5², 2²·5³, 2³·5³, etc)

**Mesin yang sama:** Route S ladder (LDL^T interval Arb 6000-bit) + karakter aritmatik (Option A/B yang tersegel)

**Winding cross-lock:** Mekanisme yang memastikan winding number dari blok karakter (W_p) konsisten dengan winding Archimedean (W₀₂, W_R) — tidak ada "crossing" tanpa sertifikat.

**Ukur-dinding-dulu:** Sebelum komputasi spektral penuh, hitung batas eigenvalue minimum (wall) menggunakan estimasi Chebyshev/Trace formula untuk menentukan range komputasi yang aman.

**Resolusi per T:** N=100 (dim 201) baseline; opsi N=150 (dim 301) untuk resolusi 2

## 3. Algoritma yang dikunci

**Langkah 1: Ukur Dinding (Wall Measurement)**
- Gunakan rumus Trace Chebyshev untuk estimasi eigenvalue minimum
- Tentukan batas bawah λ_min_est > 0 yang aman (margin ≥ 10⁻³ dari 0 relative)
- Jika λ_min_est ≤ threshold: STOP untuk T tersebut, verdict INCONCLUSIVE

**Langkah 2: Winding Cross-lock Verification**
- Hitung winding number untuk setiap blok: W₀₂, W_R, W_p
- Verifikasi: |winding(W_p) - winding(W_R) - winding(W_02)| ≤ 1 (cross-lock condition)
- Jika gagal: STOP untuk T tersebut, verdict INCONCLUSIVE

**Langkah 3: Komputasi Spektral Penuh (jika L1 & L2 PASS)**
- Bangun matriks τ terpotong dimensi dim = 2N+1 untuk N yang dipilih
- LDL^T interval (Arb 6000-bit) untuk sertifikat positive-definite
- Gate G-M0: n_pos = dim, n_neg = 0, entries_finite = true
- Capture eigenvalue minimum dengan sertifikat

**Langkah 4: Dual-engine Verification (Engine A + Engine B)**
- Engine A: Arb 6000-bit (canonical)
- Engine B: mpmath dps 50 (independent verification)
- Kesepakatan: λ_min_A ≈ λ_min_B (rel_tol ≤ 1e-12), verdict identik

## 4. Konfigurasi yang dikunci

| Parameter | Nilai |
|-----------|-------|
| Konduktor T | 100 (baseline), 200, 300, 400, 500 (subset feasible) |
| Presisi Arb | 6000 bit |
| Dimensi N | 100 (dim 201) baseline; opsi N=150 (dim 301) |
| Threshold wall | λ_min_est > 0 (positive definiteness) |
| Cross-lock tol | |Δwinding| ≤ 1 |
| Engine B dps | 50 |
| Timeout per T | 30 menit (fail-closed) |

Tidak ada parameter tambahan setelah hasil terlihat.

## 5. Pemeriksaan integritas (C1–C4)

**C1: Wall measurement PASS** untuk setiap T yang dieksekusi
- λ_min_est > threshold dengan margin dokumentasi

**C2: Winding cross-lock PASS** untuk setiap T yang dieksekusi
- |Δwinding| ≤ 1 untuk semua blok

**C3: Spektral PASS (Engine A)** untuk setiap T yang dieksekusi
- G-M0 PASS: n_pos = dim, n_neg = 0, entries_finite = true
- λ_min > 0 dengan sertifikat

**C4: Dual-engine agreement** untuk setiap T yang dieksekusi
- λ_min_A ≈ λ_min_B (rel_tol ≤ 1e-12)
- Verdict identik (PASS/FAIL/INCONCLUSIVE)

## 6. Verdict

- **ALL PASS**: C1–C4 PASS untuk semua T yang dieksekusi
- **PARTIAL**: Beberapa T PASS, beberapa INCONCLUSIVE/FAILED (dokumentasikan)
- **FAILED**: C1 atau C2 gagal untuk T yang dipilih
- **INCONCLUSIVE**: Tool error, memori tidak cukup, timeout, atau hash mismatch

Registry `A-2026-0034` hanya bila verdict `ALL PASS` untuk minimal T ∈ {100, 200, 300} dan integritas PASS.

## 7. Falsifier

Paket ini falsified bila:
- λ_min_est ≤ threshold untuk T yang dipilih
- |Δwinding| > 1 untuk T yang dipilih
- G-M0 FAIL pada Engine A untuk T yang dipilih
- λ_min_A dan λ_min_B tidak sepakat (rel_tol > 1e-12)
- Timeout > 30 menit per T
- Receipt tidak deterministik atau hash mismatch

## 8. Artefak dan urutan eksekusi

1. Tulis dan hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/gw_rh_extension_extended.py` meng-extends `gw_rh_extension.py`.
3. Guard `msaf/tests/test_gw_rh_extension_extended.py`: uji wall measurement, cross-lock, spektral, dual-engine untuk multiple T.
4. Jalankan kampanye untuk T ∈ {100, 200, 300, 400, 500} (urut naik, stop kalau timeout/FAILED).
5. Tulis laporan `reports/RH_EXTENSION_EXTENDED_2026-10-21.md` dengan angka verbatim per T.
6. Bila `ALL PASS`: registry `A-2026-0034`, HANDOFF §2.0ba, sertifikat sha256LF.
7. Suite penuh dan `freeze.py --verify`; commit/push hanya bila diminta.

## 9. Batas eksplisit

- Hanya T ≤ 500 untuk kampanye ini (feasibility)
- Hanya Route S ladder + karakter aritmatik tersegel (Option A/B)
- Tidak ada klaim RH terbukti/tidak terbukti
- Tidak ada klaim σ = 1/2, lokasi nol, faktorisasi, RSA/ECC, Anderson, fisika
- Tidak ada klaim asimtotik
- Tidak merubah/mengulang kampanye H1/Engine B/Quantum yang tersegel