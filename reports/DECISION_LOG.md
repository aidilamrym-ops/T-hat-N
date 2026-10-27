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

## 2026-10-27 — Konsolidasi MCP T2N: `t2n_core` + `t2n_viz`

- **Keputusan pemilik:** dua server t2n final — `t2n_core` (repokeeper +
  archivist + science + scribe + watchtower, 30 tool) dan `t2n_viz`
  (illumina + materials, 7 tool). Dua server `shp_*` tidak disentuh, sehingga
  total target 4 server aktif.
- **Bug yang diperbaiki:** `mcp/t2n/illumina.py` gagal diimpor karena definisi
  `render_html_dashboard` hilang; badannya tertinggal setelah `return` di
  `render_materials_dashboard`. Fungsi dipulihkan sebagai tool publik, dan
  jalur materials memakai impor malas.
- **Artefak:** `mcp/t2n_core.py`, `mcp/t2n_viz.py`, shim
  `mcp/t2n_combined.py`, `opencode.jsonc` (2 entri), guard
  `msaf/tests/test_mcp_servers.py`.
- **Verifikasi:** `python -m pytest msaf/tests/test_mcp_servers.py -q` →
  7 passed; smoke produksi menunjukkan `t2n_core` 30 tool dan `t2n_viz`
  7 tool dengan `repo_root`/`write_roots` benar. Empat guard minimum plus
  guard MCP: 21 passed. `lake build` tidak dijalankan karena tidak ada
  perubahan Lean.
- **Commit:** pra-registrasi `91818bc`; implementasi `7412eff`.
- **Proses:** seluruh 10 proses t2n berhenti saat `opencode.jsonc` di-reload;
  6 proses `shp_*` (3 batch) tetap berjalan. Duplikasi shp tidak diubah
  karena batas "jangan sentuh `shp_*`".
- **Batas:** ini perbaikan infrastruktur, bukan klaim ilmiah. Tidak ada klaim
  RH/abc/BSD/figure-eight/Lean/Coq/fisika; `materials.mp_query` tetap butuh
  jaringan dan tidak diuji.

## 2026-10-27 — Pemisahan suite lambat dari CI default

- **Keputusan:** kampanye figure-eight r5/r6 ditandai `slow` dan dipindah ke
  workflow `Slow tests` (terjadwal 02:00 WIB + manual, `timeout-minutes:
  300`); job `python-tests` menjalankan
  `python -m pytest msaf -q -m "not slow"`.
- **Alasan:** `python-tests` dibatasi 60 menit, sedangkan run `40401144645`
  berjalan 57+ menit tanpa selesai; `msaf/tests/test_figure_eight_r6.py`
  juga memanggil `run_campaign()` dua kali tanpa fixture.
- **Perubahan:** `pytest.ini` mendaftarkan marker `slow`; dua uji kampanye r5
  diberi marker; r6 memakai fixture `scope="module"` (satu kampanye, bukan
  dua) dan dua uji kampanye diberi marker; guard
  `msaf/tests/test_ci_slow_split.py` mengunci pemisahan ini.
- **Verifikasi:** koleksi `-m slow` = 4 uji, `-m "not slow"` = 786 uji,
  total 790; uji murah r5/r6 8 passed; `test_fence_registry` dan
  `test_ci_verification_paths` lulus setelah hash `ci.yml` dan
  `test_figure_eight_r6.py` diperbarui dengan catatan bertanggal.
- **Commit:** pra-registrasi `a33d5db`; implementasi `4570e0a`.
- **Batas:** "CI hijau" kini berarti suite cepat. r5/r6 hanya dibuktikan oleh
  workflow `Slow tests`; jangan menyebut r5/r6 hijau tanpa hasil workflow itu.
  Tidak ada asersi, ambang, receipt, atau verdict yang dihapus/diubah.
- **Koreksi 2026-10-27:** angka `timeout-minutes: 60` yang disebut di atas
  adalah milik job `lean-kernel`, bukan `python-tests`; job `python-tests`
  tidak memiliki timeout. Alasan pemisahan yang terukur adalah run P2
  `40261066426` yang menghabiskan 202,5 menit pada `python-tests`, dan run
  `40401144645` yang berjalan 57+ menit tanpa selesai. Keputusan desain tidak
  berubah; tidak ada kode/CI yang diubah oleh koreksi ini.

