# Pra-registrasi Q3 v3 â€” Sensus abc Lengkap hingga C = 10^7 â€” 2026-10-27

**Status:** scope DIKUNCI for Q3 v3; implementasi v3 belum in-commit.
Berkas ini menggantikan Q3 v2 (`PREREG_Q3_ABC_CENSUS_V2_2026-10-27.md`,
sha256LF `c638ba86767f38ca1fc0fa70b4d96980ae893fef1c5c852fde6bb98bb70db24a`).
Hash `sha256LF` file ini dihitung setelah isi dibekukan and dicatat in
receipt and report; no ada placeholder.

**Alasan supersession (bukti baru):** Q3 v2 mengunci `max_prime=100`. Itu
bukan limit which sah for kelengkapan. Batas which benar hanya
`rad(abc) < c^(5/7)`, sehingga faktor prima individual boleh jauh in atas 100.
Run v2 on C=10^7 menemukan 12 triple; enumerasi lengkap berbasis limit rad
menemukan 17 triple. Lima triple which hilang:

| Triple | Faktor prima > 100 | q |
|---|---|---|
| (5, 177147, 177152) | 173 | 1.412681 |
| (25, 4804839, 4804864) | 137 | 1.413279 |
| (43840, 4782969, 4826809) | 137 | 1.413698 |
| (2, 6436341, 6436343) | 109 | 1.629912 |
| (11, 9565927, 9565938) | 167 | 1.428323 |

Karena itu v2 hanya sah sebagai sensus parsial bilangan 100-halus, bukan
sensus lengkap. v3 menggantinya with enumerasi low-rad which lengkap.

**Tidak mengubah:** `A-2026-0032` (klaim 6 triple C=100.000 tetap benar),
P0/P1/P2, `shp_asymmetric_wager`, and `shp_bridge`.

## 1. Definisi which dikunci

- **Triple valid:** a, b, c âˆˆ â„•, a + b = c, a < b < c, gcd(a,b,c) = 1.
- **Radikal:** rad(n) = produk faktor prima unik dari n.
- **Kualitas:** q(a,b,c) = log(c) / log(rad(aÂ·bÂ·c)).
- **Threshold:** q > 1.4.
- **Batas rad:** `RAD_LIMIT(N) = floor(N^(5/7)) + 1`.
- **Low-rad set:** `L_N = {n âˆˆ [1,N] : rad(n) â‰¤ RAD_LIMIT(N)}`.
- **C which dikunci:** gate 10^5, validasi 10^6, full 10^7.

## 2. Justifikasi kelengkapan

Jika q > 1.4 maka:

```text
log(c) / log(rad(abc)) > 1.4
log(rad(abc)) < (5/7) log(c)
rad(abc) < c^(5/7) â‰¤ N^(5/7)
```

Karena `rad(a) â‰¤ rad(abc)`, `rad(b) â‰¤ rad(abc)`, and `rad(c) â‰¤ rad(abc)`,
maka a, b, c semuanya berada in `L_N`. Jadi enumerasi atas `L_N` lengkap:
no ada triple q > 1.4 which dapat lolos.

## 3. Algoritma which dikunci

### 3.1 Aturan kandidat (sama for A and B)

1. Iterasi c âˆˆ L_N with c â‰¥ 3.
2. Uji eksak integer `rad(c)^7 < c^5`; jika no, lewati.
3. Untuk setiap a âˆˆ L_N which diurutkan berdasarkan rad, with
   `rad(a) â‰¤ floor(c^(5/7) / rad(c)) + 2` and `2a < c`:
   - b = c âˆ’ a;
   - jika b âˆ‰ L_N, lewati;
   - uji eksak integer `(rad(a)Â·rad(b)Â·rad(c))^7 < c^5`; jika no, lewati;
   - jika gcd(a,b) â‰  1, lewati (for a+b=c, ini ekuivalen with
     gcd(a,b,c)=1);
   - hitung q with `math.log` float64; terima jika q > 1.4.
4. `max_gap` = maksimum `a_sekarang âˆ’ a_sebelumnya` dalam urutan c menaik.

Penggunaan `+2` on limit `rad(a)` hanyalah kelonggaran float; uji eksak
integer which menentukan. Uji `prod^7 < c^5` ekuivalen eksak with q > 1.4
dalam aritmetika real. `q` float64 hanya dipakai for pelaporan and
verifikasi akhir.

### 3.2 Sieve A

- `_rad_sieve(N)`: multiplicative rad sieve satu lintasan.
- Bangun `L_N` with scan `rad`, `bytearray` keanggotaan, and urutan
  `low_by_rad` berdasarkan rad.
- Loop kandidat seperti Â§3.1.

### 3.3 Sieve B

- `_rad_sieve_segmented(N)`: segmented rad sieve on `array("I")`.
- Bangun `L_N` secara independen dari rad B (scan sendiri, bukan impor A).
- Loop kandidat with kode terpisah (while-loop, akses array).
- Re-verifikasi setiap triple final with `sympy.factorint` on `aÂ·bÂ·c`.
  `factorint` no dipanggil for setiap bilangan 3..N.

