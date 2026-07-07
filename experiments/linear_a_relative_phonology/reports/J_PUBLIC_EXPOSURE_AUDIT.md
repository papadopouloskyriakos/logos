# J1 — Anetaki Public-Exposure Audit (KN Zg 57 / KN Zg 58)

**Task:** J1 (honesty-critical). Before any prospective Anetaki seal is frozen, inventory
everything ALREADY PUBLIC about KN Zg 57 (ivory Ring, ~119 signs, longest known Linear A
inscription) and KN Zg 58 (ivory handle), and define the UNSEEN final-edition delta.
**as_of:** 2026-07-07 · **seed:** 20260708 · Constitution v2.2.
**Machine artifact:** `../data/J1_exposure.json` (script-generated: `../scripts/j1_build_exposure.py`).

**Bottom line:** The whole inscription is NOT prospectively sealed. A large public metadata
layer already exists (carrier identity, ~119-sign length, per-face layout, sign-group COUNTS,
and every individually-printed sign). What remains held out is precisely the **transliterated
sign-group content** — which no source, scholarly or popular, has yet printed. Prospective
scoring must be confined to that unpublished content.

---

## 1. Repo search (Article XI source-dependency; done first)

Existing repo references to Anetaki / Zg 57 / Zg 58 / the ~119-sign material:

- **`experiments/crossscript_gate/phase3/anetaki_extraction.md`** — the authoritative,
  rule-honoring, page-cited extraction of editor-printed content (nothing read off photographs).
  This audit REUSES it rather than re-deriving; it is the primary already-public inventory.
- **`experiments/crossscript_gate/phase3/GAP_DELTA.md`** — verdict `PENDING-FULL-EDITION`:
  0 new LOTO legs, 0 transliterated candidate words (>=16 sign-groups exist but are unpublished).
- **`docs/watch/anetaki_ii.md`** — the standing watch (INSTAP series *The Religious Center of
  the City of Knossos*; sibling Vol. 1 *The Fetish Shrine*; trigger mechanics).
- **`docs/linear-a-claims-2026.md` §"Anetaki sceptre claims registry"** — the two REGISTRY
  objects (Rjabchikov 2025 fringe; Chiapello 2024 prediction), both gradable only when Anetaki II
  lands.
- **`scripts/comparison/litindex.py`** — `_FRINGE_SCEPTRE_READINGS` + `CITATION_RJABCHIKOV`
  (the 15 photo-derived fringe values, quarantined).
- **`experiments/linear_a_foundry/manifests/SEAL_5_prospective_gold_anetaki_II.json`** — the
  prospective seal (status `NO_CANDIDATE_TO_SEAL`; commitment_sha256 `9e412e55…425885`).
- **`docs/related/_acquisition.md`**, **`experiments/linear_a_foundry/scripts/wp7_source_register.py`**
  + `data/wp7_source_register.{csv,json}` — source register rows for all three documents +
  `SRC-ANETAKI-II` (forthcoming, unavailable).

Note: the licensed bronze PDFs (`corpus/bronze/kanta_etal_2024_anetaki/`,
`.../rjabchikov_2025_sceptre/`, `.../prepub_prediction_2024_ivory_circle/`) are **gitignored and
NOT present in this worktree**; this audit cites the repo-recorded vault SHA-256s.

## 2. Web leg (attempted per task; result recorded)

WebSearch was available (3 queries run; capture: `../data/source_watch/J1_web_capture_2026-07-07.txt`,
sha256 `a7d4ebb684ad9750865d69323871e65ef409879f63e43b308f8697febca255b7`). WebFetch of the
GreekReporter 2026-03-30 piece returned **HTTP 403** (popular-press block) — snippet-level only.

Findings:
- **No public source — scholarly or popular — carries a transliterated sign-group sequence** from
  KN Zg 57 or KN Zg 58. Popular outlets (GreekReporter, BiblicalArchaeology, LaBrujulaVerde,
  DiggingUpThePast, WorldHistory) reproduce the overview's metope/logogram description only.
- The only primary epigraphic source remains the **2024/2025 Kanta et al. Ariadne overview**.
- **Anetaki II is confirmed still unpublished** as of 2026-07-07.
- **New event surfaced (not a text):** Kanta & Charitos, June-2025 conference talk *"Knossos
  Anetaki plot: The Neopalatial Room 1 and its Ivory Repository"* (conference "Reconsidering LM IA
  Pottery Sequences and Chronologies"). A talk, no transliteration — added to the watch, not to
  the public-sign inventory.

**Limitation:** popular-press full text (GreekReporter) not retrievable (403); classified on outlet
type + snippet. This does not affect the audit — no popular outlet in this cluster is a source of
transliterations.

## 3. Sources used (with hashes)

| id | role | sha256 (repo-recorded vault; PDF gitignored/absent) |
|---|---|---|
| SRC-KANTA-2024 | PRIMARY epigraphic overview; prints NO transliteration | `87dad27b79ee3ef4539b844d7ed30a0069ac14acdd2ff75eed160f9baadf57d2` |
| SRC-RJABCHIKOV-2025 | REGISTRY fringe (photo-derived; quarantine) | `b4ce36798ad0271c86509a2c8ff54cefe52194131f0a51ee2fd2e06864c40437` |
| SRC-CHIAPELLO-2024 | REGISTRY prediction (Wayback HTML captured) | `e52e31f9be01290d241f837e9acace8ce9048a61322f1bff242f255503cf92b5` |
| SRC-J1-WEBCAPTURE | this audit's own web snapshot (hashed live) | `a7d4ebb684ad9750865d69323871e65ef409879f63e43b308f8697febca255b7` |

