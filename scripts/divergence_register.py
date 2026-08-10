#!/usr/bin/env python3
"""divergence_register.py — standing multi-witness divergence register + comparator.

Tsirkas-mechanism 3 (docs/2026-08-05-tsirkas-full-repo-audit.md §5 item 5): a
machine-readable register of adjudicated transcription divergences between the corpus
witnesses held in this repo — silver (lineara.xyz lineage), the decoded SigLA database,
and Younger's text pages (via scripts/younger_parser.py) — plus the sidecar damage annex
(Tsirkas D1). Load-bearing for the held-out acceptance standard: grading predictions
against new tablets requires adjudicated readings, and any analysis touching a
registered divergence must run under both readings (CLAUDE.md corpus status).

Output: corpus/divergences.json — a COMMITTED-class file carrying DEFECT-LEVEL EXCERPTS
ONLY (readings for divergence-carrying documents; same fair-dealing basis as
docs/2026-08-05-ab21-ab22-external-audit.md). Agreeing documents are counted, never
excerpted. Every entry is generated mechanically by this script (invariant 12); the
file is regenerated with `python3 scripts/divergence_register.py` and drift-checked
with `--check`.

Reuse: the FAMILY variant-collapsing dict is imported from scripts/audit_ab21_ab22.py;
the verdict ladder (NOT_IN_SIGLA / COUNT_MISMATCH / AGREE / INVERTED / MIXED) and the
positional-alignment strategy replicate it exactly (tests/test_divergence_register.py
cross-validates the two tools' D4 output for equality). sigla_designation() EXTENDS the
audit script's Wc-only id bridge to every support class present in silver ids
(Wa/Wb/Wc/Wd/Wg/Wy, Za..Zg), verified against real SigLA designations; the audit script
itself is a frozen record and is not modified.

Seeded entries (all mechanical):
  D4    — AB21/AB22 (OVIS/CAP) inversion, Tsirkas 2026 D4: 11 INVERTED docs / 15
          tokens + PH 31a/b instance-level MIXED (re-derivation of the 2026-08-05 audit).
  HT38  — livestock-token divergences invisible to the *21/*22 label scan: silver
          carries the Latin label 'CAP' on HT38 (the audit doc's "dropped token",
          refined: present under an alternate labelling convention, still divergent vs
          SigLA AB21 / Younger 'OVIS 3'), and KH Wc 2102 / PH Wc 44 carry no livestock
          token at all where SigLA reads AB21.
  D1    — word-attached damage stripping (U+1076B), from the Phase-1 annex summary
          (scripts/audit_damage_markers.py; corpus/silver/damage_annex.json).
  BR1   — ASCII break notation leaked into 5 silver sign labels (]TU+RO, ]MI+JA,
          TE+RO[, RO+RO[, WI+ZE[), found by mechanical scan.

Round-2 entries (v2, 2026-08-10; witnesses now include the five rapports of the
CH/LA/LB series 1996-2021 — the four pre-2016 author PDFs received privately from
M. Del Freo plus the OA Rapport 2016-2021; see
experiments/crossscript_gate/phase3/sweep/round2_pre2016_rapports/ROUND2_DELTA.md):
  R2READ — token-level reading divergences silver-vs-rapport-series (KN Zb <27>
          numeral 17 vs autopsy 107; KH Wc 2124 AB 54 vs corrected AB 61 variant;
          THE Zb 15 lamp RE-SA vs ed.pr. SE-*332; HT Wc 3024; PK Zb 26; SKO Zc 1).
  R2DOUBT — items included in silver with committed readings where the rapport series
          suspends judgement or objects (KN Ze 56, LACH Za 1, DRA Zg 1, IN Zb 1,
          MI Zb 3, PK Zb 23, PE Zb 8, HT Zf(HM 767) script-undecided).
  R2SITE — site-label defects (whole Arkhanes series labelled 'Arkhalkhori'; LACH Za 1
          at 'Larani', origin witnessed by Younger's comparandum token).
  R2THE — identity resolution of silver's ad-hoc Thera IDs against THE 7-12
          (THEtab.4 = THE 7, THEfr.1 = THE 10 confirmed; fr.2/3 and tab.5
          witness-conflicted; THE 8 missing in silver, present in SigLA).
  R2REST — restored formula text carried without break/restoration marking
          (IO Za 16, PK Za 27, SY Za 8) — D1-family instances.
Every R2 rapport quote is verified verbatim (whitespace-normalized) against the held
rapport text at build time; silver/SigLA/Younger sides are derived live. The build
FAILS if a quote or a mechanical assertion no longer holds.

Constitution: Art. XI (source-lineage defects recorded), Art. XVII (append-only:
register supplements, silver untouched — no rebuild without an explicit decision),
Art. XXII (this header), invariant 12 (all counts script-generated). Claim layer: L0
(physical/transcriptional); no interpretive reading is asserted. Credit: Tsirkas D1/D4
(github.com/ChristosTsirkas/corpus-validation-for-undeciphered-scripts-linear-a).

    python3 scripts/divergence_register.py [--out corpus/divergences.json]
                                           [--check] [--summary-only]
"""
import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.audit_ab21_ab22 import FAMILY            # noqa: E402  (single source)
from scripts import younger_parser as yp              # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SILVER = os.path.join(ROOT, "corpus", "silver", "inscriptions.json")
SIGLA = os.path.join(ROOT, "corpus", "bronze", "sigla_browse_2026", "sigla_documents.json")
ANNEX = os.path.join(ROOT, "corpus", "silver", "damage_annex.json")
OUT = os.path.join(ROOT, "corpus", "divergences.json")

