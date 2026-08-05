"""Locked properties of the reopening-thresholds calculator (scripts/reopening_thresholds.py):

(a) threshold extraction is monotone-honest: PAV isotonic smoothing; an increasing detection
    curve yields the interpolated crossing; a curve that never reaches the target yields None
    (never a fabricated number);
(b) the H2 closed form matches a brute-force numeric solve on hand-built Heaps params, and an
    LA-like hand parameterization lands >= ~2 orders of magnitude short (the published
    info-floor shape);
(c) anchor counting is mechanical: fixture rows count 8-slot anchors; the REAL committed
    census reproduces ZERO independent 8-slot anchors (guard vs the anchor-lattice pricing);
(d) D1 phantom sensitivity fails soft: annex absent -> approx=true pinned values, never a
    crash, never silently exact;
(e) unit conversion follows the stamped ratios; route 7 is non-convertible (reopen_at None);
(f) segmentation honesty: fitted asymptote at/below the 0.62 target -> ASYMPTOTE_LIMITED with
    threshold None; an asymptote pinned at its bound -> FIT_UNCONSTRAINED (no extrapolation);
(g) the vectorized within-form permutation preserves each word's sign multiset and length
    (nulls.within_form_permutation semantics, Nair 2026);
(h) determinism: identical seeds -> byte-identical JSON (analytic routes);
(i) markdown purity: docs/reopening-thresholds.md is a pure function of
    results/reopening_thresholds.json (re-render == committed bytes; GENERATED header);
(j) contradiction guards: LB-full clears the morphology bigram floor (locks the published
    0.562-fires); the LA corpus at its own size does NOT fire (the published NO-POWER); and
    the artifact does not promise a token-count reopening for morphology — the measured LB
    threshold sits at/below LA-now (SIZE_NOT_BINDING: size was never the binding constraint,
    the honest resolution of the plan's 'threshold > 3,147' expectation, which the measured
    analogue refutes);
(k) the shipped artifact records fast=false and carries all 7 routes.

LB/LA-dependent tests are licensed_data-marked AND runtime-skipped when the gitignored
corpora are absent (house pattern).
"""
import json
import os
import sys

import numpy as np
import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts import reopening_thresholds as RT                      # noqa: E402
from scripts.comparison import morphology as M                      # noqa: E402
from scripts.comparison import linb_morphology_control as LBC       # noqa: E402
from scripts.comparison.nulls import within_form_permutation        # noqa: E402

_have_la = os.path.exists(M.DEFAULT_SILVER)
_have_lb = os.path.exists(LBC.DAMOS)
needs_la = pytest.mark.skipif(not _have_la, reason="gitignored LA silver not present")
needs_lb = pytest.mark.skipif(not _have_lb, reason="gitignored DĀMOS not present")
needs_both = pytest.mark.skipif(not (_have_la and _have_lb),
                                reason="gitignored LA silver / DĀMOS not present")
_have_artifact = os.path.exists(RT.RESULTS_PATH)
needs_artifact = pytest.mark.skipif(not _have_artifact,
                                    reason="results/reopening_thresholds.json not present")


# ------------------------------------------------------------------ (a) ----- #
class TestThresholdExtraction:
    def test_increasing_curve_interpolates(self):
        thr, fit, note = RT.threshold_from_curve([100, 200, 300], [0.0, 0.5, 1.0], 0.8)
        assert note == "interpolated"
        assert 200 < thr < 300
        assert fit == [0.0, 0.5, 1.0]

    def test_decreasing_curve_refuses(self):
        thr, fit, note = RT.threshold_from_curve([100, 200, 300], [0.9, 0.5, 0.1], 0.8)
        assert thr is None and note == "never_reaches_target"
        # PAV pools a decreasing curve to its mean
        assert all(abs(f - 0.5) < 1e-9 for f in fit)

    def test_never_reaching_refuses(self):
        thr, _, note = RT.threshold_from_curve([1, 2, 3], [0.1, 0.2, 0.3], 0.8)
        assert thr is None and note == "never_reaches_target"

    def test_at_or_below_grid_min(self):
        thr, _, note = RT.threshold_from_curve([100, 200], [0.9, 1.0], 0.8)
        assert thr == 100.0 and note == "at_or_below_grid_min"

    def test_pav_is_nondecreasing_and_noise_tolerant(self):
        fit = RT.pav_isotonic([0.0, 0.4, 0.3, 0.9, 1.0])
        assert all(b >= a - 1e-12 for a, b in zip(fit, fit[1:]))


