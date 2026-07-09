# EPOCH-004 prereg — FRACTION_ORDER_ANETAKI_SEAL: third prospective seal (fraction relative-value order, face δ)

- **epoch_id:** EPOCH-004
- **frontier:** F10 (prospective prediction systems) · substantive gate D
- **campaign:** research/linear-a-frontier-72h
- **date frozen:** 2026-07-08 (this file is written and hashed BEFORE any derivation stage runs)
- **seed:** 20260708
- **constitution:** v2.2
- **articles_triggered:** V (claim layers), VII (search receipt — inherited from EPOCH-001 2026-07-08
  sweep, no new external search planned), VIII (effective_n), IX (information budget), XI
  (source-dependency: every prediction row carries witness doc ids), XII (no grading a target by the
  rule that created it — the held-out target is untouched, contamination audit is part of the plan),
  XV (licence gate — NO licence claimed or consumed; numeral-notation structure only), XVII
  (append-only), XVIII (assumption register A-FD1..A-FD6), XXII (stage header + compliance line).
- **claim layer:** **L2/L3 (numeral-notation structure / functional value-order of klasmatograms).**
  No semantic, lexical, phonetic, language-id or translation content. SEMANTIC+ remains NOT_AUTHORIZED.

## Purpose (exact)

Kanta, Nakassis, Palaima & Perna 2024 (Ariadne Suppl. 5, pp. 41–42 — PUBLIC, on disk, audited in
EPOCH-001) state that KN Zg 58 (ivory handle) Face δ carries, after two ligatured vases and units,
a sequence of **six different fraction signs**, and that this sequence "provides us with a different
sequence of values than those suggested until now" (fn. 12 cites Corazza et al. 2021). The sign
identities and their order are **NOT published**; they are held out until the editio princeps
(*Anetaki II*, INSTAP Academic Press, forthcoming).

BEFORE that publication, freeze a third prospective seal that commits:
1. **OUR corpus-derived relative-value ordering** of the Linear A fraction signs (pairwise
   probability matrix + maximum-consistency orderings), derived ONLY from `corpus/silver` sequence
   evidence + the two in-repo arithmetic anchors (Bennett/Schrijver-audited);
2. the **Corazza et al. 2021 published ordering** as comparator (values verified 2026-07-08 against a
   secondary source reproducing the paper's table; identical to the repo's audited
   `scripts/comparison/metrology.py::CORAZZA_2021`);
3. an **exact mechanical scoring rule** against the future ed.pr. face-δ sequence, with VOID and
   failure criteria and an immutable sha256 manifest.

## Non-circularity / independence (Art. XI, XII)

- OUR matrix uses ONLY: (a) multi-sign fraction tokens inside `corpus/silver` inscriptions
  (lineara.xyz-derived, ingested long before Kanta et al. 2024 was read by any session), and (b) the
  arithmetic anchors J=1/2 (Bennett 1950; HT 104 + HT Zd 156 + PE 1 + HT 123a per the audited
  Schrijver record) and E=1/4 (JE composite = ¾, additivity Schrijver-validated except D).
  **No Corazza value enters the derivation**; Corazza is comparator only.
- The held-out target (face-δ identities/order) is unpublished; EPOCH-001's 14-route search receipt
  (2026-07-08) + register row 35 (`quarantine: unpublished_content`) attest no public exposure. The
  fringe photo-based source (Rjabchikov, quarantined conf 0.0) is NOT read in this epoch; the plan
  only counts pattern matches blind (see contamination checks C1–C5).
- KNOWN LEAK (recorded, discounted): the PUBLIC editors' statement already implies ≥1 discordance
  between the face-δ order and Corazza 2021. Therefore any prediction of the form "Corazza will show
  ≥1 error" earns ZERO credit. All credited content is: WHICH pairwise directions hold, committed
  blind. Our matrix is frozen without any knowledge of which pairs discord.

## Derivation set vs held-out

- **Derivation:** `corpus/silver/inscriptions_structured.json` (1,341 inscriptions) — the ONLY
  value-bearing input; plus the two arithmetic anchors above.
