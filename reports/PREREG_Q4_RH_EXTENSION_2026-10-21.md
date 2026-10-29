# Pra-registrasi: RH Extension â€” T = 100 (winding cross-lock) â€” 2026-10-21

**Status:** scope DIKUNCI for paket Q4; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket Q4. Hash `sha256LF` file ini
dicatat in receipt and report.

**Paket:** Q4 dari
[`reports/DAFTAR_MASALAH_KERJA.md`](DAFTAR_MASALAH_KERJA.md),
yaitu Ekstensi RH â€” Fragmen: T = 100 with mesin which sama (COMPLETE + winding cross-lock), DENGAN ukur-dinding-dulu.

**Berkas target:** `msaf/gw_rh_extension.py` (baru), guard
`msaf/tests/test_gw_rh_extension.py` (baru), report
`reports/RH_EXTENSION_2026-10-21.md`, receipt
`reports/rh_extension_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`acb`, `arb`), `msaf/gw_route_s_ladder.py`, `msaf/gw_character_arithmetic.py`. Tidak ada `numpy`/`scipy` in jalur inti.

**Registry which direncanakan:** `A-2026-0033`, hanya bila verdict inti
`ALL PASS` and integritas PASS.

**Tidak mengubah:** V1â€“V6 (`A-2026-0015`â€“`A-2026-0021`), `A-2026-0022`â€“`A-2026-0032`, `ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins, seluruh report/artefak beku.

## 1. Maksud and limit

Paket ini melakukan **ekstensi RH ke konduktor T = 100** menggunakan mesin
Guinand-Weil Route S which sama (which already tersegel for c = 100 Montgomery
construction), ditambah mekanisme **winding cross-lock** and prosedur
**ukur-dinding-dulu** (measure wall first).

**Objek komputasi:**
- Matriks Guinand-Weil terpotong for karakter Dirichlet non-primitif with konduktor T = 100
- Blok Ï„ = Wâ‚€â‚‚ - W_R - W_p with karakter Ï‡_{q,n} induced by modulus q = 100
- Mekanisme winding cross-lock: memastikan konsistensi winding number lintas blok
- Prosedur ukur-dinding-dulu: tentukan limit eigenvalue (wall) sebelum komputasi spektral penuh

**Paket ini BUKAN:**
- Pembuktian RH (hanya ekstensi finit hingga T = 100)
- Klaim asimtotik (hanya komputasi hingga T = 100)
- Klaim Ïƒ = 1/2, lokasi nol, faktorisasi, RSA/ECC, Anderson, or fisika
- Rerun kampanye H1/Engine B/Quantum which already tersegel

## 2. Definisi which dikunci

**Konduktor T:** T = 100 (konduktor karakter Dirichlet non-primitif)

**Mesin which sama:** Route S ladder (LDL^T interval Arb 6000-bit) + karakter aritmatik (Option A/B which tersegel)

**Winding cross-lock:** Mekanisme which memastikan winding number dari blok karakter (W_p) konsisten with winding Archimedean (Wâ‚€â‚‚, W_R) â€” no ada "crossing" tanpa sertifikat.

**Ukur-dinding-dulu:** Sebelum komputasi spektral penuh, hitung limit eigenvalue minimum (wall) menggunakan estimasi Chebyshev/Trace formula for menentukan range komputasi which aman.

**Karakter target:** Ï‡_{100,n} non-primitif which terinduksi dari modulus 100 (faktor 2Â²Â·5Â²)

## 3. Algoritma which dikunci

**Langkah 1: Ukur dinding (Wall Measurement)**
- Gunakan rumus Trace Chebyshev for estimasi eigenvalue minimum
- Tentukan limit bawah Î»_min_est > 0 which aman (margin â‰¥ 10â»Â³ dari 0)
- Jika Î»_min_est â‰¤ threshold: STOP, verdict INCONCLUSIVE

**Langkah 2: Winding cross-lock verification**
- Hitung winding number for setiap blok: Wâ‚€â‚‚, W_R, W_p
- Verifikasi: |winding(W_p) - winding(W_R) - winding(Wâ‚€â‚‚)| â‰¤ 1 (cross-lock condition)
- Jika gagal: STOP, verdict INCONCLUSIVE

