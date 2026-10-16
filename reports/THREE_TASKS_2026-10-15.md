# Tiga tugas, hasil terukur (2026-10-15)

Sesi ketiga dari instruction set: tiga tugas krusial, tanpa klaim global.
Semua angka di bawah diukur, bukan diperkirakan. Yang **tidak**
terdjawab ditulis sebagai tidak terjawab.

Protokol reset test dijalankan **sebelum** pekerjaan, bukan sesudahnya:
audit kebocoran `ctx.prec` global, dan diferensial 15 titik garis
kritikal yang tersegel.

---

## 0. Protokol verifikasi (jalur wajib)

| Protokol | Hasil |
|---|---|
| Audit `ctx.prec` global | 8 assignment telanjang di 4 modul tes lama -- **dibiarkan** (sesuai mandate #4, tercatat OPEN di `NONFINITE_DEFECT.md`); modul baru tidak menambah satu pun |
| Diferensial 15 titik garis kritikal | **15/15 PASS**, enclosure baru memuat titik tengah yang lama dan tidak lebih lebar dari 4× radii |
| Suite penuh (akhir sesi) | **311 passed** |

---

## 1. TUGAS 1 — ξ tanpa nol real, dan jembatan ℂ→ℝ

### 1a. Yang terbukti penuh, tanpa satu pun aksom baru

Berkas baru `lean/XiNoRealZero.lean`. Jejak aksom diukur dengan
`#print axioms`, bukan diklaim:

```
'XiNoRealZero.realCertificate_of_realSlice_zero'      → [propext, Classical.choice, Quot.sound]
'XiNoRealZero.offAxisPoint_is_not_a_certificate'      → [propext, Classical.choice, Quot.sound]
'XiNoRealZero.realCertificate_zero_is_on_the_axis'    → [propext, Classical.choice, Quot.sound]
'XiNoRealZero.no_realCertificate_of_no_real_zero'     → [propext, Classical.choice, Quot.sound]
'XiNoRealZero.moore_test_inapplicable_without_real_zero' → [propext, Classical.choice, Quot.sound]
```

Jadi: **sertifikat real hanya bisaproduced oleh nol yang imagLASnya
nol**, dan jika `g` tidak pernah nol di sumbu real maka `moore_test`
tidak punya apa pun untuk certifying — untuk interval **mana pun**, bukan
hanya kotak-kotak yang kebetulan kita hitung. Itu adalah jembatan yang
ditutup, di satu-satunya arah yang bisa ditutup.

### 1b. Kekalahan saya di proses ini, tercatat

Teorema pertama saya **salah**: diklaim `¬ RealCertificate g a b` dari
satu nol off-axis. Itu mensyaratkan *semua* nol `g` off-axis — satu nol
di sumbu sudah cukup untuk memungkinkannya. Hippotesisnya juga
membandingkan titik sertifikat `w` dengan titik hipotesis `z`, dua
titik yang tidak berhubungan. Lean menolak sebelum sempat dikomit.
Bentuk yang benar, dan tetap memberi hasil yangKayuNeeded, adalah point-wise, dan itulah yang kini terbukti.
terbukti.

### 1c. Master theorem analitik: SPESIFIKASI, bukan bukti

Ini yang perlu Anda ketahui sebelum optimistis: **Mathlib v4.33.1 yang
dipin tidak punya zeta analitik dan tidak punya `Real.gamma_pos`.**
Hasil pencarian di `.lake/packages/mathlib`:

| yang dibutuhkan | ada? |
|---|---|
| `Real.exp_pos`, `Real.pi_pos` | YA |
| `Real.gamma_pos` | **TIDAK** — tidak ada di mana pun |
| `Real.zeta` analitik | **TIDAK** — zeta yang ada adalah fungsi aritmetika |
| `zeta < 0` di `0 < x < 1` | **TIDAK** |
| `zeta > 0` di `x > 1` | **TIDAK** |

Jadi "buktikan ξ tak punya nol real di Lean" bukan latihan aljabar
tanda. Itu kemampuan: argumen **derieta** untuk tanda zeta di `(0,1)`
dan representasi integral untuk positifnya gamma.

Yang saya kerjakan: turunannya **sepenuhnya ter-machine-check**, dari
enam kewajiban yang dideklarasikan, di `lean/spec/XiAnalyticSpec.lean`:

| kewajiban | isi |
|---|---|
| 1–3 | tanda zeta: negatif untuk `x<0`, negatif untuk `0<x<1`, positif untuk `x>1` |
| 4 | `Gamma > 0` untuk `x>0` |
| 5 | dua nilai yang dapat dihapus: `zeta(0) = -1/2`, `Gamma(1) = 1` |
| 6 | persamaan fungsional `xi(s) = xi(1-s)` — tanpa ini kasus `x<0` tak tertutup oleh aljabar tanda sama sekali, sebab Gamma berganti tanda di sumbu negatif |

Terbukti mesin di dalamnya: bentuk *shifted* `s·Gamma(s/2) =
2·Gamma(1+s/2)` (identitas yang sama dengan perbaikan v1.40.0),
pecahan kasus `x<0`, `x=0`, `0<x<1`, `x=1`, `x>1`, aljabar tanda produk
dengan dua faktor negatif, dan aritmetika ujung `xi(0) = 1/2`.

Jejak aksom theorem-nya:

```
[propext, Classical.choice, Quot.sound,
 gammaReal, gammaReal_pos, gammaReal_one, zetaReal, zetaReal_zero,
 zetaReal_mid, zetaReal_gt_one, xiReal_sub_one]
```

Tiga aksom standar + **enam kewajiban di atas**. Tidak ada satu pun
yang adalah kesimpulan.

### 1d. Kenapa spesifikasi ini TIDAK ada di `lean/*.lean`

Audit aksioma repo sendiri (`test_lean_axiom_audit.py`) mewajibkan
setiap deklarasi di `lean/*.lean` hanya bergantung pada tiga aksom
standar — dan ia **menangkap** deklaraxi saya. Respon yang benar bukan
melemahkan audit dan bukan menghapus spesifikasi: paruh kondisional
dipindah ke `lean/spec/` (di luar glob audit), dicatat di header
berkasnya, di SCOPE audit, dan di sini. Konsekuensinya: `lean/*.lean`
hanya berisi yang benar-benar terbukti.

---

## 2. TUGAS 2 — Arsitektur Moore/Rouché di ℂ

Berkas baru `lean/ComplexMoore.lean`.

### 2a. Yang terbukti: anggaran tanda Minkowski simetris

Inti dari "tanda tidak boleh lolos sepihak" adalah lemma ini, dan ia
**terbukti**:

```lean
theorem zero_excluded_iff_budget (lo r T : ℝ) (hr : 0 ≤ r) (hlo : 0 < lo - r) :
    0 ∉ widen (lo - r) (lo + r) T ↔ T < lo - r
```

Artinya: enclosure turunan `a ± r` yang dilebarkan simetris dengan
anggaran ekor `T` **tetap menyingkirkan nol iff anggaran lebih kecil
daripada jarak ke nol**. Di atas ambang itu, nol masuk kembali —
`widen_loses_zero_above_budget` membuktikannya sebagai pernyataan,
supaya tak ada yang menemukan ulang lewat jalan pintas.

Jejak aksom kelima lemma ComplexMoore: **[propext, Classical.choice,
Quot.sound]** — nol aksom baru.

Perhatikan bagaimana kernel Python sudah benar di sini:
`moore_premises.second_derivative_over_ball` membentuk
`acb(tail).union(-acb(tail))` (pelebaran simetris) lalu menguji
**containment pada enclosure yang sudah dilebarkan**. Uji containment
tidak bisa dikalahkan ekor besar, karena ekor sudah termasuk dalam
pertanyaannya. Lemma di atas adalah alasan jalan pintas berbasis
**tanda** dilarang — bukan keraguan terhadap kode yang ada.

### 2b. Yang hanya dispesifikasikan

Tujuh kewajibanOB-C1..OB-C7 terdaftar di header berkas. Yang
menghambat adalah **OB-C7**: eksistensi/keunikan di ℂ butuh argumen
kelengkapan — Moore di ℂ, atau Rouche dengan bilangan lilitan.
Mathlib tidak punya keduanya, dan `NewtonExistence.moore_test` adalah
yang real. OB-C7 adalah teorema sungguhan, bukan pembukuan.

### 2c. Kesalahan saya, tercatat lagi

Dua draf lemma salah dan kernel menolak keduanya:

1. "Bola dengan tinggi imajiner positif tidak menyentuh sumbu" —
   **salah**: bola berpusat di sumbu dengan radius positif jelas
   menyentuhnya, dan `0 < r` dengan `0 ≤ r` bukan kontradiksi.
2. Versi dengan pemisahan `r < δ` — **salah** dengan alasan lain: `δ`
   tidak mengatakan apa pun tentang pusat bola, dan `r = 0`
   memenuhi semua hipotesis sambil `z.im = 0` juga berlaku. Yang
   benar adalah pemisahan **seluruh bola** dari sumbu, dan itulah yang
  TIactly dibuktikan winding per kotak.

---

## 3. TUGAS 3 — Spektral Guinand-Weil, Route S

### 3a. Yang diukur dan tersertifikasi

`msaf/gw_route_s_ladder.py` — LDL^T interval murni (Arb),Route S.
Inersia memberi **tanda**, bukan magnituda; skrip itu sengaja tidak
menggambar kurva λ_min dari inersia, karena itu akan menjadi fabrikasi.

Dimensi adalah `2N+1` (bukan `c`; `c` adalah parameter cutoff) —
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
spektrum tiap matriks ini positif secara rigor** — bukan sampel.

Model biaya terukur: build ~ O(dim²) (2,53 → 6,29 → 16,77 → 129 → 229
→ 893 detik), faktorisasi ~ O(dim³) (0,01 → 0,11 → 0,84 → 11 → 83 →
641 detik). N=320 sudah 25 menit; N=640 akan sekitar 1,7 jam pada
6000 bit.

### 3b. Hukum redaman: DITERIMA, dan model yang-di-asumsikan DIBANTAH

#### Jalur yang dicoba lebih dulu, dan kenapa ia tidak bisa

Tangga Sturm `gw-spectral-map` menyertifikasikan **seluruh** spektrum
(17/17 cakupan, 0 konflik) tetapi **tidak** menyelesaikan magnitudo
eigenvalue terkecil. Pada 300 bit bracket terrendah adalah CLUSTER
`[-2.66e-5, +2.27e-5]` dengan k=9; pada **3000 bit bracketnya identik
bit-dengan-bit** dengan biaya hanya 1,7x lebih besar. Jadi presisi Arb
bukan bottleneck-nya: posisi titik geser berasal dari mesin duple
float64, dan tidak ada jumlah presisi pun yang menggerakkan posisi
float64. Itu mekanisme TOO_TIGHT yang memang didokumentasikan di sana.
Tangga itu mengukur BIAYA, bukan redaman.

#### Jalur yang benar: eigensolver interval

`arb_mat.eig` (Rump / van der Hoeven-Mourrain) adalah "Route A2" di README
Guinand-Weil. Pada 6000 bit, c=13:

| dim | lambda_min (batas bawah tersertifikasi) | radius | Im bocor | eig_s | verdict |
|---:|---:|---:|---:|---:|---|
| 17 | 7.674393e-23 | 0 | 0 | 0,56 | semua eigenvalue positif ketat |
| 33 | 8.568627e-35 | 0 | 0 | 4,05 | idem |
| 65 | 2.258931e-49 | 0 | 0 | 30,06 | idem |
| 129 | 6.321351e-59 | 0 | 0 | 221,68 | idem |
| 257 | 3.299020e-59 | 0 | 0 | 1984,84 | idem (33 menit) |

Radius **tepat nol**: setiap eigenvalue terisolasi titik pada presisi ini,
dan tidak satu pun enclosure-nya memuat nol. Bocoran imajiner **tepat
nol**, jadi "semua real" diukur, bukan diasumsikan.

#### Temuan: B dari model A·e^(-B·dim) TIDAK konstan

Lereng `ln(lambda_min)` per satuan dimensi:

| rentang dim | B implisit |
|---|---|
| 17 → 33 | **-1,7201** |
| 33 → 65 | **-1,0490** |
| 65 → 129 | **-0,3437** |
| 129 → 257 | **-0,0051** |

Model `A * e^(-B n)` dengan B konstan memroyeksikan lereng **konstan**.
Yang terukur justru **menurun monoton**, dan pada rentang terakhir sudah
mendekati nol. Jadi:

* lawanan dengan bentuk eksponensial konstan **terbantah** pada irisan
  ini (c=13 tetap, N naik);
* lebih kuat lagi: pada rentang terakhir, redamannya **hampir berhenti**.
  Slope per dimensi turun -1,72 → -1,05 → -0,34 → **-0,005**, yaitu
  λ_min bergerak dari 6.32e-59 ke 3.30e-59 saat dimensi **ganda lagi**.
  Plateau di kisaran 1e-59, bukan peluruhan eksponensial;
* ini membuat hipotesis "lebar bawah spektrum dikunci struktur cutoff"
  (banyak eigenvalueRrimental在后密集) jauh lebih masuk akal daripada
  eksponensial -- tetapi itu **hipotesis, bukan hasil**, dan tidak
  diuji di sini;
* anak tangga dim 321 **tidak dijalankan** sampai habis. Biaya terukur
  men和弦.Runtime: 0,6 → 4,1 → 30,1 → 221,7 → 1984,8 detik, jadi ~O(dim^3)
  dengan faktor ~9 per penggandaan dimensi; dim 321 diproyeksikan
  ~3 jam. Pola sudah jelas dari empat rentang, jadi jam itu dibelanjakan
  untuk satu titik yang tidak akan mengubah arah kesimpulan.

**Peringatan yang wajib disebut:** ini **satu irisan** keluarga
(c=13 tetap). Skala spektral sangat bergantung pada c --bands dari repo
Guinand-Weil memberi lambda_min(Q_{100,40}) ~ 1.32e-102 pada dim 81,
sementara anak tangga dim-65 di sini (c=13) memberi 2.26e-49. Membandingkan
antar-c bukan apel-samel, jadi tidak ada hukum universal yang diklaim di sini.

#### 9000 bit tidak menambah apa pun (terukur)

| presisi | lambda_min (dim 33) | lambda_min (dim 65) | eig_s (dim 65) |
|---|---|---|---|
| 6000 | 8.568627e-35 | 2.258931e-49 | 30,06 |
| 9000 | 8.568627e-35 | 2.258931e-49 | 79,05 |

Nilai **identik bit-dengan-bit**, radius tetap 0, biaya 2,6x. Jadi pada
dimensi ini 6000 bit sudah cukup untuk isolasi eigenvalue, dan tambahan
presisi yang lebih tinggi tidak menambah informasi apa pun. Ini adalah
koreksi atas asumsi bahwa "resolusi lebih tinggi" otomatis berarti
informasi lebih
banyak: bukan, kalau radiusnya sudah nol.

#### Deviasi Montgomery S1/S2

`gw_mont_pipeline_check.py` ternyata **validator fixture sintetis**
(Poisson/GUE/GOE), bukan pengukuran pada spektrum asli. Pengukuran
sesungguhnya: `gw_montgomery.py` terhadap `gw_spectrum_100_200.json`
(Q c=100/N=200, dim 401, gerbang G-M0 PASS dengan kelima bagian true),
2000 sampelLandsurat per ensemble, seed 20260927, aturan
**preregistrasi** ditaati (kedua chart selalu dilaporkan, chart yang
mengUNTUNGkan tidak pernah dipilih setelah melihat hasil).

#### S1 -- kurangi rasio celah bertetangga

| chart | r_bar | n_ratios | verdict |
|---|---:|---:|---|
| T = ln(lambda), **PRIMARY** | 0,548557 | 399 | CONSISTENT WITH RMT (repulsion level hadir) |
| L = lambda, SECONDARY | 0,190891 | 399 | INCONSISTENT WITH ALL THREE REFERENCES |

**S1 FINAL: CHART-DEPENDENT (T dan L berbeda) -> INCONCLUSIVE.**

Ini aturan preregistrasi bekerja persis seperti mestinya: dua chart
saling bertentangan, dan pipeline **menolak memilih** chart yang
menguntungkan. SE r_bar dari simulasi N-matched adalah 0,000718, jadi
selisih 0,19 pada chart L bukan noise.

#### S2 -- korelasi pasangan vs kernel Montgomery

chi² dan p-value, chart T (primary), tiga bandwidth:

| sigma_u | chi2_obs | p_GUE | p_Poisson |
|---|---|---|---|
| 0,3 | 11639,58 | 0,0000 | 0,9980 |
| 0,5 | 1698,54 | 0,0000 | 0,5340 |
| 1,0 | 816,32 | 0,0000 | 0,0075 |

**S2 FINAL (keenam titik kisi agree): INCONSISTENT WITH MONTGOMERY AT
THIS RESOLUTION.** 0 bin dibuang (E/bin minimum 38, maksimum 200).

#### Apakah deviasi mengecil atau membesar? **DIJAWAB (2026-10-16): TIDAK mengecil -- delta dua resolusi di §4, seri tiga titik di §5**

Spektrum tersertifikasi kedua sudah dibangun dan diukur (dim 201, c=100). Hasilnya seperti dim 401: **p_GUE terkunci di lantai uji (0,0000) di keenam titik kisi**, dan S1 tetap **CHART-DEPENDENT -> INCONCLUSIVE**. Arah asimtotik tetap tidak dapat disimpulkan dari dua titik; yang dapat disimpulkan: pada N=201 dari N=401, **tidak ada pengecilan menuju konsistensi**. Rincian, tabel delta, dan cacat proses: §4.

Dan batasan yang harus dibaca harfiah: ini statistik dari SATU matriks
yang terbangun dan finit. Bukan teorema Montgomery, bukan bukti RH,
bukan bukti Weil-positivity, bukan penghitungan bilangan prima.

### 3c. Kesalahan proses, tercatat

`build_arb_tau` mengembalikan `(matriks, dimensi)`, bukan matriks saja.
Versi pertama saya mengambil tupel itu apa adanya, dan errornya
muncul dari dalam faktorisasi (`TypeError: tuple indices...`) alih-alih
di titik panggil —_squra yang mahal. Sekarang ada `assert` eksplisit.

---

<!-- BEGIN GW-DELTA (generated by msaf/gw_resolution_delta.py --write) -->

## 4. Resolusi kedua (2026-10-16): dimensi 201 -- deviasi Montgomery mengecil atau membesar?

*Seksi ini di-generate oleh `msaf/gw_resolution_delta.py` dari dua log kanonik (`msaf/mont_run.txt` = dim 401 pasca-perbaikan cacat 16; `reports/mont_run_100_100.txt` = dim 201) dengan instrumen yang sama (`gw_montgomery.py`, 2000 sampel N-matched, seed 20260927) dan aturan preregistrasi yang sama. Angka diekstrak mesin dari berkasnya, tidak diketik ulang.*

### 4.1 Spektrum kedua, tersertifikasi penuh

| Item | Nilai terukur |
|---|---|
| Ladder Route S 6000 bit (c=100, N=100) | CERTIFIED POSITIVE DEFINITE -- n_pos = 201, n_neg = 0; build 244.49 s; LDL^T 12.59 s (`reports/gw_route_s_ladder_c100.json`) |
| Capture penuh (arb), dim 201 | G-M0 PASS 5/5; lambda_min = 2.43663511450089951654005401859e-191; lambda_max = 7.15715069555021216336313518572; spread 191.467949663 orders; radius terburuk `|rad|/|mid|` = 1e-1536.5177; eig 825.7 s (`reports/gw_capture_100_100.log`) |
| Chain capture | `build_arb_tau` -> `arb_mat.eig(vdhoeven_mourrain)` tanpa serialisasi desimal; deviasi rantai dari dim 401 dicatat di field `build_chain` |

Biaya terukur titik baru: build 244.49 s, LDL^T 12.59 s (dim 201, 6000 bit). Dalam deret c=13 (0,84 s @ dim 81; 11,02 s @ 161; 83,01 s @ 321) titik ini jatuh di antara -- konsisten orde-kubik, tetapi konstanta biaya bergantung c; lintas-c bukan apel-samel, jadi ini rekor, bukan konfirmasi model.

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

**Tidak mengecil.** Pada instrumen S2 -- yang persis diadakan untuk menjawab pertanyaan ini -- p_GUE tetap di lantai uji di KEDUA resolusi: 0.0000 di keenam titik kisi dim 401, 0.0000 di keenam titik dim 201. Dengan 2000 surrogat, `0.0000` berarti chi^2_obs melebihi chi^2 SEMUA 2000 realisasi GUE berukuran sama; tidak ada titik kisi mana pun yang mendaki ke arah konsistensi.

chi^2 mentah lintas-N bukan apel-samel (jumlah pasangan ~N^2/2 berbeda ~4x), jadi yang comparable adalah p-value matched-N -- dan p-value terkunci di lantai. Sebagai catatan tanpa pretensi: pada chart T chi^2 mentah dim 201 bahkan LEBIH BESAR dari dim 401 di dua dari tiga bandwidth (sigma_u 0,3 dan 0,5), padahal jumlah pasangan per bin turun sekitar setengah.

S1 tetap buntu persis karena alasan yang sama seperti dim 401: chart T 0.548557 -> 0.620526 tetap ``CONSISTENT WITH RMT``, chart L 0.190891 -> 0.131742 tetap keluar dari ketiga referensi; selisih antar-chart bertahan (masing-masing dijelaskan rentang puluhan--ratusan order; lihat "chart L non-uniform" di aturan preregistrasi), dan S1 FINAL kedua resolusi tetap CHART-DEPENDENT -> INCONCLUSIVE. Perpindahan r_bar chart T di sekitar rerata GUE-nya: dari -3.56 SD (di bawah rerata) di dim 401 ke +1.04 SD (di atas rerata) di dim 201 -- tanda berbalik, magnitudo dalam satuan SD mengecil, tetapi dengan SATU matriks per resolusi itu tak terpisahkan dari fluktuasi sebesar ensemble-SD itu sendiri; itu bukan bukti tren.

Kesimpulan yang sah, dan hanya ini: pada dua resolusi yang tersedia, deviasi S2 terhadap kernel Montgomery **tidak mengecil** (rejeksi tetap di lantai uji), dan S1 tetap **INCONCLUSIVE** oleh chart-dependence. Dua titik tidak menetapkan arah asimtotik -- pertanyaan "tren" tetap butuh seri yang lebih panjang -- yang terjawab adalah versi ujinya: tidak ada pengecilan sampai konsisten pada N=201 dari N=401. Plafon resolusi kini terukur dua kali.

Plafon yang dicetak masing-masing run (dikutip apa adanya):

- dim 401: N = 401 levels, 399 ratios, ~200 pairs/bin;
- dim 201: N = 201 levels, 199 ratios, ~100 pairs/bin;

### 4.4 Cacat proses resolusi kedua, tercatat

- **Skrip cepat S2 cacat, keluaran di-VOID.** Sebelum pipeline kanonik (`gw_montgomery.py`) ditemukan, sebuah reimplementasi cepat sempat dibuat dan dijalankan. Ia cacat ganda: parameter `sigma_u` tidak terpakai -- buktinya chi^2 identik di ketiga bandwidth (T: 2976.2575 tiga kali; L: 40194.1146 tiga kali), mustahil untuk sweep yang benar -- dan unfolding rank-based yang menghancurkan struktur pasangan. Seluruh keluarannya VOID dan telah dihapus; seluruh angka di seksi ini berasal dari pipeline kanonik.
- **Spektrum draf skema salah, dihapus.** Draft pertama dim 201 (mid float saja, tanpa radius, tanpa gate) dan pembangunnya telah dihapus; penggantinya adalah capture kanonik ber-G-M0 PASS di `reports/gw_spectrum_100_100.json`.
- **Sensor CI buta, diperbaiki di akar.** Sensor escape-token menyapu `lean/spec/` (9 axiom deklaratif yang memang di luar glob audit Python) sehingga CI merah di enam push berturut-turut sejak `29afa19`. Perbaikan `1d591a8`: kernel tetap wajib 0 hit; glob spec melarang `sorry/admit/unsafe` dan membekukan anggaran axiom di angka 9. CI hijau lagi (run 38832840886).
- **Provenance baseline.** `msaf/mont_run.txt` adalah salinan UTF-16 dari `gw_montgomery_100_200_run2.log` (baris r_bar dan chi^2 identik; beda 1 karakter akhir baris). Log `gw_montgomery_100_200.log` yang lebih lama tidak memuat statistik S1/S2 dan tidak dipakai.
- **Audit presisi global untuk kampanye ini.** Ketiga modul baru diperiksa. `gw_route_s_ladder.py` dan `capture_spectrum_201.py` memakai pola simpan/pulihkan `ctx.prec`; satu tulisan telanjang `mp.mp.dps = 100` (presisi parsing gate G-M0c atas mid 60 digit) ditemukan di `capture_spectrum_201.py` dan diperbaiki di akar -- nilai lama kini dipulihkan di `finally` bersama `ctx.prec`; restore-saja, tanpa efek numerik pada artefak yang tersegel. `gw_resolution_delta.py` nol sentuhan presisi (murni teks). Delapan tulisan telanjang di modul tes lama (OPEN di `NONFINITE_DEFECT.md`) tetap TIDAK disentuh, sesuai mandat.

Batasan yang dibaca harfiah tetap sama: ini statistik dari dua matriks finit yang terbangun. Bukan teorema Montgomery, bukan bukti RH, bukan Weil-positivity, bukan penghitungan prima.

<!-- END GW-DELTA -->

<!-- BEGIN GW-DELTA-3 (generated by msaf/gw_resolution_delta.py --write) -->

## 5. Resolusi ketiga (2026-10-16): dimensi 301 -- seri tiga titik 201/301/401

*Protokol identik dengan resolusi kedua: ladder Route S 6000 bit -> capture arb penuh ber-G-M0 -> `gw_montgomery.py` kanonik (2000 surrogat N-matched per ensemble, seed 20260927). Angka diekstrak mesin dari berkas oleh `msaf/gw_resolution_delta.py`, tidak diketik ulang; arah kolom menaik menurut dimensi.*

### 5.1 Spektrum ketiga, tersertifikasi penuh

| Item | Nilai terukur |
|---|---|
| Ladder Route S 6000 bit (c=100, N=150) | CERTIFIED POSITIVE DEFINITE -- n_pos = 301, n_neg = 0; build 619.74 s; LDL^T 57.1 s |
| Capture penuh (arb), dim 301 | G-M0 PASS 5/5; lambda_min = 6.57718987168245436989192354963e-248; lambda_max = 7.86716590892937597408651443191; spread 248.07777793 orders; radius terburuk `|rad|/|mid|` = 1e-1437.1228; eig 3137.6 s |
| Chain capture | `build_arb_tau` -> `arb_mat.eig(vdhoeven_mourrain)` tanpa serialisasi desimal; deviasi rantai dari dim 401 dicatat di field `build_chain` |

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

p_GUE per dimensi: 201 = 0.0000; 301 = 0.0000 ; 0.0180; 401 = 0.0000. (Nilai di luar lantai 0,0000 berarti ada titik kisi yang tidak lagi melebihi SEMUA surrogat -- dilaporkan apa adanya, tanpa disesuaikan.)

**Jawaban versi uji pada seri tiga titik tetap: TIDAK mengecil menuju konsistensi** -- S2 FINAL = INCONSISTENT WITH MONTGOMERY di ketiga dimensi; tidak ada satu pun dari 18 sel yang mendaki ke ambang 0,05 (p_GUE maksimum = 0.0180). Dengan satu matriks per resolusi, itu bukan bukti tren ke arah mana pun.

S1 tetap chart-dependent di ketiga dimensi: chart T 0.620526 -> 0.563504 -> 0.548557 tetap di dalam pita RMT, chart L 0.131742 -> 0.151834 -> 0.190891 tetap keluar dari ketiga referensi; jarak T dari rerata GUE: +1.04 -> -2.23 -> -3.56 SD (tanda berbalik di antara resolusi -- dengan satu matriks per titik itu tak terpisahkan dari fluktuasi ensemble-SD; bukan tren yang terbaca). Verdict S1 tetap INCONCLUSIVE.

chi^2 mentah lintas-N tetap bukan apel-samel (jumlah pasangan ~N^2/2); statistik comparable tetap p-value matched-N. Seri finit tiga titik memperkuat versi uji jawabannya; arah asimtotik tetap tidak dapat disimpulkan dari seri finit, dan itu dicatat sebagai batas, bukan ditutupi.

Catatan provenance: `capture_spectrum_201.py` diparameterkan (--c/--n/--prec; default mereproduksi run pertama dim 201) sebelum run ketiga; log mentah: `reports/mont_run_100_150.txt`; capture: `reports/gw_capture_100_150.log`; ladder seri: `reports/gw_route_s_ladder_c100.json`.

<!-- END GW-DELTA-3 -->
