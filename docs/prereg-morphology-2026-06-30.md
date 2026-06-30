# Pre-registration — Linear A morphology / segmentation induction (Direction A)

**Registered: 2026-06-30, BEFORE building or running any segmentation/morphology model** (the git commit
of this file is the timestamp). Per the logos discipline harness: predictions are fixed here so the model
cannot be tuned to them after the fact (invariant 8; the "grade from artifacts, never narration" rule).

## What is being tested
Whether an unsupervised morphology/segmentation ensemble over the full Linear A corpus, validated against
the scribe's own word-dividers, **recovers (confirms) / extends / or refutes** the published, field-accepted
*structural* claims about Linear A — WITHOUT any phonetic-value claim. These are the predictions whose
confirmation an Aegean epigrapher would accept.

## H1 — Word-order / verb structure (Davis)
Source: B. Davis, "Syntax in Linear A: The Word-Order of the 'Libation Formula'", *Kadmos* 52 (2013);
*Minoan Stone Vessels with Linear A Inscriptions*, Aegaeum 36 (2014).
- **H1a:** the libation-formula first sequence is the **verb**, with a stable root **`i-*301`** carrying
  changing affixes (the "if not the verb, the text would require OSV (<1% of languages)" argument).
- **H1b:** dominant constituent order is **V-S-O**.
- *Test:* does the induced segmentation place a recurring morpheme boundary isolating `i-*301` as a stem
  with variable affixes across the libation corpus, at a rate above the permutation null?

## H2 — Verbal affix inventory (Thomas)
Source: R. Thomas, "Some reflections on morphology in the language of the Linear A libation formula",
*Kadmos* (2020).
- **Prefixes:** `a-/ja-`, `ta-`, `na-`, `t-`.
- **Suffixes:** `-wa-/-u-`, `-ja-`, `-ti-`, `-nu-`, `-e-`, `-de-`, `-ka`.
- *Test:* each pre-registered affix must recur on **≥2 distinct stems** (the productivity gate from
  `morphostat`) across **independent inscriptions**, at frequency **above the within-form permutation null**,
  and survive **Deflated-Sharpe** correction for the number of affixes tested (target **p < 0.01** corrected).

## H3 — Nominal affixes (Duhoux / Valério)
- `i-` = locative/allative "to/in"; `-te / -ti` = ablative/genitive "from/of".
- *Test:* same productivity + above-null recurrence test as H2, on non-libation (administrative) words.

## Validation protocol (fixed in advance)
1. **Held-out ground truth:** the scribe's word divisions (`words` field of the structured re-ingest) +
   the `𐄁` divider glyph. Boundary-recovery scored by precision/recall/F1 of predicted vs scribe boundaries
   on **held-out inscriptions** (leave-one-site-out, not ordinary k-fold — formulaic dependence).
2. **Null models (must FAIL on these):** (a) sign-order shuffle within each inscription; (b) the **L_fake**
   fabricated-language corpus. The model must NOT "find morphology" / beat boundary-recovery chance on
   either — if it does, the method is overfitting and the result is void.
3. **Multiplicity:** all pre-registered affixes (H2+H3) tested jointly; Deflated-Sharpe / effective-n
   correction applied; report the corrected p per affix.
4. **Ensemble:** Morfessor Baseline + a hierarchical Pitman-Yor / Adaptor-Grammar segmenter + a neural span
   segmenter; report each + their agreement (not a single cherry-picked model).
5. **No phonetic claim.** A confirmed affix is a *structural* (paradigmatic) object; sign *values* are imputed
   only where internal slot-alternation constrains them, never from cross-script phonetics.

## Acceptance / outcomes (any is a publishable result)
- **CONFIRM:** ≥1 pre-registered affix (H2/H3) survives the null + DSR at p<0.01 AND boundary recovery beats
  permutation null on held-out — a validated structural result extending Davis/Thomas computationally.
- **EXTEND:** a *new* recurring affix/paradigm not in H1–H3 survives the same gate (flagged as exploratory,
  hierarchical-FDR not FWER).
- **REFUTE / NULL:** a pre-registered affix does NOT survive — reported honestly (the field benefits from a
  rigorous negative on a specific claim).
- **NO POWER:** the corpus is too short/formulaic for the test to discriminate (S_morph-style no-power) —
  reported as such, not as a refutation.

*Counts and corpus state are generated, not hand-written. This file is frozen at commit time; any change is
a new dated pre-registration, never an edit of this one.*
