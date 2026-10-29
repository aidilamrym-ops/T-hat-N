# Audit Titik-Buta: Empat Repo Milik Kita (review read-only, tanpa unduh)

Tanggal: 2026-10-15. Metode: baca via API (metadata, listing, file),
tanpa menjalankan kode mereka, tanpa menulis ke repo mana pun.
Standar which dipakai persis standar which dipakai ke diri sendiri:
klaim = saksi mesin + scope tertulis; sisanya marked.

Legenda: **[B-*]** blind spot (butuh perbaikan) Â· **[S-*]** kekuatan
(diakui, diadopsi bila cocok) Â· tingkat: kritis / sedang / ringan.

---

## 1. anti-turing-pnp â€” verdict: teorema benar, entailment no ada

**[S-AT1]** 6 teorema Lean adalah analisis elementer which benar
(positivitas/limit sigmoid, penghitungan indikator, 2^n > 1).
Hasil Z3 UNSAT atas enkoding ODE juga dibaca apa adanya: benar
on level enkodingnya.

**[B-AT1] KRITIS â€” no ada definisi P, NP, SAT, waktu-polinomial,
reduksi, or Cook-Levin in rantai bukti.** Berkas lengkap already
dibaca (`AntiTuringCore.lean`): objeknya `VectorFieldLTC`,
`tau_LTC`, `bypass_selector`, `DiscreteTuringStep`. Ketidakhadiran
total kosakata kompleksitas membuat "resolusi P vs NP" no
ter-derive secara prinsip, bukan karena kurang step. O(1)
kontinu â‰  O(1) Turing (model analog; result literatur komputasi
analog justru menunjukkan presisi tak terbatas menyelundupkan
infinity kembali â€” ironis for repo anti-infinity).
Rekomendasi: turunkan headline ke "continuous relaxation bounds"
(ini which sebenarnya dibuktikan), ATAU formalkan jembatan
Cook-Levin (proyek raksasa). Alasan: klaim tanpa jembatan adalah
klaim tanpa rantai bukti â€” kelas which sama with which kita tolak
in repo sendiri.

**[B-AT2] SEDANG â€” sel "0 axiom" tak terverifikasi.** Berkas membuka
`open Classical`, memakai `Real.sqrt`/`Real.exp` Mathlib
(noncomputable). Prediksi terukur: `#print axioms` menghasilkan
tiga aksioma standar (persis seperti audit 73/73 kita) â€” artinya
sel itu berarti "tanpa deklarasi axiom", BUKAN "tanpa ketergantungan
aksioma". Rekomendasi: jalankan audit `#print axioms` (pola kita,
30 detik) and tulis ulang selnya. Alasan: sel which salah membaca
membuat seluruh matriks audit diragukan.

**[B-AT3] RINGAN â€” drift dokumen vs kode.** Laporan bilang 5 teorema;
file memuat 6 (`continuous_energy_decreasing` tak terdaftar).
Rekomendasi: hitung teorema secara mekanis (regex `^theorem`),
jangan tulis tangan. Alasan: ini persis kelas bug "baris-G1-basi"
which pernah kita miliki.

**[B-AT4] RINGAN â€” konstanta mati / klaim dimensi.** `StateDim := 42`
didefinisikan tapi struktur hanya punya 4 field (w1..w4); "for n
klausa" no terhubung ke 42. `bypass_selector` disebut "lim" tapi
tak ada limit which diformalkan (jumlah 4 indikator). Rekomendasi:
parameterisasi dimensi or dokumentasikan 4 sebagai instans;
ganti nama "lim" or formalkan limitnya. Alasan: nama which
melebihi isi adalah klaim which belum dibayar.

**[B-AT5] SEDANG â€” skrip Z3 verifying enkoding, bukan kompleksitas.**
`UNSAT` atas konsistensi ODE â‰  limit atas/bawah kompleksitas.
Rekomendasi: note scope satu baris per batch (apa which in-encode,
apa which TIDAK disimpulkan). Alasan: tanpa itu pembaca mengira
tribunal memutuskan P vs NP.

Disposisi queue TETAP: B-list formalisasi-saja. Satu-satunya
kontribusi jujur repo ini ke P-vs-NP adalah merumuskan presisi
GAP-nya â€” and itu pekerjaan mereka, bukan kita.

---

## 2. gw-spectral-map â€” verdict: teladan disiplin, temuan ringan

