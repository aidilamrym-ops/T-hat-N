# Praâ€‘registrasi: BSD pilot Q1 v2 â€” 2-descent + simbol modular for 5 kurva rank-0 â€” 2026-10-30

**Status:** PREâ€‘REG, locked before implementation.

## 1. Lingkup and Batas
Memverifikasi formula BSD rank 0 tanpa hardcode for 5 kurva pilot:
L(E,1)/Î© = |Ð¨| Â· (âˆ c_p) / |E(Q)_tors|Â²

Tabel parameter terkunci (LMFDB/Cremona):
- **11a1**: Torsion = 5, âˆ c_p = 5, L(E,1)/Î© = 1/5
- **14a1**: Torsion = 6, âˆ c_p = 6, L(E,1)/Î© = 1/6
- **15a1**: Torsion = 8, âˆ c_p = 8, L(E,1)/Î© = 1/8
- **17a1**: Torsion = 4, âˆ c_p = 4, L(E,1)/Î© = 1/4
- **19a1**: Torsion = 3, âˆ c_p = 3, L(E,1)/Î© = 1/3

## 2. Persyaratan Implementsi
- Tanpa float, numpy, or lookup tabel tautologis in jalur hitung.
- Modul target: `msaf/bsd_v2.py`
- Guard: `msaf/tests/test_bsd_v2.py`
- Receipt: `reports/bsd_v2_2026-10-30.json`

sha256LF 4e45fc096dff53854de40ee885717037920d371480c39328a10e8232f2999566 reports/PREREG_Q1_BSD_V2_2026-10-30.md


