# Pra-registrasi Chrono-Geometric Runtime — T-hat-N / MSAF — 2026-10-30

**Status:** scope DIKUNCI. Berkas ini adalah pra-registrasi terpisah yang **wajib
di-commit dan dipush sebelum** satu baris pun kode implementasi di `msaf/`
ditulis. Isinya mengikat: definisi, path, skema, kriteria penerimaan, dan
falsifier di bawah tidak boleh diubah tanpa amendment bertanggal.

**Otoritas:** `CURRENT_AUTHORITY.md` > `AGENTS.md` > `reports/DECISION_LOG.md` >
`reports/FENCE_REGISTRY.md`. Berkas ini berada di bawah keempatnya.

**Tidak mengubah:** klaim yang sudah ada (`T-2026-0064`, `T-2026-0065`,
`T-2026-0066`, `T-2026-0067`, `A-2026-0053`, `F-2026-0001`, `F-2026-0002`, dan
seterusnya), status baseline P0/P1/P2, maupun artefak ber-`sha256LF`.

**Keputusan pemilik yang dikunci di sini (2026-10-30):**

1. `ChronoGeometric_Framework/` dipertahankan sebagai **vendored read-only
   subtree** (opsi i). Dilarang commit, mutasi, `git add`, atau `git rm` di
   dalamnya. Remote `chrono` tidak dipakai.
2. `N_STEPS` memakai **integer eksak** hasil `floor` dari modulus rigid
   `T^N = I`, bukan literal float dan bukan ball non-integer.
3. Lingkup spektrum Riemann hanya artefak yang **sudah ada**: dim 201
   (`reports/gw_spectrum_100_100.json`) dan dim 301
   (`reports/gw_spectrum_100_150.json`). Dim 401 dilarang sampai ada kampanye
   baru dengan pra-registrasi sendiri.
4. Definisi `p_i`, `H_S`, dan `L_Im` memakai penahanan Arb, dan setiap output
   wajib memuat blok `scope` dengan tiga klaim global bernilai `false`.

---

## 1. Definisi yang dikunci

### 1.1 Latis dan jam diskret

| Simbol | Nilai / definisi | Provenance |
|---|---|---|
| `N_STEPS` | `54446853992717733278474003174004102075476951347404957757284586` | `int(msaf.grid.n_steps_floor())`; 62 digit, 206 bit; `msaf/constants.N_STEPS` adalah ball non-integer dan **tidak** dipakai sebagai eksponen |
| `L_PLANCK_M` | `Fraction(1616255, 10**41)` meter | literal `1.616255e-35` yang sama dengan `msaf/grid.py` |
| `C_M_PER_S` | `Fraction(299792458)` | definisi SI eksak |
| `TICK_SECONDS` | `L_PLANCK_M / C_M_PER_S` | konvensi model, bukan pengukuran fisika |
| `HORIZON_SECONDS` | `N_STEPS * TICK_SECONDS` | `≈ D_OBS / c` hingga efek `floor`; bukan klaim kosmologis |
| `phase(t)` | `t % N_STEPS` untuk `t ∈ ℤ`, `t ≥ 0` | satu-satunya tempat wrap diizinkan |
| `tick` | integer Python tak terbatas | jumlah `Chronon.next` sejak `now` |
| `Chronon` (Python) | `now = 0`, `next(k) = k + 1` | mirror `ChronoNat.Chronon` |

Aturan mutlak:

- Tidak ada `float` di jalur komputasi. Semua waktu, rasio, dan bobot adalah
  `fractions.Fraction`, `int`, atau ball `arb`/`acb` yang dibangun dari
  `fmpq`/string desimal eksak.
- `TICK_SECONDS`, `HORIZON_SECONDS`, dan `phase` tidak boleh dihitung lewat
  pembagian float. `HORIZON_SECONDS` disimpan sebagai `Fraction` (pembilang
  dan penyebut besar), bukan diringkas ke desimal.
- `t < 0` ditolak dengan `ValueError`; tidak ada fase negatif yang
  didefinisikan.
