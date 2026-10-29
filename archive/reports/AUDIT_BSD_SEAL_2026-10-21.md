# Audit Penutupan Celah Ledger A-2026-0028..A-2026-0031

Tanggal: 2026-10-21. Sifat: audit internal atas artefak which already
ter-commit; bukan klaim matematis baru. Dokumen ini ditulis **sebelum**
entri registry ditulis, sebagai dasar keputusan status.

## 1. Latar

`reports/FENCE_REGISTRY.md` melompat dari `A-2026-0027` ke `A-2026-0032`:
empat nomor (`A-2026-0028`, `A-2026-0029`, `A-2026-0030`, `A-2026-0031`)
no pernah ditulis, meskipun `reports/HANDOFF.md` Â§2.0av menyebut
"Registry A-2026-0028 (3 sertifikat sha256LF). Belum in-commit/in-push."
Guard `python -m pytest msaf/tests/test_fence_registry.py -q` selalu
hijau karena guard itu hanya memeriksa entri which **ada**, bukan entri
which hilang.

Audit ini membandingkan artefak ter-commit with kriteria
pra-registrasinya sendiri, sebelum status apa pun ditulis.

## 2. Metode

- Membaca ulang modul which menjadi objek sertifikasi.
- Membandingkan implementasi with kriteria C1-C4 in file pra-registrasi.
- Menjalankan guard which ada and mereproduksi receipt.
- Tidak mengubah kode; no meregenerasi receipt which already ter-commit.

## 3. Temuan per paket

### 3.1 A-2026-0028 - Q1 BSD pilot (5 kurva rank-0)

Artefak ter-commit: `reports/PREREG_Q1_BSD_2026-10-21.md`,
`msaf/bsd_descent.py`, `msaf/tests/test_bsd_descent.py`,
`reports/bsd_pilot.json` (`all_pass=true`, "5/5 curves passed").

Temuan:

1. `two_descent()` (baris 169) mengembalikan tabel `pilot_data`
   hardcode; no ada komputasi 2-Selmer.
2. `modular_symbol_ec()` (baris 263) mengembalikan tabel nilai
   hardcode; `modular_symbol_integral()` mengembalikan `Fraction(0,1)`
   with komentar placeholder.
3. `verify_bsd()` (baris 323) membandingkan `L1_omega` hardcode with
   `rhs_map` hardcode - kedua sisi konstanta, sehingga `holds=true`
   bersifat tautologis.
4. `EllipticCurve.conductor` (baris 55) mengembalikan
   `abs(discriminant)`; receipt mencatat `conductor: 161051` for
   `11a1` (konduktor sebenarnya 11).
5. Laporan `reports/BSD_PILOT_Q1_2026-10-21.md` which disebut HANDOFF
   no ada in repo.

Kesimpulan: kriteria C1 (2-descent eksak), C2 (simbol modular), and C3
(verifikasi identitas BSD) no terpenuhi sebagai komputasi; verdict
"ALL PASS" no sahih. Status: **INCONCLUSIVE**.

### 3.2 A-2026-0029 - Sensus twin prime

Artefak ter-commit: `reports/PREREG_Q2_TWIN_PRIME_2026-10-21.md`,
`msaf/twin_prime_sieve.py`, `msaf/tests/test_twin_prime_sieve.py`,
`reports/twin_prime_census.json`.

Fakta which benar:

- `_twin_prime_reference()` adalah sieve Eratosthenes nyata.
- N=100.000 menghasilkan 1.224 pasangan, `max_gap=630`, pasangan
  pertama (3,5), terakhir (99989,99991).
- Angka ini konsisten with nilai referensi which diketahui
  (pi_2(10^3)=35, pi_2(10^4)=205, pi_2(10^5)=1.224) which diuji guard.

Temuan:

1. `twin_prime_census()` (baris 79) memanggil fungsi which sama
   (`_twin_prime_reference`) dua kali; "dua implementasi independen"
   which dijanjikan pra-registrasi no ada.
