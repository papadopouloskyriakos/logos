# EPOCH-014 — PREREGISTRATION (frozen BEFORE any analysis run)

**Campaign:** linear-a-frontier-72h · frontier **F7** (gate A) — register-stratified phonotactics.
**Epoch question:** Do Linear A's registers — libation-formula carriers (stone vessels), administrative
ledgers (tablets), sealing documents (nodules/roundels/sealings) — exhibit measurably DISTINCT value-free
sign-sequence statistics, consistent with distinct linguistic strata, or one global system? If strata exist,
are they FORMULA-VOCABULARY (a few repeated word types) or SYSTEMIC (survive removal of recurrent word
types)? And is register divergence larger than within-register SITE divergence?
**Branch:** research/linear-a-frontier-72h · **Seed:** 20260708 · **Date frozen:** 2026-07-08
**Substantive gate:** A. **Claim ceiling:** L2 (structure). No language is named; no phonetic value used.
**Articles triggered:** V (L2 only; "consistent with distinct strata" is the maximum wording, and ONLY if
the LB single-language benchmark is exceeded — see interpretation gate), VII (search receipt: the full
metric/threshold space is enumerated here; nothing selected post hoc), VIII (effective_n = documents, not
sign tokens; all inference by document-level permutation), IX (info budget: token counts per register on
every claim), XI/XII (registers are defined by SUPPORT TYPE (physical carrier), never by the sequence
statistics being tested; the formula-word list for step 3 is derived mechanically from document recurrence,
not from any prior campaign's reading), XV (no licence touched), XVII (append-only; deviations logged in
result.json), XVIII (assumptions A1–A5 below), XXII (this header).

## Prior art cited + differenced (do-not-repeat check)

- **Relative-phonology campaign (CLOSED):** validated K1-adaptive L2/L3 positives incl. libation-formula
  word ORDER as a register-internal regularity. Difference: E014 does not re-test formula order; it tests
  whether registers differ in aggregate sign-sequence statistics (bigrams/positional), a between-register
  question never preregistered before.
- **Methodology inventory (OPEN_AND_UNTESTED):** register-stratified phonotactics is not among the 214
  catalogued instances; nearest lineage is corpus-global bigram work (constraint-expansion), never
  register-split.
- **Observable-channels programme:** L3 word-context→channel REFUTED — E014 makes no channel/content claim;
  registers are physical-support classes, not induced channels.
- **E011/E007:** frequency-artifact unmaskings motivate the class-prior discipline here: the permutation
  null preserves per-register document-length profiles, so a "register effect" cannot be a document-length
  artifact.

## Data / registers (frozen; mechanical)

- **LA:** `corpus/silver/inscriptions_structured.json` (1,341). Registers by `support`:
  LIB = "Stone vessel"; LEDG = "Tablet"; SEAL = {"Nodule","Roundel","Sealing"}. All other supports excluded.
- **Analysis stream per document:** the `words` field; keep words with ≥2 signs (single-sign words are
  logogram-dominated and would inject commodity vocabulary, not phonotactics). Signs used AS IDENTITIES
  (L1/L2); no phonetic value consulted. Pre-freeze descriptive audit (counts only): LIB 85 docs / 259 words
  / 896 sign tokens; LEDG 257 / 844 / 2,294; SEAL 92 / 106 / 266. Documents with zero qualifying words drop.
- **LB (controls):** DĀMOS `corpus/bronze/linearb/damos/items.jsonl`, words via
  `scripts.cross_script.data._damos_wordforms` (syllabic wordforms only, ≥2 signs). Register labels from the
  DB `series` field + site prefix of `heading` — KN series **A** (personnel; 180 docs / 751 words) vs KN
  series **D** (livestock; 698 docs / 1,356 words). Same site (KN), same language, known document-type
  contrast: the method MUST detect it.
- **Sign alphabet:** per script, signs with pooled analysis-stream count < 10 map to `OTH` (register-neutral,
  computed on the pooled stream of the pair being compared... NO: computed once on the pooled ALL-register
  analysis stream of that script, so the alphabet is identical across pairs).

## Statistics (frozen)

