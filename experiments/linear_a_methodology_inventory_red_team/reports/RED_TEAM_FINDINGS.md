# Red-team findings — independent verification of the LOGOS Linear A methodology inventory

**Branch** `audit/linear-a-methodology-inventory-red-team` (from `e800b63`, read-only; P1 report preserved unchanged).
**Method:** independent content-hash enumeration (986 distinct-content artifacts across 12 worktrees) → 8-agent
per-lineage independent re-derivation + row-by-row verification + numerical trace + verdict-semantics audit.

## Bottom line
**Prompt 1's inventory is substantially accurate and honest.** Of 215 rows independently checked:
**203 VERIFIED, 12 VERIFIED_WITH_MINOR_CORRECTION, 0 MATERIAL_ERROR, 0 UNSUPPORTED, 0 MISSING_ARTIFACT, 0
DUPLICATE_INSTANCE, 0 WRONG_LINEAGE.** Every one of ~60 load-bearing numbers independently checked was
`REPRODUCED` or `ARTIFACT_VERIFIED` (0 MISMATCH, 0 MISSING). The corrections are one omitted method, a handful of
stale supersession-links/headline nits, and count-framing clarifications — none overturns any conclusion.

## Answers to the 13 required questions

**1. Did Prompt 1 cover every methodology in repository history?** Almost — **214 of 215** (99.5%). One material
omission (Q2). Coverage of the paper, constraint-expansion, foundry, relative-phonology, di-mino, admin/structure,
and egyptian lineages is complete; the gap was isolated to the external-anchor lineage where P1 read a stale
inherited copy.

**2. Which methods were omitted?** **One material: `EA-13` — the FROZEN Egyptian-loanword (Hoch) power-envelope
pass** on external anchors (`frozen_power_pass.py` + `FROZEN_POWER_PASS.md` + `frozen_power_envelope.json`) at
`research/external-minoan-anchors@3310e4b`. P1's dir-ownership heuristic read the older la-lb-ritual inherited copy
(57 files) instead of the newer owning branch (80 files), so it missed this pass. It **materially qualifies P1's
`EA-02` "leans NO_POWER"**: the frozen pass shows `POWERED_DESIGN at La≥4` — the channel is
design-conditionally-powered-but-scarcity-limited, not simply no-power. Added as `EA-13` in the verified table.
(No other omitted *methods*: the remaining delta is 41 `.pyc` caches, 11 reference PDFs/transcripts, and ~18
subsumed input/result data-files of already-catalogued methods.)

**3. Which were double-counted?** **None materially.** The genuine multi-row spreads are legitimate distinct
instances, not false novelty: A- prefixation appears across E1(induction)/E5(control)/K1(adaptive-null)/SEAL_2
(held-out) — four *methods*, one *positive*; C3_lb_calib vs C_AUDIT are an initial calibration and its rigorous
supersession (both correctly on-LB); CSA PC-19/21/22 are engineering stages of one matcher (none counted as an LA
result). **Clarification (not an error):** ~7 constraint-expansion rows + all positive-controls/instruments are
`claim_layer=meta`/`NOT_APPLICABLE` — correctly *not* presented as LA readings, but a headline "N LA methods tried"
should exclude them (see Q9).

**4. Which outcomes were misclassified?** None materially. Verdict semantics are correct throughout
(`VERDICT_SEMANTICS_AUDIT.md`): `NO_POWER` never stated as refutation; `SOURCE_BLOCKED` never as a negative result;
`REJECT` scoped to the registered chain; literature-recovery labeled `TRIVIAL_RECOVERY` not discovery; relative
classes never stated as absolute values; broad-family nulls scoped, not "refutes all models". **One stale wording:**
the constraint-expansion `CE-H/CE-J` rows still phrase the bigram-LL relabeling-invariance as a *global provable
theorem*; P1's own `LIN-05` + master report record it as SUPERSEDED/OVERSTATED, but the row text lacks the
forward-supersession link (→ minor correction, applied).

**5. Which numbers were wrong or untraceable?** None wrong. All checked reproduced from committed JSON. Minor
labeling: P1's `RESULT_NUMBERS.csv` tags every row `REPORT_ONLY`, but ~40% are actually `ARTIFACT_VERIFIED` from
committed JSONs (a *conservative under-claim*, corrected in `RESULT_NUMBERS_VERIFIED.csv` guidance); and `K1` libation
p is reported as 0.030 while the artifact field is `adaptive_p_random_anchor=0.00202` (both are real statistics in
the same file — a labeling nuance, not a mismatch).