- Tidak ada klaim apa pun tentang horizon wrap. Setiap run nyata hanya
  menyentuh `t ≪ N_STEPS`; wrap diuji sebagai fungsi aritmetika, bukan sebagai
  peristiwa fisik.

### 1.2 `Shape` → `flatten`

`Shape` di Lean (`ChronoNat.lean`) tidak punya payload. Mirror Python-nya
mengikuti persis konstruktor Lean:

```text
flatten(point)       = [1]
flatten(line a b)    = flatten(a) ++ flatten(b)
flatten(plane a b c) = flatten(a) ++ flatten(b) ++ flatten(c)
flatten(space xs)    = concat (map flatten xs)
```

- `flatten` mengembalikan `list[int]`; setiap `point` menyumbang satu elemen
  bernilai `1`.
- `space []` menghasilkan panjang `0`; operator berskala nol ditolak dengan
  `ValueError` (tidak ada matriks `0×0` yang diklaim).
- `leaf_count(shape) = len(flatten(shape))`.

### 1.3 `Shape` → `(H_hat, T_hat)`

Untuk `n = leaf_count(shape) ≥ 1`:

- `T_hat(n)` adalah matriks permutasi siklik `n×n` dengan
  `T_hat[i][(i+1) mod n] = 1`, entri lain `0`.
- `H_hat(n)` adalah sirkulan simetris `I_n + J_n` (`J_n` matriks semua-satu).
  Alasannya dikunci: satu-satunya informasi yang dibawa `Shape` adalah jumlah
  titik, sehingga operator simetris kanonik pada himpunan titik tanpa label
  adalah graf lengkap dengan self-loop. Ini **pilihan model**, bukan klaim
  tentang matriks Guinand–Weil.
- Keduanya dibangun sebagai matriks integer eksak; tidak ada float, tidak ada
  pembulatan.

Konsekuensi yang harus ditulis jujur di laporan: karena `H_hat` dan `T_hat`
keduanya sirkulan **berdasarkan konstruksi**, `[H_hat, T_hat] = 0` adalah
tautologi. Uji komutasi because itu diberi label `CONSTRUCTION-GUARD` dan
**tidak boleh** dilaporkan sebagai bukti empiris, apalagi sebagai bukti tentang
ζ. Yang punya isi adalah uji §1.6 pada spektrum artefak nyata.

### 1.4 Emulator transisi

State runtime dikunci sebagai:

```text
ChronoState(value: int, shape: Shape, tick: int)
```

Aturan transisi `step` adalah mirror `ChronoState.advance`:

```text
step(value, shape, tick) = (value, line(shape, point), tick + 1)
```

Invarian yang wajib disertifikatkan setiap langkah:

```text
value(t)      == value(0)                       (ChronoState.advance)
leaf_count(t) == leaf_count(0) + t              (ChronoState.advance_shape)
tick(t)       == t                              (definisi)
phase(t)      == t mod N_STEPS                  (lattice.wrap)
```

`collapse` adalah mirror `ChronoState.collapse_to_harmony`: jika
`shape.tag == "space"` dan `tick ≥ 1`, hasilnya `(value, point, tick)`;
selain itu state tidak berubah. Tidak ada `time.time()`, `datetime.now()`,
atau sumber waktu sistem operasi di modul runtime.

Setiap `step` menghasilkan satu certificate dengan skema §1.7. Sertifikat
interval untuk permutasi/penambahan simpul bersifat eksak (radius `0`); itu
sah, tetapi harus dilabeli `EXACT-DISCRETE`, bukan "verifikasi numerik sulit".

### 1.5 Observabel spektrum dari artefak

Artefak `reports/gw_spectrum_100_100.json` dan
`reports/gw_spectrum_100_150.json` hanya memuat **spektrum**, bukan matriks.
`build_chain` menyebut `source_arb_ldlt_certify.build_arb_tau`, modul yang
**tidak ada** di repositori ini. Karena itu:

- Tidak ada rekonstruksi matriks dari spektrum. Rekonstruksi tidak tunggal dan
  akan menjadi fabrikasi.
- Semua observabel didefinisikan pada multiset eigenvalue
  `λ_i = acb(re_i, im_i)` dengan `re_i` dari field `"re"` dan radius dari field
  `"re_rad"`, serta `im_i` dari field `"im_abs"`.
- `n` harus sama dengan `len(eig)` dan dengan field `n` artefak
  (201 dan 301). Ketidakcocokan → `FAILED`, bukan dipaksa.

Definisi yang dikunci (semua dengan `arb`/`acb`, `log` = logaritma natural):

```text
|λ_i|    = abs(acb(re_i, im_i))
Σ|λ|     = Σ_i |λ_i|
p_i      = |λ_i| / Σ|λ|
H_S      = -Σ_i p_i * log(p_i)          dengan konvensi 0*log 0 := 0
L_Im     = (Σ_i |Im λ_i|) / (Σ_i |λ_i|)
```

`H_S` dan `L_Im` dilaporkan sebagai pasangan `{mid, rad}` dari ball `arb`.
`p_i` tidak diserialisasi satu per satu; cukup `H_S`, `L_Im`, `Σ|λ|`, dan
jumlah eigenvalue.

### 1.6 Uji struktur sirkulan pada spektrum nyata

Karena matriks tidak tersedia, satu-satunya uji struktur matriks yang bisa
dibuat dari spektrum adalah syarat **perlu** berikut.

Untuk matriks riil simetris sirkulan, spektrumnya riil dan memenuhi
`λ_j = λ_{n-1-j}` setelah diurutkan menurun (multiset invarian terhadap
involusi dengan satu titik tetap). Didefinisikan:

```text
sort_λ        = urutkan menurun berdasarkan midpoint
ordering_ok   = setiap dua ball berurutan saling lepas (disjoint)
defect        = max_{0 ≤ j < n} |λ_(j) - λ_(n-1-j)|      (ball arb)
witness       = pasangan j dengan lower_bound(defect_j) > 0
```

Verdict yang diizinkan, dan hanya tiga ini:

| Verdict | Syarat |
|---|---|
| `NOT-SYMMETRIC-CIRCULANT` | ada `j` dengan ball `λ_(j)` dan `λ_(n-1-j)` lepas; lower bound `|λ_(j) - λ_(n-1-j)| > 0` dicatat sebagai witness |
| `COMPATIBLE-NECESSARY-ONLY` | `ordering_ok` dan tidak ada pasangan lepas; **bukan** bukti sirkulan, hanya tidak terbantah |
| `UNAVAILABLE` | `ordering_ok` gagal (ball berurutan tumpang tindih) |

Verdict `CIRCULANT` **dilarang** muncul dari uji ini. Uji ini hanya syarat
perlu; ia tidak membuktikan sirkulanitas dan tidak menyentuh ζ.

Untuk dua artefak yang ada, nilai midpoint menunjukkan `defect` orde 7
(dim 201) dan 6 (dim 301), sedangkan radius eigenvalue orde `1e-1728`.
Karena itu hasil yang **diharapkan** adalah `NOT-SYMMETRIC-CIRCULANT` untuk
keduanya. Ekspektasi ini bukan kriteria penerimaan: yang diwajibkan adalah
verdict + witness yang dihitung, bukan verdict yang diinginkan.

### 1.7 Uji perturbasi sintetis (bukan nol ζ)

Keluarga perturbasi yang dikunci:

```text
M_0   : λ_i                 (artefak apa adanya)
M_ε   : λ_i + i·ε           untuk setiap i, ε ∈ {1/100, 1/50}
```

`ε` dibangun dari `fmpq(1, 100)` dan `fmpq(1, 50)`, bukan string desimal dan
bukan float. Setiap record perturbasi wajib memuat
`"synthetic_only": true` dan `"zero_location_claim": false`.

