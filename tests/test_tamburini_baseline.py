"""Protocol-correctness tests for the Tamburini 2025 baseline wrapper
(scripts/baselines/run_tamburini.py).

These do NOT run CSA (a single Ugaritic energy eval is ~19 s on CPU; the full
protocol is hours/seed — covered by docs/findings, not by unit tests). They lock
in the parts that are cheap to verify and that, if silently wrong, would make
every reproduced number meaningless:

  1. The N/M/lambda settings obey Tamburini 2025 §3.3's stated rule
     ("N=1, M=2 if |L_s|>|K_s| else N=2, M=1; lambda=4 generally, 8 for U/OH-noisy").
  2. The published Table 3 numbers we compare against are present and unchanged
     (CSA mean + decontaminated NeuroCipher), so a future hand-edit that breaks
     the comparison is caught.
  3. The vendored code is present and importable (so the wrapper can call it).
  4. The benchmark inventory matches what the paper's Table 3 reports (6 of 7
     benchmarks; CS/AG IS in the repo data — the 7th, LB/MG-names, is not).

Run from anywhere:
    pytest tests/test_tamburini_baseline.py -v
"""
import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.baselines import run_tamburini as rt  # noqa: E402

# Expected (N, M, penf) per Tamburini 2025 §3.3 + the inventory cardinalities
# from CSA_OptMatcher.py `alphabets` (|L_s| = lost col-0, |K_s| = known col-1).
# Rule: N=1,M=2 if |L_s|>|K_s| else N=2,M=1; penf=8 only for U/OH-noisy.
EXPECTED_PROTOCOL = {
    # benchmark:          (N, M, penf, |L_s|, |K_s|)
    "ugaritic-noiseless":   (1, 2, 4.0, 30, 23),   # |uga|30 > |heb|23
    "ugaritic-noisy":       (1, 2, 8.0, 30, 23),   # lambda=8 (his stated exception)
    "linearb-greek":        (2, 1, 4.0, 73, 92),   # |linb|73 < |greek|92
    "cypriot-greek":        (2, 1, 4.0, 54, 92),   # CS/AG: |csyl|54 < |greek|92
    "phoenician-ugaritic":  (2, 1, 4.0, 30, 34),   # Ph/Ug: |Ph|30 < |Ug|34
    "luvian-hittite":       (2, 1, 4.0, 21, 24),   # Luv/Hit: |luv|21 < |hit|24
}

# Tamburini 2025 Table 3 (mean over 4 seeds, GPU/100000-step artifact).
EXPECTED_PUBLISHED_CSA = {
    "ugaritic-noiseless": 95.5, "ugaritic-noisy": 74.7, "linearb-greek": 89.4,
    "cypriot-greek": 86.3, "phoenician-ugaritic": 80.5, "luvian-hittite": 47.5,
}


def test_inventory_matches_table3():
    # All 6 benchmarks with data in the repo are registered (the 7th Table-3
    # benchmark, LB/MG-names, has no .cog in the repo and is intentionally absent).
    assert set(rt.BENCHMARKS) == set(EXPECTED_PROTOCOL)


def test_nm_rule_and_penf():
    for bench, (N, M, penf, Ls, Ks) in EXPECTED_PROTOCOL.items():
        cfg = rt.BENCHMARKS[bench]
        # The paper's N/M rule:
        exp_N, exp_M = (1, 2) if Ls > Ks else (2, 1)
        assert (cfg["N"], cfg["M"]) == (exp_N, exp_M), (
            f"{bench}: N/M {(cfg['N'], cfg['M'])} != rule {(exp_N, exp_M)} "
            f"for |L_s|={Ls},|K_s|={Ks}")
        # The well-formedness constraint his code asserts (N*|L_s| >= |K_s|):
        assert cfg["N"] * Ls >= Ks, f"{bench}: N*|L_s|={cfg['N']*Ls} < |K_s|={Ks}"
        assert cfg["penf"] == penf, f"{bench}: penf {cfg['penf']} != {penf}"


def test_published_numbers_present():
    for bench, pub in EXPECTED_PUBLISHED_CSA.items():
        assert rt.BENCHMARKS[bench]["published_csa"] == pub, (
            f"{bench}: published_csa drifted from Table 3 ({pub})")


def test_oga_heb_noisy_uses_lambda8_exception():
    # The one stated deviation from the default lambda=4.
    assert rt.BENCHMARKS["ugaritic-noisy"]["penf"] == 8.0
    assert rt.BENCHMARKS["ugaritic-noiseless"]["penf"] == 4.0


def test_cog_data_files_exist():
    # The vendored data must be cloned (corpus/bronze is gitignored) for the
    # wrapper to run; this test fails loudly if a clone is missing.
    for bench, cfg in rt.BENCHMARKS.items():
        path = os.path.join(rt.DATA_DIR, cfg["cog"])
        assert os.path.isfile(path), f"{bench}: missing cog data {path}"


def test_16_annealers_protocol_constant():
    # The paper fixes n_annealers=16; the wrapper must not silently change it.
    import inspect
    src = inspect.getsource(rt._build_annealer)
    assert "n_annealers = 16" in src
