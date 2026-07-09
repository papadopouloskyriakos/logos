# EPOCH-068 REPORT — Is the A-prefixed vocabulary more cross-site-shared than frequency-matched non-A vocabulary?

**Layer:** L3 (grammar x lexicon; cross-site structural recurrence)
**Campaign:** Linear A frontier-72h
**Verdict (FROZEN, MECHANICAL):** `A_MARKED_VOCAB_MORE_SHARED`

---

## 1. Question

The campaign's through-line is *shared administrative GRAMMAR + site-local LEXICON*. The A-prefix
(anonymous word-initial slot 'A') is cross-site robust (E023: significant in 9/10 sites), while whole-word
vocabulary is site-local (E032). This epoch asks: is the A-prefix a grammatical marker attached to
**equally-site-local** stems (A-words share no more than other words — supports the through-line), or does
A- mark a **more-shared** pan-administrative sub-vocabulary (A-words recur across sites MORE than
frequency-matched non-A words)?

Pure structural word-form recurrence (L2/L3). Anonymous sign-sequences; 'A' = the anonymous initial-slot
label from E022-E025; NO phonetic value, NO reading, NO meaning.

## 2. Method (frozen in prereg.md, hash 4f0204d5…)

- **Unit:** word-TYPE = tuple of signs (multi-sign, len>=2). token count = total occurrences; sites = set
  of distinct `site` values.
- **A-TYPE:** first sign == 'A'. **NON-A:** first sign != 'A'.
- **SHARED:** appears at >=2 distinct sites.
- **Informative types:** count>=2 (count-1 hapax can never be shared; excluded from both rates).
- **Metric:** D = share_rate(A) − share_rate(nonA), share_rate = (#shared types)/(#types), over count>=2.
- **Null (FREQUENCY-MATCHED):** within EACH token-count stratum, permute A/non-A labels preserving the
  per-stratum A-count; recompute D; one-sided perm p = frac(null D >= D_obs). This controls token
  frequency exactly — labels only shuffle among equal-count types.

## 3. Global result

| quantity | value |
|---|---|
| informative A-types (count>=2) | 16 |
| informative non-A types (count>=2) | 142 |
| share_rate(A) | **0.6875** (11/16) |
| share_rate(nonA) | **0.3169** (45/142) |
| **D_obs** | **+0.3706** |
| null mean D | 0.0435 |
| **perm p** (one-sided, A more shared, 5000 draws) | **0.0072** |

A-prefixed types recur across >=2 sites at roughly **2.2×** the rate of frequency-matched non-A types.

## 4. Positive control (SYNTHETIC — gates the verdict)

| gate | result | threshold | pass |
|---|---|---|---|
| (a) DETECT (planted A-more-shared) | perm p = 0.0002 | ≤0.05 | ✅ |
| (b) FALSE-POSITIVE (random labels within strata) | rejection rate = 0.00 over 20 draws | ≤0.10 | ✅ |
| (c) POWER (planted +0.3 gap, real per-stratum A-counts) | power = 1.00 | ≥0.5 | ✅ |

**PC verdict: PASSED.** Machinery self-check: stratified null has E[D_null]≈0 (−0.0024 on synthetic),
confirming the null is unbiased. PC is synthetic (stated).

## 5. Robustness — per-stratum share rates

A leads non-A in share-rate at **every** stratum where both are present — the effect is broad, not a
single-stratum artifact:

| count | share_A | share_nonA |
|------:|--------:|-----------:|
| 2     | 0.50    | 0.33       |
| 3     | 0.80    | 0.12       |
| 4     | 1.00    | 0.29       |

The result is driven by **16 informative A-types** (11 shared). 99 of 115 A-types are count-1 hapax and
cannot be shared by construction; the comparison is necessarily over the small informative base, which is
why the power check was required (and passed at 1.0).

## 6. Frozen mechanical verdict

PC passed AND power≥0.5 AND D_obs>0 significant (perm p=0.0072 ≤ 0.05) →
**`A_MARKED_VOCAB_MORE_SHARED`**.

## 7. Interpretation (honest bottom line)

The A-prefix does **not** merely sit on site-local stems. A-prefixed multi-sign word-forms recur across
sites significantly more than frequency-matched non-A forms. This means A- marks (or selects into) a
**more-shared, pan-administrative sub-vocabulary** — a partial refinement of the through-line: the
administrative grammar is shared (E023), and the A-marked *portion* of the lexicon is also more shared
than generic vocabulary, even though vocabulary as a whole is site-local (E032). The effect rests on 16
informative A-types (small but consistent and broad across strata); a positional control (E072) and a
bootstrap CI (E074) are flagged as successors to harden specificity.

**Caveat stated plainly:** only 16 informative A-types drive this; the power check (1.0 for a +0.3 gap)
and the broad per-stratum pattern support the call, but the small base is the main fragility.

## 8. Non-circularity

Anonymous word-forms only. 'A' = anonymous word-initial slot label (no phonetic value, no reading, no
meaning). Sharing = pure structural recurrence across >=2 sites. Frequency confound controlled by
within-stratum label permutation. No semantic/phonetic/reading circularity invoked.

## Outputs
- prereg: experiments/linear_a_frontier_72h/epochs/EPOCH-068/prereg.md
- plan_hash: experiments/linear_a_frontier_72h/epochs/EPOCH-068/plan_hash.txt
- machinery: experiments/linear_a_frontier_72h/epochs/EPOCH-068/machinery.py
- result: experiments/linear_a_frontier_72h/epochs/EPOCH-068/result.json
- data: experiments/linear_a_frontier_72h/data/epoch_068/strata_and_types.md
