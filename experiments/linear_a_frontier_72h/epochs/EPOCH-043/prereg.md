# EPOCH-043 — CROSS-SITE CERTIFICATION OF POSITIONAL SPECIALIZATION (L2/L3)

Successor of EPOCH-042. E042 established GLOBALLY that ~33% of the LA sign
inventory (17/51) is position-specialized under the analytic Poisson-binomial
within-word null (PC PASSED on LB), but was UNDERPOWERED cross-site: its >=200
sign-token threshold admitted only Haghia Triada, so the cross-site claim could
not be certified and the verdict was SPECIALIZATION_UNDERPOWERED. This epoch
CERTIFIES cross-site at a FEASIBLE threshold (>=80 sign-tokens) and tests
REPLICATION: do the SAME signs specialize across independent sites, or is the
effect HT-specific?

## QUESTION
Is positional specialization PRESENT and CONSISTENT across independent LA sites,
and do the SAME signs specialize (replication of the E042 global set), or is the
effect an HT-only artifact? Signs are ANONYMOUS; L2/L3 only; no
phonetics/meaning/value.

## SCOPE / DISCIPLINE (hard)
- Pure positional structure (L2/L3): signs are ANONYMOUS tokens. No phonetics, no
  sound, no meaning, no value, no reading is assigned. "Specialized" is a
  positional-distribution statistic, NOT a morpheme-with-meaning.
- LB is a POSITIVE-CONTROL benchmark ONLY (known positional structure: case
  endings, common word-initial syllables). LB signs are likewise anonymous tokens
  for the PC; their deciphered values are NOT used.
- Freeze prereg + plan_hash BEFORE running. PC FIRST. Mechanical verdict from the
  FROZEN rule below.

## DATA (verified)
- LA corpus: `corpus/silver/inscriptions_structured.json`. Word tokens are stream
  entries with `t=='word'` and a `signs` list; only words with `len(signs)>=2`.
- A site QUALIFIES for cross-site analysis iff it has >=80 SIGN-TOKENS (sum of
  word lengths over len>=2 words) in the corpus. (Verified: 9 sites qualify —
  Haghia Triada, Zakros, Khania, Knossos, Palaikastro, Phaistos, Iouktas,
  Arkhalkhori, Syme. The actual set is reported in outputs.)
- Positions: INITIAL = index 0; FINAL = index L-1.
- LB positive control: `scripts/cross_script/data.py::load_b_damos()[0]` — list of
  word sign-sequences (anonymous tokens), words len>=2.

## ANALYTIC NULL (frozen — reused from E042)
Under the within-word uniform permutation H0, for a word w of length L containing
sign S exactly k_w times, the probability that a SPECIFIC position p (initial
index 0, or final index L-1) holds S is k_w / L_w, INDEPENDENTLY across words
(positions are distinct slots, one draw each). The null count of S at position p
is therefore a POISSON-BINOMIAL over the per-word Bernoulli probabilities
p_w = k_w / L_w (words not containing S contribute 0 and are dropped).

For each sign S and each position p in {initial, final}:
  - Build per-word Bernoulli probabilities p_w = k_w(S) / L_w over words
    containing S.
  - One-sided UPPER-TAIL p-value = P(X >= observed_count) under that
    Poisson-binomial.
  - EXACT PMF via DP/convolution when n_bernoulli <= EXACT_CAP (4000); else normal
    approximation with continuity correction. Method recorded per test.
- Holm correction across ALL (sign x position) tests WITHIN A SCOPE at family
  alpha 0.05.
- A sign is POSITION-SPECIALIZED (in a given site, or globally) if enriched in
  INITIAL OR FINAL after Holm correction within that scope. Its PREFERRED
  POSITION is the position with the smaller Holm-corrected p (ties -> larger rate
  excess).
- SPECIALIZED_FRACTION (per site) = (#specialized signs) / (#signs tested in that
  site). Per site, test signs with >=8 occurrences IN THAT SITE. Globally, test
  signs with >=15 occurrences in the whole corpus (reproduce E042).

