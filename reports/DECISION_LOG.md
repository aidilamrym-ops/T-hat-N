# Decision Log

Log keputusan which mengikat sesi berikutnya. Entri baru ditambahkan in akhir;
entri lama no ditulis ulang. Setiap entri menyebut tanggal, keputusan,
alasan, commit, and dampaknya.

Urutan otoritas: `CURRENT_AUTHORITY.md` > `AGENTS.md` > log ini >
`reports/FENCE_REGISTRY.md` > dokumen historis.

## 2026-10-30 — Formalisasi Stage 7 Tail Extension

- **Keputusan:** Formalisasi `sum_Ico_offdiag_le` diselesaikan dan didaftarkan sebagai `T-2026-0060`.
- **Alasan:** Memenuhi target roadmap MSAF RH scaffold untuk bounds off-diagonal.
- **Commit:** `e6b3c8b`
- **Dampak:** Registry diperbarui; klaim `T-2026-0060` (PROPOSED) ditambahkan; CI harus divalidasi.

- **Temuan:** audit `reports/AUDIT_2026-10-24_26_REVIEW.md` Â§T6 menemukan
  empat commit which mencampur pra-registrasi and kode dalam satu commit:
  `eb61af7` (Learnharness v1), `ad34cbc` (figure-eight r6), `19fb2ec` (BSD
  v2), and `ee9a5f3` (twin prime v4). Dua file pra-registrasi bertanggal
  2026-10-30, yaitu tanggal target, bukan tanggal registrasi.
- **Keputusan:** tanggal no diedit secara retroaktif; status sertifikasi
  no diturunkan secara diam-diam. Pelanggaran dicatat sebagai temuan audit.
- **Status:** menunggu keputusan pemilik. Tidak ada perubahan status which
  dilakukan oleh P0/P1/P2.
- **Dampak:** `T-2026-0049`, `A-2026-0047`, and `A-2026-0048` tetap seperti
  tercatat sampai ada keputusan eksplisit.

## 2026-10-26 â€” P0: koreksi lingkup Stage 2/3 and perbaikan guard

- **Commit:** `5fea118`.
- **Keputusan:**
  - Implementasi aktif Stage 2/3 adalah `lean/Stage_2_Tail_Bound.lean` and
    `lean/Stage_3_Eigenvalue_Locking.lean`, bukan placeholder in
    `reports/RH_SCAFFOLD_NOTES/`.
  - Target `|XC(n)| <= C_arch/n` dari prompt Stage 2 salah secara internal;
    tail harmonik divergen. Target which konsisten adalah `1/n^2`.
  - Induksi naik Stage 3 no valid karena Cauchy interlacing; modul aktif
    hanya record data.
  - Audit aksioma per-deklarasi and guard CI diperbaiki.
- **Dokumen:** `reports/AUDIT_2026-10-24_26_REVIEW.md`,
  `reports/RH_SCAFFOLD_NOTES/STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md`,
  `reports/RH_SCAFFOLD_NOTES/KERNEL_CHECK_2026-10-25.md`.
- **Batas:** P0 adalah audit artefak; no ada klaim matematika baru.

## 2026-10-26 â€” P1: envelope entry and perturbasi finit

- **Pra-registrasi:** `34ee072`, dikomit and dipush **sebelum** kode P1.
- **Implementasi:** `b7b5f2e`.
- **Registry:** `T-2026-0051`.
- **Keputusan:** envelope entry `c=13, N=160, dim=321` dikunci on
  `epsilon = 10^-100`, `delta = 321 * 10^-100`, and
  `lambda_min = 3.123458832662237e-59`; lima teorema Lean masuk kernel.
- **Batas:** `posDef_add_of_quadratic_bound` and
  `gw_entry_perturbation_posDef` kondisional on `A.PosDef` and `hAquad`.
  Ini bukan bukti positivity matriks Arb; otoritas positivity tetap run
  `arb_mat.eig` eksternal.

## 2026-10-26 â€” P2: limit tail diagonal `XC`

- **Pra-registrasi:** `fc33084`, dikomit and dipush **sebelum** kode P2.
- **Implementasi:** `0b0a32c`.
- **Registry:** `T-2026-0052`.
- **Keputusan:** for `c=13`, `|XC(n)| < 1/n^2` and
  `epsilon_XC(N) < 2/N -> 0`. Grid Arb `n=1..4096` on 512 bit; nilai
  maksimum `max n^2|XC(n)| = 0.0661824765...` in `n=1`.
- **Amendment:** `reports/PREREG_ANALYTIC_TAIL_2026-10-26.md` Â§9 mencatat
  dua penyimpangan setelah kode dimulai: nama/indeks `Ico` and grid 4096
  (dari 512). Tidak ada konstanta, klaim, or ambang which dilonggarkan.
- **Lean:** empat deklarasi in `lean/Stage_6_Analytic_Tail.lean` lulus
  kernel; `lake build` 8721 jobs. Aksioma hanya `propext`,
  `Classical.choice`, `Quot.sound`.
