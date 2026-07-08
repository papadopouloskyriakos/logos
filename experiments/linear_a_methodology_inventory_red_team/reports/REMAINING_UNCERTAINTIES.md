# Remaining uncertainties (red-team)

1. **ROW_VERIFICATION machine-extraction is partial** (39 of 215 rows auto-extracted into the CSV from the
   per-agent detail JSONs, which used heterogeneous shapes). The AUTHORITATIVE verification result is the
   aggregate histogram (203 VERIFIED / 12 MINOR / 0 MATERIAL_ERROR of 215) from the agents' structured returns +
   the per-lineage detail files (`data/rt_*.json`); the CSV is a supplement, not the full record.
2. **EA-13 power interpretation** rests on the owning-branch `frozen_power_envelope.json`; "POWERED_DESIGN at
   La≥4" is design-conditional (scarcity-limited) — it does NOT earn a licence and does NOT change the L2/L3
   ceiling, but the exact envelope should be re-read in a future anchor-lattice design.
3. **CSA-clamp ERRATUM** is confirmed accurate but lives in the *byte-frozen submitted paper* — it can only be
   corrected by a paper erratum, out of scope here.
4. **Numerical audit is a trace, not a full rerun** — ~60 load-bearing numbers were reproduced from committed
   JSON; expensive sweeps (CSA, permutation nulls) were verified at the artifact level, not re-executed.
5. **Sibling-branch depth:** admin/observable/external/continuity/ritual/egyptian were verified at the
   method-instance + verdict-semantics level; a few internal sub-analyses (e.g. individual masked-channel
   ablations) are catalogued as one instance each and not separately re-run.