VERSION = "divergence-register-v2"
GENERATED_BY = f"scripts/divergence_register.py {VERSION}"

AUDIT_DOC = "docs/2026-08-05-ab21-ab22-external-audit.md"
TSIRKAS_DOC = "docs/2026-08-05-tsirkas-full-repo-audit.md"
TSIRKAS_REPO = "github.com/ChristosTsirkas/corpus-validation-for-undeciphered-scripts-linear-a"

# Silver id bridge, extended beyond audit_ab21_ab22's Wc-only handling.
_ID = re.compile(r"^([A-Z]+?)(\(\?\))?(W[abcdgy]|Z[a-g])?(\d+[a-z]?)(\(\?\))?$")
_YOUNGER_FAM = re.compile(r"(OVIS|CAP)[mfx]?$")


def sigla_designation(silver_id):
    """HT136a -> 'HT 136a', KNWc29 -> 'KN Wc 29', IOZa2 -> 'IO Za 2', PH(?)31a -> 'PH 31a'.

    Extends audit_ab21_ab22.sigla_designation() to all support classes found in silver
    ids (Wa/Wb/Wc/Wd/Wg/Wy, Za..Zg). Anchored: ids it cannot parse (THEfr.1,
    HTZd157+156, ...) pass through unchanged rather than mis-keying."""
    m = _ID.match(silver_id)
    if not m:
        return silver_id
    site, _, cls, num, _ = m.groups()
    return f"{site} {cls} {num}" if cls else f"{site} {num}"


def silver_id(designation):
    """Inverse bridge: 'KN Wc 29' -> 'KNWc29'. (PH(?) ids lose their '(?)' marker —
    the forward direction drops it; documented one-way loss.)"""
    return "".join(designation.split())


def fold_family(label):
    """Collapse one witness label to its livestock family: '21', '22', or None.

    Conventions folded: silver * -forms (via audit_ab21_ab22.FAMILY), SigLA AB-forms,
    Younger/silver Latin names with optional gender (OVIS/OVISf/CAP/CAPm/...).
    Ligatures (OVIS+SI, CAPm+KU) fold to None — never positionally adjudicated,
    mirroring the audit's exact-label rule on the SigLA side."""
    if label in FAMILY:
        return FAMILY[label]
    if label in ("AB21", "AB22"):
        return label[-2:]
    m = _YOUNGER_FAM.fullmatch(label)
    if m:
        return "21" if m.group(1) == "OVIS" else "22"
    return None


def adjudicate(fams, sig_fams):
    """The audit_ab21_ab22 verdict ladder, verbatim, as a pure function."""
    if sig_fams is None:
        return "NOT_IN_SIGLA"
    if len(sig_fams) != len(fams):
        return "COUNT_MISMATCH"      # alignment not attemptable at family level
    if all(a == b for a, b in zip(fams, sig_fams)):
        return "AGREE"
    if all(a != b for a, b in zip(fams, sig_fams)):
        return "INVERTED"
    return "MIXED"


def load_witnesses(silver_path=SILVER, sigla_path=SIGLA):
    silver = json.loads(open(silver_path, encoding="utf-8").read())
    sigla = json.loads(open(sigla_path, encoding="utf-8").read())
    return silver, {d["designation"]: d for d in sigla}


def _sigla_family_labels(sigla_by_des, designation):
    sd = sigla_by_des.get(designation)
    if sd is None:
        return None
    return [s for s in sd["transcription"] if s in ("AB21", "AB22")]


def scan_family_inversion(silver, sigla_by_des):
    """Re-derive the D4 audit: one row per silver doc carrying *21/*22-family tokens."""
    rows = []
    for doc in silver:
        tokens = [s for s in doc["signs"] if s in FAMILY]
        if not tokens:
            continue
        des = sigla_designation(doc["id"])
        sig = _sigla_family_labels(sigla_by_des, des)
        fams = [FAMILY[t] for t in tokens]
        sig_fams = [s[-2:] for s in sig] if sig is not None else None
        rows.append({
            "id": doc["id"], "designation": des, "silver": tokens, "sigla": sig,
            "verdict": adjudicate(fams, sig_fams),
            "divergent_positions": (
                [i for i, (a, b) in enumerate(zip(fams, sig_fams)) if a != b]
                if sig_fams is not None and len(sig_fams) == len(fams) else None),
        })
    return rows


def scan_livestock_alt_or_missing(silver, sigla_by_des):
    """Livestock divergences the *-label scan cannot see: silver docs WITHOUT
    *21/*22-family labels that either carry a foldable Latin livestock label (HT38's
    'CAP') or bridge to a SigLA doc reading AB21/AB22 (missing token)."""
    rows = []
    for doc in silver:
        if any(s in FAMILY for s in doc["signs"]):
            continue                       # in the D4 scan already
        alt = [s for s in doc["signs"] if fold_family(s)]
        des = sigla_designation(doc["id"])
        sig = _sigla_family_labels(sigla_by_des, des)
        if not alt and not sig:
            continue
        if sig is None:
            verdict = "NOT_IN_SIGLA"
        elif not alt:
            verdict = "MISSING_IN_SILVER"
        else:
            verdict = adjudicate([fold_family(s) for s in alt], [s[-2:] for s in sig])
        rows.append({"id": doc["id"], "designation": des, "silver": alt,
                     "sigla": sig, "verdict": verdict})
    return rows


