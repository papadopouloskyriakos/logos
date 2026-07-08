# EPOCH029 REPORT — Word-internal sign-bigram collocation structure (L2/L3)

**Task:** EPOCH-029 · Linear A frontier-72h
**Question:** Beyond the position-1 A- prefix, do Linear A words carry a COMBINATORIAL grammar — specific adjacent sign-PAIRS (bigrams) that are over- or under-represented relative to a within-word shuffle null — and is that structure ROBUST across independent sites?
**Layer:** L2/L3 (positional / combinatorial distributional statistics ONLY). **No phonetics, no meaning, no reading.** Bigrams reported as ANONYMOUS sign ids.
**Verdict (mechanical, frozen rule):** `MACHINERY_UNINFORMATIVE`

---

## 1. Verdict gate trace (frozen rule, prereg.md §6)

The frozen verdict is GATED by the positive control (PC). PC must pass before any LA verdict is admissible. PC FAILED → `MACHINERY_UNINFORMATIVE` regardless of the LA numbers below.

| Gate | Condition | Value | Pass? |
|---|---|---|---|
| PC (a) LB real structure | search-adj p ≤ 0.05 on LB | p = 0.0020 | ✅ |
| PC (b) false-positive control | synthetic i.i.d. rejection rate ≤ 0.10 | **0.30** | ❌ |
| Global LA structure | search-adj p ≤ 0.05 | 0.0020 | (would pass) |
| ≥2 sites individually sig | count of sites p ≤ 0.05 | 4 / 6 | (would pass) |
| Held-out replication | ≥50% of HT top-K replicate | 0.20 (2/10) | (would fail) |

PC gate (b) fails (synthetic i.i.d. false-positive rate 0.30 ≫ 0.10 threshold) → **MACHINERY_UNINFORMATIVE**. The LA findings below are therefore reported as **exploratory / not adjudicated** — the method as configured cannot be trusted to separate real adjacency structure from i.i.d. noise.

## 2. Positive control (gates the verdict) — FAILED

- **(a) LB real phonotactics detected:** on Linear B words, structure_score = 575, search-adj p = 0.0020. The machinery *does* see LB's real adjacency structure. ✅
- **(b) False-positive control FAILED:** 20 synthetic corpora built by sampling signs i.i.d. from the LB unigram distribution (NO real adjacency structure by construction) were each tested at search-adj p ≤ 0.05. **Rejection rate = 0.30** (6/20 rejected), against a frozen threshold of ≤ 0.10.
  - Synthetic p-values ranged from 0.0020 to 0.57; six fell at or below 0.05 (0.030, 0.066, 0.050, 0.032, 0.0060, 0.0099, plus borderline).
  - Interpretation: the structure_score statistic + search-adjusted p, as parameterized (count_threshold=5, 1000 per-bigram draws, 500 search draws), has an inflated type-I error rate on i.i.d. data. It is **not calibrated**. Per the frozen rule, this is `MACHINERY_UNINFORMATIVE`.

## 3. Global LA signal (exploratory — NOT adjudicated, PC failed)

Inspection of LA words with `len(signs) >= 2`:

- n_words = 1369
- n_distinct_bigrams = 1174
- Top raw-count bigrams (sign names shown for inspection only; verdict uses anonymous ids): KU·RO (39), TA·I (22), SA·RA (22), TA·NA (21), SA·RA₂ (21), A·TA (20), SA·SA (18), JA·SA (18), KI·RO (17), A·DU (17).

Global structure_score = **49** bigrams (obs ≥ 5, |z| ≥ 3) vs the within-word shuffle; search-adj p = **0.0020**. *If the machinery were calibrated*, this would indicate significant non-random adjacency structure corpus-wide. Because PC (b) failed, this is reported as a candidate signal requiring a re-calibrated re-test, not an established fact.

Top over-represented bigrams (anonymous, obs, z, direction):

| Bigram | obs | z | dir |
|---|---:|---:|---|
| S98·S127 | 39 | 19.31 | over |
| S129·S122 | 22 | 8.82 | over |
| S136·S90 | 22 | 7.34 | over |
| S73·S136 | 20 | 6.63 | over |
| S136·S103 | 21 | 6.17 | over |
| S122·S100 | 13 | 3.31 | over |
| S149·S91 | 14 | 3.91 | over |
| S98·S114 | 14 | 4.82 | over |
| S90·S7 | 16 | 2.65 | over |
| S7·S149 | 14 | 2.61 | over |

