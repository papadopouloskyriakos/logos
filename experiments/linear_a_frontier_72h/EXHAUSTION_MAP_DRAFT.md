# Frontier-72h — Exhaustion Map (§12 capstone) — **LIVING DRAFT**

> **STATUS: DRAFT. NOT FINALIZED.** Finalization is mechanically gated by `scripts/clock_check.py`
> (`finalization_authorized = now ≥ 2026-07-11T03:20Z AND completed_substantive_epochs ≥ 18`).
> As of last edit: **78 distinct epochs banked** (85 ledger rows; 7 early epochs carry superseding duplicates, deduped by `epoch_id`, last-wins), gate **BLOCKED** (time_gate open ~42h to 2026-07-11T03:20Z).
> This document accretes as epochs bank; it becomes the §12 capstone **only** when the clock authorizes.
> A null/negative here is a **result**, never an early stop. Counts are read from `EPOCH_LEDGER.yaml`.
> Layer ceiling across the entire campaign: **L2/L3**. Transfer licences earned: **none**. No decipherment.

## Outcome tally (generated from `EPOCH_LEDGER.yaml` — 84 distinct epochs, each classified once)

| Bucket | N | What it means |
|---|---|---|
| **Load-bearing cross-site positives** | **33** | Survived calibrated/adaptive null + PC + cross-site/held-out, coordinator-reverified (§A) |
| Bounded negatives | 19 | Well-powered PC-passed tests returning informative *absence* (§B) |
| Genre-/site-local structural findings | 5 | Well-powered PC-passed *detections* that landed on the site-local / genre-graded side of the dichotomy (§B) |
| Positive-hardening / qualification | 3 | Robustness passes that *qualified* or *hardened* a positive without overturning it (`E075` on `E072`, §A7; `E083` qualifying `E079`, `E084` hardening `E080`, §A8) |
| No-power | 3 | Detector had no power for the question (§C) |
| Underpowered | 3 | Real data limit, stated (§C) |
| Machinery-uninformative | 9 | Instrument failed its own calibration → **no LA inference drawn** (§C; `E082` added — the pitch metric is uncalibratable at glyph level) |
| Prospective / provenance / other | 9 | Frozen-prospective, provenance, source-blocked channels (§D) |

*33 positives / 19 bounded-negatives + 5 genre-/site-local findings / 3 positive-hardening-or-qualification / 15 no-inference
(no-power + underpowered + machinery-uninf) / 9 setup. Zero of the 33 positives rises above L2/L3. The honest
denominator is on-screen: this is a structural map, not a reading. Three positives carry breadth caveats, flagged
in §A: `E067` depth-2 concentration is global + only partial cross-site (2/6 sites); `E072` libation-formula
canonical order is real but **narrow** (hardened by `E075`: effective-n 8 inscriptions / 6 sites, hub-dominated);
`E078` glyph-size economy replicates in 2/5 sites (the powered ones) + corpus-wide + within-class. **Four** of the
33 positives are on a GENUINELY NEW data modality — SigLA per-glyph BOUNDING BOXES (§A8: glyph size E076,
size-economy E078, horizontal glyph-spacing E079, vertical line-spacing E080), untouched by the first 75
linear-token epochs; a fifth spatial test (`E081` left-margin justification) landed **site-local** (§B) — the
spatial modality has its OWN shared-vs-site-local split (spacing shared cross-site, justification a site register).*

### Discipline-compliance certificate (Art. V layer ceiling + Art. XV transfer licences) — mechanically audited
Scanned all 84 distinct ledger entries (layer counts script-generated, deduped by `epoch_id`): **no epoch is
worded above L3** (layers: L1×5, L2×22, L2/L3×35, L3×8, early-pre-convention-unlabelled×14; **zero L4+** — E079/
E080/E081 and the E082–E084 spatial-decomposition arc are all L2, positions-only); **every `licences_changed`
field is `none`** (0/84 non-none — 70 explicit `none` + 14 early entries predating the field; no result silently
earned a licence); the 7 transfer
licences remain exactly as of 2026-07-07 (STRUCTURAL `NOT_EARNED`, FUNCTIONAL `NOT_YET_EARNED`, SEMANTIC+
`NOT_AUTHORIZED`). Every mention of "phonetic value / meaning / language" across the positives is a **disclaimer**,
not a claim. The positives are **direct structural observations of Linear A's own distribution** (Linear B is
control-only in every `non_circular` field) — licence-*independent* L2 descriptions, not cross-script transfers.
**No decipherment; no licence; no layer breach.**

## What this campaign is
A time-boxed, pre-registered, positive-control-gated sweep of the **structural** questions the Linear A
corpus can answer at L2/L3 (writing-system + administrative-grammar structure), each epoch a mechanical
held-out test on a *distinct* question, executed by GLM-5.2 through the gated runner and independently
re-verified by the coordinator. The point is to **map the frontier**: what the corpus structurally supports,
what it bounds as absent, and what it simply cannot resolve — so a future decipherment attempt knows exactly
where the load-bearing structure is and where the walls are.

---

## A. LOAD-BEARING CROSS-SITE POSITIVES — the certified structural portrait (L2/L3)

These survived a calibrated/adaptive null, a positive control, AND cross-site / held-out robustness, and were
independently recomputed by the coordinator.