def bracket_residue(silver):
    """Sign labels with leaked break notation: leading ']' or trailing '['."""
    hits = {}
    for doc in silver:
        for i, s in enumerate(doc["signs"]):
            if s.startswith("]") or s.endswith("["):
                hits.setdefault(s, []).append([doc["id"], i])
    return hits


def younger_key(silver_doc_id):
    """Silver id -> (Younger base designation, side letter or None).
    HT136a -> ('HT 136', 'a'); PH(?)31a -> ('PH(?) 31', 'a'); KNWc29 -> ('KN Wc 29', None)."""
    m = _ID.match(silver_doc_id)
    if not m:
        return silver_doc_id, None
    site, q, cls, num, _ = m.groups()
    side = None
    if num and num[-1].isalpha():
        num, side = num[:-1], num[-1]
    base = site + (q or "") + " " + ((cls + " ") if cls else "") + num
    return base, side


def younger_witness(silver_doc_id, ydocs):
    """Younger family-label readings for one silver doc, or None if not parseable.

    Doc-level fold only (no positional alignment): deduplicated side.line rows,
    side-filtered when the silver id names a face, unrestored simple OVIS/CAP labels
    (ligatures excluded — see fold_family)."""
    base, side = younger_key(silver_doc_id)
    slot = ydocs.get(base)
    if not slot:
        return None
    rows = yp.dedup_rows(slot["rows"])
    if side:
        rows = [r for r in rows if r["line"].startswith(side)]
    labels = [l for r in rows for l in r["logograms"] if _YOUNGER_FAM.fullmatch(l)]
    return labels or None


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _entry_d4(d4_rows, ydocs):
    verdicts = {}
    for r in d4_rows:
        verdicts[r["verdict"]] = verdicts.get(r["verdict"], 0) + 1
    inverted = [r for r in d4_rows if r["verdict"] == "INVERTED"]
    mixed = [r for r in d4_rows if r["verdict"] == "MIXED"]
    docs = {}
    for r in inverted + mixed:
        docs[r["id"]] = {
            "verdict": r["verdict"],
            "readings": {"silver": r["silver"], "sigla": r["sigla"],
                         "younger": younger_witness(r["id"], ydocs)},
        }
        if r["verdict"] == "MIXED":
            docs[r["id"]]["divergent_positions"] = r["divergent_positions"]
    return {
        "id": "D4",
        "kind": "sign_family_inversion",
        "status": "CONFIRMED",
        "generated_by": GENERATED_BY,
        "claim": ("the lineara.xyz tabulation behind silver swaps the livestock "
                  "logograms AB21 (*21, OVIS) and AB22 (*22, CAP) in a specific "
                  "document set; SigLA and Younger agree against it"),
        "docs": docs,
        "evidence": {
            "method": ("positional family-level alignment of silver *21/*22-family "
                       "tokens vs SigLA AB21/AB22, verdict ladder as in "
                       "scripts/audit_ab21_ab22.py; Younger fold is doc-level"),
            "per_document_verdicts": verdicts,
            "docs_with_family_tokens": len(d4_rows),
            "family_tokens": sum(len(r["silver"]) for r in d4_rows),
            "inverted_docs": len(inverted),
            "tokens_in_inverted_docs": sum(len(r["silver"]) for r in inverted),
            "agreeing_docs_not_excerpted": verdicts.get("AGREE", 0),
        },
        "sensitive_analyses": [
            "any analysis attaching commodity semantics (sheep vs goat) to the listed "
            "docs — e.g. research/observable-admin-channel-recovery commodity-logogram "
            "work; must run under both readings",
            "site- or document-level livestock counts",
        ],
        "refs": [AUDIT_DOC, f"Tsirkas 2026 D4, {TSIRKAS_REPO}"],
    }


def _entry_ht38(alt_rows, ydocs):
    divergent = [r for r in alt_rows
                 if r["verdict"] in ("INVERTED", "MIXED", "COUNT_MISMATCH",
                                     "MISSING_IN_SILVER")]
    not_attestable = sorted(r["id"] for r in alt_rows if r["verdict"] == "NOT_IN_SIGLA")
    verdicts = {}
    for r in alt_rows:
        verdicts[r["verdict"]] = verdicts.get(r["verdict"], 0) + 1
    docs = {}
    for r in divergent:
        docs[r["id"]] = {
            "verdict": r["verdict"],
            "readings": {"silver": r["silver"], "sigla": r["sigla"],
                         "younger": younger_witness(r["id"], ydocs)},
        }
    return {
        "id": "HT38",
        "kind": "livestock_token_alt_label_or_missing",
        "status": "CONFIRMED",
        "generated_by": GENERATED_BY,
        "claim": ("livestock-token divergences invisible to the *21/*22 label scan: "
                  "silver reads the Latin label CAP on HT38 where SigLA reads AB21 and "
                  "Younger reads OVIS; KH Wc 2102 and PH Wc 44 carry no livestock token "
                  "in silver where SigLA reads AB21"),
        "docs": docs,
        "evidence": {
            "method": ("scan of silver docs WITHOUT *21/*22-family labels for foldable "
                       "Latin livestock labels or a bridged SigLA doc reading "
                       "AB21/AB22 (see scan_livestock_alt_or_missing)"),
            "per_document_verdicts": verdicts,
            "alt_label_docs_not_in_sigla": not_attestable,
            "refinement": (f"{AUDIT_DOC} described HT38 as a dropped token; "
                           "mechanically the token is PRESENT in silver under the "
                           "Latin label CAP (family *22) — still divergent, consistent "
                           "with Tsirkas's report that the lineara.xyz lineage reads "
                           "*22 there"),
        },
        "sensitive_analyses": [
            "same commodity-semantics exposure as D4 on the listed docs",
            "token/type counts that assume livestock logograms are label-uniform "
            "(* -forms only) in silver",
        ],
        "refs": [AUDIT_DOC, f"Tsirkas 2026 D4, {TSIRKAS_REPO}"],
    }


