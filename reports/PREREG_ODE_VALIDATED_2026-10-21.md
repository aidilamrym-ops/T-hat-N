# Pra-registrasi: T1 - Integrator ODE tervalidasi (milestone prasyarat Daftar-B) - 2026-10-21

**Status:** scope DIKUNCI untuk milestone T1; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis dan di-commit sebelum kode T1. Hash `sha256LF`
berkas ini dicatat di receipt dan laporan.

**Paket:** milestone prasyarat dari
[`reports/DAFTAR_MASALAH_KERJA.md`](DAFTAR_MASALAH_KERJA.md) §4, untuk membuka
item Daftar-B:

- item 16 (Three-Body): "SYARAT MASUK: integrator ODE tervalidasi dulu";
- item 20 (Soliton): "SYARAT MASUK: sama dengan Three-Body".

Satu milestone membuka dua item; itulah alasan trek ini dipilih pertama di
antara tiga kandidat prasyarat Daftar-B.

**Berkas target:** `msaf/ode_validated.py` (baru), guard
`msaf/tests/test_ode_validated.py` (baru), laporan
`reports/ODE_VALIDATED_2026-10-21.md`, receipt
`reports/ode_validated_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`arb` ball arithmetic),
`fractions` (stdlib). Tidak ada dependensi float di jalur tersertifikasi.

**Registry yang direncanakan:** `A-2026-0040`, hanya bila verdict `ALL PASS`
dan integritas PASS.

**Tidak mengubah:** V1-V6, `A-2026-0022`-`A-2026-0039`, `ci.yml`, workflow
spec, `lean/lakefile.toml`, freeze pins, artefak beku.

## 1. Maksud dan batas

Milestone ini membangun **kapabilitas**: integrator ODE yang setiap langkahnya
menghasilkan *enclosure* (selang yang dijamin memuat solusi eksak), memakai
aritmetika bola `arb` + deret Taylor dengan sisa (remainder) eksplisit.

Yang disertifikasi adalah **mesin enclosure**, bukan fisika:

- setiap nilai yang dilaporkan adalah selang, bukan titik;
- setiap selang harus memuat nilai eksak yang diketahui (konstanta gerak
  rasional atau solusi eksak rasional);
- tidak ada fallback ke float di jalur tersertifikasi.

Milestone ini **bukan**:

- bukti keberadaan/stabilitas orbit figure-eight;
- perhitungan fungsi Evans / indeks stabilitas Soliton;
- klaim chaos, ergodisitas, globalitas, atau fisika;
- bukti formal Lean (verifikasi di sini adalah verifikasi numerik
  rigor-terbatas, bukan bukti teorema).

Setelah milestone tersegel, item 16 dan 20 Daftar-B boleh masuk A-list;
pekerjaan figure-eight/Evans menjadi trek berikutnya, bukan bagian paket ini.

## 2. Arsitektur

**2.1 Aritmetika bola.** `flint.arb` pada presisi 256 bit. Sebuah bola
`[m +/- r]` dianggap memuat nilai eksak `v` bila `|v - m| <= r`. Tidak ada
konversi ke float untuk keputusan lulus/gagal.

**2.2 Deret Taylor terpotong.** Tipe `Series` atas koefisien `arb` mendukung
`+`, `-`, `*`, `/`, `sqrt`, dan `pow(-3/2)` (dibutuhkan oleh `r^{-3}` pada
Kepler dan three-body). Semua operasi memakai aturan bola.

**2.3 Langkah Taylor.** Untuk `x' = f(x,t)`, koefisien Taylor `x_k` dihitung
dengan rekurensi jet orde `p`; sisa langkah dibatasi dengan mengevaluasi suku
Taylor ke-`(p+1)` pada kotak langkah (Taylor remainder). Orde dan langkah
dikunci di §3.

**2.4 Audit containment.** Setiap pemeriksaan menyimpan: deskriptor waktu,
selang komponen, nilai eksak pembanding (Fraction), dan verdict containment.
Receipt tidak memuat field runtime.

## 3. Sistem dan konfigurasi yang dikunci

| Kode | Sistem | Data awal (rasional eksak) | Langkah | Orde | Cakupan |
|------|--------|----------------------------|---------|------|---------|
| S1 | `x' = x^2` | `x(0)=1` | `1/32` | 16 dan 24 | t=0..1/2 |
| S2 | `x''=-x` | `x(0)=1, v(0)=0` | `pi/32` (arb) | 24 | 32 dan 64 langkah (t=pi, 2pi) |
| S3 | Kepler sirkular | `(x,y,vx,vy)=(1,0,0,1)`, `G=M=1` | `2*pi/256` | 24 | 10 periode (2560 langkah) |
| S4 | Three-body figure-eight (RHS) | posisi `(-1,0),(1,0),(0,0)`; kecepatan `(a,b),(a,b),(-2a,-2b)`, `a=347111/10^6`, `b=532728/10^6`; `m=1,G=1` | `T/512`, `T=632591398/10^8` | 24 | 1 periode (512 langkah) |

Presisi: 256 bit untuk semua sistem. Tidak ada parameter yang diubah setelah
hasil terlihat.

Catatan S4: data awal dan periode di atas adalah **data uji stress** untuk RHS
three-body; paket ini **tidak** mengklaim bahwa data tersebut menghasilkan
orbit figure-eight periodik. Konstanta gerak yang diperiksa adalah energi
`E0 = -257428899017/200000000000` dan momentum sudut `L0 = 0` (keduanya eksak
untuk data awal yang dikunci), ditambah pusat massa posisi/kecepatan `= 0`.

