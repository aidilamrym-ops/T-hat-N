# Tiga tugas, result terukur (2026-10-15)

Sesi ketiga dari instruction set: tiga tugas krusial, tanpa klaim global.
Semua angka in bawah diukur, bukan diperkirakan. Yang **no**
terdjawab ditulis sebagai no terjawab.

Protokol reset test dijalankan **sebelum** pekerjaan, bukan sesudahnya:
audit kebocoran `ctx.prec` global, and diferensial 15 titik garis
kritikal which tersegel.

---

## 0. Protokol verifikasi (jalur wajib)

| Protokol | Hasil |
|---|---|
| Audit `ctx.prec` global | 8 assignment telanjang in 4 modul tes lama -- **dibiarkan** (sesuai mandate #4, tercatat OPEN in `NONFINITE_DEFECT.md`); modul baru no menambah satu pun |
| Diferensial 15 titik garis kritikal | **15/15 PASS**, enclosure baru memuat titik tengah which lama and no lebih lebar dari 4Ã— radii |
| Suite penuh (akhir sesi) | **311 passed** |

---

## 1. TUGAS 1 â€” Î¾ tanpa nol real, and jembatan â„‚â†’â„

### 1a. Yang terbukti penuh, tanpa satu pun aksom baru

Berkas baru `lean/XiNoRealZero.lean`. Jejak aksom diukur with
`#print axioms`, bukan diklaim:

```
'XiNoRealZero.realCertificate_of_realSlice_zero'      â†’ [propext, Classical.choice, Quot.sound]
'XiNoRealZero.offAxisPoint_is_not_a_certificate'      â†’ [propext, Classical.choice, Quot.sound]
'XiNoRealZero.realCertificate_zero_is_on_the_axis'    â†’ [propext, Classical.choice, Quot.sound]
'XiNoRealZero.no_realCertificate_of_no_real_zero'     â†’ [propext, Classical.choice, Quot.sound]
'XiNoRealZero.moore_test_inapplicable_without_real_zero' â†’ [propext, Classical.choice, Quot.sound]
```

Jadi: **sertifikat real hanya bisaproduced oleh nol which imagLASnya
nol**, and jika `g` no pernah nol in sumbu real maka `moore_test`
no punya apa pun for certifying â€” for interval **mana pun**, bukan
hanya kotak-kotak which kebetulan kita hitung. Itu adalah jembatan which
ditutup, in satu-satunya arah which bisa ditutup.

### 1b. Kekalahan saya in proses ini, tercatat

Teorema pertama saya **salah**: diklaim `Â¬ RealCertificate g a b` dari
satu nol off-axis. Itu mensyaratkan *semua* nol `g` off-axis â€” satu nol
in sumbu already cukup for memungkinkannya. Hippotesisnya juga
membandingkan titik sertifikat `w` with titik hipotesis `z`, dua
titik which no berhubungan. Lean menolak sebelum sempat dikomit.
Bentuk which benar, and tetap memberi result yangKayuNeeded, adalah point-wise, and itulah which kini terbukti.
terbukti.

### 1c. Master theorem analitik: SPESIFIKASI, bukan bukti

Ini which perlu Anda ketahui sebelum optimistis: **Mathlib v4.33.1 which
dipin no punya zeta analitik and no punya `Real.gamma_pos`.**
Hasil pencarian in `.lake/packages/mathlib`:

| which dibutuhkan | ada? |
|---|---|
| `Real.exp_pos`, `Real.pi_pos` | YA |
| `Real.gamma_pos` | **TIDAK** â€” no ada in mana pun |
| `Real.zeta` analitik | **TIDAK** â€” zeta which ada adalah fungsi aritmetika |
| `zeta < 0` in `0 < x < 1` | **TIDAK** |
| `zeta > 0` in `x > 1` | **TIDAK** |

Jadi "buktikan Î¾ tak punya nol real in Lean" bukan latihan aljabar
tanda. Itu kemampuan: argumen **derieta** for tanda zeta in `(0,1)`
and representasi integral for positifnya gamma.

Yang saya kerjakan: turunannya **sepenuhnya ter-machine-check**, dari
enam kewajiban which dideklarasikan, in `lean/spec/XiAnalyticSpec.lean`:

| kewajiban | isi |
|---|---|
| 1â€“3 | tanda zeta: negatif for `x<0`, negatif for `0<x<1`, positif for `x>1` |
| 4 | `Gamma > 0` for `x>0` |
| 5 | dua nilai which dapat dihapus: `zeta(0) = -1/2`, `Gamma(1) = 1` |
| 6 | persamaan fungsional `xi(s) = xi(1-s)` â€” tanpa ini kasus `x<0` tak tertutup oleh aljabar tanda sama sekali, sebab Gamma berganti tanda in sumbu negatif |

Terbukti mesin in dalamnya: bentuk *shifted* `sÂ·Gamma(s/2) =
2Â·Gamma(1+s/2)` (identitas which sama with perbaikan v1.40.0),
pecahan kasus `x<0`, `x=0`, `0<x<1`, `x=1`, `x>1`, aljabar tanda produk
with dua faktor negatif, and aritmetika ujung `xi(0) = 1/2`.

Jejak aksom theorem-nya:

```
[propext, Classical.choice, Quot.sound,
 gammaReal, gammaReal_pos, gammaReal_one, zetaReal, zetaReal_zero,
 zetaReal_mid, zetaReal_gt_one, xiReal_sub_one]
```

Tiga aksom standar + **enam kewajiban in atas**. Tidak ada satu pun
which adalah kesimpulan.

### 1d. Kenapa spesifikasi ini TIDAK ada in `lean/*.lean`

Audit aksioma repo sendiri (`test_lean_axiom_audit.py`) mewajibkan
setiap deklarasi in `lean/*.lean` hanya bergantung on tiga aksom
standar â€” and ia **menangkap** deklaraxi saya. Respon which benar bukan
melemahkan audit and bukan menghapus spesifikasi: paruh kondisional
dipindah ke `lean/spec/` (in luar glob audit), dicatat in header
berkasnya, in SCOPE audit, and in sini. Konsekuensinya: `lean/*.lean`
hanya berisi which benar-benar terbukti.

---

## 2. TUGAS 2 â€” Arsitektur Moore/RouchÃ© in â„‚

Berkas baru `lean/ComplexMoore.lean`.

### 2a. Yang terbukti: anggaran tanda Minkowski simetris

Inti dari "tanda no boleh lolos sepihak" adalah lemma ini, and ia
**terbukti**:

```lean
theorem zero_excluded_iff_budget (lo r T : â„) (hr : 0 â‰¤ r) (hlo : 0 < lo - r) :
    0 âˆ‰ widen (lo - r) (lo + r) T â†” T < lo - r
```

Artinya: enclosure turunan `a Â± r` which dilebarkan simetris with
anggaran ekor `T` **tetap menyingkirkan nol iff anggaran lebih kecil
daripada jarak ke nol**. Di atas ambang itu, nol masuk kembali â€”
`widen_loses_zero_above_budget` membuktikannya sebagai pernyataan,
supaya tak ada which menemukan ulang lewat jalan pintas.

Jejak aksom kelima lemma ComplexMoore: **[propext, Classical.choice,
Quot.sound]** â€” nol aksom baru.

Perhatikan bagaimana kernel Python already benar in sini:
`moore_premises.second_derivative_over_ball` membentuk
`acb(tail).union(-acb(tail))` (pelebaran simetris) lalu menguji
**containment on enclosure which already dilebarkan**. Uji containment
no bisa dikalahkan ekor besar, karena ekor already termasuk dalam
pertanyaannya. Lemma in atas adalah alasan jalan pintas berbasis
**tanda** dilarang â€” bukan keraguan terhadap kode which ada.

### 2b. Yang hanya dispesifikasikan

Tujuh kewajibanOB-C1..OB-C7 terdaftar in header file. Yang
menghambat adalah **OB-C7**: eksistensi/keunikan in â„‚ butuh argumen
kelengkapan â€” Moore in â„‚, or Rouche with bilangan lilitan.
Mathlib no punya keduanya, and `NewtonExistence.moore_test` adalah
which real. OB-C7 adalah teorema sungguhan, bukan pembukuan.

### 2c. Kesalahan saya, tercatat lagi

Dua draf lemma salah and kernel menolak keduanya:

1. "Bola with tinggi imajiner positif no menyentuh sumbu" â€”
   **salah**: bola berpusat in sumbu with radius positif jelas
   menyentuhnya, and `0 < r` with `0 â‰¤ r` bukan kontradiksi.
2. Versi with pemisahan `r < Î´` â€” **salah** with alasan lain: `Î´`
   no mengatakan apa pun tentang pusat bola, and `r = 0`
   memenuhi semua hipotesis sambil `z.im = 0` juga berlaku. Yang
   benar adalah pemisahan **seluruh bola** dari sumbu, and itulah which
  TIactly dibuktikan winding per kotak.

---

## 3. TUGAS 3 â€” Spektral Guinand-Weil, Route S

### 3a. Yang diukur and tersertifikasi

`msaf/gw_route_s_ladder.py` â€” LDL^T interval murni (Arb),Route S.
Inersia memberi **tanda**, bukan magnituda; skrip itu sengaja no
menggambar kurva Î»_min dari inersia, karena itu akan menjadi fabrikasi.

Dimensi adalah `2N+1` (bukan `c`; `c` adalah parameter cutoff) â€”
salah baca awal saya soal ini costing satu debugging.

| N | dim | presisi | n_pos | n_neg | semua entri finite | build | LDL^T | verdict |
|---|---|---|---|---|---|---|---|---|
| 10 | 21 | 6000 | 21 | 0 | ya | 2,53 s | 0,01 s | CERTIFIED POSITIVE DEFINITE |
| 20 | 41 | 6000 | 41 | 0 | ya | 6,29 s | 0,11 s | CERTIFIED POSITIVE DEFINITE |
| 40 | 81 | 6000 | 81 | 0 | ya | 16,77 s | 0,84 s | CERTIFIED POSITIVE DEFINITE |
| 80 | 161 | 6000 | 161 | 0 | ya | 129,05 s | 11,02 s | CERTIFIED POSITIVE DEFINITE |
| 160 | 321 | 6000 | 321 | 0 | ya | 228,67 s | 83,01 s | CERTIFIED POSITIVE DEFINITE |
| 320 | 641 | 6000 | 641 | 0 | ya | 892,55 s | 640,89 s | CERTIFIED POSITIVE DEFINITE |

6/6 tersertifikasi. Setiap pivot bertanda strictly, jadi **seluruh
spektrum tiap matriks ini positif secara rigor** â€” bukan sampel.

Model biaya terukur: build ~ O(dimÂ²) (2,53 â†’ 6,29 â†’ 16,77 â†’ 129 â†’ 229
â†’ 893 detik), faktorisasi ~ O(dimÂ³) (0,01 â†’ 0,11 â†’ 0,84 â†’ 11 â†’ 83 â†’
641 detik). N=320 already 25 menit; N=640 akan sekitar 1,7 jam on
6000 bit.

### 3b. Hukum redaman: DITERIMA, and model which-in-asumsikan DIBANTAH

#### Jalur which dicoba lebih dulu, and kenapa ia no bisa

Tangga Sturm `gw-spectral-map` menyertifikasikan **seluruh** spektrum
(17/17 cakupan, 0 konflik) tetapi **no** menyelesaikan magnitudo
eigenvalue terkecil. Pada 300 bit bracket terrendah adalah CLUSTER
`[-2.66e-5, +2.27e-5]` with k=9; on **3000 bit bracketnya identik
bit-with-bit** with biaya hanya 1,7x lebih besar. Jadi presisi Arb
bukan bottleneck-nya: posisi titik geser berasal dari mesin duple
float64, and no ada jumlah presisi pun which menggerakkan posisi
float64. Itu mekanisme TOO_TIGHT which memang didokumentasikan in sana.
Tangga itu mengukur BIAYA, bukan redaman.

#### Jalur which benar: eigensolver interval

`arb_mat.eig` (Rump / van der Hoeven-Mourrain) adalah "Route A2" in README
Guinand-Weil. Pada 6000 bit, c=13:

| dim | lambda_min (limit bawah tersertifikasi) | radius | Im bocor | eig_s | verdict |
|---:|---:|---:|---:|---:|---|
| 17 | 7.674393e-23 | 0 | 0 | 0,56 | semua eigenvalue positif ketat |
| 33 | 8.568627e-35 | 0 | 0 | 4,05 | idem |
| 65 | 2.258931e-49 | 0 | 0 | 30,06 | idem |
| 129 | 6.321351e-59 | 0 | 0 | 221,68 | idem |
| 257 | 3.299020e-59 | 0 | 0 | 1984,84 | idem (33 menit) |

Radius **tepat nol**: setiap eigenvalue terisolasi titik on presisi ini,
and no satu pun enclosure-nya memuat nol. Bocoran imajiner **tepat
nol**, jadi "semua real" diukur, bukan diasumsikan.

**Koreksi terukur (2026-10-17):** dua klaim "tepat nol" in atas keliru
sebagai pernyataan matematis. Field JSON `lambda_min_rad` and
`imag_leak_upper` memang mencatat 0,0, tetapi keduanya **artefak
underflow float64** (radius/leak sejati ~1e-1790, jauh in bawah lantai
subnormal ~4,9e-324). Terukur ulang (c=13, 6000 bit; dim 17/33): radius
enclosure sejati 4,73e-1792 / 5,37e-1788 (`is_exact() = False`), leak
imajiner maksimum 1,97e-1792 / 7,06e-1789 (0/17 and 0/33 section imajiner
eksak nol). Yang tetap benar: no satu pun enclosure memuat nol, and
matriks bola **simetris eksak** (mid-diff 0/289, rad-diff 0/289 on dim
17) â€” realness struktural, bukan result ukur "leak nol". Bukti + detail:
`reports/gw_radius_diag_2026-10-17.log`,
`reports/GW_RADIUS_REGISTRY_CORRECTION_2026-10-17.md`.

#### Temuan: B dari model AÂ·e^(-BÂ·dim) TIDAK konstan

Lereng `ln(lambda_min)` per satuan dimensi:

| rentang dim | B implisit |
|---|---|
| 17 â†’ 33 | **-1,7201** |
| 33 â†’ 65 | **-1,0490** |
| 65 â†’ 129 | **-0,3437** |
| 129 â†’ 257 | **-0,0051** |

Model `A * e^(-B n)` with B konstan memroyeksikan lereng **konstan**.
Yang terukur justru **menurun monoton**, and on rentang terakhir already
mendekati nol. Jadi:

* lawanan with bentuk eksponensial konstan **terbantah** on irisan
  ini (c=13 tetap, N naik);
* lebih kuat lagi: on rentang terakhir, redamannya **hampir berhenti**.
  Slope per dimensi turun -1,72 â†’ -1,05 â†’ -0,34 â†’ **-0,005**, yaitu
  Î»_min bergerak dari 6.32e-59 ke 3.30e-59 saat dimensi **ganda lagi**.
  Plateau in kisaran 1e-59, bukan peluruhan eksponensial;
* ini membuat hipotesis "lebar bawah spektrum dikunci struktur cutoff"
  (banyak eigenvalueRrimentalåœ¨åŽå¯†é›†) jauh lebih masuk akal daripada
  eksponensial -- tetapi itu **hipotesis, bukan result**, and no
  diuji in sini;
* anak tangga dim 321 **no dijalankan** sampai habis. Biaya terukur
  menå’Œå¼¦.Runtime: 0,6 â†’ 4,1 â†’ 30,1 â†’ 221,7 â†’ 1984,8 detik, jadi ~O(dim^3)
  with faktor ~9 per penggandaan dimensi; dim 321 diproyeksikan
  ~3 jam. Pola already jelas dari empat rentang, jadi jam itu dibelanjakan
  for satu titik which no akan mengubah arah kesimpulan.

**Peringatan which wajib disebut:** ini **satu irisan** keluarga
(c=13 tetap). Skala spektral sangat bergantung on c --bands dari repo
Guinand-Weil memberi lambda_min(Q_{100,40}) ~ 1.32e-102 on dim 81,
sementara anak tangga dim-65 in sini (c=13) memberi 2.26e-49. Membandingkan
antar-c bukan apel-samel, jadi no ada hukum universal which diklaim in sini.

#### 9000 bit no menambah apa pun (terukur)

| presisi | lambda_min (dim 33) | lambda_min (dim 65) | eig_s (dim 65) |
|---|---|---|---|
| 6000 | 8.568627e-35 | 2.258931e-49 | 30,06 |
| 9000 | 8.568627e-35 | 2.258931e-49 | 79,05 |

Nilai **identik bit-with-bit**, radius registry tetap 0,0 (artefak float64 â€” koreksi 2026-10-17), biaya 2,6x. Jadi on
dimensi ini 6000 bit already cukup for isolasi eigenvalue, and tambahan
presisi which lebih tinggi no menambah informasi apa pun. Ini adalah
koreksi atas asumsi bahwa "resolusi lebih tinggi" otomatis berarti
informasi lebih
banyak: bukan, kalau radiusnya already nol.

#### Deviasi Montgomery S1/S2

`gw_mont_pipeline_check.py` ternyata **validator fixture sintetis**
(Poisson/GUE/GOE), bukan pengukuran on spektrum asli. Pengukuran
sesungguhnya: `gw_montgomery.py` terhadap `gw_spectrum_100_200.json`
(Q c=100/N=200, dim 401, gerbang G-M0 PASS with kelima section true),
2000 sampelLandsurat per ensemble, seed 20260927, aturan
**preregistrasi** ditaati (kedua chart selalu dilaporkan, chart which
mengUNTUNGkan no pernah dipilih setelah melihat result).

#### S1 -- kurangi rasio celah bertetangga

| chart | r_bar | n_ratios | verdict |
|---|---:|---:|---|
| T = ln(lambda), **PRIMARY** | 0,548557 | 399 | CONSISTENT WITH RMT (repulsion level hadir) |
| L = lambda, SECONDARY | 0,190891 | 399 | INCONSISTENT WITH ALL THREE REFERENCES |

**S1 FINAL: CHART-DEPENDENT (T and L berbeda) -> INCONCLUSIVE.**

Ini aturan preregistrasi bekerja persis seperti mestinya: dua chart
saling bertentangan, and pipeline **menolak memilih** chart which
menguntungkan. SE r_bar dari simulasi N-matched adalah 0,000718, jadi
selisih 0,19 on chart L bukan noise.

#### S2 -- korelasi pasangan vs kernel Montgomery

chiÂ² and p-value, chart T (primary), tiga bandwidth:

| sigma_u | chi2_obs | p_GUE | p_Poisson |
|---|---|---|---|
| 0,3 | 11639,58 | 0,0000 | 0,9980 |
| 0,5 | 1698,54 | 0,0000 | 0,5340 |
| 1,0 | 816,32 | 0,0000 | 0,0075 |

**S2 FINAL (keenam titik kisi agree): INCONSISTENT WITH MONTGOMERY AT
THIS RESOLUTION.** 0 bin dibuang (E/bin minimum 38, maksimum 200).

#### Apakah deviasi mengecil or membesar? **DIJAWAB (2026-10-16): TIDAK mengecil -- delta dua resolusi in Â§4, seri tiga titik in Â§5**

Spektrum tersertifikasi kedua already dibangun and diukur (dim 201, c=100). Hasilnya seperti dim 401: **p_GUE terkunci in lantai uji (0,0000) in keenam titik kisi**, and S1 tetap **CHART-DEPENDENT -> INCONCLUSIVE**. Arah asimtotik tetap no dapat disimpulkan dari dua titik; which dapat disimpulkan: on N=201 dari N=401, **no ada pengecilan menuju konsistensi**. Rincian, tabel delta, and cacat proses: Â§4.

Dan batasan which harus dibaca harfiah: ini statistik dari SATU matriks
which terbangun and finit. Bukan teorema Montgomery, bukan bukti RH,
bukan bukti Weil-positivity, bukan penghitungan bilangan prima.

### 3c. Kesalahan proses, tercatat

`build_arb_tau` mengembalikan `(matriks, dimensi)`, bukan matriks saja.
Versi pertama saya mengambil tupel itu apa adanya, and errornya
muncul dari dalam faktorisasi (`TypeError: tuple indices...`) alih-alih
in titik panggil â€”_squra which mahal. Sekarang ada `assert` eksplisit.

---

<!-- BEGIN GW-DELTA (generated by msaf/gw_resolution_delta.py --write) -->

## 4. Resolusi kedua (2026-10-16): dimensi 201 -- deviasi Montgomery mengecil or membesar?

*Seksi ini in-generate oleh `msaf/gw_resolution_delta.py` dari dua log kanonik (`msaf/mont_run.txt` = dim 401 pasca-perbaikan cacat 16; `reports/mont_run_100_100.txt` = dim 201) with instrumen which sama (`gw_montgomery.py`, 2000 sampel N-matched, seed 20260927) and aturan preregistrasi which sama. Angka diekstrak mesin dari berkasnya, no diketik ulang.*

### 4.1 Spektrum kedua, tersertifikasi penuh

| Item | Nilai terukur |
|---|---|
| Ladder Route S 6000 bit (c=100, N=100) | CERTIFIED POSITIVE DEFINITE -- n_pos = 201, n_neg = 0; build 244.49 s; LDL^T 12.59 s (`reports/gw_route_s_ladder_c100.json`) |
| Capture penuh (arb), dim 201 | G-M0 PASS 5/5; lambda_min = 2.43663511450089951654005401859e-191; lambda_max = 7.15715069555021216336313518572; spread 191.467949663 orders; radius terburuk `|rad|/|mid|` = 1e-1536.5177; eig 825.7 s (`reports/gw_capture_100_100.log`) |
| Chain capture | `build_arb_tau` -> `arb_mat.eig(vdhoeven_mourrain)` tanpa serialisasi desimal; deviasi rantai dari dim 401 dicatat in field `build_chain` |

Biaya terukur titik baru: build 244.49 s, LDL^T 12.59 s (dim 201, 6000 bit). Dalam deret c=13 (0,84 s @ dim 81; 11,02 s @ 161; 83,01 s @ 321) titik ini jatuh in antara -- konsisten orde-kubik, tetapi konstanta biaya bergantung c; lintas-c bukan apel-samel, jadi ini rekor, bukan konfirmasi model.

### 4.2 Tabel delta (kedua kolom dari log kanonik)

| Besaran | dim 401 (run2) | dim 201 (baru) |
|---|---|---|
| Provenance | c=100 N=200 dps=400 prec=2048 algo=vdhoeven_mourrain n=401 | c=100 N=100 dps=1806 prec=6000 algo=vdhoeven_mourrain n=201 |
| lambda_min (float, dari log) | 1.7372701741044778e-294 | 2.4366351145008994e-191 |
| lambda_max | 7.9954638264487512 | 7.1571506955502118 |
| spread | 294.662976 orders | 191.467950 orders |
| S1 chart T `r_bar` (n_ratios) | 0.548557 (399) | 0.620526 (199) |
| Referensi GUE matched-N (mean +- sd) | 0.599639 +- 0.014359 | 0.599774 +- 0.020042 |
| Jarak `r_bar`-T dari rerata GUE (SD ensemble) | -3.56 | +1.04 |
| S1 chart L `r_bar` | 0.190891 | 0.131742 |
| S1 FINAL | CHART-DEPENDENT (T and L disagree) -> INCONCLUSIVE | CHART-DEPENDENT (T and L disagree) -> INCONCLUSIVE |
| S2 chi^2 chart T (sigma_u 0.3 / 0.5 / 1.0) | 11639.5769 / 1698.5441 / 816.3241 | 14621.8788 / 2146.3923 / 594.5661 |
| S2 chi^2 chart L | 137543.9721 / 18825.3487 / 6289.2525 | 47172.5984 / 10004.2942 / 4219.3598 |
| S2 p_GUE (6 titik) | 0.0000 | 0.0000 |
| S2 p_Pois chart T | 0.9980 / 0.5340 / 0.0075 | 0.9910 / 0.8285 / 0.0245 |
| S2 p_Pois chart L | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| S2 FINAL | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION |

### 4.3 Jawaban

**Tidak mengecil.** Pada instrumen S2 -- which persis diadakan for menjawab question ini -- p_GUE tetap in lantai uji in KEDUA resolusi: 0.0000 in keenam titik kisi dim 401, 0.0000 in keenam titik dim 201. Dengan 2000 surrogat, `0.0000` berarti chi^2_obs melebihi chi^2 SEMUA 2000 realisasi GUE berukuran sama; no ada titik kisi mana pun which mendaki ke arah konsistensi.

chi^2 mentah lintas-N bukan apel-samel (jumlah pasangan ~N^2/2 berbeda ~4x), jadi which comparable adalah p-value matched-N -- and p-value terkunci in lantai. Sebagai note tanpa pretensi: on chart T chi^2 mentah dim 201 bahkan LEBIH BESAR dari dim 401 in dua dari tiga bandwidth (sigma_u 0,3 and 0,5), padahal jumlah pasangan per bin turun sekitar setengah.

S1 tetap buntu persis karena alasan which sama seperti dim 401: chart T 0.548557 -> 0.620526 tetap ``CONSISTENT WITH RMT``, chart L 0.190891 -> 0.131742 tetap keluar dari ketiga referensi; selisih antar-chart bertahan (masing-masing dijelaskan rentang puluhan--ratusan order; lihat "chart L non-uniform" in aturan preregistrasi), and S1 FINAL kedua resolusi tetap CHART-DEPENDENT -> INCONCLUSIVE. Perpindahan r_bar chart T in sekitar rerata GUE-nya: dari -3.56 SD (in bawah rerata) in dim 401 ke +1.04 SD (in atas rerata) in dim 201 -- tanda berbalik, magnitudo dalam satuan SD mengecil, tetapi with SATU matriks per resolusi itu tak terpisahkan dari fluktuasi sebesar ensemble-SD itu sendiri; itu bukan bukti tren.

Kesimpulan which sah, and hanya ini: on dua resolusi which tersedia, deviasi S2 terhadap kernel Montgomery **no mengecil** (rejeksi tetap in lantai uji), and S1 tetap **INCONCLUSIVE** oleh chart-dependence. Dua titik no menetapkan arah asimtotik -- question "tren" tetap butuh seri which lebih panjang -- which terjawab adalah versi ujinya: no ada pengecilan sampai konsisten on N=201 dari N=401. Plafon resolusi kini terukur dua kali.

Plafon which dicetak masing-masing run (dikutip apa adanya):

- dim 401: N = 401 levels, 399 ratios, ~200 pairs/bin;
- dim 201: N = 201 levels, 199 ratios, ~100 pairs/bin;

### 4.4 Cacat proses resolusi kedua, tercatat

- **Skrip cepat S2 cacat, keluaran in-VOID.** Sebelum pipeline kanonik (`gw_montgomery.py`) ditemukan, sebuah reimplementasi cepat sempat created and dijalankan. Ia cacat ganda: parameter `sigma_u` no terpakai -- buktinya chi^2 identik in ketiga bandwidth (T: 2976.2575 tiga kali; L: 40194.1146 tiga kali), mustahil for sweep which benar -- and unfolding rank-based which menghancurkan struktur pasangan. Seluruh keluarannya VOID and telah dihapus; seluruh angka in seksi ini berasal dari pipeline kanonik.
- **Spektrum draf skema salah, dihapus.** Draft pertama dim 201 (mid float saja, tanpa radius, tanpa gate) and pembangunnya telah dihapus; penggantinya adalah capture kanonik ber-G-M0 PASS in `reports/gw_spectrum_100_100.json`.
- **Sensor CI buta, diperbaiki in akar.** Sensor escape-token menyapu `lean/spec/` (9 axiom deklaratif which memang in luar glob audit Python) sehingga CI merah in enam push berturut-turut sejak `29afa19`. Perbaikan `1d591a8`: kernel tetap wajib 0 hit; glob spec melarang `sorry/admit/unsafe` and membekukan anggaran axiom in angka 9. CI hijau lagi (run 38832840886).
- **Provenance baseline.** `msaf/mont_run.txt` adalah salinan UTF-16 dari `gw_montgomery_100_200_run2.log` (baris r_bar and chi^2 identik; beda 1 karakter akhir baris). Log `gw_montgomery_100_200.log` which lebih lama no memuat statistik S1/S2 and no dipakai.
- **Audit presisi global for kampanye ini.** Ketiga modul baru diperiksa. `gw_route_s_ladder.py` and `capture_spectrum_201.py` memakai pola simpan/pulihkan `ctx.prec`; satu tulisan telanjang `mp.mp.dps = 100` (presisi parsing gate G-M0c atas mid 60 digit) ditemukan in `capture_spectrum_201.py` and diperbaiki in akar -- nilai lama kini dipulihkan in `finally` bersama `ctx.prec`; restore-saja, tanpa efek numerik on artefak which tersegel. `gw_resolution_delta.py` nol sentuhan presisi (murni teks). Delapan tulisan telanjang in modul tes lama (OPEN in `NONFINITE_DEFECT.md`) tetap TIDAK disentuh, sesuai mandat.

Batasan which dibaca harfiah tetap sama: ini statistik dari dua matriks finit which terbangun. Bukan teorema Montgomery, bukan bukti RH, bukan Weil-positivity, bukan penghitungan prima.

<!-- END GW-DELTA -->

<!-- BEGIN GW-DELTA-3 (generated by msaf/gw_resolution_delta.py --write) -->

## 5. Resolusi ketiga (2026-10-16): dimensi 301 -- seri tiga titik 201/301/401

*Protokol identik with resolusi kedua: ladder Route S 6000 bit -> capture arb penuh ber-G-M0 -> `gw_montgomery.py` kanonik (2000 surrogat N-matched per ensemble, seed 20260927). Angka diekstrak mesin dari file oleh `msaf/gw_resolution_delta.py`, no diketik ulang; arah kolom menaik menurut dimensi.*

### 5.1 Spektrum ketiga, tersertifikasi penuh

| Item | Nilai terukur |
|---|---|
| Ladder Route S 6000 bit (c=100, N=150) | CERTIFIED POSITIVE DEFINITE -- n_pos = 301, n_neg = 0; build 619.74 s; LDL^T 57.1 s |
| Capture penuh (arb), dim 301 | G-M0 PASS 5/5; lambda_min = 6.57718987168245436989192354963e-248; lambda_max = 7.86716590892937597408651443191; spread 248.07777793 orders; radius terburuk `|rad|/|mid|` = 1e-1437.1228; eig 3137.6 s |
| Chain capture | `build_arb_tau` -> `arb_mat.eig(vdhoeven_mourrain)` tanpa serialisasi desimal; deviasi rantai dari dim 401 dicatat in field `build_chain` |

### 5.2 Tabel seri tiga titik

| Besaran | dim 201 | dim 301 | dim 401 |
|---|---|---|---|
| Provenance | c=100 N=100 dps=1806 prec=6000 algo=vdhoeven_mourrain n=201 | c=100 N=150 dps=1806 prec=6000 algo=vdhoeven_mourrain n=301 | c=100 N=200 dps=400 prec=2048 algo=vdhoeven_mourrain n=401 |
| lambda_min (float) | 2.4366351145008994e-191 | 6.5771898716824545e-248 | 1.7372701741044778e-294 |
| lambda_max | 7.1571506955502118 | 7.8671659089293762 | 7.9954638264487512 |
| spread (orders) | 191.467950 | 248.077778 | 294.662976 |
| S1 chart T `r_bar` (n_ratios) | 0.620526 (199) | 0.563504 (299) | 0.548557 (399) |
| Referensi GUE matched-N (mean +- sd) | 0.599774 +- 0.020042 | 0.600043 +- 0.016401 | 0.599639 +- 0.014359 |
| Jarak T dari rerata GUE (SD ensemble) | +1.04 | -2.23 | -3.56 |
| S1 chart L `r_bar` | 0.131742 | 0.151834 | 0.190891 |
| S1 FINAL | CHART-DEPENDENT (T and L disagree) -> INCONCLUSIVE | CHART-DEPENDENT (T and L disagree) -> INCONCLUSIVE | CHART-DEPENDENT (T and L disagree) -> INCONCLUSIVE |
| S2 chi^2 chart T (sigma_u 0.3 / 0.5 / 1.0) | 14621.8788 / 2146.3923 / 594.5661 | 12448.7407 / 1393.1679 / 869.3876 | 11639.5769 / 1698.5441 / 816.3241 |
| S2 chi^2 chart L | 47172.5984 / 10004.2942 / 4219.3598 | 107396.0291 / 15289.0448 / 5786.2945 | 137543.9721 / 18825.3487 / 6289.2525 |
| S2 p_GUE (6 titik) | 0.0000 | 0.0000 ; 0.0180 | 0.0000 |
| S2 p_Pois chart T | 0.9910 / 0.8285 / 0.0245 | 0.9950 / 0.2390 / 0.0720 | 0.9980 / 0.5340 / 0.0075 |
| S2 p_Pois chart L | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| S2 FINAL | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION | INCONSISTENT WITH MONTGOMERY AT THIS RESOLUTION |

### 5.3 Verdict seri tiga titik

p_GUE per dimensi: 201 = 0.0000; 301 = 0.0000 ; 0.0180; 401 = 0.0000. (Nilai in luar lantai 0,0000 berarti ada titik kisi which no lagi melebihi SEMUA surrogat -- dilaporkan apa adanya, tanpa disesuaikan.)

**Jawaban versi uji on seri tiga titik tetap: TIDAK mengecil menuju konsistensi** -- S2 FINAL = INCONSISTENT WITH MONTGOMERY in ketiga dimensi; no ada satu pun dari 18 sel which mendaki ke ambang 0,05 (p_GUE maksimum = 0.0180). Dengan satu matriks per resolusi, itu bukan bukti tren ke arah mana pun.

S1 tetap chart-dependent in ketiga dimensi: chart T 0.620526 -> 0.563504 -> 0.548557 tetap in dalam pita RMT, chart L 0.131742 -> 0.151834 -> 0.190891 tetap keluar dari ketiga referensi; jarak T dari rerata GUE: +1.04 -> -2.23 -> -3.56 SD (tanda berbalik in antara resolusi -- with satu matriks per titik itu tak terpisahkan dari fluktuasi ensemble-SD; bukan tren which terbaca). Verdict S1 tetap INCONCLUSIVE.

chi^2 mentah lintas-N tetap bukan apel-samel (jumlah pasangan ~N^2/2); statistik comparable tetap p-value matched-N. Seri finit tiga titik memperkuat versi uji jawabannya; arah asimtotik tetap no dapat disimpulkan dari seri finit, and itu dicatat sebagai limit, bukan ditutupi.

Catatan provenance: `capture_spectrum_201.py` diparameterkan (--c/--n/--prec; default mereproduksi run pertama dim 201) sebelum run ketiga; log mentah: `reports/mont_run_100_150.txt`; capture: `reports/gw_capture_100_150.log`; ladder seri: `reports/gw_route_s_ladder_c100.json`.

<!-- END GW-DELTA-3 -->

<!-- BEGIN GW-RES4-OUTCOME (hand-written outcome notice appended 2026-10-17; NOT a generated measurement block) -->

## 6. Titik keempat (dim 501) â€” OUTCOME non-PD: statistik titik berakhir in ladder

*Pra-registrasi `reports/RESOLUTION4_DIM501_PREREG_2026-10-17.md` (commit `ea2ed77`, dipush sebelum launch). Ladder Route S 6000 bit, c=100, N=250 â†’ dim 501. Angka mesin verbatim dari `reports/gw_route_s_ladder_c100_n250.log`:*

| N | dim | prec | n_pos | n_neg | finite | build_s | ldlt_s | verdict |
|---|---|---|---|---|---|---|---|---|
| 250 | 501 | 6000 | 446 | 0 | True | 1612.96 | 177.07 | UNDETERMINED at pivot 446 |

`1 run(s); 0 certified, 1 not certified` â€” bukan CERTIFIED POSITIVE DEFINITE; sesuai pra-registrasi Â§4 ini OUTCOME (bukan infrastruktur) and statistik titik keempat BERAKHIR: capture penuh + pengukuran Montgomery for dim 501 no dijalankan; no ada angka S1/S2 baru and **no ada blok GW-DELTA keempat**. Laporan bertanggal (termasuk insiden wrapper `ExitCode` kosong which no memengaruhi result): `reports/GW_RESOLUTION4_DIM501_2026-10-17.md`.

Batas: sertifikat tanda LDL^T interval on satu matriks finit (6000 bit) â€” bukan pernyataan tentang spektrum sebenarnya, bukan teorema Montgomery, bukan bukti RH, bukan tren.

Blok ini no mengubah byte apa pun dari GW-DELTA and GW-DELTA-3 in atas.

<!-- END GW-RES4-OUTCOME -->


