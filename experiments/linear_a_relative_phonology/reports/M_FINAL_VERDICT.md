# M — Final campaign verdict: Linear A relative-phonology / segmentation / seals

**Branch:** `research/linear-a-relative-phonology-seals` · **Parent:** Foundry `09f7ef9` · **Constitution:** v2.2 ·
**Opened:** 2026-07-07 · **Closed:** 2026-07-08.

> **FINAL MECHANICAL VERDICT:** **`NEW_CONSTRAINTS_BUT_NO_DECIPHERMENT`** — with the value-layer question resolved
> to its sharpest, most-audited state yet, and a held-out-validated L2/L3 structural positive.
>
> - **`RELATIVE_PHONOLOGICAL_STRUCTURE`: `SUPPORTED_ON_KNOWN_SCRIPT_ANALOGUE`, `NULL_ON_LINEAR_A`.** Internal
>   substitution structure genuinely breaks the C/V symmetry on opaque Linear B (twice-audited), but Linear A does
>   not exhibit the exploitable axis.
> - **Highest earned claim layer on Linear A: L2/L3** (anonymous administrative structure), validated on held-out
>   inscriptions, an unseen site, and an unseen formula family.
> - **All seven transfer licences (STRUCTURAL…TRANSLATION): `NOT_EARNED`.** No phonetic value is recoverable or
>   assigned anywhere.

---

## 1–3. Isolation & compliance
Forked cleanly from Foundry `09f7ef9`; `main` `6fd4f20` untouched; Constitution v2.2; paper byte-frozen
(arxiv sha256 `a2ab89fa…`); `paper/`, `runtime/`, CSA, and all completed branches untouched; append-only ledger
active; test baseline 38 passed. The two frozen preregistered one-shots were NOT re-run (their machinery was
imported read-only). Non-circular throughout: known LB/LA values grade benchmarks only, never a model input.

## 4–6. The C/V analogue: reproduced, then refuted (WP-A)
The Foundry position→C/V result **reproduces exactly** (single-feature 0.744/p0.035, 7-feature CV 0.835/p0.01)
but **does not survive audit** (`CV_ANALOGUE_REFUTED`): it fails multiplicity (Bonferroni×13 0.455, Holm 0.36,
FDR q 0.168), is not even the best channel (log_freq 0.878 beats position 0.744), fails independent replication
(GMM/HMM both fail), is non-significant under the honest two-sided null (p 0.146), and collapses under the
frequency-band-disjoint split (position-only 0.481=chance). The surviving signal is a **frequency typological
prior** ("vowels are frequent" — external, relabeling-invariant), not corpus-internal structure. The full
degradation surface is a flat non-significant plateau (no cell beats its own null). Also found + documented a
floating-point filter bug in the Foundry code (`exp(log(20))<20`).

## 7. Segmentation (WP-B)
All six unsupervised families beat baselines on known-LB boundaries (Bayesian F1 0.608), but at Linear A's hapax
regime **boundary skill over "cut-everywhere" collapses to ~0** — any LA segmentation is an over-cut superset. C/V
recovery is segmentation-invariant. Held-out LB recovery endorses **GORILA_WORD** segmentation; the real boundary
signal on LA is the **physical/administrative layout channel** (row-break AUC 0.875), not distribution (0.565).

## 8–10. Substitution, relative posterior, seeds (WP-C, WP-D)
- **The substitution consonant-held axis is a genuine relative-structure signal on opaque LB** (`C_AUDIT`
  `VALIDATED`): survives the exact battery that refuted position — 4/4 independent implementations agree, the
  frequency-normalized scorers are strongest, it holds under the frequency-band-disjoint split (0.657–0.725) and
  passes the frequency-matched null (p 0.0033). **This is the correct, scoped refutation of value-blindness:
  internal methods are not universally value-blind — via substitution, not position.**
