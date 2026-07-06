import os, sys, random
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT,"src/positive_control")); import degrade
def test_degrade_deterministic_same_seed():
    a=degrade.degrade(list("konoso"), random.Random(3))
    b=degrade.degrade(list("konoso"), random.Random(3))
    assert a==b
def test_degrade_params_fixed_not_empty():
    assert set(degrade.DEFAULT)>={"vowel_drop","omission","subst"} and all(0<=v<=1 for v in degrade.DEFAULT.values())
def test_degrade_can_shorten():
    # with vowel drop + omission, output is typically <= input length
    rng=random.Random(1); tot=sum(len(degrade.degrade(list("aminiso"),rng))<=7 for _ in range(20))
    assert tot>=15
