# AUDIT DBN — L4: laporan verdict (final)

Ditulis 2026-10-17 (waktu lokal mesin). Status: **SELESAI** — langkah L4
(terakhir) dari pra-registrasi audit P1.

- **Target ter-pin (beku):** rilis `review-01787854-v3`, repo
  `judegomila/dbn-lambda-01787854-candidate-audit`, commit
  `2e9976c4becbf97e31c56fe75fce07cdff5dd4ea` (dibaca 2026-10-17).
- **Pra-registrasi:** `reports/AUDIT_DBN_PREREG_2026-10-17.md`
  (commit `86a32c9`; §2 definisi L1–L4, §6 protokol L4 — naskah beku,
  tidak diamandemen).
- **Bahan:** recon `reports/AUDIT_DBN_RECON_2026-10-17.md`; laporan L3
  `reports/AUDIT_DBN_L3_2026-10-17.md`; log + JSON item L2
  `reports/audit_p1_l2_*`; log L1 `reports/audit_p1_l1_launch.log`;
  gate Lean `reports/audit_p1_lean_gate.log`.
- **Registry P3:** `reports/FENCE_REGISTRY.md` (skema + entri awal;
  verdict audit ini = entri `A-2026-0001`); guard CI fail-closed
  `msaf/tests/test_fence_registry.py`.

Laporan ini memakai **struktur template reviewer milik rilis sendiri**
(`REVIEWER_REPORT_TEMPLATE.md` di commit ter-pin; transkripsi penuh di
recon §7.12) dengan field wajibnya diisi dari log sebenarnya. Token
label lapis mengikuti template (`valid` / `needs repair` / `invalid` /
`not reviewed`); verdict per-obligasi mengikuti skema pra-reg §6
(`accepted` / `rejected` / `unresolved`).

## 1. Blok template reviewer (terisi; kutipan mesin)

