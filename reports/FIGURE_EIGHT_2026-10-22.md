# T2 - Orbit figure-eight tervalidasi (three-body) - 2026-10-22

**Verdict: FAILED.** K1 PASS; K3 FAILED karena turunan peta Kembali-2
singular secara eksak (simetri translasi-x); K2, K4, dan K5 tidak
dievaluasi karena pipeline berhenti di K3. Registry `A-2026-0041`
**tidak dibuat**. T2 ditutup sebagai rekaman FAILED yang jujur; perbaikan
memerlukan pra-registrasi baru (T2-r2), bukan amendemen T2.

T2 tidak mengklaim keberadaan maupun keunikan orbit figure-eight. Yang
gagal adalah **sertifikasi Krawczyk** pada formulasi 11-dimensi yang
terkunci, bukan (belum tentu) orbitnya. Batas klaim §8 tetap berlaku.

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
| Modul beku (diimpor, tidak diubah) | `msaf/ode_validated.py` `c1d9b5d6...6251b9`, `msaf/ode_validated_block.py` `42d196a5...0b5b97` |

## 1. Ringkasan hasil

| Kriteria | Hasil | Angka verbatim utama |
|---|---|---|
| K1 data eksak / AST | **PASS** | `ast_scan_hits: []`; semua konstanta rasional; tidak ada literal float, `math`, `numpy`, `scipy`, `random`, waktu |
| K2 tabung tervalidasi | **tidak dievaluasi** | Pipeline berhenti di K3; `checks.K2: null` |
| K3 keberadaan + keunikan lokal | **FAILED** | `DF` singular eksak; inverse titik-tengah gagal; `f_inf` iterasi 1 = `[3.472944747528028818997538721126432618653075900709138328507495961663232947344e-12 +/- 1.28e-88]`; witness translasi residual `[8.889540874705036720169762511019484523641894350159950509743603060615433269673e-22 +/- 1.93e-98]` |
| K4 monodromy | **tidak dievaluasi** | `checks.K4: null` |
| K5 deskriptor bentuk | **tidak dievaluasi** | `checks.K5: null`; temuan frame probe dicatat di §3 (bukan hasil tersertifikasi) |
| K6 guard/mutasi | **tidak terpenuhi penuh** | Determinisme dijalankan; M1 fail-fast via Picard (bukan gerbang K2), M3/M4 bekerja; M2 dan M5 **tidak diskriminatif** karena K3 sudah singular (§5) |

Verdict mengikuti §5: K3 gagal -> **FAILED**; K4/K5 tidak pernah dievaluasi
sehingga aturan "INCONCLUSIVE bila K3 PASS tetapi K4/K5 gagal" tidak
berlaku. Tidak ada dasar untuk `ALL PASS` maupun registry.

## 2. Sebab K3: simetri translasi-x eksak

Peta dua-kembali `F` pada seksi `Sigma = {q3y = 0, v3y < 0}` invarian
terhadap translasi seragam sumbu-x. Untuk

```
e = (1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0)
```

dan setiap `c`, translasi semua posisi-x awal dengan `c` tidak mengubah
vektor relatif, percepatan, maupun waktu silang `q3y = 0`; karenanya

```
P^2(x + c e) = P^2(x) + c e      =>      F(x + c e) = F(x).
```

Diferensialkan: `DF(x) e = 0` **eksak**. Jadi `DF` tidak invertibel, dan
titik tetap `F(x*) = 0` tidak terisolasi: untuk `c` kecil, `x* + c e` juga
titik tetap di dalam kotak B. Klaim "tepat satu titik tetap di B" adalah
**salah** untuk formulasi 11-dimensi yang terkunci.

Witness tersertifikasi di receipt dihitung dari enclosure interval `DF`
(literal `e` di atas): kesebelas komponen `DF @ e` memuat nol, dengan
residual maksimum `8.8895e-22` (lebar < `1e-21`). Ini bukan noise: ia
membuktikan arah nol yang eksak.

Krawczyk membutuhkan `W ~ DF^{-1}`. Invers matriks titik-tengah di
presisi 256-bit melempar `ZeroDivisionError: matrix is singular`; modul
menangkapnya dan mencatat K3 FAILED (bukan crash). Tidak ada penambahan
presisi yang dapat memperbaiki ini: singularitasnya struktural.

