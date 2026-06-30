"""Adversarial unit tests for scripts.decipher (the combinatorial/EM decipherment engine).

Covers, per the verification brief:
  1. weighted_edit_distance + align_pairs: known DP cases + phi-dependent substitution.
  2. maplearn.fit_map: recovers a known small map; M-step sign/orientation correct.
  3. run_em: converges, deterministic (same input -> same phi), recovers the synthetic map.
  4. null_linear_a: reports chance-level cognate accuracy (no hallucinated signal).

Run from anywhere:
    pytest tests/test_decipher.py -v
"""
import os
import sys

# Make `scripts.decipher` importable regardless of pytest's invocation cwd
# (mirrors the sys.path trick the CLI itself uses).
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.decipher import (  # noqa: E402
    editdist,
    align,
    maplearn,
    eval as evalmod,
    decipher,
    demo_fixture,
    null_linear_a,
)


# --------------------------------------------------------------------------- #
# 1. weighted_edit_distance + align_pairs (the E-step local scorer / DP)
# --------------------------------------------------------------------------- #
class TestEditDistance:
    def _id(self, *seqs):
        # identity phi over the union of tokens: a token vs ITSELF is free (Levenshtein semantics).
        return {t: t for s in seqs for t in s}

    def test_identical_sequences_are_zero(self):
        cw = ("a", "b", "c")
        assert editdist.weighted_edit_distance(cw, cw, phi=self._id(cw)) == 0.0

    def test_single_substitution_costs_sub_cost(self):
        # one differing token -> exactly one substitution (matches free under identity phi)
        a, b = ("a", "b"), ("a", "x")
        assert editdist.weighted_edit_distance(a, b, phi=self._id(a, b)) == 1.0
        # sub_cost below 2*indel (1+1) so substitution beats delete+insert:
        assert editdist.weighted_edit_distance(a, b, phi=self._id(a, b), sub_cost=1.5) == 1.5
        # sub_cost above 2*indel -> DP correctly prefers delete+insert over the sub:
        assert editdist.weighted_edit_distance(a, b, phi=self._id(a, b), sub_cost=2.5) == 2.0

    def test_single_insertion_and_deletion_cost_indel(self):
        a, b = ("a", "b"), ("a", "b", "c")
        assert editdist.weighted_edit_distance(a, b, phi=self._id(a, b)) == 1.0   # insert c
        assert editdist.weighted_edit_distance(b, a, phi=self._id(a, b)) == 1.0   # delete c
        assert editdist.weighted_edit_distance(("a",), ("a", "b", "c"),
                                               phi={"a": "a"}, indel_cost=0.5) == 1.0

    def test_empty_sequences(self):
        assert editdist.weighted_edit_distance((), ()) == 0.0
        assert editdist.weighted_edit_distance((), ("a", "b")) == 2.0   # 2 insertions
        assert editdist.weighted_edit_distance(("a", "b"), ()) == 2.0   # 2 deletions

    def test_classic_levenshtein_kitten_sitting(self):
        # Textbook Levenshtein: kitten -> sitting = 3 (identity phi => matches free).
        k, s = tuple("kitten"), tuple("sitting")
        assert editdist.weighted_edit_distance(k, s, phi=self._id(k, s)) == 3.0

    def test_empty_phi_charges_for_identical_tokens(self):
        # IMPORTANT semantic (locked): an EMPTY phi does NOT reduce to Levenshtein on a
        # SHARED alphabet — phi.get(c) is None != c, so even c->c costs sub_cost. The
        # "reduces to Levenshtein" claim holds for the IDENTITY cold start (phi={c:c}),
        # or for empty phi only on DISJOINT alphabets (where no cipher token ever equals
        # a plain token, so there are no self-matches to misprice). See editdist docstring.
        cw = ("a", "b")
        assert editdist.weighted_edit_distance(cw, cw, phi={}) == 2.0  # two self-subs @ 1.0
        assert editdist.weighted_edit_distance(cw, cw, phi={}, sub_cost=0.7) == 1.4

    def test_phi_agreeing_substitution_is_free(self):
        # phi maps cipher x -> plain y: substituting x for y must cost 0.
        assert editdist.weighted_edit_distance(("x",), ("y",), phi={"x": "y"}) == 0.0
        # And a multi-token word where phi fully agrees is free.
        cw, pw = ("x", "q"), ("y", "z")
        assert editdist.weighted_edit_distance(cw, pw, phi={"x": "y", "q": "z"}) == 0.0

    def test_phi_missing_key_is_a_mismatch(self):
        # cipher token absent from phi is a full-cost substitution, not free.
        assert editdist.weighted_edit_distance(("x",), ("y",), phi={}) == 1.0
        assert editdist.weighted_edit_distance(("x",), ("y",), phi={"w": "y"}) == 1.0

    def test_symmetry_of_plain_levenshtein(self):
        # With empty phi and unit costs, edit distance is symmetric.
        a, b = tuple("abc"), tuple("xyz")
        assert editdist.weighted_edit_distance(a, b) == editdist.weighted_edit_distance(b, a)

    def test_align_pairs_score_matches_distance(self):
        # The score returned by align_pairs must equal weighted_edit_distance.
        a, b = tuple("kitten"), tuple("sitting")
        score, pairs = editdist.align_pairs(a, b)
        assert score == editdist.weighted_edit_distance(a, b)

    def test_align_pairs_skips_indels(self):
        # Only substitution/match columns survive; insertions/deletions are dropped.
        # cipher "AB" vs plain "AXB": align A-A (match), insert X, B-B (match) -> 2 pairs, no 'X'.
        cw, pw = ("A", "B"), ("A", "X", "B")
        score, pairs = editdist.align_pairs(cw, pw, phi={"A": "A", "B": "B"})
        assert score == 1.0  # one insertion of X
        assert pairs == [("A", "A"), ("B", "B")]  # X (plain-only) is skipped

    def test_align_pairs_columns_are_left_to_right(self):
        cw, pw = ("A", "B", "C"), ("A", "B", "C")
        _score, pairs = editdist.align_pairs(cw, pw, phi={"A": "A", "B": "B", "C": "C"})
        assert [c for c, _p in pairs] == ["A", "B", "C"]
        assert [p for _c, p in pairs] == ["A", "B", "C"]


