# DECISION LOG — append-only (Art. XVII)

- **Campaign opened 2026-07-07.** Forked research/linear-a-relative-phonology-seals from Foundry 09f7ef9.
  Verified: main 6fd4f20 untouched; Constitution v2.2 authoritative; paper arxiv pdf sha256 a2ab89fa313e5b30
  (frozen); test baseline 38 passed (run_tamburini collection quirk pre-existing, not a failure). Scaffold +
  TASK_LEDGER.yaml (WPs A–M) committed. First substantive task: WP-A replication + multiplicity audit of the
  Foundry position→C/V result — explicitly authorized to downgrade/refute my own prior claim.

- **WP-A COMPLETE → `CV_ANALOGUE_REFUTED` (refutes my own prior Foundry C1 pillar).** A1 reproduced all headline
  numbers exactly (0.744/0.835/p0.01) + found a filter bug (exp(log(20))<20 drops 3 signs; clean 77-sign
  position-only 0.586). A2: single-feature position survives NO multiplicity (Bonf×13 0.455, Holm 0.36, FDR q
  0.168) and isn't even the best channel (log_freq 0.878, rnbr_ent 0.800 beat it). A3: 2 independent unsupervised
  models fail (GMM/HMM); oriented null p 0.146; only 3/5 vowels; drop-A → 0.448. A4: survives corpus-domain
  grouping but collapses under frequency-band-disjoint split (position-only 0.481=chance); 4/5 vowels in top freq
  quartile. A5: flat non-significant surface (undegraded LB p≈0.16). A6: random-label p 0.146, freq-matched p
  0.130, order-destruction leaves AUC unchanged, best_of_model null fails p 0.129. ERRATUM: Foundry C1
  (position→C/V) SUPERSEDED — the surviving signal is a frequency PRIOR (external, relabeling-invariant), not
  corpus-internal positional structure. The 'not value-blind' question now rests entirely on the SUBSTITUTION
  channel (C3 consonant-held axis), which must face the same audit (WP-C4/C5+D = load-bearing). Highest layer L2;
  licences NOT_EARNED. Append-only: Foundry record intact; this supersedes the position interpretation.
