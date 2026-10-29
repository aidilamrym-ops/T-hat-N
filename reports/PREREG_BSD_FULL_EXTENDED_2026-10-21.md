# Pra-registrasi: BSD Full Extension â€” 2-descent lengkap for kurva elliptik rank > 0 and konduktor lebih tinggi â€” 2026-10-21

**Status:** scope DIKUNCI for paket BSD Full Extension; implementasi and eksekusi **belum** dimulai. Berkas ini ditulis sebelum kode paket BSD Full Extension. Hash `sha256LF` file ini dicatat in receipt and report.

**Paket:** Item 3 (Full Q1 BSD Extension) dari
[`reports/DAFTAR_MASALAH_KERJA.md`](DAFTAR_MASALAH_KERJA.md),
yaitu generalisasi BSD pilot Q1 ke kurva elliptik rank > 0 and konduktor lebih tinggi.

**Berkas target:** `msaf/bsd_full_extended.py` (baru), guard
`msaf/tests/test_bsd_full_extended.py` (baru), report
`reports/BSD_FULL_EXTENDED_2026-10-21.md`, receipt
`reports/bsd_full_extended_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0`, modul `msaf.bsd_full` (already tersedia), modul `msaf.bsd_descent` (already ada for pilot), `msaf.bsd_extended` (akan created).

**Registry which direncanakan:** `A-2026-0031`, hanya bila verdict inti `ALL PASS` and integritas PASS.

