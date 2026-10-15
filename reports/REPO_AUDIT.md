# Audit Titik-Buta: Empat Repo Milik Kita (review read-only, tanpa unduh)

Tanggal: 2026-10-15. Metode: baca via API (metadata, listing, file),
tanpa menjalankan kode mereka, tanpa menulis ke repo mana pun.
Standar yang dipakai persis standar yang dipakai ke diri sendiri:
klaim = saksi mesin + scope tertulis; sisanya ditandai.

Legenda: **[B-*]** blind spot (butuh perbaikan) · **[S-*]** kekuatan
(diakui, diadopsi bila cocok) · tingkat: kritis / sedang / ringan.

---

## 1. anti-turing-pnp — verdict: teorema benar, entailment tidak ada

**[S-AT1]** 6 teorema Lean adalah analisis elementer yang benar
(positivitas/batas sigmoid, penghitungan indikator, 2^n > 1).
Hasil Z3 UNSAT atas enkoding ODE juga dibaca apa adanya: benar
pada level enkodingnya.

**[B-AT1] KRITIS — tidak ada definisi P, NP, SAT, waktu-polinomial,
reduksi, atau Cook-Levin di rantai bukti.** Berkas lengkap sudah
dibaca (`AntiTuringCore.lean`): objeknya `VectorFieldLTC`,
`tau_LTC`, `bypass_selector`, `DiscreteTuringStep`. Ketidakhadiran
total kosakata kompleksitas membuat "resolusi P vs NP" tidak
ter-derive secara prinsip, bukan karena kurang langkah. O(1)
kontinu ≠ O(1) Turing (model analog; hasil literatur komputasi
analog justru menunjukkan presisi tak terbatas menyelundupkan
infinity kembali — ironis untuk repo anti-infinity).
Rekomendasi: turunkan headline ke "continuous relaxation bounds"
(ini yang sebenarnya dibuktikan), ATAU formalkan jembatan
Cook-Levin (proyek raksasa). Alasan: klaim tanpa jembatan adalah
klaim tanpa rantai bukti — kelas yang sama dengan yang kita tolak
di repo sendiri.

**[B-AT2] SEDANG — sel "0 axiom" tak terverifikasi.** Berkas membuka
`open Classical`, memakai `Real.sqrt`/`Real.exp` Mathlib
(noncomputable). Prediksi terukur: `#print axioms` menghasilkan
tiga aksioma standar (persis seperti audit 73/73 kita) — artinya
sel itu berarti "tanpa deklarasi axiom", BUKAN "tanpa ketergantungan
aksioma". Rekomendasi: jalankan audit `#print axioms` (pola kita,
30 detik) dan tulis ulang selnya. Alasan: sel yang salah membaca
membuat seluruh matriks audit diragukan.

**[B-AT3] RINGAN — drift dokumen vs kode.** Laporan bilang 5 teorema;
berkas memuat 6 (`continuous_energy_decreasing` tak terdaftar).
Rekomendasi: hitung teorema secara mekanis (regex `^theorem`),
jangan tulis tangan. Alasan: ini persis kelas bug "baris-G1-basi"
yang pernah kita miliki.

**[B-AT4] RINGAN — konstanta mati / klaim dimensi.** `StateDim := 42`
didefinisikan tapi struktur hanya punya 4 field (w1..w4); "untuk n
klausa" tidak terhubung ke 42. `bypass_selector` disebut "lim" tapi
tak ada limit yang diformalkan (jumlah 4 indikator). Rekomendasi:
parameterisasi dimensi atau dokumentasikan 4 sebagai instans;
ganti nama "lim" atau formalkan limitnya. Alasan: nama yang
melebihi isi adalah klaim yang belum dibayar.

**[B-AT5] SEDANG — skrip Z3 memverifikasi enkoding, bukan kompleksitas.**
`UNSAT` atas konsistensi ODE ≠ batas atas/bawah kompleksitas.
Rekomendasi: catatan scope satu baris per batch (apa yang di-encode,
apa yang TIDAK disimpulkan). Alasan: tanpa itu pembaca mengira
tribunal memutuskan P vs NP.

Disposisi queue TETAP: B-list formalisasi-saja. Satu-satunya
kontribusi jujur repo ini ke P-vs-NP adalah merumuskan presisi
GAP-nya — dan itu pekerjaan mereka, bukan kita.

---

## 2. gw-spectral-map — verdict: teladan disiplin, temuan ringan

