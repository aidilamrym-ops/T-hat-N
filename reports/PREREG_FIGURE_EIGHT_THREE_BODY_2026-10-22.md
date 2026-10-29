# Pra-registrasi T2: orbit periodik figure-eight three-body tervalidasi (Daftar-B 16) - 2026-10-22

**Status:** scope DIKUNCI for trek T2; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis and in-commit sebelum kode T2. Hash `sha256LF`
file ini dicatat in receipt T2 and report.

**Latar:** T1b (`reports/PREREG_ODE_VALIDATED_T1B_2026-10-21.md`) already
diseal with verdict **ALL PASS** and registry `A-2026-0040`. Pemilik membuka
Daftar-B butir 16 (orbit figure-eight tervalidasi) melalui pilihan soal
("Daftar-B 16: Three-Body (Recommended)"), pola sama with T1/T1b:
ukur-dulu â†’ pra-registrasi in-commit sebelum kode â†’ implementasi â†’ seal â†’
registry hanya bila ALL PASS â†’ push. Pra-registrasi ini mengunci scope T2
**setelah** kampanye probe (pengungkapan wajib in Â§2), sebelum ada satu baris
kode pun in `msaf/figure_eight.py`.

**Paket:** Daftar-B 16. **Bukan** klaim prioritas; **bukan** klaim bahwa
data desimal-eksak ini "figure-eight which asli" dalam arti data bilangan
real sejatinya; **bukan** bukti in Lean/Coq.

**Berkas target:** `msaf/figure_eight.py` (modul bersertifikat baru),
`msaf/tests/test_figure_eight.py` (guard), kampanye â†’ receipt
`reports/figure_eight_three_body_2026-10-22.json`, report
`reports/FIGURE_EIGHT_2026-10-22.md`. Registry which direncanakan:
`A-2026-0041`, **hanya** bila verdict ALL PASS.

**Dependensi:** Python 3.14, python-flint 0.9.0 (.ball/arb), `fractions`.
Reuse **import-saja** dari modul tersegel `msaf/ode_validated.py`
(`sha256LF c1d9b5d60036a5f0772f7e3f1b8c78969efaa7146a713c762531ddce346251b9`)
and `msaf/ode_validated_block.py`
(`sha256LF 42d196a51c5ae45e3b87b8c1e36319abfeb93df776b3c2317e812f7c2c0b5b97`,
guard `f061e7ebeabfaa808280455f6d5bff595c32d9feaef164fa11d76bcbcf8aa98f`,
terpin in `A-2026-0040`). Tidak ada modul beku which diubah. Probe memakai
floating-point in **luar** jalur tersertifikasi (dibatasi Â§2 and K1).

---

## 1. Maksud and limit

T2 menyertifikasi sebagai result komputer-assisted **miliknya sendiri**:

1. **Keberadaan + keunikan lokal** orbit periodik masalah tiga-bodi planar
   Newtonian (m = G = 1) for IVP which dinyatakan **persis rasional**
   (desimal-pendekatan klasik Moore, dipotong menjadi pecahan), dekat data
   awal which diukur probe, melalui keberadaan titik tetap peta Kembali-2 in
   seksi PoincarÃ© (Krawczyk).
2. **Tabung (tube) lintasan tervalidasi** satu-periode: pembungkus keadaan
   in sepanjang horizon, termasuk pembungkus matriks monodromi
   (`âˆ‚Î¦/âˆ‚yâ‚€`, 12Ã—12) sebagai artefak for T2b.
3. **Deskriptor bentuk tervalidasi** (K5): struktur penyilangan sumbu-x badan
   3 and cacat koreografi.

Yang **no** diklaim in T2 (and no boleh muncul in report/receipt):

- **Spektrum/stabilitas Floquet** (multiplikator dekat-1) â†’ dialihkan ke
  **T2b** with alasan terukur: probe FD vs monodromy no konvergen
  (Â§2). K4 hanya menghasilkan matriks terenclosure, tanpa klaim eigen.
