# Pra-registrasi: BSD Full — 2-descent lengkap untuk kurva elliptik sembarang — 2026-10-21

**Status:** scope DIKUNCI untuk paket Full Q1 BSD; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket Full Q1 BSD. Hash `sha256LF` berkas ini
dicatat di receipt dan laporan.

**Paket:** Item 3 (Full Q1 BSD) dari
[`reports/DAFTAR_MASALAH_KERJA.md`](DAFTAR_MASALAH_KERJA.md),
yaitu verifikasi BSD lengkap untuk kurva elliptik sembarang melalui
2-descent lengkap + simbol modular + regulator.

**Berkas target:** `msaf/bsd_full.py` (baru), guard
`msaf/tests/test_bsd_full.py` (baru), laporan
`reports/BSD_FULL_2026-10-21.md`, receipt
`reports/bsd_full_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0`, modul `msaf.bsd_descent` (sudah ada untuk pilot),
modul `msaf.ec` (baru, untuk aritmetika kurva elliptik umum).

**Registry yang direncanakan:** `A-2026-0030`, hanya bila verdict inti
`ALL PASS` dan integritas PASS.

**Tidak mengubah:** V1–V6, `A-2026-0022`–`A-2026-0029`, `ci.yml`,
workflow spec, `lean/lakefile.toml`, freeze pins, artefak beku.

## 1. Maksud dan batas

Paket ini menggeneralisasikan pilot Q1 BSD (5 kurva rank-0 spesifik) ke
**kurva elliptik sembarang** over Q dengan konduktor hingga batas tertentu.
Komponen utamanya:

1. **2-descent lengkap** — komputasi 2-Selmer group eksak untuk kurva
   sembarang over Q via homogeneous spaces (bukan hanya rank-0).
   - Selmer rank = rank(E) + dim_2(Ш[2])
   - Identifikasi rank = Selmer rank - dim_2(Ш[2]) (dengan asumsi Ш[2] terhitung)

2. **Simbol modular L(E,1)** — komputasi L(E,1)/Ω_E eksak untuk kurva
   sembarang via simbol modular (Manin symbols / modular symbols).
   - L(E,1)/Ω_E sebagai Fraction eksak
   - Berfungsi untuk rank 0 dan rank > 0 (menggunakan derivatif untuk rank > 0)

3. **Regulator eksak** — komputasi regulator kanonikal untuk rank > 0
   - Menggunakan 2-descent untuk menemukan generator
   - Height pairing matrix eksak via bilinear form

4. **Verifikasi identitas BSD penuh** —
   L(E,1)/Ω = |Ш| · (∏ c_p) · 2^{ω(N)-1} · Reg / |E(Q)_tors|² (rank 0)
   L(E,1)/Ω = ... (rank > 0 dengan regulator)

Paket ini **bukan**:
- pembuktian BSD untuk semua kurva (hanya verifikasi hingga batas konduktor).
- klaim Ш fini untuk semua kurva (hanya verifikasi untuk kurva yang diuji).
- klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, atau fisika.

## 2. Definisi yang dikunci

**2-descent lengkap:**
- Homogeneous spaces: w^2 = f(x) untuk f degree 4
- Local solubility di semua tempat (archimedean + p-adic)
- Selmer group sebagai subset H^1(G_Q, E[2]) yang locally soluble
- Rank = Selmer rank - dim_2(Ш[2])

**Simbol modular:**
- Manin symbols untuk Γ_0(N)
- L(E,1) via integral modular symbol
- L(E,1)/Ω_E sebagai Fraction eksak

**Regulator:**
- Generator dari E(Q) via descent
- Height pairing: <P, Q> = h(P+Q) - h(P) - h(Q)
- Regulator = det(<P_i, P_j>) untuk basis P_i

**Formula BSD penuh:**
```
L(E,1)/Ω = |Ш| · (∏ c_p) · 2^{ω(N)-1} · Reg / |E(Q)_tors|²   (rank 0)
L(E,1)/Ω = |Ш| · (∏ c_p) · 2^{ω(N)-1} · Reg / |E(Q)_tors|² · L^{(r)}(E,1)/r!  (rank r)
```

## 3. Konfigurasi yang dikunci

| Parameter | Nilai |
|-----------|-------|
| Maksimal konduktor | 1000 (untuk kampanye ini) |
| Kurva diuji | Semua kurva Cremona konduktor ≤ 1000 |
| Presisi | Exact (Fraction, integer) |
| Presisi regulator | Ball enclosure (arb) |

Tidak ada parameter tambahan setelah hasil terlihat.

## 4. Pemeriksaan integritas (C1–C5)

**C1: 2-descent benar**
- Selmer group dihitung eksak untuk semua kurva diuji
- Selmer rank ≥ analytic rank (paritas cocok)

**C2: Simbol modular akurat**
- L(E,1)/Ω_E cocok dengan nilai LMFDB/Cremona untuk kurva yang diuji
- Derivatif L(E,1) untuk rank > 0 konsisten

**C3: Regulator benar**
- Generator dari descent menghasilkan regulasi > 0
- Regulator konsisten dengan formula BSD

**C4: Identitas BSD**
- LHS = RHS untuk semua kurva diuji (dengan asumsi Ш = 1 atau terhitung)

**C5: Determinisme & receipt**
- Receipt deterministik, hash sha256 terkunci

## 5. Verdict

- **ALL PASS**: C1–C5 PASS untuk semua kurva konduktor ≤ 1000.
- **PARTIAL**: beberapa kurva lolos, beberapa tidak (dicatat).
- **FAILED**: C1–C5 gagal sistematis.
- **INCONCLUSIVE**: tool error atau dependensi tidak tersedia.

Registry `A-2026-0030` hanya bila verdict `ALL PASS` dan integritas PASS.

## 6. Falsifier

Paket ini falsified bila:
- 2-descent menghasilkan Selmer rank < analytic rank
- L(E,1)/Ω tidak cocok dengan LMFDB untuk kurva yang diuji
- Regulator ≤ 0 atau tidak konsisten dengan BSD
- Float/float64 leakage di jalur exact
- Receipt tidak deterministik

## 7. Artefak dan urutan eksekusi

1. Tulis dan hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/bsd_full.py` dengan:
   - `EllipticCurve` class umum
   - `TwoDescent` class (homogeneous spaces)
   - `ModularSymbols` class (Manin symbols)
   - `Regulator` class (height pairing)
   - `BSDVerifier` class (identitas penuh)
2. Guard `msaf/tests/test_bsd_full.py`
3. Jalankan untuk semua kurva Cremona konduktor ≤ 1000
4. Tulis laporan `reports/BSD_FULL_2026-10-21.md`
5. Bila `ALL PASS`: registry `A-2026-0030`, HANDOFF §2.0aw
6. Suite penuh dan `freeze.py --verify`; commit/push hanya bila diminta.

## 8. Batas eksplisit

- Hanya kurva Cremona konduktor ≤ 1000 (batas komputasional)
- Hanya kurva dengan rank ≤ 2 (batas implementasi descent)
- Ш diasumsikan 1 untuk kurva yang tidak terverifikasi
- Tidak ada klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, atau fisika.
- `ALL PASS` hanya untuk kurva konduktor ≤ 1000 yang diuji.