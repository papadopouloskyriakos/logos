# EPOCH-039 — PREREGISTRATION (FROZEN BEFORE RUN)

## Task
PREFIX PARADIGM vs A-ONLY (morphology; L2/L3).

E038 found Linear A is word-INITIAL-concentrated (H_first < H_last; asymmetry
H_first - H_last = -0.223 bits; reverse-tail p = 0.0005), i.e. a prefixing-like
distributional pattern (opposite of Greek/LB). E025 certified sign A as a
productive word-initial marker (prefix). QUESTION: is the initial-concentration a
genuine PREFIX PARADIGM (a SET of productive word-initial marker signs), or is it
driven ONLY by A-?

## Discipline (HARD, NON-CIRCULAR)
Signs carry NO phonetic value, sound, meaning, or reading. L2/L3 statistics ONLY.
"prefix" = word-INITIAL positional enrichment (a distributional statistic), NOT a
grammatical morpheme with meaning. Linear B is a POSITIVE-CONTROL benchmark ONLY;
no LB result is interpreted as a Linear-A claim.

## Data (verified)
- corpus/silver/inscriptions_structured.json — word tokens (stream entry t=='word'
  with 'signs'); words with len(signs)>=2.
- Inspect: n_words(len>=2)=1369; n_A_initial=155 (11.3%); n_A_removed=1214.
- Sites with >=50 words: Haghia Triada (694), Zakros (132), Khania (120),
  Knossos (61), Phaistos (58), Palaikastro (57) -> 6 testable sites.
- LB positive control via scripts.cross_script.data.load_b_damos()[0] (13562 words).

## Metrics (FROZEN)
H = Shannon entropy (bits) of the sign distribution at a position.
(a) FULL asymmetry = H_first - H_last over ALL len>=2 words (negative =>
    initial-concentrated; from E038).
(b) A-REMOVED asymmetry = same but EXCLUDING words whose first sign is A.
(c) PREFIX INVENTORY = signs S (with >=15 occurrences) whose word-INITIAL rate
    significantly exceeds the within-word permutation null (one-sided p<=0.05,
    Holm-corrected across tested signs). Count with A and without A; list
    ANONYMOUSLY with initial-rates.

## NULL (FROZEN, within-word permutation — calibrated)
For each null draw, permute the sign order WITHIN each word (preserves each word's
multiset and length). For (a)/(b) recompute the asymmetry; for (c) recompute each
sign's initial rate. >=2000 draws. One-sided p for initial-concentration /
initial-enrichment:
  - asymmetry: p = frac draws with null_asym <= observed_asym (observed at least as
    initial-concentrated / negative as null). Initial-concentrated iff asymmetry<0
    AND p<=0.05.
  - sign initial-rate: p = frac draws with null_init_rate >= observed_init_rate
    (observed at least as initial-enriched as null).

## PROTOCOL (in order)
0. Inspect (above).
1. FREEZE prereg + plan_hash; machinery.py with __main__ self-check.
2. GLOBAL: full asymmetry + null p; A-REMOVED asymmetry + null p; Holm-significant
   word-initial-enriched sign inventory (count with A, count without A; list
   ANONYMOUSLY with initial-rates).
3. POSITIVE CONTROL FIRST (gates verdict). On LB:
   (a) DETECT — construct a corpus with a KNOWN multi-prefix paradigm (plant >=3
       distinct signs as productive prefixes) and confirm A-removed-style
       concentration SURVIVES removing ONE planted prefix (paradigm detected as
       multi-prefix).
   (b) FALSE-POSITIVE — on within-word-shuffled words, the initial-enriched-sign
       count and the concentration must be at null (rejection rate <=0.10 across
       >=20 sets).
   If it cannot detect a multi-prefix paradigm OR fires on shuffled words ->
   MACHINERY_UNINFORMATIVE.
4. LA MAIN — CROSS-SITE held-out: per site with >=50 words, compute the A-REMOVED
   asymmetry + null p; count sites where initial-concentration SURVIVES A-removal
   (p<=0.05 same direction). Leave-one-site-out on Haghia Triada.
5. FROZEN MECHANICAL VERDICT (count):
   - PREFIX_PARADIGM_BEYOND_A iff PC passed AND A-REMOVED asymmetry is still
     significantly initial-concentrated globally (p<=0.05) AND >=2 signs BESIDES A
     are Holm-significant word-initial-enriched AND A-removed concentration holds
     in >=2 sites.
   - INITIAL_CONCENTRATION_A_ONLY iff FULL asymmetry is initial-concentrated BUT
     A-REMOVED asymmetry is NOT significant AND <2 non-A signs are initial-enriched.
   - NO_INITIAL_CONCENTRATION_WITHOUT_A iff neither full nor A-removed shows
     initial concentration (contradicts E038 -> flag).
   - PARADIGM_UNDERPOWERED iff <2 sites have >=50 words.
   - MACHINERY_UNINFORMATIVE iff PC failed.

## OUTPUTS (exact PATH CONTRACT paths)
prereg.md, plan_hash.txt, machinery.py, result.json,
reports/EPOCH039_REPORT.md, data/epoch_039/.

## Seeds / knobs (FROZEN)
SEED_GLOBAL=20390760, SEED_NULL=20390761, SEED_PC_DETECT=20390762,
SEED_PC_FP=20390763, SEED_PC_PLANT=20390764, SEED_PER_SITE=20390765,
SEED_LOO=20390766, SEED_INVENTORY=20390767.
N_DRAWS=2000; PC_DETECT_DRAWS=2000; PC_FP_DRAWS=1000; N_FP_SETS=20;
MIN_SIGN_OCC=15; MIN_SITE_WORDS=50.