def _entry_d1(annex):
    s = annex["summary"]
    return {
        "id": "D1",
        "kind": "word_attached_damage_stripped",
        "status": "CONFIRMED",
        "generated_by": GENERATED_BY,
        "claim": ("the lineara.xyz lineage strips word-attached damage notation "
                  "(marker U+1076B) from the transliteratedWords layer silver ingests; "
                  "phantom types (attested only damaged) are indistinguishable from "
                  "complete types in silver"),
        "docs": {"scope": "corpus-wide", "silver_docs": s["docs"]},
        "readings_note": {
            "bronze_words_layer": "U+1076B word-attached damage markers present",
            "silver": ("no damage field in either silver file; sidecar annex "
                       "corpus/silver/damage_annex.json carries per-token codes"),
        },
        "evidence": {
            "annex_version": annex["version"],
            "bronze_sha256": annex["bronze_sha256"],
            "summary": s,
        },
        "sensitive_analyses": [
            "distinct word-type counts (denominator shrinks under phantom exclusion "
            "— see evidence.summary)",
            "effective_n / information-budget panel inputs",
            "any type-count-sensitive figure (packed-word counts, unicity panels)",
        ],
        "refs": [f"{TSIRKAS_DOC} §2", "scripts/audit_damage_markers.py",
                 f"Tsirkas 2026 D1, {TSIRKAS_REPO}"],
    }


def _entry_br1(hits):
    return {
        "id": "BR1",
        "kind": "break_notation_in_sign_labels",
        "status": "CONFIRMED",
        "generated_by": GENERATED_BY,
        "claim": ("ASCII break notation leaked into silver sign labels: a leading ']' "
                  "or trailing '[' makes each such label a spurious distinct sign type"),
        "docs": {label: {"occurrences": occ, "implied_clean_label": label.strip("[]")}
                 for label, occ in sorted(hits.items())},
        "evidence": {
            "method": "mechanical scan: sign label starts with ']' or ends with '['",
            "n_labels": len(hits),
            "n_occurrences": sum(len(v) for v in hits.values()),
        },
        "sensitive_analyses": [
            "sign-label inventories / distinct-sign counts",
            "sequence analyses treating a broken label as a distinct sign",
        ],
        "refs": [f"{TSIRKAS_DOC} §2 (leaked ASCII brackets)"],
    }


# ---------- Round 2 (2026-08-10): rapport-series witnesses ----------
RAPPORT_DIR = os.path.join(ROOT, "corpus", "bronze", "delfreo_rapports_pre2016")
RAPPORT_TXT = {
    "1996-2000": os.path.join(RAPPORT_DIR, "olivier_rapport_1996-2000.txt"),
    "2001-2005": os.path.join(RAPPORT_DIR, "delfreo_rapport_2001-2005.txt"),
    "2006-2010": os.path.join(RAPPORT_DIR, "delfreo_rapport_2006-2010.txt"),
    "2011-2015": os.path.join(RAPPORT_DIR, "delfreo_rapport_2011-2015.txt"),
    "2016-2021": os.path.join(ROOT, "corpus", "bronze",
                              "delfreo_rapport_koronowesa", "rapport.txt"),
}
SILVER_STRUCTURED = os.path.join(ROOT, "corpus", "silver",
                                 "inscriptions_structured.json")
ROUND2_DELTA = ("experiments/crossscript_gate/phase3/sweep/round2_pre2016_rapports/"
                "ROUND2_DELTA.md")


def _ws(s):
    """Whitespace-collapse + apostrophe/quote normalization for quote matching."""
    return re.sub(r"\s+", " ", s).replace("’", "'").replace("‘", "'")


def _quote_ok(window, quote, _cache={}):
    if window not in _cache:
        _cache[window] = _ws(open(RAPPORT_TXT[window], encoding="utf-8").read())
    return _ws(quote) in _cache[window]


def _mech_ok(mech, sdoc, sigla_by_des, ydocs):
    """Evaluate one case's mechanical assertions against the live witnesses."""
    for kind, want in mech.items():
        if kind == "silver_words":
            if (sdoc or {}).get("words") != want:
                return False
        elif kind == "silver_word_at":
            i, w = want
            words = (sdoc or {}).get("words") or []
            if len(words) <= i or words[i] != w:
                return False
        elif kind == "silver_sign_present":
            if want not in ((sdoc or {}).get("signs") or []):
                return False
        elif kind == "silver_numerals":
            nums = [s["v"] for s in (sdoc or {}).get("stream", [])
                    if s.get("t") == "num"]
            if nums != want:
                return False
        elif kind == "silver_site":
            if (sdoc or {}).get("site") != want:
                return False
        elif kind == "silver_absent":
            if (sdoc is None) != want:
                return False
        elif kind == "sigla_site":
            des, site = want
            d = sigla_by_des.get(des)
            if d is None or d.get("site") != site:
                return False
        elif kind == "sigla_transcription":
            des, tr = want
            d = sigla_by_des.get(des)
            if (d["transcription"] if d else None) != tr:
                return False
        elif kind == "sigla_absent":
            if (sigla_by_des.get(want) is not None):
                return False
        elif kind == "younger_word_token":
            des, token = want
            slot = ydocs.get(des)
            rows = yp.dedup_rows(slot["rows"]) if slot else []
            if not any(token in r.get("words", []) for r in rows):
                return False
        else:
            raise ValueError(f"unknown mech assertion: {kind}")
    return True


