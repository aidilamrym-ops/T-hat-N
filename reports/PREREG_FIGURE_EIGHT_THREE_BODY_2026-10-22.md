# Pra-registrasi T2: orbit periodik figure-eight three-body tervalidasi (Daftar-B 16) - 2026-10-22

**Status:** scope DIKUNCI untuk trek T2; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis dan di-commit sebelum kode T2. Hash `sha256LF`
berkas ini dicatat di receipt T2 dan laporan.

**Latar:** T1b (`reports/PREREG_ODE_VALIDATED_T1B_2026-10-21.md`) sudah
diseal dengan verdict **ALL PASS** dan registry `A-2026-0040`. Pemilik membuka
Daftar-B butir 16 (orbit figure-eight tervalidasi) melalui pilihan soal
("Daftar-B 16: Three-Body (Recommended)"), pola sama dengan T1/T1b:
ukur-dulu → pra-registrasi di-commit sebelum kode → implementasi → seal →
registry hanya bila ALL PASS → push. Pra-registrasi ini mengunci scope T2
**setelah** kampanye probe (pengungkapan wajib di §2), sebelum ada satu baris
kode pun di `msaf/figure_eight.py`.

**Paket:** Daftar-B 16. **Bukan** klaim prioritas; **bukan** klaim bahwa
data desimal-eksak ini "figure-eight yang asli" dalam arti data bilangan
real sejatinya; **bukan** bukti di Lean/Coq.

**Berkas target:** `msaf/figure_eight.py` (modul bersertifikat baru),
`msaf/tests/test_figure_eight.py` (guard), kampanye → receipt
`reports/figure_eight_three_body_2026-10-22.json`, laporan
`reports/FIGURE_EIGHT_2026-10-22.md`. Registry yang direncanakan:
`A-2026-0041`, **hanya** bila verdict ALL PASS.

**Dependensi:** Python 3.14, python-flint 0.9.0 (.ball/arb), `fractions`.
Reuse **import-saja** dari modul tersegel `msaf/ode_validated.py`
(`sha256LF c1d9b5d60036a5f0772f7e3f1b8c78969efaa7146a713c762531ddce346251b9`)
dan `msaf/ode_validated_block.py`
(`sha256LF 42d196a51c5ae45e3b87b8c1e36319abfeb93df776b3c2317e812f7c2c0b5b97`,
guard `f061e7ebeabfaa808280455f6d5bff595c32d9feaef164fa11d76bcbcf8aa98f`,
terpin di `A-2026-0040`). Tidak ada modul beku yang diubah. Probe memakai
floating-point di **luar** jalur tersertifikasi (dibatasi §2 dan K1).

---

## 1. Maksud dan batas

T2 menyertifikasi sebagai hasil komputer-assisted **miliknya sendiri**:

1. **Keberadaan + keunikan lokal** orbit periodik masalah tiga-bodi planar
   Newtonian (m = G = 1) untuk IVP yang dinyatakan **persis rasional**
   (desimal-pendekatan klasik Moore, dipotong menjadi pecahan), dekat data
   awal yang diukur probe, melalui keberadaan titik tetap peta Kembali-2 di
   seksi Poincaré (Krawczyk).
2. **Tabung (tube) lintasan tervalidasi** satu-periode: pembungkus keadaan
   di sepanjang horizon, termasuk pembungkus matriks monodromi
   (`∂Φ/∂y₀`, 12×12) sebagai artefak untuk T2b.
3. **Deskriptor bentuk tervalidasi** (K5): struktur penyilangan sumbu-x badan
   3 dan cacat koreografi.

Yang **tidak** diklaim di T2 (dan tidak boleh muncul di laporan/receipt):

- **Spektrum/stabilitas Floquet** (multiplikator dekat-1) → dialihkan ke
  **T2b** dengan alasan terukur: probe FD vs monodromy tidak konvergen
  (§2). K4 hanya menghasilkan matriks terenclosure, tanpa klaim eigen.
- Keunikan **global** (hanya lokal di kotak Krawczyk), keberadaan orbit
  lain, atau identifikasi absolut dengan figure-eight bilangan-real sejati.
- Segala klaim di luar batas T1b: RH/PDE/chaos/ergodicity/Soliton/Evans/
  fisika/analytic-continuation/prioritas/bukti formal. Hasil S4 T1b tetap
  **bukan** klaim keberadaan orbit figure-eight (batas T1b tidak dicabut;
  T2 adalah lintasan klaim yang terpisah dengan mekanisme dan pra-registrasi
  sendiri).

