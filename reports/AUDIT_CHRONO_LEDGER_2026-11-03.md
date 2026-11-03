# Audit Independen: Pergeseran Hash Ledger Chrono (baris 13-17)

- **Tanggal:** 2026-11-03
- **Ruang lingkup:** `ledger/chrono_execution_ledger.jsonl` vs
  `msaf/tests/test_chrono_ledger.py`
- **Sifat:** audit forensik riwayat git, bukan audit matematis
- **Kesimpulan singkat:** pergeseran hash itu **nyata** dan merupakan
  **penulisan ulang riwayat**, bukan perbaikan. Ledger tidak ditulis ulang
  lagi oleh audit ini; sebagai gantinya dipasang pagar prefix-freeze.

## 1. Pertanyaan

`test_chrono_ledger.py` memverifikasi rantai hash secara internal
(`verify_chain`). Apakah hash pada baris fisik 13-17 pernah bergeser, dan
jika ya, apakah pergeseran itu konsisten dengan klaim "ledger hanya
di-append, tidak pernah ditulis ulang"?

## 2. Metode

1. Ambil blob ledger pada setiap commit yang menyentuh file tersebut
   (`git show <rev>:ledger/chrono_execution_ledger.jsonl`).
2. Hitung ulang `record_hash` dengan fungsi kanonik yang sama seperti
   `msaf/chrono_runtime/ledger.py`: JSON `sort_keys=True`,
   `separators=(",", ":")`, `ensure_ascii=True`, field `record_hash`
   dikeluarkan sebelum hashing.
3. Bandingkan `record_hash`, `previous_hash`, `execution_status`, dan
   `numerical_verdict` antar commit.
4. Periksa anchor `sha256LF` di `reports/FENCE_REGISTRY.md` dan klaim di
   `reports/chrono_rh_multi_track_receipt_2026-11-01.json`.

## 3. Temuan

### 3.1 Keadaan sebelum `e6ec63f` (commit `5df5533`, 2026-11-01)

Lima record memang sudah tidak konsisten: baris 13-17 (index 12-16)
memiliki `record_hash` yang tidak sama dengan hasil hitung ulang. Ini
konsisten dengan catatan receipt: `verify_chain_errors_at_head = 5`,
`first_broken_line = 13`, `last_index_at_head = 16`.

### 3.2 Commit `e6ec63f` (2026-11-02, "Stabilize ledger and resolve collection failures")

Commit ini mengubah 19 baris ledger sekaligus. Perbandingan hash:

| baris | hash lama | hash baru | status lama | status baru |
|---|---|---|---|---|
| 13 | `391e2b07a9f8` | `a4e6018ac6b1` | PASS | PASS |
| 14 | `eb68a5e2e96d` | `b3e465429442` | PASS | PASS |
| 15 | `a53ae1694ed6` | `3b9219def016` | **PENDING** | **PASS** |
| 16 | `28e9fcacd32d` | `f4d9f8d5d7ea` | PASS | PASS |
| 17 | `f1a93b9483f7` | `fd48c6bfebfe` | **NOT_VERIFIED** | **PASS** |
| 18 | `7fde38a19330` | `b554d25eb92e` | PASS | PASS |
| 19 | `49241ced717f` | `4eccbbd0d982` | PASS | PASS |

Baris 18-19 bergeser sebagai efek berantai `previous_hash`. Baris 1-12
tidak berubah hash-nya (hanya format spasi JSON yang dirapatkan), sehingga
perubahan terisolasi tepat pada rentang yang sudah rusak.

### 3.3 Anomali yang menyertai

1. **Dua status dinaikkan.** Baris 15 `PENDING` menjadi `PASS`; baris 17
   `NOT_VERIFIED` menjadi `PASS`.
2. **Baris 17 kini kontradiktif.** `execution_status` = `PASS`, tetapi
   `numerical_verdict` masih berbunyi
   `... localization 0/3, containment NOT_VERIFIED (supersedes index 15)`.
