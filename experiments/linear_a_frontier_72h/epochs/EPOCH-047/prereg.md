# EPOCH-047 — HELD-OUT PREDICTABILITY OF THE DOCUMENT TOKEN-TYPE GRAMMAR

**Campaign:** Linear A frontier-72h · **Epoch:** 047 · **Layer:** L2/L3 (document token-type grammar)
**Operator:** logos z.ai research worker (GLM-5.2) · **Discipline:** STRICT LOGOS

## QUESTION (frozen)
Does the Linear A **document TOKEN-TYPE stream** (the ordered sequence of token TYPES —
`word` / `num` / `nl` / `div` / `other` — within each inscription) have a **PREDICTABLE
grammar** that **GENERALIZES to HELD-OUT inscriptions**? Concretely: does a **first-order
Markov model** of token-TYPE transitions achieve **lower held-out cross-entropy** (perplexity)
than a **unigram baseline**, and does that generalization **hold across a site-blocked split**?

This CONSOLIDATES the certified ledger/document findings (E031 word→numeral, E037
numeral-line-final) into a single PREDICTIVE test — the closest L2/L3 analog to "predicts
held-out material". Pure token-TYPE sequence structure (L2/L3): **NO sign identities, NO
numeral values, NO phonetics, NO meaning.**

## NON-CIRCULAR / DISCIPLINE (hard)
- Token TYPES only (`word` / `num` / `nl` / `div` / `other`). NO sign/word identities, NO
  numeral values, NO phonetics/meaning. L2/L3 ONLY.
- LB used as CONTROL-ONLY. LB DĀMOS has NO token-type stream (only wordforms); a SYNTHETIC
  type-stream control is built for LB and **SAID SO** explicitly.
- Prereg + plan_hash FROZEN BEFORE running. PC FIRST. Mechanical verdict from a FROZEN rule.
- Held-out split MUST be respected: transition probabilities trained on TRAIN only;
  cross-entropy evaluated on TEST only.

## DATA (verified)
- `corpus/silver/inscriptions_structured.json` — ORDERED `stream`; token types
  `word` / `num` / `nl` / `div` / `other`. Model the per-inscription type sequence with
  BOS/EOS markers added.
- Corpus path: BASE/corpus then repo-root.
- LB PC via `load_b_damos` (returns flat list of wordforms; **no token-type stream** →
  synthetic type-stream control built and labelled).

## METHOD (frozen)
- **First-order Markov model** over token TYPES: transition matrix `P(next_type | cur_type)`,
  Laplace-smoothed (add-1 over the type vocabulary + BOS/EOS), trained on TRAIN inscriptions.
- **Evaluate** mean per-token cross-entropy (bits/token) on TEST inscriptions:
  `xent = -mean log2 P(t_i | t_{i-1})` over all non-BOS tokens (EOS counted as a predicted
  token).
- **BASELINE** = unigram type model (marginal type frequencies incl. BOS/EOS), Laplace-smoothed,
  trained on TRAIN, evaluated on TEST: `xent = -mean log2 P(t_i)`.
- **IMPROVEMENT** = `baseline_xent - markov_xent` (bits/token; >0 ⇒ Markov grammar is
  predictive).
- **Two splits:**
  - (a) **RANDOM 5-fold CV** (seed-frozen): report mean improvement across folds.
  - (b) **SITE-BLOCKED**: train on all-but-one site, test on the held-out site, for each site
    with ≥15 inscriptions (tests cross-site generalization).
- **Significance** of improvement via an **order-shuffle permutation null**: for each TEST
  inscription, shuffle its type order (BOS/EOS stay at ends), recompute Markov xent; the real
  Markov xent must beat the order-shuffled xent. Permutation p-value computed by repeated
  shuffles of the TEST set (≥200 permutations) comparing real-vs-shuffled Markov xent.

## POSITIVE CONTROL (gates verdict)
- **(a) DETECT:** on a synthetic stream with a KNOWN strong transition grammar (planted
  `word → num → nl` cycles with noise), the Markov model MUST beat unigram
  (improvement > 0, permutation p ≤ 0.05).
- **(b) FALSE-POSITIVE:** on order-shuffled streams (no sequential grammar), improvement ≈ 0
  and NOT significant across ≥20 sets.
- If it cannot detect a planted grammar OR claims significant improvement on shuffled →
  **MACHINERY_UNINFORMATIVE**.

## FROZEN MECHANICAL VERDICT
- **DOC_GRAMMAR_PREDICTIVE_HELDOUT** iff PC passed AND global CV improvement > 0 significant
  (p ≤ 0.05) AND site-blocked held-out improvement > 0 (AND order-shuffle p ≤ 0.05) in ≥3
  sites (generalizes to unseen sites).
- **DOC_GRAMMAR_PREDICTIVE_SITE_LOCAL** iff global CV improvement significant BUT site-blocked
  held-out fails in most sites (<3) → predictable within-sample but does not generalize across
  sites.
- **DOC_GRAMMAR_NOT_PREDICTIVE** iff global CV improvement not significant (Markov ≈ unigram).
- **DOC_GRAMMAR_UNDERPOWERED** iff <3 sites have ≥15 inscriptions.
- **MACHINERY_UNINFORMATIVE** iff PC failed.

## OUTPUTS
- `prereg.md`, `plan_hash.txt`, `machinery.py`, `result.json`, `report` (EPOCH047_REPORT.md),
  `data/epoch_047/` — at the PATH CONTRACT paths.
- `result.json` keys: `task_id="EPOCH-047"`, `method`, `result`, `verdict` (one allowed token),
  `numbers`, `key_findings` (≥3), `successor_hypotheses` (≥5), `layer="L2/L3"`,
  `la_touched=true`, `non_circular` (str), `deviations` (list).
