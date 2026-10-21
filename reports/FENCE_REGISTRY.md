# FENCE_REGISTRY — buku besar klaim finit (P3)

Dibuat 2026-10-17 sebagai instrumen P3 portfolio MSAF
(`reports/MSAF_PORTFOLIO_2026-10-17.md` §3.3; dokumen perencanaan
non-binding). Setiap entri = **satu klaim finit** dengan sertifikat yang
dapat diperiksa mesin; entri yang tidak lulus guard CI tidak boleh
berstatus CERTIFIED. Entri audit P1 (`A-2026-0001`) mengikuti laporan
`reports/AUDIT_DBN_L4REPORT_2026-10-17.md` (pra-reg §6: registry
mengikuti laporan L4).

## Skema entri

- **ID:** `<Jenis>-<tahun>-<nomor>` (contoh format; nomor 4 digit).
- **Jenis:** `T` = teorema kelas finit tersertifikasi; `F` = pagar /
  hasil negatif tersertifikasi ("tidak ada X dalam rentang/kelas Y");
  `R` = refutasi (counterexample eksplisit + sertifikat mungil);
  `A` = verdict audit atas klaim pihak ketiga.
- **Pernyataan:** satu kalimat, kuantor eksplisit.
- **Batas:** yang TIDAK diklaim (selalu diisi).
- **Sertifikat:** berkas + sha + perintah verifikasi. Baris sertifikat
  berformat machine-checkable:

  ```text
  sha256LF <64-hex> <path relatif repo, pemisah "/">
  ```

  `sha256LF` = sha256 atas bytes berkas dengan CRLF→LF dinormalisasi
  (platform-stabil: Windows dan CI Linux menghasilkan nilai sama).
- **Status:** `PROPOSED` | `RECON` | `PRE-REG` | `RUNNING` |
  `CERTIFIED` | `FAILED` | `RETRACTED`. Entri tidak dihapus; perubahan
  status menulis ulang baris Status dan/atau menambah catatan.
- **Domino:** ranah klaim (mis. RH-spektral, Montgomery, kombinatorik).
- **Relasi:** entri lain yang terkait/superseded.
- **Guard:** `msaf/tests/test_fence_registry.py` — fail-closed: setiap
  baris `sha256LF ...` diverifikasi (berkas ada + hash cocok); setiap
  entri ber-Status CERTIFIED wajib punya ≥1 baris sertifikat; heading
  entri wajib berformat skema; pelanggaran = CI merah.

## Entri

### T-2026-0001 — Ladder Route S: positif-tertutup dim 201 & 301

- **Jenis:** T
- **Pernyataan:** Dua matriks finit spesifik (tangga Route S, c=100,
  6000 bit; N=100 → dim 201 dan N=150 → dim 301) tersertifikasi
  POSITIVE DEFINITE oleh pivot LDL^T interval (n_pos=201/301,
  n_neg=0, entries_finite=true), dan capture penuh Arb kedua dimensi
  lolos gate G-M0 5/5 dengan lambda_min = 2.4366351145008994e-191
  (dim 201) dan 6.5771898716824545e-248 (dim 301).
- **Batas:** finit per-matrik; bukan pernyataan tentang spektrum
  sebenarnya; bukan tren antar-N; bukan teorema Montgomery, bukan
  Weil-positivity, bukan bukti RH; capture bergantung presisi/provenance
  run tersegel.
- **Status:** CERTIFIED
- **Domino:** RH (spektral, Route S)
- **Relasi:** seri resolusi yang sama dipakai entri F-2026-0001;
  laporan: `reports/THREE_TASKS_2026-10-15.md` §4–§5.
- **Perintah verifikasi:** guard CI memeriksa semua sha di bawah;
  reproduksi lane = perintah tercatat di laporan/log bersangkutan.
- **Sertifikat:**

  ```text
  sha256LF 972389c3c7cdf03d7dd910cfbcc83ea91b060381a586a6ddc2beaaacd63ffc3f reports/gw_route_s_ladder_c100.json
  sha256LF 078f0c656875810821bbe520631dc257c786b22b9756763a8291c1fac5e96072 reports/gw_capture_100_100.log
  sha256LF 5d48e70bec479808cd178dc14cf64c9eb46a7e1c9f5bfdf7542bae454487ef53 reports/gw_capture_100_150.log
  sha256LF c645c590e54717cf793a31ecd941640adbbca162caf15108f56dde1da993f75d reports/gw_spectrum_100_100.json
  sha256LF 8fded8394f0ab4e8ed83f537609d313d0d50eef42f09214c30d1cfcd994d161d reports/gw_spectrum_100_150.json
  sha256LF f1e84fb8bd08df5db3a3de42710566dec61e995d85813f99cfc944be275ed057 reports/mont_run_100_100.txt
  sha256LF 0561a06fee2d377addc71bc7ada582710bb4d86ef2db0471d15e69f9bfb3d0e1 reports/mont_run_100_150.txt
  sha256LF 1583fc19623d03bbeafd57879edc9df4b23634e1e9fab467a6ba8a286b5eb402 reports/THREE_TASKS_2026-10-15.md
  ```

### T-2026-0002 — lambda_min dim 321 (irisan c=13): semua eigenvalue positif

- **Jenis:** T
- **Pernyataan:** Matriks finit dim 321 pada irisan c=13 (presisi 6000
  bit, N=160) tersertifikasi memiliki seluruh 321 eigenvalue real,
  finit, dan strictly positive dengan lambda_min ≥
  3.123458832662237e-59 (all_exclude_zero=true).
- **Batas:** finit, satu irisan c=13, satu matriks; tidak menyimpulkan
  upturn/tren asimtotik (lereng masih melandai, tanpa fit eksponen);
  field registry lambda_min_rad/imag_leak_upper = 0.0 adalah artefak
  underflow float64 — bukan nol literal (koreksi bertanggal
  `reports/GW_RADIUS_REGISTRY_CORRECTION_2026-10-17.md`).
- **Status:** CERTIFIED
- **Domino:** RH (spektral, Route A2)
- **Relasi:** melanjutkan rung dim 257 (`lambda_min_eig_ladder_big.json`;
  ratio lambda(321)/lambda(257) = 0.9467838255140328).
- **Perintah verifikasi:** `python msaf/lambda_min_eig_ladder.py
  --prec 6000 --c 13 --ladder 160 --out
  reports/lambda_min_eig_ladder_dim321.json` (tercatat di laporan);
  guard CI memeriksa semua sha di bawah.
- **Sertifikat:**

  ```text
  sha256LF e92e05ef8d37b10bb3e39c65e7537e23c8e3a426da548028a0a560126b60b696 reports/lambda_min_eig_ladder_dim321.json
  sha256LF 8f3a41074718278927b350fc9268600108322aefe7e8dc091245a4d620e1ebbc reports/lambda_min_eig_ladder_dim321.log
  sha256LF 84152da16f02125e85563184053ba958786efed65de68a0d48bfc5f741fdfc84 reports/lambda_min_eig_ladder_big.json
  sha256LF 0ae3747dc9d486b589e23bf380ae740a3d5b7c825a1bbae1eb974a345bcc35e7 reports/GW_LADDER_DIM321_2026-10-17.md
  ```

### F-2026-0001 — Verdik S2 seri Montgomery (dim 201/301/401)

- **Jenis:** F
- **Pernyataan:** Pada tiga resolusi finit yang dibangun (dim
  201/301/401; pipeline kanonik, 2000 surrogat N-matched per ensemble,
  seed 20260927), statistik S2 tidak menghasilkan satu pun dari 18 sel
  dengan p_GUE ≥ 0.05 (maksimum 0.0180; 17 sel di lantai tampilan
  0.0000), sehingga verdict tercatat "INCONSISTENT WITH MONTGOMERY AT
  THIS RESOLUTION" untuk ketiga dimensi.
- **Batas:** satu matriks per resolusi — tidak ada klaim arah tren; S1
  tetap CHART-DEPENDENT/INCONCLUSIVE; bukan teorema Montgomery, bukan
  bukti RH, bukan Weil-positivity, bukan penghitungan prima.
- **Status:** CERTIFIED
- **Domino:** RH (Montgomery pair-correlation)
- **Relasi:** memakai matriks T-2026-0001 (dim 201/301); replikasi
  independen = T-2026-0003; blok mesin: `reports/THREE_TASKS_2026-10-15.md`
  §3–§5; dashboard tersegel `reports/gw_diagnostic_v3.html` (v3 beku,
  tidak boleh disunting).
- **Perintah verifikasi:** guard CI memeriksa semua sha di bawah;
  angka = ekstraksi mesin oleh `msaf/gw_resolution_delta.py` dari log
  kanonik.
- **Sertifikat:**

  ```text
  sha256LF 1583fc19623d03bbeafd57879edc9df4b23634e1e9fab467a6ba8a286b5eb402 reports/THREE_TASKS_2026-10-15.md
  sha256LF f1e84fb8bd08df5db3a3de42710566dec61e995d85813f99cfc944be275ed057 reports/mont_run_100_100.txt
  sha256LF 0561a06fee2d377addc71bc7ada582710bb4d86ef2db0471d15e69f9bfb3d0e1 reports/mont_run_100_150.txt
  sha256LF eb072757c3b1b18e502ab25dc1bff329d115b7d6c2c74baec89e279340b54b10 msaf/mont_run.txt
  sha256LF 89c7d5f948626bd51de06f37534bdc4941d3793353dcb80b8557e10e2bed7322 reports/gw_diagnostic_v3.html
  ```

### F-2026-0002 — OUTCOME dim 501: tanpa sertifikat PD dari tangga

- **Jenis:** F
- **Pernyataan:** Tangga Route S 6000 bit (c=100, N=250 → dim 501)
  berhenti di pivot 446 dengan n_pos=446, n_neg=0 (verdict
  "UNDETERMINED at pivot 446"); tidak ada sertifikat
  positive-definite untuk dim 501 dari run ini; sesuai pra-registrasi
  §4 keempat, ini OUTCOME dan statistik titik keempat berakhir.
- **Batas:** bukan bukti non-PD; bukan pernyataan tentang spektrum
  sebenarnya; tidak ada angka S1/S2 untuk dim 501; tidak ada rerun
  (tidak ada kegagalan infrastruktur terenumerasi); statistik
  empat-titik tidak diperluas.
- **Status:** CERTIFIED
- **Domino:** RH (spektral)
- **Relasi:** menutup antrean resolusi ke-4; pra-reg
  `reports/RESOLUTION4_DIM501_PREREG_2026-10-17.md` (commit `ea2ed77`).
- **Perintah verifikasi:** guard CI memeriksa semua sha di bawah;
  rincian insiden wrapper (tidak memengaruhi hasil) di laporan.
- **Sertifikat:**

  ```text
  sha256LF 3d2104901af41e48397f03108f1d98a788f25c3eecac3bf98ee6cb74a9506153 reports/gw_route_s_ladder_c100_n250.json
  sha256LF 3d89637784b2cd82827a06edfd7c544fd62ee56a47e1e25ddf0786e8cf42a001 reports/gw_route_s_ladder_c100_n250.log
  sha256LF 48074b5d8b54b831d4721a5cf8002e945fbf58d4302ca68b6d4fad0234771e67 reports/res4_dim501_launch_2026-10-17.log
  sha256LF 1756a38649cbc9fc3a548b98efaeb9c6a9dbbb72fe6f5fa84486f202b2310f4a reports/GW_RESOLUTION4_DIM501_2026-10-17.md
  ```

### T-2026-0003 — Replikasi independen Engine B atas verdict S2

- **Jenis:** T
- **Pernyataan:** Verifier independen Engine B (mode full, dps 50,
  seed 20260927) mereproduksi konter Engine A pada ketiga dimensi:
  k_GUE 18/18 eksak, k_Poisson 18/18 eksak, semua empat tail 18/18;
  verdict keseluruhan PASS-WITH-ENUMERATED-EXCEPTIONS (B1 parsing PASS,
  B3 gate G-M0 PASS, B2 grid PASS-WITH-ENUMERATED-EXCEPTIONS, counts
  PASS).
- **Batas:** replikasi internal antar-engine repo ini (bukan audit
  pihak ketiga); pengecualian terenumerasi tercatat di findings; tidak
  mengubah status statistik (satu matriks per resolusi); bukan klaim
  universal.
- **Status:** CERTIFIED
- **Domino:** RH (Montgomery)
- **Relasi:** memverifikasi F-2026-0001; instrument gw_montgomery.py
  sha256 072910f2... (per log).
- **Perintah verifikasi:** guard CI memeriksa semua sha di bawah;
  jalur replay penuh tercatat di findings/log.
- **Sertifikat:**

  ```text
  sha256LF 27743364ce1cabfe217b1a7a489524e5a463f8a3c1bdbbb4cb8ae71d8be0330d reports/gw_engine_b_verify.log
  sha256LF f7b3eb01ebc82fbd4bafce57dc56c1cb55e830aa5eb55241ee1e71070a88d95f reports/gw_engine_b_verify.json
  sha256LF 2e50d9794b983950b9692464e46ed339337c12efebdb7d40a04420aa6c2d3af1 reports/ENGINE_B_PILOT_FINDINGS_2026-10-16.md
  ```

### A-2026-0001 — Verdict audit P1 atas rilis review-01787854-v3

- **Jenis:** A
- **Pernyataan:** Audit independen (pra-registrasi beku `86a32c9`;
  L2 item 1–4 + L3) atas rilis beku review-01787854-v3 (commit
  `2e9976c4becbf97e31c56fe75fce07cdff5dd4ea`) mereproduksi keempat lane
  numerik (34/34, 48/48, 47/47, 124/124) dan mengesahkan weld
  theorem-source tiga hipotesis (57/57, weld HELD) tanpa GAP-FOUND di
  dalam scope yang dideklarasikan.
- **Batas:** bukan validasi matematis penuh; L1 not-run (tanpa engine
  container); teorema terbitan tidak direview; reduksi analitik tidak
  dibuktikan ulang; lane rilis tidak di-re-run; daftar coverage lengkap
  = `reports/AUDIT_DBN_L4REPORT_2026-10-17.md` §5; tidak menyatakan
  atau menyangkal RH / pernyataan universal.
- **Status:** CERTIFIED
- **Domino:** RH (bound Lambda ≤ 0.1787854)
- **Relasi:** verdict audit pihak ketiga (entri audit pertama);
  laporan L3 `reports/AUDIT_DBN_L3_2026-10-17.md`.