- **Batas:** hanya diagonal `XC`. `S(n)`, `Wp`, `W02`, entri off-diagonal,
  positivity matriks, spektrum zeta, Weil positivity, and RH no tercakup.
  Batas pointwise adalah kertas + grid Arb, bukan keluaran kernel. Tidak ada
  klaim `epsilon_XC(N) < lambda_min(N)`.

## 2026-10-26 â€” Authority layer aditif

- **Keputusan:** membuat `AGENTS.md`, `CURRENT_AUTHORITY.md`,
  `reports/DECISION_LOG.md`, `reports/ARCHIVE_TOMBSTONES.md`,
  `reports/AUTHORITY_MANIFEST.json`, and
  `msaf/tests/test_authority_manifest.py`.
- **Alasan:** sesi berikutnya no boleh resurrect instruksi dari
  `reports/HANDOFF.md` or placeholder Stage 2/3, and no boleh menghapus
  artefak which already tersertifikasi.
- **Sifat:** aditif. Tidak ada file which dihapus or diganti on fase ini.
  `reports/HANDOFF.md` masih ada and tetap historis; stub and tombstone
  menunggu persetujuan pemilik.
- **Guard:** manifest menghitung `sha256LF` dari empat dokumen otoritas;
  perubahan dokumen tanpa memperbarui manifest akan menggagalkan CI.

## 2026-10-26 â€” P2 CI hijau and tag baseline

- **Run:** `40261066426` for `0b0a32c`.
- **Hasil:** ketiga job **success** (`lean-kernel`, `coq-kernel`,
  `python-tests`).
- **Tag:** `p2-green-0b0a32c`.
- **Dampak:** baseline P2 menjadi rujukan tag; commit authority layer
  sesudahnya no mengubah tag tersebut.

## 2026-10-26 â€” Persetujuan pemilik for stub and tombstone

- **Keputusan pemilik:** menyetujui daftar stub/tombstone which diajukan,
  with syarat setiap file diperiksa ulang sebelum dihapus.
- **Disetujui:**
  - `reports/HANDOFF.md` â†’ stub historis.
  - `reports/RH_SCAFFOLD_NOTES/Stage_2_Derivation_Analytic_Tail_Bound.md`
    â†’ dihapus + tombstone.
  - `reports/RH_SCAFFOLD_NOTES/Stage_3_Eigenvalue_Locking_Dimension_Induction.md`
    â†’ dihapus + tombstone.
  - `reports/RH_SCAFFOLD_NOTES/README_custody.md` â†’ stub custody historis.
  - `reports/RH_SCAFFOLD_NOTES/append_status.py` â†’ dihapus + tombstone.
- **Pemeriksaan sebelum eksekusi:** no ada baris `sha256LF` for kelima
  path; no ada test/CI which merujuknya; kelima file ada in `0b0a32c`
  and `origin/main` berada in commit itu. Bukti lengkap ada in
  `reports/ARCHIVE_TOMBSTONES.md` Â§"Verifikasi sebelum eksekusi".
- **Tidak dihapus:** `Stage_2/3*.lean` and receipt-nya (pernah lulus kernel),
  `Stage_4_Containment_Proof.lean` (registry `T-2026-0050`),
  `STAGE_2_3_SCOPE_CORRECTION_2026-10-26.md`, and
  `reports/TARGET_STATUS_2026-10-25.md` (hash-frozen).
- **Urutan:** eksekusi hanya setelah authority layer Phase 1 masuk `main`
  and CI-nya hijau. Tag `p2-green-0b0a32c` menunjuk `0b0a32c` and no
  berubah karena commit Phase 1/2.
- **Status:** disetujui; eksekusi tercatat sebagai entri terpisah saat
  Phase 2 dikomit.

## 2026-10-26 â€” r6 figure-eight dikonfirmasi CERTIFIED (`A-2026-0047`)

- **Keputusan pemilik:** r6 adalah result kerja terbaru; status `ALL PASS`,
  `CERTIFIED`, with ID registry `A-2026-0047`.
- **Bukti:** `reports/figure_eight_r6_2026-10-25.json` mencatat
  `all_pass: true`, `summary: ALL PASS`, and K6 M1-M10 semuanya
  `passed: true`; base K1-K5 memakai modul/receipt r3
  (`8eddc2bb...`, `6b0b71e9...`). Pra-registrasi r6 ber-hash `92b687f5...`.
- **Celah which ditutup:** commit `ad34cbc` menambahkan modul, test, prereg,
  and receipt r6, serta menyebut `A-2026-0047` in pesan commit, tetapi
  **no** menulis entri ke `reports/FENCE_REGISTRY.md`. Entri ledger
  ditambahkan on commit authority layer ini.
