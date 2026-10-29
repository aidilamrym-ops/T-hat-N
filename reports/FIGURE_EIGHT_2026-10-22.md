# T2 - Orbit figure-eight tervalidasi (three-body) - 2026-10-22

**Verdict: FAILED.** K1 PASS; K3 FAILED karena turunan peta Kembali-2
singular secara eksak (simetri translasi-x); K2, K4, and K5 no
dievaluasi karena pipeline berhenti in K3. Registry `A-2026-0041`
**no created**. T2 ditutup sebagai rekaman FAILED which jujur; perbaikan
memerlukan pra-registrasi baru (T2-r2), bukan amendemen T2.

T2 no mengklaim keberadaan maupun keunikan orbit figure-eight. Yang
gagal adalah **sertifikasi Krawczyk** on formulasi 11-dimensi which
terkunci, bukan (belum tentu) orbitnya. Batas klaim Â§8 tetap berlaku.

| Acuan | Nilai |
|---|---|
| Pra-registrasi | `reports/PREREG_FIGURE_EIGHT_THREE_BODY_2026-10-22.md` |
| sha256LF pra-registrasi (terkunci) | `6cc2ef2a613ae9ed5f9d1917624c57e3b1a0cbe915d2a0052dcf8a7f99f27ddf` |
| Linieage pra-registrasi | `7a15ec5` (dibuka) -> `22b0b9d` (amendemen #1) -> `966d400` (amendemen #2, final) |
| Modul T2 | `msaf/figure_eight.py` |
| sha256LF modul T2 | `a36cbe34cc75723bbb21f8cf3422fe7c44ce3367165d05f24eae6046d9e77419` |
| Guard | `msaf/tests/test_figure_eight.py` |
| sha256LF guard | `fbef84d72ee252563c9f029278102296fee1e3356b3af56d2457ce0f4f287be0` |
| Receipt | `reports/figure_eight_three_body_2026-10-22.json` |
| sha256LF receipt | `72309f63d2bd9da14659fda0461ca1a9aaee85eec6f0cc9dabd3cf5e18842fce` |
| Determinisme | dua run `python -m msaf.figure_eight` berturut-turut identik byte (hash sama; run 1c 7,17 menit, run 2 8,06 menit) |
| Lingkungan | Python 3.14.4, `python-flint` 0.9.0, `flint.ctx.workprec(256)`, orde 24 |
| Modul beku (diimpor, no diubah) | `msaf/ode_validated.py` `c1d9b5d6...6251b9`, `msaf/ode_validated_block.py` `42d196a5...0b5b97` |

## 1. Ringkasan result

| Kriteria | Hasil | Angka verbatim utama |
|---|---|---|
| K1 data eksak / AST | **PASS** | `ast_scan_hits: []`; semua konstanta rasional; no ada literal float, `math`, `numpy`, `scipy`, `random`, waktu |
| K2 tabung tervalidasi | **no dievaluasi** | Pipeline berhenti in K3; `checks.K2: null` |
| K3 keberadaan + keunikan lokal | **FAILED** | `DF` singular eksak; inverse titik-tengah gagal; `f_inf` iterasi 1 = `[3.472944747528028818997538721126432618653075900709138328507495961663232947344e-12 +/- 1.28e-88]`; witness translasi residual `[8.889540874705036720169762511019484523641894350159950509743603060615433269673e-22 +/- 1.93e-98]` |
| K4 monodromy | **no dievaluasi** | `checks.K4: null` |
| K5 deskriptor bentuk | **no dievaluasi** | `checks.K5: null`; temuan frame probe dicatat in Â§3 (bukan result tersertifikasi) |
| K6 guard/mutasi | **no terpenuhi penuh** | Determinisme dijalankan; M1 fail-fast via Picard (bukan gerbang K2), M3/M4 bekerja; M2 and M5 **no diskriminatif** karena K3 already singular (Â§5) |

Verdict mengikuti Â§5: K3 gagal -> **FAILED**; K4/K5 no pernah dievaluasi
sehingga aturan "INCONCLUSIVE bila K3 PASS tetapi K4/K5 gagal" no
berlaku. Tidak ada dasar for `ALL PASS` maupun registry.

## 2. Sebab K3: simetri translasi-x eksak

Peta dua-kembali `F` on seksi `Sigma = {q3y = 0, v3y < 0}` invarian
terhadap translasi seragam sumbu-x. Untuk

```
e = (1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0)
```

and setiap `c`, translasi semua posisi-x awal with `c` no mengubah
vektor relatif, percepatan, maupun waktu silang `q3y = 0`; karenanya

```
P^2(x + c e) = P^2(x) + c e      =>      F(x + c e) = F(x).
```

Diferensialkan: `DF(x) e = 0` **eksak**. Jadi `DF` no invertibel, and
titik tetap `F(x*) = 0` no terisolasi: for `c` kecil, `x* + c e` juga
titik tetap in dalam kotak B. Klaim "tepat satu titik tetap in B" adalah
**salah** for formulasi 11-dimensi which terkunci.

Witness tersertifikasi in receipt dihitung dari enclosure interval `DF`
(literal `e` in atas): kesebelas komponen `DF @ e` memuat nol, with
residual maksimum `8.8895e-22` (lebar < `1e-21`). Ini bukan noise: ia
membuktikan arah nol which eksak.

Krawczyk membutuhkan `W ~ DF^{-1}`. Invers matriks titik-tengah in
presisi 256-bit melempar `ZeroDivisionError: matrix is singular`; modul
menangkapnya and mencatat K3 FAILED (bukan crash). Tidak ada penambahan
presisi which dapat memperbaiki ini: singularitasnya struktural.

Catatan penting: probe FD in pra-registrasi melaporkan `sigma_min(DF) =
1.5e-9`; itu adalah **lantai noise FD**, bukan nilai sesungguhnya. Prereg
Â§2f sendiri already menulis "sigma_min no terukur andal in ganda". Nilai
eksak which benar adalah 0 for arah translasi-x. Probe float 96 step
menemukan dua arah hampir-nol (~5e-15), konsisten with simetri tambahan
(translasi/boost/keluarga energi); hanya arah translasi-x which
disertifikasi in receipt ini.

## 3. K5: temuan frame (diagnostik probe, bukan verdict)

K5 no dievaluasi karena K3 gagal lebih dulu. Namun probe pra-kampanye
menemukan kekeliruan frame which harus diungkap:

- Probe mengukur waktu relatif terhadap `x_c2 = 3.162988113`, sedangkan
  kampanye memakai waktu absolut dari `t = 0` (benih Â§2d).
- Jendela K5(a) which terkunci, `2.108735283` and `4.217376381`, adalah
  waktu relatif, bukan absolut. Silang-naik `q3y` which sebenarnya berada
  in `t = 1.054388268` and `t = 5.271750210` (absolut).
- Pemeriksaan aritmetika: `4.217376381 = 3.162988113 + 1.054388268`
  (anchor `x_c2`), sedangkan `2.108735283 = 5.271750210 - 3.163014927`
  (anchor `w1`). Dua jendela bahkan memakai dua anchor berbeda
  (selisih anchor `2.6814e-5`).
- Akibatnya no ada silang-naik in dalam kedua jendela terkunci; uji
  tanda `q3y` gagal sebelum range `q3x` diuji.
- K5(b) range `q3x` juga tertukar: on `w1` nilai aktual ~0 (range
  terkunci `[-6e-5, -3e-5]`), on `w2` nilai aktual ~`-4.77e-5` (range
  terkunci `[-1e-6, +1e-6]`).
- Margin amendemen #2 (`0.0061` in `w1`, `0.0107` in `w2`) juga tertukar
  posisinya; ini hanya disclosure, karena gerbang which dikunci adalah
  `v3y <= -1/2` and nilai `v3y` in `w1/w2` (`-1.065`/`-0.612`) lolos.

Semua angka in Â§3 berasal dari probe diagnostik, **bukan** dari receipt
FAILED; no ada klaim K5 which created.

## 4. Riwayat eksekusi and kegagalan

1. **Run 1 (modul awal).** Kampanye berhenti with
   `ZeroDivisionError: matrix is singular` in `_inverse_mid` setelah 6,49
   menit; receipt no ditulis. Ini adalah gejala pertama singularitas
   `DF`.
2. **Run 1b (penanganan crash).** Inverse singular ditangkap; K1 justru
   FAILED karena scanner AST baru sendiri memakai nama `float`
   (`name:float:1089`) â€” pelanggaran K1 which jujur dicatat, bukan
   disembunyikan. Receipt run 1b (hash `d5344371...`) **superseded**.
3. **Run 1c (final).** Scanner mengganti klasifikasi literal float menjadi
   `type(...).__name__`; K1 PASS. K3 FAILED with witness translasi;
   receipt `72309f63...`; 7,17 menit.
4. **Run 2 (determinisme).** Payload identik byte with run 1c; sha256LF
   receipt sama; 7,24 menit.

Kegagalan K1 in run 1b and `ZeroDivisionError` in run 1 adalah cacat
implementasi which diperbaiki **tanpa** mengubah ambang, konstanta, or
scope pra-registrasi; keduanya diungkap in sini.

5. **Suite penuh and freeze.** `pytest -q msaf/tests`: **629 passed, 1
   skipped** (29:19), termasuk guard T2 8/8 and guard T1b;
   `python audit_quantum/freeze.py --verify`: **OK**, 14 pin, digest
   `f6352884d85bab5a68c01a4e1d4a73618304464fd300d56bce1f8cc2f62baa25`.

## 5. K6 and mutasi

| Mutasi | Perilaku aktual | Status |
|---|---|---|
| M1 `REMAINDER_FACTOR := 1e70` | Berhenti fail-fast lebih awal dari checkpoint K2: `aborted at step 2: Picard enclosure failed` (radius sisa which digelembungkan menggagalkan kotak Picard). Gerbang lebar K2 no tercapai | **Bekerja sebagai fail-fast, bukan lewat gerbang K2** |
| M2 benih `q1x += 1e-3` | K3 FAILED, tetapi karena `DF` singular which sama; bukan karena aturan monoton | **Tidak diskriminatif** |
| M3 satu byte receipt diubah | Perbandingan payload/hash mendeteksi perubahan | **Bekerja** |
| M4 injeksi float literal / `float(x)` | `_ast_hits` menolak literal (`literal:float:...`) and nama (`name:float:...`); modul bersih | **Bekerja** |
| M5 `SWEEP_SIGNED := False` | K3 FAILED, tetapi karena singularitas `DF` which sama; ledakan `DF(B)` in kampanye kotak no pernah tercapai | **Tidak diskriminatif** |

Karena kampanye jujur already gagal in inversi pertama, M2 and M5 no
menguji mekanisme which dimaksud Â§9.3. K6 karenanya **no terpenuhi
penuh**; ini konsisten with verdict FAILED and menjadi alasan tambahan
no ada registry. M1 tetap berguna sebagai uji fail-fast, meskipun
abort-nya lewat Picard (step 2), bukan gerbang lebar K2; M3/M4 menguji
integritas receipt and AST.

## 6. Mengapa no ada registry A-2026-0041

Â§5 menetapkan `ALL PASS (K1-K6)` sebagai satu-satunya syarat registry.
K3 gagal secara struktural and K6 no terpenuhi penuh, jadi no ada
`ALL PASS`. `reports/FENCE_REGISTRY.md` no diubah and `A-2026-0041`
no created. T2 tetap tercatat sebagai trek FAILED; T1b (`A-2026-0040`)
and modul beku no terpengaruh.

## 7. Perbaikan which diperlukan: T2-r2 (pra-registrasi baru)

T2 no boleh diamendemen setelah kode ditulis (Â§9 baris 409-411).
Perbaikan harus lewat trek baru with pra-registrasi which ditulis
**sebelum** kode:

1. **Quotien simetri.** Bekerja in frame pusat massa: `q1+q2+q3 = 0`,
   `p1+p2+p3 = 0` (4 constraint), and hilangkan arah keluarga energi
   with mengunci energi or memperlakukan periode `T` sebagai variabel
   with kondisi fase. Analisis simetri rotasi/`L = 0` sebelum mengunci
   dimensi seksi. Klaim keunikan harus dinyatakan **modulo simetri**
   (orbit which ditranslasikan/boosted bukan objek berbeda).
2. **Frame K5 absolut.** Semua waktu diukur dari `t = 0` benih (or dari
   silang-turun pertama which tersertifikasi, secara konsisten); jendela
   silang-naik menjadi `1.054388268` and `5.271750210`; range `q3x` in
   `w1/w2` ditukar/diturunkan dari orbit tersertifikasi, bukan dari probe
   `x_c2`.
3. **Mutasi which diskriminatif.** M2 harus menggeser arah transverse
   terhadap manifold solusi (bukan arah simetri); M5 harus menguji
   ledakan `DF(B)` on kampanye kotak setelah K3 reduced terbukti PASS.
4. **Modul baru** (bukan mengedit `msaf/figure_eight.py`), receipt baru,
   and guard baru; T2b (spektrum) tetap in luar scope.

## 8. Batas klaim

T2 **no** mengklaim keberadaan orbit periodik, keunikan lokal, tube
tervalidasi, monodromy, or deskriptor bentuk: K3 gagal and K2/K4/K5
no dievaluasi. Tidak ada klaim RH/PDE/chaos/ergodisitas/Soliton/Evans/
fisika/analitik-kontinuasi/prioritas/pembuktian formal Lean. T1b S4 tetap
uji-stress tersegel, bukan klaim figure-eight. Angka probe in Â§3 bukan
result tersertifikasi.

## 9. Artefak

- `msaf/figure_eight.py` (baru; sha256LF in tabel).
- `msaf/tests/test_figure_eight.py` (guard baru; sha256LF in tabel).
- `reports/figure_eight_three_body_2026-10-22.json` (receipt FAILED;
  sha256LF `72309f63...`; dua run byte-identical).
- Modul beku `msaf/ode_validated.py` and `msaf/ode_validated_block.py`
  no berubah; hash cocok with pin `A-2026-0039`/`A-2026-0040`.
- Registry `A-2026-0041`: **no created**.