- Keunikan **global** (hanya lokal in kotak Krawczyk), keberadaan orbit
  lain, or identifikasi absolut with figure-eight bilangan-real sejati.
- Segala klaim in luar limit T1b: RH/PDE/chaos/ergodicity/Soliton/Evans/
  fisika/analytic-continuation/prioritas/bukti formal. Hasil S4 T1b tetap
  **bukan** klaim keberadaan orbit figure-eight (limit T1b no dicabut;
  T2 adalah lintasan klaim which terpisah with mekanisme and pra-registrasi
  sendiri).

---

## 2. Pengukuran pra-kunci (probe â€” sebelum scope dikunci)

Semua angka in bawah diukur **sebelum** file ini ditulis; angka inilah which
mengunci toleransi Â§3â€“Â§4. Probe memakai scipy DOP853 (rtol=2.3e-14, atol=1e-15,
max_step=0.005) and Jacobian syuting analitik (matriks variasional + koreksi
waktu-implisit), **in luar** jalur tersertifikasi.

**a. Data IVP tersegel (T1b `_run_s4`):** q(0) = (âˆ’1,0), (1,0), (0,0);
vâ‚ = vâ‚‚ = (347111/10â¶, 532728/10â¶); vâ‚ƒ = (âˆ’694222/10â¶, âˆ’1065456/10â¶);
Eâ‚€ = âˆ’257428899017/200000000000 = âˆ’1.287144495085; Lâ‚€ = 0; COM = 0.

**b. Orbit periodik sejati (Newton least-squares, pangkal analitik):**
residu |G|âˆž: 1.7e-6 â†’ 4.561e-14; jarak data-awal-seeded 1.089e-04
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

E(orbit) = âˆ’1.2871299154104481 (Î” = 1.458e-05 dari Eâ‚€); L(orbit) = âˆ’1.9e-12.

**c. Seksi PoincarÃ© (codim-1) â€” Î£ = {qâ‚ƒáµ§ = 0, orientasi vâ‚ƒáµ§ < 0}:**
penyilangan qâ‚ƒáµ§ on orbit sejati (periode [0, T\*]):

| waktu | qâ‚ƒx | vâ‚ƒáµ§ |
|---|---|---|
| 0 (titik awal, eksak) | 0 | âˆ’1.065450 |
| 2.108735283 | âˆ’1.0000047703 | +0.532725 |
| 3.162988113 | âˆ’4.769194074911e-05 | âˆ’0.612126 |
| 4.217376381 | +1.0000047717 | +0.532725 |
| T\* â‰ˆ 6.326003040 | 0 (kembali) | âˆ’1.065450 |

Jadi per periode ada **4 penyilangan** (2 turun = orientasi seksi: t=0 and
tâ‰ˆ3.163; 2 naik in luar orientasi), jarak antar-silang â‰¥ 3.16. Keadaan
seksi bebas-rotasi in titik kerja (qâ‚ƒx â‰  0; rotasi no mempertahankan Î£
kecuali Î¸ = kÏ€).

**d. Titik kerja (pembulatan 12 desimal â†’ benih rasional eksak):** dari
x_c2 (seksi on silang-turun 3.162988113) diperbaiki sekali step lstsq
Jacobian seksi (jarak step 9.484e-07, |F|âˆž 3.379e-11 â†’ 6.176e-12):

```
xÌ‚â‚€ = ( 0.881825885905,  0.471573247799,
       -0.881817147851, -0.471630773362,
       -0.000048006190,
       -0.557287392981,  0.306081711672,
       -0.557356449974,  0.306044779690,
        1.114643842954, -0.612126491362)
```

(koordinat seksi: q1x,q1y,q2x,q2y,q3x, v1x,v1y,v2x,v2y,v3x,v3y).