**A1. A-prefixation + prefixing morphology** — the strongest held-out LA positive. A word-initial `A-` sign
functions as a **productive, positional (heading/initial), selectional prefix**.
`E022` (survives LA-structure-matched adaptive null) → `E023` (cross-site robust, 9/10 sites) →
`E024` (multi-axis robust: support-type + chronological phase) → `E025` (productive slot, not a few frozen
forms) → `E050` (selectional — constrains what follows). Reinforced by `E039` (the initial-concentration
extends to a **small prefix inventory**, not `A-` alone).
**The underlying positional-entropy typology is itself cross-site robust:** `E064` word-**initial** sign
entropy is significantly lower (more concentrated) than word-final, globally (A=+0.223 bits vs ~0 within-word-
shuffle null, p=5e-4) and in 5–6/10 sites, LOO-robust (drop-HT strengthens it) — the prefixing signature
generalizes beyond the single `A-` slot. `E067` the concentration extends to a **second slot** (a decaying
prefix-*zone*, A0=0.375 > A1=0.233 > A2=0.128, all p≤5e-4) — *global + partial cross-site only* (pos1 sig in
2/6 sites; interpretively ambiguous between true prefix-stacking and prefix→continuation selection, E050).
**And the A-marked vocabulary is itself more cross-site-shared:** `E068` A-prefixed word-forms recur across
sites at 0.69 vs 0.32 for *frequency-matched* non-A forms (D=+0.37, stratified perm p=7e-3, power=1.0) — so the
`A-` prefix marks a **pan-administrative sub-lexicon** that partially bucks the site-local-vocabulary trend
(small informative base, 16 A-types; prime for prospective replication).

**A2. Administrative ledger grammar** — the corpus has a real, cross-site accounting syntax.
`E031` **word → numeral** order (entry then quantity), certified under a *calibrated pair-flip* null
(independently reproduced: word_first=1040, P=0.99); `E037` **line-final numeral** template — numerals are
overwhelmingly line-final within numeral-bearing ledger lines (0.87–0.99 vs a ~0.45 null, p=2e-4; the exact
fraction is line-definition-sensitive — see `VERIFICATION_AUDIT.md`); `E044` numeral groups are
**single-numeral-dominant** (simple quantity slots, not compound numerals); `E057` the explicit **divider
(`div`) is a lexical word-separator that respects `word+numeral` as a bound entry unit** — divs sit at
word|word boundaries far above a gap-reshuffle null (0.749 vs 0.403, p=1e-3) and are massively depleted at the
word|quantity boundary (13 observed vs ~142 expected, p=1e-3), significant on both statistics in 3/6 sites
(HT, Khania, Zakros; non-sig sites are ceiling-limited), LOO-robust. Independent gap-reshuffle null *matched*
the epoch's null (0.405 vs 0.403), S2 count exact.
**`E060` completes the entry template via the metrological/logographic layer** (the corpus `other` tokens =
logograms + fractions, previously unexamined): **logogram-class tokens are entry-initial and precede a numeral**
(commodity → quantity, 0.58 vs 0.26 null, p=0, 3/3 sites) and **fraction-class tokens are entry-terminal** (the
fractional remainder closes the entry, 0.99 vs 0.46 null, p=0, 3/3 sites). Both observed statistics *and* both
within-line permutation nulls independently reconstructed. ⇒ the **complete Linear A ledger entry template**:
`[commodity-logogram | word] → integer-numeral → fraction → line-end`. L2 strict: token *classes* by position;
logogram identity and fraction value unused.
**`E069` adds a positional word-length facet:** entries **open with a longer "head" word** (entry-initial words
2.55 signs vs 1.76 internal, ~11σ above a within-line word-order shuffle null, p=5e-4), cross-site (3/3 sites),
LOO-robust, and **not** the `A-`-prefix confound (survives excluding all A-initial words: 0.72, p=5e-4) — a
name-then-modifiers layout, orthogonal to the E028/E065 length axes.
*Nuance (from `E070`, a site-local finding — see §B): the template's positional **skeleton** (frac→nl, numeral
line-final, word→num) is cross-site, but the **fraction's metrological attachment is NOT uniform** — Haghia
Triada realizes num→frac (0.48, "N and a fraction"), Khania attaches fractions to words (num→frac 0.055);
site-contrast p=2e-4. So E060's "complete template" is cross-site in skeleton, site-local in metrological
realization.*

**A3. Positional sign specialization** (`E043`, cross-site robust after the `E041`/`E042` power+calibration
repairs) — signs carry **position-dependent roles** within the word (templatic organization), stable across
sites.

**A4. Shared writing-system fingerprint + logo-syllabic architecture** — `E036` cross-site **sign-frequency
concordance** (the sign inventory + frequencies are shared across sites, the "one script" leg); `E056` the
sign inventory **distributionally partitions into a logogram-like class** (17 signs: numeral-adjacent, stands
alone, short words) **vs a syllabogram-like class** (44 signs: compositional) — silhouette 0.543 vs null 0.196
(~14σ, perm p=0), recovered from *pure distribution* with no sign values, and surviving a tautology probe
(numeral-adjacency+length alone → silhouette 0.565). This is the expected **logo-syllabic** architecture of an
Aegean administrative script, recovered blind. *Weak legs (honest): the numeral-adjacency discrimination is
marginal (MW p=0.044) and cross-site replication is weak (ARI 0.095, above chance-floor but low; one site-pair
near chance) — so `CROSS_SITE_ROBUST` is earned at the floor: corpus-wide strong, site-by-site weak. L2
distributional labels, NOT epigraphic identifications, NOT readings.*

