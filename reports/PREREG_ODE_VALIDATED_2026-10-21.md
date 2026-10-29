# Pra-registrasi: T1 - Integrator ODE tervalidasi (milestone prasyarat Daftar-B) - 2026-10-21

**Status:** scope DIKUNCI for milestone T1; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis and in-commit sebelum kode T1. Hash `sha256LF`
file ini dicatat in receipt and report.

**Paket:** milestone prasyarat dari
[`reports/DAFTAR_MASALAH_KERJA.md`](DAFTAR_MASALAH_KERJA.md) Â§4, for membuka
item Daftar-B:

- item 16 (Three-Body): "SYARAT MASUK: integrator ODE tervalidasi dulu";
- item 20 (Soliton): "SYARAT MASUK: sama with Three-Body".

Satu milestone membuka dua item; itulah alasan trek ini dipilih pertama in
antara tiga kandidat prasyarat Daftar-B.

**Berkas target:** `msaf/ode_validated.py` (baru), guard
`msaf/tests/test_ode_validated.py` (baru), report
`reports/ODE_VALIDATED_2026-10-21.md`, receipt
`reports/ode_validated_2026-10-21.json`.

**Dependensi:** Python 3.14, `python-flint==0.9.0` (`arb` ball arithmetic),
`fractions` (stdlib). Tidak ada dependensi float in jalur tersertifikasi.

**Registry which direncanakan:** `A-2026-0040`, hanya bila verdict `ALL PASS`
and integritas PASS.

**Tidak mengubah:** V1-V6, `A-2026-0022`-`A-2026-0039`, `ci.yml`, workflow
spec, `lean/lakefile.toml`, freeze pins, artefak beku.

## 1. Maksud and limit

Milestone ini membangun **kapabilitas**: integrator ODE which setiap langkahnya
menghasilkan *enclosure* (selang which dijamin memuat solusi eksak), memakai
aritmetika bola `arb` + deret Taylor with sisa (remainder) eksplisit.

Yang disertifikasi adalah **mesin enclosure**, bukan fisika:

- setiap nilai which dilaporkan adalah selang, bukan titik;
- setiap selang harus memuat nilai eksak which diketahui (konstanta gerak
  rasional or solusi eksak rasional);
- no ada fallback ke float in jalur tersertifikasi.

Milestone ini **bukan**:

- bukti keberadaan/stabilitas orbit figure-eight;
- perhitungan fungsi Evans / indeks stabilitas Soliton;
- klaim chaos, ergodisitas, globalitas, or fisika;
- bukti formal Lean (verifikasi in sini adalah verifikasi numerik
  rigor-terbatas, bukan bukti teorema).

Setelah milestone tersegel, item 16 and 20 Daftar-B boleh masuk A-list;
pekerjaan figure-eight/Evans menjadi trek berikutnya, bukan section paket ini.

## 2. Arsitektur

**2.1 Aritmetika bola.** `flint.arb` on presisi 256 bit. Sebuah bola
`[m +/- r]` dianggap memuat nilai eksak `v` bila `|v - m| <= r`. Tidak ada
konversi ke float for keputusan lulus/gagal.

**2.2 Deret Taylor terpotong.** Tipe `Series` atas koefisien `arb` mendukung
`+`, `-`, `*`, `/`, `sqrt`, and `pow(-3/2)` (dibutuhkan oleh `r^{-3}` on
Kepler and three-body). Semua operasi memakai aturan bola.

**2.3 Langkah Taylor.** Untuk `x' = f(x,t)`, koefisien Taylor `x_k` dihitung
with rekurensi jet orde `p`; sisa step dibatasi with mengevaluasi suku
Taylor ke-`(p+1)` on kotak step (Taylor remainder). Orde and step
dikunci in Â§3.

**2.4 Audit containment.** Setiap pemeriksaan menyimpan: deskriptor waktu,
selang komponen, nilai eksak pembanding (Fraction), and verdict containment.
Receipt no memuat field runtime.

## 3. Sistem and konfigurasi which dikunci

| Kode | Sistem | Data awal (rasional eksak) | Langkah | Orde | Cakupan |
|------|--------|----------------------------|---------|------|---------|
| S1 | `x' = x^2` | `x(0)=1` | `1/32` | 16 and 24 | t=0..1/2 |
| S2 | `x''=-x` | `x(0)=1, v(0)=0` | `pi/32` (arb) | 24 | 32 and 64 step (t=pi, 2pi) |
| S3 | Kepler sirkular | `(x,y,vx,vy)=(1,0,0,1)`, `G=M=1` | `2*pi/256` | 24 | 10 periode (2560 step) |
| S4 | Three-body figure-eight (RHS) | posisi `(-1,0),(1,0),(0,0)`; kecepatan `(a,b),(a,b),(-2a,-2b)`, `a=347111/10^6`, `b=532728/10^6`; `m=1,G=1` | `T/512`, `T=632591398/10^8` | 24 | 1 periode (512 step) |

Presisi: 256 bit for semua sistem. Tidak ada parameter which diubah setelah
result terlihat.

Catatan S4: data awal and periode in atas adalah **data uji stress** for RHS
three-body; paket ini **no** mengklaim bahwa data tersebut menghasilkan
orbit figure-eight periodik. Konstanta gerak which diperiksa adalah energi
`E0 = -257428899017/200000000000` and momentum sudut `L0 = 0` (keduanya eksak
for data awal which dikunci), ditambah pusat massa posisi/kecepatan `= 0`.

