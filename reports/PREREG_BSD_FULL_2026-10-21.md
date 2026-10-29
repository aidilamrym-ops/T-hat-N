# Pra-registrasi: BSD Full â€” 2-descent lengkap for kurva elliptik sembarang â€” 2026-10-21

**Status:** scope DIKUNCI for paket Full Q1 BSD; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket Full Q1 BSD. Hash `sha256LF` file ini
dicatat in receipt and report.

**Paket:** Item 3 (Full Q1 BSD) dari
[`reports/DAFTAR_MASALAH_KERJA.md`](DAFTAR_MASALAH_KERJA.md),
yaitu verifikasi BSD lengkap for kurva elliptik sembarang melalui
2-descent lengkap + simbol modular + regulator.

**Berkas target:** `msaf/bsd_full.py` (baru), guard
`msaf/tests/test_bsd_full.py` (baru), report
`reports/BSD_FULL_2026-10-21.md`, receipt
`reports/bsd_full_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0`, modul `msaf.bsd_descent` (already ada for pilot),
modul `msaf.ec` (baru, for aritmetika kurva elliptik umum).

**Registry which direncanakan:** `A-2026-0030`, hanya bila verdict inti
`ALL PASS` and integritas PASS.

**Tidak mengubah:** V1â€“V6, `A-2026-0022`â€“`A-2026-0029`, `ci.yml`,
workflow spec, `lean/lakefile.toml`, freeze pins, artefak beku.

## 1. Maksud and limit

Paket ini menggeneralisasikan pilot Q1 BSD (5 kurva rank-0 spesifik) ke
**kurva elliptik sembarang** over Q with konduktor hingga limit tertentu.
Komponen utamanya:

1. **2-descent lengkap** â€” komputasi 2-Selmer group eksak for kurva
   sembarang over Q via homogeneous spaces (bukan hanya rank-0).
   - Selmer rank = rank(E) + dim_2(Ð¨[2])
   - Identifikasi rank = Selmer rank - dim_2(Ð¨[2]) (with asumsi Ð¨[2] terhitung)

2. **Simbol modular L(E,1)** â€” komputasi L(E,1)/Î©_E eksak for kurva
   sembarang via simbol modular (Manin symbols / modular symbols).
   - L(E,1)/Î©_E sebagai Fraction eksak
   - Berfungsi for rank 0 and rank > 0 (menggunakan derivatif for rank > 0)

3. **Regulator eksak** â€” komputasi regulator kanonikal for rank > 0
   - Menggunakan 2-descent for menemukan generator
   - Height pairing matrix eksak via bilinear form

4. **Verifikasi identitas BSD penuh** â€”
   L(E,1)/Î© = |Ð¨| Â· (âˆ c_p) Â· 2^{Ï‰(N)-1} Â· Reg / |E(Q)_tors|Â² (rank 0)
   L(E,1)/Î© = ... (rank > 0 with regulator)

Paket ini **bukan**:
- pembuktian BSD for semua kurva (hanya verifikasi hingga limit konduktor).
- klaim Ð¨ fini for semua kurva (hanya verifikasi for kurva which diuji).
- klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, or fisika.

## 2. Definisi which dikunci

**2-descent lengkap:**
- Homogeneous spaces: w^2 = f(x) for f degree 4
- Local solubility in semua tempat (archimedean + p-adic)
- Selmer group sebagai subset H^1(G_Q, E[2]) which locally soluble
- Rank = Selmer rank - dim_2(Ð¨[2])

**Simbol modular:**
- Manin symbols for Î“_0(N)
- L(E,1) via integral modular symbol
- L(E,1)/Î©_E sebagai Fraction eksak

**Regulator:**
- Generator dari E(Q) via descent
- Height pairing: <P, Q> = h(P+Q) - h(P) - h(Q)
- Regulator = det(<P_i, P_j>) for basis P_i

**Formula BSD penuh:**
```
L(E,1)/Î© = |Ð¨| Â· (âˆ c_p) Â· 2^{Ï‰(N)-1} Â· Reg / |E(Q)_tors|Â²   (rank 0)
L(E,1)/Î© = |Ð¨| Â· (âˆ c_p) Â· 2^{Ï‰(N)-1} Â· Reg / |E(Q)_tors|Â² Â· L^{(r)}(E,1)/r!  (rank r)
```

## 3. Konfigurasi which dikunci

| Parameter | Nilai |
|-----------|-------|
| Maksimal konduktor | 1000 (for kampanye ini) |
| Kurva diuji | Semua kurva Cremona konduktor â‰¤ 1000 |
| Presisi | Exact (Fraction, integer) |
| Presisi regulator | Ball enclosure (arb) |

Tidak ada parameter tambahan setelah result terlihat.

## 4. Pemeriksaan integritas (C1â€“C5)

**C1: 2-descent benar**
- Selmer group dihitung eksak for semua kurva diuji
- Selmer rank â‰¥ analytic rank (paritas cocok)

**C2: Simbol modular akurat**
- L(E,1)/Î©_E cocok with nilai LMFDB/Cremona for kurva which diuji
- Derivatif L(E,1) for rank > 0 konsisten

**C3: Regulator benar**
- Generator dari descent menghasilkan regulasi > 0
- Regulator konsisten with formula BSD

**C4: Identitas BSD**
- LHS = RHS for semua kurva diuji (with asumsi Ð¨ = 1 or terhitung)

**C5: Determinisme & receipt**
- Receipt deterministik, hash sha256 terkunci

## 5. Verdict

- **ALL PASS**: C1â€“C5 PASS for semua kurva konduktor â‰¤ 1000.
- **PARTIAL**: beberapa kurva lolos, beberapa no (dicatat).
- **FAILED**: C1â€“C5 gagal sistematis.
- **INCONCLUSIVE**: tool error or dependensi no tersedia.

Registry `A-2026-0030` hanya bila verdict `ALL PASS` and integritas PASS.

## 6. Falsifier

Paket ini falsified bila:
- 2-descent menghasilkan Selmer rank < analytic rank
- L(E,1)/Î© no cocok with LMFDB for kurva which diuji
- Regulator â‰¤ 0 or no konsisten with BSD
- Float/float64 leakage in jalur exact
- Receipt no deterministik

## 7. Artefak and urutan eksekusi

1. Tulis and hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/bsd_full.py` with:
   - `EllipticCurve` class umum
   - `TwoDescent` class (homogeneous spaces)
   - `ModularSymbols` class (Manin symbols)
   - `Regulator` class (height pairing)
   - `BSDVerifier` class (identitas penuh)
2. Guard `msaf/tests/test_bsd_full.py`
3. Jalankan for semua kurva Cremona konduktor â‰¤ 1000
4. Tulis report `reports/BSD_FULL_2026-10-21.md`
5. Bila `ALL PASS`: registry `A-2026-0030`, HANDOFF Â§2.0aw
6. Suite penuh and `freeze.py --verify`; commit/push hanya bila diminta.

## 8. Batas eksplisit

- Hanya kurva Cremona konduktor â‰¤ 1000 (limit komputasional)
- Hanya kurva with rank â‰¤ 2 (limit implementasi descent)
- Ð¨ diasumsikan 1 for kurva which no terverifikasi
- Tidak ada klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, or fisika.
- `ALL PASS` hanya for kurva konduktor â‰¤ 1000 which diuji.