**A5. Document registers** — `E028` **document-class word-length signature** (support type predicts a
word-length register); `E047` the **document token-type grammar is held-out predictable** (Markov > unigram);
`E049` document-level **sign co-occurrence / topic association** is cross-site (caveated: association, not a
lexicon). `E026` word-**final** positional class is concentrated (a terminal analog of the `A-` initial slot).
`E061` the corpus's most frequent `other` sign (**U+1076B**, n=474) is a **systematic line-isolated document
marker** — it occupies its own content-line 91% of the time vs a ~20% position-shuffle null (p=5e-4), in
**5/5 sites**, LOO-robust; observed and null both independently reconstructed. A standalone section/entry/
separator-type structural element (L2: position only, no reading).
`E062` sharpens U+1076B's role: it is **document-peripheral** — it sits on the first or last content-line 69%
vs a 38% line-shuffle null (p=5e-4), both poles enriched (heading + colophon), interior *depleted*, **6/6
sites**, LOO-robust. `E063` shows the standalone-marker inventory is **position-differentiated**: a second
line-isolated token (the em-dash U+2014) occupies the **complementary interior** niche (peripheral 0.12 vs
U+1076B's 0.69; never a heading; contrast relabel p=0) — LA documents deploy ≥2 line-isolated markers with
complementary structural roles (U+2014 is HT-anchored → cross-site not certified, and may be a transcription
ruling-mark; the complementarity holds either way; L2 position only).

**A6. Allographic / scribal-shape structure is real** — `E017`/`E020` site-level **allograph** variation
survives an adaptive null (sign *shape* varies by site, distinct from the shared frequency fingerprint);
`E018` the `E013` component-composition channel survives its adaptive null.

**A7. The libation formula has a cross-site canonical ORDER (but narrow breadth) — and it decomposes cleanly.**
The Linear A libation (stone-vessel/dedicatory) corpus is the classic "religious formula" register. This session
decomposed the word "formula" into its two parts on one corpus:
`E072` **the ORDER is a cross-site canonical sequence** — when two libation word-forms co-occur, their relative
order is perfectly consistent (all 13 testable pairs and all 10 cross-site pairs order-consistency 1.000 vs a
within-inscription order-shuffle null ~0.74; A_cross 10/10 vs null ~3.7–4.3; every perm p=5e-4), PC-passed
(planted order detected 20/20, false-pos 0.0, power 1.0; empirical null ~0.74, not naive-0.5). **`E075` hardens
this positive and QUALIFIES it to NARROW breadth** (invariant #3 + Art. VIII effective-n): the order signal is
genuine and robust — it survives *every* leave-one-site-out (incl. the hub site Iouktas at the power floor,
p=0.044) and the leave-the-hub-inscription-out (drop `IOZa2` alone → n_cross=4, p=0.008); C_cross stays exactly
1.0 in every powered leave-out (it never collapses toward the null). BUT its cross-site *breadth* rests on a small
effective-n — 10 raw pairs but only **8 carrier inscriptions across 6 sites**, with the hub inscription `IOZa2`
(Iouktas) an endpoint of all 10 and ~3 inscriptions carrying most weight (dropping the top-2 carriers → a
powerless n_cross=3). So `E072` reads as *"a canonical order shared across a small set of libation inscriptions
spanning several sites,"* **not** a broad corpus-wide formula. *Honest framing:* the canonical libation-formula
order is a **mainstream-known** structure (Davis, Duhoux, Schoep); `E072`'s value is mechanical confirmation under
a proper held-out null + the machinery-detects-real-order demonstration, not a novel discovery. L3: anonymous
sign-tuples, structural ORDER only — no reading, no meaning, no licence.
*The complement is `E071` (§B): the libation formula's **vocabulary** (which forms recur, and their cross-site
spread) is fully **frequency-explained** — so "the formula" = frequency/site-local vocabulary (E071) + cross-site
canonical order (E072). And the ORDER rigidity is **genre-graded** (`E073`, §B) but genre↔site **confounded**
(`E074`, §B) — see the genre-site-confound note.*

**A8. Graphic conventions on a NEW data modality (SigLA per-glyph BOUNDING BOXES).** All 75 linear-token epochs
used the silver stream; `E076`–`E081` opened the untouched **spatial** modality (glyph bbox positions + sizes,
decoded via `scripts/sigla_decode.py`; licensed-derived JSON gitignored). **Four cross-site positives** map two
veins — glyph SIZE and glyph PLACEMENT (a 2D ruled grid) — plus one bounded negative and one site-local qualifier:

*Glyph-SIZE vein:*
- `E076` **glyph SIZE is a shared cross-site graphic convention** — per-sign within-document-normalized size
  correlates strongly across all 5 testable site-pairs (r 0.70–0.85, median 0.79; perm p ≤ 1.6e-3 vs a
  sign-label-shuffle null; PC power 1.0). Size patterns with the **shared** sign-frequency fingerprint (E036/A4),
  NOT with site-local allograph SHAPE (E017/E020/A6) — the graphic realization SPLITS: *size shared, shape local.*
  *(Honest: substantially intrinsic-form-driven — the spatial analog of the E036 frequency fingerprint, not an
  independent size-marking system.)*
- `E078` **glyph size shows ECONOMY OF EFFORT** — more frequent signs are drawn SMALLER (r_all=−0.351, freq-shuffle
  perm p=4e-4), a spatial **Zipf's-law-of-abbreviation** analog. It **survives the sign-class control** (within
  the AB syllabary r_AB=−0.317, p=5e-3; the AB/A classes have ~equal mean size, so it is NOT the logogram-
  complexity confound) and replicates in the 2 powered sites (HT p=7e-4, Khania p=3e-3). A genuine functional-
  adaptive graphic property, recovered blind. Breadth caveat: 2/5 sites powered; corpus-wide + within-class primary.
- (Bounded negative `E077`, §B: glyph size carries NO cross-site *positional* information — it is not a spatial
  heading marker.)

*Glyph-PLACEMENT vein — a 2D RULED GRID, evenly spaced in both axes, cross-site (3/3 sites each):*
- `E079` **horizontal glyph SPACING is regular** — within-line center-to-center pitch is far more uniform than a
  random gap-allocation null that preserves row span + glyph count (global median doc pitch-CV 0.329 vs null 0.743,
  perm p=0, ratio 0.44); significant in **3/3** testable sites (HT/Khania/Zakros). Glyphs are laid along the line
  with ruled/monospaced-like regularity (CV ~0.33 = regular but hand-inscribed, not typeface-perfect).