**[S-SM1]** Diakui and patut ditiru: two-engine with vetting
ambiguitas eksplisit, exit code fail-closed (0/1/2), artefak KILLED
disimpan sebagai rekor jujur, result negatif S2 dilaporkan
(INCONSISTENT WITH MONTGOMERY â€” bukan disembunyikan), analisis biaya
level-0 vs level-1 sebelum kampanye, resume JSONL terverifikasi.

**[B-SM1] SEDANG â€” basis data verdict S2 no berprovisional.**
Status S2 INCONSISTENT dikutip, tapi kampanye penuh masih QUEUED in
belakang OMEGA; pembaca tak bisa tahu artefak hash apa which memberi
makan verdict itu. Rekomendasi: tiap verdict menunjuk hash artefak
data (pola sama with digest transkrip pivot mereka). Alasan:
verdict tanpa data-pin adalah kalimat, bukan sertifikat.

**[B-SM2] RINGAN â€” konstanta vetting `ambig = 1e-6 * scale` heuristik.**
Sudah dimitigasi (cluster certificate for zona ketat), tapi
s sixty sensitivitasnya tak tercatat. Rekomendasi: catat variasi
ambig Ã—/Ã·10 on selftest and tunjukkan verdict stabil. Alasan:
konstanta tanpa uji sensitivitas adalah asumsi which belum dibayar.

**[B-SM3] RINGAN â€” konvensi endpoint bracket tak tertulis.**
`N(mu) = n_neg` menghitung strictly-below; bracket "(lo,hi]"
with eigenvalue TEPAT in endpoint butuh konvensi which dicetak.
Undetermined-pivot menanganinya operasional, tapi dokumen harus
menyatakannya. Rekomendasi: satu paragraf konvensi + satu uji
eigenvalue-in-tepi. Alasan: ambiguitas konvensi adalah blind spot
klasik penghitung interval.

**[B-SM4] RINGAN â€” `results/` tanpa manifest.** Enam JSON + rekor
KILLED, tapi tak ada CHECKSUM/manifest terlihat (praktik which justru
ada in repo saudaranya). Rekomendasi: port praktik manifest ke sini.
Alasan: artefak tanpa manifest bisa diganti diam-diam.

---

## 3. guinand-weil-rigorous-numerics â€” verdict: pola kelas-satu, 2 lubang

**[S-GW1]** Diakui: cross-check literal READMEâ†”Lean via regex (tak
percaya salinan tangan); file SMT single-assert which kompatibel
with auditor sirkularitas + tujuh run individual (pelajaran
VACUOUS mereka documented!); analisis diskrepansi which JUJUR
(`tolerance_fails_the_coarse_bound` â€” teorema which menyatakan kapan
angka report TIDAK cocok, for mengidentifikasi norma which
dipakai); exit code 0/1/2/3; artefak SMT+log ter-commit; status tool
per-run (coqc/isabelle/dkcheck/gcc NOT RUN â€” ditulis, bukan disembunyikan).

**[B-GW1] SEDANG â€” cross-check literal memeriksa KEBERADAAN, bukan
ATRIBUSI.** `ok = (mant, exp10) in readme_set`: pasangan digit
cukup MUNCUL in README in mana saja â€” angka rhoActual which tertulis
in paragraf which salah (topik lain) tetap MATCH. Rekomendasi:
jangkarkan per-konstanta (nama konstanta dalam N baris dari angka,
or posisi seksi). Alasan: existence â‰  attribution; lubang kecil,
probabilitas rendah, tapi tepat in gerbang which mengklaim ketepatan.

**[B-GW2] SEDANG â€” pasangan Leanâ†”SMT manual.** Komentar "keep names
identical so a reader can pair them up" = pairing oleh mata.
Rekomendasi (murah, pola kita): uji mekanis dua arah â€” setiap nama
in CLAIMS ada in .lean, and setiap teorema `norm_num` in .lean ada
in CLAIMS (klaim tanpa pasangan = klaim tanpa audit). Alasan:
drift pasangan adalah versi lain dari bug baris-basi kita; which
menangkapnya harus mesin (`audited == found` â€” mereka belum punya
bentuk ini for pasangan klaim).

---

## 4. the-asymmetric-wager-msaf â€” verdict: gate prosa paling matang which
pernah saya baca; pengencangan, bukan perbaikan

