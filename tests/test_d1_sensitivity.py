"""Locked properties of the D1 sensitivity checks (scripts/d1_sensitivity.py):

(a) phantom semantics (pure): a type is phantom iff EVERY occurrence carries a nonempty
    damage code; token counting follows the same rule;
(b) damage-attribution mirror (pure, synthetic tablets): stripping the damage flags
    reproduces metrology.parse_tablet EXACTLY; a unit is flagged iff its KU-RO total
    line or any contributing item line carries a damage-flagged word token; commodity
    columns keep their damage attribution separate; code/label misalignment fails loud;
(c) markdown rendering: every number comes from the result dict and the discipline
    sentence is present verbatim (no hand-typed counts; invariant #12);
(d) NO-VERDICT-FLIP LOCKS (real data): the damage-filtered metrology re-run stays NULL
    (not separated, p >= 0.05), the phantom-filtered segmentation gap stays positive,
    and verdict_flips is empty — an improvement is NOT a claim (discipline rule);
(e) as-published reproduction: the recomputed as-published legs match the runtime
    baselines (metrology 32 docs / 35 units, held-out 0.0, p = 1.0; segmentation
    dp_unigram 0.4361 vs random 0.3888);
(f) pinned denominators regression (1,165 -> 806 types / 3,147 -> 2,752 tokens /
    359 phantom types / 395 phantom tokens) + per-block determinism.

Data-dependent tests are licensed_data-marked AND runtime-skipped when the gitignored
annex / silver / runtime baselines are absent (house pattern).
"""
import json
import os
import sys

import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts import d1_sensitivity as d1            # noqa: E402
from scripts.comparison import metrology            # noqa: E402

_have_data = os.path.exists(d1.ANNEX) and os.path.exists(d1.SILVER_STRUCT)
_have_metrology_baseline = os.path.exists(d1.PUB_METROLOGY)
_have_morphology_baseline = os.path.exists(d1.PUB_MORPHOLOGY)
_have_results = os.path.exists(d1.OUT)

needs_data = pytest.mark.skipif(not _have_data, reason="gitignored annex/silver not present")


# --------------------------------------------------------------------------- #
# (a) phantom semantics — pure
# --------------------------------------------------------------------------- #
class TestPhantomSemantics:
    DOCS = {
        "D1": {"w": ["L", "", "T"], "types": ["A", "B", "C"]},
        "D2": {"w": ["T", ""], "types": ["A", "C"]},
    }

    def test_phantom_iff_every_occurrence_damaged(self):
        # A: damaged in D1 and D2 -> phantom; B: clean -> no; C: damaged once, clean once -> no
        assert d1.phantom_type_set(self.DOCS) == {"A"}

    def test_phantom_token_count(self):
        assert d1.phantom_token_count(self.DOCS, {"A"}) == 2


# --------------------------------------------------------------------------- #
# (b) damage-attribution mirror — pure synthetic tablets
# --------------------------------------------------------------------------- #
def _tab(*lines):
    toks = []
    for ln in lines:
        toks.extend(ln)
        toks.append({"k": "nl"})
    return {"doc": "SYN1", "context": "LMIB", "tokens": toks}


def _lab(s):
    return {"k": "label", "s": s}


def _num(v):
    return {"k": "num", "v": v}


class TestDamageMirror:
    def _simple(self):
        return _tab(
            [_lab("W1"), _num(5)],
            [_lab("W2"), _num(3)],
            [_lab("KU-RO"), _num(8)],
        )

    def test_strip_equals_parse_tablet_and_item_damage_flags_unit(self):
        tab = self._simple()
        units, dmg = d1.mirror_parse_tablet_damage(tab, set(), ["T", "", ""])
        assert units == metrology.parse_tablet(tab, set())
        assert dmg == [True]

    def test_total_line_damage_flags_unit(self):
        _, dmg = d1.mirror_parse_tablet_damage(self._simple(), set(), ["", "", "L"])
        assert dmg == [True]

    def test_clean_tablet_not_flagged(self):
        tab = self._simple()
        units, dmg = d1.mirror_parse_tablet_damage(tab, set(), ["", "", ""])
        assert units == metrology.parse_tablet(tab, set())
        assert dmg == [False]

    def test_commodity_columns_keep_damage_separate(self):
        commodities = {"GRA", "VIN"}
        tab = _tab(
            [_lab("W1"), _lab("GRA"), _num(2)],
            [_lab("W2"), _lab("VIN"), _num(3)],
            [_lab("KU-RO"), _lab("GRA"), _num(2)],
            [_lab("KU-RO"), _lab("VIN"), _num(3)],
        )
        # labels in stream order: W1 GRA W2 VIN KU-RO GRA KU-RO VIN; only W2 damaged
        codes = ["", "", "L", "", "", "", "", ""]
        units, dmg = d1.mirror_parse_tablet_damage(tab, commodities, codes)
        assert units == metrology.parse_tablet(tab, commodities)
        assert [u["commodity"] for u in units] == ["GRA", "VIN"]
        assert dmg == [False, True]

    def test_code_misalignment_fails_loud(self):
        with pytest.raises(RuntimeError):
            d1.mirror_parse_tablet_damage(self._simple(), set(), ["", ""])


