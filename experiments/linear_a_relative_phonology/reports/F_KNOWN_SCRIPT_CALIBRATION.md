# F2 — Known-Script Calibration of Cross-Script Evidence

**Constitution v2.2 · Articles VII (search receipt), VIII (effective_n), IX (info budget), XII
(no grading a target by the rule that created it), XV (transfer licences), XVIII (assumptions).**
Seed 20260708. Script: `scripts/f2_known_script_calibration.py`. Data: `data/F2_calibration.json`.

## Why this task exists

WP-A refuted the Foundry position→C/V symmetry-break; the **C3 substitution channel** (consonant-held
axis) is now the campaign's load-bearing surviving relative-structure candidate. The natural next lean
is **cross-script** evidence — the field's assumption that a Linear A sign which is *shape-homomorphic*
with a Linear B sign may borrow the Linear B value. Before that lean, F2 asks the calibration question
on **deciphered** scripts, where the answer is known: **how much is each class of cross-script evidence
actually worth?** Four evidence types, each with an explicit null.

**Non-circular discipline (Art. XII):** known phonetic values are used ONLY as (a) the identity of the
descent hypothesis under test and (b) grading labels. No value is ever a model input feature — every
profile feature is a pure distributional statistic over sign identities.

**Data resource discovered:** the Linear A corpus tokens are already in the scholarly LB-value
transliteration for *homomorphic* signs (`QE`, `RA2`, `KI`, …) and stay as `*NNN` for Linear-A-only
signs. That value-bearing-vs-`*NNN` split **is** the machine-readable descent relation. Value inventories
for Linear B (60 canonical CV cells) and the Cypriot Syllabary (55) come from Unicode sign names — two
independently-deciphered Greek syllabaries with a common Aegean ancestry and an ~800-yr gap.

**Scope limit (stated up front):** raw glyph *geometry* for the known pairs is only present as scanned
PDFs (Salgarella 2020, Steele & Meissner 2017) — not machine-readable here. F2 therefore calibrates
**descent** (the scholarly homomorphy relation, encoded in the joint AB/value numbering) and **function**
(distributional profiles), **not** independent pixel-level shape. This is the honest boundary of what
the in-repo data supports.

---

## Q1 — Relatedness/descent → value continuity (Linear B ↔ Cypriot, both deciphered)

Overlap of the canonical C×V value grids of two related deciphered Greek syllabaries, against a null of
two independent random syllabaries of the same sizes drawn from the attested 15-onset × 5-vowel space
(75 cells).

| quantity | value |
|---|---|
| LB canonical cells / Cypriot cells / value space | 60 / 55 / 75 |
| shared cells | 48 |
| observed Jaccard | **0.716** |
| Cypriot grid covered by LB | 0.873 |
| null Jaccard mean (20 000 draws) | 0.620 |
| **lift over null** | **1.155×** |
| p(Jaccard ≥ obs) | **0.0139** |

**Read:** the shared value grid is significant (p≈0.014) but the **lift is small (1.15×)**. Because the
Greek CV grid is tiny and nearly saturated, two *random* syllabaries of this size already overlap ~62%.
**Calibration lesson: value-inventory overlap between two CV Greek syllabaries is largely forced by the
shared phonological grid, so it is weak evidence of relatedness on its own.** Do not treat "the value
inventories overlap" as strong cross-script support.

## Q2 — Descent (homomorphy) → functional continuity (Linear A ↔ Linear B) — LOAD-BEARING

For the **51 value-bearing signs shared by LA-usage and LB-usage** (count ≥ 8 in each), the 7-feature
distributional profile is computed *independently within each script* and standardized. Two tests:

**(a) Matched-identity concordance vs a derangement null** (each sign re-paired to a *different* LB sign):

| quantity | value |
|---|---|
| n shared homomorphic signs | 51 |
| observed matched-profile cosine | **0.259** |
| null shuffled cosine mean / p95 | 0.018 / 0.135 |
| **p(match ≥ null)** | **0.000** (0/4000) |

**(b) Cross-script retrieval** — rank each LA sign's true LB twin by profile cosine:

| quantity | value | chance |
|---|---|---|
| top-1 accuracy | **0.059** | 0.020 |
| MRR | **0.164** | 0.089 |

**Read:** shape-homomorphic descent **does** carry real cross-script functional continuity — in
aggregate the effect is unmistakable (p = 0, cosine 14× the null mean). **But per-sign it is weak:**
you recover the correct twin at top-1 only 5.9% of the time (~3× chance) and MRR ~1.8× chance.
**Calibration lesson: cross-script homomorphy is worth a genuine but modest prior — enough to say
"these signs behave alike," nowhere near enough to *pin an individual value* from distribution alone.**
This is the quantitative ceiling on any LA←LB value-transfer that leans on functional similarity.