Catatan penting: probe FD di pra-registrasi melaporkan `sigma_min(DF) =
1.5e-9`; itu adalah **lantai noise FD**, bukan nilai sesungguhnya. Prereg
§2f sendiri sudah menulis "sigma_min tidak terukur andal di ganda". Nilai
eksak yang benar adalah 0 untuk arah translasi-x. Probe float 96 langkah
menemukan dua arah hampir-nol (~5e-15), konsisten dengan simetri tambahan
(translasi/boost/keluarga energi); hanya arah translasi-x yang
disertifikasi di receipt ini.

## 3. K5: temuan frame (diagnostik probe, bukan verdict)

K5 tidak dievaluasi karena K3 gagal lebih dulu. Namun probe pra-kampanye
menemukan kekeliruan frame yang harus diungkap:

- Probe mengukur waktu relatif terhadap `x_c2 = 3.162988113`, sedangkan
  kampanye memakai waktu absolut dari `t = 0` (benih §2d).
- Jendela K5(a) yang terkunci, `2.108735283` dan `4.217376381`, adalah
  waktu relatif, bukan absolut. Silang-naik `q3y` yang sebenarnya berada
  di `t = 1.054388268` dan `t = 5.271750210` (absolut).
- Pemeriksaan aritmetika: `4.217376381 = 3.162988113 + 1.054388268`
  (anchor `x_c2`), sedangkan `2.108735283 = 5.271750210 - 3.163014927`
  (anchor `w1`). Dua jendela bahkan memakai dua anchor berbeda
  (selisih anchor `2.6814e-5`).
- Akibatnya tidak ada silang-naik di dalam kedua jendela terkunci; uji
  tanda `q3y` gagal sebelum range `q3x` diuji.
- K5(b) range `q3x` juga tertukar: pada `w1` nilai aktual ~0 (range
  terkunci `[-6e-5, -3e-5]`), pada `w2` nilai aktual ~`-4.77e-5` (range
  terkunci `[-1e-6, +1e-6]`).
- Margin amendemen #2 (`0.0061` di `w1`, `0.0107` di `w2`) juga tertukar
  posisinya; ini hanya disclosure, karena gerbang yang dikunci adalah
  `v3y <= -1/2` dan nilai `v3y` di `w1/w2` (`-1.065`/`-0.612`) lolos.

Semua angka di §3 berasal dari probe diagnostik, **bukan** dari receipt
FAILED; tidak ada klaim K5 yang dibuat.

## 4. Riwayat eksekusi dan kegagalan

1. **Run 1 (modul awal).** Kampanye berhenti dengan
   `ZeroDivisionError: matrix is singular` di `_inverse_mid` setelah 6,49
   menit; receipt tidak ditulis. Ini adalah gejala pertama singularitas
   `DF`.
2. **Run 1b (penanganan crash).** Inverse singular ditangkap; K1 justru
   FAILED karena scanner AST baru sendiri memakai nama `float`
   (`name:float:1089`) — pelanggaran K1 yang jujur dicatat, bukan
   disembunyikan. Receipt run 1b (hash `d5344371...`) **superseded**.
3. **Run 1c (final).** Scanner mengganti klasifikasi literal float menjadi
   `type(...).__name__`; K1 PASS. K3 FAILED dengan witness translasi;
   receipt `72309f63...`; 7,17 menit.
4. **Run 2 (determinisme).** Payload identik byte dengan run 1c; sha256LF
   receipt sama; 7,24 menit.

Kegagalan K1 di run 1b dan `ZeroDivisionError` di run 1 adalah cacat
implementasi yang diperbaiki **tanpa** mengubah ambang, konstanta, atau
scope pra-registrasi; keduanya diungkap di sini.

5. **Suite penuh dan freeze.** `pytest -q msaf/tests`: **629 passed, 1
   skipped** (29:19), termasuk guard T2 8/8 dan guard T1b;
   `python audit_quantum/freeze.py --verify`: **OK**, 14 pin, digest
   `f6352884d85bab5a68c01a4e1d4a73618304464fd300d56bce1f8cc2f62baa25`.

## 5. K6 dan mutasi

