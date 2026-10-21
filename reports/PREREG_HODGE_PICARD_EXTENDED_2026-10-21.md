# Pra-registrasi: Hodge Picard Bound Ekstensi F_5, F_7 — 2026-10-21

**Status:** scope DIKUNCI untuk paket Hodge Ekstensi F_5, F_7; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket. Hash `sha256LF` berkas ini
dicatat di receipt dan laporan.

**Paket:** Hodge TREK AKTIF — Bound Picard Ekstensi ke F_5, F_7 untuk mencari bound informatif (< 20).
Melanjutkan `A-2026-0036` (Hodge Picard Bound F_3).

**Berkas target:** `msaf/hodge_picard_extended.py` (baru), guard
`msaf/tests/test_hodge_picard_extended.py` (baru), laporan
`reports/HODGE_PICARD_EXTENDED_2026-10-21.md`, receipt
`reports/hodge_picard_extended.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`acb`, `arb`), `msaf/hodge/*.py` (sealed).
Tidak ada `numpy`/`scipy` di jalur inti.

**Registry yang direncanakan:** `A-2026-0037`, hanya bila verdict inti
`ALL PASS` dan integritas PASS.

**Tidak mengubah:** V1–V6 (`A-2026-0015`–`A-2026-0021`), `A-2026-0022`–`A-2026-0036`,
`ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins,
seluruh laporan/artefak beku.

## 1. Maksud dan batas

Paket ini memperluas program Hodge Picard Bound ke lapangan **F_5 dan F_7**
untuk mencari **bound Picard informatif (< 20)** pada smooth quartic yang sama
(surface dengan koefisien tersegel dari `HODGE_CLOSURE.md`).

**Latar belakang:**
- F_3: bound = 22 (vacuous, b_2 = 22) — `A-2026-0036`
- **Tujuan:** cari bound < 20 di F_5 dan/atau F_7 pada surface yang sama
- Surface: smooth quartic over F_p (koefisien tersegel `HODGE_CLOSURE.md`)

**Paket ini BUKAN:**
- Pembuktian konjektur Hodge
- Surface baru (menggunakan surface yang sama F_3)
- Klaim RH, faktorisasi, RSA/ECC, Anderson, fisika

## 2. Data input (tersegel)

**Surface coefficients (tersegel `HODGE_CLOSURE.md`):**
```
coeffs = {
    (0, 0): 2, (0, 1): 1, (0, 2): 2, (0, 3): 1, (0, 4): 1,
    (1, 0): 1, (1, 1): 2, (1, 2): 1, (1, 3): 1,
    (2, 0): 1, (2, 1): 1, (2, 2): 2,
    (3, 0): 2, (3, 1): 1,
    (4, 0): 1
}
```
Smoothness verified over F_3, F_5, F_7 ✓

**Existing traces (tersegel):**
- F_3: 11 traces (k=1..11) → bound 22 (vacuous) — `A-2026-0036`
- F_5: 11 traces Fermat → bound 20 (informative) — referensi

## 3. Algoritma yang dikunci

### 3.1 Point Counting (Exact)
- `count_quartic_brute` untuk k=1..11 di F_5, F_7
- Validasi Weil bound: |a_k| ≤ 22·p^k
- Cross-check dengan vectorised counter (jika k ≤ 3)

### 3.2 Trace Computation
- a_k = #X(F_{p^k}) - 1 - p^{2k} untuk k=1..11
- Validasi Weil bound sebagai sanity check

### 3.3 Picard Bound (van Luijk / Moebius)
- Dari traces lengkap k=1..11 → char poly via Newton + FE
- Picard bound via van Luijk / Moebius inversion (exact GCD)
- Both FE signs tried; max taken (sound)
- **Threshold informatif:** bound < 20 (untuk K3, b_2 = 22)

## 4. Konfigurasi yang dikunci

| Parameter | Nilai |
|-----------|-------|
| Surface | Koefisien tersegel (HODGE_CLOSURE) |
| Lapangan | F_5, F_7 |
| Traces | k = 1..11 (exact) |
| Threshold informatif | bound < 20 |
| Timeout per surface | 30 menit |

## 5. Pemeriksaan integritas (C1–C4)

**C1: Point Counting Valid**
- Weil bound |a_k| ≤ 22·p^k terpenuhi semua k
- Exact count (brute force) konsisten

**C2: Picard Bound Computed**
- Char poly dari traces k=1..11 via Newton + FE
- Van Luijk bound dihitung via Moebius inversion exact

**C3: Informative Bound Found**
- Minimal 1 surface dengan bound < 20
- Atau: dokumentasi mengapa tidak ditemukan

**C4: Determinisme & Receipt**
- Output deterministik, hash sha256LF terkunci

## 6. Verdict

- **ALL PASS**: Minimal 1 bound informatif (< 20) ditemukan
- **PARTIAL**: Counting valid tapi semua bound ≥ 20 (dokumentasikan)
- **FAILED**: Counting gagal / trace incomplete
- **INCONCLUSIVE**: Tool error / timeout

Registry `A-2026-0037` hanya bila verdict `ALL PASS` dan integritas PASS.

## 7. Falsifier

Paket ini falsified bila:
- Point counting gagal / Weil bound violated
- Trace incomplete (k < 11)
- Receipt tidak deterministik / hash mismatch

## 8. Artefak dan urutan eksekusi

1. Tulis dan hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/hodge_picard_extended.py`: point counting F_5, F_7 + Picard bound.
3. Guard `msaf/tests/test_hodge_picard_extended.py`: uji counting + bound.
4. Jalankan kampanye untuk F_5, F_7 pada surface yang sama.
5. Tulis laporan `reports/HODGE_PICARD_EXTENDED_2026-10-21.md` dengan table bound.
6. Bila `ALL PASS`: registry `A-2026-0037`, HANDOFF §2.0bd, sertifikat sha256LF.
6. Suite penuh dan `freeze.py --verify`; commit/push hanya bila diminta.

## 9. Batas eksplisit

- Hanya surface yang sama (koefisien tersegel HODGE_CLOSURE)
- Hanya F_5, F_7 (bukan F_3 ulang, bukan F_11 dst)
- Hanya bound finit, bukan teorema asimtotik
- Tidak ada klaim konjektur Hodge, RH, faktorisasi, RSA/ECC, Anderson, fisika