- **Held-out:** the unpublished *Anetaki II* face-δ fraction sequence (6 signs, order, identities).
  Nothing in this epoch reads, estimates, or conditions on it.

## Frozen extraction + derivation procedure (run exactly this; all mechanical)

P1. **Sequence-token extraction.** From every silver record's `stream`, take `other` tokens whose
    raw (after stripping `≈` and whitespace) consists ONLY of Aegean fraction glyphs
    U+10740–U+1075F (named), length ≥ 2 (reuse `scripts/comparison/metrology.py` recognizers).
    Letter = last field of the Unicode name (A701 A → `A`). Editorial vulgar-fraction glosses
    (single tokens like ¹⁄₂, ³⁄₄) are single signs, NOT sequences.
P2. **Horizon split.** PRIMARY = records whose `context` starts with `LMI` (Corazza's own LM I
    restriction; the Anetaki deposit is Neopalatial). SECONDARY = all records (reported in the seal
    as a separate, non-primary tier).
P3. **Votes.** Within each sequence token, every ordered pair of positions i<j with DISTINCT letters
    votes `letter_i ≥ letter_j`. Doc-level dedup: per (doc, unordered pair), one vote whose direction
    is the majority across that doc's pair instances; within-doc ties are dropped.
P4. **Arithmetic anchors + convention reliability.** Anchored values: J=1/2, E=1/4 (JE=J+E=3/4).
    D is NOT anchored (Schrijver: D non-additive). Frozen arithmetic claims: J>E, JE>J, JE>E at
    q=0.99. The descending-order convention reliability p has prior **Beta(8,2)** (typological;
    frozen here; sensitivity band Beta(4,1) and Beta(16,4) reported, primary is Beta(8,2)); it is
    updated on every PRIMARY doc-level vote among anchored letters {J, E, JE}: each vote descending
    → success, ascending → failure. Votes so consumed are EXCLUDED from the P5 matrix (no
    double-use; arithmetic overrides them).
P5. **Pairwise posterior matrix.** For a pair with s doc-votes X-first and f doc-votes Y-first,
    q(X>Y) = M(s,f) / (M(s,f)+M(f,s)) with M(s,f) = E_{p~posterior Beta}[p^s (1-p)^f]
    (Beta-function ratio, exact), clipped to [0.01, 0.99]. Direct-evidence pairs use direct q only.
    **Transitive tier:** for pairs with NO direct evidence, q = max over directed paths of the
    product of edge q's; claim iff ≥ 0.60, flagged `transitive`. All other pairs = ABSTAIN.
P6. **Orderings.** Exhaustive over all letters carrying ≥1 primary claim: report the maximum-
    likelihood total order(s) (product of q / (1−q) over claimed pairs), top-5 linear extensions,
    the number of tied maximum-likelihood extensions, and P(all direct claims correct) = Π q.
P7. **Corazza comparator (frozen):** tier-1 {J=1/2, E=1/4, B=1/5, D=1/6, F=1/8, K=1/10, L2=1/20,
    L3=1/30, L4=1/40, L6=1/60}; tier-2 author-flagged uncertain/composite {H=1/16?, A=1/24?,
    W=2/5 (=BB?), X=1/12 (=AA?)}; JE=3/4, DD=1/3 composites. Citation: Corazza, Ferrara, Montecchi,
    Tamburini & Valério (2021), J. Archaeol. Sci. 125:105214, doi:10.1016/j.jas.2020.105214.
P8. **Divergence registry (mechanical):** all pairs where OUR claim direction contradicts the
    Corazza order, listed with tiers — these are the seal's sharpest discriminating predictions.

## Controls (positive control FIRST; all gate this epoch's verdict)

- **PC-1 (pipeline recovery, runs before any real derivation output is inspected):** plant the
  Corazza tier-1+tier-2 values as ground truth; regenerate the SAME token/doc structure as the real
  primary corpus (same docs, same letter multisets per token) with every token written strictly
  descending (noiseless). Run P3–P6. **PASS iff 100% of claimed direct pairs have the correct
  planted direction and q is non-decreasing in vote count k.** A noisy variant (each token
  independently ascending with prob 0.2, 200 reps) is reported descriptively (mean direction
  accuracy), non-gating.
