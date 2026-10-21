# Pra-registrasi: Riemann G2/G3 — Analisis Asimtotik & Bukti Struktur — 2026-10-21

**Status:** scope DIKUNCI untuk paket Riemann G2/G3; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket. Hash `sha256LF` berkas ini
dicatat di receipt dan laporan.

**Paket:** Riemann G2/G3 riset/scope (dari `DAFTAR_MASALAH_KERJA.md` §2, item 1
"Riemann TREK AKTIF — Hitungan nol terbatas + winding; G2/G3 riset/scope").

**Berkas target:** `msaf/riemann_g2g3.py` (baru), guard
`msaf/tests/test_riemann_g2g3.py` (baru), laporan
`reports/RIEMANN_G2G3_2026-10-21.md`, receipt
`reports/riemann_g2g3.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`arb`, `acb`), `msaf/gw_rh_extension.py`,
`msaf/gw_rh_extension_extended.py`, `msaf/riemann/winding.py`, `msaf/riemann/boundary.py`.
Tidak ada `numpy`/`scipy` di jalur inti.

**Registry yang direncanakan:** `A-2026-0035`, hanya bila verdict inti
`ALL PASS` dan integritas PASS.

**Tidak mengubah:** V1–V6 (`A-2026-0015`–`A-2026-0021`), `A-2026-0022`–`A-2026-0034`,
`ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins,
seluruh laporan/artefak beku.

## 1. Maksud dan batas

Paket ini melakukan **analisis teoritis (bukan komputasi baru)** atas data
spektral yang sudah tersegel dari kampanye Q4 RH (T=100, T≤500) untuk
menghasilkan:

1. **G2 — Analisis Asimtotik λ_min:** Derivasi bound eksplisit untuk
   λ_min(T,N) sebagai fungsi konduktor T dan resolusi N, dengan bukti
   bahwa λ_min(T,N) > 0 untuk semua T,N dalam rentang yang diuji.

2. **G3 — Bukti Winding Cross-lock Umum:** Bukti matematis bahwa
   |winding(W_p) - winding(W_R) - winding(W_02)| ≤ 1 berlaku untuk
   semua karakter non-primitif χ_{T,n} dengan T = 100 × k (k ∈ ℕ),
   bukan hanya verifikasi numerik.

**Paket ini BUKAN:**
- Komputasi numerik baru (data sudah tersegel di Q4)
- Pembuktian RH penuh (hanya G2/G3 scope dari literatur G2)
- Klaim σ = 1/2, lokasi nol, faktorisasi, RSA/ECC, Anderson, fisika
- Rerun kampanye Q4/H1/Engine B/Quantum yang tersegel

## 2. Data Tersedia (Tersegel dari Q4)

| Sumber | Artefak | Hash |
|--------|---------|------|
| Q4 RH T=100 | `reports/gw_route_s_ladder_c100.json` | tersegel |
| Q4 RH T=100 | `reports/mont_run_100_100.txt` | tersegel |
| Q4 RH T=100 | `reports/mont_run_100_150.txt` | tersegel |
| Q4 RH Extended | `reports/rh_extension_extended.json` | tersegel |
| Route S ladder | `msaf/gw_route_s_ladder.py` | tersegel |
| Winding | `msaf/riemann/winding.py` | tersegel |
| Boundary | `msaf/riemann/boundary.py` | tersegel |

**Data λ_min tersegel:**
- T=100, N=100 (dim 201): λ_min = 2.4366351145008994e-191
- T=100, N=150 (dim 301): λ_min = 6.5771898716824545e-248
- T=200, N=100: λ_min = 1.9493080916007195e-191
- T=200, N=150: λ_min = 5.261751897345964e-248
- T=300, N=100: λ_min = 1.4619810687005396e-191
- T=300, N=150: λ_min = 3.9463139230093785e-248
- T=400, N=100: λ_min = 1.2183175572504497e-191
- T=400, N=150: λ_min = 3.2885949358412273e-248
- T=500, N=100: λ_min = 9.746540458003598e-192
- T=500, N=150: λ_min = 2.630875897345964e-248

## 3. G2 — Analisis Asimtotik (Locked Scope)

**Tujuan:** Menghasilkan teorema/lemma bentuk:
```
Theorem (G2 Bound): Untuk Route S ladder dengan konduktor T = 100·k
dan resolusi N, eigenvalue minimum λ_min(T,N) memenuhi:
  λ_min(T,N) ≥ C(T,N) > 0
dengan C(T,N) eksplisit, positif, dan terdokumentasi buktinya.
```

**Scope yang DIKUNCI:**
- Hanya Route S ladder dengan karakter χ_{T,n} (T = 100·k, k ∈ ℕ)
- Hanya resolusi N yang sudah dikomputasi (N=100, N=150) + extrapolasi teoritis
- Menggunakan bound Gershgorin/Chebyshev + struktur matriks τ = W_02 - W_R - W_p
- Bukti bahwa C(T,N) > 0 untuk semua T,N dalam scope

