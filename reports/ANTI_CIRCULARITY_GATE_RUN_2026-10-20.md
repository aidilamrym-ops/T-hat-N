# Gate anti-circularity: PASS for source Lean kernel (2026-10-20)

**Konteks:** infrastruktur verifikasi setelah Paket 9 (`A-2026-0014`); no
mengubah Paket 1â€“9.
**Berkas baru:** `harness/run_anti_circularity_gate.py`,
`reports/anti_circularity_gate_2026-10-20.log`,
`msaf/tests/test_anti_circularity_gate.py`.
**Registry:** `A-2026-0015` (entri ke-20).
**Status:** **PASS for scope source Lean kernel**; `lean/spec/` OUT OF
SCOPE; no ada input SMT.

## 1. Ringkasan

Gate anti-circularity eksternal sekarang **benar-benar dijalankan** atas
empat file source Lean kernel:

```text
lean/ComplexMoore.lean
lean/NavierStokesCore.lean
lean/NewtonExistence.lean
lean/XiNoRealZero.lean
```

Hasil verbatim:

```text
ANTI-CIRCULARITY GATE [lean]
  result: FAIL=0  NOT_RUN=0  SKIP=0
  verdict: PASS
```

```text
ANTI-CIRCULARITY GATE [check]
  result: FAIL=0  NOT_RUN=0  SKIP=0
  verdict: PASS
```

Kedua perintah exit 0. Tidak ada `sorry`, `admit`, `axiom`, or `Abort`
in kode setelah komentar dibuang. `check` juga no menemukan klaim
`MACHINE RESULT` which membutuhkan log samping. Log deterministik 51 baris
(dua run byte-identik), sha256
`6e5c97a9d780e54a54968ca06a4d453236f65b45f881fbc6234902ef53ed9aab`.

Ini **bukan** klaim bahwa teorema Lean terbukti, **bukan** audit SMT, and
**bukan** verifikasi ulang paket Coq. Lihat Â§4â€“Â§5.

## 2. Mengapa status sebelumnya `TOOL NOT RUN`

Laporan Paket 7â€“9 menjalankan gate with input directory Coq
(`formal_bridge/`) or dokumen report. Gate menerima hanya `.lean`;
karena no ada `.lean` in input itu, keluarannya:

```text
ANTI-CIRCULARITY GATE [check]
  NOT RUN  NO_LEAN_FILES: no .lean input matched
  result: FAIL=0  NOT_RUN=1  SKIP=0
  verdict: TOOL NOT RUN
```

Itu **scope mismatch**, bukan kegagalan bukti Coq. Verdict `TOOL NOT RUN`
no pernah dihitung sebagai sukses. Kalimat itu tetap benar for
lingkup Coq and **no ditulis ulang** in report beku Paket 7â€“9.

Yang berubah sekarang: gate diberi input which memang domainnya â€” source
Lean kernel which already ada in repo. Status for scope itu menjadi PASS.
Status historis for scope Coq tetap `TOOL NOT RUN` and tetap no
dihitung sebagai sukses.

## 3. Input, output, and limit scope

| Input | Dimasukkan ke verdict? | Hasil |
|---|---|---|
| `lean/*.lean` (4 file) | **ya** | **PASS** 4/4, exit 0 |
| `lean/spec/` (3 file) | **no** (OUT OF SCOPE) | diagnostik `FAIL=9`; 9 aksioma deklaratif |
| `*.smt2` | no ada | sub-gate audit **no dipanggil** |
| `formal_bridge/` (Coq) | no berlaku | receipt Coq Paket 8/9 no berubah |

`lean/spec/` sengaja in luar scope. `XiAnalyticSpec.lean` memuat sembilan
aksioma deklaratif (dua simbol opak + tujuh obligasi analitik) which no
dapat didischarge oleh Mathlib v4.33.1 which ter-pin; file itu sendiri
menulis "SPECIFICATION, NOT PROOF". CI membekukan anggaran itu:

```text
spec/ axiom budget: 9 / 9
```

Diagnostik out-of-scope (bukan verdict gate):