**[S-MW1]** Diakui: exit 2 tak-pernah-pass; vocabulary self-guard
(generator which salah menghentikan gate, bukan memiringkannya);
manifest memeriksa tally-nya sendiri; deteksi ghost dua arah (P6);
map_check P8; tiap pola disertai komentar pelajaran dari miss
terdahulu (A16-R1, F8-R1, tally_object ordering). Ini in atas praktik
kita for gate prosa â€” no ada which setara in repo kerja.

**[B-MW1] SEDANG â€” jangkar `now`, `F\d`, `A\d` terlalu permisif.**
`anchor_window` memvalidasi SELURUH angka in baris bila SATU jangkar
ada in Â±1 baris â€” and `\bnow\b` ("now" = kini!) mengesahkan riwayat.
Baris "now 13 gates" with angka basi lolos. Rekomendasi: jangkar
hanya tag eksplisit (tanggal/fase/versi), ATAU kedekatan per-klaim
(jangkar dalam N karakter dari angka). Alasan: jangkar which longgar
mengubah gate presisi menjadi gate perasaan; catat biaya
false-positive bila diketatkan.

**[B-MW2] RINGAN â€” file non-UTF8 dilewati diam-diam.**
`readable()` None â†’ `continue` in `dated_claims` (hanya BRAIN which
dijaga exit-2). Dokumen .md non-UTF8 with angka basi lolos lewat
omisi. Rekomendasi: catat SKIP eksplisit per file. Alasan: omisi
diam-diam adalah bentuk pass-diam-diam.

**[B-MW3] RINGAN â€” siapa mengawasi pengawas.** Pola klaim baru in
luar pola which ada lolos by-design (tak ada pola = tak ada klaim
terbaca). Mereka menjawab sebagian (komentar tiap miss), tapi tak
ada suite fixture-negatif which terlihat in listing (tak ada dir
tests/ in root; `harnesses/` belum diperiksa isinya).
Rekomendasi: suite fixture which HARUS gagal (pola anti-circularity
kita punya `tests/run_tests.py` 11 kasus sebagai contoh) + entri CI.
Alasan: gate tanpa negatif which gagal adalah gate which tak bisa
dibuktikan hidup â€” pelajaran which KITA petik with cara keras
(audit 0 deklarasi).

---

## 5. Yang diadopsi kembali ke repo kerja (result audit ini)

- **[ADOPT-1]** Praktik manifest for directory artefak: `results/`
  mereka (and `reports/*.json` KITA â€” artefak trace kuartik!) belum
  punya CHECKSUM. Dicatat sebagai peningkatan antrian, bukan klaim.
- **[ADOPT-2]** Bentuk `audited == found` for pasangan klaim
  (pelajaran B-GW2) â€” already kita miliki for aksioma Lean; spek CH
  kita (combiner vs klaim) akan mengikutinya.
- **[ADOPT-3]** Sel status-tool per-run (NOT RUN ditulis eksplisit,
  pola OMEGATrackC) â€” diadopsi for run berat kita (offline k=10
  already mencatat elapsed; format diselaraskan berikutnya).
## 6. FIXES APPLIED â€” anti-turing-pnp (2026-10-15, pushed, CI green)

- Kernel builds green LOCALLY (`lake env lean`, exit 0, no warnings)
  and REMOTELY (`lake build`, 8707 jobs, exit 0); `#print axioms`
  6/6 = exactly propext/choice/Quot.sound (measured in-repo, not
  inferred).
- lakefile rewritten to the current Lake DSL (`open Lake DDList` had
  been removed from Lake; no modern lake could parse the config) +
  mathlib pinned @ v4.33.1 (manifest rev == tag sha, verified);
  lake-manifest.json committed; `.gitignore` + CI added.
- 4 proofs repaired (lemma names absent from Mathlib v4.33.1; one
  removed step unprovable-false at zero gradient; GT/LT instance
  matching; atom-orphaning `dsimp` + `linarith` closer).
- B-AT1: headline scoped to relaxation bounds + GAP-PNP.md (G1-G4);
  entailment still open BY NATURE (no bridge exists here).
- B-AT2: cells read the measured footprint. B-AT3: 6, mechanical.
  B-AT4: StateDim deleted; finite-sum naming. B-AT5: batch scope
  notes (batch 2 = n >= 100 instance; Lean covers general n >= 1).
- Z3 scripts fail-closed (exit codes); both batches re-ran UNSAT.
- CI history kept honest: one sensor trip (slogan prose matched the
  token pattern -- fixed by rewording, discipline documented), one
  transient download failure (rerun green). Neither hidden.
