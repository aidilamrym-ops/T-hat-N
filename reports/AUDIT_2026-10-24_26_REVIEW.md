# Audit jendela 2026-10-24 sampai 2026-10-26

Status: audit historis + verifikasi artefak. Dokumen ini **bukan** bukti RH
dan tidak mengubah verdict matematika apa pun.

Ruang lingkup: commit `2a4d65d` sampai `9d13787` di `main`, remote
`https://github.com/aidilamrym-ops/T-hat-N`, issue/PR/rilis GitHub, serta
artefak Stage 2–4 dan registry yang disentuh pada jendela tersebut.
Waktu audit: 2026-10-26.

## 1. Ringkasan eksekusi

| Item | Hasil |
|---|---|
| `main` lokal vs `origin/main` | identik pada `9d13787`; working tree bersih saat audit dimulai |
| Branch remote | hanya `main` |
| Issue GitHub | 0 |
| Pull request GitHub | 0 |
| Rilis GitHub | dua rilis lama (`v1.1.0`, `v1.40.0-alpha-final-certified-delivery`); tidak ada rilis baru pada jendela ini |
| Commit jendela | 35 commit, `2a4d65d` … `9d13787` |
| `lake build` | 3242 jobs, exit 0 |
| Anti-circularity gate | PASS, `FAIL=0 NOT_RUN=0 SKIP=0` |
| Registry pytest | 2 passed |
| Hash sertifikat `T-2026-0050` | 9/9 cocok dengan berkas HEAD |
| CI GitHub | **merah terus** sejak sekurangnya 2026-10-24; 30 run terakhir semuanya `failure`, kecuali run HEAD yang masih berjalan dan job `lean-kernel`-nya sudah `failure` |

Kesimpulan singkat: intuisi bahwa ada pekerjaan yang terlewat atau terulang
**benar**. Yang paling material bukan serangan matematika baru, melainkan:
arsip Stage 2/3 tidak diperbarui, commit `19fb2ec` tidak berisi berkas yang
diklaim judulnya, registry `T-2026-0050` ditulis ulang di tempat, beberapa
prasyarat “prereg sebelum kode” dilanggar, dan CI sudah lama merah.

## 2. Peta commit jendela

| Commit | Waktu | Isi | Catatan audit |
|---|---|---|---|
| `2a4d65d` | 2026-10-25 10:35 | scaffold Stage 2–4 + receipts | menyebut “Complete” padahal masih placeholder |
| `a55fe79` | 2026-10-25 12:17 | kernel check + migrasi import Mathlib | dokumen kernel-check pertama |
| `19fb2ec` | 2026-10-25 20:57 | judul: Stage 2/3 placeholder + Stage 4 | **tidak menambah berkas Stage 2/3**; menambah BSD v2, `error.txt`, `lean/error.txt` |
| `63e56d4` | 2026-10-25 22:26 | update registry | sertifikat Stage 2/3 masih placeholder |
| `08ae970` | 2026-10-26 02:05 | Stage 2/3/4 “Complete” | berkas Stage 2/3 baru benar-benar muncul di sini |
| `9d13787` | 2026-10-26 09:18 | ganti konstanta sintetis dengan data GW nyata | menulis ulang `T-2026-0050` di tempat |

Di luar RH, jendela yang sama juga berisi Q2 twin prime v2/v3/v4, BSD Q1
recon/v2, figure-eight r6, Learnharness v1, dan MCP T2N.

## 3. Temuan

### T1 — Arsip Stage 2/3 tertinggal, Stage 4 tidak

`Stage_4_Containment_Proof.md` mendapat addendum 2026-10-26 yang menjelaskan
bahwa berkas Lean-nya sudah ditulis ulang. Stage 2 dan Stage 3 **tidak**
mendapat addendum serupa, padahal implementasi aktifnya pindah ke
`lean/Stage_2_Tail_Bound.lean` dan `lean/Stage_3_Eigenvalue_Locking.lean`.

Akibatnya `TARGET_STATUS_2026-10-25.md` §4.1 dan
`KERNEL_CHECK_2026-10-25.md` §2 masih menunjuk berkas arsip placeholder
sebagai “Stage 2” dan “Stage 3”. Pembaca yang hanya membaca tabel itu akan
mengira implementasi aktif masih placeholder, atau sebaliknya mengira arsip
placeholder adalah implementasi.

Tindakan P0: addendum Stage 2/3, dokumen koreksi lingkup, pembaruan tabel
status/kernel-check.

### T2 — Target `C/n` di prompt Stage 2 salah secara internal

Prompt meminta `|XC(n)| <= C_arch / n` dan tail `C_arch L^2 / (pi N)`.
Tail harmonik divergen, jadi target ini tidak bisa menghasilkan
`epsilon(N) -> 0`. Target yang konsisten adalah `1/n^2`.

