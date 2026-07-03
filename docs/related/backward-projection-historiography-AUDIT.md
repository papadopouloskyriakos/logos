# AUDIT — backward-projection-historiography-2026-07-03.md

- **Target**: `docs/related/backward-projection-historiography-2026-07-03.md` (archived deep-research report)
- **Audit date**: 2026-07-03
- **Method**: 5 source-cluster verifier agents (`sm2017-pdf`, `repo-evidence`, `web-companion`, `web-history`, `web-recent`) + 1 completeness critic. Primary sources: the on-disk Steele & Meissner 2017 chapter PDF (`corpus/bronze/steele_meissner_2017/chapter-6.pdf`), the OA accepted manuscript of the companion paper (Meissner & Steele, "Linear A and Linear B: Structural and contextual concerns", Cambridge repository), repo machine evidence (litindex, crossscript gate artifacts, references/digests), and the open web.
- **Recovery caveat**: the workflow's final assembly was lost to a tool error. Results were recovered from the workflow journal (`wf_d8d102ac-532/journal.jsonl`). Only **3 of 5** verifier clusters returned results before the crash: `sm2017-pdf`, `repo-evidence`, `web-companion`. The `web-history` and `web-recent` verifiers were cut off mid-work (no result payload — their transcripts end on a pending tool call), and the **completeness critic never started**. Their assigned claims are listed below as UNAUDITED. Nothing in this document is inferred beyond the recovered journal payloads.

## Verdict tally (recovered clusters only — 21 claims)

| Verdict | n |
|---|---|
| VERIFIED | 12 |
| PARTIALLY | 7 |
| CONTRADICTED | 1 |
| UNVERIFIABLE | 1 |
| UNAUDITED (results lost) | 13 assigned claims across web-history (5) and web-recent (8) |

## Corrections that matter

Every PARTIALLY/CONTRADICTED verdict with its correction, most consequential first.