**e. Peta kembali-2:** dari x_c2: kaki-1 (silang turun berikutnya, in tâ‚ =
3.163014927), kaki-2 (tâ‚‚ = 3.162988113); tâ‚+tâ‚‚ = 6.326003040 = TÌƒ (diskalai
sebagai TÌƒ). |PÌƒÂ²(x_c2) âˆ’ x_c2|âˆž = 3.379e-11 (ganda).

**f. Kondisi Jacobian seksi DF (FD ganda â€” TIDAK andal, dipakai hanya for
estimasi):** Ïƒmax = 61.59, Ïƒmin = 1.5368e-09, cond = 4.008e+10. Lantai noise
FD â‰ˆ 5e-7 per entri (integrasi + akar) â†’ Ïƒmin **no terukur andal** in
ganda; monodromy menyiratkan |Î¼âˆ’1| terkecil ~1.5e-07. Pasangan eigen jauh
FD cocok silang with monodromy sampai 9 digit
(âˆ’0.2976Â±0.9547j, 0.9986Â±0.0529j). **Konsekuensi:** K3 bergantung on
Ïƒmin DF sesungguhnya; kasus terburuk terukur (1.5e-09) memberi margin
inclusion tipis (Â§4 K3). Bila inclusion gagal â†’ FAILED jujur, bukan cacat
pra-registrasi.

**g. Monodromy (matriks variasional benar):** 12 multiplikator â€” 4 real
{1.000001239651, 1.000000246527, 0.999999753473, 0.999998760351}, dua pasang
nyaris-1 {1Â±1.463e-7j, 1Â±1.5538e-6j}, dua pasang unit {âˆ’0.2976Â±0.9547j,
0.9986Â±0.0529j}; |detM âˆ’ 1| = 5.77e-14.

**h. Klaster nyaris-1 belum konvergen antar-metode:** FD peta kembali-2
memberi deviasi ~5e-4, monodromy ~1.2e-6 â€” keduanya bisa tercemar (noise FD
vs pengelompokan eigen dekat-1). **Maka stabilitas spektral DIKECUALI dari
T2 (â†’ T2b).**

**i. Koreografi (orbit sejati, ganda):** â€–q1(t+T/3) âˆ’ q2(t)â€–âˆž â‰¤ 2.524e-11;
â€–q1(t+2T/3) âˆ’ q3(t)â€–âˆž â‰¤ 2.687e-11 â€” koreografi **eksak** sampai noise
integrasi.

**j. Simetri antipodal setengah-periode: FALSE** â€” residu terbaik atas semua
permutasi label = 6.946e-01. Tidak ada klaim simetri (no dikunci).

**k. Kecacatan probe (diungkap, bukan dihaluskan):** matriks variasional on
probe sempat salah tanda **and** salah skala (`âˆ’K`, pembagian `dÂ²`, seharusnya
`+K`, `dÂ³`); angka monodromy lama (953, 28) **dibuang** and dihitung ulang.
Probe hanya mengukur; no ada angka probe which masuk jalur tersertifikasi
selain benih rasional Â§2d and jendela Â§3 which semuanya dinyatakan persis.

---

## 3. Formulasi which dikunci

**3.1 Sistem.** Tiga-bodi planar Newtonian, massa = 1, G = 1; tata letak
keadaan 12-dim identik T1b: y = (q1x,q1y,q2x,q2y,q3x,q3y, v1x,v1y,v2x,v2y,
v3x,v3y). Koefisien gaya diimpor dari modul tersegel (`coeffs_three_body`).

**3.2 Seksi and peta.** Î£ = {qâ‚ƒáµ§ = 0} with orientasi silang-turun
(vâ‚ƒáµ§ < 0). Koordinat seksi x âˆˆ â„Â¹Â¹ = (q1x,q1y,q2x,q2y,q3x, v1x,v1y,v2x,
v2y,v3x,v3y); embedding y = (xâ‚€,xâ‚,xâ‚‚,xâ‚ƒ, xâ‚„, 0, xâ‚…,â€¦,xâ‚â‚€); proyeksi
balik membuang qâ‚ƒáµ§. PÌƒ = kembali-silang-turun-pertama; F(x) =
Î (PÌƒÂ²(x)) âˆ’ x. Titik tetap F(x\*) = 0 â‡” orbit periodik with periode
tâ‚(x\*)+tâ‚‚(x\*).