- **Primary metric:** Jensen–Shannon divergence (bits) between register bigram distributions. Bigrams =
  word-internal adjacent sign pairs PLUS boundary events (#,s₁) and (s_L,#) per word. Distributions are
  add-0.5 smoothed over the union of bigram types observed in the two registers being compared.
- **Secondary (descriptive, non-gating):** JSD of word-initial-sign and word-final-sign distributions;
  mean word length in signs.
- **Null (document-matched permutation):** for a pair (A,B), pool documents, bin by qualifying-word-count
  {1, 2, 3–5, 6–10, ≥11}, shuffle register labels WITHIN bins (preserving per-bin register counts), recompute
  JSD. **n_perm = 2,000** (seeded). p = (1 + #{JSD_perm ≥ JSD_obs}) / (1 + n_perm).
- **Effect size:** excess = JSD_obs − mean(JSD_perm); **excess ratio** = excess / mean(JSD_perm) (used for
  cross-comparison gates; assumption A3).
- **Multiplicity:** Holm over the 3 LA register pairs (primary metric only gates).

## Controls (run FIRST, in this order)

- **PC1 (must-fire):** LB KN-A vs KN-D, full pipeline → perm p < 0.05. Machinery gate.
- **PC2 (must-NOT-fire):** KN-D docs randomly split 50/50 into pseudo-registers, full pipeline, 20 seeded
  reps (500 perms each) → false-positive rate at p<0.05 must be ≤ 3/20. Machinery gate.
- **PC3 (power at LA scale):** for each LA pair, subsample KN-A and KN-D docs to match that pair's word
  counts (sample docs until word budget reached; A plays the smaller register), 10 seeded reps (500 perms)
  → detection rate. A pair has POWER iff ≥ 7/10. Used only to separate ABSENT from NO_POWER.
- **LB single-language benchmark (interpretation calibration):** run step 3 (recurrent-word removal, rule
  below) on KN-A vs KN-D. Record post-removal p and excess ratio = **B_LB**. Since LB registers share one
  language, B_LB is the ceiling that same-language register separation can produce; LA "consistent with
  distinct strata" wording requires exceeding it.

## LA test sequence

1. Pairwise JSD + permutation p for LIB–LEDG, LIB–SEAL, LEDG–SEAL; Holm.
2. **Step 3 (vocabulary attribution)**, only for Holm-significant pairs: recurrent word types = word types
   occurring in ≥3 distinct documents of either register of the pair (union, computed per register then
   united); delete ALL tokens of those types from BOTH registers; documents may drop; re-run the identical
   pipeline (re-binned, 2,000 perms). Holm over the surviving pairs.
3. **Step 4 (site control):** within-register site divergence with the identical pipeline: LEDG HT vs
   LEDG non-HT; SEAL HT vs SEAL non-HT (run only if both sides ≥ 30 words; LIB has no usable site split —
   assumption A4). Site benchmark **S** = max observed site excess ratio among runnable within-register
   splits. A significant register pair is SITE-DISCOUNTED iff its excess ratio ≤ S.
   Non-gating robustness: for the strongest surviving pair, token-matched subsample check at the site-pair
   size (10 reps, medians reported).

## MECHANICAL verdict (frozen)

- PC1 fails OR PC2 fails → **REGISTER_STRATA_NO_POWER** (machinery), stop.
- No LA pair Holm-significant: all three pairs have PC3 power → **REGISTER_STRATA_ABSENT**;
  otherwise → **REGISTER_STRATA_NO_POWER**.
- ≥1 pair Holm-significant: drop SITE-DISCOUNTED pairs; if none survive → **REGISTER_STRATA_NO_POWER**
  (site-register confound undecidable at this corpus).
- Surviving pairs → step 3: if ≥1 surviving pair stays Holm-significant post-removal with excess > 0 →
  **REGISTER_STRATA_SYSTEMIC**; else → **REGISTER_STRATA_VOCABULARY_ONLY**.
- **Interpretation gate (wording, not verdict):** SYSTEMIC may be worded "consistent with distinct
  linguistic strata (L2)" ONLY if the driving pair's post-removal excess ratio > B_LB; otherwise it must be
  worded "systemic register phonotactics within single-language range".

## Assumptions (Art. XVIII)

- **A1:** `support` field is an honest physical-register proxy (editorial, pre-linguistic; non-circular).
- **A2:** GORILA transliteration conventions are register-uniform (a stone-vessel reading is segmented by
  the same editorial rules as a tablet). Known caveat: stone-vessel words are dotted/divider-segmented by
  editors — flagged on any positive.
- **A3:** excess ratio is approximately sample-size comparable (used only for cross-comparison gates;
  raw excesses also reported).
- **A4:** LIB site splits are unusable (no site holds ≥30 LIB words twice); LIB-involving site confound is
  therefore only partially controllable — any LIB-driven positive carries this caveat explicitly.
- **A5:** ≥2-sign word filter removes logogram vocabulary asymmetry; residual logogram-like multi-sign
  compounds remain a leakage path — step 3 (recurrent-type removal) bounds it.

## Search receipt (Art. VII)

Metrics tried: exactly those above (bigram JSD primary; positional JSDs secondary-descriptive). Thresholds:
p<0.05 Holm, PC gates as stated. No alternative binnings, smoothings, or register definitions will be tried;
any deviation is logged in result.json `deviations`.

## Outputs

`epochs/EPOCH-014/{prereg.md,plan_hash.txt,result.json}`, `data/register_strata/*.json`,
`reports/EPOCH014_REGISTER_STRATA.md`. Compliance line closes the report.
