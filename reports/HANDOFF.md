# HANDOFF — titik sambung untuk sesi berikutnya

Ditulis 2026-10-15, akhir sesi repo-audit + Zenodo.
**Update 2026-10-16:** resolusi kedua (dim 201) dan ketiga (dim 301) diukur;
sensor CI diperbaiki di akar; jawaban "mengecil atau membesar" di §2.0b dan
`reports/THREE_TASKS_2026-10-15.md` §4 + §5 (seri tiga titik 201/301/401,
dashboard `reports/gw_diagnostic_v3.html`).
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
| Seri tiga titik dim 201/301/401 + §5 + dashboard v3 | commit yang membawa baris ini | `reports/THREE_TASKS_2026-10-15.md` §5, `reports/gw_diagnostic_v3.html` |

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

## 3. Zenodo: jalur kanonik masih tertutup

- Jalur kanonik (GitHub release → DOI otomatis) **tidak aktif**:
  akun GitHub punya **0 release di 15 repo publik**, dan webhook
  Zenodo↔GitHub hanya bisa diaktifkan pemilik lewat login browser
  (zenodo.org → Settings → GitHub → Enable). Tidak ada API token yang
  bisa melewati ini.
- Jalur yang dipakai: `msaf/zenodo_deposit.py` (depositor API, menolak
  mengarang lisensi/klaim, mencatat sha256, retry saat upload putus).
- 11 repo publik masih tanpa DOI (menunggu audit, sesuai keputusan
  operator: deposit hanya repo yang gate-nya hijau & CI hijau):
  AETHER-Z3-OMEGA, ASLC-OMEGA-LEDGER, T-hat-N, gnase-engine,
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
- GitHub auth lewat keyring `gh` (tanpa token). Token Zenodo hanya
  berlaku di dalam sesi tempat user give — jangan tulis ke berkas
  mana pun.
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