Uji ini **bukan** simulasi pergeseran nol ζ dari σ = 1/2 ke 0.49/0.51. Nol ζ
bukan parameter bebas dari blok Guinand–Weil terpotong, dan tidak ada artefak
di repo ini yang membangun blok dengan nol yang digeser. Yang diuji adalah
sensitivitas definisi observabel terhadap kebocoran imajiner yang disuntikkan
secara sintetis. Klaim yang boleh dibuat hanya tentang operator sintetis itu.

Sifat yang wajib disertifikatkan (bukan diasumsikan):

```text
P1  L_Im(M_0) == 0  secara eksak, karena seluruh im_abs = "0"
P2  L_Im(M_ε) > 0    (lower bound ball > 0) untuk ε > 0
P3  H_S(M_ε) - H_S(M_0) > 0, dan untuk dua artefak ini selisihnya ≥ 1/1000
P4  L_Im(M_{1/50}) > L_Im(M_{1/100})  (respons monoton terhadap ε)
```

P1–P4 adalah alasan uji ini tidak vacuous: definisi yang sama akan mendeteksi
kebocoran `ε = 1/100` (nilai terukur orde `4.7e-3` untuk dim 201), sehingga
`L_Im = 0` pada artefak tak-perturbasi adalah hasil pengukuran, bukan
konsekuensi struktural dari definisi.

### 1.8 "Constraint Geometri Waktu" — versi finit

Frasa "mengunci kebenaran atau kesalahan lokasi nol ζ" **ditolak**. Yang
dikunci sebagai constraint finit adalah:

> Untuk keluarga bernama `(c=100, N=100, dim=201)` dan
> `(c=100, N=150, dim=301)`, spektrum yang direkam tidak kompatibel dengan
> spektrum matriks riil simetris sirkulan, dengan witness pasangan eigenvalue
> yang ball-nya lepas dan lower bound defect > 0.

Itu pernyataan tentang dua artefak finit, bukan tentang lokasi nol ζ. Karena
itu constraint ini juga menjelaskan mengapa lapisan sirkulan `H_hat`/`T_hat`
adalah model terpisah: ia **tidak** menggambarkan blok GW, dan komutasi di
lapisan itu tidak boleh dipakai sebagai evidensi apa pun tentang ζ.

---

## 2. Lingkup dan non-klaim

### 2.1 Yang diklaim

1. Latis dengan `N_STEPS` eksak dan akuntansi tick integer/Fraction.
2. Emulator diskret yang setiap langkahnya menghasilkan certificate dan
   memenuhi invarian §1.4.
3. Observabel `H_S`, `L_Im`, `Σ|λ|`, dan `circulant_pairing_defect` untuk dim
   201 dan 301, dengan penahanan Arb dan provenance artefak.
4. Ledger append-only dengan rantai hash yang valid.
5. Laporan `reports/CHRONO_RUNTIME_2026-10-30.md` dan
   `reports/CHRONO_RIEMANN_INSIGHTS.json` yang memuat angka verbatim.

### 2.2 Yang tidak diklaim

- Bukan bukti Riemann Hypothesis, bukan klaim lokasi nol ζ, bukan Weil
  positivity, bukan positivity matriks, bukan spektrum zeta, bukan kontrol
  tail matriks.
- Bukan rekonstruksi blok Guinand–Weil. Matriksnya tidak ada di repo ini.
- Bukan pernyataan bahwa `[H_hat, T_hat] = 0` membawa informasi tentang ζ.
  Komutasi itu tautologi konstruksi dan dilabeli demikian.
- Bukan pernyataan fisika: `TICK_SECONDS` dan `HORIZON_SECONDS` adalah
  konvensi model dari konstanta grid, bukan pengukuran.
- Bukan formalisasi Lean baru. Tidak ada file di `ChronoGeometric_Framework/`
  atau `lean/` yang diubah dalam kampanye ini.
- Dim 401 tidak disentuh, tidak dibangun, dan tidak diklaim.

### 2.3 Blok scope wajib