---

## 2. Pengukuran pra-kunci (probe — sebelum scope dikunci)

Semua angka di bawah diukur **sebelum** berkas ini ditulis; angka inilah yang
mengunci toleransi §3–§4. Probe memakai scipy DOP853 (rtol=2.3e-14, atol=1e-15,
max_step=0.005) dan Jacobian syuting analitik (matriks variasional + koreksi
waktu-implisit), **di luar** jalur tersertifikasi.

**a. Data IVP tersegel (T1b `_run_s4`):** q(0) = (−1,0), (1,0), (0,0);
v₁ = v₂ = (347111/10⁶, 532728/10⁶); v₃ = (−694222/10⁶, −1065456/10⁶);
E₀ = −257428899017/200000000000 = −1.287144495085; L₀ = 0; COM = 0.

**b. Orbit periodik sejati (Newton least-squares, pangkal analitik):**
residu |G|∞: 1.7e-6 → 4.561e-14; jarak data-awal-seeded 1.089e-04
(didominasi geser periode). Data (dalam presisi ganda, **bukan** benih
tersertifikasi):

```
q1 = (-1.000028237415442, -3.601363571456254e-05)
q2 = ( 0.9999905329089701, -2.1852871993005e-05)
v1 = ( 0.34708885820984614, 0.5327249027394381)
v2 = ( 0.3471341172021619, 0.5327249030598572)
v3 = (-0.694222975412007, -1.0654498057992956)
T* = 6.326003039910031
```

E(orbit) = −1.2871299154104481 (Δ = 1.458e-05 dari E₀); L(orbit) = −1.9e-12.

**c. Seksi Poincaré (codim-1) — Σ = {q₃ᵧ = 0, orientasi v₃ᵧ < 0}:**
penyilangan q₃ᵧ pada orbit sejati (periode [0, T\*]):

| waktu | q₃x | v₃ᵧ |
|---|---|---|
| 0 (titik awal, eksak) | 0 | −1.065450 |
| 2.108735283 | −1.0000047703 | +0.532725 |
| 3.162988113 | −4.769194074911e-05 | −0.612126 |
| 4.217376381 | +1.0000047717 | +0.532725 |
| T\* ≈ 6.326003040 | 0 (kembali) | −1.065450 |

Jadi per periode ada **4 penyilangan** (2 turun = orientasi seksi: t=0 dan
t≈3.163; 2 naik di luar orientasi), jarak antar-silang ≥ 3.16. Keadaan
seksi bebas-rotasi di titik kerja (q₃x ≠ 0; rotasi tidak mempertahankan Σ
kecuali θ = kπ).

**d. Titik kerja (pembulatan 12 desimal → benih rasional eksak):** dari
x_c2 (seksi pada silang-turun 3.162988113) diperbaiki sekali langkah lstsq
Jacobian seksi (jarak langkah 9.484e-07, |F|∞ 3.379e-11 → 6.176e-12):

```
x̂₀ = ( 0.881825885905,  0.471573247799,
       -0.881817147851, -0.471630773362,
       -0.000048006190,
       -0.557287392981,  0.306081711672,
       -0.557356449974,  0.306044779690,
        1.114643842954, -0.612126491362)
```

(koordinat seksi: q1x,q1y,q2x,q2y,q3x, v1x,v1y,v2x,v2y,v3x,v3y).

**e. Peta kembali-2:** dari x_c2: kaki-1 (silang turun berikutnya, di t₁ =
3.163014927), kaki-2 (t₂ = 3.162988113); t₁+t₂ = 6.326003040 = T̃ (diskalai
sebagai T̃). |P̃²(x_c2) − x_c2|∞ = 3.379e-11 (ganda).

**f. Kondisi Jacobian seksi DF (FD ganda — TIDAK andal, dipakai hanya untuk
estimasi):** σmax = 61.59, σmin = 1.5368e-09, cond = 4.008e+10. Lantai noise
FD ≈ 5e-7 per entri (integrasi + akar) → σmin **tidak terukur andal** di
ganda; monodromy menyiratkan |μ−1| terkecil ~1.5e-07. Pasangan eigen jauh
FD cocok silang dengan monodromy sampai 9 digit
(−0.2976±0.9547j, 0.9986±0.0529j). **Konsekuensi:** K3 bergantung pada
σmin DF sesungguhnya; kasus terburuk terukur (1.5e-09) memberi margin
inclusion tipis (§4 K3). Bila inclusion gagal → FAILED jujur, bukan cacat
pra-registrasi.

