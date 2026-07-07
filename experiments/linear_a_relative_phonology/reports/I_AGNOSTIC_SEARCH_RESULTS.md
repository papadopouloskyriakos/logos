# I1 — Agnostic value-system search — RESULTS

**Verdict (frozen mechanical rule, §6 of the spec): `UNDERDETERMINED_NO_RECOVERY`.**
Seed 20260708 · Constitution v2.2 · claim layer ≤ L3 · all transfer licences NOT_EARNED.
Numbers are read from `data/I1_agnostic.json` (generated, not hand-written).

## 0. What was searched

A **value system** = a C×V factorisation φ of the **55** core Linear A signs (freq ≥ 10) into an abstract
consonant×vowel grid; the grid induces a factored bigram model P(cᵢ|cᵢ₋₁)·P(vᵢ|vᵢ₋₁) over the **2,462**
GORILA word units. Two search methods (greedy best-swap hill-climbing, 20 restarts + annealed swap-MCMC,
12 chains × 9,000 steps) maximise the frozen objective O = seqLL + 0.01·(relAgree+formConsist+morphCompat+
crossCompat). Nulls: 10,000 random assignments; a permuted-corpus null; a Linear B positive control.
Grid |C|∈{12,15,18}, |V|=5. Primary grid |C|=15.

## 1. The design correction that makes the result interpretable (recorded, not silent)

The **first, freely-optimised** objective is a *dead* detector. A φ allowed to lump signs into arbitrarily
few cells drives seqLL up by **collapse**: on this small corpus the best free assignment occupies only
**4 cells** (seqLL −1.16 vs random-φ mean −3.66) — a near-unigram whose high held-out likelihood is a
low-variance-estimation artifact, not phonology. The Linear B positive control collapsed identically and
recovered **zero** vowel structure (AMI 0.000, p 1.00). Evidence preserved in
`data/I1_agnostic_free_objective_collapse.json`. This is the same *frequency/estimation-artifact* failure
mode the campaign already found for seed-propagation.

The **primary** search therefore fixes granularity: φ ranges over **balanced** partitions (each class holds
a fixed sign-count) and every move is a size-preserving **swap**, so collapse is off the table and the
search varies only *which* signs group together — the phonological question. With this fix the detector
becomes **live**: the Linear B control recovers its consonant grid (below).

## 2. Linear B positive control — detector is LIVE (on the consonant axis)

| | best seqLL | %ile vs random-φ | occupied cells | C-axis AMI (nmi / perm-p) | V-axis AMI (nmi / perm-p) |
|---|---|---|---|---|---|
| Linear B (13,562 wordforms, 80 core signs) | −3.3225 | 100.0 | 34 | **0.504 / 0.024** | 0.107 / 0.204 |

The balanced search recovers the true Linear B **consonant** partition significantly (perm-p 0.024) — matching
the campaign's standing wave-2 finding that the *consonant* axis is the recoverable one on Linear B. The
vowel axis is not recovered by this objective (perm-p 0.204), a known limitation of a factored-bigram
likelihood as a phonology detector. **The apparatus can detect real CV structure where it exists**, so a
Linear A null is informative, not merely powerless.

## 3. Linear A — best system vs nulls

| grid | best seqLL | random-φ mean / p99 | %ile | occ. cells | C-axis perm-p | V-axis perm-p | MDL bits |
|---|---|---|---|---|---|---|---|
| C12 | −3.1742 | −3.76 / −3.69 | 100.0 | 25 | 0.235 | 0.210 | **8,590 (min)** |
| **C15** | **−3.2942** | −3.762 / −3.694 | 100.0 | 23 | **0.046** | 0.592 | 9,363 |
| C18 | −3.3974 | −3.76 / −3.69 | 100.0 | 31 | 0.020 | 0.311 | 10,191 |

At face value the best Linear A system beats the random-φ 99th percentile (condition a ✓) and the C15 winner's
consonant grade is *nominally* p=0.046. **Both are artifacts**, shown by the two controls below. MDL selects
the smallest grid (C12), i.e. the data does not pay for finer structure.

## 4. The two decisive controls — why the apparent signal is NULL

**(A) Permuted-corpus control (condition b — the killer).** Shuffling sign tokens within word positions
destroys all bigram phonotactics while preserving lengths + unigram marginals. The seqLL gain over the
random-φ median is:

- real corpus: **0.469 nats/token**  ·  permuted corpus: **0.462 nats/token**  ·  **ratio 1.014**.

The improvement over chance is **entirely reproduced on phonotactically-destroyed data** ⇒ the seqLL channel
carries **no** real sequential value-structure; the "gain" is the balanced search fitting held-out marginals.
Condition b (ratio > 2) **FAILS**. This is the third-plus independent confirmation of a null value layer.

**(B) The consonant-axis grade does not survive its own controls.**
- *Permuted-corpus match:* the permuted-corpus winner's consonant-axis nmi is **0.525** vs the real winner's
  **0.558** — excess only **0.033** (ratio 1.06). A value system chosen on destroyed data aligns with Linear B
  consonants essentially as well as one chosen on real data ⇒ the alignment is a property of the balanced
  search, not of Linear A structure.
- *Grid instability:* consonant perm-p swings 0.235 → 0.046 → 0.020 monotonically with |C| — a granularity
  statistic, not a stable phonological fact.
- *Multiplicity (Art. VIII):* 6 grid×axis grade tests. Holm-Bonferroni: min adjusted p = **0.123** — **nothing
  is significant** after correction (`robustness` block, `i1_robustness.py`).

## 5. Constraint terms contributed nothing decisive

At the winner: relAgree 0.296, formConsist 1.0, morphCompat 0.265, crossCompat 0.682 (the cross-script term
is at its balanced-baseline; consistent with the campaign's cross-script NULL). Their combined weight (≤0.04)
is ~1% of the seqLL scale (~3.3 nats): by design they only break ties, and per Constitution truth-layer caps
they cannot decide. Anchor-consistency term = 0 (SEED_A=0, no secure anchors) — recorded, contributes nothing.

## 6. Frozen verdict conditions

| condition | requirement | result |
|---|---|---|
| a — best seqLL > random-φ p99 | yes | ✓ (but see §4A) |
| b — real gain > 2× permuted gain | **ratio 1.014** | ✗ **FAIL** |
| c — winner axis aligns with LB above perm-null | C-axis raw p 0.046 | ✓ raw, ✗ after multiplicity (Holm 0.123) |
| LB detector fires | consonant perm-p < 0.05 | ✓ (0.024) |

Detector is live; the pivotal honesty condition (b) fails and the one nominal signal (c) is multiplicity- and
permutation-refuted ⇒ **`UNDERDETERMINED_NO_RECOVERY`**. No value-bearing system beats the honest nulls, and
none yields any basis for a held-out reading. Highest claim layer unchanged at **L2/L3** (anonymous structure);
no phonetic value recovered or assigned.

## 7. Placement in the campaign

This adds a **new agnostic channel** — compact value-system search under a combined held-out-likelihood +
relative-constraint objective, with two independent search methods — to the already-closed value layer. It
returns the same verdict as position→C/V (refuted), substitution-on-LA (underpowered), cross-script (null),
anchors (SEED_A=0), seed-propagation (frequency artifact) and multi-view fusion (no recovery): **the corpus
does not identify a phonetic value system.** The equivalence-class accounting (`I_EQUIVALENCE_CLASSES.md`)
quantifies *why*: any candidate has ≥10²⁷ symmetry-equivalent twins on a landscape the honest objective cannot
distinguish from chance.