1. **Misattributed quote — "at least 10 or 11 signs… palaeographical" (CONTRADICTED in sm2017-pdf; PARTIALLY in web-companion).** The quote appears in NEITHER 2017 paper. It is from **Steele 2023, *Exploring Writing Systems and Practices in the Bronze Age Aegean* (Oxbow), ch. 1, p. 8**, ending "…palaeographical **arguments for further correspondences**" (not "comparisons"). The 2017 chapter (p. 98) instead says "Eleven signs can be identified with a high degree of certainty" (a, i, da, na, pa, po, ro, sa, se, ti, to; Table 6.2; si a "good contender"). The companion paper (MS p. 3) says "11 cognate signs with shared value with confidence". Cite accordingly.
2. **"By 2005" is companion-paper wording only — and uncited there (PARTIALLY, sm2017-pdf; caveat, web-companion).** The chapter (p. 95) says "By **now**, due to new finds and better epigraphic study… **about** 64 out of 89" (72%); "2005" appears nowhere in the chapter. The companion paper (MS p. 2) does say "By 2005… 64 out of 89… 72%", but that date carries **no supporting citation** — only the 53/89 = 60% baseline is sourced (Docs² p. 33). Do not attach "By 2005" to the chapter; flag the 64/89 figure as uncited if used.
3. **Packard ratios 2:1 / 3:1 are NOT in S&M 2017 (PARTIALLY, sm2017-pdf).** The chapter (p. 106) gives: 9 random frequency-matched fictitious decipherments; Ventris values yield **5x** as many parallels with **Knossian** Linear B words as the fictitious average; mainland names show no such effect (a confirming negative control). The 2:1 and 3:1 ratios must be sourced to van Soesbergen and Pope & Raison 1978 respectively — both were assigned to the lost `web-history` verifier, so they remain UNAUDITED. No "tenth decipherment with genuine values" is mentioned in the chapter.
4. **Salgarella quoted formulations uncorroborated (PARTIALLY + UNVERIFIABLE, repo-evidence).** "read but cannot understand" and "not unproblematic" appear nowhere in `docs/related/salgarella-2025.md` or the repo. The digest supports the substance (the "reading+ approach": read structurally, decline translation; ~1,400 readable inscriptions) but not the wording — source both externally (SigLA site / Salgarella's public writing) before quoting. The SigLA transliteration-policy quote ("using (approximate) phonetic values (based on comparison with Linear B)") is UNVERIFIABLE from the repo; verify against sigla.phis.me. Also reconcile the co-author surname: report says "Castellano", repo's `docs/data-provenance.md` says "S. Castellan".
5. **Carian externals not from S&M 2017 (correction attached to a VERIFIED item, sm2017-pdf).** The chapter (p. 105 + fn 21) supports only: a/o/s/u retained; sources Schürr 1992 and Adiego 2010. **Ray 1981** and the **1996** Kaunos bilingual date appear nowhere in the chapter and need an independent source — the verifier assigned to them (`web-history`) was lost, so they remain UNAUDITED.
6. **Seven o-signs claim needs narrower wording (PARTIALLY, repo-evidence).** Repo data corroborates **six** (do, mo, no, qo, so, wo) as absent from the homomorph inventory. **jo** is split: listed in the `litindex.py` LB_TRANSFER_SIGNS seed, but zero LA-stream attestations (`anchors_summary.json` "seed_signs_without_la_stream_presence") and no row in `anchors.csv`. Safest wording: "six o-signs absent from the homomorph inventory; jo carried in the conventional AB inventory but unattested in the LA corpus stream". zo is LA-attested and rightly outside the seven. (Note: the companion paper itself does state all seven — see web-companion table — so the seven-sign claim can be cited to it, not to repo evidence.)
7. **The "four pillars" framing is incomplete (PARTIALLY, sm2017-pdf).** The chapter defends the projection along at least **seven** lines: script descent/sign identity (§2), Cypriot stability (§3), shared names incl. toponyms (§4), internal sequence variation (§5), morphological adaptation trends (§7), Packard's statistics (§8), acrophony/ideograms (§9), capped by the context-of-adaptation argument (§10) — §10 is the chapter's "final justification" and is missing from the report.
8. **Sign2Vec venue uncorroborated (PARTIALLY, repo-evidence).** Method/target characterizations of Corazza 2022 (Sign2Vec, Cypro-Minoan), Corazza et al. 2021 (fraction values, J. Archaeol. Sci.), and Luo/Cao/Barzilay 2019 (Ugaritic→Hebrew, Linear B→Greek, not Linear A) all match repo records — but "**PLOS ONE** 2022" and the author order "Corazza, Tamburini, Valério & Ferrara" appear nowhere in the repo; verify externally before citing.
9. **Duhoux caveat can be upgraded (VERIFIED with note, sm2017-pdf).** The 81%/99% sequence-identity figures are verified **as reported by S&M 2017, p. 100** (secondary attribution to Duhoux 1989, 69); primary verification against Duhoux itself is still outstanding.
10. **Docs² quotes: only p. 33 and p. 40 are cited in the chapter.** The "no guarantee" (Docs p. 37) and "wholesale reshuffling" (p. 39) quotes are not from the chapter. The companion paper does quote "a wholesale reshuffling process" citing Docs² p. 39 (fn 10) — partial corroboration; Bennett's "no guarantee" (p. 37) remains unchecked against Ventris & Chadwick 1973 (assigned to the lost `web-history` verifier).

## Cluster: sm2017-pdf (on-disk Steele & Meissner 2017 chapter PDF) — result recovered

| claim | verdict | evidence (compact) | correction |
|---|---|---|---|
| Chapter title + pp. 93-110 as cited | VERIFIED | PDF p. 16 (book p. 93): "From Linear B to Linear A: The problem of the backward projection of sound values"; ends p. 110 (§11 Conclusion). | Author is "Meißner" (ß); report renders "Meissner". |
| Prior arguers Hooker 1975, Olivier 1975, Pope & Raison 1978, Godart 1984, Duhoux 1989 at p. 93 | VERIFIED | p. 93: "Hooker (1975) and Olivier (1975)… first looked at the problem in detail"; all five names/years match. | — |
| 53/89 = 60% and 64/89 = 72%; "By 2005… had risen" | PARTIALLY | p. 95: Docs² (p. 33) table 53/89 = 60%; "By now… has risen to about 64 out of 89" (72%). "2005" nowhere in chapter. | Cite chapter as "by now… about 64/89"; "By 2005" belongs only to the companion paper. |
| Packard §8 (p. 106): 9 fictitious decipherments; 5x parallels; 2:1/3:1 ratios | PARTIALLY | p. 106: "Packard even constructed 9 random… false decipherments"; "five times as many parallels with Knossian Linear B words". 2:1/3:1 absent. | Source 2:1/3:1 to Pope & Raison 1978 / van Soesbergen, not S&M. Mainland-names negative control is in the chapter; "tenth decipherment" is not. |
| Carian §6 (p. 105): a/o/s/u retained; fn cites Schürr, Adiego; Ray 1981 / 1996 in chapter? | VERIFIED | p. 105: "only the signs for a, o, s and u are kept"; fn 21: "Schürr 1992; Adiego 2010". Ray 1981 and "1996" absent; Kaunos bilingual undated. | Restrict S&M attribution to a/o/s/u + fn 21; Ray 1981 and 1996 need an independent source. |
| Duhoux 1989 stats at p. 100: low-80% (3 signs), 99% (4 signs) | VERIFIED | p. 100: "Duhoux (1989, 69)… sequence of 3 signs… low 80% range… 4… 99%"; later "81% and 99%". | Upgrade caveat: verified as reported by S&M p. 100; Duhoux primary still unchecked. |
| Report's §3 quote "at least 10 or 11 signs… palaeographical" is in this chapter | CONTRADICTED | p. 98 reads instead: "Eleven signs can be identified with a high degree of certainty" (a, i, da, na, pa, po, ro, sa, se, ti, to; Table 6.2). | Quote is not in the chapter; attribute the "10 or 11" wording elsewhere (see web-companion: Steele 2023, p. 8). |
| Tables 6.3/6.4 (pp. 101-102): pa-i-to, se-to-i-ja, su-ki-ri-ta; da-i-pi-ta, pa-ra-ne, qa-qa-ru~qa-qa-ro, di-de-ru~di-de-ro | VERIFIED | Table 6.3 (p. 101) and 6.4 (p. 102) contain all listed equations; qa-qa-ru/di-de-ru pairs recur in Table 6.8 (p. 105). | "Phaistos"/"Sybrita" glosses are the report's, not the tables'. |
| Chapter defends along the report's four pillars | PARTIALLY | Four sections exist (§3, §4, §8, §9), but chapter also argues §2 descent, §5 sequence variation, §7 morphology, §10 context of adaptation, §11 conclusion. | State ~seven lines of defense, capped by §10 (missing from the report). |
| Docs² citations in chapter: p. 33 (shared signs) and p. 40 (nwa, fn 10) only | VERIFIED | p. 95 cites Docs² p. 33; p. 96 fn 10 quotes Docs² p. 40 (nwa). "No guarantee" (p. 37) and "wholesale reshuffling" (p. 39) not in chapter. | — |

## Cluster: repo-evidence (repo machine evidence) — result recovered

| claim | verdict | evidence (compact) | correction |
|---|---|---|---|
| Non-shape signal reduces to place-name identifications (REFUTE_LOTO_FRAGILE, toponym-off floor 0.0000, only pins I and RI) | VERIFIED | `experiments/crossscript_gate/results/oneshot_gate.json`: verdict REFUTE_LOTO_FRAGILE; off-axis top1 0.0, p_raw 1.0; full 0.1, p 0.0305; pins I (se-to-i-ja), RI (su-ki-ri-ta); LOTO variants fail. | Nuance: secondary descriptive axis had one further pin, SA via tu-ru-sa (does not clear). DOIs 10.5281/zenodo.21168887 + 21169626 check out. |
| Seven LB o-signs (do, jo, mo, no, qo, so, wo) have no attested LA predecessor per litindex/anchors | PARTIALLY | `litindex.py` LB_TRANSFER_SIGNS lacks DO/MO/NO/QO/SO/WO but INCLUDES JO; `anchors_summary.json` lists JO among "seed_signs_without_la_stream_presence"; no JO row in anchors.csv. | Say: six o-signs absent outright; jo in conventional AB inventory but unattested in LA stream. zo (LA-attested, n=2) rightly excluded. |
| Salgarella "read but cannot understand" / "not unproblematic" supported by `docs/related/salgarella-2025.md` | PARTIALLY | Neither formulation in the digest or repo; digest supports "reading+ approach" (read structurally, decline translation), ~1,400 readable inscriptions. | Source both quotes externally (SigLA site / Salgarella's writing) before quoting as her wording. |
| CITATION_GORILA matches "Godart & Olivier 1976-1985, Études crétoises" (5 vols) | VERIFIED | `litindex.py` lines 52-56: "Recueil des inscriptions en Linéaire A (Études crétoises 21, 1976-1985)"; `docs/data-provenance.md` agrees. | CITATION_GORILA does not itself state "5 vols." or the vol-5/AB-numbering detail. |
| Corazza/Sign2Vec 2022, Corazza et al. 2021 (fractions), Luo/Cao/Barzilay 2019 characterizations consistent with repo | PARTIALLY | `docs/references.md`: Sign2Vec = Cypro-Minoan clustering; Corazza 2021 = fraction values (J. Archaeol. Sci., MiniZinc/Gecode; J=1/2 is Bennett 1950); Luo 2019 = Ugaritic→Hebrew, LB→Greek, "did NOT crack Linear A". | "PLOS ONE 2022" venue and author order "Corazza, Tamburini, Valério & Ferrara" uncorroborated in repo — verify externally. |
| SigLA "plans transliterations using (approximate) phonetic values (based on comparison with Linear B)" per repo records | UNVERIFIABLE | Repo records SigLA only as the sign-level palaeographic database (references.md, data-provenance.md, DESIGN.md); the quoted policy statement appears nowhere. | Verify wording against sigla.phis.me. Also reconcile surname: report "Castellano" vs repo "S. Castellan". |

## Cluster: web-companion (OA companion paper, Meissner & Steele) — result recovered

| claim | verdict | evidence (compact) | correction |
|---|---|---|---|
| "has as its basis an assumption that such a view… must be correct… retained with little modification" | VERIFIED | Accepted MS p. 1 (Cambridge repository bitstream), Introduction; ellipsis correctly elides "of the relationships between the two scripts". | Published pagination (Aegean Scripts, Incunabula Graeca CV, 2017, pp. 99-114) unconfirmed; only the accepted MS is OA. |
| "at least 10 or 11 signs… palaeographical" is in the companion paper | PARTIALLY | Not in the companion paper or the Oxbow chapter. Real source: Steele 2023, *Exploring Writing Systems…*, ch. 1, p. 8; ends "…palaeographical arguments for further correspondences". | Attribute to Steele 2023, p. 8; for the 2017 papers use MS p. 3 ("11 cognate signs with shared value with confidence") or chapter p. 98. |
| "the consistency in the use of to in these place names strongly suggests… closely matching values" | VERIFIED | MS p. 6, O-vowel signs section (pa-i-to, se-to-i-ja); fn 14 "Steele and Meißner forthcoming". | Full ending is "closely matching values for those signs"; "to" italicized. Published page unconfirmed. |
| Companion paper phrases the rise as "By 2005… 64 out of 89… 72%" | VERIFIED | MS p. 2: "By 2005, due to new finds and better epigraphic study, this figure had risen to 64 out of 89". Fn 3 (Docs² p. 33) supports only the 53/89 baseline. | The 2005 date carries no citation at all in the paper — note this if citing. |
| O-series reassignment hypothesis attributed to Palaima & Sikkenga 1999; S&M argue against | VERIFIED | MS pp. 3-5: "no attested Linear A sign corresponding to do, jo, mo, no, qo, so or wo"; quotes Palaima & Sikkenga 1999, 603-4; "a wholesale reshuffling process" (fn 10 = Docs² p. 39); argues the frequency reading is "much more plausible". | — |

## Cluster: web-history — RESULT LOST (agent truncated mid-work; no verdicts recovered)

The journal has a `started` entry but no `result`; the transcript ends on a pending WebFetch call. The following assigned claims are **UNAUDITED** — treat all as unverified:

1. Evans, Scripta Minoa I (1909) p. 38 — "contain a large proportion of common elements" (Heidelberg digitization check).
2. Ventris & Chadwick, Documents — "wholesale reshuffling" (reported p. 39) and Bennett's "no guarantee that the same value is assigned" (reported p. 37) against the 1956/1973 editions. (Partially mitigated: the companion paper quotes "a wholesale reshuffling process" citing Docs² p. 39 — see web-companion table; the Bennett p. 37 quote remains fully unchecked.)
3. Packard, Minoan Linear A (1974) — publication details, Harvard PhD year, fictitious-decipherment description, van Soesbergen "2:1", Pope & Raison 1978 "3:1", page-range variants 112-114 vs 113-115.
4. Carian — Ray 1981 as breakthrough, Adiego/Schürr in the 1990s, Kaunos bilingual discovery year (1996), most Carian values differ from Greek look-alikes.
5. GORILA vol. 5 (1985) — unified AB numbering up to AB 131.

## Cluster: web-recent — RESULT LOST (agent truncated mid-work; no verdicts recovered)

The journal has a `started` entry but no `result`; the transcript ends on an unanswered tool result. The following assigned claims are **UNAUDITED** — treat all as unverified:

1. Younger's Linear A site — launch year ~2000, GORILA-based; which toponym identifications (ku-do-ni, di-ka-te, i-da, tu-ri-so, wi-na-du, su-ki-ri-ta, pa-i-to, se-to-i-ja) actually appear.
2. SigLA transliteration-policy wording (also UNVERIFIABLE from repo evidence — see repo-evidence table).
3. Steele 2023/2024 (Oxbow) ch. 1 title verification. (Partially mitigated: web-companion independently located Steele 2023 ch. 1, p. 8 as the true source of the "10 or 11 signs" quote.)
4. Computational Linguistics 50(2) (2024) "systematic review" — existence, authors, Linear A coverage; Nepal & Perono Cacciafoco (2024) — real? venue?
5. Palaima & Sikkenga 1999 — exact venue and the "provisional"/"conventionally transcribed" and "essential core" quotes.
6. Davis 2014 — vowel frequencies a 39.3% / i 25.7% / u 18.1% / e 14% / o 2.9%.
7. Facchetti 1999, Kadmos 38 — real? topic?
8. Gareth Owens mainstream-reception characterization.

## Completeness critic

**MISSING.** The completeness critic never started (no `started` or `result` entry in the workflow journal); its findings were lost with the workflow crash. No completeness assessment of the archived report exists. The nearest recovered substitute is the sm2017-pdf verifier's four-pillars finding (the report omits the chapter's §2, §5, §7 and — most importantly — §10 "The context of adaptation" and §11); a dedicated completeness pass over both 2017 papers and the report's Key Findings has NOT been performed and should be re-run before the report is used for citation harvesting.

---

Rule for consumers: cite nothing from the archived report without checking this audit; VERIFIED items may be cited with the evidence's page numbers; UNVERIFIABLE items need primary acquisition first.
