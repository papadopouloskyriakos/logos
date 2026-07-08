# EPOCH-007 — PREREGISTRATION (frozen BEFORE any analysis run)

**Campaign:** linear-a-frontier-72h · frontier **F5** (ledger-role induction as anchor constraints)
**Epoch question:** Can transaction-role slots (name-slot / commodity / unit / totals-marker; quantity = the
numeral itself) be induced BLIND from ledger document structure alone, validated on Linear B (known), and
transferred to Linear A as slot-semantics (L2/L3) constraints?
**Branch:** research/linear-a-frontier-72h · **Seed:** 20260708 · **Date frozen:** 2026-07-08
**Substantive gate:** A/C.
**Articles triggered:** V (claim layers — everything here is L2/L3 functional-slot, NO value/semantic claim),
VII (search receipt), VIII (effective_n: doc-level binomials, not occurrence-level), IX (info budget),
XI/XII (non-circularity: features never read sign values; gold labels used ONLY to grade; KU-RO/KI-RO/A-prefix
known structure used ONLY as consistency checks, never as features or fit targets), XV (no transfer licence is
earned; a FUNCTIONAL licence would require this + independent convergence — out of scope), XVII (append-only),
XXII (this header).
**Claim layer of ANY result here: L2/L3 (functional slot-role, relative/structural). No phonetic, lexical or
semantic value can emerge from this epoch.**

## Prior art cited + differenced (do-not-repeat check)

- Observable-channels programme (`research/observable-admin-channel-recovery`): L3 **word-context → commodity
  channel** REFUTED (well-powered A12; word contexts do not predict WHICH commodity); L2 doc-structure
  (templates + closure) SUPPORTED but earned no functional licence. **Difference here:** we do NOT predict
  which commodity/channel a word belongs to. We induce PER-SLOT ROLES (is this token occupying a name-slot,
  a commodity-slot, a unit-slot, a totals-slot?) from within-document geometry (numeral adjacency, line
  position, repetition profile). The refuted task was lexical-distributional (word → channel identity); this
  task is positional-functional (occurrence → slot type). A commodity-slot verdict says nothing about which
  commodity.
- Relative-phonology campaign K1: KU-RO-terminal, A- prefixation, libation order = validated L2/L3 structure.
  Used here ONLY as post-hoc consistency checks on the LA side (Art. XII: they are not features, not fit
  targets, and were established by independent machinery).

## Data / units (frozen; pre-freeze descriptive audit only — no role analysis run)

- **LB:** DĀMOS `corpus/bronze/linearb/damos/items.jsonl` (5,840 items; `item.content` transliteration).
  Ledger filter (both scripts): ≥2 numeral tokens AND ≥3 sign-group tokens AND ≥2 lines. Pre-audit: 2,569
  items have ≥2 numerals (before the other two filter clauses). Derivation = KN items; held-out = all
  non-KN items (PY/TH/MY/TI/KH/…). Unit of analysis = document.
- **LA:** `corpus/silver/inscriptions_structured.json` (1,341 unique ids; `stream` = word/num/div/nl events).
  Same ledger filter → pre-audit 235 docs with ≥2 numerals (HT 146, KH 30, ZA 23, rest ≤9).
  Pre-audit check-token counts: KU-RO 36 occ, KI-RO 15 occ, A-prefix multi-sign words 72 occ.

## Blinding contract (Art. XI)

Features may use ONLY: token category (sign-group vs numeral — L1 graphically observable), numeral values
(L1), sign-group length in signs, position in line, line position in document, and recurrence of the HASHED
group identity (identity is L1; the value/reading is never read). Editorial case (DAMOS lowercase syllabic vs
uppercase logogram) is an annotation of VALUE-knowledge → it is erased: blind id = sha1(casefold(token));
group length = number of hyphen-separated parts (an uppercase logogram = 1 part = 1 sign; this matches script
reality, not editorial judgment). Gold labels (which DO use case and readings) are computed in a separate
grading module and never enter the feature/cluster path.

## Pipeline (frozen)

1. **Parse** documents into lines of tokens: GROUP(blind_id, n_signs) | NUM(value). Editorial cleanup:
   strip ⟦…⟧, brackets/damage marks `[ ] ? < > ' "`; drop line labels (`.1`, `.2a`, `v.1`, `.A`…), drop
   `vac./vacat/deest/mut./sup./inf./vest.` and pure punctuation (`/`, `,`). LA stream events map directly
   (word→GROUP, num→NUM; `div`/`nl` structure kept; fractions in `other` events are dropped as tokens but
   do not break adjacency). LB fractions do not occur (unit signs instead).
