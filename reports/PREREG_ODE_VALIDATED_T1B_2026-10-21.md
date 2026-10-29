# Pra-registrasi T1b: propagasi blok bertanda for integrator ODE tervalidasi - 2026-10-21

**Status:** scope DIKUNCI for milestone T1b; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis and in-commit sebelum kode T1b. Hash `sha256LF`
file ini dicatat in receipt T1b and report.

**Latar:** T1 (`reports/PREREG_ODE_VALIDATED_2026-10-21.md`) already dieksekusi
with verdict **FAILED** (`reports/ODE_VALIDATED_2026-10-21.md`):
C1-C3 PASS; C4 melewati toleransi `1e-12` in checkpoint 1024
(`1.388201187303098743663909431234060321003198623657226562500000000000000000000e-11`)
lalu abort `Picard enclosure failed` in step 1557; C5 abort in step 42;
C6 no lengkap; registry `A-2026-0040` no created. Diagnosis T1: limit
norma spektral **per step** (`sigma_step ~ 1.0375` for Kepler; jauh lebih
besar in jalur three-body) dipakai secara multiplikatif, sehingga limit
ketidakpastian membengkak eksponensial, padahal aliran sesungguhnya
periodik/monodromi terbatas. T1b mengganti **mekanisme propagasi
ketidakpastian** tanpa mengubah sistem, konfigurasi, or toleransi.

**Paket:** kelanjutan trek T1 (prasyarat item Daftar-B 16 Three-Body and 20
Soliton). Item tetap tertutup sampai verdict `ALL PASS`.

**Berkas target:** `msaf/ode_validated_block.py` (baru), guard
`msaf/tests/test_ode_validated_block.py` (baru), report
`reports/ODE_VALIDATED_T1B_2026-10-21.md`, receipt
`reports/ode_validated_t1b_2026-10-21.json`.

**Dependensi:** sama with T1 (Python 3.14, `python-flint==0.9.0`,
`fractions`); no ada float in jalur tersertifikasi.

**Registry which direncanakan:** `A-2026-0040` (masih bebas karena T1 FAILED),
hanya bila verdict `ALL PASS` and integritas PASS.

**Tidak mengubah:** semua artefak T1 - khususnya modul
`msaf/ode_validated.py` (sha256LF
`c1d9b5d60036a5f0772f7e3f1b8c78969efaa7146a713c762531ddce346251b9`), receipt
`reports/ode_validated_2026-10-21.json`, report `ODE_VALIDATED_2026-10-21.md`,
pra-registrasi T1 - serta V1-V6, `A-2026-0022`-`A-2026-0039`, `ci.yml`,
workflow spec, `lean/lakefile.toml`, freeze pins, and artefak beku lain.

## 1. Maksud and limit

T1b adalah **satu perubahan mekanisme**: ketidakpastian state no lagi
dipropagasi sebagai radius skalar which dikalikan limit norma per step,
melainkan sebagai **himpunan bertanda** which respons linearnya disimpan
eksplisit sepanjang integrasi. Tujuannya adalah lulus kriteria T1 which sama
persis, bukan menurunkan standar.

Yang tetap berlaku dari T1: which disertifikasi adalah **mesin enclosure**,
bukan fisika; no ada fallback float in jalur tersertifikasi; bukan bukti
formal Lean.

T1b **bukan**: bukti keberadaan/stabilitas figure-eight; perhitungan
Soliton/Evans; klaim chaos/ergodisitas/globalitas/fisika/PDE/RH.

## 2. Mekanisme which dikunci

**2.1 Representasi ketidakpastian bertanda.** State on awal step
direpresentasikan sebagai

    X = m + S * xi + slack,   xi in [-1,1]^m,   slack: bola Euclidean radius rho,

with `S` matriks interval `n x m` (kolom = arah noise) and `m` = panjang
state. Kotak pembungkus which dipakai for Picard and for report adalah
`[m_i +/- (sum_j |S_ij| + rho)]`; limit ini harus dihitung with limit atas
which rigor. Propagasi satu step:

- `m' = P_m(h)` - polinomial Taylor titik in tengah (seperti T1);
- `S' = J_step * S` - **perkalian matriks interval bertanda** (bukan nilai
  mutlak, bukan norma skalar);