- **Batas:** hanya keberadaan and keunikan lokal in dalam box B, kondisional
  on base K1-K5 and K6 M1-M10; bukan klaim global, stabilitas, spektrum,
  chaos, ergodisitas, KAM, PDE, fisika, prioritas, Lean/Coq, or RH.
- **Catatan proses:** audit Â§T6 mencatat pra-registrasi r6 in-commit bersama
  kode (`ad34cbc`). Catatan itu dipertahankan; keputusan pemilik menetapkan
  sertifikasi r6 berlaku.
- **Temuan terpisah (belum diputuskan):** `README.md` baris 27 mengklaim
  Learn-harness `A-2026-0050`, tetapi belum ada entri `A-2026-0050` in
  registry. ID itu masih kosong; `T-2026-0050` adalah ID berbeda (RH
  scaffold). Klaim README belum bisa diverifikasi dari ledger.

## 2026-10-27 â€” Q3 v2 superseded oleh Q3 v3 (sensus abc low-rad lengkap)

- **Keputusan:** Sensus Q3 v2 which mengunci `max_prime = 100` dinyatakan
  parsial and superseded. Q3 v3 memakai limit kelengkapan
  `rad(abc) < c^(5/7)`, sehingga enumerasi low-rad lengkap.
- **Alasan:** v2 menemukan 12 triple on C=10^7; enumerasi lengkap menemukan
  17 triple. Lima triple which hilang memuat prima 109â€“173, jadi
  `max_prime=100` bukan limit which sah for kelengkapan.
- **Commit:** pra-registrasi v3 `0d229bb` (sha256LF `aed8e63c...`);
  implementasi, receipt, report, and registry dicatat on commit `29b1739`.
- **Registry:** `A-2026-0052` (v3, 17 triple) ditambahkan with verdict
  `ALL PASS`. `A-2026-0032` (C=100.000, 6 triple) no in-retract; dua baris
  hash modul/guard diperbarui ke v3 with note tanggal, and klaim 6 triple
  no berubah.
- **Batas:** sensus finit C=10^7; bukan pembuktian konjektur abc; no ada
  klaim asimtotik/RH/GRH/faktorisasi/RSA/ECC/Anderson/fisika.
- **Dampak:** `reports/DAFTAR_MASALAH_KERJA.md` Q3 menjadi ALL PASS v3;
  `brain.md` Â§10.3 Q3 menjadi DONE/CERTIFIED. Receipt v2 parsial disimpan in
  `reports/abc_census_v2_10000000.json` sebagai bukti supersession, bukan
  sertifikat.

## 2026-10-27 â€” Koreksi registry: r7, BSD v2, BSD v3

- **Keputusan pemilik:**
  - `A-2026-0049` (r7) in-retract menjadi `RETRACTED`: receipt `result: {}`,
    report placeholder, modul hanya memanggil r5, and
    `msaf/tests/test_figure_eight_r7.py` no ada.
  - `T-2026-0049` (BSD v2) dipulihkan sebagai heading in atas badan yatim;
    klaim 5 kurva pilot no berubah.
  - `A-2026-0051` (BSD v3) direklasifikasi dari `CERTIFIED (pending CI)` ke
    `RECON`: `PREREG_BSD_V3_2026-10-27.md` bukan pra-registrasi sah and
    `msaf/bsd_v3.py` hanya membungkus `bsd_v2`. Receipt stub dipertahankan
    sebagai bukti; relasi dikoreksi ke `T-2026-0049`.
- **Alasan:** status registry sebelumnya no cocok with artefak; r7 no
  punya receipt/test r7, BSD v3 no punya prereg sah, and badan BSD v2
  kehilangan heading akibat `d56242c`.
- **Commit:** `6fb3e17` (patch registry and dossier); receipt stub BSD v3
  in-track on `c4d2ee1`.
- **Dampak:** `reports/REGISTRY_CORRECTION_DOSSIER_2026-10-27.md` menjadi
  note keputusan; `brain.md` Â§10.3 menandai r7 RETRACTED and BSD v3 RECON.
  Tidak ada artefak ber-`sha256LF` which dihapus; `A-2026-0052` no berubah.

## 2026-10-27 â€” Konsolidasi MCP T2N: `t2n_core` + `t2n_viz`

- **Keputusan pemilik:** dua server t2n final â€” `t2n_core` (repokeeper +
  archivist + science + scribe + watchtower, 30 tool) and `t2n_viz`
  (illumina + materials, 7 tool). Dua server `shp_*` no disentuh, sehingga
  total target 4 server aktif.
- **Bug which diperbaiki:** `mcp/t2n/illumina.py` gagal diimpor karena definisi
  `render_html_dashboard` hilang; badannya tertinggal setelah `return` in
  `render_materials_dashboard`. Fungsi dipulihkan sebagai tool publik, and
  jalur materials memakai impor malas.
- **Artefak:** `mcp/t2n_core.py`, `mcp/t2n_viz.py`, shim
  `mcp/t2n_combined.py`, `opencode.jsonc` (2 entri), guard
  `msaf/tests/test_mcp_servers.py`.