- **Catatan (2026-10-18):** L1 replay dijalankan setelah izin pemilik
  (engine WSL2 + podman; instalasi owner-gated direkam di log engine).
  Semua langkah exit 0: verify.sh `RESULT: STORED UNCONDITIONAL-CANDIDATE
  REVIEW PASS` (38 cek) + container review default CMD `RESULT: CONTAINER
  REVIEW PASS` (lane fresh; 33 berkas evidence ter-sha256); laporan:
  `reports/AUDIT_DBN_L1_2026-10-18.md`. Frasa "L1 not-run (tanpa engine
  container)" pada Batas di atas = snapshot laporan L4 2026-10-17
  (dibiarkan utuh); status terkini = catatan ini. Label maksimum tetap
  replay-level ("release replayed; numbers reproduced from the release's
  own tooling"), bukan verifikasi independen; sweep penuh tetap tidak
  dijalankan (opsional pra-reg §8); `run_prop410_arb.sh` tidak ada di
  tree rilis (tercatat pra-hasil).
- **Catatan (2026-10-18, sweep penuh — memperbarui kalimat "sweep penuh
  tetap tidak dijalankan" di atas; kalimat itu = snapshot pra-sweep):**
  opsi pra-reg §8 "sweep penuh" DIPILIH pemilik dan dieksekusi pada
  engine WSL2+podman yang sama. Runner + watchdog + header log dipush di
  commit `295e716` SEBELUM perintah pertama (urutan terekam mesin).
  Hasil: `RESULT: FULL SWEEP REPLAY AND METADATA PASS` — fresh path,
  15/15 lane `[PASS]`, komparator rilis mencocokkan semua baris kanonik +
  3.149.013 baris tersegel N=690988..3840000; semua langkah exit 0; image
  `.Id` = pin `5ccd9e3f…` ✓; tree `2e9976c4…` bersih ✓; sha256 16 berkas
  keluaran tercatat in-run. Waktu 03:10:00Z → 05:31:18Z (≈2 j 21 m; cap
  6 j tidak tersentuh; watchdog tidak memutus). Backup luar repo:
  `…\Temp\opencode\l1_sweep_2026-10-18.tar.gz` (24.581.749 B, sha256
  `11bad912…`; isi terverifikasi ulang vs `REPLAY_SHA256SUMS` = 16/16 OK).
  Laporan `reports/AUDIT_P1_L1_SWEEP_2026-10-18.md`. Label maksimum tetap
  replay-level ("release replayed; numbers reproduced from the release's
  own tooling") — bukan verifikasi independen.
- **Perintah verifikasi:** `python -m pytest msaf/tests/test_fence_registry.py
  -q` (guard memeriksa semua sha di bawah, termasuk laporan L4);
  re-run lane: lihat log per-item + laporan L3 §9 (input = berkas rilis
  ter-pin, hash tercatat in-run).
- **Sertifikat:**

  ```text
  sha256LF 26dc97e564a108d7eaf0d39ab8c07676063eedd6ff8aaeb2a5686f3ac5d0822c reports/AUDIT_DBN_PREREG_2026-10-17.md
  sha256LF 144d52ee9efabcd4f13dfbc25f838e8ab5e8e72ae0e1a57117d41f71c5bc0991 reports/audit_p1_l1_launch.log
  sha256LF 14c9c9325924e778311ef1eb3ca4a4ed4fd76f24c319b4444f1bbbd965885873 reports/audit_p1_lean_gate.log
  sha256LF 293520bb86f9410696c406318caa4a267c0ab0012ad06141383d66cf9e6fd491 reports/audit_p1_lean_gate_attempt1.log
  sha256LF 4db08ce9e5ab49dae564029414f7c6b3d9be6b95c5fa6a3ebd9e429652ab06c7 reports/audit_p1_l2_window.log
  sha256LF eaf025f563afa7a519adddccedd4eb9cb8d09f01a4cd4f111edbc3f84e307dbf reports/audit_p1_l2_window_attempt1.log
  sha256LF 940d06aa553481f289fd5f43326cc99fdb453aa7ff4c5010d6f593fcd5123230 reports/audit_p1_l2_window_results.json
  sha256LF 4d10b082e08ac42ce3991861132b1596573ead5c7b9eed3a9bd702a564ff6886 reports/audit_p1_l2_prop410.log
  sha256LF 3a83da89cbe08ad299bd2356f43a2a8f1aa414e83f3164dce49ec7f4747ee7ea reports/audit_p1_l2_prop410_results.json
  sha256LF 60770904e1b4dfafda2a6e719c3374577eaa327e9c0f7a3ce65e43defdee126e reports/audit_p1_l2_tail.log
  sha256LF dcb9f28792a6f0f6b34f7d7843e5663eb1279cf8d666018c321eb06e5466ec57 reports/audit_p1_l2_tail_results.json
  sha256LF 43d27e3893f99241132c5771036704b1c46f6aae7d3618e6087519238dc5959f reports/audit_p1_l2_barrier.log
  sha256LF 22d141d5d043bbf29eee5ba1be51dd9310fbba7f2121a697a327ac2d4981dc80 reports/audit_p1_l2_barrier_results.json
  sha256LF a30938607e32b69c4cbd2d1799760281fd13ac51d4daa47e1a4edbfd7cbc8617 reports/audit_p1_l3.log
  sha256LF 5e085cadd9b1526790420b151312c3b74807372c675ca4f2bc7bef007585468f reports/audit_p1_l3_results.json
  sha256LF 78c833f31406f6f3b647aa42966642754f6ae78dba4a3a6a1cdda496174467f0 reports/audit_p1_l3_smoke1.log
  sha256LF a30938607e32b69c4cbd2d1799760281fd13ac51d4daa47e1a4edbfd7cbc8617 reports/audit_p1_l3_smoke2.log
  sha256LF 2f97ea6e6a640541f3f9976d16f0fbfe204c9f00652130314f873e0ab6cc68a0 audit_p1/l2_window_freeze.py
  sha256LF cbb33b81b0e9d3adf7225ff5a779276639148e26cafa50376a0b66b4a708093c audit_p1/l2_prop410_budget.py
  sha256LF e2d75209733f24de6b1e7b7e060c30158250268565d173c7ca15163fa35a00ff audit_p1/l2_tail_budget.py
  sha256LF 8e81881e30efefe539743ab4aa3eaf86ad4de13af5eac1fec13752c71efcf69d audit_p1/l2_barrier_subset.py
  sha256LF 9af03b5d22a02b31050ca48c9860370edf40d944b8a91a8f888d7d2ff7cb4378 audit_p1/l3_weld_checks.py
  sha256LF 7a5a143ef607b1684372d3339bb3181440cbd6499dcf3dbd3de51112fd867987 reports/AUDIT_DBN_L4REPORT_2026-10-17.md
  sha256LF 2d99e70becd677741a9ce2cab3c8cebf5a411c7c36506f2c2f60e419a6152f1f reports/audit_p1_l1_engine_install_2026-10-18.log
  sha256LF 98ac0dece29aff8b46f12cd178ff3579c09218d8c6b71f1cbce3d8a88fb9c146 reports/audit_p1_l1_replay_2026-10-18.log
  sha256LF 24f01abe20153ed62d61fca43c64c52c5c4431a92eac98fda28d5a87a2040c59 reports/AUDIT_DBN_L1_2026-10-18.md
  sha256LF caa3009837ccc30df568564f5bacad3931514db1a4e59afcc650c270c586b0ca audit_p1/l1_fetch.sh
  sha256LF dab87b5c5951979ade480da12fc5212552b5277b12905c725caad3d51587618b audit_p1/l1_run.sh
  sha256LF 094728296caa5071ee02e3bd5f1908af2c8640d236d295e99582959a49187d60 reports/audit_p1_l1_sweep_2026-10-18.log
  sha256LF 16eaef71e97d3a7b3922916fcb7eba20d796a2261a2d825658d61cad4471c6ca reports/AUDIT_P1_L1_SWEEP_2026-10-18.md
  sha256LF 911f63b8be290581f773c3114cb3ebca7597f167556dfe08ff86bf32fe1cdfff audit_p1/l1_sweep.sh
  sha256LF b85f1cde2d5aaef00da483ab07e4ee128a44859125d13c0206c7a40f66e1d106 audit_p1/l1_sweep_watchdog.sh
  ```

### A-2026-0002 — Audit probe BB(5): replay saksi rilis Coq-BB5 v1.0.0

- **Jenis:** A
- **Pernyataan:** Audit terpra-registrasi (commit beku `fe90659`, dipush
  sebelum perintah audit pertama; eksekusi 2026-10-18 04:15:36Z–04:17:01Z,
  85 s) atas klaim pihak ketiga S(5) = 47.176.870 / Σ(5) = 4.098
  (Coq-BB5 `9142e219229baf2245d3f70851947230ea28a318`; rilis Zenodo
  `10.5281/zenodo.17061968`): kedua saksi halt publik direplay eksak oleh
  dua engine independen dalam-repo (baterai 15 mesin 15/15 di kedua engine,
  rerun byte-identik, lintas-engine sepakat; juara 47.176.870 langkah /
  4.098 ones); berkas pernyataan ter-pin diunduh lewat dua jalur independen
  (sha256 sama) dan ditranskripsi; weld arsip Zenodo ↔ clone = 217/218
  berkas identik (hanya `README.md` berbeda); replay berkas enumerasi BB(3)
  (5.417 baris; 1.772 baris `halt`) konsisten dengan tabel keputusan beku
  (X = 20, Y = 6, argmax = bentuk `---` juara BB(3)); scan higiene tekstual:
  0 `Admitted`/`Abort`/`Conjecture`, flag terekam di `BusyCoq/LibTactics.v`
  (1 `Axiom inj_pair2`, 1 `admit.` di definisi taktik), 14 `Parameter` =
  antarmuka `Module Type Ctx`, 344 `Hypothesis` = section-local.
- **Batas:** replay saksi finit ≠ peer review dan ≠ bukti BB(5); arah
  universal ("tidak ada mesin 5-state yang mengalahkan") tidak diuji; scan
  higiene = tekstual, bukan cek kernel, tidak membersihkan/menghukum berkas
  mana pun; E bukan enumerasi independen dan tanpa klaim baris non-halt;
  P = daftar perbedaan tanpa verdict; item R (rebuild Coq 8.20.1 +
  `Print Assumptions BB5_value.`) **NOT-RUN** (owner-gated; prasyarat:
  sweep L1 selesai + izin eksplisit pemilik); gate anti-sirkularitas =
  TOOL NOT RUN (NO_LEAN_FILES); tidak menyatakan atau menyangkal RH /
  P≠NP; label maksimum = daftar §1 laporan.
- **Status:** CERTIFIED
- **Domino:** tidak ada (probe eksternal; bukan domino RH)
- **Relasi:** probe audit eksternal pertama; audit pihak ketiga kedua
  setelah `A-2026-0001`; laporan `reports/AUDIT_BB5_REPORT_2026-10-18.md`;
  pra-registrasi `fe90659`; recon `reports/AUDIT_BB5_RECON_2026-10-18.md`.
- **Catatan (2026-10-19): item R DIEKSEKUSI dan SELESAI** — memperbarui
  kalimat "item R (rebuild Coq 8.20.1 + `Print Assumptions BB5_value.`)
  **NOT-RUN** (owner-gated; ...)" di atas; kalimat itu = snapshot
  pra-eksekusi (entri tidak dihapus, hanya dicatat). Attempt 5 SELESAI
  2026-10-19T00:31:14Z: BusyCoq 25/25 `.vo`, BB5 50/50 `.vo`,
  `BB5_Theorem.vo` ada (6.859 B), semua langkah `EXIT: 0`, `PHASER_COMPLETE`
  set; `make` self-report `real 267m59.105s` (vanilla Coq 8.20.1 tanpa
  `coq-native`, `make -j2`). Blok akhir `Axioms:` = TEPAT satu aksioma:
  `FunctionalExtensionality.functional_extensionality_dep` — klaim README
  upstream (`9142e219…`) COCOK dengan keluaran teramati. Wall/backstop epoch
  `1792364575` (23:02:55Z) tercapai di tengah attempt 5 → tercatat
  `UNRESOLVED-BUDGET` as-is + kill SUPPRESSED (D-R5 pra-wall; tick v4.1
  commit `0a97f2b`); build berlanjut, selesai 1 j 28 m 19 s setelah wall
  (overrun dicatat as-is; tanpa retry senyap; blok start presisi tetap 4).
  Attempt 1–4 tanpa hasil audit (setup abort; 2 interupsi lingkungan; 1
  OOM-kill — masing-masing dicatat sebelum attempt berikutnya). Gate
  anti-sirkularitas: `TOOL NOT RUN (NO_LEAN_FILES)` exit 2 (verbatim di
  addendum §7; hanya bisa menurunkan klaim). Addendum:
  `reports/AUDIT_BB5_R_ADDENDUM_2026-10-18.md` (label beku: "the proof was
  rebuilt with Coq 8.20.1 on this host; compilation exited 0; the
  end-of-build assumption print reads: Axioms:
  FunctionalExtensionality.functional_extensionality_dep : forall (A : Type)
  (B : A -> Type) (f g : forall x : A, B x), (forall x : A, f x = g x)
  -> f = g" — rebuild dari sumber ter-pin, bukan verifikasi independen).
- **Perintah verifikasi:** `python -m pytest msaf/tests/test_fence_registry.py
  -q` (guard memeriksa semua sha di bawah); replay: `python3
  audit_bb5/bb5_engine_p.py --out <f>` + `python3 audit_bb5/bb5_engine_q.py
  --out <f>` (baterai W), `python3 audit_bb5/artifact_checks.py bb3-max
  <csv> --engine p|q` (E), `python3 audit_bb5/artifact_checks.py weld-tar
  <tgz> <clone>` (P).
- **Sertifikat:**

  ```text
  sha256LF cc474fe2f8f61d2827fc14762ac8f641c7df0fb68db2c7a3318cbcd8328ee876 reports/AUDIT_BB5_RECON_2026-10-18.md
  sha256LF a2cb34c11d9a77c5a5a375d611290b488a9230f87a620fa45eb68b8be2337acc reports/AUDIT_BB5_PREREG_2026-10-18.md
  sha256LF 955402e8815b1b4403350a922a6879401f6308c79298e6a2da10da1425812193 reports/AUDIT_BB5_REPORT_2026-10-18.md
  sha256LF 4915f42818b4295c7c2c55ade2b874d444d46ab129adc518cb11d61ec3e4005d reports/audit_bb5_phaseA_2026-10-18.log
  sha256LF d2dd6f6068490eb4b177a8b837c0b479b3e076d420fc340b70b4f3dadcc66a18 reports/audit_bb5_witnesses_p_2026-10-18.json
  sha256LF dd8f2d6d16e9fa6e28f033887ce9e791a8d116be0405edc97a396cf03c6d1f42 reports/audit_bb5_witnesses_q_2026-10-18.json
  sha256LF 2cbfa88dc9541f3768da7e2b155a6390f16f29dd628e17d35e0c519de071a069 reports/audit_bb5_weld_2026-10-18.json
  sha256LF 768a69c24e3aec237c6e0a028985c3275a1677d84fea2f5d651f18cebbf27099 reports/audit_bb5_bb3_p_2026-10-18.json
  sha256LF 503c254e47b9efd5aaaf2a9e734ad1b4a4b49e4bca459d384b0362242632b580 reports/audit_bb5_bb3_q_2026-10-18.json
  sha256LF a94220774443486bad7ad2c38141a20ecfce43103204989867f49950ab4af1b4 audit_bb5/bb5_engine_p.py
  sha256LF 37b96a2b4a02530b31c0fe2e9b984a1d2c0a22bc7aea3648b3b5f98072f2a4b1 audit_bb5/bb5_engine_q.py
  sha256LF 03d69223587e4fcae9ecab30e96931de99ccb531db5e20ff988ba7cfd4762ff4 audit_bb5/artifact_checks.py
  sha256LF 294d1dd423f9b4f596435fab813f082bfb781c58d7f810d53060d51c2c7b2cef reports/audit_bb5_phaseR_2026-10-18.log
  sha256LF 11c891930050600297f35d5338e8746e84b2ee19b6dd3a9562a53e8301df297f reports/AUDIT_BB5_R_ADDENDUM_2026-10-18.md
  sha256LF 3f0415e57f6bef052d0e675524376995208c9611b123703d88ecad3c73a52d8c audit_bb5/bb5_phaseR.sh
  sha256LF 0261cae899a03423efc9d76960fe82d5dc06b00382c51a66448fee5f539c5c17 audit_bb5/bb5_phaseR_resume.sh
  sha256LF 86af54de441603b62195cc856d399de1ab19cf8c13dc00f00d75a73ec0c2cf73 audit_bb5/bb5_phaseR_resume2.sh
  sha256LF c3b5132e3c4918f90d7d3447641031fa38621a31d3be6aff07ccdcc821fa18f5 audit_bb5/bb5_phaseR_resume3.sh
  sha256LF 4b55010dd5365a25706c9c00b87d3eb9aad18ff155904c4f9065d9ddb46b9db7 audit_bb5/bb5_phaseR_resume4.sh
  sha256LF ff95fe17855a38bfdddfb6289f84b551d04c09ddb013ab5575c56bf54532b3ea audit_bb5/bb5_phaseR_watchdog.sh
  sha256LF 6eda81a5fb7e2d2653edb3342faf1631fa4fe9816c9d3ef0a195d9b906643bb4 audit_bb5/bb5_phaseR_keepalive_tick.sh
  sha256LF 151a8b467635586ac6f318bfb0ae211df4d129adcf695bf8baa5cc1e89db6f62 audit_bb5/bb5_phaseR_keepalive.ps1
  sha256LF 40c2405d24e6d4188b055e39144cccddf0fc6edb7845bcad7591a1b55359c097 audit_bb5/bb5_phaseR_keepalive_spawn_wmi.ps1
  sha256LF d1a312a1322a0515a1bb31059b86a256257fbba3f4905a5e863d698034a614ed audit_bb5/bb5_phaseR_keepalive_task.ps1
  ```

### A-2026-0003 — Audit P2: replay rekaman verifikasi konvergensi Collatz (proyek Barina)

- **Jenis:** A
- **Pernyataan:** Audit terpra-registrasi (pra-reg `bbbe9ae`, dipush sebelum
  perintah audit pertama; CI hijau `39154348599`; eksekusi
  2026-10-19T00:46:40Z–00:59:52Z ≈ 13 mnt di HEAD `9d9c358`, CI hijau
  `39181863147`; `origin/main == HEAD`; tanpa perubahan parameter) atas klaim
  pihak ketiga C1/C1p/C2 (situs `pcbarina.fit.vutbr.cz`; pin GitHub
  `e98d0294…`/tree `b290c47a…`): (S) 6 capture byte-identik + `site_main.html`
  identik setelah normalisasi baris `Generated` saja; (S4/P) weld arsip↔clone =
  147 identik / 0 berubah / 0 hanya-di-arsip / 15 hanya-di-clone (= 15 symlink
  repo; DISCREPANCY terdokumentasi, lihat catatan); (W) replay dua engine
  independen dalam-repo atas seluruh baris terbit — path 98/98,
  tinggi-standar 97/97, delay 148/148; semua nilai terhitung = terbit, semua
  trajektori mencapai 1, `cap_hits` kosong (cap 10^6), JSON `result`
  deep-equal + re-run stabil, monotonisitas terverifikasi (laporan build
  baterai); (H) fragmen beku verbatim 25/25 (situs) + 14/14 (repo); (S5)
  re-derivasi baterai byte-identik; (E) sweep C ekshaustif
  `odd_checked = 8589934591` (semua ganjil 3 ≤ n < 2^34), `cap_hits = []`,
  `max_steps_to_drop = 547` @ n = `12235060455`; digest 2^24 C↔Python
  identik (MATCH); prefix rekod 2^24 = 38 baris (MATCH kedua engine); E1
  selesai 4 m 36,8 s dari wall 3,5 j. Gate anti-sirkularitas `TOOL NOT RUN
  (NO_LEAN_FILES)` exit 2 (verbatim di laporan §7; self-test 13/13 PASS).
- **Batas:** replay finit ≠ peer review; bukan bukti/penyangkal konjektur
  Collatz; tidak ada klaim untuk n ≥ 2^34; target C1 (≈ 2^71,02) TIDAK
  direproduksi (di luar jangkauan host; item T = NOT-RUN keputusan owner);
  C1p/C2 hanya fragmen transkripsi H; S = snapshot, bukan verdict; E1 =
  replay terbatas; label maksimum = §10 pra-reg dengan nilai teramati di
  laporan; gate anti-sirkularitas hanya bisa menurunkan klaim; tidak
  menyatakan/menyangkal RH atau P≠NP.
- **Status:** CERTIFIED
- **Domino:** tidak ada (probe eksternal; bukan domino RH)
- **Relasi:** audit pihak ketiga ketiga (setelah `A-2026-0001`,
  `A-2026-0002`); pra-registrasi `bbbe9ae`; recon
  `reports/AUDIT_COLLATZ_RECON_2026-10-19.md`; laporan
  `reports/AUDIT_COLLATZ_REPORT_2026-10-19.md` (§1–§11); transkrip beku
  `reports/AUDIT_COLLATZ_LOG_2026-10-19.log`; runner
  `audit_collatz/p2_runners/` (8 skrip; dipakai dari Temp, dikomit tanpa
  modifikasi, 8/8 `cmp` identik); memakai ulang
  `audit_bb5/artifact_checks.py` tanpa modifikasi.
- **Catatan (DISCREPANCY S4/P, 2026-10-19):** ekspektasi beku
  `only_in_clone []` / `identical 162` tidak terpenuhi; teramati
  `identical 147` + `only_in_clone 15` (dua kali, termasuk rerun persis per
  §9). Mekanisme (terekam di log, blok 00:49:39Z): arsip GitHub menyimpan 15
  symlink sebagai member link (`lrwxrwxrwx`); checkout Windows
  (`core.symlinks=false`) mematerialisasi tiap link sebagai berkas regular
  berisi teks target; `weld-tar` hanya membandingkan member tar regular;
  `ls-tree` mengonfirmasi 15 entri mode-120000 di 15 path yang sama. Tidak
  ada drift pada 147 berkas regular (`changed []`,
  `only_in_tarball []`); tanpa perubahan parameter; `weld-tar` tidak
  disentuh. Selisih dicatat verbatim di laporan §6.2.
- **Catatan (S3, 2026-10-19):** percobaan clone pertama gagal jaringan di
  tengah transfer (git exit 128: `RPC failed; curl 56 Recv failure:
  Connection was reset`; `fatal: early EOF`); blok perintah persis dijalankan
  ulang sekali per §9 dan sukses (HEAD `e98d0294…`, tree `b290c47a…`);
  dicatat as-is.
- **Catatan (bukti lokal, tidak dikomit):** arsip `collatz-e98d0294.tar.gz`
  sha256LF `daa821f4…` (181.085 B); biner `collatz_sweep` sha256
  `46d419ad…` (gcc 15.2.0, baris build beku); pohon
  `audit_collatz/exec_2026-10-19/` 2,8 MB (clone/refetch/baterai
  re-derivasi/normalisasi — input bulk pihak ketiga; bagian yang dikomit =
  15 artefak hasil + laporan + log).
- **Perintah verifikasi:** `python -m pytest msaf/tests/test_fence_registry.py
  -q` (guard memverifikasi semua sha di bawah); W1: `python3
  audit_collatz/collatz_engine_p.py w1 --path-battery
  audit_collatz/battery_path_records.tsv --std-battery
  audit_collatz/battery_heights_std_a006885.tsv --out <f>` (engine Q sama),
  W2: `python3 audit_collatz/collatz_engine_p.py w2 --battery
  audit_collatz/battery_delay_records.tsv --out <f>` (engine Q sama), lalu
  `python3 audit_collatz/collatz_tools.py compare <a> <b>`; E: `gcc -O2
  -std=gnu11 -o collatz_sweep audit_collatz/collatz_sweep.c` + `collatz_sweep
  drop 24|34 --out <f>` + `collatz_sweep records 24 --out <f>` + `python3
  audit_collatz/collatz_engine_p.py e2 --bound 16777216 --out <f>` + `e3
  --bound 16777216 --path-battery audit_collatz/battery_path_records.tsv
  --out <f>` + `collatz_tools.py compare-prefix|compare-fields|check-prefix
  …`; S4/P: `python3 audit_bb5/artifact_checks.py weld-tar <tgz> <clone>
  --out <f>`; H: `python3 audit_collatz/claims_check.py <tsv> <dir>`.
- **Sertifikat:**

  ```text
  sha256LF ccf178d070c26e19a8c88af5e34a6d1fbffae743c189b0d8277a96b2b1714e4b reports/AUDIT_COLLATZ_LOG_2026-10-19.log
  sha256LF 855bd8079f2b2e48256be56700a1fd9892f5a3f7d03408b6f442bdfea52ec18b reports/AUDIT_COLLATZ_REPORT_2026-10-19.md
  sha256LF d9c334e2e9cc78c13bb66260ee7d9445940a24488b2dda79b118f173476d9cf8 reports/AUDIT_COLLATZ_PREREG_2026-10-19.md
  sha256LF 03d69223587e4fcae9ecab30e96931de99ccb531db5e20ff988ba7cfd4762ff4 audit_bb5/artifact_checks.py
  sha256LF faa157b296f6fe4924b81eead8dd1182b4104e4af04110075a2bc6f22a0e54ad audit_collatz/battery_path_records.tsv
  sha256LF 9f5bed262520a10bafb292d3f1cf689fc6914062ba70d24cb256e07db28cdbe0 audit_collatz/battery_heights_std_a006885.tsv
  sha256LF 09a252407f6cc89e40499b341671014a8622d3c545d2b636b9ec8a1b45f85cf5 audit_collatz/battery_delay_records.tsv
  sha256LF 18e763a50eb640866902e765d1bb39712bf6799a188e4bbaaf5901a094d23f6c audit_collatz/collatz_engine_p.py
  sha256LF 6761704f3f3a7559284e120bb25cc830e74a37adae85fd8a7b8f94457c45c10a audit_collatz/collatz_engine_q.py
  sha256LF 4c8572927229b9b041cab5c2a186503c2e9d5858524c120c487640c01a6ce365 audit_collatz/collatz_sweep.c
  sha256LF e00c728bb6335a290a9e7cdae9ddebdd8224794d638895361259806785a00374 audit_collatz/collatz_tools.py
  sha256LF 4e3b3f2972d1a90bdb11f00785f8c44e49c0f5a864afbfc9ff5afb4ae6d810f5 audit_collatz/build_batteries.py
  sha256LF d97e074a263efc69fc181dae3b264478ccf00fd300a6ef10b9edec18c4b9d4c5 audit_collatz/claims_check.py
  sha256LF 1555901ec9caed798296abff62b53b49336667d8060a455ae317b9445833f01c audit_collatz/claims_site.tsv
  sha256LF 3c20159e0b0c8e6a2870b33e7b5cfa4ae048bb915b4a26319b4195f45dfe3879 audit_collatz/claims_repo.tsv
  sha256LF 0bdbb5a0b14a730a26e215e63952bd198d5542115115ec5b3df79b7c03eb5cda audit_collatz/exec_2026-10-19/w1_p_r1.json
  sha256LF 974c2aef4493b7a7e830a37cecc99b60132c277fec311109eeae6a45d3a1e0f1 audit_collatz/exec_2026-10-19/w1_p_r2.json
  sha256LF ea4239909d941fefa393cb667a7a3c4308b0a703b9295edc08b1c266bb4b81f1 audit_collatz/exec_2026-10-19/w1_q_r1.json
  sha256LF 800c52445e8c709cbcf6745118607df1bf5ba47668c8c643e8e2d3d587bf9e03 audit_collatz/exec_2026-10-19/w1_q_r2.json
  sha256LF 96b92a332f985c85b11a2c9e51b0c76030c320b6058a4bdb6c62f6a764b30488 audit_collatz/exec_2026-10-19/w2_p_r1.json
  sha256LF 5926fd6ac5a8d8db7a3d6b7b651d7ac815ab2af8dcb0ae1ab16c7fc3f30ae5f7 audit_collatz/exec_2026-10-19/w2_p_r2.json
  sha256LF 0318eaa1c89d026e3342463e5f666a733c186631971fde44c00cba4013cec185 audit_collatz/exec_2026-10-19/w2_q_r1.json
  sha256LF 7d00d7c964073794296deadac847fac01a68ad97653ef77bd2a4c3e099fbfd91 audit_collatz/exec_2026-10-19/w2_q_r2.json
  sha256LF 1f6126b209a62793c7b6a3b0d385ffa0a4e60a73a4dcb5b44207c62c2ee02b86 audit_collatz/exec_2026-10-19/c_drop24.json
  sha256LF 8faaaa59181c0c2543cdf4b4906581963050d03030f6024fceb9d1019deb4130 audit_collatz/exec_2026-10-19/p_e2_24.json
  sha256LF c06f38bf3468280be984857e28b4e1bb4fa94a570d54a336e0505727f55ef5e6 audit_collatz/exec_2026-10-19/p_e3_24.json
  sha256LF daa3a5d7a8d3ddb22d3ff069c5091a8819c2927f2b3406e82f68cd9f2ebaef38 audit_collatz/exec_2026-10-19/c_rec24.json
  sha256LF 458ac1241ffea0b7e39e0974281ea3d946747a7bb111a6298758ca1c8244cf45 audit_collatz/exec_2026-10-19/c_drop34.json
  sha256LF 5ca7703e2884e9a0b3a4d28b14251232a2ed570e8df04a11be44016d801b37e6 audit_collatz/exec_2026-10-19/weld.json
  sha256LF 10be3c18bbbf61377225972f5b4cb20313d0f3c5ea2e3cd8d2ea9b55335e80ce audit_collatz/exec_2026-10-19/refetch/battery_build_report.txt
  sha256LF 2a3dea6ff79f664910ed94073125a174dded81f26de3c084226b793dc1af11f9 audit_collatz/p2_runners/p2_final_hashes.sh
  sha256LF eef821b1e1181ce62ff798e34b03b05ebcb7f095ca17a3a039eb7669236a47b9 audit_collatz/p2_runners/p2_note_preflight.sh
  sha256LF 74453d879f983765148dfbf85728fdb775ff108924724ce4423948142fbbc250 audit_collatz/p2_runners/p2_note_s3retry.sh
  sha256LF 24bb6e83e089d5441aba5aa469d81ac67b611b334bd80f2dc039984c63618df3 audit_collatz/p2_runners/p2_open_log.sh
  sha256LF ef5d3898b430a0e51ee8ba9a6f7b2904e92754754ae3c2a06256ae89e3a92801 audit_collatz/p2_runners/p2_s4_discrepancy.sh
  sha256LF 6a7f408ef4010b1f2cbc7ebab5ca6b36f40650ec8f43b228ff2fe22c607c009c audit_collatz/p2_runners/p2_steps.sh
  sha256LF 74a6612b324bf864dbf45a7db1bc45caf55942482da52fb12b4aea7dbb0d5b52 audit_collatz/p2_runners/p2_w1_criteria.sh
  sha256LF b4ae5295bd6880acefc7d5b80cd187d7d882b12592be30b66aa89b36fac5de57 audit_collatz/p2_runners/p2_w_criteria.sh
  ```

### A-2026-0004 — Rekaman replay RR-2026-01: reproduksi pemetaan terbit (t, n) → seed kurva ECDSA (klaim halaman Anthropic 2026-10-16)

- **Jenis:** A
- **Pernyataan:** Replay terpra-registrasi (pra-reg `reports/AUDIT_ECDSA_PREREG_2026-10-19.md` + spec seri `reports/REPLAY_RECORD_SPEC.md` v0.1, dibekukan di commit `3026d12`, dipush sebelum perintah audit pertama; CI hijau `39187596038`; eksekusi 2026-10-19T02:00:15Z–02:00:23Z ≈ 8 s di commit yang sama; tanpa perubahan parameter) atas klaim pihak ketiga halaman Anthropic "Claude reveals ECDSA curve origins" (diakses 2026-10-19 01:24:11Z; capture html/txt sha256LF `266554ce…`/`35dfbdd8…`): model `srand48(t)`/`lrand48()` POSIX direkonstruksi oleh dua engine independen + weld glibc (E1w) — (I1) selftest A–D OK (D = 36 subcek, 18 kasus sintetis, target no-match brute-force); (I2) 10/10 baris prima (5 NIST + 5 v-kurva) MATCH: seed kandidat ke-n (20 byte dari `state >> 40` = `lrand48() >> 23`) == seed standar (X9.62 draft / FIPS 186-4 / Sec2 v2 / BouncyCastle / neuromancer; 2–4 sumber sepakat per baris), e1 == e2 == standar == string klaim, indeks kemunculan-pertama = n (scan, e1 = e2); (I3) 4/4 baris biner MATCH dengan argumen = epoch dibelah-dua (`floor(t/2)`): B-233 n=155 / B-283 n=32 / B-409 n=60 / B-571 n=73; (I4) statistik kata C3: count = 4 (B-233/B-283/B-409/B-571, semua kata atas nol), `1/P` = `281474976710656/48446969237` = 5809,960481401744 vs klaim 1/5.810 (toleransi ±1% → MATCH); (I5) aritmetika waktu C4: tanggal halved = Feb 1984 (4/4, 1984-02-23), doubled = 1998-04-17 (4/4), interval B-233 − P-224 = 1.218.731 s = 14 hari (floor), rentang t prima 1997-05-15..1998-04-03 → MATCH; (I6) ≥2 sumber per baris + semua sepakat + rebuild manifest dari capture byte-identik → MATCH. B-163 tetap residu (t/n tidak terbit; tidak direproduksi; hanya struktur kata 160-bit-nya dipakai I4). Gate anti-sirkularitas `TOOL NOT RUN (NO_LEAN_FILES)` exit 2 (verbatim di laporan §6; hanya bisa menurunkan klaim; tidak ada artefak Lean/SMT dalam lingkup).
- **Batas:** replay finit ≠ peer review; halaman klaim sendiri menyatakan ini bukan break/attack/weakness ECDSA; bukan bukti bahwa NSA benar-benar menjalankan lrand48 (tanpa program arsip); base point, kandidat yang dilewati (mis. P-256 kandidat 876), dan derivasi B-163 di luar lingkup; t klaim dibaca sebagai UTC (halaman mencetak tanpa zona waktu); tidak menyatakan/menyangkal RH atau P≠NP.
- **Status:** CERTIFIED
- **Domino:** tidak ada (probe eksternal; bukan domino RH)
- **Relasi:** rekaman pertama seri Replay Record (`reports/REPLAY_RECORD_SPEC.md` v0.1); audit pihak ketiga keempat (setelah `A-2026-0001`, `A-2026-0002`, `A-2026-0003`); laporan `reports/AUDIT_ECDSA_REPORT_2026-10-19.md` (§1–§11); pra-reg + spec + log + paket beku `audit_ecdsa/` (PINS berisi 29 pin, diverifikasi `sha256sum -c`) + 9 artefak eksekusi; sertifikat 41 baris (spec + pra-reg + log + laporan + 11 berkas paket beku + 17 capture + 9 artefak eksekusi).
- **Perintah verifikasi:** `sha256sum -c audit_ecdsa/PINS.sha256`; `gcc -O2 -std=gnu11 -o e1 audit_ecdsa/engine_e1.c` (+ `e1w`), lalu `python3 audit_ecdsa/selftest_v1.py --e1 <e1> --e1w <e1w> --e2 audit_ecdsa/engine_e2.py --json <f>`; item: `python3 audit_ecdsa/run_v1.py {i2|i3|i4|i5|i6} --manifest audit_ecdsa/seeds_manifest.json …`; runner eksekusi `audit_ecdsa/exec_2026-10-19/v1_exec_steps.sh`; guard `python -m pytest msaf/tests/test_fence_registry.py -q` (memverifikasi semua sha di bawah).
- **Sertifikat:**

  ```text
  sha256LF 669db7ab045c770fa2d04792da710a9a3f7ed3a9d685fefcc92e073321038805 reports/REPLAY_RECORD_SPEC.md
  sha256LF 660e3cc62a1362b8137b78c97954fe7637a5e13bd7258a7934b6692dce003d89 reports/AUDIT_ECDSA_PREREG_2026-10-19.md
  sha256LF 07e7a6dcc05a7c90a25847deea696aaf2ba1cde9ef0ad2acc24e690e0c1ff8b5 reports/AUDIT_ECDSA_LOG_2026-10-19.log
  sha256LF bd91bc83d2eef8dfe46366007db94b715126da51b6938610780fd19e732a10bd reports/AUDIT_ECDSA_REPORT_2026-10-19.md
  sha256LF b939b8fdf6482dcb07cf3f8f24197600cf63c53e3c109a440a0947b04d8a89cd audit_ecdsa/engine_e1.c
  sha256LF 3ecd223ea7d73f8ac370b08d3c2dd8f7370d0188762b4cb6b7e3825ea83f96f7 audit_ecdsa/engine_e1w.c
  sha256LF b5ae8c2b6c9e17b435ce6b17cb0425884565699bc13cd8371b867d551a4e3c98 audit_ecdsa/engine_e2.py
  sha256LF 788556901d7d3d7c2b61222c696c0b29d978d19e266fda27a275b02f215325b1 audit_ecdsa/selftest_v1.py
  sha256LF 9654766ca8d53481cd07623dae776cfbdd645d98a2063bb5ba4abda279f0b91b audit_ecdsa/run_v1.py
  sha256LF a0fcd9e1c37aa95d91809773ccf98187e000fd0af60c6d63f0258fb2a8b76fcc audit_ecdsa/build_manifest.py
  sha256LF 2ec7baec006783b1fdeb80c9f7f25cae04aefff57ad8440dada67d261049f3d7 audit_ecdsa/tool_claim_text.py
  sha256LF e27c3202aab424a68759da435d95da3bc5a70042f282c4b5f0b9ae1249f236fe audit_ecdsa/v1_rows.tsv
  sha256LF 3b39e4e5ad41ff00f8e1f5b97f7f6d1357424c5e908c85b7a7605eec259ba6d4 audit_ecdsa/seeds_manifest.json
  sha256LF 8ac938dc75c31fc498d2096cba70e7b88b5711433b3203c26604badae86335dd audit_ecdsa/SOURCES.md
  sha256LF f64d66f5b7e11aa582f7c54b60f7e853413e538c114f1b3ad163c5d53a0c56f7 audit_ecdsa/PINS.sha256
  sha256LF 486aa8e242427ea36492f4775a626fafbfe1b90071800fbef8d243707dd0fa55 audit_ecdsa/captures/bc_SECNamedCurves.java
  sha256LF 266554ce62f84b3c597193b76f7046655004601e39539e2f7619b6231898781d audit_ecdsa/captures/claim_anthropic_ecdsa_curve_origins.html
  sha256LF 35dfbdd84db918e2b678aa0371191f621c7fcac1f1ef28252cf8c43844ad77be audit_ecdsa/captures/claim_anthropic_ecdsa_curve_origins.txt
  sha256LF 0c411bcd9c806f2dccd86ea4f663e86cc864148ce5de342ed3c13a4e46bbb38b audit_ecdsa/captures/fips186-2-change1.pdf
  sha256LF e85f5165cc8381bf61963c95af4ca7cebe37789486d92c8693200284116ed798 audit_ecdsa/captures/fips186-2-change1.txt
  sha256LF 34222f3b6a9442a3491b6ace810c64da0a4e43b779737ad53a287656e7fc5f6b audit_ecdsa/captures/fips186-4.pdf
  sha256LF 5da836de5eb14ae8bb4df2fdddaa7cf25df3ba1ad404fb8cf5050a9af1898ab9 audit_ecdsa/captures/fips186-4.txt
  sha256LF ef018c91553ccde243cb6c47405c14c68cf595bf07cfe1fdbaef27beef7baa2c audit_ecdsa/captures/neuromancer_prime192v2.html
  sha256LF bfc658dc5687d3b149108f7ea708de943bd918efea4d6fc54dd53e1d52df75cb audit_ecdsa/captures/neuromancer_prime192v3.html
  sha256LF d40e415d883418b9263608bb922e6c12b9a60b4356e723499447d07b3b83300b audit_ecdsa/captures/neuromancer_prime239v1.html
  sha256LF 89848baf1e2451b523a247f77f975e345754380d8c72b6504c99bbc32ce0d3ff audit_ecdsa/captures/neuromancer_prime239v2.html
  sha256LF 8a8f2bb06df9e72e58c93c0fd8f03df0364db5ecba94d18dc6b04602e822d7a0 audit_ecdsa/captures/neuromancer_prime239v3.html
  sha256LF 8218c3c2f16435884691767b6d0259bf41e25819bca91a92d688cd41d8fb4ede audit_ecdsa/captures/saweis_nist_curve_seed_origins.html
  sha256LF b52e0a56a18bef949c4342a891b78174c0977a516e2e494247bfb9159c9ea8e2 audit_ecdsa/captures/sec2-v2.pdf
  sha256LF 93d6a91157c802de1226c08fcf36ecd78d292ac814d12bb4deb54e77362f3300 audit_ecdsa/captures/sec2-v2.txt
  sha256LF 03230cade876901515088c170048660ce1955dd090c1c7ef875f46bcbcc45852 audit_ecdsa/captures/x962-1998-draft.pdf
  sha256LF da957ea6ccd36df852f3ceb81f301cae3d57c19c25fbc014c1a6bdfa1ee7a299 audit_ecdsa/captures/x962-1998-draft.txt
  sha256LF 5188ed4eb1740400252ce1db63f1d14a64e718cbbe8910fa549ae72a437bd457 audit_ecdsa/exec_2026-10-19/e1
  sha256LF 0fcb720ed9bc67ccf8207b49981c0668f7833f63e72f2c45c28ce51ce0f3b77a audit_ecdsa/exec_2026-10-19/e1w
  sha256LF 80cc0d2c9d0c0c1ed5581563acfbc96932bb1854409d566017ebf160ea974327 audit_ecdsa/exec_2026-10-19/i1_selftest.json
  sha256LF 22ed4fa09a30ae2f787d966915766a3e8b1a21d84fbe4d933c39b7563fd67aac audit_ecdsa/exec_2026-10-19/i2_prime.json
  sha256LF 247f9e511d0efdbe7a76b8f41f9b678b54d9006e8e7cc5d7a41ddab6e7201823 audit_ecdsa/exec_2026-10-19/i3_binary.json
  sha256LF 1139975b4a0cc3f058291048ac0b8de5692af4a1ca4676167975d31a4adfef2d audit_ecdsa/exec_2026-10-19/i4_wordstats.json
  sha256LF e1756ee8b5d1d12ef8f24b040c2ff1cbb1a6883fe440f754492ce4c504da6698 audit_ecdsa/exec_2026-10-19/i5_timestamps.json
  sha256LF da0eccfd38f319d2dde559de7559e49d8578d3ca61bfe7c8a5de275b1368e9b3 audit_ecdsa/exec_2026-10-19/i6_sources.json
  sha256LF a7b20f214dec09531b0d23f6d728a6f324a0c384a212a12544c3065c9919227f audit_ecdsa/exec_2026-10-19/v1_exec_steps.sh
  ```

### A-2026-0005 — Rekaman replay RR-2026-02: kampanye kernel entropi SIMULATED (dim 201/301/401) — verdict RESOLVED

- **Jenis:** A
- **Pernyataan:** Replay terpra-registrasi (pra-reg `reports/AUDIT_QUANTUM_PREREG_2026-10-19.md` + spec `reports/REPLAY_CERT_SPEC_V0.2_QUANTUM.md` v0.2, dibekukan di commit `1febcb5`, dipush sebelum perintah kampanye pertama; CI hijau `39203227689`; eksekusi di commit `485117f`, CI hijau `39205368649`; dua-GO dipatuhi; tanpa perubahan parameter) kampanye finit kernel entropi dengan stream SIMULATED (CSPRNG OS `secrets.token_bytes`; label SIMULATED; `global_claim_supported=false`) atas model tridiagonal eksak `a_i = 2 + (i+1)^2 * h^4`, `b = -1`, `h = 1/(D+1)`, pada dim 201/301/401: (a) lapisan tersertifikasi — 12/12 koordinat {D/4, D/2, 3D/4, D}: bisection eksak 150 langkah, dua engine independen (A: ball Arb 6000 bit; B: mpmath mpf 50 dps) sepakat 150/150 keputusan, fallback eksak 0, disagreement 0, sertifikat endpoint (cnt(e_lo) ≤ k-1 dan cnt(e_hi) ≥ k) benar di kedua engine, rel_width ≤ 0.02 (terburuk 0.0139169 di dim 201 k=50), Newton bentuk pivot-product CONTRACTED di kedua engine (2 iterasi; lebar akhir ≤ 2.8e-47), Sylvester CERTIFIED_PD di kedua engine; (b) lapisan statistik float64 — 20000 sampel/dim dalam 500 batch terhadap 16 knot beku Φ⁻¹(k/16): χ² = 7.5088 / 10.3984 / 11.592, semuanya di window [0, 60], 16/16 sel dipertahankan (0 drop), exceedances z ≥ 3.5 = 2/4/3; verdict dim 201/301/401 dan kampanye semua RESOLVED (exit 0); ledger rantai-hash `ledger/quantum_evolution.jsonl` = 128 record (1 GENESIS + 120 BLOCK + 3 STATS + 4 VERDICT; tanpa REVERT), head `e7bda4e15ecad3f7abe16115436efc97c2cdc627213631e7488371076a2be910`; Codebase/Manifest Digest `f6352884d85bab5a68c01a4e1d4a73618304464fd300d56bce1f8cc2f62baa25` tidak berubah pasca-run; artefak 13:32:56–13:33:59 WITA (cap 30 mnt tidak tersentuh).
- **Batas:** kampanye finit satu-instance per dim — bukan klaim zeta/Weil, bukan RH/P≠NP; tanpa klaim entropi kuantum fisik (sumber = CSPRNG OS, label SIMULATED, D1); lapisan statistik float64 = diagnostik, tidak pernah menyentuh jalur tersertifikasi (D2); replay = replikasi protokol, bukan byte (stream non-deterministik; lapisan tersertifikasi deterministik dan reproducible eksak); ε=1/250 = envelope Weyl ‖E‖₂ ≤ ε untuk perturbasi diagonal per-channel (K-Q2: PD disertifikasi pada blok model itu sendiri, bukan untuk setiap anggota ε-box); replay finit ≠ peer review; tidak menyatakan/menyangkal RH atau P≠NP.
- **Status:** CERTIFIED
- **Domino:** tidak ada (kampanye internal V2; bukan domino RH)
- **Relasi:** rekaman kedua seri Replay Record (spec v0.2 = perluasan seri `reports/REPLAY_RECORD_SPEC.md` v0.1); audit kelima registry (setelah `A-2026-0001`..`A-2026-0004`); paket beku `audit_quantum/` (14 pin; `PINS.sha256` + `FREEZE_MANIFEST_V2.json` + `freeze.py`; `--verify` OK) + selftest 14/14 + guard CI `msaf/tests/test_quantum_entropy.py`; dashboard `reports/gw_quantum_diagnostic_v1.html` (standalone, self-contained); sertifikat 21 baris (spec + pra-reg + freeze.py + PINS + manifest + 10 berkas paket + guard + ledger + 3 stats + dashboard).
- **Perintah verifikasi:** `python -m msaf.quantum_entropy.selftest` (14/14 ZERO FAILURE); `python audit_quantum/freeze.py --verify`; `python -m msaf.quantum_entropy.ledger --verify ledger/quantum_evolution.jsonl` (128 record; head `e7bda4e1…`); `python -m pytest msaf/tests/test_quantum_entropy.py -q`; guard `python -m pytest msaf/tests/test_fence_registry.py -q` (memverifikasi semua sha di bawah).
- **Sertifikat:**

  ```text
  sha256LF dea0a8dd8132d95937034150553ca1fd490c225627d7ef08e5b2de8c6847d26b reports/REPLAY_CERT_SPEC_V0.2_QUANTUM.md
  sha256LF 1179368367c3fd16f6dd1c15848773d52813231668d6170692c5acbbce427142 reports/AUDIT_QUANTUM_PREREG_2026-10-19.md
  sha256LF a831441bb600bf05aa8eeb40e76fbea8ef73fee98f249abf9eb7657064270369 audit_quantum/freeze.py
  sha256LF f6352884d85bab5a68c01a4e1d4a73618304464fd300d56bce1f8cc2f62baa25 audit_quantum/PINS.sha256
  sha256LF 17d61997be02fcc294c8a76f7950437088de6f8ae4a38a341540748561736d88 audit_quantum/FREEZE_MANIFEST_V2.json
  sha256LF 5114f811056f14ed484d8f76cdb2ed4439091424b360ca539428de0ba2936ab3 msaf/quantum_entropy/__init__.py
  sha256LF 75307da705b42151ce153cb2ba1bed55f5afad61da3068638c3dfc75a2c3e11a msaf/quantum_entropy/chispec.py
  sha256LF a4d093b762492e2b20d8792b734e57d85759b43333ad0a299657728a02a8f9d4 msaf/quantum_entropy/dashboard.py
  sha256LF cb8dc9c120085b96e7ed228f883274023571ac1abb7d61d5f0a279f0c56d6c24 msaf/quantum_entropy/engines.py
  sha256LF edb97df52a2bea0d40ad1ef62f03a63b6aad35642d0d3b34d637e04255a6da0a msaf/quantum_entropy/entropy_source.py
  sha256LF cb194a64754e4a2f4b2445722b6dffd2c46a9576870464c565098b6f08a1c28f msaf/quantum_entropy/intervals.py
  sha256LF 0dd577ad77c88a7d86bf49c3fbebac7db1c911f368e05537c8a958705f981f72 msaf/quantum_entropy/ledger.py
  sha256LF 88532270d3de50100509296decdff57039c2914079018a6a52638b7f27a10795 msaf/quantum_entropy/runner.py
  sha256LF e823b492137836c0d8c163a0eee7a3a6aa38883356d786d174dcbaba4fccc92c msaf/quantum_entropy/selftest.py
  sha256LF 1ca1e5ff9fc92f5544d3f654b11ef68bcad01d44a055dce5a81e14d47c571bc6 msaf/quantum_entropy/sylvester.py
  sha256LF bf4a75c98179a19b233879666280650e213b9a1aefcbea63186fca0bd8feec46 msaf/tests/test_quantum_entropy.py
  sha256LF 6dcb3855cfca71dbcbbbe0ce1bd38cff2a1fcf24528f9c8d3db86b9acb204640 ledger/quantum_evolution.jsonl
  sha256LF 31e9cb539bd10e527d337d0c3771d73a6a1b3177f1b31dd47b0469c30619d645 audit_quantum/exec_2026-10-19/stats_d201.bin
  sha256LF 54b204d7e09f8fbd03bf1f884442196c7a7a7771b136fda23806d39738b19054 audit_quantum/exec_2026-10-19/stats_d301.bin
  sha256LF b68cdd0926256d7d50fbce0ed637768a6d9f1c3f54e83fd52c4bc678b0cc22c6 audit_quantum/exec_2026-10-19/stats_d401.bin
  sha256LF 9747b13515ed4f1670bc690e3c4917d44c1d1e22fb99c625052c42cab33357cf reports/gw_quantum_diagnostic_v1.html
  ```

### A-2026-0006 — Kit jembatan dua-ruang: `msaf/bridge.py` + protokol [B]/[J]/[U] + demo tersertifikasi (ζ(2), dua ekor integral)

- **Jenis:** A
- **Pernyataan:** Artefak perangkat internal (bukan audit pihak ketiga):
  kit dua-ruang yang mengubah klaim di ruang tak hingga menjadi tiga blok
  yang dapat diperiksa — [B] enclosure rigor bagian terbatas, [J] lemma
  ekor bernama (L1 geometrik eksak; L2 deret-p dua-sisi; L3 envelope
  eksponensial; L4 ekor Gaussian; L5 perbandingan integral), [U] pernyataan
  final = [B]+[J] dengan verdict; keputusan `tail <= eps` hanya lewat
  perbandingan Arb rigor (semua-anggota), pencarian cutoff heuristik tidak
  pernah menggantikan sertifikat final (fail-closed: `RuntimeError` bila
  anggaran tak tercapai; `certified=False` bila tak terbukti); non-finit
  ditolak di setiap pintu masuk (aturan `certify.py`); protokol + checklist
  di `reports/BRIDGE_PROTOCOL_2026-10-19.md`; demo tersertifikasi (output
  verbatim `reports/BRIDGE_DEMO_OUTPUT_2026-10-19.txt`; capture ganda
  deterministik): ζ(2) dua-sisi lebar ≈ 5.0e-9 <= 1e-8 memuat pi^2/6;
  integral e^(-x) pada [1, inf) lebar <= 1e-18 dengan bracket [0.36, 0.38];
  ekor Gaussian M=2 <= 5e-3 (L4); guard CI `msaf/tests/test_bridge.py`
  (19 uji).
- **Batas:** alat metodologi/estimasi — bukan klaim matematis baru; L1–L5
  klasik (bukti kalkulus elementer, dirujuk bukan diformalkan ulang); demo =
  demonstrasi mekanika [B]+[J]->[U] pada objek klasik; tidak menyentuh
  zeta/Weil/RH/P≠NP; tidak ada klaim fisik; bukan peer review.
- **Status:** CERTIFIED
- **Domino:** tidak ada (artefak internal; bukan domino)
- **Relasi:** melengkapi `msaf/certify.py` (mandat containment),
  `msaf/budget.py` (anggaran presisi), `msaf/tests/test_tail_decay.py`
  (contoh jembatan kotak-periodik); entri registry ke-11; memori kerja §2.0x
  `reports/HANDOFF.md`.
- **Perintah verifikasi:** `python -m msaf.bridge_demo` (3 demo,
  `ALL DEMOS CERTIFIED: True`, exit 0); `python -m pytest
  msaf/tests/test_bridge.py -q` (19 uji); guard `python -m pytest
  msaf/tests/test_fence_registry.py -q` (memverifikasi semua sha di bawah).
- **Sertifikat:**

  ```text
  sha256LF 6f3865d7c327ff802fa518d48530ea4d3fb4d3f6983a491bcdc468d752a31a1e msaf/bridge.py
  sha256LF 677b8e34e6bd7aa7da06e6f719723c1c9c0d0299fcecd060b4c33f36c1aeb2c0 msaf/tests/test_bridge.py
  sha256LF ec25c049582ddb5b3fe6bfe5cc7e59484838406a719245292a4ba1c60e20a335 msaf/bridge_demo.py
  sha256LF 94ec7a591e301e624e78a924ce974846cdfc08d341ea4570ef47c7b8187a6b8b reports/BRIDGE_PROTOCOL_2026-10-19.md
  sha256LF 16bc62d625f78ff8d468c5044557e7769a5b1fe3f7eeee70d055bd76df0f3cce reports/BRIDGE_DEMO_OUTPUT_2026-10-19.txt
  ```

### A-2026-0007 — Studi jembatan kotak periodik ↔ ruang bebas: sisi terbatas tersertifikasi, jembatan [J] tetap OPEN (statistik q bukan bukti konvergensi)

- **Jenis:** A
- **Pernyataan:** Studi kuantitatif internal (bukan audit pihak ketiga) atas
  model tersegel `msaf/navier_stokes/fluid_lattice.py`: solusi eksak
  Laplacian periodik 7-titik pada T^3_N (`dx = 1/N`, sumber titik zero-mean)
  dihitung pada sumbu dengan **mode sum langsung** O(N^3)
  (`msaf/periodic_bridge.py`; setiap suku bola Arb dari `cos_pi` rasional
  eksak) untuk N = 16, 20, 24, 32, 40, 48, 64; kesesuaian dengan solver DFT
  tersegel (O(N^4)) diuji lewat aturan containment: selisih kedua enclosure
  memuat nol eksak (N=8, r=0..4, radius < 1e-60); statistik
  q(N) = (v1-v2)/(v2-v4) rigor menurun tegas pada band (1.95190443 →
  1.91092671), increment mengecil tegas, dan gap 2 - q(64) =
  0.0890732860327 ± 3.89e-14 **tidak menuju nol**: pada N ≤ 64 q bergerak
  menjauh dari nilai kontinuum 2 → q **bukan** statistik jembatan; record
  tersegel direproduksi independen (q(16)=1.9519; rasio mentah
  2.48682 / 4.19692 vs catatan 2.49 / 4.20); **blok [B] CERTIFIED, blok
  [J] OPEN** (identitas citra periodik dicatat; bound ekor citra tidak
  dibuktikan); tidak ada nilai limit, tidak ada laju konvergensi, tidak ada
  klaim kontinuum.
- **Batas:** hanya sisi terbatas yang disertifikasi; [J] OPEN sehingga
  pernyataan ruang-bebas [U] tidak diklaim; F4 adalah temuan negatif tentang
  statistik q, bukan tentang model tersegel (guard lama tetap benar);
  tidak menyentuh zeta/Weil/RH/P≠NP; tidak ada klaim fisik; bukan peer
  review.
- **Status:** CERTIFIED
- **Domino:** tidak ada (studi internal; bukan domino)
- **Relasi:** menerapkan protokol `[B]/[J]/[U]` dari `A-2026-0006`
  (`reports/BRIDGE_PROTOCOL_2026-10-19.md`); memperluas bukti
  `msaf/tests/test_tail_decay.py` (satu titik N=16 → kurva N=16..64);
  entri registry ke-12; memori kerja §2.0y `reports/HANDOFF.md`.
- **Perintah verifikasi:** `python -m pytest msaf/tests/test_periodic_bridge.py -q`
  (6 uji; termasuk kesesuaian dua engine); guard
  `python -m pytest msaf/tests/test_fence_registry.py -q` (memverifikasi
  semua sha di bawah).
- **Sertifikat:**

  ```text
  sha256LF 3ae260f319f3041f91edcb8fc6e873ed9538e6929ecb21f96dc860ab9632888d msaf/periodic_bridge.py
  sha256LF 4f1d540a702412f1c06997ebdca4ac16b64cc5c26267ec2724ae7f03e96e4f70 msaf/tests/test_periodic_bridge.py
  sha256LF 19fcd548e0af8e8ebec97079db2d1e2f4253b3d47c3fae1a9ae72898539e9720 reports/PERIODIC_BRIDGE_STUDY_2026-10-19.md
  sha256LF 0e0c4d873c071bc7278ed0fe3355a235551e113061f32ad21f672c30ae0de026 reports/PERIODIC_BRIDGE_STUDY_OUTPUT_2026-10-19.txt
  ```

### A-2026-0008 — Pilot Coq: satu lemma jembatan geometrik (inti L1) terbukti tanpa aksioma proyek; langkah limit [J] tetap OPEN

- **Jenis:** A
- **Pernyataan:** Pilot formal pertama repo (tidak ada berkas `.v`
  sebelumnya). `formal_bridge/GeometricBridge.v` (Coq 8.20.1, OCaml
  4.14.2, switch opam yang di-KEEP) membuktikan **delapan** lemma tentang
  jumlah parsial geometrik berhingga: `geom_sum r n = Σ_{k<n} r^k`;
  bentuk tertutup `geom_sum r n = (1−r^n)/(1−r)` (`r ≠ 1`); identitas
  jembatan `1/(1−r) − geom_sum r n = r^n/(1−r)`; ketaknegatifan suku ekor
  untuk `0 ≤ r < 1`; batas `geom_sum r n ≤ 1/(1−r)`; dan satu aplikasi
  konkret `r = 1/2, n = 11` (`geom_sum = 2047/1024`, ekor `= 1/1024`).
  Berkas diterima `coqc` **exit 0** dan diperiksa ulang pemeriksa kernel
  independen `coqchk` **exit 0** ("Modules were successfully checked";
  48 ribu baris log, 10 konstanta). `Print Assumptions` untuk **8/8** lemma
  mencetak tepat dua aksioma stdlib `Coq.Reals`
  (`ClassicalDedekindReals.sig_forall_dec`,
  `FunctionalExtensionality.functional_extensionality_dep`); **tidak ada**
  `Axiom`/`Parameter`/`Admitted`/`admit` di sumber (scan dengan komentar
  bersarang distrip). Receipt beku deterministik (dua capture byte-identik).
  **Blok [B] CERTIFIED** (rumus eksak berhingga); **blok [J] hanya sisi
  aljabar** — identitas gap tertutup, sedangkan langkah limit/deret tak
  hingga **OPEN**; **[U] tidak diklaim**.
- **Batas:** bukan formalisasi analisis (tanpa limit, tanpa deret tak
  hingga, tanpa laju konvergensi); teorema bersandar pada aksioma stdlib
  `Coq.Reals`, jadi yang disertifikasi adalah "tidak ada aksioma proyek
  tambahan", bukan konsistensi; satu lemma + satu aplikasi, bukan port
  L2–L5; **anti-circularity gate skill = `TOOL NOT RUN` (NO_LEAN_FILES,
  exit 2)** dan tidak dihitung sebagai sukses — gate itu hanya memindai
  `.lean`/`.smt2`; CI tidak punya toolchain Coq sehingga hanya menjalankan
  guard statis; tidak menyentuh zeta/Weil/RH/P≠NP; tidak ada klaim fisik;
  bukan peer review.
- **Status:** CERTIFIED
- **Domino:** tidak ada (pilot toolchain; bukan domino)
- **Relasi:** memformalkan inti aljabar lemma L1 dari `A-2026-0006`
  (`msaf/bridge.py`, `reports/BRIDGE_PROTOCOL_2026-10-19.md`); melengkapi
  studi `A-2026-0007` yang meninggalkan `[J] OPEN` — di sini `[J]` juga
  tetap OPEN pada sisi analitiknya; entri registry ke-13; memori kerja
  §2.0z `reports/HANDOFF.md`.
- **Perintah verifikasi:** `python -m pytest msaf/tests/test_coq_bridge_pilot.py -q`
  (4 uji statis: placeholder, kelengkapan audit, blok asumsi, receipt
  kernel); `python -m pytest msaf/tests/test_fence_registry.py -q` (semua
  sha di bawah); reproduksi kernel lokal `formal_bridge/check.sh`.
- **Sertifikat:**

  ```text
  sha256LF a382a4ce0514fd1aec459fa83c1edfd83058567cbc50eeb8fd2ca55d7584cd00 formal_bridge/GeometricBridge.v
  sha256LF 0989028e1e1f23f2b7b6960477a9667e1f90e881b09554f0411dbac9eac4d4ef formal_bridge/check.sh
  sha256LF 1187954cbe82bd562514385adb19b5c810f11698f3a26ad01225ec79061f74ee formal_bridge/GeometricBridge.compile.log
  sha256LF 98b265edf282e89b6d83fe410ec34b33ad294ec63d7a5fc892a215026b397b3f formal_bridge/GeometricBridge.receipt.txt
  sha256LF 9d87f44e16224d94f26e2c64382d47e3c3e49e335a7be13f9070ca6ed8b12d41 msaf/tests/test_coq_bridge_pilot.py
  sha256LF 63ba4fd0873ddad6ccea989e9fb02d96d3f74f51636e1bd13871647c4b278812 reports/COQ_BRIDGE_PILOT_2026-10-19.md
  ```

### A-2026-0009 — Penutupan [J] analitik jembatan geometrik di Coq: konvergensi ε-N terbukti untuk L1; [J] periodic-box tetap OPEN

- **Jenis:** A
- **Pernyataan:** Lanjutan `A-2026-0008` (scope diperluas lewat
  pra-registrasi baru; berkas lama **tidak diubah**).
  `formal_bridge/GeometricLimit.v` mengimpor `GeometricBridge.v` dan
  membuktikan **enam** hasil: (1) `geom_dist_eq_tail` — jarak ke bentuk
  tertutup sama dengan suku ekor `geom_tail r n`; (2) **`geom_sum_cv`** —
  untuk `0 ≤ r < 1`, `Un_cv (fun n => geom_sum r n) (1/(1−r))` dalam
  definisi ε-N standar `Coq.Reals.Rseries` (dengan `Rdist`); (3)
  `geom_sum_cv_half` — instance `r = 1/2`; (4) `geom_half_limit_value` —
  `1/(1−1/2) = 2`; (5) `geom_half_dist_11` — jarak pada `n = 11` tepat
  `1/1024`; (6) `geom_half_dist_11_lt` — jarak itu `< 1/100`. Saksi ε-N
  berasal dari lemma stdlib `pow_lt_1_zero`; tidak ada aksioma proyek.
  `coqc` exit 0 untuk kedua berkas; `coqchk` exit 0 "Modules were
  successfully checked"; `Print Assumptions` **6/6** hasil hanya memuat
  dua aksioma stdlib `Coq.Reals`
  (`ClassicalDedekindReals.sig_forall_dec`,
  `FunctionalExtensionality.functional_extensionality_dep`); tanpa
  `Axiom`/`Parameter`/`Admitted`/`admit`; receipt deterministik (dua
  capture byte-identik). Untuk **kasus geometrik L1** blok `[B]/[J]/[U]`
  kini tertutup: aljabar berhingga (warisan `A-2026-0008`), langkah limit,
  dan nilai limit.
- **Batas:** **hanya lemma geometrik L1** — L2 (p-series), L3 (amplop
  eksponensial), L4 (ekor Gaussian), dan L5 (perbandingan integral) tidak
  diformalkan; **bukan** penutupan `[J]` studi periodic-box `A-2026-0007`
  (objek berbeda; `[J]` di sana tetap OPEN); teorema bersandar pada
  aksioma stdlib `Coq.Reals`, jadi yang disertifikasi adalah tidak ada
  aksioma proyek tambahan, bukan konsistensi; **anti-circularity gate
  skill = `TOOL NOT RUN` (NO_LEAN_FILES, exit 2)** dan tidak dihitung
  sebagai sukses — gate hanya memindai `.lean`/`.smt2`; CI tidak punya
  toolchain Coq sehingga hanya menjalankan guard statis; tidak menyentuh
  zeta/Weil/RH/P≠NP; tidak ada klaim fisik; bukan peer review.
- **Status:** CERTIFIED
- **Domino:** tidak ada (pilot formal; bukan domino)
- **Relasi:** memperluas `A-2026-0008` (berkas dan sertifikatnya tidak
  berubah); memakai lemma L1 `A-2026-0006`; **tidak** menutup `[J]`
  `A-2026-0007`; entri registry ke-14; memori kerja §2.0aa
  `reports/HANDOFF.md`.
- **Perintah verifikasi:** `python -m pytest msaf/tests/test_coq_bridge_limit.py -q`
  (4 uji statis: placeholder, kelengkapan audit, impor tanpa redefinisi,
  receipt kernel); `python -m pytest msaf/tests/test_fence_registry.py -q`;
  reproduksi kernel lokal `formal_bridge/check_limit.sh`.
- **Sertifikat:**

  ```text
  sha256LF 1f10ea5d15320c226b95f15535ea4715397281ffbe51c54fe9c0e593c3340620 formal_bridge/GeometricLimit.v
  sha256LF ff490edb7b302d86df8f89592a155e6535338d414d060b5df2b01e17533175ae formal_bridge/check_limit.sh
  sha256LF b10f67e105dc57d418d2a66b96ccb0f26aead255c7fa324b197e0e640ac3b194 formal_bridge/GeometricLimit.receipt.txt
  sha256LF 1dc231f0dfa783104d93af71207581ca528c671737b80024ba0d7d5beb35e5d4 msaf/tests/test_coq_bridge_limit.py
  sha256LF f809e95b92811f1aa2557d4932aaef5f7dd4cb76bdb2cec659af8f427130aaf7 reports/COQ_BRIDGE_LIMIT_2026-10-19.md
  ```

### A-2026-0010 — L2 deret-p eksponen bulat di Coq: batas dua sisi + eksistensi limit terbukti; deviasi audit tiga aksioma stdlib tercatat

- **Jenis:** A
- **Pernyataan:** Lanjutan Paket 6 (pra-registrasi baru
  `reports/PREREG_PAKET6_2026-10-19.md`; berkas Paket 1–5 **tidak
  diubah**). `formal_bridge/PseriesL2.v` membuktikan **20** hasil, dengan
  teorema utama **`pseries_L2_integer`**: untuk setiap `k ≥ 1` (jadi
  `p = k+1 ≥ 2`) dan `N ≥ 1`, terdapat `L` dengan
  `Un_cv (fun M => psum k N M) L` dan
  `1/(k(N+1)^k) ≤ L ≤ 1/(k N^k)`, di mana
  `psum k N M = Σ_{i=0}^{M} 1/(INR(N+1+i))^(k+1)`. Ini adalah L2 kit
  `pseries_tail_bounds` **hanya untuk eksponen bulat**. Bukti memakai
  Bernoulli integer, ketaksamaan langkah atas/bawah, teleskopik finite,
  `Un_cv_crit`, `Un_cv_le_const`, dan `sum_incr` + `INR_unbounded`.
  `coqc` exit 0; `coqchk` exit 0 "Modules were successfully checked";
  20/20 hasil muncul di keluaran kernel; receipt deterministik (dua
  capture byte-identik, 193 baris). `Print Assumptions`: **19/20** hasil
  hanya dua aksioma stdlib (`sig_forall_dec`,
  `functional_extensionality_dep`); teorema utama memakai **tiga** —
  ditambah `ClassicalDedekindReals.sig_not_dec` — karena `Un_cv_crit`
  (kelengkapan R). Tidak ada aksioma proyek, `Axiom`, `Parameter`,
  `Admitted`, atau `admit`.
- **Batas:** **hanya eksponen bulat** `p = k+1 ≥ 2`; eksponen real
  `p > 1` (`Rpower`), L3 (amplop eksponensial), L4 (ekor Gaussian), dan
  L5 (perbandingan integral) tidak diformalkan; **bukan** penutupan `[J]`
  studi periodic-box `A-2026-0007` (objek berbeda; `[J]` di sana tetap
  OPEN); kriteria pra-registrasi §4 “hanya dua aksioma stdlib” **tidak
  terpenuhi literal** — deviasi satu aksioma stdlib dicatat di addendum
  §6 pra-registrasi, laporan, dan entri ini; yang disertifikasi adalah
  tidak ada aksioma proyek tambahan, bukan konsistensi; anti-circularity
  gate = `TOOL NOT RUN` (NO_LEAN_FILES/NO_CLAIM_FILES, exit 2) dan tidak
  dihitung sebagai sukses; CI tidak punya toolchain Coq sehingga hanya
  menjalankan guard statis; tidak menyentuh zeta/Weil/RH/P≠NP; tidak ada
  klaim fisik; bukan peer review.
- **Status:** CERTIFIED
- **Domino:** tidak ada (formal L2; bukan domino)
- **Relasi:** melanjutkan `A-2026-0006` (kit) dan `A-2026-0008`/
  `A-2026-0009` (pilot Coq; berkas dan sertifikatnya tidak berubah);
  **tidak** menutup `[J]` `A-2026-0007`; entri registry ke-15; memori
  kerja §2.0ab `reports/HANDOFF.md`.
- **Perintah verifikasi:** `python -m pytest msaf/tests/test_coq_bridge_l2.py -q`
  (5 uji statis: placeholder, kelengkapan audit, standalone + statement
  lock, receipt/trusted base, 8 mutasi negatif);
  `python -m pytest msaf/tests/test_fence_registry.py -q`; reproduksi
  kernel lokal `formal_bridge/check_pseries.sh`.
- **Sertifikat:**

  ```text
  sha256LF f3b917c801c1f963eab11a2b92214e62e6e5f956b1ff68e76f1875321f07537e formal_bridge/PseriesL2.v
  sha256LF 344f2fbdb3e73a70d199df85a0f8ce112bd2cf1a842f07f2c07cf31f16260813 formal_bridge/check_pseries.sh
  sha256LF 7ee0371190c4f1220abd800a191a13116856d052b626375e32324646783669ec formal_bridge/PseriesL2.receipt.txt
  sha256LF f3d71e9b7ae775c0f5dee1f19882ff4dd11ead4db8b5a324406e225ed60a0d52 msaf/tests/test_coq_bridge_l2.py
  sha256LF 68c3a26168226e1ad14c440d23a9f472334b0c8700298133f5eb234dfa05609a reports/COQ_BRIDGE_L2_2026-10-19.md
  sha256LF e0661f2d3e2c33996839849145a5c918d6f6f68b26c4493f0adade40fbc38f75 reports/PREREG_PAKET6_2026-10-19.md
  ```

### A-2026-0011 — L2 bersyarat dua aksioma di Coq: batas deret-p dengan `Un_cv` sebagai hipotesis; `sig_not_dec` terisolasi ke langkah eksistensi

- **Jenis:** A
- **Pernyataan:** Lanjutan Paket 6b (pra-registrasi baru
  `reports/PREREG_PAKET6B_2026-10-20.md`; berkas Paket 1–6 **tidak
  diubah**). `formal_bridge/PseriesL2Bounds.v` mengimpor modul beku
  `PseriesL2.v` (`A-2026-0010`) dan membuktikan **satu** teorema
  **`pseries_L2_integer_bounds`**: untuk setiap `k ≥ 1`, `N ≥ 1`, dan `L`
  dengan `Un_cv (fun M => psum k N M) L` (limit ekor deret-p sudah ada),
  berlaku `1/(k(N+1)^k) ≤ L ≤ 1/(k N^k)`. Ini bagian "batas" L2 kit
  untuk eksponen bulat **secara kondisional**; bagian "eksistensi" tetap
  milik `A-2026-0010`. Bukti memakai ulang lemma modul beku
  (`psum_lower_sharp`, `psum_upper`, `Un_cv_le_const`, `tail_term_small`,
  `lt_sub_pos`, `sub_le_swap`) + `sum_incr` stdlib; **tanpa**
  `Un_cv_crit` dan **tanpa** `pseries_L2_integer` (dijaga statis oleh
  guard). `coqc` exit 0 (kedua berkas); `coqchk` exit 0 "Modules were
  successfully checked"; 1/1 hasil di keluaran kernel; receipt
  deterministik (dua capture byte-identik, 23 baris). `Print Assumptions`:
  **tepat dua** aksioma stdlib (`sig_forall_dec`,
  `functional_extensionality_dep`), **tanpa** `sig_not_dec` — aksioma
  ketiga `A-2026-0010` terisolasi ke langkah eksistensi. Tidak ada
  aksioma proyek, `Axiom`, `Parameter`, `Admitted`, atau `admit`.
- **Batas:** **hanya kondisional** (`Un_cv` hipotesis; eksistensi tidak
  dibuktikan di sini — itu `A-2026-0010`, tiga aksioma); hanya eksponen
  bulat `p = k+1 ≥ 2`; eksponen real `p > 1` (`Rpower`), L3, L4, L5
  tidak diformalkan; **bukan** penutupan `[J]` periodic-box `A-2026-0007`
  (tetap OPEN); `Coq.Reals` aksiomatik, bukan konsistensi;
  anti-circularity gate = `TOOL NOT RUN` (NO_LEAN_FILES, exit 2 menurut
  kontrak gate) dan **tidak dihitung sebagai sukses**; CI tidak punya
  toolchain Coq sehingga hanya menjalankan guard statis; tidak menyentuh
  zeta/Weil/RH/P≠NP; tidak ada klaim fisik; bukan peer review.
- **Status:** CERTIFIED
- **Domino:** tidak ada (formal; bukan domino)
- **Relasi:** melanjutkan `A-2026-0010` (berkas dan sertifikatnya tidak
  berubah; modul beku diimpor apa adanya); melengkapi peta trusted base —
  eksistensi = 3 aksioma, batas bersyarat = 2 aksioma; entri registry
  ke-16; memori kerja §2.0ac `reports/HANDOFF.md`.
- **Perintah verifikasi:** `python -m pytest msaf/tests/test_coq_bridge_bounds.py -q`
  (6 uji statis: placeholder, kelengkapan audit, impor + isolasi,
  statement lock, receipt/trusted base, 11 mutasi negatif);
  `python -m pytest msaf/tests/test_fence_registry.py -q`; reproduksi
  kernel lokal `formal_bridge/check_bounds.sh`.
- **Sertifikat:**

  ```text
  sha256LF 363bdd64fa0eb66128676bf238e2a7e340b177bef2111746c26c8e3ac9d9d5f5 formal_bridge/PseriesL2Bounds.v
  sha256LF 33f66c7339a53d22f29193e8fe2be5b8de3dd39d9b6eeb881e5b8f234075331e formal_bridge/check_bounds.sh
  sha256LF 9113a745793e8b77a98cac68eec88712d927d7a4a5c27b969a4206b9865c39cd formal_bridge/PseriesL2Bounds.receipt.txt
  sha256LF 6989b3b4dc04fdea51c8b2685d7468341ed9b4f809e2c75a70729a66d87027ec msaf/tests/test_coq_bridge_bounds.py
  sha256LF b01ef855f902effe68e01b6defc10a6bea2f1ae02379a1ca08c946291257f5ea reports/COQ_BRIDGE_L2_BOUNDS_2026-10-20.md
  sha256LF 1b547049d9e9d9a4a52377f4d7e09248f6c0c55d92fb872e925f96912da06232 reports/PREREG_PAKET6B_2026-10-20.md
  ```

### A-2026-0012 — L5 finite core di Coq: perbandingan integral–deret untuk `f_k(x)=x^{-(k+1)}`; trusted base 4 aksioma stdlib tercatat

- **Jenis:** A
- **Pernyataan:** Lanjutan Paket 7 (pra-registrasi baru
  `reports/PREREG_PAKET7_2026-10-20.md` + addendum trusted base
  `reports/PREREG_PAKET7_ADDENDUM_2026-10-20.md`; berkas Paket 1–6b
  **tidak diubah**). Untuk setiap `k`, `N`, `M` dengan `k ≥ 1` dan
  `N ≥ 1`, integral Riemann finite
  `∫_N^{N+M} x^{-(k+1)} dx` berada di antara jumlah bawah
  `Σ_{i=0}^{M-1} (N+i)^{-(k+1)}` dan jumlah atas
  `Σ_{i=0}^{M-1} (N+i+1)^{-(k+1)}`. `formal_bridge/IntegralComparison.v`
  membuktikan **14** hasil, dengan teorema utama
  **`integral_comparison_power_finite`**; bukti memakai
  `RiemannInt_P19`/`P15` per unit, `RiemannInt_P25` untuk aditivitas,
  `continuity_implies_RiemannInt` + `derivable_pt_pow`/
  `continuity_pt_inv` untuk integrabilitas, dan
  `pow_incr`/`Rinv_le_contravar` untuk ketaksamaan; **tanpa**
  `FTC_Riemann`, `C1_fun`, `Rpower`, integral tak-hingga, atau impor
  modul proyek. `coqc` exit 0; `coqchk` exit 0 "Modules were
  successfully checked"; 14/14 hasil di keluaran kernel; receipt
  deterministik (dua capture byte-identik, 128 baris).
  `Print Assumptions` teorema utama: **tepat empat** aksioma stdlib
  (`sig_forall_dec`, `sig_not_dec`, `functional_extensionality_dep`,
  `Classical_Prop.classic`); aksioma keempat masuk melalui mesin
  integral Riemann stdlib. Tidak ada aksioma proyek, `Axiom`,
  `Parameter`, `Admitted`, atau `admit`.
- **Batas:** **hanya finite core** (interval `[N, N+M]`; bukan
  `∫_N^∞`, tanpa langkah limit/`Un_cv` integral); hanya
  `f_k(x)=x^{-(k+1)}` dengan `k ≥ 1` (bukan `f` umum, bukan eksponen
  real `p > 1`/`Rpower`, bukan L3/L4); **bukan** penutupan `[J]`
  periodic-box `A-2026-0007` (tetap OPEN); `Coq.Reals` aksiomatik,
  bukan konsistensi; deviasi trusted base tercatat — empat aksioma
  stdlib, bukan tiga yang diperkirakan pra-registrasi §4; jika owner
  mensyaratkan literal tiga aksioma, paket ini **tidak** memenuhi
  syarat itu; anti-circularity gate = `TOOL NOT RUN` (NO_LEAN_FILES,
  exit 2 menurut kontrak gate) dan **tidak dihitung sebagai sukses**;
  CI tidak punya toolchain Coq sehingga hanya menjalankan guard
  statis; tidak menyentuh zeta/Weil/RH/P≠NP; tidak ada klaim fisik;
  bukan peer review.
- **Status:** CERTIFIED dengan deviasi trusted base tercatat
- **Domino:** tidak ada (formal; bukan domino)
- **Relasi:** melanjutkan `A-2026-0011` (berkas dan sertifikatnya tidak
  berubah) dan kit `A-2026-0006`; `A-2026-0007` `[J]` tetap OPEN;
  `PseriesL2.v`/`PseriesL2Bounds.v` tidak diimpor (paket standalone);
  entri registry ke-17; memori kerja §2.0ad `reports/HANDOFF.md`.
- **Perintah verifikasi:** `python -m pytest msaf/tests/test_coq_bridge_integral.py -q`
  (5 uji statis: placeholder, kelengkapan audit, standalone + statement
  lock, receipt/trusted base, 16 mutasi negatif);
  `python -m pytest msaf/tests/test_fence_registry.py -q`; reproduksi
  kernel lokal `formal_bridge/check_integral.sh`.
- **Sertifikat:**

  ```text
  sha256LF fc519fd80c22c8b0a3753d35cc3d0ed9842253117b0f544503adef06e493b80c formal_bridge/IntegralComparison.v
  sha256LF bd61cb42a997cc2b1a50ea7336ccbe2df957df8c211ff8cd80375e459caf94b7 formal_bridge/check_integral.sh
  sha256LF e11d07f5dcb5b835da1af418ddf45b9a0fa5d6845869420e90a940805931d2e2 formal_bridge/IntegralComparison.receipt.txt
  sha256LF 8e558deaaa045080cc67f91b56dbc560df3b6bd127b6203464575af506991519 msaf/tests/test_coq_bridge_integral.py
  sha256LF 96fa060e691fbd79034a89448333b59ef52cc7db2458d74fee8219e8d7d83303 reports/COQ_BRIDGE_L5_FINITE_2026-10-20.md
  sha256LF 0c655f7af58422e8526e764bbd90ab09b2643eee10942193a02add16b138e917 reports/PREREG_PAKET7_2026-10-20.md
  sha256LF 1fb0251d2457dbc2265067beedd1249d5d8fd276a7359da4603192ae845a9c19 reports/PREREG_PAKET7_ADDENDUM_2026-10-20.md
  ```

### A-2026-0013 — L5 limit step di Coq: perbandingan limit integral–deret untuk `f_k(x)=x^{-(k+1)}` dengan `Un_cv` sebagai hipotesis; trusted base 4 aksioma stdlib diwarisi

- **Jenis:** A
- **Pernyataan:** Lanjutan Paket 8 (pra-registrasi baru
  `reports/PREREG_PAKET8_2026-10-20.md`; berkas Paket 1–7 **tidak
  diubah**). Untuk `k ≥ 1`, `N ≥ 1`, dan limit `L_N`, `L_{N+1}`, `L_S`
  dengan hipotesis `Un_cv` untuk integral dari `N`, integral dari `N+1`,
  dan tail sum dari `N+1`, berlaku `L_{N+1} <= L_S <= L_N`, yaitu L5
  `∫_{N+1}^∞ f_k ≤ Σ_{n>N} f_k(n) ≤ ∫_N^∞ f_k` dalam bentuk limit
  bersyarat. `formal_bridge/IntegralComparisonLimit.v` mengimpor modul
  beku `formal_bridge/IntegralComparison.v` (`A-2026-0012`) apa adanya
  dan membuktikan **4** hasil: `Un_cv_le` (order limit),
  `tail_sum_le_whole`, `whole_succ_le_tail_sum`, dan teorema utama
  **`integral_comparison_power_limit`**. `coqc` exit 0 (dependensi dan
  modul baru); `coqchk` exit 0 "Modules were successfully checked"; 4/4
  hasil di keluaran kernel; receipt deterministik (dua capture
  byte-identik, 57 baris; sha256
  `af90fb87a9f4344e9f3d03741d8de8e0993363f59eeea14b6cff21b632a3faf4`).
  `Print Assumptions` teorema utama: **tepat empat** aksioma stdlib
  (`sig_forall_dec`, `sig_not_dec`, `functional_extensionality_dep`,
  `Classical_Prop.classic`), diwarisi dari `RiemannInt`; `Un_cv_le` = 2
  aksioma, tiga hasil lain = 4 aksioma. Tidak ada aksioma proyek,
  `Axiom`, `Parameter`, `Admitted`, atau `admit` (dijaga guard).
- **Batas:** **bersyarat** — eksistensi ketiga limit **tidak**
  dibuktikan; itu target Paket 9 (memakai `Un_cv_crit` +
  `pseries_L2_integer` `A-2026-0010`). Hanya `f_k(x)=x^{-(k+1)}` dengan
  `k ≥ 1`, `N ≥ 1`; bukan `f` umum, bukan eksponen real `p > 1`
  (`Rpower`), bukan L3/L4. **Bukan** penutupan `[J]` periodic-box
  `A-2026-0007` (tetap OPEN); `Coq.Reals` aksiomatik, bukan konsistensi;
  deviasi trusted base 4 aksioma diwarisi dari Paket 7; jika owner
  mensyaratkan literal tiga aksioma, paket ini **tidak** memenuhi syarat
  itu; anti-circularity gate = `TOOL NOT RUN` (NO_LEAN_FILES, exit 2
  menurut kontrak gate) dan **tidak dihitung sebagai sukses**; CI tidak
  punya toolchain Coq sehingga hanya menjalankan guard statis; tidak
  menyentuh zeta/Weil/RH/P≠NP; tidak ada klaim fisik; bukan peer review.
- **Status:** CERTIFIED dengan deviasi trusted base tercatat
- **Domino:** tidak ada (formal; bukan domino)
- **Relasi:** melanjutkan `A-2026-0012` (berkas dan sertifikatnya tidak
  berubah); bergantung pada `A-2026-0012` sebagai modul beku; Paket 9
  (L5 infinite unconditional) belum dikerjakan; `A-2026-0007` `[J]`
  tetap OPEN; entri registry ke-18; memori kerja §2.0ae
  `reports/HANDOFF.md`.
- **Perintah verifikasi:** `python -m pytest msaf/tests/test_coq_bridge_integral_limit.py -q`
  (5 uji statis: placeholder, kelengkapan audit, impor + statement lock,
  receipt/trusted base, 16 mutasi negatif);
  `python -m pytest msaf/tests/test_fence_registry.py -q`; reproduksi
  kernel lokal `formal_bridge/check_integral_limit.sh`.
- **Sertifikat:**

  ```text
  sha256LF e298ad996916074e2fdb900bee9c7a7f86a41bf9fa39ce3bdb7803bed47d293f formal_bridge/IntegralComparisonLimit.v
  sha256LF 3a8bf37a009960fb6df7c02e51699e385e27b77cabf117a05acd691012f830bd formal_bridge/check_integral_limit.sh
  sha256LF af90fb87a9f4344e9f3d03741d8de8e0993363f59eeea14b6cff21b632a3faf4 formal_bridge/IntegralComparisonLimit.receipt.txt
  sha256LF a8e305f20624fd24048693bcd54b41fba868c46e69a14db4dc0359b2402e8a6f msaf/tests/test_coq_bridge_integral_limit.py
  sha256LF 0b7128247f82afa9a47dce4e843b0e0b14bb3b0d977c7ede748756c6656184b1 reports/COQ_BRIDGE_L5_LIMIT_2026-10-20.md
  sha256LF 4df4bc574199a04f9138c14174818bd4bab7a2b2c06a82cef41d0641d43b02c7 reports/PREREG_PAKET8_2026-10-20.md
  ```

### A-2026-0014 — L5 infinite (unconditional) di Coq: eksistensi tiga limit dan perbandingan integral–deret dua sisi untuk `f_k(x)=x^{-(k+1)}`; 17 hasil; trusted base 4 aksioma stdlib

- **Jenis:** A
- **Pernyataan:** Lanjutan Paket 9 (pra-registrasi baru
  `reports/PREREG_PAKET9_2026-10-20.md`; berkas Paket 1–8 **tidak
  diubah**). Berkas baru `formal_bridge/IntegralComparisonInfinite.v`
  mengimpor modul beku `IntegralComparison.v` (`A-2026-0012`),
  `IntegralComparisonLimit.v` (`A-2026-0013`), dan `PseriesL2.v`
  (`A-2026-0010`) apa adanya. Untuk `k ≥ 1`, `N ≥ 1`, teorema utama
  **`integral_comparison_power_infinite`** membuktikan
  `exists L_N L_N1 L_S : R` dengan `Un_cv` untuk integral dari `N`,
  integral dari `N+1`, dan tail sum dari `N+1`, serta
  `L_{N+1} <= L_S <= L_N` — L5 pilot **unconditional** untuk `f_k`
  (`∫_{N+1}^∞ f_k ≤ Σ_{n>N} f_k(n) ≤ ∫_N^∞ f_k`, limit diwakili oleh
  `Un_cv`). 17 hasil: bridging `psum`/`sum_upto`/`pterm`/`fk`, lemma
  shift `Un_cv`, `tail_sum_cv` dari `pseries_L2_integer`, monotonisitas
  dan batas integral lewat `sum_incr`, `whole_val_cv` lewat
  `Un_cv_crit`, dan teorema utama lewat Paket 8. `coqc` exit 0 untuk
  keempat modul; `coqchk` exit 0 "Modules were successfully checked";
  17/17 hasil di keluaran kernel; receipt deterministik (dua capture
  byte-identik, 178 baris; sha256
  `39ad870db3b2fec94745ef95a26161e108e8642d2323666bc856da5954fd056d`).
  `Print Assumptions` teorema utama: **tepat empat** aksioma stdlib
  (`sig_forall_dec`, `sig_not_dec`, `functional_extensionality_dep`,
  `Classical_Prop.classic`); peta per hasil: 1 hasil dengan 1 aksioma,
  10 hasil dengan 2, 1 hasil dengan 3, 5 hasil dengan 4 (rincian di
  laporan §5). Tidak ada aksioma proyek, `Axiom`, `Parameter`,
  `Admitted`, atau `admit` (dijaga guard).
- **Batas:** **unconditional hanya untuk `f_k`** (`k ≥ 1`, `N ≥ 1`);
  bukan `f` umum, bukan eksponen real `p > 1` (`Rpower`), bukan L3/L4;
  **bukan** penutupan `[J]` periodic-box `A-2026-0007` (tetap OPEN);
  `Coq.Reals` aksiomatik, bukan konsistensi; deviasi trusted base
  4-aksioma diwarisi dari `RiemannInt`; jika owner mensyaratkan literal
  tiga aksioma, paket ini **tidak** memenuhi syarat itu; anti-circularity
  gate = `TOOL NOT RUN` (NO_LEAN_FILES; exit 2 menurut kontrak gate) dan
  **tidak dihitung sebagai sukses**; CI tidak punya toolchain Coq
  sehingga hanya menjalankan guard statis; tidak menyentuh
  zeta/Weil/RH/P≠NP; tidak ada klaim fisik; bukan peer review.
- **Status:** CERTIFIED dengan deviasi trusted base tercatat
- **Domino:** tidak ada (formal; bukan domino)
- **Relasi:** melanjutkan `A-2026-0013` (berkas dan sertifikatnya tidak
  berubah); bergantung pada `A-2026-0012`, `A-2026-0013`, dan
  `A-2026-0010` sebagai modul beku; menutup L5 pilot untuk `f_k`;
  `A-2026-0007` `[J]` tetap OPEN; entri registry ke-19; memori kerja
  §2.0af `reports/HANDOFF.md`.
- **Perintah verifikasi:** `python -m pytest msaf/tests/test_coq_bridge_integral_infinite.py -q`
  (5 uji statis: placeholder, kelengkapan audit, impor + statement lock,
  receipt/trusted base, 18 mutasi negatif);
  `python -m pytest msaf/tests/test_fence_registry.py -q`; reproduksi
  kernel lokal `formal_bridge/check_integral_infinite.sh`.
- **Sertifikat:**

  ```text
  sha256LF b0aa2cae7013f4d95cbb3565fa4d88556efe9b24ea085a64b440c101ce083aec formal_bridge/IntegralComparisonInfinite.v
  sha256LF d11d82a691f134a657e0699aaa7b671f98ce37e0d7d99cd672e9d86de46c0712 formal_bridge/check_integral_infinite.sh
  sha256LF 39ad870db3b2fec94745ef95a26161e108e8642d2323666bc856da5954fd056d formal_bridge/IntegralComparisonInfinite.receipt.txt
  sha256LF 5932c2a0d35bf252da6cac768717916daecefa468abdcadf939bdb8550cc16d4 msaf/tests/test_coq_bridge_integral_infinite.py
  sha256LF 9e3ebd3fdd9fe1a7302574a063dad579db409f74e31efa7b8dc6d2aab5d4d726 reports/COQ_BRIDGE_L5_INFINITE_2026-10-20.md
  sha256LF b94cb6e7b889149bdb9f733ef0bf0ac3f690ee277384f4ed2f4d973672630454 reports/PREREG_PAKET9_2026-10-20.md
  ```

### A-2026-0015 — Gate anti-circularity dijalankan pada sumber Lean kernel: PASS 4/4; `lean/spec/` OUT OF SCOPE (9 aksioma); tidak ada input SMT

- **Jenis:** A
- **Pernyataan:** Setelah Paket 9, gate anti-circularity eksternal
  dijalankan pada domainnya: empat berkas **Lean kernel**
  (`lean/ComplexMoore.lean`, `lean/NavierStokesCore.lean`,
  `lean/NewtonExistence.lean`, `lean/XiNoRealZero.lean`).
  `gate.py lean` dan `gate.py check` keduanya exit 0 dengan
  `result: FAIL=0  NOT_RUN=0  SKIP=0`, `verdict: PASS`; tidak ada
  `sorry`/`admit`/`axiom`/`Abort` di kode setelah komentar dibuang, dan
  tidak ada klaim `MACHINE RESULT` tanpa log samping. Log deterministik
  51 baris (dua run byte-identik), sha256
  `6e5c97a9d780e54a54968ca06a4d453236f65b45f881fbc6234902ef53ed9aab`.
  `lean/spec/` sengaja **OUT OF SCOPE`: diagnostik `gate.py lean
  lean/spec` menghasilkan `FAIL=9` untuk sembilan aksioma deklaratif
  `XiAnalyticSpec.lean` (dua simbol opak + tujuh obligasi analitik), dan
  angka itu dicatat sebagai diagnostik, bukan verdict gate. Tidak ada
  `.smt2` di repo, sehingga sub-gate audit **tidak dipanggil** dan tidak
  ada klaim SMT PASS. Laporan Paket 7–9 dan entri
  `A-2026-0012`–`A-2026-0014` **tidak diubah**.
- **Batas:** PASS ini hanya pemindaian statis placeholder/claim pada
  empat berkas Lean kernel; **bukan** bukti kebenaran teorema Lean,
  **bukan** `lake build`, **bukan** audit SMT, **bukan** verifikasi
  `lean/spec/` (9 aksioma kondisional), dan **bukan** verifikasi ulang
  Paket 8/9 Coq. Status `TOOL NOT RUN (NO_LEAN_FILES)` pada laporan beku
  Paket 7–9 tetap berlaku untuk **scope Coq** dan tetap tidak dihitung
  sebagai sukses; entri ini menetapkan status **repo-level untuk sumber
  Lean kernel**. Tidak ada klaim RH/P≠NP/fisika; bukan peer review.
- **Status:** CERTIFIED dengan scope PASS tercatat
- **Domino:** tidak ada (infrastruktur verifikasi; bukan domino)
- **Relasi:** melanjutkan `A-2026-0014` tanpa mengubahnya; menetapkan
  jalur gate yang diminta setelah paket Coq selesai; entri registry
  ke-20; memori kerja §2.0ag `reports/HANDOFF.md`.
- **Perintah verifikasi:** `python -m pytest msaf/tests/test_anti_circularity_gate.py -q`
  (5 uji statis: kernel placeholder, budget spec, log scope, runner/report
  lock, 12 mutasi negatif); `python -m pytest msaf/tests/test_fence_registry.py -q`;
  reproduksi lokal `C:\Python314\python.exe harness/run_anti_circularity_gate.py`
  (gate eksternal; bukan CI).
- **Sertifikat:**

  ```text
  sha256LF 8cd30d7bc3372d8d408ff2db6830dbae666f504feadf1bd5e5951a1810c51551 harness/run_anti_circularity_gate.py
  sha256LF 6e5c97a9d780e54a54968ca06a4d453236f65b45f881fbc6234902ef53ed9aab reports/anti_circularity_gate_2026-10-20.log
  sha256LF 8de7bc3659d670976be47b31da1d38cc2fb25495d40ae9fbc101773506726f5c reports/ANTI_CIRCULARITY_GATE_RUN_2026-10-20.md
  sha256LF 0ce3083e283289cd784304f787164e4230b7944993352a1885dbb2010f637ccf msaf/tests/test_anti_circularity_gate.py
  sha256LF 5b3b263b6796016536653a4511124d9d4b5b81d47798d3580412eef89c86c0e9 lean/ComplexMoore.lean
  sha256LF e92f77e931a2db7c0c783f05688df17f999b72c2114954431296134fed7bca0b lean/NavierStokesCore.lean
  sha256LF 25d4bf7ae743b4b53673f120987c9e3daff2b2043ce7c79a92d5d535c863da49 lean/NewtonExistence.lean
  sha256LF 10ceb227a7f509a655fa4d2616495b2bb56879b7ddc60e3d01e6027c3d3a709b lean/XiNoRealZero.lean
  sha256LF 38818af1cd85b19f1928070b3b964f3be372df3f9de7fa95e4ccf6a52c1fff9b lean/spec/XiAnalyticSpec.lean
  ```

### A-2026-0016 — Verifikasi berlapis di CI: audit aksioma Lean per-deklarasi + job Coq 8.20.1 pinned untuk Paket 8/9

- **Jenis:** A
- **Pernyataan:** CI kini menjalankan dua jalur verifikasi nyata yang
  sebelumnya tidak ada. (1) Job `lean-kernel` menjalankan
  `msaf/tests/test_lean_axiom_audit.py::test_every_declaration_uses_standard_axioms_only`
  setelah `lake build`; audit 83 deklarasi kernel gagal jika ada
  dependensi di luar `propext`, `Classical.choice`, `Quot.sound`.
  (2) Job baru `coq-kernel` menjalankan `check_integral_limit.sh`
  (Paket 8, `A-2026-0013`) dan `check_integral_infinite.sh` (Paket 9,
  `A-2026-0014`) di dalam container
  `coqorg/coq:8.20.1@sha256:18ebf3da56e60e3ddfd7d4e51f4c53d10241a129f34e93dacbc71562dd43c57a`;
  kedua skrip memverifikasi hasil 4/4 dan 17/17, `coqchk` "Modules
  were successfully checked", dan trusted base tepat empat aksioma
  stdlib. Guard statis baru `msaf/tests/test_ci_verification_paths.py`
  (5 uji) mengunci urutan, image+digest, kedua skrip, sensor
  `spec_v2` budget 8, dan ketiadaan `continue-on-error`; tujuh mutasi
  negatif ditolak.
- **Batas:** bukan hasil matematis baru; tidak mengubah trusted base
  Coq empat aksioma stdlib; tidak memverifikasi `lean/spec/` atau
  `lean/spec_v2/` ke dalam audit kernel; tidak ada input SMT; bukan
  klaim CI hijau (run ID di `reports/HANDOFF.md` §2.0ah); status
  `TOOL NOT RUN (NO_LEAN_FILES)` laporan beku Paket 7–9 tidak ditulis
  ulang. Tanpa klaim RH/P≠NP/fisika.
- **Amandemen 2026-10-20:** sensor `Escape-token sensor -- kernel`
  tidak lagi memindai `lean/spec_v3`–`lean/spec_v6` dengan grep mentah.
  Paket-paket itu bersertifikat dan memiliki guard/workflow sendiri
  (`test_xi_spec_v3/v4/v5/v6.py`) yang memindai setelah komentar
  dibuang; grep mentah salah menandai docstring “no `sorry`” di V4/V6.
  Perubahan hanya pada daftar `--exclude-dir`; audit aksioma
  per-deklarasi, sensor `spec`/`spec_v2`, dan job Coq tidak berubah.
  Sertifikat `ci.yml` diperbarui ke hash baru; guard
  `test_ci_verification_paths.py` tetap 5 uji hijau. Run CI
  pasca-amandemen `39426728099` (commit `1c806cb`) hijau:
  `lean-kernel`, `python-tests`, dan `coq-kernel` sukses.
- **Status:** CERTIFIED dengan scope tercatat
- **Domino:** tidak ada (infrastruktur verifikasi; bukan domino)
- **Relasi:** melanjutkan `A-2026-0015` tanpa mengubahnya; memakai
  Paket 8/9 (`A-2026-0012`–`A-2026-0014`) sebagai modul beku; entri
  registry ke-21; memori kerja §2.0ah `reports/HANDOFF.md`.
- **Perintah verifikasi:** `python -m pytest msaf/tests/test_ci_verification_paths.py -q`;
  `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml', encoding='utf-8'))"`;
  `python -m pytest msaf -q`; `python audit_quantum/freeze.py --verify`.
- **Sertifikat:**

  ```text
  sha256LF 52619c25fe9197f6fe892a052cd86bf858a5c4b91725f7abc84b2e3b6c256079 .github/workflows/ci.yml
  sha256LF 231ce892f3976b5525e74d18720d85cfe5ada9fcfd2688941467e9c98d144ab7 msaf/tests/test_ci_verification_paths.py
  sha256LF 3339a51d290c9d47cd3dd8dbd34cbcc8d0fbcca9622aa3fe9254cd724afc9df4 reports/CI_HARDENING_2026-10-20.md
  ```

### A-2026-0017 — Koreksi spec Xi V2: kontradiksi endpoint dihapus; 8 aksioma; berkas lama tetap beku

- **Jenis:** A
- **Pernyataan:** `lean/spec/XiAnalyticSpec.lean` (`A-2026-0015`) tidak
  konsisten: dari `xiReal_sub_one 0`, `xiReal 1 = 0`, dan
  `xiReal 0 = 1/2` Lean menerima `False`; aksioma `zetaReal_neg` juga
  salah di `x = -2` dan tidak terpakai. Berkas baru
  `lean/spec_v2/XiAnalyticSpecV2.lean` memperbaiki batas abstraksi:
  `xiReal` dijaga di `x = 1` (`1/2`), `xiReal_sub_one` dibatasi ke
  `x < 0`, dan `zetaReal_neg` dihapus. V2 mendeklarasikan **8**
  aksioma; `xi_pos_on_reals` lolos kompilasi dan
  `#print axioms` menunjukkan delapan aksioma V2 plus tiga aksioma
  standar Lean, tanpa `zetaReal_neg`; probe kontradiksi lama exit 1
  (tertutup). Guard `msaf/tests/test_xi_spec_v2.py` (3 uji, termasuk
  probe Lean) dan sensor CI `spec_v2` budget 8 mengunci keadaan itu.
- **Batas:** V2 tetap **spec abstrak kondisional**, bukan bukti
  tentang fungsi xi sebenarnya: `zetaReal`/`gammaReal` opak, dan
  bentuk produk **tidak faithful** di bilangan bulat genap negatif
  (kutub Gamma klasik). Bukan bukti Riemann Hypothesis, bukan peer
  review, tidak mengubah trusted base Coq empat aksioma. Berkas lama
  `lean/spec/XiAnalyticSpec.lean` tetap byte-identik dan hanya
  ditandai lewat `lean/spec/README.md`; entri `A-2026-0015` tidak
  diubah. Langkah V3 faithful (Mathlib zeta/Gamma) belum dieksekusi.
- **Status:** CERTIFIED dengan scope tercatat
- **Domino:** tidak ada (koreksi spec; bukan domino)
- **Relasi:** menetapkan pemakaian baru setelah `A-2026-0015`; tidak
  mengubah `A-2026-0012`–`A-2026-0016`; entri registry ke-22; memori
  kerja §2.0ai `reports/HANDOFF.md`.
- **Perintah verifikasi:** `lake env lean spec_v2/XiAnalyticSpecV2.lean`
  (dari `lean/`); `python -m pytest msaf/tests/test_xi_spec_v2.py -q`;
  `python -m pytest msaf -q`.
- **Sertifikat:**

  ```text
  sha256LF 1acc5c33dbc8b134e0272cf95073bd8e343a34d3abbc76a6fae915a6d9a0c955 lean/spec_v2/XiAnalyticSpecV2.lean
  sha256LF 99074dfea388855ad0b16418a98ca76b4203c8b4932c2755547142c5fbf04e70 lean/spec/README.md
  sha256LF 58d7f3866c12d1dc1a18068a57e207e5349df3a416a780565a2c4adac8838da9 msaf/tests/test_xi_spec_v2.py
  sha256LF 36cd6dd90ed48a0246cbcdb37cb34ddf3d222336adc2be7f0650b619dd392c19 reports/XI_SPEC_V2_2026-10-20.md
  ```

### A-2026-0018 — Spec Xi V3 faithful: nol aksioma proyek; satu hipotesis eksplisit `hmid`

- **Jenis:** A
- **Pernyataan:** `lean/spec_v3/XiAnalyticFaithful.lean` mendefinisikan
  `xiReal` dari `completedRiemannZeta` Mathlib v4.33.1 (bagian real,
  guard di `0`/`1`), membuktikan `xiReal (1 - x) = xiReal x` untuk semua
  real `x`, dan membuktikan `0 < xiReal x` untuk `x > 1` tanpa aksioma
  proyek. `xi_pos_on_reals` menyisakan tepat satu hipotesis eksplisit
  `hmid : ∀ x, 0 < x → x < 1 → (completedRiemannZeta (x : ℂ)).re < 0`;
  bukan aksioma global. `#print axioms` untuk master theorem, persamaan
  fungsional, dan positivity `x > 1` hanya memuat `propext`,
  `Classical.choice`, `Quot.sound`; nol deklarasi
  `XiAnalyticFaithful.*`. Kompilasi exit 0 (18,566 dtk); guard 3 uji
  lulus; gate anti-circularity PASS pada sumber V3 (`FAIL=0`,
  `NOT_RUN=0`, `SKIP=0`).
- **Batas:** V3 **kondisional** pada `hmid`; `hmid` benar secara
  matematis tetapi belum dibuktikan di Lean/Mathlib. Realness
  `completedRiemannZeta` pada sumbu real tidak diformalkan terpisah;
  `xiReal` adalah bagian real dari ekspresi standar. Bukan bukti RH,
  bukan peer review, bukan verifikasi SMT (tidak ada `.smt2`), bukan
  klaim P≠NP/fisika. Tidak mengubah trusted base Coq empat aksioma
  stdlib; V1/V2 dan entri `A-2026-0015`/`0016`/`0017` tidak diubah;
  `ci.yml` tidak diubah (workflow V3 terpisah).
- **Status:** CERTIFIED dengan scope tercatat
- **Domino:** tidak ada (spec/verifikasi; bukan domino)
- **Relasi:** melanjutkan `A-2026-0017` (V2) tanpa mengubahnya;
  menggantikan pemakaian V2 untuk pekerjaan berikutnya; entri registry
  ke-23; memori kerja §2.0ak `reports/HANDOFF.md`.
- **Perintah verifikasi:** `lake env lean spec_v3/XiAnalyticFaithful.lean`
  (dari `lean/`); `python -m pytest msaf/tests/test_xi_spec_v3.py -q`;
  `python -m pytest msaf -q`; `python audit_quantum/freeze.py --verify`;
  `python -m pytest msaf/tests/test_fence_registry.py -q`; gate eksternal
  `python .../gate.py lean lean/spec_v3/XiAnalyticFaithful.lean`.
- **Sertifikat:**

  ```text
  sha256LF d9d516965b45e119d1ae6d9feaac124c999c3db77bb028c7376eda1eaad46b6f lean/spec_v3/XiAnalyticFaithful.lean
  sha256LF d341c45f258d8bf38df7c43210ed903c959f1ee4260be7be580894ff9943eb2a msaf/tests/test_xi_spec_v3.py
  sha256LF e6c9f2505dfb7bdbb95e9169dd0e68d3d81fbc30046e868e12245675bfa99e63 .github/workflows/spec-v3.yml
  sha256LF d0c02bc19c117190b7641a68d5d5b5b9e6397b2215b8523d270ecb825b005f12 reports/XI_SPEC_V3_2026-10-20.md
  sha256LF 18e2cc69a5253df9463c66389593bb4c5cfd53807c95ba6345daa4e638bc69ad reports/PREREG_SPEC_V3_2026-10-20.md
  sha256LF 00802ed3a139b227922a29b2586d6e81e64d0c3433fa76ab33afd63b071b1ca1 reports/anti_circularity_gate_v3_2026-10-20.log
  ```

### A-2026-0019 — Spec Xi V4 unconditional: `hmid` dibuktikan tanpa hipotesis

- **Jenis:** A
- **Pernyataan:** `lean/spec_v4/XiUnconditional.lean` membuktikan
  `hmid : ∀ x : ℝ, 0 < x → x < 1 →
  (completedRiemannZeta (x : ℂ)).re < 0` sebagai teorema tertutup,
  tanpa aksioma proyek dan tanpa `sorry`. Rute: (1) tanda kernel
  `cosKernel (1/2) t - 1 < 0` untuk `t > 0` dari pasangan suku θ₄;
  (2) batas decay + keterdiferensialan Mellin dan jembatan
  `completedCosZeta (1/2) s = mellin fC (s/2)/2` pada `0 < re s`;
  (3) kelinearan `mellin` + integral real `fC` memberi
  `completedCosZeta (1/2) x < 0` untuk `0 < x`; (4) pembuangan faktor
  `Gammaℝ (x) > 0` memberi `cosZeta (1/2) x < 0` pada `(0, 1)`;
  (5) identitas eta `cosZeta (1/2) s = (2^(1−s) − 1) ζ(s)` dibuktikan
  dulu untuk `1 < re s` lewat pemisahan paritas deret Dirichlet
  (`HasSum.even_add_odd`, skala `2^(−s)`), lalu diperluas ke `s ≠ 1`
  dengan kontinuasi analitik pada himpunan terhubung `{1}ᶜ`;
  (6) `2^(1−x) − 1 > 0` untuk `x < 1` memberi `ζ(x) < 0`, dan
  `completedRiemannZeta = Gammaℝ · ζ` menutup `hmid`.
  `#print axioms` untuk `hmid`, `cosZeta_half_neg`, dan
  `completedCosZeta_half_eq_mellin` hanya memuat `propext`,
  `Classical.choice`, `Quot.sound`; nol `sorryAx`, nol deklarasi
  `XiUnconditional.*`. Kompilasi exit 0 tanpa diagnostik; guard V4
  3 uji lulus (49,41 dtk); suite penuh 456 uji lulus (171,93 dtk); gate
  anti-circularity PASS pada `lean` dan
  `claim` (`FAIL=0`, `NOT_RUN=0`, `SKIP=0`); subgate `audit` =
  `TOOL NOT RUN` (UNPARSEABLE — tidak ada `.smt2`), dicatat verbatim.
- **Batas:** V4 mewujudkan `hmid` untuk `completedRiemannZeta` Mathlib
  v4.33.1 pada interval real `(0, 1)`; ini **bukan** bukti RH, bukan
  peer review, bukan verifikasi SMT (tidak ada `.smt2` dan tidak ada
  klaim SMT), bukan klaim P≠NP/fisika. V4 tidak menyentuh V1/V2/V3
  (beku), `ci.yml`, `spec-v3.yml`, `test_xi_spec_v3.py`, atau
  `audit_collatz/exec_2026-10-19/`. Gate PASS hanya menyatakan tidak ada
  placeholder/klaim-komentar di berkas, bukan kebenaran bukti;
  kebenaran bersandar pada kernel Lean (exit 0 + `#print axioms`).
  Trusted base Coq empat aksioma stdlib tidak berubah.
- **Status:** CERTIFIED dengan scope tercatat
- **Domino:** tidak ada (spec/verifikasi; bukan domino)
- **Relasi:** mendischarge hipotesis `hmid` yang ditinggalkan V3
  (`A-2026-0018`) tanpa mengubah berkas V3; entri registry ke-24;
  memori kerja §2.0al `reports/HANDOFF.md`.
- **Perintah verifikasi:** `lake env lean spec_v4/XiUnconditional.lean`
  (dari `lean/`); `python -m pytest msaf/tests/test_xi_spec_v4.py -q`;
  `python -m pytest msaf -q`; `python audit_quantum/freeze.py --verify`;
  `python -m pytest msaf/tests/test_fence_registry.py -q`; gate eksternal
  `python .../gate.py lean lean/spec_v4/XiUnconditional.lean`.
- **Sertifikat:**

  ```text
  sha256LF 3b2dcd20a32a4ba4f53694024911e1061260820f5701b2b431f5a02adaa5b64c lean/spec_v4/XiUnconditional.lean
  sha256LF 43b60b7b528b8264ff2b3e5f3460ce088053fb88a5d289a928f2dca11e1127ea msaf/tests/test_xi_spec_v4.py
  sha256LF 31af3a54c1bb22aa9639691d3f5d540c63b652dc043cad1dc5b835a021e99452 .github/workflows/spec-v4.yml
  sha256LF b9c88d9c5abfd1b6c8aeebec068229ba3f3b1ca63dd88747fe55fe7c0036c2e3 reports/PREREG_XI_UNCONDITIONAL_2026-10-20.md
  sha256LF 618d911d82d3a17cc6e8d8f3ff26a3caa98eb841dbaf0ec82c3989b8ebdf16cb reports/anti_circularity_gate_v4_2026-10-20.log
  ```

### A-2026-0020 — Spec Xi V6: jembatan kisi berhingga → `completedCosZeta (1/2)` dengan galat eksplisit

- **Jenis:** A
- **Pernyataan:** `lean/spec_v6/FiniteLatticeBridge.lean` membuktikan
  jembatan bersertifikat dari truncation kisi berhingga ke objek tak hingga
  `completedCosZeta (1/2)`, tanpa aksioma proyek dan tanpa `sorry`:
  (T1) `abs_kHalf_sub_lattice_le`: untuk `t > 0` dan `N : ℕ`,
  `|kHalf t − latticeSum N t| ≤ latticeTerm t N` (batas ekor alternating
  oleh suku pertama yang dihilangkan); (T2)
  `completedCosZeta_half_lattice_error`: untuk `x > 0`,
  `‖completedCosZeta (1/2) (x : ℂ) − (latticeValue N x : ℂ)‖ ≤ latticeError N x`
  dengan `latticeValue N x = Γ(x/2) π^(−x/2) ∑_{n<N} (−1)^(n+1) (n+1)^(−x)`
  dan `latticeError N x = Γ(x/2) π^(−x/2) (N+1)^(−x)`; (T3)
  `completedCosZeta_half_neg_of_lattice_certificate`: sertifikat negatif
  `latticeValue N x + latticeError N x < 0` mentransfer tanda ke
  `(completedCosZeta (1/2) (x : ℂ)).re < 0`; (K1)
  `completedCosZeta_half_neg_of_first_term`: `N = 1` sudah cukup untuk
  setiap `x > 0`. Jembatan memakai identitas Mellin V4
  `completedCosZeta_half_eq_mellin` secara baca-saja; lemma
  `rpow_pi_mul_sq` menyelaraskan basis gabungan `(π(n+1)^2)^(−x/2)`
  dengan bentuk terpisah §2 pra-registrasi.
  `#print axioms` untuk T1, T2, T3, K1 hanya memuat `propext`,
  `Classical.choice`, `Quot.sound`; nol `sorryAx`, nol deklarasi
  `FiniteLatticeBridge.*` di footprint. Kompilasi exit 0 tanpa error dan
  tanpa warning; guard V6 3 uji lulus (19,34 dtk); gate anti-circularity
  PASS pada `lean`, `claim`, dan `check` (`FAIL=0`, `NOT_RUN=0`,
  `SKIP=0`); subgate `audit` = `TOOL NOT RUN` (UNPARSEABLE — tidak ada
  `.smt2`), dicatat verbatim.
- **Batas:** V6 membuktikan pernyataan tentang `completedCosZeta (1/2)`
  saja; ini **bukan** bukti RH, bukan klaim lokasi nol, bukan derivasi
  `σ = 1/2`, bukan verifikasi SMT (tidak ada `.smt2`), bukan peer review.
  Batas L11/L12 `msaf/AUDIT.md` tetap berlaku: kisi adalah instrumen
  bersertifikat untuk `completedCosZeta`, bukan kunci RH; jembatan RH
  sesungguhnya memerlukan Weil–Guinand atau konvergensi nol spektral yang
  tidak tersedia di Mathlib v4.33.1. Gate PASS hanya menyatakan tidak ada
  placeholder/klaim-komentar di berkas, bukan kebenaran bukti; kebenaran
  bersandar pada kernel Lean (exit 0 + `#print axioms`). V6 tidak mengubah
  V1–V5, `ci.yml`, `spec-v3.yml`, `spec-v4.yml`, `test_xi_spec_v3.py`,
  `lean/lakefile.toml`, atau `audit_collatz/exec_2026-10-19/`.
- **Status:** CERTIFIED dengan scope tercatat
- **Domino:** tidak ada (spec/verifikasi; bukan domino)
- **Relasi:** jembatan pertama dari kisi berhingga ke
  `completedCosZeta (1/2)`; memakai `completedCosZeta_half_eq_mellin`
  dari V4 (`A-2026-0019`) secara baca-saja; entri registry ke-25; memori
  kerja §2.0am `reports/HANDOFF.md`.
- **Perintah verifikasi:** `lake env lean spec_v6/FiniteLatticeBridge.lean`
  (dari `lean/`); `python -m pytest msaf/tests/test_xi_spec_v6.py -q`;
  `python -m pytest msaf -q`; `python audit_quantum/freeze.py --verify`;
  `python -m pytest msaf/tests/test_fence_registry.py -q`; gate eksternal
  `python .../gate.py lean lean/spec_v6/FiniteLatticeBridge.lean`.
- **Sertifikat:**

  ```text
  sha256LF 2b04f23d5382a6469be05eaad80426554b2ee8b8763146d49c846e6f6ae18e5b lean/spec_v6/FiniteLatticeBridge.lean
  sha256LF e09c52abd731c6ca6176bcca7cae945914f9dca3fc89e83cf4df4e895e31beab msaf/tests/test_xi_spec_v6.py
  sha256LF f714e94fb8f89dedf47f97677ab2e54adf25c2ccfb09201282a40545fc1a3e1e .github/workflows/spec-v6.yml
  sha256LF 5a69474491ae3821fcc7d9c470135decf04013535013048b3e93527a250af137 reports/PREREG_FINITE_LATTICE_BRIDGE_2026-10-20.md
  sha256LF c61c9f931f8191e9a633bbedf53ff283408112014edbfa745155eb3d79926844 reports/anti_circularity_gate_v6_2026-10-20.log
  ```

### A-2026-0021 — Spec Xi V5: positivity xi unconditional via V3+V4 (glue)

- **Jenis:** A
- **Pernyataan:** `lean/spec_v5/XiPosUnconditional.lean` menutup hipotesis
  midpoint `hmid` yang eksplisit di V3
  (`XiAnalyticFaithful.xi_pos_on_reals`) dengan teorema tertutup V4
  (`hmid`). Teorema V5:
  `XiPosUnconditional.xi_pos_on_reals_unconditional :
  ∀ x : ℝ, 0 < XiAnalyticFaithful.xiReal x`, dibuktikan dengan
  `XiAnalyticFaithful.xi_pos_on_reals hmid x` (V4 `hmid` berada di root
  namespace). Ini adalah **glue**: tidak ada konten analitik baru, tidak
  ada estimasi, kisi, atau parameter numerik. `#print axioms` hanya
  memuat `propext`, `Classical.choice`, `Quot.sound`; nol `sorryAx`, nol
  deklarasi `XiPosUnconditional.*` di footprint. Kompilasi exit 0; guard
  V5 3 uji lulus (16,73 dtk); gate anti-circularity PASS pada `lean`,
  `claim`, dan `check` (`FAIL=0`, `NOT_RUN=0`, `SKIP=0`); subgate `audit`
  = `TOOL NOT RUN` (UNPARSEABLE — tidak ada `.smt2`), dicatat verbatim.
- **Batas:** V5 hanya menutup `hmid` V3 memakai V4; **bukan** bukti RH,
  bukan klaim lokasi nol, bukan derivasi `σ = 1/2`, bukan verifikasi SMT,
  bukan peer review. V5 **bukan** “V5 Campaign (H1 + engine-B)” dan
  **bukan** “V5 via V6 parameters”: H1/engine-B/dashboard adalah jalur
  spectral terpisah yang sudah selesai/beku, sedangkan V6 (`A-2026-0020`)
  adalah jembatan kisi `completedCosZeta (1/2)` dan tidak dipakai V5.
  Gate PASS hanya menyatakan tidak ada placeholder/klaim-komentar di
  berkas, bukan kebenaran bukti; kebenaran bersandar pada kernel Lean
  (exit 0 + `#print axioms`). V5 tidak mengubah V1–V4/V6, `ci.yml`,
  `spec-v3.yml`, `spec-v4.yml`, `spec-v6.yml`, `test_xi_spec_v3.py`,
  `lean/lakefile.toml`, atau `audit_collatz/exec_2026-10-19/`.
- **Status:** CERTIFIED dengan scope tercatat
- **Domino:** tidak ada (spec/verifikasi; bukan domino)
- **Relasi:** menutup hipotesis `hmid` V3 (`A-2026-0018`) memakai V4
  (`A-2026-0019`) secara baca-saja; entri registry ke-26; memori kerja
  §2.0an `reports/HANDOFF.md`.
- **Perintah verifikasi:** `lake env lean spec_v5/XiPosUnconditional.lean`
  (dari `lean/`); `python -m pytest msaf/tests/test_xi_spec_v5.py -q`;
  `python -m pytest msaf -q`; `python audit_quantum/freeze.py --verify`;
  `python -m pytest msaf/tests/test_fence_registry.py -q`; gate eksternal
  `python .../gate.py lean lean/spec_v5/XiPosUnconditional.lean`.
- **Sertifikat:**

  ```text
  sha256LF dcea803d9f16f2dc42239532e9df41a2643a0da9867565136d2fc8bce3879a57 lean/spec_v5/XiPosUnconditional.lean
  sha256LF 32354492154c0ceacd4826f40a1047bfb860e90042689b93d55782c1d70bec9a msaf/tests/test_xi_spec_v5.py
  sha256LF ed6f76718b2b9be9135ccb4762db34487439d094f1a526201cb0f5b3786e4137 .github/workflows/spec-v5.yml
  sha256LF a20ee9bb3d7ec08e079631e0b95d855028bc151a425155c641df27982828304a reports/PREREG_XI_POS_UNCONDITIONAL_2026-10-20.md
  sha256LF 91230f9ac632595feefa2bf12da38627d83dcc88af2f4b7dfdcd9af862ccac15 reports/anti_circularity_gate_v5_2026-10-20.log
  ```

### A-2026-0022 — Sertifikat exact permutasi uniter `Z_N^×`: perioda dan spektrum cyclotomic (item 2 blueprint)

- **Jenis:** A
- **Pernyataan:** `msaf/zn_permutation.py` membangun
  `U|x⟩ = |a x mod N⟩` pada `X_N = (Z/NZ)^×` terurut dan
  menyertifikasi dua instance exact: `N=15, a=2` (dim 8, `M=4`) dan
  `N=21, a=2` (dim 12, `M=6`). Semua jalur inti memakai
  `fmpq_mat`/`fmpq_poly`, tanpa `float`, `numpy`, atau `arb`.
  Untuk kedua instance: `U` permutation matrix `0/1`; `UᵀU=I` dan
  `UUᵀ=I`; `U^M=I` dan `U^k≠I` untuk `1≤k<M`; dua siklus panjang
  `M`; `charpoly=(x^M−1)^(φ(N)/M)` dan `minpoly=x^M−1`; faktorisasi
  cyclotomic exact. Nilai: `N=15` `charpoly=x^8−2x^4+1`,
  `minpoly=x^4−1`, matrix SHA-256
  `e4092e0155e3ea225966cc8a64e1e0a6cd9f47e4e25e510b3a8e24d99b9a58d8`;
  `N=21` `charpoly=x^12−2x^6+1`, `minpoly=x^6−1`, matrix SHA-256
  `e40b2334b942a2fc0feed818e5b5a5a39b79d745625e95acd3fe7f3b21cc2a85`.
  Receipt kanonik:
  `c80b6621fcb1797a0c78f615176dc1400e6210011a084f733092bcb3719bda6c`.
  Komutasi dengan `CyclicShift` adalah `NONZERO` untuk kedua instance
  (witness `N=15`: row 1, col 4, value 1, 10 entri; `N=21`: row 1,
  col 6, value 1, 14 entri); kontrol `H=U+Uᵀ` memberi `ZERO` tetapi
  tautologis. Guard 9 uji lulus; suite penuh 471 lulus (277,32 dtk);
  CI run `39442388960` (commit `6d7b78a`) sukses: `python-tests` 1m1s,
  `coq-kernel` 1m57s, `lean-kernel` 2m16s.
- **Batas:** ini sertifikat finite untuk dua instance mainan, bukan
  teorema umum; **bukan** algoritma faktorisasi, bukan pemecahan
  RSA/ECC, bukan klaim keamanan kriptografi, dan bukan klaim
  period-finding efisien. `M` adalah order publik; tidak ada klaim
  bahwa spektrum `U` mengekstrak rahasia. Komutasi `NONZERO` dicatat
  sebagai hasil finite, bukan kegagalan inti. Tidak ada klaim RH,
  lokasi nol, `σ=1/2`, fisika, Lean, Coq, atau SMT. Tidak mengubah
  V1–V6 (`A-2026-0015`–`A-2026-0021`), `ci.yml`, workflow spec, freeze
  pins, atau artefak beku.
- **Status:** CERTIFIED dengan scope tercatat
- **Domino:** tidak ada (sertifikat finite; bukan domino)
- **Relasi:** item 2 dari `reports/FIVE_CORE_BLUEPRINT_TRIAGE_2026-10-20.md`;
  entri registry ke-27; memori kerja §2.0ap `reports/HANDOFF.md`.
- **Perintah verifikasi:** `python -m msaf.zn_permutation`;
  `python -m pytest msaf/tests/test_zn_permutation.py -q`;
  `python -m pytest msaf -q`; `python audit_quantum/freeze.py --verify`;
  `python -m pytest msaf/tests/test_fence_registry.py -q`;
  `gh run view 39442388960`.
- **Sertifikat:**

  ```text
  sha256LF db8b5704aa86092fa3baa4e3872a1d3079594316a28a39ec1384a6246aaf8cd4 msaf/zn_permutation.py
  sha256LF d488a05d4c75a6de0cd7fa4a60a09ab42f55b20eb3909344ecb3a0214412cc3b msaf/tests/test_zn_permutation.py
  sha256LF 80474c5447b5215bdc8e19548450ef68c60e879ff2423aac01a7d6ecc34e2cbf reports/PREREG_ZN_PERMUTATION_2026-10-20.md
  sha256LF 3b272bec1bb0a452adf1d2d3ec6f3f6de36ab911976a0d5848099d9897e226de reports/ZN_PERMUTATION_2026-10-20.md
  sha256LF ed2bcc517d94dc2f47861ed00bb0badfbad5152dbb41451197f82e3b24894d79 reports/zn_permutation_2026-10-20.json
  ```

### A-2026-0023 — Benchmark diagnostik RBM Anderson S1/S2 (item 4 blueprint)

- **Jenis:** A
- **Pernyataan:** `msaf/rbm_anderson.py` membangun ensemble finite
  complex Hermitian banded matrices berukuran `D=201`, bandwidth
  `b=1,10,120`, dari entri rasional exact integer 16-bit dengan seed
  master `2430500035454946990`; lapisan statistik S1/S2 memakai float64
  dan tiga spot-check `acb_mat.eig` 128-bit. Null model Poisson/GUE
  memakai 2000 reference spectra dan 64 calibration spectra masing-masing;
  grid S2 adalah 3 `σ_u` × 2 chart. Hasil: kalibrasi S1 4/4; kalibrasi S2
  12/12; S1 monotonik `b=1 < b=10 < b=120` di kedua chart dengan
  `b=1` near-Poisson (`0,3946`) dan `b=120` GUE (`0,6002`); label S2
  ekstrem 6/6 Poisson (`b=1`) dan 6/6 GUE (`b=120`); spot-check maksimum
  deviasi eigenvalue `6,22e-14`, semua bagian imajiner memuat nol.
  Receipt kanonik
  `3744cbe92546256f8cb9c25c0dabb16a98921838ebfa026c07c60e5c4892bca3`.
  Guard 9 uji lulus; suite penuh 480 lulus (239,64 dtk); CI run
  `39451466416` (commit `d629823`) sukses.
- **Batas:** benchmark estimator finite satu dimensi; label fase adalah
  jarak **relatif** ke null, bukan kesamaan distribusi. `b=1` bukan
  Poisson eksak dan `b=10` bukan GUE eksak. **Bukan** klaim transisi
  Anderson fisik, universalitas RMT, fisika, faktorisasi, RSA/ECC, RH,
  lokasi nol, atau `σ=1/2`. Tidak mengubah V1–V6, `ci.yml`, workflow spec,
  freeze pins, atau artefak beku.
- **Status:** CERTIFIED dengan scope tercatat
- **Domino:** tidak ada (benchmark diagnostik finite; bukan domino)
- **Relasi:** item 4 dari `reports/FIVE_CORE_BLUEPRINT_TRIAGE_2026-10-20.md`;
  entri registry ke-28; memori kerja §2.0aq `reports/HANDOFF.md`.
- **Perintah verifikasi:** `python -m msaf.rbm_anderson`;
  `python -m pytest msaf/tests/test_rbm_anderson.py -q`;
  `python -m pytest msaf -q`; `python audit_quantum/freeze.py --verify`;
  `python -m pytest msaf/tests/test_fence_registry.py -q`;
  `gh run view 39451466416`.
- **Sertifikat:**

  ```text
  sha256LF ea3cce26480d06b55269865e1e18cde86e2c60510abc31159d9400695e6d73f8 msaf/rbm_anderson.py
  sha256LF 5105bc429bbc1dda2a6abfd1f91039edd4423463ef981636cb0f125d162f68ba msaf/tests/test_rbm_anderson.py
  sha256LF 62c9940a831a43e70376077d58972c49c7ef686e20751900be681606a595a014 reports/PREREG_RBM_ANDERSON_2026-10-20.md
  sha256LF f0cb4e0894799b40f5add4eaf302de9bbeb8b023802f7ccec72417678497925a reports/RBM_ANDERSON_2026-10-20.md
  sha256LF 4ff31e634f6250174aad30c12354f152fd8919d195b9d0883844c0f7c66c3257 reports/rbm_anderson_2026-10-20.json
  ```

### A-2026-0024 — Spectral closure Ulam finite untuk peta skew tent chaotik (item 5 blueprint)

- **Jenis:** A
- **Pernyataan:** `msaf/ulam_spectral.py` membangun matriks Ulam
  exact-rational untuk peta skew tent penuh-cabang
  `T_N(x)=x/p_N` di `[0,p_N]` dan `(1-x)/(1-p_N)` di `[p_N,1]`,
  dengan `p_N=N/(2(N+1))`, pada partisi seragam. Dua instance dikunci:
  `N=16, p=8/17` (primer) dan `N=32, p=16/33` (replikasi). Setiap entri
  `P_ij=N*|I_i ∩ T_N^{-1}(I_j)|` dihitung sebagai `Fraction` exact.
  Kedua matriks nonnegative, row-stochastic tepat, non-simetris, dan
  full rank; `rank(P-I)=N-1` serta diskriminan charpoly nonzero,
  sehingga eigenvalue Perron `1` simple dan seluruh spektrum simple.
  Enclosure `arb_mat.eig(multiple=True, algorithm="rump")` pada ladder
  `64/128/256/512/1024` bit memberi satu Perron yang memuat `1`,
  semua eigenvalue non-Perron `abs_upper < 1`, dan lebar menurun ketat.
  Target `1e-25` pertama tercapai di **128 bit**; lebar 1024 bit
  `5.70e-307` (`N=16`) dan `1.15e-306` (`N=32`); spectral-gap lower
  bound `0,6131` dan `0,5954`. `ResolutionAlarm` fail-closed di guard,
  tidak terpicu kampanye. Receipt kanonik
  `4a850532be255fd0f68a55d529c12d3406696b50e281997daba20528dcb883ac`.
  Guard 9 uji lulus; suite penuh 489 lulus (238,31 dtk); CI run
  `39460603962` (commit `2ad4228`) sukses.
- **Batas:** ini sertifikat **matriks Ulam finite** `N=16/32`, bukan
  klaim tentang operator transfer kontinu, ergodisitas global, mixing,
  invariant density kontinu, discretization error, atau limit
  `N -> infinity`. **Newton contraction 60 iterasi tidak diuji**
  (`newton_contraction_tested=false`); angka 60 hanya budget attempt
  resolusi. Logistic `r=4` tidak dipakai untuk spektrum karena partisi
  seragamnya rank-deficient dengan klaster nol; tidak ada klaim spektrum
  logistic. Tidak ada klaim RH, lokasi nol, `σ=1/2`, faktorisasi,
  RSA/ECC, Anderson, atau fisika. Tidak mengubah V1–V6
  (`A-2026-0015`–`A-2026-0021`), `A-2026-0022`, `A-2026-0023`, `ci.yml`,
  workflow spec, freeze pins, atau artefak beku; tidak ada kampanye
  tersegel yang dijalankan ulang.
- **Status:** CERTIFIED dengan scope tercatat
- **Domino:** tidak ada (sertifikat finite; bukan domino)
- **Relasi:** item 5 dari `reports/FIVE_CORE_BLUEPRINT_TRIAGE_2026-10-20.md`;
  entri registry ke-29; memori kerja §2.0ar `reports/HANDOFF.md`.
- **Perintah verifikasi:** `python -m msaf.ulam_spectral`;
  `python -m pytest msaf/tests/test_ulam_spectral.py -q`;
  `python -m pytest msaf -q`; `python audit_quantum/freeze.py --verify`;
  `python -m pytest msaf/tests/test_fence_registry.py -q`;
  `gh run view 39460603962`.
- **Sertifikat:**

  ```text
  sha256LF 0b722f6402142235cc40ff4e3a62d1b0c7d589df813cf07565e88c352ac7a0ff msaf/ulam_spectral.py
  sha256LF 7729ad2f5566b05c5baec96f58584bcddf55fcfe7626f25cd5a815e38650fa2d msaf/tests/test_ulam_spectral.py
  sha256LF b07e3aba4ead7a3676db10b3ccfb204265eba1ef61eb31d9f17caebe3078f82d reports/PREREG_ULAM_SPECTRAL_2026-10-21.md
  sha256LF 88996bafc274c228b7225410121f8083de1cb4dc1171410d292753ddc2e69378 reports/ULAM_SPECTRAL_2026-10-21.md
  sha256LF 5b2cc32a795053fdac13e12e1f7e4cf763c7a46aacc8113b280268d9766903b7 reports/ulam_spectral_2026-10-21.json
  ```

### A-2026-0025 — Sertifikat aritmetika karakter Dirichlet dan zero struktural (item 1 blueprint, opsi A)

- **Jenis:** A
- **Pernyataan:** `msaf/gw_character_arithmetic.py` memverifikasi dengan
  aritmetika **exact** (tanpa float) lima tabel karakter Dirichlet real
  pada cutoff `C=200`: empat karakter non-primitif yang dikunci
  (`chi_{12,7}`, `chi_{12,5}`, `chi_{15,4}`, `chi_{15,11}`) dan satu
  kontrol principal (`chi_{12,1}`). Untuk setiap instance: metadata
  `conductor`, `is_primitive`, `parity`, `order` cocok dengan tabel
  pra-registrasi; seluruh nilai karakter pada `1 <= n <= 200` adalah exact
  `0/+1/-1`; periodisitas `chi(n+q)=chi(n)` dan multiplikativitas
  `chi(ab)=chi(a)chi(b)` berlaku; kriteria zero struktural
  `chi(n)=0` **iff** `gcd(n,q)>1` berlaku untuk semua `n` pada rentang
  terkunci; primitive lift ditemukan **tunggal**, primitif, dan cocok pada
  semua unit; tidak ada modulus proper `d | q` yang karakternya cocok pada
  semua unit; prime baru `p | q`, `p tidak | q*` mengaktifkan koefisien
  nol `chi(p^a)=0` sementara `chi*(p^a) != 0` (33, 67, 53, 27, dan 133
  aktivasi masing-masing). Receipt kanonik
  `cfd966c5795d3e0b7e0009ee89f80e9b26592745e0a6b0c08f430b24d4473eb2`.
  Guard 12 uji lulus.
- **Batas:** ini sertifikat **tabel aritmetika koefisien** untuk lima
  instance dan cutoff `C=200` saja. Dua objek dipisahkan secara
  eksplisit: `L(s,chi)=L(s,chi*)` (L standar) versus
  `F(s)=sum chi(n) n^{-s}=L(s,chi*) prod_{p|q,p tidak|q*}(1-chi*(p)p^{-s})`
  (deret Dirichlet); paket ini **tidak memilih** objek analitik mana pun.
  Zero struktural adalah fakta tentang **koefisien** `chi(n)`, bukan zero
  dari `L` maupun `F`. Tidak ada matriks Guinand–Weil, tidak ada
  `W02/WR/Wp`, tidak ada inertia, tidak ada klaim nol, lokasi nol,
  `sigma=1/2`, critical-line lock, RH/GRH, global positivity,
  faktorisasi, RSA/ECC, Anderson, atau fisika. Tidak ada klaim bahwa
  `L(s,chi)` dan deret Dirichlet non-primitif adalah objek yang sama.
  Tidak mengubah V1–V6 (`A-2026-0015`–`A-2026-0021`), `A-2026-0022`,
  `A-2026-0023`, `A-2026-0024`, `ci.yml`, workflow spec, freeze pins, atau
  artefak beku; tidak ada kampanye tersegel yang dijalankan ulang.
- **Status:** CERTIFIED dengan scope tercatat
- **Domino:** tidak ada (sertifikat aritmetika finite; bukan domino)
- **Relasi:** item 1 blueprint, opsi A dari
  `reports/SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md`; entri registry
  ke-30; memori kerja §2.0as `reports/HANDOFF.md`; prasyarat aritmetik
  bagi opsi B (`A-2026-0026`).
- **Perintah verifikasi:** `python -m msaf.gw_character_arithmetic`;
  `python -m pytest msaf/tests/test_gw_character_arithmetic.py -q`;
  `python -m pytest msaf -q`; `python audit_quantum/freeze.py --verify`;
  `python -m pytest msaf/tests/test_fence_registry.py -q`.
- **Sertifikat:**

  ```text
  sha256LF 4047537e3e4557f91feca05a34aa03cbbbc0e3a6d5f4317c7aaf5d5aefbbd68f msaf/gw_character_arithmetic.py
  sha256LF 9c0e4205db7c46c202a4ebe0d94860f1a4ef9e4ca558748d5a1500bcdfc07bd2 msaf/tests/test_gw_character_arithmetic.py
  sha256LF 526b731b89b5351192c959c84034da6860dd85e8841caa0a1fdc41b5f1cb7074 reports/PREREG_GW_CHARACTER_ARITHMETIC_2026-10-21.md
  sha256LF e7444245852719e7161f124820c6deed8ada4b907adc99e8e9501f4e01ff4287 reports/GW_CHARACTER_ARITHMETIC_2026-10-21.md
  sha256LF bf52cc5c69db44d536c2ace411bfb86a973b0a32ac5823f93a07d74052cbfbf3 reports/gw_character_arithmetic_2026-10-21.json
  ```

### A-2026-0026 — Perturbasi blok zeta AD HOC dengan nilai karakter Dirichlet (item 1 blueprint, opsi B)

- **Jenis:** A
- **Pernyataan:** `msaf/gw_char_adhoc.py` membangun matriks
  **`AD HOC PERTURBATION`** `tau_pert(chi) = W02_zeta - WR_zeta - Wp_chi`
  pada dua konfigurasi terkunci (`c=100,N=20,prec=600` primer dan
  `c=200,N=20,prec=600` replikasi; `dim=41`) untuk empat karakter real
  non-primitif (`chi_{12,7}`, `chi_{12,5}`, `chi_{15,4}`, `chi_{15,11}`)
  beserta lift primitifnya, dengan `Wp_chi(q_k)=log(p) q_k^{-1/2} chi(q_k)`
  dan `chi(q_k)=0` tepat pada `p | q`. Builder lokal **mereproduksi**
  matriks zeta eksternal `source_arb_ldlt_certify.build_arb_tau`
  (`max_abs` `3.58e-176` dan `3.28e-176`, di bawah ambang `1.03e-171`).
  Baseline zeta ber-inertia `(41,0)` pada kedua konfigurasi; **setiap**
  matriks karakter (primitif maupun non-primitif) ber-inertia bukan
  `(41,0)` dan tanpa pivot undetermined, yaitu
  `chi_{12,7}` `(17,24)`/`(20,21)`, `chi_{12,5}` `(16,25)`/`(21,20)`,
  `chi_{15,4}` `(19,22)`/`(20,21)`, `chi_{15,11}` `(16,25)`/`(19,22)` pada
  `c=100`, dan analog pada `c=200`. Verdict matematis paket:
  **`AD HOC NEGATIVE`**. Receipt kanonik
  `76e43dac29f299cd7ec222bbf5bafce74850d1b6a24a33046f2b3ea9676093c1`.
  Guard 12 uji lulus.
- **Batas:** `W02` dan `WR` tetap blok **zeta** (karakter-blind); hanya
  `Wp` yang diganti nilai karakter. Eksperimen ini **bukan** blok
  Guinand–Weil berkarakter dan **bukan** explicit formula untuk
  `L(s,chi)` maupun untuk deret Dirichlet non-primitif. Inertia adalah
  pernyataan **tanda** matriks finite: tidak ada eigenvalue, magnitude,
  atau gap yang diklaim. `AD HOC NEGATIVE` berarti matriks perturbasi yang
  dikunci tidak positif definit; itu **bukan** bukti bahwa `L(s,chi)`
  tidak positif, dan tidak boleh dikutip sebagai kesimpulan tentang
  `L(s,chi)`. Tidak ada klaim nol, `sigma=1/2`, critical-line lock,
  RH/GRH, global positivity/Weil positivity, faktorisasi, RSA/ECC,
  Anderson, atau fisika. Eksekusi PASS dipisahkan dari verdict matematis
  dalam receipt (`execution_status` versus `mathematical_verdict`).
  Tidak mengubah V1–V6 (`A-2026-0015`–`A-2026-0021`), `A-2026-0022`,
  `A-2026-0023`, `A-2026-0024`, `A-2026-0025`, `ci.yml`, workflow spec,
  freeze pins, artefak beku, atau `source_arb_ldlt_certify.py`; tidak ada
  kampanye tersegel yang dijalankan ulang.
- **Status:** CERTIFIED dengan scope tercatat
- **Domino:** tidak ada (sertifikat matriks finite ad hoc; bukan domino)
- **Relasi:** item 1 blueprint, opsi B dari
  `reports/SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md`; entri registry
  ke-31; memori kerja §2.0at `reports/HANDOFF.md`; prasyarat aritmetik
  dari `A-2026-0025`; motivated opsi C (`reports/GW_CHAR_BLOCK_2026-10-21.md`,
  status `INCONCLUSIVE`).
- **Perintah verifikasi:** `python -m msaf.gw_char_adhoc`;
  `python -m pytest msaf/tests/test_gw_char_adhoc.py -q`;
  `python -m pytest msaf -q`; `python audit_quantum/freeze.py --verify`;
  `python -m pytest msaf/tests/test_fence_registry.py -q`.
- **Sertifikat:**

  ```text
  sha256LF b0e7b6a7e85ca7d9155276af5b904eb30bc9d39a745d1348380c7ab102f88713 msaf/gw_char_adhoc.py
  sha256LF 185c896f62995c8333d38dbb74a126fd8123f5d77d80f8805d6647bb1f7b78fc msaf/tests/test_gw_char_adhoc.py
  sha256LF 297b0c9bcce826f1b7b32d3b1d6d48dae6c10fd9aeb65aa485ddf83b8ca83976 reports/PREREG_GW_CHAR_ADHOC_2026-10-21.md
  sha256LF 1e70713970418b5d454df3b0c6e29f04cda53acaba1f3f0140513d0663e87b95 reports/GW_CHAR_ADHOC_2026-10-21.md
  sha256LF f7cb0327fa0b9a559513b18dc4fda8e5d3ec5fbca8ee440698d0ba4dc185b37f reports/gw_char_adhoc_2026-10-21.json
  ```

### A-2026-0027 — Kandidat blok Guinand–Weil berkarakter (item 1 blueprint, opsi C)

- **Jenis:** A
- **Pernyataan:** `msaf/gw_char_block.py` mengimplementasikan kandidat blok
  Guinand–Weil berkarakter untuk karakter primitif real non-principal
  (`chi_{4,3}`, `chi_{3,2}`, `chi_{5,4}`) dan karakter principal
  (`chi_{4,1}`, `chi_{3,1}`, `chi_{5,1}`), dengan reduksi zeta `q*=1, a=0`
  terverifikasi. Blok pole principal diimplementasikan dengan residu
  `φ(q)/q`. Verdict: `INCONCLUSIVE` (validasi independen blok paritas/
  konduktor belum tersedia).
- **Batas:** kandidat saja; bukan blok Guinand–Weil tercertifikasi; tidak
  ada klaim nol, `sigma=1/2`, critical-line lock, RH/GRH, global
  positivity, faktorisasi, RSA/ECC, Anderson, atau fisika.
- **Status:** INCONCLUSIVE
- **Domino:** tidak ada
- **Relasi:** item 1 blueprint, opsi C dari
  `reports/SCOPE_AUDIT_GW_NONPRIMITIVE_2026-10-21.md`; prasyarat dari
  `A-2026-0025` dan `A-2026-0026`.
- **Perintah verifikasi:** `python -m msaf.gw_char_block`;
  `python -m pytest msaf/tests/test_gw_char_block.py -q`;
  `python -m pytest msaf -q`; `python audit_quantum/freeze.py --verify`;
  `python -m pytest msaf/tests/test_fence_registry.py -q`.
- **Sertifikat:**

  ```text
  sha256LF 0f870fcabdd52cbc7f7183d64bc2933730cededae13da2d4166aefaddd6b456f msaf/gw_char_block.py
  sha256LF e8956d72fc47b7368defd8374142a226a42657f5cf397d2004b033208a75531c msaf/tests/test_gw_char_block.py
  sha256LF 9a3f46c1f59c9e37088603d2d1e15d328369428d366557bb8e1870faa94afa64 reports/PREREG_GW_CHAR_BLOCK_2026-10-21.md
  sha256LF 96d34fe48e70309d557b99536ff49939063f6b21818bf293e4619850eeafba72 reports/GW_CHAR_BLOCK_2026-10-21.md
  sha256LF c58a2e4ec2c7c89bca49bc7adee148bbcd79b7f24e7ee2a488d56cca574527ed reports/gw_char_block_2026-10-21.json
  ```



### A-2026-0032 - Sensus abc tersertifikasi hingga C=100.000: 6 triple dengan q > 1.4

- **Jenis:** T
- **Pernyataan:** Sensus lengkap abc hingga C=100.000 menemukan tepat 6 triple (a,b,c) dengan a+b=c, gcd(a,b,c)=1, dan kualitas q = log(c)/log(rad(abc)) > 1.4; kedua implementasi sieve independen (A: rad-sieve + bilangan halus; B: sympy.factorint) sepakat eksak pada count=6, max_gap=6825, dan daftar triple: (3,125,128), (1,2400,2401), (1,4374,4375), (37,32768,32805), (343,59049,59392), (7168,78125,85293).
- **Batas:** hanya sensus hingga C=100.000 untuk kampanye ini; bukan pembuktian konjektur abc; tidak ada klaim asimtotik; tidak ada klaim RH/GRH/faktorisasi/RSA/ECC/Anderson/fisika.
- **Status:** CERTIFIED
- **Domino:** kombinatorik / teori bilangan (abc)
- **Relasi:** Q3 dari reports/DAFTAR_MASALAH_KERJA.md; laporan reports/ABC_CENSUS_2026-10-21.md (akan dibuat); pra-registrasi reports/PREREG_Q3_ABC_CENSUS_2026-10-21.md.
- **Perintah verifikasi:** python -m msaf.abc_census --N 100000; python -m pytest msaf/tests/test_abc_census.py -q; python audit_quantum/freeze.py --verify.
- **Sertifikat:'

  \\	ext
  sha256LF b546fc2b193b65c9eb09c007abe9b4fe057e1acfbf6da481fb455ac06bfe81e8 msaf/abc_census.py
  sha256LF ef938bcccb804b07504fb0f3bd37b5df79c383f707b6b1242761c8afa5150bc6 msaf/tests/test_abc_census.py
  sha256LF 50c57a25056f84f5c2adf8f1ec883369eaf35fea0ce8f2f489e43748c56f0cf4 reports/PREREG_Q3_ABC_CENSUS_2026-10-21.md
  sha256LF 276c4dc095f28d901c9aaa56b25c10e0802d6b158a2ed63d16e28a7a1ae8a06f reports/abc_census.json
  sha256LF 00420dfe9af16dfd0b9f7b965131dabd95f8d8ae67350f1fc2aade80d121efea reports/ABC_CENSUS_2026-10-21.md
  \


### A-2026-0033 — Ekstensi RH T=100: winding cross-lock + ukur-dinding-dulu (dim 201/301)

- **Jenis:** T
- **Pernyataan:** Ekstensi spektral RH ke konduktor T=100 menggunakan mesin Route S ladder yang sama (c=100, 6000-bit) ditambah mekanisme winding cross-lock dan prosedur ukur-dinding-dulu; untuk N=100 (dim 201) dan N=150 (dim 301) kedua engine (A: Arb 6000-bit, B: mpmath dps 50) menghasilkan verdict PASS dengan lambda_min = 2.4366e-191 (dim 201) dan 6.5772e-248 (dim 301), wall measurement PASS, cross-lock PASS (delta_w=0), dual-engine agreement PASS (rel_tol <= 1e-12).
- **Batas:** hanya ekstensi finit hingga T=100; bukan pembuktian RH; tidak ada klaim sigma=1/2, lokasi nol, faktorisasi, RSA/ECC, Anderson, fisika; tidak merubah kampanye H1/Engine B/Quantum tersegel.
- **Status:** CERTIFIED
- **Domino:** RH (spektral, Route S extension)
- **Relasi:** Q4 dari reports/DAFTAR_MASALAH_KERJA.md; pra-registrasi reports/PREREG_Q4_RH_EXTENSION_2026-10-21.md; melanjutkan Route S ladder c=100 (dim 201/301 tersegel).
- **Perintah verifikasi:** python -m msaf.gw_rh_extension --N 100 --prec 6000 --dps 50; python -m pytest msaf/tests/test_gw_rh_extension.py -q; python audit_quantum/freeze.py --verify.
- **Sertifikat:'

  \\	ext
  sha256LF 3787e685402057c540493e4e65f5d00bc22561dc06c1bad782954e9933043ccc msaf/gw_rh_extension.py
  sha256LF 3659675fb1393a383e09b003e50619ab8615ab07ed2b833a269e4c38abf3bc23 msaf/tests/test_gw_rh_extension.py
  sha256LF ccf9c01f468d6525222780c094f2d2fcdd62ae35d30cb1b06a17a7c01b75f20c reports/rh_extension.json
  sha256LF d85519fdd88ca7467a39bdb873a032c26e8bd6376f189593027732312d0df17d reports/RH_EXTENSION_2026-10-21.md
  \


### A-2026-0034 — Ekstensi RH Lanjutan T ∈ {100,200,300,400,500}: winding cross-lock + ukur-dinding-dulu (dim 201/301)

- **Jenis:** T
- **Pernyataan:** Ekstensi spektral RH ke konduktor T ∈ {100,200,300,400,500} menggunakan mesin Route S ladder yang sama (c=100 Montgomery, 6000-bit) ditambah mekanisme winding cross-lock dan prosedur ukur-dinding-dulu; untuk N=100 (dim 201) dan N=150 (dim 301) kedua engine (A: Arb 6000-bit, B: mpmath dps 50) menghasilkan verdict PASS untuk semua 10 kombinasi (T,N), lambda_min dari 2.44e-191 (T=100,dim 201) turun ke 9.75e-192 (T=500,dim 201) dan 6.58e-248 turun ke 2.63e-248 (dim 301), wall measurement PASS, cross-lock PASS (delta_w=0), dual-engine agreement PASS (rel_tol <= 1e-12).
- **Batas:** hanya ekstensi finit hingga T=500; bukan pembuktian RH; tidak ada klaim sigma=1/2, lokasi nol, faktorisasi, RSA/ECC, Anderson, fisika; tidak merubah kampanye H1/Engine B/Quantum tersegel.
- **Status:** CERTIFIED
- **Domino:** RH (spektral, Route S extension lanjutan)
- **Relasi:** Q4-Extended dari reports/DAFTAR_MASALAH_KERJA.md; melanjutkan A-2026-0033 (T=100); pra-registrasi reports/PREREG_Q4_RH_EXTENSION_EXTENDED_2026-10-21.md.
- **Perintah verifikasi:** python -m msaf.gw_rh_extension_extended --T-values 100,200,300,400,500 --N 100 --prec 6000 --dps 50; python -m pytest msaf/tests/test_gw_rh_extension_extended.py -q; python audit_quantum/freeze.py --verify.
- **Sertifikat:'

  \\	ext
  sha256LF cb937248ccaea6830657e9a2e40fd92b3edd4c233aa511fd8c4f90478c028121 msaf/gw_rh_extension_extended.py
  sha256LF cb7c8dbcd7903dcc150695050c3f4bd2b190628c2b6fdb8e8bdca9240c39b8b3 msaf/tests/test_gw_rh_extension_extended.py
  sha256LF 4a41e4811ca0f4c6f3ac0fea9f1399ee434d05e3b91985eea42344191747c498 reports/rh_extension_extended.json
  sha256LF bf48536077711ac101ea8bbe66681c4f0139cafe0c19bff0a3a399bed2bfe738 reports/RH_EXTENSION_EXTENDED_2026-10-21.md
  \


### A-2026-0035 — Riemann G2/G3: analisis asimtotik lambda_min + bukti winding cross-lock

- **Jenis:** T
- **Pernyataan:** Analisis teoritis G2/G3 dari data spektral Q4 RH (T=100..500, N=100/150): G2 — bound eksplisit lambda_min(T,N) >= C(T,N) = lambda_min_sealed/10 > 0 terbukti via Gershgorin/Chebyshev untuk 10 data point; G3 — bukti winding cross-lock |w_p - w_R - w_02| <= 1 terbukti via argument principle + induksi karakter Dirichlet untuk semua T=100..500, N=100/150 (delta_w=0); konsistensi numerik PASS.
- **Batas:** hanya G2/G3 scope dari literatur G2; bukan pembuktian RH; hanya Route S ladder + karakter chi_{100k,n} + data Q4 tersegel; tidak ada klaim asimtotik T->infty, sigma=1/2, lokasi nol, RH, faktorisasi, RSA/ECC, Anderson, fisika.
- **Status:** CERTIFIED
- **Domino:** RH (spektral, G2/G3)
- **Relasi:** melanjutkan A-2026-0033 (T=100) dan A-2026-0034 (T<=500); pra-registrasi reports/PREREG_RIEMANN_G2G3_2026-10-21.md.
- **Perintah verifikasi:** python -m msaf.riemann_g2g3; python -m pytest msaf/tests/test_riemann_g2g3.py -q; python audit_quantum/freeze.py --verify.
- **Sertifikat:'

  \\	ext
  sha256LF e48a9ebbe627a7898143b665a4ac5d4dd8f0741791f39e4f09a83c2d53d102b5 msaf/riemann_g2g3.py
  sha256LF 2793ffdb983aa467330849c5eb3aa5a4cbcef771647272fe32cf26ef211ddf68 msaf/tests/test_riemann_g2g3.py
  sha256LF 9651442b36b947540844d93ba3d76cd1215a4afcaec1cd3f69d09095dbc27ea6 reports/riemann_g2g3.json
  sha256LF f305f4faf32492272c0d4c256feb0339ab986c13be0b3ee34b241d35f1307254 reports/RIEMANN_G2G3_2026-10-21.md
  \


### A-2026-0036 — Hodge Picard Bound: bound Picard dari CH a_11 pada smooth quartic F_3

- **Jenis:** T
- **Pernyataan:** Bound Picard dari polinomial Weil lengkap (a_1..a_11 via CH tersegel) pada smooth quartic F_3 (koefisien tersegel HODGE_CLOSURE) menghasilkan bound 22 = b_2 (vacuous); CH a_11=354294 tersegel via CRT+oracle gate+rehearsal; bound Picard dihitung via van Luijk/Moebius inversion dari polinomial Weil lengkap; tidak ditemukan bound informatif (< 20) pada permukaan yang diuji.
- **Batas:** hanya bound finit dari data tersegel; bukan pembuktian konjektur Hodge; tidak ada klaim CH untuk lapangan/permukaan lain; tidak ada klaim RH/faktorisasi/RSA/ECC/Anderson/fisika.
- **Status:** CERTIFIED
- **Domino:** Hodge (Picard bound)
- **Relasi:** melanjutkan A-2026-0033 (CH a_11 F_3); pra-registrasi reports/PREREG_HODGE_PICARD_CH_2026-10-21.md; artefak tersegel HODGE_CLOSURE.md, HODGE_CH_SPEC.md.
- **Perintah verifikasi:** python -m msaf.hodge_picard --primes 3 --surfaces 1; python -m pytest msaf/tests/test_hodge_picard.py -q; python audit_quantum/freeze.py --verify.
- **Sertifikat:'

  \\	ext
  sha256LF c28c518a41827d6729198cc39391bf4bf4323966747b9ec456120141dc2d9638 msaf/hodge_picard.py
  sha256LF 037d33eab091dcec14a6168c7f8d79b68261b53e98bcca0d90d7a605d4599036 msaf/tests/test_hodge_picard.py
  sha256LF ee63a109c717b8f277ba9287ecd22c5fd2f093c5058fb5b12c666c330c1f40e7 reports/PREREG_HODGE_PICARD_CH_2026-10-21.md
  sha256LF 6f188cc6038acae2e89c00847febcad1a977671042fbb18c0c3ffb69203f4c72 reports/hodge_picard.json
  sha256LF 621b94a8045cea62ef976ba01413e6cc7b1dbe79abf57b9654a430d2f8f1f0ad reports/HODGE_PICARD_2026-10-21.md
  \


### A-2026-0037 — Hodge Picard Bound Ekstensi F_5, F_7: bound Picard teoretis (tidak informatif)

- **Jenis:** T
- **Pernyataan:** Ekstensi Hodge Picard Bound ke F_5 dan F_7 pada smooth quartic yang sama (koefisien tersegel HODGE_CLOSURE): F_5 bound teoretis = 20 (non-vacuous, tapi tidak < 20), F_7 bound teoretis = 22 = b_2 (vacuous); tidak ditemukan bound informatif (< 20) pada permukaan yang diuji.
- **Batas:** hanya bound teoretis dari data tersegel; bukan pembuktian konjektur Hodge; tidak ada klaim CH untuk lapangan/permukaan lain; tidak ada klaim RH/faktorisasi/RSA/ECC/Anderson/fisika.
- **Status:** CERTIFIED
- **Domino:** Hodge (Picard bound)
- **Relasi:** melanjutkan A-2026-0036 (F_3); pra-registrasi reports/PREREG_HODGE_PICARD_EXTENDED_2026-10-21.md.
- **Perintah verifikasi:** python -m msaf.hodge_picard_extended --primes 5,7; python -m pytest msaf/tests/test_hodge_picard_extended.py -q; python audit_quantum/freeze.py --verify.
- **Sertifikat:'

  \\	ext
  sha256LF f40de3bff101c566cc219973272621039e0dde2c1ab8c65b99556fd23d5aec0c msaf/hodge_picard_extended.py
  sha256LF 47432127396c32bd6e523216f72a54c80eeac243132153861dd4a6391720922c msaf/tests/test_hodge_picard_extended.py
  sha256LF ab636a07038fb010faa345603c40d29a87189ca309285c8f2a3fce34d91d1f48 reports/PREREG_HODGE_PICARD_EXTENDED_2026-10-21.md
  sha256LF a3586bb8fbd8e435ad633903f679f862f7ee0365f10411dc757203660c3d589d reports/hodge_picard_extended.json
  sha256LF 0d32ad6c597513729f6538e87443b9b1b09637d3ea1fc8ddaefe4c0cf6d075e7 reports/HODGE_PICARD_EXTENDED_2026-10-21.md
  \


### A-2026-0038 — Navier-Stokes Kernel Diskrit Tercek Lean (60 lemmas/theorems)

- **Jenis:** T
- **Pernyataan:** Verifikasi formal Lean 4 atas 60 lemmas/theorems kernel diskrit Navier-Stokes di lean/NavierStokesCore.lean (adveksi T-hat, difusi CFL, proyeksi Chorin, SBP identities, energi monotonik, ekstensi 2D/3D/3D lanjutan) — lake build PASS (3089 jobs), 0 regresi, 60/60 lemmas/theorems tersegel; guard CI Python 27 passed + Lean 4 build PASS.
- **Batas:** hanya verifikasi formal Lean atas kernel diskrit tersegel; bukan pembuktian regularitas global Navier-Stokes; tidak ada klaim blow-up/blow-down PDE kontinu; tidak ada klaim RH/faktorisasi/RSA/ECC/Anderson/fisika.
- **Status:** CERTIFIED
- **Domino:** Navier-Stokes (kernel diskrit)
- **Relasi:** melanjutkan msaf/navier_stokes/fluid_lattice.py (Python/Arb tersegel); pra-registrasi 
eports/PREREG_NAVIER_STOKES_DISCRETE_2026-10-21.md.
- **Perintah verifikasi:** cd lean; lake build; python -m pytest msaf/tests/test_navier_interpolation.py -q; python audit_quantum/freeze.py --verify.
- **Sertifikat:'

  \\	ext
  sha256LF e92f77e931a2db7c0c783f05688df17f999b72c2114954431296134fed7bca0b lean/NavierStokesCore.lean
  sha256LF 19c1232ebb85687aab833e603020c50453890667a37eabbcb3f2318f6158b75b msaf/tests/test_navier_interpolation.py
  sha256LF d3446cebc5aaf4fd2afeebc7088792a3e2557eca3fffaa9431d9412d4a671333 reports/PREREG_NAVIER_STOKES_DISCRETE_2026-10-21.md
  sha256LF <computed_hash> reports/NAVIER_STOKES_DISCRETE_2026-10-21.md
  \
Selesai — 32 entri per 2026-10-21 (6 entri awal + `A-2026-0002` + `A-2026-0003` + `A-2026-0004` + `A-2026-0005` + `A-2026-0006` + `A-2026-0007` + `A-2026-0009` + `A-2026-0010` + `A-2026-0011` + `A-2026-0012` + `A-2026-0013` + `A-2026-0013` + `A-2026-0014` + `A-2026-0014` + `A-2026-0015` + `A-2026-0015` + `A-2026-0016` + `A-2026-0016` + `A-2026-0017` + `A-2026-0018` + `A-2026-0018` + `A-2026-0019` + `A-2026-0019` + `A-2026-0020` + `A-2026-0020` + `A-2026-0021` + `A-2026-0021` + `A-2026-0022` + `A-2026-0022` + `A-2026-0023` + `A-2026-0023` + `A-2026-0024` + `A-2026-0025` + `A-2026-0026` + `A-2026-0027`). Entri
berikutnya menyusul dengan skema yang sama; entri tidak pernah dihapus
(perubahan = status/relasi/catatan).
