"""Locked properties of the name-parallel probe layer (scripts/comparison/name_parallel.py + the
promoted scripts/comparison/nulls.banded_map_permutation) — Phase 5a build+calibration scope:

(a) criterion semantics: slots 1..n_exact value-identical, consonant slot via cv_label with vowel
    disregard; fail CLOSED on undecodable signs (*NN / no-cv values), short words, missing slots;
    the keyed match_count agrees with the pairwise reference matches() on every grid variant;
(b) promoted null (banded_map_permutation): within-band bijection over the value map, band
    locality, seeded determinism — algorithm verbatim from the di-mino-301 audit PC2 control;
(c) name-join: every reported count is recomputed from the returned lists (generated, never
    hand-written); the KN join lands in the sanity band 100-250; dual-computed attribution
    mismatch < 2%;
(d) logogram filter: ontology non-syllabic classes + '+'-ligatures excluded from the pool; *NN in
    criterion slots 1-3 COUNTED out of the decodable pool, never silently dropped;
(e) synthetic positive control: planted name parallels FIRE above the deflated bars; the
    unplanted background does not — the machinery discriminates;
(f) cherry-pick bounded only when n_eff is honest: best-of-grid on null corpora is suppressed at
    instrumented n_eff=12 but fires against the undeflated null mean — multiplicity is
    load-bearing;
(g) strata (Art. XII, reported non-verdict): S1 keeps only all-dark-blue criterion slots, S2 drops
    toponym-motivated signs; the committed Salgarella/census files yield 25 / 27 signs;
(h) n_eff-monotone bars: expected-max and operative bars nondecreasing in n_eff;
(i) determinism: same-seed draws identical, different-seed draws differ (nulls, N2, lfake corpus);
(j) no-verdict-import (invariant 2/4): name_parallel never imports scripts.verdict.

Phase 5b properties (prereg freeze, run_probe refusing without a green calibration file,
plan_hash match, effective_n/info-budget presence in result.json) are NOT locked here — they
belong to the separately gated probe step.
"""
import json
import os
import subprocess
import sys
from collections import Counter

import numpy as np
import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.comparison import name_parallel as npb  # noqa: E402
from scripts.comparison.nulls import banded_map_permutation  # noqa: E402

_have_data = all(os.path.exists(p) for p in
                 (npb.STRUCTURED_SILVER, npb.ONTOLOGY, npb.NAMES_COG, npb.DAMOS_ITEMS))
needs_data = pytest.mark.skipif(not _have_data, reason="gitignored bronze/silver not present")

C1 = npb.PRIMARY

# ---- shared synthetic fixture (25 CV signs + 5 pure vowels; all cv_label-decodable) ---- #
_CONS = ["K", "S", "T", "R", "N"]
_VOW = ["A", "E", "I", "O", "U"]
_SIGNS = [c + v for c in _CONS for v in _VOW] + _VOW


def _rand_word(rng, lens=(3, 4)):
    L = int(rng.choice(lens))
    return tuple(_SIGNS[int(i)] for i in rng.integers(0, len(_SIGNS), size=L))


def _fixture(seed=7, n_names=20, n_background=80):
    rng = np.random.default_rng(seed)
    names = sorted({_rand_word(rng) for _ in range(n_names)})
    background = sorted({_rand_word(rng) for _ in range(n_background)})
    return rng, names, background


