# Decision Log

Log keputusan yang mengikat sesi berikutnya. Entri baru ditambahkan di akhir;
entri lama tidak ditulis ulang. Setiap entri menyebut tanggal, keputusan,
alasan, commit, dan dampaknya.

Urutan otoritas: `CURRENT_AUTHORITY.md` > `AGENTS.md` > log ini >
`reports/FENCE_REGISTRY.md` > dokumen historis.

## 2026-10-25 — Pelanggaran prereg dicatat, belum diputuskan

- **Temuan:** audit `reports/AUDIT_2026-10-24_26_REVIEW.md` §T6 menemukan
  empat commit yang mencampur pra-registrasi dan kode dalam satu commit:
  `eb61af7` (Learnharness v1), `ad34cbc` (figure-eight r6), `19fb2ec` (BSD
  v2), dan `ee9a5f3` (twin prime v4). Dua berkas pra-registrasi bertanggal
  2026-10-30, yaitu tanggal target, bukan tanggal registrasi.
- **Keputusan:** tanggal tidak diedit secara retroaktif; status sertifikasi
  tidak diturunkan secara diam-diam. Pelanggaran dicatat sebagai temuan audit.
- **Status:** menunggu keputusan pemilik. Tidak ada perubahan status yang
  dilakukan oleh P0/P1/P2.
- **Dampak:** `T-2026-0049`, `A-2026-0047`, dan `A-2026-0048` tetap seperti
  tercatat sampai ada keputusan eksplisit.

## 2026-10-26 — P0: koreksi lingkup Stage 2/3 dan perbaikan guard

- **Commit:** `5fea118`.
- **Keputusan:**
  - Implementasi aktif Stage 2/3 adalah `lean/Stage_2_Tail_Bound.lean` dan
    `lean/Stage_3_Eigenvalue_Locking.lean`, bukan placeholder di
    `reports/RH_SCAFFOLD_NOTES/`.
  - Target `|XC(n)| <= C_arch/n` dari prompt Stage 2 salah secara internal;
    tail harmonik divergen. Target yang konsisten adalah `1/n^2`.
  - Induksi naik Stage 3 tidak valid karena Cauchy interlacing; modul aktif
    hanya record data.
  - Audit aksioma per-deklarasi dan guard CI diperbaiki.
- **Dokumen:** `reports/AUDIT_2026-10-24_26_REVIEW.md`,
  `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md`,
  `reports/RH_SCAFFOLD_NOTES/KERNEL_CHECK_2026-10-25.md`.
- **Batas:** P0 adalah audit artefak; tidak ada klaim matematika baru.

## 2026-10-26 — P1: envelope entry dan perturbasi finit

- **Pra-registrasi:** `34ee072`, dikomit dan dipush **sebelum** kode P1.
- **Implementasi:** `b7b5f2e`.
- **Registry:** `T-2026-0051`.
- **Keputusan:** envelope entry `c=13, N=160, dim=321` dikunci pada
  `epsilon = 10^-100`, `delta = 321 * 10^-100`, dan
  `lambda_min = 3.123458832662237e-59`; lima teorema Lean masuk kernel.
- **Batas:** `posDef_add_of_quadratic_bound` dan
  `gw_entry_perturbation_posDef` kondisional pada `A.PosDef` dan `hAquad`.
  Ini bukan bukti positivity matriks Arb; otoritas positivity tetap run
  `arb_mat.eig` eksternal.

## 2026-10-26 — P2: batas tail diagonal `XC`

- **Pra-registrasi:** `fc33084`, dikomit dan dipush **sebelum** kode P2.
- **Implementasi:** `0b0a32c`.
- **Registry:** `T-2026-0052`.
- **Keputusan:** untuk `c=13`, `|XC(n)| < 1/n^2` dan
  `epsilon_XC(N) < 2/N -> 0`. Grid Arb `n=1..4096` pada 512 bit; nilai
  maksimum `max n^2|XC(n)| = 0.0661824765...` di `n=1`.
- **Amendment:** `reports/PREREG_ANALYTIC_TAIL_2026-10-26.md` §9 mencatat
  dua penyimpangan setelah kode dimulai: nama/indeks `Ico` dan grid 4096
  (dari 512). Tidak ada konstanta, klaim, atau ambang yang dilonggarkan.
- **Lean:** empat deklarasi di `lean/Stage_6_Analytic_Tail.lean` lulus
  kernel; `lake build` 8721 jobs. Aksioma hanya `propext`,
  `Classical.choice`, `Quot.sound`.