# ------------------------------------------------------------------ (b) ----- #
class TestH2ClosedForm:
    def test_matches_numeric_solve(self):
        K, beta, c_min, r = 8.0, 0.35, 3.0, 0.75
        nstar = RT.h2_closed_form(K, beta, c_min, r)
        # brute-force: smallest N with r*N / (K*N^beta)^2 >= c_min
        f = lambda n: r * n / (K * n ** beta) ** 2
        assert abs(f(nstar) - c_min) / c_min < 1e-9

    def test_vocab_growth_dominates_refuses(self):
        assert RT.h2_closed_form(K=2.0, beta=0.5, c_min=5.0, r=1.0) is None
        assert RT.h2_closed_form(K=2.0, beta=0.8, c_min=5.0, r=1.0) is None

    def test_la_like_params_orders_short(self):
        # hand-built LA-like parameterization: V ~ 260 signs at ~5.8k sign tokens under
        # K=9.8, beta=0.375; empirical c_min ~3.4; r ~0.77 -> N* orders of magnitude beyond
        # the corpus (the published info-floor shape: >= ~2 orders short).
        n_now = 5792.0
        nstar = RT.h2_closed_form(K=9.8, beta=0.375, c_min=3.4, r=0.77)
        assert nstar is not None
        assert np.log10(nstar / n_now) >= 2.0


# ------------------------------------------------------------------ (c) ----- #
FIXTURE_ROWS = [
    {"anchor_id": "a1", "class": "toponym", "covered_signs": "PA,I,TO",
     "sm_trust": "tempting", "fringe_flag": "false"},
    {"anchor_id": "a2", "class": "toponym", "covered_signs": "A,B,C,D,E,F,G,H",
     "sm_trust": "neutral", "fringe_flag": "false"},
    {"anchor_id": "a3", "class": "personal_name", "covered_signs": "A,B,C,D,E,F,G,H,I",
     "sm_trust": "debunked", "fringe_flag": "false"},
    {"anchor_id": "a4", "class": "personal_name", "covered_signs": "A,B,C,D,E,F,G,H",
     "sm_trust": "neutral", "fringe_flag": "true"},
]


class TestAnchorCounting:
    def test_fixture_counting(self):
        c = RT.anchor_counts(FIXTURE_ROWS)
        assert c["census_rows"] == 4
        assert c["max_covered_slots"] == 9
        # a2 qualifies; a3 is debunked; a4 is fringe; a1 too short
        assert c["eight_slot_anchors"] == 1
        assert c["eight_slot_anchor_ids"] == ["a2"]

    def test_real_census_reproduces_zero(self):
        rows = RT.parse_census()
        c = RT.anchor_counts(rows)
        assert c["census_rows"] == 47
        assert c["max_covered_slots"] < RT.FOOTHOLD_SLOTS
        assert c["eight_slot_anchors"] == 0, (
            "census now contains an 8-slot anchor: the anchors route must be re-run and the "
            "anchor-lattice pricing re-checked before this pin moves")

    def test_identification_lineage_single_vote(self):
        from scripts import source_dependency
        conc = source_dependency.concordance(
            ["SRC-DECIPHERMENT-1952", "SRC-DAMOS", "SRC-VC-DOCS2"])
        assert conc["verdict"] == "SINGLE_LINEAGE"
        assert conc["effective_n"] == 1


# ------------------------------------------------------------------ (d) ----- #
class TestPhantomFailSoft:
    def test_absent_annex_is_approx_pinned(self):
        ph = RT.load_phantom("/nonexistent/damage_annex.json")
        assert ph["approx"] is True
        assert ph["phantom_type_set"] is None
        assert ph["phantom_types"] == RT.D1_PINNED["phantom_types"]
        assert ph["word_tokens_excl_phantoms"] == RT.D1_PINNED["word_tokens_excl_phantoms"]

    def test_distance_row_carries_approx_flag(self):
        units = RT.compute_units(None, RT.load_phantom("/nonexistent/damage_annex.json"))
        row = RT._phantom_distance_row(5000.0, units)
        assert row["approx"] is True
        assert row["la_word_tokens_now_excl_phantoms"] == \
            RT.D1_PINNED["word_tokens_excl_phantoms"]
        assert row["additional_word_tokens_excl_phantoms"] > 0

    @pytest.mark.licensed_data
    @needs_la
    def test_present_annex_is_exact(self):
        if not os.path.exists(RT.ANNEX_PATH):
            pytest.skip("damage annex not built")
        ph = RT.load_phantom()
        assert ph["approx"] is False
        assert ph["phantom_types"] == 359
        assert ph["word_tokens_excl_phantoms"] == 2752


