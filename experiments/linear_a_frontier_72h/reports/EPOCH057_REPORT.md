# EPOCH-057 REPORT — The 'div' token's structural role (L2)

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-057
**Layer:** L2 (pure token-position structure; token TYPES only — word/num/div/nl/other)
**Verdict (mechanical, frozen rule):** `DIV_LEXICAL_SEPARATOR_CROSS_SITE`
**Operator:** logos z.ai research worker (GLM-5.2) — proposer/operator, never adjudicator.

---

## 1. Object & question (NEW CHANNEL)

The corpus `div` token — an explicit within-line word-divider mark (n=463 raw). Distinct from
E037's `nl` (line breaks) and E031's word→num order test. This epoch asks: is `div` a systematic
LEXICAL WORD-SEPARATOR that (S1) sits at word|word boundaries (enriched vs null) AND (S2) AVOIDS
the word|numeral boundary (depleted vs null) — i.e. respects "word+numeral" as a bound entry unit,
separating counted entries/words but never splitting a word from its quantity? And is that pattern
beyond a position-shuffled null AND cross-site robust?

**Discipline (hard, non-circular):** only token TYPES used; `div` is the observed token type; no
sign values, readings, phonetics, or semantics. Prereg + plan_hash frozen BEFORE any real-corpus
machinery execution. Positive control FIRST; mechanical verdict from a FROZEN rule.

## 2. Data inspection

- Corpus: `corpus/silver/inscriptions_structured.json` — 1341 inscriptions, ordered `stream`.
- Token-type counts: word 3147, num 1276, div 463, nl 2114, other 1056.
- 52 sites; div by site (top): Haghia Triada 235, Khania 35, Knossos 35, Zakros 29, Iouktas 27,
  Palaikastro 27 → **6 sites with ≥15 div** (testable).
- Flanking (raw, in-stream before/after the div token):
  - BEFORE hist: word 382, other 34, nl 24, START 17, div 6.
  - AFTER hist: word 283, nl 96, other 42, END 20, num 16, div 6.
  - Top transition: **word>div>word = 235** (51% of divs); word>div>num = 13 (rare).

## 3. Frozen metric & null

- **S1 (WORD|WORD ENRICHMENT):** fraction of divs whose bracketing content-gap is word|word.
- **S2 (WORD|NUM AVOIDANCE):** count of divs whose bracketing content-gap is word|num or num|word.
- **NULL (calibrated by construction):** within each inscription, re-place the same number of div
  tokens uniformly at random among the inter-content-token gaps (gaps between word/num/other
  tokens), preserving the content-token sequence and div count. ≥500 reshuffles (1000 for global).
  One-sided p: S1 enrichment, S2 depletion.
- A `div` maps to a content-gap via its nearest preceding and following content token; 40 divs at
  stream start/end with no bracketing content token on one side are excluded from the gap-based
  statistics (consistent for observed and null). → n_div(gap-based) = **423**.

## 4. Positive control (FIRST; gates verdict; SYNTHETIC — LB corpus lacks this div structure)

The Linear B corpus lacks this `div` structure, so the PC is fully synthetic, built from the real
content-token skeletons with planted div placements.

- **(a) DETECT** — synthetic corpus where div placed ONLY at word|word gaps (never word|num):
  S1 p = 0.0020 (enriched), S2 p = 0.0020 (depleted). **Detected.**
- **(b) FALSE-POSITIVE** — synthetic where div placed UNIFORMLY at random gaps; 30 draws:
  rejection rate = 0.067 (≤0.10). **Does not fire on uniform placement.**
- **PC verdict: PASSED.** Machinery is informative.

## 5. Global results

| statistic | observed | null mean | perm p | direction |
|---|---|---|---|---|
| S1 word\|word fraction | **0.749** | 0.403 | **0.001** | enriched |
| S2 word\|num count | **28** | 141.7 | **0.001** | depleted |

The divider sits at word|word gaps ~1.86× more often than chance, and at word|num boundaries only
28 times vs an expectation of ~142 — a ~5× depletion. Both highly significant.

## 6. Cross-site (≥15 div) + leave-one-site-out

6 testable sites. Per-site (obs vs null, p):

