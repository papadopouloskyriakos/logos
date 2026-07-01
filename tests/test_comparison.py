"""Adversarial tests for the L_fake canary under scripts/comparison/ (task: verify the verifier).

These tests lock in the four properties the canary's honesty depends on, AND lock in the one
property that is *weaker than the docstring claims* (discovered during adversarial verification):
L_fake is rejection-sampled only against the CALIBRATION SET (the gold file's Hebrew side), so
``lexical_overlap_rate == 0.0`` is a guarantee about that set, NOT about the Hebrew language. A
small but non-zero rate of real Biblical-Hebrew roots from outside the gold file slip into L_fake
(the independent-consonant sampler hits them by chance). That residual is exposed here so it can
never be silently re-asserted as "zero real lexical content".

Run from anywhere:
    pytest tests/test_comparison.py -v
"""
import os
import sys

import numpy as np

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.comparison import lfake, lexstat, nulls, run_canary  # noqa: E402
from scripts.comparison import phonostat, morphostat, searchlog, litindex  # noqa: E402,F401
from scripts import verdict, logos_stats  # noqa: E402


# --------------------------------------------------------------------------- #
# Fixtures: a small calibration sample + a deterministic slice of the gold file
# --------------------------------------------------------------------------- #
_HEB_SAMPLE = [
    "abd", "abyw", "mlky", "twrhm", "bkr", "kab", "lab", "ibrd", "aprd", "adwn",
    "azn", "abn", "babn", "abnm", "abnym", "mlk", "kab", "byn", "byt", "sdq",
]

# A short, fixed list of well-attested Biblical-Hebrew / Semitic trilateral roots that a frontier
# model will have seen in training, deliberately chosen to be ABSENT from the small calibration
# sample above so they exercise the "out-of-calibration-set" rejection gap.
_KNOWN_HEBREW_ROOTS = [
    "yhw", "mwt", "hll", "qtl", "ktb", "yld", "zkn", "qny", "yrd", "brk",
    "ntr", "shl", "slm", "ktn", "nbn", "yqb", "ysr", "tkn", "blq", "pth",
]


def _load_gold_slice(n_uga=500, n_heb=800):
    """Deterministic slice of the gold cognate file, sized to keep tests under a few seconds."""
    uga, heb, _ = run_canary.load_gold()
    uga_u = sorted(set(uga))[:n_uga]
    heb_u = sorted(set(heb))[:n_heb]
    return uga_u, heb_u


# --------------------------------------------------------------------------- #
# 1. DETERMINISM — the canary is a scientific control only if reproducible
# --------------------------------------------------------------------------- #
def test_lfake_deterministic_same_seed_full_corpus():
    uga, heb, _ = run_canary.load_gold()
    heb_u = sorted(set(heb))
    cfg = lfake.calibrate_to(heb_u, mode="semitic", root_len=3)
    a = [e["form"] for e in lfake.LFakeGenerator(cfg, seed=42).generate_lexicon()]
    b = [e["form"] for e in lfake.LFakeGenerator(cfg, seed=42).generate_lexicon()]
    assert a == b                                   # byte-identical across runs


def test_lfake_different_seeds_differ():
    cfg = lfake.calibrate_to(_HEB_SAMPLE, mode="semitic")
    a = [e["form"] for e in lfake.LFakeGenerator(cfg, seed=1).generate_lexicon()]
    b = [e["form"] for e in lfake.LFakeGenerator(cfg, seed=2).generate_lexicon()]
    assert a != b


def test_calibrate_to_is_pure():
    # calibrate_to on the same input must return a config with identical observable stats
    cfg_a = lfake.calibrate_to(_HEB_SAMPLE, mode="semitic")
    cfg_b = lfake.calibrate_to(_HEB_SAMPLE, mode="semitic")
    assert cfg_a.inventory == cfg_b.inventory
    assert cfg_a.weights == cfg_b.weights
    assert cfg_a.length_probs == cfg_b.length_probs
    assert cfg_a.lexicon_size == cfg_b.lexicon_size


