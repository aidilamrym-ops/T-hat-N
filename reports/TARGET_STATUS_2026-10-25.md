# Status Target Program — 2026-10-25

Dokumen ini mengumpulkan semua target matematika/fisika yang pernah masuk
antrian program, beserta status jujurnya per 2026-10-25. Sumber utama:
`reports/DAFTAR_MASALAH_KERJA.md`, `reports/FENCE_REGISTRY.md`,
`reports/HANDOFF.md`, dan berkas kampanye di `reports/`.

**Prinsip yang tidak berubah:** tidak ada klaim universal/infinite; setiap
target hanya boleh berstatus CERTIFIED jika ada artefak finit, receipt
deterministik, guard CI, dan entri registry. Status FAILED/INCONCLUSIVE/
PARTIAL dicatat apa adanya dan tidak "dinaikkan" menjadi CERTIFIED.

---

## 1. Ringkasan eksekutif

| Kelompok | Status ringkas |
|---|---|
| Figure-eight three-body (T2-r3/r4/r5) | r3 INCONCLUSIVE; **r4 CERTIFIED (T-2026-0043)**; r5 FAILED (tanpa A-2026-0044) |
| T1/T1b integrator ODE | CERTIFIED (A-2026-0040) |
| Navier–Stokes diskrit | CERTIFIED terbatas (A-2026-0038/0039); regularitas global TIDAK diklaim |
| RH / Guinand–Weil (ladder, T=100..500) | Beberapa fragmen CERTIFIED (T-2026-0001/0002, F-2026-0001/0002, A-2026-0033/0034/0035); RH global TIDAK diklaim |
| Hodge Picard bound | CERTIFIED terbatas (A-2026-0036/0037); hasil F_5/F_7 tidak informatif |
| BSD Q1 | Audit integritas (A-2026-0028/0030); verifikasi identitas BSD BELUM terpenuhi; recon 2026-10-25 menemukan formula pra-registrasi salah dan 14a1/15a1 tidak cocok dengan LMFDB |
| Twin prime Q2 | Sensus v3 N=10^9 **ALL PASS** dengan dua sieve independen (**A-2026-0046**); v2 N=10^7 tetap CERTIFIED (A-2026-0045); entri lama N=100.000 tetap INCONCLUSIVE (A-2026-0029) |
| ABC Q3 | CERTIFIED sensus C=100.000 (A-2026-0032) — 6 triple q>1.4 |
| RH scaffold Stage 1–4 | Scaffold Lean **kernel-checked PASS** (definisi + lemma trivial); **bukan bukti analitik penuh** |
| Quantum audit | Statistik 16-bin + χ² + tail z≥3.5 direproduksi; verdict RESOLVED (layer statistik, bukan klaim fisika) |
| Learnharness | Prototipe stub (engine + test); model nyata belum ada |
| MCP T2N | Modul asli dipulihkan; `opencode.jsonc` tetap menunjuk enam server |

---

## 2. Disposisi 20 masalah (`DAFTAR_MASALAH_KERJA.md`)