- `E080` **vertical LINE SPACING is regular** — the orthogonal axis: row-to-row pitch is far more uniform than a
  clustering-conditional random row-allocation null (global median doc line-pitch-CV 0.118 vs null 0.354, perm p=0);
  significant in **3/3** sites. Line spacing (CV ~0.11) is even MORE regular than glyph spacing — coarser ruling is
  more deliberate. *(Coordinator-adjudicated: the gate flagged a null-definition mismatch; independent
  reconstruction confirmed the worker's clustering-conditional null is the correct/exchangeable one — the
  unconditional null has PC false-positive rate 1.00 vs conditional 0.05; verdict robust under both, perm p=0. The
  inverse of E059 — see `epochs/EPOCH-080/COORDINATOR_NOTE.md`. A methodology datapoint: the gate + independent
  null-reconstruction catch null issues in BOTH directions.)*
- **DECOMPOSITION of the "2D grid" (`E082`→`E083`→`E084`) — the grid is NOT symmetric; it decomposes into a
  deliberate VERTICAL ruling + a horizontal SIZE byproduct.** E079/E080's pitch-CV metric conflates deliberate
  spacing with glyph SIZE (pitch = gap + glyph-width/height; uniform sizes E076 regularize pitch even with random
  gaps). Three epochs separated them with *size-preserving* nulls (keep each glyph's actual width/height, randomize
  only the gaps):
  - `E082` (hardening) first flagged the confound but its glyph-level PC could not calibrate (glyph-size
    regularization) → `MACHINERY_UNINFORMATIVE`; the raw threshold-sweep was verified robust, but a failed PC earns
    no certification (the third PC-adjudication pattern after E059-overturn / E080-confirm: uncalibratable → no
    certification; `epochs/EPOCH-082/COORDINATOR_NOTE.md`).
  - `E083` **HORIZONTAL = WIDTH-DRIVEN** — against a width-preserving random-gap null, observed pitch-CV is NOT below
    the null (0.338 vs 0.271, perm p=1.0, all 3 sites; PC passed). The inter-glyph GAPS are not deliberately regular
    → **E079's "ruled" horizontal spacing is a downstream byproduct of uniform glyph size, NOT deliberate even
    spacing.** (Append-only qualification of E079 — its measurement stands, its "deliberate spacing" reading is
    refuted.)
  - `E084` **VERTICAL = DELIBERATE** — against a height-preserving random-gap null, observed line-pitch-CV IS
    significantly below the null (0.111 vs 0.161, perm p=0.002, ratio 0.69, HT + Zakros significant / Khania
    underpowered; PC passed, coordinator-stabilized). The inter-line GAPS **are** deliberately regular → **E080's
    vertical line spacing is a genuine deliberate scribal convention** (confirmed + hardened).
