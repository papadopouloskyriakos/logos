#!/usr/bin/env python3
"""B1 — Linear A segmentation representations (Constitution v2.2; non-circular).

Builds eight segmentation representations of the Linear A corpus, each preserving
SOURCE PROVENANCE (every unit carries its inscription id / site / support / period)
and REVERSIBILITY (every unit carries the stream span + word-index range it came
from, so any sign can be traced back to its inscription and position).

Single source of truth: corpus/silver/inscriptions_structured.json (1,341
inscriptions, 52 sites). Stream tokens: word / nl / num / div / other(raw).

Representations
  SEG_DIPLOMATIC             raw inscription sign stream          (unit = inscription)
  SEG_GORILA_WORD            GORILA word units                    (unit = word)
  SEG_INSCRIPTION_CONTEXT    whole inscription as one unit        (unit = inscription, +ctx)
  SEG_ROW                    line/row units (split at 'nl')       (unit = row)
  SEG_ENTRY                  administrative word+numeral groups   (unit = entry)
  SEG_FORMULA                formula-carrier segments (numeral-free word runs)
  SEG_PROBABILISTIC_BOUNDARY per-position boundary prob (unsup. branching entropy)
  SEG_MULTI_SCALE            nested word / entry / inscription

NON-CIRCULARITY: no phonetic value is ever an input. The GORILA word boundaries
are used ONLY to GRADE the unsupervised boundary detector (never to train it).
Seed 20260708. Deterministic; read-only corpus.
"""
from __future__ import annotations

import json
import math
import os
import statistics
import sys
from collections import Counter, defaultdict

WT = "/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals"
sys.path.insert(0, WT)

SEED = 20260708
HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
STRUCT = os.path.join(WT, "corpus", "silver", "inscriptions_structured.json")
OUTDIR = os.path.join(CAMP, "data", "segmentations")
os.makedirs(OUTDIR, exist_ok=True)

PROV_SRC = "corpus/silver/inscriptions_structured.json"


def load_struct():
    return json.load(open(STRUCT))


def meta(rec):
    return {
        "inscription_id": rec["id"],
        "site": rec.get("site"),
        "support": rec.get("support"),
        "period": rec.get("context"),
    }


def mean_len(units, key="signs"):
    lens = [len(u[key]) for u in units]
    if not lens:
        return 0.0, 0
    return sum(lens) / len(lens), sum(lens)


def write_rep(name, description, units, extra=None):
    lens = [len(u["signs"]) for u in units] if units and "signs" in units[0] else []
    ml = (sum(lens) / len(lens)) if lens else 0.0
    payload = {
        "representation": name,
        "description": description,
        "provenance": {
            "source_file": PROV_SRC,
            "seed": SEED,
            "reversible": True,
            "reversibility_note": (
                "each unit carries inscription_id + stream span (word_index range and/or "
                "stream token indices); a sign at unit position p traces to (inscription_id, "
                "word_index, sign position)."
            ),
        },
        "n_units": len(units),
        "n_signs_total": sum(lens),
        "mean_length_signs": round(ml, 4),
        "units": units,
    }
    if extra:
        payload.update(extra)
    path = os.path.join(OUTDIR, name + ".json")
    json.dump(payload, open(path, "w"), ensure_ascii=False, indent=1)
    return {
        "representation": name,
        "n_units": len(units),
        "mean_length_signs": round(ml, 4),
        "n_signs_total": sum(lens),
        "path": os.path.relpath(path, WT),
    }


# ---------------------------------------------------------------------------
# stream parsing helpers
# ---------------------------------------------------------------------------
def word_tokens(rec):
    """List of (word_index_in_stream, signs) for 'word' tokens, in stream order."""
    out = []
    for si, tok in enumerate(rec.get("stream") or []):
        if tok.get("t") == "word":
            out.append((si, list(tok.get("signs", []))))
    return out