| site | n_div | S1 obs / null / p | sig_s1 | S2 obs / null / p | sig_s2 |
|---|---|---|---|---|---|
| Haghia Triada | 229 | 0.677 / 0.196 / 0.002 | ✓ | 23 / 114.5 / 0.002 | ✓ |
| Khania | 35 | 0.800 / 0.272 / 0.002 | ✓ | 1 / 9.97 / 0.002 | ✓ |
| Zakros | 29 | 0.655 / 0.340 / 0.002 | ✓ | 4 / 11.28 / 0.004 | ✓ |
| Knossos | 27 | 0.815 / 0.797 / 0.493 | ✗ | 0 / 0.51 / 0.493 | ✗ |
| Palaikastro | 25 | 0.920 / 0.866 / 0.287 | ✗ | 0 / 0.57 / 0.431 | ✗ |
| Iouktas | 21 | 1.000 / 1.000 / 1.000 | ✗ | 0 / 0.00 / 1.000 | ✗ (degenerate: no word\|num gaps) |

- **n_sites_sig_both = 3** (Haghia Triada, Khania, Zakros) — all same-direction (S1 enriched, S2 depleted).
- **direction_consistent = True** (among the 3 significant sites).
- **Leave-one-site-out:** dropping each testable site in turn, the global S1 and S2 p-values remain
  ≤0.002 in every case (max LOO p = 0.0020). **LOO survives.**

Note: Knossos/Palaikastro/Iouktas are not significant — their content-token skeletons are already
almost entirely word|word (few or no word|num gaps), so the null already predicts near-pure
word|word placement and there is no room for the divider to show avoidance. This is a power/skeleton
artifact, not a contradiction of the global pattern.

## 7. Frozen mechanical verdict

Rule: `DIV_LEXICAL_SEPARATOR_CROSS_SITE` iff PC passed AND global S1 enriched (p≤0.05) AND global
S2 depleted (p≤0.05) AND both hold same-direction in ≥2 sites AND survive leave-one-site-out.

- PC passed ✓
- Global S1 enriched p=0.001 ✓
- Global S2 depleted p=0.001 ✓
- ≥2 sites same-direction (3 sites: HT, Khania, Zakros) ✓
- LOO survives (max p=0.002) ✓

**→ DIV_LEXICAL_SEPARATOR_CROSS_SITE**

## 8. Bottom line (honest)

Yes — at the L2 token-type level, `div` behaves as a systematic lexical word-separator that
respects "word+numeral" as a bound entry unit: it is strongly enriched at word|word boundaries
(~1.9× over a gap-shuffle null) and strongly depleted at word|numeral boundaries (~5× under
expectation), globally and in the three sites with sufficient word|num structure to test it
(Haghia Triada, Khania, Zakros), surviving leave-one-site-out. The divider separates counted
entries/words but does not split a word from its quantity. Three smaller sites (Knossos,
Palaikastro, Iouktas) lack sufficient word|num gaps to exhibit the avoidance and are non-significant
(a skeleton/power limit, not a counter-signal). Token TYPES only; no sign values or readings used.

## 9. Outputs

- prereg: `experiments/linear_a_frontier_72h/epochs/EPOCH-057/prereg.md`
- plan_hash: `experiments/linear_a_frontier_72h/epochs/EPOCH-057/plan_hash.txt`
- machinery: `experiments/linear_a_frontier_72h/epochs/EPOCH-057/machinery.py` (self-check OK)
- driver: `experiments/linear_a_frontier_72h/epochs/EPOCH-057/driver.py`
- result: `experiments/linear_a_frontier_72h/epochs/EPOCH-057/result.json`
- data: `experiments/linear_a_frontier_72h/data/epoch_057/analysis.json`
- report: `experiments/linear_a_frontier_72h/reports/EPOCH057_REPORT.md` (this file)

## 10. Deviations

1. n_div in the gap-based global analysis = 423, not the raw 463: 40 divs at stream start/end with
   no bracketing content token on one side are excluded (pre-registered in the gap definition;
   consistent for observed and null).
2. Positive control is fully synthetic (Linear B corpus lacks this div structure, per task spec);
   PC corpora built from real content-token skeletons with planted div placements.
3. LOO used 500 permutations per leave-one-out (vs 1000 for the main global); all LOO p ≤ 0.002.
