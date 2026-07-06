import os, sys, random
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT,"src/nulls")); import nulllib

def test_synthetic_sign_system_preserves_length():
    rng=random.Random(1); cands=[[1,2,3],[4,5],[1,1,1,1]]
    g=nulllib.synthetic_sign_system(cands,rng); assert nulllib.preserves_length_dist(cands,g)

def test_shuffled_anchor_ids_keeps_forms():
    rng=random.Random(1); anc=[{"label":"A","skeleton":[1,2]},{"label":"B","skeleton":[3]}]
    g=nulllib.shuffled_anchor_ids(anc,rng)
    assert sorted(tuple(a["skeleton"]) for a in g)==sorted(tuple(a["skeleton"]) for a in anc)

def test_synthetic_toponyms_length_matched():
    rng=random.Random(1); anc=[{"label":"A","skeleton":[1,2,3]},{"label":"B","skeleton":[4,5]}]
    g=nulllib.synthetic_toponyms(anc, list(range(10)), rng)
    assert nulllib.preserves_length_dist([a["skeleton"] for a in anc],[x["skeleton"] for x in g])

def test_receipt_required(tmp_path):
    r=nulllib.emit_receipt(str(tmp_path),"exp1",null_family="real",seed=1,selected_result={"matched":0})
    assert os.path.exists(os.path.join(str(tmp_path),"exp1","receipts.jsonl"))

def test_all_families_declared():
    assert set(nulllib.STUBS) <= set(nulllib.FAMILIES) and len(nulllib.FAMILIES)==11