```text
# Suggested referee response — filled by our independent audit

## Overall assessment
plausible but incomplete  — read as OUR assessment status, not as a defect
claim on the submission: every executed independent lane passed (L2 items
1-4 REPRODUCED; L3 weld HELD), and the parts we did not execute (coverage,
section 5) prevent us from claiming "validated as stated". No GAP-FOUND;
see aggregates (section 6).

## Claim reviewed
Lambda <= 893927/5000000 = 0.1787854.

## Required fields
commit SHA: 2e9976c4becbf97e31c56fe75fce07cdff5dd4ea (pinned; unchanged
during the audit).
os: Microsoft Windows 10 Pro 10.0.19045 (4 logical processors;
PowerShell 5.1.19041.6456).
python: Python 3.14.4 (mpmath 1.3.0; sympy 1.14.0).
stored checks: PASS — the release was consumed from its pinned tree;
every statement-source and input file used by our lanes was re-verified
in-run by git blob sha1 + size (and sha256) against the pinned commit
(per-item counts: item 1 = 3 sources, item 2 = 7, item 3 = 10,
item 4 = 11 provenance gates, L3 = 14 blob gates; reference PDF hashes
byte-identical to references/README.md: Polymath 60d0d2d3..., Platt-
Trudgian 3362f66a...). Logs: reports/audit_p1_l2_*.log,
reports/audit_p1_l3.log.
container checks: NOT RUN — no container engine on the audit machine
(docker/podman/nerdctl absent; WSL2 without distro; no OCI archive in a
bounded local search); prereg section 3.4 stop rule applied; L1 =
NOT-RUN-ENVIRONMENT (reports/audit_p1_l1_launch.log). Enabling an engine
is owner-gated.

## Layer findings
(valid / needs repair / invalid / not reviewed)
1. exact Polymath Theorem 1.2 statement and Platt-Trudgian height input:
   valid (statement level). Evidence (L3): e-print v2 tar 1be3bc38...,
   debruijn.tex 560a28fe...; Thm 1.2 segment (lines 145-152) digest
   06290d46...; Thm 1.3 (223-244) digests 2bdd6d87.../cebe9801...;
   region (168-170) 4353e6c8...; Lemma 8.4 (1442-1453) b2fbc004...;
   Platt-Trudgian v1 e-print payload c6c29099... (Thm 1, lines 61-63:
   height exactly 3000175332800 = T_PT); margin identity
   X/2 + 350479773/2 = T_PT exact. Proof of the published theorems
   themselves NOT reviewed (coverage 5.6).
2. finite producer, all 3,149,013 stored rows, and direct singleton
   checks: not reviewed. Partition arithmetic only: 3149013 =
   3840000 - 690988 + 1, overlap legs contiguous (L3 E.*); row contents
   not re-generated (full sweep optional per prereg section 8; not
   executed).
3. direct all-height Triangle theorem and continuous window freeze:
   valid at checked level. L2 item 1: 34/34 (window-freeze inequalities
   + affine sign map re-derived independently in exact rational
   arithmetic). The Triangle/Dini analytic theorem (F2) itself not
   re-proved (coverage 5.8).
4. native normalization and effective-error binding: valid at checked
   level. L2 item 2: 48/48 (e_A+e_B <= sealed 2.057023688667e-12;
   e_C,0 <= sealed 2.33492848188649183e-7; E_max <= sealed
   2.33494905212337849e-7; margin >= sealed 5.57871094787e-7; sampled
   windows only — first window + 3 further windows incl. far end; their
   evaluator not run).
5. standalone infinite-tail theorem: valid at checked level, DESIGN
   POINT ONLY (N = N_* = 3840000). L2 item 3: 47/47 (corridor
   0.999719 < D < 0.999721; (1-D)/M_max > 0.0001735326089372; tail error
   < 0.000000011671604; post-error margin > 0.0001735209373337; anchors
   M = 153814, M_err = 3000, M_max < 1.608290). Release Arb/FLINT C lane
   and 160/256-bit Python lane not re-run; Polymath Thm 1.3 itself not
   re-derived (coverage 5.4, 5.8).
6. repaired 883-prism closed barrier, including the full spatial
   derivative envelope and t=0 endpoint: valid at descriptor/subset
   level. L2 item 4: 124/124 (883/883 prism gates exact; K = 8
   smallest-margin prisms (875-882) + seam faces + first/last
   deep-checked; aggregate winding +/-8.95e-13 inside (-1/4, 1/4); seam
   882/882 tokens). C/Arb lanes not re-run; per-prism descriptors trusted
   as sealed inputs; coefficient regeneration and Taylor-tail artefacts
   not rechecked (coverage 5.5).
7. the three-hypothesis criterion weld and final exact substitution:
   valid. L3: 57/57; hypotheses (i)/(ii)/(iii) all compatible; weld
   verdict HELD; canonicalised statement equality (equal=True);
   containment exact (y0^2-(1809/10000)^2 = 234599/10^8 > 0; canopy
   893927/2500000 < 1); citation-chain hashes byte-identical both sides.

## Decisive objections or repairs
none within the executed scope (no GAP-FOUND; nothing rejected). The
unresolved / not-reviewed items in the obligation table (section 3) and
coverage (section 5) are resource limits of this audit — they are not
claimed defects, and no repair is requested on their basis.

## Disclosure recommendation
This audit makes no disclosure recommendation for the release; the
underlying record is public in the audit repository, and the release's
own disposition is the release owner's call. No objection was found in
scope that would require a corrected preprint.
```

## 2. Ringkas hasil L1–L3 (pembacaan)

- **L1 — TIDAK dijalankan: `NOT-RUN-ENVIRONMENT`.** Tidak ada engine
  container di mesin audit (docker/podman/nerdctl absen; WSL2 tanpa
  distro; pencarian arsip OCI lokal terbatas tidak menemukan paket);
  aturan stop pra-reg §3.4 berlaku; instalasi engine = owner-gated.
  Attempt A/B/C (dua kegagalan awal) tercatat apa adanya di
  `reports/audit_p1_l1_launch.log`.
- **Gate Lean — AUXILIARY, bukan verdict rilis.** Rilis ter-pin memuat
  **0 berkas `.lean`**; gate dijalankan atas `lean/` di commit
  pasca-rilis ter-pin `a74738de` dan diberi label **AUXILIARY** (bukan
  bukti depot rilis; diskrepansi dicatat di coverage §5.7). Hasil:
  scan placeholder PASS (25 berkas; `FAIL=0 NOT_RUN=0 SKIP=0`; token
  `{sorry, admit, unsafe, axiom, native_decide, Abort}` total 0);
  self-test gate 13/13; attempt-1 (bug fetch, superseded) tersimpan di
  `reports/audit_p1_lean_gate_attempt1.log`.