| No | Masalah | Status 2026-10-25 | Artefak / batas |
|---|---|---|---|
| 1 | Riemann | TREK AKTIF — fragmen finit | Ladder 201/301/401, dim 501 OUTCOME non-PD, T=100..500 winding cross-lock (A-2026-0033/0034/0035); RH global TIDAK diklaim |
| 2 | P vs NP | DAFTAR-B — formalisasi saja | Belum ada serangan komputasional; hanya rencana formalisasi fragmen |
| 3 | Hodge | TREK AKTIF — fragmen finit | Picard bound CH a_11 F_3 (A-2026-0036); F_5/F_7 non-informatif (A-2026-0037) |
| 4 | Yang–Mills mass gap | TIDAK MASUK | Butuh konstruksi QFT; di luar alat |
| 5 | Navier–Stokes | TREK AKTIF — diskrit | Kernel diskrit Lean (A-2026-0038), regularitas diskrit (A-2026-0039); global TIDAK diklaim |
| 6 | BSD | Q1 — INCONCLUSIVE/BLOCKED | A-2026-0028 (pilot 5 kurva), A-2026-0030 (full 21 kurva); recon 2026-10-25 menemukan hardcode, formula `2^{ω(N)-1}` tidak standar, dan 14a1/15a1 tidak cocok dengan LMFDB; tidak ada entri baru |
| 7 | Renormalisasi QFT | TIDAK MASUK | Fondasi, bukan klaim komputasional |
| 8 | Informasi black hole | TIDAK MASUK | Interpretasional |
| 9 | Konstanta kosmologis | TIDAK MASUK | Puzzle fisika; energi vakum tak terhitung rigorous |
| 10 | Pengukuran kuantum | TIDAK MASUK | Interpretasional |
| 11 | Gravitasi kuantum | TIDAK MASUK | Tak ada teori untuk dihitung |
| 12 | Twin prime | Q2 - fragmen finit CERTIFIED | A-2026-0046: N=10^9, dua sieve independen sepakat (count=3.424.506, max_gap=4.770, digest 427f9211…); A-2026-0045: N=10^7 (count=58.980); A-2026-0029 (N=100.000) tetap INCONCLUSIVE |
| 13 | abc | Q3 — CERTIFIED sensus | A-2026-0032: C=100.000, 6 triple q>1.4 |
| 14 | Asimetri materi | TIDAK MASUK | Model-dependent, kosmologi |
| 15 | Superkonduktivitas Tc-tinggi | TIDAK MASUK | Numerik Hubbard bukan rigorous-verifiable |
| 16 | Three-body | TREK AKTIF — r4 CERTIFIED, r5 FAILED | r3 INCONCLUSIVE; r4 T-2026-0043; r5 FAILED (M3/M8 non-diskriminatif), tanpa A-2026-0044 |
| 17 | Schanuel | DAFTAR-B — formalisasi saja | Hanya rencana instans Lindemann–Weierstrass |
| 18 | Cosmic censorship | TIDAK MASUK | PDE Einstein di luar jangkauan |
| 19 | Anderson | DAFTAR-B — syarat | Benchmark RBM S1/S2 (A-2026-0023) ada, tetapi transisi Anderson fisik TIDAK diklaim |
| 20 | Soliton | DAFTAR-B — syarat | Belum ada enclosure Evans; menunggu integrator tervalidasi |

---

## 3. Garis figure-eight (three-body reduced 8×8)

| Trek | Verdict | Registry | Catatan |
|---|---|---|---|
| T2 | FAILED | — | K3 singularitas translasi-x eksak (`DF e = 0`) |
| T2-r2 | FAILED | — | K2: slack kuadratik T1b beku, width 320 di step 96 |
| T2-r3 | INCONCLUSIVE | — | K6/M5 non-diskriminatif; tidak ada A-2026-0042 |
| T2-r4 | **CERTIFIED** | **T-2026-0043** + A-2026-0043 | K1–K5 + K6 M1–M9 diskriminatif; receipt `8b6088c2…` |
| T2-r5 | FAILED | — | M3 (`C=1/3`) dan M8 (`GAUSS_COND_MAX=10^6`) non-diskriminatif; A-2026-0044 tidak dibuat |

Klaim r4 tetap: keberadaan dan **keunikan lokal** orbit figure-eight di dalam
box `B`, modulo gauge `q1y=1/5`, `I_xy=0`, dengan `R_B=1e-18`. Tidak ada
klaim global, stabilitas, chaos, ergodisitas, KAM, PDE, RH, fisika, atau
prioritas.

---

## 4. RH scaffold, quantum audit, learnharness

### 4.1 RH scaffold (`reports/RH_SCAFFOLD_NOTES/`)

| Stage | Berkas Lean | Receipt | Status jujur |
|---|---|---|---|
| 1 | `Stage_1_Formalization_Test_Function_Space.lean` | `Stage_1_..._receipt.json` | Scaffold definisi `MSAFTestFunctionSpace` dan `continuous_quadratic_form`; **kernel-checked PASS**, belum ada bukti analitik penuh |
| 2 | `Stage_2_Derivation_Analytic_Tail_Bound.lean` | `Stage_2_..._receipt.json` | Scaffold bound non-negatif; **kernel-checked PASS**, **bukan** derivasi tail Archimedean penuh |
| 3 | `Stage_3_Eigenvalue_Locking_Dimension_Induction.lean` | `Stage_3_..._receipt.json` | Scaffold predikat locking; **kernel-checked PASS**, **bukan** induksi dimensi penuh |
| 4 | `Stage_4_Containment_Proof.lean` | `Stage_4_..._receipt.json` | Scaffold predikat containment; **kernel-checked PASS**, **bukan** bukti L² penuh |

