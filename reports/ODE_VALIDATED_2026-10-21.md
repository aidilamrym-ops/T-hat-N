# T1 - Integrator ODE tervalidasi: hasil kampanye - 2026-10-21

**Verdict: FAILED** (C1-C3 PASS; C4 dan C5 FAILED; C6 tidak lengkap).
Tidak ada entri registry: `A-2026-0040` **tidak dibuat**. Item Daftar-B
16 (Three-Body) dan 20 (Soliton) **tetap tertutup**.

Kegagalan di sini adalah kegagalan **toleransi/enclosure** yang jujur:
tidak ada nilai eksak yang jatuh di luar enclosure pada checkpoint mana pun
yang sempat diukur; yang gagal adalah pelebaran selang yang melampaui
toleransi yang dikunci di pra-registrasi. Tidak ada klaim baru apa pun.

| Acuan | Nilai |
|---|---|
| Pra-registrasi | `reports/PREREG_ODE_VALIDATED_2026-10-21.md` |
| sha256LF pra-registrasi | `0630557deec4f18a526e89bc797e7f3cd2b5d2bcf1b3122b6929210fa6a9a4d6` |
| Modul | `msaf/ode_validated.py` |
| sha256LF modul | `c1d9b5d60036a5f0772f7e3f1b8c78969efaa7146a713c762531ddce346251b9` |
| Receipt | `reports/ode_validated_2026-10-21.json` |
| sha256LF receipt | `29b58ad6037d84a33acce5d33daa931795ea9904ff81a61c77bc032a73c012ff` |
| Determinisme receipt | dua run berturut-turut identik byte (5.560 byte; hash sama) |

## 1. Ringkasan hasil

| Kriteria | Hasil | Angka verbatim utama |
|---|---|---|
| C1 primitif bola | **PASS** | 2.000 kasus, `failures: []` |
| C2 langkah Taylor S1 | **PASS** | orde 16: lebar `3.197111822382543803678709215857454972731233056038036011159420013427734375000e-19`, memuat 2; orde 24: lebar `[1.216149746413838327420901550601500686382228599396711568592088781315396772698e-28 +/- 4.33e-104]`, memuat 2 |
| C3 osilator harmonik S2 | **PASS** | 32 langkah: lebar tiap komponen `8.995137842308963824421392003731237312162999499893777547185307911125391066150e-49`; 64 langkah: `1.799027568461792764884278400746247462432599899978755509437061582225078213230e-48`; keduanya memuat nilai eksak |
| C4 Kepler sirkular S3 | **FAILED** | checkpoint 256/512/768 lolos (lebar energi <= `2.892518311102572173309274011776537349760474171489477157592773437500000000000e-16`); checkpoint 1024 lebar energi `1.388201187303098743663909431234060321003198623657226562500000000000000000000e-11` > `1e-12`; checkpoint 1280 `6.662401546009277808479964733123779296875000000000000000000000000000000000000e-7`; checkpoint 1536 `0.04241811827523633837699890136718750000000000000000000000000000000000000000000`; langkah 1557 masuk `Picard enclosure failed` |
| C5 three-body S4 | **FAILED** | tidak ada checkpoint tercapai; langkah 42 masuk `Picard enclosure failed` |
| C6 determinisme/integritas | **TIDAK LENGKAP** | pemindai AST bersih (`ast_scan_hits: []`); determinisme receipt terpenuhi; guard `msaf/tests/test_ode_validated.py` beserta uji mutasi M1-M4 **belum ditulis** |

Verdict mengikuti pra-registrasi §5: salah satu C2-C5 gagal -> `FAILED`.
Karena verdict bukan `ALL PASS`, tidak ada entri registry dan tidak ada
sertifikat tambahan.

## 2. Apa yang lulus (C1-C3)

- **C1** - generator LCG `s_{n+1} = (1103515245*s_n + 12345) mod 2^31`, seed
  20261021; 1.000 pasangan operasi `+ - * /` dan 1.000 kasus `sqrt` semuanya
  memuat hasil Fraction eksak (`cases: 2000`, `failures: []`).
