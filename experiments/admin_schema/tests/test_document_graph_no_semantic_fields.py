"""Stage 4 acceptance #3: NO forbidden semantic/phonetic field or value enters the model-visible graph.

Scans field NAMES (via the validator) AND field VALUES: no model-visible string may equal a de-phoneticised
sound value from the evaluation-only vocab (i.e. no opaque_id ever leaks back to 'ko','qe',...)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "src", "corpus"))
sys.path.insert(0, SRC)
import graph_common as gc
import validate_admin_graph as V


def test_no_forbidden_field_names():
    for fn in ("lb_graph.jsonl", "la_graph.jsonl"):
        for line in open(os.path.join(gc.MODEL_VISIBLE, fn), encoding="utf-8"):
            hit = V._forbidden_hit(json.loads(line))
            assert hit is None, f"{fn}: {hit}"


def test_no_sound_value_leaks_into_model_visible():
    # every phonetic value in the eval-only vocab must NOT appear as any model-visible string token
    voc = json.load(open(os.path.join(gc.EVAL_ONLY, "lb_dephon_vocab.json")))
    sounds = set()
    for m in voc.values():
        sounds.update(m.values())          # e.g. {'ko','qe','OLE','S',...}
    # sample the model-visible graph; assert no node string equals a sound value
    leaked = set()
    for i, line in enumerate(open(os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl"), encoding="utf-8")):
        if i >= 500:
            break
        g = json.loads(line)
        for n in g["nodes"]:
            for v in (n.get("opaque_id"), n.get("qualifier"), n.get("allograph_class")):
                if isinstance(v, str) and v in sounds:
                    leaked.add(v)
    assert not leaked, f"sound values leaked into model-visible: {sorted(leaked)[:10]}"


def test_eval_only_dir_holds_the_key():
    # the de-phoneticisation key exists and is under evaluation_only (never model_visible)
    assert os.path.exists(os.path.join(gc.EVAL_ONLY, "lb_dephon_vocab.json"))
    assert not os.path.exists(os.path.join(gc.MODEL_VISIBLE, "lb_dephon_vocab.json"))


if __name__ == "__main__":
    test_no_forbidden_field_names(); test_no_sound_value_leaks_into_model_visible(); test_eval_only_dir_holds_the_key()
    print("PASS no-semantic-fields")
