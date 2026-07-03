# Revision-queue: two-attempt synthesis — the cross-script value-recovery gate (final, N=2)

**Status:** revision material only; the paper stays byte-frozen through TACL review. Companion
to `crossscript_gate_arc.md` (this note carries the referee-facing paragraphs; that one the
inventory). Date: 2026-07-03. The attempt ledger is CLOSED at N=2.

## The arc in one table

| attempt | design | bar | verdict | promise DOI (UTC) | results DOI (UTC) |
|---|---|---|---|---|---|
| Phase 1 | 5 toponym anchors, stratified h=20 | raw p<0.05 | REFUTE_LOTO_FRAGILE | 10.5281/zenodo.21168887 (14:35:02) | 10.5281/zenodo.21169626 (14:59:59) |
| Phase 2 | 8 vetted anchors (content-blind selection, LOTO-certified design) | corrected p<0.02532 (Šidák, N=2) | REFUTE | 10.5281/zenodo.21173639 (16:48:50) | 10.5281/zenodo.21174173 (17:00:29) |

## The near-miss paragraph (ready to adapt)

> Phase 2's full statistic reached p = 0.0255 against the pre-committed two-attempt bar of
> 0.02532 — a miss of 0.0002. This near-miss carries no counterfactual regret: at the
> unadjusted single-attempt bar the same result dies on the conjunctive leave-one-anchor-out
> clause (both pin-carrying variants p ≈ 0.21), so the outcome is negative under either bar
> choice. The corrected bar was frozen before execution (commit
> `0aeaee8aa4c5d5c8e2120d38c57c8013def5e067`, externally timestamped 16:48:50Z), with the veto
> alternative documented and declined; no post-hoc bar selection occurred in either direction.

## The central finding: the s≈0 / 0.45 diagnosis (ready to adapt)

> The Phase-2 design was certified before execution at LOTO-survival power 0.82 for planted
> signal strength s = 3. The corpus, however, operates at s ≈ 0: the distributional channel
> recovered 0.0000 of held-out values — its fourth consecutive independent null across two
> corpus scales and two protocols — leaving the place-name word-completion channel as the
> convention's entire non-shape support. At s ≈ 0 the certified LOTO-survival is 0.45: with
> the full strict-tier anchor supply of the published literature, at current corpus scale, the
> toponym channel delivers a robustness-surviving validation less than half the time. The
> two nulls are therefore power-bounded and evidential — they locate the corpus's true
> operating point; they do not assert the backward projection is false.

## The 4/4-pins observation (POST-HOC DESCRIPTIVE POOLING — flag stays attached)

> Pooling across both attempts — a post-hoc, descriptive observation, not a pre-registered
> test — every clean word-completion the gates produced (I and RI in Phase 1; TO and SU in
> Phase 2; 4 of 4) returned the sign's conventional Linear B value. Two truths must be stated
> together: this is accumulating consistency evidence for the convention on toponym-covered
> signs, and it never gate-validated because every instance stood exactly one identification
> deep. The observation motivates supply acquisition; it licenses no claim.

## The Phase-1 certification-gap disclosure (defensive voice, pre-written for referees)

> Phase 1's power certification was run against the raw-bar detection event only; the
> conjunctive LOTO-survival event — the quantity its clause (ii) actually gated — was first
> certified one phase later, when the Phase-2 quota sweep measured it at 0.65–0.78 for
> five-anchor designs: below the band. Phase 1 was therefore under-certified for its own
> robustness clause, and its REFUTE_LOTO_FRAGILE outcome is exactly what an honest gate
> produces in that regime. We disclose this ordering plainly; the Phase-2 design closed the
> gap by certifying the conjunctive event on the fielded geometry before its freeze.

## The procurement-spec conclusion (ready to adapt)

> What moves this number is not protocol work — the strict-tier census of published anchors is
> near exhaustion — but epigraphic supply: new excavated attestations of anchor words in fresh
> contexts, or an independent non-toponym channel. A concrete candidate exists: the Anetaki
> ivory sceptre from the Knossos Cult Center (KN Zg 57–58, ~119 signs, the longest known
> Linear A inscription, a cult-context genre where formula words and toponyms are plausible),
> whose ~16 sign-groups remain unpublished as of July 2026 (overview: Kanta, Nakassis, Palaima
> & Perna 2024; transliterations deferred to Kanta (ed.), *Anetaki II*, INSTAP Academic Press,
> forthcoming). The census re-scan is pre-built
> (`experiments/crossscript_gate/phase3/GAP_DELTA.md`) and runs mechanically the day the
> edition publishes.

## Tooling item

The rank-lookup reporting interface crashed once in each phase (post-computation,
pre-observation; fixed and disclosed both times — Phase 1: numpy-bool serialization; Phase 2:
similarity-matrix-vs-rank-order return contract). Fixed at the interface level with regression
tests covering both crash shapes (see the §4 housekeeping commit); recorded artifacts and
statistics are untouched.

## The selected anchors under Salgarella 2020 (descriptive; no statistic recomputed; ledger closed)

Provenance metadata about the FROZEN Phase-1/Phase-2 anchor sets, mapped onto the current
palaeographic authority (Salgarella 2020, Tables 2–3 pp. 35–36; key p. 34: dark blue =
"homomorphic and also likely homophone", light blue = "homomorphic"):

| anchor (P1 = first five; P2 = all eight) | covered signs | her grade per sign |
|---|---|---|
| pa-i-to | PA I TO | all likely-homophone |
| se-to-i-ja | SE TO I JA | SE TO I likely-homophone; **JA homomorphic-only** |
| tu-ru-sa | TU RU SA | all likely-homophone |
| di-ki-te | DI KI TE | all likely-homophone |
| su-ki-ri-ta | SU KI RI TA | all likely-homophone |
| ku-ta (P2, Younger) | KU TA | TA likely-homophone; **KU homomorphic-only** |
| ku-ni-su (P2, Younger) | KU NI SU | NI SU likely-homophone; **KU homomorphic-only** |
| sa-ra₂ (P2, Younger) | SA RA2 | SA likely-homophone; **RA2 homomorphic-only** |

Ready-to-adapt sentence: *Every sign of every anchor fielded in either attempt is at minimum
"homomorphic" under Salgarella's (2020) analysis, and 14 of the 17 covered signs carry her
strongest grade ("homomorphic and also likely homophone"); she separately endorses the five
S&M place/name equations as "reasonably secure readings" (p. 33) and grades all eleven
Cypriot-stable signs at the strongest tier — i.e., the gates failed on anchor SUPPLY and
corpus scale, not on the philological quality of the anchors fielded.* The only recorded
tension is internal to her treatment (JU: "ju?" in Table 2 vs undeciphered *65 in Table 4),
and JU was never a selected anchor sign.
