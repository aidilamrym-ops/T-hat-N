# Pra-registrasi Rekonstruksi Matriks Tau (build_arb_tau) — 2026-10-30

**Status:** Pra-registrasi terpisah — **wajib di-commit dan dipush sebelum** satu baris pun kode implementasi ditulis.

**Otoritas:** `CURRENT_AUTHORITY.md` > `AGENTS.md` > `reports/DECISION_LOG.md` > `reports/FENCE_REGISTRY.md`. Berkas ini di bawah keempatnya.

**Tidak mengubah:** Semua sertifikasi yang ada (`T-2026-0068`, `T-2026-0069`, `A-2026-0054`, `F-2026-0001`, `F-2026-0002`, dsb.), status baseline P0/P1/P2, dan artefak ber-`sha256LF`.

---

## 1. Latar Belakang & Kebutuhan

Investigasi `reports/NON_CIRCULANT_STRUCTURE_2026-10-30.md` mengonfirmasi: **tidak ada matriks tersedia** di repositori untuk uji struktur Toeplitz/Hankel/SVD. Artefak yang ada hanya spektrum eigenvalue dari pipeline `source_arb_ldlt_certify.build_arb_tau(c=100,N=100/150,prec=6000)` yang **tidak ada** di repo ini.

Kampanye ini membangun ulang fungsi `build_arb_tau` secara lokal untuk menghasilkan **file matriks biner tersertifikasi hash** guna memungkinkan analisis struktur matriks lanjutan.

---

## 2. Cetak Biru Formulasi Matriks (Matematika Terkunci)

### 2.1 Definisi Blok Guinand-Weil $\tau$

Sesuai T-hat-N README Section 6.1 (versi terkunci di commit `e52c41d`):

$$
\tau = W_{02} - W_R - W_p
$$

di mana:

| Komponen | Dimensi | Definisi Matematis | Sumber |
|---|---|---|---|
| $W_{02}$ | $n \times n$ | Matriks diagonal dengan entri $W_{02}[k,k] = \frac{1}{2}\log\frac{N}{2\pi} + \Re\psi(\frac{1}{2} + i\gamma_k)$ | Guinand 1948, Weil 1952 |
| $W_R$ | $n \times n$ | Matriks penuh dengan $W_R[j,k] = \frac{\sin(\gamma_j - \gamma_k)\log(\frac{N}{2\pi})}{\gamma_j - \gamma_k}$ untuk $j \ne k$, diagonal $W_R[k,k] = \log\frac{N}{2\pi}$ | Riemann-von Mangoldt |
| $W_p$ | $n \times n$ | Matriks Hankel (skew-diagonal konstan) dengan $W_p[j,k] = f_p(j+k)$ tergantung prima $p \le N$ | Weil explicit formula |

**Parameter terkunci untuk kampanye ini:**
- $c = 100$ (cutoff tinggi nol zeta)
- $N = 100$ (dim 201) dan $N = 150$ (dim 301)
- $n = 2N+1$ → dim 201 dan 301
- Presisi komputasi: **minimum 256-bit** untuk development, **6000-bit** untuk artefak produksi (sesuai `dps=1806` historis)

### 2.2 Penahanan Interval (Arb Enclosure)

Semua konstanta dan fungsi khusus dibangun sebagai bola `arb`/`acb`:

| Entri | Metode Arb | Presisi Minimum |
|---|---|---|
| $\log(N/2\pi)$ | `arb.log()` dari `fmpq` eksak | 256-bit |
| $\psi(z)$ (Digamma) | `acb.digamma()` atau evaluasi deret | 256-bit |
| $\psi_1(z)$ (Trigamma) | `acb.polygamma(1, z)` | 256-bit |
| $\sin(x)/x$ | `arb.sin(x)/x` dengan limit $x\to0$ | 256-bit |
| Prima $p \le N$ | `fmpz` eksak, dikonversi ke `arb` | Eksak |

**Aturan numerik:** Tidak ada `float` di jalur komputasi. Semua input dari `fmpq` string desimal eksak atau `fmpz` prima.

---

## 3. Target Artefak & Skema Output