# ------------------------------------------------------------------ (e) ----- #
class TestUnitConversion:
    UNITS = {"la_word_tokens_now": 3147, "tokens_per_doc": 2.3468,
             "kn_zg57_word_token_equiv": 64.66}

    def test_conversion_math(self):
        ra = RT.convert_threshold(3147 + 2.3468 * 100, self.UNITS)
        assert abs(ra["approx_new_docs"] - 100.0) < 0.1
        ra = RT.convert_threshold(3147 + 64.66 * 2, self.UNITS)
        assert abs(ra["approx_kn_zg57_equivalents"] - 2.0) < 0.01

    def test_below_now_clamps_to_zero_additional(self):
        ra = RT.convert_threshold(1000.0, self.UNITS)
        assert ra["additional_word_tokens"] == 0.0
        assert ra["approx_new_docs"] == 0.0

    def test_none_is_none(self):
        assert RT.convert_threshold(None, self.UNITS) is None

    def test_route7_not_convertible(self):
        assert RT.ROUTES["anchors"].convertible is False

    @needs_artifact
    def test_artifact_anchors_reopen_is_event_not_tokens(self):
        res = json.load(open(RT.RESULTS_PATH, encoding="utf-8"))
        a = res["routes"]["anchors"]
        assert a["reopen_at"] is None
        assert a["status"] == "EVENT_COUNT"
        assert a["native_axis"] == "independent_lineage_anchors"


# ------------------------------------------------------------------ (f) ----- #
class TestSegmentationHonesty:
    def test_asymptote_below_target_refuses(self):
        # saturating curve with asymptote 0.45 < 0.62
        N = np.array([500.0, 1000, 2000, 3000, 4000])
        F = 0.45 - 0.2 * np.exp(-0.001 * N)
        fit = RT.fit_saturating(N, F)
        thr, status = RT.segmentation_threshold(fit)
        assert thr is None and status == "ASYMPTOTE_LIMITED"

    def test_unconstrained_fit_refuses(self):
        thr, status = RT.segmentation_threshold((1.0, 0.7, 1e-5))
        assert thr is None and status == "FIT_UNCONSTRAINED"

    def test_fit_failure_refuses(self):
        thr, status = RT.segmentation_threshold(None)
        assert thr is None and status == "FIT_FAILED"

    def test_asymptote_above_target_extrapolates(self):
        N = np.array([500.0, 1000, 2000, 3000, 4000, 6000])
        F = 0.7 - 0.4 * np.exp(-0.0008 * N)
        fit = RT.fit_saturating(N, F)
        thr, status = RT.segmentation_threshold(fit)
        assert status == "EXTRAPOLATED" and thr is not None and thr > 0
        # the crossing solves a - b*exp(-c*N) = 0.62
        a, b, c = fit
        assert abs((a - b * np.exp(-c * thr)) - RT.SUPERVISED_HEADROOM_F1) < 1e-6


# ------------------------------------------------------------------ (g) ----- #
class TestVectorizedNull:
    def test_preserves_multiset_and_length(self):
        rng = np.random.default_rng(7)
        groups = {3: rng.integers(0, 9, size=(40, 3)), 5: rng.integers(0, 9, size=(10, 5))}
        perm = RT._grouped_within_form_permutation(groups, np.random.default_rng(0))
        for L in groups:
            assert perm[L].shape == groups[L].shape
            assert np.array_equal(np.sort(perm[L], axis=1), np.sort(groups[L], axis=1))

    def test_matches_nulls_module_semantics(self):
        # the reference within_form_permutation also only reorders within each form
        forms = ["abc", "abcde", "xy"]
        out = within_form_permutation(forms, seed=3)
        for a, b in zip(forms, out):
            assert sorted(a) == sorted(b) and len(a) == len(b)


