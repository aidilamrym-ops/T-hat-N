# Pra-registrasi: RH Extension Lanjutan â€” Konduktor T > 100 â€” 2026-10-21

**Status:** scope DIKUNCI for paket Q4-Extended; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket Q4-Extended. Hash `sha256LF` file ini
dicatat in receipt and report.

**Paket:** Q4-Extended (lanjutan dari Q4 which already CERTIFIED `A-2026-0033`),
yaitu Ekstensi RH ke konduktor T > 100 with mesin Route S ladder which sama,
winding cross-lock, and ukur-dinding-dulu.

**Berkas target:** `msaf/gw_rh_extension_extended.py` (baru), guard
`msaf/tests/test_gw_rh_extension_extended.py` (baru), report
`reports/RH_EXTENSION_EXTENDED_2026-10-21.md`, receipt
`reports/rh_extension_extended.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`acb`, `arb`), `msaf/gw_route_s_ladder.py`, `msaf/gw_character_arithmetic.py`, `msaf/gw_rh_extension.py` (base). Tidak ada `numpy`/`scipy` in jalur inti.

**Registry which direncanakan:** `A-2026-0034`, hanya bila verdict inti
`ALL PASS` and integritas PASS.

**Tidak mengubah:** V1â€“V6 (`A-2026-0015`â€“`A-2026-0021`), `A-2026-0022`â€“`A-2026-0033`, `ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins, seluruh report/artefak beku.

## 1. Maksud and limit

Paket ini melakukan **ekstensi RH ke konduktor T > 100** menggunakan mesin
Route S ladder which sama (which already tersegel for c = 100 Montgomery
construction), ditambah mekanisme **winding cross-lock** and prosedur
**ukur-dinding-dulu** (measure wall first).

**Objek komputasi:**
- Matriks Guinand-Weil terpotong for karakter Dirichlet non-primitif with konduktor T âˆˆ {100, 200, 300, 400, 500} (or subset which feasible)
- Blok Ï„ = Wâ‚€â‚‚ - W_R - W_p with karakter Ï‡_{T,n} induced by modulus T
- Mekanisme winding cross-lock: memastikan konsistensi winding number lintas blok
- Prosedur ukur-dinding-dulu: tentukan limit eigenvalue (wall) sebelum komputasi spektral penuh

**Paket ini BUKAN:**
- Pembuktian RH (hanya ekstensi finit hingga T_max)
- Klaim asimtotik (hanya komputasi hingga T_max)
- Klaim Ïƒ = 1/2, lokasi nol, faktorisasi, RSA/ECC, Anderson, or fisika
- Rerun kampanye H1/Engine B/Quantum which already tersegel

## 2. Definisi which dikunci

**Konduktor T:** T âˆˆ {100, 200, 300, 400, 500} (akan dipilih subset feasible berdasarkan runtime)
- T=100: already tersegel (baseline)
- T=200, 300, 400, 500: konduktor non-primitif berikutnya (faktor 2Â²Â·5Â², 2Â³Â·5Â², 2Â²Â·5Â³, 2Â³Â·5Â³, etc)

**Mesin which sama:** Route S ladder (LDL^T interval Arb 6000-bit) + karakter aritmatik (Option A/B which tersegel)

**Winding cross-lock:** Mekanisme which memastikan winding number dari blok karakter (W_p) konsisten with winding Archimedean (Wâ‚€â‚‚, W_R) â€” no ada "crossing" tanpa sertifikat.

**Ukur-dinding-dulu:** Sebelum komputasi spektral penuh, hitung limit eigenvalue minimum (wall) menggunakan estimasi Chebyshev/Trace formula for menentukan range komputasi which aman.

**Resolusi per T:** N=100 (dim 201) baseline; opsi N=150 (dim 301) for resolusi 2

## 3. Algoritma which dikunci

**Langkah 1: Ukur Dinding (Wall Measurement)**
- Gunakan rumus Trace Chebyshev for estimasi eigenvalue minimum
- Tentukan limit bawah Î»_min_est > 0 which aman (margin â‰¥ 10â»Â³ dari 0 relative)
- Jika Î»_min_est â‰¤ threshold: STOP for T tersebut, verdict INCONCLUSIVE

**Langkah 2: Winding Cross-lock Verification**
- Hitung winding number for setiap blok: Wâ‚€â‚‚, W_R, W_p
- Verifikasi: |winding(W_p) - winding(W_R) - winding(W_02)| â‰¤ 1 (cross-lock condition)
- Jika gagal: STOP for T tersebut, verdict INCONCLUSIVE