| Mutasi | Perilaku aktual | Status |
|---|---|---|
| M1 `REMAINDER_FACTOR := 1e70` | Berhenti fail-fast lebih awal dari checkpoint K2: `aborted at step 2: Picard enclosure failed` (radius sisa yang digelembungkan menggagalkan kotak Picard). Gerbang lebar K2 tidak tercapai | **Bekerja sebagai fail-fast, bukan lewat gerbang K2** |
| M2 benih `q1x += 1e-3` | K3 FAILED, tetapi karena `DF` singular yang sama; bukan karena aturan monoton | **Tidak diskriminatif** |
| M3 satu byte receipt diubah | Perbandingan payload/hash mendeteksi perubahan | **Bekerja** |
| M4 injeksi float literal / `float(x)` | `_ast_hits` menolak literal (`literal:float:...`) dan nama (`name:float:...`); modul bersih | **Bekerja** |
| M5 `SWEEP_SIGNED := False` | K3 FAILED, tetapi karena singularitas `DF` yang sama; ledakan `DF(B)` di kampanye kotak tidak pernah tercapai | **Tidak diskriminatif** |

Karena kampanye jujur sudah gagal di inversi pertama, M2 dan M5 tidak
menguji mekanisme yang dimaksud §9.3. K6 karenanya **tidak terpenuhi
penuh**; ini konsisten dengan verdict FAILED dan menjadi alasan tambahan
tidak ada registry. M1 tetap berguna sebagai uji fail-fast, meskipun
abort-nya lewat Picard (step 2), bukan gerbang lebar K2; M3/M4 menguji
integritas receipt dan AST.

## 6. Mengapa tidak ada registry A-2026-0041

§5 menetapkan `ALL PASS (K1-K6)` sebagai satu-satunya syarat registry.
K3 gagal secara struktural dan K6 tidak terpenuhi penuh, jadi tidak ada
`ALL PASS`. `reports/FENCE_REGISTRY.md` tidak diubah dan `A-2026-0041`
tidak dibuat. T2 tetap tercatat sebagai trek FAILED; T1b (`A-2026-0040`)
dan modul beku tidak terpengaruh.

## 7. Perbaikan yang diperlukan: T2-r2 (pra-registrasi baru)

T2 tidak boleh diamendemen setelah kode ditulis (§9 baris 409-411).
Perbaikan harus lewat trek baru dengan pra-registrasi yang ditulis
**sebelum** kode:

1. **Quotien simetri.** Bekerja di frame pusat massa: `q1+q2+q3 = 0`,
   `p1+p2+p3 = 0` (4 constraint), dan hilangkan arah keluarga energi
   dengan mengunci energi atau memperlakukan periode `T` sebagai variabel
   dengan kondisi fase. Analisis simetri rotasi/`L = 0` sebelum mengunci
   dimensi seksi. Klaim keunikan harus dinyatakan **modulo simetri**
   (orbit yang ditranslasikan/boosted bukan objek berbeda).
2. **Frame K5 absolut.** Semua waktu diukur dari `t = 0` benih (atau dari
   silang-turun pertama yang tersertifikasi, secara konsisten); jendela
   silang-naik menjadi `1.054388268` dan `5.271750210`; range `q3x` di
   `w1/w2` ditukar/diturunkan dari orbit tersertifikasi, bukan dari probe
   `x_c2`.
3. **Mutasi yang diskriminatif.** M2 harus menggeser arah transverse
   terhadap manifold solusi (bukan arah simetri); M5 harus menguji
   ledakan `DF(B)` pada kampanye kotak setelah K3 reduced terbukti PASS.
4. **Modul baru** (bukan mengedit `msaf/figure_eight.py`), receipt baru,
   dan guard baru; T2b (spektrum) tetap di luar scope.

## 8. Batas klaim

T2 **tidak** mengklaim keberadaan orbit periodik, keunikan lokal, tube
tervalidasi, monodromy, atau deskriptor bentuk: K3 gagal dan K2/K4/K5
tidak dievaluasi. Tidak ada klaim RH/PDE/chaos/ergodisitas/Soliton/Evans/
fisika/analitik-kontinuasi/prioritas/pembuktian formal Lean. T1b S4 tetap
uji-stress tersegel, bukan klaim figure-eight. Angka probe di §3 bukan
hasil tersertifikasi.

## 9. Artefak

- `msaf/figure_eight.py` (baru; sha256LF di tabel).
- `msaf/tests/test_figure_eight.py` (guard baru; sha256LF di tabel).
- `reports/figure_eight_three_body_2026-10-22.json` (receipt FAILED;
  sha256LF `72309f63...`; dua run byte-identical).
- Modul beku `msaf/ode_validated.py` dan `msaf/ode_validated_block.py`
  tidak berubah; hash cocok dengan pin `A-2026-0039`/`A-2026-0040`.
- Registry `A-2026-0041`: **tidak dibuat**.