**3.3 Jendela waktu (terkunci dari Â§2):**

- wâ‚ = [3.163014927 âˆ’ 0.01, 3.163014927 + 0.01] (silang-turun pertama),
- wâ‚‚ = [6.326003040 âˆ’ 0.01, 6.326003040 + 0.01] (silang-turun kedua).

Uji tanda tersertifikasi in ujung-ujung jendela (qâ‚ƒáµ§ bertanda ketat:
wâ‚: âˆ’/+; wâ‚‚: +/âˆ’; margin terukur 0.06 and 0.10) **and** keadaan
monoton vâ‚ƒáµ§ â‰¤ âˆ’1/2 in sepanjang kedua jendela â†’ silang unik per jendela.
Lebar pembungkus waktu-silang â‰¤ 1e-19 (bisection-berpagar on polinomial
Taylor tersertifikasi; monoton memberi limit |Î”t| â‰¤ |qâ‚ƒáµ§|/0.5).

**3.4 Grid.** TÌƒ = 6.326003040 (desimal-hingga, rasional); h := TÌƒ/1536 =
0.0041184915625 (eksak, sehingga TÌƒ/3 = 512h and 2TÌƒ/3 = 1024h bilangan
bulat â€” syarat perbandingan koreografi on Â§4 K5); N = 1554 step
(H = NÂ·h â‰¥ 6.4 â‰¥ atas-wâ‚‚); ambang-atas N dikunci, bukan knob.

**3.5 Konfigurasi.** Presisi 256-bit; orde Taylor 24; sisa (remainder) 1Ã—
nilai baku T1b; propagasi ketidakpastian **sweep bertanda lintas-blok**
(mekanisme T1b, diimpor) â€” knob `SWEEP_SIGNED = True` (mutasi M5 membalik
nilai ini tanpa mengubah nilai baku lainnya); faktor sisa `REMAINDER_FACTOR
= 1` (mutasi M1 mengubahnya).

**3.6 Mekanisme Krawczyk.** Benih: xÌ‚â‚€ Â§2d. (i) **Newton bersertifikat
presisi-256-bit, â‰¤ 6 iterasi**: tiap iterasi wajib menurunkan |F|âˆž secara
ketat; dua kenaikan berturut-turut â†’ abort K3 (status gagal jujur); berhenti
bila |F|âˆž â‰¤ 1e-20. (ii) **Satu kampanye kotak**: integrasi tervalidasi dari
kotak B = box(xÌ‚, r_B), r_B = 1e-10, in sepanjang [0, H] with propagasi
turunan S (âˆ‚Î¦/âˆ‚yâ‚€) which sama; tabung, F(xÌ‚), and DF(B) dihitung dari satu
kampanye ini (DF dari produk Jacobian step + koreksi waktu-implisit
rumus peta PoincarÃ©: âˆ‚Î¦_{t(x)}/âˆ‚x = S âˆ’ fÂ·(âˆ‡gÂ·S)/(âˆ‡gÂ·f), g = qâ‚ƒáµ§).
(iii) Å´ = invers matriks titik-tengah DF(xÌ‚) in 256-bit;
K(B) = xÌ‚ âˆ’ Å´F(xÌ‚) + (I âˆ’ Å´Â·DF(B))Â·(B âˆ’ xÌ‚); suksesi:
K(B) âŠ† box(xÌ‚, 0.9Â·r_B).

