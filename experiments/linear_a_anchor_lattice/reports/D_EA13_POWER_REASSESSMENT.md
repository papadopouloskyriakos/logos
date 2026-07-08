# WP-D — EA-13 (Egyptian toponym channel) Power Reassessment

**Branch** `research/linear-a-anchor-lattice` · **v2.2** · **Seed** 20260708 · **Date** 2026-07-08
**Articles:** VIII (effective_n/power), IX (info budget), XI (dependency), XII (non-circularity), XV (licence).
**Truth-layer:** design/power analysis only (≤0.75). NOT a reading.

## What EA-13 said (re-read of `logos-external-anchors/.../FROZEN_POWER_PASS.md` + `frozen_power_envelope.json`)

EA-13 is the *frozen-regime* power envelope for the Egyptian toponym channel: a FIXED a-priori
correspondence (Kilani group-writing→sound model, so **no mapping search** — the multiple-testing trap is
removed, not relocated). Measured over realistic Egyptian consonant-skeleton lengths at the real anchor
scarcity (n = 3–4 securely-identified Cretan toponyms):

| skeleton La | Lc | FP_frozen | REC (optimistic) | powered? |
|---|---|---|---|---|
| 3 | 3 | 0.24–0.26 | 0.87–0.97 | **NO** (FP ≫ 0.10) |
| 3 | 4 | 0.41–0.42 | 0.90–0.98 | **NO** |
| **4** | **4** | **0.043** | 0.71–0.91 | **yes** |
| **4** | **5** | **0.07–0.08** | 0.74–0.92 | **yes** |

`best_config`: n_anchors 4, La 4, Lc 4, FP 0.043, REC 0.91, gap 0.868. **Verdict: `POWERED_DESIGN` —
but conditional on skeleton length La ≥ 4**, and REC is an *optimistic ceiling* (assumes Kilani gives the
exact map AND each anchor has a real LA image). EA-13's honest close: *design-viable, real-attempt-trivial*
(the one confirmatory run, `research/egyptian-calibration-gate`, returned `TRIVIAL_RECOVERY`: the
correspondence rested on a single training record š~s / HV-0234; leave-one-out flips 3→1). Unlock named by
EA-13: **more securely-identified Cretan toponyms with ≥4 distinctive skeleton slots AND an independently
calibrated correspondence not resting on one record.**

## The reassessment question
> Does EA-13's La ≥ 4 power become **reachable** with any newly-found multi-slot anchor (WP-D)?

The frozen La ≥ 4 regime is powered *only if you can populate it with ≥ 3 anchors that are each*
**(a)** LA-attested at ≥ 4 distinctive slots **AND (b)** rendered in the independent Egyptian record.
WP-D measured that intersection directly (`ea13_reassessment` in `new_anchors.json`).

## Measured answer — NO

```
externally rendered (Kom el-Hetan) Cretan toponyms : Amnisos, Phaistos, Kydonia, Knossos, Lyktos
LA-attested toponyms at >=4 slots                  : Setoija, Sybrita, Tylissos, Dikte
overlap (externally rendered AND LA-attested, any) : { Phaistos }          <- 1, and it is 3 slots / 1 site
EA-13-eligible (LA>=4 slots AND externally rendered): { }                  <- 0
required for the La>=4 regime                       : >= 3
La>=4 regime reachable                              : False
```

**The two sets are effectively disjoint.** Every Egyptian-rendered Cretan toponym except Phaistos is absent
from Linear A (attested in Linear B only); the Egyptian rendering of Phaistos is La ≈ 4 but its *LA* form
PA-I-TO is only 3 slots at 1 site — below the powered bar on both axes. Conversely, every LA toponym that
reaches ≥ 4 slots (Setoija, Sybrita, Tylissos, Dikte) is **absent from the Egyptian record**, so it supplies
no Egyptian skeleton to match against at all.

### Why WP-D cannot move this
EA-13's stated unlock was "more ≥4-slot anchors." WP-D shows the binding constraint is **not** skeleton length
in the abstract — it is the **empty overlap** between the two attestation sets. Adding LA-side ≥4-slot
toponyms (which the corpus has) does nothing, because none of them is in the Egyptian source; adding
Egyptian-side names (which the record has) does nothing, because none of the extra ones (Amnisos, Kydonia,
Knossos, Lyktos) is in Linear A. New corpus of the *same kind* cannot fix this: it would take a newly
excavated Linear A tablet bearing one of the Egyptian-list city names at ≥4 slots — i.e. new inscriptions,
not a new reading of the present corpus (Inv. 3, held-out standard).

## Verdict (mechanical)
- **EA-13 La ≥ 4 regime: `UNREACHABLE_WITH_PRESENT_ANCHORS`** (n_eligible = 0 vs required 3).
- EA-13's own status is **unchanged**: *design-conditionally-powered (La ≥ 4), real-attempt `TRIVIAL_RECOVERY`,
  scarcity-limited*. WP-D converts "scarcity-limited" from a vague caveat into a measured fact: the scarcity
  is a **zero-cardinality intersection**, not merely a small anchor count.
- **No transfer licence earned** (SEMANTIC+ remains NOT_AUTHORIZED; SEED_A = 0). The Egyptian channel stays a
  ≤0.75 truth-layer design result.

## Concrete unlock (unchanged, now sharpened)
The channel becomes reachable **iff** ≥ 3 Cretan toponyms are simultaneously (i) in the Egyptian record at
≥ 4 distinctive slots and (ii) newly attested in Linear A at ≥ 4 slots — plus a correspondence calibrated on
> 1 record. WP-K (active acquisition) should therefore rank *newly-excavated LA inscriptions bearing
Egyptian-list city-names* (Amnisos, Knossos, Kydonia, Lyktos) as the highest-value acquisition for this
channel; re-reading the present corpus cannot deliver it.

**Compliance line:** EA-13 re-read COMPLETE · La≥4 regime UNREACHABLE_WITH_PRESENT_ANCHORS (0/3) · EA-13
status unchanged (design-viable, real-attempt-trivial) · no licence · SEED_A=0 · truth-layer ≤0.75 · numbers
from `scripts/d_source_expansion.py`.
