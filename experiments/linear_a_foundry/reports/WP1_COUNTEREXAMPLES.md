# WP1 — counterexamples (internal evidence breaks partial symmetry)

`scripts/wp1_symmetry_break.py` → `data/wp1_symmetry_break.json`. **The relabeling stopping theorem is
refuted as a universal claim.**

## Counterexample 1 — word position recovers the C/V partition (validated on known-truth LB)

A relabeling-invariant objective assigns identical scores to all sign permutations. Word-**position**
statistics do not: on Linear B (values known, vowels = {A,E,I,O,U}), word-initial-rate separates the 5 vowel
signs from the 72 consonant signs at **AUC 0.744, permutation p=0.035** (2000 perms). Ranks of the true
vowels by initial-rate: A=4, E=9, O=14, I=29, U=51 — front/back vowels A/E/O rank high (a-, e-, o- words),
consistent with Greek onset structure; the effect is real but single-feature-modest.

**This is the existence proof:** a position objective is `Sym(S)`-variant, so internal evidence is not
value-blind — it distinguishes the vowel class from the consonant class above chance.

## Counterexample 2 — applied to Linear A (non-circular)

Applying the same LA-internal position statistic (no LB values used), the top word-initial signs are
**A (rate 0.43), … I (0.20), U (0.18)** — the LA signs that *independently* correspond to vowels a/i/u under
the AB homomorphy. So LA's own position structure carries vowel-like information, reducing the C/V equivalence
classes without any external input. (The single feature also surfaces some CV signs — QE/KA/SI — so this is a
weak prior to be sharpened, not a finished partition; that is WP3's job.)

## What this changes

- The value layer is **not** provably closed to internal methods (WP1 theorem, §3).
- Internal evidence yields **relative** structure (C/V, similarity, morphology) that **reduces the sign-value
  equivalence classes**; external anchors are then needed only to fix absolute representatives, and *fewer*
  of them.
- The campaign's real, labor-intensive target is now defined: WP3 builds the multi-feature C/V + scribal-
  substitution + morphology recovery (validated on opaque LB); WP4 tests cross-script asymmetry; WP5 supplies
  the reduced external-anchor requirement; WP6 runs candidate rounds against the reduced space.

## Deferred / synthetic counterexamples (WP3, WP10)

Full synthetic corpora with planted phonology (recover planted C/V, similarity, paradigms) and opaque-LB
recovery of names/morphology are built in WP3 and the known-script laboratory (WP10), where the position,
substitution, and morphology channels are validated jointly before any LA application.
