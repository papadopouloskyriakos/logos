# EPOCH-048 — SIGN-LEVEL HELD-OUT REDUNDANCY / ENTROPY RATE

**Campaign:** Linear A frontier-72h · **Epoch:** 048 · **Layer:** L2/L3 (sign-sequence statistics)
**Operator:** logos z.ai research worker (GLM-5.2) · **Discipline:** STRICT LOGOS
**Verdict (mechanical, frozen rule):** `SIGN_SEQUENCE_NEAR_RANDOM`

---

## 1. QUESTION (frozen)

Does the Linear A **sign sequence within words** carry language-like sequential redundancy
that **generalizes to held-out data** — i.e. does a first-order sign Markov model achieve
lower held-out cross-entropy than a sign-unigram baseline, and does this hold across a
site-blocked split? Also: estimate the per-sign **entropy rate**.

Pure sign-sequence statistics (L2/L3). Signs are **ANONYMOUS identifiers** — no phonetic
values, no sound, no meaning, no reading, no language identification. "Redundancy" is an
information-theoretic quantity, not a decipherment or language-ID claim.

## 2. DATA (verified)

- `corpus/silver/inscriptions_structured.json` — word tokens `t=='word'` with `signs`.
- **3,147 words**, **259-sign vocabulary**, mean word length **1.84 signs**.
- **56.5 % of words are single signs** (length 1) — a structural fact that matters below.
- LB positive control via `load_b_damos()[0]`: 13,562 words, 89-sign vocab, mean len 3.23.

## 3. METHOD (frozen)

- **Markov**: first-order `P(next | cur)` with add-k smoothing; BOS/EOS boundaries per word.
- **Baseline**: sign-unigram (add-k) on the same vocabulary.
- **Cross-entropy** (bits/sign): mean per-word, denominator = number of signs in the word.
- **k** chosen on TRAIN via internal train/val split over `{0.01,0.05,0.1,0.2,0.5,1.0}`.
  (Selected k = 0.05 in every LA fold.)
- **Splits**: (a) random 5-fold CV; (b) site-blocked leave-one-site-out, sites with ≥30 words.
- **Significance**: order-shuffle null (permute interior signs of each TEST word; R=200);
  p = fraction of shuffles with shuffled-improvement ≥ observed.
- Held-out discipline: train on TRAIN only, evaluate on TEST only.

## 4. POSITIVE CONTROL (gates the verdict) — **PASSED**

| Check | Result |
|---|---|
| **DETECT** (LB, a real language): Markov improvement over unigram | **+0.260 bits/sign**, p = 0.0 ✓ |
| **FALSE-POSITIVE** (order-shuffled LA words, 20 sets): fires (imp>0 & p≤0.05) | **0 / 20** (rate 0.00) ✓ |

The machinery **detects** language-like sequential redundancy where it exists (LB) and does
**not** fire on structure-destroyed (shuffled) data. It is informative. PC gates the verdict.

## 5. LA GLOBAL — 5-fold CV

| Quantity | Value |
|---|---|
| Markov held-out xent (**entropy rate**) | **7.576 bits/sign** |
| Unigram held-out xent (**unigram entropy**) | **6.577 bits/sign** |
| **Improvement (unigram − Markov)** | **−0.999 bits/sign** |
| Order-shuffle p | 0.0 |

The first-order sign Markov is **worse than the unigram** on held-out LA data by ~1 bit/sign.
The negative improvement is reliable (p=0.0 in the sense that the Markov's deficit is
consistently below the shuffled null). **There is no generalizable first-order sign-sequential
redundancy in LA words.**

For comparison, the **LB entropy rate is 5.420 bits/sign** (more predictable; lower entropy
rate) and LB shows **+0.260 bits/sign** Markov improvement — the contrast is real.

## 6. LA SITE-BLOCKED (leave-one-site-out, ≥30 words)

10 qualifying sites. Per-site improvement (bits/sign):

| Site | n_test | improvement | p |
|---|---|---|---|
| Haghia Triada | 1891 | −1.93 | 0.00 |
| Khania | 368 | −1.80 | 0.00 |
| Zakros | 218 | −1.61 | 0.00 |
| Phaistos | 110 | −1.82 | 0.00 |
| Knossos | 98 | −2.05 | 0.045 |
| Palaikastro | 77 | −0.87 | 0.00 |
| Arkhalkhori | 63 | −1.18 | 0.00 |
| Tylissos | 43 | −2.28 | 0.025 |
| Malia | 41 | −4.34 | 0.025 |
| Iouktas | 39 | **+0.33** | 0.00 |

