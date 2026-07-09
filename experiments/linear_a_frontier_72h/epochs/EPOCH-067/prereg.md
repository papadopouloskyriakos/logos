# EPOCH-067 — PREREGISTRATION (FROZEN)

**Task:** How deep is word-initial concentration? Single prefix slot (position 0 only) or a SECOND
concentrated initial slot at position 1 (depth-2 prefixing / "prefix-stacking")?

**Campaign:** Linear A frontier-72h. **Layer:** L3 (morphological typology; L2/L3 anonymous-positional).
**Operator:** logos z.ai research worker (GLM-5.2). **Discipline:** STRICT LOGOS — proposer/operator,
never adjudicator; MECHANICAL verdict from a FROZEN rule.

---

## 1. QUESTION (frozen)

E064 established that word-INITIAL (position 0) sign entropy is significantly LOWER (more concentrated)
than word-final, cross-site — a prefixing signature (the A-prefix of E022–E025 is one instance).

**E067 asks:** does the concentration extend to POSITION 1 (a SECOND concentrated initial slot →
depth-2 prefixing / "prefix-stacking", which the campaign's frozen paper characterizes LA morphology as),
or does it STOP at position 0 (a SINGLE prefix slot)?

## 2. DATA (verified)

- Source: `corpus/silver/inscriptions_structured.json`. Word tokens carry `signs` (list of sign strings).
- Target population: words with `len(signs) >= 3` (so positions 0,1,2 all exist). **n = 752**.
- Sites with >=30 such words (testable cross-site): **6** — Haghia Triada 353, Zakros 76, Khania 46,
  Knossos 41, Palaikastro 39, Phaistos 34. (>=2 → not underpowered.)

## 3. METRIC (frozen)

Over the >=3-sign words, for position k in {0,1,2}:

- `H_k` = Shannon entropy (bits) of the (anonymous) sign distribution at position k.
- `A_k = E_null[H] - H_k`, where `E_null[H]` is the within-word-shuffle expected per-position entropy.
- `A_k > 0` ⇔ position k is MORE concentrated than chance.

Signs are treated as ANONYMOUS IDs (no readings, no values, no meaning). Only positional entropy is used.

## 4. NULL (frozen)

Within EACH word, uniformly PERMUTE its sign order; recompute `H_k` for each position k over the
shuffled words; **>=1000 shuffles**. Under this null, positions are exchangeable within a word, so
`E[A_k] = 0` for all k (this controls sign-frequency, word-length, and sample size simultaneously —
all three are held fixed by permuting within word).

`perm p_k = frac(null A_k >= observed A_k)`, one-sided (concentration direction).

## 5. PROTOCOL (frozen)

0. Inspect: n; `H_0,H_1,H_2`; shuffle-expected `E_null[H]`; `A_0,A_1,A_2`.
1. Freeze prereg + plan_hash; ship `machinery.py` with `__main__` self-check (validates the
   within-word permutation null: confirms `E[A_k] ≈ 0` on a synthetic exchangeable corpus).
2. GLOBAL: `A_0, A_1, A_2` + perm p each (1000 shuffles).
3. POSITIVE CONTROL FIRST (synthetic — gates the verdict):
   - (a) **DETECT-DEPTH2**: plant words with BOTH pos0 AND pos1 drawn from RESTRICTED inventories
         (two concentrated slots) + diverse pos2+; expect `A_0` AND `A_1` flagged (p<=0.05).
   - (b) **DETECT-SINGLE**: plant words with ONLY pos0 restricted (pos1+ diverse); expect `A_0`
         flagged but `A_1` NOT flagged (guards against spurious pos1 firing when only pos0 is
         concentrated).
   - (c) **FALSE-POSITIVE**: plant words with all positions from the SAME distribution; expect no
         `A_k` flagged (rejection rate <=0.10 across >=20 draws).
   - If depth-2 undetectable, OR single-slot's pos1 spuriously fires, OR uniform fires →
     `MACHINERY_UNINFORMATIVE`.
4. CROSS-SITE (robustness of the pos1 slot — pos0 is E064-established): per site with >=30 >=3-sign
   words, recompute `A_1` + within-word-shuffle null + perm p; count sites with `A_1>0` significant.
5. FROZEN MECHANICAL VERDICT (see §6).
6. Write outputs to the PATH CONTRACT paths.

## 6. FROZEN MECHANICAL VERDICT (one token)

- `CONCENTRATION_DEPTH_2` iff PC passed AND `A_0` sig (p<=0.05) AND `A_1` sig (p<=0.05) globally AND
  `A_1` replicates (sig, `A_1>0`) in >=2 sites — a second concentrated initial slot (depth-2;
  stacking-or-selection, see caveat).
- `CONCENTRATION_SINGLE_SLOT` iff `A_0` sig BUT `A_1` NOT sig globally (or not in >=2 sites) —
  concentration confined to position 0 (single prefix slot).
- `NO_INITIAL_CONCENTRATION` iff `A_0` NOT sig (would contradict E064; report honestly).
- `DEPTH_UNDERPOWERED` iff <2 sites have >=30 >=3-sign words.
- `MACHINERY_UNINFORMATIVE` iff PC failed.

## 7. HONEST INTERPRETIVE CAVEAT (frozen, must appear in result + report)

A significant pos1 concentration is **AMBIGUOUS** between (a) a genuine SECOND prefix morpheme
(true prefix-stacking) and (b) the first prefix's SELECTIONAL restriction on the following sign
(E050 found A- has a weak generic continuation restriction). At L2/L3 we report only the STRUCTURAL
fact (is pos1 concentrated beyond the shuffle null); we do **NOT** adjudicate stacking-vs-selection.

## 8. NON-CIRCULAR / DISCIPLINE (hard)

- Anonymous sign IDs only (signs relabeled to opaque tokens internally if helpful; values never used).
- Positional ENTROPY only — no n-gram models, no sign identities in the metric.
- Within-word shuffle makes all positions exchangeable ⇒ `E[H]` equal across positions under the null
  (controls sign-frequency + word-length + sample size).
- L2/L3-typology ONLY. No reading, no meaning, no phonology.
- PC is SYNTHETIC and is stated as such.

## 9. OUTPUTS

`prereg.md`, `plan_hash.txt`, `machinery.py`, `result.json`, `EPOCH067_REPORT.md`, and a `data/`
directory — all at the PATH CONTRACT paths.