- **C2** - S1 `x' = x^2`, `x(0)=1`, 16 langkah `h=1/32`, pada `t=1/2`
  (solusi eksak `x=2`): orde 16 dan orde 24 keduanya memuat 2 memakai
  remainder eksplisit; rasio lebar orde 24 terhadap orde 16 jauh melebihi
  `1e4` (kontrol mutasi M2: tanpa remainder, containment gagal - lihat §5).
- **C3** - S2 `x'' = -x`, `(x(0),v(0))=(1,0)`: pada `t=pi` dan `t=2pi`
  enclosure memuat `(-1,0)` dan `(1,0)` dengan lebar orde `1e-48`, jauh di
  bawah toleransi `1e-20`.

## 3. Rincian kegagalan C4 (S3, Kepler sirkular)

Checkpoint tiap 256 langkah; toleransi lebar maksimum `1e-12` (energi dan
momentum sudut). Semua containment yang sempat diukur bernilai benar
(`energy_ok: true`, `angular_ok: true`); yang gagal adalah lebar.

| Langkah | Lebar energi (verbatim) | Lebar momentum sudut | width_ok |
|---|---|---|---|
| 256 | `1.255782632936734287251467402523413711677057391299938693407511891564354300499e-25` | `1.255763460304137912318550230262995278725601344498030709218028277973644435406e-25` | true |
| 512 | `6.026980916211821895292696552106921203256773011958102870266884565353393554688e-21` | `6.026888916097611400011902214674723663595523603930814715567976236343383789063e-21` | true |
| 768 | `2.892518311102572173309274011776537349760474171489477157592773437500000000000e-16` | `2.892474152065571029926851001623511194793536560609936714172363281250000000000e-16` | true |
| 1024 | `1.388201187303098743663909431234060321003198623657226562500000000000000000000e-11` | `1.388179997926890230086627298078383319079875946044921875000000000000000000000e-11` | **false** |
| 1280 | `6.662401546009277808479964733123779296875000000000000000000000000000000000000e-7` | `6.662299840698437947139609605073928833007812500000000000000000000000000000000e-7` | false |
| 1536 | `0.04241811827523633837699890136718750000000000000000000000000000000000000000000` | `0.04241214628564193844795227050781250000000000000000000000000000000000000000000` | false |

Receipt mencatat: `"error": "aborted at step 1557: ValidationError: Picard
enclosure failed"`. Jadi C4 gagal dua kali: toleransi lebar terlampaui lebih
dulu (checkpoint 1024), lalu mesin berhenti karena kotak Picard tidak lagi
bisa ditutup (langkah 1557).

## 4. Rincian kegagalan C5 (S4, RHS three-body)

Checkpoint pertama baru jatuh di langkah 64; integrasi sudah berhenti di
langkah 42 dengan `"error": "aborted at step 42: ValidationError: Picard
enclosure failed"` dan `checkpoints: []`. Tidak ada containment yang
dilanggar (belum ada checkpoint), tetapi enclosure tidak dapat dilanjutkan.
Jalur tiga-benda memperlihatkan inflasi yang jauh lebih cepat daripada
Kepler (radius yang dipropagasi mencapai orde `1e29` sebelum abort, dari
diagnostik terpisah).

## 5. Diagnosis mode kegagalan

Modul memakai skema yang dapat diaudit:

1. koefisien Taylor dihitung pada **titik tengah** kotak state (bukan dari
   bola state), memakai jet `Dual` untuk mendapatkan Jacobian interval `J_X`;
2. kotak Picard diverifikasi per langkah;
3. sisa Taylor orde `(p+1)` dibatasi pada kotak Picard;
4. ketidakpastian input dibawa sebagai **radius Euclidean** dan dipropagasi
   dengan bentuk nilai rata-rata `F(X) subset F(m) + J_X*(X-m)` memakai batas
   norma spektral `||J_X||_2` (lewat `||J^T J||_inf`).

Skema ini **sound** (semua containment yang terukur benar), tetapi batas
norma spektral per langkah bersifat **pesimistis secara eksponensial**:
untuk Kepler satu langkah Jacobian punya nilai singular terbesar sekitar
`1.0375` (numerik, diagnostik), karena perturbasi radial memiliki perilaku
hiperbolik transien. Mengalikan batas itu 2.560 kali menghasilkan
`1.0375^2560 ~ e^94`, padahal aliran sebenarnya periodik dan monodromi satu
periode terbatas. Radius yang teramati: `1.3e-34` (langkah 1), `4.3e-29`
(langkah 100), `1.2e-12` (langkah 1000), lalu meledak hingga abort
(langkah 1557). Jalur three-body (12 komponen, nonlinearitas lebih keras)
abort jauh lebih awal.

