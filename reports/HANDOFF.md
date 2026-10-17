# HANDOFF — titik sambung untuk sesi berikutnya

Ditulis 2026-10-15, akhir sesi repo-audit + Zenodo.
**Update 2026-10-16:** resolusi kedua (dim 201) dan ketiga (dim 301) diukur;
sensor CI diperbaiki di akar; jawaban "mengecil atau membesar" di §2.0b dan
`reports/THREE_TASKS_2026-10-15.md` §4 + §5 (seri tiga titik 201/301/401,
dashboard `reports/gw_diagnostic_v3.html`; README §6 memuat peta jalan
kampanye + rumus instrumen lengkap). **Konsolidasi 2026-10-16:** manuskrip
`exports/research_paper.tex` (Main Spectral Results + register cacat,
transkripsi artefak tersegel saja) ditambahkan; dashboard v3 diuji ulang
byte-stabil; delivery akhir ditandai tag `v1.40.0-alpha-final-certified-delivery`. **H0 lockdown (2026-10-16):** `docs/ZENODO_ACTIVATE.md` (panduan aktivasi webhook Zenodo) + template release + pra-registrasi amandemen lantai `reports/AMENDMENT_FLOOR_SPEC.md` (DIBEKUKAN, sha256 di §1) disegel; TIDAK ada komputasi baru dijalankan. **Deposit + release (2026-10-16):** delivery T-hat-N diamankan sebagai VERSI BARU record Zenodo via depositor API — DOI versi `10.5281/zenodo.23410894` (konsep `10.5281/zenodo.23338271`; arsip tarball commit `a37b50b`, sha256 `44bdfb87...`); release GitHub `v1.40.0-alpha-final-certified-delivery` diterbitkan via `gh`; skrip depositor diperluas (`--date`/`--version`, commit `3305221`). **H1 amandemen lantai (2026-10-16):** bagian (A)+(B) dari `reports/AMENDMENT_FLOOR_SPEC.md` (DIBEKUKAN) dieksekusi penuh — grid refined 20000 surrogat + array robustness C4 5-seed; hasil terukur, klasifikasi beku (NOT STABLE), dan falsifikasi ekspektasi pra-registrasi di §2.0c dan `reports/AMENDMENT_FLOOR_RESULTS.md`; manuskrip `exports/research_paper.tex` diamandemen bertanggal (section sebelum register cacat + pointer abstrak + catatan header). (C) engine B = sesi berikutnya. **H1 (C) engine B SELESAI (2026-10-17):** verifikasi independen S2 run penuh 20000 sampel — verdict `PASS-WITH-ENUMERATED-EXCEPTIONS`, counts 18/18 eksak vs engine A (exit 0, 9062 s); log + JSON tersegel di repo, riwayat interupsi R1/R2 di `reports/ENGINE_B_PILOT_FINDINGS_2026-10-16.md`, rincian §8 `reports/AMENDMENT_FLOOR_RESULTS.md`. **README publikasi (2026-10-17):** README.md diperbarui — banner terbaru penutupan H1, Section 7 baru (peta alur kerja + rantai verifikasi + blok status mesin + "verify it yourself"); blok status dan 2 diagram SVG digenerate `msaf/gw_readme.py` HANYA dari artefak tersegel (hash + byte-count LF-normalised), dijaga `msaf/tests/test_readme_guard.py` (drift = CI merah); commit `90a6520`, perbaikan byte-count checkout-stable `c957503` (run pertama `38975016984` GAGAL — kolom bytes pakai st_size mentah, CRLF vs LF CI; diperbaiki di akar + disimulasikan di worktree LF lokal); CI hijau run `38975450198`; suite 345 passed. **Dashboard v5 (2026-10-17):** halaman v5 dibangun DI ATAS v4 byte-identik (v4 disegel sebagai preserved — sha256 penuh di panel 6 v5 + dipin `msaf/tests/test_gw_dashboard_v5.py`); 14 patch deterministik terdokumentasi + 1 patch koreksi radius/leak float64 2026-10-17 (total 15; laporan `reports/GW_RADIUS_REGISTRY_CORRECTION_2026-10-17.md`) + 2 panel baru (Panel 7: grid refined H1 + array 5-seed dengan grafik seed baru; Panel 8: census 720 bin engine B + counts 18/18 eksak + provenance); semua angka diekstrak mesin saat build; commit `2d7b72c`, CI hijau run `38992695849`; suite 349 passed. Koreksi radius/leak float64 2026-10-17: commit `6304599`, CI hijau run `38995193745`. **Tangga λ_min diperpanjang (2026-10-17):** rung dim 321 (N=160, c=13, 6000 bit) terukur CERTIFIED — λ_min = `3.123458832662237e-59` (eig 3110,88 s; build 199,9 s), λ_max = `6.113965017866562`; lereng 257→321 = −0,000854 (ratio 0,9468 per 64 dim — masih mengecil, terus melandai, belum ada upturn); artefak `reports/lambda_min_eig_ladder_dim321.json` (LF sha256 `e92e05ef8d37b10bb3e39c65e7537e23c8e3a426da548028a0a560126b60b696`) + log; laporan `reports/GW_LADDER_DIM321_2026-10-17.md`; commit `9ce44be` + baris ini; CI hijau run `38999210393`.
**C4 S10 (2026-10-17):** array robustness C4 diperluas 5 → 10 seed di bawah pra-registrasi beku (`reports/C4_SEEDS10_PREREG_2026-10-17.md`, commit `657352c`, dipush sebelum draw pertama; ordering PASS) — pooled `11458/200000` = 5.72900e-02 (CP95 [5.62754e-02, 5.83174e-02]); homogenitas chi2 = 131.2879 (df 9), p = 6.44376e-24 → **NOT STABLE (dispersion-dominated) bertahan**; angka of record TIDAK berubah (`1262/20000` = 6.31000e-02). Insiden CI dicatat: run pertama `39019056454` GAGAL karena tes kesetaraan float bit-exact lintas platform (scipy beta.ppf ~1 ULP; semua count/label identik) — diperbaiki di akar di tes (float rel_tol = 1e-12, int/string eksak) di commit `15f767f`; CI hijau `39019664353`; rincian `reports/C4_SEEDS10_RESULTS_2026-10-17.md`.

**Resolusi ke-4 (dim 501) — OUTCOME (2026-10-17):** pra-registrasi
`reports/RESOLUTION4_DIM501_PREREG_2026-10-17.md` (commit `ea2ed77`, dipush
+ CI hijau `39020789629` sebelum launch; ordering PASS). Ladder Route S
6000 bit (c=100, N=250 → dim 501) mencetak `UNDETERMINED at pivot 446`
(n_pos=446, n_neg=0; 0 certified) — non-PD, maka sesuai pra-registrasi §4
statistik titik keempat **BERAKHIR di ladder** (Stage C/M tidak dijalankan;
tidak ada angka S1/S2 untuk dim 501). Insiden wrapper dicatat &
di-root-cause: `Start-Process -PassThru` + `.WaitForExit()` mengembalikan
`ExitCode` kosong di PS 5.1 → launcher salah-branch ke ABORT; komputasi
TIDAK terpengaruh (runner selalu exit 0, artefak lengkap, segel seri lama
utuh). Laporan: `reports/GW_RESOLUTION4_DIM501_2026-10-17.md`; detail §2.0e.
Gate pra-registrasi audit P1 kini TERBUKA (C4 + 501 keduanya tertutup).

**P1 audit — pra-registrasi DIBEKUKAN (2026-10-17):**
`reports/AUDIT_DBN_PREREG_2026-10-17.md` (commit `86a32c9`, CI hijau
`39024004135`) — target beku rilis `review-01787854-v3` (commit
`2e9976c4...`, OCI digest `6e29bc53...`; BUKAN HEAD bergerak), level
L1–L4 + kriteria verdict + coverage + cap anggaran. Temuan lingkungan
(tercatat sebelum eksekusi): mesin ini TIDAK punya engine container
(docker/podman absen; WSL2 tanpa distro) → L1 conditional (jika tak ada
engine saat attempt → NOT-RUN-ENVIRONMENT; L2/L3 tetap jalan) —
mengaktifkan engine = keputusan pemilik. Urutan eksekusi beku: §2.0f.
**Anchor baseline:** tag git `baseline-2026-10-17` (commit `8038243`,
CI `39025604163` hijau) — titik pulih bila ganti sesi / listrik padam.