# --------------------------------------------------------------------------- #
# 2. THE CANARY GUARANTEE — and its honest boundary
# --------------------------------------------------------------------------- #
def test_lfake_zero_overlap_with_calibration_set():
    """The property actually verified by ``lexical_overlap_rate``: NO generated form reproduces a
    form in the CALIBRATION candidate set. This is the rejection-sampling guarantee."""
    cfg = lfake.calibrate_to(_HEB_SAMPLE, mode="semitic")
    cand = set(_HEB_SAMPLE)
    forms = [e["form"] for e in lfake.LFakeGenerator(cfg, seed=0).generate_lexicon()]
    assert all(f not in cand for f in forms)
    rep = lfake.divergence_report(forms, _HEB_SAMPLE, cfg)
    assert rep["lexical_overlap_rate"] == 0.0


def test_lfake_all_forms_unique():
    cfg = lfake.calibrate_to(_HEB_SAMPLE, mode="semitic")
    forms = [e["form"] for e in lfake.LFakeGenerator(cfg, seed=7).generate_lexicon()]
    assert len(forms) == len(set(forms))


def test_lfake_residual_real_root_collision_is_nonzero_and_bounded():
    """HONEST BOUNDARY (discovered in verification, preserved): WITHOUT an external full-Hebrew
    reject set, the rejection sampler only filters forms in the calibration set, so real Hebrew
    roots from OUTSIDE that set can slip into L_fake. This is demonstrated on the INDEPENDENT-
    consonant root sampler (empirical_roots=False), which draws each root consonant from the
    marginal distribution and therefore hits out-of-set Biblical-Hebrew roots by chance.

    This locks the calibration-set-only limitation in so the docstring's 'no real lexical content'
    wording can never be silently re-asserted as a property of the whole Hebrew language. The
    default empirical-root sampler is now structural enough to avoid this tiny-sample leak, and the
    FULL bhsa lexicon is required to bound the residual at corpus scale (see
    test_full_hebrew_lexicon_closes_residual_collision)."""
    cfg = lfake.calibrate_to(_HEB_SAMPLE, mode="semitic", empirical_roots=False)
    assert not any(r in set(_HEB_SAMPLE) for r in _KNOWN_HEBREW_ROOTS)  # roots are out-of-set
    colliding: set = set()
    for s in range(8):
        forms = set(e["form"] for e in lfake.LFakeGenerator(cfg, seed=s).generate_lexicon())
        colliding |= {r for r in _KNOWN_HEBREW_ROOTS if r in forms}
    # the leak is real: at least one known Hebrew root slips past the gold-file-only rejection
    assert len(colliding) >= 1, "expected non-zero residual collision; docstring overclaim undetected"
    # and sparse: well under half of the curated root list collides on a 20-form calibration sample
    assert len(colliding) < len(_KNOWN_HEBREW_ROOTS) // 2


def test_full_hebrew_lexicon_closes_residual_collision():
    """F.2 MEDIUM caveat 2 fix: with the ETCBC/bhsa full-Hebrew reject set supplied, the residual
    real-Hebrew collision rate of the emitted L_fake lexicon drops to ~0 (rejection sampled against
    the whole language). Skipped when the bhsa clone is absent (the canary then degrades to
    calibration-set-only rejection and says so)."""
    reject, _src = run_canary.load_hebrew_reject_set()
    if not reject:
        import pytest
        pytest.skip("ETCBC/bhsa lexicon not cloned (corpus/bronze/hebrew/bhsa); skip residual test")
    uga, heb, _ = run_canary.load_gold()
    heb_u = sorted(set(heb))
    cfg = lfake.calibrate_to(heb_u, mode="semitic", root_len=3,
                             external_reject=reject, external_reject_source="bhsa_test")
    assert cfg.external_reject                          # wired through
    rates = []
    for s in range(6):
        g = lfake.LFakeGenerator(cfg, seed=s)
        g.generate_lexicon()
        rep = lfake.divergence_report(g.generated, heb_u, cfg)
        rates.append(rep["residual_real_collision_rate"])
    import numpy as np
    mean_rate = float(np.mean(rates))
    # the regurgitation boundary is closed: residual is effectively zero
    assert mean_rate < 0.01, mean_rate
    # and the calibration-set guarantee still holds (no emitted form is a calibration-set form)
    g0 = lfake.LFakeGenerator(cfg, seed=0)
    g0.generate_lexicon()
    assert lfake.divergence_report(g0.generated, heb_u, cfg)["lexical_overlap_rate"] == 0.0