- The provided tokens were NOT used (gh keyring auth sufficed);
  owner to revoke them regardless.

## 7. FIXES APPLIED â€” gw-spectral-map (2026-10-15, pushed, CI green)

- B-SM1: S1/S2 verdict lines now point at the producing machinery
  (OMEGA gw_montgomery.py:562 + K5 fixture gw_mont_pipeline_check.py:195,256)
  and state the certified-spectrum re-run is QUEUED.
- B-SM2: ambig sensitivity MEASURED (17/17 + 0 conflicts at 1e-7/1e-6/1e-5;
  only granularity moves 9/1, 8/1, 7/1) â€” recorded, not assumed.
- B-SM3: endpoint-convention test 5/5 PASS (exact-hit -> UNDETERMINED;
  strict-below exact); convention documented in NOTES section D.
- B-SM4: results/MANIFEST.sha256 + stdlib verifier (roundtrip green).
- CI added (py_compile + sm_dual + manifest + endpoint loud-SKIP +
  sibling-gated selftests). CI history honest: one CRLF/LF manifest
  failure (all 7 files flagged drifted on Linux checkouts) fixed at
  the root (LF-normalized hashing â€” immune to checkout style).
- Verified locally first: sm_dual PASS, sturm 10/10, brackets 17/17
  (matches README), endpoint 5/5 â€” via a sibling tree wired in temp
  (nested copy), both repos otherwise untouched.

## 8. FIXES APPLIED â€” guinand-weil-rigorous-numerics (2026-10-15, pushed, CI green)

- B-GW1: cross-check now requires ATTRIBUTION (full-precision pair
  within +-3 lines of a naming line, narrow per-constant patterns);
  verified 3/3 attributed MATCHes on unmodified files. A backslash-
  counting scare during implementation (patterns looked broken) was
  settled by execution, not by eye.
- B-GW2: bidirectional CLAIMS <-> `by norm_num` pairing, exact set
  match. Caught real drift shape: one proof spanned two lines
  (missed by line-anchored drafts twice); golfed
  `tolerance_fails_the_coarse_bound` to bare `by norm_num` (green
  rebuild verified in our toolchain) and switched the parser to
  block-scan with exact-equality proof match (zero backslash risk
  in the final form). Pairing: 7/7 empty. `--emit-only` added for
  solver-less environments.
- Semantic check (scratch, not committed): all 8 negations (combined
  + 7 singles) independently UNSAT via z3 bindings; --emit-only exit
  0 with byte-identical SMT size (1533).
- One Lean proof golfed (comment preserves the record); the kernel
  was verified green BEFORE touching (baseline) and stays green.
- CI added (py_compile + --emit-only + solver-presence gate); green,
  with pairing/MATCH lines verified in the CI log itself (not just
  the conclusion).

## 9. FIXES APPLIED - the-asymmetric-wager-msaf (2026-10-15, pushed, CI green)

Branch `audit-fixes-bmw`, commit `66310cf`. CI is new (the repo had none):
`.github/workflows/claims.yml` on ubuntu + windows, green at that commit,
with the three verdicts visible in the log itself, not just the conclusion
(`FIXTURES: PASS -- 19`, `CHECKSUM: PASS -- 106 files`,
`report_claim_check: PASS`).

- **B-MW1 - history anchors tiered (root fix, not a patch).** `now`,
  `->` and bare `F\d`/`A\d` were anchors in P5. They assert currency or
  change, never history, and a bare phase tag dates its own clause, not
  every number on the line. Removed. What remains is a date,
  `at A5`/`at v1.9`, `then`, `as of`, or a bracketed era stamp `(A5)`.
  The matcher was also case-sensitive, so `At F5's start, eleven root
  gates were runnable` - a *correctly dated* sentence - was reported as
  undated. Measured on eight planted defects: the old anchor set let
  three through (`now`, `->`, bare tag), the new one lets none.
  Blockquotes now count as quoted evidence, like fenced blocks.
- **B-MW2 - unreadable documents skip loudly.** Non-UTF-8 and BOM files
  vanished from the sweep without a word. They are now named, counted
  and summarised in the final line.
- **B-MW3 - the gate becomes falsifiable.** `claim_fixture_check.py`:
  19 fixtures over a temp corpus, in three families - defects that MUST be
  flagged, lines that must be ACCEPTED (including a positive control on
  live values, so a gate that flags everything cannot pass), and loud
  SKIPs. One blind spot it does not catch (`harnesses 21`, noun before
  number) is recorded as an `expectedFailure` rather than forgotten; it
  will start failing loudly the day someone closes it.
