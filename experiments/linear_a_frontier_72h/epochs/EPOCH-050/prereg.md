# EPOCH-050 — A-PREFIX CONTINUATION SELECTIVITY (preregistration, FROZEN)

**Task:** EPOCH-050 of the Linear A frontier-72h campaign.
**Question (L2/L3):** Is the word-initial sign token `A` SELECTIONAL over its continuation —
i.e. is the entropy of the 2nd-sign distribution among A-initial words (len>=2) significantly
LOWER than a frequency-matched null — or does `A` attach freely (no selection)?
**Discipline:** signs ANONYMOUS; `A` denotes the word-initial sign token 'A' ONLY (no phonetic
value, no morpheme, no meaning); L2/L3 ONLY; LB used as control-only. Pure continuation-
distribution structure.

## Data (verified)
- Corpus: `corpus/silver/inscriptions_structured.json` — list of inscriptions; word tokens are
  `stream` entries with `t=='word'` and a `signs` list.
- A-initial word: `signs[0]=='A'` AND `len(signs)>=2` (so a 2nd sign exists).
- CONTINUATION = `signs[1]` (the 2nd sign).
- LB control: `cross_script.data.load_b_damos()[0]` (Linear B wordforms, control-only).

## Inspection (frozen facts, pre-analysis)
- n A-initial words (len>=2) = **155**.
- H_after_A (entropy of 2nd-sign dist after A) = **4.762 bits** (40 distinct 2nd signs).
- Global 2nd-position entropy (all len>=2 words) = 5.732 bits.
- Top continuations after A (anonymous): TA 20 (0.129), DU 14 (0.090), RA 10 (0.065), RI 8, SI/SE/SA 7 each.
- Comparator initial signs' 2nd-sign entropies: KU 3.064 (n=89), KA 4.436 (n=46), SI 3.916 (n=47), I 4.313 (n=80), TE 3.654 (n=21). A- has the HIGHEST 2nd-sign entropy among common initials.
- Per-site A-initial (len>=2) counts >=15: Haghia Triada 41, Khania 20, Zakros 19. (3 testable sites.)

## Metric (frozen)
- selectivity = observed H_after_A significantly LOWER than null H (one-sided).
- NULL (frequency-matched bootstrap): draw N=155 2nd-signs from the GLOBAL 2nd-position
  distribution (all len>=2 words, n=1369) with replacement; compute H; repeat B=2000 times;
  null_H = mean; p = fraction of bootstrap H <= observed H_after_A.
- Comparator: 2nd-sign entropy after KU, KA, SI, I (most-frequent initials).
- Cross-site: per site with >=15 A-initial words, bootstrap null from that site's own 2nd-position
  distribution; count sites with p<=0.05 (restricted). Leave-one-site-out on HT (the largest site):
  recompute global restricted test excluding HT.

## Positive Control (gates verdict) — FROZEN
- (a) DETECT: construct a synthetic prefix `__PLANT__` whose continuation is drawn from a
  RESTRICTED set of K=5 signs (low entropy); confirm the test flags it selectional (p<=0.05).
  Also a synthetic prefix with FREE continuation (matched to global 2nd-position dist) is NOT
  flagged.
- (b) LB sanity: 2nd-sign entropy after a chosen frequent LB initial sign vs LB null.
- FP control: free-continuation synthetic must be flagged selectional <=0.10 of the time
  (false-positive rate over >=200 free synthetic prefixes).
- If DETECT fails OR FP rate >0.10 -> MACHINERY_UNINFORMATIVE.

## Mechanical verdict (FROZEN rule — proposer never adjudicates)
- `A_PREFIX_SELECTIONAL_CROSS_SITE` iff PC passed AND global H_after_A significantly < null
  (p<=0.05) AND >=2 sites significantly restricted (p<=0.05) AND survives leave-one-site-out.
- `A_PREFIX_SELECTIONAL_SITE_LOCAL` iff global restricted BUT <2 sites / collapses under LOO.
- `A_PREFIX_NON_SELECTIONAL` iff H_after_A NOT significantly below null (A- attaches freely).
- `A_SELECTIVITY_UNDERPOWERED` iff <2 sites have >=15 A-initial words.
- `MACHINERY_UNINFORMATIVE` iff PC failed.

## Outputs (PATH CONTRACT)
- prereg -> experiments/linear_a_frontier_72h/epochs/EPOCH-050/prereg.md
- plan_hash -> experiments/linear_a_frontier_72h/epochs/EPOCH-050/plan_hash.txt
- machinery -> experiments/linear_a_frontier_72h/epochs/EPOCH-050/machinery.py
- result -> experiments/linear_a_frontier_72h/epochs/EPOCH-050/result.json
- report -> experiments/linear_a_frontier_72h/reports/EPOCH050_REPORT.md
- data dir -> experiments/linear_a_frontier_72h/data/epoch_050/

Seed: 20260708 (campaign). Pure stdlib. Synchronous.
