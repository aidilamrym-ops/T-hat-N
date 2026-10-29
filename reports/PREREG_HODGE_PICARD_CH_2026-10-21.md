# Pra-registrasi: Hodge â€” Bound Picard & CH for a_11 â€” 2026-10-21

**Status:** scope DIKUNCI for paket Hodge Picard Bound; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket. Hash `sha256LF` file ini
dicatat in receipt and report.

**Paket:** Hodge TREK AKTIF â€” Bound Picard atas per-permukaan-per-lapangan;
CH (Couveignes-Henocq) for a_11 on permukaan K3 umum (bukan Fermat).

**Berkas target:** `msaf/hodge_picard.py` (baru), guard
`msaf/tests/test_hodge_picard.py` (baru), report
`reports/HODGE_PICARD_2026-10-21.md`, receipt
`reports/hodge_picard.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`acb`, `arb`), `msaf/hodge_ch.py`,
`msaf/hodge_counter.py`, `msaf/groebner.py`. Tidak ada `numpy`/`scipy` in jalur inti.

**Registry which direncanakan:** `A-2026-0036`, hanya bila verdict inti
`ALL PASS` and integritas PASS.

**Tidak mengubah:** V1â€“V6 (`A-2026-0015`â€“`A-2026-0021`), `A-2026-0022`â€“`A-2026-0035`,
`ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins,
seluruh report/artefak beku.

## 1. Maksud and limit

Paket ini melanjutkan program Hodge which already tersegel (`HODGE_CLOSURE.md`,
`HODGE_CH_SPEC.md`) with dua tujuan:

1. **CH for a_11 on permukaan K3 umum (non-Fermat):**
   - Ekstensi metode Couveignes-Henocq (CH) which already tersegel for quartic Fermat
   - Ke permukaan K3 umum (smooth quartic in P^3) with Picard rank rendah
   - Tujuan: dapatkan a_11 via CRT + oracle gate + leave-one-out rehearsal

2. **Bound Picard per permukaan per lapangan:**
   - Dari polinomial karakteristik lengkap (a_1..a_11 via CH), hitung bound Picard
   - Metode van Luijk / K3 rank bound dari polinomial Weil
   - Target: bound informatif (< 20) on K3 with Picard rank geometris rendah

**Paket ini BUKAN:**
- Pembuktian konjektur Hodge (hanya bound finit)
- Kembali ke keluarga Fermat (already exhaustive, bound 20/vacuous)
- Karakteristik 2 (blokir tercatat: inseparable cover)
- Klaim konjektur Hodge, RH, faktorisasi, RSA/ECC, Anderson, fisika

## 2. Latar belakang (dari artefak tersegel)

**HODGE_CLOSURE.md** (tersegel):
- CH for a_11 on smooth quartic over F_3: **EXECUTED AND VERIFIED**
  - a_11 = 354294 uniquely isolated
  - CRT combiner (M > 2B), oracle gate HOLD, leave-one-out rehearsal (10/10 PASS)
  - Circle test PASS
- Famili Fermat: **EXHAUSTED** â€” Picard rank 20 = b_2 - 2, bound â‰¤ 20 vacuous
- General quartic: "wall is arithmetic" â€” butuh a_1..a_11 (k hingga 11)
  - Counter k=9: ~12 min, k=10: ~2h, k=11: ~19h (out of reach)
  - CH dirancang for ini: counts kâ‰¤7 + Frobenius mod l + CRT

**HODGE_CH_SPEC.md** (tersegel, option 2 adopted):
- Option 2: Weil-constraint search (enumerate candidate a_11 in [-B,B], Schur-Cohn)
- CRT combiner (M > 2B), oracle gate HOLD, leave-one-out rehearsal (10/10 PASS)
- Circle test PASS
- Residue engine (option 1/3) retired for surface ini

## 3. Scope which dikunci

| Objek | Lapangan | Status | Aksi |
|-------|----------|--------|------|
| Smooth quartic (F_3) | F_3 | CH done (a_11=354294) | Picard bound dari char poly lengkap |
| Smooth quartic (F_5) | F_5 | CH pending | Ekstensi CH ke F_5 |
| Smooth quartic (F_7) | F_7 | CH pending | Ekstensi CH ke F_7 |
| K3 Picard rendah | F_p | Baru | Cari bound < 20 |

**Target permukaan:** Smooth quartic in P^3 with Groebner smoothness witness,
Picard rank geometris rendah (non-Fermat), sehingga van Luijk bound bisa < 20.

## 4. Algoritma which dikunci

