# Protokol Dua Ruang + Kit Jembatan `msaf/bridge.py` (bounded ↔ tak hingga)

- **Tanggal:** 2026-10-19
- **Status:** protokol + perangkat metodologi (internal); bukan audit pihak
  ketiga, bukan klaim matematis baru
- **Berkas kit:** `msaf/bridge.py` (mesin), `msaf/tests/test_bridge.py`
  (guard CI), `msaf/bridge_demo.py` (demo),
  `reports/BRIDGE_DEMO_OUTPUT_2026-10-19.txt` (output verbatim)
- **Registry:** `A-2026-0006`

## 1. Doktrin dua ruang (ringkas)

Sebuah klaim tentang objek tak hingga tidak pernah dihasilkan dengan menukar
ruang secara diam-diam. Klaim semacam itu dirakit dari tiga blok:

- **[B] sertifikat terbatas** — enclosure rigor untuk bagian finit (jumlah
  parsial, integral pada interval kompak, bentuk tutup);
- **[J] jembatan** — lemma klasik bernama yang membatasi ekor, dengan
  parameter eksplisit dan arah yang benar (upper harus *memuat* batas atas
  sejati; lower harus *termuat di* batas bawah sejati);
- **[U] pernyataan tak hingga** — enclosure final = [B] + [J], dengan
  pergantian ruang tercatat (label, cutoff, anggaran, verdict).

Aturan arah adalah inti doktrin: salah arah = klaim palsu meski aritmetikanya
"benar". Karena itu semua keputusan (`tail <= eps`) memakai perbandingan Arb
yang rigor (benar hanya bila berlaku untuk *semua* anggota kedua bola) —
bukan perbandingan titik-tengah atau float.

Kaitan dengan mesin yang sudah ada:

- `msaf/certify.py`: mandat containment ("zero-claim must be certified by
  containment, never by equality") — kit jembatan memperluas disiplin yang
  sama ke klaim lintas-ruang; non-finit (NaN/inf) ditolak di setiap pintu
  masuk, tidak pernah lolos sebagai sertifikat;
- `msaf/budget.py`: anggaran presisi — `split_budget` melengkapinya dengan
  anggaran pemotongan (bagian terbatas vs ekor);
- `msaf/tests/test_tail_decay.py`: contoh jembatan yang sudah berjalan
  (kotak periodik N=16 vs free-space) — kit ini menstandarkan polanya.

## 2. Kit `msaf/bridge.py` — lemma yang diinstansiasi

| Kode | Lemma | Syarat | Bentuk |
|------|-------|--------|--------|
| L1 | ekor geometrik (eksak, dua arah) | 0 <= r < 1 | sum_{n>N} r^n = r^(N+1)/(1-r) |
| L2 | ekor deret-p (dua sisi) | p > 1, N >= 1 | 1/((p-1)(N+1)^(p-1)) <= sum_{n>N} n^(-p) <= 1/((p-1)N^(p-1)) |
| L3 | envelope eksponensial (upper) | C >= 0, lam > 0 | f <= C*exp(-lam*x) pada [M,inf) => int_M^inf f <= (C/lam)*exp(-lam*M) |
| L4 | ekor Gaussian (upper) | M > 0 | int_M^inf exp(-x^2) dx <= exp(-M^2)/(2M) |
| L5 | perbandingan integral (mekanisme L2) | f positif menurun | int_{N+1}^inf f <= sum_{n>N} f(n) <= int_N^inf f |

Pembuktian L1–L5 adalah kalkulus elementer standar (deret geometri; uji
integral; dominasi pembilang; trik x >= M saat menaksir e^(-x^2)). Lemma
*dirujuk*, tidak diformalkan ulang di sini.

Fungsi publik: `split_budget`, `geometric_tail`, `pseries_tail_bounds`,
`exp_envelope_tail`, `gaussian_tail_ub`, `choose_cutoff`,
`choose_cutoff_real`, `assemble` (emitter `BridgeCertificate` dengan
`lines()` [B]/[J]/[U]).

### 2.1 Pencarian vs sertifikat

Cutoff dicari dengan heuristik murni (doubling + bisection bilangan bulat;
bisection float untuk variabel kontinu). Pencarian **tidak pernah** menjadi
bukti: nilai akhir hanya diterima bila `assemble` membuktikan `width <= eps`
lewat perbandingan rigor. Anggaran yang tak tercapai → `RuntimeError`
(fail-closed), bukan lolos diam-diam; `assemble` pada kasus tak terbukti
mengembalikan `certified=False` + verdict eksplisit.

## 3. Protokol [B]/[J]/[U] (checklist)

Template minimal untuk klaim baru lintas-ruang:

```text
[B] bounded  : <enclosure rigor bagian finit + metode>
[J] bridge   : <lemma bernama L? + parameter eksplisit + arah + bound ekor>
[U] statement: <enclosure final = [B]+[J]; label; cutoff; eps; verdict>
```

Checklist:

1. Identifikasi ruang objek (terbatas / tak hingga / mana yang menjadi
   klaim).
2. Tentukan bagian terbatas [B]: bentuk tutup atau komputasi rigor (ball
   arithmetic); tanpa float di jalur keputusan.
3. Pilih lemma jembatan [J] yang bernama; tulis parameter eksplisit;
   periksa arah (upper memuat; lower termuat).
4. Pecah anggaran: `split_budget(eps)` (atau pecahan eksplisit).
5. Cari cutoff (`choose_cutoff` / `choose_cutoff_real`) — heuristik; catat
   bahwa keputusan final rigor.
6. Rakit + sertifikasi ulang di `assemble`: `width <= eps` harus terbukti;
   kalau tidak, label turun (`certified=False`).
7. Rekam: label, cutoff, eps, verdict; promosikan ke registry (`sha256LF`)
   hanya bila disegel.
8. Tulis "Batas" (apa yang *tidak* diklaim; mis. lemma klasik dirujuk,
   bukan diformalkan).

## 4. Demo tersertifikasi (verbatim)

Perintah: `python -m msaf.bridge_demo` (Arb prec 128; deterministik — output
di bawah disalin byte-exact dari berkas output, diverifikasi oleh capture
ganda saat pembekuan).

```text
BRIDGE KIT DEMO -- bounded [B] + bridge [J] + unbounded [U]
arb precision: 128

D1  zeta(2) = sum_{n>=1} 1/n^2   (L2, two-sided)
    cutoff N = 14142 (partial-sum terms: 14142)
    [B] bounded part : [1.644863357991971647375416036165980 +/- 5.24e-34]
    [J] tail in      : [[7.0706356501449480308279714346319734144e-5 +/- 5.02e-43], [7.0711356243812756328666383821241691415e-5 +/- 6.77e-43]]
    [U] total in     : [[1.644934064348473096855724315880326 +/- 2.05e-34], [1.6449340693482154601317447025498008 +/- 8.38e-35]]
        budget eps   : [1.0000000000000000000000000000000000000e-8 +/- 2.11e-47]   (width <= eps: True)
        verdict      : CERTIFIED: bounded + bridge within budget
        label        : zeta(2) via partial sum + p-series tail
    contains pi^2/6  : True

D2  int_1^inf exp(-x) dx   (L3, envelope C=1 lam=1)
    cutoff M = [42.139678854464590000000000000000000000 +/- 2.07e-38]
    [B] bounded part : [0.36787944117144232109552377016737205657 +/- 6.88e-39]
    [J] tail in      : [0, [4.9999999999408881087057409504529027083e-19 +/- 7.80e-57]]
    [U] total in     : [[0.36787944117144232109552377016737205657 +/- 6.88e-39], [0.36787944117144232159552377016146086744 +/- 7.72e-39]]
        budget eps   : [1.0000000000000000000000000000000000000e-18 +/- 2.03e-57]   (width <= eps: True)
        verdict      : CERTIFIED: bounded + bridge within budget
        label        : int_1^inf exp(-x) dx (closed form + envelope)
    bracket [0.36, 0.38] : True

D3  int_2^inf exp(-x^2) dx   (L4, Gaussian tail)
    [B] bounded part : 0
    [J] tail in      : [0, [0.0045789097221835450734295053183103105530 +/- 4.79e-41]]
    [U] total in     : [0, [0.0045789097221835450734295053183103105530 +/- 4.79e-41]]
        budget eps   : [0.0050000000000000000000000000000000000000 +/- 7.38e-42]   (width <= eps: True)
        verdict      : CERTIFIED: bounded + bridge within budget
        label        : gaussian tail bound at M=2 (L4)

ALL DEMOS CERTIFIED: True
```

Ringkas angka: D1 memakai [B] jumlah parsial N=14142 + [J] dua-sisi
1/(N+1) <= ekor <= 1/N → lebar ≈ 5.0e-9 (<= 1e-8) dan memuat π²/6; D2
memakai [B] bentuk tutup + [J] envelope L3, cutoff M ≈ 42.13967885446459 →
lebar <= 1e-18 (bracket [0.36, 0.38]); D3 memakai L4 murni (tanpa bentuk
tutup) → batas atas ekor Gaussian pada M=2 di bawah 5e-3.

## 5. Batas

- Kit adalah **alat metodologi/estimasi**; ia tidak menghasilkan klaim baru
  tentang objek apa pun — ia hanya membuat klaim lintas-ruang dapat
  diperiksa dan tercatat.
- L1–L5 klasik; bukti dirujuk (kalkulus elementer), tidak diformalkan ulang
  di sini; tidak ada klaim RH/P≠NP; tidak ada klaim fisik.
- Angka demo adalah demonstrasi mekanika [B]+[J]→[U] pada objek klasik
  (ζ(2), dua ekor integral), bukan pernyataan riset baru.
- Protokol ini tidak menggantikan peer review; ia membuat rantai
  [B]–[J]–[U] eksplisit dan dapat direplay.

## 6. Reproduksi

- `python -m msaf.bridge_demo` → 3 demo; `ALL DEMOS CERTIFIED: True`;
  exit 0.
- `python -m pytest msaf/tests/test_bridge.py -q` → 19 uji.
- Guard registry: `python -m pytest msaf/tests/test_fence_registry.py -q`.
- Output beku: `reports/BRIDGE_DEMO_OUTPUT_2026-10-19.txt` (sha256LF
  tercatat di `A-2026-0006`).
