# Kompilasi Rumus, Turunan, dan Penjelasan Simbol
## Paradoks Skala Kausal dan Mekanika Spektral MSAF
**Author:** Muhammad Aidil Amry (Independent Researcher, South Sulawesi, Indonesia)

---

### Section 1: Kuantisasi Skala Kausalitas Semesta

**1. Persamaan Batasan Piksel Informasi Semesta**
$$N_{\text{steps}} = \frac{D_{\text{obs}}}{\ell_P}$$

**Penurunan Nilai Empiris:**
* Panjang Planck:
$$\ell_P = \sqrt{\frac{\hbar G}{c^3}} \approx 1.62 \times 10^{-35} \text{ meter}$$
* Jumlah piksel berhingga ($N_{\text{steps}}$):
$$N_{\text{steps}} \approx \frac{8.8 \times 10^{26}}{1.62 \times 10^{-35}} \approx 5.4 \times 10^{61} \text{ langkah}$$

**Penjelasan Simbol:**
* $N_{\text{steps}}$: Jumlah total piksel/langkah informasi berhingga dalam ruang-waktu teramati.
* $D_{\text{obs}}$: Diameter Kausalitas Alam Semesta Teramati ($pprox 8.8 \times 10^{26}$ meter).
* $\ell_P$: Panjang Planck, batas bawah spasial mutlak.
* $\hbar$: Konstanta Planck tereduksi ($1.054 \times 10^{-34} \text{ J}\cdot\text{s}$).
* $G$: Konstanta Gravitasi universal ($6.674 \times 10^{-11} \text{ m}^3\text{kg}^{-1}\text{s}^{-2}$).
* $c$: Kecepatan cahaya dalam ruang hampa ($2.998 \times 10^8 \text{ m/s}$).

---

### Section 2: Pemetaan Chebyshev Diskret ($\psi_d$)

**1. Diskretisasi Kisi Jarak dan Waktu Kausal**
$$x_k = k \cdot \ell_P, \quad k \in \{1, 2, \dots, N_{\text{steps}}\}$$
$$t_P = \frac{\ell_P}{c} \approx 5.39 \times 10^{-44} \text{ detik}$$
$$t_k = k \cdot t_P$$

**2. Fungsi Tangga Chebyshev Terkuantisasi**
$$\Lambda_d(k) = \begin{cases} \ln(p), & \text{jika } k \cdot \ell_P = p^m \\ 0, & \text{untuk indeks lainnya} \end{cases}$$
$$\psi_d(k) = \sum_{j=1}^{k} \Lambda_d(j)$$

**3. Rumus Eksplisit Kisi Berhingga dengan Cut-off Spektral**
$$\psi_d(k) = k \cdot \ell_P - \sum_{i=1}^{M} \frac{(k \cdot \ell_P)^{\rho_i}}{\rho_i} - \mathcal{E}_{\text{trunc}}(k)$$

**Penjelasan Simbol:**
* $k$: Indeks alamat numerik piksel/detak jam kuantum semesta.
* $t_P$: Waktu Planck, satuan waktu fundamental terkecil.
* $\psi_d(k)$: Fungsi tangga Chebyshev terkuantisasi pada piksel ke-$k$.
* $\Lambda_d(j)$: Fungsi Mangoldt Diskret pada indeks $j$.
* $\rho_i$: Akar non-trivial fungsi zeta Riemann ke-$i$ ($ho_i = 0.5 + i\gamma_i$).
* $M$: Batas atas indeks akar spektral di bawah frekuensi Nyquist informasi kisi.
* $\mathcal{E}_{\text{trunc}}(k)$: Batas galat pemotongan analitis pada piksel $k$.

---

### Section 3: Mekanika Spektral Diskret dan Batas Entropi

**1. Operator Pergeseran Waktu Sirkulan ($\hat{T}$) dan Hamiltonian Spektral ($\hat{H}$)**
$$\hat{T} = \begin{pmatrix} 0 & 1 & 0 & \cdots & 0 \\ 0 & 0 & 1 & \cdots & 0 \\ \vdots & \vdots & \vdots & \ddots & \vdots \\ 0 & 0 & 0 & \cdots & 1 \\ 1 & 0 & 0 & \cdots & 0 \end{pmatrix}, \quad \hat{T}^N = \mathbb{I}$$
$$\hat{T}[\psi_d(k)] = \psi_d(k+1) = \psi_d(k) + \Lambda_d(k+1)$$
$$[\hat{H}, \hat{T}] = 0 \implies \gamma_m = f\left(e^{i \frac{2\pi m}{N}}\right)$$

**2. Perhitungan Eksak Batas Keruntuhan Numerik (Underflow)**
$$p_k = \frac{|\lambda_k|}{\sum_{j=1}^n |\lambda_j|}$$
$$H_{\text{spectral}}(n) = - \sum_{k=1}^n p_k \log_2(p_k)$$
$$\lambda_{\min}(n) \sim \mathcal{A} \cdot e^{-\mathcal{B} \cdot n}$$
$$b > -\log_2(\lambda_{\min}(n)) \approx \log_2\left(\frac{1}{\mathcal{A}}\right) + \mathcal{B} \cdot n \cdot \log_2(e)$$

**Penurunan Dimensi Kritis Kausal ($n_{\text{crit}}$):**
$$H_{\text{spectral}}(n) \times b > I_{\max} \implies n \cdot [\mathcal{B} \cdot n \cdot \log_2(e)] \ge N_{\text{steps}}$$
$$n_{\text{crit}} \approx \sqrt{\frac{N_{\text{steps}}}{\mathcal{B} \cdot \log_2(e)}} \approx \sqrt{\frac{5.4 \times 10^{61}}{0.115 \cdot 1.4426}} \approx 1.8 \times 10^{31}$$

**Penjelasan Simbol:**
* $\hat{T}$: Matriks Pergeseran Siklik Uniter (representasi kausalitas waktu Planck).
* $\hat{H}$ : Operator Hamiltonian Spektral.
* $\mathbb{I}$: Matriks Identitas berdimensi $N \times N$.
* $H_{\text{spectral}}(n)$: Entropi Shannon dari distribusi spektral matriks dimensi $n$.
* $\lambda_{\min}(n)$: Nilai eigen terkecil dari matriks berhingga dimensi $n$.
* $\mathcal{B}$: Konstanta laju penyusutan spektral Guinand-Weil ($pprox 0.115$).
* $b$: Panjang bit memori untuk mengunci stabilitas *ball arithmetic*.
* $n_{\text{crit}}$: Batas dimensi matriks kritis teoretis sebelum terjadi keruntuhan *underflow* mutlak.

---

### Section 4: Aksioma Transisi Pemotongan Deterministik

**1. Persamaan Eliminasi Galat Ekor**
$$\mathcal{E}_{\text{trunc}} \equiv \sum_{k=N_{\text{steps}}+1}^{2N_{\text{steps}}} \text{Noise}_{\text{Planck}}(k) \le \ell_P \cdot e^{-N_{\text{steps}}}$$
$$\mathcal{E}_{\text{trunc}} \le 1.62 \times 10^{-35} \cdot e^{-5.4 \times 10^{61}} \equiv 0 \quad (\text{Lenyap secara Kausal})$$

**Penjelasan Simbol:**
* $\text{Noise}_{\text{Planck}}(k)$: Fluktuasi ketidakpastian informasi kuantum di luar horison kuantum.
* $e^{-N_{\text{steps}}}$: Faktor redaman eksponensial ekstrem semesta.
