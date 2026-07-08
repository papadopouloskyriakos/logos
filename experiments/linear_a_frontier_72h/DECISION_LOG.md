# DECISION LOG — frontier 72h (append-only)
- 2026-07-08T03:20Z opened from anchor-lattice d46a11e. Clock written mechanically (72h, min 18 epochs);
  finalization gate = scripts/clock_check.py (exit-code enforced). 24 tests pass; paper a2ab89fa untouched;
  corpus symlinked. NOTE: anchor-lattice WP-N still running on its own branch/worktree — its result closes THAT
  campaign and feeds this baseline at checkpoint 1; not a blocker for epoch execution.
- EPOCH-001 selected = top of TASK_QUEUE: Ariadne-2025 Anetaki preliminary-material source acquisition (frontier
  F8/F1; gate B/H) — the #1-ranked acquisition from the anchor-lattice K queue, genuinely new published data not
  in silver.
- EPOCH-001/002 complete (both substantive). E001: Anetaki contradiction resolved; seals intact; KNZg57a
  provenance gap registered. E002: FIRST Holm-surviving cross-script motif recovery on KNOWN LB<->Cypriot —
  a candidate NEW_SYMMETRY_BREAKING_CHANNEL at known-script level, seed-budget-limited. Queue re-ranked:
  E003 seed-poverty curve (F3, decisive for LA applicability), E004 fraction-order third seal (F10, cheap
  falsifiable prereg before Anetaki II lands), E005 KNZg57a provenance trace (F8; seals' exclusion lists may
  need ERRATUM). Launching all three.
- EPOCH-007 (F5, gate A/C) executed: ledger-role induction as anchor constraints. Prereg 6c85277d frozen
  04:13:24Z BEFORE any run. PC1 caught the initial machinery (k=5/13-feature) as broken (macro-F1 .69,
  recall(U)=0) — calibrated on SYNTHETIC ONLY (DEV-1 preceding-token features, DEV-2 k=12 -> PC1 1.00),
  then a single real run. LB detector did NOT fire: heldout macro-F1 .341 (<.50), recall(T)=recall(U)=0 —
  KN-vs-rest split crosses a genuine convention divide (to-so is a Pylos habit: 261 PY vs 57 KN; KN gold T
  = 0.4% of derivation tokens). Verdict ROLE_INDUCTION_NO_POWER (mechanical). Post-hoc (labeled): units-slot
  IS structurally identifiable (recall .862 under recall-lift decode) -> successor channel; totals need
  arithmetic sum-consistency features + within-site splits. LA leg stayed gated (exploratory readout only,
  no constraints emitted).
- EPOCH-014 banked (12/18). E012 (allograph structure) + E013 (component matcher) hit the provider session
  limit (resets 09:00 Europe/Amsterdam = 07:00 UTC) -> COMPUTE_BLOCKED temporarily; workflow resume-id
  wf_aca1e317-7d0 (E014 replays from cache; E012/E013 run live on resume). Not an early-stop condition;
  campaign continues on reset.
- EPOCH-012 COMPLETE + banked (13/18), resumed after the 07:00 UTC session reset (prereg a051ea37 was
  frozen 05:15Z BEFORE the interruption; run artifacts written 07:18Z; report + ledger written on resume —
  no re-analysis, no threshold touched). Verdict ALLOGRAPH_STRUCTURE_CONFOUNDED: both confirmatory legs
  fire (per-sign spread T .2046 p_holm 2e-4; doc-site bal-acc .2797 p_holm .0061) but the document channel
  fails G3 (nuisance embedding .3307 > .2797) and G2 (HT-vs-KH tablets null) -> no doc->site/hand lattice
  output licensed. The per-sign aggregate spread channel is individually robust (G1 pass; tablet-only
  posthoc p 1e-4) -> decisive successor = photograph-level re-extraction (AB58/A704/AB73). Bonus: medium
  structure within HT (p .0028); chronology contexts NO_POWER.
- EPOCH-016 (F9, gate A) executed: SBI pilot, known-script calibration only. Prereg a15faa74 frozen
  12:35:48Z BEFORE any run (script sha256 matches). All controls PASS (PC-A .6846>=.40; NEG no leak;
  MISSPEC ROBUST drop .074<.10). Mechanical verdict SBI_MATCHES at b=0/3/5 (exactly the preregistered
  modal prediction p=.35); miscalibration override false. Full script re-execution reproduced every
  number byte-identically (determinism check, not required by prereg but run anyway given the pilot's
  novelty). Honest reading beyond the verdict: raw-cosine spectral clustering (no learning) is the
  single best method at every budget tested; SBI never beats it by a material margin. BASE_M1 (E003
  G-surface analogue) reconfirmed weakest baseline under a disjoint estimator family -> the
  anchor-geometry bottleneck E003 found is not an artifact of that estimator. Sub-prediction "LB
  flagged OOD >=50% of replicates" REFUTED (0/20) -> the OOD detector has low power; this weakens
  (does not overturn) the MISSPEC ROBUST read. No support gained for SBI as an F9 architecture upgrade
  at LA's operating scale; F9 stays ACTIVE. LA never loaded (grep-verified); L2 ceiling; no licences
  touched. Report: reports/EPOCH016_SBI_PILOT.md · 7 ranked successors.
