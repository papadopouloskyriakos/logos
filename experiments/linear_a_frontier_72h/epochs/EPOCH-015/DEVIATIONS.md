# EPOCH-015 deviations log (Art. XVII — append-only; prereg d35828be unchanged)

## D1 (2026-07-08, after PC-LB first run) — POSTHOC characterization threshold
The frozen inventory rule R (p<=0.01, n_null=200) yields an EMPTY gold inventory on gold-boundary
LB TEST words (best candidate JO|SUF p=0.0149) -> the preregistered recovery test is VACUOUS
(target empty; F1=0 for all arms; strict-prereg PC verdict = MACHINERY_UNINFORMATIVE / TARGET_VACUOUS).
Deviation: ADD a posthoc scoring pass at p<=0.05 (same machinery, same nulls, applied identically to
gold/frozen/marginalized) + a posthoc better-powered reference target G_full (gold inventory computed
on ALL 11,908 gold words, p<=0.01, n_null=1000; target-side only). Status: POSTHOC_CHARACTERIZATION,
never the preregistered verdict. Decided after seeing gold + marg stats (flagged as such).

## D2 (2026-07-08, after PC-LB first run) — SUPERSEDING marginalized-null construction
The preregistered marginalized null ("null replicate j = mean_k productivity on a FRESH matched
synthetic corpus per sample k") is mechanically ANTI-CONSERVATIVE: averaging K independent synthetic
corpora shrinks null variance ~1/K, while the K observed segmentation samples share ONE real sign
stream (their productivities are strongly correlated); any real-corpus offset then yields p ~ 1/(n+1).
DEMONSTRATED by the controls: 16 marg inventory items vs empty gold target on real LB; 12 items under
the wrong-structure shuffle (both arms should be empty). Correction (applied uniformly BEFORE any LA
run): stream-level null — each null replicate synthesizes the sign STREAM once (i.i.d. sign-unigram,
lengths preserved), then applies the SAME K sampled gap-sets, preserving cross-sample correlation;
for a single frozen segmentation this reduces exactly to the E1 word-level null (frozen/gold arms
unchanged). Original-null outputs remain recorded in data/marginalized_morph/pc_lb.json.