# ---------------------------------------------------------------------------
# 1. SEG_DIPLOMATIC  — raw inscription sign stream
# ---------------------------------------------------------------------------
def build_diplomatic(recs):
    units = []
    for rec in recs:
        signs = list(rec.get("signs", []))
        if not signs:
            continue
        m = meta(rec)
        units.append({
            "unit_id": rec["id"] + "#dip",
            **m,
            "signs": signs,
            "span": {"n_signs": len(signs), "stream_tokens": len(rec.get("stream") or [])},
        })
    return units


# ---------------------------------------------------------------------------
# 2. SEG_GORILA_WORD  — GORILA word units
# ---------------------------------------------------------------------------
def build_gorila_word(recs):
    units = []
    for rec in recs:
        m = meta(rec)
        for wi, (stream_idx, signs) in enumerate(word_tokens(rec)):
            if not signs:
                continue
            units.append({
                "unit_id": f"{rec['id']}#w{wi}",
                **m,
                "signs": signs,
                "span": {"word_index": wi, "stream_index": stream_idx},
            })
    return units


# ---------------------------------------------------------------------------
# 3. SEG_INSCRIPTION_CONTEXT  — whole inscription as one context unit
# ---------------------------------------------------------------------------
def build_inscription_context(recs):
    units = []
    for rec in recs:
        signs = list(rec.get("signs", []))
        if not signs:
            continue
        m = meta(rec)
        stream = rec.get("stream") or []
        nums = [t["v"] for t in stream if t.get("t") == "num"]
        words = word_tokens(rec)
        units.append({
            "unit_id": rec["id"] + "#ctx",
            **m,
            "signs": signs,
            "context": {
                "n_words": len(words),
                "n_numerals": len(nums),
                "numerals": nums,
                "n_rows": 1 + sum(1 for t in stream if t.get("t") == "nl"),
            },
            "span": {"n_signs": len(signs), "whole_inscription": True},
        })
    return units


# ---------------------------------------------------------------------------
# 4. SEG_ROW  — line / row units (split at 'nl')
# ---------------------------------------------------------------------------
def build_rows(recs):
    units = []
    for rec in recs:
        m = meta(rec)
        stream = rec.get("stream") or []
        row_idx = 0
        cur_signs = []
        cur_nums = []
        cur_word_idxs = []
        wcount = 0

        def flush():
            nonlocal row_idx, cur_signs, cur_nums, cur_word_idxs
            if cur_signs:
                units.append({
                    "unit_id": f"{rec['id']}#row{row_idx}",
                    **m,
                    "signs": list(cur_signs),
                    "numerals": list(cur_nums),
                    "span": {"row_index": row_idx, "word_indices": list(cur_word_idxs)},
                })
                row_idx += 1
            cur_signs = []
            cur_nums = []
            cur_word_idxs = []

        for tok in stream:
            t = tok.get("t")
            if t == "word":
                cur_signs.extend(tok.get("signs", []))
                cur_word_idxs.append(wcount)
                wcount += 1
            elif t == "num":
                cur_nums.append(tok.get("v"))
            elif t == "nl":
                flush()
        flush()
    return units


# ---------------------------------------------------------------------------
# 5. SEG_ENTRY  — administrative entry = word(s)+numeral group
#    6. SEG_FORMULA harvested in the same pass (numeral-free word runs)
# ---------------------------------------------------------------------------
def build_entries_and_formula(recs):
    entries = []
    formula = []
    for rec in recs:
        m = meta(rec)
        stream = rec.get("stream") or []
        buf_signs = []
        buf_word_idxs = []
        wcount = 0
        e_idx = 0
        f_idx = 0

        def flush_entry(val):
            nonlocal buf_signs, buf_word_idxs, e_idx
            if buf_signs:
                entries.append({
                    "unit_id": f"{rec['id']}#e{e_idx}",
                    **m,
                    "signs": list(buf_signs),
                    "numeral": val,
                    "span": {"entry_index": e_idx, "word_indices": list(buf_word_idxs)},
                })
                e_idx += 1
            buf_signs = []
            buf_word_idxs = []

        def flush_formula():
            nonlocal buf_signs, buf_word_idxs, f_idx
            if buf_signs:
                formula.append({
                    "unit_id": f"{rec['id']}#f{f_idx}",
                    **m,
                    "signs": list(buf_signs),
                    "span": {"formula_index": f_idx, "word_indices": list(buf_word_idxs)},
                })
                f_idx += 1
            buf_signs = []
            buf_word_idxs = []

        for tok in stream:
            t = tok.get("t")
            if t == "word":
                buf_signs.extend(tok.get("signs", []))
                buf_word_idxs.append(wcount)
                wcount += 1
            elif t == "num":
                flush_entry(tok.get("v"))
            elif t == "nl":
                # a line that ended with word(s) and no numeral = non-accounting text
                flush_formula()
        # trailing residue with no numeral = formula carrier
        flush_formula()
    return entries, formula


