# Egyptian foreign-form calibration corpus — audit (REQ-02) and BLOCKER finding

## REQ-02 source audit
- **Edition:** Hoch, J.E. 1994, *Semitic Words in Egyptian Texts of the New Kingdom and Third
  Intermediate Period* (Princeton). Local scan `hoch1994_semitic-words-in-egyptian-texts.pdf`,
  594 pp, sha `4df9bc09…`. Copyright Princeton UP; stored local-only, derived records only.
- **Content:** ~500 Semitic words/names/loanwords in Egyptian "group writing" (syllabic orthography),
  each entry: Egyptian group-writing + proposed Semitic cognate + meaning + refs. Names, toponyms,
  loanwords ARE distinguishable in the text (`n. loc.`, `PN`, glosses).

## BLOCKER — the PDF text layer does not preserve the transliteration to a fittable standard
The specialized transliteration that carries the phonological information is **corrupted** by the PDF
text extraction:
- Egyptian group-writing diacritics mangled: aleph ꜣ → `—`, ayin ꜥ → `c`, š → `$`, emphatics lost;
  group boundaries survive only as `=` (e.g. `sa=ca=ra` "gate", `h=—r=ya` "dung", `n=k-fi=ta={r}
  nikiptu`, `Ti 2 =ku=ru 2 B=c-—r`).
- Semitic source forms (Hebrew/Ugaritic/Akkadian script + transliteration) render as garbage
  (`3K`, `TA`, `B=c-—r`).
- Result: the **segment-level Egyptian-group ↔ Semitic-consonant correspondences** — the exact pairs
  a correspondence model is fit on — cannot be recovered reliably. Auto-parsing them would be the
  "unverified scraped snippets" this pass explicitly forbids, and would **bake OCR noise into the
  correspondence probabilities**, corrupting the very false-positive calibration the gate depends on.
- **No machine-readable alternative exists:** confirmed by web audit — Hoch 1994 is print/PDF only;
  no released TSV/dataset; no Schneider (or other) machine-readable Egyptian group-writing
  correspondence database was found. (An OAPEN "Vocalization in Group Writing" item exists but is a
  monograph on vocalization, not a correspondence table.)

## Consequence
A **verified** Egyptian→foreign calibration corpus (Task B) cannot be built from the available
material to the standard required (per-record `source_form_confidence`, `egyptian_reading_confidence`,
segment alignment). Therefore the frozen correspondence model (Task C), the matched-scarcity positive
control under an empirical model (Task E), the enabled null families (Task F), and the calibrated
power envelope (Task H) **cannot be executed to standard in this pass**. This is a
data/implementation blocker → the gate is **not evaluable** → **INCOMPLETE**, not NO_POWER.

## What would unblock it (smallest sufficient input)
Any ONE of: (1) a machine-readable Hoch dataset (structured Egyptian group-writing ↔ Semitic form
table); (2) a curated, source-cited cognate list with clean transliteration (e.g. digitized from
Hoch's numbered entries or Schneider's loanword corpus); (3) a hand-verified high-confidence subset
(≥ ~150 entries) extracted with a transliteration-aware OCR pass and checked — large enough to fit a
non-degenerate model (a smaller subset would itself be NO_POWER for calibration). See
`MATERIAL_REQUESTS.md` (REQ-02b).

## UPDATE 2026-07-06 — BLOCKER LIFTED by open research
Extensive web research found usable open sources, changing the verdict from *blocked* to
*unblocked-pending-fit*:
- **Kilani 2019, *Vocalisation in Group Writing*** — **CC-BY 4.0**, born-digital, CLEAN text layer
  (161 pp, 322k chars), with **explicit group-writing→sound correspondences** (`/a/=A>ⲟ`,
  `/i:/,/u:/=A>ⲏ` …), Appendix A corpus, a group index with variants, and Onomasticon-of-Amenope
  name attestations. This is a **machine-parseable Egyptian group-writing→value model** — the core
  correspondence layer — and CC-BY means **derived correspondence records may be committed**.
  Downloaded (`kilani2019_…pdf`, checksummed). **This supersedes the Hoch-OCR blocker for the sign→
  sound layer.**
- **TLA Late Egyptian v19 (Hugging Face)** — CC-BY-SA-4.0, ungated, `train.jsonl` — machine-readable
  Egyptian lexical/text corpus for the Egyptian side (not yet fetched).
- **Kitchen, NK Topographical Lists** (open) — context for the foreign-toponym-list collation (also
  informs the REQ-01 primary-edition gap).
- **Muchiki 1999** (foreign proper names + loanwords in NW Semitic) — the **foreign-approximation**
  layer (names/toponyms specifically); print/paywalled → `MATERIAL_REQUESTS` REQ-02c (optional
  strengthening; Kilani alone suffices for a first model).

**Caveat:** Kilani calibrates the group-writing→sound layer from *native* Egyptian words (via Coptic);
the *foreign-consonant-approximation* layer (how Egyptian rendered non-Egyptian sounds) is best
strengthened by Muchiki/Hoch. A first correspondence model can be fit from Kilani now; the foreign
layer is a documented approximation until Muchiki lands. → **Calibration is no longer data-blocked.**
