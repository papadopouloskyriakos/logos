# PROJECT CHARTER — LA↔LB Toponym-Continuity Feasibility Pass

**Branch:** `research/la-lb-toponym-continuity`  ·  **Worktree:** `/home/claude-runner/gitlab/n8n/logos-la-lb-continuity`
**Forked from:** `research/external-minoan-anchors` @ `6d2e926` (recorded in DECISION_LOG.md).

## Decision (what this pass is)

Adopt the **Linear A → Linear B internal toponym-persistence channel** as the *next primary*
feasibility experiment — **not** as a confirmed redirect and **not** as independent phonetic
evidence. The Egyptian channel is **preserved unchanged** on the parent branch: this pass does not
fit, delete, or merge it. We return to Egyptian only after LA↔LB gets a mechanical power +
circularity verdict.

**Objective:** determine whether the LA↔LB channel has usable power *after removing projected
phonetic readings, post-hoc pair selection, and free mapping search*. A rigorous null or circularity
failure is a **successful** result.

## Research question

> Do Linear A strings selected as toponym-like **from internal context** recur in Linear B as
> **independently identified** Cretan toponyms at a rate/specificity exceeding matched end-to-end
> nulls, when comparison is on **raw sign identity** or a **frozen palaeographic A↔B equivalence
> map** rather than projected phonetic readings?

Secondary: (1) present at raw sign-ID level? (2) requires projected LB phonetic values? (3) survives
leave-one-pair-out? (4) generalizes beyond the five known examples? (5) retains power after candidate
multiplicity, site/genre structure, transcription uncertainty, allography, length, sign frequency,
post-hoc risk?

## Categories — never infer the stronger from the weaker

```
ORTHOGRAPHIC_CONTINUITY   (shared sign shapes / IDs)
LEXICAL_CONTINUITY        (same administrative entity/word persists)
PHONETIC_CONTINUITY       (same sound values)
```

## Comparison levels (kept strictly separate)

```
LEVEL_1  exact raw sign-ID identity where IDs are directly shared
LEVEL_2  frozen palaeographic A↔B equivalence classes         ← primary basis
LEVEL_3  projected Linear B phonetic values                   ← ABLATION/SENSITIVITY ONLY
```
LEVEL_3 must never define the primary result.

## Verdict ontologies (mechanical; the LLM never grades the outcome — logos invariant 2)

```
status            ∈ {INCOMPLETE, COMPLETE}
channel_readiness ∈ {NOT_READY, READY_FOR_PREREG_DRAFT, NO_POWER}
circularity       ∈ {CIRCULARITY_LOW, CIRCULARITY_MANAGED, CIRCULARITY_HIGH, CIRCULARITY_FATAL}
```
The primary channel cannot advance if circularity is HIGH or FATAL. `INCOMPLETE` must **not** be used
to dodge a warranted `NO_POWER`.

## The five known examples are DEVELOPMENT material, not discoveries

`pa-i-to · tu-ru-sa · di-ki-ta · i-da · se-to-i-ja` were already observed (Salgarella lecture) →
default class **DEVELOPMENT_BENCHMARK**. They may debug the pipeline and act as positive controls,
but are **not** evidence of generalization and are **not** described as newly discovered here.
Speculative morphology (`di-de-ru~di-de-ro`, `pa-je-re~pa-je-ro`) is stored separately as
`SPECULATIVE_MORPHOLOGICAL_CONTINUITY` and must not influence the map, thresholds, or power result.

## Isolation & forbidden actions (§II, §XVI)

MUST NOT: touch `runtime/csa_sweep/`; signal/inspect-destructively any CSA process; modify `paper/`
or the TACL correction; resume/alter the Egyptian-model pass; access protected fenced compute; change
the frozen slot rules **in place** (use read-only); rewrite the parent external-anchor branch.
Light local CPU only. STOP conditions: isolation failure, SigLA licensing bars intended handling,
non-deterministic source reconstruction, equivalence map inseparable from known lexemes, slot
classifier found to leak phonetics, LB targets selected by LA resemblance, an adaptive choice that
cannot enter the null, compute would interfere with the live sweep, or real LA phonetic
interpretation becomes required. **No** language-family/decipherment verdict is issued by this pass.

## Deliverables (§XVII) & commit plan (§XVIII)

Reports: SIGLA_SOURCE_AUDIT · SIGLA_SILVER_CROSSWALK · SIGLA_CORPUS_DELTA · AB_SIGN_EQUIVALENCE_AUDIT
· KNOWN_PERSISTENCE_PAIR_AUDIT · LA_CANDIDATE_FREEZE · LB_TOPONYM_TARGET_AUDIT · CONTINUITY_MODEL_SPEC
· POSITIVE_CONTROL_RESULTS · END_TO_END_NULL_RESULTS · CONTINUITY_POWER_ENVELOPE · CIRCULARITY_AUDIT ·
CHANNEL_COMPARISON · FINAL_CHANNEL_VERDICT. Plus machine-readable manifests, checksums, deterministic
regeneration code, tests, search receipts, result files. Commits are logically separated (1 scaffold →
2 SigLA reconcile → 3 A↔B equivalence → 4 known-pair audit → 5 candidate/target freeze → 6 model+ablations
→ 7 positive controls → 8 nulls → 9 power → 10 circularity+verdict); all hashes logged in DECISION_LOG.md.

## Data handling

`corpus/silver/*` and the SigLA decode are **gitignored licensed-derived data**, present only in the
main worktree. This pass **references** them read-only from canonical main-repo paths and commits
**code + checksums + counts + schema + reproducibility tests**, never the licensed data itself.
