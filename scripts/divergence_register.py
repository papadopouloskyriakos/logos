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

VERSION = "divergence-register-v1"
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


def build_register(silver_path=SILVER, sigla_path=SIGLA, annex_path=ANNEX,
                   younger_dir=yp.YOUNGER_DIR):
    silver, sigla_by_des = load_witnesses(silver_path, sigla_path)
    annex = json.load(open(annex_path, encoding="utf-8"))
    ydocs = yp.parse_dir(younger_dir)

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
                "sigla_documents": _sha(sigla_path),
                "damage_annex": _sha(annex_path),
                "younger_txt": {fn: _sha(os.path.join(younger_dir, fn))
                                for fn in yp.FILES
                                if os.path.exists(os.path.join(younger_dir, fn))},
            },
            "refs": [AUDIT_DOC, TSIRKAS_DOC],
        },
        "entries": [
            _entry_d4(d4_rows, ydocs),
            _entry_ht38(alt_rows, ydocs),
            _entry_d1(annex),
            _entry_br1(br_hits),
        ],
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

    for p in (SILVER, SIGLA, ANNEX):
        if not os.path.exists(p):
            sys.exit(f"witness not found: {p} (licensed data; see corpus/bronze)")

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
