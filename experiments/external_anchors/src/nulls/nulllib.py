"""nulllib.py — end-to-end null generators + search-receipt emitter (Task C scaffold).

Structure-preserving null families that pass through the SAME pipeline as the real run. No adaptive
choice may run without emit_receipt(). Working generators: synthetic_sign_system,
shuffled_anchor_ids, shuffled_candidate_assignments, target_label_permutation, synthetic_toponyms.
Stubs (need real anchor+calibration inputs): unrelated_real_toponyms, transcription_variant_draw,
wrong_projected_map, corrupted_positive_control, false_candidate_language.
"""
import json, os, random, collections

FAMILIES = ["real", "synthetic_toponyms", "unrelated_real_toponyms", "shuffled_anchor_ids",
            "shuffled_candidate_assignments", "synthetic_sign_system", "transcription_variant_draw",
            "wrong_projected_map", "corrupted_positive_control", "false_candidate_language",
            "target_label_permutation"]

def emit_receipt(results_dir, experiment_id, **fields):
    d = os.path.join(results_dir, experiment_id); os.makedirs(d, exist_ok=True)
    rec = {"experiment_id": experiment_id, **fields}
    with open(os.path.join(d, "receipts.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec

# --- structure-preserving generators (operate on abstract token lists) ---
def synthetic_sign_system(candidates, rng):
    """Preserve per-position sign-frequency; regenerate strings. candidates: list[list[sign]]."""
    freq = collections.Counter(s for c in candidates for s in c)
    signs, weights = zip(*freq.items()) if freq else ((0,), (1,))
    return [[rng.choices(signs, weights=weights)[0] for _ in c] for c in candidates]

def shuffled_anchor_ids(anchors, rng):
    """Real anchor forms, permuted labels."""
    labels = [a["label"] for a in anchors]; rng.shuffle(labels)
    return [dict(a, label=l) for a, l in zip(anchors, labels)]

def shuffled_candidate_assignments(candidates_with_class, rng):
    classes = [c["candidate_class"] for c in candidates_with_class]; rng.shuffle(classes)
    return [dict(c, candidate_class=k) for c, k in zip(candidates_with_class, classes)]

def target_label_permutation(heldout_truth, rng):
    v = list(heldout_truth); rng.shuffle(v); return v

def synthetic_toponyms(real_anchors, alphabet, rng):
    """Random skeletons over `alphabet`, preserving the EXACT length multiset of the real anchors."""
    lens = [len(a["skeleton"]) for a in real_anchors]; rng.shuffle(lens)
    return [{"label": f"SYN{i}", "skeleton": [rng.choice(alphabet) for _ in range(L)]}
            for i, L in enumerate(lens)]

STUBS = {"unrelated_real_toponyms", "transcription_variant_draw", "wrong_projected_map",
         "corrupted_positive_control", "false_candidate_language"}

def preserves_length_dist(orig, gen):
    from collections import Counter
    return Counter(len(x) for x in orig) == Counter(len(x) for x in gen)
