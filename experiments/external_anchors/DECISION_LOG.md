# DECISION LOG

Append-only. Each entry: date · decision · rationale.

- **2026-07-06 · Isolate via separate branch + worktree, forked from `main@762f48d`.** Keeps the
  live CSA sweep / Exit-B correction / frozen paper untouched; `runtime/` is gitignored so the
  worktree naturally excludes sweep artifacts.
- **2026-07-06 · Reference the Linear A silver corpus read-only, never copy/commit it.** It is
  gitignored licensed-derived data (invariant 10). Checksums pinned in
  `data/manifests/linear_a_inputs.sha256`; subproject code reads from the main worktree path.
- **2026-07-06 · Toponyms before personal names.** Place-names persist across the Minoan→Mycenaean
  shift (geography doesn't change language), so they carry lower false-anchor risk than personal
  names, which for the LM II–IIIA Keftiu horizon may be Minoan *or* Greek. Personal names (E4) run
  after E3 and gate on `minoan_vs_greek_confidence`.
- **2026-07-06 · Freeze the Egyptian→foreign correspondence model on an INDEPENDENT calibration
  corpus before any Cretan match.** The three-layer flexibility (lossy Egyptian spelling ×
  position-inferred LA slots × parameterized distortion model) is exactly where a false "consistent
  mapping" is manufacturable; the model must be estimated where it cannot see the answer. → REQ-02
  is `BLOCKING` for RQ2/RQ3.
- **2026-07-06 · Temporal overlap is a hard, evidence-class-sensitive filter (tiers A–D), not a
  metadata column.** Names/vocabulary: strong exclusion for later tiers; toponyms: later admissible
  with explicit persistence; admin semantics: informative but non-phonetic; ritual: exploratory.
- **2026-07-06 · Keftiu incantations (EA10059) are exploratory-only for phonology** (`voces magicae`
  distortion; possible non-coherence). No direct word-matching to LA libation formulae without a
  separate later prereg.
- **2026-07-06 · Population genetics (RQ6) may reorder candidate tests by at most a modest prior-odds
  nudge; held-out textual evidence remains decisive.** Genes ≠ language.
- **2026-07-06 · Candidate-language tournament (E8) is LAST**, after anchors + calibration + nulls are
  frozen, with equal budget per candidate and a mandatory "none supported" option — so it cannot
  become thesaurus-fishing (the "English is Semitic" failure mode).
- **2026-07-06 · EA5647 Keftiu personal names are GREEK, not Minoan (Dautais & Gabolde 2022).** The
  leading recent edition reads all seven names via Linear B / Greek onomastics (Eudamos, Nasios,
  Panaretos, Lysis…) and calls the board the *earliest written evidence of Greek names*. → The
  richest external source of "Cretan" personal names is Mycenaean-Greek, confirming the Minoan-vs-
  Greek confound. EA5647 is ingested as a **Greek negative-control / calibration** for E4
  (`minoan_vs_greek_confidence≈0.1`, tier-D, held-out), **not** a Minoan anchor. Reinforces:
  toponyms lead; personal names run last and gated; the Minoan personal-name channel is thin.
- **2026-07-06 · Milestone commits** — Task A slot classifier: `dcba879`,`db09ca0`,`d6cfe4f`; Task
  C/D/B + E to follow this entry. design_readiness=READY_FOR_CALIBRATION; naive design leans
  NO_POWER (in-sample FP≈1.0; held-out FP≈0.25 vs recovery≈0.40). Next: fit the frozen Hoch
  correspondence model, then re-run the power envelope + matched-scarcity control under it.