- **Verifikasi:** `python -m pytest msaf/tests/test_mcp_servers.py -q` â†’
  7 passed; smoke produksi menunjukkan `t2n_core` 30 tool and `t2n_viz`
  7 tool with `repo_root`/`write_roots` benar. Empat guard minimum plus
  guard MCP: 21 passed. `lake build` no dijalankan karena no ada
  perubahan Lean.
- **Commit:** pra-registrasi `91818bc`; implementasi `7412eff`.
- **Proses:** seluruh 10 proses t2n berhenti saat `opencode.jsonc` in-reload;
  6 proses `shp_*` (3 batch) tetap berjalan. Duplikasi shp no diubah
  karena limit "jangan sentuh `shp_*`".
- **Batas:** ini perbaikan infrastruktur, bukan klaim ilmiah. Tidak ada klaim
  RH/abc/BSD/figure-eight/Lean/Coq/fisika; `materials.mp_query` tetap butuh
  jaringan and no diuji.

## 2026-10-27 â€” Pemisahan suite lambat dari CI default

- **Keputusan:** kampanye figure-eight r5/r6 marked `slow` and dipindah ke
  workflow `Slow tests` (terjadwal 02:00 WIB + manual, `timeout-minutes:
  300`); job `python-tests` menjalankan
  `python -m pytest msaf -q -m "not slow"`.
- **Alasan:** `python-tests` dibatasi 60 menit, sedangkan run `40401144645`
  berjalan 57+ menit tanpa selesai; `msaf/tests/test_figure_eight_r6.py`
  juga memanggil `run_campaign()` dua kali tanpa fixture.
- **Perubahan:** `pytest.ini` mendaftarkan marker `slow`; dua uji kampanye r5
  diberi marker; r6 memakai fixture `scope="module"` (satu kampanye, bukan
  dua) and dua uji kampanye diberi marker; guard
  `msaf/tests/test_ci_slow_split.py` mengunci pemisahan ini.
- **Verifikasi:** koleksi `-m slow` = 4 uji, `-m "not slow"` = 786 uji,
  total 790; uji murah r5/r6 8 passed; `test_fence_registry` and
  `test_ci_verification_paths` lulus setelah hash `ci.yml` and
  `test_figure_eight_r6.py` diperbarui with note bertanggal.
- **Commit:** pra-registrasi `a33d5db`; implementasi `4570e0a`.
- **Batas:** "CI hijau" kini berarti suite cepat. r5/r6 hanya dibuktikan oleh
  workflow `Slow tests`; jangan menyebut r5/r6 hijau tanpa result workflow itu.
  Tidak ada asersi, ambang, receipt, or verdict which dihapus/diubah.
- **Koreksi 2026-10-27:** angka `timeout-minutes: 60` which disebut in atas
  adalah milik job `lean-kernel`, bukan `python-tests`; job `python-tests`
  no memiliki timeout. Alasan pemisahan which terukur adalah run P2
  `40261066426` which menghabiskan 202,5 menit on `python-tests`, and run
  `40401144645` which berjalan 57+ menit tanpa selesai. Keputusan desain no
  berubah; no ada kode/CI which diubah oleh koreksi ini.

## 2026-10-27 â€” Tiga keputusan delegasi: status sertifikasi and gerbang klaim r5/r6

- **Dasar delegasi:** pemilik menyerahkan keputusan with syarat klaim hanya
  boleh jika semua syarat terpenuhi and terbukti/dapat dibuktikan. Keputusan
  berikut berbasis pemeriksaan artefak, bukan asumsi.

### D1 â€” `T-2026-0049` and `A-2026-0048` tetap CERTIFIED with pengecualian proses tercatat

- **Keputusan:** kedua entri tetap `CERTIFIED`. Pelanggaran prereg 2026-10-25
  (commit campuran; tanggal 2026-10-30 adalah tanggal target, bukan tanggal
  registrasi) dicatat sebagai pengecualian proses, bukan alasan menurunkan
  status. Preseden: `A-2026-0047` (r6), diputuskan pemilik 2026-10-26.
- **Bukti `T-2026-0049`:** receipt `reports/bsd_v2_2026-10-30.json` mencatat
  `all_pass: true`, 5 kurva, and `match: true` on setiap kurva; hash
  pra-registrasi, receipt, and modul cocok with baris `sha256LF`;
  `msaf/tests/test_bsd_v2.py` lulus 2/2 and menghitung ulang formula eksak
  melalui `bsd_v2.build_payload()` tanpa float/numpy.
- **Bukti `A-2026-0048`:** receipt `reports/twin_prime_v4_2026-10-30.json`
  mencatat `all_pass: true`, `count_a = count_b = 27.412.679`,
  `elementwise_mismatches = 0`, and `pairs_sha256_a == pairs_sha256_b`;
  checkpoint 10^6â€“10^9 cocok with nilai referensi (8169, 58980, 440312,
  3424506); hash pra-registrasi, receipt, and modul cocok.