## 2026-10-27 — Tiga keputusan delegasi: status sertifikasi dan gerbang klaim r5/r6

- **Dasar delegasi:** pemilik menyerahkan keputusan dengan syarat klaim hanya
  boleh jika semua syarat terpenuhi dan terbukti/dapat dibuktikan. Keputusan
  berikut berbasis pemeriksaan artefak, bukan asumsi.

### D1 — `T-2026-0049` dan `A-2026-0048` tetap CERTIFIED dengan pengecualian proses tercatat

- **Keputusan:** kedua entri tetap `CERTIFIED`. Pelanggaran prereg 2026-10-25
  (commit campuran; tanggal 2026-10-30 adalah tanggal target, bukan tanggal
  registrasi) dicatat sebagai pengecualian proses, bukan alasan menurunkan
  status. Preseden: `A-2026-0047` (r6), diputuskan pemilik 2026-10-26.
- **Bukti `T-2026-0049`:** receipt `reports/bsd_v2_2026-10-30.json` mencatat
  `all_pass: true`, 5 kurva, dan `match: true` pada setiap kurva; hash
  pra-registrasi, receipt, dan modul cocok dengan baris `sha256LF`;
  `msaf/tests/test_bsd_v2.py` lulus 2/2 dan menghitung ulang formula eksak
  melalui `bsd_v2.build_payload()` tanpa float/numpy.
- **Bukti `A-2026-0048`:** receipt `reports/twin_prime_v4_2026-10-30.json`
  mencatat `all_pass: true`, `count_a = count_b = 27.412.679`,
  `elementwise_mismatches = 0`, dan `pairs_sha256_a == pairs_sha256_b`;
  checkpoint 10^6–10^9 cocok dengan nilai referensi (8169, 58980, 440312,
  3424506); hash pra-registrasi, receipt, dan modul cocok.
- **Batas:** klaim tetap finit — 5 kurva pilot rank-0 dengan `|Ш| = 1`
  diasumsikan (BSD v2), dan sensus 10^10 (twin v4). Bukan bukti BSD atau twin
  prime umum. Tidak ada uji lokal yang menjalankan ulang sensus 10^10;
  integritas receipt dijaga `test_fence_registry` dan checkpoint referensi.
- **Konsekuensi:** tanggal tidak diedit retroaktif; tidak ada penulisan ulang
  entri `CERTIFIED`; cukup catatan bertanggal yang aditif.

### D2 — `A-2026-0050` tetap CERTIFIED untuk stub deterministik

- **Keputusan:** `CERTIFIED` dipertahankan. Label ini menyatakan perilaku stub
  deterministik yang tercatat, bukan klaim belajar.
- **Bukti:** pra-registrasi nyata, receipt `ALL PASS`, hash
  pra-registrasi/receipt/modul/test cocok, dan
  `msaf/tests/test_learnharness_v1.py` lulus.
- **Batas:** tidak ada klaim performa ML, generalisasi, atau kualitas model;
  label `CERTIFIED` tidak menaikkan stub menjadi implementasi ML.

### D3 — Gerbang klaim r5/r6

- **Keputusan:** "CI hijau" default **tidak pernah** mencakup r5/r6. Klaim
  tentang r5/r6 hanya boleh jika (a) job `python-tests` hijau dan (b) workflow
  `Slow tests` hijau pada commit yang sama.
- **r5:** verdict tersegel adalah `FAILED` (`all_pass: false`, 8/10 baris K6
  lulus). r5 tidak boleh disebut "green"; yang boleh diklaim hanyalah verdict
  `FAILED` yang direproduksi.
- **r6:** verdict `ALL PASS`; klaim tetap lokal di box B dan kondisional pada
  K1–K5 serta M1–M10.
- **Penguatan bukti:** `slow-tests.yml` kini menjalankan
  `test_fence_registry` **sebelum** kampanye (amendemen pra-registrasi §8,
  commit `0d25a53`; implementasi `3a56b86`), sehingga `Slow tests` yang hijau
  ikut membuktikan segel receipt. Guard `test_ci_slow_split.py` mengunci
  urutan langkah.
