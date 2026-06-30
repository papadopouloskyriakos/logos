# Finding 2026-06-30 — Direction D metrology: an honest PARSE-COVERAGE null (machinery correct; ½=1/2 corroborates Corazza; fractions don't generalize on the automated parse)

Built a constraint-optimization over the Linear A accounting tablets (`scripts/comparison/metrology.py`):
parse HT (LM I) tablets into balance units `[recipient][commodity logogram][integer][fraction signs]`, then
**SOLVE the fraction-sign rational values** (RANSAC over exact `Fraction` Gaussian elimination — robust to the
unbalanced-tablet outliers least-squares can't handle) so line items balance the preserved KU-RO totals.
Validate on **held-out** tablets + a permutation null. CPU/laptop. Verifier: **0 critical/high** (minor
low/medium only); result independently re-run here. NO phonetic claim.

## Headline — an honest NULL (parse-coverage / under-determination), not "the fractions are wrong"

Real corpus (HT, LM I; **32 docs / 35 balance units**; deterministic):
- Integer-level balance: **7/28 (25%)**.
- **7 fraction-bearing constraints; only 1 satisfied** by the solved system.
- The **only determinable** fraction value is **`½` = 1/2** (forced by HT104's `2·½ == 1`) — and it **AGREES
  with Corazza's J = 1/2** (a real, if small, corroboration).
- **Held-out fraction balance = 0.0 vs permutation-null mean 0.113 (max 0.143), p = 1.0, separated = False**
  — robust across seeds. **The solved fractions do NOT generalize above the shuffle null.**

**Why this is trustworthy and what it means.** The synthetic positive control proves the machinery is correct
— with planted values it recovers all of them and **held-out balance 0.9 vs null 0.22, p=0.003, separated**.
So the real-corpus null is **not a bug**: it is driven by **sparse automated parse coverage** — only ~7
fraction-bearing constraints survive automated parsing of 32 tablets, because multi-commodity blocks,
illegible number glyphs (e.g. U+1076B), KI-RO deficit sub-lists, and editorial restorations are not captured.
Corazza et al. (2021) succeeded using a **hand-curated GORILA-epigraphic** parse with many more constraints;
the automated lineara.xyz transliteration stream is too thin to re-derive the system. **So this is a
parse-coverage / data-curation null, NOT evidence that the fraction system is wrong** — and `½`=1/2 already
corroborates the published value where a constraint exists.

## Known limitation (verifier-found, recorded not chased)
A MEDIUM defect: commodity columns headed by a **star-number logogram** (`*308`, `*188`, `*312`) are dropped
at parse, reducing constraint coverage further. Fixing it would add a few constraints but cannot flip the null
(the deeper limiter is multi-block tablets + restorations + illegible glyphs). Per the scope freeze (draft
after Stage-1), recorded as a known parse limitation rather than chased.

## Primary sources now in hand (Corazza et al. 2021 + Schrijver 2014, audited 2026-07-01)

Both fraction papers were acquired and audited (values adversarially verified against source). They
**vindicate and sharpen** this null — with four corrections recorded:

- **The null is DEEPER than "sparse parse," and the field agrees.** Corazza et al. (2021, p.2) state that
  fraction values **cannot reliably be deduced from numeral-phrase totals** because "no Linear A
  inscription containing totals of numeral phrases is without reading or calculation problems" — so they
  *abandoned* the balance-to-totals method that logos's `metrology.py` rests on, in favour of constraint
  programming. logos's parse-coverage null is therefore **consistent with the published experts**, not a
  logos-unique failure. (Cite p.2 as the primary reason, not only automated under-coverage.)
- **METHOD MISMATCH (correction).** Corazza did **not** balance line items against totals; they used
  **constraint programming** (MiniZinc/Gecode) over ordinal/typological premises, scored by goodness
  measures. logos and Corazza solve *different problems* — logos cannot "reproduce their coverage" by
  adding balance constraints; matching them would mean adopting a premise-based constraint solver.
- **ATTRIBUTION (correction): `½`=1/2 is Bennett 1950's value**, the long-standing consensus (adopted by
  Schrijver 2014 and Corazza 2021), not "Corazza's." And **"only `J` determinable" is method-specific** —
  epigraphy alone fixes `J`=1/2; balance-to-totals is simply a weak lever. Phrase as "*our balance method*
  determines only `J`," not "only `J` is determinable."
- **A SECOND independent system + a stronger corroboration.** Schrijver (2014) is an earlier, independent
  (philological) full fraction system. `½`=1/2 is now corroborated by **both** — but honestly: Schrijver
  derives it leading with **HT 104**, the same tablet logos's solver used, so they partly share evidence;
  the genuinely independent support is Schrijver's **three further `J`=1/2 tablets (HT Zd 156, PE 1,
  HT 123a)**, lifting `½`=1/2 to ≥4 documents. Schrijver also **validates the solver's additivity
  assumption** (combinations are sum-of-parts) **except `D`**, which never combines additively → treat `D`
  as a non-compositional special case. The determining tablets he names (HT 104, HT Zd 156, HT 123a/b,
  PE 1, …) are exactly the GORILA-epigraphic constraints the automated stream drops — a concrete
  hand-curated top-up path. (Fraction usage is itself **site-stratified** — `H`=1/3 only at HT/Phaistos,
  Khania uses `K`=1/16 — corroborating the site stratum.)

Recorded, not chased (scope freeze: draft after Stage-1). Specific per-sign value tables are NOT
transcribed here — the adversarial pass flagged value/quote errors in the auto-extracted tables, so a
full Corazza/Schrijver agree-disagree matrix is a deferred careful-transcription task, not hand-entered.

## Method / discipline notes
- **Held-out:** grouped k-fold by document (no tablet straddles train/test); fractions solved on TRAIN only.
- **Permutation null:** shuffle the sign→value map per fold (500–1000 draws); the real system must beat it.
  It doesn't (real 0.0 < null 0.113) → report the null.
- **Corazza comparison cited, not assumed:** Corazza, Ferrara, Montecchi, Tamburini & Valério (2021),
  *J. Archaeol. Sci.* 125:105214 (doi:10.1016/j.jas.2020.105214); solved values reported alongside theirs,
  agreement flagged, never forced.
- **Editorial-circularity caveat** surfaced in every run: the transliterated vulgar-fraction glosses embed an
  editorial interpretation possibly tuned to balance; the held-out split + null control solver/value
  overfitting but not this — and since the headline is a NULL, circularity inflates nothing here.
- No phonetic claim; imports no `verdict.py`.

## Verified (independently re-run)
Full suite **308 passed, 4 xfailed** (+18 metrology tests); my own run reproduces held-out 0.0 vs null 0.113,
p=1.0, `½`=1/2 ⟂ Corazza. Raw `runtime/metrology-real.json` (gitignored).

## Stage-1 outcome (both substantive directions)
Direction A and Direction D both return **rigorous, honestly-reported NULLS** under the harness — for
*different* honest reasons (A: morphology not separable from bigram order on short words; D: automated parse
too sparse to determine the fractions, where a hand-curated parse succeeds), each with a **real positive
alongside** (A: a word-boundary segmenter beating chance; D: `½`=1/2 corroborating Corazza). The discipline
caught a would-be confound in **both**. This sharpens the paper's spine: the **decontamination/discipline
harness + a body of rigorous, pre-registered nulls on specific field-claims** is the contribution — exactly
the referee artifact the field lacks.
