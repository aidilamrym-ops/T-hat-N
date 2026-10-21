# Pra-registrasi: Hodge — Bound Picard & CH untuk a_11 — 2026-10-21

**Status:** scope DIKUNCI untuk paket Hodge Picard Bound; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket. Hash `sha256LF` berkas ini
dicatat di receipt dan laporan.

**Paket:** Hodge TREK AKTIF — Bound Picard atas per-permukaan-per-lapangan;
CH (Couveignes-Henocq) untuk a_11 pada permukaan K3 umum (bukan Fermat).

**Berkas target:** `msaf/hodge_picard.py` (baru), guard
`msaf/tests/test_hodge_picard.py` (baru), laporan
`reports/HODGE_PICARD_2026-10-21.md`, receipt
`reports/hodge_picard.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`acb`, `arb`), `msaf/hodge_ch.py`,
`msaf/hodge_counter.py`, `msaf/groebner.py`. Tidak ada `numpy`/`scipy` di jalur inti.

**Registry yang direncanakan:** `A-2026-0036`, hanya bila verdict inti
`ALL PASS` dan integritas PASS.

**Tidak mengubah:** V1–V6 (`A-2026-0015`–`A-2026-0021`), `A-2026-0022`–`A-2026-0035`,
`ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins,
seluruh laporan/artefak beku.

## 1. Maksud dan batas

Paket ini melanjutkan program Hodge yang sudah tersegel (`HODGE_CLOSURE.md`,
`HODGE_CH_SPEC.md`) dengan dua tujuan:

1. **CH untuk a_11 pada permukaan K3 umum (non-Fermat):**
   - Ekstensi metode Couveignes-Henocq (CH) yang sudah tersegel untuk quartic Fermat
   - Ke permukaan K3 umum (smooth quartic di P^3) dengan Picard rank rendah
   - Tujuan: dapatkan a_11 via CRT + oracle gate + leave-one-out rehearsal

2. **Bound Picard per permukaan per lapangan:**
   - Dari polinomial karakteristik lengkap (a_1..a_11 via CH), hitung bound Picard
   - Metode van Luijk / K3 rank bound dari polinomial Weil
   - Target: bound informatif (< 20) pada K3 dengan Picard rank geometris rendah

**Paket ini BUKAN:**
- Pembuktian konjektur Hodge (hanya bound finit)
- Kembali ke keluarga Fermat (sudah exhaustive, bound 20/vacuous)
- Karakteristik 2 (blokir tercatat: inseparable cover)
- Klaim konjektur Hodge, RH, faktorisasi, RSA/ECC, Anderson, fisika

## 2. Latar belakang (dari artefak tersegel)

**HODGE_CLOSURE.md** (tersegel):
- CH untuk a_11 pada smooth quartic over F_3: **EXECUTED AND VERIFIED**
  - a_11 = 354294 uniquely isolated
  - CRT combiner (M > 2B), oracle gate HOLD, leave-one-out rehearsal (10/10 PASS)
  - Circle test PASS
- Famili Fermat: **EXHAUSTED** — Picard rank 20 = b_2 - 2, bound ≤ 20 vacuous
- General quartic: "wall is arithmetic" — butuh a_1..a_11 (k hingga 11)
  - Counter k=9: ~12 min, k=10: ~2h, k=11: ~19h (out of reach)
  - CH dirancang untuk ini: counts k≤7 + Frobenius mod l + CRT

**HODGE_CH_SPEC.md** (tersegel, option 2 adopted):
- Option 2: Weil-constraint search (enumerate candidate a_11 in [-B,B], Schur-Cohn)
- CRT combiner (M > 2B), oracle gate HOLD, leave-one-out rehearsal (10/10 PASS)
- Circle test PASS
- Residue engine (option 1/3) retired untuk surface ini

## 3. Scope yang dikunci

| Objek | Lapangan | Status | Aksi |
|-------|----------|--------|------|
| Smooth quartic (F_3) | F_3 | CH done (a_11=354294) | Picard bound dari char poly lengkap |
| Smooth quartic (F_5) | F_5 | CH pending | Ekstensi CH ke F_5 |
| Smooth quartic (F_7) | F_7 | CH pending | Ekstensi CH ke F_7 |
| K3 Picard rendah | F_p | Baru | Cari bound < 20 |

**Target permukaan:** Smooth quartic di P^3 dengan Groebner smoothness witness,
Picard rank geometris rendah (non-Fermat), sehingga van Luijk bound bisa < 20.

## 4. Algoritma yang dikunci

