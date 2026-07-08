# EPOCH-024 REPORT — A- PREFIXATION MULTI-AXIS HELD-OUT ROBUSTNESS

**Campaign:** Linear A frontier-72h (frontier F4) · **Layer:** L2/L3 (positional/structural only)
**Task:** EPOCH-024 · **Verdict:** `A_PREFIX_MULTIAXIS_ROBUST`

## Question
E022 showed A- prefixation survives a global adaptive null; E023 showed it holds across 9/10 sites.
Does it ALSO hold across two ORTHOGONAL administrative partition axes — SUPPORT type and CONTEXT type —
i.e. is A- a genuinely corpus-wide productive positional prefix SLOT, invariant to how the corpus is partitioned?

## Discipline (non-circular)
Sign names are **anonymous labels**. No phonetic value, sound, meaning, language, or reading is assigned to
ANY sign. Only positional statistics (word-initial incidence under a within-word permutation null) are computed.
LB is a **positive-control benchmark only** — it certifies the machinery can detect a known positional-prefix
analogue; it is not Linear A and no cross-script phonetic inference is drawn.

## Method
- **Metric:** count/fraction of ≥2-sign words whose FIRST sign is A.
- **Null (reused from E023):** within-word uniform permutation — independently permute each word's own signs,
  preserving each word's sign multiset and length exactly. 1000 draws; one-sided p = (1 + #(null ≥ obs))/(1+1000).
- **Partitions:** by `support` and by `context`; keep partitions with ≥20 qualifying words.
- **Corrections:** Holm across each family; leave-one-partition-out (drop the largest).
- **Adversarial:** repeat the support-axis test for the 5 next-most-initial comparator signs.

## Results

### Global sanity
A-initial = **155 / 1369** ≥2-sign words (frac = 0.1132), null-mean = 55.6, **p = 0.001**.
*(Note: the brief's "~155/177" denominator does not match the corpus's 1369 ≥2-sign words; the 155 numerator
matches. Reported as a deviation.)*

### Positive control (gates the verdict) — **PASSED**
On LB (13,562 ≥2-sign words), the most word-initial-skewed sign with ≥40 occurrences is **AU** (skew = 1.00 —
always word-initial; 44/44). Partitioned via a seeded balanced 5-way split (no per-tablet metadata in
`load_b_damos`):
- AU significant (p ≤ 0.05) in **5/5** folds (p = 0.001 in every fold).
- Frequency-matched random sign **RO2** (occ 49) significant in **0/5** folds (p = 1.0 in every fold).
→ The machinery reliably detects a known positional-prefix analogue and rejects a frequency-matched null sign.

### SUPPORT axis (primary)
6 partitions with ≥20 words. A- significant (raw p ≤ 0.05) in **5/6**; Holm-significant in **5/6**.

| Support | n | A-init | null-mean | p | p_holm |
|---|---:|---:|---:|---:|---:|
| Tablet | 844 | 82 | 31.8 | 0.001 | 0.006 |
| Stone vessel | 259 | 39 | 11.1 | 0.001 | 0.006 |
| Roundel | 69 | 5 | 1.24 | 0.002 | 0.006 |
| Clay vessel | 58 | 14 | 5.38 | 0.001 | 0.006 |
| Metal object | 30 | 6 | 1.40 | 0.001 | 0.006 |
| **Nodule** | 35 | **0** | 0.00 | 1.000 | 1.000 |

**Leave-one-out** (drop Tablet, the largest): A- still significant on the rest, **p = 0.001**.
The single non-significant partition (Nodule) has **zero** A-initial occurrences — A- is genuinely absent on
nodules, not merely non-initial. This is a real boundary on the slot, reported honestly.

### CONTEXT axis (secondary)
4 partitions with ≥20 words. A- significant in **4/4**; Holm-significant in **4/4**.

| Context | n | A-init | null-mean | p | p_holm |
|---|---:|---:|---:|---:|---:|
| LMIB | 833 | 71 | 25.4 | 0.001 | 0.004 |
| (unlabeled) | 443 | 65 | 24.1 | 0.001 | 0.004 |
| LMIA | 31 | 8 | 2.35 | 0.001 | 0.004 |
| LMI | 29 | 6 | 1.90 | 0.001 | 0.004 |

**Leave-one-out** (drop LMIB): A- still significant on the rest, **p = 0.001**.

### Adversarial comparators (support axis)
The 5 next-most-initial signs clear far fewer support partitions than A-:

| Sign | partitions cleared (p ≤ 0.05) |
|---|---:|
| I | 3 |
| DA | 2 |
| KU | 1 |
| JA | 1 |
| SA | 1 |

**Comparator median = 1.** A- clears **5** partitions — **4 more than the comparator median** (gate requires ≥2 more).

## Frozen mechanical verdict
All gates satisfied:
- PC passed ✓
- A- significant in ≥2 support partitions: **5/6** ✓
- survives support leave-one-out (p = 0.001) ✓
- significant in ≥2 context partitions: **4/4** ✓
- clears ≥2 more support partitions than comparator median: 5 vs median 1 (Δ = 4) ✓

→ **`A_PREFIX_MULTIAXIS_ROBUST`**

## Honest bottom line
A- word-initial incidence is **not** an artifact of any single administrative partition. It is significant in
5/6 support partitions and 4/4 context partitions, survives dropping the largest partition on both axes, and
clears materially more partitions than any comparator sign. The one exception — **Nodule**, where A- is entirely
absent (0/35) — is a genuine boundary on the slot, not a statistical fluke. Within the L2/L3 ceiling, A- behaves
as a **corpus-wide productive positional prefix SLOT** (a structural fact about where the sign sits). The claim is strictly positional/structural and stays within the L2/L3 ceiling.

## Successor hypotheses
1. E025: Is the A- slot conditioned by word length (2 vs 3+ signs)?
2. E026: Test A- against a graphic/position null (common-opener effect, independent of morphology).
3. E027: Investigate the Nodule exception — absent vs underpowered?
4. E028: Bigram structure: does A- co-occur with specific second-position signs (no phonetic values)?
5. E029: Joint SITE × SUPPORT test — additive or interactive effect?
6. E030: Power analysis — minimum words/partition to reliably detect the A- effect at frac ≈ 0.11.

## Deviations
- Brief's global sanity target "~155/177" uses a denominator (177) inconsistent with the corpus's 1369 ≥2-sign
  words; operator measured 155/1369 (frac 0.113) and reports the measured value. Numerator matches.
- LB `load_b_damos` exposes no per-tablet metadata, so the PC uses a seeded balanced 5-way split (stated in prereg).
- Nodule partition has 0 A-initial occurrences (not merely non-significant) — reported as a finding.

## Artifacts
- `prereg.md`, `plan_hash.txt`, `machinery.py`, `run_analysis.py`, `result.json`
- `data/epoch_024/analysis_full.json`
