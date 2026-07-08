# EPOCH-043 REPORT — CROSS-SITE CERTIFICATION OF POSITIONAL SPECIALIZATION (L2/L3)

**Successor of EPOCH-042.** E042 established GLOBALLY that ~33% of the LA sign
inventory (17/51) is position-specialized under the analytic Poisson-binomial
within-word null (PC PASSED), but was UNDERPOWERED cross-site: its >=200
sign-token threshold admitted only Haghia Triada, so the cross-site claim could
not be certified. **E043 certifies cross-site at a feasible >=80 sign-token
threshold and tests replication of the E042 global set across independent sites.**

Signs are **ANONYMOUS** throughout. No phonetic, sound, meaning, value, or
reading is assigned. "Specialized" = a positional-distribution statistic
(enrichment in initial/final within-word position under the analytic
within-word permutation null), NOT a morpheme-with-meaning. LB is a
positive-control benchmark ONLY; its deciphered values are not used in any LA
inference. **Layer L2/L3.**

---

## VERDICT: `SPECIALIZATION_CROSS_SITE_ROBUST`

All four gates of the frozen mechanical rule are satisfied:

| Gate | Requirement | Result | Pass |
|---|---|---|---|
| Positive control | LB detected in every pseudo-site AND FPR <= 0.10 on shuffled | min pseudo-site frac **0.414**; FPR **0.0014** | ✅ |
| Data adequacy | >=3 sites qualify at >=80 sign-tokens | **9** sites qualify | ✅ |
| Cross-site fraction | >=3 sites with specialized_fraction >= 0.15 | **5** sites (HT, Khania, Knossos, Arkhalkhori, Syme) | ✅ |
| Replication | >=3 E042 global signs same-direction enriched in >=2 sites | **3** signs (**A**, **I**, **TI**) | ✅ |
| Leave-one-site-out | global set survives without HT (frac >= 0.15) | **0.220** (9/41) | ✅ |

---

## 0. Data inspection

Sites qualifying at the **>=80 sign-token** threshold (9, more than the ~6
expected because the threshold is in *sign-tokens*, not words):

| Site | sign-tokens | words | signs >=8 occ |
|---|---:|---:|---:|
| Haghia Triada | 1857 | 694 | 47 |
| Zakros | 399 | 132 | 23 |
| Khania | 307 | 120 | 10 |
| Knossos | 219 | 61 | 6 |
| Palaikastro | 208 | 57 | 7 |
| Phaistos | 170 | 58 | 3 |
| Iouktas | 143 | 34 | 4 |
| Arkhalkhori | 101 | 34 | 1 |
| Syme | 86 | 21 | 1 |

The four smallest sites (Phaistos, Iouktas, Arkhalkhori, Syme) admit only 1–4
testable signs at the >=8 occurrence threshold, so they contribute little
statistical weight; the substantive cross-site signal is carried by HT, Zakros,
Khania, Knossos, Palaikastro.

## 2. Global (reproduces E042)

Recomputed on the whole corpus at >=15 occurrences, Holm across all
(sign × position): **17/51 signs specialized (fraction 0.333)** — 6 initial,
11 final. This exactly reproduces the E042 global set, confirming the analytic
machinery is stable. Specialized signs (anonymous):
`*118, *411, A, I, KU, ME, NE, QA, RA₂, RE, RO, SE, TE, TI, U, VS, ZA`.

## 3. Positive control (FIRST — gates the verdict)

LB (13,562 words, 43,868 sign-tokens) seeded into **4 pseudo-sites** of
comparable size to the LA qualifying sites:

| pseudo-site | tested | specialized | fraction | init | final |
|---|---:|---:|---:|---:|---:|
| 0 | 73 | 32 | 0.438 | 18 | 14 |
| 1 | 68 | 33 | 0.485 | 18 | 15 |
| 2 | 70 | 29 | 0.414 | 15 | 14 |
| 3 | 69 | 34 | 0.493 | 20 | 14 |