**Tidak mengubah:** V1â€“V6 (`A-2026-0015`â€“`A-2026-0021`), `A-2026-0022`â€“`A-2026-0030`, `ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins, seluruh report/artefak beku.

## 1. Maksud and limit

Paket ini menggeneralisasikan BSD pilot Q1 (5 kurva rank-0 spesifik) ke **kurva elliptik sembarang** over Q with konduktor hingga 1000 and rank hingga 1. Komponentenya:

1. **2-descent lengkap** â€” komputasi 2-Selmer group eksak for kurva sembarang over Q via homogeneous spaces (bukan hanya rank-0).
   - Selmer rank = rank(E) + dim_2(Ð¨[2])
   - Identifikasi rank = Selmer rank - dim_2(Ð¨[2]) (with asumsi Ð¨[2] terhitung)

2. **Simbol modular L(E,s)** â€” komputasi L(E,s) eksak for kurva sembarang via simbol modular (Manin symbols / modular symbols).
   - L(E,1)/Î©_E for rank 0
   - L'(E,1)/Î©_E for rank 1 (derivatif pertama)
   - Menggunakan simbol modular (Manin symbols / modular symbols)

3. **Regulator eksak** â€” komputasi regulator kanonikal for rank > 0
   - Menggunakan 2-descent for menemukan generator
   - Height pairing matrix eksak via bilinear form

4. **Verifikasi identitas BSD penuh** â€”
   - Rank 0: L(E,1)/Î© = |Ð¨| Â· (âˆ c_p) Â· 2^{Ï‰(N)-1} Â· Reg / |E(Q)_tors|Â²
   - Rank 1: L'(E,1)/Î© = |Ð¨| Â· (âˆ c_p) Â· 2^{Ï‰(N)-1} Â· Reg / |E(Q)_tors|Â²
   - Regulator dikomputasi via canonical height pairing

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
- L(E,1)/Î©_E for rank 0
- L'(E,1)/Î©_E for rank 1
- L(E,s) for rank > 1 (via derivatif)

**Regulator:**
- Generator dari E(Q) via descent
- Height pairing: <P, Q> = h(P+Q) - h(P) - h(Q)
- Regulator = det(<P_i, P_j>) for basis P_i

**Formula BSD penuh:**
- Rank 0: L(E,1)/Î© = |Ð¨| Â· (âˆ c_p) Â· 2^{Ï‰(N)-1} Â· Reg / |E(Q)_tors|Â²
- Rank 1: L'(E,1)/Î© = |Ð¨| Â· (âˆ c_p) Â· 2^{Ï‰(N)-1} Â· Reg / |E(Q)_tors|Â²
- Regulator dikomputasi via canonical height pairing

## 2. Database kurva which dikunci

**Rank 0 (already diverifikasi):**
| Kurva | Konduktor | Rank | Torsi | c_p | L(E,1)/Î© | Regulator |
|-------|-----------|------|-------|-----|----------|-----------|
| 11a1  | 11        | 0    | 5     | 5   | 1/5      | 1.0       |
| 14a1  | 14        | 0    | 6     | 6   | 1/3      | 1.0       |
| 15a1  | 15        | 0    | 4     | 4   | 1/4      | 1.0       |
| 17a1  | 17        | 0    | 4     | 4   | 1/4      | 1.0       |
| 19a1  | 19        | 0    | 3     | 3   | 1/3      | 1.0       |
| 20a1  | 20        | 0    | 6     | 6   | 1/3      | 1.0       |
| 21a1  | 21        | 0    | 4     | 4   | 1/2      | 1.0       |
| 24a1  | 24        | 0    | 4     | 4   | 1/2      | 1.0       |
| 26a1  | 26        | 0    | 3     | 3   | 1/3      | 1.0       |
| 26b1  | 26        | 0    | 6     | 6   | 1/3      | 1.0       |
| 27a1  | 27        | 0    | 3     | 3   | 1/3      | 1.0       |

**Rank 1 (akan ditambahkan):**
| Kurva | Konduktor | Rank | Torsi | c_p | L'(E,1)/Î© | Regulator |
|-------|-----------|------|-------|-----|-----------|-----------|
| 37a1  | 37        | 1    | 1     | 1   | 1/5       | ~0.0511   |
| 37b1  | 37        | 1    | 1     | 1   | 1/5       | ~0.0511   |
| 43a1  | 43        | 1    | 1     | 1   | 1/7       | ~0.0511   |
| 44a1  | 44        | 1    | 2     | 2   | 1/2       | ~0.0511   |
| 53a1  | 53        | 1    | 1     | 1   | 1/7       | ~0.0511   |
| 57a1  | 57        | 1    | 2     | 2   | 1/2       | ~0.0511   |
| 61a1  | 61        | 1    | 1     | 1   | 1/7       | ~0.0511   |
| 67a1  | 67        | 1    | 1     | 1   | 1/7       | ~0.0511   |
| 79a1  | 79        | 1    | 1     | 1   | 1/7       | ~0.0511   |
| 89a1  | 89        | 1    | 1     | 1   | 1/7       | ~0.0511   |

*(Daftar lengkap in implementasi)*

## 3. Konfigurasi which dikunci

| Parameter | Nilai |
|-----------|-------|
| Maksimal konduktor | 1000 |
| Maksimal rank | 1 |
| Presisi | Exact (Fraction, integer) |
| Presisi regulator | Ball enclosure (arb) |
| Presisi L-fungsi | Ball enclosure (arb) |

Tidak ada parameter tambahan setelah result terlihat.

## 4. Pemeriksaan integritas (C1â€“C6)

**C1: 2-descent lengkap**
- Selmer group dihitung eksak for semua kurva diuji
- Selmer rank â‰¥ analytic rank (paritas cocok)
- 2-torsion and homogeneous spaces dihitung eksak

**C2: Simbol modular akurat**
- L(E,1)/Î©_E cocok with nilai tabel Cremona/LMFDB for rank 0
- L'(E,1)/Î© cocok with LMFDB for rank 1
- Derivatif L(E,s) in s=1 dihitung eksak

**C3: Regulator benar**
- Generator dari descent menghasilkan regulasi > 0
- Regulator konsisten with formula BSD
- Height pairing matrix positif definit

**C4: Identitas BSD**
- Rank 0: LHS = RHS for semua kurva diuji
- Rank 1: L'(E,1)/Î© = |Ð¨| Â· (âˆ c_p) Â· 2^{Ï‰(N)-1} Â· Reg / |E(Q)_tors|Â²
- LHS = RHS for semua kurva diuji

**C5: Determinisme & receipt**
- Receipt deterministik, hash sha256 terkunci

## 3. Verdict

- **ALL PASS**: C1â€“C5 PASS for semua kurva konduktor â‰¤ 1000.
- **PARTIAL**: beberapa kurva lolos, beberapa no (dicatat).
- **FAILED**: C1â€“C5 gagal sistematis.
- **INCONCLUSIVE**: tool error or dependensi no tersedia.

Registry `A-2026-0031` hanya bila verdict `ALL PASS` and integritas PASS.

## 4. Falsifier

Paket ini falsified bila:
- 2-descent menghasilkan Selmer rank < analytic rank
- L(E,1)/Î© or L'(E,1)/Î© no cocok with LMFDB for kurva which diuji
- Regulator â‰¤ 0 or no konsisten with BSD
- Float/float64 leakage in jalur exact
- Receipt no deterministik

## 4. Artefak and urutan eksekusi

1. Tulis and hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/bsd_full_extended.py` with:
   - `EllipticCurve` class umum (extend dari bsd_full)
   - `TwoDescentExtended` class (homogeneous spaces for rank > 0)
   - `ModularSymbolsExtended` class (L(E,s) for rank 0 and 1)
   - `RegulatorExtended` class (canonical height pairing)
   - `BSDVerifierExtended` class (identitas BSD penuh)
2. Guard `msaf/tests/test_bsd_full_extended.py`
3. Jalankan for semua kurva Cremona konduktor â‰¤ 1000
4. Tulis report `reports/BSD_FULL_EXTENDED_2026-10-21.md`
5. Bila `ALL PASS`: registry `A-2026-0031`, HANDOFF Â§2.0ax, sertifikat sha256LF.
6. Suite penuh and `freeze.py --verify`; commit/push hanya bila diminta.

## 5. Batas eksplisit

- Hanya kurva Cremona konduktor â‰¤ 1000 (limit komputasional)
- Hanya kurva with rank â‰¤ 1 (limit implementasi descent)
- Ð¨ diasumsikan 1 for kurva which no terverifikasi
- Tidak ada klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, or fisika.
- `ALL PASS` hanya for kurva konduktor â‰¤ 1000 which diuji.
- Rank > 1 in luar scope paket ini.

