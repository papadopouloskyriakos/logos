# EPOCH-044 — NUMERAL-GROUP CARDINALITY / COMPOUND-QUANTITY STRUCTURE (L2/L3)

Successor of EPOCH-043. This epoch asks a STRUCTURAL question about Linear A
ledger entries: is a quantity a SINGLE numeral token, or a RUN of consecutive
numeral tokens (a COMPOUND quantity — e.g. integer followed by fraction, the
notation LA is hypothesized to use)? We measure the distribution of numeral-run
lengths and test whether multi-token (compound) structure is PRESENT and
CONSISTENT across sites. PURE TOKEN-COUNT STRUCTURE: we count how many `num`
tokens cluster consecutively; we do NOT interpret numeral VALUES and do NOT do
arithmetic. Tokens are ANONYMOUS; no phonetics/meaning.

## QUESTION
In LA ledger entries, is a quantity a SINGLE `num` token or a RUN of consecutive
`num` tokens (compound)? What is the distribution of numeral-run lengths, and is
a multi-token (compound) structure PRESENT and CONSISTENT across sites?

## SCOPE / DISCIPLINE (hard)
- Pure token-count structure (L2/L3): tokens are ANONYMOUS. No phonetics, no
  sound, no meaning, no reading. Numeral VALUES are NOT interpreted; NO
  arithmetic is performed. Only the COUNT of consecutive `num` tokens matters.
- LB control: the LA corpus stream is the unit of analysis. LB lacks a
  comparable stream-level numeral-run structure in the available data, so the
  POSITIVE CONTROL is built on the LA stream itself with a SYNTHETIC clustering
  / spreading injection and a token-order-shuffle null (stated explicitly).
- Freeze prereg + plan_hash BEFORE running. PC FIRST. Mechanical verdict from the
  FROZEN rule below.

## DATA (verified)
- LA corpus: `corpus/silver/inscriptions_structured.json`. Each inscription has
  an ORDERED `stream` of tokens; each token has a `t` field; numeral tokens have
  `t == 'num'`.
- A NUMERAL-RUN = a maximal run of consecutive `num` tokens in the stream. A run
  is broken by ANY non-`num` token (word / nl / div / other). RUN-LENGTH = number
  of `num` tokens in the run.
- A site QUALIFIES for cross-site analysis iff it has >=20 numeral-runs.

## METRIC (frozen)
- p_compound = (number of numeral-runs with length >= 2) / (total numeral-runs).
- Run-length histogram: count of runs of each length {1, 2, 3, ...}.

## NULL (frozen)
Token-order shuffle WITHIN each inscription: permute the stream token order,
preserving the type multiset of that inscription, recompute p_compound on the
permuted corpus, repeat >= 1000 draws. Two-sided p = fraction of draws with
p_compound at least as far from the null mean as the observed (in units of the
null SD), equivalently 2 * min(P(null <= obs), P(null >= obs)).
- EXCESS compound (observed > null mean) = numerals CLUSTER = compound quantities.
- DEFICIT compound (observed < null mean) = numerals SPREAD OUT = one-per-entry.

## PROTOCOL
0. Inspect: n numeral-runs; run-length distribution; p_compound observed;
   per-site counts.
1. FREEZE prereg + plan_hash + machinery.py (with __main__ self-check).
2. GLOBAL: p_compound; shuffle-null mean + two-sided p + direction; run-length
   histogram.
3. POSITIVE CONTROL FIRST (gates verdict):
   (a) DETECT — plant a known clustering (force numerals into compound runs in
       X% of a synthetic stream built from the LA type multiset) and confirm
       excess detected (p <= 0.05, correct direction = excess); AND plant known
       one-per-entry (force all numerals isolated) and confirm deficit detected
       (p <= 0.05, correct direction = deficit).
   (b) FALSE-POSITIVE — on token-order-shuffled streams (true H0), rejection
       rate <= 0.10 across >= 20 independent sets.
   If it cannot detect planted clustering/spreading OR fires on shuffled ->
   MACHINERY_UNINFORMATIVE.
4. LA MAIN — CROSS-SITE held-out: per site with >=20 numeral-runs, compute
   p_compound + shuffle p + direction; count sites significant same direction;
   require CONSISTENT direction. Leave-one-site-out on the largest site
   (Haghia Triada): drop HT, recompute global p_compound + shuffle p.
5. FROZEN MECHANICAL VERDICT (one token):
   - COMPOUND_QUANTITY_STRUCTURE_CROSS_SITE iff PC passed AND global EXCESS
     compound significant (p <= 0.05) AND >= 3 sites significant EXCESS AND
     survives leave-one-site-out.
   - COMPOUND_QUANTITY_SITE_LOCAL iff global excess significant BUT < 3 sites /
     collapses under LOO.
   - SINGLE_NUMERAL_DOMINANT iff runs are overwhelmingly length-1 AND no
     significant excess (p > 0.05 OR deficit) -> quantities are one numeral-token
     each (report p_compound).
   - NUMERAL_GROUP_UNDERPOWERED iff < 3 sites have >= 20 numeral-runs.
   - MACHINERY_UNINFORMATIVE iff PC failed.

## OUTPUTS
prereg.md, plan_hash.txt, machinery.py, result.json, report, data dir — at the
PATH CONTRACT paths. result.json keys: task_id="EPOCH-044", method, result,
verdict (one allowed token), numbers, key_findings (>=3), successor_hypotheses
(>=5), layer="L2/L3", la_touched=true, non_circular (str), deviations (list).
