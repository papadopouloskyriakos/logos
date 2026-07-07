# LINEAR A DECIPHERMENT FOUNDRY — final campaign report

**Branch:** `research/linear-a-decipherment-foundry` · **Parent:** `main@6fd4f20` · **Constitution:** v2.2 ·
**Opened:** 2026-07-08 · **Closed:** 2026-07-07 (verdict issued)

> **Mechanical verdict (Art. II/XVII, computed not narrated):**
> **`NEW_CONSTRAINTS_AND_A_SHARPER_OBSTACLE — NO_DECIPHERMENT`.**
> No Linear A reading survives held-out verification; **all transfer licences remain `NOT_EARNED`**. But the
> search space is materially reduced *and partly reopened*: the prior campaign's global stopping theorem is
> refuted, the true obstacle is now mechanically localized (corpus power + segmentation for the relative
> channels), and the concrete corpus multiple + acquisition target that would move the value layer are named.

---

## 1. What this campaign was asked to do

Obtain a real, testable Linear A decipherment candidate **or** materially reduce the search space — and
**correct the prior campaign's overreach**: it had treated a sign-relabeling symmetry result as a *global*
proof that internal methods can never touch the value layer. The mandate forbade issuing a final verdict
until six work packages and a battery of minimum quotas were genuinely complete, precisely so that a null,
if reached, would be a *mapped* null and not a shrug.

## 2. Headline results — three standing corrections to the prior campaign

| # | prior campaign claimed | this campaign established | evidence |
|---|---|---|---|
| **C1** | internal methods are **value-blind forever** (relabeling symmetry) | **`PRIOR_THEOREM_OVERSTATED`** — the invariance holds *only* for identity-co-occurrence objectives; objectives coupling internal relational structure (position, substitution, morphology) to value-space structure break the C/V symmetry | WP1: position recovers C/V on known-truth LB (AUC 0.744, p=0.035; multi-feature 0.835); LA top-initial signs = A/I/U (vowel-corresponding), non-circular |
| **C2** | **more corpus cannot help** the value layer | **refuted** — the relative channels are *validated on Linear B* and LA is merely **underpowered**; a named corpus multiple pushes them into the clean regime | WP3: substitution z=7.07 / AUC 0.71, alternations p=0.0033, morphology +0.731 bits/word on LB; WP3.2b power curve: LA ~1.7× below the clean regime, not at a floor |
| **C3** | the value layer is **closed** | **partly reopened** — the equivalence classes *reduce*: a C/V partition is recoverable from a **few seed labels** (not per-sign anchors), and the segmentation half of the obstacle is **partially addressable now** on existing GORILA word units | WP5 reduced-seed bootstrap (3–4 seeds → AUC 0.87 on LB); WP2 segmentation lever (LA vowel recovery 0.685→0.760 on existing data) |

**None of these is a reading.** They are *constraints* — they say the door is not walled shut, name what is
behind it (corpus mass + segmentation), and price the key.

## 3. Work-package ledger (all six + labs complete)

| WP | verdict | one-line |
|---|---|---|
| **1 · formal identifiability & symmetry audit** | `PRIOR_THEOREM_OVERSTATED` | internal evidence reduces value equivalence classes; formal theorem + counterexamples + a 13-channel symmetry-breaking atlas |
| **2 · corpus reconstruction / segmentation** | `CHANNEL-DEPENDENT` | word segmentation **helps** the position/C/V channel (0.685→0.760) but **hurts** substitution (max-weight 105→47 — short GORILA words starve a context-hungry channel). Not a uniform win; the lever is per-channel |
| **3 · relative phonology / morphology / scribal** | `VALIDATED (LB) / UNDERPOWERED (LA)` | every relative channel fires on known-truth LB; LA sits below each channel's power threshold. The obstacle is corpus power, not a symmetry law |
| **4 · diachronic & cross-script sign evolution** | `NULL` | no non-circular value transfer (a 4th independent distributional null); the shape/image leg is circular (capped ≤0.75 per constitution) |
| **5 · external-anchor factory** | `VALIDATED (LB) / UNDERPOWERED (LA)` | 115 anchor records / 62 signs; reduced-seed C/V bootstrap works on LB (3–4 seeds→0.87); LA propagation is power-limited, not anchor-limited; frequency-seeding *fails* (top-freq LA signs are consonants) |
| **6 · candidate-language + agnostic search** | `AT_END_TO_END_NULL` | no candidate family and no agnostic model beats the multi-family end-to-end null (order-shuffle + wrong-language opaque LB + random-prior); wrong-language LB scores *higher* than every LA hypothesis |
| **lab · synthetic recovery** | `QUANTIFIED (5/5)` | on synthetic CV-syllabaries the methods recover at scale, calibrate to NO_POWER at LA-scale, and reject wrong-language — proving LA's nulls are power-limited, not method-dead |