Setiap output mesin (`reports/CHRONO_RIEMANN_INSIGHTS.json`, summary run, dan
setiap record ledger) wajib memuat:

```json
"scope": {
  "rh_claim": false,
  "zero_location_claim": false,
  "weil_positivity_claim": false
}
```

Record perturbasi menambahkan `"synthetic_only": true`. Tidak adanya blok ini
membuat output invalid.

---

## 3. Tata letak file yang dikunci

```text
msaf/chrono_runtime/__init__.py
msaf/chrono_runtime/lattice.py            N_STEPS, TICK_SECONDS, phase, wrap
msaf/chrono_runtime/shape_ops.py          flatten, leaf_count, circulant, dft
msaf/chrono_runtime/emulator.py           step, collapse, certificate
msaf/chrono_runtime/riemann_operator.py   spectrum loading, H_S, L_Im, defect, perturb
msaf/chrono_runtime/ledger.py             canonical JSON, hash chain, append
msaf/bridge/__init__.py
msaf/bridge/chrono_bridge.py              Shape -> (H_hat, T_hat), commutation guard
msaf/tests/test_chrono_runtime.py
msaf/tests/test_chrono_riemann_operator.py
msaf/tests/test_chrono_ledger.py
ledger/chrono_execution_ledger.jsonl      append-only evidence
reports/CHRONO_RIEMANN_INSIGHTS.json      output wajib
reports/CHRONO_RUNTIME_2026-10-30.md      laporan
mcp/out/chrono_runtime/<run_id>/summary.json
mcp/out/chrono_runtime/<run_id>/certificates.jsonl
```

Aturan path:

- Kode **hanya** di `msaf/`. `mcp/out/` hanya untuk ekspor yang dapat
  diregenerasi dan **tidak** di-commit.
- `ledger/chrono_execution_ledger.jsonl` dan
  `reports/CHRONO_RIEMANN_INSIGHTS.json` **di-commit** sebagai bukti.
- Tidak ada file baru di `ChronoGeometric_Framework/`, `lean/`, `lean/spec/`,
  atau `harness/`.
- `run_id` adalah `sha256` dari JSON kanonik konfigurasi run (dim, artefak,
  `prec`, `ε`, versi skema). `run_id` deterministik; timestamp tidak dipakai
  untuk verifikasi.

---

## 4. Skema data yang dikunci

### 4.1 Certificate (`certificates.jsonl`, satu objek per baris)

```json
{
  "schema": "msaf.chrono_runtime.certificate.v1",
  "rule_id": "CHRONO-ADVANCE",
  "tick": 0,
  "phase": 0,
  "value": 0,
  "leaf_count": 1,
  "prev_state_hash": "<hex>",
  "state_hash": "<hex>",
  "observable": {"name": "leaf_count", "mid": "1", "rad": "0"},
  "kind": "EXACT-DISCRETE",
  "lean_decl": "ChronoState.advance_shape",
  "anchor_status": "ANCHORED"
}
```

`anchor_status` hanya boleh `ANCHORED` (ada deklarasi Lean yang dirujuk) atau
`UNANCHORED` (tidak ada deklarasi Lean; wajib disertai `anchor_reason`).
Langkah `LATTICE-WRAP`, `SHAPE-FLATTEN`, dan `CIRCULANT-BUILD` adalah
`UNANCHORED`; itu dicatat, bukan ditutupi dengan nama deklarasi palsu.

### 4.2 Record ledger (`ledger/chrono_execution_ledger.jsonl`)

```json
{
  "schema": "msaf.chrono_execution.v1",
  "index": 0,
  "run_id": "<sha256>",
  "rule_id": "TAU-SPECTRUM",
  "dim": 201,
  "execution_status": "PASS",
  "numerical_verdict": "spectrum observed; L_Im = 0; circulant pairing refuted",
  "payload_sha256": "<sha256 of canonical result payload>",
  "scope": {"rh_claim": false, "zero_location_claim": false, "weil_positivity_claim": false},
  "previous_hash": "GENESIS",
  "record_hash": "<sha256>"
}
```