- **PC-2 (scorer round-trip):** score a synthetic six-sign "face-δ" sequence drawn descending under
  the planted values against the PC-1 matrix → must return OURS_SUPPORTED; score the reversed
  sequence → must return OURS_REFUTED. PASS iff both.
- **NC-1 (order-shuffle null):** shuffle within-token glyph order uniformly (20,000 reps, seed
  20260708), recompute the doc-level net-margin statistic W = Σ_pairs |s−f| over PRIMARY matrix
  pairs (E–J-type anchored votes excluded, as in P4). p = P(W_shuffle ≥ W_real).
  **PASS iff p < 0.10** (the real data's cross-document unanimity must be improbable under
  direction-random writing).
- **NC-2 (frequency adversary, informative):** order letters by total corpus glyph frequency
  (standalone + within sequences); report which claimed pairs contradict the frequency-rank
  direction. PASS iff ≥ 1 claimed pair contradicts frequency (channel not reducible to frequency);
  if 0, the seal is still frozen but carries flag `FREQUENCY_CONFOUND_UNBROKEN`.
- **NC-3 (relabeling sanity):** apply a fixed letter permutation to the extracted tokens, re-run
  P3–P5, verify the output matrix is the identical permutation of the original. PASS/FAIL.

## Frozen scoring rule (executed only when *Anetaki II* publishes; scorer code in the manifest)