- **L2 — 4 item, semua `REPRODUCED` di level yang dideklarasikan:**
  item 1 window freeze & affine sign map **34/34**; item 2 budget error
  Prop 4.10 **48/48** (jendela tersampel); item 3 tail lane **47/47**
  (titik desain `N = N_* = 3840000`); item 4 subset barrier **124/124**
  (K = 8 + seam + first/last; margin minimum tersegel
  `0.519849894613872543374989997` di prisma 882 direproduksi eksak).
  Stack kita: Python 3.14 + `mpmath.iv` (240-bit) +
  `fractions.Fraction` — bukan FLINT/Arb; tanpa reuse source/parser/
  partisi/decimal table rilis. Batas per item = coverage §5.3–§5.5.
- **L3 — weld theorem-source `HELD` 57/57.** Statement weld (i)/(ii)/
  (iii) + konklusi ≡ `PROOF_NOTE` (2.1)–(2.4) setelah kanonikalisasi
  terdokumentasi (`equal=True`); temuan kunci: PT Thm 1 (v1, baris
  61–63) berbunyi height persis `3 000 175 332 800 = T_PT` (abstrak
  hanya membulatkan ke 3·10^12) dan identitas margin `X/2 +
  350479773/2 = T_PT` eksak; containment + overlap + citation chain
  eksak/byte-identik. Batas = coverage §5.6.
- **Lane rilis tidak di-re-run** untuk semua item (verdict item 1–4
  dikonsumsi dari log ter-commit; input reuse sesuai pra-reg).

## 3. Tabel per-obligasi (ID blueprint rilis; kutipan mesin)

```text
Table schema per prereg section 6: obligation ID | L1 evidence |
L2 evidence | L3 evidence | verdict | references.
L1 column is "—" for every row: L1 = NOT-RUN-ENVIRONMENT (no container
engine), so no row carries replay-level evidence; the L2/L3 columns
carry all independent weight.

P1 | verified-height theorem: normalization & range | — | — | PT v1 e-print payload c6c29099...; Thm 1 lines 61-63: height exactly 3000175332800 = T_PT; margin identity X/2 + 350479773/2 = T_PT exact; PROOF_NOTE statement-canonical-equal | accepted | L3 report sec. 2; audit_p1/l3_weld_checks.py sha256 9AF03B5D...
P2 | Thm 1.2/1.3 + Lemma 8.4 transcription | — | — | segment digests reproduced (06290d46 / 2bdd6d87 / cebe9801 / 4353e6c8 / b2fbc004); F.hyp_* + F.conclusion strings equal after documented canonicalisation | accepted | recon sec. 7.11; L3 log
P3 | Cor 6.6(vi) => x-12, 10.50 bound without eq. (24) | — | item 2 covers the finite-lane budget only, not this weld | document blob gate only; verifier not re-run | unresolved | coverage sec. 5.8
G1 | exact parameters, sign conventions, final substitution | — | anchors rechecked in items 2-4 | CANDIDATE_PARAMETERS identities exact; final-substitution strings canonical-equal; overlap 3149013 = 3840000 - 690988 + 1 contiguous | accepted | L3 log (C.*, E.legs, F.conclusion)
F1 | native finite convolution + effective-error bridge | — | item 1 34/34; item 2 48/48 | NATIVE_BINDING + WINDOW_FREEZE_THEOREM blob gates | accepted | item logs; coverage sec. 5.3
F2 | Dini upper bound + normalizer monotonicity | — | — | — (document not fetched; analytic content not re-proved) | unresolved | coverage sec. 5.8
F3 | all finite rows (3149013) + half-open seam | — | item 1 freeze/endpoints only | partition arithmetic + seam window domains | unresolved | coverage sec. 5.8 (rows not re-generated)
T1 | tail all-N: endpoint-cap, partition, monotonicity | — | item 3 47/47 (design point) | TAIL_LEMMA + TAIL_PROVENANCE blob gates | accepted | item 3 log; all-N = release sec. 6/7 reductions (gated as premises)
T2 | two independent tail implementations | — | verifier sources blob-gated (claim identification only) | — | unresolved | item 3 log source list; coverage sec. 5.8
B1 | derivative box, quadrature, Taylor, coefficient provenance | — | item 4 124/124 (descriptor / error-budget level) | BARRIER_CERTIFICATE + DERIVATIVE_BOX_LEMMA blob gates | accepted | item 4 log; coefficient regeneration + Taylor-tail not rechecked (coverage sec. 5.5)
B2 | every prism + seam + homotopy winding nonzero | — | item 4: 883/883 gates exact; K=8 smallest (prisms 875-882) + seam + first/last; aggregate winding +/-8.95e-13 in (-1/4, 1/4); seam 882/882 tokens | log-side byte identity | accepted | item 4 log (min margin 0.519849894613872543374989997 reproduced)
C1 | overlap domain + three-hypothesis weld without weakening | — | inputs from items 1-4 | weld HELD 57/57; hypotheses (i)/(ii)/(iii) compatible; canonicalised equality equal=True; containment exact | accepted | L3 report; audit_p1/l3_weld_checks.py
```

