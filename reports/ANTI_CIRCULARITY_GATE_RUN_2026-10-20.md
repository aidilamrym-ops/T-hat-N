# Gate anti-circularity: PASS untuk sumber Lean kernel (2026-10-20)

**Konteks:** infrastruktur verifikasi setelah Paket 9 (`A-2026-0014`); tidak
mengubah Paket 1–9.
**Berkas baru:** `harness/run_anti_circularity_gate.py`,
`reports/anti_circularity_gate_2026-10-20.log`,
`msaf/tests/test_anti_circularity_gate.py`.
**Registry:** `A-2026-0015` (entri ke-20).
**Status:** **PASS untuk scope sumber Lean kernel**; `lean/spec/` OUT OF
SCOPE; tidak ada input SMT.

## 1. Ringkasan

Gate anti-circularity eksternal sekarang **benar-benar dijalankan** atas
empat berkas sumber Lean kernel:

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

Kedua perintah exit 0. Tidak ada `sorry`, `admit`, `axiom`, atau `Abort`
di kode setelah komentar dibuang. `check` juga tidak menemukan klaim
`MACHINE RESULT` yang membutuhkan log samping. Log deterministik 51 baris
(dua run byte-identik), sha256
`6e5c97a9d780e54a54968ca06a4d453236f65b45f881fbc6234902ef53ed9aab`.

Ini **bukan** klaim bahwa teorema Lean terbukti, **bukan** audit SMT, dan
**bukan** verifikasi ulang paket Coq. Lihat §4–§5.

## 2. Mengapa status sebelumnya `TOOL NOT RUN`

Laporan Paket 7–9 menjalankan gate dengan input direktori Coq
(`formal_bridge/`) atau dokumen laporan. Gate menerima hanya `.lean`;
karena tidak ada `.lean` di input itu, keluarannya:

```text
ANTI-CIRCULARITY GATE [check]
  NOT RUN  NO_LEAN_FILES: no .lean input matched
  result: FAIL=0  NOT_RUN=1  SKIP=0
  verdict: TOOL NOT RUN
```

Itu **scope mismatch**, bukan kegagalan bukti Coq. Verdict `TOOL NOT RUN`
tidak pernah dihitung sebagai sukses. Kalimat itu tetap benar untuk
lingkup Coq dan **tidak ditulis ulang** di laporan beku Paket 7–9.

Yang berubah sekarang: gate diberi input yang memang domainnya — sumber
Lean kernel yang sudah ada di repo. Status untuk scope itu menjadi PASS.
Status historis untuk scope Coq tetap `TOOL NOT RUN` dan tetap tidak
dihitung sebagai sukses.

## 3. Input, output, dan batas scope

| Input | Dimasukkan ke verdict? | Hasil |
|---|---|---|
| `lean/*.lean` (4 berkas) | **ya** | **PASS** 4/4, exit 0 |
| `lean/spec/` (3 berkas) | **tidak** (OUT OF SCOPE) | diagnostik `FAIL=9`; 9 aksioma deklaratif |
| `*.smt2` | tidak ada | sub-gate audit **tidak dipanggil** |
| `formal_bridge/` (Coq) | tidak berlaku | receipt Coq Paket 8/9 tidak berubah |

`lean/spec/` sengaja di luar scope. `XiAnalyticSpec.lean` memuat sembilan
aksioma deklaratif (dua simbol opak + tujuh obligasi analitik) yang tidak
dapat didischarge oleh Mathlib v4.33.1 yang ter-pin; file itu sendiri
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

Baris `FAIL=9` itu **tidak boleh** dibaca sebagai verdict paket. Ia
dicatat justru untuk menunjukkan mengapa spec tidak boleh dimasukkan ke
klaim PASS. Tidak ada `.smt2` di repo, jadi auditor sirkularitas tidak
dijalankan dan **tidak ada klaim SMT PASS**.

## 4. Apa yang PASS ini buktikan — dan tidak

**Bukti:**

- Keempat berkas kernel tidak memuat pola placeholder gate (`sorry`,
  `admit`, `axiom`, `Abort`) di kode setelah komentar dibuang.
- Tidak ada klaim `MACHINE RESULT` tanpa log samping di keempat berkas.
- Input yang dipindai adalah byte yang di-pin di log (sha256LF per berkas)
  dan di registry `A-2026-0015`.

**Bukan bukti:**

- Bukan bukti kebenaran teorema Lean. Gate adalah pemindai statis, bukan
  kernel Lean dan bukan `#print axioms`.
- Bukan audit SMT: tidak ada `.smt2`, sub-gate audit tidak dipanggil.
- Bukan verifikasi `lean/spec/`; spec tetap kondisional dengan 9 aksioma.
- Bukan verifikasi ulang Paket 8/9. Kedua paket Coq tetap
  diotoritaskan oleh `coqc`/`coqchk` dan `Print Assumptions` di receipt
  masing-masing; trusted base empat aksioma stdlib tidak berubah.
- Bukan klaim RH, P≠NP, atau fisika; bukan peer review.

## 5. Reproduksi

```powershell
C:\Python314\python.exe harness\run_anti_circularity_gate.py
python -m pytest msaf\tests\test_anti_circularity_gate.py -q
python -m pytest msaf\tests\test_fence_registry.py -q
```

Runner menerima `--gate` dan `--python` bila path skill berbeda. Log yang
ditulis adalah `reports/anti_circularity_gate_2026-10-20.log`; dua run
pada mesin yang sama menghasilkan byte identik. Guard CI tidak memanggil
gate eksternal (tidak tersedia di runner); ia memeriksa secara statis
bahwa empat berkas kernel bebas placeholder, bahwa spec tetap 9 aksioma,
dan bahwa log memuat verdict PASS dengan scope yang benar.

## 6. Uji negatif guard

`python -m pytest msaf/tests/test_anti_circularity_gate.py -q` — **5 uji**,
semuanya hijau; **12 mutasi negatif** tertangkap:

1. `sorry` disuntikkan ke teks kernel;
2. `axiom` disuntikkan ke teks kernel;
3. `Abort` disuntikkan ke teks kernel;
4. daftar kernel kehilangan satu berkas (scope drift);
5. aksioma spec ditambah menjadi 10 (budget drift);
6. `sorry` disuntikkan ke spec;
7. log diubah `kernel_gate=PASS` → `FAIL`;
8. log diubah `smt2_files=0` → `1`;
9. log diubah `spec_axioms=9` → `8`;
10. log diubah `spec_diagnostic_exit=1` → `0`;
11. klaim palsu SMT PASS ditambahkan ke log;
12. klaim palsu RH ditambahkan ke laporan.

## 7. Registry dan memori kerja

`A-2026-0015` (entri ke-20) memuat sertifikat sha256LF untuk log, laporan
ini, guard, runner, empat berkas kernel Lean, dan `XiAnalyticSpec.lean`
(9 aksioma). Memori kerja: `reports/HANDOFF.md` §2.0ag. Laporan Paket 7–9
dan entri `A-2026-0012`–`A-2026-0014` tidak diubah.
