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

Model `A * e^(-B n)` dengan B konstan memroyeksikan lereng **konstan**.
Yang terukur justru **menurun monoton**, dan pada rentang terakhir sudah
mendekati nol. Jadi:

* lawanan dengan bentuk eksponensial konstan **terbantah** pada irisan
  ini (c=13 tetap, N naik);
* redamannya **sub-eksponensial** terhadap dimensi sepanjang jalur itu;
* apakah B terus turun atau membungkuk ke asimtot lain **belum
  ditentukan** oleh empat anak tangga. Dua anak tangga panjang
  (dim 257 dan 321) sedang dijalankan; itulah yang akan memutuskan.

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

#### Apakah deviasi mengecil atau membesar? **TIDAK DIJAWAB**

Skripnya sendiri menyebut plafon resolusinya: "RESOLUTION CEILING:
N = 401 levels, 399 ratios, ~200 pairs/bin". Satu titik resolusi tidak
dapat menjawab arah kecenderungan. Menjawabnya butuh **spektrum
tersertifikasi kedua pada resolusi berbeda** lalu S1/S2 diulang pada
keduanya -- itu eksperimennya, dan belum dijalankan. Yang bisasaid hari
ini: pada N=401, statistik ini **tidak** bisa dibedakan dari kernel
Montgomery, dan S1 bahkan gagal memberi verdict karena chart-nya
saling bertentangan.

Dan batasan yang harus dibaca harfiah: ini statistik dari SATU matriks
yang terbangun dan finit. Bukan teorema Montgomery, bukan bukti RH,
bukan bukti Weil-positivity, bukan penghitungan bilangan prima.

### 3c. Kesalahan proses, tercatat

`build_arb_tau` mengembalikan `(matriks, dimensi)`, bukan matriks saja.
Versi pertama saya mengambil tupel itu apa adanya, dan errornya
muncul dari dalam faktorisasi (`TypeError: tuple indices...`) alih-alih
di titik panggil —_squra yang mahal. Sekarang ada `assert` eksplisit.
