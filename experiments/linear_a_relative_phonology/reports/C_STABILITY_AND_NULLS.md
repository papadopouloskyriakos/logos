# C5 — Stability & Nulls of the Linear A Substitution Graph

**Task C5 (stability half).** Subject the C4 Linear A sign-substitution graph — clean, non-allographic
sign edges licensed by ≥1 **long** (≥3-sign) frame; **strong** edges = ≥2 long frames; `REL_CLASS`es =
connected components of the strong graph — to bootstrap stability, site-holdout, segmentation
sensitivity, corpus-encoding sensitivity, damage exclusion, and formula-family exclusion.

- Engine: `experiments/linear_a_relative_phonology/scripts/c5_stability_infogain.py`
- Data: `experiments/linear_a_relative_phonology/data/C5_stability.json`
- Seed 20260708, deterministic, pure stdlib + audited C1/C3/C4 primitives. All counts script-generated
  (Inv. 12). **Non-circular** (Art. XII): every rebuild consumes sign identity + frame membership +
  word-final position only; GORILA/LB (C,V) values grade the deflation afterward, never as an input.

## Baseline (what is under audit)

3,147 GORILA word tokens → 1,165 types (984 length ≥2), **57 clean syllabogram signs** present in
length-≥2 words. Clean non-allographic long-frame sign edges: **130**. Strong edges (≥2 long frames):
**12**. `REL_CLASS`es: **5** — `{A,DA,JA,KA,MI,RU,SI,TA} {KU,MA,SA} {RA,RE} {PA,TE} {KI,WA}`. (C4
already found **none** of these earns the consonant-held signature; the within-graph word-final null was
beaten by no class, best p = 0.67.) C5 asks whether even the *anonymous relative structure* is stable.

## Verdict table (6 stress tests)

| test | what it perturbs | strong-edge survival | verdict |
|---|---|---|---|
| **1 bootstrap** | resample documents w/ replacement (×500) | mean recurrence **0.279**; 1/12 edges recur ≥50%, 0/12 ≥90% | **FRAGILE** |
| **2 site-holdout** | leave-one-site-out (52 sites) | 51 minor sites: ≥48/52 survive; **Haghia Triada holdout: 12 → 3** | **SEVERE dominant-site dependency** |
| **3 segmentation** | GORILA word → B1 alt. segmentations | ENTRY 0/12, FORMULA 0/12, PROB-BOUNDARY 0/12, ROW 1/12 | **FRAGILE** |
| **4 encoding** | collapse allographs to base sign | **12/12** preserved (strong Jaccard 0.71) | ROBUST |
| **5 damage excl.** | drop 212 types with a `*NNN`/measure sign | **12/12** survive | ROBUST |
| **6 formula-family** | remove the 361-form ledger paradigm | **12/12** survive outside the giant component | ROBUST |

The graph is **robust to nuisance choices** (allograph encoding, damaged signs, the single dominant
ledger paradigm) but **fragile to the two tests that gate generalization** — resampling the documents
and re-segmenting the corpus — and it is **dominated by one site**.

## 1. Bootstrap (document resample, ×500)

Each strong edge rests on only **2–3 distinct long frames**, i.e. a handful of documents; a bootstrap
that drops ~37% of documents knocks most edges below the ≥2-frame threshold.

- Mean strong-edge recurrence **0.279**; only **1/12** edges recur in ≥50% of resamples
  (`DA/RU` at 0.57), **0/12** at ≥90%.
- Class co-membership: of 34 baseline co-classed sign pairs, mean recurrence **0.143**; only **1**
  pair recurs ≥50%.
- ΔEqClasses (if-true information content, see companion report) collapses from the point estimate
  **12** to a bootstrap mean **3.3**, 95% CI **[1, 7]** — i.e. most of the apparent structure is a
  small-sample artifact.

Strong-edge recurrence (with the FLAGGED benchmark grade — grades only, earns no licence):

