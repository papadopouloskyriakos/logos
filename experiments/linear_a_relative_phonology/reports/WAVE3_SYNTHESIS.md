# Wave 3 synthesis — value layer comprehensively closed on LA; a real modest morphology remains

## A third correction to the Foundry: seed-propagation is a frequency artifact
`D3` audited the Foundry's "3–4 seed labels → ~0.87 C/V recovery" (reduced-seed bootstrap) exactly as WP-A
audited position → **`SEED_PROPAGATION_FREQUENCY_ARTIFACT`**:
- Pure frequency ranking of LB signs (NO seeds, NO propagation) gives AUC **0.872**, exceeding the 0.87 headline —
  the 5 vowels are simply the high-frequency signs.
- The published 0.87 was an `n_draws=5` lucky sample; honest full enumeration collapses it to 0.784 (sd 0.19).
- Design leak: LB has only 5 vowels, so kv=4 seeds reveal 80% of the positive class; AUC tracks the fraction of
  the answer key revealed (recall@k 0.057).
- The Foundry ran a random-seed null for the frequency-prior regime but NOT for the pivotal clean-seed regime;
  run here it is non-significant (pos p=0.33, pos+sub p=0.13). Leave-one-seed-out unstable (drop-U → 0.469).

**This is the THIRD standing correction to the Foundry** (C1 position→C/V, and now the seed-propagation pillar of
C3). The Foundry's "value layer partly reopened" story rested on position + seed-propagation; both are frequency
artifacts. What survives from the Foundry is only the substitution channel's validity *on LB* (wave-2 C_AUDIT),
which does not transfer to LA.

## The value layer is comprehensively closed on Linear A (every channel audited)
`D1/D2` multi-view fusion: NO frequency-robust phonetic signal on LA (fused vowel-AUC 0.538 p=0.096; residualized
0.450; every config <0.55 after frequency removal, vs the LB control which fires freq-robust at 0.564). `D4`: LA
sits below the minimal-seed threshold — value-blind seed selection recovers nothing (random/shape flat at 0.50,
the measured price of relabeling-invariance), correct seeds need k=4 of 5 vowels to separate from null, and LA has
no secure seeds (SEED_A=0, anchor-derived tops at k=2 {A,I}→{I}). `D5`: a stable anonymous K=2 partition exists
but aligns with vowel/CV only at chance (AMI perm-p 0.14–0.16); its axis is provenance-dispersion + word-initial
morphology, not phonetics. **No phonetic value recovered or assigned anywhere.**

## What DOES survive: a real, modest, anonymous L2/L3 morphology + formula grammar
`E1/E3/E5`: **A- prefixation** is a genuine productive Linear A word-initial affix — it survives the
frequency-matched Holm null (p_holm 0.050), generalizes cross-site on a partition disjoint from Haghia Triada
(p 0.0099), and beats all label-corruption + no-morphology controls (paired p 0.0005; 0.760 vs 0.56 random).
The Foundry/wave-2 "three affixes A-/I-/-JA" is **corrected to one**: `-JA` is HT/tablet-bound and `I-` is
frequency-indistinguishable. `E2`: two clean formula grammars — the ledger register (KU-RO = terminal TOTAL slot,
arithmetic sum-consistency 7/31 exact / 12/31 within 2; KI-RO = mid-text DEFICIT) and the libation register (rigid
anchor order OP<SSR<UNK<IPN<SIR, zero inversions, permutation p 5e-5), in complementary distribution (ledgers on
numeral docs, libation on vessels). `E4` caveat: the morphology compresses training (1165→709 morphemes, −14.2%
DL) but does NOT buy held-out word prediction — even LB's real morphology fails that metric, so it is a
metric-insensitivity result, not evidence against the (control-validated) A- structure.

## Net
Highest claim layer **L2/L3** (anonymous administrative/morphological structure): A- prefixation + two formula
grammars, all value-free. Every value-bearing channel — position, substitution (on LA), cross-script, anchors,
seed-propagation, multi-view fusion — is audited to null on Linear A. All transfer licences **NOT_EARNED**.
