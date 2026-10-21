# Pra-registrasi T1b: propagasi blok bertanda untuk integrator ODE tervalidasi - 2026-10-21

**Status:** scope DIKUNCI untuk milestone T1b; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis dan di-commit sebelum kode T1b. Hash `sha256LF`
berkas ini dicatat di receipt T1b dan laporan.

**Latar:** T1 (`reports/PREREG_ODE_VALIDATED_2026-10-21.md`) sudah dieksekusi
dengan verdict **FAILED** (`reports/ODE_VALIDATED_2026-10-21.md`):
C1-C3 PASS; C4 melewati toleransi `1e-12` di checkpoint 1024
(`1.388201187303098743663909431234060321003198623657226562500000000000000000000e-11`)
lalu abort `Picard enclosure failed` di langkah 1557; C5 abort di langkah 42;
C6 tidak lengkap; registry `A-2026-0040` tidak dibuat. Diagnosis T1: batas
norma spektral **per langkah** (`sigma_step ~ 1.0375` untuk Kepler; jauh lebih
besar di jalur three-body) dipakai secara multiplikatif, sehingga batas
ketidakpastian membengkak eksponensial, padahal aliran sesungguhnya
periodik/monodromi terbatas. T1b mengganti **mekanisme propagasi
ketidakpastian** tanpa mengubah sistem, konfigurasi, atau toleransi.

**Paket:** kelanjutan trek T1 (prasyarat item Daftar-B 16 Three-Body dan 20
Soliton). Item tetap tertutup sampai verdict `ALL PASS`.

**Berkas target:** `msaf/ode_validated_block.py` (baru), guard
`msaf/tests/test_ode_validated_block.py` (baru), laporan
`reports/ODE_VALIDATED_T1B_2026-10-21.md`, receipt
`reports/ode_validated_t1b_2026-10-21.json`.

**Dependensi:** sama dengan T1 (Python 3.14, `python-flint==0.9.0`,
`fractions`); tidak ada float di jalur tersertifikasi.

**Registry yang direncanakan:** `A-2026-0040` (masih bebas karena T1 FAILED),
hanya bila verdict `ALL PASS` dan integritas PASS.

**Tidak mengubah:** semua artefak T1 - khususnya modul
`msaf/ode_validated.py` (sha256LF
`c1d9b5d60036a5f0772f7e3f1b8c78969efaa7146a713c762531ddce346251b9`), receipt
`reports/ode_validated_2026-10-21.json`, laporan `ODE_VALIDATED_2026-10-21.md`,
pra-registrasi T1 - serta V1-V6, `A-2026-0022`-`A-2026-0039`, `ci.yml`,
workflow spec, `lean/lakefile.toml`, freeze pins, dan artefak beku lain.

## 1. Maksud dan batas

T1b adalah **satu perubahan mekanisme**: ketidakpastian state tidak lagi
dipropagasi sebagai radius skalar yang dikalikan batas norma per langkah,
melainkan sebagai **himpunan bertanda** yang respons linearnya disimpan
eksplisit sepanjang integrasi. Tujuannya adalah lulus kriteria T1 yang sama
persis, bukan menurunkan standar.

Yang tetap berlaku dari T1: yang disertifikasi adalah **mesin enclosure**,
bukan fisika; tidak ada fallback float di jalur tersertifikasi; bukan bukti
formal Lean.

T1b **bukan**: bukti keberadaan/stabilitas figure-eight; perhitungan
Soliton/Evans; klaim chaos/ergodisitas/globalitas/fisika/PDE/RH.

## 2. Mekanisme yang dikunci

**2.1 Representasi ketidakpastian bertanda.** State pada awal langkah
direpresentasikan sebagai

    X = m + S * xi + slack,   xi in [-1,1]^m,   slack: bola Euclidean radius rho,

dengan `S` matriks interval `n x m` (kolom = arah noise) dan `m` = panjang
state. Kotak pembungkus yang dipakai untuk Picard dan untuk laporan adalah
`[m_i +/- (sum_j |S_ij| + rho)]`; batas ini harus dihitung dengan batas atas
yang rigor. Propagasi satu langkah:

- `m' = P_m(h)` - polinomial Taylor titik di tengah (seperti T1);
- `S' = J_step * S` - **perkalian matriks interval bertanda** (bukan nilai
  mutlak, bukan norma skalar);
- `rho' = ||J_step||_2 * rho + 3 * rem + kappa_nl * r_tot^2`, dengan
  `r_tot = max_i (sum_j |S_ij| + rho)` dan `rem` = batas sisa Taylor satu
  langkah (seperti T1).

