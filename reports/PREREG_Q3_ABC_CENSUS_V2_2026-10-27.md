# Pra-registrasi Q3 v2 — Receipt, Progress, dan Sensus abc C=10^7 — 2026-10-27

**Status:** scope DIKUNCI untuk Q3 v2; implementasi dan eksekusi **belum**
dimulai. Berkas ini ditulis sebelum kode Q3 v2. Hash `sha256LF` berkas ini
dihitung setelah isi dibekukan dan dicatat di receipt serta laporan; tidak ada
placeholder.

**Menggantikan:** run eksploratori 2026-10-27 03:35:35–04:55:48 (PID 15272).
Run itu dihentikan setelah 1:20:12 (CPU 4.664,6 s, RAM ~382 MB) tanpa receipt
karena `main()` mengabaikan `--out` dan Sieve B memanggil `sympy.factorint`
untuk setiap bilangan 3..N. Run itu **tidak certifiable** dan tidak menjadi
bagian dari klaim apa pun.

**Tidak mengubah:** `A-2026-0032` (C=100.000), P0/P1/P2, registry yang ada,
`shp_asymmetric_wager`, dan `shp_bridge`.

## 1. Maksud dan batas

Q3 v2 memperbaiki pipeline sensus abc agar:

1. **Receipt benar-benar ditulis** ke path `--out` secara atomik.
2. **Progress terlihat** per fase dan per chunk, tidak menggantung tanpa log.
3. **Sieve B tidak lagi O(N) factorint** untuk membangun daftar bilangan halus.
4. **Run panjang bisa dipecah** menjadi chunk dengan checkpoint/resume, agar
   laptop tidak dipaksa bekerja monolitik berjam-jam.
5. **Validasi bertahap:** C=10^5 (gate), C=10^6 (validasi), C=10^7 (full).

Paket ini **bukan**:

- Pembuktian konjektur abc; hanya sensus finit hingga C yang dikunci.
- Klaim asimtotik, RH, GRH, faktorisasi, RSA/ECC, Anderson, atau fisika.
- Klaim bahwa q dihitung dengan interval arithmetic rigorous. `q` memakai
  `math.log` float64; triple yang dilaporkan adalah integer eksak dan
  diverifikasi ulang. Batas ini harus ditulis di receipt dan laporan.

## 2. Definisi yang dikunci

- **Triple valid:** a, b, c ∈ ℕ, a + b = c, a < b < c, gcd(a,b,c) = 1.
- **Radikal:** rad(n) = produk faktor prima unik dari n.
- **Kualitas:** q(a,b,c) = log(c) / log(rad(a·b·c)).
- **Threshold:** q > 1.4.
- **Bilangan halus:** semua faktor prima ≤ 100.
- **C yang dikunci:** gate 10^5, validasi 10^6, full 10^7.

## 3. Algoritma yang dikunci

### 3.1 Sieve A — linear rad sieve + smooth numbers

- `_rad_sieve(N)`: sieve linear untuk rad(n), seperti implementasi C=100.000.
- `_generate_smooth_numbers(N, 100)`: enumerasi rekursif bilangan 100-halus.
- Loop c dan a seperti implementasi C=100.000, dengan micro-optimasi yang
  **tidak mengubah matematika**:
  - binding lokal untuk `rad`, `smooth`, `gcd`, `log`;
  - cek produk `ra*rb*rc >= c` sebelum `gcd` bila aman;
  - hindari `gcd` berulang untuk pasangan yang sama.
- Tidak memakai `numpy`, `scipy`, atau `sympy`.

### 3.2 Sieve B — segmented rad sieve + heap smooth + sympy re-check

- Bangun `rad_b[1..N]` dengan **segmented sieve** yang tidak memakai
  `_rad_sieve` milik A.
- Bangun daftar bilangan 100-halus dengan **min-heap** (bukan fungsi rekursif
  A).
- Hitung kandidat dengan `rad_b` dan koreksi gcd; **tidak** memanggil
  `factorint` untuk setiap bilangan 3..N.
- Untuk setiap triple final dengan q > 1.4, verifikasi ulang `rad(a·b·c)`
  dengan `sympy.factorint`. Ini menjaga pemeriksaan independen pada hasil,
  bukan pada seluruh ruang.
- Tidak mengimpor fungsi internal A.

### 3.3 Chunking dan checkpoint

- Kedua sieve memakai daftar c yang sama (bilangan 100-halus terurut).
- `--max-seconds` (default 900) menghentikan run setelah batas waktu dan
  menulis checkpoint.
