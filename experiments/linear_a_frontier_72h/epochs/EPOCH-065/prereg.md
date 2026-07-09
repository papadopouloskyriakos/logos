# EPOCH-065 PREREGISTRATION (FROZEN)

## Task
EPOCH-065 — Is word-length a SITE REGISTER (site-local) beyond document class, or functionally invariant?

Layer: **L2** (pure structural token-length; word-length = number of signs; NO sign values, NO readings, NO meaning).

## Context
E028 established that word-length (sign count) carries a strong DOCUMENT-CLASS signature that is
CROSS-SITE ROBUST (DOCCLASS_LENGTH_SIGNATURE_ROBUST: Nodule ~1.1 -> Metal ~3.9). That is the FUNCTIONAL
axis. This epoch probes the orthogonal SITE axis: CONTROLLING for document class, is there RESIDUAL SITE
variation in word-length?

## Definitions (NON-CIRCULAR)
- **word-length** = `len(word)` where `word` is a sign-list. Purely structural (count of signs). No sign
  identities, no readings, no semantics.
- **document class** = the corpus `support` field (physical support type; given, not derived from signs).
- **site** = the corpus `site` field (findspot; given, not derived from signs).
- The STRATIFIED null permutes SITE labels WITHIN each class, preserving the class word-length multiset
  AND each site's n-in-class. Any detected effect is therefore site variation BEYOND class.

## Data
- Source: `corpus/silver/inscriptions_structured.json` (1341 inscriptions).
- Each inscription has `site`, `support` (document class), `words` (list of sign-lists).
- **TESTABLE classes** = `support` classes with >=2 sites having >=30 words each.
  Verified testable classes: **Tablet** (Arkhalkhori, Haghia Triada, Khania, Phaistos, Tylissos),
  **Roundel** (Haghia Triada, Khania), **Stone vessel** (Iouktas, Palaikastro, Zakros).
- Only sites with >=30 words in a class enter that class's test.

## Metric (FROZEN)
For each testable class `c`:
- `obs_H[c]` = Kruskal-Wallis H statistic on word-length grouped by SITE (sites with >=30 words in `c`),
  WITH tie correction. Word-lengths are small integers -> heavy ties, so:
  `H_corr = H_raw / (1 - sum(t^3 - t)/(N^3 - N))` where the sum is over tied groups of size t.
- `combined statistic` = sum over testable classes of `obs_H[c]`.

## Null (FROZEN, STRATIFIED)
For each class INDEPENDENTLY: permute the SITE labels among that class's words (preserving the class
word-length multiset AND each site's n-in-class); recompute H per class; sum. >=1000 draws.
- `combined perm p` = frac(null_sum >= obs_sum), one-sided.
- Per-class `perm p` likewise (permute within that class only).

## Contrast (RAW, uncontrolled)
Also report the RAW (uncontrolled) site Kruskal-Wallis H over ALL words (site-only, ignoring class) +
its perm p, to quantify how much of any raw site effect is CLASS-CONFOUNDED vs residual.

## Protocol
0. Inspect: testable classes; per (class, site) n and mean word-length; obs_H per class; raw site H.
1. FREEZE prereg + plan_hash BEFORE running; machinery.py with __main__ self-check.
2. GLOBAL: per-class obs_H + perm p; combined obs_sum + combined perm p; raw site H + perm p.
3. POSITIVE CONTROL FIRST (gates verdict), SYNTHETIC:
   (a) DETECT — plant a residual SITE-REGISTER effect (shift one site's word-lengths by +1 within a class,
       holding class distributions otherwise equal); confirm STRATIFIED test flags it (combined perm p<=0.05).
   (b) FALSE-POSITIVE — plant word-lengths that depend ONLY on class (site labels assigned at random within
       each class, no residual site effect); confirm stratified test does NOT flag (rejection <=0.10 across
       >=20 draws). If it can't detect a planted register OR fires on class-only data -> MACHINERY_UNINFORMATIVE.
4. PER-CLASS DIRECTION: which classes individually show a significant within-class site effect + per-site means.
5. FROZEN MECHANICAL VERDICT:
   - `WORDLEN_SITE_REGISTER` iff PC passed AND stratified combined site effect significant (combined perm
     p<=0.05) AND >=2 testable classes individually significant (GENERAL register).
   - `WORDLEN_SITE_REGISTER_SITE_LOCAL` iff stratified combined effect significant BUT only 1 class shows it.
   - `WORDLEN_FUNCTIONAL_INVARIANT` iff stratified combined site effect NOT significant — EVEN IF raw site H
     is significant (class-confounding, removed by stratified null).
   - `WORDLEN_UNDERPOWERED` iff <1 class has >=2 sites with >=30 words.
   - `MACHINERY_UNINFORMATIVE` iff PC failed.
6. WRITE OUTPUTS to exact PATH CONTRACT paths.

## Discipline
- Proposer/operator, never adjudicator: MECHANICAL verdict from FROZEN rule.
- L2 ONLY. Structural word-length only; NO reading.
- PC synthetic (plant a residual site-register effect); stated plainly.
- Freeze prereg + plan_hash BEFORE running permutation tests.