# --------------------------------------------------------------------------- #
# (a) criterion semantics
# --------------------------------------------------------------------------- #
class TestCriterionSemantics:
    def test_vowel_disregard_in_consonant_slot(self):
        assert npb.matches(("KU", "RO", "SA"), ("KU", "RO", "SE"), C1)

    def test_exact_slots_required(self):
        assert not npb.matches(("KU", "RA", "SA"), ("KU", "RO", "SE"), C1)

    def test_undecodable_slot3_fails_closed_both_sides(self):
        assert not npb.matches(("KU", "RO", "*301"), ("KU", "RO", "SE"), C1)
        # RA2 has no cv parse (trailing digit) — undecodable on the NAME side too
        assert not npb.matches(("KU", "RO", "RA"), ("KU", "RO", "RA2"), C1)

    def test_two_sign_word_rejected(self):
        assert not npb.matches(("KU", "RO"), ("KU", "RO", "SE"), C1)
        assert not npb.matches(("KU", "RO", "SE"), ("KU", "RO"), C1)

    def test_exact_slot3_mode(self):
        c = npb.Criterion(name="t_exact", min_signs=3, n_exact=2, slot3_mode="exact")
        assert npb.matches(("KU", "RO", "SA"), ("KU", "RO", "SA"), c)
        assert not npb.matches(("KU", "RO", "SA"), ("KU", "RO", "SE"), c)

    def test_pure_vowel_shares_zero_consonant_class(self):
        # documented semantics: cv_label('A') == ('', 'A') — two pure vowels share consonant ''
        assert npb.matches(("KU", "RO", "A"), ("KU", "RO", "E"), C1)

    def test_missing_consonant_slot_fails_closed(self):
        c = npb.Criterion(name="t_e3", min_signs=3, n_exact=3, slot3_mode="consonant")
        # needs 4 slots; 3-sign sequences can never match
        assert not npb.matches(("KU", "RO", "SA"), ("KU", "RO", "SA"), c)

    def test_grid_shape_and_primary(self):
        grid = npb.criterion_grid()
        assert len(grid) == 12 and len({g.name for g in grid}) == 12
        assert grid[0] is npb.PRIMARY
        assert (C1.name, C1.min_signs, C1.n_exact, C1.slot3_mode) == \
            ("packard1974_kn_primary", 3, 2, "consonant")

    def test_keyed_match_count_equals_pairwise(self):
        _, names, background = _fixture()
        for crit in npb.criterion_grid():
            brute = sum(1 for w in background if any(npb.matches(w, n, crit) for n in names))
            assert npb.match_count(background, names, crit) == brute


# --------------------------------------------------------------------------- #
# (b) promoted null — banded_map_permutation
# --------------------------------------------------------------------------- #
class TestPromotedNull:
    VALUES = list("abcdefgh")
    FREQ = Counter({"a": 100, "b": 90, "c": 80, "d": 70, "e": 10, "f": 9, "g": 8, "h": 7})
    VMAP = {v: v.upper() for v in VALUES}

    def test_within_band_bijection(self):
        pm = banded_map_permutation(self.VALUES, self.VMAP, self.FREQ, seed=0, n_bands=2)
        assert {pm[v] for v in "abcd"} == {"A", "B", "C", "D"}   # band 1 readings preserved
        assert {pm[v] for v in "efgh"} == {"E", "F", "G", "H"}   # band 2 readings preserved
        assert sorted(pm.values()) == sorted(self.VMAP.values())  # global bijection

    def test_band_locality(self):
        # a common sign NEVER receives a rare sign's reading (Packard's banding)
        for seed in range(6):
            pm = banded_map_permutation(self.VALUES, self.VMAP, self.FREQ,
                                        seed=seed, n_bands=2)
            for v in "abcd":
                assert pm[v] in {"A", "B", "C", "D"}

    def test_determinism_and_seed_sensitivity(self):
        a = banded_map_permutation(self.VALUES, self.VMAP, self.FREQ, seed=3, n_bands=2)
        b = banded_map_permutation(self.VALUES, self.VMAP, self.FREQ, seed=3, n_bands=2)
        assert a == b
        others = [banded_map_permutation(self.VALUES, self.VMAP, self.FREQ, seed=s, n_bands=2)
                  for s in range(6)]
        assert any(o != a for o in others)


# --------------------------------------------------------------------------- #
# (c) name-join (licensed data)
# --------------------------------------------------------------------------- #
@pytest.mark.licensed_data
@needs_data
class TestNameJoin:
    @pytest.fixture(scope="class")
    def joined(self):
        ni = npb.load_names_cog()
        docs = npb.load_damos_docs()
        return ni, npb.kn_attested_names(ni["names"], docs)

    def test_counts_generated_not_hand_written(self, joined):
        ni, join = joined
        assert ni["diagnostics"]["distinct_name_types"] == len(ni["names"])
        assert join["diagnostics"]["kn_names"] == len(join["kn_names"])
        assert join["diagnostics"]["kn_vocab_types"] == len(join["kn_vocab"])

    def test_pinned_regression(self, joined):
        ni, join = joined
        d = ni["diagnostics"]
        assert (d["rows"], d["glossed_rows"], d["glossed_fully_decodable_ge3_rows"]) == \
            (919, 455, 429)
        assert join["diagnostics"]["kn_names"] == 155

    def test_sanity_band_and_attribution(self, joined):
        _, join = joined
        d = join["diagnostics"]
        assert d["in_sanity_band"] and d["sanity_band"] == [100, 250]
        assert d["doc_attribution_mismatch_fraction"] < 0.02
        assert not d["attribution_mismatch_over_2pct"]
        assert d["kn_vocab_symmetric_difference_vs_heading"] == 0

    def test_names_are_kn_attested(self, joined):
        _, join = joined
        vocab = set(join["kn_vocab"])
        assert all(n in vocab for n in join["kn_names"])