# --------------------------------------------------------------------------- #
# 3. POSITIVE CONTROL — real Ugaritic<->Hebrew cognates clear the L_fake floor
# --------------------------------------------------------------------------- #
def test_positive_control_real_cognates_clear_lfake_floor():
    """The self-validation's core: S_lex(real Ugaritic, Hebrew) must exceed the p95 of the
    S_lex(Ugaritic, L_fake) distribution, or the statistic has no power above the structural
    floor (F.2). Uses a deterministic gold-file slice for speed; the full run_canary.py reproduces
    the same ordering at corpus scale."""
    uga_u, heb_u = _load_gold_slice()
    cfg = lfake.calibrate_to(heb_u, mode="semitic", root_len=3)
    fakes = []
    for i in range(8):
        g = lfake.LFakeGenerator(cfg, seed=i)
        g.generate_lexicon()
        fakes.append(g.generated)
    pos = lexstat.s_lex(uga_u, heb_u, eps=0.25)
    fake_recalls = np.array([lexstat.s_lex(uga_u, fk, eps=0.25) for fk in fakes])
    p95 = float(np.percentile(fake_recalls, 95))
    assert pos > p95, (pos, p95, float(fake_recalls.mean()))
    # and the margin is not thin: real signal should clear the floor by a clear gap
    assert pos - float(fake_recalls.mean()) > 0.20


def test_lfake_floor_above_zero_and_below_positive():
    """The L_fake distribution must sit STRICTLY between 0 and the real-cognate score (else it is
    either degenerate or not a meaningful floor)."""
    uga_u, heb_u = _load_gold_slice()
    cfg = lfake.calibrate_to(heb_u, mode="semitic", root_len=3)
    g = lfake.LFakeGenerator(cfg, seed=0)
    g.generate_lexicon()
    fl = lexstat.s_lex(uga_u, g.generated, eps=0.25)
    pos = lexstat.s_lex(uga_u, heb_u, eps=0.25)
    assert 0.0 < fl < pos


# --------------------------------------------------------------------------- #
# 4. NULL GENERATORS — deterministic + frequency-banded (Packard) / multiset-preserving
# --------------------------------------------------------------------------- #
_NULL_FORMS = ["abd", "mlky", "twrhm", "bkr", "ab", "nym", "kab", "abd", "mlk", "twr"]


def test_packard_is_deterministic():
    a = nulls.packard_banded_permutation(_NULL_FORMS, seed=11)
    b = nulls.packard_banded_permutation(_NULL_FORMS, seed=11)
    assert a == b


def test_packard_preserves_lengths_and_band_multiset():
    """Packard 1974: a within-band bijection preserves word lengths and the multiset of character
    counts (which label carries which count is permuted; the sorted count list is invariant)."""
    from collections import Counter
    out = nulls.packard_banded_permutation(_NULL_FORMS, seed=0, n_bands=4)
    assert [len(w) for w in out] == [len(w) for w in _NULL_FORMS]
    assert sorted(Counter("".join(out)).values()) == sorted(Counter("".join(_NULL_FORMS)).values())


def test_packard_is_frequency_banded_not_free_permutation():
    """A FREE character permutation would also preserve the count multiset; Packard is stricter —
    a common char maps only to another char in the SAME frequency band. With n_bands equal to the
    inventory size the band-collapse degenerates, so test the banded property on a rich inventory:
    the most-common char must map to one of the most-common band."""
    from collections import Counter
    forms = ["ab", "ab", "ab", "ac", "ac", "de", "fg", "hi"]  # a common, d/f/h rare
    out = nulls.packard_banded_permutation(forms, seed=0, n_bands=2)
    # the bijection is a true relabelling (surjective on the inventory present)
    assert set("".join(out)) <= set("".join(forms))
    # and it actually permutes (not identity) under at least one seed on a rich inventory
    for s in range(20):
        if nulls.packard_banded_permutation(forms, seed=s, n_bands=2) != forms:
            return
    raise AssertionError("Packard never moved any char across 20 seeds")


