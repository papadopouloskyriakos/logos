# EPOCH-065 REPORT — Word-length site register beyond document class (L2)

**Verdict: `WORDLEN_SITE_REGISTER`** (PC PASSED; stratified combined site effect significant; ≥2 classes individually significant — a GENERAL register).

## Question
E028 established that word-length (sign count) carries a strong DOCUMENT-CLASS signature that is
cross-site robust (the FUNCTIONAL axis). This epoch asks the orthogonal SITE question: **controlling
for document class, is there residual SITE variation in word-length** — a site-level scribal register —
or is word-length fully determined by document function (cross-site-invariant given class)?

Layer **L2** only: word-length = `len(signs)` (structural count; no sign values, no readings, no meaning).

## Discipline (non-circular)
- word-length = `len(word)` where `word` is a sign-list (structural).
- document class = corpus `support` field (physical, given).
- site = corpus `site` field (findspot, given).
- **STRATIFIED null** permutes SITE labels WITHIN each class, preserving the class word-length multiset
  and each site's n-in-class. Any detected effect is site variation BEYOND class.

## Data
Source: `corpus/silver/inscriptions_structured.json` (1341 inscriptions). Testable classes = `support`
classes with ≥2 sites having ≥30 words each:

| Class | Eligible sites (≥30 words) |
|---|---|
| Tablet | Arkhalkhori, Haghia Triada, Khania, Phaistos, Tylissos |
| Roundel | Haghia Triada, Khania |
| Stone vessel | Iouktas, Palaikastro, Zakros |

## Metric (frozen)
Per class `c`: tie-corrected Kruskal-Wallis H on word-length grouped by SITE
(`H_corr = H_raw / (1 - Σ(t³−t)/(N³−N))`; word-lengths are small integers → heavy ties).
Combined statistic = Σ obs_H[c]. Stratified null: ≥2000 draws, permute site labels within each class.

## Positive control (gates verdict) — SYNTHETIC, stated
- **DETECT**: planted a residual site-register effect (one site's word-lengths shifted +1 within a class,
  class distributions otherwise equal) → combined perm **p = 0.0** (flagged). ✓
- **FALSE-POSITIVE**: class-only data (word-length depends only on class; site labels random within class)
  → **0 / 20** rejections (≤ 0.10). ✓
- Sanity: identical groups → H≈0; perfectly separated groups → H large. ✓
- **PC PASSED** → machinery informative.

## Results

### Stratified (within-class) site effect
| Class | obs_H | perm p | Site means (descriptive, untested) |
|---|---|---|---|
| Tablet | 45.25 | **0.0000** | Arkhalkhori 1.91, Haghia Triada 1.86, Khania 1.50, Phaistos 2.05, Tylissos 1.93 |
| Stone vessel | 29.93 | **0.0000** | Iouktas 3.76, Palaikastro 3.21, Zakros 2.17 |
| Roundel | 14.41 | **0.0000** | Haghia Triada 2.47, Khania 1.62 |

- **Combined**: obs_sum_H = **89.60**, perm **p = 0.0000**.
- n_classes_testable = 3, **n_classes_sig = 3** (≥2 → GENERAL register).

### Raw (uncontrolled) site effect — for contrast
- Raw site KW H (all words, sites ≥30 words, ignoring class) = **223.03**, perm p = 0.0000.
- Raw is ~2.5× the stratified combined H (89.60). **~60% of the raw site effect is class-confounded**
  (e.g., Iouktas/Palaikastro are Stone-vessel-heavy with long words; Haghia Triada/Khania are
  Tablet-heavy with short words). The stratified null removes this and a **~40% residual** survives as
  genuine within-class site variation.

## Verdict logic (frozen, mechanical)
PC passed ✓ AND stratified combined site effect significant (p=0.0000 ≤ 0.05) ✓ AND ≥2 classes
individually significant (3 of 3) ✓ → **`WORDLEN_SITE_REGISTER`**.

## Bottom line
**Yes — word-length carries a GENERAL site register BEYOND document class.** Controlling for support
class, sites still differ significantly in how long their words are, in all three testable classes.
This adds word-length REGISTER to the SITE-LOCAL side of the campaign's dichotomy (alongside
vocabulary/typology/sub-lexical). Document class is the dominant axis (it explains ~60% of the raw
site effect), but it does NOT fully determine word-length: a substantial residual site-level scribal
register remains. Structural word-length only; no reading. Layer L2.

## Outputs
- prereg: `experiments/linear_a_frontier_72h/epochs/EPOCH-065/prereg.md`
- plan_hash: `experiments/linear_a_frontier_72h/epochs/EPOCH-065/plan_hash.txt`
- machinery: `experiments/linear_a_frontier_72h/epochs/EPOCH-065/machinery.py`
- result: `experiments/linear_a_frontier_72h/epochs/EPOCH-065/result.json`
- data: `experiments/linear_a_frontier_72h/data/epoch_065/` (testable_class_site_wordlengths.json, class_site_summary.json)