# --------------------------------------------------------------------------- #
# (d) logogram filter + *NN exclusion accounting
# --------------------------------------------------------------------------- #
class TestLogogramFilter:
    TYPES = [("GRA", "KU", "RO"),            # ontology logogram in a slot -> excluded
             ("VIN+KA", "KU", "RO"),         # '+'-ligature -> excluded
             ("*301", "KU", "RO"),           # *NN in slots 1-3 -> counted out of decodable
             ("KU", "RO", "SA", "*301"),     # *NN at slot 4 -> stays (fail-closes per-criterion)
             ("KU", "RO", "SA"),
             ("KU", "RO")]                   # < min_signs -> not a pool type at all

    def test_build_pool_accounting(self):
        pool, counts = npb.build_pool(self.TYPES, nonsyllabic={"GRA"}, min_signs=3)
        assert pool == [("KU", "RO", "SA"), ("KU", "RO", "SA", "*301")]
        assert counts["types_ge_min_signs"] == 5
        assert counts["excluded_logogram_types"] == 2
        assert counts["types_after_logogram_filter"] == 3
        assert counts["excluded_undecodable_star_slots_1_3"] == 1
        assert counts["pool_decodable_types"] == 2

    @pytest.mark.licensed_data
    @needs_data
    def test_real_pool_pinned_and_clean(self):
        la = npb.load_la_packard_pool()
        d = la["diagnostics"]
        assert (d["types_ge_min_signs"], d["types_after_logogram_filter"],
                d["excluded_logogram_types"], d["excluded_undecodable_star_slots_1_3"],
                d["pool_decodable_types"], d["docs"]) == (610, 571, 39, 70, 501, 1341)
        assert d["pool_decodable_types"] == len(la["pool"])
        nonsyll = npb.nonsyllabic_tokens()
        for w in la["pool"]:
            assert not any(s in nonsyll or "+" in s for s in w)
            assert not any(s.startswith("*") for s in w[:3])


# --------------------------------------------------------------------------- #
# (e) synthetic positive control — the machinery discriminates
# --------------------------------------------------------------------------- #
class TestSyntheticPositiveControl:
    def test_planted_parallels_fire_background_does_not(self):
        _, names, background = _fixture(seed=7)
        planted = []
        for n in names[:10]:                    # plant slots-1-2-exact + consonant-slot-3 matches
            cv = npb.cv_label(n[2])
            alt_v = "E" if cv[1] != "E" else "O"
            planted.append((n[0], n[1], (cv[0] + alt_v) if cv[0] else alt_v))
        pool = sorted((set(background) | set(planted)) - set(names))
        obs = npb.match_count(pool, names, C1)
        assert obs >= 10                        # every plant is found
        bars = npb.bars_from_nulls(npb.n1_banded_null(pool, names, C1, B=200, seed=11),
                                   n_eff=12)
        assert obs > bars["operative_bar"]      # FIRES above both deflated bars
        obs_bg = npb.match_count(background, names, C1)
        bars_bg = npb.bars_from_nulls(npb.n1_banded_null(background, names, C1, B=200, seed=11),
                                      n_eff=12)
        assert obs_bg <= bars_bg["operative_bar"]  # no plant, no fire


# --------------------------------------------------------------------------- #
# (f) cherry-pick bounded ONLY when n_eff is honest (multiplicity is load-bearing)
# --------------------------------------------------------------------------- #
class TestCherryPickBounded:
    def test_honest_n_eff_suppresses_best_of_grid(self):
        rng, names, _ = _fixture(seed=7)
        grid = npb.criterion_grid()
        base = sorted({_rand_word(rng, lens=(3, 4, 5)) for _ in range(120)})
        fires_honest = fires_dishonest = fires_naive = 0
        for t in range(20):                      # 20 null corpora, no genuine correspondence
            fake = npb.banded_pool_null(base, seed=100 + t)
            best_crit, best_m = None, -1
            for c in grid:
                m = npb.match_count(fake, names, c)
                if m > best_m:
                    best_crit, best_m = c, m
            nl = npb.n1_banded_null(fake, names, best_crit, B=100, seed=9000 + t)
            honest = npb.bars_from_nulls(nl, n_eff=12)
            dishonest = npb.bars_from_nulls(nl, n_eff=1)
            assert honest["operative_bar"] >= dishonest["operative_bar"]
            fires_honest += int(best_m > honest["operative_bar"])
            fires_dishonest += int(best_m > dishonest["operative_bar"])
            fires_naive += int(best_m > honest["mu0"])   # no deflation at all: the null mean
        assert fires_honest == 0                 # deterministic fixture: fully suppressed
        assert fires_honest <= fires_dishonest
        assert fires_naive >= 10                 # cherry-picking DOES beat the raw null mean