### 4.1 CH Pipeline (reuse dari HODGE_CH_SPEC)
1. **Point counts k=1..7** via vectorised counter (ball-certified)
2. **Frobenius mod l** for l dalam set prima (baby-step giant-step)
3. **Residue engine** â†’ r_l = a_11 mod l
4. **CRT combiner** (M > 2B, B = 22Â·p^11) â†’ candidate a_11
5. **Oracle gate** â†’ verifikasi a_1..a_10 dari engine sama
6. **Leave-one-out rehearsal** (10/10 PASS)
7. **Circle test** â†’ verifikasi root in |z| = p^{11/2}

### 4.2 Picard Bound dari Weil Polynomial
Diberikan polinomial karakteristik lengkap Ï‡(T) = det(1 - FrobÂ·T | H^2):
1. Faktorisasi Ï‡(T) in Q_l
2. Hitung multiplicity eigenvalue 1 (geometric Picard rank â‰¥ multiplicity)
3. Van Luijk bound: Ï â‰¤ 22 - (jumlah eigenvalue â‰  1 with argumen tertentu)
3. Atau: bound via Artin-Tate conjecture (jika NS rank diketahui)

### 4.3 Target Bound Informatif
- **Threshold:** Bound Picard < 20 (non-vacuous)
- **Kriteria permukaan:** Picard rank geometris rendah (bukan Fermat)
- **Output:** Table bound per (surface, field) with status vacuous/informative

## 5. Konfigurasi which dikunci

| Parameter | Nilai |
|-----------|-------|
| Prima prima l | {2,3,5,7,11,13,17,19,23,29,31,37} (M > 2B) |
| B (Weil bound) | B = 22Â·p^11 for F_p |
| Prima target p | 3, 5, 7, 11 (awal) |
| Permukaan target | 3-5 smooth quartic non-Fermat per p |
| Timeout per surface | 4 jam (k=11 via CH) |

## 5. Pemeriksaan Integritas (C1â€“C4)

**C1: CH Pipeline Valid**
- a_11 integer with |a_11| â‰¤ B, recovered via combiner (M > 2B)
- Oracle gate HOLD on a_1..a_10 dari engine sama
- Leave-one-out rehearsal 10/10 PASS
- Circle test PASS

**C2: Picard Bound Computed**
- Bound dihitung dari Weil polynomial lengkap
- Metode terdokumentasi (van Luijk / Artin-Tate)

**C3: Bound Informatif Ditemukan**
- Minimal 1 permukaan with bound < 20
- Atau: dokumentasi mengapa no ditemukan (jika semua â‰¥ 20)

**C4: Determinisme & Receipt**
- Output deterministik, hash sha256LF terkunci
- Receipt berisi table bound per (surface, field)

## 6. Verdict

- **ALL PASS**: C1â€“C4 PASS, minimal 1 bound informatif (< 20)
- **PARTIAL**: C1 PASS tapi no ada bound informatif (semua â‰¥ 20)
- **FAILED**: C1 gagal (CH pipeline broken)
- **INCONCLUSIVE**: Tool error, timeout, hash mismatch

Registry `A-2026-0036` hanya bila verdict `ALL PASS` and integritas PASS.

## 7. Falsifier

Paket ini falsified bila:
- CH pipeline gagal (oracle gate FAIL, rehearsal < 10/10, circle test FAIL)
- CRT combiner no unique (M â‰¤ 2B)
- Semua permukaan memberikan bound â‰¥ 20 (tanpa penjelasan teoritis)
- Receipt no deterministik or hash mismatch

## 8. Artefak and urutan eksekusi

1. Tulis and hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/hodge_picard.py`: CH pipeline + Picard bound.
3. Guard `msaf/tests/test_hodge_picard.py`: uji CH pipeline + bound.
5. Jalankan kampanye for p âˆˆ {3,5,7} on 3-5 permukaan per p.
6. Tulis report `reports/HODGE_PICARD_2026-10-21.md` with table bound.
6. Bila `ALL PASS`: registry `A-2026-0036`, HANDOFF Â§2.0bc, sertifikat sha256LF.
7. Suite penuh and `freeze.py --verify`; commit/push hanya bila diminta.

## 9. Batas eksplisit

- Hanya permukaan K3 (smooth quartic in P^3), karakteristik ganjil
- Tidak ada klaim konjektur Hodge, RH, faktorisasi, RSA/ECC, Anderson, fisika
- Tidak kembali ke keluarga Fermat (exhaustive)
- Tidak karakteristik 2 (blokir tercatat)
- Hanya bound finit, bukan teorema asimtotik