- **Batas:** klaim tetap finit â€” 5 kurva pilot rank-0 with `|Ð¨| = 1`
  diasumsikan (BSD v2), and sensus 10^10 (twin v4). Bukan bukti BSD or twin
  prime umum. Tidak ada uji lokal which menjalankan ulang sensus 10^10;
  integritas receipt dijaga `test_fence_registry` and checkpoint referensi.
- **Konsekuensi:** tanggal no diedit retroaktif; no ada penulisan ulang
  entri `CERTIFIED`; cukup note bertanggal which aditif.

### D2 â€” `A-2026-0050` tetap CERTIFIED for stub deterministik

- **Keputusan:** `CERTIFIED` dipertahankan. Label ini menyatakan perilaku stub
  deterministik which tercatat, bukan klaim belajar.
- **Bukti:** pra-registrasi nyata, receipt `ALL PASS`, hash
  pra-registrasi/receipt/modul/test cocok, and
  `msaf/tests/test_learnharness_v1.py` lulus.
- **Batas:** no ada klaim performa ML, generalisasi, or kualitas model;
  label `CERTIFIED` no menaikkan stub menjadi implementasi ML.

### D3 â€” Gerbang klaim r5/r6

- **Keputusan:** "CI hijau" default **no pernah** mencakup r5/r6. Klaim
  tentang r5/r6 hanya boleh jika (a) job `python-tests` hijau and (b) workflow
  `Slow tests` hijau on commit which sama.
- **r5:** verdict tersegel adalah `FAILED` (`all_pass: false`, 8/10 baris K6
  lulus). r5 no boleh disebut "green"; which boleh diklaim hanyalah verdict
  `FAILED` which direproduksi.
- **r6:** verdict `ALL PASS`; klaim tetap lokal in box B and kondisional on
  K1â€“K5 serta M1â€“M10.
- **Penguatan bukti:** `slow-tests.yml` kini menjalankan
  `test_fence_registry` **sebelum** kampanye (amendemen pra-registrasi Â§8,
  commit `0d25a53`; implementasi `3a56b86`), sehingga `Slow tests` which hijau
  ikut membuktikan segel receipt. Guard `test_ci_slow_split.py` mengunci
  urutan step.
- **Batas:** hash payload Arb penuh no in-pin karena string interval Arb
  no stabil lintas platform.

## 2026-10-27 â€” Sinkronisasi lapisan otoritas: ledger tombstone, guard, manifest, CURRENT_AUTHORITY

- **Dasar:** pemilik menyetujui eksekusi paket koreksi result audit read-only
  2026-10-27 ("kerjakan and saya setuju"). Audit menemukan hash `sha256LF`
  0 drift and 0 sertifikat hilang; temuan utamanya justru lapisan otoritas
  which stale, ledger tombstone which mengunci pernyataan palsu, and cacat
  tampilan/teks registry. Paket which dieksekusi entri ini: **D1 (tombstone)**
  and **D2 ("otoritas")**. D3 (registry), D4 (Stage), D6 (housekeeping)
  menyusul on entri/commit terpisah.
- **Perubahan D1:**
  `reports/ARCHIVE_TOMBSTONES.md` â€” section "Tombstone which already dieksekusi"
  kini memuat tabel 5 baris (3 `tombstoned`: Stage 2 MD, Stage 3 MD,
  `append_status.py`; 2 `stubbed`: `HANDOFF.md`, `README_custody.md`),
  recovery `git show 995576c~1:<path>` (semuanya terverifikasi ada in komit
  itu, reachable dari `main`). Kalimat "Belum ada tombstone which dieksekusi."
  dihapus karena no benar sejak `995576c`.
- **Perubahan guard:** `msaf/tests/test_authority_manifest.py` no lagi
  mengunci pernyataan palsu itu. Guard baru menolak ledger which masih
  berklaim "belum ada"; verifying bahwa tabel eksekusi ada, menyebut
  commit `995576c`, and mencakup `tombstoned`+`stubbed`. State `stubbed`
  ditambahkan ke `ALLOWED_SUPERSEDED_STATES`.
- **Perubahan manifest:** `reports/AUTHORITY_MANIFEST.json` â€” lima entri
  `superseded` diselaraskan with disk (`tombstoned`/`stubbed`,
  `recovery_commit: 995576c~1`); hash aktif semua dokumen otoritas diperbarui
  on commit which sama.
- **Perubahan D2:** `CURRENT_AUTHORITY.md` Â§5 and header diperbarui: status
  D1/D2 delegasi 2026-10-27 (`T-2026-0049`, `A-2026-0048` CERTIFIED with
  pengecualian proses; r7 `A-2026-0049` RETRACTED; `A-2026-0050` CERTIFIED
  terbatas stub deterministik) tertulis eksplisit, sehingga dokumen ini lebih
  tinggi no lagi bertentangan with `DECISION_LOG`.