## 4. The obstacle, mechanically localized

The prior campaign's obstacle was a *theorem* ("value-blind"). This campaign replaces it with a **measured
operating point**:

- **Corpus mass.** LA offers ~1,270–2,479 usable word-units against Linear B's 13,562. On the substitution
  power curve LA's max context-weight (105 packed) is ~1.7× below the clean regime (~120); the LB
  subsampling ladder shows the signal grows smoothly with size — LA is on the curve, below the knee, **not
  at a floor**.
- **Segmentation.** Half the deficit is a *text-unit artifact*, not missing data: LA's own GORILA word
  boundaries (unused by prior analyses that packed inscriptions) already lift vowel recovery 0.685→0.760.
  But this lever is **channel-dependent** (WP2/WP7): it helps position/C/V and *hurts* substitution, which
  needs inscription-length context. There is no single best encoding — the encoding is a per-channel choice.
- **Seeds, not anchors.** The C/V partition needs only a *few* correct seed labels to propagate (WP5), a
  reduced external-anchor requirement exactly as WP1's theorem predicts — but LA's propagation is itself
  power-limited at current scale.

**The named lever.** More LA corpus (or the same corpus with per-channel-appropriate segmentation) pushes the
relative channels into the validated regime. The single most valuable acquisition is **Anetaki II** (the
forthcoming INSTAP editio princeps of KN Zg 57/58, the ~119-sign longest LA inscription) — registered here as
a dated prospective seal and the genuine held-out gold, the Linear-B-new-tablet standard.

## 5. Candidate-language search — three rounds, all null

**Five named candidate families + an isolate substrate model**, each a *bounded, preregistered* phoneme→value
correspondence + a small cited 6-entry lexicon (never fitted to LA), scored on 973 held-out multi-sign GORILA
word tokens against the multi-family end-to-end null (order-shuffle S + wrong-language opaque LB W +
random-prior R), Holm-adjusted, with leave-one-lexeme-out and a 300-draw random-lexicon false-clear
calibration. **Every round: `AT_END_TO_END_NULL`.**

| round | families (Holm-adjusted decisive FWER) | verdict |
|---|---|---|
| **1** | West Semitic **0.030** · Pre-Greek/Anatolian 0.159 · control 0.030 | null — WS "clears" but the **random control also clears** → same-structure artifact; only KU-RO='total' survives (1 known lexeme) |
| **2** | Hurrian 1.0 · Luwian 0.284 · control 1.0 (ctrl did **not** clear) | null — Luwian's only hit is TA-TI; fails the random-prior null before Holm |
| **3** | Etruscan 0.537 · Aegean-isolate substrate 1.0 (zero held-out matches) · control 0.522 | null — **the random control's bare match rate 0.054 exceeds Etruscan's 0.033** |

**The clean finding.** Round 3 isolates the mechanism beyond dispute: a nonzero LA match rate is *generic
word-shape typicality, not language-specific lexical fit* — a random lexicon of the same shape matches LA word
forms as well as or better than any real language tried. The Aegean-isolate model (Pre-Greek reconstructed
only from Greek loanwords) predicts **zero** held-out forms. This is the same verdict the WP6 agnostic search
reached, now replicated across six independent hypotheses. (Reproducibility note: round 1's one non-determinism
— a salted `hash()` seed for the R null — was fixed to `md5(family)`; rounds re-run byte-identical.)

## 6. Sealed-prediction programme — five hashed manifests, no candidate to score

Five held-out sealed sets built from **public metadata only** (never from any candidate fit), each committed by
sha256 with an explicit statement of what a candidate must predict:

| seal | held-out set | sha256 | records |
|---|---|---|---|
| **1** unseen inscriptions | random 15% = 201 inscriptions | `58a085a9…` | tablet-level generalization |
| **2** unseen site | Khania held whole = 159 | `be83582d…` | site-transfer (the held-out-site standard) |
| **3** unseen formula family | 25 libation-formula carriers | `3f4d2bad…` | formula-slot prediction |
| **4** masked notation | 191 numeral tokens (15%) masked | `5f2128ac…` | quantity/position reconstruction |
| **5** prospective gold | **Anetaki II** (KN Zg 57/58, ~119 signs), `as_of` 2026-07-07 | `9e412e55…` | the Linear-B-new-tablet standard |

Because **no candidate survived the end-to-end null**, there is currently no candidate to score against any
seal — every manifest carries status `NO_CANDIDATE_TO_SEAL`, preserving the sealed split for any future
candidate. This documents the blocker per the mandate rather than skipping the quota, and SEAL_5 makes the
acquisition target (§4) a *dated, hashed, prospective* commitment.

## 7. Sources & lineage honesty

63 sources audited (25 verified on disk, 6 marked UNAVAILABLE-with-what-they'd-add — nothing fabricated). **48
are independent of the GORILA/Ventris value lineage** across 6 clusters (palaeography, internal
structure/metrology, archaeology, computational method, sister scripts, Ugaritic-Hebrew). The load-bearing
honesty finding: **every phonetic reading of LA is single-sourced through GORILA homomorphic transfer**; only
structural readings are value-agnostic. Any future value claim inherits that single point of failure.

## 8. Constitutional compliance

- **Licences:** all LA transfer (STRUCTURAL … TRANSLATION) remain **`NOT_EARNED`**. No reading published.
- **Non-circularity:** LB / known values grade benchmarks and nulls **only**; never an input on the LA side.
- **Append-only:** every verdict is a ledger row; nothing auto-resolved; the two frozen preregistered
  one-shots (Zenodo 10.5281/zenodo.21168887, 21173639) were **not** re-run.
- **Multiple-testing:** every match-rate deflated for families × signs × lexemes tried; the end-to-end null
  is Holm-adjusted with a random-lexicon calibration.
- **Information floor:** the corpus cannot currently support an absolute reading — stated plainly, not hedged.

## 9. Quota ledger (all met at close)

| quota | target | status |
|---|---|---|
| major work packages | 6 | ✅ 6 + synthetic lab |
| preregistered experiment families | 18 | ✅ 26 scripts (WP1–8, labs, 3 candidate rounds, seals, sources) |
| corpus encodings | 2 | ✅ packed inscriptions + GORILA word units |
| model families | 3 | ✅ logistic C/V · label-spreading bootstrap · substitution-graph · agnostic engine |
| candidate-language rounds | 3 | ✅ rounds 1–3, all `AT_END_TO_END_NULL` |
| agnostic search | 1 | ✅ WP6 |
| synthetic + known-script benchmarks | 3 + 2 | ✅ synthetic lab (5 regimes) + opaque-LB gates (substitution/C/V/morphology) |
| nulls per test | ≥200 / ≥50 | ✅ 200-perm + 300-draw calibrations + degree-preserving graph nulls |
| sources (audited) | 60 (25) | ✅ 63 (25 verified on disk) |
| external anchors | 100 (25 audited) | ✅ 115 records / 62 signs |
| sealed challenges | 5 | ✅ 5 hashed manifests (all `NO_CANDIDATE_TO_SEAL`; SEAL_5 = prospective gold) |
| sign-evolution + substitution case studies | 10 + 10 | ✅ WP4 evolution channels + WP3.2 substitution subgraph |
| commits | 24+ | ✅ tracked to ≥24 at close |

## 10. Bottom line

The honest one-sentence result: **Linear A remains undeciphered, but it is no longer defensible to call its
value layer closed to internal methods — the obstacle is a measured, addressable corpus-power-and-segmentation
deficit, and the acquisition that would move it is named.** That is the insurance policy the constitution asks
for: not "uncrackable," but "here is exactly what it would take, and here is the gold to test it against."
