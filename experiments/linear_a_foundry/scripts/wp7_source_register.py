#!/usr/bin/env python3
"""wp7_source_register.py — Source Audit Sweep for the Linear A decipherment foundry.

Builds a machine-readable SOURCE REGISTER of every machine-usable + scholarly source that
logos holds (corpus/bronze/*, corpus/silver/*, corpus/derived/*) or cites for the Linear A
problem, and classifies each by DEPENDENCY CLUSTER.

THE ANALYTICAL POINT (non-circularity, foundry KEY): almost every *phonetic* reading of
Linear A descends from ONE lineage — GORILA (Godart & Olivier 1976-85) transliterates each
homomorphic Linear A sign with the phonetic value of its Linear B look-alike, and those
values come from Ventris & Chadwick's 1953 Linear B decipherment. A source is "genuinely
independent" ONLY if the information it contributes does NOT ride on that value transfer:
raw sign palaeography, internal distributional/structural analysis, archaeological context,
general (non-Aegean) computational-decipherment method, or an independently-deciphered
sister script (the Cypriot Syllabary was cracked by G. Smith in the 1870s, before Ventris).

Every record is grounded in a file actually present under corpus/ or a citation actually
recorded in docs/ ; nothing is fabricated. Sources not held are marked UNAVAILABLE with the
information they *would* add. Deterministic (seed 20260708); pure stdlib.

Outputs (data/):
  wp7_source_register.csv    — the register, one row per source (>=40 rows)
  wp7_source_register.json   — same + provenance-present flags + cluster tallies
  wp7_source_register_summary.txt — human-readable audit summary
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from datetime import date

SEED = 20260708
REPO = "/home/claude-runner/gitlab/n8n/logos"
BRONZE = os.path.join(REPO, "corpus", "bronze")
SILVER = os.path.join(REPO, "corpus", "silver")
DERIVED = os.path.join(REPO, "corpus", "derived")
OUTDIR = os.path.join(
    "/home/claude-runner/gitlab/n8n/logos-linear-a-decipherment-foundry",
    "experiments", "linear_a_foundry", "data",
)

# ---------------------------------------------------------------------------
# Dependency clusters. `independent` = NOT derived from the GORILA/Ventris
# homomorphic phonetic-value transfer.
# ---------------------------------------------------------------------------
CLUSTERS = {
    "L_GORILA_VENTRIS": dict(independent=False, desc=(
        "The single homomorphic phonetic-value lineage: GORILA transliteration assigns "
        "Linear A signs the Linear B value of their look-alike; LB values are Ventris & "
        "Chadwick 1953. Every LA phonetic reading built on the GORILA transcription lives "
        "here. This is the lineage non-circularity must hold OUT of LA-side model inputs.")),
    "L_LB_DECIPHERMENT": dict(independent=False, desc=(
        "Deciphered Linear B (Ventris lineage) used ONLY as known-truth grading, never as an "
        "LA-side model input. DAMOS wordforms + LB->Greek cognate data live here.")),
    "L_LA_PALAEOGRAPHY": dict(independent=True, desc=(
        "Sign SHAPES and their classification, independent of any phonetic value: GORILA "
        "drawings-as-shapes, SigLA, sign images, Salgarella's combinatory taxonomy. A "
        "genuinely independent channel (shape != sound).")),
    "L_LA_STRUCTURE": dict(independent=True, desc=(
        "Internal distributional / structural readings that DO NOT assign phonetic values: "
        "the KU-RO/KI-RO accounting logograms, numeral & fraction systems, word-order (VSO), "
        "affix morphology. Rides on GORILA SEGMENTATION but not on the value transfer.")),
    "L_ARCHAEOLOGY": dict(independent=True, desc=(
        "Primary material / excavation context: find reports, archaeobotany, deposit context. "
        "Physically independent of any reading.")),
    "L_COMPUTATIONAL_METHOD": dict(independent=True, desc=(
        "General (non-Aegean) automatic-decipherment method + ML-for-ancient-languages "
        "engineering. Independent of Linear A specifics.")),
    "L_SISTER_SCRIPT": dict(independent=True, desc=(
        "Related Aegean/Cypriot scripts as comparanda. The Cypriot Syllabary was deciphered "
        "independently of Ventris (G. Smith, 1870s), so its values are an independent anchor; "
        "Cretan Hieroglyphic and Cypro-Minoan are structurally related but value-undeciphered.")),
    "L_SEMITIC_DATA": dict(independent=True, desc=(
        "Ugaritic<->Hebrew cognate training data for the cross-script CSA harness. Independent "
        "language-pair data; used to VALIDATE the method, never as an LA input.")),
    "L_FRINGE_REGISTRY": dict(independent=False, desc=(
        "Quarantined / registry objects: fringe 'decipherments' and dated pre-publication "
        "predictions. Indexed so a model regurgitating them is caught; NEVER evidence. Most "
        "read the GORILA transliteration, so tagged non-independent.")),
}

# ---------------------------------------------------------------------------
# The register. rel = a path (relative to REPO) whose existence is verified at
# runtime to set provenance_present; None => not held in-repo (UNAVAILABLE or CITED_ONLY).
# ms = machine_readable in {yes, partial, no}
# ing = ingestion_status in {INGESTED_MACHINE, PDF_IN_HAND, TEXT_EXTRACTED,
#        ARCHIVED_PAGE, CODE_IN_REPO, CITED_ONLY, UNAVAILABLE}
# ---------------------------------------------------------------------------
R = []
def add(**k): R.append(k)

# ---- Machine-readable corpus / data assets (in-repo) -----------------------
add(source_id="SRC-GORILA", type="corpus_edition", cluster="L_GORILA_VENTRIS",
    citation="L. Godart & J.-P. Olivier, Recueil des inscriptions en Lineaire A (GORILA), "
             "Etudes cretoises 21, 1976-1985.",
    edition_lineage="GORILA (the critical edition; primary autopsy of the tablets)",
    ms="partial", ing="INGESTED_MACHINE", rel="corpus/silver/inscriptions_structured.json",
    new_information="The canonical corpus + sign inventory. All logos LA sequences descend "
             "from it; its transliteration is what fixes homomorphic values.")
add(source_id="SRC-SILVER-LA-WORDS", type="dataset", cluster="L_LA_PALAEOGRAPHY",
    citation="logos silver Linear A, inscriptions_structured.json, GORILA word-segmented "
             "stream (t=='word'): 1,341 inscriptions / 3,147 word tokens (mean 1.84 signs).",
    edition_lineage="GORILA -> logos silver normalization (word units, the WP2 preferred unit)",
    ms="yes", ing="INGESTED_MACHINE", rel="corpus/silver/inscriptions_structured.json",
    new_information="Word-segmented LA sign sequences — the primary modelling substrate "
             "(word units beat load_a()'s 539 packed inscriptions: AUC 0.76 vs 0.685).")
add(source_id="SRC-SIGNS-ONTOLOGY", type="dataset", cluster="L_LA_PALAEOGRAPHY",
    citation="logos signs_ontology.json — sign classes, allographs, AB-numbering.",
    edition_lineage="GORILA/AB numbering -> logos ontology",
    ms="yes", ing="INGESTED_MACHINE", rel="corpus/silver/signs_ontology.json",
    new_information="Sign-class / allograph structure (shape level), used to scope parameters.")
add(source_id="SRC-SIGLA", type="database", cluster="L_LA_PALAEOGRAPHY",
    citation="E. Salgarella & S. Castellan, SigLA: The signs of Linear A, a palaeographical "
             "database, https://sigla.phis.me/ (CC BY-NC-SA 4.0). Snapshot 2026-07-03.",
    edition_lineage="Built FROM GORILA corpus (all GORILA tablets present, 2021-08-24 changelog) "
             "+ post-GORILA additions; palaeographic drawings are new autopsy work",
    ms="yes", ing="INGESTED_MACHINE", rel="corpus/bronze/sigla_browse_2026/sigla_documents.json",
    new_information="802 documents / 376 signs with glyph-level bounding boxes and hand drawings "
             "— an INDEPENDENT palaeographic channel (shape, not sound). Decoded to JSON.")
add(source_id="SRC-DAMOS-LB", type="database", cluster="L_LB_DECIPHERMENT",
    citation="DAMOS (Database of Mycenaean at Oslo), Linear B — 13,562 wordforms; "
             "loaded via scripts.cross_script.data.load_b_damos().",
    edition_lineage="Ventris & Chadwick 1953 decipherment -> DAMOS digital edition",
    ms="yes", ing="INGESTED_MACHINE", rel=None,
    new_information="Deciphered LB word corpus — the known-truth C/V + morphology grading side. "
             "GRADE ONLY on the LA problem (non-circularity).")
add(source_id="SRC-LINB-GREEK-COG", type="dataset", cluster="L_LB_DECIPHERMENT",
    citation="linear_b-greek.cog (Tamburini CSA_OptMatcher data) — LB->Greek cognate pairs.",
    edition_lineage="Ventris 1953 -> Tamburini CSA benchmark set",
    ms="yes", ing="INGESTED_MACHINE", rel="corpus/bronze/linearb/linear_b-greek.cog",
    new_information="LB->Greek gold cognate pairs — the primary analog for the CSA sufficiency "
             "sweep (LB->Greek at its chance floor at LA scale).")
add(source_id="SRC-UGA-HEB-COG", type="dataset", cluster="L_SEMITIC_DATA",
    citation="Ugaritic<->Hebrew cognate sets: uga-heb.gold.cog / .noisy.cog / .full.cog "
             "(Tamburini CSA_OptMatcher + Luo NeuroDecipher).",
    edition_lineage="Independent Semitic language-pair data (not Aegean)",
    ms="yes", ing="INGESTED_MACHINE", rel="corpus/bronze/ugaritic/uga-heb.gold.cog",
    new_information="Known-answer cross-script training pair — validates that the CSA/matcher "
             "detector fires when the signal is real. Independent of Linear A.")
add(source_id="SRC-SIGN-IMAGES", type="dataset", cluster="L_LA_PALAEOGRAPHY",
    citation="logos sign_images/ — linA, linB and damaged glyph rasters + manifest.json.",
    edition_lineage="GORILA/Unicode glyph shapes",
    ms="yes", ing="INGESTED_MACHINE", rel="corpus/bronze/sign_images/manifest.json",
    new_information="Per-sign glyph images (visual channel) for LA and LB; shape-level.")
add(source_id="SRC-LINA-CODEPOINTS", type="dataset", cluster="L_LA_PALAEOGRAPHY",
    citation="palaeo/linA_codepoint_map.json + Unicode Linear A block (U+10600-1077F); "
             "Noto/Aegean fonts in corpus/bronze/fonts/.",
    edition_lineage="Unicode Aegean encoding (from GORILA/Younger sign lists)",
    ms="yes", ing="INGESTED_MACHINE", rel="corpus/bronze/palaeo/linA_codepoint_map.json",
    new_information="Codepoint<->AB-number mapping + rendering fonts; enables glyph rendering "
             "and normalization.")
add(source_id="SRC-YOUNGER-TEXTS", type="website", cluster="L_GORILA_VENTRIS",
    citation="J. G. Younger, Linear A Texts & Inscriptions in phonetic transcription (KU "
             "personal site), HTtexts + misctexts + religioustexts; Wayback 2023 captures.",
    edition_lineage="GORILA editions -> Younger's phonetic (GORILA-value) transcription",
    ms="yes", ing="ARCHIVED_PAGE", rel="corpus/bronze/younger_lineara/HTtexts.txt",
    new_information="Full LA text transliterations in one place + libation-formula segmentation. "
             "SECONDARY pointer to primary editions; uses GORILA values (same lineage).")
add(source_id="SRC-YOUNGER-LEXICON", type="website", cluster="L_GORILA_VENTRIS",
    citation="J. G. Younger, Linear A Lexicon (last update 2023-08-07), Wayback capture.",
    edition_lineage="GORILA/Ventris values -> Younger lexicon + place-name identifications",
    ms="yes", ing="ARCHIVED_PAGE", rel="corpus/bronze/younger_lineara/lexicon.txt",
    new_information="Word list + toponym identifications (PA-I-TO=Phaistos, SU-KI-RI-TA=Sybrita, "
             "DI-KI-TE=Mt Dikte, ...). Toponym anchors ride on GORILA phonetic values.")
add(source_id="SRC-YOUNGER-BIBLIO", type="website", cluster="L_LA_STRUCTURE",
    citation="J. G. Younger, Linear A Bibliography from 1980, Wayback capture 2024-01-27.",
    edition_lineage="secondary bibliographic index",
    ms="yes", ing="ARCHIVED_PAGE", rel="corpus/bronze/younger_lineara/biblio.txt",
    new_information="Resolves the author-year citations used across the LA text lists — a "
             "bibliographic backbone (independent index, not a reading).")
add(source_id="SRC-LITINDEX", type="dataset", cluster="L_FRINGE_REGISTRY",
    citation="logos literature_index.json — 93 published/quarantined LA sign-value & reading "
             "claims (litindex.py L_known / L_not_indexed partition).",
    edition_lineage="aggregates GORILA transfers + Semitic + structural + fringe claims",
    ms="yes", ing="INGESTED_MACHINE", rel="corpus/silver/literature_index.json",
    new_information="The decontamination index: what has been PUBLISHED, so regurgitation is "
             "caught and can never count as discovery. Spans multiple lineages by design.")
add(source_id="SRC-CSA-OPTMATCHER", type="code", cluster="L_COMPUTATIONAL_METHOD",
    citation="F. Tamburini, CSA_OptMatcher (Combinatorial Sign Assignment optimal matcher), "
             "vendored in corpus/bronze/code/.",
    edition_lineage="independent computational method (combinatorial optimization)",
    ms="yes", ing="CODE_IN_REPO", rel="corpus/bronze/code/CSA_OptMatcher/CSA_OptMatcher.py",
    new_information="The CSA solver used for the sufficiency sweep. NOTE: serial path "
             "(processes=1) is BROKEN — always run parallel (forked isolation).")
add(source_id="SRC-EDITDISTWILD", type="code", cluster="L_COMPUTATIONAL_METHOD",
    citation="EditDistanceWild — CUDA/CPU wildcard edit-distance kernel, vendored.",
    edition_lineage="independent computational method (string alignment)",
    ms="yes", ing="CODE_IN_REPO", rel="corpus/bronze/code/EditDistanceWild/editdistance.cpp",
    new_information="Wildcard edit-distance primitive for the matcher (built .so present).")
add(source_id="SRC-POST-GORILA-ADD", type="dataset", cluster="L_LA_STRUCTURE",
    citation="logos corpus/derived/post_gorila_additions/ — hand-audited post-GORILA finds "
             "(KN Zb 36a-d, PH Chalara 2017, THE Zb 14, VRY Za 4) with editorial-mark fidelity.",
    edition_lineage="Del Freo 2024 / primary editions -> logos structured extraction",
    ms="yes", ing="INGESTED_MACHINE", rel="corpus/derived/post_gorila_additions/the_zb_14.json",
    new_information="New inscriptions not in GORILA, extracted with dot/bracket certainty "
             "preserved — the held-out-supply frontier.")

# ---- Scholarly literature held as PDF / text in-repo ------------------------
add(source_id="SRC-SALGARELLA-2020", type="monograph", cluster="L_LA_PALAEOGRAPHY",
    citation="E. Salgarella, Aegean Linear Script(s): Rethinking the Relationship between "
             "Linear A and Linear B, CUP 2020. DOI 10.1017/9781108783477.",
    edition_lineage="synthesis over GORILA + SigLA palaeography (A<->B homomorphy grading)",
    ms="partial", ing="PDF_IN_HAND", rel="corpus/bronze/salgarella_2020/16.0_pp_412_416_INDEX_OF_SIGNS_CITED.pdf",
    new_information="The authoritative A<->B relationship + homomorphy grades (anchors.csv). "
             "Independent palaeographic argument about shape continuity, not value transfer.")
add(source_id="SRC-SALGARELLA-2025", type="monograph", cluster="L_LA_STRUCTURE",
    citation="E. Salgarella, Writing in Bronze Age Crete: 'Minoan' Linear A (Cambridge "
             "Elements), 2025. DOI 10.1017/9781009520041.",
    edition_lineage="current synthesis; endorses Davis 2013 structural reading",
    ms="no", ing="TEXT_EXTRACTED", rel="docs/related/salgarella-2025.md",
    new_information="Current authoritative synthesis: Minoan is a language ISOLATE, agglutinative, "
             "provisional VSO; REJECTS the etymological/Semitic method category-wide (S8).")
add(source_id="SRC-STEELE-MEISSNER-2017", type="chapter", cluster="L_GORILA_VENTRIS",
    citation="P. M. Steele & T. Meissner, 'From Linear B to Linear A: the problem of the "
             "backward projection of sound values', in Understanding Relations Between "
             "Scripts, Oxbow 2017, 93-110.",
    edition_lineage="CRITIQUE of the GORILA/Ventris backward projection itself",
    ms="no", ing="PDF_IN_HAND", rel="corpus/bronze/steele_meissner_2017/chapter-6.pdf",
    new_information="The load-bearing methodological critique of homomorphic value transfer + "
             "Cypriot-stable eleven (Table 6.2) + place-name equations. Meta-evidence on the lineage.")
add(source_id="SRC-KANTA-2024", type="conference_paper", cluster="L_ARCHAEOLOGY",
    citation="A. Kanta, D. Nakassis, T. G. Palaima & M. Perna, 'An archaeological and "
             "epigraphical overview ... (Anetaki plot)', KO-RO-NO-WE-SA (Ariadne Suppl. 5), "
             "2024, 27-43. DOI 10.26248/ariadne.vi.1841.",
    edition_lineage="primary autopsy of KN Zg 57/58 (Anetaki Ivory Repository)",
    ms="no", ing="PDF_IN_HAND", rel="corpus/bronze/kanta_etal_2024_anetaki/kanta_etal_2024_anetaki.pdf",
    new_information="The longest known LA inscription (~119 signs, KN Zg 57 ring + KN Zg 58). "
             "Prints NO transliteration — archaeological context only; full edition forthcoming.")
add(source_id="SRC-DELFREO-2024", type="conference_paper", cluster="L_ARCHAEOLOGY",
    citation="M. Del Freo, 'Rapport 2016-2021 sur les textes en ecriture hieroglyphique "
             "cretoise, en lineaire A et en lineaire B', KO-RO-NO-WE-SA (Ariadne Suppl. 5), "
             "2024, 87-124. DOI 10.26248/ariadne.vi.1843.",
    edition_lineage="primary find-report / editio-princeps pointers 2016-2021",
    ms="no", ing="TEXT_EXTRACTED", rel="corpus/bronze/delfreo_rapport_koronowesa/rapport.txt",
    new_information="Backbone find-report for LA finds 2016-2021 (S2 pp.96-108) — the "
             "post-GORILA supply enumeration. Independent of any reading.")
add(source_id="SRC-HENKEL-MARGARITIS-2022", type="journal_article", cluster="L_ARCHAEOLOGY",
    citation="C. Henkel & E. Margaritis, 'Examining the Ritual Landscape of Bronze Age Crete "
             "through the Lens of Archaeobotany', Religions 13(1):81, 2022. DOI 10.3390/rel13010081.",
    edition_lineage="primary archaeobotany (open access, CC BY)",
    ms="no", ing="PDF_IN_HAND", rel="corpus/bronze/anetaki_context/henkel_margaritis_2022_religions.pdf",
    new_information="Ritual-plant context for the Knossos Anetaki Fetish Shrine (KN Zg 57/58 "
             "deposit). Context only; no inscription content.")
add(source_id="SRC-KENTRO-2021", type="website", cluster="L_ARCHAEOLOGY",
    citation="Kentro: The Newsletter of the INSTAP Study Center for East Crete, Vol. 24 "
             "(Fall 2021), 40 pp.",
    edition_lineage="institutional newsletter (public)",
    ms="no", ing="PDF_IN_HAND", rel="corpus/bronze/kentro_newsletters/Kentro_2021_WEBSITEviewing.pdf",
    new_information="2021 corroboration that the Anetaki excavation volumes are in preparation; "
             "archaeobotany of Anetaki cult deposits. Marginal context.")
add(source_id="SRC-BRAOVIC-2024", type="survey", cluster="L_COMPUTATIONAL_METHOD",
    citation="M. Braovic, D. Krstinic, M. Stula & A. Ivanda, survey, Computational Linguistics "
             "50(2):725-779, 2024. OA https://aclanthology.org/2024.cl-2.7.pdf.",
    edition_lineage="independent computational survey",
    ms="no", ing="TEXT_EXTRACTED", rel="docs/related/braovic-2024.md",
    new_information="The comparable prior-review of computational decipherment — cite-or-be-desk-"
             "rejected map of the method space.")
add(source_id="SRC-SALGARELLA-JUDSON-2024", type="conference_paper", cluster="L_LA_PALAEOGRAPHY",
    citation="E. Salgarella & A. Judson, 'Signs of the times?', KO-RO-NO-WE-SA (Ariadne "
             "Suppl. 5), 2024, 359-379.",
    edition_lineage="palaeographic stratification over GORILA/SigLA",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Hand/stratum stratification — drove the morphology stratification "
             "prereg addendum. Palaeographic (independent) channel.")
add(source_id="SRC-SALGARELLA-BELLINATO-FERRARA-2025", type="journal_article", cluster="L_GORILA_VENTRIS",
    citation="E. Salgarella, F. Bellinato & S. Ferrara, 'On Aegean spices...', Kadmos "
             "64(1/2):29-44, 2025. DOI 10.1515/kadmos-2025-0002.",
    edition_lineage="logographic readings over GORILA sign inventory (KA+PO *127 etc.)",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Public 2025 logographic/composite readings (KA+PO='spice', A646/A341='root'). "
             "SPECULATIVE by authors' own hedge; quarantined so it cannot leak as discovery.")

# ---- Published READINGS / proposals (litindex claim sources) ---------------
add(source_id="SRC-VENTRIS-1953", type="journal_article", cluster="L_LB_DECIPHERMENT",
    citation="M. Ventris & J. Chadwick, 'Evidence for Greek dialect in the Mycenaean archives', "
             "JHS 73, 1953.",
    edition_lineage="ROOT of the phonetic-value lineage (Linear B = Greek)",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Fixes the syllabic values later transferred to homomorphic Linear A signs. "
             "The single origin of every GORILA-value reading.")
add(source_id="SRC-GORDON-1966", type="monograph", cluster="L_FRINGE_REGISTRY",
    citation="C. H. Gordon, Evidence for the Minoan Language, Ventnor 1966 (syn. of 1957- "
             "articles). Reviewed by G. A. Rendsburg, Biblical Archaeologist 59:1 (1996) 36-43.",
    edition_lineage="West-Semitic reading OF the GORILA transliteration",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="The canonical West-Semitic proposal (su-pu, ka-ro-pa, ku-ro, ya-ne). "
             "DISPUTED; indexed for decontamination. Reads GORILA values -> not independent.")
add(source_id="SRC-BEST-1981", type="journal_article", cluster="L_FRINGE_REGISTRY",
    citation="J. G. P. Best, 'YASSARAM!', Talanta 13 (1981) 17-21 — (j)a-sa-sa-ra-me = "
             "vocative 'oh Asherah!'. Refuted for the goddess reading by M. Pope, BICS 8 (1961).",
    edition_lineage="Semitic reading OF the GORILA transliteration",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="The a-sa-sa-ra-me Semitic reading. DISPUTED; indexed for decontamination.")
add(source_id="SRC-DAVIS-2013", type="journal_article", cluster="L_LA_STRUCTURE",
    citation="B. Davis, 'Syntax in Linear A', Kadmos 52 (2013) 35-52.",
    edition_lineage="internal syntactic/structural analysis (value-agnostic on *301)",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="i-*301 = 'give/dedicate' libation-formula verb, double-ended inflection; "
             "morphology 'neither IE nor Afroasiatic' (p.38 n.13). The serious structural reading; "
             "assigns *301 NO phonetic value -> genuinely independent of the value lineage.")
add(source_id="SRC-DAVIS-2014", type="monograph", cluster="L_LA_STRUCTURE",
    citation="B. Davis, Minoan Stone Vessels with Linear A Inscriptions, Aegaeum 36, 2014.",
    edition_lineage="structural / word-order analysis of the LA corpus",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="The fullest modern structural (word-order/VSO) analysis; libation-formula "
             "corpus. Structure, not values -> independent.")
add(source_id="SRC-DUHOUX", type="journal_article", cluster="L_LA_STRUCTURE",
    citation="Y. Duhoux, standard analyses of the Linear A libation formula (1978, 1992, 1997).",
    edition_lineage="internal formula segmentation + agglutinative typology",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Libation-formula segmentation + the agglutinative-typology argument. "
             "The held-out formula set. Structural -> independent.")
add(source_id="SRC-VALERIO-2007", type="journal_article", cluster="L_LA_STRUCTURE",
    citation="M. Valerio (2007) — LA ablative-like suffix analysis (per Salgarella 2025 S8).",
    edition_lineage="internal affix morphology",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Proposed ablative-like suffix ('from'). Morphological/structural -> independent.")
add(source_id="SRC-SCHRIJVER-2014", type="journal_article", cluster="L_LA_STRUCTURE",
    citation="P. Schrijver, LA fraction system, Kadmos 53 (2014) 1-44.",
    edition_lineage="internal metrological analysis (fractions)",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="One of two independent Direction-D fraction-system reconstructions. "
             "Metrology from internal structure -> independent of the value lineage.")
add(source_id="SRC-CORAZZA-2021", type="journal_article", cluster="L_LA_STRUCTURE",
    citation="M. Corazza et al., LA fraction system, JAS 125 (2021) 105214.",
    edition_lineage="internal metrological analysis (fractions), independent of Schrijver",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="The second independent fraction-system reconstruction. Metrology -> independent.")
add(source_id="SRC-PACKARD-1974", type="monograph", cluster="L_COMPUTATIONAL_METHOD",
    citation="D. W. Packard, Minoan Linear A, UC Press 1974.",
    edition_lineage="statistical null / fictitious-decipherment control (method ancestor)",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Built 9 FICTITIOUS decipherments as a null — Ventris-value transfer beat "
             "them only ~2:1. The direct ancestor of the foundry's permutation-null discipline.")
add(source_id="SRC-BARBER-1974", type="monograph", cluster="L_COMPUTATIONAL_METHOD",
    citation="E. J. W. Barber, Archaeological Decipherment: A Handbook, 1974.",
    edition_lineage="decipherment methodology / identifiability theory",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="The identifiability-without-a-known-target threshold the unicity/information "
             "-floor argument must engage. Method theory -> independent.")

# ---- Computational method + ML prior art (cited, code not in repo) ---------
add(source_id="SRC-LUO-2019", type="method_paper", cluster="L_COMPUTATIONAL_METHOD",
    citation="J. Luo, Y. Cao & R. Barzilay, 'Neural Decipherment via Minimum-Cost Flow: From "
             "Ugaritic to Linear B', ACL 2019 (P19-1303); arXiv 1906.06718.",
    edition_lineage="independent neural decipherment method",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="The seminal auto-decipherment result (Ugaritic->Hebrew; partial LB->Greek; "
             "explicitly did NOT crack LA). The foundry's baseline method. Code not released.")
add(source_id="SRC-LUO-2021", type="method_paper", cluster="L_COMPUTATIONAL_METHOD",
    citation="J. Luo et al., 'Deciphering Undersegmented Ancient Scripts Using Phonetic Prior', "
             "TACL 2021.",
    edition_lineage="independent method (undersegmented scripts)",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Directly relevant to LA's segmentation obstacle (scripts without clear word "
             "boundaries). Gothic/Ugaritic/Iberian.")
add(source_id="SRC-SNYDER-2010", type="method_paper", cluster="L_COMPUTATIONAL_METHOD",
    citation="B. Snyder, R. Barzilay & K. Knight, 'A Statistical Model for Lost Language "
             "Decipherment', ACL 2010.",
    edition_lineage="Bayesian cognate decipherment (method root)",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Non-parametric Bayesian cognate matching (Ugaritic->Hebrew). A method root.")
add(source_id="SRC-BERGKIRK-2011", type="method_paper", cluster="L_COMPUTATIONAL_METHOD",
    citation="T. Berg-Kirkpatrick & D. Klein, 'Simple Effective Decipherment via Combinatorial "
             "Optimization', EMNLP 2011.",
    edition_lineage="combinatorial-optimization decipherment (the numpy/scipy core)",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Cognate decipherment as min edit-distance under a char mapping — the "
             "combinatorial core logos implements.")
add(source_id="SRC-RAVI-KNIGHT-2011", type="method_paper", cluster="L_COMPUTATIONAL_METHOD",
    citation="S. Ravi & K. Knight, 'Deciphering Foreign Language', ACL 2011.",
    edition_lineage="Bayesian/MT-decipherment lineage",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="The IBM-model-style statistical-decipherment root that Luo neuralizes.")
add(source_id="SRC-SOMMERSCHIELD-2023", type="survey", cluster="L_COMPUTATIONAL_METHOD",
    citation="T. Sommerschield et al., 'Machine Learning for Ancient Languages: A Survey', "
             "Computational Linguistics 49(3), 2023. DOI 10.1162/coli_a_00481.",
    edition_lineage="the 240+ paper field map",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="The comprehensive ML-for-ancient-languages map — the reading baseline; "
             "sources the entropy-vs-languagehood caution (Rao/Sproat).")
add(source_id="SRC-ITHACA", type="code", cluster="L_COMPUTATIONAL_METHOD",
    citation="Y. Assael et al., DeepMind Ithaca (+ predecessor Pythia; + Aeneas), "
             "github.com/google-deepmind/ithaca.",
    edition_lineage="restoration/attribution of KNOWN-language (Greek) text — engineering ref",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Sparse-text transformer restoration + geo/chrono attribution (~62%/71%). "
             "Engineering reference only — does NOT decipher unknown scripts.")
add(source_id="SRC-CORAZZA-SIGN2VEC-2022", type="method_paper", cluster="L_COMPUTATIONAL_METHOD",
    citation="M. Corazza et al., 'Sign2Vec' — unsupervised sign clustering (ResNet50+k-means) "
             "for Cypro-Minoan, 2022.",
    edition_lineage="representation-layer prior art (visual clustering)",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Direct prior art for the sign-representation layer (2/3 signs correct on "
             "Cypro-Minoan). Must-cite, not our novelty.")
add(source_id="SRC-KARAJGIKAR-2021", type="method_paper", cluster="L_COMPUTATIONAL_METHOD",
    citation="J. Karajgikar, A. Al-Khulaidy & A. Berea, word2vec embeddings for Linear A "
             "glyphs + symbol grouping, 2021.",
    edition_lineage="LA embedding prior art",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Prior art establishing LA-glyph embeddings + grouping exist (not our novelty).")
add(source_id="SRC-PAPAVASSILIOU-2020", type="method_paper", cluster="L_COMPUTATIONAL_METHOD",
    citation="G. Papavassiliou, G. Owens & D. Kosmopoulos, 'include related writing systems "
             "(Linear B) as the key to decipherment', 2020; + Papavassileiou et al. 2023 LB LM.",
    edition_lineage="cross-script transfer prior art",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Establishes the 'Linear B as key' cross-script idea PREDATES logos (must-cite). "
             "2023 LB generative LM = the known-side asset.")
add(source_id="SRC-DAGGUMATI-REVESZ-2018", type="method_paper", cluster="L_COMPUTATIONAL_METHOD",
    citation="S. Daggumati & P. Z. Revesz, CNN+SVM script-family trees; + Revesz 2019/2023 "
             "cross-script CNN (Information, MDPI OA).",
    edition_lineage="visual script-family CNN prior art",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="CNN script-family trees ('Linear B close to Cretan Hieroglyphic'). Visual "
             "cross-script prior art.")
add(source_id="SRC-LOH-CACCIAFOCO-2020", type="conference_paper", cluster="L_COMPUTATIONAL_METHOD",
    citation="C. J. S. Loh & F. Perono Cacciafoco, 'A new approach to the decipherment of Linear "
             "A ... a brute force attack', Grapholinguistics 2020, 927-943. DOI 10.36824/2020-graf-cacc. OA.",
    edition_lineage="independent brute-force decipherment attempt",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="OA brute-force LA attempt (note: survey miscites as 'Colin & Cacciafoco'). "
             "Peer decipherment attempt.")

# ---- Sister-script comparanda ----------------------------------------------
add(source_id="SRC-CHIC", type="corpus_edition", cluster="L_SISTER_SCRIPT",
    citation="J.-P. Olivier & L. Godart, Corpus Hieroglyphicarum Inscriptionum Cretae (CHIC), "
             "Etudes cretoises 31, 1996.",
    edition_lineage="Cretan Hieroglyphic critical edition (sister script, value-undeciphered)",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="The Cretan Hieroglyphic corpus — structurally-related predecessor script. "
             "Value-undeciphered, so an INDEPENDENT (non-Ventris) comparandum. Not held in-repo.")
add(source_id="SRC-CYPRIOT-SYLLABARY", type="corpus_edition", cluster="L_SISTER_SCRIPT",
    citation="Cypriot Syllabary values (deciphered independently by G. Smith, 1870s); used in "
             "Steele & Meissner 2017 Table 6.2 (the Cypriot-stable eleven).",
    edition_lineage="INDEPENDENT decipherment (Cypriot Greek), predates Ventris",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="An independently-cracked syllabary whose stable sign values give a "
             "cross-check on Aegean values NOT sourced from Ventris. Genuinely independent anchor.")
add(source_id="SRC-CYPRO-MINOAN", type="corpus_edition", cluster="L_SISTER_SCRIPT",
    citation="Cypro-Minoan corpus (Ferrara, Cypro-Minoan Inscriptions, 2012/2013; HoChyMin).",
    edition_lineage="sister script (undeciphered), descended from Linear A",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="The undeciphered LA-descended Cypriot script; target of the Sign2Vec work. "
             "Independent script family. Not held in-repo.")

# ---- Fringe / registry objects (quarantine) --------------------------------
add(source_id="SRC-RJABCHIKOV-2025", type="fringe_registry", cluster="L_FRINGE_REGISTRY",
    citation="S. V. Rjabchikov, 'The Decipherment of two Records of Linear A on the Ivory Mirror "
             "from Knossos', Novaya Nauka conf. (Petrozavodsk 2025), 100-106. ISBN 978-5-00215-841-6.",
    edition_lineage="fringe reading from PHOTOGRAPHS of KN Zg 57/58, before any transliteration",
    ms="no", ing="PDF_IN_HAND", rel="corpus/bronze/rjabchikov_2025_sceptre/KOF-1370_novaya_nauka_2025_proceedings.pdf",
    new_information="15 fringe sceptre readings, quarantined (litindex fringe_sceptre_reading). "
             "Mechanically gradable vs Anetaki II when it publishes. NEVER evidence.")
add(source_id="SRC-CHIAPELLO-2024", type="fringe_registry", cluster="L_FRINGE_REGISTRY",
    citation="D. Chiapello, 'Deductions on an unknown find ... the Linear A inscribed ivory "
             "circle found at Knossos', Academia.edu, posted 2024-02-07.",
    edition_lineage="dated PRE-PUBLICATION prediction (registry object, no fringe flag)",
    ms="no", ing="ARCHIVED_PAGE", rel="corpus/bronze/prepub_prediction_2024_ivory_circle/academia_page_wayback_20260703.html",
    new_information="Falsifiable pre-pub prediction (greater A/B similarity; Greek-reading "
             "reappraisal), scorable when Anetaki II lands. PDF itself login-gated (NOT acquired).")
add(source_id="SRC-DIMINO-2026", type="fringe_registry", cluster="L_FRINGE_REGISTRY",
    citation="T. Di Mino (2026), 'Ya Diktu: Grammar of the Minoan Peak Sanctuary Libation "
             "Formula' (draft). Reads *301 as Semitic N-W-Y 'to dwell'.",
    edition_lineage="Semitic reading assigning *301 a /na/ value (no cross-script anchor)",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Quarantined Semitic *301 proposal; internally refuted (his own table draws "
             "agglutinative morphology, the opposite of Semitic root-and-pattern). NEVER evidence.")

# ---- UNAVAILABLE but would-add (marked, not fabricated) --------------------
add(source_id="SRC-ANETAKI-II", type="forthcoming_unavailable", cluster="L_ARCHAEOLOGY",
    citation="A. Kanta (ed.), Anetaki II: the Neopalatial Room 1 and the Ivory Repository "
             "(The Religious Center of the City of Knossos, Vol. 1), Philadelphia: INSTAP, forthcoming.",
    edition_lineage="THE editio princeps of KN Zg 57/58 (primary autopsy)",
    ms="no", ing="UNAVAILABLE", rel=None,
    new_information="WOULD ADD: the official transliteration of the longest LA inscription — the "
             "genuine HELD-OUT gold that would grade every Anetaki prediction. Not yet published.")
add(source_id="SRC-SCHOEP-2002", type="monograph", cluster="L_LA_STRUCTURE",
    citation="I. Schoep, The Administration of Neopalatial Crete, Minos Suppl. 17, 2002.",
    edition_lineage="administrative/structural synthesis + sign counts",
    ms="no", ing="UNAVAILABLE", rel=None,
    new_information="WOULD ADD: the Semitic/Lycian best-founded ranking + the 7,362-7,396 sign "
             "count (information-budget denominator). Paywalled; operator-supplies.")
add(source_id="SRC-FERRARA-TAMBURINI-2022", type="journal_article", cluster="L_COMPUTATIONAL_METHOD",
    citation="S. Ferrara & F. Tamburini, 'Advanced techniques...', Lingue e Linguaggio "
             "2/2022:239-259 (il Mulino).",
    edition_lineage="the only comparable prior computational review",
    ms="no", ing="UNAVAILABLE", rel=None,
    new_information="WOULD ADD: the closest comparable review ('cite or be desk-rejected'). "
             "Paywalled (il Mulino).")
add(source_id="SRC-FULS-2015", type="journal_article", cluster="L_LA_STRUCTURE",
    citation="A. Fuls, 'Classifying undeciphered writing systems', Historische Sprachforschung "
             "128(1):42-58, 2015.",
    edition_lineage="quantitative typology of undeciphered scripts",
    ms="no", ing="UNAVAILABLE", rel=None,
    new_information="WOULD ADD: the 3.3-sign word-length figure to reconcile against the "
             "word-unit premise (mean 1.84 signs here). Paywalled.")
add(source_id="SRC-JUDSON-2020", type="monograph", cluster="L_SISTER_SCRIPT",
    citation="A. P. Judson, The Undeciphered Signs of Linear B, CUP 2020.",
    edition_lineage="LB scribal-practice framing (known-side)",
    ms="no", ing="UNAVAILABLE", rel=None,
    new_information="WOULD ADD: LB *127/*157 inventory + scribal-practice framing for the "
             "known-side transfer. Paywalled.")
add(source_id="SRC-SACCONI-1972", type="journal_article", cluster="L_GORILA_VENTRIS",
    citation="A. Sacconi, 'The monogram KAPO', Kadmos 11(1):22-26, 1972 (+ Foster 1974 Duke diss.).",
    edition_lineage="origin of the KA+PO=cinnamon/fenugreek logographic reading",
    ms="no", ing="UNAVAILABLE", rel=None,
    new_information="WOULD ADD: the primary origin of the KA+PO monogram reading (decontamination "
             "provenance for the 2025 spice paper). Paywalled.")
add(source_id="SRC-SALGARELLA-2019", type="journal_article", cluster="L_LA_PALAEOGRAPHY",
    citation="E. Salgarella, 'Drawing lines', Kadmos 58:61-92, 2019.",
    edition_lineage="synchronic palaeographic variation (hand strata)",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Hand-stratum / synchronic-variation palaeography — resolves the stratification "
             "question. Independent palaeographic channel.")
add(source_id="SRC-SALGARELLA-2022", type="journal_article", cluster="L_LA_PALAEOGRAPHY",
    citation="E. Salgarella, 'Mix and match: a combinatory (re-)classification of Linear A "
             "signs', TALANTA 54:31-52, 2022. OA (CC BY-NC-ND), Cambridge repository.",
    edition_lineage="combinatory sign classification over SigLA",
    ms="no", ing="CITED_ONLY", rel=None,
    new_information="Combinatory sign re-classification — OA palaeographic taxonomy. Independent.")

# ---------------------------------------------------------------------------
# Verify provenance-present flags against the filesystem; compute tallies.
# ---------------------------------------------------------------------------
def sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()[:16]

for r in R:
    rel = r.get("rel")
    present = bool(rel) and os.path.exists(os.path.join(REPO, rel))
    r["provenance_present"] = present
    r["file_sha16"] = sha16(os.path.join(REPO, rel)) if present else ""
    r["independent"] = CLUSTERS[r["cluster"]]["independent"]

# Deterministic ordering: cluster, then source_id.
R.sort(key=lambda r: (r["cluster"], r["source_id"]))

n_total = len(R)
n_present = sum(r["provenance_present"] for r in R)
n_independent = sum(r["independent"] for r in R)
n_machine = sum(r["ms"] == "yes" for r in R)
by_cluster = {}
for r in R:
    by_cluster.setdefault(r["cluster"], []).append(r["source_id"])
by_status = {}
for r in R:
    by_status[r["ing"]] = by_status.get(r["ing"], 0) + 1

# Independent LINEAGES (distinct clusters that are independent of GORILA/Ventris).
independent_clusters = [c for c, m in CLUSTERS.items() if m["independent"]]

os.makedirs(OUTDIR, exist_ok=True)

# CSV
cols = ["source_id", "citation", "type", "edition_lineage", "machine_readable",
        "new_information", "dependency_cluster", "ingestion_status",
        "independent_of_gorila_ventris", "provenance_present", "file_sha16"]
csv_path = os.path.join(OUTDIR, "wp7_source_register.csv")
with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(cols)
    for r in R:
        w.writerow([r["source_id"], r["citation"], r["type"], r["edition_lineage"],
                    r["ms"], r["new_information"], r["cluster"], r["ing"],
                    r["independent"], r["provenance_present"], r["file_sha16"]])

# JSON
json_path = os.path.join(OUTDIR, "wp7_source_register.json")
with open(json_path, "w") as f:
    json.dump({
        "schema": "foundry.source_register/v1",
        "seed": SEED,
        "built": str(date.today()),
        "note": ("Source Audit Sweep toward the 60-source quota. Non-fabricated: every held "
                 "record maps to a file under corpus/; unavailable sources are marked UNAVAILABLE "
                 "with what they would add."),
        "clusters": CLUSTERS,
        "independent_clusters": independent_clusters,
        "tally": {
            "n_sources": n_total,
            "n_provenance_present_in_repo": n_present,
            "n_fully_machine_readable": n_machine,
            "n_independent_of_gorila_ventris": n_independent,
            "n_in_gorila_ventris_or_fringe_lineage": n_total - n_independent,
            "n_independent_lineage_clusters": len(independent_clusters),
        },
        "by_cluster": {c: sorted(v) for c, v in sorted(by_cluster.items())},
        "by_ingestion_status": by_status,
        "records": R,
    }, f, indent=1)

# Summary text
sum_path = os.path.join(OUTDIR, "wp7_source_register_summary.txt")
lines = []
lines.append("LINEAR A FOUNDRY — SOURCE AUDIT SWEEP (wp7_source_register)")
lines.append("=" * 64)
lines.append(f"sources audited            : {n_total}")
lines.append(f"held in-repo (file present): {n_present}")
lines.append(f"fully machine-readable     : {n_machine}")
lines.append(f"INDEPENDENT of GORILA/Ventris value transfer: {n_independent}")
lines.append(f"in the GORILA/Ventris or fringe(regurgitation) lineage: {n_total - n_independent}")
lines.append(f"distinct INDEPENDENT lineage clusters: {len(independent_clusters)} "
             f"({', '.join(independent_clusters)})")
lines.append("")
lines.append("BY DEPENDENCY CLUSTER (independent? / n):")
for c in sorted(by_cluster):
    lines.append(f"  {c:22s} indep={str(CLUSTERS[c]['independent']):5s} n={len(by_cluster[c]):2d}"
                 f"  {', '.join(sorted(by_cluster[c]))}")
lines.append("")
lines.append("BY INGESTION STATUS:")
for s in sorted(by_status):
    lines.append(f"  {s:20s} {by_status[s]}")
lines.append("")
lines.append("HEADLINE: the phonetic-value knowledge of Linear A traces to ONE lineage")
lines.append("(GORILA homomorphic transfer of Ventris-1953 Linear B values). Genuine")
lines.append("independence comes from 5 non-value channels: palaeography (shape), internal")
lines.append("structure/metrology, archaeology, general computational method, and the")
lines.append("independently-deciphered Cypriot Syllabary + undeciphered sister scripts.")
with open(sum_path, "w") as f:
    f.write("\n".join(lines) + "\n")

print("\n".join(lines))
print("\nWROTE:")
for p in (csv_path, json_path, sum_path):
    print(" ", p)
