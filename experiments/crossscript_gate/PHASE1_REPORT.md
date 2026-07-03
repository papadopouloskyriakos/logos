# Phase 1 report — final freeze, external timestamp, and the one-shot run

**Date:** 2026-07-03. **Gate verdict (primary axis, computed mechanically from the persisted
artifact): `REFUTE_LOTO_FRAGILE`.** Secondary axis (descriptive only): `REFUTE`. Nothing under
`paper/` was read or written at any point; all commits pushed.

## 1. Chronology (the discipline, satisfied)

| step | evidence |
|---|---|
| §E rules pre-stated | commit `15c7032` |
| §1 power checks run | `results/phase1_power.json` (secondary DESCRIPTIVE, final N=1; primary stratified bridging **GO re-certified**, power 0.82–0.98 at s=0–3) |
| **Freeze** | commit `23da20d`, `PREREG_FINAL.md` SHA-256 `a74f99e7…f055f` |
| **External timestamp** | **DOI 10.5281/zenodo.21168887**, published **2026-07-03T14:35:02Z**, byte-exact deposit verified (MD5 match); recorded at commit `16f2641` |
| One-shot run | after all of the above; artifact `results/oneshot_gate.json`, SHA-256 `d03a79b08054d7bec11fa2652351b687413ef540388f49c0ded3dab9f6fa5ac9`, wall-clock 1.2 s |

The frozen operative test was carried verbatim from commits `00fb9ea`/`33a3fec` into
`PREREG_FINAL.md` §A (quoted there); the run used the Phase-0.5-certified configuration lineage
(PPMI w2/cds 0.75/SVD d24 seed 0 both sides; Procrustes on train pairs; NN over 73 candidates;
Addendum-B toponym pins), **grid = 1, no tuning step, n_trials = 1 per axis**.

**Execution disclosure:** the first invocation of `oneshot_run.py` crashed on a JSON
serialization bug (numpy bool) AFTER computing but BEFORE printing or persisting any statistic
— zero results were observed. The serializer was fixed (two lines, no analysis code touched)
and the identical frozen deterministic computation re-executed; that execution is the recorded
run. Nothing adaptive occurred between the two.

## 2. Primary axis (h=20 stratified from the 49 eligible, selection seed 20260710)

Held out: DI I KU ME NA NE NI NU O PA PO QA QE RA2 RE RI TA2 TE WA ZA (train = 31).
The seeded draw yielded **2 pinned signs** (of the ~2.2 expected): **I** (via se-to-i-ja: SE,
TO, JA all in training) and **RI** (via su-ki-ri-ta: SU, KI, TA all in training). PA, DI, TE
lost their pins to co-sign masking (I and TE/DI drawn together), PO/NA had none available.

| scoring | observed top-1 | null mean | p (add-one, N=1) | clears (α=0.05) |
|---|---|---|---|---|
| **full** | **0.1000** (2/20) | 0.0122 | **0.0305** | **yes** |
| LOTO −pa-i-to | 0.1000 | 0.0122 | 0.0305 | yes |
| **LOTO −se-to-i-ja** | 0.0500 | 0.0116 | **0.2044** | **NO** |
| LOTO −tu-ri-so | 0.1000 | 0.0122 | 0.0305 | yes |
| LOTO −di-ka-ta(-jo) | 0.1000 | 0.0122 | 0.0305 | yes |
| **LOTO −su-ki-ri-ta** | 0.0500 | 0.0120 | **0.2084** | **NO** |
| toponym-off floor (descriptive) | **0.0000** | 0.0114 | 1.0000 | no |

**Verdict clauses (§H):** (i) full clears (0.0305 < 0.05) ✓; (ii) LOTO-stability FAILS — the
two variants that remove se-to-i-ja or su-ki-ri-ta each lose their single pin and drop to
p ≈ 0.20 ✗; (iii) instrumentation complete (SearchLog n_eff = 4012 = 2 configs + 4000 null
draws + 10 LOTO entries; nulls non-degenerate; banned modules: none) ✓.
**→ `REFUTE_LOTO_FRAGILE`** — a fail-closed negative: the borderline positive rests entirely
on two individual toponym identifications, one sign each; removing either kills it.

Recovered signs (for the record, per §5): **I** (pin; NN rank of true value 15) and **RI**
(pin; NN rank deep). The distributional channel produced **zero** held-out hits — best NN
near-miss: RE at rank 2 (descriptive footnote, not a hit).

## 3. Secondary axis (Cypriot-stable eleven, DESCRIPTIVE per §E.1)

Held out: A DA I NA PA PO RO SA SE TI TO (train = 40); 1 pin (**SA** via tu-ru-sa). Full:
obs 0.0909 (1/11), p = 0.1484 — does not clear; toponym-off floor 0.0000. Descriptive
verdict-equivalent: REFUTE. (PO's Table-6.2 "Not attested?" CM caveat is reported per the
prereg; PO was neither pinned nor NN-recovered.)

## 4. Honest read

The gate worked exactly as designed, and the answer is a disciplined no. Three findings:

1. **The distributional channel carries nothing.** Zero of 31 held-out sign predictions (both
   axes) from PPMI-SVD + Procrustes hit the conventional value; the toponym-off floor sits at
   0.0000 against a 0.0137 chance rate. This is the third independent confirmation of the
   repo's cross-script co-occurrence null (after run_ab cog and DĀMOS scales), now under a
   pre-registered, externally timestamped protocol.
2. **The toponym channel is real but irreducibly thin.** The two pins it delivered are genuine
   word-completion recoveries (I, RI — each predicted from its word's other signs plus the LB
   lexicon, never from its own label), and the full statistic cleared the raw bar (p = 0.0305).
   But each recovery hangs on exactly one place-name identification, and the pre-registered
   leave-one-toponym-out clause — the very condition the Phase-0.5 GO was conditioned on —
   correctly refuses to let a two-identification result stand as gate-cleared. Five toponym
   equations spread over 14 coverable signs simply cannot yield a LOTO-robust positive at
   h=20 with this draw density.
3. **What would change the verdict** (for any future phase, which would need a NEW prereg):
   more independent lexical anchors — each additional sourced toponym/lexeme equation adds
   pins AND redundancy across LOTO variants. The identifiability bottleneck has moved from
   "no signal" to "one-deep signal": the value convention's non-shape support now measurably
   equals the place-name identifications themselves, nothing more. That is a sharper — and
   publishable — form of the identifiability thesis, and it is the NULL-side abstract of the
   prereg (§I.ii, "did not survive toponym removal") verbatim.

No sound value was assigned to any A-only sign; Minoan remains unread; the paper's frozen
claims are untouched.

## 5. Confirmations

- Real held-out labels were compared against predictions exactly once, by the single frozen
  configuration, after the Zenodo DOI existed (§K chronology above).
- No threshold, axis, eligibility rule, or clause was modified after the freeze commit
  `23da20d`; the serializer fix touched no analysis code.
- Grep-clean (§G): the frozen pattern was run over all imported gate modules; every match is a
  numpy `.shape` attribute access, docstring prose, or the banned-modules constant itself —
  zero image/shape feature modules. Fresh-interpreter import check: no banned module loaded;
  runtime check inside the run: clean (recorded in the artifact).
- SearchLog: n_eff = n_logged = 4012; **n_trials = 1 per axis** (no tuning step existed);
  selection rule outcome: not applicable (grid = 1, config-provenance clause).
- Nothing under `paper/` read or written. All commits pushed
  (`15c7032` → `23da20d` → `16f2641` → `9a934e0` → this report).