### 3.1 File Output (Di-commit sebagai Bukti)

| File | Dimensi | Deskripsi |
|---|---|---|
| `reports/gw_matrix_100_100.json` | 201 × 201 | Matriks $\tau$ lengkap (real symmetric) dengan penahanan per entri |
| `reports/gw_matrix_100_150.json` | 301 × 301 | Matriks $\tau$ lengkap (real symmetric) dengan penahanan per entri |

### 3.2 Skema JSON per File

```json
{
  "schema": "msaf.gw_matrix.v1",
  "dim": 201,
  "conductor": 100,
  "block": 100,
  "prec_bits": 6000,
  "dps": 1806,
  "matrix": [
    [ {"mid": "...", "rad": "..."}, ... ],
    ...
  ],
  "build_chain": "msaf.tau_reconstruction.build_arb_tau(c=100,N=100,prec=6000) at ctx.prec=6000",
  "gate_verdict": "G-M0 PASS",
  "sha256lf": "<diisi setelah generasi>"
}
```

- `matrix[i][j]` adalah objek `{mid, rad}` merepresentasikan bola `arb` untuk entri real (matriks simetris, hanya segitiga atas perlu disimpan tapi full disimpan untuk kesederhanaan).
- `build_chain` mencatat provenance lengkap.
- `gate_verdict` diisi **hanya setelah** gate G-M0 lulus.

---

## 4. Gate Validasi G-M0 (Wajib Lulus Sebelum CERTIFIED)

File matriks **tidak boleh** diberi status `CERTIFIED` di `FENCE_REGISTRY` sebelum ketiga gate berikut lulus:

| Gate | Syarat | Toleransi |
|---|---|---|
| **G-M0.1 Finite Spectrum** | Semua eigenvalue `arb_mat.eig()` hingga (menggunakan presisi 6000-bit) hingga | Radius eigenvalue < $10^{-100}$ |
| **G-M0.2 Strict Positivity** | Semua eigenvalue real part > 0 (lower bound > 0) | Ball lower bound > 0 |
| **G-M0.3 Momentum Cross-check** | $| \frac{1}{n}\tr(\tau^k) - M_k^{theory} | < 10^{-300}$ untuk $k=1..4$ | $10^{-300}$ |

**Implementasi gate:** Ditulis di `msaf/tau_reconstruction/gates.py` dan dijalankan otomatis setelah matriks dibangun.

---

## 5. Lingkup & Non-Klaim

### 5.1 Yang Diklaim
- Rekonstruksi fungsional `build_arb_tau` di `msaf/tau_reconstruction/` menggunakan Arb-only.
- Dua file matriks tersertifikasi (dim 201, 301) dengan gate G-M0 lulus.
- Ledger evidence baru untuk reconstruct chain.

### 5.2 Yang Tidak Diklaim
- Bukti RH, lokasi nol ζ, Weil positivity, positivity matriks penuh.
- Spektrum zeta, kontrol tail, atau klasifikasi universal operator.
- Dim 401 (N=200) — memerlukan pra-registrasi terpisah.
- Modifikasi apapun di `ChronoGeometric_Framework/`, `lean/`, `harness/`.

### 5.3 Blok Scope Wajib (Setiap Output)

```json
{
  "rh_claim": false,
  "zero_location_claim": false,
  "weil_positivity_claim": false
}
```

---

## 6. Tata Letak File yang Dikunci

```
msaf/tau_reconstruction/__init__.py
msaf/tau_reconstruction/constants.py       # c, N, prec, daftar prima
msaf/tau_reconstruction/special.py         # ψ, ψ₁, sin(x)/x dengan Arb
msaf/tau_reconstruction/build.py           # build_arb_tau(c, N, prec) → arb_mat
msaf/tau_reconstruction/gates.py           # G-M0.1, G-M0.2, G-M0.3
msaf/tau_reconstruction/serialize.py       # matrix → JSON {mid, rad}
msaf/tau_reconstruction/cli.py             # entry point CLI
msaf/tests/test_tau_reconstruction.py      # unit & integration tests
reports/gw_matrix_100_100.json             # output dim 201
reports/gw_matrix_100_150.json             # output dim 301
ledger/tau_reconstruction_ledger.jsonl     # evidence chain
reports/TAU_RECONSTRUCTION_2026-10-30.md   # laporan akhir
```