```text
ANTI-CIRCULARITY GATE [lean]
  FAIL     lean\spec\XiAnalyticSpec.lean:44: axiom placeholder
  FAIL     lean\spec\XiAnalyticSpec.lean:47: axiom placeholder
  FAIL     lean\spec\XiAnalyticSpec.lean:50: axiom placeholder
  FAIL     lean\spec\XiAnalyticSpec.lean:56: axiom placeholder
  FAIL     lean\spec\XiAnalyticSpec.lean:60: axiom placeholder
  FAIL     lean\spec\XiAnalyticSpec.lean:64: axiom placeholder
  FAIL     lean\spec\XiAnalyticSpec.lean:69: axiom placeholder
  FAIL     lean\spec\XiAnalyticSpec.lean:70: axiom placeholder
  FAIL     lean\spec\XiAnalyticSpec.lean:89: axiom placeholder
  result: FAIL=9  NOT_RUN=0  SKIP=0
  verdict: FAIL
```

Baris `FAIL=9` itu **no boleh** dibaca sebagai verdict paket. Ia
dicatat justru for menunjukkan mengapa spec no boleh dimasukkan ke
klaim PASS. Tidak ada `.smt2` in repo, jadi auditor sirkularitas no
dijalankan and **no ada klaim SMT PASS**.

## 4. Apa which PASS ini buktikan â€” and no

**Bukti:**

- Keempat file kernel no memuat pola placeholder gate (`sorry`,
  `admit`, `axiom`, `Abort`) in kode setelah komentar dibuang.
- Tidak ada klaim `MACHINE RESULT` tanpa log samping in keempat file.
- Input which dipindai adalah byte which in-pin in log (sha256LF per file)
  and in registry `A-2026-0015`.

**Bukan bukti:**

- Bukan bukti kebenaran teorema Lean. Gate adalah pemindai statis, bukan
  kernel Lean and bukan `#print axioms`.
- Bukan audit SMT: no ada `.smt2`, sub-gate audit no dipanggil.
- Bukan verifikasi `lean/spec/`; spec tetap kondisional with 9 aksioma.
- Bukan verifikasi ulang Paket 8/9. Kedua paket Coq tetap
  diotoritaskan oleh `coqc`/`coqchk` and `Print Assumptions` in receipt
  masing-masing; trusted base empat aksioma stdlib no berubah.
- Bukan klaim RH, Pâ‰ NP, or fisika; bukan peer review.

## 5. Reproduksi

```powershell
C:\Python314\python.exe harness\run_anti_circularity_gate.py
python -m pytest msaf\tests\test_anti_circularity_gate.py -q
python -m pytest msaf\tests\test_fence_registry.py -q
```

Runner menerima `--gate` and `--python` bila path skill berbeda. Log which
ditulis adalah `reports/anti_circularity_gate_2026-10-20.log`; dua run
on mesin which sama menghasilkan byte identik. Guard CI no memanggil
gate eksternal (no tersedia in runner); ia memeriksa secara statis
bahwa empat file kernel bebas placeholder, bahwa spec tetap 9 aksioma,
and bahwa log memuat verdict PASS with scope which benar.

## 6. Uji negatif guard

`python -m pytest msaf/tests/test_anti_circularity_gate.py -q` â€” **5 uji**,
semuanya hijau; **12 mutasi negatif** tertangkap:

1. `sorry` disuntikkan ke teks kernel;
2. `axiom` disuntikkan ke teks kernel;
3. `Abort` disuntikkan ke teks kernel;
4. daftar kernel kehilangan satu file (scope drift);
5. aksioma spec ditambah menjadi 10 (budget drift);
6. `sorry` disuntikkan ke spec;
7. log diubah `kernel_gate=PASS` â†’ `FAIL`;
8. log diubah `smt2_files=0` â†’ `1`;
9. log diubah `spec_axioms=9` â†’ `8`;
10. log diubah `spec_diagnostic_exit=1` â†’ `0`;
11. klaim palsu SMT PASS ditambahkan ke log;
12. klaim palsu RH ditambahkan ke report.

## 7. Registry and memori kerja

`A-2026-0015` (entri ke-20) memuat sertifikat sha256LF for log, report
ini, guard, runner, empat file kernel Lean, and `XiAnalyticSpec.lean`
(9 aksioma). Memori kerja: `reports/HANDOFF.md` Â§2.0ag. Laporan Paket 7â€“9
and entri `A-2026-0012`â€“`A-2026-0014` no diubah.