**g. Monodromy (matriks variasional benar):** 12 multiplikator — 4 real
{1.000001239651, 1.000000246527, 0.999999753473, 0.999998760351}, dua pasang
nyaris-1 {1±1.463e-7j, 1±1.5538e-6j}, dua pasang unit {−0.2976±0.9547j,
0.9986±0.0529j}; |detM − 1| = 5.77e-14.

**h. Klaster nyaris-1 belum konvergen antar-metode:** FD peta kembali-2
memberi deviasi ~5e-4, monodromy ~1.2e-6 — keduanya bisa tercemar (noise FD
vs pengelompokan eigen dekat-1). **Maka stabilitas spektral DIKECUALI dari
T2 (→ T2b).**

**i. Koreografi (orbit sejati, ganda):** ‖q1(t+T/3) − q2(t)‖∞ ≤ 2.524e-11;
‖q1(t+2T/3) − q3(t)‖∞ ≤ 2.687e-11 — koreografi **eksak** sampai noise
integrasi.

**j. Simetri antipodal setengah-periode: FALSE** — residu terbaik atas semua
permutasi label = 6.946e-01. Tidak ada klaim simetri (tidak dikunci).

**k. Kecacatan probe (diungkap, bukan dihaluskan):** matriks variasional pada
probe sempat salah tanda **dan** salah skala (`−K`, pembagian `d²`, seharusnya
`+K`, `d³`); angka monodromy lama (953, 28) **dibuang** dan dihitung ulang.
Probe hanya mengukur; tidak ada angka probe yang masuk jalur tersertifikasi
selain benih rasional §2d dan jendela §3 yang semuanya dinyatakan persis.

---

## 3. Formulasi yang dikunci

**3.1 Sistem.** Tiga-bodi planar Newtonian, massa = 1, G = 1; tata letak
keadaan 12-dim identik T1b: y = (q1x,q1y,q2x,q2y,q3x,q3y, v1x,v1y,v2x,v2y,
v3x,v3y). Koefisien gaya diimpor dari modul tersegel (`coeffs_three_body`).

**3.2 Seksi dan peta.** Σ = {q₃ᵧ = 0} dengan orientasi silang-turun
(v₃ᵧ < 0). Koordinat seksi x ∈ ℝ¹¹ = (q1x,q1y,q2x,q2y,q3x, v1x,v1y,v2x,
v2y,v3x,v3y); embedding y = (x₀,x₁,x₂,x₃, x₄, 0, x₅,…,x₁₀); proyeksi
balik membuang q₃ᵧ. P̃ = kembali-silang-turun-pertama; F(x) =
Π(P̃²(x)) − x. Titik tetap F(x\*) = 0 ⇔ orbit periodik dengan periode
t₁(x\*)+t₂(x\*).

**3.3 Jendela waktu (terkunci dari §2):**

- w₁ = [3.163014927 − 0.01, 3.163014927 + 0.01] (silang-turun pertama),
- w₂ = [6.326003040 − 0.01, 6.326003040 + 0.01] (silang-turun kedua).

Uji tanda tersertifikasi di ujung-ujung jendela (q₃ᵧ bertanda ketat:
w₁: −/+; w₂: +/−; margin terukur 0.06 dan 0.10) **dan** keadaan
monoton v₃ᵧ ≤ −1/2 di sepanjang kedua jendela → silang unik per jendela.
Lebar pembungkus waktu-silang ≤ 1e-19 (bisection-berpagar pada polinomial
Taylor tersertifikasi; monoton memberi batas |Δt| ≤ |q₃ᵧ|/0.5).

**3.4 Grid.** T̃ = 6.326003040 (desimal-hingga, rasional); h := T̃/1536 =
0.0041184915625 (eksak, sehingga T̃/3 = 512h dan 2T̃/3 = 1024h bilangan
bulat — syarat perbandingan koreografi pada §4 K5); N = 1554 langkah
(H = N·h ≥ 6.4 ≥ atas-w₂); ambang-atas N dikunci, bukan knob.

**3.5 Konfigurasi.** Presisi 256-bit; orde Taylor 24; sisa (remainder) 1×
nilai baku T1b; propagasi ketidakpastian **sweep bertanda lintas-blok**
(mekanisme T1b, diimpor) — knob `SWEEP_SIGNED = True` (mutasi M5 membalik
nilai ini tanpa mengubah nilai baku lainnya); faktor sisa `REMAINDER_FACTOR
= 1` (mutasi M1 mengubahnya).

