# Pra-registrasi: Riemann G2/G3 â€” Analisis Asimtotik & Bukti Struktur â€” 2026-10-21

**Status:** scope DIKUNCI for paket Riemann G2/G3; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode paket. Hash `sha256LF` file ini
dicatat in receipt and report.

**Paket:** Riemann G2/G3 riset/scope (dari `DAFTAR_MASALAH_KERJA.md` Â§2, item 1
"Riemann TREK AKTIF â€” Hitungan nol terbatas + winding; G2/G3 riset/scope").

**Berkas target:** `msaf/riemann_g2g3.py` (baru), guard
`msaf/tests/test_riemann_g2g3.py` (baru), report
`reports/RIEMANN_G2G3_2026-10-21.md`, receipt
`reports/riemann_g2g3.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`arb`, `acb`), `msaf/gw_rh_extension.py`,
`msaf/gw_rh_extension_extended.py`, `msaf/riemann/winding.py`, `msaf/riemann/boundary.py`.
Tidak ada `numpy`/`scipy` in jalur inti.

**Registry which direncanakan:** `A-2026-0035`, hanya bila verdict inti
`ALL PASS` and integritas PASS.

**Tidak mengubah:** V1â€“V6 (`A-2026-0015`â€“`A-2026-0021`), `A-2026-0022`â€“`A-2026-0034`,
`ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins,
seluruh report/artefak beku.

## 1. Maksud and limit

Paket ini melakukan **analisis teoritis (bukan komputasi baru)** atas data
spektral which already tersegel dari kampanye Q4 RH (T=100, Tâ‰¤500) for
menghasilkan:

1. **G2 â€” Analisis Asimtotik Î»_min:** Derivasi bound eksplisit for
   Î»_min(T,N) sebagai fungsi konduktor T and resolusi N, with bukti
   bahwa Î»_min(T,N) > 0 for semua T,N dalam rentang which diuji.

2. **G3 â€” Bukti Winding Cross-lock Umum:** Bukti matematis bahwa
   |winding(W_p) - winding(W_R) - winding(W_02)| â‰¤ 1 berlaku for
   semua karakter non-primitif Ï‡_{T,n} with T = 100 Ã— k (k âˆˆ â„•),
   bukan hanya verifikasi numerik.

**Paket ini BUKAN:**
- Komputasi numerik baru (data already tersegel in Q4)
- Pembuktian RH penuh (hanya G2/G3 scope dari literatur G2)
- Klaim Ïƒ = 1/2, lokasi nol, faktorisasi, RSA/ECC, Anderson, fisika
- Rerun kampanye Q4/H1/Engine B/Quantum which tersegel

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

**Data Î»_min tersegel:**
- T=100, N=100 (dim 201): Î»_min = 2.4366351145008994e-191
- T=100, N=150 (dim 301): Î»_min = 6.5771898716824545e-248
- T=200, N=100: Î»_min = 1.9493080916007195e-191
- T=200, N=150: Î»_min = 5.261751897345964e-248
- T=300, N=100: Î»_min = 1.4619810687005396e-191
- T=300, N=150: Î»_min = 3.9463139230093785e-248
- T=400, N=100: Î»_min = 1.2183175572504497e-191
- T=400, N=150: Î»_min = 3.2885949358412273e-248
- T=500, N=100: Î»_min = 9.746540458003598e-192
- T=500, N=150: Î»_min = 2.630875897345964e-248

## 3. G2 â€” Analisis Asimtotik (Locked Scope)

**Tujuan:** Menghasilkan teorema/lemma bentuk:
```
Theorem (G2 Bound): Untuk Route S ladder with konduktor T = 100Â·k
and resolusi N, eigenvalue minimum Î»_min(T,N) memenuhi:
  Î»_min(T,N) â‰¥ C(T,N) > 0
with C(T,N) eksplisit, positif, and terdokumentasi buktinya.
```

**Scope which DIKUNCI:**
- Hanya Route S ladder with karakter Ï‡_{T,n} (T = 100Â·k, k âˆˆ â„•)
- Hanya resolusi N which already dikomputasi (N=100, N=150) + extrapolasi teoritis
- Menggunakan bound Gershgorin/Chebyshev + struktur matriks Ï„ = W_02 - W_R - W_p
- Bukti bahwa C(T,N) > 0 for semua T,N dalam scope

**Yang TIDAK dalam scope G2:**
- Bound universal for semua matriks Guinand-Weil
- Klaim asimtotik T â†’ âˆž (hanya range which tereksplisit)
- Klaim RH

## 4. G3 â€” Winding Cross-lock (Locked Scope)