- **Batas:** no ada baris `sha256LF` registry, receipt, kode matematika,
  or verdict which berubah; no ada status registry dinaikkan/diturunkan.
- **Risiko tercatat (bukan keputusan terbuka):** workflow `Slow tests`
  belum pernah menjalankan r6 in `main`; klaim r6 tetap berbasis keputusan
  pemilik 2026-10-26 + receipt, and gerbang D3 (2026-10-27) menuntut run
  `Slow tests` hijau for pembuktian lanjutan.
- **Verifikasi lokal saat entri ini ditulis:** 14 passed on
  `test_authority_manifest`, `test_fence_registry`, `test_lean_axiom_audit`,
  `test_anti_circularity_gate`.

## 2026-10-27 â€” Reparasi teks registry (D3): fence, marker, inline, relasi, note skema

- **Dasar:** paket koreksi result audit read-only 2026-10-27 disetujui pemilik.
  Audit menemukan 0 drift `sha256LF`; seluruh temuan bersifat teks, bukan
  sertifikat. Eksekusi dalam dua pass: pass utama (skrip sementara
  `repair_registry.py`) lalu pass penyelesaian (`finish_d3.py`) setelah
  verifikasi byte-level; keduanya memakai asersi preimage per baris and
  menolak menulis bila no cocok.
- **Mekanisme korupsi (dicek terhadap blob kelahiran entri, commit
  `7c13788`):** backtick diikuti huruf/digit which juga karakter escape Python
  (`a b f r t e 1-7`) dimakan oleh sebuah pass escape: urutan `\a`â†’0x07 dst.
  juga menelan tetangganya â€” contoh: kata `all_pass` on kalimat K6 lahir
  sebagai byte 0x5C+0x07+`ll_pass`; nama `run_base()` lahir sebagai
  `un_base()` tanpa huruf `r`. Backslash tak-dikenal kadang bertahan
  (contoh: `...md\ in-commit`). Peta pemulihan: chr 7â†’a, 6â†’6, 8â†’b, 12â†’f,
  13â†’r, 1â†’1, TABâ†’t, backslashâ†’backtick.
- **Pass 1 (registry `reports/FENCE_REGISTRY.md`):** 10 fence-open and 10
  fence-close korup; 8 marker `**Sertifikat:'` dikembalikan ke
  `**Sertifikat:**`; 14 baris prosa with control char dikembalikan ke
  konten aslinya; 5 jalur `eports/` dikembalikan ke `reports/`. Relasi logika:
  on entri r6, "target r5 which INCONCLUSIVE" dikoreksi ke "FAILED" (N1,
  sesuai verdict tersegel r5); on entri r7, "melanjutkan A-2026-0044 (r5)"
  diperjelas bahwa r5 no membuka entri registry and slot `A-2026-0044`
  sengaja kosong (N2). Ditambah: note duplikat in bawah `T-2026-0043`
  (sertifikasi kanonik r4 = `A-2026-0043`; entri dianggap penjelasan ulang,
  no dihapus) and bullet skema tentang prefix `A-` on entri `0032..0047`
  which on masanya dipakai sebagai label slot urutan, bukan tipe audit;
  `Jenis:` in badan entri lama adalah verdict otoritatif, entri baru wajib
  prefix = `Jenis` (N4).
