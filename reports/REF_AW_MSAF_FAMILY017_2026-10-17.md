# REF â€” Vault audit "MSAF Family 017" oleh proyek lain (eksternal) â€” 2026-10-17

Status: **Referensi eksternal; bukan result MSAF; dikomit 2026-10-17 (batch strategi).**
Sumber: `https://github.com/aidilamrym-ops/the-asymmetric-wager-msaf-family017`
(HEAD `7db7d46bc745945b29e1bfae80c8812f6479ed32`, 2026-10-10 17:59 +0800;
tag `v1.0.0`). Disalin sebagai clone kerja ke
`C:\Users\usER\AppData\Local\Temp\opencode\aw_msaf_family017` (temp;
no ada penulisan ke repo source). Berguna sebagai: prior-art
metode harness/registry for portofolio kita (P3/P5) and peta
ekosistem dual-core proyek lain (Core B:
`guinand-weil-rigorous-numerics`) for P4.

## 1. Apa itu

Vault audit + certificate + release for OpenAI Family 017
(`OAI.NumberTheory.PiExponent`, eksponen irasionalitas pi):

- 869 source Lean (copy subtree OAI, Apache-2.0) + 4.345 artefak bukti
  (`proofs/OAI/**`); total repo â‰ˆ 272,9 MB (5.262 file non-`.git`).
- `MANIFEST.sha256` (850.044 byte; 5.252 entri; **path absolut staging
  `D:\MSAF_CLEAN_DEPLOY\â€¦`**) + 10 eksklusi terdokumentasi (self, README,
  RELEASE, `config/patches/README.md`, `.gitattributes`, 5 file
  `.github/`).
- Harness PowerShell: `build_sequential.ps1` + H1 (escape-token, canary
  positif wajib), H2 (reachability), H3 (compile axiom), H4 (patch
  integrity).
- `config/`: pins `lakefile.lean`, `lake-manifest.json`, `lean-toolchain`
  (`v4.34.1`), + 23 patch kompatibilitas dependensi pihak ketiga.
- Klaim verdict mereka (kata mereka): 869/869 modul elaborated; 0 escape
  token (semua kelas hazard); footprint aksioma
  `[propext, Classical.choice, Quot.sound]` on 3 deklarasi entry;
  Anti-Circularity Gate `lean` `FAIL=0 NOT_RUN=0` â†’ PASS; dua anomali
  harness (H2/H3) didisklose terbuka.

## 2. Verifikasi silang MSAF (2026-10-17, dari clone kami)

- `MANIFEST.sha256` = `18B72FC8â€¦` âœ“ (persis payload rilis mereka);
  certificate = `07121A53â€¦` âœ“; hitungan 5.262 file âœ“; 5.252 baris âœ“;
  869 source âœ“; 4.345 artefak âœ“.
- **Verifikasi per-entri (kita, 5.252 entri dihitung ulang):**
  3.477 bit-exact; 1.774 beda **hanya line-ending** (manifest LF vs
  checkout CRLF â€” konversi autocrlf; 0 beda konten setelah normalisasi);
  **1 entri (`NOTICE`, baris 906) no tereproduksi** dari konten repo â€”
  diuji 48 kombinasi BOM Ã— EOL Ã— final-newline Ã— UTF-16 atas (a) file
  checkout kami and (b) blob git `39c578d8â€¦` (satu-satunya commit which
  menyentuh `NOTICE`; riwayat penuh setelah unshallow) â€” no ada which
  cocok; hash entri unik in manifest (COUNT=1, bukan mix-up).
  Tafsir paling mungkin: salinan staging `NOTICE` berbeda dari which
  in-commit saat lock, or satu entri hash keliru. **Tidak
  load-bearing** (file atribusi lisensi 159 byte; verdict mereka
  berdiri in artefak Lean/kernel/certificate). Dicatat sebagai limit
  bila mengutip vault ini.
- Teknik byte-pin `.gitattributes` mereka terbukti bekerja: `MANIFEST`
  (`-text`) and certificate (`eol=crlf`) keduanya cocok apa-adanya.

## 3. Yang kita ambil (metode saja; no ada klaim matematis)

- **H1**: scanner escape-token wajib punya **canary positif hidup**
  ("harness which melaporkan 0 token tanpa membuktikan bisa mendeteksi =
  sampah"); exit contract 0/1/2. Prinsip validitas which sama with skill
  anti-circularity kita; prior-art bagus for P3/P5.
- **H3 pelajaran**: exit code skrip BUKAN otoritas â€” literal stdout
  kernel (`#print axioms`, exit 0) which menjadi bukti; selaras with
  disiplin kita "footer log runner otoritatif, bukan ExitCode
  Start-Process".
- **`.gitattributes` byte-pinning** for file ber-hash terbit
  (`-text` / `eol=crlf`) â€” teknik for CI guard P3 (imutabilitas hash
  terbit lintas checkout).
- **Manifest + tabel eksklusi eksplisit** (10 eksklusi ber-alasan) â€”
  prior-art for registry lock P3/P5.
- **Build sekuensial frontier** (satu proses; unit kegagalan = unit
  eksekusi; verifikasi artefak per step; nol proses residu) â€”
  sejalan with disiplin kita "satu kampanye berat sekaligus".
- **Dual-core A/B** (formal Lean â†” numerik Arb; "agreement is checked,
  not assumed"; Core B = repo `aidilamrym-ops/guinand-weil-rigorous-numerics`,
  mesin Arb/LDLáµ€) â€” analog struktural for L2 and kandidat rujukan P4
  (belum kami periksa; TO-PIN bila mau dipakai).

## 4. Pin for salin-ulang (working-tree clone, SHA-256 first16)

| Berkas | first16 |
|---|---|
| `README.md` | `B53AC95F448F7A01` |
| `OAI_FAMILY_017_CORE_CERTIFICATE.md` | `07121A536CC5956D` |
| `GUINAND_WEIL_LINK.md` | `F5994A966E70FB12` |
| `MANIFEST.sha256` | `18B72FC87EF4CD02` |
| `RELEASE_v1.0.0.md` | `65F1DF164C76A490` |
| `harness/build_sequential.ps1` | `5F397F0B93CB3226` |
| `harness/H1-EscapeToken.ps1` | `9DCEA0F9E9A712D8` |
| `harness/H2-Reachability.ps1` | `328899F930843910` |
| `harness/H3-CompileAxiom.ps1` | `11C735501DDBA439` |
| `harness/H4-PatchIntegrity.ps1` | `21C3C44954FE025C` |

(SHA in atas = checkout CRLF kami on 2026-10-17; for file
tak-terpin, normalisasi LF dulu bila membandingkan with entri manifest
mereka. Tidak ada file which disalin ke repo kita; tersedia in path
temp in atas bila portofolio memutuskan mengadopsi.)

## 5. Sikap MSAF

Eksternal; no diaudit oleh kita; angka Â§1 = artefak terukur mereka +
verifikasi hash kita (Â§2); no ada verdict MSAF which berubah and no
ada klaim which diadopsi. Lisensi artefak audit mereka: MIT (kode) /
CC-BY-4.0 (docs); source Lean: Apache-2.0 (OpenAI) â€” atribusi lengkap
ada in repo mereka.

Ditulis 2026-10-17 (sesi analisis; read-only on repo source).


