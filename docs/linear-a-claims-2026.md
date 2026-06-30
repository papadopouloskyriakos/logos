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
2. **The anchor is contradicted by prior scholarship.** Brent Davis (cited on HN) argues the
   recurring root is **`i-*301` = "give"** (cf. *ta-na-i-301-u-ti-nu*), not N-W-Y "to dwell" —
   and "give" vs "dwell" are semantically far apart. If Davis is right, the lynchpin fails.
   - **Attribution discipline (audit 2026-06-30).** The counter-reading is **Brent Davis's**
     (*Kadmos* 52, 2013; *Minoan Stone Vessels*, Aegaeum 36, 2014). **Do NOT re-attribute it to
     Steele 2024** — the Steele-2024 item in hand is **O. Dickinson's book review** (JGA), which
     carries **no `*301` gloss** (its p. 474 "prayers or dedications" line is neutral on the
     dwell-vs-give crux; quoting it as support for "give" would be exactly the evidence-inflation
     logos refuses). The current expert benchmark, **Salgarella 2025 §8**, is paywalled — checking
     `*301` against it is an **open item**, not resolved. logos's charter: get the crux-sign gloss
     right or it is a referee magnet. Still needed: the primary Davis text with the
     `ta-na-i-*301-u-ti-nu` parallel quoted with page numbers.
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
  **Quarantine, not dismiss:** per **Schoep 2002** (via Braović et al. 2024, p. 734) Semitic and
  Lycian are the *two best-founded* language hypotheses, so the Di Mino/Gordon reading is indexed
  to catch regurgitation and graded as a capped family — never labelled "crank."
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
- logos will **reproduce the Luo 2019 null** (a neural decipherer fails on Linear A without a
  known cognate) as a baseline milestone — the empirical confirmation of point 6.
