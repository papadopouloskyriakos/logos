# EPOCH-001 prereg — Ariadne-2025 Anetaki source acquisition (frontier F8/F1)

- **epoch_id:** EPOCH-001
- **campaign:** research/linear-a-frontier-72h
- **date frozen:** 2026-07-08 (before any external search of this epoch ran)
- **seed:** 20260708
- **constitution:** v2.2
- **articles_triggered:** VII (search receipt), IX (info budget), XI (source-dependency),
  XII (no grading a target by the rule that created it), XV (licence gate — acquisition only,
  no licence claimed), XVII (append-only), XVIII (assumptions), XXII (stage header)
- **claim layer:** **L0/L1 only** (physical carriers + sign identification *as printed by
  editors*). NO structural, semantic, or phonetic claim is made or scored in this epoch.
  This is a SUPPLY/ACQUISITION epoch: it measures what is public, not what is true.

## Question to resolve (exact)

Two prior findings appear to conflict:
- anchor-lattice K (2026-07-08): "Anetaki ivory scepter (~119 signs) is published
  (Kanta/Nakassis/Palaima/Perna, Ariadne Supplements) and NOT in the silver corpus."
- di-mino J1 + anchor-lattice M (2026-07-08): "no complete transliteration is public;
  editio princeps (*Anetaki II*) unpublished."

Resolve precisely; acquire whatever IS public as of 2026-07-08; quantify the genuinely-new
information vs `corpus/silver`; quarantine everything under
`experiments/linear_a_frontier_72h/data/anetaki_2025/`; never touch `corpus/silver`.

## Prior state already on disk (derivation set, known before this epoch)

1. `corpus/bronze/kanta_etal_2024_anetaki/` — Kanta, Nakassis, Palaima & Perna 2024,
   Ariadne Suppl. 5, pp. 27–43 (DOI 10.26248/ariadne.vi.1841; CC BY-NC-SA 4.0; SHA-256
   87dad27b…57d2 + frontmatter variant bc50adba…69bb). Editor-printed content already
   extracted at `experiments/crossscript_gate/phase3/anetaki_extraction.md`;
   GAP verdict `PENDING-FULL-EDITION` (`GAP_DELTA.md`).
2. `corpus/bronze/delfreo_rapport_koronowesa/` — Del Freo, Rapport 2016-2021 (same volume,
   pp. 87–124, DOI 10.26248/ariadne.vi.1843): KN Zg 57 (ivory ring) + KN Zg 58 (ivory bar)
   both **inédit**, no readings printed (rapport pp. 99–100).
3. `corpus/bronze/rjabchikov_2025_sceptre/` — fringe photo-based readings, QUARANTINED
   (litindex claim_type `fringe_sceptre_reading`); registry object, not evidence.
4. `corpus/bronze/prepub_prediction_2024_ivory_circle/` — Chiapello 2024 prediction,
   registry object, no readings.
5. `corpus/silver`: `KNZg55` (JA-SA-JA steatite disk seal — an OLDER, different object) and
   `KNZg57a` (ivory object; signs *401+RU, *401+RU, *418+L2, NI, VAS + lacunae) — i.e. the
   lineara.xyz-derived silver ALREADY carries a partial preliminary reading under the id
   KN Zg 57a. Provenance of that reading = lineara.xyz bronze; ultimate source TO BE
   ESTABLISHED this epoch.
6. Known numbering collision to resolve: Younger's misctexts assigns **KN Zg 58** to an OLD
   steatite amygdaloid (HM 843; CMS II 3 no. 23) while Del Freo/Kanta assign KN Zg 58 to the
   NEW ivory bar; Younger lists the ring as unnumbered "KN Zh no no."; KN Zg 56 is absent
   from every holding.
7. Frozen prospective seals that TARGET this material (contamination boundary, Art. XII):
   - `ANETAKI_FINAL_EDITION_DELTA_SEAL` (relative-phonology campaign; plan_hash
     979e2fd2…85f6; SEALED_PROSPECTIVE; structural-only; excludes all J1-public items).
   - `M_ANETAKI_LATTICE_DELTA_SEAL` (anchor-lattice M; SEALED_PROSPECTIVE; MP1 A-only token
     fraction, MP2 anchor-delta darkness, MP3 conditional substitution non-rescue).

## Frozen plan (procedures; run exactly these, report all)