**3.7 Batas sensitivitas (diungkap):** margin inclusion bergantung on
Ïƒmin DF and L = â€–DÂ²Fâ€–: on kasus terburuk terukur (Ïƒmin = 1.5e-09)
kebutuhan â€–Å´â€–Â·LÂ·r_BÂ² + â€–Å´â€–Â·1e-20 â‰ˆ 6.7e-12Â·L + 6.7e-12 < 9e-11 menuntut
L â‰² 12; on Ïƒmin â‰¥ 1e-07 margin melompat lebar. Kegagalan â†’ FAILED jujur.

---

## 4. Kriteria lulus

- **K1 â€” data persis, tanpa float.** Semua konstanta modul rasional (benih
  12-desimal Â§2d, jendela Â§3.3, TÌƒ, h, N, r_B, ambang); AST-scan
  `msaf/figure_eight.py` tanpa literal float, `math`, `numpy`, `scipy`,
  `random`, waktu; import hanya dari modul tersegel; hash modul tersegel
  no berubah (diverifikasi suite/freeze which already ada).

- **K2 â€” integrasi tervalidasi.** Tabung keadaan â‰¤ 1e-22 in **semua**
  checkpoint in [0, H] (termasuk in dalam wâ‚ and wâ‚‚); lebar pembungkus
  waktu-silang â‰¤ 1e-19; uji tanda qâ‚ƒáµ§ in ujung jendela ketat sesuai Â§3.3;
  vâ‚ƒáµ§ â‰¤ âˆ’1/2 in kedua jendela (monotonitas tersertifikasi).

- **K3 â€” keberadaan + keunikan lokal.** Newton Â§3.6 mencapai |F|âˆž â‰¤ 1e-20
  dalam â‰¤ 6 iterasi monoton, lalu Krawczyk: K(B) âŠ† box(xÌ‚, 9e-11).
  Implikasi which diklaim: ada **tepat satu** titik tetap F in B (â†’ orbit
  periodik periode tâ‚+tâ‚‚ with tâ‚‚ âˆˆ wâ‚‚, keunikan **lokal in B saja**).

- **K4 â€” artefak monodromy.** Matriks 12Ã—12 âˆ‚Î¦/âˆ‚yâ‚€ on silang-turun kedua
  terkenclosure: lebar per entri â‰¤ 1e-16; determinan terenclosure
  (hitungan interval 256-bit) **memuat 1** (Liouville). Tanpa klaim eigen.

- **K5 â€” deskriptor bentuk.** (a) Ada silang naik qâ‚ƒáµ§ unik in
  [2.108735283 Â± 1e-6] and [4.217376381 Â± 1e-6] with vâ‚ƒáµ§ â‰¥ +1/4 in
  bracket, and qâ‚ƒx in silang masing-masing âˆˆ [âˆ’1.00001, âˆ’0.99999] and
  [0.99999, 1.00001]; (b) silang in wâ‚: qâ‚ƒx âˆˆ [âˆ’6e-05, âˆ’3e-05]; silang in
  wâ‚‚: qâ‚ƒx âˆˆ [âˆ’1e-06, +1e-06]; (c) selisih periode |TÌƒ âˆ’ (tâ‚+tâ‚‚)(xÌ‚)| â‰¤ 1e-09;
  (d) cacat koreografi on **semua** checkpoint kisi with jarak tepat
  TÌƒ/3 = 512h and 2TÌƒ/3 = 1024h: â€–q1(t+TÌƒ/3) âˆ’ q2(t)â€–âˆž â‰¤ 1e-06 and
  â€–q1(t+2TÌƒ/3) âˆ’ q3(t)â€–âˆž â‰¤ 1e-06 (ukur 2.5e-11 + koreksi selisih-periode
  â‰¤ 4.3e-10 dari (c)).