Kanonikalisasi dan rantai:

```text
payload      = record tanpa field "record_hash"
canonical    = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
record_hash  = sha256(canonical).hexdigest()
previous_hash= record_hash milik record index-1; record 0 memakai "GENESIS"
index        = 0, 1, 2, ... tanpa lompatan
```

`execution_status` hanya `PASS` atau `FAILED`. Kegagalan **tidak** mematikan
server MCP dan **tidak** melempar exception ke pemanggil level atas: kegagalan
dikembalikan sebagai record `FAILED` dengan `deviation` yang menjelaskan
penyebabnya. `FAILED` tidak pernah menjadi `CERTIFIED` di registry.

### 4.3 `reports/CHRONO_RIEMANN_INSIGHTS.json`

```json
{
  "schema": "msaf.chrono_riemann_insights.v1",
  "prereg_sha256lf": "<sha256LF reports/PREREG_CHRONO_RUNTIME_2026-10-30.md>",
  "generated_utc": "<ISO-8601>",
  "scope": {"rh_claim": false, "zero_location_claim": false, "weil_positivity_claim": false},
  "records": [
    {
      "dim": 201,
      "artifact": "reports/gw_spectrum_100_100.json",
      "artifact_sha256lf": "<hex>",
      "eigenvalue_count": 201,
      "prec_bits": 256,
      "sigma_abs_sum": {"mid": "...", "rad": "..."},
      "spectral_entropy": {"mid": "...", "rad": "..."},
      "imaginary_leak": {"mid": "0", "rad": "0"},
      "circulant_pairing": {
        "verdict": "NOT-SYMMETRIC-CIRCULANT",
        "witness_index": 0,
        "defect_lower_bound": "...",
        "ordering_certified": true
      },
      "perturbations": [
        {
          "epsilon": "1/100",
          "synthetic_only": true,
          "spectral_entropy": {"mid": "...", "rad": "..."},
          "imaginary_leak": {"mid": "...", "rad": "..."},
          "execution_status": "PASS"
        }
      ],
      "numerical_verdict": "...",
      "execution_status": "PASS"
    }
  ],
  "deviations": []
}
```

Larangan skema:

- Kunci `mathematical_verdict` **dilarang**; yang dipakai hanya
  `numerical_verdict`.
- `dim` hanya boleh `201` atau `301`.
- `scope` wajib ada dan ketiga nilainya `false`.
- Setiap `artifact_sha256lf` harus cocok dengan file artefak saat uji.
- `prereg_sha256lf` harus cocok dengan hash berkas ini saat uji.
- `epsilon` diserialisasi sebagai string rasio (`"1/100"`), bukan float.

---

## 5. Kriteria penerimaan (A1–A10)

Semua harus lulus pada commit implementasi sebelum entri registry ditulis.

**A1 — Disiplin numerik.** Audit AST atas `msaf/chrono_runtime/*.py` dan
`msaf/bridge/chrono_bridge.py` tidak menemukan `ast.Constant` bertipe `float`,
tidak menemukan panggilan `float(...)`, dan tidak menemukan `time.time` /
`datetime.now`. Semua observabel numerik bertipe `arb`/`acb`/`Fraction`/`int`.

**A2 — Latis eksak.** `N_STEPS == int(msaf.grid.n_steps_floor())`;
`len(str(N_STEPS)) == 62`; `N_STEPS.bit_length() == 206`;
`TICK_SECONDS == Fraction(1616255, 10**41 * 299792458)`;
`phase(t) == t % N_STEPS`; `t < 0` ditolak; `HORIZON_SECONDS` adalah
`Fraction`.

**A3 — Mirror `Shape`.** `flatten` memenuhi empat persamaan §1.2; `space []`
ditolak oleh pembangun operator; untuk setiap `t`, emulator memenuhi
`leaf_count(t) - leaf_count(0) == t`, `value(t) == value(0)`, dan
`phase(t) == t % N_STEPS`.

