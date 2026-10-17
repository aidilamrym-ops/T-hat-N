# HANDOFF — titik sambung untuk sesi berikutnya

Ditulis 2026-10-15, akhir sesi repo-audit + Zenodo.
**Update 2026-10-16:** resolusi kedua (dim 201) dan ketiga (dim 301) diukur;
sensor CI diperbaiki di akar; jawaban "mengecil atau membesar" di §2.0b dan
`reports/THREE_TASKS_2026-10-15.md` §4 + §5 (seri tiga titik 201/301/401,
dashboard `reports/gw_diagnostic_v3.html`; README §6 memuat peta jalan
kampanye + rumus instrumen lengkap). **Konsolidasi 2026-10-16:** manuskrip
`exports/research_paper.tex` (Main Spectral Results + register cacat,
transkripsi artefak tersegel saja) ditambahkan; dashboard v3 diuji ulang
byte-stabil; delivery akhir ditandai tag `v1.40.0-alpha-final-certified-delivery`. **H0 lockdown (2026-10-16):** `docs/ZENODO_ACTIVATE.md` (panduan aktivasi webhook Zenodo) + template release + pra-registrasi amandemen lantai `reports/AMENDMENT_FLOOR_SPEC.md` (DIBEKUKAN, sha256 di §1) disegel; TIDAK ada komputasi baru dijalankan. **Deposit + release (2026-10-16):** delivery T-hat-N diamankan sebagai VERSI BARU record Zenodo via depositor API — DOI versi `10.5281/zenodo.23410894` (konsep `10.5281/zenodo.23338271`; arsip tarball commit `a37b50b`, sha256 `44bdfb87...`); release GitHub `v1.40.0-alpha-final-certified-delivery` diterbitkan via `gh`; skrip depositor diperluas (`--date`/`--version`, commit `3305221`). **H1 amandemen lantai (2026-10-16):** bagian (A)+(B) dari `reports/AMENDMENT_FLOOR_SPEC.md` (DIBEKUKAN) dieksekusi penuh — grid refined 20000 surrogat + array robustness C4 5-seed; hasil terukur, klasifikasi beku (NOT STABLE), dan falsifikasi ekspektasi pra-registrasi di §2.0c dan `reports/AMENDMENT_FLOOR_RESULTS.md`; manuskrip `exports/research_paper.tex` diamandemen bertanggal (section sebelum register cacat + pointer abstrak + catatan header). (C) engine B = sesi berikutnya. **H1 (C) engine B SELESAI (2026-10-17):** verifikasi independen S2 run penuh 20000 sampel — verdict `PASS-WITH-ENUMERATED-EXCEPTIONS`, counts 18/18 eksak vs engine A (exit 0, 9062 s); log + JSON tersegel di repo, riwayat interupsi R1/R2 di `reports/ENGINE_B_PILOT_FINDINGS_2026-10-16.md`, rincian §8 `reports/AMENDMENT_FLOOR_RESULTS.md`. **README publikasi (2026-10-17):** README.md diperbarui — banner terbaru penutupan H1, Section 7 baru (peta alur kerja + rantai verifikasi + blok status mesin + "verify it yourself"); blok status dan 2 diagram SVG digenerate `msaf/gw_readme.py` HANYA dari artefak tersegel (hash + byte-count LF-normalised), dijaga `msaf/tests/test_readme_guard.py` (drift = CI merah); commit `90a6520`, perbaikan byte-count checkout-stable `c957503` (run pertama `38975016984` GAGAL — kolom bytes pakai st_size mentah, CRLF vs LF CI; diperbaiki di akar + disimulasikan di worktree LF lokal); CI hijau run `38975450198`; suite 345 passed. **Dashboard v5 (2026-10-17):** halaman v5 dibangun DI ATAS v4 byte-identik (v4 disegel sebagai preserved — sha256 penuh di panel 6 v5 + dipin `msaf/tests/test_gw_dashboard_v5.py`); 14 patch deterministik terdokumentasi + 2 panel baru (Panel 7: grid refined H1 + array 5-seed dengan grafik seed baru; Panel 8: census 720 bin engine B + counts 18/18 eksak + provenance); semua angka diekstrak mesin saat build; suite 349 passed.
**Sesi berikutnya: baca berkas ini dulu**, lalu `reports/REPO_AUDIT.md`
(§1–4 verdict, §6–10 perbaikan tersegel) dan
`reports/DAFTAR_MASALAH_KERJA.md` (antrean 20 masalah).

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
| Dashboard v5 — ekstensi H1 + engine B di atas v4 byte-identik | commit yang membawa baris ini; dibangun di atas `9af033b`; v4 preserved sha256 penuh `C9EC26217F516A1A73527BC098ADBC11A4935F6965D905D38A7DBEB7D95A8B6` (embed di panel 6 v5 + dipin test guard); v3 tetap `89C7D5F948626BD51DE06F37534BDC4941D3793353DCB80B8557E10E2BED7322`; 14 patch deterministik + Panel 7/8 (H1 refined grid, array 5-seed, census 720 bin engine B, counts 18/18 eksak); suite 349 passed | `reports/gw_diagnostic_v5.html`, `msaf/gw_dashboard_v5.py`, `msaf/tests/test_gw_dashboard_v5.py`, `msaf/gw_readme.py`, `README.md` |

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
  8.569e-35 (33), 2.259e-49 (65), 6.321e-59 (129) — radius **tepat nol**,
  Im bocor **tepat nol**. Lereng `ln λ_min` per dimensi: −1,72 → −1,05 →
  −0,34, jadi `A·e^(−Bn)` dengan B konstan **terbantah** pada irisan ini.
  ⚠️ hanya satu irisan (c=13);across-c bukan apel-samel.
- **9000 bit terbukti tidak menambah apa pun**: nilai identik
  bit-dengan-bit dengan 6000 bit, radius tetap 0, biaya 2,6×.
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
- **Urutan berikutnya yang masuk akal:** (1) anak tangga λ_min lebih
  panjang kalau arah B mau dipastikan (dim 257/321; 321 belum tuntas);
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
