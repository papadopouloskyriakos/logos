# EPOCH-074 PREREGISTRATION — Cross-Genre Lexicon Partition vs the Genre-Site Confound

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-074
**Layer:** L3 (pure structural lexicon overlap; anonymous word-forms = sign tuples; NO reading, NO meaning)
**Status:** FROZEN BEFORE ANY NULL RUN. PC is SYNTHETIC (constructed corpora).

## 1. Question (mechanical, value-blind)

The libation (religious) and administrative genres share almost no vocabulary (S_shared=20, Jaccard 0.024),
dramatically below a frequency-preserving token→genre permutation null (~69, p_below~0.0005). Naively this
suggests genre-specialized lexicons. BUT in this corpus GENRE and FIND-SITE are near-perfectly confounded
(only Palaikastro has both genres ≥10 tokens: 36 lib / 13 adm; 83.4% of tokens have genre fixed by a
single-genre site), and E071 already established Linear A vocabulary is SITE-local.

**Mechanical question:** does the lexicon partition SURVIVE controlling for site (a genuine genre effect
BEYOND site), or is genre-vs-site UNDERDETERMINED because the two are confounded?

## 2. Definitions (NON-CIRCULAR)

- **Word-FORM** = tuple of signs from a `word` token in `stream`, with `len(signs) >= 2`. Anonymous.
- **GENRE** = physical `support` field. LIBATION = `support=='Stone vessel'`. ADMIN = `support in {Tablet, Nodule, Roundel}`.
- **SITE** = `site` field (find-site).
- **S_shared** = number of word-FORM types present in BOTH genres (the metric).
- **GLOBAL null** (context only): token→genre permutation preserving each form's total token count AND each
  genre's total token count. (Frequency-preserving; ignores site.)
- **SITE-STRATIFIED null** (LOAD-BEARING): permute genre labels ONLY AMONG TOKENS AT THE SAME SITE,
  preserving per-site genre token counts and per-site form counts. A form's site-membership is FIXED; only
  its genre can change WITHIN a site. This removes the site-locality explanation and isolates any residual
  genre effect. If almost all sites are single-genre, this null has almost no genre-swappable tokens and
  CANNOT test a genre effect.

## 3. Confound metric (frozen)

- `n_both_sites_ge10` = number of sites with BOTH genres ≥10 tokens.
- `n_swappable_tokens` = total tokens at sites that have ≥1 token in EACH genre (only these can change genre
  under site control).
- `genre_site_determinism` = fraction of tokens whose genre is FIXED by their single-genre site.

## 4. Protocol

0. Inspect: per-genre form/token counts; S_shared; Jaccard; per-site genre token counts; confound metric.
1. FREEZE this prereg + plan_hash + machinery.py (with `__main__` self-check) BEFORE any null run.
2. GLOBAL null (context): obs S_shared vs null mean + p_below (frac null ≤ obs); closed-form E[S] sanity.
3. CONFOUND: n_both_sites_ge10, n_swappable_tokens, genre_site_determinism.
4. SITE-STRATIFIED null (load-bearing): obs S_shared vs site-stratified null mean + p_below_sitestrat.
5. POSITIVE CONTROL (SYNTHETIC, gates verdict):
   - (a) DETECT-BEYOND-SITE: synthetic corpus with the SAME site/genre token structure as observed but a
     PLANTED genre-specialized lexicon AT BOTH-GENRE SITES (lib vs adm forms disjoint within Palaikastro etc.);
     measure fraction of ≥20 replicates where the site-stratified null flags it (power_est).
   - (b) FALSE-POSITIVE: site-local but genre-NEUTRAL within each site; confirm site-stratified null does NOT
     flag a genre effect (rejection ≤ 0.10).
   - (c) GLOBAL-CALIBRATION: confirm GLOBAL null flags a fully genre-partitioned corpus and not a
     frequency-only one.
   - If site-stratified control has power_est ≥ 0.5 AND is calibrated, a null result is a REAL "no genre
     effect beyond site"; if power_est < 0.5, the control is underpowered ⇒ genre/site confounded ⇒
     UNDERDETERMINED.
6. FROZEN MECHANICAL VERDICT (one token):
   - `GENRE_LEXICON_PARTITIONED_BEYOND_SITE` iff PC passed AND site-stratified power_est ≥ 0.5 AND observed
     S_shared significantly BELOW the SITE-STRATIFIED null (p_below_sitestrat ≤ 0.05).
   - `GENRE_SITE_CONFOUNDED_UNDERDETERMINED` iff site-stratified control UNDERPOWERED (power_est < 0.5 OR
     n_both_sites_ge10 < 2). The GLOBAL partition is REAL but cannot be attributed to genre beyond E071's
     site-locality.
   - `GENRE_LEXICON_OVERLAP_FREQUENCY_EXPLAINED` iff GLOBAL observed S_shared consistent with the global
     frequency null (p_below > 0.05 AND p_above > 0.05).
   - `MACHINERY_UNINFORMATIVE` iff GLOBAL PC calibration fails.

## 5. Discipline

Anonymous word-forms (sign tuples, len≥2). Genre = physical support. Site = find-site. NO reading, NO
meaning, NO phonologization. L3 only. PC is synthetic and is stated as such. Verdict is mechanical from the
frozen rule above; the operator never adjudicates.
