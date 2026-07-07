"""Stage 4 tests: LFs deterministic, expose abstention, structural separate from index; no eval-gold in vote."""
import os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE,"..","src","weak_supervision")))
import labeling_functions as LF
def test_lfs_deterministic_and_abstain():
    feats=LF.features(); fo=next(iter(feats))
    for n,fn in LF.LFS.items():
        assert fn(fo,feats[fo])==fn(fo,feats[fo])           # deterministic
    # abstention exists across the corpus
    assert any(all(LF.LFS[n](fo,feats[fo]) is None for n in LF.LFS) for fo in list(feats)[:200])
def test_structural_and_index_lfs_separated():
    classes=set(LF.LF_CLASS.values())
    assert "EDITION_INDEPENDENT" in classes and "SHARED_DECIPHERMENT" in classes
    idx=[n for n,c in LF.LF_CLASS.items() if c=="SHARED_DECIPHERMENT"]
    struct=[n for n,c in LF.LF_CLASS.items() if c=="EDITION_INDEPENDENT"]
    assert set(idx).isdisjoint(struct)
def test_person_name_lf_abstains_no_index():
    feats=LF.features()
    assert all(LF.LF_PERSON_NAME_INDEX(fo,feats[fo]) is None for fo in list(feats)[:100])
if __name__=="__main__":
    test_lfs_deterministic_and_abstain();test_structural_and_index_lfs_separated();test_person_name_lf_abstains_no_index()
    print("PASS label-functions")