3. **Anchor registry di-re-pin pada commit yang sama.** Empat entri
   CERTIFIED mengubah `sha256LF` ledger dari
   `345b00142ebddb02efe9fca2c15d0d403bb4d313288f4b8b632655a87f103250`
   menjadi
   `ce26e84e5ca1a42b51c0b46c268fba6e4226f4ba8634d130bf0c8849551d51c0`.
4. **Klaim receipt menjadi tidak benar.** Receipt
   `chrono_rh_multi_track_receipt_2026-11-01.json` mencatat
   "the ledger was appended to, never rewritten". Klaim itu benar pada
   `5df5533`, tetapi tidak lagi benar setelah `e6ec63f`.
5. **README masih memuat klaim lama.** README baris 2029-2035 menyatakan
   "No certified registry entry and no ledger line was rewritten."

## 4. Penilaian

- Pergeseran hash **bukan** artefak pengukuran dan **bukan** efek
  line-ending: `record_hash` dihitung dari objek JSON yang sudah
  di-parse, sehingga CRLF/LF tidak berpengaruh.
- Perubahan `e6ec63f` membuat rantai **valid secara internal**, tetapi
  dengan mengubah 7 `record_hash` dan 2 `execution_status`. Itu adalah
  penulisan ulang riwayat, bukan perbaikan.
- `test_chrono_ledger.py` tidak dapat membedakan keduanya: `verify_chain`
  hanya memeriksa konsistensi internal, dan anchor eksternalnya
  (registry) diperbarui di commit yang sama. Guard-nya sirkular.
- Tingkat keparahan: **tinggi** untuk baris 17 (status PASS berhadapan
  dengan verdict NOT_VERIFIED), **sedang** untuk baris 15
  (PENDING menjadi PASS).

## 5. Tindakan

1. **Ledger tidak ditulis ulang lagi.** Isi saat ini dibekukan sebagai
   baseline: 10.778 byte (LF), `sha256LF
   ce26e84e5ca1a42b51c0b46c268fba6e4226f4ba8634d130bf0c8849551d51c0`.
2. **Pagar baru:** `test_chrono_ledger.py` menambahkan
   `test_ledger_prefix_is_frozen`, yang menghitung sha256 dari 10.778 byte
   pertama dan membandingkannya dengan konstanta baseline. Append tetap
   lolos; penulisan ulang record mana pun di 19 baris pertama gagal.
3. **Entri registry** `T-2026-0110` mencatat audit ini dan sertifikat
   pagar baru.
4. **Tidak ada** entri CERTIFIED yang ditulis ulang, dan tidak ada baris
   ledger yang dihapus.

## 6. Batas

- Pagar prefix-freeze tidak dapat mencegah commit yang menulis ulang
  ledger **dan** memperbarui konstanta baseline sekaligus. Yang dijamin
  adalah perubahan seperti itu harus eksplisit, terlihat di diff, dan
  tidak bisa lolos diam-diam.
- Bukti otoritatif tetap riwayat git; laporan ini adalah peta ke bukti
  tersebut, bukan penggantinya.
- Audit ini tidak menyentuh klaim matematis apa pun. Status `PASS` pada
  index 14 dan 16 tidak dipulihkan menjadi `PENDING`/`NOT_VERIFIED`
  karena pemulihan itu sendiri akan menjadi penulisan ulang riwayat
  ketiga; verdict tekstual di `numerical_verdict` tetap otoritatif.

## 7. Reproduksi

```text
python -m pytest msaf/tests/test_chrono_ledger.py -q
git show 5df5533:ledger/chrono_execution_ledger.jsonl
git show e6ec63f:ledger/chrono_execution_ledger.jsonl
git show e6ec63f -- ledger/chrono_execution_ledger.jsonl reports/FENCE_REGISTRY.md
```