## PROTOCOL
0. Inspect: qualifying sites (>=80 sign-tokens) + per-site sign counts at >=8 occ.
1. FREEZE prereg at the PATH CONTRACT path; plan_hash.txt = "<sha256>  prereg.md";
   machinery.py at epochs/EPOCH-043/machinery.py with an __main__ self-check
   (incl. Poisson-binomial upper tail vs brute-force permutation on a small
   synthetic case, asserted within tolerance).
2. GLOBAL (context): recompute the E042 global specialized set (>=15 occ corpus-
   wide, Holm across all sign x position). Expect ~17 signs.
3. POSITIVE CONTROL FIRST (gates verdict). Seed LB into >=4 pseudo-sites of
   comparable size to the LA qualifying sites. The analytic machinery must:
   (a) DETECT specialization in each pseudo-site (specialized_fraction > 0,
       especially finals); AND
   (b) NOT fire on within-word-shuffled pseudo-sites (specialized_fraction
       <= 0.10 across the shuffled sets). If it cannot detect OR fires on
       shuffled -> MACHINERY_UNINFORMATIVE.
4. LA MAIN — CROSS-SITE: per qualifying site compute specialized_fraction (Holm
   within-site, signs >=8 occ in that site) + the set of specialized signs.
   Count sites with specialized_fraction >= 0.15. REPLICATION: for the top
   globally-specialized signs (the E042 global set), what fraction are ALSO
   specialized (or same-direction enriched, Holm or nominal p<=0.05) in >=2 OTHER
   sites? LEAVE-ONE-SITE-OUT on HT: does the global specialized set survive
   (recompute global specialized set on the corpus MINUS HT; report its
   specialized_fraction)?
5. FROZEN MECHANICAL VERDICT (precedence: PC gates everything; then data
   adequacy; then replication):
   - MACHINERY_UNINFORMATIVE iff PC failed.
   - SPECIALIZATION_UNDERPOWERED iff (PC passed AND) <3 sites qualify even at
     >=80 sign-tokens.
   - SPECIALIZATION_CROSS_SITE_ROBUST iff PC passed AND >=3 sites have
     specialized_fraction >= 0.15 AND >=3 of the E042 global specialized signs
     REPLICATE (same-direction, Holm or nominal p<=0.05) in >=2 other sites AND
     the global set survives leave-one-site-out (LOO global specialized_fraction
     >= 0.15).
   - SPECIALIZATION_SITE_LOCAL iff specialization is significant globally / at HT
     BUT (<3 sites reach 0.15 OR the global set collapses under LOO, i.e. LOO
     global specialized_fraction < 0.15) — i.e. HT-driven.
   - SPECIALIZATION_NOT_REPLICATED iff sites show specialization but DIFFERENT
     signs each (no shared specialized set: <3 global signs replicate in >=2
     other sites) while not collapsing to SITE_LOCAL.
6. WRITE OUTPUTS to the EXACT PATH CONTRACT paths.

## OUTPUTS
- prereg.md, plan_hash.txt, machinery.py, result.json,
  reports/EPOCH043_REPORT.md, data dir data/epoch_043/.
- result.json keys: task_id="EPOCH-043", method, result, verdict (one allowed
  token), numbers, key_findings (>=3), successor_hypotheses (>=5), layer="L2/L3",
  la_touched=true, non_circular (str), deviations (list).
- numbers.global = {"n_sites_qualifying": int, "token_threshold": 80,
  "global_specialized_signs": int}.
- numbers.per_site = {"<site>": {"n_tokens": int, "n_signs_tested": int,
  "specialized_fraction": float, "n_specialized": int}, ...}.
- numbers.replication = {"top_signs_checked": int, "n_replicated_ge2_sites": int,
  "replicated_signs": ["<sign>", ...]}.
- numbers.positive_control = {"pc_verdict": "PASSED"|"FAILED",
  "lb_min_site_fraction": float, "false_pos_rate": float}.
- numbers.loo = {"loo_excluded": "Haghia Triada", "loo_global_fraction": float}.

## NON-CIRCULARITY
Signs carry NO phonetic/sound/meaning/reading. L2/L3 statistics ONLY. LB is a
positive-control benchmark ONLY; its deciphered values are not used in any LA
inference. The verdict is a positional-distribution statistic, not a decipherment.