- **Batas:** hash payload Arb penuh tidak di-pin karena string interval Arb
  tidak stabil lintas platform.

## 2026-10-27 — Sinkronisasi lapisan otoritas: ledger tombstone, guard, manifest, CURRENT_AUTHORITY

- **Dasar:** pemilik menyetujui eksekusi paket koreksi hasil audit read-only
  2026-10-27 ("kerjakan dan saya setuju"). Audit menemukan hash `sha256LF`
  0 drift dan 0 sertifikat hilang; temuan utamanya justru lapisan otoritas
  yang stale, ledger tombstone yang mengunci pernyataan palsu, dan cacat
  tampilan/teks registry. Paket yang dieksekusi entri ini: **D1 (tombstone)**
  dan **D2 ("otoritas")**. D3 (registry), D4 (Stage), D6 (housekeeping)
  menyusul pada entri/commit terpisah.
- **Perubahan D1:**
  `reports/ARCHIVE_TOMBSTONES.md` — bagian "Tombstone yang sudah dieksekusi"
  kini memuat tabel 5 baris (3 `tombstoned`: Stage 2 MD, Stage 3 MD,
  `append_status.py`; 2 `stubbed`: `HANDOFF.md`, `README_custody.md`),
  recovery `git show 995576c~1:<path>` (semuanya terverifikasi ada di komit
  itu, reachable dari `main`). Kalimat "Belum ada tombstone yang dieksekusi."
  dihapus karena tidak benar sejak `995576c`.
- **Perubahan guard:** `msaf/tests/test_authority_manifest.py` tidak lagi
  mengunci pernyataan palsu itu. Guard baru menolak ledger yang masih
  berklaim "belum ada"; memverifikasi bahwa tabel eksekusi ada, menyebut
  commit `995576c`, dan mencakup `tombstoned`+`stubbed`. State `stubbed`
  ditambahkan ke `ALLOWED_SUPERSEDED_STATES`.
- **Perubahan manifest:** `reports/AUTHORITY_MANIFEST.json` — lima entri
  `superseded` diselaraskan dengan disk (`tombstoned`/`stubbed`,
  `recovery_commit: 995576c~1`); hash aktif semua dokumen otoritas diperbarui
  pada commit yang sama.
- **Perubahan D2:** `CURRENT_AUTHORITY.md` §5 dan header diperbarui: status
  D1/D2 delegasi 2026-10-27 (`T-2026-0049`, `A-2026-0048` CERTIFIED dengan
  pengecualian proses; r7 `A-2026-0049` RETRACTED; `A-2026-0050` CERTIFIED
  terbatas stub deterministik) tertulis eksplisit, sehingga dokumen ini lebih
  tinggi tidak lagi bertentangan dengan `DECISION_LOG`.
- **Batas:** tidak ada baris `sha256LF` registry, receipt, kode matematika,
  atau verdict yang berubah; tidak ada status registry dinaikkan/diturunkan.
- **Risiko tercatat (bukan keputusan terbuka):** workflow `Slow tests`
  belum pernah menjalankan r6 di `main`; klaim r6 tetap berbasis keputusan
  pemilik 2026-10-26 + receipt, dan gerbang D3 (2026-10-27) menuntut run
  `Slow tests` hijau untuk pembuktian lanjutan.
- **Verifikasi lokal saat entri ini ditulis:** 14 passed pada
  `test_authority_manifest`, `test_fence_registry`, `test_lean_axiom_audit`,
  `test_anti_circularity_gate`.

## Keputusan yang masih menunggu pemilik

Tiga pertanyaan delegasi 2026-10-27 sudah diputuskan di atas (D1–D3). Tidak
ada item dari daftar itu yang tersisa. Risiko residual yang dicatat, bukan
keputusan terbuka: `A-2026-0048` tidak memiliki uji khusus v4 yang dapat
menjalankan ulang sensus 10^10 secara lokal; verifikasinya bergantung pada
receipt tersegel, checkpoint referensi, dan guard registry.