Semua berkas Lean bebas `sorry`/`admit`/`unsafe`/`axiom`, dan keempatnya
sekarang **lulus kernel check** dengan Lean 4.33.1 / Mathlib `0df444a360`
(perintah `lake env lean`, receipt mencatat hasil PASS). Namun isinya masih
definisi dan lemma trivial: Stage 2 bukan derivasi tail Archimedean, Stage 3
bukan induksi dimensi, Stage 4 memakai predikat placeholder `True`. Jangan
menyebutnya "bukti RH" atau "bukti analytic tail bound". Ini hanya kerangka
kerja yang sudah dikompilasi, bukan bukti analitik.

Log lengkap: `reports/RH_SCAFFOLD_NOTES/KERNEL_CHECK_2026-10-25.md` (perintah
kernel, SHA-256LF, axiom footprint, dan anti-circularity gate PASS).

### 4.2 Quantum audit (`audit_quantum/`)

- `audit_quantum/analyze_stats.py` membaca tiga binary `stats_d201.bin`,
  `stats_d301.bin`, `stats_d401.bin` (masing-masing 20.000 float64
  little-endian).
- Setiap set dibagi ke 16 bin equiprobable normal; expected 1250/bin.
- Hasil: χ² = 7.508800 / 10.398400 / 11.592000, semuanya di dalam window
  [0, 60]; tail satu sisi z ≥ 3.5 = 2 / 4 / 3. Overall **RESOLVED**.
- `reports/audit_quantum_2026-10-19.md` memuat tabel bin, verdict, dan
  receipt JSON; `reports/audit_quantum_2026-10-19.json` memuat receipt
  lengkap (hash file, counts, χ², mean, stdev).
- **Batas:** ini layer statistik SIMULATED; bukan klaim fisika, bukan
  pengganti layer interval tersertifikasi.

### 4.3 Learnharness (`msaf/learnharness_prototype.py`)

- `msaf/learnharness_prototype.py`: kelas `LearnEngine` stub (`train` menyimpan
  panjang data, `predict` mengembalikan matriks identitas 8×8).
- `msaf/tests/test_learnharness_prototype.py`: tes dasar.
- **Batas:** bukan model ML nyata, tidak dilatih pada data kampanye, tidak
  terintegrasi ke pipeline figure-eight. Status: PROTOTIPE.
- Catatan: `msaf/learnharness/` adalah repo pihak ketiga terpisah (nested git,
  di-ignore oleh repo utama). Prototipe MSAF sengaja diletakkan di
  `msaf/learnharness_prototype.py` agar dapat dilacak oleh repo utama.

### 4.4 Twin prime Q2 v2 (`msaf/twin_prime_v2.py`)

- Dua sieve independen: A = Eratosthenes bytearray penuh; B = segmented
  sieve, base prime sampai `isqrt(N+2)`, blok `2^20`.
- Konfigurasi terkunci: `N = 10_000_000`; integer Python eksak; receipt tanpa
  runtime/timestamp.
- Hasil: `count = 58.980`, `max_gap = 1.722`, pasangan pertama `(3,5)`,
  pasangan terakhir `(9.999.971, 9.999.973)`; `pairs_A == pairs_B`;
  `pairs_sha256 = 64ecf493…d380`.
- Determinisme: dua run menghasilkan receipt SHA-256
  `6c613dd573867e2d54cf7ed162413cb7f1b5e40b8be2724797681dddb72094d4`.
- Registry: `A-2026-0045` (CERTIFIED untuk fragmen finit ini).
- **Batas:** bukan bukti konjektur twin prime, bukan klaim asimtotik, dan
  tidak mencakup `N = 10^9`.

### 4.5 BSD Q1 recon (`reports/BSD_Q1_RECON_2026-10-25.md`)

- Audit lama `A-2026-0028` hanya menunjukkan hardcode/tautologi; recon
  baru memeriksa nilai tabel terhadap LMFDB.
- Kode `msaf/bsd_descent.py` tetap hardcode: `two_descent()` tabel lookup,
  `modular_symbol_ec()` tabel, `real_period()` = 1,
  `verify_bsd()` membandingkan `invariants` dengan `rhs_map`, dan
  `conductor` mengembalikan `|Δ|`.
- Formula pra-registrasi `2^(ω(N)-1)` bukan formula BSD standar. Untuk
  `14a1` faktor itu menghasilkan `1/3`, sedangkan LMFDB memberi `1/6`.
  Untuk `15a1` pra-registrasi menulis torsion `4`/Tamagawa `4`/`1/4`,
  sedangkan LMFDB memberi torsion `8`/Tamagawa `8`/`1/8`.
