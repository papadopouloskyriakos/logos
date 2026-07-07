# END-TO-END ADAPTIVE NULL — SPECIFICATION (frozen before running)

**Campaign:** Di Mino `*301=/na/` exact audit · **Constitution** v2.2 · **Seed** 20260708
**Prereg:** `DI_MINO_EXACT_CLAIM_V1` (sha 8b098a4c) · **Binding:** `reports/VERDICT_FRAMING_CONSTRAINTS.md`
**Generator:** `scripts/end_to_end_null.py` → `data/results/end_to_end_null.json`

## 0. Purpose (mandate §XVII)

Measure the **whole-pipeline** false-positive rate, not a single trial. The published Di Mino chain is
the output of an **adaptive search** with many free choices. The null MUST reproduce *every* adaptive
choice so that the reported FP rate is:

> P( a null run, given the SAME search freedoms, manufactures a match at least as strong as the observed
> `/na/ → N-W-Y → "dwell" → Semitic` chain on the combined preregistered statistic ).

If the observed chain is **indistinguishable** from this null → `NULL_PUBLISHED` for the lexical/gloss legs.
Because the positive controls PASSED (pipeline demonstrably recovers a planted value, PC3 rank 1/113), a
null-indistinguishable observed result is a **genuine negative**, not a dead detector.

## 1. The observed chain (what the null must match or beat)

The reading's ONLY novel free parameter is `*301=/na/`; the other five signs are literature values.
Achieved profile of the observed chain, from the completed family results:

| Leg | Observed outcome | Source |
|-----|------------------|--------|
| VALUE · S_morph (primary held-out) | **invariant under relabelling** — 0.2738 for /na/ *and* every other value | `301_value_sweep.json` |
| VALUE · S_lex | /na/ **rank 21/65**, 49th pctile, **below** Packard null mean (0.667 vs 0.752) | `301_value_sweep.json` |
| VALUE · S_phono | /na/ rank 1/65 (phonotactic only; not lexical evidence) | `301_value_sweep.json` |
| ROOT existence (n-w-y / n-w-h) | real weak root exists (BDB `nwh`) | `root_search.json` B1 |
| GLOSS tier reached | **EXACT** ("dwell") — via III-y→III-h weak collapse + best-of-Hebrew/Aramaic | `root_search.json` B3 |
| Held-out root recurrence (H2) | **0/3** divergent clean sites carry the WA-JA root | `loso.json` |
| Gloss beats formula features (H3/B5) | dwell **0.0/3**, below give/dedicate (3.0) & invocation (2.5) | `root_search.json` B5 |

**Observed combined strength := a coherent chain that (i) selects a value, (ii) forms a real Semitic weak
root from the *301-derived skeleton, and (iii) reaches an EXACT-tier gloss under the best-of-language ×
best-of-collapse × gloss-polysemy search.** This is the strength the null must reach to count as a match.

## 2. Adaptive choices the null reproduces (all of them)

Per mandate. Each realization re-runs the FULL adaptive selection:

1. **random *301 value** and **frequency-matched *301 value** — Packard frequency-banded permutation of the
   sign→value map (`nulls.packard_banded_permutation`, n_bands=4); *301 receives a random CV value.
2. **best-of-value search** — the reading keeps the best of the 65 CV candidates. The root skeleton depends
   only on *301's onset phoneme, so the value space collapses to 13 distinct outcomes → enumerated EXACTLY
   and additionally MC-sampled under the frequency weights.
3. **random segmentations** + **best-of-segmentation** — 4 families (Di Mino / Davis / Thomas / diplomatic)
   plus random cut sets; the search keeps whichever isolates a scorable root.
4. **random Semitic roots** + **fake lexica (L_fake)** + **wrong-language lexica** — the edit-distance
   "match-exists" channel, re-sampled to reconfirm it is NO_POWER (L_fake floor).
5. **random glosses / random language families** — best-of-{6 languages} × {5 collapse modes} ×
   {gloss polysemy}, the search that manufactured "dwell".
6. **random morphological parses** — S_morph recomputed under relabelling (must stay invariant → contributes
   NO discrimination, per framing-constraint §1).
7. **combined statistic** — the strongest tier the whole pipeline manufactures for that realization.

## 3. Match indicators (nested, pre-declared)

- **M_root** (loose): best-of search yields a real Semitic weak/hollow root for the *301-derived skeleton.
- **M_gloss_fixed** (dwell target pre-committed): best-of-{language×collapse} reaches a dwell-tier (≥broad)
  gloss for the *301 skeleton, with the semantic target FIXED as "dwell/habitation" in advance.
- **M_gloss_free** (PRIMARY — matches the observed post-hoc procedure): best-of search reaches SOME
  EXACT-tier gloss in *any* coherent semantic field (the reader chooses the field after seeing the root, as
  Di Mino chose "dwell" to fit a sanctuary context). This is the honest whole-pipeline strength.
- **M_gate** (strict, full preregistered graduation): the run ALSO clears the value bar (S_lex rank 1 with
  margin) + held-out root recurrence + beats E[max_Neff]. This is the GRADUATE_EXACT_CLAIM FP.

## 4. Realization budget (pre-declared; report CI)

- cheap (root + gloss legs): **N ≥ 1000**
- moderate (+ value channel + segmentation): **N ≥ 500**
- full pipeline (all legs + combined + graduation): **N ≥ 100**
- Value space is enumerable (13 onset outcomes) → **exact** rates ALSO reported alongside MC; CI via
  Wilson (proportions) and one-sided Clopper–Pearson upper for zero/near-zero cells.

## 5. Decision rule (frozen — from prereg + framing constraints)

- Value · S_morph → report as **`NO_DISCRIMINATIVE_POWER_FOR_VALUE`** (invariant; NOT itself a rejection).
- Value · S_lex → /na/ fails rank-1 clause with **power** (PC3 recovers a planted value rank 1) → REJECT
  contribution.
- Lexical/gloss chain (H2/H3): if observed EXACT-dwell strength is **indistinguishable** from the
  M_gloss_free null (FP ≥ ~α, chain strength inside the null band) → **`NULL_PUBLISHED`** at that layer.
- Whole chain `/na/ → N-W-Y → dwell → Semitic`: **`REJECT`** iff adequate power (PC PASS) **and** ≥1
  load-bearing clause fails (value rank-1, H2 recurrence, H3 beats-features). Charge the III-y→III-h
  transform to the receipt. Do **not** claim impossibility; do **not** derive REJECT from S_morph invariance;
  preserve the layer split (structural `i-*301` core may remain literature-supported).
