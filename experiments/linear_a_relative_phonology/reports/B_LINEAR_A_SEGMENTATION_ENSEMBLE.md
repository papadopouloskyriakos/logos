# B5 — Linear A Segmentation Ensemble (probabilistic boundary set)

**Task:** B5 · **Branch:** research/linear-a-relative-phonology-seals · **Constitution:** v2.2
(Art. III guilty-until-proven · VII search-receipt · VIII effective-n · XII no-grading-by-the-rule-that-made-it)
· **Seed:** 20260708 · **Script:** `scripts/b5_la_segmentation_ensemble.py`
· **Data:** `data/segmentations/la_ensemble.json`

## Question
Apply the **B3-validated** unsupervised segmentation families — and only those — to Linear A, and
report, for every inter-sign gap, six attributes: **boundary probability, cross-model agreement,
source representation, site stability, encoding sensitivity, damage sensitivity.** Per B4, any LA
segmentation is an **over-cut superset** (~0 skill over cut-everywhere at LA's hapax regime), so we
publish a **probabilistic boundary set with an explicit over-segmentation caveat**, never one
deterministic ground-truth segmentation.

## Validated families used (frozen B3 implementations, imported, not re-derived)
5 base models: **CUE_TP_min, CUE_BranchEntropy, BAYESIAN_unigram, MDL, FINITE_STATE_bigram**; plus
the B3 **MULTISCALE_ENSEMBLE** (≥2-of-4 vote of BE/Bayes/MDL/FST) reported separately. The supervised
`SUP_CLF_localcue` is excluded (uses labels; not transferable — per B3). Boundary probability =
**vote fraction over the 5 base models**; MULTISCALE is a derived decision, not double-counted.

## Non-circularity (Art. XII)
GORILA word dividers and every phonetic value are used **only to grade** (P/R/F1, over-cut ratio,
gold-discrimination AUC). They are **never** an input to any model. Models train unsupervised
(EM/cue rules) on sign streams; boundary probability is computed from model votes alone.

## Corpus
`corpus/silver/inscriptions_structured.json`: 1,341 inscriptions / 52 sites. Models train co-occurrence
on **all** streams; boundaries predicted on the **618** inscriptions with ≥2 signs (**4,451** internal
gaps, **1,806** GORILA gold boundaries, 259 distinct sign types). Perturbations: **site** =
leave-one-site-out retrain (52 folds); **encoding** = unicode-subscript folding (RA₂→RA; retrain,
gap indices align 1:1); **damage** = K=15 replicates of per-sign deletion p=0.15, full retrain, cuts
mapped back to surviving original gaps.

## Result 1 — the ensemble is an over-cut superset (B4 confirmed on real LA)
Grading vs GORILA (grading only). **All-cut baseline F1 = 0.5773.**

| boundary set | P | R | F1 | over-cut ratio | **margin vs all-cut** |
|---|---|---|---|---|---|
| prob ≥ 1/5 models | 0.417 | 0.950 | 0.580 | 2.28 | **+0.0023** |
| prob ≥ 2/5 | 0.421 | 0.854 | 0.564 | 2.03 | −0.0133 |
| prob ≥ 3/5 | 0.425 | 0.751 | 0.543 | 1.77 | −0.0343 |
| prob ≥ 4/5 | 0.443 | 0.674 | 0.535 | 1.52 | −0.0425 |
| prob = 5/5 (unanimous) | 0.492 | 0.301 | 0.374 | 0.61 | −0.2037 |
| MULTISCALE (≥2/4) | 0.415 | 0.787 | 0.544 | 1.90 | −0.0337 |

**No threshold beats cut-everywhere** (best margin +0.0023, at the ≈cut-everywhere threshold). Every
non-trivial threshold is **negative**. Per-model over-cut ratios: MDL 2.04, BranchEntropy 1.78,
FiniteState 1.75, Bayesian 1.67, TP_min 0.96 (the lone precision-balanced model, B4's signature),
MULTISCALE 1.90. This is **exactly** B4's LA-regime prediction (raw F1 ≈0.5–0.58 but zero real skill;
universal over-cut, recall≫precision). **The ensemble does not locate LA word edges.**

## Result 2 — boundary probability carries only a whisper of true-boundary signal
Ranking every gap by ensemble probability to discriminate gold boundaries (grading-only AUC, 0.5=chance):

- **ensemble prob → gold AUC = 0.565** — barely above chance. Higher agreement ⇏ true boundary.
- mean prob at **gold** gaps 0.706 vs **non-gold** gaps 0.639 (Δ +0.068): a real but tiny separation.
- 336/4,451 gaps (7.5%) are cut by **no** model; 1,106 (24.8%) are cut **unanimously** (5/5) — yet the
  unanimous set has P only 0.49. Consensus is a **frequency artifact**, not a correctness signal.

## Result 3 — SOURCE REPRESENTATION is the real boundary signal, not distribution
Each gap carries the independent structural marks reconstructed from the raw stream — a **row-break**
(`NL`), a **numeral closure** (`NUM`, entry end), or a **word-divider glyph** (`DIV`). These physical/
administrative marks predict GORILA gold boundaries **far better than any distributional model**:

| source-representation signal | gold-discrimination AUC |
|---|---|
| row-break `NL` | **0.875** |
| numeral closure `NUM` (entry end) | **0.752** |
| divider glyph `DIV` | 0.607 |
| **ensemble distributional prob** | 0.565 |
| prob + any structural mark | 0.857 |

**Headline:** LA word segmentation is recoverable mainly from the **layout/administrative channel**
(rows, numerals, dividers), which the B3 distributional families do not use and cannot match. The
probabilistic set is most trustworthy exactly where a model cut **coincides with a physical mark**;
a distribution-only cut with no mark is near-chance. (1,619/4,451 gaps carry ≥1 mark: NL 1,356,
NUM 909, DIV 387.)

## Result 4 — stability attributes (per cut gap; means over 4,115 cut gaps)
| attribute | mean | reading |
|---|---|---|
| **site stability** (LOSO) | **0.841** | ~16% of the base vote is lost when the gap's own site is held out |
| **encoding sensitivity** (subscript fold) | **0.968** | boundaries are near-invariant to subscript-variant encoding (folding touches 128/5,792 tokens) |
| **damage sensitivity** (15% deletion) | **0.866** | ~13% of the vote is lost under damage on gaps whose flanks survive |

**Crucial null: stability does NOT track truth.** Gold vs non-gold cut gaps have essentially equal
(or inverted) stability — site 0.815 gold vs 0.860 non-gold; encoding 0.973 vs 0.965; damage 0.865
vs 0.867. **A stable ensemble cut is no more likely to be a real boundary than an unstable one.**
Stability describes the *robustness of the model's decision*, not its correctness — so it must not be
used to promote a boundary. (This mirrors the campaign-wide finding that internal evidence is
value-blind: consensus/robustness ≠ ground truth.)

## The published object
`data/segmentations/la_ensemble.json` — per inscription, every gap records: `prob` (vote fraction),
`models` (which of the 5 fired), `multiscale` (bool), `struct` (source marks), `is_gold` (grading),
and for cut gaps `site_stab` / `enc_stab` / `dmg_stab` / `dmg_testable_frac`. Plus `grading`,
`per_model_vs_gorila`, `grading_signal`, and `summary` blocks. **Read `prob` as vote-share, not
P(true boundary).** No deterministic segmentation is asserted.

## Honesty / limits
- **Over-segmentation is not a bug to threshold away** — no threshold recovers skill (Result 1). Any
  downstream use must be robust to ~1.5–2.3× spurious cuts, or gate cuts on a **structural mark**.
- **Encoding perturbation is conservative** — subscript folding merges only 4 sign types / 128 tokens;
  a deeper paleographic re-encoding (toward the ~92-sign functional syllabary) is out of scope here.
- This is an **L2/L3 structural** result (sign-string boundaries). **No phonetic/semantic/lexical
  licence** is earned or implied; probabilities are anonymous relative structure, no values assigned.

## Verdict
```
LA_SEGMENTATION_ENSEMBLE: DELIVERED as a PROBABILISTIC over-cut boundary set (not ground truth).
- B4 CONFIRMED on real LA: best margin over cut-everywhere = +0.0023 (prob>=1/5); every non-trivial
  threshold negative; universal over-cut (ratio 1.5-2.3, recall>>precision). Ensemble does NOT locate word edges.
- Boundary probability barely discriminates truth (prob->gold AUC 0.565).
- SOURCE REPRESENTATION dominates: physical/administrative marks recover boundaries far better
  (row-break AUC 0.875, numeral-closure 0.752) than distribution (0.565) -> LA segmentation is a
  layout/administrative signal, not a distributional one. Trust a cut most where it meets a mark.
- STABILITY (site 0.841 / encoding 0.968 / damage 0.866) is a robustness descriptor, NOT a truth
  signal: gold and non-gold cut gaps are equally stable (honest null).
LICENCE: L2/L3 structural only; no phonetic/semantic/lexical licence earned or implied.
```