- `11a1`, `17a1`, dan `19a1` cocok dengan LMFDB; ketiganya berkonduktor
  prima sehingga faktor tambahan bernilai 1 dan kesalahan formula tidak
  terlihat.
- Verdict: **INCONCLUSIVE/BLOCKED**; C1/C2/C3 tidak terpenuhi. Tidak ada
  entri registry baru; `A-2026-0028` dan `A-2026-0030` tetap `INCONCLUSIVE`.

---

## 5. Registry (ringkas)

- Entri **T** (teorema finit): `T-2026-0001`, `T-2026-0002`, `T-2026-0043`.
- Entri **F** (pagar): `F-2026-0001`, `F-2026-0002`.
- Entri **A** (audit/verdict): `A-2026-0001` … `A-2026-0040` (dengan `A-2026-0031` tidak ada), `A-2026-0043`, dan `A-2026-0045`.
- `A-2026-0041` dan `A-2026-0042` **tidak ada** (r2/r3 gagal/inconclusive).
- `A-2026-0044` **tidak ada** (r5 FAILED).
- Entri terbaru figure-eight: `T-2026-0043` (r4) dan `A-2026-0043` (audit K6 r4).
- Entri terbaru twin prime: `A-2026-0045` (Q2 v2, N=10^7).

---

## 6. Sisa pekerjaan yang jujur

1. **RH scaffold Stage 1–4**: scaffold sudah kernel-checked (PASS), tetapi
   isinya masih definisi dan lemma trivial. Pekerjaan sebenarnya adalah
   mengganti placeholder dengan derivasi tail Archimedean, induksi eigenvalue
   locking, dan bukti containment L². Jangan menaikkan status sebelum ada
   pembuktian baru + kernel check + receipt baru.
2. **Quantum audit lanjutan**: layer statistik 16-bin sudah selesai
   (χ² 7.5088/10.3984/11.592; tail 2/4/3; RESOLVED). Jika ingin klaim
   fisik, perlu studi baru dengan null ensemble eksplisit dan prereg
   terpisah.
3. **Learnharness**: tentukan use-case nyata, latih model pada dataset
   kampanye, tambahkan guard agar prediksi tidak pernah menggantikan
   sertifikat.
4. **Figure-eight r6** (opsional): PRREG baru sebelum kode, perbaiki M3
   (mutasi gauge yang benar-benar memindahkan `I_xy`) dan M8 (cap di bawah
   nilai terukur ≈2.96e4), lalu jalankan K6 M1–M10.
5. **BSD Q1**: recon 2026-10-25
   (`reports/BSD_Q1_RECON_2026-10-25.md`) menunjukkan paket lama
   hardcode/tautologis dan nilai pra-registrasi `14a1`/`15a1` salah.
   Verifikasi identitas BSD belum dimulai; perlu pra-registrasi baru
   sebelum kode baru. `A-2026-0028`/`A-2026-0030` tetap `INCONCLUSIVE`.
6. **Twin prime Q2 lanjutan**: v2 sudah ALL PASS pada N=10^7 (A-2026-0045).
   Target asli N=10^9 belum dikerjakan; jika dilanjutkan, butuh pra-registrasi
   baru dan mesin/memori yang memadai. Jangan memperluas klaim tanpa sensus
   eksak baru.
7. **MCP T2N**: modul asli sudah dipulihkan; `opencode.jsonc` masih menunjuk
   enam server. Perubahan MCP belum dilakukan dan tidak boleh dicampur dengan
   kampanye matematika.

8. **Arsip**: artefak yang dirujuk `FENCE_REGISTRY.md` tetap di `reports/`;
   `archive/README.md` mencatat kebijakan ini. Jangan memindahkan sertifikat
   sealed ke `archive/` karena akan memutus baris `sha256LF <hash> <path>`.

---

## 7. Batas klaim

Dokumen ini **bukan** bukti RH, bukan bukti BSD, bukan bukti Navier–Stokes
global, bukan bukti three-body global, bukan klaim Hodge umum, bukan klaim
fisika, dan bukan klaim prioritas. Semua status di atas adalah status
artefak finit yang dapat diperiksa mesin, dengan batas yang ditulis eksplisit.

---

Ditulis 2026-10-25 sebagai indeks status program.