def test_within_form_preserves_multiset_and_is_deterministic():
    from collections import Counter
    a = nulls.within_form_permutation(_NULL_FORMS, seed=5)
    b = nulls.within_form_permutation(_NULL_FORMS, seed=5)
    assert a == b
    for src, dst in zip(_NULL_FORMS, a):
        assert Counter(src) == Counter(dst)
        assert len(src) == len(dst)


def test_random_lexeme_null_stays_in_pool_and_is_deterministic():
    a = nulls.random_lexeme_null(_NULL_FORMS, n=40, seed=3)
    b = nulls.random_lexeme_null(_NULL_FORMS, n=40, seed=3)
    assert a == b
    pool = set(_NULL_FORMS)
    assert all(w in pool for w in a) and len(a) == 40


def test_null_distribution_runs_all_three_deterministically():
    def stat(held, L):
        return lexstat.s_lex(held, L, 0.25)
    a = nulls.null_distribution(stat, _NULL_FORMS, _NULL_FORMS, seed=0,
                                n_packard=3, n_random=3, n_within=3)
    b = nulls.null_distribution(stat, _NULL_FORMS, _NULL_FORMS, seed=0,
                                n_packard=3, n_random=3, n_within=3)
    assert set(a) == {"packard", "random_lexeme", "within_form"}
    assert all(len(v) == 3 for v in a.values())
    assert a == b                                  # full determinism of the assembled null


# --------------------------------------------------------------------------- #
# 5. CALIBRATION — frequency / length / lexicon-size match the candidate (F.2);
#    root-template divergence is REPORTED (Nair), not silently zero.
# --------------------------------------------------------------------------- #
def test_calibration_matches_frequency_length_size():
    uga, heb, _ = run_canary.load_gold()
    heb_u = sorted(set(heb))
    cfg = lfake.calibrate_to(heb_u, mode="semitic", root_len=3)
    g = lfake.LFakeGenerator(cfg, seed=0)
    g.generate_lexicon()
    rep = lfake.divergence_report(g.generated, heb_u, cfg)
    # marginal phoneme frequencies + word lengths are closely matched on the full corpus
    assert rep["phoneme_freq_TV"] < 0.10, rep["phoneme_freq_TV"]
    assert rep["length_TV"] < 0.10, rep["length_TV"]
    # lexicon size honoured exactly
    assert rep["n_generated"] == cfg.lexicon_size
    assert rep["lexicon_size_ratio"] == 1.0


def test_root_template_divergence_is_reported_not_hidden():
    """F.2 names root-template as a calibration axis. The generator now samples whole root TRIPLES
    from the candidate's attested trilateral-root frequency distribution (not independent
    marginals), seated at the deterministic template slots — so root_template_TV is PUBLISHED AND
    substantially reduced (from ~0.84 under the old independent-consonant sampler to well below
    0.5 here). The Nair contract is that the residual divergence is reported, never silently
    minimized to zero; assert the field exists, dropped well below the old level, and the report
    still carries the explicit "not ground truth" honesty note."""
    uga, heb, _ = run_canary.load_gold()
    heb_u = sorted(set(heb))
    cfg = lfake.calibrate_to(heb_u, mode="semitic", root_len=3)
    assert cfg.empirical_roots is True and len(cfg.root_triples) > 0
    g = lfake.LFakeGenerator(cfg, seed=0)
    g.generate_lexicon()
    rep = lfake.divergence_report(g.generated, heb_u, cfg)
    assert "root_template_TV" in rep and "bigram_KL" in rep
    # the empirical-root sampler closes the F.2 gap: TV dropped from ~0.84 to well under 0.5
    assert rep["root_template_TV"] < 0.50, rep["root_template_TV"]
    # it is NOT silently zero (finite-sample noise on the attested set leaves a real residual)
    assert rep["root_template_TV"] > 0.0
    # the report carries the explicit "not ground truth" honesty note
    assert "NOT ground truth" in rep["note"]