## 4. Verdict L3 (kutipan mesin; dari log resmi)

```text
hypothesis (i)   (slot P1)                : compatible
hypothesis (ii)  (slot T1 + F1-F3)        : compatible
hypothesis (iii) (slot B1-B2 + C1)        : compatible
weld verdict                              : HELD
checks_total: 57  checks_failed: 0
L3 machine verdict: PASS
```

## 5. Coverage — langkah yang TIDAK dilakukan (masing-masing dengan sebab)

1. **L1 replay repository** (`verify.sh`, `run_prop410_arb.sh`,
   `run_tail_arb.sh`, `run_barrier_replay.sh`, `run_full_sweep.sh`) —
   TIDAK dijalankan: tidak ada engine container; stop rule pra-reg
   §3.4; instalasi engine owner-gated. Bukti: `audit_p1_l1_launch.log`.
2. **`run_full_sweep.sh`** — TIDAK dijalankan (optional per pra-reg §8;
   anggaran).
3. **Item 2 — jendela tersampel saja:** jendela pertama + 3 jendela
   lain (termasuk ujung jauh); sisa `N = 690989…3839999` dikreditkan ke
   teorema window-freeze rilis (tidak dire-derivasi ulang melebihi item
   1); evaluator rilis tidak dijalankan; item ini mensertifikasi
   jendela tersampel saja.
4. **Item 3 — titik desain saja (`N = N_* = 3840000`):** semua-N ≥ N_*
   dan cakupan y di atas I_box = reduksi §6/§7 rilis (gate dicek
   sebagai premis); lane Arb/FLINT C dan lane Python 160/256-bit rilis
   tidak di-re-run; Polymath Thm 1.3 sendiri tidak dire-derivasi.
5. **Item 4 — subset + input tersegel:** lane C/Arb (`barrier_closed`,
   `uniform_error`) tidak di-re-run; deskriptor per-prisma (mesh,
   winding, Dz, Dt) dipercaya sebagai input tersegel; regenerasi
   koefisien stored-sum + artefak Taylor-tail tidak dicek ulang;
   byte-identity seam terserialisasi dalam assembli rilis tidak dicek
   ulang (identitas token sisi log saja); sapuan penuh 883 prisma tidak
   diulang; lane prop43/prop62 di luar scope.
6. **L3 — batas-batas (dari `boundary` di JSON L3):** kebenaran
   teorema terbitan tidak direview (statement + pemetaan yang di-weld);
   reduksi analitik paket (Dini all-y, limit t=0, native binding,
   derivative-box/tail) tidak dibuktikan ulang; full text Bull. LMS
   (refereed) tidak dapat diakses fetch scripted (403) — hanya record
   bibliografi; pagination typeset Polymath jurnal tidak dibandingkan
   (v2 = "final version" per record arXiv); snapshot arXiv dated
   2026-10-17; bracket π sekunder non-primer (mpmath-60d);
   bentuk zero-count PT tidak dikonsumsi; tidak ada lane rilis di-re-run.
7. **Gate Lean = AUXILIARY, bukan verdict rilis:** rilis ter-pin memuat
   0 berkas `.lean`; gate dijalankan atas `lean/` commit pasca-rilis
   `a74738de`; scan teks (placeholder) + self-test saja — bukan
   pembangunan ulang Lean; diskrepansi rilis-vs-HEAD dicatat; attempt-1
   (bug fetch) tersimpan.
8. **Item lain yang tidak dieksekusi:** F2 (dokumen Dini/Triangle tidak
   di-fetch/hash; tidak dibuktikan ulang); P3 (verifier
   `verify_error_constant_weld.py` tidak di-re-run); T2 (dua
   implementasi tail rilis tidak dieksekusi ulang; sumber di-gate
   sebagai identifikasi klaim saja); F3 (baris finite tidak
   diregenerasi); verifier rilis lain (`verify_assembly_1787854.py`,
   `verify_criterion_sign_map.py`, `verify_tail*`, dsb.) tidak
   di-re-run — yang di-gate hanya sebagai identifikasi klaim/sumber;
   mutation-kill verifier rilis tidak dilakukan; sapuan penuh baris/
   prisma tidak dilakukan.
