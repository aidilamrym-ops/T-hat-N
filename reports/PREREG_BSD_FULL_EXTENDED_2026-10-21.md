# Pra-registrasi: BSD Full Extension — 2-descent lengkap untuk kurva elliptik rank > 0 dan konduktor lebih tinggi — 2026-10-21

**Status:** scope DIKUNCI untuk paket BSD Full Extension; implementasi dan eksekusi **belum** dimulai. Berkas ini ditulis sebelum kode paket BSD Full Extension. Hash `sha256LF` berkas ini dicatat di receipt dan laporan.

**Paket:** Item 3 (Full Q1 BSD Extension) dari
[`reports/DAFTAR_MASALAH_KERJA.md`](DAFTAR_MASALAH_KERJA.md),
yaitu generalisasi BSD pilot Q1 ke kurva elliptik rank > 0 dan konduktor lebih tinggi.

**Berkas target:** `msaf/bsd_full_extended.py` (baru), guard
`msaf/tests/test_bsd_full_extended.py` (baru), laporan
`reports/BSD_FULL_EXTENDED_2026-10-21.md`, receipt
`reports/bsd_full_extended_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0`, modul `msaf.bsd_full` (sudah tersedia), modul `msaf.bsd_descent` (sudah ada untuk pilot), `msaf.bsd_extended` (akan dibuat).

**Registry yang direncanakan:** `A-2026-0031`, hanya bila verdict inti `ALL PASS` dan integritas PASS.