Top under-represented bigrams (anonymous):

| Bigram | obs | z | dir |
|---|---:|---:|---|
| S103·S142 | 6 | 8.01 | under |
| S79·S90 | 6 | 7.64 | under |
| S91·S112 | 6 | 6.69 | under |
| S73·S91 | 5 | 6.14 | under |
| S99·S90 | 5 | 5.31 | under |

## 4. Cross-site (exploratory — NOT adjudicated, PC failed)

Sites with ≥ 40 words (len ≥ 2): **6**.

| Site | n_words | structure_score | search-adj p | sig? |
|---|---:|---:|---:|---|
| Haghia Triada | 694 | 16 | 0.0020 | ✅ |
| Zakros | 132 | 1 | 0.0020 | ✅ |
| Khania | 120 | 1 | 0.0020 | ✅ |
| Knossos | 61 | 0 | 1.0 | ❌ |
| Phaistos | 58 | 0 | 1.0 | ❌ |
| Palaikastro | 57 | 1 | 0.0040 | ✅ |

4 / 6 sites individually significant at p ≤ 0.05. *(Again: not adjudicated — PC failed.)*

**Held-out replication (HT-trained → pooled other sites), K_top = 10:** 2 / 10 of the HT top over-represented bigrams replicate at p ≤ 0.05 on the pooled other sites → **frac = 0.20** (threshold ≥ 0.50). The two replicating bigrams were S136·S103 (obs 12, p = 0.001) and S101·S103 (obs 7, p = 0.003). Even setting PC aside, this specific-structure generalization **fails** the frozen 50% bar.

## 5. Bottom line (honest, bounded)

- **The machinery is not calibrated.** The within-word-shuffle structure_score statistic, at the frozen parameters, rejects i.i.d. synthetic data 30% of the time (threshold 10%). It cannot distinguish real adjacency grammar from sampling noise. Per the frozen rule this is `MACHINERY_UNINFORMATIVE`, and no LA claim is adjudicated.
- **What the (un-adjudicated) numbers would suggest, if re-calibrated:** a corpus-wide adjacency signal (search-adj p = 0.0020), present individually at 4/6 sites, but with **weak held-out generalization of specific bigrams** (only 2/10 HT-trained bigrams replicate on other sites). Even on its own terms the cross-site-robust bar is NOT met.
- **Honest reading:** there may be real within-word adjacency structure in Linear A (the LB positive control (a) does fire, and the LA signal is strong in raw terms), but THIS epoch's configuration cannot establish it. The result is a methodological null, not a substantive null.
- **No meaning claimed.** Bigrams are anonymous sign pairs. Nothing here assigns phonetic, semantic, or reading values.

## 6. Successor hypotheses (for a re-calibrated re-test)

- Re-run with a calibrated structure_score: raise count_threshold, use a proper whole-statistic permutation (not the exchangeable-pool approximation), and/or Bonferroni/BH-adjust the per-bigram z-tests before counting, so the i.i.d. false-positive rate ≤ 0.10.
- L3: extend to sign-TRIGRAMS (within-word) under the same shuffle null once calibrated.
- L2: test held-out replication of UNDER-represented (forbidden) bigrams — avoidance patterns may generalize where over-representation does not.
- L3: relate bigram structure to word-POSITION (initial/medial/final) — position-locked bigrams would indicate morphotactic slots.
- L2: compare LA structure_score to LB under matched sample size (subsample LB to LA's word count).

## 7. Outputs

- `epochs/EPOCH-029/prereg.md`, `plan_hash.txt` (frozen before verdict; PC run first).
- `epochs/EPOCH-029/machinery.py` — within-word shuffle bigram collocation; structure_score; search-adj p via exchangeable shuffle pool; LB positive control + i.i.d. synthetic false-positive control.
- `epochs/EPOCH-029/result.json` — full numbers incl. per-site, held-out detail, synthetic p-values.