`J_step` adalah Jacobian interval dari peta satu langkah terhadap state awal
(dihitung lewat jet `Dual` over kotak state saat itu). Perkalian `J_step * S`
memakai entri bertanda; **dilarang** menggantinya dengan `||J_step|| * S`
atau dengan radius skalar saja.

**2.2 Sisa lokal sebagai arah noise.** Sisa Taylor satu langkah harus
disisipkan sebagai arah noise baru (kolom baru), bukan hanya dilipat ke
`rho`, kecuali kapasitas noise sudah penuh. Jika kapasitas penuh, dua kolom
`S_a`, `S_b` digabung menjadi satu kolom `|S_a| + |S_b|` (nilai mutlak
komponen), memilih pasangan dengan massa `sum |.|` terkecil. Batas kapasitas:
`m_max = 64` untuk S3 dan `m_max = 96` untuk S4. Jumlah penggabungan per blok
direkam di receipt.

**2.3 Term kuadratik.** `kappa_nl = 1e18` dikunci. Receipt wajib merekam
`kappa_nl * r_tot^2` pada setiap blok dan **wajib** menunjukkan nilainya
`<= 1e-30`; bila ada blok yang melewatinya, verdict T1b = FAILED (tidak boleh
dilonggarkan secara diam-diam).

**2.4 Blok dan checkpoint.** Blok = interval checkpoint: S3 = 256 langkah,
S4 = 64 langkah (sama dengan T1). Kotak checkpoint dihitung dari `(m, S, rho)`
saat itu. Tidak ada reset yang mengubah data; `S` dan `rho` dibawa apa adanya
antar blok.

**2.5 Modul T1 beku.** `msaf/ode_validated_block.py` **mengimpor** definisi
sistem (`coeffs_*`, `rhs_*`, konstanta S1-S4) dari `msaf/ode_validated.py`
tanpa memodifikasi berkas itu. Modul T1 tetap menjadi rekaman FAILED yang
utuh; T1b tidak boleh "memperbaiki" hash-nya.

## 3. Sistem dan konfigurasi (identik T1 §3)

| Kode | Sistem | Data awal (rasional eksak) | Langkah | Orde | Cakupan |
|------|--------|----------------------------|---------|------|---------|
| S1 | `x' = x^2` | `x(0)=1` | `1/32` | 16 dan 24 | t=0..1/2 |
| S2 | `x''=-x` | `x(0)=1, v(0)=0` | `pi/32` (arb) | 24 | 32 dan 64 langkah (t=pi, 2pi) |
| S3 | Kepler sirkular | `(x,y,vx,vy)=(1,0,0,1)`, `G=M=1` | `2*pi/256` | 24 | 10 periode (2560 langkah) |
| S4 | Three-body figure-eight (RHS) | posisi `(-1,0),(1,0),(0,0)`; kecepatan `(a,b),(a,b),(-2a,-2b)`, `a=347111/10^6`, `b=532728/10^6`; `m=1,G=1` | `T/512`, `T=632591398/10^8` | 24 | 1 periode (512 langkah) |

Presisi 256 bit. Tidak ada parameter yang diubah setelah hasil terlihat.
Catatan S4 sama dengan T1: data uji stress untuk RHS, bukan klaim orbit
figure-eight periodik; konstanta gerak yang diperiksa `E0 =
-257428899017/200000000000`, `L0 = 0`, pusat massa `= 0`.

## 4. Kriteria lulus

C1-C6 identik dengan T1 §4 (toleransi sama: C2 `1e-12`/`1e-18` + rasio `1e4`;
C3 `1e-20`; C4 `1e-12`; C5 `1e-10`; C6 determinisme + guard + mutasi
M1-M4 + pemindai AST), ditambah:

**C7 - Pembeda mekanisme (mutasi M5).** Menjalankan T1b dengan propagasi
bertanda **dimatikan** (yaitu hanya `||J_step|| * S` / radius skalar per
langkah, persis mekanisme T1) harus mereproduksi kegagalan T1:

- C4: lebar energi checkpoint 1024 melewati `1e-12` **atau** abort
  `Picard enclosure failed` paling lambat langkah 1557; dan
- C5: abort `Picard enclosure failed` paling lambat langkah 42.

Bila M5 tidak mereproduksi kegagalan itu, diagnosis T1 dianggap keliru dan
verdict T1b = INCONCLUSIVE sampai laporan T1 direvisi.

C6 dilengkapi di T1b: guard menjalankan ulang kampanye, membandingkan payload
kanonik receipt, dan memuat minimal mutasi M1 (endpoint di luar selang),
M2 (remainder = 0 pada C2), M3 (ubah `E0` di receipt), M4 (suntik
`float(`/`math.` ke salinan modul, pemindai AST harus menolak), M5 (C7).

