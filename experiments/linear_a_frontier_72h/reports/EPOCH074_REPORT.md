# EPOCH-074 REPORT — Cross-Genre Lexicon Partition vs the Genre-Site Confound

**Campaign:** Linear A frontier-72h · **Epoch:** EPOCH-074 · **Layer:** L3 (structural lexicon overlap only)
**Verdict (mechanical, frozen rule):** `GENRE_SITE_CONFOUNDED_UNDERDETERMINED`
**PC:** SYNTHETIC, PASSED · **Anonymous word-forms (sign tuples, len≥2); NO reading, NO meaning.**

---

## 1. Question

The libation (religious) and administrative genres share almost no vocabulary (S_shared=20, Jaccard 0.024),
dramatically below a frequency-preserving token→genre permutation null (~69, p_below~0.0005). Naively this
screams "genre-specialized lexicons." **But** in this corpus GENRE and FIND-SITE are near-perfectly
confounded, and E071 already established Linear A vocabulary is SITE-local. **Mechanical question:** does
the lexicon partition SURVIVE controlling for site (a genuine genre effect BEYOND site), or is genre-vs-site
UNDERDETERMINED because the two are confounded?

## 2. Data & metric (verified pre-counts reproduced exactly)

- LIBATION = `support=='Stone vessel'`; ADMIN = `support in {Tablet, Nodule, Roundel}`.
- Word-FORM = tuple(signs), len≥2. **S_shared** = number of form types in BOTH genres.
- Reproduced: **lib 211 forms / 259 tokens; admin 651 forms / 948 tokens; S_shared=20; Jaccard 0.024.**

## 3. GLOBAL partition (context) — striking and real

| quantity | value |
|---|---|
| observed S_shared | **20** |
| GLOBAL null mean (5000 reps) | **68.87** |
| p_below (frac null ≤ obs) | **~0.0** |
| p_above | 1.0 |
| closed-form E[S] (indep. upper bound) | 188.56 |

The global partition is unambiguous: 20 shared forms vs an expected ~69 under frequency-preserving
token→genre shuffling (p_below≈0). The naive "genre-specialized lexicons" reading is well-supported
**globally**. *(The closed-form 188.56 is an independence-approximation UPPER BOUND that overestimates
because the global null is a single without-replacement permutation; the operative value is the Monte Carlo
mean 68.87, matching the verified pre-count ~69.)*

## 4. The confound — severe and structural

| confound metric | value |
|---|---|
| n_both_sites_ge10 (both genres ≥10 tokens) | **1** (Palaikastro 36 lib / 13 adm) |
| sites with both genres (any size) | 3 (Knossos 9/12, Palaikastro 36/13, Zakros 128/2) |
| n_swappable_tokens (tokens at both-genre sites) | **200 / 1207 (16.6%)** |
| genre_site_determinism (genre fixed by single-genre site) | **0.834** |

Every high-volume site is essentially single-genre: Haghia Triada 0 lib / 683 adm; Zakros 128 lib / 2 adm;
Khania 0/120; Iouktas 33/0; Syme 20/0. **83.4% of tokens have their genre fixed by their site.** Only
Palaikastro has both genres at ≥10 tokens.

## 5. SITE-STRATIFIED null (load-bearing) — no residual genre effect

Permute genre labels **only within each site** (site-membership fixed; only genre can change within a site).
This removes the site-locality explanation and isolates any residual genre effect.

| quantity | value |
|---|---|
| observed S_shared | **20** |
| site-stratified null mean (5000 reps) | **21.47** |
| p_below_sitestrat | **0.26** (NOT significant) |

Once site is controlled, the partition **vanishes**: obs 20 vs null 21.47, p=0.26. No residual genre-lexicon
effect is detectable beyond site.

## 6. Positive Control (SYNTHETIC) — PASSED, gates the verdict

The PC is the key honest test: is the site-stratified null result a real "no genre effect beyond site," or a
power failure? Three synthetic sub-controls:

| sub-control | result | criterion | pass? |
|---|---|---|---|
| (a) DETECT-BEYOND-SITE power | **power_est = 0.96** (24/25 reps flagged) | ≥ 0.5 | ✅ |
| (b) FALSE-POSITIVE (genre-neutral within site) | rejection **0.04** | ≤ 0.10 | ✅ |
| (c) GLOBAL-CALIBRATION partitioned corpus | obs 0 vs mean 123.24, p_below=0 (flagged) | flag | ✅ |
| (c) GLOBAL-CALIBRATION frequency-only corpus | obs 143 vs mean 150.24, p_below=0.16 (not flagged) | not flag | ✅ |

**PC VERDICT: PASSED.** The site-stratified control is **POWERED** (power_est=0.96) to detect a genuine
genre effect planted within both-genre sites, is **calibrated** (false-positive 0.04), and the GLOBAL null
is calibrated. So the null site-stratified result on the real corpus is **NOT a machinery power failure**.

## 7. Frozen mechanical verdict

Rule (verbatim from prereg):
- `GENRE_LEXICON_PARTITIONED_BEYOND_SITE` iff PC passed AND power_est≥0.5 AND p_below_sitestrat≤0.05.
- `GENRE_SITE_CONFOUNDED_UNDERDETERMINED` iff power_est<0.5 **OR n_both_sites_ge10<2**.
- `GENRE_LEXICON_OVERLAP_FREQUENCY_EXPLAINED` iff global p_below>0.05 AND p_above>0.05.
- `MACHINERY_UNINFORMATIVE` iff GLOBAL PC calibration fails.

Inputs: PC passed ✓ · power_est=0.96 ✓ · **p_below_sitestrat=0.26 (>0.05)** · **n_both_sites_ge10=1 (<2)** ·
global p_below≈0 (partition real, not frequency-explained) · global calib ok.

→ **`GENRE_SITE_CONFOUNDED_UNDERDETERMINED`** (fires on n_both_sites_ge10=1<2; corroborated by the
non-significant site-stratified result p=0.26).

## 8. Honest bottom line

**The striking global libation/admin lexicon partition (20 shared forms vs ~69 expected, p≈0) is REAL but
CANNOT be attributed to genre beyond E071's site-locality: genre and find-site are structurally confounded
in this corpus (only Palaikastro has both genres ≥10 tokens; 83.4% of tokens have genre fixed by site).**
The site-stratified control — proven POWERED and calibrated by the synthetic PC (power_est=0.96) — finds no
residual genre effect once site is fixed (obs 20 vs null 21.47, p=0.26). This is **not** a missed effect and
**not** a power failure of the machinery; it is an honest, design-limited **UNDERDETERMINED** verdict: with
only one informative both-genre site, genre and site cannot be separated, and the global partition is most
parsimoniously read as E071's site-locality re-expressed as "genre." The naive "genre-specialized lexicons"
reading is **downgraded to underdetermined**.

## 9. Discipline note

Anonymous word-forms (sign tuples, len≥2); genre = physical support; site = find-site. NO reading, NO
meaning, NO phonologization. S_shared is pure structural set overlap. Nulls are mechanical permutations
preserving stated marginals (verified by self-check). PC is synthetic and stated as such. Verdict is
mechanical from the frozen rule; the operator never adjudicates.

## 10. Successor hypotheses (in result.json)

E075 expand both-genre site sample · E076 within-Palaikastro genre test · E077 support-type granularity ·
E078 site-locality vs genre-locality strength · E079 cross-site shared-form test per genre · E080 joint
site+genre factorial model with explicit power analysis.