# --------------------------------------------------------------------------- #
# (c) markdown rendering — pure (fake result dict; every number flows through)
# --------------------------------------------------------------------------- #
def _fake_result():
    return {
        "version": d1.VERSION, "stage": d1.STAGE, "seed": 0,
        "annex_version": "damage-annex-v1", "annex_bronze_sha256": "ab" * 32,
        "discipline": d1.DISCIPLINE,
        "verdict_flips": [],
        "blocks": {
            "denominators": {
                "name": "denominators", "phantom_types": 2, "phantom_type_tokens": 3,
                "published_value": {"distinct_types": 10, "word_tokens": 20, "docs": 5,
                                    "sites": 3, "effective_n_doc_site": 3},
                "sensitivity_value": {"distinct_types": 8, "word_tokens": 17, "docs": 5,
                                      "sites": 3, "effective_n_doc_site": 3},
                "delta": {"distinct_types": -2, "word_tokens": -3, "docs": 0, "sites": 0,
                          "effective_n_doc_site": 0},
                "verdict_flip": False, "interpretation": "denominator interp line",
            },
            "metrology": {
                "name": "metrology", "mapping": "MAPDOC", "mapping_caveat": "CAVEAT",
                "n_tablets": 4, "n_units_excluded": 1,
                "n_units_excluded_fraction_bearing": 0,
                "published_value": {"n_units": 4, "n_documents": 4,
                                    "heldout_fraction_balance_rate": 0.0,
                                    "null_mean": 0.1, "p_value": 1.0, "separated": False},
                "published_source": "test", "reproduction": {"matches_published": True},
                "sensitivity_value": {"n_units": 3, "heldout_fraction_balance_rate": 0.0,
                                      "null_mean": 0.2, "p_value": 1.0, "separated": False},
                "delta": {"n_units": -1, "heldout_fraction_balance_rate": 0.0,
                          "null_mean": 0.1, "p_value": 0.0},
                "verdict_flip": False, "interpretation": "metrology interp line",
            },
            "segmentation": {
                "name": "segmentation", "phantom_types": 2, "annex_phantom_tokens": 3,
                "dropped_tokens_agree_with_annex": True,
                "published_value": {"dp_unigram_micro_f1": 0.44, "random_micro_f1": 0.39,
                                    "gap": 0.05},
                "published_source": "test", "reproduction": {"matches_published": True},
                "sensitivity_value": {"dp_unigram_micro_f1": 0.47, "random_micro_f1": 0.4,
                                      "gap": 0.07, "n_words_dropped": 3,
                                      "n_inscriptions_dropped": 1, "n_inscriptions": 4},
                "delta": {"dp_unigram_micro_f1": 0.03, "random_micro_f1": 0.01,
                          "gap": 0.02},
                "verdict_flip": False, "interpretation": "segmentation interp line",
            },
        },
    }


class TestRenderMd:
    def test_contains_all_blocks_numbers_and_discipline(self):
        md = d1.render_md(_fake_result())
        for needle in (
            "## Phase 1b", "### (1) Denominators", "### (2) Metrology",
            "### (3) Segmentation", d1.DISCIPLINE, "Verdict flips: NONE",
            "| distinct word types | 10 | 8 | -2 |",
            "| null mean | 0.1 | 0.2 | 0.1 |",
            "| gap (dp − random) | 0.05 | 0.07 | 0.02 |",
            "MAPDOC", "CAVEAT",
            "denominator interp line", "metrology interp line", "segmentation interp line",
        ):
            assert needle in md, needle

    def test_flip_is_surfaced(self):
        r = _fake_result()
        r["verdict_flips"] = ["metrology"]
        assert "Verdict flips: metrology" in d1.render_md(r)