Pengukuran 1000-bit menunjukkan `n^2 * XC(n)` stabil di sekitar
`-0.05621508517` untuk `n = 10..10^6`. Itu bukti numerik, bukan bukti.
Implementasi Lean sekarang tidak mengklaim salah satu dari keduanya; ia hanya
membuktikan ketaksamaan sisa truncation geometrik terhadap dua citra desimal
`lambda_min`.

Tindakan P0: catat koreksi target dan batas klaim. Derivasi `1/n^2` tetap P2.

### T3 — Induksi Stage 3 tidak valid

Cauchy interlacing memberi `lambda_min(A_{N+1}) <= lambda_min(A_N)`, sehingga
positif-definit tidak merambat naik. Prompt Stage 3 meminta induksi ke arah
yang salah. Implementasi aktif sudah berupa record data, bukan induksi, tetapi
judul dan arsipnya masih menyiratkan induksi.

Tindakan P0: dokumentasikan ketidakvalidan dan lingkup record.

### T4 — Commit `19fb2ec` salah judul dan mencampur pekerjaan

Judul commit mengatakan “Add Stage 2 TailBound placeholder, Stage 3
EigenvalueLock placeholder”, tetapi daftar berkasnya tidak memuat
`lean/Stage_2_Tail_Bound.lean` maupun `lean/Stage_3_Eigenvalue_Locking.lean`.
Berkas itu baru muncul di `08ae970`.

Commit yang sama juga menambahkan:

- `msaf/bsd_v2.py`, `msaf/tests/test_bsd_v2.py`, dan receipt BSD v2;
- `reports/PREREG_Q1_BSD_V2_2026-10-30.md`;
- `error.txt` (7006 byte) dan `lean/error.txt` (0 byte).

Jadi ada pekerjaan yang **terlewat** dari commit yang seharusnya
membawanya, dan ada pekerjaan lain yang **menumpang** di commit itu.

Tindakan P0: hapus dua `error.txt` yang tidak dirujuk; catat insiden commit.
Perbaikan BSD tidak dilakukan di P0/P1.

### T5 — `T-2026-0050` ditulis ulang di tempat

Registry menetapkan entri tidak dihapus; perubahan status menulis ulang baris
Status dan/atau menambah catatan. Pada `9d13787`, pernyataan dan seluruh baris
sertifikat `T-2026-0050` diganti. Baris sertifikat lama
(`8e2cf67a…` untuk Stage 2, `571f600a…` untuk Stage 3) hanya dapat dipulihkan
dari git history, bukan dari registry sekarang.

Entri memang memuat catatan historis dan relasi ke `08ae970`, tetapi ini tetap
preseden yang lemah untuk audit trail. P1 akan memakai entri baru
`T-2026-0051`, bukan menulis ulang `T-2026-0050` lagi.

### T6 — Beberapa “prereg sebelum kode” dilanggar pada 2026-10-25

Yang benar: Q2 v3 (`d9848b7` prereg, lalu `bcb6883`/`ad34cbc` kode dan
sertifikasi).

Yang tidak benar:

| Commit | Pelanggaran |
|---|---|
| `eb61af7` | `PREREG_LEARNHARNES_V1` + `msaf/learnharness_v1.py` + test dalam satu commit |
| `ad34cbc` | `PREREG_FIGURE_EIGHT_R6` + `msaf/figure_eight_r6.py` + receipt dalam satu commit |
| `19fb2ec` | `PREREG_Q1_BSD_V2_2026-10-30.md` + `msaf/bsd_v2.py` + receipt dalam satu commit; tanggal prereg justru 2026-10-30 |
| `ee9a5f3` | `PREREG_Q2_TWIN_PRIME_V4_2026-10-30.md` + `msaf/twin_prime_v4.py` + receipt dalam satu commit; tanggal prereg 2026-10-30 |

Tanggal 2026-10-30 pada dua berkas itu adalah tanggal target, bukan tanggal
preregistrasi. Commit-nya terjadi 2026-10-25. Ini tidak boleh diperbaiki
dengan mengedit tanggal secara retroaktif; butuh keputusan pemilik proyek.
P1 akan mengikuti aturan yang benar: commit prereg tersendiri dan dipush
sebelum kode.

### T7 — CI merah sejak 2026-10-24

`gh run list` menunjukkan 30 run terakhir semuanya `failure` (run HEAD masih
`in_progress`, tetapi job `lean-kernel` sudah `failure`). Ini bertentangan
dengan kalimat README bahwa setiap push harus hijau.

Kegagalan pada `08ae970` (5 failed, 685 passed, 9 skipped, 2:29:18):

