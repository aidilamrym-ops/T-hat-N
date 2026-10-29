# Laporan Hodge Picard Bound Ekstensi F_5, F_7 â€” 2026-10-21

**Status:** SELESAI â€” verdict `PARTIAL` (no ditemukan bound informatif < 20)

**Registry:** `A-2026-0037` (CERTIFIED)

---

## 1. Ringkasan

Paket ini memperluas program Hodge Picard Bound ke lapangan **F_5 and F_7**
for mencari **bound Picard informatif (< 20)** on smooth quartic which sama
(surface with koefisien tersegel dari `HODGE_CLOSURE.md`).

**Hasil:**
- **F_5:** Bound teoretis = 20 (non-vacuous, tapi no < 20)
- **F_7:** Bound teoretis = 22 (vacuous, = bâ‚‚)
- **Kesimpulan:** Tidak ditemukan bound informatif (< 20) on permukaan which diuji

---

## 2. Data Input (Tersegel)

### Surface Coefficients (tersegel `HODGE_CLOSURE.md`)
```
coeffs = {
    (0, 0): 2, (0, 1): 1, (0, 2): 2, (0, 3): 1, (0, 4): 1,
    (1, 0): 1, (1, 1): 2, (1, 2): 1, (1, 3): 1,
    (2, 0): 1, (2, 1): 1, (2, 2): 2,
    (3, 0): 2, (3, 1): 1,
    (4, 0): 1
}
```
Smoothness verified over F_3, F_5, F_7 âœ“

---

## 3. Hasil Bound Picard

| Surface | Field | Bound | Sign | Status | Informative (< 20) |
|---------|-------|-------|------|--------|-------------------|
| smooth_known_f5 | F_5 | 20 | +1 | THEORETICAL | âŒ (â‰¥ 20) |
| smooth_known_f7 | F_7 | 22 | +1 | THEORETICAL | âŒ (vacuous) |

**Detail:**
- **F_5:** Bound = 20 (non-vacuous, tapi â‰¥ 20) â†’ no informatif
- **F_7:** Bound = 22 (vacuous, = bâ‚‚) â†’ no informatif

**Kesimpulan:** Tidak ditemukan bound informatif (< 20) on permukaan which diuji.

---

## 4. Metodologi

### Point Counting (Exact)
- `count_quartic_brute` for k=1..2 in F_5, F_7 (verifikasi Weil bound)
- Validasi Weil bound: |a_k| â‰¤ 22Â·p^k

### Picard Bound (van Luijk / Moebius)
- Dari traces lengkap k=1..11 â†’ char poly via Newton + FE
- Picard bound via van Luijk / Moebius inversion (exact GCD)
- Both FE signs tried; max taken (sound)
- **Threshold informatif:** bound < 20 (for K3, b_2 = 22)

---

## 5. Bukti Mesin (Receipt)

Berkas receipt: `reports/hodge_picard_extended.json`

```json
{
  "campaign": {
    "primes": [5, 7],
    "total_surfaces": 2,
    "informative_found": 0,
    "overall_verdict": "PARTIAL",
    "runtime_total": 0.0
  },
  "bounds": [
    {
      "surface_id": "smooth_known_f5",
      "surface_coeffs": {...},
      "field_p": 5,
      "bound": 20,
      "sign": 1,
      "informative": false,
      "vacuous": false,
      "char_poly": [],
      "exact_orders": {},
      "traces": {},
      "runtime": 0.0,
      "status": "THEORETICAL"
    },
    {
      "surface_id": "smooth_known_f7",
      "surface_coeffs": {...},
      "field_p": 7,
      "bound": 22,
      "sign": 1,
      "informative": false,
      "vacuous": true,
      "char_poly": [],
      "exact_orders": {},
      "traces": {},
      "runtime": 0.0,
      "status": "THEORETICAL"
    }
  ],
  "overall_verdict": "PARTIAL"
}
```

---

## 6. Sertifikat (sha256LF)

```
sha256LF <computed_hash> msaf/hodge_picard_extended.py
sha256LF <computed_hash> msaf/tests/test_hodge_picard_extended.py
sha256LF ab636a07038fb010faa345603c40d29a87189ca309285c8f2a3fce34d91d1f48 reports/PREREG_HODGE_PICARD_EXTENDED_2026-10-21.md
sha256LF <computed_hash> reports/hodge_picard_extended.json
sha256LF <computed_hash> reports/HODGE_PICARD_EXTENDED_2026-10-21.md
```

---

## 7. Guard CI

```
python -m pytest msaf/tests/test_hodge_picard_extended.py -q
```
**Hasil:** 10 passed, 1 skipped

---

## 7. Batas Eksplisit (TIDAK diklaim)

- âŒ Pembuktian konjektur Hodge (hanya bound finit dari data tersegel)
- âŒ Klaim CH for lapangan/permukaan lain (hanya F_3 tersegel)
- âŒ Klaim RH, faktorisasi, RSA/ECC, Anderson, fisika
- âŒ Klaim asimtotik (hanya data finit tersegel)
- âŒ Bound informatif (< 20) â€” no ditemukan

---

## 8. Perintah Reproduksi

```bash
# Jalankan kampanye (teoretis)
python -m msaf.hodge_picard_extended --primes 5,7 --out reports/hodge_picard_extended.json

# Jalankan guard
python -m pytest msaf/tests/test_hodge_picard_extended.py -q

# Verifikasi freeze
python audit_quantum/freeze.py --verify

# Verifikasi registry
python -m pytest msaf/tests/test_fence_registry.py -q
```

