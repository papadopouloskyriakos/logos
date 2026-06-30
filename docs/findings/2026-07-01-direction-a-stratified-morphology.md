# Finding 2026-07-01 — Direction-A STRATIFIED morphology re-run (#20): the pooled null HOLDS under stratification, and sharpens

Executes the two dated pre-registration addenda (`prereg-morphology-stratification-addendum-2026-06-30`
+ `prereg-morphology-salgarella-addendum-2026-06-30`) over the full corpus
(`scripts/comparison/morphology_stratified.py`). Induces the FROZEN pre-registered affix panel **per
genre stratum**, tests **cross-stratum stability** above a **per-affix L_fake bigram floor**, with the
**abbreviation channel excluded** and **within-site** non-independence controlled (hands are
unavailable for Linear A — TASK #19). Graded from the persisted artifact
(`runtime/morphology-stratified.json`). CPU/laptop. NO phonetic claim; imports no `verdict.py`.

## Headline — NULL: no validated cross-stratum morphology

| stratum (genre, from GORILA `support`) | inscriptions | words | sites | real-confirm | passes L_fake floor |
|---|---|---|---|---|---|
| **admin** (tablets, bars) | 290 | 1,486 | 14 | `a-`, `-ti` | **`-ti`** |
| **libation** (stone vessels) | 124 | 413 | 28 | `i-*301`, `a-`, `ja-` | **`ja-`** |
| **other** (clay/metal/graffiti…) | 104 | 144 | 34 | `a-`, `-te/-ti` | **`-te/-ti`** |

Abbreviation channel **excluded**: 740 seal inscriptions (Nodule/Roundel/Sealing/Label, 771 words) +
333 admin list-headers. Chronological CV **declined** (corpus is 988/1341 ≈ 74% single-horizon LM IB).

- **Cross-stratum-stable affixes: none.** No pre-registered affix passes the bigram floor in ≥2 genre
  strata, so none is site-robust across strata either → **`has_validated_morphology = False`.**
- The affixes that do pass the floor (`-ti`, `ja-`, `-te/-ti`) each survive in **exactly one** stratum
  → they are **register features**, not validated language morphology.

## What stratification ADDED over the pooled null (two sharper facts)

1. **Even `i-*301` (Davis's verb stem) is bigram-reproducible in the libation register.** In the
   libation stratum the fabricated (markov, sign-bigram) L_fake corpus *also* confirms `i-*301`, `a-`,
   `ja-` — the libation formula is so repetitive that a 1st-order sign-transition model manufactures
   the apparent verb morphology. Davis's structural reading is not refuted (the formula's slot grammar
   is real); what the test shows is that on this corpus it is **not statistically separable from sign
   bigrams** — the same limit the pooled run found, now localized to the formulaic register.
2. **The would-be signals are register-specific.** `-ti` survives only in admin, `ja-` only in
   libation, `-te/-ti` only in other. An affix confined to one genre is a register/sandhi feature, not
   pan-corpus morphology — exactly the confound the within-permutation null (which preserves pooling)
   cannot catch, and the reason the stratification addendum was registered.

## The discipline caught a grading confound mid-build (recorded, not hidden)

The first implementation graded cross-stratum stability on **panel-CONFIRM** (an affix that beats its
own within-word permutation null + the DSR multiplicity bar). Scrutinizing the artifact showed the
prefix `a-` (the commonest word-initial sign) "confirming" in all three strata while `real == L_fake`
in admin — a bigram-trivial free-rider. Fixed by adding a **per-affix L_fake bigram floor**: an affix
counts as morphology only if it confirms on the real corpus **and NOT** on the fabricated corpus
(`morphology_affixes = real_confirmed − L_fake_confirmed`, union over 3 L_fake draws). `a-` is excluded
from **every** stratum by this floor (a regression test locks it). This is the same "beat the bigram
floor" lesson as the pooled finding, now enforced per-affix — and a sixth confound the
grade-from-artifacts rule caught.

## Method / discipline notes

- **Genre strata** from the `support` field (Salgarella 2025 §6): seal supports = the abbreviation
  channel (excluded); stone vessels = libation; tablets/bars = admin; rest = other.
- **Within-site control (#19):** Linear A hands are not individuated (Salgarella 2019), so the
  independence unit is the SITE; a candidate must be **site-robust** (borne across ≥2 distinct sites)
  in addition to cross-stratum stable. No affix reached even the cross-stratum bar, so site-robustness
  was not the binding constraint here.
- **Abbreviation channel** excluded before induction and **reported** (no silent truncation): seal
  inscriptions wholesale + admin-tablet ≤3-sign list-headers (votive first-words are dedicatory text,
  kept).
- **No phonetic claim.** A passing affix is a structural/paradigmatic object; no sign value is imputed.

## Verified (independently re-run)

Full suite green (+5 stratified tests; partitioning is deterministic — 740 seal / 290 admin / 124
libation / 104 other). Raw result `runtime/morphology-stratified.json` (gitignored).

## Implication for the draft

Direction A's negative is now **two-layer**: (1) the pooled pre-registered null on the Davis/Thomas
affixes (bigram-reproducible), and (2) the stratified null showing the residual signals are
**register-specific and still bigram-reproducible**, with hands unavailable to push further. A
rigorous, pre-registered, *stratified* negative on a specific set of field claims — with the grading
confound caught and reported — is a stronger referee artifact than the pooled null alone. Track-1
morphology is complete; the remaining substantive surface is Direction-D (data-limited) and the
Track-2 items.