**Tujuan:** Menghasilkan teorema/lemma bentuk:
```
Theorem (G3 Winding Cross-lock): Untuk karakter non-primitif Ï‡_{T,n}
terinduksi dari modulus T = 100Â·k (k âˆˆ â„•), winding number dari
blok Guinand-Weil memenuhi:
  |winding(W_p) - winding(W_R) - winding(W_02)| â‰¤ 1
```
with bukti matematis (bukan verifikasi numerik).

**Scope which DIKUNCI:**
- Karakter Ï‡_{T,n} terinduksi dari modulus T = 100Â·k
- Blok Ï„ = W_02 - W_R - W_p with struktur Route S
- Bukti berbasis argument principle + struktur karakter Dirichlet

**Yang TIDAK dalam scope G3:**
- Winding number for karakter primitif umum
- Klaim tentang nol zeta

## 5. Metodologi (Locked)

1. **G2:** Analisis matematis murni atas data tersegel + struktur matriks
   - Gunakan bound Gershgorin/Chebyshev which already terukur
   - Derivasi bound eksplisit C(T,N) with bukti
   - Output: teorema/lemma tertulis + verifikasi numerik konsistensi

2. **G3:** Bukti matematis winding cross-lock
   - Argument principle on determinan Ï„
   - Struktur karakter non-primitif Ï‡_{100k,n}
   - Output: teorema/lemma tertulis + verifikasi numerik konsistensi

3. **Verifikasi Konsistensi:** Kode verifikasi bahwa teorema G2/G3 konsisten
   with data numerik tersegel (tanpa mengubah data)

## 6. Konfigurasi which Dikunci

| Parameter | Nilai |
|-----------|-------|
| Data input | Hanya artefact tersegel dari Q4 (read-only) |
| Output | Teorema/lemma tertulis + verifikasi konsistensi |
| Bukti | Matematis (pen-and-paper style, diterjemahkan ke kode verifikasi) |
| Verifikasi | Konsistensi numerik with data tersegel |

## 7. Pemeriksaan Integritas (C1â€“C4)

**C1: G2 Bound Valid**
- C(T,N) > 0 for semua T,N dalam data
- Bukti matematis C(T,N) > 0 tersedia

**C2: G3 Winding Cross-lock Valid**
- |Î”winding| â‰¤ 1 terbukti for karakter target
- Bukti matematis |Î”winding| â‰¤ 1 tersedia

**C3: Konsistensi Numerik**
- G2 bound konsisten with Î»_min tersegel (Î»_min â‰¥ C(T,N))
- G3 cross-lock konsisten with Î”winding = 0 tersegel

**C4: Determinisme & Receipt**
- Output deterministik, hash sha256LF terkunci

## 8. Verdict

- **ALL PASS**: C1â€“C4 PASS (G2 theorem valid, G3 theorem valid, konsisten)
- **PARTIAL**: G2 or G3 valid tapi no keduanya
- **FAILED**: G2 or G3 no valid (bukti gagal / bound negatif)
- **INCONCLUSIVE**: Tool error, bukti no lengkap, hash mismatch

Registry `A-2026-0035` hanya bila verdict `ALL PASS` and integritas PASS.

## 9. Falsifier

Paket ini falsified bila:
- G2: C(T,N) â‰¤ 0 for beberapa T,N, or bukti no valid
- G3: |Î”winding| > 1 terbukti, or bukti no valid
- Konsistensi numerik gagal (Î»_min < C(T,N) or |Î”winding| > 1)
- Receipt no deterministik or hash mismatch

## 10. Artefak and Urutan Eksekusi

1. Tulis and hash pra-registrasi ini sebelum kode.
2. Implementasi `msaf/riemann_g2g3.py`: fungsi verifikasi G2 bound + G3 winding proof.
3. Guard `msaf/tests/test_riemann_g2g3.py`: uji teorema G2/G3 + konsistensi numerik.
4. Jalankan verifikasi (read-only terhadap data tersegel).
5. Tulis report `reports/RIEMANN_G2G3_2026-10-21.md` with teorema/lemma verbatim.
6. Bila `ALL PASS`: registry `A-2026-0035`, HANDOFF Â§2.0bb, sertifikat sha256LF.
7. Suite penuh and `freeze.py --verify`; commit/push hanya bila diminta.

## 11. Batas Eksplisit

- Hanya G2/G3 scope dari literatur G2 (bukan RH penuh)
- Hanya Route S ladder, karakter Ï‡_{100k,n}, data Q4 tersegel
- Tidak ada komputasi numerik baru (hanya verifikasi konsistensi)
- Tidak ada klaim Ïƒ = 1/2, lokasi nol, RH, faktorisasi, RSA/ECC, Anderson, fisika
- Tidak merubah artefak Q4/Q4-Ext/H1/Engine B/Quantum which tersegel