### 3.4 Chunking and checkpoint

- Checkpoint menyimpan `next_index` per sieve, count, max_gap, last_a,
  pairs, runtime, and done.
- `--max-seconds` (default 900) menghentikan chunk and menulis checkpoint.
- Resume harus menghasilkan `canonical_sha256` identik with run bersih.
- Receipt hanya ditulis setelah kedua sieve mencapai akhir.

## 4. Konfigurasi which dikunci

| Parameter | Nilai |
|---|---|
| N_gate | 100.000 |
| N_validate | 1.000.000 |
| N_full | 10.000.000 |
| Threshold | 1.4 |
| RAD_LIMIT | floor(N^(5/7)) + 1 |
| max_seconds per chunk | 900 |
| segment_size | 1.048.576 |

Tidak ada parameter which diubah setelah result terlihat, kecuali amendment
bertanggal which dicatat sebelum perubahan.

## 5. Receipt and determinisme

Receipt JSON minimal:

```json
{
  "schema": "msaf.abc_census.v3",
  "N": 10000000,
  "threshold": 1.4,
  "rad_limit": 100001,
  "candidate_rule": "low-rad enumeration; exact prod^7 < c^5",
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
  "factorint_verified": true,
  "verdict": "ALL PASS",
  "canonical_sha256": "..."
}
```

- `canonical_sha256` dihitung dari payload tanpa `runtime_a`, `runtime_b`, and
  `canonical_sha256`, with `json.dumps(sort_keys=True,
  separators=(",", ":"))`.
- Dua run C=10^5 harus menghasilkan `canonical_sha256` identik.
- Receipt ditulis ke `--out` melalui file `.tmp` lalu `os.replace`.

## 6. Kriteria penerimaan (C1â€“C7)

- **C1 â€” Gate C=10^5:** `count=6`, `max_gap=6825`, `pairs_a == pairs_b`,
  sama with `A-2026-0032`.
- **C2 â€” Validasi C=10^6:** `count=11`, `max_gap=6825`, `pairs_a == pairs_b`;
  termasuk (5, 177147, 177152).
- **C3 â€” Full C=10^7:** `count=17`, `max_gap=40640`, `pairs_a == pairs_b`;
  termasuk lima triple with prima > 100 on tabel in atas.
- **C4 â€” Determinisme:** `canonical_sha256` C=10^5 identik on dua run;
  resume dari checkpoint menghasilkan receipt sama with run bersih.
- **C5 â€” Receipt/progress:** file `--out` ada; progress log non-kosong; no
  ada placeholder hash.
- **C6 â€” Independensi:** B no mengimpor fungsi internal A; `factorint`
  hanya dipakai for verifikasi final.
- **C7 â€” Kebersihan:** no ada `numpy`/`scipy` in core; uji eksak integer
  `prod^7 < c^5`; limit float64 `q` ditulis eksplisit.

## 7. Verdict

- **ALL PASS:** C1â€“C7 terpenuhi.
- **FAILED:** salah satu kriteria gagal.
- **INCONCLUSIVE:** OOM, tool error, hash mismatch, or `sympy` no
  tersedia for verifikasi final.

`A-2026-0032` tetap menjadi sertifikat C=100.000 and no diubah klaimnya.
Registry baru `A-2026-0052` diusulkan setelah `ALL PASS`; status akhir
menunggu keputusan pemilik.

## 8. Falsifier

- Gate C=10^5 no mereproduksi 6/6825.
- C=10^6 no menghasilkan 11/6825 or kehilangan (5,177147,177152).
- C=10^7 no menghasilkan 17/40640 or kehilangan salah satu dari lima
  triple non-100-smooth.
- `pairs_a != pairs_b` on C which dikunci.
- Receipt no ditulis or `canonical_sha256` berbeda on dua run.
- Resume menghasilkan result berbeda dari run bersih.
- B mengimpor kode internal A or memakai `factorint` for seluruh rentang.
- Memori melebihi limit sistem (OOM).

## 9. Artefak and urutan eksekusi

1. Bekukan and hash file pra-registrasi ini.
2. Commit and push pra-registrasi **sebelum** commit implementasi v3.
3. Implementasi `msaf/abc_census.py` v3 and guard
   `msaf/tests/test_abc_census.py`.
4. Jalankan gate C=10^5; perbaiki bila gagal.
5. Jalankan validasi C=10^6; simpan receipt.
6. Jalankan full C=10^7; simpan receipt and progress log.
7. Tulis `reports/ABC_CENSUS_2026-10-27.md` with angka verbatim.
8. Perbarui registry `A-2026-0052` secara aditif; jalankan guard registry.

## 10. Batas eksplisit

- Hanya C = 10^7 for kampanye penuh; C=10^5 and C=10^6 adalah gate.
- Threshold q > 1.4; no ada threshold lain.
- Sensus finit; bukan pembuktian konjektur abc, bukan klaim asimtotik.
- Tidak ada klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, or fisika.
- `q` memakai float64 `math.log`; uji kelengkapan memakai integer eksak.