**[S-SM1]** Diakui dan patut ditiru: two-engine dengan vetting
ambiguitas eksplisit, exit code fail-closed (0/1/2), artefak KILLED
disimpan sebagai rekor jujur, hasil negatif S2 dilaporkan
(INCONSISTENT WITH MONTGOMERY — bukan disembunyikan), analisis biaya
level-0 vs level-1 sebelum kampanye, resume JSONL terverifikasi.

**[B-SM1] SEDANG — basis data verdict S2 tidak berprovisional.**
Status S2 INCONSISTENT dikutip, tapi kampanye penuh masih QUEUED di
belakang OMEGA; pembaca tak bisa tahu artefak hash apa yang memberi
makan verdict itu. Rekomendasi: tiap verdict menunjuk hash artefak
data (pola sama dengan digest transkrip pivot mereka). Alasan:
verdict tanpa data-pin adalah kalimat, bukan sertifikat.

**[B-SM2] RINGAN — konstanta vetting `ambig = 1e-6 * scale` heuristik.**
Sudah dimitigasi (cluster certificate untuk zona ketat), tapi
s sixty sensitivitasnya tak tercatat. Rekomendasi: catat variasi
ambig ×/÷10 pada selftest dan tunjukkan verdict stabil. Alasan:
konstanta tanpa uji sensitivitas adalah asumsi yang belum dibayar.

**[B-SM3] RINGAN — konvensi endpoint bracket tak tertulis.**
`N(mu) = n_neg` menghitung strictly-below; bracket "(lo,hi]"
dengan eigenvalue TEPAT di endpoint butuh konvensi yang dicetak.
Undetermined-pivot menanganinya operasional, tapi dokumen harus
menyatakannya. Rekomendasi: satu paragraf konvensi + satu uji
eigenvalue-di-tepi. Alasan: ambiguitas konvensi adalah blind spot
klasik penghitung interval.

**[B-SM4] RINGAN — `results/` tanpa manifest.** Enam JSON + rekor
KILLED, tapi tak ada CHECKSUM/manifest terlihat (praktik yang justru
ada di repo saudaranya). Rekomendasi: port praktik manifest ke sini.
Alasan: artefak tanpa manifest bisa diganti diam-diam.

---

## 3. guinand-weil-rigorous-numerics — verdict: pola kelas-satu, 2 lubang

**[S-GW1]** Diakui: cross-check literal README↔Lean via regex (tak
percaya salinan tangan); file SMT single-assert yang kompatibel
dengan auditor sirkularitas + tujuh run individual (pelajaran
VACUOUS mereka documented!); analisis diskrepansi yang JUJUR
(`tolerance_fails_the_coarse_bound` — teorema yang menyatakan kapan
angka laporan TIDAK cocok, untuk mengidentifikasi norma yang
dipakai); exit code 0/1/2/3; artefak SMT+log ter-commit; status tool
per-run (coqc/isabelle/dkcheck/gcc NOT RUN — ditulis, bukan disembunyikan).

**[B-GW1] SEDANG — cross-check literal memeriksa KEBERADAAN, bukan
ATRIBUSI.** `ok = (mant, exp10) in readme_set`: pasangan digit
cukup MUNCUL di README di mana saja — angka rhoActual yang tertulis
di paragraf yang salah (topik lain) tetap MATCH. Rekomendasi:
jangkarkan per-konstanta (nama konstanta dalam N baris dari angka,
atau posisi seksi). Alasan: existence ≠ attribution; lubang kecil,
probabilitas rendah, tapi tepat di gerbang yang mengklaim ketepatan.

**[B-GW2] SEDANG — pasangan Lean↔SMT manual.** Komentar "keep names
identical so a reader can pair them up" = pairing oleh mata.
Rekomendasi (murah, pola kita): uji mekanis dua arah — setiap nama
di CLAIMS ada di .lean, dan setiap teorema `norm_num` di .lean ada
di CLAIMS (klaim tanpa pasangan = klaim tanpa audit). Alasan:
drift pasangan adalah versi lain dari bug baris-basi kita; yang
menangkapnya harus mesin (`audited == found` — mereka belum punya
bentuk ini untuk pasangan klaim).

---

## 4. the-asymmetric-wager-msaf — verdict: gate prosa paling matang yang
pernah saya baca; pengencangan, bukan perbaikan