## 4. Kriteria lulus (C1-C6)

**C1 - Primitif bola sound.** Untuk 1000 pasangan rasional dari generator
deterministik (LCG `s_{n+1} = (1103515245*s_n + 12345) mod 2^31`, seed
20261021), operasi `+`, `-`, `*`, `/` menghasilkan bola which memuat result
Fraction eksak; for 1000 rasional nonnegatif, `sqrt` menghasilkan `[lo,hi]`
with `lo^2 <= q <= hi^2` (dicek with aritmetika eksak).

**C2 - Langkah Taylor nonlinear.** S1 on `t=1/2` (solusi eksak `x=2`):

- orde 16: enclosure memuat 2 and lebar `<= 1e-12`;
- orde 24: enclosure memuat 2 and lebar `<= 1e-18`;
- `lebar(24) <= lebar(16)/10^4` (konvergensi orde terlihat).

**C3 - Osilator harmonik.** S2: on 32 step (t=pi) enclosure memuat
`(x,v)=(-1,0)`; on 64 step (t=2pi) memuat `(1,0)`; lebar tiap komponen
`<= 1e-20`.

**C4 - Kepler sirkular.** S3: on setiap checkpoint (setiap 256 step,
termasuk akhir), selang energi memuat `-1/2` and selang momentum sudut memuat
`1`; lebar maksimum keduanya `<= 1e-12`.

**C5 - Three-body (RHS target).** S4: on setiap checkpoint (setiap 64
step), selang energi memuat `E0` eksak, selang momentum sudut memuat `0`,
and pusat massa posisi/kecepatan memuat `0`; lebar maksimum energi `<= 1e-10`.

**C6 - Determinisme and integritas guard.**

- Dua run berturut-turut menghasilkan payload kanonik receipt identik byte.
- Guard `msaf/tests/test_ode_validated.py` menjalankan ulang kampanye and
  membandingkan payload with receipt.
- Guard memuat minimal 4 uji mutasi which harus GAGAL bila enforcement
  dilemahkan:
  - M1: mengganti satu endpoint selang sehingga nilai eksak in luar selang;
  - M2: menetapkan remainder = 0 on pemeriksaan C2;
  - M3: mengubah `E0` in receipt;
  - M4: menyuntikkan `float(`/`math.` ke salinan modul and mengharuskan
    pemindai AST menolaknya.
- Pemindai AST `msaf/ode_validated.py`: no ada node Name/Call `float`,
  `math`, `numpy`, `scipy` in jalur tersertifikasi.

## 5. Verdict

- **ALL PASS**: C1-C6 semuanya PASS.
- **PARTIAL**: C1-C5 PASS tetapi C6 belum lengkap (mis. uji mutasi kurang);
  no ada entri registry; status dicatat in HANDOFF.
- **FAILED**: salah satu C2-C5 gagal (containment dilanggar or toleransi
  terlampaui).
- **INCONCLUSIVE**: dependensi no tersedia, tool error, or hash mismatch.

Registry `A-2026-0040` hanya bila verdict `ALL PASS`.

## 6. Falsifier

Paket ini falsified bila:

- ada nilai eksak which jatuh in luar enclosure which dilaporkan;
- toleransi C2-C5 terlampaui;
- receipt no identik byte antar dua run;
- pemindai menemukan float in jalur tersertifikasi;
- uji mutasi M1-M4 no gagal sebagaimana mestinya (artinya guard no
  menguji klaim).

## 7. Artefak and urutan eksekusi

1. Commit pra-registrasi ini sebelum kode (hash `sha256LF` dikunci).
2. Implementasi `msaf/ode_validated.py`.
3. Guard `msaf/tests/test_ode_validated.py`.
4. Jalankan kampanye; tulis receipt.
5. Tulis report `reports/ODE_VALIDATED_2026-10-21.md` with angka verbatim.
6. Bila `ALL PASS`: registry `A-2026-0040`, HANDOFF, sertifikat `sha256LF`.
7. Suite penuh + `freeze.py --verify`; commit/push hanya bila diminta.

## 8. Kapabilitas terukur (probe, sebelum penguncian)

- `arb` 256-bit: 200.000 iterasi x 3 operasi bola = 0,55 dtk
  (~1,1 juta operasi bola/dtk).
- `arb.sin`: 20.000 evaluasi = 0,08 dtk.
- `arb.pi()` tersedia on presisi 256 bit.
- Perkiraan kampanye: S3 (2.560 step, orde 24) and S4 (512 step,
  orde 24) berada on kisaran 10^6-10^7 operasi bola: detik hingga beberapa
  menit. Probe hanya mengukur waktu; no mengunci result apa pun.

## 9. Batas eksplisit

- Hanya sistem S1-S4 with konfigurasi Â§3; no ada sistem lain.
- "Tervalidasi" = enclosure rigor-terbatas terhadap nilai eksak which diketahui;
  bukan bukti formal Lean and bukan bukti global.
- Tidak ada klaim figure-eight, Soliton/Evans, chaos, ergodisitas, PDE kontinu,
  Navier-Stokes, RH/GRH, faktorisasi, RSA/ECC, Anderson, or fisika.
- Tidak mengubah modul beku; `python-flint` dipakai on versi which terpasang
  and dicatat in receipt.