**Langkah 3: Komputasi spektral penuh (jika L1 & L2 PASS)**
- Bangun matriks Ï„ terpotong dimensi dim = 2N+1 for N which dipilih
- LDL^T interval (Arb 6000-bit) for sertifikat positive-definite
- Gate G-M0: n_pos = dim, n_neg = 0, entries_finite = true
- Capture eigenvalue minimum with sertifikat

**Langkah 4: Dual-engine verification (Engine A + Engine B)**
- Engine A: Arb 6000-bit (canonical)
- Engine B: mpmath dps 50 (independent verification)
- Kesepakatan: Î»_min_A â‰ˆ Î»_min_B (rel_tol â‰¤ 1e-12), verdict identik

## 4. Konfigurasi which dikunci

| Parameter | Nilai |
|-----------|-------|
| Konduktor T | 100 |
| Presisi Arb | 6000 bit |
| Dimensi N | 100 (dim 201) for baseline; opsi N=150 (dim 301) for resolusi 2 |
| Threshold wall | Î»_min_est > 1e-3 |
| Cross-lock tol | |Î”winding| â‰¤ 1 |
| Engine B dps | 50 |

Tidak ada parameter tambahan setelah result terlihat.

## 5. Pemeriksaan integritas (C1â€“C4)

**C1: Wall measurement PASS**
- Î»_min_est > threshold with margin dokumentasi

**C2: Winding cross-lock PASS**
- |Î”winding| â‰¤ 1 for semua blok

**C3: Spektral PASS (Engine A)**
- G-M0 PASS: n_pos = dim, n_neg = 0, entries_finite = true
- Î»_min > 0 with sertifikat

**C4: Dual-engine agreement**
- Î»_min_A â‰ˆ Î»_min_B (rel_tol â‰¤ 1e-12)
- Verdict identik (PASS/FAIL/INCONCLUSIVE)

## 6. Verdict

- **ALL PASS**: C1, C2, C3, C4 PASS for T = 100
- **PARTIAL**: C1/C2 PASS tapi C3/C4 gagal (dokumentasikan sebab)
- **FAILED**: C1 or C2 gagal (wall measurement or cross-lock gagal)
- **INCONCLUSIVE**: Tool error, memori no cukup, or hash mismatch

Registry `A-2026-0033` hanya bila verdict `ALL PASS` and integritas PASS.

## 7. Falsifier

Paket ini falsified bila:
- Î»_min_est â‰¤ threshold (dinding no aman)
- |Î”winding| > 1 (cross-lock violated)
- G-M0 FAIL on Engine A
- Î»_min_A and Î»_min_B no sepakat (rel_tol > 1e-12)
- Receipt no deterministik or hash mismatch

## 8. Artefak and urutan eksekusi

1. Tulis and hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/gw_rh_extension.py` with 4 step in atas.
3. Guard `msaf/tests/test_gw_rh_extension.py`: uji wall measurement, cross-lock, spektral, dual-engine.
4. Jalankan kampanye for T = 100 (N=100 baseline, opsi N=150 resolusi 2).
5. Tulis report `reports/RH_EXTENSION_2026-10-21.md` with angka verbatim.
6. Bila `ALL PASS`: registry `A-2026-0033`, HANDOFF Â§2.0az, sertifikat sha256LF.
7. Suite penuh and `freeze.py --verify`; commit/push hanya bila diminta.

## 9. Batas eksplisit

- Hanya T = 100 (konduktor 100) for kampanye ini
- Hanya Route S ladder + karakter aritmatik tersegel (Option A/B)
- Tidak ada klaim RH terbukti/no terbukti
- Tidak ada klaim Ïƒ = 1/2, lokasi nol, faktorisasi, RSA/ECC, Anderson, fisika
- Tidak ada klaim asimtotik
- Tidak merubah/mengulang kampanye H1/Engine B/Quantum which tersegel