- **B-MW4 (found by accident, fixed at the root).** `checksum_check.py`
  counted the `.git` *file* of a linked worktree as workspace content, so
  P3 failed in a worktree (106 vs 105) and passed in a clone. Manifest
  scope must not depend on the shape of the checkout.
- **B-MW5 - absent third-party tree is TOOL NOT RUN, not FAIL.**
  `provenance_check.py` reported FAIL for a cited document living in
  `Theory_of_Everything_Derivations/`, which `.gitignore` excludes: green
  only on the author's machine, and its red indistinguishable from a real
  defect. Its two sibling gates (`quantum_censorship_check.py`,
  `tahap_uji_audit.py`) already exited 2 with a clear message; this one
  was the outlier, and now matches the repo's own convention. Verified in
  both directions: tree absent -> exit 2 with 7 checks named; tree present
  with the file missing -> exit 1, FAIL.
- **Cost paid honestly.** The new artefact moved the manifest 105 -> 106
  rows, which made three live "105" claims defective. Brain.MD and README
  were corrected to the live figure rather than dated around it, and
  Brain.MD went v1.26 -> v1.27 with the change recorded in its footer.
- **Process failure, recorded.** The doc patcher read files with universal
  newlines and wrote LF, so A12_REPORT.md (the only CRLF file it touched)
  was silently reflowed across 140 lines. Restored to CRLF, diff back to
  two lines. F0_REPORT.md, KAMUS_PEMETAAN.md and `Tugas tambahan.md` are
  still CRLF and were left untouched on purpose. A suite run in progress
  against the mutated tree was killed rather than reported.

## 10. ZENODO - 4 DOI baru terbit (2026-10-15)

Route chosen by the operator: deposit only repositories whose gates are
machine-verified and whose CI is green at the archived commit, and put
the scope correction in the description rather than in the title's
silence.

| DOI | repository | commit | bytes | licence |
|---|---|---|---|---|
| 10.5281/zenodo.23392323 | guinand-weil-rigorous-numerics | 7f8f6e7f49 | 31 053 133 | MIT |
| 10.5281/zenodo.23392641 | gw-spectral-map | 6dc9f9cebf | 29 287 | MIT |
| 10.5281/zenodo.23392667 | anti-turing-pnp | 62b37f501f | 15 157 | MIT |
| 10.5281/zenodo.23392745 | the-asymmetric-wager-msaf | 66310cfdc6 | 31 928 342 | MIT |

All four verified afterwards: `doi.org` returns 200, each record carries
`related_identifiers` pointing at its GitHub repository, and each
description records the commit sha AND the archive sha256, so the artifact
is verifiable rather than merely citable. Every description carries the
same scope paragraph: this is an archive of a software state, and no
Riemann-Hypothesis, P-versus-NP, Hodge/Picard, Navier-Stokes or
BSD/Elliott-Halberstam resolution is asserted by it.

**Two licence defects fixed before depositing.** `anti-turing-pnp` and
`gw-spectral-map` shipped with no LICENSE file at all, while their
siblings and their Zenodo records declare MIT. A DOI with a licence field
would have recorded a permission the tree does not grant. Both now carry
MIT (code) with CC-BY-4.0 for the manuscript in `anti-turing-pnp`,
mirroring the pattern already approved in
`guinand-weil-rigorous-numerics`; both licence files state that a licence
covers documents, not conclusions.

**Still without a DOI (11 public repositories, not yet audited):**
AETHER-Z3-OMEGA, ASLC-OMEGA-LEDGER, T-hat-N (has 10.5281/zenodo.23340971,
stale: 36 tags later), gnase-engine, jacobian-conjecture-audit,
lagarias-criterion, navier-stokes-formalization,
riemann-hypothesis-formalization, sovereign-enterprise-suite,
the-asymmetric-wager-msaf-family017 (has 10.5281/zenodo.23279278),
zeta-23-audit.

**Blocker for the canonical route.** Zenodo's GitHub integration mints
DOIs only from GitHub *releases*, and this account has **zero releases
across all 15 public repositories**. Enabling the webhook also requires
the owner to log in at zenodo.org and click Enable per repository; no API
token can do it. Until that is done, future versions must be deposited by
hand - which is what `msaf/zenodo_deposit.py` does, and it is written to
refuse to invent a licence or a claim.


