# Pra-registrasi: benchmark RBM Anderson untuk estimator S1/S2 — 2026-10-20

**Status:** scope DIKUNCI untuk paket ini; implementasi dan eksekusi **belum**
dimulai. Eksekusi menunggu commit pra-registrasi ini, lalu dijalankan dengan
konfigurasi yang tertulis di bawah.

**Berkas target:** `msaf/rbm_anderson.py` (baru), guard
`msaf/tests/test_rbm_anderson.py` (baru), laporan
`reports/RBM_ANDERSON_2026-10-20.md`, receipt
`reports/rbm_anderson_2026-10-20.json`.

**Dependensi:** Python 3.14, `numpy`, `scipy==1.18.0` (untuk `ndtr`),
`python-flint==0.9.0` (untuk spot-check interval `arb_mat`).

**Registry yang direncanakan:** `A-2026-0023`, hanya bila verdict inti
minimal `PARTIAL` dan integritas PASS.

**Tidak mengubah:** V1–V6 (`A-2026-0015`–`A-2026-0021`), `A-2026-0022`,
`ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins,
dan seluruh laporan/artefak beku.

## 1. Maksud dan batas

Blueprint item 4 meminta uji diagnostik estimator **S1 (mean adjacent gap
ratio)** dan **S2 (binned pair correlation)** pada random banded Hermitian
matrices (RBM), dengan fase terlokalisasi menuju fase delokalisasi. Paket ini
menguji apakah estimator tersebut (a) terkalibrasi pada null model Poisson
dan GUE, dan (b) memisahkan fase RBM pada satu dimensi tetap.

Paket ini **bukan**:

- klaim transisi Anderson fisik, klaim thermodynamic limit, atau klaim
  universalitas;
- algoritma faktorisasi, klaim RSA/ECC, atau klaim kriptografi;
- klaim RH, lokasi nol, `σ = 1/2`, atau fisika apa pun di luar benchmark
  finite;
- sertifikasi interval untuk seluruh statistik. Matriks inti exact-rational
  dan ada spot-check Arb; estimator S1/S2 memakai float64 pada lapisan
  statistik dan diberi label `SIMULATED`/diagnostik.

## 2. Konfigurasi yang dikunci

| Parameter | Nilai |
|---|---:|
| Dimensi `D = 2N+1` | 201 (`N=100`) |
| Bandwidth `b` | 1, 10, 120 |
| Jumlah matriks RBM per `b` | 64 |
| Null reference (GUE/Poisson) | 2000 spectra masing-masing |
| Null calibration (GUE/Poisson) | 64 spectra masing-masing |
| Bootstrap replicates | 2000 |
| `σ_u` | 0.3, 0.5, 1.0 |
| Chart | `T` (primary, `ln` shifted) dan `L` (secondary, shifted linear) |
| `σ_e` | 0.5 |
| Grid `u` | 20 bin, `u ∈ {0.25, 0.75, ..., 9.75}` |
| Fine histogram R2 | lebar 0.02 pada `[0, 10]` |

**Master seed:** `2430500035454946990` (`0x21badee7a7ddceae`), dibuat
sekali dengan `secrets.randbits(64)` sebelum pra-registrasi ini ditulis.
Seed ini bukan seed standar kecil; ia direkam agar hasil deterministik dan
dapat direproduksi. Tidak ada hasil RBM dengan seed ini yang dibaca sebelum
pra-registrasi.

Seed per stream diturunkan secara deterministik:

```text
seed(label) = int.from_bytes(sha256(f"{MASTER_SEED}:{label}").digest()[:8], "big")
```

Label yang dikunci: `rbm:b:i`, `gue:ref:i`, `pois:ref:i`, `gue:cal:i`,
`pois:cal:i`, dan label bootstrap yang tertulis di kode.

## 3. Ensemble matriks

Untuk setiap label, ambil `re` dan `im` sebagai integer 16-bit dari
`numpy.random.Generator(PCG64(seed))` pada rentang `[-32768, 32767]`.
Entri matriks adalah rasional exact:

```text
A_ij = (re_ij + i im_ij) / 32768,   |i-j| <= b
A_ij = 0,                           |i-j| > b
A = (A + A†)/2
```

Diagonal menjadi real; matriks Hermitian. Karena penyebutnya pangkat dua,
entri float64 yang dipakai estimator **tepat** sama dengan rasional exact
tersebut. Untuk null GUE, dipakai `b = D-1` (full band). Untuk Poisson,
level dibuat dari eksponensial i.i.d. dengan rate 1 lalu dijumlahkan
(cumulative spacings); tidak ada matriks.

Chart terhadap eigenvalue real `λ` yang sudah diurutkan:

```text
s = 1 - min(λ)
x_L = λ + s            (min = 1)
x_T = ln(λ + s)        (min = 0)
```

Chart `L` dan `T` diterapkan sama pada RBM, GUE, dan Poisson. Untuk Poisson,
`λ` adalah cumulative exponential levels.

## 4. Estimator S1

Untuk level terurut `x_1 < ... < x_D`:

```text
s_i = x_{i+1} - x_i
r_i = min(s_i, s_{i+1}) / max(s_i, s_{i+1})
r_bar = mean(r_i)
```

S1 tidak bergantung pada `σ_u`; untuk setiap `b` dan setiap chart dihitung
mean `r_bar` atas 64 matriks. Null reference/calibration dihitung dengan
rumus yang sama.

## 5. Estimator S2

Untuk level `y` dan `σ_u`:

1. Local mean spacing dari ±10 tetangga:

```text
h_m = (y_hi(m) - y_lo(m)) / (hi(m) - lo(m))
```

dengan `lo=max(m-10,0)`, `hi=min(m+10,D-1)`. Jika `h_m = 0`, pakai mean
spacing global.

2. Unfolding:

```text
z_km = (y_k - y_m) / (σ_u h_m)
x_k  = Σ_m Φ(z_km)
```

`Φ` adalah normal CDF (`scipy.special.ndtr`). Kemudian `x` diurutkan dan
di-rescale agar mean gap tepat 1:

```text
x ← (x - x_1) * (D-1) / (x_D - x_1)
```

3. Pair-correlation estimator pada `u`:

```text
R2_est(u) = (1/D) Σ_{i≠j} Gauss_{σ_e}(u - (x_i - x_j))
```

Implementasi binned: hitung `|x_i-x_j|` untuk `i<j`, histogram pada fine
grid 0.02, lalu kalikan dengan kernel Gaussian `σ_e=0.5` yang dievaluasi
pada 20 center `u`; faktor `2/D` untuk pasangan `i<j`. Ini adalah estimator
binned yang dipra-registrasi, bukan integral kontinu.

4. Bin yang dipakai: semua 20 bin. Untuk `D=201`, expected pair count
`D * R2_GUE(u) * 0.5` pada `u=0.25` adalah ~19 (>5), jadi tidak ada bin yang
dibuang. Jika implementasi menemukan bin dengan expected <5, bin itu
dibuang dan dicatat; keputusan tidak boleh diubah setelah melihat hasil.

## 6. Null model, kalibrasi, dan p-value

Untuk setiap null kind (`gue`, `pois`):

- **reference:** 2000 spectra, dipakai untuk mean/variance per bin;
- **calibration:** 64 spectra independen, dipakai untuk menguji kalibrasi;
- **bootstrap:** 2000 resampel mean berukuran 64 dari reference.

S1 p-value dua sisi:

```text
p_null = fraction(|mean_boot - mean_ref| >= |mean_obs - mean_ref|)
```

S2 chi-square diagonal:

```text
mean_ref(bin), var_ref(bin)
chi2_obs = Σ_bin (mean_obs(bin) - mean_ref(bin))^2 / (var_ref(bin)/64)
chi2_boot = Σ_bin (mean_boot(bin) - mean_ref(bin))^2 / (var_ref(bin)/64)
p_GUE  = fraction(chi2_GUE_boot  >= chi2_obs)
p_Pois = fraction(chi2_Pois_boot <= chi2_obs)
```

Korelasi antar-bin tidak dimodelkan; ini chi-square diagonal yang
dipra-registrasi. p-value dicatat sebagai count/N dan desimal; count 0
dilaporkan sebagai `0/N` dengan 95% upper bound, bukan sebagai kepastian
nol.

**Label fase:**

- S1: jarak ke rerata null dalam unit SD reference; label `POISSON` bila
  lebih dekat ke Poisson, `GUE` bila lebih dekat ke GUE.
- S2: chi² ternormalisasi terhadap rerata bootstrap masing-masing null;
  label `POISSON` bila nilai ternormalisasi Poisson lebih kecil, `GUE` bila
  GUE lebih kecil.

## 7. Kriteria verdict

### 7.1 Kalibrasi null (wajib)

- S1: label benar untuk GUE dan Poisson di kedua chart: **4/4**.
- S2: label benar dan `p_own >= 0.05` untuk sekurangnya **10/12** sel
  (2 null × 3 `σ_u` × 2 chart).
- Jika kalibrasi gagal: `FAILED` untuk estimator; hasil RBM tetap dilaporkan
  tetapi tidak boleh diklaim tervalidasi.

### 7.2 RBM S1

- Monotonik: `r_bar(b=1) < r_bar(b=10) < r_bar(b=120)` untuk kedua chart,
  dengan selisih minimum `0.01` antar titik.
- Label ekstrem: `b=1` = `POISSON` dan `b=120` = `GUE` untuk kedua chart.

### 7.3 RBM S2

- `b=1`: label `POISSON` pada sekurangnya **5/6** sel.
- `b=120`: label `GUE` pada sekurangnya **5/6** sel.
- `b=10` tidak dipaksa; hasilnya dilaporkan sebagai titik transisi.

### 7.4 Verdict keseluruhan

- `PASS`: kalibrasi null PASS, S1 PASS, S2 PASS, dan integritas PASS.
- `PARTIAL`: kalibrasi PASS dan integritas PASS, tetapi hanya salah satu
  dari S1/S2 yang PASS.
- `INCONCLUSIVE`: kalibrasi PASS, integritas PASS, tetapi S1 dan S2 sama-sama
  tidak memenuhi kriteria; tidak ada klaim validasi.
- `FAILED`: kalibrasi null gagal atau integritas gagal (hash, determinisme,
  spot-check interval).
- `TOOL NOT RUN`: dependensi/API tidak tersedia; tidak pernah dinaikkan
  menjadi PASS.

## 8. Integritas dan spot-check interval

1. Matriks RBM/GUE dibangun dari integer exact dan hash kanonik dicatat.
2. Untuk matriks pertama setiap `b`, bangun `arb_mat` dari `fmpq` exact,
   hitung `eig` pada presisi 128 bit, lalu:
   - setiap bagian imajiner interval harus memuat 0;
   - setiap eigenvalue real interval harus memuat eigenvalue float64 yang
     sesuai (toleransi 1e-8);
   - urutan dicocokkan setelah sort berdasarkan midpoint.
3. Spot-check ini hanya untuk integritas matriks/float; bukan sertifikasi
   interval seluruh statistik.
4. Receipt kanonik deterministik; dua run dengan seed yang sama harus
   menghasilkan payload yang sama (kecuali metadata waktu yang tidak
   dimasukkan ke hash).

## 9. Artefak dan urutan eksekusi

1. Commit pra-registrasi ini sebelum kode.
2. Implementasi `msaf/rbm_anderson.py` dengan konfigurasi penuh dan mode
   `quick` untuk guard.
3. Guard `msaf/tests/test_rbm_anderson.py`: uji formula S1/S2, determinisme
   seed, ukuran/band, tamper, receipt, dan jalur `quick`; guard tidak
   menjalankan kampanye penuh.
4. Jalankan kampanye penuh sekali, hasilkan receipt.
5. Tulis laporan `reports/RBM_ANDERSON_2026-10-20.md` dengan hasil verbatim,
   p-values, label, verdict, runtime, hash, dan batas.
6. Bila verdict minimal `PARTIAL` dan integritas PASS: registry
   `A-2026-0023`, HANDOFF §2.0aq, sertifikat sha256LF.
7. Suite penuh, `freeze.py --verify`, push/CI hanya bila diminta.

## 10. Falsifier

Paket FAILED bila:

- matriks tidak Hermitian/banded sesuai definisi, atau hash tidak cocok;
- spot-check interval gagal;
- null S1/GUE atau Poisson tidak terkalibrasi (label/p-value di luar §7.1);
- receipt tidak deterministik;
- guard tidak menangkap tamper yang diwajibkan;
- `TOOL NOT RUN` dinaikkan menjadi PASS.

Kegagalan S1/S2 pada RBM **bukan** pelanggaran integritas; itu hasil
diagnostik dan harus dilaporkan sebagai `PARTIAL`/`INCONCLUSIVE`.

## 11. Batas eksplisit

- Satu dimensi `D=201`; tidak ada ekstrapolasi thermodynamic limit.
- Tiga bandwidth; bukan kurva fase kontinu.
- Statistik memakai float64 setelah entri exact; hanya spot-check Arb.
- Tidak ada klaim Anderson transition, universalitas RMT, atau fisika.
- Tidak ada klaim kriptografi, faktorisasi, RH, atau `σ=1/2`.
- `PASS` adalah validasi estimator pada konfigurasi ini, bukan peer review.
