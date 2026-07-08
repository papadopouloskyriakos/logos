# EPOCH-036 REPORT — CROSS-SITE SIGN-FREQUENCY CONCORDANCE

**Campaign:** Linear A frontier-72h · **Epoch:** EPOCH-036 · **Layer:** L2/L3 (distributional sign-usage statistics ONLY)
**Verdict (mechanical):** `SIGN_FREQ_CONCORDANCE_CROSS_SITE`
**Plan hash:** `c210b88f8d66e2e71b45db6820d754630667168976d124a9c1d090213cd4c73a  prereg.md`

---

## 1. QUESTION

E032 showed WORD-FORMS are site-local. This epoch asks the SIGN-INVENTORY question: do
independent SITES share the SAME sign-frequency profile — a common writing-system fingerprint
(frequent signs are frequent everywhere) — or do they DIVERGE (dialect-like), and is any site a
clear OUTLIER? Pure distributional sign-usage statistics. Signs are **ANONYMOUS ids**; no
phonetics, no sound, no meaning, no reading.

## 2. DATA (verified)

`corpus/silver/inscriptions_structured.json`. Per site, sign frequencies counted over all signs
in all `word` tokens. **Qualifying sites: >=100 sign tokens.**

| site | sign tokens | distinct signs |
|---|---:|---:|
| Haghia Triada | 3054 | 178 |
| Khania | 555 | 108 |
| Zakros | 485 | 79 |
| Knossos | 256 | 69 |
| Palaikastro | 228 | 47 |
| Phaistos | 222 | 72 |
| Iouktas | 148 | 30 |
| Arkhalkhori | 130 | 52 |

**8 qualifying sites**, **union inventory = 234 anonymous sign ids**. (>=4 → not underpowered.)

## 3. METRIC & NULL (frozen)

- **CONCORDANCE** = mean pairwise Spearman rank correlation of per-site sign-frequency vectors
  over the union inventory.
- **NULL** = within-site sign-label shuffle: for each site, permute which count attaches to which
  sign id (full permutation over the union inventory on that site's vector); recompute mean
  pairwise Spearman; 1000 draws; one-sided p = frac draws with shuffled >= observed. Calibrated
  by construction: each site's frequency SHAPE is preserved, cross-site sign-IDENTITY alignment
  is destroyed → null centres at ~0.

## 4. POSITIVE CONTROL (gates the verdict) — **PASSED**

LB (`load_b_damos()[0]`, DĀMOS, ~43,868 sign tokens, 89 signs) has NO site metadata → **SEEDED**
partition into **5 pseudo-sites** (shuffled wordforms, 1200 each).

- **DETECT:** LB is one shared script → concordance **0.978**, shuffle-null mean ~0.0007,
  **detect p = 0.0** (≤ 0.05). ✅
- **FALSE-POSITIVE:** 20 control sets of pseudo-sites with **independent random-permutation**
  frequency vectors (no shared fingerprint; observed concordance ≈ −0.05) → rejection rate
  **0.10** (≤ 0.10; verified stable at 0.10 over 40 sets). ✅

Machinery is **informative**. PC gates the verdict.

## 5. GLOBAL RESULT

| quantity | value |
|---|---:|
| n qualifying sites | 8 |
| union inventory | 234 |
| **observed mean pairwise Spearman** | **0.605** |
| shuffle-null mean | −0.0003 |
| shuffle-null std | ~0.012 |
| **one-sided p** | **0.0** (1000 draws) |

Observed concordance is ~50 null-SDs above the null. The 8 sites share a strong common
sign-frequency fingerprint.

## 6. LA MAIN — held-out / outlier structure

### (a) Leave-one-site-out
Every LOO concordance stays in **0.581–0.634**, far above the null (~0.00). Concordance is
**NOT driven by a single pair**; it survives removal of any one site. (Removing the
token-dominant Haghia Triada leaves concordance at 0.619 — not an artefact of HT's sample size.)

### (b) Per-site mean correlation to the others

| site | mean corr to others |
|---|---:|
| Knossos | 0.674 |
| Palaikastro | 0.662 |
| Arkhalkhori | 0.652 |
| Zakros | 0.644 |
| Phaistos | 0.565 |
| Haghia Triada | 0.562 |
| Iouktas | 0.558 |
| **Khania** | **0.518** (lowest) |

**No outlier.** The lowest site (Khania, 0.518) is within 2 SD of the across-site mean (0.593)
and the gap to the next site (0.040) is well under 1 SD of the per-site values (~0.054). No
site qualifies as a clear low outlier → no dialect-like divergent site in this anonymous,
frequency-only view.

## 7. FROZEN MECHANICAL VERDICT

PC PASSED · observed concordance significant (p = 0.0 ≤ 0.05) · survives leave-one-site-out ·
no strong outlier site ⇒ **`SIGN_FREQ_CONCORDANCE_CROSS_SITE`**.

## 8. KEY FINDINGS

1. The 8 qualifying LA sites share a strong common sign-FREQUENCY fingerprint: mean pairwise
   Spearman = **0.605** vs shuffle-null ~0.00 (p = 0.0).
2. Symmetric counterpart to E032: WORD-FORMS are site-local, but the SIGN-INVENTORY usage
   profile is shared — a writing-system-level (syllabary-usage) regularity, not a word-form one.
3. Not driven by a single pair/site: every LOO concordance stays 0.581–0.634.
4. No outlier site (Khania lowest at 0.518, within noise of the pack).
5. PC PASSED (LB detect p = 0.0; FP rate 0.10 ≤ 0.10).

## 9. NON-CIRCULARITY / HONEST BOTTOM LINE

Signs are ANONYMOUS ids. No phonetic/sound/meaning/reading was assigned or used; all statistics
are L2/L3 distributional sign-usage. LB is a positive-control benchmark ONLY. **Concordance is a
distributional statistic — it is NOT evidence of shared LANGUAGE.** It says only that the
*frequency profile of the sign inventory* is concordant across sites: the signs that are
frequent at one site tend to be frequent at the others. Why (shared scribal convention? shared
document/genre mix? shared underlying language?) cannot be decided from this anonymous,
frequency-only test.

## 10. SUCCESSOR HYPOTHESES (L2/L3 unless noted)

- **H1:** Top-k rank-stable core — do the top-10 signs alone reproduce the concordance?
- **H2:** Decompose by rank band (head/mid/tail) — Zipf-shape artefact vs identity-specific alignment?
- **H3:** Do underpowered sites (Syme, Tylissos, Malia, 69–88 tokens) join the fingerprint pooled?
- **H4:** Cross-check vs E032 — shared sign USAGE but divergent sign COMBINATION (bigram/word-form)?
- **H5:** Monitor Khania (lowest-correlating) for dialect-like divergence as data grows.
- **H6:** Anonymous rank-frequency-curve shape comparison LA vs LB.

## 11. OUTPUTS

- `experiments/linear_a_frontier_72h/epochs/EPOCH-036/prereg.md` (frozen)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-036/plan_hash.txt`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-036/machinery.py` (`__main__` self-check)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-036/result.json`
- `experiments/linear_a_frontier_72h/data/epoch_036/site_sign_frequencies.json`
- `experiments/linear_a_frontier_72h/reports/EPOCH036_REPORT.md` (this file)

**Deviations:** none.