## 4. Kriteria lulus (C1-C6)

**C1 - Primitif bola sound.** Untuk 1000 pasangan rasional dari generator
deterministik (LCG `s_{n+1} = (1103515245*s_n + 12345) mod 2^31`, seed
20261021), operasi `+`, `-`, `*`, `/` menghasilkan bola yang memuat hasil
Fraction eksak; untuk 1000 rasional nonnegatif, `sqrt` menghasilkan `[lo,hi]`
dengan `lo^2 <= q <= hi^2` (dicek dengan aritmetika eksak).

**C2 - Langkah Taylor nonlinear.** S1 pada `t=1/2` (solusi eksak `x=2`):

- orde 16: enclosure memuat 2 dan lebar `<= 1e-12`;
- orde 24: enclosure memuat 2 dan lebar `<= 1e-18`;
- `lebar(24) <= lebar(16)/10^4` (konvergensi orde terlihat).

**C3 - Osilator harmonik.** S2: pada 32 langkah (t=pi) enclosure memuat
`(x,v)=(-1,0)`; pada 64 langkah (t=2pi) memuat `(1,0)`; lebar tiap komponen
`<= 1e-20`.

**C4 - Kepler sirkular.** S3: pada setiap checkpoint (setiap 256 langkah,
termasuk akhir), selang energi memuat `-1/2` dan selang momentum sudut memuat
`1`; lebar maksimum keduanya `<= 1e-12`.

**C5 - Three-body (RHS target).** S4: pada setiap checkpoint (setiap 64
langkah), selang energi memuat `E0` eksak, selang momentum sudut memuat `0`,
dan pusat massa posisi/kecepatan memuat `0`; lebar maksimum energi `<= 1e-10`.

**C6 - Determinisme dan integritas guard.**

- Dua run berturut-turut menghasilkan payload kanonik receipt identik byte.
- Guard `msaf/tests/test_ode_validated.py` menjalankan ulang kampanye dan
  membandingkan payload dengan receipt.
- Guard memuat minimal 4 uji mutasi yang harus GAGAL bila enforcement
  dilemahkan:
  - M1: mengganti satu endpoint selang sehingga nilai eksak di luar selang;
  - M2: menetapkan remainder = 0 pada pemeriksaan C2;
  - M3: mengubah `E0` di receipt;
  - M4: menyuntikkan `float(`/`math.` ke salinan modul dan mengharuskan
    pemindai AST menolaknya.
- Pemindai AST `msaf/ode_validated.py`: tidak ada node Name/Call `float`,
  `math`, `numpy`, `scipy` di jalur tersertifikasi.

## 5. Verdict

- **ALL PASS**: C1-C6 semuanya PASS.
- **PARTIAL**: C1-C5 PASS tetapi C6 belum lengkap (mis. uji mutasi kurang);
  tidak ada entri registry; status dicatat di HANDOFF.
- **FAILED**: salah satu C2-C5 gagal (containment dilanggar atau toleransi
  terlampaui).
- **INCONCLUSIVE**: dependensi tidak tersedia, tool error, atau hash mismatch.

Registry `A-2026-0040` hanya bila verdict `ALL PASS`.

## 6. Falsifier

Paket ini falsified bila:

- ada nilai eksak yang jatuh di luar enclosure yang dilaporkan;
- toleransi C2-C5 terlampaui;
- receipt tidak identik byte antar dua run;
- pemindai menemukan float di jalur tersertifikasi;
- uji mutasi M1-M4 tidak gagal sebagaimana mestinya (artinya guard tidak
  menguji klaim).

## 7. Artefak dan urutan eksekusi

1. Commit pra-registrasi ini sebelum kode (hash `sha256LF` dikunci).
2. Implementasi `msaf/ode_validated.py`.
3. Guard `msaf/tests/test_ode_validated.py`.
4. Jalankan kampanye; tulis receipt.
5. Tulis laporan `reports/ODE_VALIDATED_2026-10-21.md` dengan angka verbatim.
6. Bila `ALL PASS`: registry `A-2026-0040`, HANDOFF, sertifikat `sha256LF`.
7. Suite penuh + `freeze.py --verify`; commit/push hanya bila diminta.

## 8. Kapabilitas terukur (probe, sebelum penguncian)

- `arb` 256-bit: 200.000 iterasi x 3 operasi bola = 0,55 dtk
  (~1,1 juta operasi bola/dtk).
- `arb.sin`: 20.000 evaluasi = 0,08 dtk.
- `arb.pi()` tersedia pada presisi 256 bit.
- Perkiraan kampanye: S3 (2.560 langkah, orde 24) dan S4 (512 langkah,
  orde 24) berada pada kisaran 10^6-10^7 operasi bola: detik hingga beberapa
  menit. Probe hanya mengukur waktu; tidak mengunci hasil apa pun.

## 9. Batas eksplisit

- Hanya sistem S1-S4 dengan konfigurasi §3; tidak ada sistem lain.
- "Tervalidasi" = enclosure rigor-terbatas terhadap nilai eksak yang diketahui;
  bukan bukti formal Lean dan bukan bukti global.
- Tidak ada klaim figure-eight, Soliton/Evans, chaos, ergodisitas, PDE kontinu,
  Navier-Stokes, RH/GRH, faktorisasi, RSA/ECC, Anderson, atau fisika.
- Tidak mengubah modul beku; `python-flint` dipakai pada versi yang terpasang
  dan dicatat di receipt.