# --------------------------------------------------------------------------- #
# 2. maplearn.fit_map (the M-step) + build_count_matrix
# --------------------------------------------------------------------------- #
class TestFitMap:
    def test_recovers_known_small_map_from_clean_co_occurrence(self):
        # Three cipher tokens each co-occur overwhelmingly with one plain token.
        # fit_map must recover A->X, B->Y, C->Z (the max-co-occurrence assignment).
        pairs = [("A", "X")] * 10 + [("B", "Y")] * 9 + [("C", "Z")] * 8
        phi = maplearn.fit_map(pairs)
        assert phi == {"A": "X", "B": "Y", "C": "Z"}

    def test_sign_is_maximises_co_occurrence_not_minimises(self):
        # Adversarial: if the sign were wrong (cost = +count), fit_map would pick
        # the LEAST co-occurring pairs. Inject a clear winner and a clear loser.
        pairs = [("A", "WIN")] * 20 + [("A", "LOSE")] * 1
        phi = maplearn.fit_map(pairs)
        assert phi.get("A") == "WIN"  # maximises count, not minimises

    def test_orientation_is_cipher_to_plain(self):
        # phi keys must be cipher tokens (first column), values plain tokens (second).
        pairs = [("CIPHER1", "PLAIN1")] * 5
        phi = maplearn.fit_map(pairs)
        assert "CIPHER1" in phi
        assert phi["CIPHER1"] == "PLAIN1"

    def test_rectangular_more_cipher_than_plain_maps_min(self):
        # 3 cipher tokens, 2 plain: only 2 get mapped (1-1 policy, documented LIMITATION).
        pairs = [("C1", "P1")] * 5 + [("C2", "P2")] * 5 + [("C3", "P1")] * 1
        phi = maplearn.fit_map(pairs)
        assert len(phi) == 2  # min(|cipher|, |plain|)
        # The two strongest pairs win.
        assert phi.get("C1") == "P1"
        assert phi.get("C2") == "P2"

    def test_smoothing_does_not_change_argmin(self):
        # A uniform additive smoothing shifts every cell equally -> same assignment.
        pairs = [("A", "X")] * 10 + [("B", "Y")] * 3
        phi0 = maplearn.fit_map(pairs, smoothing=0.0)
        phi_s = maplearn.fit_map(pairs, smoothing=5.0)
        assert phi0 == phi_s

    def test_empty_pairs_returns_empty_map(self):
        assert maplearn.fit_map([]) == {}

    def test_build_count_matrix_shape_and_tallies(self):
        pairs = [("A", "X"), ("A", "X"), ("A", "Y"), ("B", "X")]
        M, cchars, pchars = maplearn.build_count_matrix(pairs)
        assert cchars == ["A", "B"]            # sorted cipher tokens
        assert pchars == ["X", "Y"]            # sorted plain tokens
        assert M.shape == (2, 2)
        ci = cchars.index("A"); cj_x = pchars.index("X"); cj_y = pchars.index("Y")
        assert M[ci, cj_x] == 2.0
        assert M[ci, cj_y] == 1.0