### 4.1 CH Pipeline (reuse dari HODGE_CH_SPEC)
1. **Point counts k=1..7** via vectorised counter (ball-certified)
2. **Frobenius mod l** untuk l dalam set prima (baby-step giant-step)
3. **Residue engine** → r_l = a_11 mod l
4. **CRT combiner** (M > 2B, B = 22·p^11) → candidate a_11
5. **Oracle gate** → verifikasi a_1..a_10 dari engine sama
6. **Leave-one-out rehearsal** (10/10 PASS)
7. **Circle test** → verifikasi root di |z| = p^{11/2}

### 4.2 Picard Bound dari Weil Polynomial
Diberikan polinomial karakteristik lengkap χ(T) = det(1 - Frob·T | H^2):
1. Faktorisasi χ(T) di Q_l
2. Hitung multiplicity eigenvalue 1 (geometric Picard rank ≥ multiplicity)
3. Van Luijk bound: ρ ≤ 22 - (jumlah eigenvalue ≠ 1 dengan argumen tertentu)
3. Atau: bound via Artin-Tate conjecture (jika NS rank diketahui)

### 4.3 Target Bound Informatif
- **Threshold:** Bound Picard < 20 (non-vacuous)
- **Kriteria permukaan:** Picard rank geometris rendah (bukan Fermat)
- **Output:** Table bound per (surface, field) dengan status vacuous/informative

## 5. Konfigurasi yang dikunci

| Parameter | Nilai |
|-----------|-------|
| Prima prima l | {2,3,5,7,11,13,17,19,23,29,31,37} (M > 2B) |
| B (Weil bound) | B = 22·p^11 untuk F_p |
| Prima target p | 3, 5, 7, 11 (awal) |
| Permukaan target | 3-5 smooth quartic non-Fermat per p |
| Timeout per surface | 4 jam (k=11 via CH) |

## 5. Pemeriksaan Integritas (C1–C4)

**C1: CH Pipeline Valid**
- a_11 integer dengan |a_11| ≤ B, recovered via combiner (M > 2B)
- Oracle gate HOLD pada a_1..a_10 dari engine sama
- Leave-one-out rehearsal 10/10 PASS
- Circle test PASS

**C2: Picard Bound Computed**
- Bound dihitung dari Weil polynomial lengkap
- Metode terdokumentasi (van Luijk / Artin-Tate)

**C3: Bound Informatif Ditemukan**
- Minimal 1 permukaan dengan bound < 20
- Atau: dokumentasi mengapa tidak ditemukan (jika semua ≥ 20)

**C4: Determinisme & Receipt**
- Output deterministik, hash sha256LF terkunci
- Receipt berisi table bound per (surface, field)

## 6. Verdict

- **ALL PASS**: C1–C4 PASS, minimal 1 bound informatif (< 20)
- **PARTIAL**: C1 PASS tapi tidak ada bound informatif (semua ≥ 20)
- **FAILED**: C1 gagal (CH pipeline broken)
- **INCONCLUSIVE**: Tool error, timeout, hash mismatch

Registry `A-2026-0036` hanya bila verdict `ALL PASS` dan integritas PASS.

## 7. Falsifier

Paket ini falsified bila:
- CH pipeline gagal (oracle gate FAIL, rehearsal < 10/10, circle test FAIL)
- CRT combiner tidak unique (M ≤ 2B)
- Semua permukaan memberikan bound ≥ 20 (tanpa penjelasan teoritis)
- Receipt tidak deterministik atau hash mismatch

## 8. Artefak dan urutan eksekusi

1. Tulis dan hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/hodge_picard.py`: CH pipeline + Picard bound.
3. Guard `msaf/tests/test_hodge_picard.py`: uji CH pipeline + bound.
5. Jalankan kampanye untuk p ∈ {3,5,7} pada 3-5 permukaan per p.
6. Tulis laporan `reports/HODGE_PICARD_2026-10-21.md` dengan table bound.
6. Bila `ALL PASS`: registry `A-2026-0036`, HANDOFF §2.0bc, sertifikat sha256LF.
7. Suite penuh dan `freeze.py --verify`; commit/push hanya bila diminta.

## 9. Batas eksplisit

- Hanya permukaan K3 (smooth quartic di P^3), karakteristik ganjil
- Tidak ada klaim konjektur Hodge, RH, faktorisasi, RSA/ECC, Anderson, fisika
- Tidak kembali ke keluarga Fermat (exhaustive)
- Tidak karakteristik 2 (blokir tercatat)
- Hanya bound finit, bukan teorema asimtotik