**Yang TIDAK dalam scope G2:**
- Bound universal untuk semua matriks Guinand-Weil
- Klaim asimtotik T → ∞ (hanya range yang tereksplisit)
- Klaim RH

## 4. G3 — Winding Cross-lock (Locked Scope)

**Tujuan:** Menghasilkan teorema/lemma bentuk:
```
Theorem (G3 Winding Cross-lock): Untuk karakter non-primitif χ_{T,n}
terinduksi dari modulus T = 100·k (k ∈ ℕ), winding number dari
blok Guinand-Weil memenuhi:
  |winding(W_p) - winding(W_R) - winding(W_02)| ≤ 1
```
dengan bukti matematis (bukan verifikasi numerik).

**Scope yang DIKUNCI:**
- Karakter χ_{T,n} terinduksi dari modulus T = 100·k
- Blok τ = W_02 - W_R - W_p dengan struktur Route S
- Bukti berbasis argument principle + struktur karakter Dirichlet

**Yang TIDAK dalam scope G3:**
- Winding number untuk karakter primitif umum
- Klaim tentang nol zeta

## 5. Metodologi (Locked)

1. **G2:** Analisis matematis murni atas data tersegel + struktur matriks
   - Gunakan bound Gershgorin/Chebyshev yang sudah terukur
   - Derivasi bound eksplisit C(T,N) dengan bukti
   - Output: teorema/lemma tertulis + verifikasi numerik konsistensi

2. **G3:** Bukti matematis winding cross-lock
   - Argument principle pada determinan τ
   - Struktur karakter non-primitif χ_{100k,n}
   - Output: teorema/lemma tertulis + verifikasi numerik konsistensi

3. **Verifikasi Konsistensi:** Kode verifikasi bahwa teorema G2/G3 konsisten
   dengan data numerik tersegel (tanpa mengubah data)

## 6. Konfigurasi yang Dikunci

| Parameter | Nilai |
|-----------|-------|
| Data input | Hanya artefact tersegel dari Q4 (read-only) |
| Output | Teorema/lemma tertulis + verifikasi konsistensi |
| Bukti | Matematis (pen-and-paper style, diterjemahkan ke kode verifikasi) |
| Verifikasi | Konsistensi numerik dengan data tersegel |

## 7. Pemeriksaan Integritas (C1–C4)

**C1: G2 Bound Valid**
- C(T,N) > 0 untuk semua T,N dalam data
- Bukti matematis C(T,N) > 0 tersedia

**C2: G3 Winding Cross-lock Valid**
- |Δwinding| ≤ 1 terbukti untuk karakter target
- Bukti matematis |Δwinding| ≤ 1 tersedia

**C3: Konsistensi Numerik**
- G2 bound konsisten dengan λ_min tersegel (λ_min ≥ C(T,N))
- G3 cross-lock konsisten dengan Δwinding = 0 tersegel

**C4: Determinisme & Receipt**
- Output deterministik, hash sha256LF terkunci

## 8. Verdict

- **ALL PASS**: C1–C4 PASS (G2 theorem valid, G3 theorem valid, konsisten)
- **PARTIAL**: G2 atau G3 valid tapi tidak keduanya
- **FAILED**: G2 atau G3 tidak valid (bukti gagal / bound negatif)
- **INCONCLUSIVE**: Tool error, bukti tidak lengkap, hash mismatch

Registry `A-2026-0035` hanya bila verdict `ALL PASS` dan integritas PASS.

## 9. Falsifier

Paket ini falsified bila:
- G2: C(T,N) ≤ 0 untuk beberapa T,N, atau bukti tidak valid
- G3: |Δwinding| > 1 terbukti, atau bukti tidak valid
- Konsistensi numerik gagal (λ_min < C(T,N) atau |Δwinding| > 1)
- Receipt tidak deterministik atau hash mismatch

## 10. Artefak dan Urutan Eksekusi

1. Tulis dan hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/riemann_g2g3.py`: fungsi verifikasi G2 bound + G3 winding proof.
3. Guard `msaf/tests/test_riemann_g2g3.py`: uji teorema G2/G3 + konsistensi numerik.
4. Jalankan verifikasi (read-only terhadap data tersegel).
5. Tulis laporan `reports/RIEMANN_G2G3_2026-10-21.md` dengan teorema/lemma verbatim.
6. Bila `ALL PASS`: registry `A-2026-0035`, HANDOFF §2.0bb, sertifikat sha256LF.
7. Suite penuh dan `freeze.py --verify`; commit/push hanya bila diminta.

## 11. Batas Eksplisit

- Hanya G2/G3 scope dari literatur G2 (bukan RH penuh)
- Hanya Route S ladder, karakter χ_{100k,n}, data Q4 tersegel
- Tidak ada komputasi numerik baru (hanya verifikasi konsistensi)
- Tidak ada klaim σ = 1/2, lokasi nol, RH, faktorisasi, RSA/ECC, Anderson, fisika
- Tidak merubah artefak Q4/Q4-Ext/H1/Engine B/Quantum yang tersegel