- **K6 â€” guard integritas.** (i) determinisme: dua kampanye penuh
  menghasilkan receipt **byte-identical** and sama with receipt ter-commit;
  (ii) AST-scan K1 lolos; (iii) lima mutasi gagal sebagaimana mestinya:
  - **M1** `REMAINDER_FACTOR := 10` â†’ tabung melebar â†’ K2 gagal **cepat**
    (abort on checkpoint pertama which melebihi 1e-22);
  - **M2** benih digeser +1e-03 on kolom q1x â†’ Newton monoton gagal
    mencapai 1e-20 (â‰¥2 kenaikan) â†’ K3 gagal;
  - **M3** satu byte receipt diubah â†’ deteksi hash mismatch;
  - **M4** injeksi literal float in modul â†’ AST-scan gagal;
  - **M5** `SWEEP_SIGNED := False` (varian reset-per-blok) â†’ lebar tabung
    meledak in horizon â†’ K2 gagal cepat (differentiator mekanisme inti).

---

## 5. Verdict

- **ALL PASS (K1â€“K6)** â†’ registry `A-2026-0041`, sertifikat hash
  (prereg + receipt + modul + guard), klaim Â§1 sah.
- **FAILED** bila K1, K2, or K3 gagal, **or** K6 gagal (integritas:
  determinisme/AST/mutasi no berperilaku sebagaimana dikunci).
- **INCONCLUSIVE** bila K3 PASS tetapi K4 or K5 gagal (keberadaan
  tercatat in report, tanpa registry).
- Anggaran durasi (kampanye tunggal ~est. 2â€“6 menit; suite ~20â€“30 menit
  with guard) adalah **note operasional**, bukan kriteria verdict.

---

## 6. Falsifier

Pra-registrasi ini gagal/terbantahkan bila:

1. ditemukan nilai in luar enclosure which diklaim (mis. tabung > 1e-22
   tetapi K2 dilaporkan PASS);
2. K(B) âŠ„ int(B) tetapi K3 dilaporkan PASS, or benih/jendela diubah
   setelah commit ini;
3. receipt no byte-identical antar-dua-run or beda dari commit;
4. ada float/literally-time/random in jalur tersertifikasi (AST);
5. mutasi M1â€“M5 no gagal sesuai ekspektasi Â§4 K6;
6. report/receipt memuat klaim spektrum/stabilitas, simetri antipodal,
   keunikan global, prioritas, or klaim in luar Â§1;
7. modul tersegel (hash Â§header) berubah.

---

## 7. Artefak and urutan eksekusi

1. Commit file pra-registrasi ini (hash-nya dikunci; **no diedit**
   setelahnya â€” perubahan hanya via amendemen bernomor which ditulis sebelum
   kode, pola T1b).
2. Commit docs: `DAFTAR_MASALAH_KERJA.md` butir 16 â†’ TREK AKTIF;
   `HANDOFF.md` seksi `## 2.0bl` (berisi ringkasan probe + deferensi T2b).
3. Implementasi `msaf/figure_eight.py` + guard
   `msaf/tests/test_figure_eight.py` (determinisme, AST, M1â€“M5 fail-fast).
4. Kampanye â†’ receipt `reports/figure_eight_three_body_2026-10-22.json`
   (memuat hash prereg ini, semua ambang K1â€“K6, angka aktual).
5. Laporan `reports/FIGURE_EIGHT_2026-10-22.md` (bahasa Indonesia).
6. Suite penuh + `freeze.py --verify` + registry `A-2026-0041` bila ALL
   PASS (entry memuat hash prereg/receipt/modul/guard).
7. HANDOFF final + push (dijamin "silahkan lanjutkan").

---

## 8. Batas eksplisit

- Hasil T2 adalah **keberadaan lokal + keunikan lokal** orbit periodik for
  IVP rasional-eksak seperti didefinisikan in K1, dekat benih Â§2d â€” bukan
  identifikasi absolut with figure-eight bilangan-real sejati, bukan
  keunikan global, bukan eksistensi atas sistem lain.
- Stabilitas (spektrum multiplikator, Lyapunov, stabilitas nonlinear)
  **in luar** T2; hanya T2b (pra-registrasi terpisah) which boleh mengklaim,
  setelah diverifikasi konvergen antar-metode (Â§2h).