**P1 audit — eksekusi L2 (2026-10-17):** L1 = NOT-RUN-ENVIRONMENT (tanpa
engine container; `reports/audit_p1_l1_launch.log`, commit `20a77c8`).
Gate Lean anti-circularity PASS 25/25 (catatan mesin: rilis memuat 0
berkas `.lean`; gate dijalankan atas `lean/` commit pasca-rilis terpin
`a74738de` berlabel AUXILIARY; diskrepansi → coverage L4; log + attempt1,
commit `ad4755c`). L2 item 1 SELESAI 34/34 (commit `de4d686`, CI
`39033622304`). L2 item 2 SELESAI — Prop 4.10 budget 48/48: e_A+e_B ≤
8.7446e-13 ≤ sealed 2.057e-12 (gap ≥ 1.18256e-12); e_C,0 ≤ sealed dengan
gap ≥ 3.20854e-25 (kasus batas 24 dp dicatat); E_max ≤ sealed; margin ≥
sealed → verdict REPRODUCED; artefak `audit_p1/l2_prop410_budget.py` +
log + JSON + 3 transkrip smoke (commit bersama baris ini). **L2 item 3
SELESAI — tail lane 47/47 PASS (REPRODUCED):** koridor dua sisi
(`D_lb − 0.999719 ≥ 4.7893e-7`, `0.999721 − D_ub ≥ 9.0620e-8`),
`flow_lo − sealed ≥ 5.47846e-12`, `sealed − err_ub ≥ 1.41081e-15`,
`margin_lo − sealed ≥ 5.47937e-12`, `Mmax_ub < 1.608290`; artefak
`audit_p1/l2_tail_budget.py` + log resmi + JSON + 4 transkrip smoke
(2 gagal, dicatat). **L2 item 4 SELESAI — barrier subset 124/124 PASS
(REPRODUCED level-descriptor):** gate `M_i > D_z,i/(2(num−1)) +
D_t,i·dt_i + 1/800` eksak untuk 883/883 prisma; subset K=8 margin
terkecil (#875–#882) + seam + first/last; minimum margin re-komputasi
eksak = klaim sealed `0.519849894613872543374989997` (digit penuh);
agregat winding `±8.95e-13` ∋ 0 ⊂ (−1/4,1/4); uniform error (3 nilai)
< klaim beku; artefak `audit_p1/l2_barrier_subset.py` + log resmi +
JSON + 1 transkrip smoke — commit bersama baris ini. **L3 SELESAI —
weld theorem-source HELD (57/57 PASS):** PT Thm 1 = height eksak
`3000175332800` (bukan hanya pembulatan 3·10^12 abstrak); identitas
margin `X/2 + 350479773/2 = T_PT` eksak; statement weld (i)/(ii)/(iii)
+ konklusi ≡ PROOF_NOTE (2.1)–(2.4) setelah kanonikalisasi
terdokumentasi (equal=True, string tercetak di log); containment +
overlap + citation chain byte-identik dua sisi; artefak
`audit_p1/l3_weld_checks.py` + log resmi + JSON + 2 transkrip smoke +
`reports/AUDIT_DBN_L3_2026-10-17.md` — commit bersama baris ini.
**L4 SELESAI + registry P3 aktif:** laporan
`reports/AUDIT_DBN_L4REPORT_2026-10-17.md` (tabel per-obligasi 8
`accepted` / 4 `unresolved` resource-bound; agregat tanpa GAP-FOUND;
coverage 9 butir) + `reports/FENCE_REGISTRY.md` (skema + 6 entri awal;
verdict audit = `A-2026-0001`) + guard CI fail-closed
`msaf/tests/test_fence_registry.py` (suite lokal 355 passed). Pra-reg
audit P1 tuntas; sisa hanya owner-gated (dashboard v6, Scope Note,
engine L1).

**Sesi berikutnya: baca berkas ini dulu**, lalu `reports/REPO_AUDIT.md`
(§1–4 verdict, §6–10 perbaikan tersegel) dan
`reports/DAFTAR_MASALAH_KERJA.md` (antrean 20 masalah).

**Berikutnya dieksekusi: audit P1** — baca
`reports/MSAF_PORTFOLIO_2026-10-17.md` §2 (P1) +
`reports/AUDIT_DBN_RECON_2026-10-17.md` + pra-registrasi beku
`reports/AUDIT_DBN_PREREG_2026-10-17.md` (target rilis, kriteria
verdict, urutan L2, cap anggaran, coverage).

Tidak ada konteks yang hidup hanya di dalam percakapan. Yang menentukan
ada di git (pushed), di Zenodo (DOI), atau di berkas ini.

---

## 1. Apa yang TERSEGEL (aman, tidak hilang)

| Segel | Lokasi | Bukti |
|---|---|---|
| Audit 4 repo anak + 4 DOI Zenodo | commit `4f4f846` di repo kerja (remote `T-hat-N`, branch `main`) | `reports/REPO_AUDIT.md` §6–§10 |
| Anti-turing-pnp | commit `62b37f50`, CI hijau | DOI 10.5281/zenodo.23392667 |
| gw-spectral-map | commit `6dc9f9ce`, CI hijau | DOI 10.5281/zenodo.23392641 |
| guinand-weil-rigorous-numerics | commit `7f8f6e7f`, CI hijau | DOI 10.5281/zenodo.23392323 |
| the-asymmetric-wager-msaf | branch `audit-fixes-bmw` commit `b9958be`, CI hijau (ubuntu+windows) | DOI 10.5281/zenodo.23392745 |
| Program msaf sendiri | tag `v1.39.0-alpha` (terbaru) | `msaf/tests` 250 passed |
| Anti-Turing / P-vs-NP | v1.39.0-alpha, entails gap didokumentasikan | `GAP-PNP.md` |
| Hodge → HODGE-CH | v1.38.0-alpha, polinomial Weil eksak | `reports/HODGE_CLOSURE.md`, `HODGE_CH_SPEC.md` |
| Resolusi kedua dim 201 + delta S1/S2 + perbaikan sensor CI | commits `1d591a8`, `da94306`, dan commit yang membawa baris ini; CI hijau run `38832840886` | `reports/THREE_TASKS_2026-10-15.md` §4 |
| Seri tiga titik dim 201/301/401 + §5 + dashboard v3 | commit `da93d19` dan commit yang membawa baris ini; CI hijau run `38850650775` | `reports/THREE_TASKS_2026-10-15.md` §5, `reports/gw_diagnostic_v3.html` |
| README §6 (peta jalan lengkap + rumus instrumen) | commit `28de2b8` dan commit yang membawa baris ini; CI hijau run `38852216992` | `README.md` §6, aset `docs/math/gw_*.svg` |
| Konsolidasi manuskrip + tag delivery akhir | commit yang membawa baris ini; dibangun di atas `28de2b8`/`86b161f` (CI hijau run `38852216992` / `38852448159`); tag `v1.40.0-alpha-final-certified-delivery` | `exports/research_paper.tex`, `reports/gw_diagnostic_v3.html` (sha256 `89C7D5F948626BD51DE06F37534BDC4941D3793353DCB80B8557E10E2BED7322`, byte-identik pasca rerun `--write`), `reports/THREE_TASKS_2026-10-15.md` §4.4 + §5 |
| H0 lockdown + pra-registrasi amandemen lantai (H1) | commit yang membawa baris ini; dibangun di atas `a37b50b` (CI hijau run `38854261266` / `38854493402`); spesifikasi DIBEKUKAN, sha256 `3C9958BEE3021385B242B84B2ECDA136E15F35D5682C16FF690713830EFBB917` | `docs/ZENODO_ACTIVATE.md`, `reports/RELEASE_v1.40.0-alpha-final-certified-delivery.md`, `reports/AMENDMENT_FLOOR_SPEC.md` |
| Deposit delivery T-hat-N (versi baru Zenodo) + release GitHub delivery | commit yang membawa baris ini; DOI versi `10.5281/zenodo.23410894` (konsep `10.5281/zenodo.23338271`); arsip tarball commit `a37b50b` sha256 `44bdfb87788b1f1da687b2d8e852641385b5c80de99c072768f6b67120198f61` (546.800 byte, md5 cocok), CI hijau run `38854261266` / `38854493402`; release `v1.40.0-alpha-final-certified-delivery` terbit via `gh` | `https://doi.org/10.5281/zenodo.23410894`, `msaf/zenodo_deposit.py` (commit `3305221`), halaman release |
| Amandemen lantai H1 — grid refined 20000 surrogat + array robustness C4 5-seed | commit yang membawa baris ini; dibangun di atas rantai tooling H1 `993b0e8` → `2f6100e` → `32ac8dc` (CI hijau run `38888730255` untuk `32ac8dc`; catatan jujur: run pertama `993b0e8` GAGAL karena runner CI belum punya scipy — diperbaiki di akar oleh `2f6100e`, pin `scipy==1.18.0`); spec DIBEKUKAN sha256 `3C9958BEE3021385B242B84B2ECDA136E15F35D5682C16FF690713830EFBB917`; angka eksak (spec §6.5): C4 kanonik `1262/20000` = 6.31000e-02 (NO DISCRIMINATION AT N=401), pooled `5877/100000` = 5.87700e-02, homogenitas p = 2.01097e-22 → klasifikasi NOT STABLE (dispersion-dominated); 17/18 sel di lantai `0/20000` (bound `1.49775e-04`); ekspektasi pra-registrasi "semua cabang di bawah 0.05" TERFALSIFIKASI (4/5 seed ≥ 0.05) | `reports/AMENDMENT_FLOOR_RESULTS.md` (generator `msaf/gw_h1_report.py`), `reports/gw_h1_floor_refine.json`, `reports/h1_floor_refine_section.md`, 7 log `reports/mont_run_20000_*.txt` |
| Amandemen lantai H1 — (C) verifikasi independen engine B (S2 penuh 20000) | commit `669a3c3` + commit yang membawa baris ini; dibangun di atas `84248da` (CI hijau run `38922309908`); CI hijau run `38972531845` (python-tests + lean-kernel); verdict `PASS-WITH-ENUMERATED-EXCEPTIONS`, counts 18/18 eksak, exit 0, 9062 s | `reports/gw_engine_b_verify.log`, `reports/gw_engine_b_verify.json`, `reports/ENGINE_B_PILOT_FINDINGS_2026-10-16.md` (R1/R2), `msaf/tests/test_gw_engine_b_full_artifact.py` |
| README Section 7 — status tersegel mesin + diagram alur kerja / rantai verifikasi | commit `90a6520` + `c957503` (perbaikan byte-count LF-normalised; run `38975016984` GAGAL pada kolom bytes, diperbaiki di akar); CI hijau run `38975450198`; suite 345 passed | `README.md` §7, `docs/math/readme_workflow.svg`, `docs/math/readme_trustchain.svg`, `msaf/gw_readme.py`, `msaf/tests/test_readme_guard.py` |
| Dashboard v5 — ekstensi H1 + engine B di atas v4 byte-identik | commit `2d7b72c` + `6304599` + baris ini; dibangun di atas `9af033b`; CI hijau run `38992695849` + `38995193745`; v4 preserved sha256 penuh `C9EC26217F516A1A73527BC098ADBC11A4935F6965D905D38A7DBEB7D95A8B6` (embed di panel 6 v5 + dipin test guard); v3 tetap `89C7D5F948626BD51DE06F37534BDC4941D3793353DCB80B8557E10E2BED7322`; 15 patch deterministik (14 + koreksi radius float64 2026-10-17) + Panel 7/8 (H1 refined grid, array 5-seed, census 720 bin engine B, counts 18/18 eksak); suite 349 passed | `reports/gw_diagnostic_v5.html`, `msaf/gw_dashboard_v5.py`, `msaf/tests/test_gw_dashboard_v5.py`, `msaf/gw_readme.py`, `README.md` |
| Tangga λ_min c=13 diperpanjang — rung dim 321 (rung dim 257 pendahulu) | commit `9ce44be` + baris ini; dibangun di atas `abecb07`; CI hijau run `38999210393`; λ_min `3.2990200597971055e-59` (dim 257, 2026-10-15) → `3.123458832662237e-59` (dim 321, 2026-10-17), verdict CERTIFIED + all_exclude_zero; lereng 257→321 −0,000854 (ratio 0,9468 per 64 dim — masih mengecil, terus melandai, belum ada upturn); registry rad/leak 0,0 = underflow float64 (koreksi 2026-10-17) | `reports/lambda_min_eig_ladder_big.json`, `reports/lambda_min_eig_ladder_dim321.json` + `reports/lambda_min_eig_ladder_dim321.log`, `reports/GW_LADDER_DIM321_2026-10-17.md` |
| C4 robustness array diperluas (S5 → S10; item H1) | commit `19fe938` + `15f767f`; dibangun di atas `657352c` (pra-registrasi, dipush sebelum draw pertama); CI hijau run `39019664353`; catatan jujur: run pertama `39019056454` GAGAL pada tes kesetaraan float bit-exact lintas platform (scipy beta.ppf ~1 ULP; semua count/label/pooled identik) — diperbaiki di akar di tes (float rel_tol = 1e-12, int/string eksak) di `15f767f`; hasil pooled `11458/200000` = 5.72900e-02 (CP95 [5.62754e-02, 5.83174e-02]), chi2 = 131.2879 (df 9), p = 6.44376e-24 → NOT STABLE; angka of record tetap `1262/20000` = 6.31000e-02 | `reports/C4_SEEDS10_RESULTS_2026-10-17.md`, `reports/gw_h1_c4_seeds10.json`, `reports/h1_c4_seeds10_section.md`, `reports/c4_seeds10_launch_2026-10-17.log`, 5 log `reports/mont_run_20000_s2026100[5-9]_100_150.txt` |
| Resolusi ke-4 (dim 501) — OUTCOME non-PD di ladder (statistik berakhir) | commit yang membawa baris ini; dibangun di atas `ea2ed77` (pra-registrasi, dipush sebelum launch; CI hijau `39020789629`); ladder `UNDETERMINED at pivot 446` (n_pos=446, n_neg=0; 0 certified) → OUTCOME per pra-registrasi §4 (statistik berakhir; tanpa rerun); insiden wrapper `ExitCode` kosong di launcher (PS 5.1 `Start-Process -PassThru` + `.WaitForExit()`) di-root-cause tanpa dampak pada hasil; Stage C/M tidak dijalankan (artefak C/M tidak ada) | `reports/GW_RESOLUTION4_DIM501_2026-10-17.md`, `reports/gw_route_s_ladder_c100_n250.json` (raw `319e50d7...`), `reports/gw_route_s_ladder_c100_n250.log` (raw `c6e48510...`), `reports/gw_route_s_ladder_c100_n250.err.log` (0 byte), `reports/res4_dim501_launch_2026-10-17.log` (raw `d4225ac0...`), `reports/RESOLUTION4_DIM501_PREREG_2026-10-17.md` |
| P1 audit Λ (DBN/Gomila) — pra-registrasi L1–L4 dibekukan sebelum eksekusi | commit `86a32c9` + baris ini; dibangun di atas `b7e0e8f` (penutupan 501); CI hijau `39024004135`; target beku rilis `review-01787854-v3` (commit `2e9976c4...`, seal `89a20156...`, OCI digest `6e29bc53...`; BUKAN HEAD bergerak); L1 conditional — mesin audit tanpa engine container (docker/podman absen; WSL2 tanpa distro; 2026-10-17; keputusan pemilik); stack L2 kita = mpmath.iv + fractions (bukan jalur C/FLINT mereka) | `reports/AUDIT_DBN_PREREG_2026-10-17.md`, `reports/AUDIT_DBN_RECON_2026-10-17.md`, `reports/MSAF_PORTFOLIO_2026-10-17.md` |

Empat DOI diverifikasi setelah terbit: `doi.org` → 200, tiap record punya
`related_identifiers` ke repo GitHub-nya, tiap deskripsi memuat commit sha
DAN sha256 arsip.

---

## 2. YANG BELUM SELESAI — baca sebelum starting apa pun

### 2.0b [BARU, 2026-10-15 sore] Tiga tugas tertutup sebagian — baca `reports/THREE_TASKS_2026-10-15.md`

- **Jembatan ℂ→ℝ tertutup** (`lean/XiNoRealZero.lean`, nol aksom baru —
  diukur dengan `#print axioms`). Sertifikat real hanya bisa lahir dari
  nol berpilar imajiner nol; fungsi yang tak pernah nol di sumbu real
  tidak punya sertifikat real untuk interval **mana pun**.
- **Paruh analitik = SPESIFIKASI, bukan bukti.** Mathlib v4.33.1 tidak
  punya zeta analitik maupun `Real.gamma_pos`, jadi `lean/spec/XiAnalyticSpec.lean`
  menurunkan `xi > 0` dari **enam kewajiban yang dideklarasikan**.
  Paruh ini sengaja di luar `lean/*.lean` karena audit aksioma repo
  menangkapnya — dan itu benar.
- **Anggaran tanda Minkowski terbukti** (`lean/ComplexMoore.lean`):
  enclosure `a ± r` yang dilebarkan symetris dengan `T` tetap
  menyingkirkan nol **iff `T < a - r`**.
- **Route S tersertifikasi ke dim 641** pada 6000 bit, 6/6
  CERTIFIED POSITIVE DEFINITE (`reports/gw_route_s_ladder.json`).
- **Hukum redaman DITERIMA lewat `arb_mat.eig`, dan model yang diasumsikan
  TERBANTAH.** Pada 6000 bit (c=13): λ_min ≥ 7.674e-23 (dim 17),
  8.569e-35 (33), 2.259e-49 (65), 6.321e-59 (129), 3.299e-59 (257,
  2026-10-15), 3.123e-59 (321, 2026-10-17) — radius & Im bocor
  registry 0,0 (**koreksi terukur 2026-10-17**: keduanya artefak underflow
  float64; nilai sejati ~1e-1790; matriks bola simetris eksak → realness
  struktural; lihat `reports/GW_RADIUS_REGISTRY_CORRECTION_2026-10-17.md`).
  Lereng `ln λ_min` per dimensi: −1,72 → −1,05 →
  −0,34 → −0,0051 → −0,000854, jadi `A·e^(−Bn)` dengan B konstan
  **terbantah** pada irisan ini (rung dim 321 masih mengecil — ratio 0,9468
  per 64 dim — tetapi laju terus melandai; belum ada upturn).
  ⚠️ hanya satu irisan (c=13);across-c bukan apel-samel.
- **9000 bit terbukti tidak menambah apa pun**: nilai identik
  bit-dengan-bit dengan 6000 bit, radius registry tetap 0,0 (koreksi 2026-10-17), biaya 2,6×.
- **Tangga Sturm tidak bisa mengukur λ_min** dan alasannya mekanis:
  bracket cluster identik pada 300 maupun 3000 bit, karena titik geser
  dari mesin duble float64.
- **S1/S2 terukur pada TIGA resolusi → seri tiga titik 201/301/401.**
  dim 401 (`gw_spectrum_100_200.json`, run2), dim 201 (c=100/N=100,
  `reports/gw_spectrum_100_100.json`), dan dim 301 (c=100/N=150, 6000 bit,
  G-M0 PASS, `reports/gw_spectrum_100_150.json`): **S1 FINAL =
  INCONCLUSIVE di ketiganya** (chart-dependence bertahan; r_bar T
  0,6205 → 0,5635 → 0,5486 menurut dim menaik 201/301/401; L 0,1317 →
  0,1518 → 0,1909), **S2 FINAL = INCONSISTENT di ketiganya** (p_GUE
  0,0000 di 17 dari 18 sel; satu sel dim 301 = 0,0180 — tetap di bawah
  ambang 0,05; 2000 surrogat per ensemble, seed 20260927). **"Mengecil
  atau membesar" TERJAWAB pada versi ujinya: TIDAK mengecil** — tidak ada
  pendakian menuju konsistensi dari N=401 ke N=301 ke N=201; arah
  asimtotik tetap terbuka (seri lebih panjang). Delta lengkap + cacat
  proses: `THREE_TASKS_2026-10-15.md` §4 + §5 (generator:
  `msaf/gw_resolution_delta.py`; log: `reports/mont_run_100_100.txt`,
  `reports/mont_run_100_150.txt`).
- **Urutan berikutnya yang masuk akal:** (1) ~~anak tangga λ_min lebih
  panjang kalau arah B mau dipastikan (dim 257/321; 321 belum tuntas)~~ —
  **SELESAI 2026-10-17**: dim 257 (2026-10-15) + dim 321 terukur CERTIFIED
  (λ_min 3,299e-59 → 3,123e-59; lereng −0,0051 → −0,000854; laporan
  `reports/GW_LADDER_DIM321_2026-10-17.md`);
  (2) ~~spektrum kedua + S1/S2~~ **SELESAI 2026-10-16** — lihat bullet di
  atas; (3) ~~seri resolusi ketiga~~ **SELESAI 2026-10-16** (dim 301; §5) —
  yang tersisa: seri keempat (plafon ~100–200 pasangan/bin sudah terukur
  tiga kali), atau daya uji di atas lantai 2000 surrogat; (4) hanya setelah
  itu boleh bicara hukum redaman sebagai hukum.
- **Pembaruan 2026-10-16 (H1):** daya uji di atas lantai 2000 surrogat
  DIJALANKAN — grid refined 20000 + array C4 5-seed; hasil terukur +
  klasifikasi beku + falsifikasi ekspektasi pra-registrasi: lihat §2.0c
  (`reports/AMENDMENT_FLOOR_RESULTS.md`).

### 2.0c [BARU, 2026-10-16] Amandemen lantai H1 SELESAI — refined 20000 surrogat + array C4 5-seed

- **Pra-registrasi beku** `reports/AMENDMENT_FLOOR_SPEC.md` (sha256
  `3C9958BEE3021385B242B84B2ECDA136E15F35D5682C16FF690713830EFBB917`):
  bagian (A) + (B) tuntas; **(C) engine B SELESAI 2026-10-17** — run penuh
  lulus (lihat bullet terakhir; arsitektur dibekukan; tidak pernah
  verdict-bearing).
- **(A) Grid refined** (18 sel, 20000 surrogat/ensemble, seed 20260927):
  **17/18 sel k_GUE = 0/20000** → BOUND 95% `p_GUE < 1.49775e-04`
  (format "0.0000" pensiun), verdict INCONSISTENT tetap. Sel off-floor
  tunggal C4 (301|T|0.5): chi2 1367.6160, **1262/20000 = 6.31000e-02**
  (CP95 [5.97690e-02, 6.65587e-02]), k_Pois 4807/20000, verdict
  **NO DISCRIMINATION AT N=401**; nilai tersegel 36/2000 = 0.0180
  (INCONSISTENT) disupersede — kolom tersegel tetap terlihat.
- **(B) Array 5-seed S5** pada C4: k = 1262 / 960 / 1289 / 1021 / 1345
  → pooled **5877/100000 = 5.87700e-02** (CP95 [5.73201e-02,
  6.02456e-02]); homogenitas Pearson chi2 = 107.9299 (df 4),
  p = 2.01097e-22 → **NOT STABLE (dispersion-dominated)**; C4
  ditandai resolution-sensitive; angka of record tetap kanonik 20000.
- **Ekspektasi pra-registrasi TERFALSIFIKASI (dicatat, tidak dipatch):**
  spec §4 "setiap cabang meninggalkan C4 di bawah ambang 0.05" —
  terukur pooled 5.87700e-02 ≥ 0.05; 4/5 seed ≥ 0.05 (hanya 20261001 =
  4.80000e-02 di bawah).
- **Reproduktibilitas:** REPRO CHECK PASS (rerun dim 201 @2000 capped
  mereproduksi log tersegel identik); instrumen tak berubah
  (`b0af0f5...` / sha256 `072910f2...`); cap thread murni kinerja;
  7 log `reports/mont_run_20000_*.txt` (elapsed 3115.4 / 7514.3 /
  10443.3 / 6636.1 / 5947.4 / 4812.3 / 4106.2 s; semua exit 0).
- **Artefak:** `reports/AMENDMENT_FLOOR_RESULTS.md` (generator
  `msaf/gw_h1_report.py`; semua angka mesin, bukan retype),
  `reports/gw_h1_floor_refine.json`, `reports/h1_floor_refine_section.md`;
  extractor `msaf/gw_h1_extract.py`; manuskrip `exports/research_paper.tex`
  diamandemen bertanggal (section sebelum register cacat + pointer
  abstrak + catatan header).
- **Batas interpretasi (beku):** NOT STABLE; bukan "physical"; bukan
  teorema Montgomery, bukan bukti RH. Seri resolusi keempat tetap
  tersisa.
- **(C) Engine B SELESAI 2026-10-17:** verifikasi independen S2 run
  penuh (20000 sampel/ensemble, seed 20260927) — exit 0, 9062 s;
  verdict `PASS-WITH-ENUMERATED-EXCEPTIONS` (9 sel bersih + 9 sel
  edge-cluster terenumerasi, 0 gagal); counts 18/18 eksak vs engine A
  (k_GUE, k_Pois, four tails); artefak `reports/gw_engine_b_verify.log`
  + `reports/gw_engine_b_verify.json`; guard CI
  `msaf/tests/test_gw_engine_b_full_artifact.py`; riwayat R1/R2 di
  `reports/ENGINE_B_PILOT_FINDINGS_2026-10-16.md`; rincian §8
  `reports/AMENDMENT_FLOOR_RESULTS.md`.

### 2.0d [BARU, 2026-10-17] C4 S10 SELESAI — array robustness diperluas 5 → 10 seed

- Pra-registrasi `reports/C4_SEEDS10_PREREG_2026-10-17.md` (sha256_lf
  `d8dd65cd...`; commit `657352c`, dipush sebelum draw pertama;
  ordering check PASS di artefak: commit 13:45:32 < start run pertama
  13:47:32 lokal).
- Lima run baru seed 20261005..20261009 (cap-2 rolling queue; launcher
  log `reports/c4_seeds10_launch_2026-10-17.log`); semua `exit = 0`;
  36/36 tangkapan eksak; instrument sha `072910f2...` / spectrum sha
  `8fded839...` cocok di semua header; elapsed 4126.0 / 4151.7 /
  4000.5 / 3925.8 / 2852.0 s.
- Hasil (ekstraktor `msaf/gw_h1_c4_seeds10.py`, sha `c65dcc7f...`,
  tidak berubah; semua angka dari log):
  k = [1262, 960, 1289, 1021, 1345, 1164, 1115, 1114, 1022, 1166];
  pooled `11458/200000` = 5.72900e-02 (CP95 [5.62754e-02,
  5.83174e-02]); homogenitas chi2 = 131.2879 (df 9),
  p = 6.44376e-24 → **NOT STABLE (dispersion-dominated)** — dispersi
  S5 bertahan pada n = 10 (pertanyaan pra-registrasi terjawab:
  bertahan).
- Konteks warisan: 9/10 seed `p_hat_i >= 0.05` (yang di bawah hanya
  20261001 = 4.80000e-02); pooled >= 0.05; angka of record TIDAK
  berubah (`1262/20000` = 6.31000e-02).
- Insiden CI (dicatat, tidak disembunyikan): run `39019056454` GAGAL —
  self-validation menuntut float bit-exact; scipy `beta.ppf` tidak
  bit-identik Windows vs Linux (~1 ULP; semua count/label/pooled
  identik). Diperbaiki di akar: komparator toleransi (int/string eksak;
  float rel_tol = 1e-12, kebijakan `_close` yang sama) + tes pengunci;
  commit `15f767f`; CI hijau `39019664353`. Artefak/log/angka/ekstraktor
  tidak disentuh. Suite lokal 353 passed; CI 352 passed + 1 skipped.
- Artefak: `reports/C4_SEEDS10_RESULTS_2026-10-17.md` (laporan
  bertanggal, blok mesin verbatim), `reports/gw_h1_c4_seeds10.json`,
  `reports/h1_c4_seeds10_section.md`.
- Batas: NOT STABLE; bukan 'physical'; bukan teorema Montgomery; bukan
  bukti RH. Seri resolusi keempat (dim 501): dijalankan 2026-10-17 →
  OUTCOME non-PD, statistik berakhir; lihat §2.0e.

### 2.0e [BARU, 2026-10-17] Resolusi ke-4 (dim 501) SELESAI — OUTCOME non-PD di ladder

- Pra-registrasi beku `reports/RESOLUTION4_DIM501_PREREG_2026-10-17.md`
  (commit `ea2ed77`, dipush + CI `39020789629` hijau sebelum launch;
  launcher start 17:24:00).
- Stage L: ladder Route S 6000 bit (c=100, N=250 → dim 501) →
  `UNDETERMINED at pivot 446` (n_pos=446, n_neg=0, entries_finite=true;
  build 1612.96 s; LDL^T 177.07 s; total 1790.13 s; elapsed launcher
  1791 s). Bukan PD → pra-registrasi §4: OUTCOME, bukan infrastruktur;
  statistik titik ini BERAKHIR (Stage C/M tidak dijalankan; tidak ada
  angka S1/S2; tidak ada blok GW-DELTA keempat; tidak ada rerun; tidak
  ada parameter yang diubah).
- Insiden wrapper (dicatat, tidak disembunyikan): launcher log mencatat
  `stage L finished exit=` (kosong) → salah-branch ke ABORT
  "infrastructure failure". Root cause direproduksi di mesin ini: PS 5.1
  `Start-Process -PassThru` + redirect + `.WaitForExit()` → `ExitCode`
  null (`HasExited` True); dengan `-Wait` atau `cmd`+`$LASTEXITCODE`
  tertangkap benar. Komputasi tidak terpengaruh (runner selalu exit 0;
  log/JSON lengkap; err 0 byte). Log launcher TIDAK diedit (arsip);
  klasifikasi resmi di laporan bertanggal.
- Cek ulang segel pra-registrasi §5: 8 file raw + 3 item sha256_lf —
  PASS semua (termasuk `reports/gw_route_s_ladder_c100.json` raw
  `674a50d3...` — file seri lama tidak tersentuh; daftar lengkap di
  laporan §5).
- Artefak: `reports/GW_RESOLUTION4_DIM501_2026-10-17.md`,
  `reports/gw_route_s_ladder_c100_n250.json` (raw `319e50d7...`),
  `...c100_n250.log` (raw `c6e48510...`), `...c100_n250.err.log`
  (0 byte), `reports/res4_dim501_launch_2026-10-17.log` (raw
  `d4225ac0...`).
- Publikasi append-only: `reports/THREE_TASKS_2026-10-15.md` blok baru
  (notice outcome; GW-DELTA/GW-DELTA-3 tidak disentuh); README §6.7
  item 2 diperbarui.
- Batas: sertifikat tanda LDL^T interval pada satu matriks finit
  (6000 bit) — bukan teorema Montgomery, bukan bukti RH, bukan
  Weil-positivity, bukan tren. Gate pra-registrasi audit P1
  (`reports/AUDIT_DBN_RECON_2026-10-17.md`) kini TERBUKA: C4 (S10) +
  501 (outcome) keduanya tertutup; pra-registrasi audit SELESAI
  2026-10-17 (`reports/AUDIT_DBN_PREREG_2026-10-17.md`, commit
  `86a32c9`); eksekusi audit = tahap berikutnya → §2.0f.

### 2.0f [BARU, 2026-10-17] P1 audit — pra-registrasi DIBEKUKAN; eksekusi menyusul

- **Berkas beku:** `reports/AUDIT_DBN_PREREG_2026-10-17.md` (commit
  `86a32c9`, CI `39024004135`) + recon
  `reports/AUDIT_DBN_RECON_2026-10-17.md` (§1–§7 lengkap: pin,
  parameter, margin, transkripsi Thm 1.2/1.3 + Lemma 8.4, template
  reviewer). **Target:** rilis `review-01787854-v3` (commit
  `2e9976c4...`; seal `89a20156...`; OCI digest `6e29bc53...`), BUKAN
  HEAD bergerak; klaim pihak ketiga yang diuji: Λ ≤ 0.1787854
  (unrefereed).
- **Urutan eksekusi (beku di pra-registrasi):** gate Lean statis
  (anti-circularity atas `lean/` rilis) → L2 window-freeze & sign-map →
  L2 Prop 4.10 (margin target 5.57871094787e-7) → L2 tail (koridor
  0.999719 < D < 0.999721; margin pasca-error > 0.0001735209373337) →
  L2 subset barrier (K=8 + seam; cap 4 jam) → L3 weld (checklist beku;
  transkripsi di recon §7.11) → L4
  `reports/AUDIT_DBN_L4REPORT_<date>.md` + entri registry P3.
- **L1 (replay container): CONDITIONAL** — 2026-10-17: docker/podman
  absen; WSL2 tanpa distro; arsip OCI belum lokal. Jika tak ada engine
  saat attempt → NOT-RUN-ENVIRONMENT (masuk coverage); L2/L3 tetap
  jalan. Keputusan pemilik: aktifkan Docker Desktop / distro WSL bila
  L1 diinginkan.
- **Aturan mengikat (dari pra-registrasi):** tanpa perubahan parameter
  karena hasil; infra-rerun hanya setelah fix + tercatat; semua angka
  machine-extracted; coverage eksplisit; satu operator (dua pass
  berselang waktu = mitigasi, bukan dua auditor independen).

### 2.0g [BARU, 2026-10-17] P1 audit — eksekusi L2 item 1 & 2 SELESAI (gate Lean + L1 tercatat)

- **Gate Lean anti-circularity (pra-L2) SELESAI.** Fakta mesin: rilis
  `review-01787854-v3` (commit `2e9976c4...`) memuat 0 berkas `.lean` —
  prereg §7 "release's lean/ tree" karena itu dieksekusi tanpa mengedit
  prereg: gate dijalankan atas `lean/` pada commit pasca-rilis terpin
  `a74738de`, berlabel AUXILIARY; 57/57 blob rilis terverifikasi (git
  blob sha1); gate `gate.py lean` (anti-circularity) PASS 25/25 berkas;
  attempt fetch pertama yang gagal disimpan verbatim. Artefak
  `reports/audit_p1_lean_gate.log` + `reports/audit_p1_lean_gate_attempt1.log`;
  commit `ad4755c`. Diskrepansi release-vs-HEAD → masuk coverage L4.
- **L1 = NOT-RUN-ENVIRONMENT** (pra-reg §3.4): mesin tanpa engine
  container (docker/podman absen; WSL2 tanpa distro). Log
  `reports/audit_p1_l1_launch.log`; commit `20a77c8`. Instalasi engine =
  keputusan pemilik (bukan bagian audit ini).
- **L2 item 1 SELESAI — window freeze & affine sign map.** Rerun tetap
  34/34 PASS exit 0 (attempt 1 disimpan verbatim + diff mesin: hanya baris
  label pi-width berubah — disengaja); angka kunci: lebar bracket π <
  1e-100 eksak; k terbesar dengan width < 10^-k = 128; margin lantai
  `5377393.987856431175` / `11989041.174663815586`; `x_* =
  6000000185827 + sqrt(2412323/2500000)`. Commit `de4d686`, CI
  `39033622304` hijau.
- **L2 item 2 SELESAI — Prop 4.10 finite-lane error budget & binding.**
  Implementasi kita sendiri (`audit_p1/l2_prop410_budget.py`, sha256
  `cbb33b81...`): mpmath.iv 240-bit; semua angka final diekstrak sebagai
  rasional eksak (`mpmath.libmp.to_rational` atas endpoint mentah `_mpi_`)
  dan seluruh perbandingan vs konstanta sealed = perbandingan
  `fractions.Fraction` eksak; enumerasi per-suku n = 1..20000 (pilihan
  kita) + ekor via konveksitas `h(u) = (t/4)u² − σ1u + u` (check
  f-menurun per window); 4 window: 690988 (titik evaluasi rilis), 690989,
  1000000, 3840000 (= N_* (5.1), jendela overlap finite/tail). Hasil
  resmi: **48/48 PASS, exit 0, 30.6 s** (`reports/audit_p1_l2_prop410.log`;
  JSON `reports/audit_p1_l2_prop410_results.json` sha256 `3a83da89...`).
  Angka mesin: e_A+e_B ≤ `0.000000000000874463842636` ≤ sealed
  `0.000000000002057023688667` (gap ≥ `1.182559846031e-12`); e_C,0 ≤
  sealed `0.000000233492848188649183` dengan gap tipis ≥ `3.20854e-25`
  (kasus batas: nilai kita praktis sama dengan konstanta sealed di 24 dp —
  dicatat sengaja; bandingkan window N=690989: gap ≥ `5.66918e-13`,
  konsisten dengan sensitivitas log0); E_max ≤
  `0.000000233493722652491819` ≤ sealed; margin ≥ `0.000000557872277347`
  ≥ sealed. **Verdict L2 item 2 = REPRODUCED** (pra-reg §4.5: rantai
  independen kita mensertifikasi pertidaksamaan sealed pada konstanta
  sealed; untuk 4 window tersampel). Riwayat pra-run (semua tersimpan):
  smoke1 GAGAL 5 dari 47 check — converter endpoint→Fraction salah
  konvensi internal mpmath (sign/mantissa; `.a/.b` ivmpf bukan mpf) →
  semua tampilan angka 0; diperbaiki di akar; smoke2 GAGAL 1 dari 48 —
  typo arah bracket π di test sanity kita sendiri (komputasi audit lolos
  47/48 dengan nilai nyata); smoke3 PASS 48/48, lalu run resmi attempt 1
  PASS 48/48 dengan parameter tidak berubah. Transkrip:
  `reports/audit_p1_l2_prop410_smoke{1,2,3}.log`. Klaim diidentifikasi
  dari `verifiers/verify_finite_and_binding.py` (blob `17c33ac1...`) dan
  `verifiers/verify_error_constant_weld.py` (blob `891f3b01...`) —
  read-only; tidak ada kode mereka yang dipakai. Coverage item ini:
  window antara (690989..3839999) TIDAK dihitung ulang satu per satu;
  sertifikasi kita = first window + 3 window tersampel termasuk ujung
  jauh; uniformity window penuh tetap bersandar pada teorema
  window-freeze rilis (bukan objek re-derivasi penuh item 2).
- **Berikutnya: L2 item 3** (tail lane: koridor `0.999719 < D < 0.999721`;
  post-error margin `> 0.0001735209373337`; `M = 153814`, `M_err = 3000`,
  `M_max < 1.608290`) → **item 4** (subset barrier K=8 + seam +
  first/last; cap 4 jam) → **L3** (checklist weld) → **L4** report +
  registry P3.
- **Owner-gated yang menunggu (tidak memblok):** (a) update dashboard =
  wajib v6 baru (v3/v4/v5 dibekukan, tidak boleh diedit; persetujuan
  pemilik belum diberikan); (b) Scope Note recording; (c) instalasi
  engine container untuk replay L1 di masa depan.

### 2.0h [BARU, 2026-10-17] P1 audit — L2 item 3 (tail lane) SELESAI — REPRODUCED

- **Klaim beku (pra-reg §4 item 3):** koridor `0.999719 < D < 0.999721`;
  `(1−D)/M_max > 0.0001735326089372`; error ekor
  `< 0.000000011671604`; margin pasca-error `> 0.0001735209373337`;
  anchor `M = 153814`, `M_err = 3000`, `M_max < 1.608290`.
- **Implementasi kita:** `audit_p1/l2_tail_budget.py` (sha256
  `E2D75209…`, dikunci di JSON), mpmath.iv 240-bit + `fractions.Fraction`
  untuk semua angka final (perbandingan rasional eksak); 10 berkas sumber
  diverifikasi in-run via git blob sha1+size (TAIL_LEMMA,
  CANDIDATE_PARAMETERS, MAXIMUM_CHECKS, 4 log, 2 verifier); tanpa
  penggunaan kode rilis (read-only untuk identifikasi klaim + saksi
  regresi non-verdict). Device: D-side pada `I_box` tertutup; error-side
  pada `I_ext` tertutup; semua gate premis (SC1/SC2/SC3, YM, Δ-gate,
  eC0-quotient, GN-TR/GN-AB/GN-error, OVW) di-re-check sebagai premis
  perlu.
- **Run resmi:** exit 0, 75.4 s, verdict `PASS`, 47/47 check; log
  `reports/audit_p1_l2_tail.log` (sha256 `FE595389…`), JSON
  `reports/audit_p1_l2_tail_results.json` (sha256 `643F2AE8…`).
- **Angka mesin / slack vs konstanta sealed (eksak):**
  `D_lb − 0.999719 ≥ 4.78933499205324062210851e-7`;
  `0.999721 − D_ub ≥ 9.0620060210635652430292e-8`;
  `flow_lo − 0.0001735326089372 ≥ 5.478455158416791617158853e-12`;
  `0.000000011671604 − err_ub ≥ 1.410811985693537360806e-15`;
  `margin_lo − 0.0001735209373337 ≥ 5.479365970402485154519659e-12`;
  `M_max_ub − 1.608290 ≤ −8.55045859239309847667613e-7`. Nilai kunci:
  `D_ub = 0.999720909379939789…` (lebar interval `D ≤ 1.4304e-6` <
  slack koridor 1.9094e-6), `err_ub = 1.167160258918801…e-8`.
- **Probe titik (jalur mpf non-interval; 2 titik D-side + 3 titik
  hull error):** semua upper tersertifikasi mendominasi nilai titik
  tersampel; headroom terkecil `4.65707e-13` di `(t0, y_lo)/err`.
- **Perbandingan non-verdict vs titik terarah Arb 512 rilis**
  (`logs/tail_arb_512.log`, blob `c091e5ee…`): semua komponen D-side
  setuju pada 1e-16..5e-12 (rantai kita sedikit lebih ketat); `eC0`
  kita = nilai lane Python 256-bit rilis (`1.167110878131e-8`) sampai
  ~4e-19 relatif, sedangkan lane C/Arb 512 mereka lebih longgar
  `7.25e-8` relatif di eksponen (keduanya enclosure valid; target
  sealed membersihkan ketiganya).
- **Riwayat pra-run (semua transkrip tersimpan, tidak ada yang
  dipatch):** `_smoke1` GAGAL (`to_rational` mpmath mengembalikan tuple
  `(p, q)`, bukan Fraction); `_smoke2` PASS (anchors+sigma); `_smoke3`
  GAGAL di blok cetak referensi (NameError lokal `part_err`; komputasi
  dan semua verdict internal sudah lolos); `_smoke4` GAGAL di format
  `nstr10` (`mpf(Fraction)` tak didukung versi mpmath ini) — semua
  diperbaiki di akar; run resmi adalah run segar dengan parameter tidak
  berubah. Transkrip `reports/audit_p1_l2_tail_smoke{1,2,3,4}.log`.
- **Coverage item 3 (beku):** sertifikasi hanya di titik desain
  `N = N_* = 3840000`; langkah "semua N ≥ N_*" dan cakupan y di atas
  `I_box` tetap bersandar reduksi rilis §6/7 (gate di-re-check sebagai
  premis perlu); lane Arb/C dan Python 256 rilis TIDAK dijalankan ulang
  (dicatat di JSON `scope.not_done`).
- **Berikutnya: L2 item 4** (subset barrier K=8 narrowest + seam +
  first/last; cap 4 jam) → **L3** weld checklist → **L4** report +
  registry P3.

### 2.0i [BARU, 2026-10-17] P1 audit — L2 item 4 (barrier subset) SELESAI — REPRODUCED (level descriptor)

- **Klaim beku (pra-reg §4 item 4):** K=8 prisma margin tersegel
  terkecil + seam faces + prisma first/last; recheck winding dengan
  metode enclosure kita sendiri (BUKAN sampling interior); klaim:
  uniform error total `< 0.000356523011600040 < 0.00125`
  (`e_A+e_B < 3.639278679550541e-10`,
  `e_C,0 < 0.000356522647672172`); gate `M_i > D_z,i/(2(num−1)) +
  D_t,i·Δt_i + 0.00125`; agregat winding `[−8.95, 8.95]×10⁻¹³`; margin
  minimum tersegel `0.519849894613872543374989997`.
- **Implementasi kita:** `audit_p1/l2_barrier_subset.py` (sha256
  `8E81881E…`). Device: setiap token desimal log ditranskripsi ke
  `fractions.Fraction` eksak (tanpa float di semua check); setiap
  pertidaksamaan = perbandingan rasional eksak dengan endpoint luar
  konservatif; tanpa evaluasi titik interior slab; tanpa menjalankan
  ulang lane C/Arb (input reuse sesuai protokol). 10 berkas rilis pinned
  (`2e9976c4…`) diverifikasi in-run via git blob sha1 + size.
- **Gate ganda:** `rec_E8_lo = M_lo − spatial_hi − time_hi − eps_hi > 0`
  (komposisi ala verifier binding rilis, direproduksi independen) dan
  varian kita lebih kuat `rec_x_lo = M_lo − Dz/(2(Dz−1)) − Dt·Δt_hi −
  eps_hi > 0` (spatial eksak + hull ball-t); keduanya > 0 untuk 883/883.
- **Angka kunci (log resmi, machine-extracted):** min
  `rec_E8_lo = 0.519849894613872543374989997000000` di prisma 882 —
  **sama persis dengan klaim sealed sampai 27 digit**; min `rec_x_lo =
  0.519849894613872543386998324392146`; seleksi K=8 = prisma 875–882
  (set identik di ranking rec_E8_lo); subset S = {1, 874…883} (11
  prisma); winding maks |endpoint| = 2.27e-15 (prisma 1); seam 882/882
  token byte-identik; coverage `[0, 129/800]` via rantai token + endpoint
  `[0.16125 ± 2e-35]`; 883/883 margin-ball ∩ hull rekonsiliasi; eps ball
  uniform ∋ 1/800 lebar < 1e-25; header N-corners=690988,690988.
- **Agregat winding:** token `[+/- 8.95e-13]` eksak; Σ interval
  per-prisma (eksak) = `[−8.96873899183957245148028286137e-13,
  +8.96873900816042754851971713863e-13]`; irisan dengan agregat = ya
  (keduanya enclosure dari jumlah riil yang sama); containment
  Σ ⊆ agregat = **tidak** (selisih ~1.87e-15/sisi dari pembulatan print
  radius per-prisma ke 3 digit keluar — dicatat sebagai info, bukan
  verdict; |8.95e-13| ≪ 1/4 sehingga integer-winding = 0 tetap terbukti).
- **Uniform error (`uniform_error_256.log`, dibandingkan eksak):**
  `e_A+e_B upper = 3.63927867955054020359…e-10 < 3.639278679550541e-10`;
  `e_C0 upper = 0.00035652264767217171332… < 0.000356522647672172`;
  total `= 0.00035652301160003966838… < 0.000356523011600040 < 1/800`;
  aritmetika klaim eksak `eAB + eC0 = 0.00035652301160003995505… ≤
  0.000356523011600040`; ball total konsisten dengan ball-sum eAB+eC0
  (irisan; total = eAB + eC0 di sumber C rilis). Scope note rilis
  "analytic justification at t=0 remains external" dicatat.
- **Run resmi:** exit 0, verdict `PASS`, 124/124 check; log
  `reports/audit_p1_l2_barrier.log` (sha256 `DB67FDA7…`), JSON
  `reports/audit_p1_l2_barrier_results.json` (sha256 `5D7AED37…`).
  Reproducibility: log resmi **byte-identik** dengan smoke-1 (sha256
  sama) — skrip deterministik, input sama; guard LOG-EXISTS memastikan
  log resmi dibuat oleh run resmi (run segar; JSON ditulis ulang oleh
  run resmi).
- **Riwayat pra-run:** smoke-1 = run penuh pertama, PASS 124/124 tanpa
  perbaikan; tidak ada transkrip gagal (1 transkrip disimpan:
  `reports/audit_p1_l2_barrier_smoke1.log`).
- **Coverage item 4 (beku, di JSON `boundary`):** lane C/Arb TIDAK
  dijalankan ulang; enclosure descriptor per-prisma (nilai mesh,
  min_mesh, winding, Dz, Dt) dipercaya sebagai INPUT tersegel sesuai
  protokol; regenerasi koefisien stored-sum & artefak Taylor-tail tidak
  di-recheck; byte-identity seam ter-serialisasi di dalam assembly rilis
  tidak di-recheck (hanya token seam sisi-log); sweep independen penuh
  883-prisma tidak di-ulang (rekomputasi deskriptor untuk 883 + deep
  check subset); lane prop43/prop62 di luar scope.
- **Berikutnya (saat itu): L3** (weld checklist: domain/endpoint/
  quantifier/substitusi, kompatibilitas parameter X/2 vs T_PT,
  containment, citation chain) → lihat §2.0j (L3 SELESAI); berikutnya
  L4 report + registry P3.

### 2.0j [BARU, 2026-10-17] P1 audit — L3 (weld theorem-source, clean-room) SELESAI — WELD HELD

- **Protokol beku (pra-reg §5):** checklist 1–5 — pemetaan hipotesis
  (i)/(ii)/(iii) Thm 1.2 ↔ slot paket (P1/T1/B1–B2 + F1–F3, glue C1;
  id slot dari `ADVERSARIAL_REVIEW_PROTOCOL.md`); kompatibilitas
  parameter; containment; citation chain; verdict per hipotesis +
  verdict weld.
- **Implementasi:** `audit_p1/l3_weld_checks.py` (sha256 `9AF03B5D…`).
  57 cek; seluruh aritmetika verdict = `fractions.Fraction` eksak
  (tanpa float); 14 dokumen rilis di-gate in-run via git blob sha1 +
  size terhadap tree pinned `2e9976c4…` (PROOF_NOTE,
  CANDIDATE_PARAMETERS, WINDOW_FREEZE_THEOREM, TAIL_LEMMA,
  TAIL_PROVENANCE, NATIVE_BINDING, DERIVATIVE_BOX_LEMMA,
  ERROR_CONSTANT_WELD, MAXIMUM_CHECKS, README, BIBLIOGRAPHY,
  ADVERSARIAL_REVIEW_PROTOCOL, references/README, BARRIER_CERTIFICATE);
  e-print Polymath v2 (`1be3bc38…`) di-re-ekstraksi ulang dari tar
  (member `debruijn.tex` sha256 `560a28fe…`) dan digest 4 segmen
  di-reproduksi (Thm 1.2 `06290d46…`; Thm 1.3 raw/norm
  `2bdd6d87…`/`cebe9801…`; region `4353e6c8…`; Lemma 8.4
  `b2fbc004…`); PT v1 (`c4f13cdf…`) di-re-decompress (payload sha256
  `c6c29099…`).
- **Temuan kunci (machine):** PT Thm 1 (pt_v1.tex baris 61–63) berbunyi
  height persis `3 000 175 332 800` = `T_PT` paket (abstrak hanya
  membulatkan ke 3·10^12 — ini menutup titik kritis hypothesis (i));
  identitas `X/2 + 350479773/2 = 3000000092913.5 + 175239886.5 =
  3000175332800 = T_PT` eksak; statement weld hipotesis (i)/(ii)/(iii)
  + konklusi Thm 1.2: teks e-print v2 ≡ PROOF_NOTE (2.1)–(2.4)
  setelah kanonikalisasi terdokumentasi (equal=True; string
  ternormalisasi tercetak di log); containment eksak
  (`y0²−(1809/10000)² = 234599/10^8 > 0`; canopy `893927/2500000 < 1`;
  `sqrt(1−y0²) < 1`); overlap `3149013 = 3840000−690988+1` kontigu;
  bracket sekunder `x_*` (mpmath-60d π, label non-primer) > margin
  beku rilis; citation chain byte-identik dua sisi (Polymath
  `60d0d2d3…`, PT `3362f66a…`) + record v2 = "final version" (RIMS)
  + DOI refereed PT `10.1112/blms.12460` (Bull. LMS 53(3):792–797).
- **Verdict:** hypothesis (i)/(ii)/(iii) = `compatible`; `weld verdict:
  HELD`; `checks_total: 57  checks_failed: 0`; `L3 machine verdict:
  PASS`; exit 0.
- **Run resmi:** log `reports/audit_p1_l3.log` (sha256 `700315F4…`),
  JSON `reports/audit_p1_l3_results.json` (sha256 `85056681…`);
  log resmi **byte-identik** dengan smoke-2 (skrip deterministik;
  guard LOG-EXISTS). Transkrip pra-run disimpan: smoke1 (6 cek gagal —
  3 bug implementasi check/needles, dicatat apa adanya, sha256
  `95F55BFE…`) + smoke2 (bersih). Laporan:
  `reports/AUDIT_DBN_L3_2026-10-17.md`.
- **Coverage L3 (beku, di JSON `boundary`):** kebenaran teorema
  terbitan tidak direview (statement + pemetaan yang di-weld); reduksi
  analitik paket (Dini all-y, limit t=0, native binding,
  derivative-box/tail) tidak dibuktikan ulang; full text Bull. LMS
  (refereed) tidak dapat diakses fetch scripted (403) — hanya record
  bibliografi; v2 Polymath = "final version" per record arXiv
  (pagination typeset tidak dibandingkan); snapshot arXiv dated
  2026-10-17; lane rilis tidak di-re-run (verdict item 1–4 dikonsumsi
  dari log ter-commit).
- **Berikutnya (saat itu): L4** → lihat §2.0k (L4 + registry P3 SELESAI).

### 2.0k [BARU, 2026-10-17] P1 audit — L4 (verdict final) + registry P3 SELESAI

- **Laporan:** `reports/AUDIT_DBN_L4REPORT_2026-10-17.md` — struktur
  template reviewer rilis (recon §7.12) dengan field wajib terisi dari
  log: commit `2e9976c4…`; os Microsoft Windows 10 Pro 10.0.19045;
  Python 3.14.4; **stored checks PASS** (gate blob in-run per item:
  3/7/10/11 sumber + L3 14 gate; PDF referensi byte-identik
  `60d0d2d3…`/`3362f66a…`); **container checks NOT RUN** (tanpa engine;
  stop rule §3.4). Overall assessment (pilihan template) =
  `plausible but incomplete` — dibaca sebagai status penilaian KITA
  (semua lane yang dieksekusi lolos; bagian di luar scope terenumerasi).
- **Tabel per-obligasi (ID blueprint rilis P1/P2/P3/G1/F1/F2/F3/T1/T2/
  B1/B2/C1):** 8 `accepted` (P1, P2, G1, F1, T1, B1, B2, C1) +
  4 `unresolved` resource-bound (P3, F2, F3, T2 — tanpa eksekusi
  independen; masuk agregat UNVERIFIABLE-WITH-OUR-RESOURCES);
  0 `rejected`; kolom L1 = "—" di semua baris (L1 not-run). Verdict L3
  dikutip apa adanya: (i)/(ii)/(iii) `compatible`; weld `HELD`; 57/57.
- **Coverage 9 butir:** L1 stop-rule; full sweep optional; item 2
  jendela tersampel; item 3 titik desain; item 4 descriptor/subset;
  batas L3 (incl. Bull. LMS 403, bracket π sekunder, reduksi analitik
  tidak dibuktikan ulang); gate Lean berlabel AUXILIARY (rilis 0
  `.lean`; `lean/` di `a74738de`; scan 25 berkas PASS; self-test
  13/13); verifier rilis tidak di-re-run; kesegaran target (watch
  bersih).
- **Agregat:** GAP-FOUND = **none**; INDEPENDENTLY-CERTIFIED = item 1–4
  (34/34, 48/48, 47/47, 124/124) + L3 (57/57) di stack kita; 
  UNVERIFIABLE = L1 replay, F2/P3/T2/F3, sapuan penuh (baris/prisma),
  full text referee.
- **Registry P3 `reports/FENCE_REGISTRY.md`:** skema (ID/Jenis/
  Pernyataan/Batas/Sertifikat/Status/Domino/Relasi; baris sertifikat
  `sha256LF <hex> <path>` = sha256 LF-normalised, platform-stabil) +
  6 entri awal: T-2026-0001 (ladder Route S positif-tertutup dim
  201/301), T-2026-0002 (λmin 321), F-2026-0001 (S2 seri Montgomery
  201/301/401), F-2026-0002 (OUTCOME dim 501), T-2026-0003 (replikasi
  Engine B 18/18), A-2026-0001 (**verdict audit P1**; 23 berkas
  sertifikat termasuk laporan L4). Entri tidak pernah dihapus;
  perubahan = status/relasi/catatan.
- **Guard CI fail-closed:** `msaf/tests/test_fence_registry.py` — tiap
  baris `sha256LF` diverifikasi (berkas ada + hash cocok); entri
  CERTIFIED wajib ≥1 baris sertifikat; heading wajib skema; ≥6 entri.
  Suite lokal: **355 passed** (302.48 s).
- **P1 audit PRA-REG TUNTAS** (setiap langkah dieksekusi atau tercatat
  not-run dengan sebab). Owner-gated yang menunggu keputusan: (a)
  dashboard v6 (v3/v4/v5 tetap beku); (b) Scope Note recording;
  (c) instalasi engine container untuk replay L1.

### 2.0 [BARU, 2026-10-15] Dua silent-pass di kernel penghitung nol — sudah diperbaiki

`msaf/certify.py` mengesahkan `nan` sebagai nol (Arb menjawab True untuk
`arb('nan').contains(0)`), dan `msaf/zeta_inversion.py` mengembalikan
`nan` tepat di s = 0 dan s = 1. Keduanya diperbaiki di commit `c4f4e4a`
dengan identitas eksak, bukan tabel nilai; 311 tes hijau. Laporan penuh
+ residual terbuka (presisi global bocor di 4 modul tes lama):
`reports/NONFINITE_DEFECT.md`.

### 2.1 the-asymmetric-wager-msaf: branch audit belum di-merge, WIP user ada

- **Lokal** `D:\THE ASYMMETRIC WAGER` ada di branch `audit-fixes-bmw`
  pada `1eb28bb`. **Tiga commit audit belum ada secara lokal** —
  `66310cf`, `04405ba`, `b9958be` (ada di remote). Mustahil di-merge
  sekarang: working tree penuh WIP user yang tumpang tindih.
- **WIP user yang tidak boleh diklampaui** (dimulai A23, masih belum di-commit):
  `A16_REPORT.md`, `Brain.MD`, `CHECKSUM.sha256`, `README.md`,
  `Skill.md`, `checksum_check.py`, `harness_check.py`, `suite_check.py`.
- Untracked baru ( progresiva, jangan dihapus): `A24_REPORT.md`,
  `A25_REPORT.md`, `A26_REPORT.md`, `harness/`, `h1_escape_gate.py`,
  `math-main/`, `openai_math_audit/`, `OMEGA N800 EVIDENCE KIT/`, dan
  lain-lain.
- **Langkah berikutnya kalau repo ini mau ditutup:** user commit WIP-nya
  dulu di `main`, baru `git merge audit-fixes-bmw`. Merge akan konflik di
  `CHECKSUM.sha256` dan `Brain.MD` (keduanya berubah di kedua sisi) —
  setelah merge, jalankan `python checksum_check.py --update` lalu
  `python report_claim_check.py`, karena kedua gate itu yang mengikat
  angkanya.

### 2.2 Suite the-asymmetric-wager-msaf tidak akan hijau di clone kosong

Terbukti dan sudah diperbaiki akarnya (`B-MW5`): empat gate butuh Z3
atau corpus pihak ketiga `Theory_of_Everything_Derivations/` yang
di-`.gitignore`. Di clone kosong: 12 ok, 1 FAIL_sebelum-perbaikan (kini
TOOL NOT RUN), 3 NOT RUN → suite `INCOMPLETE`. Itu perilaku yang benar,
bukan regresi. Di workspace penulis (corpus ada) suite jalan penuh.
Bukti keluaran bersih: `reports/TAW_clean_worktree_suite.txt`.

### 2.3 Jembatan Riemann `CORR-MOORE-COMPLEX` — plans were WRONG, read this

Satu-satunya hal yang secara logis menghalangi trek RH. **Rencana lama
("formalkan gate Moore kompleks di Lean") keliru dan sudah dikoreksi.**

`moore_test` di `lean/NewtonExistence.lean:473` dinyatakan atas interval
**ℝ**: `f : ℝ → ℝ`, kesimpulan `∃ z ∈ Set.Icc a b, f z = 0`. Nol yang
dihitung program ada di bola **kompleks** di garis kritikal, dan ξ tidak
punya nol real. Jadi transfer C→R bukan sekadar "belum diformalisasi" —
secara struktural mustahil sebagai pernyataan itu berdiri. Menutupnya
 berarti memformalkan Moore atau prinsip argumen **di ℂ**: pengembangan
Lean baru, bukan porting.

Konsekuensi urutan yang disarankan:

1. Tutup RH dengan **batasan terukur, bukan jembatan**: buktikan di Lean
   bahwa ξ tidak punya nol real (maka sertifikat real mustahil ada),
   lalu segel RH sebagai PARTIAL dengan landasan yang jujur dan disebut:
   "ball arithmetic + winding cross-check". Hasil yang bisa disegel.
2. Masukkan "Moore/Rouché di ℂ di Lean" ke **B-list** sebagai prasyarat
   kapabilitas — pola yang sama dengan "integrator ODE tervalidasi"
   yang sudah tercatat di `DAFTAR_MASALAH_KERJA.md` §4.
3. Baru Q1 BSD, dan pilot terukur lebih dulu. Bukti bahwa jalur ini
   terpisah: `msaf/hodge/weil_search.py` tidak memanggil
   `evaluate_xi`, jadi pekerjaan F₃ dan kernel ξ tidak berinteraksi.

---

## 3. Zenodo: delivery T-hat-N diamankan via API; webhook tetap opsional

- **2026-10-16: delivery T-hat-N terdeposit di Zenodo** lewat jalur
  depositor API (`msaf/zenodo_deposit.py`, commit `3305221`) sebagai
  VERSI BARU record T-hat-N: DOI versi `10.5281/zenodo.23410894`
  (konsep `10.5281/zenodo.23338271`). Rantai konsep utuh: `v1.1.0`
  (23338272) → `v1.2.0` (23340971) → `v1.40.0-alpha` (23410894).
  Arsip = tarball commit `a37b50b` sha256
  `44bdfb87788b1f1da687b2d8e852641385b5c80de99c072768f6b67120198f61`
  (546.800 byte; md5 file di Zenodo cocok byte-exact); CI hijau di
  commit arsip (`38854261266` / `38854493402`).
- Draft `23410894` dibuat 2026-10-16 06:35 UTC (lewat UI; kemungkinan
  percobaan pemilik), lalu difinalkan sesi ini: deskripsi draft lama
  (teks "v1.2.0" warisan versi sebelumnya) diganti ke format teraudit;
  cadangan JSON di luar repo.
- Jalur kanonik webhook (GitHub release → DOI otomatis) tetap
  **tidak aktif** — hanya pemilik via login browser
  (zenodo.org → Settings → GitHub → Enable). Release GitHub dibuat
  manual via `gh` dan TIDAK memicu Zenodo tanpa webhook: `v1.1.0`
  (2026-10-13) dan `v1.40.0-alpha-final-certified-delivery`
  (2026-10-16, Latest). Panduan aktivasi (untuk auto-arsip rilis
  BERIKUTNYA): `docs/ZENODO_ACTIVATE.md`.
- 10 repo publik masih tanpa DOI (menunggu audit, sesuai keputusan
  operator: deposit hanya repo yang gate-nya hijau & CI hijau):
  AETHER-Z3-OMEGA, ASLC-OMEGA-LEDGER, gnase-engine,
  jacobian-conjecture-audit, lagarias-criterion, navier-stokes-formalization,
  riemann-hypothesis-formalization, sovereign-enterprise-suite,
  the-asymmetric-wager-msaf-family017, zeta-23-audit.

---

## 4. Peta file (jangan menebak)

| Isi | Lokasi |
|---|---|
| Audit 4 repo + Zenodo | `reports/REPO_AUDIT.md` |
| Triage 3 jembatan (merah-team) | `reports/ADVERSARIAL_TRIAGE.md` |
| Antrean 20 masalah + aturan main | `reports/DAFTAR_MASALAH_KERJA.md` |
| Closure Hodge | `reports/HODGE_CLOSURE.md`, `reports/HODGE_CH_SPEC.md` |
| Roadmap formalisasi | `reports/TURING_ROADMAP.md` |
| Berek RH | `msaf/riemann/` (`winding.py`, `counter.py`, `moore_premises.py`, `boundary.py`, `exclusion.py`) |
| Berek Hodge | `msaf/hodge/` (`weil_search.py`, `fermat_k3.py`, `gauss_exact.py`) |
| Berek NS | `msaf/navier_stokes/`, kernel `lean/NavierStokesCore.lean` |
| Kernel RH | `lean/NewtonExistence.lean` |
| Test suite (311) | `msaf/tests/` |
| Konsolidasi manuskrip (ekspor LaTeX) | `exports/research_paper.tex` |
| Pra-registrasi amandemen lantai H1 (DIBEKUKAN) | `reports/AMENDMENT_FLOOR_SPEC.md` |
| Template release delivery akhir | `reports/RELEASE_v1.40.0-alpha-final-certified-delivery.md` |
| Panduan aktivasi webhook Zenodo | `docs/ZENODO_ACTIVATE.md` |
| Bukti JSON | `reports/*.json` |

**Artefak user yang SUDAH DIHAPUS (atas perintah pemilik, 2026-10-15):**
`20_masalah_matematika_fisika_tersulit.md` dan `reports/diagram.txt`
— keduanya tidak pernah ada di riwayat git, jadi penghapusannya permanen
dan tidak dapat dibatalkan. Tidak ada pengetahuan yang hilang: disposisi
kedelapan belas masalah sudah tercermin penuh di
`reports/DAFTAR_MASALAH_KERJA.md` §2, dan `diagram.txt` hanya diagram
ASCII dua jalur yang sudah usang. Jangan cari-cari keduanya di repo.

---

## 5. Disiplin yang harus dilanjutkan

1. Ball/integer eksak saja, `_reject_float()`, tanpa klaim tak terbatas.
2. PARTIAL/INCONCLUSIVE harus keras dan kedengaran.
3. Jangan pernah menambal titik buta — perbaiki akarnya, dokumentasikan
   kalau memang tidak bisa.
4. Segel = test hijau → docs/register sinkron → commit + tag + push →
   CI hijau. Tidak ada tag untuk dokumen rencana saja.
5. Kesalahan proses dicatat, disembunyikan tidak. Contoh yang sudah
   tercatat: patcher reflow CRLF→LF diam-diam (A12_REPORT.md, sudah
   dikembalikan); `git add -A` menyapu `MSG.txt` (CI yang menangkap);
   penulisan laporan mode-teks Windows yang menggandakan CR (`\r\r\n`,
   terdeteksi lewat diff seluruh baris; `msaf/gw_resolution_delta.py`
   kini menormalisasi line-ending dan menulis byte eksak).

## 6. Jebakan lingkungan (hemat waktu sesi depan)

- PowerShell tidak punya `grep`/`head`/`cat <<EOF`/`&&`. Pakai
  `Select-String`, `Get-Content`, file sementara untuk patch.
- `git commit -F` **gagal** kalau path mengandung spasi — tulis pesan
  commit ke file di `C:\Users\usER\AppData\Local\Temp\opencode\`, jangan
  menyalinnya ke dalam working tree sebelum `git add -A`.
- Lean 4 v4.33.1 + Mathlib. Verifikasi nama lemma terhadap Mathlib
  terpasang; several tidak ada
  (`div_nonpos_of_nonneg_of_nonneg`, `pow_le_pow_of_le_right`,
  `mul_le_of_le_one_right`, `div_le_one_of_le`) — yang ada antara lain
  `div_nonpos_iff`, `Nat.le_self_pow`, `mul_le_mul_of_nonneg_left`.
- Edit regex berbackslash dari shell rapuh → tulis skrip patch ke file.
- `TEMP\opencode\repofix\` = klon sementara 4 repo anak + worktree TAW.
  **Semua isinya sudah dipush**; hilang di sana tidak berarti hilang.
- Token (status 2026-10-17): nilai plaintext TIDAK PERNAH ditulis ke
  repo/chat/log. Keduanya tersimpan sebagai blob terenkripsi DPAPI
  (scope user) di luar repo: `%USERPROFILE%\.config\zenodo_token.sec`
  dan `%USERPROFILE%\.config\github_token.sec`; dekripsi hanya di titik
  pakai, nilai tidak di-echo. GitHub auth juga lewat keyring `gh`.
  Token Zenodo lama (64 char) sudah dicabut; token baru (60 char) valid
  (keduanya diverifikasi API). Rotasi ditunda ke akhir proyek.
- CI T-hat-N: sensor escape-token di `.github/workflows/ci.yml` wajib dua
  glob — kernel (0 hit, termasuk `axiom`) dan spec (`lean/spec/`: tanpa
  `sorry/admit/unsafe`, anggaran axiom dibekukan = 9). Axiom ke-10 di
  spec = CI merah sampai ci.yml diedit sengaja.
- `msaf/mont_run.txt` (log dim 401) ber-UTF-16 dengan BOM — baca eksplisit
  `decode('utf-16')` (atau `type` via cmd). Log dim 201
  (`reports/mont_run_100_100.txt`) dan dim 301 (`reports/mont_run_100_150.txt`,
  `reports/gw_capture_100_150.log`) UTF-8 murni tanpa BOM, CRLF.
- Urutan `eig` di spectrum JSON = urutan mentah keluaran flint (tidak
  terurut global; dim 201/301 sama polanya). Gate `G-M0c` memeriksa
  multiset terurut dan `gw_montgomery.py` menyortir saat baca — jangan
  "memperbaiki" urutan berkas.
