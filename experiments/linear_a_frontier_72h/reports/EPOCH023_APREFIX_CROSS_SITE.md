# EPOCH-023 — A- prefixation held-out / cross-site robustness (frontier F4)

**Executed by GLM-5.2** via `scripts/zai_agent.py` (first z.ai-worker epoch; no Anthropic tokens for the
labour). **Report authored by the Claude orchestrator** — GLM produced `prereg.md`, `plan_hash.txt`,
`machinery.py`, `result.json` (all verified) but did not write this report; the orchestrator completes it
so the record is whole (Art. XVII). Prereg frozen `plan_hash a84ac47d…`; claim ceiling **L2/L3**;
non-circular; no transfer licence touched.

## Question
A- prefixation is the campaign's one genuinely LA-side positive (E022: survives a 5,000-draw adaptive
null globally, p 0.0002). Does it meet the **Linear-B held-out standard** — significant across
*independent* site partitions and robust to removing the dominant site — or is it one-site-driven?

## Method (frozen)
- Metric: among words with ≥2 signs, count/fraction whose **first sign is A** (an anonymous positional
  slot; no phonetic value).
- Null (position-only, frequency-matched): **within-word uniform permutation** of each word's own signs,
  recompute A-initial count; 1,000 draws; one-sided p. (Machinery audited: a Bernoulli(kₐ/L) fast path is
  distributionally identical and was cross-checked against the explicit permutation.)
- Positive control **first** (gates the verdict): on Linear B, a known strongly-initial sign must be
  recovered across partitions and a frequency-matched random sign rejected.

## Positive control — PASSED
LB via `load_b_damos` (13,562 words; no per-site metadata → seeded balanced 5-way split, disclosed).
Known prefix analogue **A3** (94.5 % initial): significant **5/5** partitions (p 0.001 each).
Frequency-matched random **QI** (21 % initial): **0/5** (p 0.76–0.95). The machinery detects a real
cross-partition positional prefix and does not fire on a positionally-neutral sign.

## Result — `A_PREFIX_CROSS_SITE_ROBUST`
- Global: A word-initial **155/177** (0.876) of its occurrences; 155/1,369 of all ≥2-sign words.
- **9 of 10** qualifying sites (≥20 words) significant at raw p≤0.05 **and** Holm-adjusted; only Tylissos
  (n=21) fails.
- **Survives leave-one-site-out**: dropping the dominant site (Haghia Triada, 694 words) leaves p 0.001 on
  the remaining 675 words.
- **Clears far more sites than comparators**: the 5 next-most-initial signs clear KU 1 / I 3 / JA 3 / DA 1 /
  SA 2 (median 2); A- clears 9 — 7 above the median.
- All four conjuncts of the frozen rule are TRUE.

## Orchestrator verification (independent)
Claude independently re-derived every load-bearing number with different code and a different seed:
10 qualifying sites (match), A- significant 9/10 (match), leave-one-out p≤0.001 (match; a pool-definition
nuance — GLM pooled all non-HT words n=675, the orchestrator pooled only ≥20-word sites n=538 — both
p≤0.001, defensible, not an error), comparators 1/3/4/1/2 (match), PC A3 5/5 & QI 0/5 (match). The null
implementation was audited and is correct. **Verdict confirmed.**

## Scope (binding)
STRUCTURAL result only. A- is a **cross-site-robust productive positional prefix slot**. This does **not**
license any phonetic value, sound, meaning, language, or reading (L4+). It strengthens E022 (global
adaptive-null survival) to a **held-out-site generalisation** — the campaign's strongest genuinely
held-out LA-side positive, at layer L2/L3.

## Successors (7, from `result.json`)
Held-out by support-type (not just site); prospective seal on a future editio princeps; A- vs the E013
component channel; per-site A- effect-size gradient; a second readable-syllabary control (Cypriot);
scribe/hand partition if attributions surface; interaction of A- with word length.