**A4 — Guard konstruksi.** `H_hat @ T_hat == T_hat @ H_hat` secara eksak
(matriks integer); `H_hat == H_hat.T`; `T_hat` adalah permutasi; residual DFT
`‖F H F* − diag(λ)‖` dan `‖F T F* − diag(ω)‖` terkurung dengan radius
`< 1e-40` pada presisi 256 bit. Test ini dilabeli `CONSTRUCTION-GUARD` dan
tidak boleh dipresentasikan sebagai evidensi empiris.

**A5 — Observabel artefak.** Untuk dim 201 dan 301: `L_Im` adalah ball `[0,0]`
eksak; `H_S` adalah ball positif dengan lebar `< 1e-9`; `Σ|λ|` ball positif;
jumlah eigenvalue sama dengan field `n`; hasil hitung ulang meng-overlap
dengan `reports/CHRONO_RIEMANN_INSIGHTS.json` (artefak tidak boleh drift).

**A6 — Uji sirkulan.** Verdict dihitung, bukan di-hardcode; `ordering_ok`
disertifikasi; bila verdict `NOT-SYMMETRIC-CIRCULANT`, witness index dan
lower bound defect dicatat. Untuk dua artefak ini verdict yang diharapkan
adalah `NOT-SYMMETRIC-CIRCULANT`; bila hasilnya berbeda, perbedaan dicatat di
`deviations`, bukan dipaksa.

**A7 — Perturbasi.** P1–P4 §1.7 lulus untuk dim 201 dan 301 pada
`ε ∈ {1/100, 1/50}`; setiap record memuat `synthetic_only: true` dan blok
scope.

**A8 — Ledger.** `ledger/chrono_execution_ledger.jsonl` valid: index
berurutan, `previous_hash` cocok, `record_hash` cocok dengan kanonikalisasi
§4.2, dan record pertama `previous_hash == "GENESIS"`; record `FAILED` dapat
ditulis tanpa mematikan proses; tidak ada record `FAILED` yang berstatus
`CERTIFIED`.

**A9 — Insights JSON.** Skema §4.3 valid; `scope` tiga `false`; tidak ada
`mathematical_verdict`; `prereg_sha256lf` dan `artifact_sha256lf` cocok;
`dim ∈ {201, 301}`; `epsilon` berupa string rasio.

**A10 — Gerbang penuh.**

```text
python -m pytest msaf/tests/test_chrono_runtime.py -q
python -m pytest msaf/tests/test_chrono_riemann_operator.py -q
python -m pytest msaf/tests/test_chrono_ledger.py -q
python -m pytest msaf/tests/test_authority_manifest.py -q
python -m pytest msaf/tests/test_fence_registry.py -q
python -m pytest msaf/tests/test_lean_axiom_audit.py -q
python -m pytest msaf/tests/test_anti_circularity_gate.py -q
cd ChronoGeometric_Framework && powershell -ExecutionPolicy Bypass -File verify.ps1
```

Suite baru harus selesai `< 30 s` pada mesin ini. Bila melebihi, test boleh
dipisah dengan marker `slow`, tetapi tidak boleh dihapus atau dilemahkan.

---

## 6. Falsifier