- Checkpoint berisi: `schema`, `N`, `sieve`, `next_index`, `count`,
  `max_gap`, `last_a`, `pairs`, `prereg_sha256lf`.
- `--resume <checkpoint>` melanjutkan dari `next_index`; hasil akhir harus
  identik dengan run bersih.
- Receipt hanya ditulis setelah kedua sieve mencapai akhir.

## 4. Konfigurasi yang dikunci

| Parameter | Nilai |
|---|---|
| N_gate | 100.000 |
| N_validate | 1.000.000 |
| N_full | 10.000.000 |
| Threshold | 1.4 |
| max_prime | 100 |
| max_seconds per chunk | 900 (15 menit) |
| segment_size | 1.048.576 |

Tidak ada parameter yang diubah setelah hasil terlihat, kecuali amendment
bertanggal yang dicatat sebelum perubahan.

## 5. Receipt dan determinisme

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

- `canonical_sha256` dihitung dari payload tanpa `runtime_a`, `runtime_b`, dan
  `canonical_sha256` itu sendiri, dengan `json.dumps(sort_keys=True,
  separators=(",", ":"))`.
- Dua run C=10^5 harus menghasilkan `canonical_sha256` identik.
- Receipt ditulis ke `--out` melalui file `.tmp` lalu `os.replace`.

## 6. Kriteria penerimaan (C1–C7)

- **C1 — Gate C=10^5:** `count=6`, `max_gap=6825`, `pairs_a == pairs_b`, dan
  sama dengan `A-2026-0032`.
- **C2 — Validasi C=10^6:** kedua sieve sepakat pada count, max_gap, dan pairs;
  receipt ditulis.
- **C3 — Full C=10^7:** kedua sieve sepakat; receipt ditulis; progress log
  lengkap.
- **C4 — Determinisme:** `canonical_sha256` C=10^5 identik pada dua run;
  resume dari checkpoint C=10^6 menghasilkan receipt yang sama dengan run
  bersih.
- **C5 — Receipt/progress:** file `--out` ada; progress log non-kosong; tidak
  ada placeholder hash.
- **C6 — Independensi:** B tidak mengimpor fungsi internal A; `factorint`
  hanya dipakai untuk verifikasi final.
- **C7 — Kebersihan:** tidak ada `numpy`/`scipy` di core; batas float64 `q`
  ditulis eksplisit di receipt dan laporan.

## 7. Verdict

- **ALL PASS:** C1–C7 terpenuhi.
- **FAILED:** salah satu kriteria gagal.
- **INCONCLUSIVE:** OOM, tool error, atau hash mismatch.

Registry baru hanya diusulkan setelah `ALL PASS`; ID tidak dikunci di berkas
ini. `A-2026-0032` tetap menjadi sertifikat C=100.000 dan tidak diubah.

## 8. Falsifier

- Gate C=10^5 tidak mereproduksi 6/6825.
- `pairs_a != pairs_b` pada C yang dikunci.
- Receipt tidak ditulis atau `canonical_sha256` berbeda pada dua run.
- Resume menghasilkan hasil berbeda dari run bersih.
- B mengimpor kode internal A atau memakai `factorint` untuk seluruh rentang.
- Memori melebihi batas sistem (OOM).

## 9. Artefak dan urutan eksekusi

1. Bekukan dan hash berkas pra-registrasi ini.
2. Commit dan push pra-registrasi **sebelum** commit implementasi.
3. Implementasi `msaf/abc_census.py` dan guard
   `msaf/tests/test_abc_census.py`.
4. Jalankan gate C=10^5; perbaiki bila gagal.
5. Jalankan validasi C=10^6; simpan receipt.
6. Jalankan full C=10^7 secara chunked; simpan receipt dan progress log.
7. Tulis `reports/ABC_CENSUS_2026-10-27.md` dengan angka verbatim.
8. Registry hanya setelah verdict `ALL PASS` dan keputusan pemilik.

## 10. Batas eksplisit

- Hanya C = 10^7 untuk kampanye penuh; C=10^5 dan C=10^6 adalah gate.
- Threshold q > 1.4; tidak ada threshold lain.
- Tidak ada klaim konjektur abc terbukti/tidak terbukti.
- Tidak ada klaim asimtotik.
- Tidak ada klaim RH, GRH, faktorisasi, RSA/ECC, Anderson, atau fisika.
- `q` memakai float64 `math.log`; ini batas yang diketahui, bukan interval
  arithmetic rigorous.