# ------------------------------------------------------------------ (h) ----- #
@pytest.mark.licensed_data
@needs_both
class TestDeterminism:
    def test_analytic_routes_byte_identical(self):
        r1 = RT.compute(routes=["alternation_grid", "anchors"], fast=True, seed=0)
        r2 = RT.compute(routes=["alternation_grid", "anchors"], fast=True, seed=0)
        a = json.dumps(r1, sort_keys=True, ensure_ascii=False)
        b = json.dumps(r2, sort_keys=True, ensure_ascii=False)
        assert a == b


# ------------------------------------------------------------------ (i) ----- #
@needs_artifact
class TestMarkdownPurity:
    def test_doc_is_pure_function_of_json(self):
        if not os.path.exists(RT.DOC_PATH):
            pytest.skip("docs/reopening-thresholds.md not present")
        result = json.load(open(RT.RESULTS_PATH, encoding="utf-8"))
        rendered = RT.render_doc(result)
        committed = open(RT.DOC_PATH, encoding="utf-8").read()
        assert rendered == committed, (
            "docs/reopening-thresholds.md diverges from render_doc(results JSON) — "
            "regenerate with --render-only --write-doc; never hand-edit")

    def test_generated_header_present(self):
        result = json.load(open(RT.RESULTS_PATH, encoding="utf-8"))
        out = RT.render_doc(result)
        assert out.startswith("<!-- GENERATED FILE")
        assert "results/reopening_thresholds.json" in out.splitlines()[1]

    def test_render_is_deterministic(self):
        result = json.load(open(RT.RESULTS_PATH, encoding="utf-8"))
        assert RT.render_doc(result) == RT.render_doc(result)


# ------------------------------------------------------------------ (j) ----- #
@pytest.mark.licensed_data
@needs_both
class TestContradictionGuards:
    """Guards vs the published record. Empirical note (2026-08-05, measured at n_null=200,
    3 site-stratified replicates): the LB analogue FIRES at 3,147 and even ~800 word tokens
    — the plan's expected 'LB@3,147 does not fire / threshold > 3,147' is refuted by
    measurement, so the honest pin is SIZE_NOT_BINDING (no token-count promise), plus the
    published LA NO-POWER reproduced directly."""

    def test_lb_full_clears_morphology(self):
        corpus = LBC.load_linb()
        r = M.null_falsification(corpus, M.SignCodec.from_corpus(corpus),
                                 affixes=LBC.MYC_AFFIXES, n_null=40, seed=0)
        assert r["has_morphology_power"] is True
        assert r["real_confirm_rate"] >= 0.5      # locks the published 0.562-fires regime

    def test_la_at_own_size_does_not_fire(self):
        corpus = M.load_corpus()
        r = M.null_falsification(corpus, M.SignCodec.from_corpus(corpus),
                                 affixes=M.PREREG_AFFIXES, n_null=40, seed=0)
        assert r["has_morphology_power"] is False  # the published NO-POWER, reproduced

    @needs_artifact
    def test_artifact_does_not_promise_token_reopening_for_morphology(self):
        res = json.load(open(RT.RESULTS_PATH, encoding="utf-8"))
        m = res["routes"]["morphology"]
        assert m["status"] == "SIZE_NOT_BINDING"
        assert m["reopen_at"] is None
        assert m["threshold_native"] is not None
        assert m["threshold_native"] <= res["units"]["la_word_tokens_now"]
        assert m["la_control"]["fires"] is False
        assert m["structural_reopen_event"]


# ------------------------------------------------------------------ (k) ----- #
@needs_artifact
class TestArtifact:
    def test_full_run_all_routes(self):
        res = json.load(open(RT.RESULTS_PATH, encoding="utf-8"))
        assert res["fast"] is False, "the shipped artifact must be a full run"
        assert res["version"] == RT.VERSION
        assert res["routes_computed"] == RT.ROUTE_ORDER
        for name in RT.ROUTE_ORDER:
            r = res["routes"][name]
            for key in ("status", "info_budget", "phantom_sensitivity", "closed_result",
                        "native_axis", "caveats"):
                assert key in r, f"route {name} missing {key}"

    def test_trigger_protocol_wired(self):
        res = json.load(open(RT.RESULTS_PATH, encoding="utf-8"))
        tp = res["trigger_protocol"]
        assert tp["watch_doc"] == "docs/watch/anetaki_ii.md"
        assert "NEW pre-registration" in tp["rule"]
        assert "never an automatic claim" in tp["rule"]