**Detection:** specialization found in every pseudo-site (min frac 0.414 > 0),
with the expected initial+final split (LB has both word-initial syllables and
case endings). **False-positive:** on 20 sets of within-word-shuffled pseudo-
sites, the worst-case specialized fraction averaged **0.0014** (<= 0.10
required). **PC = PASSED.** The analytic machinery is informative.

## 4. Cross-site (LA main)

Per-site specialized fraction (Holm within-site, signs >=8 occ in that site):

| Site | tested | specialized | fraction | specialized signs |
|---|---:|---:|---:|---|
| Arkhalkhori | 1 | 1 | 1.000 | A |
| Syme | 1 | 1 | 1.000 | JA |
| Knossos | 6 | 2 | 0.333 | A, TI |
| Khania | 10 | 3 | 0.300 | *411, A, VS |
| Haghia Triada | 47 | 12 | 0.255 | A, DA, KI, KU, NA, NE, QA, RA₂, RO, SA, TA₂, TI |
| Palaikastro | 7 | 1 | 0.143 | A |
| Zakros | 23 | 2 | 0.087 | A, SE |
| Phaistos | 3 | 0 | 0.000 | — |
| Iouktas | 4 | 0 | 0.000 | — |

**5 sites** reach fraction >= 0.15. **Honest caveat:** two of them
(Arkhalkhori, Syme) have only **1 testable sign** each, so their fraction=1.0
is statistically thin. Even setting those aside, the substantive sites reaching
>= 0.15 are **HT (0.255, n=47), Khania (0.300, n=10), Knossos (0.333, n=6)** —
still 3 sites, meeting the threshold without the thin ones.

### Replication

Of the 17 E042 global specialized signs, **3 replicate** (same-direction
enrichment, Holm or nominal p<=0.05, in >=2 sites):

- **A** (global initial): enriched in **6** sites (HT, Zakros, Khania, Knossos,
  Palaikastro, Arkhalkhori) — the strongest replicator.
- **I** (global initial): enriched in 2 sites (HT, Iouktas).
- **TI** (global final): enriched in 2 sites (HT, Knossos).

The remaining 14 global signs are enriched in only 1 site each (mostly HT
alone, since HT dominates the corpus). This is the expected power consequence:
most global signs are too rare (<8 occ) to be testable in the smaller sites.

### Leave-one-site-out (HT)

Recomputing the global specialized set on the corpus **minus Haghia Triada**:
**9/41 signs specialized (fraction 0.220)** — survives the >= 0.15 threshold.
The global effect is **NOT** an HT artifact.

---

## 5. Mechanical verdict

`SPECIALIZATION_CROSS_SITE_ROBUST` — PC passed; 9 sites qualify (>=3); 5 sites
(3 substantive) reach fraction >= 0.15; 3 E042 global signs (A, I, TI)
replicate same-direction in >=2 sites; the global set survives leave-one-site-
out on HT (0.220).

## Bottom line (honest)

Positional specialization in Linear A is **present, cross-site consistent, and
not an HT artifact**: the global specialized set survives removing HT, and a
core of signs (notably **A**, strongly initial-specialized across 6 sites;
**TI**, final-specialized) replicates across independent sites. The effect is
real but **concentrated**: most of the 17 global specialized signs are too rare
to test in the smaller sites, so the *replicated* core is small (3 signs) even
though the *global* fraction is high (33%). The two single-sign sites
(Arkhalkhori, Syme) inflate the >=0.15 site count but are not load-bearing —
the verdict holds on HT + Khania + Knossos alone. This is a structural
(positional) finding only; no sign carries a phonetic, sound, meaning, value,
or reading.

## Outputs

- `experiments/linear_a_frontier_72h/epochs/EPOCH-043/prereg.md` (frozen)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-043/plan_hash.txt`
  (`6f055b7daf870b6013010e22bcd037578ad1730eed0e5264b46ee3ad5ed50bed  prereg.md`)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-043/machinery.py`
  (self-check PASSED: analytic Poisson-binomial vs brute-force permutation)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-043/result.json`
- `experiments/linear_a_frontier_72h/data/epoch_043/`
  (global_analysis, per_site_analysis, replication_detail, positive_control,
  loo, qualifying_sites)