| edge | recurrence | long-frames | benchmark |
|---|--:|--:|---|
| DA/RU | 0.57 | 3 | cross |
| A/JA | 0.44 | 3 | same_vowel |
| A/DA | 0.42 | 3 | same_vowel |
| PA/TE | 0.26 | 2 | cross |
| RU/TA | 0.26 | 2 | cross |
| KI/WA | 0.24 | 2 | cross |
| KU/MA | 0.23 | 2 | cross |
| KU/SA | 0.22 | 2 | cross |
| A/SI | 0.19 | 2 | cross |
| A/MI | 0.19 | 2 | cross |
| RA/RE | 0.18 | 2 | same_consonant |
| A/KA | 0.15 | 2 | same_vowel |

## 2. Site-holdout (leave-one-site-out, 52 sites)

The unweighted LOSO mean survival (0.955) is **misleading**: 51 of 52 sites are tiny, so removing them
changes nothing. The only load-bearing holdout is **Haghia Triada** (845 docs, ~60% of word tokens):
removing it leaves **3 of 12** strong edges. Those three survivors are exactly the **word-initial
`A-` alternations** — `A/JA, A/KA, A/MI` — which C4 already flagged as the *opposite* of the calibrated
word-final consonant-held signature. Every consonant-slot-looking edge (`DA/RU, KU/SA, KU/MA, RA/RE,
PA/TE, RU/TA, A/DA, A/SI, KI/WA`) is a **Haghia Triada artifact**. Second-worst holdout (Phaistos, 48
docs) leaves 8/12.

## 3. Segmentation sensitivity

The 12 strong edges are an artifact of the **GORILA word** segmentation and do not survive the B1
alternatives:

| segmentation | units | clean edges | strong edges | clean-edge Jaccard | baseline strong recovered |
|---|--:|--:|--:|--:|--:|
| SEG_GORILA_WORD (baseline) | 3,147 | 130 | 12 | 1.00 | 12/12 |
| SEG_ROW | 2,697 | 82 | 5 | 0.51 | **1/12** |
| SEG_FORMULA | 1,642 | 27 | 0 | 0.15 | 0/12 |
| SEG_ENTRY | 1,068 | 17 | 0 | 0.12 | 0/12 |
| SEG_PROBABILISTIC_BOUNDARY | 3,526 | 33 | 0 | 0.04 | **0/12** |

Under the unsupervised branching-entropy segmentation — the only representation that did **not** ingest
the GORILA word boundaries — clean-edge overlap with the baseline is **0.04** and no strong edge
survives. The relative structure is entangled with the disputed segmentation lineage.

## 4. Encoding sensitivity (allograph collapse) — ROBUST

Collapsing numbered/lettered allographs to their base sign (RA/RA2→RA, *21F/*21M→*21) yields 144 clean
/ 17 strong edges; strong-edge Jaccard vs the remapped baseline **0.71**, and **12/12** baseline strong
edges preserved. Encoding choice does not manufacture or destroy the strong edges.

## 5. Damage exclusion — ROBUST

Dropping all **212** word types containing a `*NNN`/measure sign (1,165→953 types) leaves **12/12**
strong edges intact (0 lost). The strong edges are not driven by unidentified/damaged signs.

## 6. Formula-family exclusion — ROBUST

Removing the single largest substitution component (the **361-form** `{KU,SA,KI,A,…}-RO/-RA₂`
deficit/total ledger paradigm) still leaves **12/12** strong sign-edges — the long frames that license
them are distributed beyond that one paradigm. The signal is not solely the giant ledger family.

## Reading

The Linear A substitution graph encodes **real relative structure of one specific corpus rendering** —
it is invariant to allograph encoding, damage, and the dominant paradigm. But it **does not generalize**:
its edges rest on 2–3 documents each (bootstrap-fragile), collapse under any re-segmentation that does
not reuse the GORILA word boundaries, and outside Haghia Triada only the word-initial `A-` alternation
(the anti-signature) survives. This is consistent with the C4 finding that no `REL_CLASS` beats the
word-final null. **Status: RELATIVE_STRUCTURE_PRESENT_BUT_NON_GENERALIZING** — no basis, at this corpus
scale, for a "not value-blind" claim to rest on the substitution channel.
