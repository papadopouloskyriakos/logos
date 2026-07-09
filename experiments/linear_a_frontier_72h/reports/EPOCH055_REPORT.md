# EPOCH-055 REPORT — Numeral Magnitude (Accounting Scale) by Document Class

**Campaign:** Linear A frontier-72h · **Epoch:** EPOCH-055 · **Layer:** L2/L3
**Verdict (mechanical, frozen rule):** `SCALE_UNDERPOWERED`
**PC:** PASSED (detect p=2.1e-12, false-pos rate=0.04)

---

## 1. Question (distinct from E028 / E045)

Do document classes (`support`) differ in the **MAGNITUDE** of their numerals — do tablets record
**larger quantities** than roundels/vessels — and does that difference **survive controlling for SITE**?

- Distinct from **E028** (word/sign length): this is numeral magnitude, not length.
- Distinct from **E045** (numeral density): this is the **scale** of quantities, not their frequency.

**Non-circular discipline:** integer magnitudes `v` only; L2/L3 only; no sign values, no readings,
no phonetics, no semantics. Prereg + plan_hash frozen before running; PC first; mechanical verdict.

## 2. Data

`corpus/silver/inscriptions_structured.json` — `num` tokens carry integer `v`; each inscription has
`support` and `site`. Each numeral assigned its inscription's support+site. `v>=1`. Support classes
with `>=30` numerals kept.

## 3. Per-support magnitudes (n>=30 kept)

| Support | n numerals | median | mean | max |
|---|---:|---:|---:|---:|
| Tablet | 1099 | 5 | 28.66 | 3000 |
| Stone vessel | 127 | 4 | 14.87 | 180 |

All other supports (Nodule, Roundel, Clay vessel, Metal object, …) carry <30 numerals total and were
excluded by the frozen threshold.

## 4. Support × Site table (numeral counts; cells ≥15)

| Site | Tablet | Stone vessel |
|---|---:|---:|
| Haghia Triada | 829 | 0 |
| Khania | 121 | 0 |
| Zakros | 0 | 126 |
| Phaistos | 33 | 0 |
| Arkhalkhori | 33 | 0 |
| Tylissos | 31 | 0 |

**Key structural fact:** Stone-vessel numerals are concentrated **entirely at Zakros** (126 of 127);
Tablet numerals occur at Haghia Triada, Khania, Phaistos, Arkhalkhori, Tylissos. **No site contains
both support classes** with ≥15 numerals each.

## 5. Positive Control (run FIRST; gates verdict)

- **DETECT:** planted magnitude-scale difference (lognormal, ~3× scale shift) → p = 2.1e-12 (≤0.05). ✓
- **FALSE-POSITIVE:** two draws from the same distribution, 25 splits → rejection rate = 0.04 (≤0.10). ✓
- **PC verdict: PASSED.** Machinery is calibrated.

## 6. Global Kruskal-Wallis (rank-based; heavy-tailed magnitudes)

Across the 2 qualifying supports on numeral magnitude:
**H = 0.0284, p = 0.866, n_supports = 2.**

No global magnitude-scale difference between Tablet and Stone vessel (medians 5 vs 4).

## 7. LA MAIN — Site-controlled test

Requires sites with ≥2 support classes each ≥15 numerals.
**Testable sites = 0.** The within-site support-magnitude effect cannot be computed: the two support
classes are geographically segregated (Stone vessel only at Zakros; Tablet only at HT/Khania/etc.).

## 8. Frozen mechanical verdict

Precedence (frozen): PC fail → MACHINERY_UNINFORMATIVE; else `<2 testable sites` → SCALE_UNDERPOWERED;
else global p>0.05 → NO_DOCCLASS_SCALE_DIFFERENCE; else `<2 sig sites same direction` →
ACCOUNTING_SCALE_SITE_CONFOUNDED; else ACCOUNTING_SCALE_DOCCLASS_ROBUST.

- PC: PASSED ✓
- Testable sites: 0 (< 2) → **SCALE_UNDERPOWERED**

(Note: the global Kruskal p=0.866 would independently point to NO_DOCCLASS_SCALE_DIFFERENCE, but the
frozen rule places the underpowered/site-untestable condition ahead, because the site-controlled test
is the only way to separate a docclass effect from a site confound — and it cannot be run here.)

## 9. Honest bottom line

**The corpus cannot answer the docclass-magnitude question at the site-controlled level.** Only two
support classes carry enough numerals (Tablet, Stone vessel), and they never co-occur at any site
with adequate sample size — Stone-vessel numerals live only at Zakros, Tablet numerals live at
Haghia Triada and elsewhere. So any raw Tablet-vs-Stone-vessel magnitude contrast is **confounded
with site** and cannot be decomposed. The global 2-class comparison shows no difference (medians
5 vs 4, p=0.866), but that is between geographically disjoint groups and is therefore uninterpretable
as a docclass effect. **Verdict: SCALE_UNDERPOWERED** — the question needs either a lower per-class
threshold (admitting more supports) or a within-Tablet across-site analysis (the only class with
multiple adequately-sampled sites).

## 10. Outputs

- `experiments/linear_a_frontier_72h/epochs/EPOCH-055/prereg.md`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-055/plan_hash.txt`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-055/machinery.py` (with `__main__` self-check)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-055/result.json`
- `experiments/linear_a_frontier_72h/data/epoch_055/magnitudes.json`
- `experiments/linear_a_frontier_72h/data/epoch_055/support_site_table.json`
