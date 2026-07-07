"""Stage 3 tests: category integrity + no circular structural labels in the load-bearing pool."""
import json, os, sys
HERE=os.path.dirname(os.path.abspath(__file__)); EXP=os.path.normpath(os.path.join(HERE,".."))
LAB=os.path.join(EXP,"data","source_labels","linear_b_source_labels.jsonl")
def _labels(): return [json.loads(l) for l in open(LAB)]
def test_reference_gold_a_is_nontrivial_nonstructural():
    for l in _labels():
        if l["label_category"]=="REFERENCE_GOLD_A":
            assert l["nontrivial"] is True and l["evidence_basis"]!="STRUCTURAL_ONLY", l["form_id"]
def test_structural_control_not_in_loadbearing():
    for l in _labels():
        if l["evidence_basis"]=="STRUCTURAL_ONLY":
            assert l["label_category"]!="REFERENCE_GOLD_A"
def test_metadata_complete():
    req=["label_id","document_id","form_id","coarse_role","label_category","evidence_basis","source_id",
         "source_citation","source_dependency_cluster","derivation_rule","confidence","dispute_status","builder_version"]
    for l in _labels():
        assert all(k in l for k in req)
def test_single_dependency_cluster_for_content():
    cl={l["source_dependency_cluster"] for l in _labels()}
    assert cl=={"SHARED_DECIPHERMENT"}, cl   # content labels are one lineage, not independent votes
if __name__=="__main__":
    test_reference_gold_a_is_nontrivial_nonstructural();test_structural_control_not_in_loadbearing()
    test_metadata_complete();test_single_dependency_cluster_for_content();print("PASS source-labels")
