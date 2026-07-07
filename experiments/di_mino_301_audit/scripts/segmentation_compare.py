#!/usr/bin/env python3
"""
T05 — Segmentation comparison on the target word A-TA-I-*301-WA-JA.

Compares 6 segmentation families:
  DI_MINO                 a|ta|i|(*301-wa-ja root)         boundaries {b1,b2,b3}
  DAVIS (i-*301 + affix)  A-TA | I-*301 | WA-JA            boundaries {b2,b4}
  THOMAS                  A-TA-I-*301-WA | JA              boundaries {b5}   (JA/E ending)
  DIPLOMATIC              A-TA-I-*301-WA-JA (one word)     boundaries {}
  NO_PHONETIC_STRUCTURAL  cut where flanking substrings independently recur (value-free)
  PROBABILISTIC           corpus-driven: branching-entropy + Viterbi unigram (MEASURED)

The two data-driven families (NO_PHONETIC_STRUCTURAL, PROBABILISTIC) are computed
from the silver LA corpus with NO phonetic values -> they provide the non-circular
check on whether Di Mino's *301-WA-JA "root" boundary is distributionally supported
or is a phonetically-motivated cut.

Signs are atomic tokens. Seed 20260708. Emits data/results/segmentation_target.json.
"""
import json, math, hashlib
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path("/home/claude-runner/gitlab/n8n/logos-di-mino-301-audit")
SILVER = ROOT / "corpus/silver/inscriptions_structured.json"
OUT_DIR = ROOT / "experiments/di_mino_301_audit/data/results"
OUT_DIR.mkdir(parents=True, exist_ok=True)
SEED = 20260708

TARGET = ["A", "TA", "I", "*301", "WA", "JA"]
# internal boundaries b1..b5 sit AFTER index 0..4
BOUNDARY_LABELS = {
    1: "A | TA...",   # after A
    2: "A-TA | I...",  # after TA
    3: "A-TA-I | *301...",  # after I
    4: "...*301 | WA...",   # after *301
    5: "...WA | JA",        # after WA
}

# ---- Fixed family parses (as boundary sets over positions 1..5) ----
FAMILIES_FIXED = {
    "DI_MINO": {
        "boundaries": {1, 2, 3},
        "morphs": [["A"], ["TA"], ["I"], ["*301", "WA", "JA"]],
        "commitment": "a-(1cs) | ta-(tG stem) | i-(stem vowel) | *301-WA-JA = root n-w-y",
        "isolates_301_wa_ja_as_unit": True,
        "301_grouped_with": "WA+JA (root)",
        "phonetically_motivated": True,
        "source_dependency": "CLB-01 Figure 1 (Di Mino, public claim)",
    },
    "DAVIS": {
        "boundaries": {2, 4},
        "morphs": [["A", "TA"], ["I", "*301"], ["WA", "JA"]],
        "commitment": "A-TA- prefix | I-*301 recurring stem | -WA-JA affix",
        "isolates_301_wa_ja_as_unit": False,
        "301_grouped_with": "I (I-*301 stem)",
        "phonetically_motivated": False,
        "source_dependency": "Davis 2014 structural family (i-*301 unit); exact paper NOT in-repo -> SOURCE_DEPENDENCY flagged",
    },
    "THOMAS": {
        "boundaries": {5},
        "morphs": [["A", "TA", "I", "*301", "WA"], ["JA"]],
        "commitment": "A-TA-I-*301-WA stem | -JA/-E inflectional ending (WA-JA~WA-E alternation)",
        "isolates_301_wa_ja_as_unit": False,
        "301_grouped_with": "stem body (A-TA-I-*301-WA)",
        "phonetically_motivated": False,
        "source_dependency": "THOMAS reduced-boundary family; exact source NOT in-repo -> SOURCE_DEPENDENCY flagged; ending cut grounded in corpus WA-JA/WA-E alternation",
    },
    "DIPLOMATIC": {
        "boundaries": set(),
        "morphs": [["A", "TA", "I", "*301", "WA", "JA"]],
        "commitment": "single graphic word, GORILA word-divider bounded; NO internal morpheme claim",
        "isolates_301_wa_ja_as_unit": False,
        "301_grouped_with": "whole word",
        "phonetically_motivated": False,
        "source_dependency": "GORILA transcription (no analysis)",
    },
}


def load_words():
    data = json.loads(SILVER.read_text())
    words = []
    for ins in data:
        for w in ins.get("words", []):
            words.append([str(s) for s in w])
    return words, data


