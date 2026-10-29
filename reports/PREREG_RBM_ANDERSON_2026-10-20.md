# Pra-registrasi: benchmark RBM Anderson for estimator S1/S2 â€” 2026-10-20

**Status:** scope DIKUNCI for paket ini; implementasi and eksekusi **belum**
dimulai. Eksekusi menunggu commit pra-registrasi ini, lalu dijalankan with
konfigurasi which tertulis in bawah.

**Berkas target:** `msaf/rbm_anderson.py` (baru), guard
`msaf/tests/test_rbm_anderson.py` (baru), report
`reports/RBM_ANDERSON_2026-10-20.md`, receipt
`reports/rbm_anderson_2026-10-20.json`.

**Dependensi:** Python 3.14, `numpy`, `scipy==1.18.0` (for `ndtr`),
`python-flint==0.9.0` (for spot-check interval `arb_mat`).

**Registry which direncanakan:** `A-2026-0023`, hanya bila verdict inti
minimal `PARTIAL` and integritas PASS.

**Tidak mengubah:** V1â€“V6 (`A-2026-0015`â€“`A-2026-0021`), `A-2026-0022`,
`ci.yml` (`A-2026-0016`), workflow spec, `lean/lakefile.toml`, freeze pins,
and seluruh report/artefak beku.

## 1. Maksud and limit

Blueprint item 4 meminta uji diagnostik estimator **S1 (mean adjacent gap
ratio)** and **S2 (binned pair correlation)** on random banded Hermitian
matrices (RBM), with fase terlokalisasi menuju fase delokalisasi. Paket ini
menguji apakah estimator tersebut (a) terkalibrasi on null model Poisson
and GUE, and (b) memisahkan fase RBM on satu dimensi tetap.

Paket ini **bukan**:

- klaim transisi Anderson fisik, klaim thermodynamic limit, or klaim
  universalitas;
- algoritma faktorisasi, klaim RSA/ECC, or klaim kriptografi;
- klaim RH, lokasi nol, `Ïƒ = 1/2`, or fisika apa pun in luar benchmark
  finite;
- sertifikasi interval for seluruh statistik. Matriks inti exact-rational
  and ada spot-check Arb; estimator S1/S2 memakai float64 on lapisan
  statistik and diberi label `SIMULATED`/diagnostik.

## 2. Konfigurasi which dikunci

| Parameter | Nilai |
|---|---:|
| Dimensi `D = 2N+1` | 201 (`N=100`) |
| Bandwidth `b` | 1, 10, 120 |
| Jumlah matriks RBM per `b` | 64 |
| Null reference (GUE/Poisson) | 2000 spectra masing-masing |
| Null calibration (GUE/Poisson) | 64 spectra masing-masing |
| Bootstrap replicates | 2000 |
| `Ïƒ_u` | 0.3, 0.5, 1.0 |
| Chart | `T` (primary, `ln` shifted) and `L` (secondary, shifted linear) |
| `Ïƒ_e` | 0.5 |
| Grid `u` | 20 bin, `u âˆˆ {0.25, 0.75, ..., 9.75}` |
| Fine histogram R2 | lebar 0.02 on `[0, 10]` |

**Master seed:** `2430500035454946990` (`0x21badee7a7ddceae`), created
sekali with `secrets.randbits(64)` sebelum pra-registrasi ini ditulis.
Seed ini bukan seed standar kecil; ia direkam agar result deterministik and
dapat direproduksi. Tidak ada result RBM with seed ini which dibaca sebelum
pra-registrasi.

Seed per stream diturunkan secara deterministik:

```text
seed(label) = int.from_bytes(sha256(f"{MASTER_SEED}:{label}").digest()[:8], "big")
```

Label which dikunci: `rbm:b:i`, `gue:ref:i`, `pois:ref:i`, `gue:cal:i`,
`pois:cal:i`, and label bootstrap which tertulis in kode.

## 3. Ensemble matriks

Untuk setiap label, ambil `re` and `im` sebagai integer 16-bit dari
`numpy.random.Generator(PCG64(seed))` on rentang `[-32768, 32767]`.
Entri matriks adalah rasional exact:

```text
A_ij = (re_ij + i im_ij) / 32768,   |i-j| <= b
A_ij = 0,                           |i-j| > b
A = (A + Aâ€ )/2
```

