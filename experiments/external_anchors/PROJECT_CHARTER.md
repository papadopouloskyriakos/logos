# PROJECT CHARTER — External Minoan Anchors, Population Priors, Falsifiable Language Testing

**Subproject of `logos`. Parallel, isolated, falsification-first.**

- **Branch:** `research/external-minoan-anchors`
- **Worktree:** `/home/claude-runner/gitlab/n8n/logos-external-anchors`
- **Source commit (forked from `main`):** `762f48d9867fb96a1315d13797bb3ca06918a47c`
- **Charter date:** 2026-07-06
- **Read-only inputs:** the licensed/gitignored Linear A corpus at
  `/home/claude-runner/gitlab/n8n/logos/corpus/silver/` — checksum-pinned in
  `data/manifests/linear_a_inputs.sha256`, **referenced in place, never copied or committed**
  (invariant 10: licensed vendor-derived data is not redistributed).

## Mission

Determine whether external archaeological, administrative, linguistic, and population-genetic
evidence can supply **independently verifiable** constraints for partial interpretation or phonetic
anchoring of Linear A — under a falsification-first procedure. **The objective is not to find a
translation.** A rigorous null (`NO_POWER` / `NULL_PUBLISHED`) is a successful result. Attractive
lexical resemblances are not evidence.

## Isolation contract (non-negotiable)

This subproject **must not** disturb the live `logos` state. Forbidden: touching
`runtime/csa_sweep/`, `.claim`/result JSONs, the CSA scheduler/watchers, the halted Exit-B sweep,
`paper/`, the TACL manuscript, existing preregistrations, or Zenodo artifacts; consuming the fenced
sweep cores; merging into the Exit-B correction branch; editing corpus files in place; or reusing
exploratory outcomes as confirmatory. Natural isolation: `runtime/` is gitignored, so this worktree
does not even contain the sweep artifacts. All subproject compute is lightweight until Stage 3+ and
will use separate/idle resources or wait for the sweep — never oversubscribe the protected fence.

## Research questions (kept separate — no single "decipherment" score)

- **RQ1 — External semantic constraints:** do external administrative/archaeological records improve
  identification of commodity classes, transaction types, roles, place-/personal-name slots, titles,
  totals/deficits/allocations? (Need not be phonetic to be useful.)
- **RQ2 — Egyptian toponym anchors:** do securely-identified Egyptian renderings of Cretan places
  impose phonetic constraints that **generalize to held-out** Linear A name-like forms better than
  matched null anchors?
- **RQ3 — Personal-name anchors:** after chronology + Minoan-vs-Greek identity are accounted for, do
  external Cretan personal names add held-out predictive value? (Higher risk than RQ2.)
- **RQ4 — Keftiu ritual-language:** can alleged Keftiu strings constrain a phoneme inventory /
  syllable structure / recurring patterns? (Exploratory; no direct word-matching to LA formulae.)
- **RQ5 — Candidate-language prioritization:** after anchors + schema are frozen, does any motivated
  language family outperform unrelated + synthetic controls at **equal search budget**?
- **RQ6 — Population-history prior:** can aDNA/archaeology justify a **weak** ordering of candidate
  families without determining the verdict? (Genes ≠ language; a modest prior-odds nudge at most.)

## Verdict ontology (mechanical, from frozen criteria — the model never grades its own narrative)

```
status  ∈ { INCOMPLETE, COMPLETE }
verdict ∈ { NO_POWER, NULL_PUBLISHED, REJECT, GRADUATE }
```
Precedence: `INCOMPLETE` (missing data/calibration/controls/provenance) → `NO_POWER` (frozen design
can't separate plausible signal from null) → `REJECT` (fails frozen criteria/controls) →
`NULL_PUBLISHED` (complete valid experiment, nothing above threshold) → `GRADUATE` (clears ALL of:
positive-control sensitivity, end-to-end null calibration, held-out prediction, transcription
sensitivity, temporal/provenance constraints, equal-budget comparison, preregistered thresholds).

## Method invariants inherited from `logos`

1. **No confirmatory claim without a frozen pre-registration + external timestamp.** Anything before
   the timestamp is exploratory and stays labelled exploratory.
2. **End-to-end null calibration, not naïve hypothesis counting** — the null pipeline replays every
   adaptive choice (candidate selection, segmentation, mapping search, model selection, restarts).
3. **Freeze before you look:** the Egyptian→foreign correspondence model is estimated on an
   *independent* calibration corpus and frozen before touching Cretan targets; the LA slot classifier
   is frozen before confirmatory phonetic testing; both applied identically to real and null anchors.
4. **Positive control gates sensitivity:** the whole pipeline must recover signal on a *deciphered*
   comparator (Linear B / Greek, degraded to LA scale) or the LA test has no interpretive value.
5. **Toponyms before personal names** (continuity across the Minoan→Mycenaean shift = lower
   false-anchor risk); **temporal overlap is a hard, evidence-class-sensitive filter**, not metadata.
6. **Transcription is not ground truth:** confirmatory findings are re-run over plausible LA
   transcription variants; one-transcription-only results are reported as fragile.
7. **Equal budget across candidate languages** — no language gets extra flexibility for looking
   promising; the candidate set must admit "none is supported".

## Provenance of the design

This charter operationalizes the external-anchor programme discussed with the human on 2026-07-06,
itself grounded in this session's exploratory schema/reconciliation work (main-repo
`experiments/schema_recon/`, `experiments/schema_induction/` — the administrative layer reconciles
~29–35% vs a 0.5% null, giving the slot-scaffold for RQ1). Those results are **exploratory** and are
inputs here, not confirmatory evidence.