# --------------------------------------------------------------------------- #
# 3. run_em: convergence, determinism, end-to-end recovery
# --------------------------------------------------------------------------- #
class TestRunEM:
    def _run(self, **kw):
        fix = demo_fixture.default_fixture()
        return decipher.run_em(
            fix["cipher_words"], fix["plain_words"], init="frequency", max_iters=25, **kw
        ), fix

    def test_recovers_full_synthetic_map(self):
        # The headline legitimacy check: on the known-map fixture the engine recovers
        # every cipher->plain token AND every word cognate.
        (phi, _al, _hist), fix = self._run()
        acc, nc, ne = evalmod.mapping_accuracy(phi, fix["truth_map"])
        assert acc == 1.0 and nc == ne == len(fix["truth_map"])

    def test_em_contributes_beyond_frequency_init(self):
        # frequency_init alone is NOT perfect (it swaps frequency-tied letters);
        # the EM loop must repair at least one tie. This proves the loop does work,
        # i.e. the 100% is not a trivial pass-through of the cold start.
        fix = demo_fixture.default_fixture()
        cw, pw, truth = fix["cipher_words"], fix["plain_words"], fix["truth_map"]
        phi0 = maplearn.frequency_init(cw, pw)
        acc0, _, _ = evalmod.mapping_accuracy(phi0, truth)
        phi, _al, _hist = decipher.run_em(cw, pw, init="frequency", max_iters=25)
        acc1, _, _ = evalmod.mapping_accuracy(phi, truth)
        assert acc1 == 1.0
        assert acc1 > acc0, "EM must improve on the cold start (else it is a no-op)"

    def test_converges_with_stable_last_iteration(self):
        phi, _al, hist = self._run()[0]
        assert len(hist) >= 1
        assert hist[-1]["stable"] is True

    def test_deterministic_same_input_same_phi(self):
        # Run twice, the learned phi must be byte-identical (no RNG anywhere).
        (phi_a, _a, _ha), _ = self._run()
        (phi_b, _b, _hb), _ = self._run()
        assert phi_a == phi_b

    def test_deterministic_across_inits(self):
        # Identity cold start is also deterministic.
        fix = demo_fixture.default_fixture()
        kw = dict(max_iters=10)
        phi_a, _, _ = decipher.run_em(fix["cipher_words"], fix["plain_words"], init="identity", **kw)
        phi_b, _, _ = decipher.run_em(fix["cipher_words"], fix["plain_words"], init="identity", **kw)
        assert phi_a == phi_b

    def test_identity_cold_start_terminates_within_max_iters(self):
        # The harder cold start is documented to often hit a local optimum; it must
        # still TERMINATE (not run forever) and stay deterministic.
        fix = demo_fixture.default_fixture()
        phi, _al, hist = decipher.run_em(
            fix["cipher_words"], fix["plain_words"], init="identity", max_iters=25
        )
        assert len(hist) <= 25
        # It either converged (stable last iter) or hit the cap — both are acceptable.
        assert hist[-1]["stable"] is True or len(hist) == 25

    def test_cognate_accuracy_full_when_map_recovered(self):
        # If phi is the true map, every cipher word's nearest plain is its true cognate.
        fix = demo_fixture.default_fixture()
        phi, al, _hist = decipher.run_em(
            fix["cipher_words"], fix["plain_words"], init="frequency", max_iters=25
        )
        best = {cw: a[0] for cw, a in al.items()}
        cacc, ncc, nec = evalmod.cognate_accuracy(best, fix["true_pairs"])
        assert cacc == 1.0 and nec == len(fix["true_pairs"])