## Q3 — Function → correspondence lift (within Linear B, known values)

Within Linear B (59 signs, count ≥ 20), does the full distributional **profile** beat a **frequency-only**
baseline at recovering the value axes? Metric: AUC over all sign pairs; permutation null on the *lift*
(1000 label shuffles).

| axis | AUC function | AUC freq-only | **lift** | null p95 | **p(lift ≥ null)** |
|---|---|---|---|---|---|
| same **vowel** | 0.550 | 0.544 | +0.006 | 0.034 | **0.365 (NULL)** |
| same **consonant** | 0.594 | 0.541 | +0.053 | 0.051 | **0.045** |

**Read:** function adds essentially nothing on the **vowel** axis (lift +0.006, p=0.37) and a small,
marginally-significant amount on the **consonant** axis (lift +0.053, p=0.045). This **converges with
C3**: the surviving relative-structure signal lives on the *consonant-held* axis, not the vowel axis.
**Calibration lesson: "function improves correspondence" is true only weakly and only for the consonant
dimension; it is not a vowel-resolving instrument.**

## Q4 — Chronology → false-match reduction (Linear B → Cypriot, ~800-yr gap)

Naive (chronology-blind) matching maps every LB cell to a same-value Cypriot cell; cells with **no**
Cypriot counterpart are forced false/empty matches.

| quantity | value |
|---|---|
| LB cells / Cypriot cells | 60 / 55 |
| survived into Cypriot | 48 |
| **lost (forced false matches)** | **12** |
| lost cells | DA DE DI DO DU · QA QE QI QO · JE JU · ZE |
| lost by onset series | **D:5, Q:4, J:2, Z:1** |
| naive false-match rate | **0.200** |
| chronology-aware false-match rate | **0.000** |
| null value-neutral false-match rate | 0.267 |

**Read:** the 12 lost cells are **exactly the known historical Greek mergers/losses** — the labiovelar
Q-series (disappeared by the 1st millennium), the D-series absorbed by the Cypriot dental T-series, the
J-glide and one Z-cell. Restricting candidates to the surviving grid (chronology-aware) removes all 12
forced false matches (0.20 → 0.00). Observed attrition (0.20) is *below* the value-neutral null (0.267),
i.e. descent preserved *more* than chance. **Calibration lesson: chronological distance imposes a real,
mechanistically-interpretable ~20% false-match load, and chronology-aware candidate restriction removes
it — a genuinely useful filter, validated by recovering documented Greek sound-change history.**

---

## Synthesis — what cross-script evidence is worth (the prior for the campaign)

| evidence type | test | effect | significance | verdict |
|---|---|---|---|---|
| **value-grid overlap** (Q1) | LB↔Cypriot Jaccard | **1.15×** | p=0.014 | weak — near-forced by the small CV grid |
| **descent/homomorphy → function** (Q2) | LA↔LB matched cosine | 0.259 vs 0.018 | **p≈0** | real in aggregate, **weak per-sign** (top-1 6%) |
| **function → correspondence** (Q3) | LB profile vs freq | +0.05 (cons only) | p=0.045 | weak, consonant-axis only; vowel axis NULL |
| **chronology → false-match cut** (Q4) | LB→Cypriot grid | 12 removed, 0.20→0.00 | below neutral null | **useful, mechanistically valid** |

**Bottom line for the relative-phonology campaign.** Cross-script evidence is **not free power**:

1. **Value-inventory overlap is near-worthless** as a standalone signal (Q1) — the CV grid is too small.
2. **Homomorphy carries a genuine but modest functional prior** (Q2, p≈0) — it justifies treating a
   homomorphic LA sign as *behaviourally like* its LB twin, but the per-sign retrieval ceiling (~6%
   top-1) means distribution **cannot pin an individual value**. Any LA←LB transfer inherits this ceiling.
3. **Function helps only on the consonant axis** (Q3) — consistent with C3's consonant-held survivor;
   the vowel axis gets no lift, so cross-script function evidence is not a vowel instrument.
4. **Chronology is a real, cheap filter** (Q4) — worth applying, and its validity is confirmed by its
   recovery of documented Greek mergers.

None of this earns a SEMANTIC/PHONETIC transfer licence (Art. XV; still NOT_AUTHORIZED). F2's role is to
set honest **priors**: cross-script shape/descent/function evidence is worth a modest aggregate nudge on
the consonant axis under a chronology filter — **not** a per-sign value oracle. The load-bearing C3
substitution channel must still stand on its own held-out audit; cross-script evidence can corroborate
its *consonant-axis* direction but cannot, on this calibration, decide values.

**Status: COMPLETE.** All four numbers are measured (not described), reproducible from
`scripts/f2_known_script_calibration.py` at seed 20260708.
