# LOGOS-2 data licences and terms (preflight scout, 2026-07-10)

Machine-readable inventory: `DATA_INVENTORY.csv`. Anything UNSTATED/unclear is treated as NON-REDISTRIBUTABLE until clarified; licensed raw data never leaves gitignored dirs.

| asset | licence/terms | redistributable |
|---|---|---|
| corpus/bronze/MANIFEST.txt | n/a (metadata) | yes |
| corpus/silver/inscriptions.json | upstream has no open licence (GORILA/lineara.xyz-derived) | no |
| corpus/silver/inscriptions_structured.json | same as inscriptions.json — no open upstream licence | no |
| corpus/silver/inventory_syllabograms_{raw,conservative,exploratory}.json (+ .stream.json) | derived from unlicensed GORILA lineage | no |
| corpus/silver/signs_ontology.json | derived from unlicensed GORILA lineage | no |
| corpus/silver/literature_index.json | factual claim excerpts; underlying papers variously licensed | unclear |
| corpus/gold/ | n/a | no (would inherit silver lineage) |
| corpus/derived/post_gorila_additions/{kn_zb_36a-d,ph_chalara_2017,the_zb_14,vry_za_4}.json | minimal factual excerpts from a CC BY-NC-SA 4.0 article | yes (committed to repo; tracked in git) |
| corpus/bronze/younger_lineara/ | UNSTATED (personal scholarly webpage, no licence) | no |
| corpus/bronze/sigla_browse_2026/ | CC BY-NC-SA 4.0 (site footer, verbatim per PROVENANCE.md and docs/sigla_decode.md) | technically NC-SA-permitted, but house policy = NOT redistributed |
| corpus/bronze/linearb/damos/items.jsonl | CC BY-NC-SA 4.0 (content); GPL-3.0 (software) — personal academic non-commercial use | no (house policy; NC terms) |
| corpus/bronze/linearb/linear_b-greek.cog | distributed in a GPL-3.0 repo (data terms not separately stated) | unclear (repo is GPL-3.0 but data provenance is Tamburini's paper) |
| corpus/bronze/ugaritic/{uga-heb.gold,uga-heb.full,uga-heb.noisy}.cog | UNSTATED for the data; host repos GPL-3.0 (CSA) / NeuroDecipher licence not recorded | unclear |
| corpus/bronze/code/CSA_OptMatcher/ (incl. data/*.cog) | GPL-3.0 (LICENSE in repo) | yes (GPL-3.0; data terms unclear) |
| corpus/bronze/code/EditDistanceWild/ | GPL-3.0 | yes |
| corpus/bronze/hebrew/bhsa/ | data CC BY-NC 4.0 (README License section, verbatim); repo code MIT | NC only; house policy: no |
| corpus/bronze/palaeo/{linA_codepoint_map.json,results_palaeo.json} | UNSTATED (lineara.xyz has no open licence) | no |
| corpus/bronze/sign_images/ | font caveat recorded in manifest: 'UFAS; tightened 2024; gitignored bronze, research-only, not redistributed' | no |
| corpus/bronze/fonts/ | Aegean = UFAS (tightened 2024, research-only per manifest caveat); Noto = SIL OFL 1.1 | Noto yes; Aegean unclear/no |
| corpus/bronze/salgarella_2020/ | personal use only (verbatim: 'personal use; GITIGNORED, never redistributed, never committed') | no |
| corpus/bronze/steele_meissner_2017/chapter-6.pdf | author self-archival permission post-embargo; no reuse licence stated | no |
| corpus/bronze/delfreo_rapport_koronowesa/ | CC BY-NC-SA 4.0 (journal-stated) | NC-SA-permitted but house policy: no |
| corpus/bronze/kanta_etal_2024_anetaki/ | CC BY-NC-SA 4.0 (article page, verbatim class) | NC-SA-permitted but house policy: no |
| corpus/bronze/anetaki_context/henkel_margaritis_2022_religions.pdf | CC BY (open access) | yes (CC BY) |
| corpus/bronze/kentro_newsletters/Kentro_2021_WEBSITEviewing.pdf | UNSTATED (freely distributed newsletter) | unclear |
| corpus/bronze/prepub_prediction_2024_ivory_circle/ | UNSTATED | no |
| corpus/bronze/rjabchikov_2025_sceptre/ | (c) author/publisher; open archive posting; no reuse licence | no |

## Scout narrative

Inventory of every data asset under /home/claude-runner/gitlab/n8n/logos/corpus/ (read-only scout, 2026-07-10). Layout: bronze = raw/licensed acquisitions (17 subdirs, ~1.9G dominated by hebrew/bhsa 1.7G and salgarella_2020 136M), silver = 11 normalized JSON files (headline: 1,341 LA inscriptions across 52 sites, sign inventory V=92 conservative / N~5,171 tokens), gold = EMPTY (generated duckdb/parquet absent, rebuild from silver), derived = 4 committed post-GORILA inscription additions sourced from the Del Freo rapport. Everything under corpus/bronze/* and corpus/silver/*.json is gitignored by design (invariant #10: licensed raw data never committed); the only tracked corpus files are the two Noto Linear A/B fonts, corpus/derived/post_gorila_additions/*.json, and the .gitkeep placeholders — force-added exceptions. Provenance discipline is strong: 10 of the bronze dirs carry a PROVENANCE.md with SHA-256s and verbatim licence statements; MANIFEST.txt covers only the 4 fetch_ugaritic.py .cog downloads. DAMOS Linear B wordforms answer: scripts/cross_script/data.py:65 defines DAMOS_ITEMS = corpus/bronze/linearb/damos/items.jsonl (5,840 tablet records, 2.9M, harvested from damos.hf.uio.no by scripts/fetch_damos.py; load_b_damos() parses ~13,562 syllabic wordforms; content CC BY-NC-SA 4.0, gitignored, not redistributed). SigLA licence answer: CC BY-NC-SA 4.0, stated verbatim in corpus/bronze/sigla_browse_2026/PROVENANCE.md ('dataset and drawings under CC BY-NC-SA 4.0 (footer on every page)') and docs/sigla_decode.md; the decoded snapshot yields 802 documents / 376 signs and is kept gitignored per house policy; the preprints additionally state the blanket policy that GORILA-, SigLA-, lineara.xyz- and DAMOS-derived corpora are never redistributed. Known-decipherment analogue data for calibration: LB-Greek (920 pairs), Cypriot-Greek (694), Ugaritic-Hebrew (2,215 gold / 43,952 full / 4,442 noisy), Luvian-Hittite (136), Phoenician-Ugaritic (164), all in .cog format under bronze/{linearb,ugaritic,code/CSA_OptMatcher/data}, plus the GPL-3.0 CSA_OptMatcher + EditDistanceWild code (serial CSA path broken — parallel only). Anetaki (KN Zg 57/58) cluster: overview article, context papers, and two quarantined registry objects (Chiapello prediction, Rjabchikov fringe reading) are archived and gradable, but the actual ~119-sign inscription remains unpublished pending Anetaki II. Per instruction, no path containing 'seal' was opened; in fact `find corpus -ipath '*seal*'` returns nothing, so no corpus asset was skipped on that ground. The relevant_to field is best-effort by function because the experiment IDs E201-E211 do not exist anywhere in the working tree (grep of experiments/, docs/, *.md/*.py/*.json found zero matches).

## Gaps

- E201-E211 are not defined anywhere in the repo working tree (grep across *.md/*.py/*.json, experiments/, docs/ found no matches) — the relevant_to mapping is therefore functional/best-effort, not ID-exact; the caller should supply the E201-E211 definitions or point at the branch that holds them
- corpus/gold/ is empty (only .gitkeep): the queryable gold store must be regenerated from silver before any experiment that expects it
- All of bronze and silver is gitignored: a fresh clone has NO corpus data; reacquisition depends on the per-dir PROVENANCE.md URLs (Younger's pages now exist ONLY as Wayback captures; DAMOS needs re-harvesting via scripts/fetch_damos.py; SigLA snapshot was a one-time polite pass)
- The Anetaki sceptre inscription itself (KN Zg 57/58, ~119 signs, longest known LA text) is NOT in any corpus asset — Kanta et al. 2024 prints no transliterated sequences; full edition (Anetaki II, INSTAP, forthcoming) is the blocking dependency for the frozen prospective programme
- Chiapello 2024 PDF was never acquired (Academia.edu login-gated); only the archived public page (title/date/abstract) is held — sufficient to grade the prediction but not to index its full text
- Per memory, Ariadne-2025 Anetaki preliminary material is published but NOT ingested into silver — a corpus-completeness delta
- corpus/bronze/palaeo/ has no PROVENANCE.md (only dir in bronze with data but no provenance file besides code/, fonts/, sign_images/ whose provenance lives in manifest.json or upstream repos)
- Licence of the NeuroDecipher-sourced uga-heb.full.cog data is not recorded (MANIFEST gives only the URL); redistribution status unclear
- Kentro newsletter has no stated formal licence (freely-distributed INSTAP copy) — marked UNSTATED
- Aegean.ttf carries a UFAS licence caveat ('tightened 2024; research-only') — sign_images derived from it inherit the research-only restriction
- sigla database.js is an undecoded OCaml Marshal blob in bronze; the decoded 802-doc/376-sign JSONs sit alongside it, but per docs/sigla_decode.md both are treated as licensed vendor-derived (CC BY-NC-SA) and must stay gitignored
- No path containing 'seal' exists under corpus/ (verified with find), so the do-not-open constraint excluded nothing; note the frozen 'Anetaki seal' prospective registration lives under experiments/, outside this inventory's scope, and was not opened
- Silver counts here (1,341 inscriptions) match CLAUDE.md but were re-derived by reading the JSON directly; per invariant #12 any published figure should come from the counting scripts, not this scout's read
