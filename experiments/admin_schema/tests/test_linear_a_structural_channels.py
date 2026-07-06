"""Stage 4.1 Correction 3: Linear A NUMERAL / ROW / ENTRY channels recovered from the silver stream."""
import json, os, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "src", "corpus")))
import graph_common as gc


def test_la_recovered_channels():
    nt = Counter()
    for line in open(os.path.join(gc.MODEL_VISIBLE, "la_graph.jsonl")):
        for n in json.loads(line)["nodes"]:
            nt[n["type"]] += 1
    assert nt["NUMERAL"] > 500, f"LA numerals not recovered ({nt['NUMERAL']})"
    assert nt["ROW"] > 1000 and nt["ENTRY"] > 1000
    assert nt["WORD_FORM"] > 2000 and nt["SIGN"] > 3000


def test_la_numeral_has_value():
    for line in open(os.path.join(gc.MODEL_VISIBLE, "la_graph.jsonl")):
        for n in json.loads(line)["nodes"]:
            if n["type"] == "NUMERAL":
                assert isinstance(n.get("value"), (int, float)), n
                return


if __name__ == "__main__":
    test_la_recovered_channels(); test_la_numeral_has_value(); print("PASS la-structural-channels")