- Batas T1b tetap berlaku for T1b: S4 tetap uji-stress tersegel, bukan
  klaim keberadaan orbit figure-eight.
- Tanpa klaim RH/PDE/chaos/ergodicity/Soliton/Evans/fisika/analytic-
  continuation/prioritas/pembuktian formal; no disebut "terbukti in
  Lean".
- Kode/docstring Inggris; report peneliti (HANDOFF/registry/daftar/report
  T2) bahasa Indonesia.

---

## 9. Amendemen #1 (ditulis SEBELUM ada kode; hash file ini terkunci on commit amendemen)

Diungkap jujur: analisis kelayakan mekanisme Krawczyk (masih pra-kode,
belum ada satu baris pun implementasi) menemukan tiga hal which menuntut
perubahan angka/mutasi in bawah. Tidak ada ambang kriteria K1-K6 which
dilonggarkan; semua perubahan MEMPERKETAT kotak/mutasi or membetulkan
gerbang mutasi which terbukti vakum. Angka probe Â§2, jendela, grid, TÌƒ,
K2, K4, K5 no berubah.

**9.1 Alasan (dependensi waktu-silang).** Pada kampanye kotak, waktu
silang tâ‚‚(x) for x âˆˆ B menyebar |dtâ‚‚/dx|Â·r_B â‰ˆ 10.5Â·r_B (turunan
implisit, terkunci Â§3.3-Â§3.6). Membungkus S on rentang waktu selebar
ini menambah lebarDF(B) ~ AÂ·r_B with A â‰ˆ 1e3-1e4 (faktor ketergantungan;
melebihi variasi sah â€–DÂ²Fâ€–Â·r_B ~ 10Â·r_B sebesar ~100Ã—). Syarat kontraksi
â€–Å´â€–Â·AÂ·r_B < 0.9 on kasus terburuk terukur Ïƒ_min = 1.5368e-09 menuntut
r_B < ~2.5e-13, bukan 1e-10.

**9.2 Perubahan angka terkunci:**

- r_B: 1e-10 â†’ **2e-13**; ambang suksesi K3 tetap K(B) âŠ† box(xÌ‚, 0.9Â·r_B)
  (kini 1.8e-13).
- Target Newton Â§3.6: |F|âˆž â‰¤ 1e-20 â†’ **|F|âˆž â‰¤ 1e-22** (masih â‰¤ target lama;
  lebar aktual tabung titik diperkirakan ~1e-76 - rems Taylor ~ h^25/25! -
  sehingga target 1e-22 punya kepala-ruang ~54 pesanan; sekaligus membatasi
  â€–xÌ‚ âˆ’ x*â€– â‰¤ Ï„_F/Ïƒ_min â‰¤ 6.7e-14 < r_B on kasus terburuk).
- Setiap iterasi Newton (termasuk xÌ‚ final) dibulatkan ke **25 desimal**
  (rasional eksak, K1); pembulatan â‰¤ 5e-26 no material.
- Sensitivitas Â§3.7 kini: total suksesi (kasus terburuk Ïƒ_min = 1.5e-09)
  â‰ˆ â€–Å´â€–Â·(Ï„_F + F-rad) + â€–Å´â€–Â·AÂ·r_BÂ² â‰ˆ 6.7e-14 + AÂ·2.7e-13Â·(A/1e3); with
  A ~ 1e3 muat in 1.8e-13 (margin ~1.2Ã—); on Ïƒ_min â‰¥ 1e-08 semua margin
  â‰¥ 5Ã—. Bila Ïƒ_min sesungguhnya â‰ª 1e-08 or A â‰« 1e4 â†’ inclusion gagal â†’
  **FAILED jujur** (falsifier Â§6 butir 2 tetap berlaku).

**9.3 Gerbang mutasi (M1, M5) dibetulkan sebelum vakum terbukti:**

