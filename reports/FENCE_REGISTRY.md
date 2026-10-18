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
  ```

Selesai — 7 entri per 2026-10-18 (6 entri awal + `A-2026-0002`). Entri
berikutnya menyusul dengan skema yang sama; entri tidak pernah dihapus
(perubahan = status/relasi/catatan).