- **Batas:** hanya diagonal `XC`. `S(n)`, `Wp`, `W02`, entri off-diagonal,
  positivity matriks, spektrum zeta, Weil positivity, dan RH tidak tercakup.
  Batas pointwise adalah kertas + grid Arb, bukan keluaran kernel. Tidak ada
  klaim `epsilon_XC(N) < lambda_min(N)`.

## 2026-10-26 — Authority layer aditif

- **Keputusan:** membuat `AGENTS.md`, `CURRENT_AUTHORITY.md`,
  `reports/DECISION_LOG.md`, `reports/ARCHIVE_TOMBSTONES.md`,
  `reports/AUTHORITY_MANIFEST.json`, dan
  `msaf/tests/test_authority_manifest.py`.
- **Alasan:** sesi berikutnya tidak boleh resurrect instruksi dari
  `reports/HANDOFF.md` atau placeholder Stage 2/3, dan tidak boleh menghapus
  artefak yang sudah tersertifikasi.
- **Sifat:** aditif. Tidak ada file yang dihapus atau diganti pada fase ini.
  `reports/HANDOFF.md` masih ada dan tetap historis; stub dan tombstone
  menunggu persetujuan pemilik.
- **Guard:** manifest menghitung `sha256LF` dari empat dokumen otoritas;
  perubahan dokumen tanpa memperbarui manifest akan menggagalkan CI.

## 2026-10-26 — P2 CI hijau dan tag baseline

- **Run:** `40261066426` untuk `0b0a32c`.
- **Hasil:** ketiga job **success** (`lean-kernel`, `coq-kernel`,
  `python-tests`).
- **Tag:** `p2-green-0b0a32c`.
- **Dampak:** baseline P2 menjadi rujukan tag; commit authority layer
  sesudahnya tidak mengubah tag tersebut.

## 2026-10-26 — Persetujuan pemilik untuk stub dan tombstone

- **Keputusan pemilik:** menyetujui daftar stub/tombstone yang diajukan,
  dengan syarat setiap berkas diperiksa ulang sebelum dihapus.
- **Disetujui:**
  - `reports/HANDOFF.md` → stub historis.
  - `reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.md`
    → dihapus + tombstone.
  - `reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.md`
    → dihapus + tombstone.
  - `reports/RH_SCAFFOLD_NOTES/README_custody.md` → stub custody historis.
  - `reports/RH_SCAFFOLD_NOTES/append_status.py` → dihapus + tombstone.
- **Pemeriksaan sebelum eksekusi:** tidak ada baris `sha256LF` untuk kelima
  path; tidak ada test/CI yang merujuknya; kelima berkas ada di `0b0a32c`
  dan `origin/main` berada di commit itu. Bukti lengkap ada di
  `reports/ARCHIVE_TOMBSTONES.md` §"Verifikasi sebelum eksekusi".
- **Tidak dihapus:** `Stage_2/3*.lean` dan receipt-nya (pernah lulus kernel),
  `Stage_4_Containment_Proof.lean` (registry `T-2026-0050`),
  `STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md`, dan
  `reports/TARGET_STATUS_2026-10-25.md` (hash-frozen).
- **Urutan:** eksekusi hanya setelah authority layer Phase 1 masuk `main`
  dan CI-nya hijau. Tag `p2-green-0b0a32c` menunjuk `0b0a32c` dan tidak
  berubah karena commit Phase 1/2.
- **Status:** disetujui; eksekusi tercatat sebagai entri terpisah saat
  Phase 2 dikomit.

## 2026-10-26 — r6 figure-eight dikonfirmasi CERTIFIED (`A-2026-0047`)

- **Keputusan pemilik:** r6 adalah hasil kerja terbaru; status `ALL PASS`,
  `CERTIFIED`, dengan ID registry `A-2026-0047`.
- **Bukti:** `reports/figure_eight_r6_2026-10-25.json` mencatat
  `all_pass: true`, `summary: ALL PASS`, dan K6 M1-M10 semuanya
  `passed: true`; base K1-K5 memakai modul/receipt r3
  (`8eddc2bb...`, `6b0b71e9...`). Pra-registrasi r6 ber-hash `92b687f5...`.
- **Celah yang ditutup:** commit `ad34cbc` menambahkan modul, test, prereg,
  dan receipt r6, serta menyebut `A-2026-0047` di pesan commit, tetapi
  **tidak** menulis entri ke `reports/FENCE_REGISTRY.md`. Entri ledger
  ditambahkan pada commit authority layer ini.
- **Batas:** hanya keberadaan dan keunikan lokal di dalam box B, kondisional
  pada base K1-K5 dan K6 M1-M10; bukan klaim global, stabilitas, spektrum,
  chaos, ergodisitas, KAM, PDE, fisika, prioritas, Lean/Coq, atau RH.
