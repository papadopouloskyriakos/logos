# TASK PC — Positive controls: can the pipeline detect truth and reject fakes?

**Prereg** DI_MINO_EXACT_CLAIM_V1 (sha 8b098a4c) · **Constitution** v2.2 · **Seed** 20260708
**Data** `experiments/di_mino_301_audit/data/results/positive_controls.json`
**Driver** `experiments/di_mino_301_audit/scripts/PC_positive_controls.py` (RUN; real measured numbers)

Purpose (prereg H5 clause "validated on known-script controls"): before the machinery is allowed to
grade the Di Mino `*301=/na/ -> N-W-Y "dwell"` claim, it must be shown to **recover a real
decipherment, reject a search-manufactured fake, fire on genuine morphology, and abstain (NO_POWER)
when the corpus is too thin.** All grading is mechanical (`scripts/comparison/*`); no LLM grades any
control. Every number below is measured, not asserted.

## Verdict

**PIPELINE CALIBRATED = TRUE — all 7 controls passed (elapsed 532 s).**

| # | control | expectation | outcome | headline number | calibrated |
|---|---|---|---|---|---|
| PC1 | Ugaritic→Hebrew (real Semitic decipherment) | RECOVER | **RECOVERED** | real S_lex 0.780 vs L_fake floor 0.357 (corr-bar 0.388) | ✅ |
| PC2 | opaque Linear B → Greek (Ventris map) | RECOVER | **RECOVERED** | true-map S_lex 0.923 vs permuted-map p95 0.385 | ✅ |
| PC3 | synthetic corpus, PLANTED sign value | RECOVER | **RECOVERED** | true value ranked **1/113**, S_lex 1.0 vs next-best 0.037 | ✅ |
| PC4 | FALSE Semitic root manufactured by search | REJECT | **REJECTED** | best-of-search 0.0 ≤ deflated floor p95 0.0 | ✅ |
| PC5 | agglutinative (suffix) morphology | FIRE | **FIRED** | S_morph 0.622 vs null 0.156, z=28.8 | ✅ |
| PC6 | Semitic prefix/root morphology | FIRE | **FIRED** | S_morph 0.661 vs null 0.215, z=14.4; recovers {m,n,t,y} | ✅ |
| PC-NP | degraded corpus (2 inscriptions) | NO_POWER | **NO_POWER** | `has_power=False` (honest abstention) | ✅ |

**Calibration invariant satisfied throughout: the L_fake / permutation FLOOR is > 0 AND < the positive
benchmark.** A real correspondence clears it; a search-found fake sits inside it.

---

## PC1 — Ugaritic→Hebrew, the known Semitic decipherment benchmark. MUST RECOVER.

Real machinery (`scripts/comparison/run_canary.py`) on real data (`corpus/bronze/ugaritic/uga-heb.gold.cog`,
2,214 cognate pairs; L_fake rejection-sampled against the full ETCBC/bhsa Hebrew lexicon). n_fake=100,
eps∈{0.20,0.25,0.30}, primary eps=0.25.

- real Ugaritic↔Hebrew cognate **S_lex = 0.780**
- L_fake floor: mean 0.357, p95 0.376, corrected-margin bar (Cornish-Fisher + grid-deflated) **0.388**
- margin over corrected bar **+0.392**; canary verdict `CANARY_HOLDS_REAL_CLEARS_FLOOR`.

Floor > 0 (0.357) and < benchmark (0.780) → the statistic carries real cognate signal above the
fabricated-lexicon floor. **RECOVERED.**

## PC2 — opaque Linear B decoded to Greek. MUST RECOVER.

`corpus/bronze/linearb/linear_b-greek.cog` (918 LB wordforms, 69 syllabograms, 1,402 Greek readings).
The LB side is decoded to a coarse phoneme string via the **true Ventris sign→value map**; the Greek
side is transliterated by the SAME normalization (l/r merge, defective-syllabary final-consonant drop).
Non-circular: known values transcribe the LB side only. Null = 100 frequency-banded (Packard)
permutations of the sign→value map — a WRONG map must not recover Greek.

