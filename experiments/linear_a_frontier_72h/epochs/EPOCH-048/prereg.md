# EPOCH-048 — SIGN-LEVEL HELD-OUT REDUNDANCY / ENTROPY RATE

**Campaign:** Linear A frontier-72h · **Epoch:** 048 · **Layer:** L2/L3 (sign-sequence statistics)
**Operator:** logos z.ai research worker (GLM-5.2) · **Discipline:** STRICT LOGOS

## QUESTION (frozen)
Does the Linear A **SIGN sequence within words** carry LANGUAGE-LIKE sequential redundancy that
**GENERALIZES to held-out data** — i.e. does a first-order sign Markov model achieve lower
held-out cross-entropy than a sign-unigram baseline (redundancy ⇒ rule-governed sequence, as in
real language), and does this hold across a **site-blocked** split? Also estimate the per-sign
**entropy rate**. This tests whether LA output is structured / language-like vs near-random at
the sign level.

Pure sign-sequence statistics (L2/L3): signs are **ANONYMOUS identifiers**. NO phonetic values,
NO sound, NO meaning, NO reading, NO language identification.

## NON-CIRCULAR / DISCIPLINE (hard)
- Signs are anonymous ids. NO phonetics / sound / meaning / reading / language-ID. L2/L3 ONLY.
- LB used as POSITIVE-CONTROL benchmark only (control-only).
- Prereg + plan_hash FROZEN BEFORE running. PC FIRST. Mechanical verdict from a FROZEN rule.
- Held-out split respected: train transition / unigram probs on TRAIN only; evaluate
  cross-entropy on TEST only.

## DATA (verified)
- `corpus/silver/inscriptions_structured.json` — word tokens `t=='word'` with `signs`.
- Model the SIGN sequence within each word; add BOS / EOS per word.
- ~259-sign vocabulary; ~3147 words; mean word length ≈ 1.84 signs.
- Corpus path: BASE/corpus then repo-root.
- LB PC via `load_b_damos()[0]` (LB word sign-sequences; ~13,562 words, 89-sign vocab).

## METHOD (frozen)
- **First-order sign Markov** `P(next_sign | cur_sign)` with Laplace / add-k smoothing. Choose
  `k` on TRAIN (minimize TRAIN held-out-style xent via internal split; disclose k). Train on
  TRAIN words; evaluate mean per-sign cross-entropy (bits) on TEST words.
- **BASELINE** = sign-unigram (add-k) on TRAIN, eval on TEST.
- **IMPROVEMENT** = `baseline_xent − markov_xent` (bits/sign; >0 ⇒ sequential redundancy).
- **ENTROPY RATE** = Markov held-out xent (bits/sign). **Unigram entropy** = unigram xent.
- **Splits:**
  - (a) RANDOM 5-fold CV (global).
  - (b) SITE-BLOCKED: train all-but-one site, test held-out site, for sites with ≥30 words.
- **Significance** via order-shuffle null: shuffle each TEST word's sign order; the Markov
  model's improvement on the unshuffled TEST must exceed the shuffled null (permutation p).

### Cross-entropy definition (frozen)
For a TEST word `w = [BOS, s1, s2, ..., sL, EOS]`, per-sign cross-entropy (bits) under model M:
```
xent_M(w) = -(1/(L+1)) * [ log2 P(s1|BOS) + sum_{i=2..L} log2 P(si|s_{i-1}) + log2 P(EOS|sL) ]
```
The Markov conditions on the previous sign; the unigram ignores context (uses marginal P(sign)).
Mean over TEST words. (BOS→s1 and sL→EOS transitions count for the Markov; for the unigram the
context-free marginal is used for every position. The denominator L+1 = number of predicted
positions = number of signs in the word; BOS/EOS are boundary markers, not counted in the
denominator.)

### Smoothing (frozen)
Add-k (Laplace) with vocabulary = TRAIN sign vocab + {BOS, EOS}. `k` chosen by internal
train/val split of the TRAIN fold (try k ∈ {0.01, 0.05, 0.1, 0.2, 0.5, 1.0}; pick min val xent).
Same k applied to unigram baseline (for fair comparison the unigram also uses add-k over the
same vocab).

### Order-shuffle null (frozen)
For each TEST word, randomly permute its interior signs (keep BOS/EOS fixed). Recompute the
Markov improvement on the shuffled TEST set. Repeat R=200 times; p = fraction of shuffles where
shuffled_improvement ≥ observed_improvement. (Shuffling destroys sequential structure, so the
Markov should NOT beat the unigram on shuffled data; a significant observed improvement means
the structure is real, not noise.)

## PROTOCOL
0. Inspect: n words, sign-vocab size, mean word length, sign-unigram entropy.
1. FREEZE prereg (this file) + plan_hash; machinery.py with `__main__` self-check.
2. GLOBAL (5-fold CV): Markov held-out xent (entropy rate), unigram xent, improvement
   (bits/sign); order-shuffle null p.
3. POSITIVE CONTROL FIRST (gates verdict):
   - (a) DETECT — on LB word sign-sequences (a REAL language, known redundant), the sign-Markov
         must beat unigram (improvement > 0, p ≤ 0.05). [confirms machinery detects
         language-like redundancy]
   - (b) FALSE-POSITIVE — on order-shuffled words (no sequential structure), improvement ≈ 0
         (not significant) across ≥20 sets. If it cannot detect LB redundancy OR fires on
         shuffled → MACHINERY_UNINFORMATIVE.
4. LA MAIN — SITE-BLOCKED held-out: train all-but-one site, test held-out site; per-site
   improvement; count sites where Markov beats baseline (improvement > 0 AND order-shuffle
   p ≤ 0.05).
5. FROZEN MECHANICAL VERDICT:
   - **SIGN_REDUNDANCY_LANGUAGELIKE_HELDOUT** iff PC passed AND global CV improvement > 0
     significant AND site-blocked improvement > 0 in ≥3 held-out sites.
   - **SIGN_REDUNDANCY_SITE_LOCAL** iff global CV significant BUT site-blocked fails in most
     sites (<3).
   - **SIGN_SEQUENCE_NEAR_RANDOM** iff global CV improvement not significant (Markov ≈ unigram
     ⇒ little sequential redundancy).
   - **SIGN_REDUNDANCY_UNDERPOWERED** iff <3 sites have ≥30 words.
   - **MACHINERY_UNINFORMATIVE** iff PC failed.
6. WRITE OUTPUTS to the EXACT PATH CONTRACT paths.

## SCOPE / WHAT THIS IS NOT
- This is an information-theoretic redundancy measurement on anonymous sign ids. A positive
  result means LA sign sequences are non-random / rule-governed at the sequential level and
  generalize to held-out data — consistent with language-like output. It is NOT a language
  identification, NOT a decipherment, NOT a phonetic/meaning claim.
