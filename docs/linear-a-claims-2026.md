# Linear A decipherment claims — 2026 (the trigger for logos)

logos was started in direct response to the June 2026 "Linear A cracked" claim. This note
records the claim, the method, why it is **not yet valid**, and the logos stance. It is the
reference for the README's "deliberate opposite" framing.

## The claim (Tom Di Mino, June 2026)

- **Author:** Tom Di Mino — AI/ML engineer (ex-Google UX, Chan Zuckerberg Initiative, JP
  Morgan Chase; now at Subquadratic), reading knowledge of 8 languages incl. Ugaritic (a
  Semitic script). *Not* an uninformed crank — a capable person with serious linguistic
  grounding. [github](https://github.com/tdimino).
- **Claim:** Linear A records an **extinct Semitic language**, a precursor to Biblical
  Hebrew/Arabic/Aramaic (as Latin is to Italian). This **revives Cyrus H. Gordon's 1957
  Semitic hypothesis** (*Antiquity*), which never gained acceptance.
- **The anchor:** the recurring **Libation Formula** across **5 peak-sanctuary sites** on
  Crete. All words "known" via Linear-B sign overlap except the first — a verb root whose
  5 known signs + the Linear-A-only `*301` + `na` he reads as **N-W-Y "to dwell"**
  (*nawaya*), then matches the prayer to later Hebrew liturgy addressed to a Goddess.
- **Tooling:** Python scripts via **Claude Code** over the **GORILA + SigLA** corpora;
  reportedly ~**100k simulations** scoring "Semitic signal vs luck," with a probability per
  proposed sound-value.
- **Claimed artifacts:** readings for **40 signs** (13 previously-unknown + 5 unsolved
  Linear-B signs), a **408-word English lexicon**, a 9-page draft ***Ya Diktu: Grammar of
  the Minoan Peak Sanctuary Libation Formula***.
- **Sources:** [aiclambake post](https://aiclambake.com/clamtakes/linear-a/) (friend-authored,
  2026-06-16) · [HN 48600107](https://news.ycombinator.com/item?id=48600107).

## Why it is NOT (yet) valid

1. **Not public / not reproducible.** No code, no lexicon table, no simulation methodology,
   no manuscript, no preprint. GitHub profile + a presentation site exist, but the
   decipherment artifacts are withheld. The "reviewed by Rutgers and Cambridge" claim is
   **unconfirmed** — no independent announcement from either; likely individual emails.
2. **The anchor refutes itself — a three-part takedown of `*301`=/na/→"dwell".** (Upgraded
   2026-07-01 with Di Mino's own published table + the now-acquired Salgarella 2025 body.)
   - **(a) The segmentation is not novel.** Root `i-*301` + affixation is the mainstream **Davis
     2013 / Thomas 2020** reading; the multi-attestation forms `ta-na-i-*301-u-ti-nu` (IO Za 6) and
     `a-ta-i-*301-de-ka` (ZA Zb 3) prove the affix-stacking. Di Mino re-segments a known structure.
   - **(b) The gloss is contested and weaker.** The mainstream value is **"give/dedicate"** (Brent
     Davis, *Kadmos* 52, 2013 + *Minoan Stone Vessels*, Aegaeum 36, 2014; **endorsed by the current
     synthesis Salgarella 2025 §7.2** as a *structural* reading that assigns `*301` **no phonetic
     value**); "dwell" (N-W-Y) is a semantically distant, unmotivated leap. *Attribution discipline:*
     this counter is **Davis's** — **do NOT re-attribute it to Steele 2024** (the Steele-2024 item in
     hand is O. Dickinson's book review, no `*301` content).
   - **(c) The morphology contradicts the assigned language family (strongest, and now corroborated).**
     Di Mino's own table draws a *concatenative, prefix-stacking, **agglutinative*** verb
     ([prefix `A` "I"][stem-morpheme `TA`][stem-vowel `I`][root `*301`]). Semitic morphology is
     **non-concatenative** (root-and-pattern). A prefix-stacked agglutinative verb is the **opposite**
     of Semitic — the claim is internally incoherent **from his own figure**, no give-vs-dwell
     adjudication required. And **Salgarella 2025 §8 (verified)** independently concludes Minoan **is
     agglutinative** (Duhoux 1978) and a language **isolate** — so his own segmentation corroborates
     the isolate typology and refutes his Semitic label.
   - **Quarantine receipt.** In his own table `*301`'s AB-number column is "—" and Linear B "(none)":
     the single sign the whole decipherment pivots on has **no cross-script anchor** — its value was
     assigned to fit the desired root. The textbook free-parameter case the MDL gate (`k ≤ U_floor`)
     refuses. Locked into `litindex.py` CITATION_DIMINO + `prereg-morphology-salgarella-addendum`.
3. **The match is partial.** A-TA-I-`*301`-WA-JA → keeping only W-J and *guessing* `*301`
   starts with N yields N-W-Y: roughly **1/5 of one word matched to 2/3 of a root**, with
   A-TA-I unexplained (and possibly the root should be N-W-H / נוה).
4. **Tiny-corpus cherry-picking.** The "English is a Semitic language" HN demo shows you can
   match baker/brought/bushel/mill to Proto-Semitic roots and "translate" any sentence. The
   "408 words" has **no published table** to audit. This is the multiple-testing disease.
5. **Typological oddness.** Semitic languages use consonantal roots (abjad); why would
   Linear A be a consonant+vowel **syllabary that writes vowels**?
6. **The information floor — measured, and it refutes the "too little text" argument.** On
   the real corpus (1,341 inscriptions, 5,792 syllable-signs, V=259), `scripts/corpus_info.py`
   gives **unicity distance U ≈ 204–415 ≪ N = 5,792** across the whole plausible (V, P) space.
   By Shannon's criterion there IS enough text to uniquely pin a decipherment — so corpus
   size is **not** the blocker (this corrects a claim made below this very thread and our own
   earlier prior). The real obstacles are the **absence of a known cognate language** to map
   to (Luo's limit), the **multiple-testing / search trap** (point 4), and a **mixed
   inventory**. Internal consistency is still not evidence. Full analysis + sensitivity:
   [docs/findings/2026-06-30-information-floor.md](findings/2026-06-30-information-floor.md).

## The logos stance

- logos is the **deliberate opposite**: open by default, mechanically verdicted, deflated for
  multiple testing, no claim of "cracked" without held-out verification.
- The Semitic/Gordon reading enters as **one capped hypothesis family** (≤0.75) among
  several (Anatolian, Tyrrenian, IE, isolate), graded head-to-head — never as ground truth.
  **Quarantine, not dismiss:** the older etymological ranking (**Schoep 2002**, via Braović 2024
  p. 734) put Semitic + Lycian among the best-founded, so logos *indexes* the reading rather than
  calling it "crank." But the **current synthesis goes further: Salgarella 2025 §8 (verified) concludes
  Minoan is a language ISOLATE** — "does not belong in any known language family" (IE/Semitic/
  Afro-Asiatic among those compared) — and rejects the whole etymological/vocabulary-comparison method
  ("not probative"; loanwords confound). So logos's **`family_scores` prior treats ISOLATE as the
  benchmark-favored hypothesis**; Semitic/Anatolian/IE/Tyrrhenian/Hurrian/Hattic are
  catalogued-but-unfounded, graded as capped families, none endorsed. Typology prior (deterministic):
  Minoan is **agglutinative** (Duhoux 1978) + provisional **VSO** (Davis 2013) — any reading implying
  non-concatenative Semitic or fusional-IE inflection is penalized as contra-benchmark.
- The Libation Formula's recurrence across **5 sites is a natural 5-fold held-out CV**: a
  hypothesis derived on N sites must mechanically read the held-out site(s). The claim's own
  structure invites this test; it has not publicly passed it. **Caveat (Salgarella & Judson 2024):
  site-level CV is necessary but NOT sufficient** — within-site scribal-hand correlation (the Hand
  103/115 idiolect artifact) must also be controlled before a held-out read counts as independent
  (see `prereg-morphology-stratification-addendum-2026-06-30.md`).
- **The 2025 loanword worked example as Di Mino's methodological counter-model.** Salgarella,
  Bellinato & Ferrara (2025, *Kadmos* 64) read spice signs by graphic + contextual + comparative
  triangulation *with explicit competing-option hedging* (three KA+PO values; a single hapax flagged
  as such) — the opposite of a single forced match. Caveat: their A646/pi step is itself
  LB-value backward-projection, so the distinction logos draws is **grounding-quality, not "they
  never backward-project"** (engage Steele & Meissner 2017 on the symmetry). These readings are now
  indexed L_known in `litindex.py` so a model cannot regurgitate them as discovery.
- **Two named failure modes for the methods paper** (Di Mino is generating clean public contrast
  cases): **(i) Narrative capture** — his table's *structure* says agglutinative/prefixing but the
  *label* says Semitic, and the label wins because the desired output is a fixed prior ("prayers to a
  Goddess in a matriarchal society"); conclusions conform to a prior rather than emerging from
  constrained readings. This is **distinct from statistical overfitting** — name it separately.
  **(ii) Free parameters > information floor** — the lexicon is "408 terms / 400 words and counting"
  on a fixed ~7,400-sign corpus; a decipherment whose lexicon *grows weekly* has more degrees of
  freedom than the data can identify. The worked example the MDL/unicity gate (point 6) is built to
  catch.
- **Reception discipline (framing, not code).** The substantive correct objections to Di Mino came
  from amateurs; defenders retreated to "under review at Rutgers and Cambridge" with no name, table,
  or preprint. So: **logos never makes an "under review at X" claim without a named reviewer**; when
  logos ships it **leads with the artifact** (corpus + harness + null + tables), claim last — directly
  answering the most-repeated unanswered public demand ("where is the table / the preprint?"). Di Mino
  has publicly committed to the **inverted pipeline** ("officially deciphered" → vet later); logos's
  **prereg → held-out → locked-artifact** sequence is the documented inverse — cite as the contrast.
- **Corpus-size reconciliation (document before quoting a count).** Di Mino states ~1,753 digitized
  inscriptions + ~50 in a French GORILA supplement; Salgarella 2025 §1–3 gives ~1,400 readable of
  ~2,500 total finds, ~7,400 sign occurrences, 56 findplaces; logos's working figure is ~1,427–1,527
  (Petrolito/Salgarella). These count **different strata** (readable vs all finds vs post-1985
  supplement). Any paper figure must state its basis; the **information-floor denominator is ~7,400
  sign occurrences**, not the document count (invariant 7, 12).
- logos will **reproduce the Luo 2019 null** (a neural decipherer fails on Linear A without a
  known cognate) as a baseline milestone — the empirical confirmation of point 6.

## Anetaki sceptre (KN Zg 57/58) claims registry

Two documents about the Anetaki-plot ivory sceptre (KN Zg 57 ring + KN Zg 58 handle, Knossos
Cult Center — see `corpus/bronze/kanta_etal_2024_anetaki/PROVENANCE.md`). Both are **REGISTRY
OBJECTS, never evidence about Linear A**: no sign is read from any photograph, and nothing
below enters the corpus or any signal path except as quarantine rows. Both become
mechanically gradable the day the official edition (Kanta (ed.), *Anetaki II*, forthcoming)
publishes its transliteration.

### Rjabchikov 2025 — fringe "decipherment" of KN Zg 57/58 (fringe_flag=true)

- **fringe_flag: true.**
- **Work (verified 2026-07-03 from the publisher's own open proceedings PDF):** Sergei V.
  Rjabchikov, "The Decipherment of two Records of Linear A on the Ivory Mirror from Knossos,
  Crete", in Ivanovskaya & Kuzmina (eds.), *Tendentsii i problemy razvitiya sovremennoy
  nauki* (IV Int. sci.-pract. conf., Petrozavodsk, 2025-08-18), MTsNP "Novaya Nauka", pp.
  100–106 (volume ISBN 978-5-00215-841-6). The article names **KN Zg 57 + KN Zg 58**
  explicitly and cites Kanta et al. 2024 as its only source for the object (his ref. [3]);
  he reinterprets the sceptre as a priestess's **mirror** and translates both texts as a
  bull-cult liturgy. Archived: `corpus/bronze/rjabchikov_2025_sceptre/` (gitignored; SHA-256
  `b4ce36798ad0271c86509a2c8ff54cefe52194131f0a51ee2fd2e06864c40437` + PROVENANCE.md; entry
  in `docs/related/_acquisition.md`).
- **(i) The readings predate any official transliteration** — Kanta et al. 2024 prints NO
  transliterated sequences and *Anetaki II* is unpublished — so every value he printed is a
  committed, dated claim that is **mechanically gradable against Anetaki II the day it
  publishes**. logos will grade it as an external hypothesis row (his 15 printed readings,
  verbatim with page refs, are locked in `litindex.py` `_FRINGE_SCEPTRE_READINGS` +
  `CITATION_RJABCHIKOV`).
- **(ii) The readings were produced from PHOTOGRAPHS** — the exact practice this project's
  extraction rules forbid (`experiments/crossscript_gate/phase3/anetaki_extraction.md`
  reads no sign from images; GAP_DELTA verdict stays PENDING-FULL-EDITION). His source
  prints no transliteration, so the sign identifications are necessarily his own readings
  off published photos — sign identification and value assignment are conflated in a
  single unaudited step.
- **Quarantine, not dismissal:** the 15 readings (KN Zg 57: RU, RA, TI, I, KU, WI-RA,
  KA-DU, RE; KN Zg 58: DI, plus A-KA claimed on both; companion HT 33/HT 29 re-readings:
  PI, PA, QE, DA-I, A-RE) are indexed as `claim_type="fringe_sceptre_reading"` — DISPUTED/
  fringe, produced from photographs — **only so no model can return them as discovery**
  (§C.1/§C.2). They are never accepted readings, and per invariant 3 they are guilty until
  Anetaki II proves otherwise.

### Chiapello 2024 — pre-publication prediction on the ivory circle (prediction registry, no fringe judgment)

- **Work (verified 2026-07-03 from the archived public page):** Duccio Chiapello,
  "Deductions on an unknown find surrounded by mystery: the Linear A inscribed ivory circle
  found at Knossos", self-posted on Academia.edu
  (<https://www.academia.edu/114586901/>), **posted 2024-02-07** (page `created_at`) —
  before the Kanta et al. 2024 overview appeared and before the 2025 media wave. Archived:
  `corpus/bronze/prepub_prediction_2024_ivory_circle/` (Wayback capture 20260703173735 of
  the public page, SHA-256
  `e52e31f9be01290d241f837e9acace8ce9048a61322f1bff242f255503cf92b5`; the PDF itself is
  login-gated on Academia.edu and was NOT acquired — gap recorded in PROVENANCE.md).
- **The committed, falsifiable prediction (abstract, verbatim):** (1) "This inscription,
  when published, will show that the similarities between Linear A and Linear B are much
  greater than hitherto assumed"; (2) "This inscription will lead to a rapid reappraisal of
  the hypothesis that Linear A encodes a form of Greek."
- **Status:** a dated pre-publication prediction in exactly the epistemic shape logos
  rewards — committed before the evidence, **scorable when Anetaki II lands** (prediction 1
  is directly checkable against the edition's sign inventory/parallels; prediction 2 is a
  sociological claim about reception, gradable only loosely). This entry records the
  prediction; it attaches **no fringe judgment** and does not endorse the "Minoan Greek"
  hypothesis (which remains one capped family among several; the benchmark-favored prior is
  ISOLATE, per Salgarella 2025 §8).