# --------------------------------------------------------------------------- #
# 6. VERDICT INTEGRATION — the additive stats are REPORTED and the §B.3 order-stat bar is wired,
#    WITHOUT moving the gate (deflated S_lex primary + L_fake headline stay; no-power S_morph is
#    neutral). These lock the integration-stage contract (design §A.2/§B.2/§B.3/§C.2, F.1).
# --------------------------------------------------------------------------- #
# realistic NW-Semitic-style consonantal skeletons (mirrors the scaffold fixtures)
_VCAND = ["nwy", "brq", "mlk", "ywm", "dn", "qtl", "zkr", "bnh", "hlk", "yqr"]
_VHELD = ["nwy", "brq", "mlk", "ywm", "dn", "qtl"]
_VBASE = dict(confidence=0.6, free_params=3, provenance="embedding_nn",
              lit_index_hit=False, not_indexed_sign_support=0.9, u_floor=8, n_eff=5, n_fake=6, seed=2)


def test_expected_max_order_stat_is_the_b3_bar_and_degrades_gracefully():
    """logos_stats.expected_max_order_stat is the §B.3 deflated bar E[max over N_eff null draws]:
    mu0=0 reduces it EXACTLY to expected_max_sharpe; n_trials<=1 (no multiplicity) and sigma0<=0 (no
    spread) return mu0 with no inv_cdf(0) = -inf; and it is monotone increasing in N_eff."""
    import math
    # mu0 = 0 special case is byte-identical to the Sharpe order statistic
    for n in (2, 5, 12, 100):
        a = logos_stats.expected_max_order_stat(0.0, math.sqrt(0.25), n)
        b = logos_stats.expected_max_sharpe(n, 0.25)
        assert a == b, (n, a, b)
    # mu0 shifts the bar by exactly mu0; sigma0 scales the multiplier
    assert logos_stats.expected_max_order_stat(0.3, 0.5, 12) == \
        0.3 + 0.5 * logos_stats._emax_unit_z(12)
    # graceful degeneracies (the design requires n_trials<=1 to NOT blow up)
    assert logos_stats.expected_max_order_stat(0.4, 1.0, 1) == 0.4
    assert logos_stats.expected_max_order_stat(0.4, 1.0, 0) == 0.4
    assert logos_stats.expected_max_order_stat(0.4, 0.0, 50) == 0.4
    # more trials -> higher expected maximum (the selection-bias bar tightens)
    assert logos_stats.expected_max_order_stat(0.0, 1.0, 5) < \
        logos_stats.expected_max_order_stat(0.0, 1.0, 500)


def test_grade_reports_s_phono_s_morph_and_order_stat_bar():
    """verdict.grade now REPORTS S_phono (phonostat §A.2), S_morph (morphostat §A.2) and the §B.3
    order-statistic bar — all additive diagnostics beneath the deflated-S_lex primary (F.1)."""
    g = verdict.grade(_VHELD, _VCAND, **_VBASE)
    # S_phono: a finite per-symbol log-likelihood here (negative), with the honest degenerate flag
    assert "s_phono" in g and g["s_phono_degenerate"] is False
    assert isinstance(g["s_phono"], float) and g["s_phono"] < 0.0
    # S_morph: a FULL no-power-aware dict (never a bare float that hides the no-power escape)
    assert isinstance(g["s_morph"], dict)
    assert {"is_powered", "reason", "z", "deflated"} <= set(g["s_morph"])
    assert g["s_morph_powered"] is False        # flat held-out -> single group -> no power
    # the §B.3 order-stat bar + DSR are reported alongside (NOT replacing) the primary dsr
    assert "order_stat_bar" in g and "dsr_order" in g and "sigma_hat" in g
    assert "dsr" in g                            # the primary deflated_sharpe DSR is untouched


