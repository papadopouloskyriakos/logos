# EPOCH-022 — Deviations (Art. XVII, append-only)

## D1 — pre-result fix to PC-power planted-corpus construction (not an erratum: caught before
`result.json` was ever written by the flawed version; analogous to E020's D-note)

**What happened.** The prereg (Step 4, PC-power) states the planted corpus "guarantees
`productivities` counts exactly `K_STEMS=45` distinct recurring stems for `__PLANT__|PRE` by
construction (deterministic ground truth)" via "each used in exactly 2 words prefixed by
`__PLANT__`". The first implementation literally inserted the SAME tuple `(PLANT,)+stem` twice
into the corpus word list. `e015_lib.productivities()` first does `wset = set(words)` — two
byte-identical words collapse to ONE element of the set, so the "2 occurrences" did not
mechanically guarantee `rc[stem] >= 2` (the recurrence criterion) the way the prereg's prose
assumed. The first run still showed strong power (`obs_plant` 30–37 rather than the intended 45,
`p_plant ≈ 0.0033` for every one of 25 seeds, `power_pass = True`) because enough stems happened
to coincide with i.i.d. filler-word residuals by chance — so the POWER CONCLUSION did not change,
but the prereg's determinism claim was false as implemented.

**Fix (applied before any result.json was written/finalized for this epoch — same status as
E020's pre-result bugfix, not an erratum on a published number):** each of the 45 stems now gets
ONE `__PLANT__`+stem carrier word AND the bare stem inserted as its own standalone word elsewhere
in the corpus, satisfying the `t in wset` branch of `productivities()`'s recurrence test directly
(no reliance on set-deduplication or incidental filler collisions). This exactly matches the
prereg's stated intent ("deterministic ground truth") and gives `obs_plant = 45` on every one of
the 25 seeds in the corrected run.

**No threshold, formula, null design, or verdict rule was altered.** Only the internal
construction of the synthetic planted corpus was corrected. The corrected run is what is reported
in `result.json`; the flawed first-pass numbers (`obs_plant` 30–37, still `power_pass=True`) are
recorded here for transparency but are not used anywhere downstream.
