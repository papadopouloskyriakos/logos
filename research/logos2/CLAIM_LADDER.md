# LOGOS-2 Claim Ladder — and its mapping to the governing Constitution

The campaign brief defines levels L0–L6. The repository's **Constitution v2.3
(`governance/CONSTITUTION.md`, Articles I–XXIII) remains authoritative**; its claim layers are
L0–L9 and its transfer-licence system (Art. XV) governs what may be asserted. This file fixes the
mapping so no wording ever exceeds the earned constitutional layer. Where the two scales differ,
the STRICTER constraint applies.

| LOGOS-2 level | meaning (campaign brief) | Constitution layer(s) | licence implicated |
|---|---|---|---|
| L0 TOOLING | software/corpus infrastructure | (none — no claim) | none |
| L1 MEASUREMENT | sign identity, allographs, transcription, provenance, hand, site, period, medium, damage | L0–L1 (physical, sign-id) | none |
| L2 STRUCTURE | positional/distributional/formulaic/phonotactic/morphological/administrative regularity | L2 (structure), L3 (functional role) | STRUCTURAL |
| L3 SEMANTIC CLASS | quantity, commodity, place, person, office, transaction type, ritual formula | L3–L4 (functional → semantic class) | FUNCTIONAL / SEMANTIC |
| L4 PHONETIC VALUE | sign or sequence values | L6 (phonetic) | PHONETIC |
| L5 LANGUAGE RELATION | family or contact-language evidence | L8 (language-id) | LANGUAGE_ID |
| L6 TRANSLATION | connected lexical/propositional interpretation | L5, L7, L9 (lexical, grammar, translation) | LEXICAL / TRANSLATION |

**Current licence state (inherited): ALL Linear A transfer licences NOT_EARNED; SEMANTIC and above
NOT_AUTHORIZED** (`governance/transfer_licences.json`). Therefore any LOGOS-2 result at L3–L6
requires earning the corresponding licence per Art. XV in addition to the campaign's own
graduation rules below — the campaign brief's rules are necessary, not sufficient.

## Graduation rules for L4–L6 (campaign brief §1, restated as the operative checklist)

1. Two evidential channels that do **not share the decisive observations** (independence audited
   in E212 against the evidence graph, per the E102 lesson: many lenses on one channel ≠ many
   channels).
2. A pre-registered prediction on held-out or prospectively sealed material.
3. Survival of matched canaries **and** family-wise multiplicity control (maxT where a valid
   joint null exists — categorical realization, per the E103R correction — else pre-declared
   Holm / closed testing / hierarchical FDR).
4. Effect-size and uncertainty statement (never a bare p-value).
5. No materially equivalent result in unrelated or synthetic control languages.
6. No unresolved transcription or leakage defect capable of generating the effect.

## Standing wording constraints (inherited, binding)

- The established A-initial result is: **"A is strongly enriched in initial position across
  overlapping segmentation variants."** It is NOT to be called prefixation, productivity, a
  prefix slot, or morphology unless E207 directly demonstrates recurrent stems, paradigmatic
  alternation, and held-out prediction (then at most LOGOS-2 L2 / Constitution L2-L3).
- A p-value is never proof of decipherment (invariant #8; multiplicity is THE enemy).
- Exploratory vs confirmatory status is a mechanical field in every experiment's
  `decision_rule.json`, never prose.
- A calibrated null is reported as what it rules out and what evidence would change it — never
  as "failure" and never as "Linear A is uncrackable" (mission constraint).