Diagonal menjadi real; matriks Hermitian. Karena penyebutnya pangkat dua,
entri float64 which dipakai estimator **tepat** sama with rasional exact
tersebut. Untuk null GUE, dipakai `b = D-1` (full band). Untuk Poisson,
level created dari eksponensial i.i.d. with rate 1 lalu dijumlahkan
(cumulative spacings); no ada matriks.

Chart terhadap eigenvalue real `Î»` which already diurutkan:

```text
s = 1 - min(Î»)
x_L = Î» + s            (min = 1)
x_T = ln(Î» + s)        (min = 0)
```

Chart `L` and `T` diterapkan sama on RBM, GUE, and Poisson. Untuk Poisson,
`Î»` adalah cumulative exponential levels.

## 4. Estimator S1

Untuk level terurut `x_1 < ... < x_D`:

```text
s_i = x_{i+1} - x_i
r_i = min(s_i, s_{i+1}) / max(s_i, s_{i+1})
r_bar = mean(r_i)
```

S1 no bergantung on `Ïƒ_u`; for setiap `b` and setiap chart dihitung
mean `r_bar` atas 64 matriks. Null reference/calibration dihitung with
rumus which sama.

## 5. Estimator S2

Untuk level `y` and `Ïƒ_u`:

1. Local mean spacing dari Â±10 tetangga:

```text
h_m = (y_hi(m) - y_lo(m)) / (hi(m) - lo(m))
```

with `lo=max(m-10,0)`, `hi=min(m+10,D-1)`. Jika `h_m = 0`, pakai mean
spacing global.

2. Unfolding:

```text
z_km = (y_k - y_m) / (Ïƒ_u h_m)
x_k  = Î£_m Î¦(z_km)
```

`Î¦` adalah normal CDF (`scipy.special.ndtr`). Kemudian `x` diurutkan and
in-rescale agar mean gap tepat 1:

```text
x â† (x - x_1) * (D-1) / (x_D - x_1)
```

3. Pair-correlation estimator on `u`:

```text
R2_est(u) = (1/D) Î£_{iâ‰ j} Gauss_{Ïƒ_e}(u - (x_i - x_j))
```

Implementasi binned: hitung `|x_i-x_j|` for `i<j`, histogram on fine
grid 0.02, lalu kalikan with kernel Gaussian `Ïƒ_e=0.5` which dievaluasi
on 20 center `u`; faktor `2/D` for pasangan `i<j`. Ini adalah estimator
binned which dipra-registrasi, bukan integral kontinu.

4. Bin which dipakai: semua 20 bin. Untuk `D=201`, expected pair count
`D * R2_GUE(u) * 0.5` on `u=0.25` adalah ~19 (>5), jadi no ada bin which
dibuang. Jika implementasi menemukan bin with expected <5, bin itu
dibuang and dicatat; keputusan no boleh diubah setelah melihat result.

## 6. Null model, kalibrasi, and p-value

Untuk setiap null kind (`gue`, `pois`):

- **reference:** 2000 spectra, dipakai for mean/variance per bin;
- **calibration:** 64 spectra independen, dipakai for menguji kalibrasi;
- **bootstrap:** 2000 resampel mean berukuran 64 dari reference.

S1 p-value dua sisi:

```text
p_null = fraction(|mean_boot - mean_ref| >= |mean_obs - mean_ref|)
```

S2 chi-square diagonal:

```text
mean_ref(bin), var_ref(bin)
chi2_obs = Î£_bin (mean_obs(bin) - mean_ref(bin))^2 / (var_ref(bin)/64)
chi2_boot = Î£_bin (mean_boot(bin) - mean_ref(bin))^2 / (var_ref(bin)/64)
p_GUE  = fraction(chi2_GUE_boot  >= chi2_obs)
p_Pois = fraction(chi2_Pois_boot <= chi2_obs)
```

Korelasi antar-bin no dimodelkan; ini chi-square diagonal which
dipra-registrasi. p-value dicatat sebagai count/N and desimal; count 0
dilaporkan sebagai `0/N` with 95% upper bound, bukan sebagai kepastian
nol.

**Label fase:**

- S1: jarak ke rerata null dalam unit SD reference; label `POISSON` bila
  lebih dekat ke Poisson, `GUE` bila lebih dekat ke GUE.
- S2: chiÂ² ternormalisasi terhadap rerata bootstrap masing-masing null;
  label `POISSON` bila nilai ternormalisasi Poisson lebih kecil, `GUE` bila
  GUE lebih kecil.

## 7. Kriteria verdict

### 7.1 Kalibrasi null (wajib)

