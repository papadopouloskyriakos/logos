# SELECTION_RULE — Phase 2 anchor selection (COMMITTED BEFORE ANY SET IS DRAWN)

**Frozen 2026-07-03.** Selection is content-blind and provenance-only: it reads the census's
provenance columns exclusively. **No anchor is ever selected, ranked, or excluded by any
computed effect on any recovery statistic.** Implemented by `p2_select_certify.py --select`;
the output set is a deterministic function of this rule and `anchor_census.csv` alone.

## Pool

Strict-tier census rows (the gap-analysis v3 strict tier, recomputed by identical filters):
classes 1–3 (toponym / personal_name / gloss_acrophonic); fringe_flag = false; sm_trust ≠
debunked; source_status ∈ {primary, secondary}; ≥ 2-sign LA form; rows whose notes carry the
source's own query ('queried') or hedge markers ('hedge', "'?'", '=?', 'perhaps',
'do not assert') excluded. Class-4 variation rows remain constraints, never pins, never
selectable. Expected pool = 31 rows. The se-to-i-ja location debate (Archanes vs eastern
Crete) is a prose caveat carried into the prereg; its word-correspondence mechanics are
undisputed and it stays selectable.

## Ordering (provenance-only rank key, ascending)

1. **class_rank:** toponym (1) < personal_name (2) < gloss_acrophonic (3);
2. **trust_rank:** S&M 'tempting' (0) < 'neutral' (1) < 'n/a' (2);
3. **status_rank:** primary (0) < secondary (1);
4. **seeded deterministic tie-break:** ascending SHA-256 hex of the string
   `"p2sel-2026-07-03|" + anchor_id` (salt stated here; content-blind, avoids alphabetic bias).

## Coverage-constrained greedy (mechanical; breadth binds, per the sweep)

Iterate candidates in rank order. ACCEPT a candidate iff it adds ≥ 1 NEW distinct
pinnable sign (a sign in the 49-eligible pool, {SI, MU} ineligible by the frozen Phase-1
principle) to the union of already-accepted anchors' signs; otherwise SKIP provisionally.
Stop at k accepted. If a full pass accepts fewer than k, fill remaining slots from the
provisionally-skipped list in rank order. The greedy is prefix-stable: acceptance decisions do
not depend on k, so k-escalation extends the set monotonically without reshuffling it.

## k-escalation clause

Initial **k = 8** (the Step-1 quota). If §2 certification fails at k, increment k by one (same
ordering, monotone extension) and re-certify; EVERY k tried is logged in P2_CERTIFICATION.md.
This escalation is synthetic-only design-space exploration — recorded, never hidden. If the
full strict-tier pool (k = 31) cannot certify: STOP; that bound is itself the result.

## Prohibition (restated, binding)

Selection and escalation read provenance columns only. The one-shot's real held-out labels are
touched exactly once, later, under the frozen configuration (d=24 / window 2 / cds 0.75 —
anchors are data; the config does not change). Nothing under `paper/` is read or written.
