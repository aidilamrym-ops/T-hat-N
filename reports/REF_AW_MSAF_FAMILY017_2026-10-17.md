# REF — Vault audit "MSAF Family 017" oleh proyek lain (eksternal) — 2026-10-17

Status: **Referensi eksternal; bukan hasil MSAF; dikomit 2026-10-17 (batch strategi).**
Sumber: `https://github.com/aidilamrym-ops/the-asymmetric-wager-msaf-family017`
(HEAD `7db7d46bc745945b29e1bfae80c8812f6479ed32`, 2026-10-10 17:59 +0800;
tag `v1.0.0`). Disalin sebagai clone kerja ke
`C:\Users\usER\AppData\Local\Temp\opencode\aw_msaf_family017` (temp;
tidak ada penulisan ke repo sumber). Berguna sebagai: prior-art
metode harness/registry untuk portofolio kita (P3/P5) dan peta
ekosistem dual-core proyek lain (Core B:
`guinand-weil-rigorous-numerics`) untuk P4.

## 1. Apa itu

Vault audit + certificate + release untuk OpenAI Family 017
(`OAI.NumberTheory.PiExponent`, eksponen irasionalitas pi):

- 869 sumber Lean (copy subtree OAI, Apache-2.0) + 4.345 artefak bukti
  (`proofs/OAI/**`); total repo ≈ 272,9 MB (5.262 berkas non-`.git`).
- `MANIFEST.sha256` (850.044 byte; 5.252 entri; **path absolut staging
  `D:\MSAF_CLEAN_DEPLOY\…`**) + 10 eksklusi terdokumentasi (self, README,
  RELEASE, `config/patches/README.md`, `.gitattributes`, 5 berkas
  `.github/`).
- Harness PowerShell: `build_sequential.ps1` + H1 (escape-token, canary
  positif wajib), H2 (reachability), H3 (compile axiom), H4 (patch
  integrity).
- `config/`: pins `lakefile.lean`, `lake-manifest.json`, `lean-toolchain`
  (`v4.34.1`), + 23 patch kompatibilitas dependensi pihak ketiga.
- Klaim verdict mereka (kata mereka): 869/869 modul elaborated; 0 escape
  token (semua kelas hazard); footprint aksioma
  `[propext, Classical.choice, Quot.sound]` pada 3 deklarasi entry;
  Anti-Circularity Gate `lean` `FAIL=0 NOT_RUN=0` → PASS; dua anomali
  harness (H2/H3) didisklose terbuka.

## 2. Verifikasi silang MSAF (2026-10-17, dari clone kami)

- `MANIFEST.sha256` = `18B72FC8…` ✓ (persis payload rilis mereka);
  certificate = `07121A53…` ✓; hitungan 5.262 berkas ✓; 5.252 baris ✓;
  869 sumber ✓; 4.345 artefak ✓.
- **Verifikasi per-entri (kita, 5.252 entri dihitung ulang):**
  3.477 bit-exact; 1.774 beda **hanya line-ending** (manifest LF vs
  checkout CRLF — konversi autocrlf; 0 beda konten setelah normalisasi);
  **1 entri (`NOTICE`, baris 906) tidak tereproduksi** dari konten repo —
  diuji 48 kombinasi BOM × EOL × final-newline × UTF-16 atas (a) berkas
  checkout kami dan (b) blob git `39c578d8…` (satu-satunya commit yang
  menyentuh `NOTICE`; riwayat penuh setelah unshallow) — tidak ada yang
  cocok; hash entri unik di manifest (COUNT=1, bukan mix-up).
  Tafsir paling mungkin: salinan staging `NOTICE` berbeda dari yang
  di-commit saat lock, atau satu entri hash keliru. **Tidak
  load-bearing** (berkas atribusi lisensi 159 byte; verdict mereka
  berdiri di artefak Lean/kernel/certificate). Dicatat sebagai limit
  bila mengutip vault ini.
- Teknik byte-pin `.gitattributes` mereka terbukti bekerja: `MANIFEST`
  (`-text`) dan certificate (`eol=crlf`) keduanya cocok apa-adanya.

## 3. Yang kita ambil (metode saja; tidak ada klaim matematis)

- **H1**: scanner escape-token wajib punya **canary positif hidup**
  ("harness yang melaporkan 0 token tanpa membuktikan bisa mendeteksi =
  sampah"); exit contract 0/1/2. Prinsip validitas yang sama dengan skill
  anti-circularity kita; prior-art bagus untuk P3/P5.
- **H3 pelajaran**: exit code skrip BUKAN otoritas — literal stdout
  kernel (`#print axioms`, exit 0) yang menjadi bukti; selaras dengan
  disiplin kita "footer log runner otoritatif, bukan ExitCode
  Start-Process".
- **`.gitattributes` byte-pinning** untuk berkas ber-hash terbit
  (`-text` / `eol=crlf`) — teknik untuk CI guard P3 (imutabilitas hash
  terbit lintas checkout).
- **Manifest + tabel eksklusi eksplisit** (10 eksklusi ber-alasan) —
  prior-art untuk registry lock P3/P5.
- **Build sekuensial frontier** (satu proses; unit kegagalan = unit
  eksekusi; verifikasi artefak per langkah; nol proses residu) —
  sejalan dengan disiplin kita "satu kampanye berat sekaligus".
- **Dual-core A/B** (formal Lean ↔ numerik Arb; "agreement is checked,
  not assumed"; Core B = repo `aidilamrym-ops/guinand-weil-rigorous-numerics`,
  mesin Arb/LDLᵀ) — analog struktural untuk L2 dan kandidat rujukan P4
  (belum kami periksa; TO-PIN bila mau dipakai).

## 4. Pin untuk salin-ulang (working-tree clone, SHA-256 first16)

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

(SHA di atas = checkout CRLF kami pada 2026-10-17; untuk berkas
tak-terpin, normalisasi LF dulu bila membandingkan dengan entri manifest
mereka. Tidak ada berkas yang disalin ke repo kita; tersedia di path
temp di atas bila portofolio memutuskan mengadopsi.)

## 5. Sikap MSAF

Eksternal; tidak diaudit oleh kita; angka §1 = artefak terukur mereka +
verifikasi hash kita (§2); tidak ada verdict MSAF yang berubah dan tidak
ada klaim yang diadopsi. Lisensi artefak audit mereka: MIT (kode) /
CC-BY-4.0 (docs); sumber Lean: Apache-2.0 (OpenAI) — atribusi lengkap
ada di repo mereka.

Ditulis 2026-10-17 (sesi analisis; read-only pada repo sumber).