# --------------------------------------------------------------------------- #
# 4. null_linear_a: the no-signal control lands at chance
# --------------------------------------------------------------------------- #
class TestNullLinearA:
    def test_null_cognate_accuracy_is_at_chance(self):
        # On an uncorrelated cipher/plain pair there is no recoverable map, so
        # word-level cognate accuracy must collapse to the chance floor (no skill).
        cipher = list(null_linear_a.DEMO_LINEAR_A)[:20]
        plain = [tuple(w.lower()) for w in null_linear_a.UNCORRELATED_PLAIN][:60]
        _phi, _al, _tp, metrics = null_linear_a.run_null(
            cipher, plain, max_len_delta=2, iters=25, init="frequency"
        )
        acc = metrics["cognate_accuracy"]
        chance = metrics["chance_cognate_accuracy"]
        # Generous band: must not be meaningfully above the chance floor...
        assert acc <= chance + 0.10, f"null hallucinated skill: {acc} vs chance {chance}"
        # ...and must be far from perfect recovery (the no-signal guarantee).
        assert acc < 0.5

    def test_null_is_deterministic(self):
        cipher = list(null_linear_a.DEMO_LINEAR_A)[:15]
        plain = [tuple(w.lower()) for w in null_linear_a.UNCORRELATED_PLAIN][:40]
        r1 = null_linear_a.run_null(cipher, plain, iters=10)[3]
        r2 = null_linear_a.run_null(cipher, plain, iters=10)[3]
        assert r1["cognate_accuracy"] == r2["cognate_accuracy"]
        assert r1["chance_cognate_accuracy"] == r2["chance_cognate_accuracy"]


# --------------------------------------------------------------------------- #
# 5. eval metrics + frequency_init sanity
# --------------------------------------------------------------------------- #
class TestEvalAndInit:
    def test_mapping_accuracy_counts_unmapped_as_wrong(self):
        truth = {"A": "X", "B": "Y", "C": "Z"}
        phi = {"A": "X"}  # B, C unmapped -> wrong
        acc, nc, ne = evalmod.mapping_accuracy(phi, truth)
        assert ne == 3 and nc == 1 and abs(acc - 1 / 3) < 1e-9

    def test_chance_cognate_accuracy_is_one_over_candidates(self):
        # One cipher word of length 3, two plain words of length 3 -> 1/2.
        cipher = [tuple("abc")]
        plain = [tuple("abc"), tuple("xyz")]
        true_pairs = {tuple("abc"): tuple("abc")}
        chance = evalmod.chance_cognate_accuracy(cipher, plain, true_pairs, max_len_delta=0)
        assert abs(chance - 0.5) < 1e-9

    def test_frequency_init_is_deterministic_and_rank_matched(self):
        # k-th most frequent cipher token -> k-th most frequent plain token.
        cipher_words = [("A", "A", "B"), ("A", "C", "C")]   # A:3, C:2, B:1
        plain_words = [("x", "x", "y"), ("x", "z", "z")]    # x:3, z:2, y:1
        phi = maplearn.frequency_init(cipher_words, plain_words)
        # Rank 1 (count 3): A -> x ; rank 2 (count 2): C -> z ; rank 3 (count 1): B -> y
        assert phi.get("A") == "x"
        assert phi.get("C") == "z"
        assert phi.get("B") == "y"
        # Deterministic.
        assert phi == maplearn.frequency_init(cipher_words, plain_words)