P1. **Search sweep** (Art. VII receipt; every query logged, negatives included) — routes:
    (a) Ariadne Suppl. 5 TOC (ejournals.lib.uoc.gr issue 178) for any OTHER Anetaki item;
    (b) *Anetaki II* publication status 2025–2026 (Kanta ed., INSTAP Academic Press /
        announcements); (c) Kadmos 2023–2026 Kanta edition; (d) academia.edu Kanta/Perna/
        Nakassis/Palaima 2025–26 Anetaki items; (e) Zenodo; (f) Aegeus society new-books/
        news; (g) BMCR review of KO-RO-NO-WE-SA; (h) "KN Zg 56" identity; (i) SigLA /
        lineara.xyz ingestion re-check; (j) media wave 2025 (already known: GreekReporter
        etc.) only for pointers to scholarly sources, never as reading sources.
P2. **Dedup editions** into `data/anetaki_2025/editions.json` (one row per distinct edition/
    witness; licensing + accessibility + what it prints).
P3. **Verify load-bearing readings** against the on-disk PDFs (page-level; the Kanta et al.
    epigraphy section pp. 34–42 re-read directly, spot-checking the phase3 extraction).
P4. **Extract machine-readable candidates** — `data/anetaki_2025/sign_candidates.json`:
    every editor-printed sign/ligature/logogram with {carrier, face, provenance page,
    editor-status, confidence, quarantine flags}. Fringe (Rjabchikov) readings included
    ONLY under `quarantine: fringe`, never merged with editor rows. Silver KNZg57a signs
    recorded as `preliminary_lineara_xyz` witness.
P5. **Delta measurement** vs silver (`scripts/anetaki_delta.py`, mechanical): new sign
    types? new *301 contexts? new A-only occurrences? new formula slots? counts only from
    script output (Invariant 12).
P6. **Quarantine + contamination boundary** — `data/anetaki_2025/CONTAMINATION_BOUNDARY.md`:
    what here is J1-public (seal-EXCLUDED) vs what would be seal-scoreable; hand any scoring
    decision to the orchestrator. This epoch does NOT open either seal.
P7. Verdict is MECHANICAL from the artifacts (see below).

## Committed verdict rules (fail closed)

- `RESOLVED_PUBLISHED_PARTIAL` iff: (i) the K-vs-J1 conflict is explained with page-level
  citations, AND (ii) ≥1 open-licensed edition witness exists on disk, AND (iii) the
  machine-readable candidate extraction is non-empty but contains **no transliterated
  multi-sign phonetic sequence** beyond what silver already holds.
- `RESOLVED_PUBLISHED_FULL` iff a complete editor transliteration of KN Zg 57/58 is found
  public (this triggers the seal-contamination protocol: STOP, record boundary, hand to
  orchestrator — do NOT score).
- `SOURCE_BLOCKED` iff neither of the above (specific blocker recorded).
- Any seal-scoreable content acquired ⇒ flag `SEAL_SCOREABLE_CONTENT_ACQUIRED=true` and NO
  scoring in this epoch regardless of verdict.

## Controls

- **Positive control (P3):** the phase3 extraction's load-bearing items must reproduce from
  the PDF read (e.g. "no phonetic sign groups on Face A" p. 39 wording; ~119 signs p. 40;
  fn. 7 GORILA numbering). Failure ⇒ extraction unreliable ⇒ redo extraction before any use.
- **Negative control (P4):** Rjabchikov fringe readings must NOT appear in any
  non-quarantined candidate row (mechanical check in the delta script).
- **Search breadth:** all P1 routes run even after an early hit; negatives reported.

## Multiplicity / information budget

No statistical claim is made; no hypothesis is graded. The only numbers are counts from P5
(descriptive, script-generated). Information-budget effect: 0 new value-bearing bits
expected (K epoch already bounds Anetaki delta at 0 absolute anchor bits); the commodity
acquired is held-out test power, which must remain UNCONSUMED (quarantine).

## Assumptions (Art. XVIII)

- A-1: ejournals.lib.uoc.gr licence statement (CC BY-NC-SA 4.0) continues to apply to
  issue-178 articles. Basis: article_page.html capture 2026-07-03.
- A-2: Del Freo's rapport + Kanta et al. 2024 are the authoritative carrier numbering
  (KN Zg 57 = ring, KN Zg 58 = bar); Younger's old "Zg 58" steatite is a superseded/
  colliding use to be recorded, not resolved by us.
- A-3: lineara.xyz's KNZg57a preliminary signs are treated as witness `preliminary_
  lineara_xyz` with confidence ≤ 0.5 unless its ultimate published source is identified.