# --------------------------------------------------------------------------- #
# (g) strata derivation (Art. XII, reported non-verdict)
# --------------------------------------------------------------------------- #
class TestStrata:
    def test_s1_darkblue_slots_only(self):
        pool = [("KU", "RO", "SA", "NI"), ("KU", "RO", "NI")]
        out = npb.stratum_s1_darkblue(pool, C1, darkblue={"KU", "RO", "SA"})
        assert out == [("KU", "RO", "SA", "NI")]   # slot 4 NI is NOT a criterion slot

    def test_s2_toponym_excluded(self):
        pool = [("PA", "RO", "SA"), ("KU", "RO", "SA")]
        out = npb.stratum_s2_toponym_excluded(pool, C1, covered={"PA"})
        assert out == [("KU", "RO", "SA")]

    def test_real_strata_sources(self):
        db = npb.load_salgarella_darkblue()
        cov = npb.load_toponym_covered_signs()
        assert len(db) == 25 and {"A", "DA", "PA"} <= db
        assert len(cov) == 27 and {"PA", "I", "TO"} <= cov


# --------------------------------------------------------------------------- #
# (h) n_eff-monotone bars
# --------------------------------------------------------------------------- #
class TestNEffMonotone:
    def test_bars_nondecreasing_in_n_eff(self):
        rng = np.random.default_rng(0)
        nulls = rng.poisson(8, size=200).astype(float)
        bars = [npb.bars_from_nulls(nulls, n_eff=n) for n in (1, 4, 12, 100)]
        emax = [b["expected_max_order_stat"] for b in bars]
        oper = [b["operative_bar"] for b in bars]
        assert emax == sorted(emax) and oper == sorted(oper)
        assert emax[-1] > emax[0]                # strictly rising once sigma0 > 0


# --------------------------------------------------------------------------- #
# (i) determinism (+ N2 machinery properties on synthetic docs)
# --------------------------------------------------------------------------- #
class TestDeterminism:
    def test_banded_pool_null_seeded(self):
        _, _, background = _fixture()
        a = npb.banded_pool_null(background, seed=5)
        b = npb.banded_pool_null(background, seed=5)
        c = npb.banded_pool_null(background, seed=6)
        assert a == b and a != c

    def test_n1_distribution_seeded(self):
        _, names, background = _fixture()
        a = npb.n1_banded_null(background, names, C1, B=30, seed=2)
        b = npb.n1_banded_null(background, names, C1, B=30, seed=2)
        assert np.array_equal(a, b)

    def test_lfake_corpus_seeded(self):
        _, _, background = _fixture()
        a = npb.lfake_la_like_corpus(background, seed=4)
        b = npb.lfake_la_like_corpus(background, seed=4)
        c = npb.lfake_la_like_corpus(background, seed=5)
        assert a == b and a != c
        assert all(s in set(_SIGNS) for w in a for s in w)  # closed over the pool inventory

    def test_n2_document_permutation_null(self):
        rng, names, background = _fixture()
        docs = [{"wordforms": frozenset({names[i], _rand_word(rng)})} for i in range(len(names))]
        a = npb.n2_document_permutation_null(background, names, docs, n_docs=5, crit=C1,
                                             B=20, seed=3)
        b = npb.n2_document_permutation_null(background, names, docs, n_docs=5, crit=C1,
                                             B=20, seed=3)
        assert np.array_equal(a, b) and len(a) == 20
        # a pseudo-Knossos list is a SUBSET of the full name list: counts bounded by the full run
        full = npb.match_count(background, names, C1)
        assert all(v <= full for v in a)


# --------------------------------------------------------------------------- #
# (j) no verdict import (invariant 2/4 — the model never grades itself)
# --------------------------------------------------------------------------- #
def test_imports_no_verdict():
    import ast
    src = open(os.path.join(_REPO_ROOT, "scripts", "comparison", "name_parallel.py"),
               encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all("verdict" not in n.name for n in node.names)
        if isinstance(node, ast.ImportFrom):
            assert "verdict" not in (node.module or "")
            assert all("verdict" not in a.name for a in node.names)
    code = ("import sys; import scripts.comparison.name_parallel; "
            "assert 'scripts.verdict' not in sys.modules, 'name_parallel imported scripts.verdict'; "
            "print('clean')")
    out = subprocess.run([sys.executable, "-c", code], cwd=_REPO_ROOT,
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "clean" in out.stdout