# Each case: quotes are (window, page, verbatim-substring) triples verified against
# the held rapport text; mech assertions are derived live; readings excerpted are
# defect-level only (register policy). silver_id None = no single silver doc.
R2_ENTRIES = [
    ("R2READ", "rapport_reading_divergences",
     "token-level reading divergences between silver and the rapport series "
     "1996-2021 (each rapport-side reading verified as a verbatim quote against "
     "the held rapport text at build time)", [
     dict(case="KNZb<27>", silver_id="KNZb<27>",
          quotes=[("2011-2015", "p. 17", "sur le bord du pithos n'est pas 117")],
          mech={"silver_numerals": [17]},
          rapport_side="AB 07-06-10 , AB 131 107 — numeral read 17 (dotted) by "
                       "GORILA IV from Brice's photo, corrected to 117 by Olivier "
                       "(Rapport 1986-1990, 446) after MacDonald rediscovered the "
                       "pithos, fixed as 107 by Del Freo & Zurbach autopsy "
                       "2012-06-22; silver retains GORILA's 17 AND the <lost> "
                       "angle brackets although the pithos was rediscovered"),
     dict(case="KHWc2124", silver_id="KHWc2124",
          quotes=[("2006-2010", "p. 8", "on lit le logogramme AB 54"),
                  ("2016-2021", "p. 101", "une variante de AB 61 dépourvue du")],
          mech={"silver_words": [["WA"]]},
          rapport_side="recto sign first reported as AB 54 (TELA) in Rapport "
                       "2006-2010; the 2018 ed.pr. + Rapport 2016-2021 correct it "
                       "to a variant of AB 61 without the inner curved stroke; "
                       "silver retains the superseded AB 54 (as syllabic WA)"),
     dict(case="THEZb15", silver_id="THEZb15",
          quotes=[("2006-2010", "pp. 12-13", "La lecture proposée est AB 09-A"),
                  ("2016-2021", "p. 106", "par les éditeurs comme Zb 15")],
          mech={"silver_words": [["RE", "SA"]], "silver_numerals": [2]},
          rapport_side="ed.pr. (Tzachili & Karnava 2016, as Zb 15) and the rapport "
                       "series read AB 09-A 332(dotted) 2 (alt AB 73); silver reads "
                       "RE-SA 2 (= AB 27-31 2) — divergent identification of the "
                       "same lamp graffito (object identity fixed by the trailing "
                       "numeral 2 + support); Del Freo numbers it Zb 14 (additions "
                       "layer holds it under that number — duplicate noted there)"),
     dict(case="HTWc3024", silver_id="HTWc3024",
          quotes=[("2001-2005", "p. 202 fn. 13", "pour HT Wc 3024 (.1 AB 06-60-69"),
                  ("2001-2005", "p. 202 fn. 13", "2 AB 21f 6")],
          mech={"silver_word_at": (0, ["A", "RA", "TU", "ME"]),
                "silver_sign_present": "*22F", "silver_numerals": []},
          rapport_side="rapport (after Hallager, Godart & Olivier 1989): .1 AB "
                       "06-60-69-13(dotted) .2 AB 21f 6 — silver reads the first "
                       "sign as A (08) not NA (06), renders the livestock logogram "
                       "as *22F where the rapport prints 21f (an AB21/22-family "
                       "instance NOT caught by the D4 scan: no *21/*22 label and "
                       "no SigLA bridge), and drops the numeral 6"),
     dict(case="PKZb26", silver_id="PKZb26",
          quotes=[("2001-2005", "p. 205", "la séquence incomplète ]AB 05-56-08")],
          mech={"silver_words": [["TO", "PA3", "DI"]]},
          rapport_side="]AB 05-56-08 (hapax) per Schoep's preliminary manuscript "
                       "apud the rapport; silver's third sign is DI (07), not "
                       "A (08)"),
     dict(case="SKOZc1", silver_id="SKOZc1",
          quotes=[("2001-2005", "pp. 206-207", "]AB 1°6°-6°7°-7°9°[")],
          mech={"silver_word_at": (1, ["QA", "KI", "TI"])},
          rapport_side="smaller fragment read ]AB 16-67-79[ (all dotted) by the "
                       "editors apud the rapport; silver's third sign is TI (37), "
                       "not ZU (79) — both sources heavily dotted"),
     ]),
    ("R2DOUBT", "doubted_items_included",
     "items present in silver with committed readings where the rapport series "
     "suspends judgement, objects, or leaves the script undecided", [
     dict(case="KNZe56", silver_id="KNZe56",
          quotes=[("1996-2000", "p. 190", "dont aucun n'est vraiment lisible")],
          mech={"silver_words": [["O", "DA"]]},
          rapport_side="Olivier: remains of three signs, none really legible; "
                       "plough/machine marks not excluded; silver commits O-DA"),
     dict(case="LACHZa1", silver_id="LACHZa1",
          quotes=[("1996-2000", "p. 193",
                   "généreusement attribuée à cette inscription est vraiment "
                   "prématurée")],
          mech={"silver_word_at": (0, ["MI"])},
          rapport_side="Olivier: the designation LACH Za 1 is premature — the two "
                       "readable signs fit LA, LB, Cypro-Minoan or the Cypriot "
                       "syllabary equally; silver includes it with a full six-sign "
                       "reading (see also R2SITE for its site label)"),
     dict(case="DRAZg1", silver_id="DRAZg1",
          quotes=[("2001-2005", "p. 211",
                   "l'identification du premier signe avec AB 01 semble plutôt "
                   "discutable")],
          mech={"silver_word_at": (0, ["DA", "DU", "*301"])},
          rapport_side="Fol & Schmitt's reading AB 01-51-A301-[.]-[.]; Del Freo: "
                       "photos do not permit assessment and the first sign is "
                       "doubtful; silver commits DA-DU-*301"),
     dict(case="INZb1", silver_id="INZb1",
          quotes=[("2011-2015", "pp. 16-17",
                   "la lecture AB 55-02 demeure pour le moins")],
          mech={"silver_words": [["NU", "RO"]]},
          rapport_side="Del Freo: both the reading AB 55-02 and the classification "
                       "as an inscription remain at best uncertain; silver commits "
                       "NU-RO"),
     dict(case="MIZb3", silver_id="MIZb3",
          quotes=[("2001-2005", "p. 212 fn. 62", "Le classement MI Zb 3")],
          mech={"silver_words": [["RE", "TI"]]},
          rapport_side="Del Freo adopts Sherratt's caution (signs not certainly "
                       "literate) and calls the MI Zb 3 classification "
                       "questionable; silver includes it as RE-TI"),
     dict(case="PKZb23", silver_id="PKZb23",
          quotes=[("1996-2000", "p. 191", "esquisse grossière"),
                  ("1996-2000", "p. 191", "qu'un signe AB 87")],
          mech={"silver_words": [["KA"]]},
          rapport_side="Olivier: rather a rough chariot sketch than the sign "
                       "AB 87; silver commits KA (77) — a sign neither source "
                       "offers"),
     dict(case="PEZb8", silver_id="PEZb8",
          quotes=[("2011-2015", "p. 14",
                   "ne sera pas inclus parmi les nouvelles inscriptions")],
          mech={"silver_words": [["A"]]},
          rapport_side="isolated AB 08 of unsure logographic value; the GORILA "
                       "Supplement's inclusion criteria exclude it; silver "
                       "includes it"),
     dict(case="HTZf(HM767)", silver_id="HTZf(HM767)",
          quotes=[("2011-2015", "p. 17",
                   "sans spécifier s'il s'agit de linéaire A ou de linéaire B")],
          mech={"silver_words": [["TI", "MA"]]},
          rapport_side="Kanta & Perna deliberately call the gold-disc inscription "
                       "only 'linear' (AB 37-80 attested in both scripts); silver "
                       "classifies it as LA"),
     ]),
    ("R2SITE", "site_label_defects",
     "silver site labels contradicted by the witnesses", [
     dict(case="ARKH-series", silver_id="ARKHZf9",
          quotes=[("2001-2005", "p. 203", "2.2.1.1. Arkhanès")],
          mech={"silver_site": "Arkhalkhori",
                "sigla_site": ("ARKH 2", "Arkhanes")},
          rapport_side="the rapport series (and SigLA's site grouping) place the "
                       "ARKH items at Arkhanes; silver labels the entire series "
                       "(ARKH 1a-6, Zc 8, Zf 9 — and also ARG Zg 1) 'Arkhalkhori' "
                       "(= Arkalochori), merging two sites; representative doc "
                       "excerpted here, full list in ROUND2_DELTA Δ10"),
     dict(case="LACHZa1-site", silver_id="LACHZa1",
          quotes=[("1996-2000", "p. 193",
                   "généreusement attribuée à cette inscription est vraiment "
                   "prématurée")],
          mech={"silver_site": "Larani",
                "younger_word_token": ("LACH Za 1", "LARANI")},
          rapport_side="Tel Lachish (Canaan) — silver's site label 'Larani' (a "
                       "Cretan site) is a defect; origin witnessed: Younger's "
                       "LACH Za 1 row carries LARANI as a comparandum token, "
                       "which the lineara.xyz lineage evidently promoted to a "
                       "site label"),
     ]),
    ("R2THE", "thera_adhoc_identity",
     "identity of silver's ad-hoc Thera IDs (THEfr.1-3, THEtab.4-5) against the "
     "rapport series' THE 7-12 and SigLA", [
     dict(case="THEtab.4=THE7", silver_id="THEtab.4",
          quotes=[("2006-2010", "p. 12",
                   "le logogramme AB 21f suivi par le chiffre 46")],
          mech={"silver_numerals": [7, 46], "sigla_absent": "THE 7"},
          rapport_side="Boulotis's THE 7 face a: sign traces + numeral 7, then "
                       "AB 21f + numeral 46 — silver THEtab.4's numeral pair "
                       "[7, 46] matches exactly (its two livestock tokens render "
                       "as CAP where the rapport prints 21f = OVISf: the D4 "
                       "register entry already lists THEtab.4); SigLA has no "
                       "THE 7. IDENTITY: near-certain"),
     dict(case="THEfr.1=THE10", silver_id="THEfr.1",
          quotes=[("2006-2010", "p. 12", "le signe isolé AB 67 est attesté")],
          mech={"silver_words": [["KI"]],
                "sigla_transcription": ("THE 10", ["AB67"])},
          rapport_side="Boulotis's THE 10 = isolated AB 67; silver THEfr.1 = KI "
                       "(67); SigLA THE 10 = AB67. IDENTITY: three witnesses "
                       "agree"),
     dict(case="THEfr.2/3-vs-THE11/12", silver_id="THEfr.2",
          quotes=[("2006-2010", "p. 12",
                   "des traces peut-être compatibles avec le logogramme A 302")],
          mech={"silver_words": [["OLE"]],
                "sigla_transcription": ("THE 11", ["A614"])},
          rapport_side="Boulotis: THE 11/12 carry traces maybe compatible with "
                       "A 302 (silver THEfr.2/3 = OLE = A 302 fits) but SigLA "
                       "reads THE 11 = A614 and THE 12 = AB22. IDENTITY: "
                       "witness-conflicted, left open",
          verdict="UNDERDETERMINED_WITNESS_CONFLICT"),
     dict(case="THEtab.5-vs-THE9", silver_id="THEtab.5",
          quotes=[("2006-2010", "p. 12", "ne contenant pas de logogrammes")],
          mech={"silver_words": [["TE", "ME", "DA", "I"]],
                "sigla_transcription": ("THE 9", ["AB04", "AB23", "AB31", "AB09"])},
          rapport_side="Boulotis's THE 9 is the fragment without logograms (not "
                       "discussed further); silver THEtab.5 is syllabic "
                       "TE-ME-DA-I; SigLA's THE 9 reads AB04-23-31-09 — first "
                       "sign agrees, the rest conflicts. IDENTITY: by elimination "
                       "only, witness-conflicted",
          verdict="UNDERDETERMINED_WITNESS_CONFLICT"),
     dict(case="THE8-missing", silver_id=None,
          quotes=[("2006-2010", "p. 12", "suivi par le chiffre 200[")],
          mech={"sigla_transcription": ("THE 8", ["AB02", "A559", "A534"])},
          rapport_side="Boulotis's THE 8 (ligature AB 54+09 — the proposed "
                       "A 534bis — + numeral 200[) has NO silver counterpart "
                       "under any ad-hoc ID; SigLA carries THE 8 (with A534). "
                       "MISSING_IN_SILVER",
          verdict="MISSING_IN_SILVER"),
     ]),
    ("R2REST", "restoration_unmarked",
     "restored formula text carried in silver without break/restoration marking "
     "(D1-family: the lineage strips damage and break notation)", [
     dict(case="IOZa16", silver_id="IOZa16",
          quotes=[("2001-2005", "p. 203", "ce dernier incomplet")],
          mech={"silver_word_at": (3, ["U", "NA", "RU", "KA", "NA", "SI"])},
          rapport_side="ed.pr. apud rapport prints AB 10-06-26-77[ (breaks off); "
                       "silver carries the full restored formula U-NA-RU-KA-NA-SI "
                       "with no break marking"),
     dict(case="PKZa27", silver_id="PKZa27",
          quotes=[("2011-2015", "p. 13", "U-NA-KA-NA-SI soit attestée")],
          mech={"silver_word_at": (1, ["U", "NA", "KA", "NA", "SI"])},
          rapport_side="rapport prints 10(dotted)-06-77-.[ with the last sign "
                       "uncertain or a divider; silver carries the full formula "
                       "U-NA-KA-NA-SI unmarked"),
     dict(case="SYZa8", silver_id="SYZa8",
          quotes=[("2006-2010", "p. 10", "]AB 28-A 301-AB 54-AB 57")],
          mech={"silver_word_at": (0, ["A", "TA", "I", "*301", "WA", "JA"])},
          rapport_side="ed.pr. apud rapport prints ]AB 28-A301-54-57 (broken "
                       "before 28); silver carries the full six-sign formula "
                       "opening unmarked"),
     ]),
]