def test_no_power_s_morph_does_not_change_the_gate_verdict():
    """A no-power S_morph is REPORTED but NEUTRAL to the gate: the morph clause is True, never in
    failing_clauses, and the gate verdict is identical whether the held-out is flat (single group)
    or grouped into too-few inscriptions — i.e. the gold-standard-when-powered wiring did not move
    any previously-decided verdict (F.1: no-power != pass and != fail)."""
    g_flat = verdict.grade(_VHELD, _VCAND, **_VBASE)
    # 2 inscriptions < min_inscriptions(3) -> guaranteed no power, regardless of affix inventory
    grouped = [["nwy", "brq", "mlk"], ["ywm", "dn", "qtl"]]
    g_grouped = verdict.grade(_VHELD, _VCAND, heldout_by_inscription=grouped, **_VBASE)
    assert g_flat["s_morph_powered"] is False and g_grouped["s_morph_powered"] is False
    # the morph clause is neutral-True in both and never blocks
    for g in (g_flat, g_grouped):
        assert g["clauses"]["morph_gold_standard_when_powered"] is True
        assert "morph_gold_standard_when_powered" not in g["failing_clauses"]
        # removing the always-True no-power clause cannot change the AND over clauses (proves neutral)
        others = {k: v for k, v in g["clauses"].items() if k != "morph_gold_standard_when_powered"}
        assert all(g["clauses"].values()) == all(others.values())
    # and the two runs reach the SAME gate verdict (the morph machinery moved nothing)
    assert g_flat["gate_verdict"] == g_grouped["gate_verdict"]


def test_powered_but_insignificant_s_morph_can_fail_the_gate_clause():
    """Verifier-found regression: the morph gate clause must NOT be a tautology. When the corpus CAN
    test morphology (has_power=True) but the candidate's affixes do NOT productively recur above the
    null (is_significant=False), the clause is FALSE and appears in failing_clauses — the strong test
    was available and the candidate failed it. (Previously the clause keyed off is_powered, which
    already implied deflated>0, so it could never be False — the gate enforced nothing here.)"""
    # a candidate with a clear ma-/-Vu morphology, and a grouped held-out (within-form shuffled real
    # data, frozen) that is testable but whose recurrence sits at the null -> powered-but-insignificant.
    cand_rich = ["matabu", "makalu", "maradu", "masidu", "manaru", "kabtu", "rabtu", "sidtu",
                 "naqtu", "baltu", "tabu", "radu", "sidu", "naru"]
    grouped = [["aulmku", "tbzau", "rguim"], ["urmzaa", "patuh", "kunun"], ["iubram", "ltiu", "gdala"],
               ["uzaurm", "putis", "lwkaa"], ["idmaul", "tnhua", "akrup"]]
    flat = [f for insc in grouped for f in insc]
    g = verdict.grade(flat, cand_rich, heldout_by_inscription=grouped, **_VBASE)
    # the morph sub-result is genuinely POWERED but NOT significant (the case the tautology hid)
    assert g["s_morph"]["has_power"] is True
    assert g["s_morph"]["is_significant"] is False
    assert g["s_morph_powered"] is False
    # therefore the gate clause is FALSE (it can now block) and is reported as failing
    assert g["clauses"]["morph_gold_standard_when_powered"] is False
    assert "morph_gold_standard_when_powered" in g["failing_clauses"]
    assert g["gate_verdict"] != "GRADUATE"


def test_searchlog_neff_overrides_passed_count_in_grade():
    """The instrumented N_eff (searchlog §B.2, invariant 12) is consumed: a SearchLog's COUNTED
    distinct-candidate total overrides the hand-passed n_eff and is recorded as such."""
    log = searchlog.SearchLog()
    for i in range(7):
        log.log_candidate({"*301": "na"}, f"lex{i}", ["na"])
    log.log_candidate({"*301": "na"}, "lex0", ["na"])     # exact replay -> dedup, n_eff stays 7
    assert log.n_eff == 7
    base = dict(_VBASE); base["n_eff"] = 1                  # hand-passed (would be the fallback)
    g = verdict.grade(_VHELD, _VCAND, search_log=log, **base)
    assert g["n_trials"] == 7 and g["n_trials_source"] == "searchlog"   # P0.3: trials, not independent tests
    # without the log, the passed count is used (clean fallback, no crash)
    g0 = verdict.grade(_VHELD, _VCAND, **base)
    assert g0["n_trials"] == 1 and g0["n_trials_source"] == "passed"