2. **Features per GROUP occurrence** (13, all structural):
   (1) min(n_signs,6); (2) followed_by_num ∈{0,1} (next token in line is NUM); (3) log1p(num value after,
   else 0); (4) num_after / max num in doc (else 0); (5) line_pos_frac; (6) is_line_initial; (7) line_frac
   = line_idx/(n_lines−1); (8) is_last_content_line; (9) min(#distinct lines in doc containing this type,5);
   (10) type document-frequency across the partition's ledger docs; (11) type line-initial rate (partition);
   (12) type followed-by-num rate (partition); (13) proximity to next NUM in line = 1/(1+#tokens between),
   0 if none. Type-level stats (10–12) are computed within the partition being featurized (unlabeled
   structure only — no label leakage).
3. **Cluster:** z-score (scaler fit on LB derivation), k-means k=5, seed 20260708, n_init=50 (sklearn).
4. **Role decode:** many-to-one cluster→gold-class mapping by majority vote on LB DERIVATION only; frozen;
   applied to held-out/LA by nearest-centroid.
5. **Gold classes (grading only, LB):** NUM excluded (quantity role is trivially the numeral). Order:
   hyphenated → T if casefold starts with `to-so`/`to-sa`; else W. Single-part → U if ∈ {S,V,T,Z,M,N,L,P,Q}
   (exact uppercase); else C if it has an uppercase letter or leading `*`; else W. Secondary descriptive
   class D = `o-pe-ro*` / bare `o` (reported, never gated).

## Controls & thresholds (frozen)

- **PC1 (positive control, run FIRST):** 150 synthetic ledgers (seeded template generator: header words,
  entry lines = name-word + commodity-logogram(+unit) + numeral, totals line = totals-word + sum numeral;
  50/50 doc split). Pipeline must reach held-out macro-F1 ≥ 0.80 over {W,C,U,T}. FAIL → machinery broken →
  verdict ROLE_INDUCTION_NO_POWER (machinery), stop.
- **LB leg — detector FIRES iff ALL of:**
  (a) held-out (non-KN) macro-F1 ≥ 0.50 over {W,C,U,T};
  (b) held-out macro-F1 > 95th pct of BOTH structure nulls: N1 shuffled-document (permute all tokens within
      doc, rebuild original line lengths; full pipeline refit; 25 reps) and N2 wrong-structure (numerals
      detached and re-inserted at random positions within doc, group order kept; full refit; 25 reps);
  (c) held-out accuracy > 95th pct of N3 label-permutation (1,000 perms of gold labels across held-out
      occurrences, real predictions fixed);
  (d) held-out recall(T) ≥ 0.50 AND recall(C) ≥ 0.50 (role-specific power needed for LA checks).
- **LA leg (only if LB fires):** featurize LA ledger docs (type stats from LA partition), scale with LB
  scaler, assign to LB centroids, frozen mapping → predicted roles. Consistency checks, doc-level
  (Art. VIII: a doc counts once per check; success = majority of its check-token occurrences get the
  predicted role), one-sided binomial vs chance = occurrence-level share of the target role among ALL LA
  group occurrences; Holm over the 4 checks:
  C1 KU-RO → T (primary); C2 known logograms → C (primary; frozen set: single-sign groups whose sign base
  before `+` ∈ {GRA, VIN, CYP, OLIV, OLE, VIR, FIC, TELA, BOS, SUS, CAP, OVIS, AU}; NI deliberately
  EXCLUDED as syllabogram-ambiguous); C3 KI-RO → T (secondary); C4 A-prefix multi-sign words → W (secondary).
  LOSO robustness: folds = HT and pooled-non-HT; requirement = C1 and C2 point estimates > their chance in
  BOTH folds (directional only; no per-fold significance demanded).
- **New-constraint output:** per LA group-type with ≥3 occurrences: modal predicted role + cross-site
  stability → `data/ledger_roles/la_role_constraints.json`. These are PROPOSED L2/L3 constraints; each
  carries its own held-out (cross-site) stability flag; none is claimed beyond L3.

## Mechanical verdict (frozen)

- PC1 fails → **ROLE_INDUCTION_NO_POWER** (machinery).
- LB leg does not fire → **ROLE_INDUCTION_NO_POWER**.
- LB fires; LA: C1 or C2 fails Holm (α=.05) or LOSO directionality fails → **ROLE_INDUCTION_VALIDATED_LB_ONLY**.
- LB fires; C1 AND C2 Holm-survive AND LOSO directional in both folds → **ROLE_INDUCTION_VALIDATED_LB_AND_TRANSFERS**.

## Multiplicity receipt (Art. VII/VIII)

One frozen feature set, one k (5), one seed, one mapping rule — no sweeps. LA checks: 4, Holm-corrected.
No post-hoc feature/threshold changes; any deviation is logged in result.json as a deviation entry.

## Assumptions (Art. XVIII)

A1: DAMOS editorial case reliably separates syllabic words from logograms for GOLD labels (grading only).
A2: within-partition type-stats are unlabeled-structure transduction, not label leakage.
A3: doc-level binomial chance = occurrence-level role share (approximation; conservative direction not
guaranteed — flagged, and per-check chance rates reported so the reader can recompute).
A4: LA `stream` segmentation (GORILA word divisions) is trusted at L1/L2.
