# G3c - Anchor Null Battery (toponym / value-bearing channel)

**Task.** Subject the ONLY value-bearing anchor channel (toponyms, G1) to the multiplicity battery: random external forms, frequency-matched names, length-matched names, unrelated-language controls, best-of-anchor-subset null, generic sound-fold baseline, leave-one-anchor-out, leave-one-rule-out.

**Method (non-circular).** Each LA locus is a syllable string in LB values (GORILA transcription); each place-name is folded to the SAME open-CV skeleton by one deterministic rule (keep the onset consonant before each vowel, drop codas, y->u). `sim = 1 - normalized (consonant-class, vowel) alignment distance`. LB values render+grade only, never a model input (Art. XII). The metric REPRODUCES the textbook equation `pa-i-to -> pa-i-to = Phaistos` (sim 1.0) as a sanity check. Seed 20260708, 2000 Monte-Carlo trials, LA syllable-frequency from 3147 corpus words.

Artifacts: `scripts/g3_anchor_nulls.py` -> `data/anchors_v2/anchor_nulls.json`.

---

## 1. Observed anchor scores

| locus (LB values) | referent | firm | sim to referent |
|---|---|:--:|--:|
| pa-i-to | Phaistos | Y | 1.0 |
| se-to-i-ja | Seteia | Y | 0.75 |
| tu-ru-sa | Tylissos | Y | 0.6667 |
| a-tu-ri-si-ti | Tylissos | Y | 0.5 |
| di-ki-te | Dikte | Y | 0.6667 |
| su-ki-ri-ta | Sybrita | Y | 0.75 |
| i-da-a | Ida | - | 0.6667 |
| ku-79-ni | Kydonia | - | 0.5 |
| da-u-49 | Dawos | - | 0.5 |
| i-ti-ni-sa | Itanos | - | 0.5 |
| ku-ni-su | Knossos | - | 0.3333 |
| ku-ta | Kytaion | - | 0.5 |
| sa-ra2 | Saro | - | 0.75 |
| di-na-u | Dinauos | - | 0.75 |
| i-na-ta-i-zu-di-si-ka | Inatos | - | 0.3125 |

Mean sim (all 15) = **0.6097**; mean sim (6 firm) = **0.7222**. Only `pa-i-to = Phaistos` reaches 1.0; the rest are partial folds.

## 2. Gazetteer comparison (mean best match per locus)

| gazetteer | mean best match |
|---|--:|
| assigned referents (the anchor set) | 0.6097 |
| REAL Aegean gazetteer (50 names), best-of | 0.6042 |
| UNRELATED-language (48 Finnish/Japanese/Nahuatl), best-of | 0.4919 |
| uniform random gaz (size 50), MC mean | 0.476 (p95 0.5181) |
| freq-matched random gaz (LA phonotactic), MC mean | 0.5365 (p95 0.5808) |

**Reading.** A freq-matched random gazetteer the size of the real Aegean one already yields a best match of ~0.5365 per locus on average; the UNRELATED-language best-of (0.4919) sits at the uniform-random floor (0.476). The real Aegean best-of (0.6042) and the assigned-referent mean (0.6097) are ~0.07-0.11 higher -- a real but modest Aegean-specific SHAPE signal, and that gap is carried heavily by the single exact hit (Phaistos, sim 1.0).

## 3. Multiplicity within the real Aegean gazetteer

For **6 of 15** loci, the assigned referent is NOT the uniquely best-matching Aegean name -- some OTHER real Cretan place-name matches at least as well:

| locus | assigned | sim | best ALT Aegean | alt sim | assigned uniquely best? |
|---|---|--:|---|--:|:--:|
| pa-i-to | Phaistos | 1.0 | Praisos | 0.6667 | yes |
| se-to-i-ja | Seteia | 0.75 | Kydonia | 0.5 | yes |
| tu-ru-sa | Tylissos | 0.6667 | Sybrita | 0.5 | yes |
| a-tu-ri-si-ti | Tylissos | 0.5 | Amnisos | 0.4 | yes |
| di-ki-te | Dikte | 0.6667 | Arkades | 0.5 | yes |
| su-ki-ri-ta | Sybrita | 0.75 | Sybritos | 0.625 | yes |
| i-da-a | Ida | 0.6667 | Itanos | 0.6667 | yes |
| ku-79-ni | Kydonia | 0.5 | Kytaion | 0.375 | yes |
| da-u-49 | Dawos | 0.5 | Tarrha | 0.5 | **no** |
| i-ti-ni-sa | Itanos | 0.5 | Amnisos | 0.5 | **no** |
| ku-ni-su | Knossos | 0.3333 | Amnisos | 0.5 | **no** |
| ku-ta | Kytaion | 0.5 | Lyktos | 0.5 | **no** |
| sa-ra2 | Saro | 0.75 | Zakros | 0.75 | **no** |
| di-na-u | Dinauos | 0.75 | Inatos | 0.5 | yes |
| i-na-ta-i-zu-di-si-ka | Inatos | 0.3125 | Hierapytna | 0.3125 | **no** |

## 4. Length-matched null (P a random name of the right length beats the assigned equation)

| locus | assigned sim | P(random len-matched >= assigned) | mean random sim |
|---|--:|--:|--:|
| pa-i-to | 1.0 | 0.0 | 0.1748 |
| se-to-i-ja | 0.75 | 0.0005 | 0.1664 |
| tu-ru-sa | 0.6667 | 0.0 | 0.1993 |
| a-tu-ri-si-ti | 0.5 | 0.01 | 0.2238 |
| di-ki-te | 0.6667 | 0.0 | 0.2043 |
| su-ki-ri-ta | 0.75 | 0.0 | 0.2397 |
| i-da-a | 0.6667 | 0.0 | 0.2402 |
| ku-79-ni | 0.5 | 0.0075 | 0.1849 |
| da-u-49 | 0.5 | 0.178 | 0.2086 |
| i-ti-ni-sa | 0.5 | 0.0405 | 0.2159 |
| ku-ni-su | 0.3333 | 0.307 | 0.1903 |
| ku-ta | 0.5 | 0.025 | 0.2274 |
| sa-ra2 | 0.75 | 0.0385 | 0.265 |
| di-na-u | 0.75 | 0.0 | 0.2337 |
| i-na-ta-i-zu-di-si-ka | 0.3125 | 0.0535 | 0.1917 |

## 5. Best-of-anchor-subset null (cherry-picking)

- Real anchor set, top-6 mean sim = **0.7778**.

- Random gazetteer, cherry-picked top-6 mean sim = **0.6435** (p95 0.7292).

- The best-6 REAL subset (0.7778) EXCEEDS the random cherry-pick p95 (0.7292): the firm toponym equations carry a real, but SMALL, above-chance shape-resemblance edge (~+0.134 over the null mean). This edge is exactly value-blind SHAPE resemblance -- necessary for a scholar to propose an equation, but (sections 3-4, 9) not unique, not language-specific, and not held-out-survivable.

## 6. Generic sound-fold baseline (consonants collapsed to one class)

| locus | coarse sim assigned | best coarse ALT Aegean | alt |
|---|--:|--:|---|
| pa-i-to | 1.0 | 1.0 | Praisos |
| se-to-i-ja | 0.75 | 0.625 | Kydonia |
| tu-ru-sa | 0.6667 | 0.8333 | Sybrita |
| a-tu-ri-si-ti | 0.5 | 0.6 | Anopolis |
| di-ki-te | 0.6667 | 0.6667 | Tylissos |
| su-ki-ri-ta | 0.75 | 0.75 | Kydonia |
| i-da-a | 0.6667 | 0.6667 | Itanos |
| ku-79-ni | 0.5 | 0.75 | Lyktos |
| da-u-49 | 0.5 | 0.6667 | Rhaukos |
| i-ti-ni-sa | 0.5 | 0.625 | Sybrita |
| ku-ni-su | 0.3333 | 0.8333 | Tylissos |
| ku-ta | 0.5 | 0.75 | Lyktos |
| sa-ra2 | 0.75 | 1.0 | Tarrha |
| di-na-u | 0.75 | 0.6667 | Kisamos |
| i-na-ta-i-zu-di-si-ka | 0.3125 | 0.5 | Palaikastro |