## 4. What is ALREADY PUBLIC (editor-printed only; nothing off photographs)

**Carriers.** KN Zg 57 = ivory Ring (elephant-tusk slice, dia ~13.5-14 cm; faces A top / B bottom
/ C external / D internal; provisionally a religious scepter). KN Zg 58 = ivory handle
(quadrangular, ~13 cm; faces α/β/γ/δ; "an accounting text").

**Length/totals (public).** Ring ~119 signs total (~84 preserved/partial + ~35 traces/probable);
**longest known Linear A inscription**; **no numerals at all** on the Ring.

**Layout skeleton + COUNTS (public):**
- Face A: 12 quadruped metopes (facing left; iconography deferred) + 16 preserved / ≥18 original
  metope signs; ≥10 engraved vases, some with syllabogram ligature (VAS+PA, VAS+RU…); 6 amphora
  vases; **NO phonetic sign-groups on Face A**.
- Face B: **6** "perfectly recognizable" sign-GROUPS + 3 logograms (LB values GRA, prob. FAR,
  OLIV); no numbers/fractions. Direction L→R (from AB81 KU, AB40 WI, AB60 RA).
- Face C: **≥9** sign-groups + 5 textile logograms (differ by fringe count); one ligatured with
  AB77 (KA); ≥40% damage. Direction L→R (from "AB60 RA, AB01 TA, AB81 KU" — printed verbatim).
- Face D: ~9 animal-hide signs (AB180), each metope; extremely damaged; ligatured sign restorable
  as AB77(KA)/AB78(QE)/AB70(KO).
- Handle α: 2 vases + phonetic-sign ligatures; sign for ten; a **probable NEW LA sign**; then
  Hieroglyphic *180 and *181.
- Handle β: a **4-sign sequence** at right end (first sign doubtful); left half likely a hide sign.
- Handle γ: boar + probably pig; no numerals.
- Handle δ: 2 vases w/ ligature; units + fractions; a **6-fraction sequence** with a new
  relative-value order.

**Individually-printed signs (public):** A, KU, DI, KA (repeated, calligraphic); RA, I, NE, SE
(KN Zf 31 comparanda); WI; "AB01 (TA)" as printed; the A+KA ligature on BOTH carriers (opposite
stacking → two hands); GRA/FAR/OLIV + textile + AB180 logograms; Hieroglyphic *180/*181 in LA use;
A664 rhyton direction indicator; the *existence* of one probable new LA sign.

**Interpretations (public):** Ring = ritual/display scepter (no numerals); handle = accounting
text; genre = Knossos Cult Center; authors' caution — "few parallels of the sign-groups on the
Ring with sign-groups on extant Linear A texts."

**Explicitly NOT public:** **no transliterated sign SEQUENCE of any length** is printed anywhere.
All sign-group content is deferred to Anetaki II.

## 5. The UNSEEN final-edition delta (what Anetaki II reveals first)

1. Transliteration of the **6 Face-B** sign-groups (with certainty marks).
2. Transliteration of the **≥9 Face-C** sign-groups.
3. Transliteration of the Handle **Face-β 4-sign** sequence.
4. Handle **Face-α** ligature readings + identity of the **probable new LA sign**.
5. The **Face-δ 6 fraction signs** and their relative-value ordering.
6. Full **Face-A syllabogram inventory** (16-18 metope signs) + VAS+X ligature resolutions.
7. **Face-D** restoration of the ~9 hide signs + the AB77/78/70 ligature choice.
8. Final CORRECTED readings (e.g. "AB01 TA" vs standard *da*), final sign order,
   joins/corrections, damaged-sign restorations.
9. Final layout / reading order per face; new photos, drawings, 3D.
10. Any editorial identification of groups as **names / toponyms / formula words** (w/ confidence).
11. Edition-specific contextual revisions (dating, findspot, function).

## 6. EXCLUDED from prospective scoring (already public → not held out)

A candidate may **not** be credited for "recovering" any of these:

1. Object identity, 2-carrier count, provenance.
2. ~119-sign length / "longest LA inscription."
3. Genre split (Ring display/cult vs handle accounting).
4. Per-face layout skeleton **and its counts** (6 Face-B / ≥9 Face-C / 4-sign β / 6 fractions δ /
   ~9 Face-D hides / 12 Face-A quadrupeds).
5. Every individually-printed sign / comparandum (A, KU, DI, KA, RA, I, NE, SE, WI, "TA", the A+KA
   ligature, all logograms, Hieroglyphic *180/*181, A664, and the *existence* of the new sign).
6. Directionality per face.
7. The existence/positions of the 6-fraction sequence and its "new ordering" claim (the VALUES
   themselves stay held out).
8. Any reading already committed by the registry (Rjabchikov's 15 photo-derived values; Chiapello's
   two predictions) — graded AS external claims; a logos candidate may not launder them as its own.

**Scoreable prospective payload:** ONLY the currently-unpublished transliterated sign-group VALUES
— the 6 Face-B groups, ≥9 Face-C groups, the 4-sign Face-β sequence, the Face-α ligatures + new-sign
identity, and the 6 fraction values/ordering. A blind reading is scored against THESE.

**Do NOT claim the whole inscription is prospectively sealed.** Its metadata skeleton is public; only
the sign-group transliterations are held out.

## 7. Compliance line

Art. XI source-graph honored (repo grepped first; vault hashes cited; gitignored PDFs flagged
absent). Art. XII non-circular: only public metadata + hashes recorded; no held-out label read, no
model run, no known Linear A value used as input. Invariant 12: counts script-generated
(`j1_build_exposure.py`). Invariant 3 respected: registry claims stay quarantined, guilty until
Anetaki II proves otherwise. STATUS: **COMPLETE**.