- **Pass 2 (penyelesaian, temuan verifikasi byte-level):** pasangan fence
  `T-2026-0043` which terlewat dipulihkan (open `` `\text `` â†’ `` ```text ``
  and close `` ` `` â†’ `` ``` ``); backtick pembuka which dimakan direkonstruksi
  on 7 lokasi: pra-registrasi Navier diskrit; kedua jalur
  `reports/FIGURE_EIGHT_R3_2026-10-23.md`/`PREREG_FIGURE_EIGHT_R4` on
  `T-2026-0043`; jalur r3 and hash `6b0b71e9...df829c9` on
  `A-2026-0043`; `un_base()` â†’ `` `run_base()` `` (nama fungsi diverifikasi
  terhadap ketiga modul); commit `3a21eb`; `` `18 passed, 1 failed` ``; and
  `` `19 passed` `` (angka sesuai report r4 Â§9, final 19 passed). Backtick
  penutup hilang direkonstruksi on `test_base_campaign_reproduces_sealed_receipt`
  (spasi ganda menjadi `` ` `` + satu spasi) and spasi ganda
  `.md  (INCON` menjadi `.md` + backtick + satu spasi.`
- **Jaminan:** 433 baris sertifikat `sha256LF` terverifikasi byte-identik
  baik terhadap `HEAD 6fa6646` maupun state pra-reparasi; 0 control char
  tersisa; hanya 2 backslash sah (path Windows in L229 and L1095); 59
  pasangan fence seimbang tanpa fence liar; seluruh baris which direparasi
  berjumlah backtick genap. Tidak ada hash, verdict, status, angka tes
  (18/19), or nama fungsi which ditulis ulang melebihi pemulihan bentuk
  aslinya; perubahan diinterpretasikan per baris.
- **Verifikasi:** 14 passed (keempat gerbang: authority-manifest,
  fence-registry, lean-axiom-audit, anti-circularity-gate).
- **Batas:** perbaikan bersifat teks/backtick pemulihan, bukan perubahan
  matematika, hash, or verdict; registry no mendapat entri baru; guard
  hanya memeriksa heading/STATUS/cert-line/hash â€” inspeksi manual per baris
  tetap dilakukan karena teks prosa in luar jangkauan guard.

## 2026-10-27 â€” Penanda historis scaffold RH (D4)

- **Dasar:** paket koreksi result audit read-only 2026-10-27 (persetujuan
  pemilik). Temuan D4: arsip `reports/RH_SCAFFOLD_NOTES/` berisi prompt
  "SYSTEM PROMPT" superseded which tampak sebagai instruksi aktif â€” risiko
  resurrect â€” and `generate_receipts.py` bisa dipakai diam-diam for
  meregenerasi receipt masa lalu tanpa otorisasi.
- **Perubahan (semuanya aditif):**
  - Header peringatan historis ditambahkan in atas
    `Stage_1_Formalization_Test_Function_Space.md` and
    `Stage_4_Containment_Proof.md`: status HISTORIS, jangan dieksekusi
    sebagai tugas baru; rujukan aturan `AGENTS.md` and koreksi lingkup
    Stage 2/3; Stage 4 diberi note khusus bahwa frasa "formal Riemann
    Hypothesis claim" on prompt adalah bacaan salah (lingkup P2 hanya
    diagonal `XC`), and `Stage_4_Containment_Proof.lean` tetap tersegel
    `T-2026-0050` (jangan edit/hapus).
  - Docstring `generate_receipts.py` diberi peringatan HISTORISâ€”JANGAN
    DIEKSEKUSI tanpa pra-registrasi and keputusan pemilik; badan kode no
    diubah and skrip no dijalankan.
  - Byte file receipt no disentuh karena beberapa receipt
    SHA-256LF-nya dipakai referensi; penanda historis masuk via ledger:
    `reports/ARCHIVE_TOMBSTONES.md` mendapat section "Penanda historis paket
    koreksi (D4, 2026-10-27)" (status `historical`) and
    `reports/AUTHORITY_MANIFEST.json` mendapat entri
    `historical_artifacts` for
    `Stage_4_Containment_Proof_receipt.json` (`recovery_commit a55fe79`;
    byte-verifikasi: isi identik with versi in `a55fe79`).
- **Jaminan:** no ada baris `sha256LF` registry, byte receipt, verdict,
  or kode matematika berubah; `.lean` Stage 1â€“4 no disentuh; guard
  registry and manifest tetap lulus.
- **Verifikasi:** 14 passed on keempat gerbang (authority-manifest,
  fence-registry, lean-axiom-audit, anti-circularity-gate).
- **Batas:** penanda hidup in dokumen prose/ledger, bukan in file artifact;
  pembaca manusia which meneruskan instruksi prompt tetap bertanggung jawab
  membaca header.

## 2026-10-27 â€” Housekeeping D6: README, dossier resolusi, banner review, guard presisi tes

- **Dasar:** paket koreksi result audit read-only 2026-10-27 (persetujuan
  pemilik); penutup dari seri D1â€“D4. Entri lain in hari which sama mencatat
  D1/D2 (sinkronisasi otoritas), D3 (reparasi registry), D4 (penanda
  historis scaffold). Risiko residual D5 dicatat on entri D1/D2 and
  gerbang D3: workflow `Slow tests` belum pernah dijalankan for r6 in
  `main` â€” bukan keputusan terbuka; pemilik memicu workflow bila ingin
  pembuktian tambahan.
- **README.md:** angka tes stale `(489 tests)` on baris badge CI dihapus;
  klaim baris status r7 dari `CERTIFIED` dikoreksi ke `RETRACTED stub` â€”
  sesuai `FENCE_REGISTRY.md` `A-2026-0049` result commit `6fb3e17`. Klaim
  Learn-harness `A-2026-0050` no diubah (already benar: "now verified with
  registry entry").
- **Dossier `REGISTRY_CORRECTION_DOSSIER_2026-10-27.md`:** section Â§7
  "Resolusi (2026-10-27)" ditambahkan (aditif): ketiga masukan dossier
  dieksekusi oleh commit `6fb3e17` â€” r7 `RETRACTED` (opsi A),
  `T-2026-0049` heading dipulihkan + `CERTIFIED` (heading dirusak
  `d56242c`), `A-2026-0051` heading and `Status: RECON`. Bagian 1â€“6 tetap
  state DRAFT ketika dossier ditulis.
- **`WEEKLY_REVIEW_2026-10-20_27.md`:** banner SNAPSHOT HISTORIS in atas
  dokumen (angka snapshot, bukan status kini; source status aktif
  `CURRENT_AUTHORITY.md` + `DECISION_LOG` + registry).
- **`NONFINITE_DEFECT.md` Â§3 + `msaf/tests/conftest.py`:** dikoreksi klaim
  lama "empat modul ... in level modul" â€” verifikasi manual menunjukkan
  keenam `ctx.prec = 256` berada in dalam fungsi (indent 4, saat tes
  berjalan, tanpa pemulihan), sehingga kelas kebocoran lintas-modul tetap
  nyata. Perbaikan direalisasi Sebagai fixture autouse
  `arb_ctx_prec_guard` which menyimpan `ctx.prec` in awal tes and
  memulihkan nilai which sama in akhirnya; enam tulisan no dihapus karena
  menghapusnya membuat result bergantung urutan eksekusi (ambient presisi
  no lagi terdefinisi), sedangkan guard menjaga nilai eksplisit tanpa
  menyentuh badan enam modul test. `conftest.py` no men-set or
  menurunkan presisi apa pun.
- **Validasi empiris:** subset 10 modul flint (test_msaf, test_xi_identities,
  test_sbp_correspondence, test_convergence_order, test_moore_premises,
  test_tail_decay, test_periodic_bridge, test_bridge, test_ulam_spectral,
  test_navier_interpolation) = 186 passed baik sebelum maupun sesudah
  conftest ditambahkan. Verdict for suite utuh adalah job CI
  `python-tests` on commit ini; no ada klaim "CI hijau" sebelum job
  itu selesai.
- **Penyisihan:** file kerja sementara dari paket koreksi (helper
  tombstone and semua `.bak`) dihapus dari working tree; semuanya
  untracked, bukan artefak, no pernah ikut commit.
- **Jaminan:** no ada baris `sha256LF` registry, receipt, verdict,
  status, or kode matematika berubah; conftest aditif; empat gerbang
  tetap dijalankan on commit ini.

## 2026-10-28 - Housekeeping: penyisihan dump konsol and artefak build

- **Dasar:** permintaan pemilik 2026-10-28 for membersihkan file which
  benar-benar no diperlukan; inventaris referensi read-only atas 761
  file tracked dijalankan lebih dulu.
- **Dihapus (tracked):** `msaf/lmbig.txt`, `msaf/lmb3000.txt`,
  `msaf/ladder9000.txt`, `msaf/ladders6000.txt` (dump konsol ladder; data
  ada in JSON `reports/lambda_min_*`), `reports/TAW_clean_worktree_suite.txt`
  (output workspace `TAW-clean`, bukan artefak repo ini), and lima
  `reports/c4_s2026100*_stderr.log` nol byte.
- **Dihapus (untracked/generated):** `formal_bridge/*.vo`, `*.glob`,
  `*.vok`, `*.vos`, `.*.aux` (dapat dibangun ulang dari `.v`),
  `__pycache__/`, `.pytest_cache/`, and `joblog/`.
- **Tidak disentuh:** semua file ber-`sha256LF`, `reports/` bersertifikat,
  `mcp/out/` (ledger hash-chain), `audit_collatz` bulk evidence,
  `msaf/learnharness/`, `lean/.lake/` (cache build 7.2 GB; dipertahankan
  agar rebuild no mahal), and seluruh log audit/attempt which tercatat
  sebagai bukti insiden.
- **Verifikasi sebelum hapus:** `git grep` no menemukan referensi; no
  ada baris `sha256LF`; no ada test/workflow which membaca path tersebut;
  salinan karantina eksternal and `MANIFEST.sha256` disimpan in
  `C:\Users\usER\AppData\Local\Temp\opencode\quarantine_T-hat-N_2026-10-28\`;
  recovery commit `f56f25f`, `feee3ce`, `ffd79f4`, and `19fe938` semuanya
  reachable dari `main`.
- **Registry/authority:** no ada entri registry which diubah or
  dicabut; tombstone dicatat in `reports/ARCHIVE_TOMBSTONES.md`; hash
  `DECISION_LOG.md` and `ARCHIVE_TOMBSTONES.md` in
  `reports/AUTHORITY_MANIFEST.json` diperbarui on commit which sama.
- **Batas:** ini penyisihan artefak, bukan perubahan klaim matematika; no
  ada verdict, receipt, kode Lean/Coq, or test which diubah. Status "CI
  hijau" tetap menunggu job `python-tests` on commit which memuat
  perubahan ini.

## Keputusan which masih menunggu pemilik

Tiga question delegasi 2026-10-27 already diputuskan in atas (D1â€“D3). Tidak
ada item dari daftar itu which tersisa. Risiko residual which dicatat, bukan
keputusan terbuka: `A-2026-0048` no memiliki uji khusus v4 which dapat
menjalankan ulang sensus 10^10 secara lokal; verifikasinya bergantung on
receipt tersegel, checkpoint referensi, and guard registry.