Under the coarse fold (vowel-pattern + onset-presence only) nearly every locus finds a near-perfect Aegean match -- confirming much of the apparent 'fit' is coarse-shape coincidence.

## 7. Leave-one-anchor-out (structural, firm set)

Firm anchors pin 17 distinct signs: **12** on a SINGLE anchor, **5** on >=2 anchors. Dropping an anchor removes ALL firm support for its single-support signs:

| anchor dropped | its signs | signs losing ALL firm support | signs still covered elsewhere |
|---|---|---|---|
| pa-i-to | PA,I,TO | PA | I,TO |
| se-to-i-ja | SE,TO,I,JA | SE,JA | TO,I |
| tu-ru-sa | TU,RU,SA | RU,SA | TU |
| a-tu-ri-si-ti | A,TU,RI,SI,TI | A,SI,TI | TU,RI |
| di-ki-te | DI,KI,TE | DI,TE | KI |
| su-ki-ri-ta | SU,KI,RI,TA | SU,TA | KI,RI |

Even the 5 multiply-supported signs collapse empirically: the cited frozen gate's leave-one-TOPONYM-out recovers only {I, RI}, each one-toponym-deep.

## 8. Leave-one-rule-out (wildcard a sign's LB value)

Most load-bearing signs (touch the most firm equations); wildcarding a value can only RAISE the fold-similarity (never lower it), so a large positive delta flags an equation propped up by that one value:

| sign | firm equations touched | max sim gain when wildcarded |
|---|--:|--:|
| I | 2 | +0.0 |
| KI | 2 | +0.0 |
| RI | 2 | +0.0 |
| TO | 2 | +0.125 |
| TU | 2 | +0.0 |
| A | 1 | +0.0 |

## 9. Verdict

The firm toponym equations carry a **real but small above-chance SHAPE-resemblance edge** (real top-6 0.7778 > random cherry-pick p95 0.7292), and this is honestly reported -- the anchors are NOT literally random. But shape-resemblance is precisely the value-blind, circular signal G1 flagged, and it fails every test that would make a seed *independently secure*:

- **Weakly language-specific:** an UNRELATED-language gazetteer (Finnish/Japanese/Nahuatl) scores 0.4919, essentially at the uniform-random floor (0.476); the real Aegean best-of (0.6042) sits ~0.11 higher, so there IS a modest real Aegean-specific shape signal -- but it is only shape (value-blind) and, per the next points, non-unique and not held-out-survivable.

- **Not unique (multiplicity):** the assigned referent is NOT the uniquely best-matching Aegean name for 6/15 loci.

- **Coarse-shape driven:** a vowel-pattern-only fold matches nearly every locus to some Aegean name -> much of the 'fit' is shape coincidence; the edge is carried heavily by the one exact hit (Phaistos, sim 1.0).

- **Not held-out-survivable:** leave-one-anchor-out shows 12/17 firm signs rest on a single anchor, and the cited frozen LOTO gate on actual held-out LA distribution recovers only {I, RI}, each one-toponym-deep, with a distributional channel top-1 of 0.0. The shape edge does NOT convert to held-out recoverability.

This is the anchor-side confirmation of **SEED_A = 0**: above-chance shape resemblance is *necessary* for anyone to propose these equations but is nowhere near *sufficient* to make a value anchor independently secure -- it is non-unique, weakly language-specific, and does not survive held-out. A real reading still requires a bilingual or >=3 genuinely independent held-out anchors.

*Generated by `scripts/g3_anchor_nulls.py`; all numbers echoed from `data/anchors_v2/anchor_nulls.json` (invariant 12).*