**3.6 Mekanisme Krawczyk.** Benih: x̂₀ §2d. (i) **Newton bersertifikat
presisi-256-bit, ≤ 6 iterasi**: tiap iterasi wajib menurunkan |F|∞ secara
ketat; dua kenaikan berturut-turut → abort K3 (status gagal jujur); berhenti
bila |F|∞ ≤ 1e-20. (ii) **Satu kampanye kotak**: integrasi tervalidasi dari
kotak B = box(x̂, r_B), r_B = 1e-10, di sepanjang [0, H] dengan propagasi
turunan S (∂Φ/∂y₀) yang sama; tabung, F(x̂), dan DF(B) dihitung dari satu
kampanye ini (DF dari produk Jacobian langkah + koreksi waktu-implisit
rumus peta Poincaré: ∂Φ_{t(x)}/∂x = S − f·(∇g·S)/(∇g·f), g = q₃ᵧ).
(iii) Ŵ = invers matriks titik-tengah DF(x̂) di 256-bit;
K(B) = x̂ − ŴF(x̂) + (I − Ŵ·DF(B))·(B − x̂); suksesi:
K(B) ⊆ box(x̂, 0.9·r_B).

**3.7 Batas sensitivitas (diungkap):** margin inclusion bergantung pada
σmin DF dan L = ‖D²F‖: pada kasus terburuk terukur (σmin = 1.5e-09)
kebutuhan ‖Ŵ‖·L·r_B² + ‖Ŵ‖·1e-20 ≈ 6.7e-12·L + 6.7e-12 < 9e-11 menuntut
L ≲ 12; pada σmin ≥ 1e-07 margin melompat lebar. Kegagalan → FAILED jujur.

---

## 4. Kriteria lulus

- **K1 — data persis, tanpa float.** Semua konstanta modul rasional (benih
  12-desimal §2d, jendela §3.3, T̃, h, N, r_B, ambang); AST-scan
  `msaf/figure_eight.py` tanpa literal float, `math`, `numpy`, `scipy`,
  `random`, waktu; import hanya dari modul tersegel; hash modul tersegel
  tidak berubah (diverifikasi suite/freeze yang sudah ada).

- **K2 — integrasi tervalidasi.** Tabung keadaan ≤ 1e-22 di **semua**
  checkpoint di [0, H] (termasuk di dalam w₁ dan w₂); lebar pembungkus
  waktu-silang ≤ 1e-19; uji tanda q₃ᵧ di ujung jendela ketat sesuai §3.3;
  v₃ᵧ ≤ −1/2 di kedua jendela (monotonitas tersertifikasi).

- **K3 — keberadaan + keunikan lokal.** Newton §3.6 mencapai |F|∞ ≤ 1e-20
  dalam ≤ 6 iterasi monoton, lalu Krawczyk: K(B) ⊆ box(x̂, 9e-11).
  Implikasi yang diklaim: ada **tepat satu** titik tetap F di B (→ orbit
  periodik periode t₁+t₂ dengan t₂ ∈ w₂, keunikan **lokal di B saja**).

- **K4 — artefak monodromy.** Matriks 12×12 ∂Φ/∂y₀ pada silang-turun kedua
  terkenclosure: lebar per entri ≤ 1e-16; determinan terenclosure
  (hitungan interval 256-bit) **memuat 1** (Liouville). Tanpa klaim eigen.

- **K5 — deskriptor bentuk.** (a) Ada silang naik q₃ᵧ unik di
  [2.108735283 ± 1e-6] dan [4.217376381 ± 1e-6] dengan v₃ᵧ ≥ +1/4 di
  bracket, dan q₃x di silang masing-masing ∈ [−1.00001, −0.99999] dan
  [0.99999, 1.00001]; (b) silang di w₁: q₃x ∈ [−6e-05, −3e-05]; silang di
  w₂: q₃x ∈ [−1e-06, +1e-06]; (c) selisih periode |T̃ − (t₁+t₂)(x̂)| ≤ 1e-09;
  (d) cacat koreografi pada **semua** checkpoint kisi dengan jarak tepat
  T̃/3 = 512h dan 2T̃/3 = 1024h: ‖q1(t+T̃/3) − q2(t)‖∞ ≤ 1e-06 dan
  ‖q1(t+2T̃/3) − q3(t)‖∞ ≤ 1e-06 (ukur 2.5e-11 + koreksi selisih-periode
  ≤ 4.3e-10 dari (c)).