# ---------------------------------------------------------------------------
# 6b. formula recurrence annotation (mechanical; no values used)
# ---------------------------------------------------------------------------
def annotate_formula_recurrence(formula):
    seq_counts = Counter(tuple(u["signs"]) for u in formula)
    insc_of = defaultdict(set)
    for u in formula:
        insc_of[tuple(u["signs"])].add(u["inscription_id"])
    for u in formula:
        key = tuple(u["signs"])
        u["recurrence"] = {
            "seq_count": seq_counts[key],
            "n_inscriptions": len(insc_of[key]),
            "is_recurrent": len(insc_of[key]) >= 2,
        }
    return formula


# ---------------------------------------------------------------------------
# 7. SEG_PROBABILISTIC_BOUNDARY  — unsupervised branching-entropy boundary model
# ---------------------------------------------------------------------------
def build_probabilistic_boundary(recs, grade_words=True):
    # Corpus of diplomatic sign streams (>=2 signs so gaps exist).
    streams = [(rec["id"], list(rec.get("signs", []))) for rec in recs]
    streams = [(i, s) for i, s in streams if len(s) >= 2]

    # order-1 successor / predecessor distributions over the whole corpus
    succ = defaultdict(Counter)   # a -> Counter(b)
    pred = defaultdict(Counter)   # b -> Counter(a)
    for _, s in streams:
        for a, b in zip(s, s[1:]):
            succ[a][b] += 1
            pred[b][a] += 1

    def entropy(counter):
        tot = sum(counter.values())
        if tot == 0:
            return 0.0
        h = 0.0
        for c in counter.values():
            p = c / tot
            h -= p * math.log(p, 2)
        return h

    Hr = {a: entropy(c) for a, c in succ.items()}   # right branching entropy after a
    Hl = {b: entropy(c) for b, c in pred.items()}   # left branching entropy before b

    # raw boundary score at gap between a (left) and b (right) = mean(Hr[a], Hl[b])
    gap_records = []  # (insc_id, gap_index, a, b, raw_score)
    for iid, s in streams:
        for gi in range(len(s) - 1):
            a, b = s[gi], s[gi + 1]
            raw = 0.5 * (Hr.get(a, 0.0) + Hl.get(b, 0.0))
            gap_records.append([iid, gi, a, b, raw])

    raws = [g[4] for g in gap_records]
    lo, hi = min(raws), max(raws)
    span = (hi - lo) or 1.0
    mean_raw = statistics.mean(raws)

    # per-inscription boundary map + induced segmentation (cut where prob > global mean)
    thr = (mean_raw - lo) / span  # normalized global-mean threshold (Harris-style)
    per_insc = defaultdict(list)
    for iid, gi, a, b, raw in gap_records:
        prob = (raw - lo) / span
        per_insc[iid].append((gi, prob))

    units = []            # induced segments
    boundary_map = []     # per-inscription boundary-probability vector (reversible)
    for iid, s in streams:
        gaps = dict(per_insc[iid])
        probs = [round(gaps.get(gi, 0.0), 5) for gi in range(len(s) - 1)]
        cut_after = [gi for gi in range(len(s) - 1) if probs[gi] > thr]
        boundary_map.append({
            "inscription_id": iid,
            "signs": s,
            "boundary_prob": probs,          # prob of a boundary in gap gi (between sign gi,gi+1)
            "cut_after_positions": cut_after,
            "threshold": round(thr, 5),
        })
        # induce segments from cuts
        start = 0
        seg_no = 0
        for gi in cut_after + [len(s) - 1]:
            seg = s[start:gi + 1]
            if seg:
                units.append({
                    "unit_id": f"{iid}#p{seg_no}",
                    "inscription_id": iid,
                    "signs": seg,
                    "span": {"sign_start": start, "sign_end": gi},
                })
                seg_no += 1
            start = gi + 1

    # ---- grading ONLY (GORILA word boundaries never entered the model) ----
    grade = None
    if grade_words:
        tp = fp = fn = 0
        recs_by_id = {r["id"]: r for r in recs}
        for bm in boundary_map:
            rec = recs_by_id[bm["inscription_id"]]
            # gold boundaries: positions after which a GORILA word ends (in the flat sign stream)
            gold = set()
            pos = 0
            wt = word_tokens(rec)
            # reconstruct flat gold cut positions from consecutive word lengths
            cum = 0
            for _, wsigns in wt:
                cum += len(wsigns)
                gold.add(cum - 1)  # boundary AFTER last sign of this word
            n = len(bm["signs"])
            gold_internal = {g for g in gold if 0 <= g < n - 1}
            pred = set(bm["cut_after_positions"])
            tp += len(pred & gold_internal)
            fp += len(pred - gold_internal)
            fn += len(gold_internal - pred)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec_ = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec_ / (prec + rec_) if (prec + rec_) else 0.0
        grade = {
            "note": "GORILA word boundaries used ONLY to grade the unsupervised model (never an input).",
            "boundary_precision": round(prec, 4),
            "boundary_recall": round(rec_, 4),
            "boundary_f1": round(f1, 4),
            "tp": tp, "fp": fp, "fn": fn,
        }

    extra = {
        "model": "unsupervised order-1 branching-entropy (Jin & Tanaka-Ishii style)",
        "n_gaps_scored": len(gap_records),
        "global_mean_threshold_norm": round(thr, 5),
        "boundary_map": boundary_map,
        "grading_vs_gorila_words": grade,
    }
    return units, extra