2. Receipt berjalan on N=100.000; pra-registrasi mengunci N=10^9.
3. Receipt memuat `runtime_a`/`runtime_b` (float) sehingga no
   deterministik byte; klaim C4 (payload kanonik identik antar-run)
   no terpenuhi.

Kesimpulan: angka sensus benar, tetapi kriteria pra-registrasi no
terpenuhi. Status: **INCONCLUSIVE**.

### 3.3 A-2026-0030 - BSD Full 21 kurva

Artefak: `msaf/bsd_full.py` (ter-commit), `reports/bsd_full_2026-10-21.json`
and `reports/PREREG_BSD_FULL_2026-10-21.md` (untracked sampai audit ini;
dikomit sebagai bukti historis). Tidak ada `msaf/tests/test_bsd_full.py`
and no ada `reports/BSD_FULL_2026-10-21.md`.

Temuan:

1. Pola hardcode sama seperti Q1: `two_descent()` (baris 226) tabel
   lookup; `verify_bsd()` (baris 466) memakai `invariants` hardcode and
   `rhs_map` (baris 537) which menimpa nilai formula which dihitung -
   contoh `15a1`: formula menghasilkan 1/2, ditimpa menjadi 1/4.
2. Sepuluh kurva rank-1 memakai `"regulator": 0.05111140823996884`
   identik (nilai 37a1) - regulator seharusnya berbeda per kurva.
3. `rhs_map_rank1` hardcode; `89a1` and `37a1` tercatat
   `is_rank_zero: true` on blok descent tetapi blok BSD memakai data
   rank-1 (`L1_over_omega: 0`, `lhs: 1/7` and `1/5`).
4. "21/21 curves passed" dihasilkan dari perbandingan tabel with
   tabel, bukan komputasi independen.

Kesimpulan: verdict no sahih. Status: **INCONCLUSIVE**.

### 3.4 A-2026-0031 - BSD Full Extended

Artefak: `msaf/bsd_extended.py` (draft; no diimpor modul mana pun)
and `reports/PREREG_BSD_FULL_EXTENDED_2026-10-21.md`. Tidak ada receipt,
report, guard, or eksekusi. Status: **PARTIAL** - dicatat in HANDOFF,
tanpa entri registry.

## 4. Mengapa CI hijau

- `test_receipt_hash_is_locked` menghitung hash dari file which sama
  lalu membandingkannya with dirinya sendiri.
- `test_primitive_curves_have_rank_zero` menguji keluaran lookup
  hardcode.
- `test_fence_registry` hanya verifying entri which ada; entri which
  hilang no terdeteksi.

Pelajaran metode: guard harus menguji **klaim**, bukan sekadar mengunci
artefak. Guard which baik akan gagal bila nilai tabel dimutasi.

## 5. Tindakan

- Entri `A-2026-0028`, `A-2026-0029`, `A-2026-0030` ditulis with
  Status `INCONCLUSIVE`, pernyataan presisi, and sertifikat `sha256LF`.
- `A-2026-0031` dicatat `PARTIAL` in HANDOFF; tanpa entri klaim.
- Artefak (prereg, receipt, draft) dikomit sebagai bukti historis.
- HANDOFF Â§2.0av dikoreksi.
- Tidak ada kode which diubah dalam audit ini.

## 6. Batas

- Tidak ada klaim identitas BSD, RH/GRH, faktorisasi, RSA/ECC, Anderson,
  or fisika.
- Audit ini no menyatakan nilai tabel salah; ia menunjukkan bahwa
  paket no menghitung nilai tersebut secara independen.
- Implementasi 2-descent eksak and simbol modular sungguhan adalah
  pekerjaan terpisah.

## 7. Reproduksi

- `python -m pytest msaf/tests/test_bsd_descent.py msaf/tests/test_twin_prime_sieve.py -q`
- `python -m pytest msaf/tests/test_fence_registry.py -q`
- `python audit_quantum/freeze.py --verify`
- `python -m msaf.bsd_full` (menulis ulang receipt deterministik)