**[S-MW1]** Diakui: exit 2 tak-pernah-pass; vocabulary self-guard
(generator yang salah menghentikan gate, bukan memiringkannya);
manifest memeriksa tally-nya sendiri; deteksi ghost dua arah (P6);
map_check P8; tiap pola disertai komentar pelajaran dari miss
terdahulu (A16-R1, F8-R1, tally_object ordering). Ini di atas praktik
kita untuk gate prosa — tidak ada yang setara di repo kerja.

**[B-MW1] SEDANG — jangkar `now`, `F\d`, `A\d` terlalu permisif.**
`anchor_window` memvalidasi SELURUH angka di baris bila SATU jangkar
ada di ±1 baris — dan `\bnow\b` ("now" = kini!) mengesahkan riwayat.
Baris "now 13 gates" dengan angka basi lolos. Rekomendasi: jangkar
hanya tag eksplisit (tanggal/fase/versi), ATAU kedekatan per-klaim
(jangkar dalam N karakter dari angka). Alasan: jangkar yang longgar
mengubah gate presisi menjadi gate perasaan; catat biaya
false-positive bila diketatkan.

**[B-MW2] RINGAN — berkas non-UTF8 dilewati diam-diam.**
`readable()` None → `continue` di `dated_claims` (hanya BRAIN yang
dijaga exit-2). Dokumen .md non-UTF8 dengan angka basi lolos lewat
omisi. Rekomendasi: catat SKIP eksplisit per berkas. Alasan: omisi
diam-diam adalah bentuk pass-diam-diam.

**[B-MW3] RINGAN — siapa mengawasi pengawas.** Pola klaim baru di
luar pola yang ada lolos by-design (tak ada pola = tak ada klaim
terbaca). Mereka menjawab sebagian (komentar tiap miss), tapi tak
ada suite fixture-negatif yang terlihat di listing (tak ada dir
tests/ di root; `harnesses/` belum diperiksa isinya).
Rekomendasi: suite fixture yang HARUS gagal (pola anti-circularity
kita punya `tests/run_tests.py` 11 kasus sebagai contoh) + entri CI.
Alasan: gate tanpa negatif yang gagal adalah gate yang tak bisa
dibuktikan hidup — pelajaran yang KITA petik dengan cara keras
(audit 0 deklarasi).

---

## 5. Yang diadopsi kembali ke repo kerja (hasil audit ini)

- **[ADOPT-1]** Praktik manifest untuk direktori artefak: `results/`
  mereka (dan `reports/*.json` KITA — artefak trace kuartik!) belum
  punya CHECKSUM. Dicatat sebagai peningkatan antrian, bukan klaim.
- **[ADOPT-2]** Bentuk `audited == found` untuk pasangan klaim
  (pelajaran B-GW2) — sudah kita miliki untuk aksioma Lean; spek CH
  kita (combiner vs klaim) akan mengikutinya.
- **[ADOPT-3]** Sel status-tool per-run (NOT RUN ditulis eksplisit,
  pola OMEGATrackC) — diadopsi untuk run berat kita (offline k=10
  sudah mencatat elapsed; format diselaraskan berikutnya).
## 6. FIXES APPLIED — anti-turing-pnp (2026-10-15, pushed, CI green)

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
- Remaining repos (gw-spectral-map, guinand-weil-rigorous-numerics,
  the-asymmetric-wager-msaf): queued next, one by one. No files were
  written to any repo except the one being fixed.

## 7. FIXES APPLIED — gw-spectral-map (2026-10-15, pushed, CI green)

- B-SM1: S1/S2 verdict lines now point at the producing machinery
  (OMEGA gw_montgomery.py:562 + K5 fixture gw_mont_pipeline_check.py:195,256)
  and state the certified-spectrum re-run is QUEUED.
- B-SM2: ambig sensitivity MEASURED (17/17 + 0 conflicts at 1e-7/1e-6/1e-5;
  only granularity moves 9/1, 8/1, 7/1) — recorded, not assumed.
- B-SM3: endpoint-convention test 5/5 PASS (exact-hit -> UNDETERMINED;
  strict-below exact); convention documented in NOTES section D.
- B-SM4: results/MANIFEST.sha256 + stdlib verifier (roundtrip green).
- CI added (py_compile + sm_dual + manifest + endpoint loud-SKIP +
  sibling-gated selftests). CI history honest: one CRLF/LF manifest
  failure (all 7 files flagged drifted on Linux checkouts) fixed at
  the root (LF-normalized hashing — immune to checkout style).
- Verified locally first: sm_dual PASS, sturm 10/10, brackets 17/17
  (matches README), endpoint 5/5 — via a sibling tree wired in temp
  (nested copy), both repos otherwise untouched.