- Lebar aktual tabung ~1e-76 berada ~50 pesanan in bawah ambang K2
  (1e-22) and K4 (1e-16); oleh itu:
- **M1 (diubah):** `REMAINDER_FACTOR := 1e70` (sebelumnya 10): faktor 10
  terbukti tak terdeteksi (lebar tetap ~1e-75 â‰ª 1e-22 - gerbang vakum);
  faktor 1e70 mendorong rem ~1e-14 â†’ tabung > 1e-22 on checkpoint
  pertama â†’ K2 gagal **cepat** (abort on checkpoint pertama which
  melebihi ambang, tetap sesuai semangat Â§4/M1).
- **M5 (gerbang diperbaiki):** `SWEEP_SIGNED := False` (reset-per-blok)
  menggembungkan c_out/S ~8.7e7Ã— per periode (ukuran T1b Â§2.3); on
  checkpoint titik lebar tetap in bawah ambang K2 (vakum in sana), tetapi
  on **kampanye kotak** DF(B) meledak sehingga K(B) âŠ„ box(xÌ‚, 0.9Â·r_B) â†’
  **K3 gagal** (bukan K2 seperti Â§4 semula). Ekspektasi kegagalan and
  sifat fail-early-nya (K3 gagal on akhir kampanye kotak) dikunci in sini.

**9.4 Mekanisme tambahan which dikunci (implementasi wajib mengikuti):**

- Tabung on waktu sembarang t in dalam step k: polinomial Taylor
  step-k dari titik-tengah tersimpan + perpanjangan suara dari
  checkpoint blok terakhir (|J|Â·c + rem + quad) + Jacobian parsial on Ï„
  (bentuk nilai-rata-rata, sama seperti `forward_step`); for uji tanda
  pembuangan-bisection, radius boleh dibatasi kasar â€–J_Ï„â€–âˆž â‰¤ 2 with
  justifikasi jarak-pasir-badan bersertifikat â‰¥ 1/2 in seluruh horizon
  (verifikasi internal, bukan kriteria).
- Pembungkus waktu-silang: bisection-berpagar on polinomial tersertifikasi
  hingga lantai radius tabung q3y tercapai; lebar aktual diperkirakan
  ~1e-75 (ambang K2 â‰¤ 1e-19 tetap berlaku sebagai limit-atas).
- F(xÌ‚) and Å´ berasal dari **kampanye titik (point-run) Newton terakhir**
  (tabung tajam); kampanye kotak menyumbang DF(B) and konfirmasi tabung;
  K5 dibaca dari kampanye titik final.
- Iterasi Newton memakai inversi matriks titik-tengah DF(x) in 256-bit
  (`arb_mat`); aturan monoton (Â§3.6) tetap berlaku.

- **Amendemen #2 (masih sebelum kode):** dua kekeliruan pencatatan probe
  in Â§3.3 dibetulkan tanpa mengubah gerbang kriteria: (a) silang-**turun**
  (v3y < 0) berarti q3y **lo > 0 and hi < 0** for KEDUA jendela â€” pola
  tertulis "wâ‚: âˆ’/+" adalah kebalikan; kini keduanya "+/âˆ’"; (b) margin
  terukur on jendela terkunci (setengah-lebar 0.01) adalah **0.0061
  (wâ‚) and 0.0107 (wâ‚‚)** â€” angka "0.06/0.10" tercatat milik hipotesis
  jendela Â±0.1 which no jadi terkunci. Gerbang K2 tetap: perubahan tanda
  ketat in kedua ujung + monotonitas v3y â‰¤ âˆ’1/2 (no berubah).
  Dibuka sebagai kesalahan pencatatan, pola kejujuran which sama with
  kecacatan probe variational Â§2k.

Amendemen berikutnya hanya boleh ditulis sebelum kode modul
`msaf/figure_eight.py`; setelah modul ditulis, scope terkunci penuh
(pola T1b: tanpa perubahan ambang pasca-kode).


