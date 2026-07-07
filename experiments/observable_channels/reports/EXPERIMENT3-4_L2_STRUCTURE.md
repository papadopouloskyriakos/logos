# Experiments 3–4 — characterizing the L2 document-structure channel

## Constitutional stage header (Art. XXII)

- **articles_consulted:** V (layers), VIII (effective_n), XII (circularity), XVI (fail states).
- **articles_triggered:** XII (Exp 3 masks a *summand*, never the total it reconstructs from — no circular
  self-grade); XIII (Exp 4 held out by whole document, no memorized layout).
- **claim_layer:** L2 (document structure) — numeral arithmetic (Exp 3) and notation-type templates (Exp 4);
  NO word-form identity, NO logogram reading. **highest_authorized_layer:** L2.
- **authorized outputs:** anonymous structural observations on Linear B. **forbidden:** any L3+ functional/
  semantic/lexical/phonetic claim; any licence grant beyond what the gate certifies.
- **compliance:** COMPLIANT — held-out by document; nulls present; masked target excluded from predictor.

## Experiment 3 — accounting-closure (`results/accounting_closure.json`)

Does a document's arithmetic close (largest entry = sum of the rest, the "list + total" pattern)?

| | value |
|---|---|
| docs with ≥3 numeric entries | 350 |
| **closure rate (exact)** vs **null** | **0.071 vs 0.049** |
| closure rate (±1 damage tol) vs null | 0.214 vs 0.143 |
| cross-site closure (exact): KN / non-KN | 0.111 / 0.052 |
| **masked-summand reconstruction** (n=25 closing) | **1.000** vs median baseline **0.200** |

- Closure is a **real but sparse** document structure — above the value-permutation null at both tolerances,
  concentrated at KN (formal totals). 7% exact is a **lower bound** (the detector catches only the simplest
  "largest = Σrest" form, not subset/per-commodity/deficit totals).
- **Where closure holds it is arithmetically exact**: a masked line item reconstructs at 100% vs a 20%
  median baseline. The accounting channel, when present, is perfectly recoverable — but it is present in a
  minority of documents.

## Experiment 4 — document-template completion (`results/template_completion.json`)

Mask an entry's notation type (word / logogram / numeral signature); predict it from the rest of the
document, held out by **unseen document**.

| | held-out unseen docs | KN | non-KN |
|---|---|---|---|
| n masked | 1,324 | 733 | 591 |
| baseline: global majority | 0.338 | 0.430 | 0.225 |
| baseline: position | 0.398 | 0.443 | 0.342 |
| **M_template (rest-of-doc majority)** | **0.508** | 0.407 | **0.633** |

- **Documents are internally templated**: the rest of a document predicts a masked entry's notation type at
  **0.508 vs 0.398** (position) / 0.338 (global) on **unseen documents** — a genuine, held-out L2 signal.
- **Site-dependent**: strong at non-KN (0.633 vs 0.34, +0.29) where documents are heterogeneous; **absent at
  KN** (0.407 < 0.44 baseline) where one type dominates and the base rate is already high. So the template
  effect is real but **single-direction** cross-site, not invariant.

## What L2 IS recoverable (the honest positive)

The observable administrative signal that exists is **document structure**: (i) internal notation-type
templates (predictable above baseline on unseen documents), and (ii) sparse-but-exact accounting closure
(perfect line-item reconstruction where the arithmetic closes). Both are **L2** — the layer the paper already
identifies as the one place Linear A shows structure (segmentation). Neither uses opaque word-form identity,
so **neither advances the L3 functional question** — they characterize the trivial-but-real structural channel.