- S1: label benar for GUE and Poisson in kedua chart: **4/4**.
- S2: label benar and `p_own >= 0.05` for sekurangnya **10/12** sel
  (2 null Ã— 3 `Ïƒ_u` Ã— 2 chart).
- Jika kalibrasi gagal: `FAILED` for estimator; result RBM tetap dilaporkan
  tetapi no boleh diklaim tervalidasi.

### 7.2 RBM S1

- Monotonik: `r_bar(b=1) < r_bar(b=10) < r_bar(b=120)` for kedua chart,
  with selisih minimum `0.01` antar titik.
- Label ekstrem: `b=1` = `POISSON` and `b=120` = `GUE` for kedua chart.

### 7.3 RBM S2

- `b=1`: label `POISSON` on sekurangnya **5/6** sel.
- `b=120`: label `GUE` on sekurangnya **5/6** sel.
- `b=10` no dipaksa; hasilnya dilaporkan sebagai titik transisi.

### 7.4 Verdict keseluruhan

- `PASS`: kalibrasi null PASS, S1 PASS, S2 PASS, and integritas PASS.
- `PARTIAL`: kalibrasi PASS and integritas PASS, tetapi hanya salah satu
  dari S1/S2 which PASS.
- `INCONCLUSIVE`: kalibrasi PASS, integritas PASS, tetapi S1 and S2 sama-sama
  no memenuhi kriteria; no ada klaim validasi.
- `FAILED`: kalibrasi null gagal or integritas gagal (hash, determinisme,
  spot-check interval).
- `TOOL NOT RUN`: dependensi/API no tersedia; no pernah dinaikkan
  menjadi PASS.

## 8. Integritas and spot-check interval

1. Matriks RBM/GUE dibangun dari integer exact and hash kanonik dicatat.
2. Untuk matriks pertama setiap `b`, bangun `arb_mat` dari `fmpq` exact,
   hitung `eig` on presisi 128 bit, lalu:
   - setiap section imajiner interval harus memuat 0;
   - setiap eigenvalue real interval harus memuat eigenvalue float64 which
     sesuai (toleransi 1e-8);
   - urutan dicocokkan setelah sort berdasarkan midpoint.
3. Spot-check ini hanya for integritas matriks/float; bukan sertifikasi
   interval seluruh statistik.
4. Receipt kanonik deterministik; dua run with seed which sama harus
   menghasilkan payload which sama (kecuali metadata waktu which no
   dimasukkan ke hash).

## 9. Artefak and urutan eksekusi

1. Commit pra-registrasi ini sebelum kode.
2. Implementasi `msaf/rbm_anderson.py` with konfigurasi penuh and mode
   `quick` for guard.
3. Guard `msaf/tests/test_rbm_anderson.py`: uji formula S1/S2, determinisme
   seed, ukuran/band, tamper, receipt, and jalur `quick`; guard no
   menjalankan kampanye penuh.
4. Jalankan kampanye penuh sekali, hasilkan receipt.
5. Tulis report `reports/RBM_ANDERSON_2026-10-20.md` with result verbatim,
   p-values, label, verdict, runtime, hash, and limit.
6. Bila verdict minimal `PARTIAL` and integritas PASS: registry
   `A-2026-0023`, HANDOFF Â§2.0aq, sertifikat sha256LF.
7. Suite penuh, `freeze.py --verify`, push/CI hanya bila diminta.

## 10. Falsifier

Paket FAILED bila:

- matriks no Hermitian/banded sesuai definisi, or hash no cocok;
- spot-check interval gagal;
- null S1/GUE or Poisson no terkalibrasi (label/p-value in luar Â§7.1);
- receipt no deterministik;
- guard no menangkap tamper which diwajibkan;
- `TOOL NOT RUN` dinaikkan menjadi PASS.

Kegagalan S1/S2 on RBM **bukan** pelanggaran integritas; itu result
diagnostik and harus dilaporkan sebagai `PARTIAL`/`INCONCLUSIVE`.

## 11. Batas eksplisit

- Satu dimensi `D=201`; no ada ekstrapolasi thermodynamic limit.
- Tiga bandwidth; bukan kurva fase kontinu.
- Statistik memakai float64 setelah entri exact; hanya spot-check Arb.
- Tidak ada klaim Anderson transition, universalitas RMT, or fisika.
- Tidak ada klaim kriptografi, faktorisasi, RH, or `Ïƒ=1/2`.
- `PASS` adalah validasi estimator on konfigurasi ini, bukan peer review.


