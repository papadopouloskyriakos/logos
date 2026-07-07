# AMENDMENT-003 — Constitution v2.1 → v2.2 (corrects B5 + B6)

Recorded under **Article XXIII**. Non-silent, **non-retroactive**. Approved by the repository owner
("proceed with all pending items", 2026-07-07). Corrects two defects that an adversarial review (workflow
`wf_c5c47c7f-d52`) found in the AMENDMENT-002 edits themselves — the honest-clock principle: the fixes were
themselves imperfect, so they are re-corrected on the record before any code relies on them.

| field | value |
|---|---|
| **date** | 2026-07-07 |
| **approver** | Repository owner |
| **old text** | `governance/CONSTITUTION.md` @ v2.1 (git history before this commit) |
| **new text** | `governance/CONSTITUTION.md` @ v2.2 |
| **retroactivity** | NON-RETROACTIVE — corrects definitions; no completed result is re-graded |

## Changes

| id | article | defect (found by adversarial review) | correction |
|---|---|---|---|
| **B5′** | VI | The mechanical class predicates used `Art. IV tier >= N`, but Article IV numbers evidence **strongest-first** (1 = newly-discovered … 6 = resampled internal). With 1=best, `tier >= 3` selected tiers 3–6 **including tier 6 (in-sample resampling)**, contradicting "held-out"; and the higher class HELD_OUT_SUPPORTED (`tier >= 4`) accepted evidence Article IV ranks weaker than SUPPORTED's tier 3 — an inverted, non-monotonic ladder. | Restated the predicates **qualitatively** (monotonic with Article IV, 1=best); **tier 6 (resampled internal) never satisfies a held-out predicate**; HELD_OUT_SUPPORTED now requires a hold-out that crosses a **structural boundary** (site/scribe/series/chronology or unseen family), not a within-population inscription split. |
| **B6′** | VI/XV | The licence-caps-confidence rule presupposed a total layer→licence map, but Article V has **10 layers** and Article XV **7 licences**; L0, L1, L7 had no licence, so B6 taken literally **froze L0/L1/L7 claims at SUPPORTED forever** and contradicted B5 (which can compute higher classes for any layer beating a held-out null). | Published an **explicit total L0–L9 → licence map**: L0/L1 → none (**exempt** from the cap — observation/identification are not transfer claims); L7 → LANGUAGE_IDENTIFICATION; L2–L6, L8, L9 as before. This matches `scripts/licence_gate.py`'s `LAYER_LICENCE`. |

## Scientific consequence

Definitional precision only; no experiment re-graded. Both corrections make the graduation ladder (B5) and
the licence cap (B6) internally consistent and code-implementable. The v2.1 text remains in git history as the
immutable prior record (Article XVII). The companion code batch (`scripts/effective_n.py`,
`info_budget.py`, `search_receipt.py`, `assumption_gate.py`, `licence_gate.py`, `source_dependency.py`) was
hardened in the same review to fail closed on unrecognized input and to compute the *conservative* joint
independence count — see the review findings applied alongside this amendment.