- **But Linear A does not exhibit it** (`C4`/`C5` `NOT_RECOVERED`): underpowered (long-frame support 3 vs LB's 98)
  and wrong-signature (LA's strongest axis is word-INITIAL prefixation, not word-final inflection); FRAGILE (severe
  Haghia-Triada dependency; deflated info-gain 4 bits).
- **Relative posterior (`D5`):** a stable anonymous K=2 partition exists but aligns with vowel/CV only at chance;
  its axis is provenance + morphology, not phonetics.
- **Seed-propagation (`D3`) is a frequency artifact** — the Foundry "3–4 seeds→0.87" is an n=5 lucky sample
  (honest 0.784) + a design leak (kv=4 reveals 80% of the 5-vowel key); pure frequency ranking gives 0.872.
- **Minimal-seed frontier (`D4`):** LA sits below threshold; value-blind seed selection recovers nothing (the
  measured price of relabeling-invariance); no secure seeds exist.

## 11. Morphology & formula grammar (WP-E) — the L2/L3 positive
- **A- prefixation** is a genuine productive Linear A word-initial affix: it survives the frequency-matched Holm
  null (p 0.050), beats all label-corruption + no-morphology controls (paired p 0.0005), and — decisively —
  survives the **best-of-selection adaptive null** (WP-K adaptive p 0.008, correcting for best-of-~195-affixes ×
  8-segmentations: observed productivity 47 vs selection-null 95th-pct 43). The wave-2 "A-/I-/-JA" is **corrected
  to A- only** (`-JA` HT-bound, `I-` frequency-indistinguishable). **ERRATUM (WP-K):** the wave-3 *cross-site*
  significance (E3, p 0.0099) does NOT survive selection correction (adaptive p 0.42 — some affix clears the
  min-both-HT-direction bar in 42% of best-of-affix nulls); A- cross-site is downgraded to **descriptive off-HT
  presence**, not a significant generalization. A- prefixation itself stands.
- **Two formula grammars:** the ledger register (KU-RO = terminal TOTAL slot with arithmetic sum-consistency
  7/31 exact; KI-RO = mid-text DEFICIT) and the libation register (rigid order OP<SSR<UNK<IPN<SIR, permutation
  p 5e-5), in complementary distribution.
- Caveat (`E4`): the morphology compresses training but does not buy held-out word prediction (a metric-
  insensitivity result — even LB's real morphology fails it — not evidence against A-).

## 12. Cross-script (WP-F)
Value transfer **NULL**, mechanically decomposed: of 8 channels only admin_function/distributional is both
non-circular and independently calibratable, and it calibrates to NULL (a 4th independent distributional null);
shape and scholarly channels are circular (capped ≤0.75); 0/59 correspondences have a primary value source.

## 13. Anchors (WP-G)
`SEED_A = 0`. 115 records dedup to 6 method-lineages / 1 value-bearing channel / 5 toponym equations; expansion
yields rich relative substrate but zero new value-bearing anchors; no independently-secure value seed exists.

## 14–15. Candidate rounds & agnostic search (WP-H, WP-I)
All null. `H1` relative-class-constrained `AT_END_TO_END_NULL`; `H2` anchor-constrained `AT_ANCHOR_CONSTRAINED_
NULL`; `H3` morphology-first joint `AT_JOINT_INFERENCE_NULL` — **the decisive round: the backbone is relabeling-
invariant (200 relabelings leave the held-out read-count exactly invariant → 0 bits of value information)**. `I1`
agnostic `UNDERDETERMINED_NO_RECOVERY` — the detector is live (LB control fires) so the LA null is informative;
any LA value system has ≥10²⁷ relabeling-equivalent twins, breakable only by an external anchor/bilingual (none).
Across all rounds the chronogeographically-impossible negative control (Finnish) and the agnostic control both sit
at the null — the bar is specific, not leaky.

## 16–18. Anetaki exposure audit & seals (WP-J)
The Anetaki inscription has a **large already-public metadata layer** (Kanta et al. 2024: carrier identity,
~119-sign length, per-face layout skeleton + sign-group counts, logograms, every printed sign). Only the
**unpublished transliterated values** are sealable — and no value candidate exists, so the Anetaki seal carries
**structural (L2/L3) predictions only**, prospective, excluding every public item. Five hashed seals: the L2/L3
structure **passes held-out tests** — SEAL_2 (unseen inscriptions) SUPPORTED, SEAL_3 (unseen site Khania)
SUPPORTED (carrier-value grammar transfers while KU-RO='total' correctly absent = HT-specific), SEAL_4 (unseen
libation family, LOO) SUPPORTED; SEAL_5 (masked notation) an honest committed NEGATIVE.

## 19. False-positive rate (WP-K) — `NULLS_CONFIRM_NULLS`
The adaptive best-of-selection null (reproducing best-of-~195-affixes × 8-segmentations × 2-slots, both HT-split
directions, random anchor systems, value relabelings; 500 full-pipeline / 500 anchor / 1000 cheap runs) confirms:
- **The value layer's false-positive rate is chance.** The held-out structural read-count (1005) is identical over
  200 value relabelings (std 0.0) → 0 selection-exploitable bits → no value positive exists to be suppressed. The
  nulls confirm the nulls.
- **The L2/L3 positives are NOT search artifacts** — they survive the null that reproduces their own selection:
  A- prefixation adaptive p **0.008** (vs naive 0.050 — selection lifts the chance bar from ~24 to ~37, observed 47
  still at the 99.2nd pctile), ledger KU-RO-terminal p **0.002** (0/500 random anchor systems match), libation
  rigid order p **0.030** (weaker than the nominal 5e-5 — zero-inversions alone is cheap at 61% of random systems;
  the strength is the 10 co-occurring consistent pairs, reached by only 2.8%). Joint adaptive p of the three ≈ 5e-7.
- **One artifact caught + downgraded:** A- cross-site generalization (adaptive p 0.42) → ERRATUM in §11.
- Expected spurious L2/L3 at A- strength over ~40 tasks ≈ 0.32 (<1) — the surviving positives are real.

## 20. Source watch (WP-L)
9 acquisitions ranked by expected information gain; #1 Anetaki II remains unpublished (web-verified 2026-07-08),
and being monolingual it authorizes no SEMANTIC+ licence alone — its value is falsification power (grades the
sealed structural predictions). Ingestion frozen READY-ON-ARRIVAL; Younger corpora offline → Wayback.

## 21–22. Strongest surviving & failed candidates
- **Strongest surviving (positive):** anonymous L2/L3 administrative structure — A- prefixation + the ledger and
  libation formula grammars — validated on held-out inscriptions, an unseen site, and an unseen formula family.
- **Strongest failed (value):** West Semitic, which raw-clears the end-to-end null but only on the single lexeme
  KU-RO='total' (a shared accounting shortcut), collapsing under Holm and leave-one-lexeme-out.

## 23. Highest earned licence
Highest earned claim layer **L2/L3** (structural/administrative, held-out-validated). All seven transfer licences
(STRUCTURAL, FUNCTIONAL, SEMANTIC, LEXICAL, PHONETIC, LANGUAGE_ID, TRANSLATION): **NOT_EARNED** — no analogue→LA
value bridge survives held-out verification.

## 24. Exact remaining uncertainty
The Linear A value layer is **underdetermined by the available monolingual evidence** (≥10²⁷ relabeling-equivalent
value systems; 0 bits of internal value information from the morphology-first backbone). This is not a proof of
impossibility: internal methods CAN break the symmetry (substitution, on LB), and LA simply lacks the power and
the word-final morphological signature to exhibit it. What is genuinely open: whether a richer text (the Anetaki
editio princeps, longer continuous context) would raise the substitution channel above its LA power floor — but
even success there would break value equivalence classes, not read the script; a bilingual or ≥3 independent
held-out anchors remain the only routes to absolute values.

## 25. Next prospective trigger
The `ANETAKI_FINAL_EDITION_DELTA_SEAL` — a dated, hashed, structural-only prediction set scored when the editio
princeps of KN Zg 57/58 publishes. The Linear-B-new-tablet standard, applied to the L2/L3 positive.

## 26. Confirmation
The submitted paper and all prior campaign history remained untouched; every correction here is an
ERRATUM/SUPERSEDING record (Art. XVII), never a silent rewrite. The Foundry record is intact; its position→C/V and
seed-propagation interpretations are superseded, not deleted.