**Ground truth hierarchy:** G1 = the ed.pr.'s explicitly printed relative-value ordering of the
face-δ signs, if the editors print one; else G2 = the written sequence order under the descending
convention (using the editors' stated reading direction). If the ed.pr. asserts the sequence is not
value-ordered AND prints no ordering → VOID (V3). Signs are mapped to klasmatogram letters by the
ed.pr.'s own identifications; unmappable/new signs drop their pairs.

- **Sub-test 1 (PRIMARY):** over all sign pairs in the published sequence where OUR primary matrix
  claims a direction: n₁ = #claimed, acc₁ = #correct/n₁, plus exact one-sided binomial p vs 0.5.
  Verdict: `OURS_SUPPORTED` iff n₁ ≥ 4 and acc₁ ≥ 0.75; `OURS_REFUTED` iff n₁ ≥ 4 and acc₁ ≤ 0.5;
  `OURS_MIXED` iff n₁ ≥ 4 and 0.5 < acc₁ < 0.75; `NO_POWER` iff n₁ < 4. Brier and log scores
  reported using the frozen q's.
- **Sub-test 2 (head-to-head):** on pairs where BOTH systems claim (Corazza tier-1 only):
  `OURS_BEATS_CORAZZA` / `CORAZZA_BEATS_OURS` / `TIE` by accuracy; requires n₂ ≥ 4 else `NO_POWER`.
- **Sub-test 3 (divergent pairs):** for every P8 registry pair present in the sequence, record the
  winner. `DIVERGENT_OURS` / `DIVERGENT_CORAZZA` / `SPLIT` / `DIVERGENT_ABSENT`.
- **Multiplicity:** the epoch registers ONE prediction system. Sub-test 1 alone determines the
  headline verdict; sub-tests 2–3 are secondary, reported always, Holm-corrected as a family of 2.
  Corazza tier-2 pairs are reported outside the gates. No post-hoc pair selection: the matrix in the
  sealed JSON is exhaustive and final.
- **VOID conditions:** V1 = ed.pr. never publishes the face-δ identities; V2 = fewer than 2
  scoreable pairs after mapping; V3 = as above; V4 (contamination) = any repo session reads the
  ed.pr. face-δ content before a scoring plan is frozen per the EPOCH-001 trigger protocol → seal
  verdict capped at DESCRIPTIVE and the session id recorded.
- **Failure is real:** OURS_REFUTED is a publishable negative for the sequence-order channel; it
  cannot be amended into a success (Art. XVII).

## Contamination checks (all mechanical, run in this epoch)

- C1: the public Kanta et al. 2024 text (pdftotext) contains NO fraction-sign identity and no
  Aegean fraction glyph codepoints in the face-δ passage (pattern scan; passage quoted in report).
- C2: EPOCH-001 register row 35 has `quarantine: unpublished_content`; fringe rows 37–39 contain no
  fraction-identity patterns (blind boolean scan only — content never displayed).
- C3: blind pattern-match COUNT (never content) of fraction-related strings in the quarantined
  fringe sources; recorded; sources not read.
- C4: derivation script asserts its only value-bearing input path is `corpus/silver` (no file under
  `data/anetaki_2025/` or `corpus/bronze/kanta_etal_2024_anetaki/` is opened by the derivation).
- C5: EPOCH-001 search receipt (14 routes, 2026-07-08) cited as the currency check that no other
  public edition exists; no new search is run (avoid re-exposure risk).

## Committed verdict rule for THIS epoch (fail closed)

`SEAL_FROZEN_PROSPECTIVE` iff ALL of: PC-1 PASS, PC-2 PASS, NC-1 p < 0.10, NC-3 PASS, C1–C5 all
pass, the primary matrix carries ≥ 8 claimed pairs, and the seal JSON + sha256 manifest are written.
Otherwise `SEAL_NOT_FROZEN(<first failing gate>)`. NC-2 failing only sets the confound flag.
No held-out data is scored in this epoch; the seal's own verdict field is `SEALED_PROSPECTIVE`.

## Information budget / effective_n (Art. VIII, IX)

Committed content ≈ one direction bit per claimed pair (~15 direct + ~10 transitive ≤ 25 bits
nominal; effective less, since transitive rows are implied). Scoring n is capped at C(6,2)=15 pairs;
expected claimed-pair coverage is uncertain (the six signs may include letters our matrix abstains
on) — P(NO_POWER on sub-test 1) is materially high and is estimated (non-binding) in the seal.

## Assumptions (Art. XVIII; appended to campaign ASSUMPTION_REGISTER.json)

- **A-FD1 (descending convention):** multi-sign fraction strings are written in non-increasing
  value order. Basis: typological (Aegean/Egyptian practice; Corazza premise). The corpus itself
  funds the reliability estimate (P4): the only arithmetic-checkable primary instance (ZA 8, E
  before J) VIOLATES it, so the frozen posterior mean is 8/11 ≈ 0.727 — the seal's confidences are
  tempered by the corpus's own counter-evidence.
- **A-FD2 (prior choice):** Beta(8,2) was frozen after a derivation-set census (unavoidable: the
  channel had to be found) but before any pipeline output; sensitivity to Beta(4,1)/Beta(16,4) is
  reported inside the seal.
- **A-FD3 (silver order fidelity):** silver raw token character order preserves the editorial
  reading order (lineara.xyz convention), uniformly across docs.
- **A-FD4 (additivity):** composite klasmatograms are sums of parts (JE=3/4), EXCEPT D-composites
  (Schrijver); hence E=1/4 anchored, D unanchored.
- **A-FD5 (letter identity):** GORILA letter names in Unicode glyph names identify the same
  klasmatogram classes the ed.pr. will use (standard in the field).
- **A-FD6 (LM I horizon):** the LM I restriction (P2) controls system drift (per Corazza); the
  MM II Phaistos evidence is quarantined to the secondary tier.

## Outputs

`epochs/EPOCH-004/{prereg.md, plan_hash.txt, derivation.json, controls.json, result.json}`;
`data/seals/FRACTION_ORDER_ANETAKI_SEAL.json` + `FRACTION_ORDER_ANETAKI_SEAL.manifest.sha256`;
`scripts/fraction_order_seal.py` (derivation + controls + the frozen scorer, all in the manifest);
`reports/EPOCH004_FRACTION_SEAL.md`; EPOCH_LEDGER.yaml + STATUS.md appended.