- `rho' = ||J_step||_2 * rho + 3 * rem + kappa_nl * r_tot^2`, with
  `r_tot = max_i (sum_j |S_ij| + rho)` and `rem` = limit sisa Taylor satu
  step (seperti T1).

`J_step` adalah Jacobian interval dari peta satu step terhadap state awal
(dihitung lewat jet `Dual` over kotak state saat itu). Perkalian `J_step * S`
memakai entri bertanda; **dilarang** menggantinya with `||J_step|| * S`
or with radius skalar saja.

**2.2 Sisa lokal sebagai arah noise.** Sisa Taylor satu step harus
disisipkan sebagai arah noise baru (kolom baru), bukan hanya dilipat ke
`rho`, kecuali kapasitas noise already penuh. Jika kapasitas penuh, dua kolom
`S_a`, `S_b` digabung menjadi satu kolom `|S_a| + |S_b|` (nilai mutlak
komponen), memilih pasangan with massa `sum |.|` terkecil. Batas kapasitas:
`m_max = 64` for S3 and `m_max = 96` for S4. Jumlah penggabungan per blok
direkam in receipt.

**2.3 Term kuadratik.** `kappa_nl = 1e18` dikunci. Receipt wajib merekam
`kappa_nl * r_tot^2` on setiap blok and **wajib** menunjukkan nilainya
`<= 1e-30`; bila ada blok which melewatinya, verdict T1b = FAILED (no boleh
dilonggarkan secara diam-diam).

**2.4 Blok and checkpoint.** Blok = interval checkpoint: S3 = 256 step,
S4 = 64 step (sama with T1). Kotak checkpoint dihitung dari `(m, S, rho)`
saat itu. Tidak ada reset which mengubah data; `S` and `rho` dibawa apa adanya
antar blok.

**2.5 Modul T1 beku.** `msaf/ode_validated_block.py` **mengimpor** definisi
sistem (`coeffs_*`, `rhs_*`, konstanta S1-S4) dari `msaf/ode_validated.py`
tanpa memodifikasi file itu. Modul T1 tetap menjadi rekaman FAILED which
utuh; T1b no boleh "memperbaiki" hash-nya.

## 3. Sistem and konfigurasi (identik T1 Â§3)

| Kode | Sistem | Data awal (rasional eksak) | Langkah | Orde | Cakupan |
|------|--------|----------------------------|---------|------|---------|
| S1 | `x' = x^2` | `x(0)=1` | `1/32` | 16 and 24 | t=0..1/2 |
| S2 | `x''=-x` | `x(0)=1, v(0)=0` | `pi/32` (arb) | 24 | 32 and 64 step (t=pi, 2pi) |
| S3 | Kepler sirkular | `(x,y,vx,vy)=(1,0,0,1)`, `G=M=1` | `2*pi/256` | 24 | 10 periode (2560 step) |
| S4 | Three-body figure-eight (RHS) | posisi `(-1,0),(1,0),(0,0)`; kecepatan `(a,b),(a,b),(-2a,-2b)`, `a=347111/10^6`, `b=532728/10^6`; `m=1,G=1` | `T/512`, `T=632591398/10^8` | 24 | 1 periode (512 step) |

Presisi 256 bit. Tidak ada parameter which diubah setelah result terlihat.
Catatan S4 sama with T1: data uji stress for RHS, bukan klaim orbit
figure-eight periodik; konstanta gerak which diperiksa `E0 =
-257428899017/200000000000`, `L0 = 0`, pusat massa `= 0`.

## 4. Kriteria lulus

C1-C6 identik with T1 Â§4 (toleransi sama: C2 `1e-12`/`1e-18` + rasio `1e4`;
C3 `1e-20`; C4 `1e-12`; C5 `1e-10`; C6 determinisme + guard + mutasi
M1-M4 + pemindai AST), ditambah:

**C7 - Pembeda mekanisme (mutasi M5).** Menjalankan T1b with propagasi
bertanda **dimatikan** (yaitu hanya `||J_step|| * S` / radius skalar per
step, persis mekanisme T1) harus mereproduksi kegagalan T1:

- C4: lebar energi checkpoint 1024 melewati `1e-12` **or** abort
  `Picard enclosure failed` paling lambat step 1557; and
- C5: abort `Picard enclosure failed` paling lambat step 42.

Bila M5 no mereproduksi kegagalan itu, diagnosis T1 dianggap keliru and
verdict T1b = INCONCLUSIVE sampai report T1 direvisi.

C6 dilengkapi in T1b: guard menjalankan ulang kampanye, membandingkan payload
kanonik receipt, and memuat minimal mutasi M1 (endpoint in luar selang),
M2 (remainder = 0 on C2), M3 (ubah `E0` in receipt), M4 (suntik
`float(`/`math.` ke salinan modul, pemindai AST harus menolak), M5 (C7).

## 5. Verdict

- **ALL PASS**: C1-C7 semuanya PASS -> registry `A-2026-0040` + sertifikat
  `sha256LF`.
- **PARTIAL**: C1-C5 PASS tetapi C6/C7 belum lengkap; tanpa registry.
- **FAILED**: salah satu C2-C5 gagal (containment dilanggar or toleransi
  terlampaui).
- **INCONCLUSIVE**: dependensi/hash/tool error, or M5 no mereproduksi
  kegagalan T1.

## 6. Falsifier

- ada nilai eksak in luar enclosure which dilaporkan;
- toleransi C2-C5 terlampaui;
- receipt no identik byte antar dua run;
- pemindai menemukan float in jalur tersertifikasi;
- uji mutasi M1-M4 no gagal sebagaimana mestinya;
- M5 no mereproduksi kegagalan T1;
- ada klaim in luar limit Â§1.

## 7. Artefak and urutan eksekusi

1. Commit pra-registrasi ini sebelum kode (hash `sha256LF` dikunci).
2. Implementasi `msaf/ode_validated_block.py` (impor T1 tanpa memodifikasinya).
3. Guard `msaf/tests/test_ode_validated_block.py`.
4. Jalankan kampanye; tulis receipt; verifikasi determinisme dua run.
5. Tulis report `reports/ODE_VALIDATED_T1B_2026-10-21.md` with angka verbatim.
6. Bila `ALL PASS`: registry `A-2026-0040`, HANDOFF, sertifikat `sha256LF`.
7. Suite penuh + `freeze.py --verify`; commit/push hanya bila diminta.

## 8. Batas eksplisit

- Hanya S1-S4 with konfigurasi Â§3; no ada sistem lain.
- "Tervalidasi" = enclosure rigor-terbatas terhadap nilai eksak which
  diketahui; bukan bukti formal and bukan bukti global.
- Tidak ada klaim figure-eight, Soliton/Evans, chaos, ergodisitas, PDE
  kontinu/Navier-Stokes, RH/GRH, faktorisasi, RSA/ECC, Anderson, or fisika.
- Hasil T1 (FAILED) tetap berlaku sebagai rekaman historis; T1b no
  mengubahnya.

## 10. Amendemen pra-implementasi (sebelum kode T1b)

Analisis implementasi - dilakukan **sebelum ada kode T1b maupun result apa
pun** - menemukan dua hal:

- Â§2.2 mewajibkan sisa Taylor disisipkan sebagai arah noise (kolom), tetapi
  Â§2.1 ikut melipat `3*rem` ke `rho`. Lipatan ganda itu no perlu, and
  karena `rho` dikalikan `||J_step||_2` setiap step, suku tersebut akan
  tumbuh `sigma^k` - persis mode kegagalan T1 (for S4 `sigma ~ 31`),
  sehingga metode bertanda no mungkin lulus.
- Jacobian which dipakai adalah **Jacobian interval atas seluruh kotak
  state**; dalam bentuk nilai rata-rata
  `P_x(h) - P_m(h) in J_box * (x - m)`, section polinomial Taylor orde `p`
  already terwakili eksak (tanpa suku kuadratik tambahan).

Amendemen (berlaku sebelum kode and sebelum result apa pun):

1. `3*rem` TIDAK dilipat ke `rho`; sisa Taylor dibawa oleh kolom noise baru
   sesuai Â§2.2.