# ---------------------------------------------------------------------------
# 8. SEG_MULTI_SCALE  — nested word / entry / inscription
# ---------------------------------------------------------------------------
def build_multi_scale(recs):
    units = []  # one nested unit per inscription
    n_entries = n_words = n_formula = 0
    words_per_entry = []
    for rec in recs:
        m = meta(rec)
        stream = rec.get("stream") or []
        # words with indices
        wt = word_tokens(rec)
        if not wt:
            continue
        # entries/formula via the same numeral logic
        entries = []
        formula = []
        buf = []           # list of (word_index, signs)
        wcount = 0
        for tok in stream:
            t = tok.get("t")
            if t == "word":
                buf.append((wcount, list(tok.get("signs", []))))
                wcount += 1
            elif t == "num":
                if buf:
                    entries.append({
                        "type": "entry",
                        "numeral": tok.get("v"),
                        "words": [{"word_index": wi, "signs": sg} for wi, sg in buf],
                        "signs": [s for _, sg in buf for s in sg],
                    })
                    words_per_entry.append(len(buf))
                    buf = []
            elif t == "nl":
                if buf:
                    formula.append({
                        "type": "formula",
                        "words": [{"word_index": wi, "signs": sg} for wi, sg in buf],
                        "signs": [s for _, sg in buf for s in sg],
                    })
                    buf = []
        if buf:
            formula.append({
                "type": "formula",
                "words": [{"word_index": wi, "signs": sg} for wi, sg in buf],
                "signs": [s for _, sg in buf for s in sg],
            })
        children = entries + formula
        all_signs = [s for _, sg in wt for s in sg]
        n_entries += len(entries)
        n_formula += len(formula)
        n_words += len(wt)
        units.append({
            "unit_id": rec["id"] + "#ms",
            **m,
            "signs": all_signs,                       # inscription scale (leaf-aggregate)
            "scales": {
                "inscription": {"n_signs": len(all_signs), "n_words": len(wt)},
                "entries": entries,
                "formula": formula,
            },
            "span": {"n_words": len(wt), "n_entries": len(entries), "n_formula": len(formula)},
        })
    levels = {
        "n_inscriptions": len(units),
        "n_entries": n_entries,
        "n_formula_runs": n_formula,
        "n_words": n_words,
        "mean_words_per_entry": round(statistics.mean(words_per_entry), 4) if words_per_entry else 0.0,
    }
    return units, levels


