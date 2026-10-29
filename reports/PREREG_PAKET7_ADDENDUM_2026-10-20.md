# Addendum pra-registrasi Paket 7 â€” deviasi trusted base: 4 aksioma stdlib (bukan 3)

**Tanggal:** 2026-10-20
**Mengacu:** `reports/PREREG_PAKET7_2026-10-20.md` Â§4
**Berkas target:** `formal_bridge/IntegralComparison.v` (scope no berubah)

## 1. Temuan

`Print Assumptions integral_comparison_power_finite` menunjukkan **empat**
aksioma stdlib:

- `ClassicalDedekindReals.sig_forall_dec`
- `ClassicalDedekindReals.sig_not_dec`
- `FunctionalExtensionality.functional_extensionality_dep`
- `Classical_Prop.classic`

Tiga which pertama adalah aksioma which diperkirakan pra-registrasi Â§4.
Aksioma keempat, `Classical_Prop.classic`, masuk melalui mesin integral
Riemann stdlib (`Coq.Reals.RiemannInt`), bukan melalui asumsi proyek.
Pemetaan 14 result: 3 result closed; 4 result with 2 aksioma; 1 result
with 1 aksioma; 6 result with 4 aksioma (rincian in receipt and
report).

## 2. Keputusan

- **Scope no berubah**: teorema utama tetap finite core L5 for
  `f_k(x) = x^{-(k+1)}`, `k >= 1`; no ada pelemahan pernyataan.
- Paket disertifikasi with trusted base **tepat empat aksioma stdlib**
  and **nol aksioma proyek**, with deviasi ini dicatat in report,
  registry, and HANDOFF.
- Kriteria "tiga aksioma" in pra-registrasi Â§4 diganti oleh kriteria
  "jumlah persis dicatat + no ada aksioma proyek"; kriteria kedua
  terpenuhi.
- Jika pemilik mensyaratkan literal tiga aksioma, Paket 7 **no**
  memenuhi syarat itu. Jalur finite integral Riemann no dapat
  menghindari klasisitas stdlib tanpa mengganti mesin integral; itu
  keputusan owner, bukan klaim tersembunyi.

## 3. Batas

Tidak ada perubahan limit: finite core saja; integral tak-hingga,
step limit, `f` umum, eksponen real, L3/L4, and `[J]` tetap in luar
scope. Tidak ada klaim RH/Pâ‰ NP/fisika.