1. `test_lean_axiom_audit.py::test_every_declaration_uses_standard_axioms_only`
2. `test_anti_circularity_gate.py::test_kernel_sources_are_placeholder_free`
3. `test_figure_eight_r2.py::test_no_r2_registry_entry`
4. `test_figure_eight_r3.py::test_no_r3_registry_entry`
5. `test_figure_eight_r4.py::test_no_r4_registry_before_guard`
6. `test_figure_eight_r5.py::test_campaign`

Penyebab yang terverifikasi:

- audit aksioma membuat `namespace ` kosong untuk Stage 2/3 yang tidak memakai
  namespace, sehingga berkas audit gagal dikompilasi;
- uji anti-circularity mengunci empat berkas kernel, lalu menganggap dua
  berkas Stage 2/3 baru sebagai “scope drift”;
- tiga uji figure-eight mencari substring `A-2026-0041`, yang sekarang muncul
  di catatan sejarah registry, bukan sebagai heading entri;
- uji r5 mengharapkan semua baris K6 lulus, padahal laporan resmi r5
  menyatakan M3 dan M8 non-diskriminatif dan verdict `FAILED`.

Tindakan P0: perbaiki empat uji murah (audit namespace, scope, heading
registry) dan uji r5 agar sesuai verdict resmi. Uji r5 tetap mahal dan tidak
dijalankan penuh secara lokal dalam audit ini; hasilnya mengacu pada receipt
tersegel `reports/figure_eight_r5_2026-10-23.json`.

### T8 — Artefak yang benar dan sudah diverifikasi

Yang tidak perlu diragukan lagi:

- `lake build` 3242 jobs exit 0;
- `Stage_4_Containment_Proof.lean` lulus kernel dan memuat
  `test_function_l2_containment`, bukan `TestFunctionInL2 := True`;
- semua hash `T-2026-0050` di registry cocok dengan berkas HEAD;
- `#print axioms` untuk sembilan teorema Stage 2/3 hanya memakai
  `propext`, `Classical.choice`, `Quot.sound` (rincian di dokumen koreksi);
- anti-circularity gate PASS pada tiga berkas aktif.

## 4. Yang terlewat, yang terulang, yang perlu diputuskan

**Terlewat**

- addendum Stage 2/3;
- berkas Stage 2/3 pada commit yang mengklaim menambahkannya;
- receipt untuk modul aktif `lean/Stage_2_Tail_Bound.lean` dan
  `lean/Stage_3_Eigenvalue_Locking.lean`;
- perbaikan CI setelah push terakhir;
- entri registry baru untuk pekerjaan baru (dipaksa menumpang di `T-2026-0050`).

**Terulang**

- kata “Complete” pada `2a4d65d` dan `08ae970` untuk pekerjaan yang berbeda;
- pembuatan receipt Stage 2–4 pada `2a4d65d`, lalu receipt itu tidak lagi
  mewakili modul aktif setelah `08ae970`/`9d13787`;
- pekerjaan BSD/twin-prime/Learnharness/r6 yang masuk ke commit dengan judul
  RH atau sebaliknya.

**Perlu keputusan pemilik**

- apakah pelanggaran prereg `eb61af7`, `ad34cbc`, `19fb2ec`, `ee9a5f3` akan
  dinyatakan sebagai amendment jujur, diulang dengan prereg baru, atau
  diturunkan statusnya;
- apakah `T-2026-0049`, `A-2026-0047`, `A-2026-0048` tetap `CERTIFIED`
  mengingat prereg-nya tidak mendahului kode;
- apakah uji r5 yang mahal akan dipisah dari suite default agar CI tidak
  memakan 2,5 jam.

## 5. Tindakan yang dieksekusi setelah audit

P0 (finit, rendah risiko):

- dokumen koreksi Stage 2/3 dan addendum arsip;
- audit aksioma eksplisit untuk sembilan teorema;
- perbaikan uji namespace/scope/heading dan uji r5;
- penghapusan `error.txt` dan `lean/error.txt`.

P1 (setelah prereg terpisah):

- envelope error entry dari `build_arb_tau`, diserialisasi sebagai string
  desimal (bukan float64);
- teorema perturbasi finit yang diperiksa kernel;
- entri registry baru, bukan penulisan ulang `T-2026-0050`.

P2 (belum dimulai):

- derivasi analitik `|XC(n)| = O(1/n^2)` dan `epsilon(N) -> 0`.

## 6. Batas klaim

Audit ini tidak membuktikan RH, tidak membuktikan Weil positivity, tidak
membuktikan tail analitik, dan tidak mengubah status matematika mana pun.
Semua verdict di atas adalah verdict artefak: berkas, hash, output compiler,
dan log CI.