| # | Kondisi | Akibat |
|---|---|---|
| F1 | Ada `float`/`time.time`/`datetime.now` di jalur runtime | A1 gagal; seluruh hasil dibatalkan |
| F2 | `N_STEPS` berbeda dari `int(n_steps_floor())` | A2 gagal; ledger tidak boleh di-append |
| F3 | `phase` salah atau tick negatif diterima | A2 gagal |
| F4 | `leaf_count(t) != leaf_count(0) + t` | A3 gagal; certificate tidak valid |
| F5 | `H @ T != T @ H` atau residual DFT ≥ `1e-40` | A4 gagal |
| F6 | `L_Im(M_0) != 0` eksak | A5 gagal; definisi atau data salah |
| F7 | `L_Im(M_ε)` lower bound ≤ 0 atau `H_S(M_ε) - H_S(M_0) ≤ 0` | A7 gagal; observabel tidak sensitif |
| F8 | JSON memuat `mathematical_verdict`, atau `dim` di luar {201,301}, atau scope tidak lengkap | A9 gagal; artefak invalid |
| F9 | `previous_hash`/`record_hash`/index tidak konsisten | A8 gagal; ledger tidak dapat dipercaya |
| F10 | Run `FAILED` diberi status `CERTIFIED` di registry | pelanggaran aturan; entri harus di-retract |
| F11 | Ada klaim RH, lokasi nol, Weil positivity, atau positivity matriks | klaim di luar lingkup; harus dicabut |
| F12 | Ada commit/mutasi di `ChronoGeometric_Framework/` atau `lean/` | pelanggaran custody; commit dibatalkan |
| F13 | `prereg_sha256lf` atau `artifact_sha256lf` tidak cocok | A9 gagal; hasil tidak terikat ke pra-registrasi |
| F14 | Verdict `CIRCULANT` dipakai dari uji §1.6 | overclaim; uji itu hanya syarat perlu |
| F15 | Hasil perturbasi disebut sebagai pergeseran nol ζ dari σ = 1/2 | fabrikasi; harus dikoreksi |

---

## 7. Registry yang diusulkan (belum ditulis)

Entri **tidak** ditulis di commit pra-registrasi ini. Entri baru ditulis hanya
setelah A1–A10 lulus, di commit terpisah, dengan `sha256LF` yang dihitung ulang.

| ID usulan | Jenis | Isi |
|---|---|---|
| `T-2026-0068` | T | Latis eksak + emulator diskret: `N_STEPS`, tick/Fraction, invarian `leaf_count`, certificate per langkah, ledger chain |
| `T-2026-0069` | T | Observabel spektrum dim 201/301: `H_S`, `L_Im = 0`, `Σ|λ|`; verdict sirkulan `NOT-SYMMETRIC-CIRCULANT` dengan witness |
| `A-2026-0054` | A | Audit: perturbasi bersifat sintetis; artefak hanya spektrum (tidak ada `build_arb_tau` di repo); tidak ada klaim lokasi nol/RH yang sah |

Bila hasil A6 berbeda dari ekspektasi, `T-2026-0069` harus ditulis dengan
verdict yang benar-benar terukur, dan perbedaan dicatat sebagai deviasi.

---

## 8. Urutan eksekusi yang mengikat

1. Commit **hanya** berkas ini:
   `reports/PREREG_CHRONO_RUNTIME_2026-10-30.md`, dengan pesan commit
   tersendiri. Push ke `origin main`.
2. Baru setelah push berhasil: tulis modul `msaf/chrono_runtime/`,
   `msaf/bridge/chrono_bridge.py`, dan test.
3. Jalankan A1–A9; perbaiki implementasi, bukan kriteria.
4. Hasilkan `reports/CHRONO_RIEMANN_INSIGHTS.json` dan
   `ledger/chrono_execution_ledger.jsonl` dari run nyata; lalu jalankan A10.
5. Tulis `reports/CHRONO_RUNTIME_2026-10-30.md` dengan angka verbatim.
6. Commit implementasi + artefak (satu tujuan), lalu commit registry
   `T-2026-0068`, `T-2026-0069`, `A-2026-0054` dengan hash.
7. Bila ada langkah yang gagal, catat sebagai deviasi di laporan dan ledger;
   jangan menurunkan kriteria dan jangan menaikkan klaim.

---

## 9. Amendment

Perubahan atas dokumen ini hanya sah bila:

- ditulis sebagai bagian **Amendment** bertanggal di berkas terpisah atau di
  akhir berkas ini tanpa menghapus isi yang sudah dikunci;
- menyebut alasan dan dampaknya terhadap A1–A10/F1–F15;
- di-commit sebelum implementasi yang terpengaruh.

```text
sha256LF <diisi setelah commit> reports/PREREG_CHRONO_RUNTIME_2026-10-30.md
```
