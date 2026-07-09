# EPOCH-053 REPORT — Ledger Entry-Word Vocabulary Restriction (Commodity Lexicon?; L2/L3)

**Task:** Are ENTRY-WORDS (word tokens immediately followed by a numeral in the
ordered stream) drawn from a more restricted, repetitive form set than NON-ENTRY
words — i.e. is there a low-diversity "commodity lexicon" of counted items?

**Layer:** L2/L3 (pure distributional vocabulary structure; forms ANONYMOUS;
no phonetics, no meaning, no numeral values).

**Verdict (frozen mechanical):** `NO_ENTRY_WORD_LEXICON_RESTRICTION`

---

## 1. Setup

- Corpus: `corpus/silver/inscriptions_structured.json` (1341 inscriptions,
  ordered `stream` of `word`/`num`/`div`/`nl` tokens).
- ENTRY-word = a `word` token whose NEXT stream token is `num` (n = 1040).
- NON-entry = a `word` token whose next token is NOT `num` (n = 2107).
- Word-form = the sign tuple (anonymous).
- Metric: (a) Type-Token Ratio (TTR) and (b) normalized entropy
  H/log2(n_types). Restriction = entry-words LOWER on BOTH.
- Size-matching (TTR is size-dependent): larger group subsampled to the smaller
  group's size; ≥500 bootstrap resamples; label-permutation p (shuffle
  entry/non labels among pooled words, recompute the matched TTR gap).

## 2. Positive Control (gates verdict) — PASSED

| Check | Result |
|---|---|
| DETECT (planted restricted+skewed entry vocab vs diverse non-entry) | p = 0.0033, direction = entry_more_restricted ✓ |
| FALSE-POSITIVE (same vocab, different sizes, 25 splits) | FP rate = 0.0 (≤ 0.10) ✓ |

The machinery detects a planted commodity lexicon and does NOT fire on
same-vocabulary different-size groups — confirming the size-matching removes the
TTR sample-size confound. **The null result below is therefore trustworthy.**

## 3. Global Result — entry-words NOT more restricted

| Metric | Entry (matched) | Non-entry (matched) | Gap (non − entry) |
|---|---|---|---|
| TTR | 0.329 | 0.372 | +0.043 (entry slightly lower) |
| Normalized entropy | 0.903 | 0.845 | **−0.058 (entry HIGHER)** |

- **Direction = MIXED.** Entry-words have marginally lower TTR but HIGHER
  normalized entropy (more evenly/uniformly distributed). A genuine commodity
  lexicon requires BOTH lower; entropy runs the opposite way.
- Label-permutation one-sided p for "entry more restricted" = **0.97**
  (the opposite tail is p = 0.03). Entry-words are decisively NOT more
  concentrated than non-entry words.

## 4. Cross-Site (≥20 entry AND ≥20 non-entry per site; 5 sites testable)

| Site | n_entry | n_non | gap_ttr | perm_p | direction |
|---|---|---|---|---|---|
| **Haghia Triada** | 686 | 1205 | **−0.062** | **1.0** | entry_less_restricted |
| Khania | 76 | 292 | +0.212 | 0.013 | entry_more_restricted |
| Phaistos | 29 | 81 | +0.238 | 0.017 | entry_more_restricted |
| Zakros | 114 | 104 | +0.075 | 0.003 | entry_more_restricted |
| Arkhalkhori | 27 | 36 | +0.142 | 0.047 | entry_more_restricted |

- 4 of 5 sites show a TTR-only entry-more-restricted signal — BUT in every one
  the normalized-entropy gap is near-zero or slightly negative (the effect is a
  TTR artifact, not genuine concentration).
- The dominant site **Haghia Triada (66% of all entry-words) goes the OPPOSITE
  way** (entry-words less restricted, p = 1.0) and drives the global null.
- `direction_consistent = false`.

## 5. Leave-One-Site-Out (drop Haghia Triada)

- LOO p (entry-more-restricted) = 0.0020, gap_ttr = +0.186, gap_entropy = +0.013.
- This flips to "significant" ONLY because the dominant counter-evidence site is
  removed; the entropy gap stays negligible (0.013). This is not a robust
  cross-site lexicon — it is an artifact of dropping 66% of the data.

## 6. Verdict Reasoning (frozen rules)

The `ENTRY_WORD_COMMODITY_LEXICON_CROSS_SITE` verdict requires, among other
conditions, that the **global** entry-words be significantly more restricted
(p ≤ 0.05). The global test gives p = 0.97 with MIXED direction (entropy
opposite). The global gate FAILS. Per the frozen rules, when entry-words are
not significantly more restricted (size-matched), the verdict is
**NO_ENTRY_WORD_LEXICON_RESTRICTION**. (The site-local TTR flicker in 4 small
sites does not rescue a global null with opposite entropy and an opposite
dominant site.)

## 7. Honest Bottom Line

There is **no robust commodity lexicon** among Linear A entry-words. Under a
rigorous size-matched test (PC-verified, false-positive rate 0.0), entry-words
are not more concentrated than non-entry words globally (p = 0.97); if anything
they are slightly MORE evenly distributed (higher normalized entropy). The
dominant site Haghia Triada shows entry-words LESS restricted, and the TTR-only
flicker in four small sites does not survive the entropy metric. "Commodity
lexicon" here is a distributional claim only (low-diversity form set), not a
meaning claim — and the distributional evidence does not support it.

## 8. Non-Circularity

Forms anonymous (sign tuples, never decoded). Entry defined by OBSERVED
numeral-adjacency. Pure L2/L3 distributional structure. LB control is synthetic
only (Linear B lacks the stream numeral-adjacency structure this test requires)
— stated explicitly. Size-matching verified to remove the TTR sample-size
confound (0.0 FP rate).

## 9. Outputs

- `experiments/linear_a_frontier_72h/epochs/EPOCH-053/prereg.md`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-053/plan_hash.txt`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-053/machinery.py`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-053/result.json`
- `experiments/linear_a_frontier_72h/data/epoch_053/` (entry/nonentry words,
  per-site, global metrics, cross-site, LOO, positive control)