9. **Kesegaran target:** audit berlaku untuk commit ter-pin; HEAD repo
   kandidat (`a74738de`, 21 Agu 2026, PGP-signed) terpisah dari target
   ter-pin; watch recon (cek-2) mencatat tidak ada commit/rilis baru
   pada saat audit; tidak ada pengaruh pada verdict.

## 6. Agregat (kutipan mesin; skema pra-reg §6)

```text
GAP-FOUND: none.
INDEPENDENTLY-CERTIFIED (parts, with level):
  - L2 item 1 (window freeze & affine sign map): REPRODUCED 34/34 — our
    stack (Python 3.14 + mpmath.iv 240-bit + fractions.Fraction).
  - L2 item 2 (Prop 4.10 finite-lane error budget & binding):
    REPRODUCED 48/48 (sampled windows; declared).
  - L2 item 3 (tail lane partition budget): REPRODUCED 47/47 (design
    point N = N_* = 3840000; declared).
  - L2 item 4 (barrier subset descriptor recheck): REPRODUCED 124/124
    (K=8 + seam + first/last subset; declared).
  - L3 (three-hypothesis weld): HELD 57/57 (statements, parameters,
    containment, citation chain; canonicalised equality equal=True).
UNVERIFIABLE-WITH-OUR-RESOURCES (parts, why):
  - L1 repository replay: no container engine (owner-gated).
  - F2 Triangle/Dini analytic theorem; P3 error-constant weld
    derivation; T2 re-execution of the two tail implementations; F3 row
    regeneration (not re-proved / not re-run).
  - Full producer sweep (3,149,013 rows) and full 883-prism sweep
    (prereg section 8 budget; subset used instead).
  - Referee full text (Bull. LMS 403); published-theorem proofs beyond
    the statements welded in L3.
RECOMMENDATION FROM AGGREGATES: no repairs requested; verdicts are
per-obligation in section 3.
```

## 7. Kalimat standar (beku; kutipan verbatim pra-reg §6)

```text
A repository replay is not a mathematical review.
their PASS is not peer acceptance.
no verdict here asserts or denies RH or any universal statement.
```

## 8. Provenans artefak audit

- Skrip inti: `audit_p1/l2_window_freeze.py`,
  `audit_p1/l2_prop410_budget.py`, `audit_p1/l2_tail_budget.py`,
  `audit_p1/l2_barrier_subset.py`, `audit_p1/l3_weld_checks.py`.
- Log + JSON resmi per item: `reports/audit_p1_l2_window.log` +
  `_results.json`; `..._prop410...`; `..._tail...`; `..._barrier...`;
  L3 `reports/audit_p1_l3.log` + `_results.json`; transkrip pra-run
  (`..._attempt1.log`, `..._smoke1.log`, `..._smoke2.log`); L1
  `reports/audit_p1_l1_launch.log`; Lean
  `reports/audit_p1_lean_gate.log` (+ `_attempt1.log`).
- **sha256LF lengkap semua artefak di atas ada di
  `reports/FENCE_REGISTRY.md`** (entri `A-2026-0001`); tiap baris
  diverifikasi ulang oleh guard CI
  `msaf/tests/test_fence_registry.py` (fail-closed).
- Catatan jujur: runner `.ps1` resmi dijalankan dari luar repo (hash
  runner tercatat di masing-masing log; skrip inti + hash input lengkap
  ada di repo, sehingga re-run dapat direproduksi); smoke/attempt yang
  gagal disimpan tanpa dihapus.

## 9. Owner-gated & berikutnya

- **Dashboard:** update apa pun wajib v6 baru (v3/v4/v5 dibekukan);
  persetujuan pemilik belum diberikan (now/defer/skip).
- **Scope Note recording** — menunggu keputusan pemilik.
- **Instalasi engine container** untuk replay L1 di masa depan —
  owner-gated, tidak memblok.
- **Registry P3 aktif:** entri awal (T-2026-0001, T-2026-0002,
  F-2026-0001, F-2026-0002, T-2026-0003, A-2026-0001) + guard CI;
  entri baru menyusul mengikuti skema yang sama.

Ditulis oleh sesi audit, 2026-10-17. Berkas ini dan registry-nya
disertakan dalam commit yang sama; tidak ada angka di laporan ini yang
diketik ulang tanpa sumber log di repo (semua blok mesin di atas
disalin dari log/JSON ter-commit).