**6. Which statuses were stale?** ~5 branch `STATUS.md` headers on CLOSED campaigns (admin_schema/no_human/
observable/continuity/ritual/egyptian) still read as scaffold/"not-yet-issued"/"READY" — P1 flagged these; the
red-team confirms and lists corrections in `BRANCH_STATUS_RECONCILIATION.md` (the *authoritative* status always
lives in CAMPAIGN/DECISION_LOG/TASK_LEDGER; STATUS headers are cosmetic and were not rewritten — read-only audit).
The one *material* status correction is `EA-02` (Q2).

**7. Which methods were proposed but never run?** 9 DESIGNED_NOT_RUN + 7 PROPOSED_ONLY + 7 SOURCE_BLOCKED + 3
POWER_GATED + 1 COMPUTE_BLOCKED — chiefly: the human-annotated admin-schema gold (`ADMIN-07`, BLOCKED then
CLOSED_BY_OWNER); the Di Mino 40-sign/408-lexicon/LB-correction/logogram gates (`SOURCE_BLOCKED`, artifacts
withheld); the CSA 600–700-word cells (`COMPUTE_BLOCKED`, never measured — the invariant-12 clamp); the Egyptian
downstream gates (`SOURCE_BLOCKED`/blocked). All correctly labeled by P1.

**8. Which results are superseded?** The five in `LIN-01/02/04/05/06` — position→C/V (frequency artifact),
reduced-seed 0.87 (frequency artifact), the value-blindness *global theorem* (overstated → LA-specific
underdetermination), 259 params (category error → V=92), palaeo image "success" (withdrawn as circular). All
recorded append-only; the later artifact governs.

**9. Exact current highest earned claim layer.** **L2/L3 (structural / administrative-functional), held-out- and
adaptive-null-validated** — document templates/closure, A- prefixation (adaptive p 0.008), KU-RO-terminal and
libation formula grammars. **No L4/L5/L6/L8 layer earned on Linear A; all transfer licences NOT_EARNED.** The 37
`SUPPORTED` rows are discipline-instruments, known-script positive controls, or L2/L3 structure — **zero are Linear
A readings** (the red-team confirms this framing is correct, and recommends the executive count separate the ~15
instrument/control/meta instances from the LA-method count).

**10. Which approaches have genuinely never been tried?** (`OPEN_AND_UNTESTED_METHODS.md`, verified) A
palaeographic **stroke corpus** cross-script channel (the one non-circular shape channel, unpopulated); a **3D/seal
imaging** channel; a **genuine bilingual** joint decipherment; the substitution consonant-axis used as a
*cross-script bridge feature*; active-learning corpus acquisition targeting max equivalence-class-reduction signs.
The **Anetaki II delta seal** is registered+hashed but unrun (awaits the editio princeps).

**11. Which prior methods should not be repeated unchanged?** position→C/V distributional recovery; reduced-seed
propagation; cross-script *distributional* transfer; unconstrained candidate-language/root search — all null or
frequency-artifact under proper multiplicity + oriented nulls.

**12. Concrete inputs for an all-unresolved-sign anchor-lattice campaign.** The de-duplicated anchor inventory
(WP-G, minus circular GORILA-lineage anchors; SEED_A=0 today); the validated substitution consonant-axis (the only
internal channel that broke C/V non-circularly, on LB); the A-/formula L2/L3 grammar as a structural prior; the
**newly surfaced `EA-13` frozen Egyptian-loanword power envelope** (design-powered at La≥4 — a concrete
scarcity-limited external-anchor lever P1 had missed); the held-out seal partitions (SEAL_2/3/4) and the frozen
Di-Mino prereg as the honesty backstop.

**13. What is missing before that campaign can be responsibly designed?** (a) ≥3 *independent* non-circular held-out
anchors or a bilingual — the value layer is relabeling-invariant/underdetermined without them (0 exploitable bits;
≥10²⁷ twins); (b) more corpus mass / longer continuous inscriptions to lift the substitution channel above its LA
scarcity floor; (c) the withheld artifacts (Anetaki editio princeps; a stroke/3D corpus). Absent these, an
anchor-lattice campaign would re-derive the same underdetermination.

## Corrections applied in the verified deliverables
1. **Added `EA-13`** (omitted frozen-power-pass) → `METHOD_INSTANCES_VERIFIED` (214→215); qualifies `EA-02`.
2. Flagged `CE-H/CE-J` and `A1_reconstruct`/`K1_nulls` bare-`SUPPORTED` tags as needing the forward-supersession /
   analogue-only qualifier (P1's lineage layer already carries it).
3. Noted `RESULT_NUMBERS` classification under-claim (many `REPORT_ONLY` are `ARTIFACT_VERIFIED`).
4. Recommended the executive "N methods" count separate ~15 instrument/control/meta instances from LA methods.
5. Confirmed the CSA-clamp ERRATUM-class finding is *accurately* reported by P1 (independently reproduced).

**No scientific history, verdict ledger, or paper artifact was changed. P1's report is preserved verbatim; all
corrections live in this red-team's `_VERIFIED` tables and reports.**
