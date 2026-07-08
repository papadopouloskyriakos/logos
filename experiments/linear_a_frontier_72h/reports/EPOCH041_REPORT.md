# EPOCH-041 — Sign positional-role specialization (templatic vs free morphology)

**Executed by GLM-5.2** via the gated runner. **Report completed by the Claude orchestrator** (GLM omitted
STEP-8 report; record completed per Art. XVII). Claim ceiling **L2/L3**; anonymous signs; no phonetics.

## Question
What fraction of the Linear A sign inventory is POSITION-SPECIALIZED (significantly enriched, Holm-corrected,
in initial / final / medial position under a within-word permutation null)? High fraction ⇒ templatic/slot
morphology; low ⇒ positionally-free signs.

## Verdict — `MACHINERY_UNINFORMATIVE` (UNDERPOWERED, fail-closed)
The positive control FAILED: on Linear B — which has *known* strong positional structure (E038 confirmed
final-concentration) — the machinery recovered **0** specialized signs, the same as its within-word-shuffled
control. Since it could not detect LB's known positional structure, no Linear A claim is authorised.

**Root cause (orchestrator-diagnosed): a draw-count / multiple-testing limit, not a logic bug.** With 2000
permutation draws the per-test p-floor is 1/2001 ≈ 5.0e-4. Holm correction across ~102 tests (51 signs × 2
positions) requires the most-significant test to reach p ≤ 0.05/102 ≈ 4.9e-4 — essentially *at* the floor —
so even genuinely strongly-specialized signs cannot clear Holm, and the specialized fraction collapses to 0
on **both** LA and LB. GLM flagged this risk in its own deviation note ("5000 draws may be needed to resolve
the Holm p-value floor"). The frozen metric/null were faithful; the draw budget was simply too small for the
correction.

## Why this is NOT the real answer (and what supersedes it)
The result `specialized_fraction = 0.0` is a draw-count artifact. It directly contradicts the *verified*
E039 finding that **≥6 signs (A, QA, KU, U, I, *411) are Holm-significant word-initial-enriched** — i.e. LA
demonstrably HAS position-specialized signs. E041's underpowered PC simply could not resolve them.

## Disposition
Banked honestly as a fail-closed `MACHINERY_UNINFORMATIVE` (the PC-first discipline correctly refused to
report an artifactual 0). **Superseded by EPOCH-042**, which re-runs the identical question with an adequate
draw budget (≥20000) so the Holm floor resolves, yielding the true specialized fraction.

## Numbers
- n signs tested = 51 (≥15 occ); n words len≥2 = 1369, len≥3 = 752.
- specialized_fraction = 0.0 (UNDERPOWERED — draw-count artifact).
- PC: LB specialized_fraction = 0.0 (should be high) → detect = False → PC FAILED.
- Cross-site not reached (PC gates it).

## Scope
No LA claim. STRUCTURAL L2/L3 machinery-calibration result only: it establishes that a Holm-corrected
per-sign positional test over the full inventory needs ≫2000 draws — a methodological constraint carried
into E042. Anonymous signs; no phonetics/meaning/language-ID.
