# Pra-registrasi Paket 7 — pilot L5 finite core: perbandingan integral–deret untuk `f_k(x)=x^{-(k+1)}`

**Tanggal:** 2026-10-20
**Status:** scope DIKUNCI sebelum implementasi (disiplin paket 4–7)
**Berkas target:** `formal_bridge/IntegralComparison.v` (baru; standalone)
**Registry yang direncanakan:** `A-2026-0012`

## 1. Latar

Kit L5 (`reports/BRIDGE_PROTOCOL_2026-10-19.md`) adalah perbandingan
integral untuk `f` positif menurun:

```text
int_{N+1}^inf f <= sum_{n>N} f(n) <= int_N^inf f
```

Integral tak-hingga di Coq memerlukan limit integral dan belum menjadi
target pilot. Paket 7 mengunci **finite core** untuk instance pangkat
bulat `f_k(x) = 1/x^{k+1}` (`k >= 1`), di mana integral finite tersedia
di stdlib (`Coq.Reals.RiemannInt`). Ini gerbang teknis sebelum L5 umum,
L2 eksponen real, L3, dan L4.

## 2. Pernyataan yang akan dibuktikan

Definisi (semua di `IntegralComparison.v`):

```coq
Definition fk (k : nat) (x : R) : R := / (x ^ S k).

Fixpoint sum_upto (g : nat -> R) (M : nat) : R :=
  match M with
  | 0%nat => 0
  | S m => sum_upto g m + g m
  end.

(* unit_val k N i HN = RiemannInt dari fk k pada [INR (N+i), INR (N+i+1)] *)
(* whole_val k N M HN = RiemannInt dari fk k pada [INR N, INR (N+M)] *)
```

Hasil yang dikunci:

1. `sum_upto_le` — monotonisitas jumlah finite.
2. `continuity_pt_fk` — `0 < x -> continuity_pt (fk k) x`.
3. `integral_unit_upper` — untuk `n >= 1`:
   `RiemannInt (unit ...) <= fk k (INR n)`.
4. `integral_unit_lower` — untuk `n >= 1`:
   `fk k (INR (n+1)) <= RiemannInt (unit ...)`.
5. `whole_val_eq_sum` — additivity finite:
   `whole_val k N M HN = sum_upto (fun i => unit_val k N i HN) M`.
6. **Teorema utama** `integral_comparison_power_finite` — untuk
   `k >= 1`, `N >= 1`:

```coq
whole_val k N M HN
  <= sum_upto (fun i => fk k (INR (N + i))) M /\
sum_upto (fun i => fk k (INR (N + i + 1))) M
  <= whole_val k N M HN.
```

Ini persis L5 finite core untuk `f_k`: integral pada `[N, N+M]` diapit
oleh jumlah titik-kiri dan jumlah titik-kanan.

## 3. Metode yang dikunci

- Hanya stdlib: `Coq.Reals.Reals`, `Coq.Reals.RiemannInt`,
  `Coq.Reals.Ranalysis1`, `Coq.Reals.Rfunctions`, `Coq.micromega.Lia`,
  `Coq.micromega.Lra`.
- Integrabilitas: `continuity_implies_RiemannInt` + kontinuitas `fk`
  (`continuity_pt_inv` + `derivable_pt_pow` + `derivable_continuous_pt`).
- Per-unit: `RiemannInt_P19` (monotonisitas) dengan `fct_cte`, nilai
  konstanta via `RiemannInt_P15`, side condition pangkat via
  `pow_incr` / `pow_lt` / `Rinv_le_contravar`.
- Additivity: `RiemannInt_P25` (Chasles) + `RiemannInt_P5`
  (proof irrelevance untuk argumen integrabilitas).
- **Tanpa** `FTC_Riemann`/`C1_fun`, **tanpa** `Rpower` (eksponen real),
  **tanpa** integral tak-hingga, **tanpa** asumsi proyek.
- Berkas **standalone**: tidak mengimpor `PseriesL2`, `GeometricBridge`,
  atau `GeometricLimit`.

## 4. Kriteria sukses

- `coqc` exit 0; `coqchk` exit 0 "Modules were successfully checked";
  semua hasil muncul di keluaran kernel; receipt deterministik (dua
  capture byte-identik).
- `Print Assumptions` hanya aksioma stdlib `Coq.Reals`. **Jumlah persis
  dicatat**; ekspektasi realistis adalah **tiga** (`sig_forall_dec`,
  `functional_extensionality_dep`, `sig_not_dec` — karena `RiemannInt`
  memakai kelengkapan R). Tidak ada aksioma proyek.
- Guard statis + mutasi negatif; registry `A-2026-0012`; HANDOFF;
  CI hijau (guard statis; CI tidak punya Coq).

## 5. Kriteria gagal (dicatat, tidak disembunyikan)

- Bila `RiemannInt` ternyata tidak cukup (mis. butuh lemma yang tidak
  ada atau memaksa aksioma di luar stdlib `Coq.Reals`), scope hanya
  boleh dipersempit lewat **addendum pra-registrasi baru**; hasil parsial
  dicatat sebagai PARTIAL/negatif, bukan diklaim selesai.
- Tidak ada klaim "L5 selesai". Yang disertifikasi hanya finite core
  instance pangkat bulat.

## 6. Batas

- **Finite core saja**: integral tak-hingga dan langkah limit **tidak**
  dibuktikan.
- Hanya `f_k(x)=x^{-(k+1)}`, `k >= 1`; bukan `f` umum, bukan L2 real
  `p > 1`, bukan L3/L4.
- **Bukan** penutupan `[J]` periodic-box `A-2026-0007` (tetap OPEN).
- Tidak menyentuh zeta/Weil/RH/P≠NP; tidak ada klaim fisik; bukan peer
  review.