- **Catatan proses:** audit §T6 mencatat pra-registrasi r6 di-commit bersama
  kode (`ad34cbc`). Catatan itu dipertahankan; keputusan pemilik menetapkan
  sertifikasi r6 berlaku.
- **Temuan terpisah (belum diputuskan):** `README.md` baris 27 mengklaim
  Learn-harness `A-2026-0050`, tetapi belum ada entri `A-2026-0050` di
  registry. ID itu masih kosong; `T-2026-0050` adalah ID berbeda (RH
  scaffold). Klaim README belum bisa diverifikasi dari ledger.

## 2026-10-27 — Q3 v2 superseded oleh Q3 v3 (sensus abc low-rad lengkap)

- **Keputusan:** Sensus Q3 v2 yang mengunci `max_prime = 100` dinyatakan
  parsial dan superseded. Q3 v3 memakai batas kelengkapan
  `rad(abc) < c^(5/7)`, sehingga enumerasi low-rad lengkap.
- **Alasan:** v2 menemukan 12 triple pada C=10^7; enumerasi lengkap menemukan
  17 triple. Lima triple yang hilang memuat prima 109–173, jadi
  `max_prime=100` bukan batas yang sah untuk kelengkapan.
- **Commit:** pra-registrasi v3 `0d229bb` (sha256LF `aed8e63c...`);
  implementasi, receipt, laporan, dan registry dicatat pada commit `29b1739`.
- **Registry:** `A-2026-0052` (v3, 17 triple) ditambahkan dengan verdict
  `ALL PASS`. `A-2026-0032` (C=100.000, 6 triple) tidak di-retract; dua baris
  hash modul/guard diperbarui ke v3 dengan catatan tanggal, dan klaim 6 triple
  tidak berubah.
- **Batas:** sensus finit C=10^7; bukan pembuktian konjektur abc; tidak ada
  klaim asimtotik/RH/GRH/faktorisasi/RSA/ECC/Anderson/fisika.
- **Dampak:** `reports/DAFTAR_MASALAH_KERJA.md` Q3 menjadi ALL PASS v3;
  `brain.md` §10.3 Q3 menjadi DONE/CERTIFIED. Receipt v2 parsial disimpan di
  `reports/abc_census_v2_10000000.json` sebagai bukti supersession, bukan
  sertifikat.

## 2026-10-27 — Koreksi registry: r7, BSD v2, BSD v3

- **Keputusan pemilik:**
  - `A-2026-0049` (r7) di-retract menjadi `RETRACTED`: receipt `result: {}`,
    report placeholder, modul hanya memanggil r5, dan
    `msaf/tests/test_figure_eight_r7.py` tidak ada.
  - `T-2026-0049` (BSD v2) dipulihkan sebagai heading di atas badan yatim;
    klaim 5 kurva pilot tidak berubah.
  - `A-2026-0051` (BSD v3) direklasifikasi dari `CERTIFIED (pending CI)` ke
    `RECON`: `PREREG_BSD_V3_2026-10-27.md` bukan pra-registrasi sah dan
    `msaf/bsd_v3.py` hanya membungkus `bsd_v2`. Receipt stub dipertahankan
    sebagai bukti; relasi dikoreksi ke `T-2026-0049`.
- **Alasan:** status registry sebelumnya tidak cocok dengan artefak; r7 tidak
  punya receipt/test r7, BSD v3 tidak punya prereg sah, dan badan BSD v2
  kehilangan heading akibat `d56242c`.
- **Commit:** `6fb3e17` (patch registry dan dossier); receipt stub BSD v3
  di-track pada `c4d2ee1`.
- **Dampak:** `reports/REGISTRY_CORRECTION_DOSSIER_2026-10-27.md` menjadi
  catatan keputusan; `brain.md` §10.3 menandai r7 RETRACTED dan BSD v3 RECON.
  Tidak ada artefak ber-`sha256LF` yang dihapus; `A-2026-0052` tidak berubah.

## Keputusan yang masih menunggu pemilik

1. Status sertifikasi `T-2026-0049` dan `A-2026-0048` sehubungan dengan
   pelanggaran prereg 2026-10-25. `A-2026-0047` sudah diputuskan pada
   2026-10-26 (CERTIFIED).
2. Entri registry Learn-harness v1: pra-registrasi memakai `A-2026-0050`
   (masih kosong), tetapi belum ada entri atau sertifikat ledger; klaim
   README belum dapat diverifikasi. `T-2026-0050` adalah ID berbeda.
3. Pemisahan uji r5 yang mahal dari suite default agar CI tidak memakan
   sekitar dua jam.

