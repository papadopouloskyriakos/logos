# EPOCH-042 — SIGN POSITIONAL-ROLE SPECIALIZATION via ANALYTIC within-word null (L2/L3)

Supersedes EPOCH-041. E041 was UNDERPOWERED at the NULL level: 2000 permutation
draws imposed a p-floor of 1/2001 ≈ 5e-4 that collided with the Holm threshold
across ~102 simultaneous (sign × position) tests, so 0 signs passed on BOTH LA and
LB and the positive control (PC) failed — not because the machinery is wrong, but
because the permutation null could not resolve small p-values. FIX (frozen for this
epoch): replace the permutation draws with the EXACT ANALYTIC within-word null. No
draw floor.

## QUESTION (unchanged from E041)
What FRACTION of the Linear A sign inventory is POSITION-SPECIALIZED — i.e.
significantly enriched, Holm-corrected, in INITIAL or FINAL within-word position
versus the within-word null? HIGH => templatic/slot morphology (signs have fixed
structural roles); LOW => positionally-free signs. Is the level ROBUST across
sites? Signs are ANONYMOUS; L2/L3 only; no phonetics/meaning/value.

## SCOPE / DISCIPLINE (hard)
- Pure positional structure (L2/L3): signs are ANONYMOUS tokens. No phonetics, no
  sound, no meaning, no value, no reading is assigned. "Specialized" is a
  positional-distribution statistic, NOT a morpheme-with-meaning.
- LB is a POSITIVE-CONTROL benchmark ONLY (it has known positional structure:
  grammatical case endings, common word-initial syllables). LB signs are likewise
  treated as anonymous tokens for the PC; their deciphered values are NOT used.
- Freeze prereg + plan_hash BEFORE running. PC FIRST. Mechanical verdict from the
  frozen rule below.

## DATA (verified)
- LA corpus: `corpus/silver/inscriptions_structured.json`. Word tokens are stream
  entries with `t=='word'` and a `signs` list. Only words with `len(signs)>=2`.
- Positions: INITIAL = index 0; FINAL = index L-1. (Medial dropped for E042: the
  question is initial-vs-final slot specialization.)
- LB positive control: `scripts/cross_script/data.py::load_b_damos()[0]` — list of
  word sign-sequences (anonymous tokens), words len>=2.

## ANALYTIC NULL (frozen — this is the method fix vs E041)
Under the within-word uniform permutation H0, for a word w of length L containing
sign S exactly k_w times, the probability that a SPECIFIC position p (initial index
0, or final index L-1) holds S is k_w / L_w, INDEPENDENTLY across words (positions
are distinct slots, one draw each). Therefore the null count of S at position p =
sum over words containing S of independent Bernoulli(k_w / L_w) trials => a
POISSON-BINOMIAL distribution.

For each sign S (>=15 occurrences in len>=2 words) and each position p in
{initial, final}:
  - Build the per-word Bernoulli probabilities p_w = k_w(S) / L_w over all words
    that contain S (words not containing S contribute 0 to the count and are
    dropped from the convolution).
  - Compute the one-sided UPPER-TAIL p-value = P(X >= observed_count) under that
    Poisson-binomial.
  - EXACT Poisson-binomial PMF via DP/convolution when n_bernoulli <= 4000
    (convolution cost O(n * max_count)); otherwise a normal approximation with
    continuity correction (mean = sum p_w, var = sum p_w(1-p_w)). The method used
    per test is recorded.
- Holm correction across ALL (sign × position) tests at family alpha 0.05.
- A sign is POSITION-SPECIALIZED if it is significantly enriched in INITIAL OR
  FINAL after Holm correction. Its PREFERRED POSITION is the position with the
  smaller Holm-corrected p (ties → the one with larger rate excess).
- SPECIALIZED_FRACTION = (#specialized signs) / (#signs tested, >=15 occ).

## PROTOCOL
0. Inspect: n words len>=2; n signs >=15 occ; rough specialized fraction.
1. FREEZE prereg + plan_hash; machinery.py at epochs/EPOCH-042/machinery.py with an
   __main__ self-check that INCLUDES validation of the Poisson-binomial upper tail
   against a brute-force permutation on a small synthetic case (assert agreement
   within tolerance).
2. GLOBAL: SPECIALIZED_FRACTION (Holm); breakdown initial vs final; list specialized
   signs ANONYMOUSLY with preferred position + initial/final rates + Holm p.
3. POSITIVE CONTROL FIRST (gates verdict). On LB (KNOWN positional structure):
   (a) DETECT — analytic machinery must find a specialized fraction significantly
       > 0 (many LB signs specialized, esp. finals); AND
   (b) FALSE-POSITIVE — on within-word-shuffled LB words (real positional structure
       destroyed), the Holm-specialized fraction must be ~chance (<=0.10) across
       >=20 sets. If it cannot detect LB structure OR fires on shuffled words ->
       MACHINERY_UNINFORMATIVE. (Must pass now that the p-floor is removed; if it
       still fails, report honestly.)
4. LA MAIN — CROSS-SITE held-out: per site with >=200 word-tokens, compute the
   specialized fraction; report per-site fractions + leave-one-site-out on HT.
5. FROZEN MECHANICAL VERDICT (precedence: PC gates everything; then data adequacy;
   then fraction thresholds):
   - MACHINERY_UNINFORMATIVE iff PC failed.
   - SPECIALIZATION_UNDERPOWERED iff (PC passed AND) (<3 sites have >=200 tokens
     OR <15 signs testable).
   - HIGH_POSITIONAL_SPECIALIZATION_CROSS_SITE iff PC passed AND data adequate AND
     global specialized_fraction >= 0.20 AND per-site fraction >= 0.15 in >=3 sites.
   - POSITIONAL_SPECIALIZATION_SITE_LOCAL iff PC passed AND data adequate AND
     global >= 0.20 BUT <3 sites / collapses under LOO.
   - LOW_POSITIONAL_SPECIALIZATION iff PC passed AND data adequate AND global
     specialized_fraction < 0.20.
6. WRITE OUTPUTS to the EXACT PATH CONTRACT paths.

## OUTPUTS
- prereg.md, plan_hash.txt, machinery.py, result.json, report
  (reports/EPOCH042_REPORT.md), data dir (data/epoch_042/).
- result.json keys: task_id="EPOCH-042", method, result, verdict (one allowed
  token), numbers, key_findings (>=3), successor_hypotheses (>=5), layer="L2/L3",
  la_touched=true, non_circular (str), deviations (list).
- numbers.global = {"n_signs_tested", "n_specialized", "specialized_fraction",
  "n_initial_spec", "n_final_spec", "null_method":"analytic_poisson_binomial"}.
- numbers.specialized_signs = [["<sign>", "initial"|"final", initial_rate,
  final_rate, holm_p], ...].
- numbers.positive_control = {"pc_verdict", "lb_specialized_fraction",
  "lb_shuffled_fraction", "false_pos_rate"}.
- numbers.cross_site = {"n_sites_testable", "per_site_fraction": {...},
  "loo_excluded", "loo_fraction"}.

## NON-CIRCULARITY
Signs carry NO phonetic/sound/meaning/reading. L2/L3 statistics ONLY. LB is a
positive-control benchmark ONLY; its deciphered values are not used in any LA
inference. The verdict is a positional-distribution statistic, not a decipherment.