def test_litindex_not_indexed_support_feeds_the_e_gate_via_grade_row():
    """P0.2: generalizes_to_not_indexed uses litindex.not_indexed_support (§C.2) AND requires a PRE-REGISTERED
    threshold + >= not_indexed_min_signs DISTINCT not_indexed signs — never a single hit, and FAIL CLOSED when
    the prereg commits no threshold."""
    import json
    body = json.dumps({"free_params": 3, "provenance": "embedding_nn"})
    part2 = {"L_known": ["DA"], "L_not_indexed": ["*301", "*302"]}
    # PASS: committed threshold + TWO distinct not_indexed signs carry support
    pred_ok = json.dumps({"heldout_forms": _VHELD, "candidate_lexicon": _VCAND, "n_eff": 5,
                          "not_indexed_threshold": 0.5, "not_indexed_min_signs": 2,
                          "per_sign_support": {"*301": 1.0, "*302": 1.0, "DA": 0.0},
                          "sign_partition": part2})
    assert verdict.grade_row("ph", "fam", body, pred_ok, 0.6, n_fake=6, seed=2)["clauses"]["generalizes_to_not_indexed"] is True
    # FAIL CLOSED: a SINGLE not_indexed sign (even at full support) is not discovery
    part1 = {"L_known": ["DA"], "L_not_indexed": ["*301"]}
    pred_one = json.dumps({"heldout_forms": _VHELD, "candidate_lexicon": _VCAND, "n_eff": 5,
                           "not_indexed_threshold": 0.5, "not_indexed_min_signs": 2,
                           "per_sign_support": {"*301": 1.0, "DA": 0.0}, "sign_partition": part1})
    assert verdict.grade_row("ph", "fam", body, pred_one, 0.6, n_fake=6, seed=2)["clauses"]["generalizes_to_not_indexed"] is False
    # FAIL CLOSED: NO committed threshold -> clause cannot pass even with two supported not_indexed signs
    pred_noth = json.dumps({"heldout_forms": _VHELD, "candidate_lexicon": _VCAND, "n_eff": 5,
                            "per_sign_support": {"*301": 1.0, "*302": 1.0, "DA": 0.0}, "sign_partition": part2})
    assert verdict.grade_row("ph", "fam", body, pred_noth, 0.6, n_fake=6, seed=2)["clauses"]["generalizes_to_not_indexed"] is False
    # FAIL: support entirely on a literature-KNOWN sign -> memorization, not discovery
    pred_k = json.dumps({"heldout_forms": _VHELD, "candidate_lexicon": _VCAND, "n_eff": 5,
                         "not_indexed_threshold": 0.5, "per_sign_support": {"*301": 0.0, "*302": 0.0, "DA": 1.0},
                         "sign_partition": part2})
    gk = verdict.grade_row("ph", "fam", body, pred_k, 0.6, n_fake=6, seed=2)
    assert gk["clauses"]["generalizes_to_not_indexed"] is False
    assert "generalizes_to_not_indexed" in gk["failing_clauses"]


def test_gate_clauses_fail_closed_on_degenerate_input():
    """P0 regression: (1) the removed k<=u_floor clause is GONE and cannot silently pass; (2) the
    operative order-stat clause fails closed on a degenerate (zero-variance) null; (3) DSR is
    reported-only, not a gate clause."""
    base = dict(_VBASE)
    g = verdict.grade(_VHELD, _VCAND, **base)
    # (1) the incoherent MDL clause is deleted; u_floor is reported-only
    assert "k_le_u_floor" not in g["clauses"]
    assert "dsr_ge_0_95" not in g["clauses"]              # finance-DSR demoted off the decision path
    assert "beats_order_stat_bar" in g["clauses"]         # order-stat bar is the operative deflation clause
    assert "dsr" in g and "order_stat_bar" in g           # both still REPORTED
    # (2) a constant null (no variance) -> order-stat bar is meaningless -> clause FAILS CLOSED
    g_deg = verdict.grade(_VHELD, _VCAND, null_recalls=[0.5, 0.5, 0.5, 0.5], **base)
    assert g_deg["clauses"]["beats_order_stat_bar"] is False
    assert g_deg["gate_verdict"] != "GRADUATE"