- **Revised synthesis (E079/E080 as decomposed by E083/E084):** the Linear A "page" is **deliberately ruled in the
  VERTICAL** (line spacing genuinely controlled, cross-site — E084/E080) and shares glyph-SIZE conventions
  (E076/E078); the **HORIZONTAL** within-line glyph-pitch regularity (E079) is a *byproduct* of that uniform glyph
  size, **not** a deliberate spacing convention (E083). So it is not a symmetric "monospaced grid" — it is
  **ruled lines filled with uniformly-sized glyphs.** A genuine, non-obvious refinement earned by adversarial
  hardening (invariant #3).
- **Qualifier (`E081`, §B — site-local):** the grid is evenly *spaced* cross-site but left-*justified*/anchored only
  at Haghia Triada (rows left-aligned, right ragged: HT perm p=2e-4; Khania NOT, p=0.55; Zakros underpowered,
  p=0.11). So the "shared 2D grid" is qualified — **spacing conventions are shared, margin justification is a site
  register** (the spatial modality's own microcosm of the through-line).

The spatial modality is L2 (opaque sign catalog IDs; positions only; NO value/reading) and joins the SHARED
cross-site layer (spacing + size), with justification on the site-local side. It also **vindicates 'inspect before
saturation' a THIRD time** (after the `other` channel and the libation register): the frontier was not exhausted —
it had an untouched modality with a whole family of distinct, powered questions. **Spatial vein now mapped:** glyph
size (shared/economy/not-positional), 2D spacing (cross-site), margin justification (site-local). Remaining spatial
candidates were assessed and DECLINED as derivative or infeasible: reading-direction (trivially circular, geometric
order = transcription, median agreement 1.000); AB/A class-size (intrinsic-form); columnar structure (mechanically
implied by E079∩E081); glyph aspect-ratio (trivially intrinsic-form); numeral spatial zoning (INFEASIBLE — SigLA
sign_class has N=1, Linear A numerals are not cataloged as SigLA signs).

### The organizing finding (the through-line of Section A)
> **Shared script + shared positional grammar/ORDER generalize cross-site; vocabulary, scribal
> register, and metrological realization are site-local.** *Cross-site:* the sign fingerprint (A4), the ledger
> syntax skeleton (A2: word→num, line-final numeral, divider, entry template, entry-head length E069), the
> positional/prefix morphology (A1: A-prefix, initial-concentration typology E064, and even the A-marked
> sub-lexicon E068), positional specialization (A3), the document-marker system (A5: E061–E063), the
> **libation formula's canonical ORDER** (A7: E072, real but narrow per E075), and — on the NEW spatial modality —
> the **graphic size conventions** (A8: glyph size shared E076, size-economy E078) AND the **deliberate VERTICAL
> line-ruling** (A8: E080 regular / E084 deliberate-beyond-height, 2/3 sites) all travel across sites — and the
> token-class grammar is held-out **predictable** on unseen sites (E047, 9/9). *(NB after the E082→E084
> decomposition: the horizontal glyph-pitch regularity E079 is NOT an independent deliberate convention — it is a
> byproduct of uniform glyph SIZE E076, per E083 WIDTH-DRIVEN — so the shared spatial layer is deliberate LINE
> spacing + glyph SIZE, not a symmetric monospaced grid.)*
> *Site-local:* the counted vocabulary (§B: E032/E034/E035/E053), the **libation formula's vocabulary** (E071 —
> frequency-explained, like admin), document typology (E058), sub-lexical structure (E059), **scribal register**
> (word-length E065, accounting-scale E066), the **metrological realization** of the entry template (fraction
> attachment E070), **glyph SHAPE** (allograph E017/E020 — note the split: glyph *size* is shared A8/E076 while
> *shape* is local), and — newly — the **left-margin JUSTIFICATION** of the 2D grid (E081: HT left-justifies, Khania
> does not; the grid's SPACING is shared but its ANCHORING is a site register) do not. **The order/grammar-vs-
> vocabulary split now holds within a single register:** the
> libation "formula" is cross-site in ORDER (E072) but site-local/frequency-explained in VOCABULARY (E071) — a
> clean one-corpus microcosm of the whole through-line.
> ⇒ Linear A behaves as a **concatenative / prefixing administrative script with a genuine shared positional
> grammar and ordering but site-local lexicon, register, and quantitative habits.** All L2/L3 — structure, not
> sound or meaning. No transfer licence follows.
> **Load-bearing caveat (E074):** *genre* and *find-site* are ~83% confounded in this corpus (administrative texts
> at palatial sites, libation texts at cult sites; only Palaikastro mixes both at scale). Any claim phrased as a
> **genre** effect (e.g. E073 "order rigidity is libation-specific") is confounded with **site** and cannot be
> attributed to genre beyond the established site-locality — see the genre-site-confound note in §B.

---

## B. BOUNDED NEGATIVES — what the corpus says Linear A is *NOT* (the insurance-policy value)

Each is a well-powered, PC-passed test that returned a *bounded absence* — informative, not a failure.

- **Not suffix-inflecting like Greek.** `E038` no positional-entropy asymmetry (no final-suffix concentration),
  `E040` intra-word sign repetition at chance → **no final-inflectional paradigm**; the productive morphology
  is **initial/prefixing** (§A1), *structurally unlike* Greek's final-inflection. (See "typological read" below.)
- **No recoverable commodity lexicon.** `E053` entry-words (counted items) are **not** drawn from a
  restricted, repetitive closed set beyond a size-matched null; `E033` no entry-vs-non-entry structural
  contrast; `E032` recurrent cross-site admin word-forms not recoverable (machinery-uninformative).
- **Document typology is site-local.** `E058` structural document types *do* exist globally (k=2, silhouette
  0.345, perm p=0.002) and are not merely the archaeological support label (support-ARI 0.39), **but they do
  not transfer across sites** — a typology trained on Haghia Triada applied to Khania gives ARI −0.10 (worse
  than the ~0 null). Independently recomputed exact. This places document *typology* on the **site-local** side
  of the through-line, opposite the cross-site-shared script + grammar.
- **Sub-lexical structure is site-local too (coordinator-corrected).** `E059` cross-site sign-bigram/trigram
  recurrence does **not** exceed a per-site unigram-preserving null (bigram obs 96 vs null 87, p=0.09; trigram
  obs *below* null) — the overlap is fully explained by shared single-sign frequencies. So there is **no
  shared multi-sign morphology beyond signs + the A-prefix**; candidate shared affixes/formulae do not exist
  above chance. *(GLM initially reported this as a cross-site positive via a null-construction bug — all sites
  drawn from one shared unigram distribution; the coordinator caught and overturned it on independent
  recomputation. See `epochs/EPOCH-059/COORDINATOR_CORRECTION.md`. Invariant #2/#3 firing on a real fabricated
  positive.)*
- **Administrative quantities are small bounded tallies.** `E054` numeral magnitudes are Benford-**deviant**
  *because they are small* (median 4, 71% ≤ 10) — Benford is inapplicable, not a fabrication signal;
  `E055` document-class accounting *scale* is **site-confounded / unanswerable** (numeral-bearing supports are
  geographically segregated).
- **Sign sequence carries little local redundancy.** `E048` near-random sign-level entropy rate (short words →
  limited sign-to-sign predictability).
- **`A-` heading is positional, not an independent document-function marker.** `E051` the A-heading × accounting-
  intensity interaction is **site-local**; `E034` A-heading role site-local; `E035` terminal total-slot site-local.
- **The libation formula's VOCABULARY is frequency-explained, not a cross-site shared lexicon.** `E071` the
  famous recurring dedicatory forms (A-TA-I-*301-WA-JA at 5 sites, SI-RU-TE 5, I-PI-NA-MA 5, JA-SA-SA-RA-ME 4)
  appear at many sites **because they are frequent** — the cross-site recurrence mass sits *below* a token→site
  reassignment null (S_obs=20 vs null ~25–33, ratio<1, perm p≈1), exactly like the administrative corpus
  (S_obs=23 vs null ~92–97). PC-passed (planted formula detected p=0.002, power 1.0). A guilty-until-proven-
  innocent catch: a literature-famous "cross-site formula" fails the frequency-controlled test at the word-form
  level. (Its cross-site signal lives in ORDER, not vocabulary breadth — see §A7/E072.)
- **Genre and find-site are confounded — cross-genre lexicon partition is UNDERDETERMINED.** `E074` the libation
  and administrative genres share almost no vocabulary (20 shared forms, Jaccard 0.024; global token→genre
  permutation null ~69, p≈0 — a striking apparent "genre-specialized lexicons" effect), **but it COLLAPSES under
  site control** (site-stratified null 21.5 ≈ observed 20, p=0.26): once each form's find-site is fixed, no
  residual genre effect is detectable. ~83% of tokens are genre-determined by a single-genre site; only Palaikastro
  mixes both at scale. PC-passed with the site-stratified control **powered** (0.96) — so `UNDERDETERMINED` reflects
  the structural confound, not a power failure. **This downgraded a p≈0 apparent positive to underdetermined at
  design time** (invariant #3), and records a campaign-wide limit: *any* genre-phrased claim is confounded with
  site (see the through-line caveat).
- **Glyph size is NOT a spatial positional marker (new modality).** `E077` glyph SIZE does not mark document-
  initial prominence cross-site (global D_init=−0.057, p=0.81; only Haghia Triada trends initial-larger at a
  borderline 1/5-site p=0.048 ≈ chance; the other 4 sites trend initial-smaller). PC-passed (planted prominence
  detected power 1.0, false-pos 0.04). So glyph size is a shared per-SIGN convention (A8/E076) that carries no
  positional/heading information — unlike the campaign's positional findings which live in sign identity (E022),
  marker position (E062), and word length (E069). Insurance value: size won't flag document structure.
- Earlier bounded/marginal: `E002` motif within-equivalent, `E010` door marginal, `E012` allograph-structure
  confounded, `E013` decomposition neutral, `E046` word-length shape inconclusive.

**Site-local structural findings (well-powered *detections* that landed site-local — they populate the
site-local side of the through-line, distinct from bounded *absences* above):**
- **Word-length is a site register.** `E065` controlling for document class (stratified permutation), word-
  length still carries a significant residual **site** effect (combined KW H=89.6, perm p=0; all 3 testable
  classes) — raw site H=223 → ~40% survives class-control. Sites differ systematically in how long their words
  are, within the same class.
- **Accounting scale is a site register.** `E066` within the Tablet class, numeral magnitude differs by site
  (KW H=45.1 vs ~4 null, p=2e-4), **general and LOO-robust** across all 5 sites (survives dropping the 79%-
  dominant HT and the outlier Tylissos); per-site medians span 1→10. (Single-class scope: only Tablets have
  cross-site numeral power.)
- **Fractional attachment is a site convention.** `E070` what a fraction attaches to is site-local — Haghia
  Triada realizes num→frac (0.48, metrological remainder), Khania attaches fractions to words (num→frac 0.055);
  site-contrast perm p=2e-4. (Nuances E060's entry template — see §A2.)
- **Word-ORDER rigidity is genre-graded (but genre↔site confounded).** `E073` administrative texts have a
  weak-but-real within-inscription word-order preference (C_glob=0.839 vs shuffle null 0.745, perm p=1.5e-3; **not**
  bag-of-words) that is significantly **less rigid** than the libation formula's perfect order (admin bootstrap
  upper 0.887 ≪ libation 1.000, Δ=0.161); PC-passed with a discrimination gate (separates rigid C≈1.0 from
  weak-order C≈0.72). So the *perfectly rigid* canonical order is a property of the libation register, while admin
  ordering is only loosely preferred. **Caveat (E074):** "libation-specific" is confounded with "cult-site-specific"
  — the mechanical rigidity contrast stands; its *genre* attribution does not (genre↔site ~83% confounded).
- **Left-margin JUSTIFICATION is a site register (new spatial modality).** `E081` rows are left-anchored (left edge
  aligned, right ragged) GLOBALLY (S_obs=+0.459 vs edge-swap null ~0, perm p=2e-4; median normalized left-edge
  spread 0.66 vs right 1.25) but the effect is **site-local to Haghia Triada** (HT perm p=2e-4; Khania NOT, S≈0,
  p=0.55; Zakros positive-but-underpowered, p=0.11 stable at 20k draws) — 1/3 sites significant. 3-arm PC passed
  (detect left / reject centered / reject right), coordinator-reproduced. This is the **spatial modality's own
  microcosm of the through-line**: the 2D grid's *spacing* is cross-site shared (E079/E080, 3/3 each) but its
  *margin justification* is a site register — like word-length (E065) and accounting-scale (E066). A deliberate
  **guard against over-claiming a "shared 2D grid."**
> These **five** refine the through-line: not only is *vocabulary* site-local, but **scribal register** (word-
> length, accounting scale), the **metrological realization** of the shared entry template (fraction attachment),
> the **rigidity of word-order** (loose in admin, rigid in libation), and the **margin justification** of the shared
> 2D grid (E081: HT left-justifies, Khania does not) are genre-/site-graded too. The shared cross-site layer is the
> positional *grammar + ordering + script* plus the 2D-grid *spacing*; the quantitative/graphic *magnitudes*,
> lexicon, order-*rigidity*, and layout *justification* are local/register-bound.

---

## C. NO-POWER / MACHINERY-UNINFORMATIVE — honest "instrument gave no reading" (NOT LA evidence)

These draw **no** inference about Linear A; the instrument lacked power or failed its own calibration, so the
epoch is logged as uninformative and excluded from both the positive and negative tallies. Recording them is
an integrity requirement (no silent drops).

- No-power: `E007` role induction, `E011` both detectors, `E014` register strata.
- Machinery-uninformative / harness-not-validated: `E019`, `E021`, `E027`, `E029`, `E030`, `E032`, `E041`
  (superseded by `E042`/`E043`), `E052` (Zipf/Heaps fitter).
- Underpowered (real limit, stated): `E042` (→ certified at `E043`), `E045`, `E055`.

---

## D. PROSPECTIVE / PROVENANCE / SOURCE-BLOCKED
- `E004` seal frozen prospective, `E005` provenance established, `E009` stroke channel calibrated-useful **but**
  the stroke / 3D channels are **SOURCE_BLOCKED** (data does not exist accessibly — see anchor-lattice memory).
- `E003`/`E006` cross-script bridge / seed-efficiency not achievable at the LA seed budget.

---

## E. Typological read (speculative, explicitly ABOVE the earned layer — flagged, not claimed)
The certified L2/L3 shape — **productive initial/prefixing morphology (A1, A39), no final-inflectional
paradigm (E038/E040), concatenative administrative syntax (A2)** — is *consistent with* (does NOT identify)
prefixing/agglutinative or root-and-prefix typologies rather than a Greek-style suffix-inflecting fusional
language. **This is a typological *silhouette*, not a language identification** — no LANGUAGE_ID licence is
earned or implied, and no specific family is claimed. Recorded as a successor-hypothesis direction only.

---

## F. Open at the saturation boundary (candidate successors — run only if genuinely distinct & powered)
- **`E056` (BANKED → §A4):** dual sign-class induction → `DUAL_SIGN_CLASS_CROSS_SITE_ROBUST` (logo-syllabic
  partition, strong global, weak cross-site).
- **`E057` (BANKED → §A2):** divider-token structural role → `DIV_LEXICAL_SEPARATOR_CROSS_SITE` — a genuinely
  strong new positive that **corrected a premature saturation call** (the `div` token was an untested observed
  channel). Lesson recorded: "saturation" claims must be checked against *all* observed token channels, not
  just the dimensions recently probed.
- **The `other` channel was NOT a grab-bag — it was the richest untested vein (lesson re-confirmed).** The
  earlier dismissal of `other` (n=1056) as "unlikely to yield clean structure" was **wrong**: inspecting it
  produced FOUR positives — `E060` (metrological entry template: logogram→num, fraction→terminal), `E061`
  (U+1076B line-isolated marker), `E062` (that marker is document-peripheral), `E063` (marker-system
  position-differentiation). The `div`/`nl` interaction candidate was examined and **declined as foregone**
  (div←word, num-terminal→nl already banked in pieces → would be trivial-recovery, not a distinct test).
- **Successors mined this session (E064–E070):** initial-concentration typology cross-site (`E064`), its depth
  (`E067`, partial), A-vocab cross-site sharing (`E068`), entry-head word-length (`E069`) on the shared side;
  word-length register (`E065`), accounting-scale register (`E066`), fractional attachment (`E070`) on the
  site-local side. The cross-site held-out grammar-prediction synthesis is already banked (`E047`).
- **The LIBATION/religious register was the next untested vein (E071–E075) — same lesson re-confirmed.** After the
  `other`-channel and administrative dimensions were mapped, the libation (stone-vessel) corpus remained a distinct
  functional register that had not been probed as a genre. Inspecting it produced a coherent five-epoch arc:
  `E071` (formula vocabulary frequency-explained → §B), `E072` (formula canonical ORDER cross-site, a POSITIVE →
  §A7), `E073` (order rigidity genre-graded → §B), `E074` (cross-genre lexicon partition = genre-site confounded /
  underdetermined → §B; records a campaign-wide confound), `E075` (hardened E072 to real-but-narrow → §A7). Net: one
  new cross-site positive (E072, narrow), two bounded negatives (E071, E074), one genre-graded finding (E073), one
  positive-qualification (E075), plus a structural limit (the genre↔site confound). The vein is now mapped.
- **The SPATIAL modality (SigLA bounding boxes) was the next untouched vein (E076–E081) — the lesson holds a third
  time, and the vein is now MAPPED.** All 75 prior epochs used the linear silver token-stream; the SigLA per-glyph
  bboxes (positions + sizes) were untouched. Opening them gave **4 cross-site positives** — E076 glyph size shared,
  E078 size-economy-of-effort, E079 horizontal glyph-spacing regular, E080 vertical line-spacing regular (E079+E080
  = a cross-site 2D ruled grid) — plus 1 bounded negative (E077 size not positional) and 1 **site-local** finding
  (E081 left-margin justification = HT register, §B), all L2, all coordinator-verified (E080 involved a
  coordinator-adjudicated null, the inverse of E059). **Remaining spatial candidates assessed and DECLINED** as
  derivative or infeasible: reading-direction (trivially circular); AB/A class-size + glyph aspect-ratio
  (intrinsic-form); columnar structure (mechanically implied by E079∩E081); numeral spatial zoning (INFEASIBLE —
  SigLA sign_class N=1, numerals not cataloged). The spatial vein's high-value, distinct, powered questions are
  now exhausted.
- **Saturation status (as of 84 epochs): genuinely narrowing; genre + FULL glyph-spatial vein now mapped AND
  internally decomposed.** Probed-and-declined earlier:
  commodity-logogram cross-site (underpowered, 2 sites), word-vs-logogram magnitude register (underpowered),
  cross-site grammar prediction (covered by E047). Scouted after E075 (E072/E073/E074 successors): admin-order-by-
  support (confound/underpowered), matched-form rigidity contrast (n small), a site+genre factorial (redundant with
  E074's confound), Palaikastro-only genre test (n=49, underpowered), within-genre cross-site spread (covered by
  E032/E071) — none clears the **distinct + well-powered + non-circular + PC-gated** bar. The SigLA **spatial
  layout** channel (once flagged as the next "new data") has now been mined to exhaustion (E076–E081) AND its
  central positive **decomposed by a robustness triplet** (E082→E084, §A8): the E079/E080 "2D ruled grid" resolves
  into a **deliberately-ruled VERTICAL line convention** (E084: obs << height-preserving null, 2/3 sites, PC-passed
  — hardens E080) plus a **HORIZONTAL glyph-pitch regularity that is a byproduct of uniform glyph SIZE (E076), NOT
  a deliberate gap convention** (E083: obs at/above a width-preserving null, PC-passed — qualifies E079's
  interpretation); the calibration limit that surfaced this (E082 MACHINERY_UNINFORMATIVE — the pitch metric
  conflates spacing with glyph width) is itself an honest, banked no-inference. Remaining structural questions need
  genuinely new data (glyph images / strokes — SOURCE_BLOCKED) or **L4+** (barred). The productive work is now
  capstone assembly; launch only if a genuinely-distinct powered channel appears. **Do not declare hard
  saturation** — the `other`- and libation-channel lessons both stand: inspect a channel before calling it empty.

---
*Draft assembled by the coordinator from `EPOCH_LEDGER.yaml`; every count/verdict is ledger-derived.
Finalization remains mechanically blocked until the clock authorizes.*

---

## H. Reconciliation with the frozen TACL paper (append-only integrity — Art. XVII)
The paper (`paper/tacl/body.tex`, byte-frozen, SUBMITTED) is checked for consistency with this campaign's
findings. **No contradiction found; no erratum required.** The one apparent tension resolves cleanly:

- **Paper §6 reports morphology `NO POWER`** (LA 4/16 affixes vs the `L_fake` bigram floor 6/16; the same test
  recovers LB inflection 9/16 — a real detector, LA's null is short-form-limited). This is a **supervised
  multi-affix paradigm-recovery** test: can a full inflectional/affixal *system* be recovered? On LA, no.
- **This campaign's headline is A-prefixation `A_PREFIX_*_ROBUST`** (§A1). This is a **single-slot distributional
  positional-enrichment** test: is the sign `A` over-represented word-initially, cross-site? It is.
- **These do not conflict.** A corpus can fail to yield a recoverable multi-affix paradigm (paper's NO POWER)
  while exhibiting *one* robust positional prefix-slot (this campaign). The frontier result is narrower,
  distributional, and strictly **L2/L3** — it never claims the recoverable morphological *system* the paper
  correctly found absent. Indeed the paper's own typology discussion already characterizes LA as
  *"agglutinative and prefixing … [prefix A]"* (§ rebuttal), which the A-prefix finding **corroborates and
  quantifies**, not contradicts.
- **Other probes are consistent:** the paper's metrology null + the campaign's small-bounded-numeral findings
  (E054/E055) agree; the paper's segmentation-supported result stands; the campaign touches no phonology (all
  L2/L3), so the paper's phonology data-limited null is untouched. The campaign's transfer-licence state matches
  the paper's ("no decipherment; methods paper").

**Bottom line:** the frontier campaign *extends and corroborates* the frozen paper (adds a shared-grammar /
site-local-content structural portrait at L2/L3) without contradicting any published claim. If any future
finding *does* contradict the paper, it is filed as an ERRATUM against the frozen record — never a silent rebuild.

---

## I. Completeness & limitations (completeness-critic pass)
Mechanical audit of the record's completeness:
- **All map sections present** (A–F, H, tally, discipline-compliance certificate). No structural gap.
- **All 31 load-bearing positives** have full artifacts (prereg + plan_hash + machinery + result + report) and are
  coordinator-verified on *both* observed statistics and (where simulated-null-dependent) reconstructed nulls
  (`VERIFICATION_AUDIT.md`). The E071–075 genre arc extends this: E072 (positive) and E075 (its hardening) both had
  their cross-site/leave-out nulls reconstructed from scratch; E074's site-stratified confound null likewise. The
  E076–078 spatial modality was independently re-decoded from SigLA and its cross-site correlations / frequency-
  shuffle / position-shuffle nulls reconstructed from scratch by the coordinator.
- **Documented limitation (not backfilled):** three *early, non-positive* epochs — E008/E009 (stroke channel, §D
  SOURCE_BLOCKED) and E013 (decomposition-neutral, §B, superseded by E018) — carry `prereg.md` + `result.json`
  but no separate `plan_hash.txt` (an early-phase convention before the hash file was standardized). They were
  pre-registered; only the separate frozen-hash file is absent. **A post-hoc hash is deliberately NOT added** —
  backfilling would fake the freeze. None is load-bearing.
- **Worker scratch files** (`_run.*`, `run_analysis.py`, `_pc_tmp.json`) remain untracked: intermediate GLM
  working files, non-canonical; the frozen record is the committed prereg/plan_hash/machinery/result/report.

**Assessment (updated after E075): near-complete; saturation calls have twice been premature, so held loosely.**
E058/E059-era assessments twice declared saturation while the corpus `other` token class (logograms + fractions)
sat UNEXAMINED — `E060` then found a strong cross-site positive there; and the 70-epoch assessment predated the
libation/religious register, which `E071–E075` then mapped (one narrow positive + confound + hardening). Lesson
re-confirmed THREE times: **do not declare a channel absent without inspecting it.** After the genre vein, the
SigLA **spatial modality** (per-glyph bounding boxes) — flagged here as "needs new data" — was itself opened
(E076–081: 4 cross-site positives + 1 bounded negative + 1 site-local finding), then internally **decomposed** by a
robustness triplet (E082–E084). Current state (84 distinct epochs):
**33 verified positives / 19 bounded-negatives + 5 genre-/site-local findings / 3 positive-hardening-or-qualification**,
all L2/L3, no licence, no decipherment. The genre vein is mapped (genre↔site confound E074 bounds all genre claims) and
the FULL glyph-spatial vein is now mapped: glyph SIZE (shared E076 / not-positional E077 / economy E078) AND glyph
PLACEMENT (a cross-site ruled layout — horizontal spacing E079 + vertical line-spacing E080 — whose left-margin
JUSTIFICATION is site-local E081). The placement positive was then **resolved into its two axes** (E082–E084): the
VERTICAL line-ruling is **deliberate beyond row height** (E084 hardens E080, PC-passed, 2/3 sites), while the
HORIZONTAL glyph-pitch regularity is a **byproduct of uniform glyph SIZE (E076), not a deliberate spacing
convention** (E083 qualifies E079, PC-passed) — surfaced by the honest E082 calibration limit
(MACHINERY_UNINFORMATIVE). So the "2D grid" is more precisely **deliberately-ruled lines filled with
uniformly-sized glyphs**, not a symmetric monospaced grid. Remaining spatial candidates were assessed and DECLINED
as derivative (columnar ≈ E079∩E081) or infeasible (numeral zoning — sign_class N=1); deeper spatial or L4+
questions need image data (SOURCE_BLOCKED) or are barred. Any remaining untested *observed* channel should still be inspected before a
completeness claim. The clock-gated §12 finalization remains blocked until 2026-07-11T03:20Z.