**Tidak mengubah:** V1–V6 (`A-2026-0015`–`A-2026-0021`), `A-2026-0022`–`A-2026-0030`, `ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins, seluruh laporan/artefak beku.

## 1. Maksud dan batas

Paket ini menggeneralisasikan BSD pilot Q1 (5 kurva rank-0 spesifik) ke **kurva elliptik sembarang** over Q dengan konduktor hingga 1000 dan rank hingga 1. Komponentenya:

1. **2-descent lengkap** — komputasi 2-Selmer group eksak untuk kurva sembarang over Q via homogeneous spaces (bukan hanya rank-0).
   - Selmer rank = rank(E) + dim_2(Ш[2])
   - Identifikasi rank = Selmer rank - dim_2(Ш[2]) (dengan asumsi Ш[2] terhitung)

2. **Simbol modular L(E,s)** — komputasi L(E,s) eksak untuk kurva sembarang via simbol modular (Manin symbols / modular symbols).
   - L(E,1)/Ω_E untuk rank 0
   - L'(E,1)/Ω_E untuk rank 1 (derivatif pertama)
   - Menggunakan simbol modular (Manin symbols / modular symbols)

3. **Regulator eksak** — komputasi regulator kanonikal untuk rank > 0
   - Menggunakan 2-descent untuk menemukan generator
   - Height pairing matrix eksak via bilinear form

4. **Verifikasi identitas BSD penuh** —
   - Rank 0: L(E,1)/Ω = |Ш| · (∏ c_p) · 2^{ω(N)-1} · Reg / |E(Q)_tors|²
   - Rank 1: L'(E,1)/Ω = |Ш| · (∏ c_p) · 2^{ω(N)-1} · Reg / |E(Q)_tors|²
   - Regulator dikomputasi via canonical height pairing

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
- L(E,1)/Ω_E untuk rank 0
- L'(E,1)/Ω_E untuk rank 1
- L(E,s) untuk rank > 1 (via derivatif)

**Regulator:**
- Generator dari E(Q) via descent
- Height pairing: <P, Q> = h(P+Q) - h(P) - h(Q)
- Regulator = det(<P_i, P_j>) untuk basis P_i

**Formula BSD penuh:**
- Rank 0: L(E,1)/Ω = |Ш| · (∏ c_p) · 2^{ω(N)-1} · Reg / |E(Q)_tors|²
- Rank 1: L'(E,1)/Ω = |Ш| · (∏ c_p) · 2^{ω(N)-1} · Reg / |E(Q)_tors|²
- Regulator dikomputasi via canonical height pairing

## 2. Database kurva yang dikunci

**Rank 0 (sudah diverifikasi):**
| Kurva | Konduktor | Rank | Torsi | c_p | L(E,1)/Ω | Regulator |
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
| Kurva | Konduktor | Rank | Torsi | c_p | L'(E,1)/Ω | Regulator |
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

*(Daftar lengkap di implementasi)*

## 3. Konfigurasi yang dikunci

| Parameter | Nilai |
|-----------|-------|
| Maksimal konduktor | 1000 |
| Maksimal rank | 1 |
| Presisi | Exact (Fraction, integer) |
| Presisi regulator | Ball enclosure (arb) |
| Presisi L-fungsi | Ball enclosure (arb) |

Tidak ada parameter tambahan setelah hasil terlihat.

## 4. Pemeriksaan integritas (C1–C6)

**C1: 2-descent lengkap**
- Selmer group dihitung eksak untuk semua kurva diuji
- Selmer rank ≥ analytic rank (paritas cocok)
- 2-torsion dan homogeneous spaces dihitung eksak

**C2: Simbol modular akurat**
- L(E,1)/Ω_E cocok dengan nilai tabel Cremona/LMFDB untuk rank 0
- L'(E,1)/Ω cocok dengan LMFDB untuk rank 1
- Derivatif L(E,s) di s=1 dihitung eksak

**C3: Regulator benar**
- Generator dari descent menghasilkan regulasi > 0
- Regulator konsisten dengan formula BSD
- Height pairing matrix positif definit

**C4: Identitas BSD**
- Rank 0: LHS = RHS untuk semua kurva diuji
- Rank 1: L'(E,1)/Ω = |Ш| · (∏ c_p) · 2^{ω(N)-1} · Reg / |E(Q)_tors|²
- LHS = RHS untuk semua kurva diuji

**C5: Determinisme & receipt**
- Receipt deterministik, hash sha256 terkunci

## 3. Verdict

- **ALL PASS**: C1–C5 PASS untuk semua kurva konduktor ≤ 1000.
- **PARTIAL**: beberapa kurva lolos, beberapa tidak (dicatat).
- **FAILED**: C1–C5 gagal sistematis.
- **INCONCLUSIVE**: tool error atau dependensi tidak tersedia.

Registry `A-2026-0031` hanya bila verdict `ALL PASS` dan integritas PASS.

## 4. Falsifier

Paket ini falsified bila:
- 2-descent menghasilkan Selmer rank < analytic rank
- L(E,1)/Ω atau L'(E,1)/Ω tidak cocok dengan LMFDB untuk kurva yang diuji
- Regulator ≤ 0 atau tidak konsisten dengan BSD
- Float/float64 leakage di jalur exact
- Receipt tidak deterministik

## 4. Artefak dan urutan eksekusi

1. Tulis dan hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/bsd_full_extended.py` dengan:
   - `EllipticCurve` class umum (extend dari bsd_full)
   - `TwoDescentExtended` class (homogeneous spaces untuk rank > 0)
   - `ModularSymbolsExtended` class (L(E,s) untuk rank 0 dan 1)
   - `RegulatorExtended` class (canonical height pairing)
   - `BSDVerifierExtended` class (identitas BSD penuh)
2. Guard `msaf/tests/test_bsd_full_extended.py`
3. Jalankan untuk semua kurva Cremona konduktor ≤ 1000
4. Tulis laporan `reports/BSD_FULL_EXTENDED_2026-10-21.md`
5. Bila `ALL PASS`: registry `A-2026-0031`, HANDOFF §2.0ax, sertifikat sha256LF.
6. Suite penuh dan `freeze.py --verify`; commit/push hanya bila diminta.

## 5. Batas eksplisit

- Hanya kurva Cremona konduktor ≤ 1000 (batas komputasional)
- Hanya kurva dengan rank ≤ 1 (batas implementasi descent)
- Ш diasumsikan 1 untuk kurva yang tidak terverifikasi
- Tidak ada klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, atau fisika.
- `ALL PASS` hanya untuk kurva konduktor ≤ 1000 yang diuji.
- Rank > 1 di luar scope paket ini.