2. `rho` hanya membawa pembulatan (`<= 1e-70` per step) and **no**
   dikalikan `||J_step||_2` per step. Batas kotak tetap dihitung dari
   `sum_j |S_ij| + rho` seperti Â§2.1.
3. `kappa_nl * r_tot^2` tetap dihitung and disisipkan sebagai kolom noise
   kecil (bukan ke `rho`), and tetap direkam in receipt with kewajiban
   `<= 1e-30` per blok; suku ini konservatif and no dipakai for
   menutupi kesalahan orde dua which no ada.
4. Kolom bertanda adalah satu-satunya mekanisme propagasi; Â§2.2 berlaku
   for semua sisa lokal (Taylor and kuadratik).
5. Tidak ada perubahan lain: sistem, konfigurasi, toleransi C1-C6, kriteria
   C7, verdict, and falsifier tetap. Hash pra-registrasi setelah amendemen
   dicatat in receipt/report; hash versi awal
   `79a4e87965cdc1682d4fa5ddb38cd2719201e316ddba1f2b32004c8379c9b0b1`
   tetap disebut on report sebagai versi sebelum amendemen.

## 11. Amendemen kedua pra-implementasi (sebelum kode T1b)

Koreksi kedua, juga ditemukan sebelum ada kode T1b and sebelum result apa pun:

- Penggabungan dua kolom `S_a`, `S_b` menjadi satu kolom `|S_a| + |S_b|`
  (Â§2.2) **no sound**: himpunan `{xi_a*S_a + xi_b*S_b}` adalah
  jajar-genjang 2 dimensi, sedangkan satu kolom `xi*c` hanya garis `[-c, c]`
  and no memuatnya secara umum. Penggabungan which sound memerlukan
  `n` kolom basis (kembali ke kotak), sehingga no mengurangi jumlah kolom.
- Tanpa penggabungan, jumlah kolom tumbuh `n` per step and biaya
  `J*S` menjadi no wajar (`~10^8` operasi bola for S3+S4).

Amendemen (berlaku sebelum kode and sebelum result apa pun):

1. Bound kotak which dikunci Â§2.1 dihitung with **dua pass ekuivalen**,
   tanpa menyimpan kolom:
   - pass maju: titik tengah `m_k`, kotak Picard, `rem_k`, `quad_k`,
     and Jacobian interval `J_k` (semua tersimpan per step);
   - pass mundur: `P = J_steps ... J_{k+1}`; bound kotak
     `c_out,i = sum_j |P_B[i,j]| * c_in,j`
     `+ sum_k sum_j |P_{B<-k+1}[i,j]| * (rem_k,j + quad_k)`.
   Identitas aljabar: result ini sama with bound which diberikan formulasi
   kolom tanpa penggabungan. Yang dikunci adalah **bound kotak and perkalian
   bertanda**, bukan urutan evaluasinya.
2. Penggabungan kolom Â§2.2 no dipakai karena no sound and no perlu;
   no ada informasi which dibuang.
3. Kotak Picard in dalam blok memakai bound berjalan which sound (boleh
   longgar, mis. `rowsum(|J_k|)*c_k + rem_k + quad_k`); bound **checkpoint**
   dihitung ketat with pass mundur Â§11.1.
4. Tidak ada perubahan lain: sistem, konfigurasi, toleransi C1-C6, kriteria
   C7, verdict, and falsifier tetap.

## 12. Amendemen implementasi (sebelum kampanye bersertifikat)

Catatan jujur tentang posisi amendemen ini: ditulis selama pengembangan
modul T1b, **setelah** jalur diagnostik C4/C5 pernah dijalankan for
mem-debug implementasi, tetapi **sebelum** kampanye bersertifikat
(`python -m msaf.ode_validated_block`) and sebelum receipt ditulis. Tidak ada
toleransi, konfigurasi, ambang Â§2.3, or kriteria which berubah karenanya â€”
hanya koreksi evaluasi mekanisme which already dikunci, ke arah which lebih setia
on Â§2.1/Â§2.4/Â§11.1:

1. **Sisa Taylor dihitung in kotak jalur (path box), bukan kotak masukan.**
   Varian kotak masukan (bound turunan orde `p+1` hanya in sekitar titik
   masukan step) terbukti **no sound** saat testing: ia melanggar
   containment C2/C3 (`contains_2=False`, `contains=False`), karena sisa
   Lagrange melibatkan turunan in sepanjang jalur, bukan in titik awal.
   Modul T1 beku juga mem-batasinya in kotak jalur. Implementasi kembali ke
   `tail = coeff_fn(box, order+1)` with `box` = kotak Picard tervalidasi.
2. **Inflasi kotak Picard.** `delta = (span/16 + r_tot + eps) * factor`,
   `factor` digandakan (maksimal 16 kali) sampai **cek Picard which sama persis**
   lulus. Gerbang soundness (containment `box[i].contains(m + c + h*image)`)
   no diubah; kotak lebih kecil hanya memperketat sisa, and ukuran kotak
   minimum which lulus ditentukan oleh dinamika, bukan oleh parameter bebas.
3. **Produk bertanda kontinu antar blok (koreksi utama Â§2.3).** Sertifikat
   checkpoint dihitung with satu sapuan mundur dari step checkpoint
   sampai step **0**: `P = J_{t-1} ... J_{k+1}` for semua step `k < t`,
   tanpa reset in limit blok. Dasar: Â§11.1 menyatakan result dua-pass **identik**
   with formulasi kolom tanpa penggabungan (which membawa kolom S bertanda
   melintasi seluruh step), and Â§2.4 melarang reset which mengubah data
   ("`S` and `rho` dibawa apa adanya antar blok"). Variasi sapuan-per-blok which
   sempat diuji menyusun kotak antar blok (`|P_blok8| ... |P_blok1|`),
   membuang korelasi tanda antar blok â€” diagnostik menunjukkan komposisi
   itu â‰ˆ `13.6^8 â‰ˆ 8.7e7` per periode for S4, padahal produk bertanda
   sesungguhnya hanya â‰ˆ `1.0e2`. Akibatnya `r_tot` S4 melewati ambang Â§2.3
   (blk7 `2.84054741614440e-30`, blk8 `7.05568884064224e-29`); with sapuan
   kontinu slack maksimum S4 = `9.724087015952757e-36` (lihat Â§5 tetap:
   ambang tetap `1e-30`, no dilonggarkan).
4. **Produk matriks dalam bentuk midpoint-radius.** Produk interval polos
   (`(M1Â±R1)(M2Â±R2)` alami) membungkus lebar Jacobian on panjang sapuan;
   bentuk `M1*M2 Â± (|M1|R2 + R1|M2| + R1R2)` membatasi pertumbuhan radius
   on akumulasi lebar Jacobian per step. Perkalian tetap bertanda on
   section midpoint (dilarang norma skalar Â§2.1 tetap berlaku).
5. **Slack kuadratik non-referensi-diri.** Per blok:
   `slack = kappa_nl * r_tot^2` with `r_tot` = radius kotak sertifikat
   checkpoint **sebelum** slack (tanpa referensi diri), disisipkan sebagai
   radius noise per step on bloknya (Â§10.3, kolom noise, bukan ke `rho`),
   and tercatat in receipt with kewajiban `<= 1e-30` (Â§2.3). Kewajiban Â§2.3
   kini ikut mengunci `all_pass` in kampanye (bukan hanya angka which direkam).
6. **Jacobi interval dihitung over `[midpoint Â± c]`** (kotak masukan step),
   seperti modul T1 beku; bound berjalan `c` dipakai hanya for kotak Picard
   and kotak Jacobi (Â§11.3), no pernah sebagai sertifikat checkpoint.
7. **Presisi.** Semua pemeriksaan C1-C5 dijalankan in dalam
   `flint.ctx.workprec(256)`; jalur in luar konteks presisi menghasilkan
   angka which salah (pernah terdeteksi saat diagnostik: kegagalan containment
   palsu with radius 3e-15) and dilarang for result apa pun which dicatat.
8. Tidak ada perubahan lain: sistem, konfigurasi, toleransi C1-C6, kriteria
   C7, ambang Â§2.3, verdict, and falsifier tetap persis seperti Â§3-Â§6.


