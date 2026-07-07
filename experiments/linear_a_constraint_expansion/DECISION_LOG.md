# DECISION LOG

## 2026-07-07
- Campaign opened from main@6fd4f20 under Constitution v2.2. Isolation + append-only ledger verified; test
  baseline 411 passed. Offensive mandate: seek value-informative constraints, not re-run closed nulls.
- **Stage A `A_REOPENED`.** Recomputed the identifiability budget from signs_ontology + the corpus's own
  inventories. Prior `259>212` is a category error (259 = all diplomatic stream tokens; a reading needs the
  syllabary = 88-92 / 123 families / 72 A-only). Corrected: 92 params < 212 STRUCTURAL constraints (ratio
  0.43, favourable) but only ~2 VALUE-INFORMATIVE constraints (46× deficit). Underdetermination cause =
  constraint informativeness at the value layer, not count. Reopen target = value-informative constraints for
  ~92 syllabic parameters. Commit: _(this)_.
- **Stage B `ADVANCES` (representation), no value gain.** 5-agent forensics (wf_da6d35c8). Confirms syllabary=92
  (259 = 108 ligatures + 13 damage + logograms). SigLA not independent (same GORILA lineage); AB value-class
  CONTESTED (10 signs flip → value channel weaker than assumed). effective_n: 1242 objects / 565 usable lexical.
  Cleaned phonetic channel (scripts/stage_b_clean_representation.py): 819/3147 word tokens non-phonetic → 944
  clean wordform types for Stage D. Recovered channels: support-invariance (H(support|site)=1.23), accounting
  (blocked on notation typing), findspot (Younger bronze). Data-hygiene: subscript key normalization fixed.
  Commit: _(this)_. Checkpoint 1 written.
- **Stage C `C_NEW_INFORMATION_FOUND` (not value-informative).** Bronze holds new/newly-available material:
  Salgarella 2020 (shape homomorphy — circular, <=0.75), Younger edition (same lineage + findspot), Kanta 2024
  Anetaki = 1 new inscription KO-RO-NO-WE-SA (5 signs), del Freo rapport, Chiapello prepub prediction (3rd-party
  registry). None supplies a non-circular VALUE constraint; corpus near-exhausted for value evidence. Findspot
  (Younger) + support-type (B6) are the usable new invariance axes for Stage D. Commit: _(this)_.
- **Stage D — no value-informative constraint; mostly CONFIRMS_KNOWN.** 5-agent mining (wf_b5d7fd20) on clean
  material. D1 formula CONFIRMS_KNOWN (libation+KU-RO only; 0% held-out cross-genre). D2 morphology NULL
  (paradigm model does not beat smoothed bigram on unseen stems; naive unigram comparison would have been a
  FALSE POSITIVE — control erased it; has power). D4 accounting CONFIRMS_KNOWN (fraction typing net-zero on
  closure; Bennett A700 hypothesis inert; re-derives KU-RO=total). D5 invariance CONFIRMS_KNOWN (real held-out
  cross-genre word-initial phonotactics r<=0.93, but value-free). D7 compression CONFIRMS_KNOWN (grammar beats
  6 baselines held-out at 1.42 vs 1.77 bits/tok, but = known admin list format). Value layer empty across every
  internal channel. Commit: _(this)_. Checkpoint 2 written. Verdict hinges on F (anchors) + J (nulls).
- **Stages E+F (wf_9cfcc3ff).** E `METHOD_VALID_LA_NULL_IS_CORPUS`: recovery methods fire on known-script/
  planted truth (LB morphology 0.56>0.31; opaque-LB self-persistence 11/11; planted power->1.0 at s=13; gate
  false-graduation 0.6%) and null on LA -> LA null is a CORPUS property. F `NO_NONCIRCULAR_ANCHOR`: Salgarella
  2020 (now available) is the shape/homomorphy channel (circular, <=0.75); her anchors are the same toponyms
  already REFUTEd; no anchor class has >=3 independent held-out non-circular anchors. Frozen preregistered
  one-shots not re-run. **Consequence:** Stage D2 relabeling-invariance + F no-anchor => Stage H (agnostic
  internal value search) is a PROVABLE null (a sign-value assignment is a relabeling; internal structure is
  relabeling-invariant). NOTE: git reports/ + data/ are gitignored — force-added the full A-F record here.
  Commit: _(this)_.