**Sites where Markov beats unigram (imp>0 AND p≤0.05): 1 / 10** (only Iouktas, the smallest
qualifying site). Sequential redundancy does **not** generalize across sites.

## 7. ROBUSTNESS (post-hoc, not used for verdict — confirms it is not an artifact)

The frozen cross-entropy definition gives the Markov one extra predicted position per word
(the `sL → EOS` transition) that the unigram does not carry. For the 56.5 % of LA words that
are single signs this doubles the Markov's per-sign cost. I verified the negative verdict is
**not** a definitional artifact:

| Variant | LA improvement (bits/sign) |
|---|---|
| Frozen definition (used for verdict) | −0.999 |
| **Symmetric** definition (same predicted positions for both models) | **−0.159** |
| Frozen definition, **length-≥2 words only** | **−0.736** |
| LB, symmetric definition (reference) | **+0.670** |

Under every fair definition LA improvement is **negative**; under the same definitions LB is
**strongly positive**. The machinery detects redundancy in a real language and LA genuinely
lacks generalizable first-order sign-sequential structure.

## 8. FROZEN MECHANICAL VERDICT

Rule applied (PC passed; global CV improvement **not** >0 significant; → NEAR_RANDOM):

> **`SIGN_SEQUENCE_NEAR_RANDOM`**

Not `LANGUAGELIKE_HELDOUT` (global improvement is negative, not positive). Not `SITE_LOCAL`
(global is not significant). Not `UNDERPOWERED` (10 sites ≥30 words). Not
`MACHINERY_UNINFORMATIVE` (PC passed).

## 9. BOTTOM LINE (honest)

At the **sign-within-word** level, Linear A does **not** show sequential redundancy that
generalizes to held-out data: a first-order sign Markov is *worse* than a sign-unigram on
held-out LA words (−1.0 bits/sign frozen; −0.16 symmetric), and only 1 of 10 sites shows a
positive effect. The same machinery finds **+0.26 bits/sign** (frozen) / **+0.67 bits/sign**
(symmetric) of genuine sequential redundancy in Linear B. The most likely structural cause is
the combination of a large sign vocabulary (259), very short words (mean 1.84 signs; 56.5 %
single-sign), and hence far too few transition observations per context for a first-order model
to learn anything that generalizes. **This is a statement about the absence of generalizable
first-order sign-sequential structure at the within-word level — it is NOT a claim that LA is
or is not a language**, and it does not rule out structure at other levels (between-word order,
positional templates, sparse frequent bigrams). Signs remain anonymous throughout; the metric
is purely information-theoretic.

## 10. SUCCESSOR HYPOTHESES (≥5)

- **H1** Higher-order / sparse-prior Markov (interpolated Kneser-Ney, Dirichlet prior) may
  extract weak structure the add-k first-order model misses.
- **H2** Test redundancy at the **word-token** level (word n-grams across an inscription)
  rather than sign-within-word.
- **H3** Sign-bigram frequency-spectrum / Zipf analysis: a small set of frequent pairs may
  carry structure even when the full transition matrix does not generalize.
- **H4** Restrict to length-≥3 words (rare longer LA words) and re-test there.
- **H5** Compare LA entropy rate to a matched-random iid null (same unigram marginals).
- **H6** Cross-script transfer: train Markov on LB, evaluate on LA held-out.
- **H7** Positional/templatic structure (sign-position-within-word distributions) instead of
  Markovian transitions.

## 11. NON-CIRCULARITY

Signs are anonymous ids throughout. No phonetic values, sound, meaning, reading, or language
identification was used or inferred. LB was used **only** as a positive-control benchmark.
The redundancy metric is purely information-theoretic (held-out cross-entropy of anonymous sign
sequences). A negative result means LA sign-within-word sequences lack generalizable
first-order sequential structure; it is not a language-identification claim.

## 12. ARTIFACTS

- prereg: `experiments/linear_a_frontier_72h/epochs/EPOCH-048/prereg.md`
- plan_hash: `experiments/linear_a_frontier_72h/epochs/EPOCH-048/plan_hash.txt`
- machinery: `experiments/linear_a_frontier_72h/epochs/EPOCH-048/machinery.py`
- result: `experiments/linear_a_frontier_72h/epochs/EPOCH-048/result.json`
- data: `experiments/linear_a_frontier_72h/data/epoch_048/` (e048_run_data.json, site_word_counts.json)
