# EPOCH-052 — ZIPF / HEAPS STATISTICAL SIGNATURE (Linear A frontier-72h)

**Layer:** L2/L3 (pure frequency-distribution statistics; anonymous forms/signs).
**Task id:** EPOCH-052
**Operator:** logos z.ai research worker (GLM-5.2). Proposer/operator, NEVER adjudicator.
**Verdict:** produced by a FROZEN mechanical rule, not by the operator.

## QUESTION
Do Linear A WORD-FORM and SIGN frequencies follow the ZIPF rank-frequency power law
(log freq ~ slope * log rank, slope ~ -1) and the HEAPS vocabulary-growth law
(V ~ N^beta, beta in ~0.4-0.8), as natural-language corpora do — and how does LA
compare to Linear B (a real language) and to a RANDOM baseline?

## HONEST FRAMING (load-bearing caveat — Miller 1957)
Zipf adherence is a **NECESSARY-NOT-SUFFICIENT** language signature. Even random
monkey-typing / i.i.d. sampling from a Zipfian unigram produces Zipf-like rank-frequency
distributions (Miller 1957, "Some effects of intermittent silence"). Therefore:

  * Zipf/Heaps adherence **CANNOT prove** LA is a language.
  * A **STRONG DEVIATION** from Zipf/Heaps would be more informative — it would be
    atypical of natural-language corpora and would argue against a language-like
    frequency structure.
  * The informative random baseline is a **UNIFORM-random** token stream (slope ~ 0,
    non-Zipfian), NOT an i.i.d. draw from the LA unigram (which would inherit Zipf).

This is pure frequency-distribution statistics (L2/L3): forms and signs are ANONYMOUS;
no phonetics, no meaning, no language identification.

## NON-CIRCULAR / DISCIPLINE (hard)
  * Anonymous forms/signs only (sign tuples and individual signs as opaque tokens).
  * L2/L3 ONLY — no phonetic values, no meanings, no language identification.
  * Linear B is a CONTROL ONLY (a known language used to validate the fitters); no
    A<->B phonetic join, no cognate claim, no reading of LA.

## DATA (verified)
  * LA: `corpus/silver/inscriptions_structured.json`. Word tokens = stream entries
    with `t=='word'` and a `signs` list. Word-form = the sign tuple. Sign = an
    individual sign in that list.
  * LB: `scripts.cross_script.data.load_b_damos()[0]` returns a list of per-word
    sign-tuples (the DAMOS Linear B corpus). Word-form = sign tuple; sign = element.

## METHOD (frozen)
1. **ZIPF.** Rank forms/signs by descending frequency; fit
   `log(freq) ~ slope * log(rank)` by OLS on ranks 1..R (R = number of distinct
   types with freq>=1). Report slope and R^2. NL word Zipf slope ~ -1 (range ~ -0.8
   to -1.2).
2. **HEAPS.** Walk the word-token stream in corpus order; after each token record
   (N = tokens seen, V = distinct forms seen). Fit `log V ~ beta * log N` by OLS.
   Report beta and R^2. NL beta ~ 0.4-0.8.
3. **BASELINES.** (a) LB (real language, positive control). (b) UNIFORM-random token
   stream of the same length drawn from the LA distinct-form vocabulary (slope ~ 0,
   non-Zipfian — the informative baseline).

## PROTOCOL
0. Inspect: n word-tokens, n distinct forms, n signs; raw rank-freq head/tail.
1. FREEZE prereg + plan_hash; write machinery.py with `__main__` self-check that
   validates the Zipf/Heaps fitters on synthetic Zipf data of KNOWN slope (assert
   recovered slope ~ planted).
2. GLOBAL: LA word-form Zipf slope + R^2; LA sign Zipf slope + R^2; LA Heaps beta + R^2.
3. POSITIVE CONTROL FIRST (gates verdict):
   (a) DETECT — on LB the fitters must recover a language-typical word Zipf slope
       (~ -0.8 to -1.2) with R^2 >= 0.9 AND Heaps beta in ~0.4-0.8; AND on a
       UNIFORM-random token stream the slope must be ~0 / non-Zipfian (|slope|<0.3).
       If the fitters cannot recover LB's known Zipf/Heaps OR cannot distinguish
       uniform-random -> MACHINERY_UNINFORMATIVE.
4. LA CLASSIFICATION (frozen thresholds): compare LA's word Zipf slope + R^2 + Heaps
   beta to the language-typical ranges and to LB.
5. FROZEN MECHANICAL VERDICT:
   - `ZIPF_HEAPS_LANGUAGELIKE` iff PC passed AND LA word Zipf slope in [-1.3,-0.6]
     with R^2>=0.9 AND Heaps beta in [0.35,0.85] (NECESSARY-not-sufficient).
   - `ZIPF_HEAPS_ATYPICAL` iff LA word Zipf slope OR Heaps beta falls clearly OUTSIDE
     the language-typical ranges (informative deviation).
   - `ZIPF_HEAPS_INCONCLUSIVE` iff fits are poor (R^2<0.9) / borderline.
   - `ZIPF_UNDERPOWERED` iff too few tokens/forms for stable fits (n_tokens<300 or
     n_forms<100).
   - `MACHINERY_UNINFORMATIVE` iff PC failed.
6. WRITE OUTPUTS to the exact PATH CONTRACT paths.

## FROZEN VERDICT RULE (mechanical; operator does not adjudicate)
Applied in code after PC. See `machinery.py::mechanical_verdict`.

## OUTPUTS
`prereg.md`, `plan_hash.txt`, `machinery.py`, `result.json`, `reports/EPOCH052_REPORT.md`,
`data/epoch_052/` (rank-frequency tables + Heaps curves for LA/LB/uniform).