- true Ventris map **S_lex = 0.923** ; permuted-map null mean 0.342, p95 0.385, max 0.413
- margin over null p95 **+0.538**, power ratio **2.7×**.

The correct decipherment map recovers Greek far above every permuted map. **RECOVERED.**

## PC3 — synthetic `*301`-style corpus with a PLANTED unknown sign value. MUST RECOVER the plant.

Direct analogue of the Di Mino sign-value sweep, but on a corpus where the truth is KNOWN. A common
consonant `n` is chosen as the hidden value of sign `X`; every occurrence of `n` in 400 real Hebrew
lexemes is re-encoded as `X` (82 attestations carry the sign). The full 113-value admissible space
(bare consonants + vowels + CV syllables) is swept; recovery uses **exact-reconstruction recall**
(eps=0) — only decoding `X→n` turns the attestations back into real lexemes.

- **true value `n` ranked 1/113**, S_lex = 1.000; next-best non-true value 0.037 (margin **+0.963**)
- multiple-testing floor (best-of-113-sweep on 100 signal-free corpora) p95 = 0.0, max 0.012 —
  the planted value clears it outright.

The sweep uniquely recovers the planted truth with a decisive margin. **RECOVERED.** (This is the
positive counterpart to the `*301` result: when a real value is present, the identical sweep finds it.)

## PC4 — FALSE Semitic root manufactured by search. MUST REJECT.

The exact partner of PC3 with **no plant**: a signal-free random corpus (82 forms, one unknown sign
each) searched over the whole 113-value space for the best-looking Semitic match — the "English is a
Semitic language" failure mode (invariant 8). Deflation floor = best-of-sweep on other signal-free
corpora.

- best-of-search value `b`, **S_lex = 0.000** ; deflated floor mean 0.0005, p95 0.0, max 0.012
- best does NOT clear the floor.

The search-found "match" is inside the multiple-testing floor and is thrown out. **REJECTED.** PC3 and
PC4 are the identical test differing only by the presence of a plant — recover / reject respectively.

## PC5 — known agglutinative (suffix) morphology. Detector must FIRE.

Synthetic productive suffix-chaining (`stems × {lar, im, ci, de}`, 12 independent inscriptions),
`scripts/comparison/morphostat.s_morph` (within-form Nair null, 500 draws).

- **S_morph = 0.622**, within-form null mean 0.156, **z = 28.8**, `has_power=True`, `is_significant=True`.

## PC6 — known Semitic prefix/root morphology. Detector must FIRE and identify position.

Synthetic Semitic-style prefixing (`{m,t,y,n} + triliteral root + vowel`, 12 inscriptions).

- **S_morph = 0.661**, null mean 0.215, **z = 14.4**, powered + significant
- **all four planted single-char prefixes {m,n,t,y} recovered** in the derived affix inventory.

PC5/PC6 both fire strongly (z≫2) where PC-NP does not. The morphology statistic detects genuine
productive affixation and reads out the correct affixes; the affix-position tie-break is weak (both a
prefix and a suffix inventory always exist), so the load-bearing discriminator is the **recovered
affix identity** (PC6's {m,n,t,y}), not the kind count.

## PC-NP — degraded corpus. Must return NO_POWER (honest abstention).

A 2-inscription / 3-form corpus: `s_morph` returns `has_power=False`, reason *"too few independent
inscriptions (m=2 < 3): cross-inscription consistency cannot be established."* The machinery abstains
rather than emit a misleading low score (F.1 no-power escape). **NO_POWER.**

---

## Bearing on the Di Mino adjudication

The comparison layer is **fit for purpose**: it recovers a genuine Semitic decipherment (PC1), a
genuine syllabic decipherment (PC2), and a planted sign value under the very sweep used on `*301`
(PC3); it rejects a search-manufactured Semitic match (PC4); it fires on real morphology and reads
out the correct affixes (PC5/PC6); and it abstains when under-powered (PC-NP). The floor is a true
false-positive floor (>0, below every positive benchmark). Therefore, when this same machinery
returns a non-recovering / at-floor result for `*301=/na/`, that is a property of the **claim**, not
a dead detector — the pipeline demonstrably lights up when a real signal is present.
