# Addendum pra-registrasi Paket 7 — deviasi trusted base: 4 aksioma stdlib (bukan 3)

**Tanggal:** 2026-10-20
**Mengacu:** `reports/PREREG_PAKET7_2026-10-20.md` §4
**Berkas target:** `formal_bridge/IntegralComparison.v` (scope tidak berubah)

## 1. Temuan

`Print Assumptions integral_comparison_power_finite` menunjukkan **empat**
aksioma stdlib:

- `ClassicalDedekindReals.sig_forall_dec`
- `ClassicalDedekindReals.sig_not_dec`
- `FunctionalExtensionality.functional_extensionality_dep`
- `Classical_Prop.classic`

Tiga yang pertama adalah aksioma yang diperkirakan pra-registrasi §4.
Aksioma keempat, `Classical_Prop.classic`, masuk melalui mesin integral
Riemann stdlib (`Coq.Reals.RiemannInt`), bukan melalui asumsi proyek.
Pemetaan 14 hasil: 3 hasil closed; 4 hasil dengan 2 aksioma; 1 hasil
dengan 1 aksioma; 6 hasil dengan 4 aksioma (rincian di receipt dan
laporan).

## 2. Keputusan

- **Scope tidak berubah**: teorema utama tetap finite core L5 untuk
  `f_k(x) = x^{-(k+1)}`, `k >= 1`; tidak ada pelemahan pernyataan.
- Paket disertifikasi dengan trusted base **tepat empat aksioma stdlib**
  dan **nol aksioma proyek**, dengan deviasi ini dicatat di laporan,
  registry, dan HANDOFF.
- Kriteria "tiga aksioma" di pra-registrasi §4 diganti oleh kriteria
  "jumlah persis dicatat + tidak ada aksioma proyek"; kriteria kedua
  terpenuhi.
- Jika pemilik mensyaratkan literal tiga aksioma, Paket 7 **tidak**
  memenuhi syarat itu. Jalur finite integral Riemann tidak dapat
  menghindari klasisitas stdlib tanpa mengganti mesin integral; itu
  keputusan owner, bukan klaim tersembunyi.

## 3. Batas

Tidak ada perubahan batas: finite core saja; integral tak-hingga,
langkah limit, `f` umum, eksponen real, L3/L4, dan `[J]` tetap di luar
scope. Tidak ada klaim RH/P≠NP/fisika.
