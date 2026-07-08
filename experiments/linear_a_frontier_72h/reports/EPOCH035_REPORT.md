# EPOCH-035 REPORT — TERMINAL TOTAL-SLOT (inscription-FINAL word-form over-representation)

**Campaign:** Linear A frontier-72h · **Epoch:** EPOCH-035 · **Layer:** L2/L3 (positional / document-structural ONLY)
**Verdict:** `TERMINAL_TOTAL_SLOT_SITE_LOCAL`
**Candidate (anonymous sign sequence):** `NI` — surfaced by the FROZEN selection rule (most inscription-FINAL occurrences among forms with total≥8 AND final≥5).

> **Non-circularity (hard):** word-forms are ANONYMOUS sign sequences — no phonetics, no sound, no
> meaning, no numeral arithmetic. "total-slot" = INSCRIPTION-FINAL POSITION only. The candidate was
> selected by a frozen rule committed in the prereg BEFORE any p-value was computed; the surfaced
> identifier is reported only as an anonymous sign sequence and the verdict does not depend on any
> assumed value of it. LB is a positive-control benchmark ONLY.

---

## 1. Question

Symmetric counterpart of E034 (A- class marks inscription-INITIAL / heading position). Is there a
recurring WORD-FORM over-represented in **inscription-FINAL position** (the LAST word token — the
mission-named "KU-RO terminal / total ledger slot"), and is it **ROBUST across independent SITES**?
Tested purely positionally and anonymously; the data surfaces the form.

## 2. Data & candidate selection (frozen rule)

- Corpus: `corpus/silver/inscriptions_structured.json` — 1341 inscriptions; **415 qualify** (≥2 word tokens).
- Word sequence of an inscription = `word` tokens in stream order.
- **CANDIDATE = word-form with the MOST inscription-FINAL occurrences, among forms with total≥8 AND final≥5.**

Top-10 inscription-FINAL word-forms (anonymous sign sequences):

| rank | form (anon) | final | total |
|---|---|---|---|
| 1 | **NI** | **22** | **71** |
| 2 | KU,RO | 12 | 36 |
| 3 | CYP | 12 | 48 |
| 4 | VIN | 10 | 42 |
| 5 | GRA | 10 | 61 |
| 6 | A | 7 | 19 |
| 7 | SI | 6 | 25 |
| 8 | KU | 5 | 17 |
| 9 | KI | 5 | 15 |
| 10 | I | 5 | 13 |

**Candidate surfaced: `NI`** (final=22, total=71).

## 3. Global result

| metric | value |
|---|---|
| final_count (observed) | 22 |
| total_count | 71 |
| **final_enrichment** | **0.310** |
| null_mean final-count (position permutation) | 14.69 |
| **one-sided p** | **0.017** ✅ significant |
| initial_rate (control) | 0.085 |

The candidate is inscription-FINAL at ~31% vs a position-permutation null of ~21% (14.69/71);
**p = 0.017**, correct direction. Its initial-position rate (0.085) is far below its final rate,
consistent with a FINAL-slot role, not an initial/heading role (the E034 axis).

## 4. Positive control (gates the verdict) — PASSED

LB benchmark via `load_b_damos` (DĀMOS; **NO site/inscription metadata → SEEDED pseudo-inscription
partition**, stated explicitly).

| arm | result |
|---|---|
| DETECT planted terminal bias | obs=1010 vs null_mean=205, **p=0.0**, correct direction ✅ |
| FALSE-POSITIVE (position-randomized, exact H0) | rejection rate **0.067** (≤0.10) over 30 sets ✅ |

**PC PASSED** → machinery is informative; the global signal is not a calibration artifact.

## 5. Cross-site held-out — NOT robust

**Candidate metric (≥10 `NI` occurrences per site):** only **2 sites** testable, **0 significant**.

| site | total | final | null_mean | p | sig |
|---|---|---|---|---|---|
| Haghia Triada | 40 | 10 | 5.95 | 0.055 | ✗ |
| Khania | 23 | 8 | 6.29 | 0.266 | ✗ |

**Aggregate final-slot CONCENTRATION fallback** (≥15 qualifying inscriptions; top-form share of
final slots vs position-permutation null): **5 sites testable, 1 significant** (Haghia Triada only).

| site | n_insc | top_form | top_share | null_mean | p | sig |
|---|---|---|---|---|---|---|
| Haghia Triada | 181 | KU,RO | 0.066 | 0.041 | 0.015 | ✓ |
| Khania | 67 | CYP | 0.149 | 0.123 | 0.212 | ✗ |
| Zakros | 34 | GRA | 0.059 | 0.061 | 0.911 | ✗ |
| Knossos | 24 | E | 0.083 | 0.068 | 0.585 | ✗ |
| Phaistos | 22 | NI | 0.091 | 0.087 | 0.774 | ✗ |

**Leave-one-site-out** (exclude largest site, Haghia Triada): obs_final=12, null_mean=8.81,
**p = 0.132 → COLLAPSES** (no longer significant).

## 6. Frozen mechanical verdict

| condition | status |
|---|---|
| PC passed | ✅ |
| global candidate final-enrichment p ≤ 0.05 | ✅ (p=0.017) |
| ≥2 sites significant same direction | ❌ (0 candidate sites; 1 aggregate site) |
| survives leave-one-site-out | ❌ (p=0.132) |

→ **`TERMINAL_TOTAL_SLOT_SITE_LOCAL`** (global significant BUT <2 sites AND collapses under
leave-one-site-out).

## 7. Honest bottom line

There IS a global inscription-FINAL over-representation of the anonymous sign sequence `NI`
(p=0.017, final-rate 0.31 vs initial-rate 0.085), and the machinery is certified sound (PC passed).
**But it is NOT a pan-Cretan document-structural regularity**: it is concentrated in / driven by
the largest site (Haghia Triada). With Haghia Triada removed the signal vanishes (p=0.132), and no
other site individually replicates it. This is a **site-local** terminal-slot tendency, not a
cross-site robust "total-slot" rule. The candidate is an ANONYMOUS sign sequence; "total-slot"
means FINAL POSITION only — no semantic reading is claimed or implied.

## 8. Outputs (PATH CONTRACT)

- `experiments/linear_a_frontier_72h/epochs/EPOCH-035/prereg.md`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-035/plan_hash.txt`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-035/machinery.py`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-035/result.json`
- `experiments/linear_a_frontier_72h/reports/EPOCH035_REPORT.md`
- `experiments/linear_a_frontier_72h/data/epoch_035/raw_stats.json`
