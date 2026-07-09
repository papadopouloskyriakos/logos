# Frontier-72h — Exhaustion Map (§12 capstone) — **LIVING DRAFT**

> **STATUS: DRAFT. NOT FINALIZED.** Finalization is mechanically gated by `scripts/clock_check.py`
> (`finalization_authorized = now ≥ 2026-07-11T03:20Z AND completed_substantive_epochs ≥ 18`).
> As of last edit: **70 substantive epochs banked**, gate **BLOCKED** (time_gate open ~45h to 2026-07-11T03:20Z).
> This document accretes as epochs bank; it becomes the §12 capstone **only** when the clock authorizes.
> A null/negative here is a **result**, never an early stop. Counts are read from `EPOCH_LEDGER.yaml`.
> Layer ceiling across the entire campaign: **L2/L3**. Transfer licences earned: **none**. No decipherment.

## Outcome tally (generated from `EPOCH_LEDGER.yaml` — 70 substantive epochs, each classified once)

| Bucket | N | What it means |
|---|---|---|
| **Load-bearing cross-site positives** | **28** | Survived calibrated/adaptive null + PC + cross-site/held-out, coordinator-reverified (§A) |
| Bounded negatives | 16 | Well-powered PC-passed tests returning informative *absence* (§B) |
| Site-local structural findings | 3 | Well-powered PC-passed *detections* that landed on the site-local side of the dichotomy (§B) |
| No-power | 3 | Detector had no power for the question (§C) |
| Underpowered | 3 | Real data limit, stated (§C) |
| Machinery-uninformative | 8 | Instrument failed its own calibration → **no LA inference drawn** (§C) |
| Prospective / provenance / other | 9 | Frozen-prospective, provenance, source-blocked channels (§D) |

*28 positives / 16 bounded-negatives + 3 site-local findings / 14 no-inference (no-power + underpowered +
machinery-uninf) / 9 setup. Zero of the 28 positives rises above L2/L3. The honest denominator is on-screen:
this is a structural map, not a reading. (One positive, `E067` depth-2 concentration, is global + only partial
cross-site — 2/6 sites — and is flagged as such in §A1.)*

### Discipline-compliance certificate (Art. V layer ceiling + Art. XV transfer licences) — mechanically audited
Scanned all 70 ledger entries (layer counts script-generated): **no epoch is worded above L3** (layers: L1×9,
L2×16, L2/L3×36, L3×3, older-unlabelled×6; zero L4+); **every `licences_changed` field is `none`** (0/70
non-none; no result silently earned a licence); the 7 transfer
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

### The organizing finding (the through-line of Section A)
> **Shared script + shared administrative grammar generalize cross-site; word-content / topic / lexicon is
> site-local.** The fingerprint (A4), the ledger syntax (A2), and the positional/prefix morphology (A1, A3)
> travel across sites; the specific counted vocabulary does not (see §B: `E032`, `E034`, `E035`, `E053`).
> ⇒ Linear A behaves as a **concatenative / prefixing administrative script with a genuine shared grammar but
> site-local vocabulary.** All L2/L3 — structure, not sound or meaning. No transfer licence follows.

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
> These three refine the through-line: not only is *vocabulary* site-local, but **scribal register** (word-
> length, accounting scale) and the **metrological realization** of the shared entry template are site-local
> too. The shared cross-site layer is the positional *grammar + script*; the quantitative/graphic *magnitudes*
> and lexicon are local.

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
- **Saturation status (as of 70 epochs): genuinely narrowing.** Probed-and-declined this session: commodity-
  logogram cross-site (underpowered, 2 sites), word-vs-logogram magnitude register (underpowered), cross-site
  grammar prediction (covered by E047), further register tests (pattern-repeat, not distinct). The remaining
  candidates are refinements or underpowered; each must still clear the **distinct + well-powered + non-circular
  + PC-gated** bar before launch, else the productive work is capstone assembly. **Do not declare hard
  saturation** — the `other`-channel lesson stands: inspect a channel before calling it empty.

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
- **All 20 load-bearing positives** have full artifacts (prereg + plan_hash + machinery + result + report) and are
  coordinator-verified on *both* observed statistics and (where simulated-null-dependent) reconstructed nulls
  (`VERIFICATION_AUDIT.md`).
- **Documented limitation (not backfilled):** three *early, non-positive* epochs — E008/E009 (stroke channel, §D
  SOURCE_BLOCKED) and E013 (decomposition-neutral, §B, superseded by E018) — carry `prereg.md` + `result.json`
  but no separate `plan_hash.txt` (an early-phase convention before the hash file was standardized). They were
  pre-registered; only the separate frozen-hash file is absent. **A post-hoc hash is deliberately NOT added** —
  backfilling would fake the freeze. None is load-bearing.
- **Worker scratch files** (`_run.*`, `run_analysis.py`, `_pc_tmp.json`) remain untracked: intermediate GLM
  working files, non-canonical; the frozen record is the committed prereg/plan_hash/machinery/result/report.

**Assessment (corrected after E060): near-complete but the "complete" call was premature.** E058/E059-era
assessments twice declared saturation while the corpus `other` token class (logograms + fractions) sat
UNEXAMINED — `E060` then found a strong cross-site positive there (the metrological/logographic entry template).
Lesson recorded: **do not declare a channel absent without inspecting it.** Current state: 21 verified positives
/ 16 bounded-negatives, all L2/L3, no licence, no decipherment. Any remaining untested observed structure should
be inspected before a completeness claim; the clock-gated §12 finalization remains blocked until 2026-07-11T03:20Z.
