# AMENDMENT-002 — Constitution v2.0 → v2.1 (precision fixes B1–B8)

Recorded under **Article XXIII**. Non-silent, **non-retroactive** (no prior verdict changes). Approved by
the repository owner ("proceed with all pending items", 2026-07-07). Enacts the eight precision defects the
adoption self-audit ([`CONSTITUTION_SELF_AUDIT.md`](./CONSTITUTION_SELF_AUDIT.md) §B) identified in the v2.0
*text* — all operational-precision fixes, none altering the anti-self-deception intent.

| field | value |
|---|---|
| **date** | 2026-07-07 |
| **approver** | Repository owner |
| **old text** | `governance/CONSTITUTION.md` @ v2.0 (git history before this commit; file was `CONSTITUTION-v2.0.md`) |
| **new text** | `governance/CONSTITUTION.md` @ v2.1 |
| **retroactivity** | NON-RETROACTIVE — clarifies definitions/vocabulary going forward; no completed result is re-graded |
| **file rename** | `CONSTITUTION-v2.0.md` → `CONSTITUTION.md` (version-neutral; version tracked in the header + amendment records) |

## Changes

| id | article | old → new |
|---|---|---|
| **B1** | XVI / status vocabulary | Added `DEPENDENCY_COLLAPSE`, `LEAKAGE_DETECTED`, `DOMAIN_SHIFT_FAILURE` to the closed "Required status vocabulary" (they were allowed failure states in XVI but absent from the vocabulary). |
| **B2** | VI / status vocabulary | Declared the **confidence axis** (VI) and **lifecycle status axis** distinct; a claim carries one token from each, disambiguated by axis where a token (`SUPPORTED`, `EXPLORATORY`) appears on both (`confidence:` vs `status:`). |
| **B3** | XIII, XV | "Required … **may** include" → every stress test / control **applicable to the claim's layer is MANDATORY**; any omission recorded as an explicit Article XXII deviation. Closes the mandatory-header/permissive-verb gap. |
| **B4** | VIII, XI | Defined **genuine independence** operationally: distinct edition AND distinct decipherment lineage AND no shared upstream lexicon; DEPENDENT until proven; enforced by `scripts/source_dependency.py`. |
| **B5** | VI | Attached each confidence class to a **mechanical predicate** over (Art. IV evidence tier × Art. VIII `effective_n` × Art. VII deflated significance) — graduation is computed, not asserted. |
| **B6** | V/VI/XV | **Licence caps confidence**: a claim's confidence class is capped by the transfer licence earned for its claim layer; no class above `SUPPORTED` without the layer's licence. |
| **B7** | IX | Scoped the information-budget panel to **inferential/graduating** claims (L2+ or seeking confidence ≥ `SUPPORTED`); bare L0/L1 observations (no MDE/power) exempt. |
| **B8** | VI | Reframed the `0.75` ceiling as an **explicitly conventional governance constant** (empirically anchored to `gate_null_calibration.py`), not a probability — cures the residual "arbitrary" half of v1.0 finding #4. |

## Scientific consequence

Definitional/vocabulary precision only. No experiment is re-graded; the three completed negatives and the
frozen paper are unaffected. B4/B5/B6 now have machine-readable backing (`source_dependency.py`;
`effective_n`/deflation to be wired per the Article VIII/IX backlog items). The v2.0 text remains in git
history as the immutable prior record (Article XVII).
