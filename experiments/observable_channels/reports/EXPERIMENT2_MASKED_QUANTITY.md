# Experiment 2 — masked quantity / accounting-channel recovery

## Constitutional stage header (Art. XXII)

- **articles_consulted:** V (claim layers), VIII (effective_n), XII (circularity), XIII (remove the
  convenience), XV (FUNCTIONAL licence), XVI (fail states).
- **articles_triggered:** XIII (the document-series + layout shortcuts must be removed), XII (target is
  the MASKED numeral — not read off itself).
- **claim_layer attempted:** L3 (functional / "quantity-bearing"). **highest_authorized_layer:** L2.
- **required gates:** beat the strongest frequency/series/layout baseline AND the label-shuffle null, under
  unseen lexical-family (A12), in ≥1 KN↔non-KN direction, with the masked numeral excluded from the predictor.
- **authorized outputs:** anonymous structural/functional *observations* on Linear B only.
  **forbidden outputs:** any Linear A semantic/lexical/phonetic claim; any licence grant.
- **compliance:** COMPLIANT — A12 enforced; numeral never enters the presence predictor; verdict fail-closed.

## Result (`results/masked_quantity.json`)

**Target (a) — quantity PRESENCE** (does the entry carry a counted quantity? balanced, majority 0.68):

| | value |
|---|---|
| unseen-family (A12) test units | **1,593** |
| baseline: majority | 0.680 |
| baseline: document-series shortcut | 0.688 |
| **M_struct (layout: position, #words, length)** | **0.709** |
| **M_sign (opaque word context)** | **0.651** |
| null (label shuffle) | 0.611 |
| cross-site KN→non-KN: M_sign vs baseline | 0.579 vs 0.557 |

**Target (b) — MAGNITUDE bucket S/M/L** (numeral value is the MASKED target, predicted from word context):

| | value |
|---|---|
| test units | 510 |
| baseline: majority / series | 0.663 / 0.702 |
| M_struct (layout) | 0.663 |
| M_sign (word context) | 0.637 |
| null (label shuffle) | 0.665 |
| cross-site KN→non-KN: M_sign vs baseline | 0.69 vs 0.753 |

## Reading (honest)

- **Well-powered** (1,593 A12 units, balanced) — not an underpower result.
- **The word-context channel is NEGATIVE.** Opaque word forms (M_sign) **fail to beat the majority
  baseline** on presence (0.651 < 0.680) and are **below the label-shuffle null** on magnitude (0.637 <
  0.665); cross-site they add ≤0.02 or transfer negatively. Under A12, word forms carry no transferable
  quantity signal — they overfit training sign–quantity associations that don't generalize (the same
  negative-transfer signature as Experiment 1).
- **The only above-baseline gain is LAYOUT, and it is L2, not L3.** M_struct beats baseline on presence
  (0.709 vs 0.688) using position + word-count + length — i.e. *document structure* (headers/totals sit at
  predictable positions; line items carry counts). That is the L2 channel the corpus already exposes, and it
  is exactly the *convenience* Art. XIII requires us to strip — not a transferable functional (L3) signal
  carried by the word forms.

## Verdict — `TRIVIAL_RECOVERY` for the functional word-context question (per-channel NEGATIVE)

Under Art. XVI: this channel does **not** clear the FUNCTIONAL gate. The recoverable part of the quantity
channel is document-structure (L2), already known; the load-bearing L3 question — *do opaque word forms
predict the accounting channel?* — is **negative** under A12 + shortcut removal.

**Two channels down (commodity, quantity), both negative for word-context.** The consistent pattern: the
observable administrative signal lives in **document structure (series / layout / position — L2)**, not in
transferable opaque word forms. `FUNCTIONAL_TRANSFER_LICENSE` stays `NOT_YET_EARNED`. Experiments 3–4
(accounting-closure, template completion) test the L2 structure channel directly — they may recover
structure, but structure recovery re-confirms L2 and does **not** earn the L3 functional licence. `effective_n`
is real here (grouped by held-out lexical + morphological family), so this is a signal result, not underpower.
