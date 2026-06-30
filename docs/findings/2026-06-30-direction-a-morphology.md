# Finding 2026-06-30 — Direction A morphology: an honest NULL on the morphology claim (the L_fake bigram floor catches a 4th would-be confound) + a modest segmentation positive

Ran the pre-registered (`docs/prereg-morphology-2026-06-30.md`, frozen *before* the model touched the data)
unsupervised morphology / segmentation induction over the full Linear A corpus (1,341 inscriptions, 52
sites; `scripts/comparison/morphology.py`). CPU/laptop per the compute rule. Verifier: **SOUND, no
overclaim, 0 critical/high**; result independently re-run here.

## Headline — NO power to claim morphology (report the null)

| measure | value |
|---|---|
| pre-registered affixes that beat the within-form permutation null + the 16-way deflated bar | **4/16** (`i-*301`, `a-`, `i-`, `-te/-ti`) |
| **real** confirm rate | 0.250 |
| **shuffle** floor (within-word sign-order permutation) | **0.000** |
| **L_fake** floor (markov / 1st-order sign-bigram corpus, lexical overlap with real = 0.0) | **0.375** |
| `has_morphology_power` | **False** |

**Interpretation (the careful, honest conclusion).** The real affix signal **beats the shuffle floor
(0.25 > 0.00) — there IS recurring edge structure**, exactly as Davis/Thomas describe; Davis's `i-*301`
stem is strongly above the permutation null (6 distinct affix environments, z≈8.0, DSR-corrected
p≈1e-14). **BUT it does NOT beat the L_fake 1st-order bigram floor (0.25 < 0.375): the apparent
affixation is fully reproducible by a sign-transition model.** On Linear A's short, mostly **1–2-sign
words**, "morphology" and "bigram order" are statistically **indistinguishable** — so we **cannot claim
validated morphology beyond sign-statistics**, and the module reports the null and makes no morphology
claim. This is the **fourth** would-be confound the discipline has caught (after the contamination
forced-1.0, the baseline-ceiling, and the L_virgin coverage confound) — and the verifier confirms it is
*caught and reported as a null*, conservative in the under-claiming direction, not presented as a result.

> This does **not** refute Davis/Thomas. Their structural observations stand; what the test shows is that
> on this corpus their affixes are not *statistically separable from bigram structure* — a limit of the
> data (short words), not of their analysis. A rigorous, pre-registered negative on a specific set of
> field claims is itself the referee artifact the field lacks.

## Word-length premise — measured, and reconciled with Fuls 2015 (added 2026-07-01)

The "short words" premise is load-bearing, and Braović et al. (2024, p. 733) cite **Fuls 2015** for a
Linear A **average word length of 3.3 signs** — superficially in tension with "1–2-sign words." Both
are correct; they count **different denominators** (`morphology.word_length_distribution()`, generated
per invariant 12):

| measure (signs/word) | value |
|---|---|
| word-tokens, all (the denominator the morphology test consumes) | **mean 1.84, median 1, mode 1** |
| % of word-tokens that are ≤2 signs | **76.1%** (56.5% are single-sign) |
| word-tokens, length ≥2 only | 2.93 |
| **distinct** words, length ≥2 only | **3.07 → recovers Fuls 2015's 3.3** |

So **Fuls's 3.3 is recovered (3.07) on distinct multi-sign words** — i.e. after de-duplicating and
excluding the ~56% **single-sign administrative/abbreviation tokens** (cf. the abbreviation channel in
`prereg-morphology-salgarella-addendum-2026-06-30.md`). On the tokens the test actually operates on,
words are short (median/mode **1**), which is *precisely why* morphology is not statistically separable
from bigram order. The premise stands; cite Fuls 2015 + report the distribution, never a single bare
"average." (Test: `test_word_length_distribution_reconciles_fuls_2015`.)

## The modest POSITIVE — word-boundary recovery beats chance

Leave-one-site-out (not k-fold — formulaic dependence), 52 sites: the DP-unigram (Goldwater-style)
segmenter recovers the scribe's word divisions at **micro-F1 0.436 vs a random-boundary baseline of
0.389** (boundary base rate 0.406) — a real, held-out, above-chance result. (Morfessor over-segments the
short syllabic corpus, micro-F1 0.156, flagged NOT usable — reported, not hidden.) So the *method* works
above chance even where the *morphology claim* does not survive the bigram floor.

## Method / discipline notes
- **Pre-reg fidelity verified:** exactly the 16 frozen Davis/Thomas/Duhoux-Valério affixes tested, none
  added or tuned to fit; the two broadened predictions (`t-` → t-series; `-te/-ti` → {TE,TI}) are flagged.
- **Falsification gate:** `has_morphology_power = (real n_confirm≥1) AND real_rate > max(shuffle, L_fake)`.
  The L_fake markov floor is the headline honesty gate (separates morphology from bigram order).
- **Multiplicity:** per-affix z vs a shared permutation null; Šidák FWER over 16 trials; the §B.3
  order-statistic deflated bar; CONFIRM requires beating the bar AND DSR-corrected p<0.01 AND the
  distribution-free permutation p<0.05.
- **No phonetic claim** anywhere; `morphology.py` imports no `verdict.py`.
- Ensemble (Morfessor + DP-unigram), reported per-segmenter — never one cherry-picked model.

## Verified (independently re-run)
Full suite **290 passed, 4 xfailed** (+15 morphology tests); `has_morphology_power=False`, dp-unigram F1
0.436>0.389 reproduced. Raw result `runtime/morphology-real.json` (gitignored). Build commit pending.

## Implication for the draft
Direction A delivers two paper-grade results: (1) a **rigorous, pre-registered NULL** on the Davis/Thomas
morphology claims for this corpus (the affixes are real edge structure but bigram-reproducible), and (2) a
**validated word-boundary segmenter** that beats chance. Both are honest and field-relevant. Direction D
(metrology) is the remaining, more tractable substantive surface before drafting.