- **K6 — guard integritas.** (i) determinisme: dua kampanye penuh
  menghasilkan receipt **byte-identical** dan sama dengan receipt ter-commit;
  (ii) AST-scan K1 lolos; (iii) lima mutasi gagal sebagaimana mestinya:
  - **M1** `REMAINDER_FACTOR := 10` → tabung melebar → K2 gagal **cepat**
    (abort pada checkpoint pertama yang melebihi 1e-22);
  - **M2** benih digeser +1e-03 pada kolom q1x → Newton monoton gagal
    mencapai 1e-20 (≥2 kenaikan) → K3 gagal;
  - **M3** satu byte receipt diubah → deteksi hash mismatch;
  - **M4** injeksi literal float di modul → AST-scan gagal;
  - **M5** `SWEEP_SIGNED := False` (varian reset-per-blok) → lebar tabung
    meledak di horizon → K2 gagal cepat (differentiator mekanisme inti).

---

## 5. Verdict

- **ALL PASS (K1–K6)** → registry `A-2026-0041`, sertifikat hash
  (prereg + receipt + modul + guard), klaim §1 sah.
- **FAILED** bila K1, K2, atau K3 gagal, **atau** K6 gagal (integritas:
  determinisme/AST/mutasi tidak berperilaku sebagaimana dikunci).
- **INCONCLUSIVE** bila K3 PASS tetapi K4 atau K5 gagal (keberadaan
  tercatat di laporan, tanpa registry).
- Anggaran durasi (kampanye tunggal ~est. 2–6 menit; suite ~20–30 menit
  dengan guard) adalah **catatan operasional**, bukan kriteria verdict.

---

## 6. Falsifier

Pra-registrasi ini gagal/terbantahkan bila:

1. ditemukan nilai di luar enclosure yang diklaim (mis. tabung > 1e-22
   tetapi K2 dilaporkan PASS);
2. K(B) ⊄ int(B) tetapi K3 dilaporkan PASS, atau benih/jendela diubah
   setelah commit ini;
3. receipt tidak byte-identical antar-dua-run atau beda dari commit;
4. ada float/literally-time/random di jalur tersertifikasi (AST);
5. mutasi M1–M5 tidak gagal sesuai ekspektasi §4 K6;
6. laporan/receipt memuat klaim spektrum/stabilitas, simetri antipodal,
   keunikan global, prioritas, atau klaim di luar §1;
7. modul tersegel (hash §header) berubah.

---

## 7. Artefak dan urutan eksekusi

1. Commit berkas pra-registrasi ini (hash-nya dikunci; **tidak diedit**
   setelahnya — perubahan hanya via amendemen bernomor yang ditulis sebelum
   kode, pola T1b).
2. Commit docs: `DAFTAR_MASALAH_KERJA.md` butir 16 → TREK AKTIF;
   `HANDOFF.md` seksi `## 2.0bl` (berisi ringkasan probe + deferensi T2b).
3. Implementasi `msaf/figure_eight.py` + guard
   `msaf/tests/test_figure_eight.py` (determinisme, AST, M1–M5 fail-fast).
4. Kampanye → receipt `reports/figure_eight_three_body_2026-10-22.json`
   (memuat hash prereg ini, semua ambang K1–K6, angka aktual).
5. Laporan `reports/FIGURE_EIGHT_2026-10-22.md` (bahasa Indonesia).
6. Suite penuh + `freeze.py --verify` + registry `A-2026-0041` bila ALL
   PASS (entry memuat hash prereg/receipt/modul/guard).
7. HANDOFF final + push (dijamin "silahkan lanjutkan").

---

## 8. Batas eksplisit

- Hasil T2 adalah **keberadaan lokal + keunikan lokal** orbit periodik untuk
  IVP rasional-eksak seperti didefinisikan di K1, dekat benih §2d — bukan
  identifikasi absolut dengan figure-eight bilangan-real sejati, bukan
  keunikan global, bukan eksistensi atas sistem lain.
- Stabilitas (spektrum multiplikator, Lyapunov, stabilitas nonlinear)
  **di luar** T2; hanya T2b (pra-registrasi terpisah) yang boleh mengklaim,
  setelah diverifikasi konvergen antar-metode (§2h).
- Batas T1b tetap berlaku untuk T1b: S4 tetap uji-stress tersegel, bukan
  klaim keberadaan orbit figure-eight.
- Tanpa klaim RH/PDE/chaos/ergodicity/Soliton/Evans/fisika/analytic-
  continuation/prioritas/pembuktian formal; tidak disebut "terbukti di
  Lean".
- Kode/docstring Inggris; laporan peneliti (HANDOFF/registry/daftar/laporan
  T2) bahasa Indonesia.
