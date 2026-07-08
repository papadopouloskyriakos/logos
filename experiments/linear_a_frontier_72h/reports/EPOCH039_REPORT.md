# EPOCH-039 REPORT — Prefix Paradigm vs A-Only (Linear A frontier-72h)

**Question.** E038 found Linear A is word-INITIAL-concentrated (H_first < H_last; asymmetry
−0.223 bits; reverse-tail p = 0.0005), a prefixing-like distributional pattern, and E025
certified sign **A** as a productive word-initial marker. Is the initial concentration a
genuine **PREFIX PARADIGM** (a SET of productive word-initial marker signs), or is it driven
**ONLY** by A-?

**Layer / discipline.** Pure L2/L3 positional-entropy structure on ANONYMOUS sign ids. No
phonetics, sound, meaning, or reading. "prefix" = word-INITIAL positional enrichment (a
distributional statistic), NOT a grammatical morpheme with meaning. LB is a positive-control
benchmark ONLY. Prereg + plan_hash frozen before running; PC first; mechanical verdict from
the frozen rule.

---

## VERDICT: `PREFIX_PARADIGM_BEYOND_A`

The word-INITIAL concentration is **not** an A-only artifact. After excluding all A-initial
words, the asymmetry remains significantly initial-concentrated, and a Holm-corrected inventory
finds **5 word-initial-enriched signs besides A**. The positive control validates the
machinery.

---

## 1. Global result (LA, n = 1369 words, len ≥ 2)

| quantity | FULL (all words) | A-REMOVED (excl. A-initial) |
|---|---|---|
| n words | 1369 | 1214 (155 A-initial removed) |
| H_first (entropy, bits) | 5.5292 | 5.6605 |
| H_last (entropy, bits) | 5.7518 | 5.7670 |
| **Asymmetry (H_first − H_last)** | **−0.2227** | **−0.1065** |
| One-sided p (initial-concentration) | **0.0005** | **0.0295** |
| Initial-concentrated? | **yes** | **yes** |

**Bottom line (global):** removing every word that begins with A leaves a *smaller but still
significantly negative* asymmetry (−0.1065 bits, p = 0.0295). The initial concentration
SURVIVES A-removal — it is not driven solely by sign A.

## 2. Prefix inventory (Holm-corrected, signs with ≥ 15 occurrences)

51 signs tested; **6 Holm-significant word-initial-enriched signs** (Holm p = 0.0255 ≤ 0.05),
of which **5 are BESIDES A**:

| sign (ANONYMOUS) | initial-rate | Holm p | raw p | n_initial | n_contain |
|---|---|---|---|---|---|
| U | 0.6094 | 0.0255 | 0.0005 | 39 | 64 |
| KU | 0.6642 | 0.0255 | 0.0005 | 89 | 134 |
| **A** | 0.9064 | 0.0255 | 0.0005 | 155 | 171 |
| I | 0.5333 | 0.0255 | 0.0005 | 32 | 60 |
| QA | 0.7436 | 0.0255 | 0.0005 | 29 | 39 |
| *411 | 1.0000 | 0.0255 | 0.0005 | 15 | 15 |

Each of these signs begins a word far more often than the within-word permutation null predicts
(initial-rates 0.53–1.00). This is a **SET** of word-initial-enriched signs, not a single-sign
effect — the defining feature of a multi-sign prefix paradigm (distributionally).

## 3. Positive control (gates verdict) — PASSED

The machinery must DETECT a known multi-prefix paradigm and must NOT fire on structureless
(within-word-shuffled) data.

| PC quantity | value |
|---|---|
| PC verdict | **PASSED** |
| Planted prefixes | 4 distinct (PFX1–PFX4), attach-rate 0.55 |
| DETECT: asymmetry after removing ONE planted prefix | **−0.5372** (still initial-concentrated) |
| DETECT p | **0.0005** (multi-prefix paradigm detected ✓) |
| False-positive rate (20 within-word-shuffled sets) | **0.05** (≤ 0.10 ✓) |

The machinery correctly detects a multi-prefix paradigm (concentration survives removing one
planted prefix) and does not fire on shuffled words. **Machinery is informative; verdict
unlocked.**

## 4. Cross-site held-out (LA, A-removed, sites with ≥ 50 words)

6 testable sites (≥ 2 required by the frozen rule, so NOT underpowered).

| site | n | n_a_removed | asymmetry | p (init-conc.) | sig? |
|---|---|---|---|---|---|
| Haghia Triada | 694 | 653 | −0.2429 | 0.0005 | **yes** |
| Khania | 120 | 100 | +0.4739 | 0.9940 | no |
| Knossos | 61 | 51 | −0.4864 | 0.0115 | **yes** |
| Phaistos | 58 | 51 | −0.2521 | 0.1059 | no |
| Palaikastro | 57 | 47 | −0.0613 | 0.3713 | no |
| Zakros | 132 | 113 | +0.0936 | 0.7331 | no |

- **Sites where A-removed concentration is significant: 2 / 6** (Haghia Triada, Knossos) —
  meets the frozen ≥ 2 threshold.
- 4 of 6 sites have negative (initial-concentrated) asymmetry; Khania and Zakros reverse.
- **Leave-one-site-out (exclude Haghia Triada):** asymmetry = −0.0423, p = 0.2944 —
  direction-consistent but **non-significant** once the largest site is removed. The global
  A-removed signal is concentrated in Haghia Triada; this is reported honestly as a robustness
  caveat.

## 5. Mechanical verdict (frozen rule)

- PC passed ✓
- A-removed asymmetry significantly initial-concentrated globally (p ≤ 0.05)? **Yes**
  (−0.1065, p = 0.0295) ✓
- ≥ 2 non-A signs Holm-significant word-initial-enriched? **Yes** (5 besides A) ✓
- A-removed concentration holds in ≥ 2 sites? **Yes** (2 / 6) ✓
- ⇒ **`PREFIX_PARADIGM_BEYOND_A`**

All four conjunctive conditions of the frozen rule are satisfied.

## 6. Honest bottom line

Linear A's word-INITIAL concentration is a **genuine multi-sign prefix paradigm beyond sign A**,
not an A-only artifact. Three independent lines of evidence converge: (i) the asymmetry stays
significantly initial-concentrated after removing all A-initial words (p = 0.0295); (ii) a
Holm-corrected inventory identifies **5 word-initial-enriched signs besides A** (U, KU, I, QA,
*411), each beginning words far above the within-word permutation null; (iii) the A-removed
concentration is significant in 2 of 6 testable sites. The positive control validates the
machinery (multi-prefix detection + 0.05 false-positive rate).

**Caveats (reported honestly):**
- The global A-removed signal is concentrated in Haghia Triada — leave-one-site-out excluding
  it gives a direction-consistent but non-significant result (p = 0.2944). The cross-site
  threshold (≥ 2 sites) is met but not by a wide margin.
- "prefix paradigm" is a **distributional** observation: a SET of signs enriched at
  word-INITIAL position relative to a within-word permutation null. It is NOT a grammatical or
  meaning claim; signs carry no phonetic value, sound, meaning, or reading.
- Whether the 5 non-A initial-enriched signs form a coherent distributional class or are an
  arbitrary set of high-initial-frequency signs is left to successor epochs.

## Artifacts
- `experiments/linear_a_frontier_72h/epochs/EPOCH-039/prereg.md`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-039/plan_hash.txt`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-039/machinery.py` (self-check: `python3 machinery.py`)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-039/result.json`
- `experiments/linear_a_frontier_72h/data/epoch_039/` (global_summary, per_site_a_removed, positive_control, prefix_inventory CSVs)
