# P2_CERTIFICATION — conjunctive certification of the design that fires (§2)

**Result: CERTIFIED at k = 8 (first and only k tried)** — artifact
`results/p2_certification.json`, 11.7 s wall-clock, cert master seed 20260713,
n_rep = 100 / n_perm = 200 per strength.

- **Bar: the cross-attempt-corrected operative rule** — Šidák over N_attempts = 2 (this is the
  second pre-registered attempt at the backward-projection hypothesis): detection iff add-one
  p_raw < 1 − 0.95^½ ≈ 0.02532, applied to the full statistic AND every leave-one-anchor-out
  variant. [Operator may veto per the prompt at the §4 handoff — a veto RELAXES the bar to
  unadjusted p < 0.05 with an explicit two-attempt history disclosure; certification at the
  corrected bar strictly dominates, so a veto cannot invalidate this certification.]
- **Geometry: the real selected set** (SELECTED_ANCHORS.md, 8 toponym words, 17 covered
  eligible signs, legs ≤ 2) with the experiment's own stratified draw (covered-by-selected-set
  × attestation tertiles; populations C: 1/8/8, U: 16/8/8; largest-remainder allocation
  1/3/3/7/3/3 of h = 20) — collisions priced in automatically.
- **LOTO-survival curve** (P[full clears AND all 8 leave-one-anchor-out variants clear], at the
  corrected bar): 0.45 / 0.48 / 0.66 / 0.65 / **0.82** / 1.00 / 1.00 / 1.00 at
  s = 0 / 0.5 / 1 / 2 / 3 / 5 / 8 / 13 (raw-bar power 0.78–0.95 over s ≤ 3; mean pinned
  held-out signs ≈ 3.0) — **passes the frozen band (≥ 0.80 at some s ≤ 3)**.
- **Machinery (pins off, corrected bar):** s=0 false-fire 0.01 (≤ 0.14) ✓; s=13 power 1.00
  (≥ 0.90) ✓.
- **k-escalation trail:** k=8 passed on the first attempt; no escalation needed (logged: {8}).
