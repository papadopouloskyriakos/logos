# Power curve + synthetic lab + WP6 agnostic search — the obstacle, fully quantified

## Seed-propagation power curve → `QUANTIFIED`
Subsampled Linear B; at each size ran the WP5 reduced-seed C/V bootstrap (3 vowel + 3 consonant seeds),
held-out AUC over 24 subsamples × seed combos. AUC crosses **0.70 at ~2620 wordforms** (bracket 2000–3500);
monotone 0.647→0.752 over 539→13562 wf. **Linear A (539 wf) sits at ~chance → needs ~4.9× its corpus (bracket
3.7–6.5×)** for the C/V bootstrap to fire — a *lower* bound (LA is below its size-matched LB point). The WP5
propagation NULL is **corpus-starvation, not a broken detector**.

## Synthetic recovery lab → `QUANTIFIED` (5/5)
Generative CV-syllabary with a *soft* planted onset-vowel bias (calibrated so synthetic-LB reproduces real-LB
recovery ~0.83, not a trivial 1.0) + inflectional endings (the substitution signal).
1. **Positive control** (LB-scale, word-segmented): position AUC 0.778, substitution fires 100% (z=3.72), WP5 0.677.
2. **Calibrated failure** (SAME language, LA-scale, packed): position AUC 0.536 (CI straddles chance), substitution
   0%, WP5 0.548 — **NO_POWER, not a false positive**.
3. **Wrong-language rejection**: position ~chance, substitution 0% at *every* scale to 43868 tokens.
Thresholds: **CORPUS axis** — recovery (AUC≥0.75) needs ≥8000 tokens word-segmented ≈ **1.88× LA**; LA-*packed*
never clears 0.75 (the **segmentation tax**). **SIGNAL axis** — at a realistic signal the binding constraint is
corpus SIZE, not signal absence. **Mechanically proves LA's empirical nulls are corpus-power-limited, not method
failures** (the machinery recovers the signal at scale and refuses to hallucinate it when underpowered/wrong-language).

## WP6 agnostic search over the reduced space → `AT_END_TO_END_NULL`
Bounded reduced-K-class value search on real LA (objective = held-out likelihood + WP3.2 substitution + WP3.1
C/V prior; fixed beam/iterations/penalty). Real held-out gain +0.0134 nats/token **beats the order-shuffle null
(z=+8.5)** — LA has real sequential structure — but **fails the decisive value-specific nulls**: wrong-language
opaque Linear B scores *higher* than LA through the identical pipeline (FWER_W=1.0, z=−2.1); the random-prior
null on LA sits *at* real (FWER_R=0.5). **Pooled decisive FWER = 0.71 ≫ 0.05.** The objective detects generic
linguistic order, not a LA value map — the necessary-not-sufficient trap, correctly separated by the multi-family
null. No value map recovered.

## Synthesis — the search space, materially sharpened (a mission objective)
The value layer is **reopened** (internal evidence is not value-blind, WP1) and the obstacle is now **fully
quantified and mechanically validated**: Linear A is **corpus-power-limited** for the validated relative channels —
it needs **~2–5× more corpus AND word segmentation**, plus 3–4 seed C/V labels (which *exist*: A, I, U). The
methods fire on known-script + synthetic truth and reject wrong-language, so this is a property of the LA corpus,
not the tools. No reading is earned; no candidate survives the end-to-end null. **This is a precise, corrected,
actionable replacement for the prior campaign's overstated impossibility claim.**