# --------------------------------------------------------------------------- #
# (f) denominators — real data, pinned + deterministic
# --------------------------------------------------------------------------- #
@pytest.mark.licensed_data
@needs_data
class TestDenominatorsReal:
    @pytest.fixture(scope="class")
    def annex(self):
        return d1.load_annex()

    @pytest.fixture(scope="class")
    def block(self, annex):
        return d1.denominators_block(annex)

    def test_pinned_regression(self, block):
        p, s = block["published_value"], block["sensitivity_value"]
        assert (p["distinct_types"], s["distinct_types"]) == (1165, 806)
        assert (p["word_tokens"], s["word_tokens"]) == (3147, 2752)
        assert block["phantom_types"] == 359
        assert block["phantom_type_tokens"] == 395
        assert p["docs"] == 1341 and p["sites"] == 52
        assert block["delta"]["distinct_types"] == -359

    def test_effective_n_is_site_bottlenecked(self, block):
        # joint components over doc+site collapse to the site level (docs nest in sites)
        assert block["published_value"]["effective_n_doc_site"] == \
            block["published_value"]["sites"]
        assert block["sensitivity_value"]["effective_n_doc_site"] == \
            block["sensitivity_value"]["sites"]

    def test_no_verdict_attached(self, block):
        assert block["verdict_flip"] is False

    def test_determinism(self, annex, block):
        again = d1.denominators_block(annex)
        assert json.dumps(block, sort_keys=True) == json.dumps(again, sort_keys=True)

    def test_cross_check_against_published_morphology(self, block):
        if not _have_morphology_baseline:
            pytest.skip("runtime/morphology-real.json not present")
        assert block["cross_check_published_morphology"]["matches_published"] is True


# --------------------------------------------------------------------------- #
# (d)+(e) metrology — real data: mapping holds, baseline reproduced, NULL stays NULL
# --------------------------------------------------------------------------- #
@pytest.mark.licensed_data
@needs_data
class TestMetrologyReal:
    @pytest.fixture(scope="class")
    def annex(self):
        return d1.load_annex()

    @pytest.fixture(scope="class")
    def block(self, annex):
        # constructing the block runs the per-tablet mapping assertions (fail loud)
        return d1.metrology_block(annex)

    def test_as_published_reproduces_baseline(self, block):
        if not _have_metrology_baseline:
            pytest.skip("runtime/metrology-real.json not present")
        assert block["published_source"] == "runtime/metrology-real.json"
        assert block["reproduction"]["matches_published"] is True
        assert block["published_value"]["n_units"] == 35
        assert block["published_value"]["n_documents"] == 32
        assert block["published_value"]["p_value"] == 1.0

    def test_null_stays_null_no_flip(self, block):
        s = block["sensitivity_value"]
        assert s["separated"] is False
        assert s["p_value"] >= 0.05
        assert block["verdict_flip"] is False

    def test_filtering_only_removes_units(self, block):
        assert block["sensitivity_value"]["n_units"] + block["n_units_excluded"] == \
            block["reproduction"]["n_units"]
        assert block["n_units_excluded"] > 0     # damage exists on these tablets

    def test_determinism(self, annex, block):
        again = d1.metrology_block(annex)
        assert json.dumps(block, sort_keys=True) == json.dumps(again, sort_keys=True)


# --------------------------------------------------------------------------- #
# (d)+(e) segmentation — real data: baseline reproduced, gap survives, no flip
# --------------------------------------------------------------------------- #
@pytest.mark.licensed_data
@needs_data
class TestSegmentationReal:
    @pytest.fixture(scope="class")
    def block(self):
        return d1.segmentation_block(d1.load_annex())

    def test_as_published_reproduces_baseline(self, block):
        if not _have_morphology_baseline:
            pytest.skip("runtime/morphology-real.json not present")
        assert block["published_source"] == "runtime/morphology-real.json"
        assert block["reproduction"]["matches_published"] is True
        assert block["published_value"]["dp_unigram_micro_f1"] == 0.4361
        assert block["published_value"]["random_micro_f1"] == 0.3888

    def test_dropped_tokens_agree_with_annex(self, block):
        assert block["dropped_tokens_agree_with_annex"] is True
        assert block["sensitivity_value"]["n_words_dropped"] == 395

    def test_gap_survives_no_flip(self, block):
        assert block["sensitivity_value"]["gap"] > 0
        assert block["verdict_flip"] is False

    def test_improvement_is_marked_not_a_claim(self, block):
        if block["delta"]["gap"] > 0:
            assert "NOT a claim" in block["interpretation"]


# --------------------------------------------------------------------------- #
# committed results file — internally consistent, no flips recorded
# --------------------------------------------------------------------------- #
@pytest.mark.skipif(not _have_results, reason="results/d1_sensitivity.json not present")
class TestResultsFile:
    @pytest.fixture(scope="class")
    def result(self):
        return json.load(open(d1.OUT, encoding="utf-8"))

    def test_no_verdict_flips_recorded(self, result):
        assert result["verdict_flips"] == []
        for b in result["blocks"].values():
            assert b["verdict_flip"] is False

    def test_all_blocks_present_with_required_keys(self, result):
        assert set(result["blocks"]) == set(d1.ALL_BLOCKS)
        for b in result["blocks"].values():
            for key in ("published_value", "sensitivity_value", "delta", "interpretation"):
                assert key in b, key

    def test_discipline_rule_verbatim(self, result):
        assert result["discipline"] == d1.DISCIPLINE
