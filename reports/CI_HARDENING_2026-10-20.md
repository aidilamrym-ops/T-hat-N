# Hardening jalur verifikasi CI (2026-10-20)

**Status:** jalur baru ditambahkan; bukti lokal tercatat. Status push/CI
dicatat in `reports/HANDOFF.md` Â§2.0ah setelah commit.
**Scope:** menambah dua jalur verifikasi nyata which sebelumnya no ada:
audit aksioma Lean per-deklarasi and kompilasi ulang Coq Paket 8/9 in CI.
**Yang no diubah:** report beku Paket 7â€“9, `reports/FENCE_REGISTRY.md`
entri lama, `lean/spec/XiAnalyticSpec.lean`, and trusted base Coq empat
aksioma stdlib.

## 1. Latar

Sebelum 2026-10-20, CI hanya menjalankan:

- `python -m pytest msaf -q` (guard statis, termasuk guard Coq which no
  mengompilasi Coq);
- `lake build` plus sensor escape-token statis in job `lean-kernel`.

Dua celah which ditutup:

1. `#print axioms` per-deklarasi already ada sebagai tes
   (`msaf/tests/test_lean_axiom_audit.py`) tetapi **no dijalankan** in
   CI, jadi kernel Lean bisa saja bergantung on aksioma tambahan tanpa
   CI gagal.
2. Tidak ada job Coq sama sekali. Paket 7â€“9 hanya dijaga oleh tes statis
   (pencocokan string/statement), bukan kompilasi `coqc`/`coqchk`.

## 2. Perubahan CI

### 2.1 Audit aksioma Lean (`lean-kernel`)

Langkah baru setelah `lake build`:

```text
python -m pip install --disable-pip-version-check pytest
python -m pytest msaf/tests/test_lean_axiom_audit.py::test_every_declaration_uses_standard_axioms_only -q
```

Tes ini memanggil `lake env lean` per deklarasi and gagal jika ada
deklarasi kernel which bergantung on aksioma in luar
`propext`/`Classical.choice`/`Quot.sound`. Scope tetap 83 deklarasi
kernel; `lean/spec/` and `lean/spec_v2/` in luar scope and tetap
kondisional.

**Fakta lokal:** `lake build` 3.089 job, 105,8 detik; audit 18,6 detik,
1 passed, 83 deklarasi. `lean/spec_v2/XiAnalyticSpecV2.lean` dikompilasi
oleh step terpisah (lihat report V2).

### 2.2 Job Coq (`coq-kernel`)

Job baru menjalankan skrip Paket 8 and Paket 9 in dalam container Coq
which dipin:

```text
coqorg/coq:8.20.1@sha256:18ebf3da56e60e3ddfd7d4e51f4c53d10241a129f34e93dacbc71562dd43c57a
```

Langkah:

1. `coqc --version` (bukti toolchain which dipakai);
2. `bash check_integral_limit.sh` (Paket 8, `A-2026-0013`);
3. `bash check_integral_infinite.sh` (Paket 9, `A-2026-0014`).

Kedua skrip menyalin source ke directory sementara, menjalankan `coqc`,
lalu `coqchk`, and gagal keras jika jumlah result, set aksioma, or
`Modules were successfully checked` no sesuai. Scope: hanya `f_k`
(`k â‰¥ 1`, `N â‰¥ 1`), trusted base empat aksioma stdlib; bukan `f` umum,
bukan eksponen real, bukan `[J]` periodic-box.

**Fakta lokal (WSL, Coq 8.20.1/OCaml 4.14.2):** limit 53,0 detik;
infinite 74,9 detik. Di CI, waktu tambahan termasuk pull image
(~1,36 GB) and kompilasi; timeout job 45 menit.

### 2.3 Guard statis jalur CI

`msaf/tests/test_ci_verification_paths.py` (5 uji) memastikan:

- step audit aksioma ada and berada setelah `lake build`, with
  instalasi pytest lebih dulu;
- job `coq-kernel` ada, memakai image+digest which dipin, mencetak versi
  `coqc`, and menjalankan kedua skrip dalam urutan Paket 8 â†’ Paket 9;
- no ada `continue-on-error` on jalur verifikasi;
- sensor `spec_v2` mengecualikan directory itu dari sensor kernel and
  mengunci budget 8 aksioma;
- lima mutasi negatif ditolak (hapus audit, hapus `lake build`, ganti
  image, hapus skrip Paket 9, tambah `continue-on-error`, hapus eksklusi
  `spec_v2`, ubah budget V2).

## 3. Batas

- Laporan ini mencatat **perubahan infrastruktur**, bukan result
  matematis baru.
- Coq CI **no** mengubah trusted base empat aksioma stdlib; no ada
  klaim bahwa tiga aksioma tercapai.
- Status `TOOL NOT RUN (NO_LEAN_FILES)` on report beku Paket 7â€“9 tetap
  berlaku for scope Coq historis; job baru no menulis ulang report
  itu.
- CI hijau belum diklaim in report ini; bukti push/run ID ada in
  HANDOFF. Jika CI gagal, status registry diperbarui sesuai skema
  (status/relasi/note; entri no dihapus).
- Tidak ada klaim RH/Pâ‰ NP/fisika; bukan peer review.

## 4. Perintah verifikasi lokal

```text
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml', encoding='utf-8'))"
python -m pytest msaf/tests/test_ci_verification_paths.py -q
python -m pytest msaf/tests/test_lean_axiom_audit.py -q
python -m pytest msaf/tests/test_xi_spec_v2.py -q
python -m pytest msaf -q
python audit_quantum/freeze.py --verify
```