def branching_entropy(words):
    """Forward/backward branching entropy at each internal boundary of TARGET.
    H_fwd(prefix) = entropy over the sign that FOLLOWS an occurrence of `prefix`
    (as a contiguous sub-sequence) anywhere in the corpus. High H after a prefix
    => the prefix is a 'complete' unit (many continuations) => boundary likely.
    """
    # index all contiguous subsequences -> Counter of following sign
    fwd = defaultdict(Counter)
    bwd = defaultdict(Counter)
    for w in words:
        n = len(w)
        for i in range(n):
            for j in range(i + 1, n + 1):
                sub = tuple(w[i:j])
                if j < n:
                    fwd[sub][w[j]] += 1
                if i > 0:
                    bwd[sub][w[i - 1]] += 1

    def ent(counter):
        tot = sum(counter.values())
        if tot == 0:
            return 0.0, 0
        h = -sum((c / tot) * math.log2(c / tot) for c in counter.values())
        return h, tot

    results = {}
    for b in range(1, 6):
        prefix = tuple(TARGET[:b])
        suffix = tuple(TARGET[b:])
        h_f, n_f = ent(fwd.get(prefix, Counter()))
        h_b, n_b = ent(bwd.get(suffix, Counter()))
        results[b] = {
            "label": BOUNDARY_LABELS[b],
            "prefix": "-".join(prefix),
            "suffix": "-".join(suffix),
            "fwd_branch_entropy_bits": round(h_f, 4),
            "fwd_support_occurrences": n_f,
            "bwd_branch_entropy_bits": round(h_b, 4),
            "bwd_support_occurrences": n_b,
            "boundary_score": round(h_f + h_b, 4),
        }
    return results


def viterbi_unigram(words):
    """Max-likelihood segmentation of TARGET using a unigram model whose lexicon
    is every attested LA word-TYPE (contiguous full words). Fallback: single sign
    with floor cost. Cost = -log( (count+1) / (N+V) ). MDL-flavoured, value-free.
    """
    type_counts = Counter(tuple(w) for w in words)
    # also allow attested contiguous sub-words that appear as standalone words
    N = sum(type_counts.values())
    V = len(type_counts)
    # sign vocabulary for floor
    signs = Counter()
    for w in words:
        for s in w:
            signs[s] += 1
    Nsign = sum(signs.values())

    def unit_cost(unit):
        c = type_counts.get(unit, 0)
        if c > 0:
            return -math.log((c + 1) / (N + V + 1))
        # floor: product of single-sign unigram costs + a segmentation penalty
        cost = 0.0
        for s in unit:
            cs = signs.get(s, 0)
            cost += -math.log((cs + 1) / (Nsign + len(signs) + 1))
        return cost + len(unit) * 2.0  # penalty for using unattested multi-sign unit

    n = len(TARGET)
    INF = float("inf")
    best = [INF] * (n + 1)
    back = [None] * (n + 1)
    best[0] = 0.0
    for j in range(1, n + 1):
        for i in range(0, j):
            unit = tuple(TARGET[i:j])
            c = best[i] + unit_cost(unit)
            if c < best[j]:
                best[j] = c
                back[j] = i
    # reconstruct
    segs = []
    j = n
    while j > 0:
        i = back[j]
        segs.append(TARGET[i:j])
        j = i
    segs.reverse()
    boundaries = set()
    pos = 0
    for seg in segs[:-1]:
        pos += len(seg)
        boundaries.add(pos)
    return {
        "segments": ["-".join(s) for s in segs],
        "boundaries": sorted(boundaries),
        "total_cost_nats": round(best[n], 4),
        "attested_units": {"-".join(s): type_counts.get(tuple(s), 0) for s in segs},
    }


def structural_recurrence(words):
    """NO_PHONETIC_STRUCTURAL: a boundary is credited where BOTH flanking
    substrings independently recur as contiguous sub-sequences elsewhere in the
    corpus (outside the target attestations). Value-free.
    """
    sub_count = Counter()
    for w in words:
        n = len(w)
        for i in range(n):
            for j in range(i + 1, n + 1):
                sub_count[tuple(w[i:j])] += 1
    target_tuple = tuple(TARGET)
    boundaries = {}
    for b in range(1, 6):
        left = tuple(TARGET[:b])
        right = tuple(TARGET[b:])
        # occurrences excluding when they are inside a full target attestation:
        # approximate by requiring the substring to appear more often than the
        # target itself (i.e. it recurs in OTHER words too)
        target_occ = sub_count.get(target_tuple, 0)
        lc = sub_count.get(left, 0)
        rc = sub_count.get(right, 0)
        left_recurs = lc > target_occ
        right_recurs = rc > target_occ
        boundaries[b] = {
            "label": BOUNDARY_LABELS[b],
            "left": "-".join(left), "left_total_occ": lc,
            "right": "-".join(right), "right_total_occ": rc,
            "target_occ": target_occ,
            "left_recurs_elsewhere": left_recurs,
            "right_recurs_elsewhere": right_recurs,
            "credited_boundary": left_recurs and right_recurs,
        }
    credited = {b for b, v in boundaries.items() if v["credited_boundary"]}
    return {"per_boundary": boundaries, "credited_boundaries": sorted(credited)}


def jaccard(a, b):
    a, b = set(a), set(b)
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b) if (a | b) else 1.0