Ini adalah keterbatasan klasik propagasi interval/bola jangka panjang:
**wrapping/dependency inflation**, bukan bug pada rekurensi koefisien dan
bukan pelanggaran containment. Angka-angka di receipt direkam apa adanya;
tidak ada penyembunyian dengan heuristik tak terlaporkan.

Arah perbaikan yang belum diimplementasikan (kandidat milestone T1b, dengan
pra-registrasi baru):

- propagasi per **blok checkpoint**: hitung hasil kali matriks Jacobian
  satu-langkah secara interval untuk setiap blok (norma monodromi satu blok
  mendekati 1), reset radius di batas blok, dan batasi kontribusi remainder
  lokal lewat norma hasil kali parsial;
- atau Taylor model / aritmetika affine dengan simbol noise yang dikelola,
  yang menekan wrapping tanpa membuang korelasi.

## 6. Checklist falsifier (pra-registrasi §6)

| Falsifier | Status |
|---|---|
| Ada nilai eksak di luar enclosure yang dilaporkan | **Tidak terjadi**: seluruh containment yang terukur (`energy_ok`, `angular_ok`, `contains`) bernilai benar |
| Toleransi C2-C5 terlampaui | **Terjadi**: C4 checkpoint 1024 (`1.388...e-11 > 1e-12`), C5 abort langkah 42 |
| Receipt tidak identik byte antar dua run | **Tidak terjadi**: dua run berturut-turut identik byte (hash `29b58ad6...`) |
| Pemindai menemukan float di jalur tersertifikasi | **Tidak terjadi**: `ast_scan_hits: []` |
| Uji mutasi M1-M4 tidak gagal sebagaimana mestinya | **Tidak diuji**: guard dan uji mutasi belum ditulis (C6 tidak lengkap); verdict sudah FAILED tanpa ini |

Falsifier "toleransi C2-C5 terlampaui" terpenuhi, sehingga paket ini
**falsified** menurut §6. Konsekuensinya persis seperti §5: verdict
`FAILED`, tanpa entri registry.

## 7. Batas dan konsekuensi

- Tidak ada entri `A-2026-0040`; `reports/FENCE_REGISTRY.md` tidak diubah.
- Item 16 dan 20 `reports/DAFTAR_MASALAH_KERJA.md` tetap **tertutup**;
  syarat masuk "integrator ODE tervalidasi" belum terpenuhi.
- Tidak ada klaim figure-eight, Soliton/Evans, chaos, ergodisitas, PDE
  kontinu/Navier-Stokes, RH/GRH, faktorisasi, RSA/ECC, Anderson, atau fisika.
- Pra-registrasi tidak diubah (scope tetap terkunci); hasil ini dicatat
  sebagai verdict FAILED apa adanya.
- Modul `msaf/ode_validated.py` tetap disimpan sebagai artefak rekayasa
  (C1-C3 lulus, mekanisme audit terlihat) dan dapat dipakai ulang untuk
  T1b; ia belum menjadi kapabilitas tersertifikasi.

## 8. Artefak

| Berkas | sha256LF |
|---|---|
| `reports/PREREG_ODE_VALIDATED_2026-10-21.md` | `0630557deec4f18a526e89bc797e7f3cd2b5d2bcf1b3122b6929210fa6a9a4d6` |
| `msaf/ode_validated.py` | `c1d9b5d60036a5f0772f7e3f1b8c78969efaa7146a713c762531ddce346251b9` |
| `reports/ode_validated_2026-10-21.json` | `29b58ad6037d84a33acce5d33daa931795ea9904ff81a61c77bc032a73c012ff` |

Catatan determinisme: dua eksekusi `python -m msaf.ode_validated` berturut-turut
menghasilkan receipt byte-identik (5.560 byte). Modul tidak pernah memanggil
float di jalur tersertifikasi (pemindai AST bersih).