---

## 7. Kriteria Penerimaan (B1–B8)

| ID | Kriteria | Verifikasi |
|---|---|---|
| **B1** | Audit AST: tidak ada `float`, `time`, `datetime` di `msaf/tau_reconstruction/*.py` | `grep -r` + AST check |
| **B2** | `build_arb_tau(100, 100, 256)` menghasilkan matriks 201×201 simetris, entri `arb` | Unit test |
| **B3** | `build_arb_tau(100, 150, 256)` menghasilkan matriks 301×301 simetris | Unit test |
| **B4** | Gate G-M0.1/2/3 lulus pada presisi 6000-bit untuk kedua dimensi | `cli.py --verify` |
| **B5** | Output JSON skema valid, `sha256lf` tercatat di `FENCE_REGISTRY` | Schema validation |
| **B6** | Ledger `tau_reconstruction_ledger.jsonl` valid (hash chain, scope block) | `ledger.verify_chain()` |
| **B7** | Laporan `TAU_RECONSTRUCTION_2026-10-30.md` dengan angka verbatim | Manual review |
| **B8** | Gerbang penuh lulus: pytest suite + `verify.ps1` | CI suite |

---

## 8. Falsifier (Otomatis Membatalkan)

| # | Kondisi | Akibat |
|---|---|---|
| F1 | Ada `float`/`time`/`datetime` di jalur numerik | B1 gagal, kode dibatalkan |
| F2 | Matriks tidak simetris (`τ != τ.T`) | B2/B3 gagal |
| F3 | Gate G-M0.1/2/3 gagal pada presisi 6000-bit | Artefak **tidak** di-commit, status `FAILED` di ledger |
| F4 | `sha256lf` di registry tidak cocok file fisik | B5 gagal, commit dibatalkan |
| F5 | Ledger chain rusak / scope block hilang | B6 gagal |
| F6 | Klaim RH / zero-location / Weil positivity muncul | Pelanggaran scope, harus dicabut |
| F7 | Commit/mutasi di `ChronoGeometric_Framework/` atau `lean/` | Pelanggaran custody, commit dibatalkan |
| F8 | Dim 401 disentuh tanpa pra-reg baru | F7 berlaku |

---

## 9. Registry yang Diusulkan (Belum Ditulis)

| ID Usulan | Jenis | Isi |
|---|---|---|
| `T-2026-0070` | T | Rekonstruksi `build_arb_tau`: matriks τ dim 201 & 301 tersertifikasi, gate G-M0 lulus |
| `T-2026-0071` | T | Artefak matriks biner: `gw_matrix_100_100.json`, `gw_matrix_100_150.json` dengan `sha256LF` |
| `A-2026-0055` | A | Audit: matriks yang dihasilkan memungkinkan uji Toeplitz/Hankel/SVD di kampanye lanjutan |

---

## 10. Urutan Eksekusi yang Mengikat

1. **Commit HANYA berkas ini:** `reports/PREREG_TAU_RECONSTRUCTION_2026-10-30.md`, pesan commit terpisah. Push ke `origin main`.
2. **Baru setelah push berhasil:** Tulis modul `msaf/tau_reconstruction/` dan test.
3. Jalankan B1–B7; perbaiki implementasi, **bukan** kriteria.
4. Hasilkan dua file matriks + ledger + laporan.
5. Commit implementasi + artefak (satu tujuan), lalu commit registry `T-2026-0070`, `T-2026-0071`, `A-2026-0055` dengan hash.
6. Jika gagal: catat deviasi di laporan & ledger; **jangan** menurunkan kriteria.

---

## 11. Amendment

Perubahan hanya sah via **Amendment** bertanggal (file terpisah atau akhir berkas ini), menyebut alasan & dampak ke B1–B8/F1–F8, di-commit sebelum implementasi terpengaruh.

```
sha256LF <diisi setelah commit> reports/PREREG_TAU_RECONSTRUCTION_2026-10-30.md
```