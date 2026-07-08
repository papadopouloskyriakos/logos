# EPOCH-023 — A- PREFIXATION HELD-OUT / CROSS-SITE ROBUSTNESS

**Campaign:** Linear A frontier-72h (frontier F4). Claim ceiling: L2/L3.
**Layer:** L2/L3 (positional / structural statistics ONLY).

## NON-CIRCULARITY NOTE (hard constraint)
Sign names (A, JA, KU, ...) are ANONYMOUS identifiers. No phonetic value, sound,
meaning, language, or reading is assigned or implied to ANY sign. "A-" denotes a
POSITIONAL SLOT (word-initial occurrence of the sign token "A") only — never a
sound or meaning. No known-value data is a model input on the LA side. Linear B
(LB) is used ONLY as a positive-control benchmark for the machinery.

## QUESTION
A- prefixation is the campaign's one genuinely LA-side positive (E022: A- survives
a 5000-draw adaptive null globally, p≈.0002). Is it a GENUINE, DISTRIBUTED
productive positional prefix that holds across independent site partitions (the
Linear-B held-out standard), or is it driven by a single site / support type?

## METRIC (fixed)
A- prefix incidence = among all words with >=2 signs, the COUNT and FRACTION whose
FIRST sign is "A". Computed globally first (sanity target: A word-initial ~155 of
~177 A-occurrences), then per partition.

## NULL (fixed, frequency-matched, within-partition)
For a given set of words, the null asks: "is A word-initial MORE than expected
given A's overall frequency and the word-length structure of THIS partition?"
Construction: for each null draw, independently PERMUTE the sign order WITHIN each
word (uniform random permutation of that word's own signs), then recompute the
A-initial count. 1000 draws. One-sided p = (1 + #{null_count >= observed}) /
(1 + n_draws). This preserves each partition's sign multiset and word lengths
exactly (tests POSITION, not frequency).

## PARTITION SCHEME
- LA MAIN: partition by `site`. Keep sites with >= 20 qualifying words (>=2 signs).
  Report which sites qualify and their word counts.
- LA leave-one-site-out: pooled corpus with the single largest site removed.
- LB POSITIVE CONTROL: `load_b_damos()` returns (wordforms, freq, value2glyph)
  with NO per-site/series/scribe metadata. Therefore the LB partition is a SEEDED
  balanced 5-way random split of the wordforms (seed=20240123). This is stated
  explicitly in all outputs.

## POSITIVE CONTROL (gates interpretation)
On LB: compute per-sign initial-rate; choose the most initial-skewed sign with
>=40 occurrences as a KNOWN positional-prefix analogue. Partition LB (seeded
balanced 5-way). Verify:
  (a) the chosen LB prefix is significant (p<=0.05 under the STEP-3 null) in
      >=3 independent partitions;
  (b) a frequency-matched RANDOM LB sign is NOT (few partitions).
If the PC fails, verdict = MACHINERY_UNINFORMATIVE and NO LA interpretation is made.

## ADVERSARIAL / MULTIPLICITY (LA)
Repeat the per-site test for the 5 next-most-frequent word-initial signs (besides
A) as frequency-matched comparators. A- is "special" only if it clears materially
more independent sites than these comparators. Holm-correct across the site family
for A- (family = the qualifying sites).

## FROZEN MECHANICAL VERDICT RULE (decide by counting, no narration)
- A_PREFIX_CROSS_SITE_ROBUST iff (PC passed) AND A- significant (p<=0.05) in
  >=3 independent sites AND A- remains significant under leave-one-site-out AND
  A- clears >= 2 more sites than the median comparator sign.
- A_PREFIX_SINGLE_SITE_CONCENTRATED iff A- significant globally but in <=1 site
  OR collapses under leave-one-site-out.
- A_PREFIX_UNDERPOWERED_BY_PARTITION iff too few sites have enough words to test
  (report the power limit; threshold: fewer than 3 sites with >=20 words).
- MACHINERY_UNINFORMATIVE iff the PC failed.

## ASSUMPTIONS
- Word boundaries in the LA silver corpus are taken as given (token t=='word').
- Signs within a word are an ordered sequence; permutation null treats all
  within-word orderings as exchangeable under H0.
- RNG: numpy default RNG with fixed seeds for reproducibility.
- "Independent site" = a distinct `site` value with >=20 qualifying words.

## OUTPUTS
- experiments/linear_a_frontier_72h/epochs/EPOCH-023/result.json
- reports/EPOCH023_APREFIX_CROSS_SITE.md
- data/aprefix_cross_site/ (intermediate JSON)
