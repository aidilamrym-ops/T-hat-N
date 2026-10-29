# Pra-registrasi Q3 v2 â€” Receipt, Progress, and Sensus abc C=10^7 â€” 2026-10-27

**Status:** scope DIKUNCI for Q3 v2; implementasi and eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode Q3 v2. Hash `sha256LF` file ini
dihitung setelah isi dibekukan and dicatat in receipt serta report; no ada
placeholder.

**Menggantikan:** run eksploratori 2026-10-27 03:35:35â€“04:55:48 (PID 15272).
Run itu dihentikan setelah 1:20:12 (CPU 4.664,6 s, RAM ~382 MB) tanpa receipt
karena `main()` mengabaikan `--out` and Sieve B memanggil `sympy.factorint`
for setiap bilangan 3..N. Run itu **no certifiable** and no menjadi
section dari klaim apa pun.

**Tidak mengubah:** `A-2026-0032` (C=100.000), P0/P1/P2, registry which ada,
`shp_asymmetric_wager`, and `shp_bridge`.

## 1. Maksud and limit

Q3 v2 memperbaiki pipeline sensus abc agar:

1. **Receipt benar-benar ditulis** ke path `--out` secara atomik.
2. **Progress terlihat** per fase and per chunk, no menggantung tanpa log.
3. **Sieve B no lagi O(N) factorint** for membangun daftar bilangan halus.
4. **Run panjang bisa dipecah** menjadi chunk with checkpoint/resume, agar
   laptop no dipaksa bekerja monolitik berjam-jam.
5. **Validasi bertahap:** C=10^5 (gate), C=10^6 (validasi), C=10^7 (full).

Paket ini **bukan**:

- Pembuktian konjektur abc; hanya sensus finit hingga C which dikunci.
- Klaim asimtotik, RH, GRH, faktorisasi, RSA/ECC, Anderson, or fisika.
- Klaim bahwa q dihitung with interval arithmetic rigorous. `q` memakai
  `math.log` float64; triple which dilaporkan adalah integer eksak and
  diverifikasi ulang. Batas ini harus ditulis in receipt and report.

## 2. Definisi which dikunci

- **Triple valid:** a, b, c âˆˆ â„•, a + b = c, a < b < c, gcd(a,b,c) = 1.
- **Radikal:** rad(n) = produk faktor prima unik dari n.
- **Kualitas:** q(a,b,c) = log(c) / log(rad(aÂ·bÂ·c)).
- **Threshold:** q > 1.4.
- **Bilangan halus:** semua faktor prima â‰¤ 100.
- **C which dikunci:** gate 10^5, validasi 10^6, full 10^7.

## 3. Algoritma which dikunci

### 3.1 Sieve A â€” linear rad sieve + smooth numbers

- `_rad_sieve(N)`: sieve linear for rad(n), seperti implementasi C=100.000.
- `_generate_smooth_numbers(N, 100)`: enumerasi rekursif bilangan 100-halus.
- Loop c and a seperti implementasi C=100.000, with micro-optimasi which
  **no mengubah matematika**:
  - binding lokal for `rad`, `smooth`, `gcd`, `log`;
  - cek produk `ra*rb*rc >= c` sebelum `gcd` bila aman;
  - hindari `gcd` berulang for pasangan which sama.
- Tidak memakai `numpy`, `scipy`, or `sympy`.

### 3.2 Sieve B â€” segmented rad sieve + heap smooth + sympy re-check

- Bangun `rad_b[1..N]` with **segmented sieve** which no memakai
  `_rad_sieve` milik A.
- Bangun daftar bilangan 100-halus with **min-heap** (bukan fungsi rekursif
  A).
- Hitung kandidat with `rad_b` and koreksi gcd; **no** memanggil
  `factorint` for setiap bilangan 3..N.
- Untuk setiap triple final with q > 1.4, verifikasi ulang `rad(aÂ·bÂ·c)`
  with `sympy.factorint`. Ini menjaga pemeriksaan independen on result,
  bukan on seluruh ruang.
- Tidak mengimpor fungsi internal A.

### 3.3 Chunking and checkpoint

- Kedua sieve memakai daftar c which sama (bilangan 100-halus terurut).
- `--max-seconds` (default 900) menghentikan run setelah limit waktu and
  menulis checkpoint.
- Checkpoint berisi: `schema`, `N`, `sieve`, `next_index`, `count`,
  `max_gap`, `last_a`, `pairs`, `prereg_sha256lf`.
- `--resume <checkpoint>` melanjutkan dari `next_index`; result akhir harus
  identik with run bersih.
