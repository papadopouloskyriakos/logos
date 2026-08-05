# 2026-08-05 — Full audit of Tsirkas's corpus-validation repo + paper

**Subject:** `github.com/ChristosTsirkas/corpus-validation-for-undeciphered-scripts-linear-a`
("Auditing the Unread", Zenodo DOI 10.5281/zenodo.21809415, v0.9.a, 2026-08-05; clone
audited at commit `d5d1e5b`). Follows up `docs/2026-08-05-ab21-ab22-external-audit.md`
(his D4, confirmed there). Method: three parallel audit passes (copy-forensics,
methodology/results, engineering practices) + six adversarial verification agents
re-deriving every load-bearing claim from scratch. articles_triggered: XI (source
dependency — new defect on our lineage), XVII (append-only record — this doc),
VIII/IX context (type counts feed effective_n/info-budget). No repo code changed by
this audit; documentation only.

---

## 1. Copying verdict: INDEPENDENT (re-verified adversarially, high confidence)

Owner's question: "did he steal my repo / my paper?" **No — for the third time, now
with mechanical evidence**, hunted adversarially in both directions:

- **Vocabulary fingerprint:** zero hits for 14+ logos-distinctive terms (`effective_n`,
  `plan_hash`, `L_not_indexed`, `L_fake`, transfer licence, claim layer, deflated,
  Clopper, agora, `21119213`, papadopoulos, …) across his working tree, the paper
  .docx XML parts, the PDF text layer, and **every blob in his git history**.
- **SigLA decoder** (the one place both repos independently solved the same problem —
  OCaml `Marshal` decoding of `database.js`): AST identifier intersection = `__init__`
  only; shared content is format-dictated (magic `0x8495A6BE`, tag/size header split,
  sharing-table semantics per OCaml `intext.h`). Architectures, unescaping algorithms,
  and extracted fields all differ — *complementarily* (his: reading-certainty, erasures,
  boundary tri-state; ours: bboxes, dividers, dimensions). His misses PH 31a/b handling
  that ours has; a copy would not under-shoot its source.
- **Paper text:** 0 shared 8-grams and 0 shared 7-grams between his 16,674-word paper
  and `paper/tacl/body.tex` (bibliography strings excluded); longest echo is one
  generic 6-gram.
- **Results:** intersection of the two projects' result sets is empty apart from facts
  forced by the shared public sources (802 SigLA docs / 5,144 attestations).
- **Strongest independence proof:** his headline findings are defects **in our own
  lineage that we did not know about** (D4 confirmed 2026-08-05; D1 confirmed below).

Recorded caveats (do not overstate the verdict): his public history is a single
squashed "copy-over from private repo" commit (2026-08-05), so timeline independence
is unverifiable from git; and one docstring parallel exists ("ships its corpus as two
OCaml Marshal blobs" — ours public since 2026-07-06, his phrasing near-identical; it
states an objective fact and the code beneath it is architecturally independent, but
exposure to our public repo cannot be mechanically excluded). *Conceptual* awareness
of logos ≠ derivation; no logos apparatus appears anywhere in his work.

## 2. NEW DEFECT — Tsirkas D1 CONFIRMED on our silver (damage markers / phantom types)

His D1: the lineara.xyz lineage strips **word-attached** damage notation from the
`transliteratedWords` layer; the marker is `U+1076B` (an *unassigned* codepoint in the
Unicode Linear A block, used by the Douros encoding as the break/lacuna marker).
Verified mechanically on our own bronze/silver (no files modified):

- Bronze (`/tmp/lineara/items_analysis/inscriptions.json`, 1,720 entries): `words`
  layer carries **2,170** marker occurrences; `transliteratedWords` only **588**, of
  which 552 are standalone lacuna tokens and 31 sit on fraction glyphs — **zero**
  attached to a latin word token. So `]WORD`, `WORD[`, and internal breaks are gone
  from exactly the layer `scripts/corpus_io.py:48` and
  `scripts/corpus_io_structured.py:65` ingest.
- Silver carries **no damage/completeness field** in either file. Nuances: the
  structured `stream` incidentally preserves 474 *standalone* lacuna markers as
  untyped `{"t":"other"}` tokens (between-word lacunae partially recoverable);
  word-attached damage is unrecoverable from any silver layer. 15 distinct sign labels
  leak ASCII brackets (5 genuine break notation: `]TU+RO`, `]MI+JA`, `TE+RO[`,
  `RO+RO[`, `WI+ZE[`; the rest ligature-uncertainty like `VIR+[?]`).
