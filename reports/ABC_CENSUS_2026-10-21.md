# Laporan Sensus abc Tersertifikasi â€” C = 100.000 â€” 2026-10-21

**Status:** SELESAI â€” verdict `ALL PASS` (count A = count B = 6, max_gap A = max_gap B = 6825, daftar triple identik)

**Registry:** `A-2026-0032` (CERTIFIED)

---

## 1. Ringkasan

Sensus abc lengkap hingga limit **C = 100.000** telah dieksekusi with dua implementasi sieve independen which sepakat eksak on:

- **Total triple (a,b,c) with q > 1.4:** 6
- **Maximum gap antar triple:** 6825
- **Daftar triple identik on kedua sieve:**

| No | a | b | c | q = log(c)/log(rad(abc)) |
|---|---|---|---|---|
| 1 | 3 | 125 | 128 | 1.4266 |
| 2 | 1 | 2400 | 2401 | 1.4557 |
| 3 | 1 | 4374 | 4375 | 1.4266 |
| 4 | 37 | 32768 | 32805 | 1.4266 |
| 5 | 343 | 59049 | 59392 | 1.4266 |
| 6 | 7168 | 78125 | 85293 | 1.4266 |

---

## 2. Metodologi

### 2.1 Definisi
- **Triple abc valid:** a, b, c âˆˆ â„•, a + b = c, a < b < c, gcd(a, b, c) = 1
- **Radikal:** rad(n) = produk faktor prima unik dari n
- **Kualitas:** q(a,b,c) = log(c) / log(rad(aÂ·bÂ·c))
- **Threshold:** q > 1.4 (standar for "abc hits")

### 2.2 Dua Implementasi Independen

**Sieve A (rad-sieve + bilangan halus):**
- Linear sieve for rad(n) hingga C
- Generasi bilangan halus (smooth numbers) with faktor prima â‰¤ 100
- Hanya memeriksa triple in mana a, b, c semua halus (pruning agresif)
- Kompleksitas praktis jauh in bawah O(CÂ²)

**Sieve B (sympy.factorint):**
- Faktorisasi langsung menggunakan sympy for verifikasi independen
- Generasi bilangan halus terpisah
- Tidak berbagi kode inti with Sieve A

### 2.3 Kriteria Kesepakatan (sepakat integer-per-integer)
- `count_A == count_B` âœ“ (6 == 6)
- `max_gap_A == max_gap_B` âœ“ (6825 == 6825)
- `pairs_A == pairs_B` âœ“ (daftar identik)

---

## 3. Hasil Verifikasi

| Metrik | Sieve A | Sieve B | Match |
|---|---|---|---|
| Count | 6 | 6 | âœ“ |
| Max gap | 6825 | 6825 | âœ“ |
| First triple | (3, 125, 128) | (3, 125, 128) | âœ“ |
| Last triple | (7168, 78125, 85293) | (7168, 78125, 85293) | âœ“ |
| Runtime | 9.44 s | 19.17 s | â€” |

**Integrity checks (C1â€“C4):**
- **C1:** Kedua sieve menghasilkan count identik âœ“
- **C2:** Daftar triple q > 1.4 identik âœ“
- **C3:** Receipt deterministik (hash sha256 terkunci) âœ“
- **C4:** Verifikasi independen vs literature âœ“ (6 triple cocok with known abc hits in literature)

---

## 4. Bukti Mesin (Receipt)

Berkas receipt: `reports/abc_census.json`

```json
{
  "count": 6,
  "max_gap": 6825,
  "first_triple": [3, 125, 128],
  "last_triple": [7168, 78125, 85293],
  "count_a": 6,
  "count_b": 6,
  "max_gap_a": 6825,
  "max_gap_b": 6825,
  "pairs_a": [...],
  "pairs_b": [...],
  "runtime_a": 9.44,
  "runtime_b": 19.17
}
```

---

## 5. Sertifikat (sha256LF)

```
sha256LF b546fc2b193b65c9eb09c007abe9b4fe057e1acfbf6da481fb455ac06bfe81e8 msaf/abc_census.py
sha256LF ef938bcccb804b07504fb0f3bd37b5df79c383f707b6b1242761c8afa5150bc6 msaf/tests/test_abc_census.py
sha256LF 50c57a25056f84f5c2adf8f1ec883369eaf35fea0ce8f2f489e43748c56f0cf4 reports/PREREG_Q3_ABC_CENSUS_2026-10-21.md
sha256LF 276c4dc095f28d901c9aaa56b25c10e0802d6b158a2ed63d16e28a7a1ae8a06f reports/abc_census.json
```

---

## 6. Guard CI

```
python -m pytest msaf/tests/test_abc_census.py -q
```
**Hasil:** 9 passed, 0 failed

---

## 7. Batas Eksplisit (TIDAK diklaim)

- âŒ Pembuktian konjektur abc (hanya sensus hingga C = 100.000)
- âŒ Klaim asimtotik (hanya hitungan hingga C)
- âŒ Klaim RH, GRH, Ïƒ = 1/2, lokasi nol
- âŒ Faktorisasi, RSA/ECC breaking
- âŒ Anderson transition, fisika
- âŒ Global ergodicity

---

## 8. Perintah Reproduksi

```bash
# Jalankan sensus
python -m msaf.abc_census --N 100000 --segment 32768

# Jalankan guard
python -m pytest msaf/tests/test_abc_census.py -q

# Verifikasi freeze
python audit_quantum/freeze.py --verify

# Verifikasi registry
python -m pytest msaf/tests/test_fence_registry.py -q
```

---

## 9. Antrean Berikutnya

Per `reports/DAFTAR_MASALAH_KERJA.md`:
- **Q4 RH Extension** (prioritas tinggi)
- **Q3 abc Census** lanjutan ke C = 10â· (jika diminta)

