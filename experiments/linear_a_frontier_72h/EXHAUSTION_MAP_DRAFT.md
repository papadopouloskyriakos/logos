# Frontier-72h — Exhaustion Map (§12 capstone) — **LIVING DRAFT**

> **STATUS: DRAFT. NOT FINALIZED.** Finalization is mechanically gated by `scripts/clock_check.py`
> (`finalization_authorized = now ≥ 2026-07-11T03:20Z AND completed_substantive_epochs ≥ 18`).
> As of last edit: **59 substantive epochs banked**, gate **BLOCKED** (time_gate open ~48.8h to 2026-07-11T03:20Z).
> This document accretes as epochs bank; it becomes the §12 capstone **only** when the clock authorizes.
> A null/negative here is a **result**, never an early stop. Counts are read from `EPOCH_LEDGER.yaml`.
> Layer ceiling across the entire campaign: **L2/L3**. Transfer licences earned: **none**. No decipherment.

## Outcome tally (generated from `EPOCH_LEDGER.yaml` — 59 substantive epochs, each classified once)

| Bucket | N | What it means |
|---|---|---|
| **Load-bearing cross-site positives** | **20** | Survived calibrated/adaptive null + PC + cross-site/held-out, coordinator-reverified (§A) |
| Bounded negatives | 16 | Well-powered PC-passed tests returning informative *absence* (§B) |
| No-power | 3 | Detector had no power for the question (§C) |
| Underpowered | 3 | Real data limit, stated (§C) |
| Machinery-uninformative | 8 | Instrument failed its own calibration → **no LA inference drawn** (§C) |
| Prospective / provenance / other | 9 | Frozen-prospective, provenance, source-blocked channels (§D) |

*20 positives / 16 bounded-negatives / 14 no-inference (no-power + underpowered + machinery-uninf) / 9 setup.
Zero of the 20 positives rises above L2/L3. The honest denominator is on-screen: this is a structural map, not a
reading.*

### Discipline-compliance certificate (Art. V layer ceiling + Art. XV transfer licences) — mechanically audited
Scanned all 59 ledger entries: **no epoch is worded above L3** (layers: L1×9, L2×7, L2/L3×36, older-unlabelled×14;
zero L4+); **every `licences_changed` field is `none`** (no result silently earned a licence); the 7 transfer
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

**A1. A-prefixation** — the strongest held-out LA positive. A word-initial `A-` sign functions as a
**productive, positional (heading/initial), selectional prefix**.
`E022` (survives LA-structure-matched adaptive null) → `E023` (cross-site robust, 9/10 sites) →
`E024` (multi-axis robust: support-type + chronological phase) → `E025` (productive slot, not a few frozen
forms) → `E050` (selectional — constrains what follows). Reinforced by `E039` (the initial-concentration
extends to a **small prefix inventory**, not `A-` alone).

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
- **Saturation status: re-opened, then narrowing.** After E057, the remaining observed channels are largely
  exhausted (word, sign, numeral, div, nl all tested); `other` (n=1056) is a heterogeneous grab-bag (damaged/
  uncertain marks) unlikely to yield clean structure. Candidate successors: whether the `div`/`nl` delimiters
  interact (nested entry vs line structure), or whether the E056 logogram class aligns with E057's entry-word
  slot (risk: circular). Each must clear the distinct + well-powered + non-circular bar before launch; if none
  does, the productive work is capstone assembly.

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