- **Measured on our 1,341 silver docs** (1:1 positional alignment of the two bronze
  layers, valid 1,719/1,720): **911 of 3,147 word tokens (28.9%) are damage-touching**;
  of 1,165 distinct word types, **359 (30.8%) are phantom types** — attested *only*
  damaged, never complete (1,165 → 806 if excluded). Same magnitude as his corpus
  (30.0%), different exact numbers (different record model), as independence predicts.

**Disposition (D4 precedent applies):** no silver rebuild without an explicit owner
decision; divergence-register-style default. Published-results exposure is
**unquantified but plausibly low** for the frozen paper (nulls get *more* null with
fewer real types; the segmentation gap is within-corpus with site-clustered CI) —
however **any type-count-sensitive figure (distinct-type counts, packed-word counts,
unicity/effective-n panels) must be re-checked under a phantom-type exclusion before
being reused in new claims.** Concrete follow-up: a scripted
`scripts/audit_damage_markers.py` mirroring `scripts/audit_ab21_ab22.py` (the
verification agent's measurement procedure above is the spec). Credit: Tsirkas D1.

## 3. Contradiction check vs published logos results: NONE

- **Segmentation:** his "Methods precluded" table row ("Morphological segmentation
  (Morfessor, BPE, etc.): No") is **scope-different, not contradictory**: it targets
  morpheme-level lexicon segmentation — where we agree (our Morfessor probe: 0.156,
  not usable; morphology NO-POWER) — while our published 0.436 vs 0.389 positive is
  scribe-word-boundary recovery (L2). His row is overbroad *as written* (his own
  §13.2 restatement, "segment the lexicon morphologically", is the defensible form);
  symmetric duty: our 0.436 must never be quoted as "segmentation is supported"
  without its 0.577 all-boundaries-ceiling caveat.
- **Affixation (his z=+5.91/+6.74) vs our morphology NO-POWER:** no conflict. His
  null (per-sign resampling from P(sign|length,position), `src/grid_null.py`)
  destroys all bigram/recurrence structure — strictly easier to beat than our
  operative floor (max of within-word shuffle and bigram-calibrated L_fake + ≥2-stem
  productivity gate + deflation). His result = "edge structure exceeds positional-
  unigram chance" (L2; could even be mere bigram phonotactics); our result = that
  structure does not clear the bigram floor. Both are true; his paper's own scoping
  ("real, but directionless") concedes the gap.
- **Phonology, entropy/adequacy:** convergent with our data-limited null and
  information-floor position; his vowel-harmony ≥0.10 exclusion and below-chance
  minimal-pair result are *additive* bounds we never computed.

## 4. Convergences — wording discipline for any public statement

Three real convergences, none quotable as "independent replication of a logos
published finding" (Art. XI: same lineara.xyz+Younger lineage ⇒ *independent
reanalysis on the same underlying corpus*, never independent evidence; and none of
the three is in the frozen paper):

1. **AB008/A-initial positional skew** — his BH-corrected `validate_final.py` finds
   AB008 initial 71/76 (~24.4 expected); independently *declines the affix reading*,
   as our E103R rename did. His deflation rationale differs (positive orthographic-
   phonotactic explanation premised on AB008=/a/, an L6-flavoured premise our licence
   terms forbid us to assert). Fair wording: "independent confirmation of the same
   positional signal, with a convergent refusal to count it as affix evidence, via
   different rationales."
2. **Libation-formula slot order** — identical five slots, identical order, 10/10
   pairwise constraints, zero inversions; his adds D9 dual-reading invariance (we
   never established that); ours adds the adaptive-null honest p=0.030 + borderline
   held-out seal transfer. Both re-derive **Younger's** published schema — credit his
   priority in any statement.
3. **KU-RO summation** — his own-total-vs-shuffled null (10/26 exact, z=+13.40;
   KI-RO 0/7 raw contrast) mechanically validates the KU-RO-as-total *premise* our
   paper cites as general knowledge (Appendix B.1 constraint, C.1 witness exclusion)
   and is stronger than our unpublished E2 corroboration (7/31). Not a logos finding;
   do not claim it as one. Verifier caveats: his z is protected by the shuffle only
   against chance value-coincidence, not sectioning-rule circularity (rule developed
   on the same data; risk modest — small epigraphically-motivated rule family, the
   discretionary axis ablated); KI-RO never gets its own null; z=+13.4 Gaussianizes a
   near-Poisson null (defensible statement: permutation p ≤ ~5e-4).

**Genuinely novel to us (citable):** the Packard 1974 replication — both halves — and
its field-facing point that the circulating "2:1" is Packard's *weak* strand
(alternations 1.55:1, p=0.17) while the Knossos-restricted name-parallel strand
(4.74:1, z=+4.34, p=0.0020) is what carries his conclusion. Unexamined Art. XII
exposure noted: ~52% of the value table is shape-analogy-assumed, and some
conventional values were historically consolidated partly because they make Cretan
names legible — the test partially grades the assignment by evidence that helped
create it (Packard's original shares this).

## 5. Adoptable improvements (ranked; none implemented in this commit)

1. **Licensing-hygiene tests** — assert corpus data is *untracked by git*
   (`git ls-files`), not merely gitignored, + `git check-ignore` coverage of generated
   paths. ~1 h. Closes the worst public-mirror exposure (our `git add -f` habit).
2. **Checksum-pinned silver + verify script** — md5+sha256 + record-count invariants
   for every silver artifact, single-sourced in one JSON (avoid his quadruplicated-pin
   drift), verify script prints the producing command for anything missing. ~1 day.
   Makes "no silver rebuild without an explicit decision" mechanically enforceable.
3. **One-command reproduce chain** — fetch script (sparse checkout of lineara.xyz,
   only the paths the normaliser reads) + `make silver` + `make reproduce-paper`. 1–2 d.
4. **D1 scripted audit** (`scripts/audit_damage_markers.py`, §2 above) + optional
   damage fields in a future silver schema (owner decision).
5. **Standing divergence register** — `corpus/divergences.json` in his machine-readable
   form (reading, sources, conflict kind, adjudicating evidence, sensitive analyses,
   status); D4+D1+HT38 are its first three entries. Serves Art. XI/XVII directly.
6. **AI_DISCLOSURE.md** — owner-sensitive; his disclosure demonstrably bought
   credibility (it is why our first audit trusted his repo quickly). Draft for owner
   review, never commit unilaterally.
7. **Stale public claims fix** — README.md:60 *and* :100 still say "under review at
   TACL" (publicly false since 2026-07-29); CITATION.cff:15 carries a leftover
   `# TODO: add your ORCID` comment. Wording = owner sign-off (submission-discipline
   adjacent).
8. **Dated "last verified rebuild" README section** — script-generated (invariant #12;
   his hand-written version drifted into self-contradiction: three dates, two hashes,
   four files).
9. **Skip-on-drift test semantics** — one corpus-checksum check, published-figure
   tests skip with explanation when upstream moved; **hard-fail** on the pinned
   snapshot (do not copy his warn-only `soft_check`).
10. **CI on the unit lane** (neither repo has CI; `make test-unit` already passes on a
    bare checkout) · license-notice-on-fetch prints · compliance checklist + data→results
    table in `docs/data-provenance.md` · reading-certainty fields added to our
    `sigla_decode.py` output · his affix-direction power-injection pattern for any
    future directional claim · a KU-RO own-total null replicated on silver to harden
    the Appendix-C exclusion argument in any new-venue build.

**Do NOT adopt:** self-modifying test baselines (his `verify.sh` sed-rewrites the
pinned hash in the test file — Art. XVII violation class, and it already bit him);
warn-only published-figure assertions; PolyForm Shield licensing (contradicts
invariant 10 / MIT-open-by-default); hand-written counts; his unpinned upstream HEAD
fetch (pin the commit).

## 6. Feedback owed to him (GitHub, the established channel; drafts only on owner ask)

- PH 31a/b **are** in SigLA's `database.js` (our decode has them); his D4 register
  marks them "absent from SigLA entirely" — a correction he'd want.
- His precluded-methods segmentation row is overbroad as written (§3); suggest his
  own §13.2 wording.
- Mutual-citation exchange remains open: his paper doesn't cite our preprint; our
  audit docs already credit his D4 (now D1).

**Compliance line:** Art. XI (defect recorded against source lineage), Art. XVII
(append-only; this doc supersedes nothing), Art. XXII (stage header above). No
verdict-path code touched; no silver rebuilt; counts in §2 are script-derived by the
verification agent's procedure (to be frozen into `scripts/audit_damage_markers.py`).
