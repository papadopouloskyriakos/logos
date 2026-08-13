# Two further lineara.xyz lineage defects: face-split word tokens (D5) and A319 mislabelled `*904` (D6)

**Date:** 2026-08-13 · **Status:** CONFIRMED (both) · **Verdict impact:** none — no published logos
result moves · **Action:** register entries + any silver rebuild are an **owner decision**

**Reproduce:** `python3 scripts/audit_face_splits.py` (read-only; all counts below are its output).

Found while auditing an external Linear A decipherment preprint against our own corpus. Both defects
are in **our** bronze/silver, independent of that preprint. They join the two already on record:

| | defect | source | record |
|---|---|---|---|
| D4 | AB21/AB22 (OVIS/CAP) inverted, 11 docs / 15 LOGO tokens | Tsirkas, external claim | `docs/2026-08-05-ab21-ab22-external-audit.md` |
| D1 | word-attached damage notation (`U+1076B`) stripped from `transliteratedWords`; 28.9 % of word tokens damage-touching, 30.8 % of types phantom | Tsirkas, confirmed on our silver | `docs/2026-08-05-tsirkas-full-repo-audit.md` §2 |
| R2* | 24 quote-verified divergences (readings, doubted items, Arkhanes→"Arkhalkhori" site labels, unmarked restorations) | Del Freo rapports, round-2 sweep | `corpus/divergences.json` v2 |
| **D5** | **word tokens split at face boundaries** | **this doc** | below |
| **D6** | **glyph A319 labelled `*904`; ontology classes it as a fraction** | **this doc** | below |

---

## D5 — face-split word tokens

Where a Linear A sign-group runs across two faces (or two ruled lines) of a stone vessel, the
lineage emits it as **two** word tokens in `transliteratedWords`. Younger's edition marks the
continuation with trailing/leading hyphens, and at IO Za 12 states it outright:
**"the two sides break up the word."**

| doc | Younger | our lineage | spurious types |
|---|---|---|---|
| `IOZa12` | `.a: ][• •] • JA-SA-` / `.b: -SA-RA-ME •` | `JA-SA` + `SA-RA-ME` | 2 |
| `IOZa16` | `.a: ] *123 • JA-SA-SA-RA-` / `.b: -ME • U-NA-RU-KA[-NA-SI` | `JA-SA-SA-RA` + `ME` | 2 |
| `KNZa10` | `]-TA-NU-MU-TI • JA-SA-SA-RA-MA-` / `.b: -NA • DA-WA-…` | `JA-SA-SA-RA-MA` + `NA` | 2 |
| `PKZa16` | `.a: ]-TO-SA • PU₂-` / `.b: -RE-JA[` ("the two lines probably run together") | `PU₂` + `RE-JA` | 2 |

**4/4 confirmed. 8 spurious word types introduced; 4 true types under-attested.**

Witness: `corpus/bronze/younger_lineara/misctexts.txt` (lines 478, 497, 2666, 3353). The script's
continuation scan finds 7 hyphen-continuation markers; three of the extra hits are the SY Za 3
lacuna run (`-- ca. 8 --`, `-- ca. 10 --`), not word splits.

### Why it matters more than 8 types out of 1,165 suggests

**Every confirmed case is a libation-formula document.** Three of the four split the *same* lexeme,
`JA-SA-SA-RA-ME` — the single most-studied word in Linear A and a fixture of the cross-script and
segmentation work. Concretely, in our silver:

- `JA-SA-SA-RA-ME`'s token count is depressed (IO Za 12 and IO Za 16 do not register as
  attestations of it at all);
- `JA-SA`, `SA-RA-ME`, `JA-SA-SA-RA`, `ME`, `JA-SA-SA-RA-MA`, `NA`, `PU₂`, `RE-JA` are counted as
  distinct types when four of them are fragments and none is an independent word;
- any type/token statistic over the formula subcorpus — including the hapax rate, which drives the
  D1 phantom-type analysis — is affected in the same direction.

**No published logos figure changes**: the segmentation, morphology and metrology nulls are
document-level or run on the administrative corpus, and the frozen paper's counts do not depend on
formula-word type identity. Re-check before reuse, per the D1 precedent.

---

## D6 — A319 mislabelled `*904`

The `transliteratedWords` layer prints `*904` for a sign whose glyph in `parsedInscription` is
**U+1066B LINEAR A SIGN A319**. Label and glyph co-occur in **3/3** label-bearing documents
(`HT132`, `HTZd155`, `HTZd157+156`), and A319 appears in no other document.

`corpus/silver/signs_ontology.json` inherits the wrong label:

```json
"*904": {"class": "fraction", "allograph_family": "*904", "frequency": 1,
         "examples": ["HTZd155"], "value_hypothesis": "Aegean fractional weight / measure"}
```

…and there is **no `*319` entry at all**. The classification is wrong twice over: A319 is a GORILA
`*`-series sign, and the genuine Aegean fraction signs (A704 E, A705 F, A707 J, A708 K) occur
*alongside* it in the very same document:

```
HT Zd 157+156:  WI-JA-SU-MA-TI-TI · A319 1 · A319 1 J · A319 2 E · A319 3 E F · TA-JA K
HT 132:         A-SE 𐄁 A319 5 · QA-RE-TO 𐄁 *22F 27 · PA₃ 𐄁 *305 1
```

So the *contextual* reading behind the entry — a counted unit in a quantity list — is defensible;
the **sign identity** is not. A `*`-series syllabogram/logogram has been folded into the fraction
class on the strength of a bad label, and the sign inventory silently loses A319.

Effect on our inventories: `inventory_syllabograms_*.json` and any sign-class count that partitions
on `signs_ontology["class"]` mis-assign this sign. Frequency is low (5 occurrences, 3 docs), so no
published count is expected to move — but the *class* error is the kind that propagates into
sign-inventory arguments, and the entry's `frequency: 1` does not match the 5 attested occurrences
either.

---

## Disposition

1. **No silver rebuild without an explicit decision** (standing rule, as for D1/D4).
2. **Register candidates.** Both are lineage-vs-edition divergences with named witnesses, i.e. the
   class `corpus/divergences.json` exists to hold. Adding them is an owner decision; the witnesses
   are in-repo (`corpus/bronze/younger_lineara/misctexts.txt`, and the bronze `parsedInscription`
   layer itself for D6).
3. **Reuse rule, per the D1/D4 precedent:** any analysis sensitive to *word-type identity in the
   libation-formula subcorpus* must run under both readings (split and joined); any analysis
   partitioning signs by ontology `class` should treat `*904` as A319 until the register decides.
4. **Standing lesson.** D6 in particular is a *self*-inconsistency: the lineage's own two layers
   (`transliteratedWords` vs `parsedInscription`) disagree, and the glyph layer is right. That is a
   cheap, general cross-check we have not systematically run — a label/glyph reconciliation sweep
   over the whole corpus is a natural follow-up (not run here; scope was the audit).

**Compliance (Art. XXII):** articles triggered VII (complete scan, no document cherry-picking), XI
(source dependency — both defects are inherited from a single upstream, lineara.xyz, which is also
the upstream of the external work that prompted the check), XVII (append-only — this doc adds a
record, edits nothing). No verdict re-graded; frozen paper untouched; silver byte-identity
unchanged (nothing was written to `corpus/`). All counts generated by
`scripts/audit_face_splits.py` (invariant #12).