def _entry_r2(entry_id, kind, claim, cases, structured_by_id, sigla_by_des, ydocs):
    docs, failures = {}, []
    for c in cases:
        sdoc = structured_by_id.get(c["silver_id"]) if c["silver_id"] else None
        quotes_ok = all(_quote_ok(w, q) for w, _, q in c["quotes"])
        mech = dict(c["mech"])
        if c["silver_id"] is None:
            mech.pop("silver_absent", None)
        mech_ok = _mech_ok(mech, sdoc, sigla_by_des, ydocs)
        if not (quotes_ok and mech_ok):
            failures.append({"case": c["case"], "quotes_ok": quotes_ok,
                             "mech_ok": mech_ok})
            continue
        rec = {
            "verdict": c.get("verdict", "CONFIRMED"),
            "silver_reading": ({"words": sdoc.get("words"),
                                "numerals": [s["v"] for s in sdoc.get("stream", [])
                                             if s.get("t") == "num"],
                                "site": sdoc.get("site")} if sdoc else None),
            "rapport_side": c["rapport_side"],
            "rapport_quotes": [{"window": w, "page": p, "quote": q,
                                "verified_in_held_text": True}
                               for w, p, q in c["quotes"]],
        }
        docs[c["case"]] = rec
    if failures:
        raise SystemExit(f"{entry_id}: build-time verification FAILED: {failures}")
    return {
        "id": entry_id, "kind": kind, "status": "CONFIRMED",
        "generated_by": GENERATED_BY, "claim": claim, "docs": docs,
        "evidence": {
            "method": ("declared rapport quotes verified verbatim "
                       "(whitespace-normalized) against the held rapport texts; "
                       "silver readings derived live from "
                       "corpus/silver/inscriptions_structured.json; SigLA/Younger "
                       "sides derived live where available"),
            "n_cases": len(docs),
        },
        "sensitive_analyses": [
            "any reuse keyed on the affected tokens, sites or document identities "
            "— run under both readings (register policy)",
            "site-clustered statistics (R2SITE); type/token counts touching the "
            "listed docs",
        ],
        "refs": [ROUND2_DELTA,
                 "corpus/bronze/delfreo_rapports_pre2016/PROVENANCE.md"],
    }


