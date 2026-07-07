# 02 — Claim graph & free-parameter (lower-bound search) receipt

## A. Dependency graph (premise → conclusion, with independence class + circularity risk)

| # | premise | conclusion | source | independence | selected-to-fit? | held-out? | circularity risk |
|---|---|---|---|---|---|---|---|
| e1 | AB08/59/28/54/57 = /a,ta,i,wa,ya/ | A,TA,I,WA,JA values | GORILA/Ventris (LB transfer) | shared-source (conventional) | no | n/a | **not discovery** — `literature_match`, scores 0 |
| e2 | `*301` needs a value; no LB anchor (AB "—") | `*301` is a free parameter | Fig.1 (own table) | none | **yes** | no | HIGH — unanchored |
| e3 | choose `*301=/na/` | last 3 signs read na-wa-ya | Di Mino | none | **yes (to fit e4)** | no | HIGH |
| e4 | na-wa-ya, strip vowels | root n-w-y | Di Mino | derived from e3 | **yes** | no | **CIRCULAR with e3** |
| e5 | n-w-y ≈ Semitic √N-W-Y | root exists in Hebrew/Akkadian/… | Semitic lexica | real (external) | root **searched** | no | multiplicity (family-wide root search) |
| e6 | √N-W-Y glossed "dwell" | gloss "dwell" | Semitic lexica | real | **gloss selected** among senses | no | semantic-specificity |
| e7 | word = invocation verb | formula position/function | Di Mino | none | yes | **testable** (cross-site) | — |
| e8 | A=1cs, TA=tG stem, I=stem-vowel | Semitic verbal morphology | Di Mino (Fig.1) | none | yes | **testable** (held-out morphology) | narrative-capture |
| e9 | e4+e5+e6+e8 | "Linear A is Semitic" | Di Mino | none | yes | no | **language-ID from one word** (forbidden) |
| e10 | apply system to 40 signs / 408 words | full decipherment | Di Mino (withheld) | none | unknown | unknown | `SOURCE_BLOCKED` |

**The load-bearing circularity (e2→e3→e4):** `*301`'s value is chosen so that na-wa-ya yields n-w-y, and n-w-y is
then offered as evidence for the value. H1 (`*301=/na/`) cannot be validated by H2 (the root) because H2 is a
deterministic consequence of H1. The mechanical break: does `/na/` **specifically** (vs the admissible value
space) produce recurring Semitic morphology on **held-out** inscriptions above the deflated bar?

## B. Free-parameter receipt (lower bound)

We cannot observe the author's exact search log, so we build a `LOWER_BOUND_SEARCH_RECEIPT` from public facts and
report the unobserved multiplicity separately (never pretending the lower bound is the full count).

| axis | lower-bound count | basis |
|---|---|---|
| candidate values for `*301` | ≥ ~55 | admissible CV syllabograms in the LA/LB syllabary (any could be C₁) |
| candidate segmentations | ≥ 4 | Di Mino / Davis / Thomas / diplomatic |
| candidate Semitic roots | ≥ 10³ per language | triconsonantal root inventory searched for a match |
| candidate languages/families | ≥ 6 | Hebrew, Akkadian, Arabic, Ugaritic, Aramaic, Phoenician |
| candidate glosses per root | ≥ 3 | polysemy (dwell/inhabit/remain/rest/settle…) |
| **author's STATED simulation count** | **≈ 100,000** | Di Mino: "~100k simulations scoring Semitic signal vs luck" (CLB-01) |

**`N_eff` (this audit) will be the LOGGED count** of `(sign-value × lexeme × segmentation)` trials the value sweep
+ root search actually scores (comparison-layer §B.2), reported exactly. **Separately**, the author's own stated
~10⁵ simulations is itself a published multiplicity: under the deflated bar `E[max_Neff]` (§B.3), a single-word
match selected as the best of ~10⁵ trials must clear an extreme-value threshold, not a single-trial p. This is the
central quantitative point — the ~100k number is not reassurance, it is the size of the search that must be
deflated against.

## C. Consequence for the gate
- 5/6 signs score 0 (conventional transfer, `literature_match`).
- The one novel parameter (`*301=/na/`) plus the root/gloss/family conclusions must clear
  `E[max_Neff]` for the logged `N_eff` **and** the author's stated ~10⁵, on **held-out** `S_morph`.
- `k` (free params asserted: the `*301` value + the correspondence rules) is checked against `U_floor` (MDL cap).