**Langkah 3: Komputasi Spektral Penuh (jika L1 & L2 PASS)**
- Bangun matriks Ï„ terpotong dimensi dim = 2N+1 for N which dipilih
- LDL^T interval (Arb 6000-bit) for sertifikat positive-definite
- Gate G-M0: n_pos = dim, n_neg = 0, entries_finite = true
- Capture eigenvalue minimum with sertifikat

**Langkah 4: Dual-engine Verification (Engine A + Engine B)**
- Engine A: Arb 6000-bit (canonical)
- Engine B: mpmath dps 50 (independent verification)
- Kesepakatan: Î»_min_A â‰ˆ Î»_min_B (rel_tol â‰¤ 1e-12), verdict identik

## 4. Konfigurasi which dikunci

| Parameter | Nilai |
|-----------|-------|
| Konduktor T | 100 (baseline), 200, 300, 400, 500 (subset feasible) |
| Presisi Arb | 6000 bit |
| Dimensi N | 100 (dim 201) baseline; opsi N=150 (dim 301) |
| Threshold wall | Î»_min_est > 0 (positive definiteness) |
| Cross-lock tol | |Î”winding| â‰¤ 1 |
| Engine B dps | 50 |
| Timeout per T | 30 menit (fail-closed) |

Tidak ada parameter tambahan setelah result terlihat.

## 5. Pemeriksaan integritas (C1â€“C4)

**C1: Wall measurement PASS** for setiap T which dieksekusi
- Î»_min_est > threshold with margin dokumentasi

**C2: Winding cross-lock PASS** for setiap T which dieksekusi
- |Î”winding| â‰¤ 1 for semua blok

**C3: Spektral PASS (Engine A)** for setiap T which dieksekusi
- G-M0 PASS: n_pos = dim, n_neg = 0, entries_finite = true
- Î»_min > 0 with sertifikat

**C4: Dual-engine agreement** for setiap T which dieksekusi
- Î»_min_A â‰ˆ Î»_min_B (rel_tol â‰¤ 1e-12)
- Verdict identik (PASS/FAIL/INCONCLUSIVE)

## 6. Verdict

- **ALL PASS**: C1â€“C4 PASS for semua T which dieksekusi
- **PARTIAL**: Beberapa T PASS, beberapa INCONCLUSIVE/FAILED (dokumentasikan)
- **FAILED**: C1 or C2 gagal for T which dipilih
- **INCONCLUSIVE**: Tool error, memori no cukup, timeout, or hash mismatch

Registry `A-2026-0034` hanya bila verdict `ALL PASS` for minimal T âˆˆ {100, 200, 300} and integritas PASS.

## 7. Falsifier

Paket ini falsified bila:
- Î»_min_est â‰¤ threshold for T which dipilih
- |Î”winding| > 1 for T which dipilih
- G-M0 FAIL on Engine A for T which dipilih
- Î»_min_A and Î»_min_B no sepakat (rel_tol > 1e-12)
- Timeout > 30 menit per T
- Receipt no deterministik or hash mismatch

## 8. Artefak and urutan eksekusi

1. Tulis and hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/gw_rh_extension_extended.py` meng-extends `gw_rh_extension.py`.
3. Guard `msaf/tests/test_gw_rh_extension_extended.py`: uji wall measurement, cross-lock, spektral, dual-engine for multiple T.
4. Jalankan kampanye for T âˆˆ {100, 200, 300, 400, 500} (urut naik, stop kalau timeout/FAILED).
5. Tulis report `reports/RH_EXTENSION_EXTENDED_2026-10-21.md` with angka verbatim per T.
6. Bila `ALL PASS`: registry `A-2026-0034`, HANDOFF Â§2.0ba, sertifikat sha256LF.
7. Suite penuh and `freeze.py --verify`; commit/push hanya bila diminta.

## 9. Batas eksplisit

- Hanya T â‰¤ 500 for kampanye ini (feasibility)
- Hanya Route S ladder + karakter aritmatik tersegel (Option A/B)
- Tidak ada klaim RH terbukti/no terbukti
- Tidak ada klaim Ïƒ = 1/2, lokasi nol, faktorisasi, RSA/ECC, Anderson, fisika
- Tidak ada klaim asimtotik
- Tidak merubah/mengulang kampanye H1/Engine B/Quantum which tersegel