## 5. Verdict

- **ALL PASS**: C1-C7 semuanya PASS -> registry `A-2026-0040` + sertifikat
  `sha256LF`.
- **PARTIAL**: C1-C5 PASS tetapi C6/C7 belum lengkap; tanpa registry.
- **FAILED**: salah satu C2-C5 gagal (containment dilanggar atau toleransi
  terlampaui).
- **INCONCLUSIVE**: dependensi/hash/tool error, atau M5 tidak mereproduksi
  kegagalan T1.

## 6. Falsifier

- ada nilai eksak di luar enclosure yang dilaporkan;
- toleransi C2-C5 terlampaui;
- receipt tidak identik byte antar dua run;
- pemindai menemukan float di jalur tersertifikasi;
- uji mutasi M1-M4 tidak gagal sebagaimana mestinya;
- M5 tidak mereproduksi kegagalan T1;
- ada klaim di luar batas §1.

## 7. Artefak dan urutan eksekusi

1. Commit pra-registrasi ini sebelum kode (hash `sha256LF` dikunci).
2. Implementasi `msaf/ode_validated_block.py` (impor T1 tanpa memodifikasinya).
3. Guard `msaf/tests/test_ode_validated_block.py`.
4. Jalankan kampanye; tulis receipt; verifikasi determinisme dua run.
5. Tulis laporan `reports/ODE_VALIDATED_T1B_2026-10-21.md` dengan angka verbatim.
6. Bila `ALL PASS`: registry `A-2026-0040`, HANDOFF, sertifikat `sha256LF`.
7. Suite penuh + `freeze.py --verify`; commit/push hanya bila diminta.

## 8. Batas eksplisit

- Hanya S1-S4 dengan konfigurasi §3; tidak ada sistem lain.
- "Tervalidasi" = enclosure rigor-terbatas terhadap nilai eksak yang
  diketahui; bukan bukti formal dan bukan bukti global.
- Tidak ada klaim figure-eight, Soliton/Evans, chaos, ergodisitas, PDE
  kontinu/Navier-Stokes, RH/GRH, faktorisasi, RSA/ECC, Anderson, atau fisika.
- Hasil T1 (FAILED) tetap berlaku sebagai rekaman historis; T1b tidak
  mengubahnya.

## 10. Amendemen pra-implementasi (sebelum kode T1b)

Analisis implementasi - dilakukan **sebelum ada kode T1b maupun hasil apa
pun** - menemukan dua hal:

- §2.2 mewajibkan sisa Taylor disisipkan sebagai arah noise (kolom), tetapi
  §2.1 ikut melipat `3*rem` ke `rho`. Lipatan ganda itu tidak perlu, dan
  karena `rho` dikalikan `||J_step||_2` setiap langkah, suku tersebut akan
  tumbuh `sigma^k` - persis mode kegagalan T1 (untuk S4 `sigma ~ 31`),
  sehingga metode bertanda tidak mungkin lulus.
- Jacobian yang dipakai adalah **Jacobian interval atas seluruh kotak
  state**; dalam bentuk nilai rata-rata
  `P_x(h) - P_m(h) in J_box * (x - m)`, bagian polinomial Taylor orde `p`
  sudah terwakili eksak (tanpa suku kuadratik tambahan).

Amendemen (berlaku sebelum kode dan sebelum hasil apa pun):

1. `3*rem` TIDAK dilipat ke `rho`; sisa Taylor dibawa oleh kolom noise baru
   sesuai §2.2.
2. `rho` hanya membawa pembulatan (`<= 1e-70` per langkah) dan **tidak**
   dikalikan `||J_step||_2` per langkah. Batas kotak tetap dihitung dari
   `sum_j |S_ij| + rho` seperti §2.1.
3. `kappa_nl * r_tot^2` tetap dihitung dan disisipkan sebagai kolom noise
   kecil (bukan ke `rho`), dan tetap direkam di receipt dengan kewajiban
   `<= 1e-30` per blok; suku ini konservatif dan tidak dipakai untuk
   menutupi kesalahan orde dua yang tidak ada.
4. Kolom bertanda adalah satu-satunya mekanisme propagasi; §2.2 berlaku
   untuk semua sisa lokal (Taylor dan kuadratik).
5. Tidak ada perubahan lain: sistem, konfigurasi, toleransi C1-C6, kriteria
   C7, verdict, dan falsifier tetap. Hash pra-registrasi setelah amendemen
   dicatat di receipt/laporan; hash versi awal
   `79a4e87965cdc1682d4fa5ddb38cd2719201e316ddba1f2b32004c8379c9b0b1`
   tetap disebut pada laporan sebagai versi sebelum amendemen.
