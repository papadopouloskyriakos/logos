# NOVELTY BOUNDARY (§II)

## Claim under test

> A corpus-wide, blinded, cross-script, uncertainty-aware administrative-**role** and document-**schema**
> benchmark in which Linear B readings/glosses are **hidden** from the model, performance is tested on
> held-out sites/scribes/document-families/unseen word-forms, and a frozen architecture becomes eligible
> for one-shot Linear A transfer only after preregistered nulls and ablations.

## Verdict: `NOVELTY_SUPPORTED` (combinatorial — defensible but attackable)

No audited work (20 total) satisfies the defining *conjunction*. The point of novelty is **not** "recover
admin content without decipherment" (old — Schoep, Tomas, and 2026 popular coverage) and **not** "neural
decipherment" (Luo 2019, which is phonetic and needs a cognate language — methodologically the inverse).
It is the **blinding-as-ablation on a *decipherable* script**: deliberately withholding the *known* Linear B
readings/glosses to force, and then validate against ground truth, a structure-only method — combined with a
preregistered cross-script transfer gate.

## Nearest neighbours (why each falls short of OVERLAP)

1. **Born, Monroe, Kelley & Sarkar 2025 — Disambiguating Numeral Sequences (Proto-Elamite)** *(the strongest
   threat).* The only work that is genuinely structure-only on an undeciphered administrative corpus,
   uncertainty-aware, and ships a held-out test. Short of OVERLAP: task is numeral-**value** disambiguation,
   not role/document-schema; **no cross-script transfer**; **no blinding-as-ablation** (Proto-Elamite is
   simply undeciphered — no known glosses are withheld) and no held-out-by-site/scribe/family + preregistered
   transfer gate.
2. **Born, Kelley et al. 2019 — Sign Clustering/Topic Extraction (Proto-Elamite).** Closest to schema
   induction (distributional sign "topics") but exploratory, no held-out generalization, no uncertainty gate,
   no transfer, no blinding.
3. **Helena Tomas — LA vs LB administrative systems.** Nearest on the cross-script *schema* axis, but
   qualitative human epigraphy conducted *with* full Linear B knowledge — the opposite of blinding.
4. **Corazza et al. 2021 — LA fraction values (INSCRIBE/Tamburini).** Nearest on *method* (computational,
   large hypothesis space, statistical pruning, LA↔LB metrology) — but numeric not role/schema, un-blinded,
   no sealed transfer gate. This is the lineage logos already builds on, not the same benchmark.
5. **Luo, Cao & Barzilay 2019 — Neural Decipherment.** The reflexive reviewer citation; fundamentally
   phonetic and cognate-dependent — the inverse of the blinded structure-only premise.

## Distinguishing features (the defensible conjunction)

- **Blinding-as-ablation on a decipherable script** (load-bearing; 0/20 precedent).
- Target = administrative **role + document-family schema** induction (not numerals, sign-clusters,
  scribal-hand identity, restoration, or phonetic cognates).
- A **preregistered cross-script transfer gate**: frozen architecture eligible for one-shot LA transfer only
  after nulls/ablations pass.
- **Held-out by site / scribe / document-family / unseen word-form** as the eligibility criterion (held-out
  eval exists in the field — Born 2025, scribal-hands, Papavassileiou — but for disambiguation/paleography/
  restoration, never as a blinded role/schema generalization test feeding a transfer gate).
- A reusable corpus-wide **benchmark** with fail-closed gate + multiple-testing deflation — not a single-pair
  case study (Davis & Valério) or a survey (Braović, Sommerschield).

## Residual prior-art risk (state honestly; do not overclaim)

- **The primitives are individually precedented** — a rigorous reviewer will frame the contribution as
  *combinatorial*, not a new primitive. Heterogeneous-graph doc models, factor graphs, CRF role labelling,
  held-out eval, statistical pruning all exist outside Aegean scripts.
- **Born et al. 2025 is the strongest threat** — a reviewer may cast the claim as "Born-2025 applied to Aegean
  scripts with a blinding wrapper and a transfer gate." Rebuttal must lean on (a) blinding-as-ablation and
  (b) the cross-script transfer gate — neither of which Born has.
- Novelty rests partly on **absence-in-survey** evidence (Braović 2024, Sommerschield 2023) — corroborating,
  not decisive; active 2025–26 Born/Sarkar and INSCRIBE/Ferrara lineages could surface a closer match.
- The claim **spans several axes**; if any single axis is judged the "real" contribution in isolation it is
  weaker. The defense depends on presenting the *integrated, unoccupied conjunction*.

**Bottom line:** proceed as `NOVELTY_SUPPORTED`, but the programme's scientific value does **not** depend on
novelty — a rigorous *blinded LB benchmark result* (positive or null) is worthwhile regardless. Novelty is a
publication concern, not a gate on the science. Preserve all receipts; re-audit before any external claim.