def build_register(silver_path=SILVER, sigla_path=SIGLA, annex_path=ANNEX,
                   younger_dir=yp.YOUNGER_DIR):
    silver, sigla_by_des = load_witnesses(silver_path, sigla_path)
    annex = json.load(open(annex_path, encoding="utf-8"))
    ydocs = yp.parse_dir(younger_dir)
    structured_by_id = {r["id"]: r for r in
                       json.load(open(SILVER_STRUCTURED, encoding="utf-8"))}

    d4_rows = scan_family_inversion(silver, sigla_by_des)
    alt_rows = scan_livestock_alt_or_missing(silver, sigla_by_des)
    br_hits = bracket_residue(silver)

    register = {
        "_meta": {
            "version": VERSION,
            "generated_by": GENERATED_BY,
            "policy": ("defect-level excerpts only (fair dealing); agreeing documents "
                       "are counted, never excerpted; append-only record (Art. XVII): "
                       "silver is NEVER rebuilt from this file — any analysis touching "
                       "a registered divergence runs under both readings"),
            "regenerate": "python3 scripts/divergence_register.py",
            "witness_sha256": {
                "silver_inscriptions": _sha(silver_path),
                "silver_structured": _sha(SILVER_STRUCTURED),
                "sigla_documents": _sha(sigla_path),
                "damage_annex": _sha(annex_path),
                "younger_txt": {fn: _sha(os.path.join(younger_dir, fn))
                                for fn in yp.FILES
                                if os.path.exists(os.path.join(younger_dir, fn))},
                "rapport_txt": {w: _sha(p) for w, p in sorted(RAPPORT_TXT.items())
                                if os.path.exists(p)},
            },
            "refs": [AUDIT_DOC, TSIRKAS_DOC, ROUND2_DELTA],
        },
        "entries": [
            _entry_d4(d4_rows, ydocs),
            _entry_ht38(alt_rows, ydocs),
            _entry_d1(annex),
            _entry_br1(br_hits),
        ] + [_entry_r2(eid, kind, claim, cases, structured_by_id, sigla_by_des,
                       ydocs)
             for eid, kind, claim, cases in R2_ENTRIES],
    }
    return register, d4_rows