- Receipt hanya ditulis setelah kedua sieve mencapai akhir.

## 4. Konfigurasi which dikunci

| Parameter | Nilai |
|---|---|
| N_gate | 100.000 |
| N_validate | 1.000.000 |
| N_full | 10.000.000 |
| Threshold | 1.4 |
| max_prime | 100 |
| max_seconds per chunk | 900 (15 menit) |
| segment_size | 1.048.576 |

Tidak ada parameter which diubah setelah result terlihat, kecuali amendment
bertanggal which dicatat sebelum perubahan.

## 5. Receipt and determinisme

Receipt JSON minimal:

```json
{
  "schema": "msaf.abc_census.v2",
  "N": 10000000,
  "threshold": 1.4,
  "count": 0,
  "max_gap": 0,
  "first_triple": null,
  "last_triple": null,
  "count_a": 0,
  "count_b": 0,
  "max_gap_a": 0,
  "max_gap_b": 0,
  "pairs_a": [],
  "pairs_b": [],
  "runtime_a": 0.0,
  "runtime_b": 0.0,
  "prereg_sha256lf": "...",
  "module_sha256lf": "...",
  "canonical_sha256": "..."
}
```

- `canonical_sha256` dihitung dari payload tanpa `runtime_a`, `runtime_b`, and
  `canonical_sha256` itu sendiri, with `json.dumps(sort_keys=True,
  separators=(",", ":"))`.
- Dua run C=10^5 harus menghasilkan `canonical_sha256` identik.
- Receipt ditulis ke `--out` melalui file `.tmp` lalu `os.replace`.

## 6. Kriteria penerimaan (C1â€“C7)

- **C1 â€” Gate C=10^5:** `count=6`, `max_gap=6825`, `pairs_a == pairs_b`, and
  sama with `A-2026-0032`.
- **C2 â€” Validasi C=10^6:** kedua sieve sepakat on count, max_gap, and pairs;
  receipt ditulis.
- **C3 â€” Full C=10^7:** kedua sieve sepakat; receipt ditulis; progress log
  lengkap.
- **C4 â€” Determinisme:** `canonical_sha256` C=10^5 identik on dua run;
  resume dari checkpoint C=10^6 menghasilkan receipt which sama with run
  bersih.
- **C5 â€” Receipt/progress:** file `--out` ada; progress log non-kosong; no
  ada placeholder hash.
- **C6 â€” Independensi:** B no mengimpor fungsi internal A; `factorint`
  hanya dipakai for verifikasi final.
- **C7 â€” Kebersihan:** no ada `numpy`/`scipy` in core; limit float64 `q`
  ditulis eksplisit in receipt and report.

## 7. Verdict

- **ALL PASS:** C1â€“C7 terpenuhi.
- **FAILED:** salah satu kriteria gagal.
- **INCONCLUSIVE:** OOM, tool error, or hash mismatch.

Registry baru hanya diusulkan setelah `ALL PASS`; ID no dikunci in file
ini. `A-2026-0032` tetap menjadi sertifikat C=100.000 and no diubah.

## 8. Falsifier

- Gate C=10^5 no mereproduksi 6/6825.
- `pairs_a != pairs_b` on C which dikunci.
- Receipt no ditulis or `canonical_sha256` berbeda on dua run.
- Resume menghasilkan result berbeda dari run bersih.
- B mengimpor kode internal A or memakai `factorint` for seluruh rentang.
- Memori melebihi limit sistem (OOM).

## 9. Artefak and urutan eksekusi

1. Bekukan and hash file pra-registrasi ini.
2. Commit and push pra-registrasi **sebelum** commit implementasi.
3. Implementasi `msaf/abc_census.py` and guard
   `msaf/tests/test_abc_census.py`.
4. Jalankan gate C=10^5; perbaiki bila gagal.
5. Jalankan validasi C=10^6; simpan receipt.
6. Jalankan full C=10^7 secara chunked; simpan receipt and progress log.
7. Tulis `reports/ABC_CENSUS_2026-10-27.md` with angka verbatim.
8. Registry hanya setelah verdict `ALL PASS` and keputusan pemilik.

## 10. Batas eksplisit

- Hanya C = 10^7 for kampanye penuh; C=10^5 and C=10^6 adalah gate.
- Threshold q > 1.4; no ada threshold lain.
- Tidak ada klaim konjektur abc terbukti/no terbukti.
- Tidak ada klaim asimtotik.
- Tidak ada klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, or fisika.
- `q` memakai float64 `math.log`; ini limit which diketahui, bukan interval
  arithmetic rigorous.