def main():
    words, _ = load_words()
    be = branching_entropy(words)
    vit = viterbi_unigram(words)
    struct = structural_recurrence(words)

    # assemble probabilistic boundary decision: take branching-entropy peaks.
    # Credit a boundary if its score exceeds the mean internal-boundary score.
    scores = {b: be[b]["boundary_score"] for b in be}
    mean_s = sum(scores.values()) / len(scores)
    be_boundaries = sorted([b for b, s in scores.items() if s > mean_s])

    families = {k: dict(v) for k, v in FAMILIES_FIXED.items()}
    for k in families:
        families[k]["boundaries"] = sorted(families[k]["boundaries"])
    families["NO_PHONETIC_STRUCTURAL"] = {
        "boundaries": struct["credited_boundaries"],
        "commitment": "boundary where BOTH flanking substrings recur elsewhere (value-free)",
        "isolates_301_wa_ja_as_unit": (
            4 in struct["credited_boundaries"] and 6 not in struct["credited_boundaries"]
        ),
        "301_grouped_with": "data-determined",
        "phonetically_motivated": False,
        "source_dependency": "silver corpus distributional recurrence (this audit)",
        "detail": struct,
    }
    families["PROBABILISTIC"] = {
        "boundaries_branching_entropy": be_boundaries,
        "boundaries_viterbi": vit["boundaries"],
        "commitment": "corpus-driven MDL/branching-entropy (value-free)",
        "301_grouped_with": "data-determined",
        "phonetically_motivated": False,
        "source_dependency": "silver corpus (this audit)",
        "branching_entropy_detail": be,
        "viterbi_detail": vit,
    }

    # ---- Pairwise agreement on boundary sets ----
    def fam_bounds(k):
        f = families[k]
        if "boundaries" in f:
            return set(f["boundaries"])
        return set(f["boundaries_branching_entropy"])  # probabilistic -> BE
    keys = ["DI_MINO", "DAVIS", "THOMAS", "DIPLOMATIC", "NO_PHONETIC_STRUCTURAL", "PROBABILISTIC"]
    agreement = {}
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            agreement[f"{a}__vs__{b}"] = {
                "jaccard_boundaries": round(jaccard(fam_bounds(a), fam_bounds(b)), 3),
                "a_boundaries": sorted(fam_bounds(a)),
                "b_boundaries": sorted(fam_bounds(b)),
                "shared": sorted(fam_bounds(a) & fam_bounds(b)),
            }

    # ---- The load-bearing question: does any DATA-DRIVEN family reproduce
    #      Di Mino's *301-WA-JA root boundary structure (cut at b3, none at b4/b5)? ----
    dimino_root_signature = {"cuts_b3": 3 in fam_bounds("DI_MINO"),
                             "no_cut_b4": 4 not in fam_bounds("DI_MINO"),
                             "no_cut_b5": 5 not in fam_bounds("DI_MINO")}
    data_families = ["NO_PHONETIC_STRUCTURAL", "PROBABILISTIC"]
    reproduces = {}
    for k in data_families:
        fb = fam_bounds(k)
        reproduces[k] = {
            "isolates_*301-WA-JA_as_root_unit": (3 in fb and 4 not in fb and 5 not in fb),
            "boundaries": sorted(fb),
            "where_it_cuts_around_301": {
                "b3_before_301": 3 in fb,
                "b4_after_301": 4 in fb,
                "b5_after_WA": 5 in fb,
            },
        }

    out = {
        "prereg": "DI_MINO_EXACT_CLAIM_V1 (sha 8b098a4c)",
        "seed": SEED,
        "target_word": "-".join(TARGET),
        "internal_boundary_legend": {str(b): BOUNDARY_LABELS[b] for b in BOUNDARY_LABELS},
        "families": families,
        "pairwise_agreement": agreement,
        "dimino_root_signature": dimino_root_signature,
        "data_driven_reproduces_dimino_root": reproduces,
        "interpretation_flags": {
            "circularity_probe": (
                "If NO data-driven family isolates *301-WA-JA as a unit, Di Mino's "
                "root boundary is phonetically motivated (chosen to make na-wa-ja=n-w-y), "
                "not distributionally supported -> supports the e2->e3->e4 circularity finding."
            ),
        },
    }
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    (OUT_DIR / "segmentation_target.json").write_text(payload)
    print("WROTE", OUT_DIR / "segmentation_target.json")
    print("sha256", hashlib.sha256(payload.encode()).hexdigest())
    print("\n== branching entropy per boundary ==")
    for b in be:
        print(f"  b{b} {be[b]['label']:22s} score={be[b]['boundary_score']:.3f} "
              f"(fwd {be[b]['fwd_branch_entropy_bits']:.2f}/{be[b]['fwd_support_occurrences']}, "
              f"bwd {be[b]['bwd_branch_entropy_bits']:.2f}/{be[b]['bwd_support_occurrences']})")
    print("BE-credited boundaries:", be_boundaries, "(mean score %.3f)" % mean_s)
    print("Viterbi segments:", vit["segments"], "boundaries", vit["boundaries"])
    print("Structural credited boundaries:", struct["credited_boundaries"])
    print("DI_MINO boundaries:", sorted(fam_bounds("DI_MINO")))
    print("\nData-driven reproduces Di Mino *301-WA-JA root unit?")
    for k, v in reproduces.items():
        print(f"  {k}: {v['isolates_*301-WA-JA_as_root_unit']}  (boundaries {v['boundaries']})")


if __name__ == "__main__":
    main()