def dumps(register):
    return json.dumps(register, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true",
                    help="rebuild and compare against the committed register")
    ap.add_argument("--summary-only", action="store_true")
    args = ap.parse_args(argv)

    for p in (SILVER, SILVER_STRUCTURED, SIGLA, ANNEX, *RAPPORT_TXT.values()):
        if not os.path.exists(p):
            sys.exit(f"witness not found: {p} (licensed/private data; see "
                     f"corpus/bronze — the rapport texts are the private author "
                     f"PDFs, see delfreo_rapports_pre2016/PROVENANCE.md)")

    register, d4_rows = build_register()
    e = {en["id"]: en for en in register["entries"]}
    print(f"divergence register ({VERSION})")
    print(f"D4: {e['D4']['evidence']['docs_with_family_tokens']} docs / "
          f"{e['D4']['evidence']['family_tokens']} family tokens scanned; "
          f"verdicts {e['D4']['evidence']['per_document_verdicts']}; "
          f"INVERTED {e['D4']['evidence']['inverted_docs']} docs / "
          f"{e['D4']['evidence']['tokens_in_inverted_docs']} tokens")
    print(f"HT38: verdicts {e['HT38']['evidence']['per_document_verdicts']}; "
          f"excerpted docs {sorted(e['HT38']['docs'])}")
    print(f"D1: {e['D1']['evidence']['summary']['word_tokens']} word tokens, "
          f"{e['D1']['evidence']['summary']['damage_touching_tokens']} damage-touching; "
          f"{e['D1']['evidence']['summary']['phantom_types']} phantom types of "
          f"{e['D1']['evidence']['summary']['distinct_types']}")
    print(f"BR1: {e['BR1']['evidence']['n_labels']} labels / "
          f"{e['BR1']['evidence']['n_occurrences']} occurrences: "
          f"{sorted(e['BR1']['docs'])}")
    for rid in ("R2READ", "R2DOUBT", "R2SITE", "R2THE", "R2REST"):
        verdicts = {}
        for d in e[rid]["docs"].values():
            verdicts[d["verdict"]] = verdicts.get(d["verdict"], 0) + 1
        print(f"{rid}: {e[rid]['evidence']['n_cases']} cases "
              f"(all quotes verified); verdicts {verdicts}")

    if args.check:
        committed = open(args.out, encoding="utf-8").read()
        if committed == dumps(register):
            print(f"check: {args.out} is up to date")
            return 0
        print(f"check: {args.out} DIFFERS from a fresh rebuild — regenerate and "
              f"review the diff (append-only discipline: never hand-edit)")
        return 1
    if not args.summary_only:
        open(args.out, "w", encoding="utf-8").write(dumps(register))
        print(f"register -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