# ---------------------------------------------------------------------------
def main():
    recs = load_struct()
    summary = {"seed": SEED, "source": PROV_SRC, "n_inscriptions_total": len(recs),
               "n_sites": len(set(r["site"] for r in recs)), "representations": []}

    dip = build_diplomatic(recs)
    summary["representations"].append(write_rep(
        "SEG_DIPLOMATIC", "Raw inscription sign stream; one unit per inscription.", dip))

    gw = build_gorila_word(recs)
    summary["representations"].append(write_rep(
        "SEG_GORILA_WORD", "GORILA word units (stream 'word' tokens).", gw))

    ic = build_inscription_context(recs)
    summary["representations"].append(write_rep(
        "SEG_INSCRIPTION_CONTEXT", "Whole inscription as one co-occurrence context unit.", ic))

    rows = build_rows(recs)
    summary["representations"].append(write_rep(
        "SEG_ROW", "Line/row units split at 'nl' stream tokens.", rows))

    entries, formula = build_entries_and_formula(recs)
    summary["representations"].append(write_rep(
        "SEG_ENTRY", "Administrative entry = word(s) group closed by a numeral.", entries))

    formula = annotate_formula_recurrence(formula)
    summary["representations"].append(write_rep(
        "SEG_FORMULA", "Formula-carrier segments = numeral-free (non-accounting) word runs.", formula,
        extra={"n_recurrent_units": sum(1 for u in formula if u["recurrence"]["is_recurrent"])}))

    pb_units, pb_extra = build_probabilistic_boundary(recs)
    summary["representations"].append(write_rep(
        "SEG_PROBABILISTIC_BOUNDARY",
        "Per-position boundary probability from an unsupervised branching-entropy model; "
        "units = induced segments (cut where prob > corpus mean).",
        pb_units, extra=pb_extra))

    ms_units, ms_levels = build_multi_scale(recs)
    summary["representations"].append(write_rep(
        "SEG_MULTI_SCALE", "Nested word / entry / inscription hierarchy.", ms_units,
        extra={"levels": ms_levels}))

    # attach grading + multiscale levels to summary
    summary["probabilistic_boundary_grading"] = pb_extra["grading_vs_gorila_words"]
    summary["multi_scale_levels"] = ms_levels

    json.dump(summary, open(os.path.join(CAMP, "data", "segmentations", "_SUMMARY.json"), "w"),
              ensure_ascii=False, indent=1)

    # console report
    print(f"source={PROV_SRC}  inscriptions={len(recs)}  sites={summary['n_sites']}  seed={SEED}")
    print(f"{'REPRESENTATION':<28}{'UNITS':>8}{'MEAN_LEN':>10}{'SIGNS':>9}")
    for r in summary["representations"]:
        print(f"{r['representation']:<28}{r['n_units']:>8}{r['mean_length_signs']:>10.4f}{r['n_signs_total']:>9}")
    print("\nMULTI_SCALE levels:", ms_levels)
    print("PROB_BOUNDARY grading vs GORILA words:", pb_extra["grading_vs_gorila_words"])
    print("FORMULA recurrent units:",
          sum(1 for u in formula if u["recurrence"]["is_recurrent"]), "/", len(formula))
    return summary


if __name__ == "__main__":
    main()
